"""Shared ingestion utilities.

- District config loading (the YAML in /config/districts/).
- HTTP fetcher with on-disk caching by content hash.
- SQLite connection helper.
- Ingestion-log writer for the methodology page's "last refreshed" display.

Keep this module dependency-free apart from the pinned third-party libs.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import re

import requests
import yaml

logger = logging.getLogger("daylight.ingestion")

# Match common API-key query params so we never log a key by accident.
_KEY_REDACT_RE = re.compile(r"([?&])(api_key|apikey|key|token)=[^&]*", re.IGNORECASE)


def _redact_url(url: str) -> str:
    """Strip API-key-shaped query params from URLs before logging."""
    return _KEY_REDACT_RE.sub(r"\1\2=REDACTED", url)


def _redact(s: str) -> str:
    return _KEY_REDACT_RE.sub(r"\1\2=REDACTED", s)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = REPO_ROOT / "data" / "daylight.db"
CACHE_DIR = REPO_ROOT / "src" / "ingestion" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class DistrictConfig:
    """Parsed view of /config/districts/<id>.yml."""

    id: str
    raw: dict[str, Any]

    @property
    def state(self) -> str:
        return self.raw["state"]

    @property
    def cycle(self) -> str:
        return str(self.raw.get("cycle", "2024"))

    @property
    def federal(self) -> list[dict[str, Any]]:
        return list(self.raw.get("federal", []) or [])

    @property
    def state_offices(self) -> list[dict[str, Any]]:
        # `state_offices` is the canonical key; older configs may use `state`
        # but that collides with the top-level state abbreviation, so prefer
        # state_offices and fall back only as a deprecation hatch.
        return list(self.raw.get("state_offices", []) or [])

    @property
    def county_offices(self) -> list[dict[str, Any]]:
        return list(self.raw.get("county", []) or [])

    @property
    def judicial_offices(self) -> list[dict[str, Any]]:
        return list(self.raw.get("judicial", []) or [])

    @property
    def special_offices(self) -> list[dict[str, Any]]:
        return list(self.raw.get("special", []) or [])

    @property
    def zip_codes(self) -> list[str]:
        return list(self.raw.get("zip_codes", []) or [])

    @property
    def data_sources(self) -> dict[str, Any]:
        return dict(self.raw.get("data_sources", {}) or {})


def load_district_config(district_id: str) -> DistrictConfig:
    """Load /config/districts/<district_id>.yml.

    Raises FileNotFoundError if the district has no config — never guesses
    boundaries.
    """
    path = REPO_ROOT / "config" / "districts" / f"{district_id}.yml"
    if not path.exists():
        raise FileNotFoundError(f"District config not found: {path}")
    with path.open() as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"District config must be a YAML mapping: {path}")
    return DistrictConfig(id=district_id, raw=data)


def list_district_configs() -> list[str]:
    """Return all district IDs that have a config file."""
    config_dir = REPO_ROOT / "config" / "districts"
    if not config_dir.exists():
        return []
    return sorted(p.stem for p in config_dir.glob("*.yml"))


def get_db(db_path: Path | None = None) -> sqlite3.Connection:
    """Open the SQLite database, applying the schema if it doesn't exist."""
    path = Path(db_path or os.environ.get("DAYLIGHT_DB_PATH", DEFAULT_DB_PATH))
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    schema_path = REPO_ROOT / "src" / "schema" / "schema.sql"
    if schema_path.exists():
        with schema_path.open() as f:
            conn.executescript(f.read())
        conn.commit()
    return conn


def _cache_path(key: str) -> Path:
    h = hashlib.sha256(key.encode()).hexdigest()
    return CACHE_DIR / f"{h}.json"


def cached_get(
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    *,
    ttl_seconds: int = 86_400,
    timeout: int = 30,
) -> dict[str, Any] | None:
    """HTTP GET with on-disk JSON caching.

    Returns parsed JSON on 2xx, None on any failure (so callers can decide
    how to degrade). Network errors are logged, not raised.
    """
    key = json.dumps({"url": url, "params": params or {}}, sort_keys=True)
    cache_file = _cache_path(key)
    if cache_file.exists() and (time.time() - cache_file.stat().st_mtime) < ttl_seconds:
        try:
            return json.loads(cache_file.read_text())
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Cache read failed for %s: %s", url, e)
    try:
        resp = requests.get(url, params=params, headers=headers or {}, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        cache_file.write_text(json.dumps(data))
        return data
    except requests.RequestException as e:
        # Never log the URL with query params or the exception's str() (both
        # would echo any embedded api_key). Redact both before logging.
        safe_url = _redact_url(url)
        safe_err = _redact(str(e))
        logger.warning("HTTP GET failed: %s (status=%s err=%s)",
                       safe_url,
                       getattr(getattr(e, "response", None), "status_code", "?"),
                       safe_err)
        return None
    except ValueError as e:
        logger.warning("Non-JSON response from %s: %s", _redact_url(url), e)
        return None


def log_ingestion(
    conn: sqlite3.Connection,
    source: str,
    status: str,
    rows_written: int = 0,
    note: str = "",
) -> None:
    """Append a row to ingestion_log so the UI can show last-refreshed times."""
    conn.execute(
        """
        INSERT INTO ingestion_log (source, started_at, finished_at, status, rows_written, note)
        VALUES (?, datetime('now'), datetime('now'), ?, ?, ?)
        """,
        (source, status, rows_written, note),
    )
    conn.commit()


def hash_inputs(*parts: str) -> str:
    """Stable hash for synthesis-cache keys and similar."""
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode())
        h.update(b"\0")
    return h.hexdigest()
