"""AI synthesis layer.

Generates the plain-English summary card per candidate using the Anthropic
API. Output is cached in the synthesis_cache table keyed by an input hash, so
re-runs against unchanged inputs cost nothing.

Neutrality is enforced by:
  - The system prompt in /src/ingestion/prompts/synthesis_prompt.md.
  - The red-flag vocabulary test in /tests/methodology/test_synthesis_neutrality.py.

Model pinning per ADR-005.
"""
from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ._common import DistrictConfig, REPO_ROOT, hash_inputs, log_ingestion

logger = logging.getLogger(__name__)

PROMPT_PATH = REPO_ROOT / "src" / "ingestion" / "prompts" / "synthesis_prompt.md"
DEFAULT_MODEL = "claude-sonnet-4-5"
SYNTHESIS_VERSION = "synthesis-v1"


def _load_prompt() -> tuple[str, str]:
    """Return (system_prompt, user_prompt_template) parsed from the markdown."""
    text = PROMPT_PATH.read_text()
    # Sections are delimited by '## System prompt' and '## User prompt'.
    parts = text.split("## System prompt", 1)
    if len(parts) != 2:
        raise ValueError("synthesis_prompt.md missing '## System prompt' section")
    after_sys = parts[1].split("## User prompt", 1)
    if len(after_sys) != 2:
        raise ValueError("synthesis_prompt.md missing '## User prompt' section")
    system_prompt = after_sys[0].strip()
    user_prompt = after_sys[1].strip()
    return system_prompt, user_prompt


def _substitute(template: str, variables: dict[str, str]) -> str:
    out = template
    for k, v in variables.items():
        out = out.replace("{{" + k + "}}", v)
    return out


def _render_bullets(items: list[str]) -> str:
    return "\n".join(f"- {x}" for x in items) if items else "- (none provided)"


def _fetch_candidate_inputs(conn: sqlite3.Connection, candidate_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT name, party, race_id FROM candidates WHERE id = ?",
        (candidate_id,),
    ).fetchone()
    if not row:
        return None
    race = conn.execute(
        "SELECT office, district_label FROM races WHERE id = ?",
        (row["race_id"],),
    ).fetchone()
    industries = conn.execute(
        """
        SELECT industry, amount FROM industry_totals
        WHERE candidate_id = ?
        ORDER BY amount DESC LIMIT 5
        """,
        (candidate_id,),
    ).fetchall()
    return {
        "name": row["name"],
        "party": row["party"] or "—",
        "office": race["office"] if race else "",
        "district": race["district_label"] if race else "",
        "incumbent": True,  # v1 only synthesizes for federal incumbents
        "stated_platform": [],  # TODO: ingest from candidate sites / Vote Smart
        "top_industries": [f"{ind['industry']}: ${ind['amount']:,.0f}" for ind in industries],
        "notable_votes": [],  # TODO: wire to bill_industry_map + votes
        "revolving_door": [],
    }


def _call_anthropic(system_prompt: str, user_prompt: str, model: str) -> str | None:
    """Call the Anthropic API. Returns None on any failure (we degrade gracefully)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set; skipping synthesis.")
        return None
    try:
        import anthropic  # type: ignore
    except ImportError:
        logger.warning("anthropic package not installed; skipping synthesis.")
        return None
    try:
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=model,
            max_tokens=400,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        # anthropic SDK returns content as list[ContentBlock]
        body = "".join(getattr(b, "text", "") for b in resp.content)
        return body.strip() or None
    except Exception as e:  # noqa: BLE001 — degrade gracefully on any client error
        logger.warning("Anthropic call failed: %s", e)
        return None


def synthesize_candidate(conn: sqlite3.Connection, candidate_id: str) -> str | None:
    """Generate (or read cached) synthesis text for a candidate."""
    inputs = _fetch_candidate_inputs(conn, candidate_id)
    if not inputs:
        return None

    snapshot_date = datetime.now(timezone.utc).date().isoformat()
    variables = {
        "candidate_name": inputs["name"],
        "office": inputs["office"],
        "district": inputs["district"],
        "party": inputs["party"],
        "is_incumbent": "yes" if inputs["incumbent"] else "no",
        "stated_platform_bullets": _render_bullets(inputs["stated_platform"]),
        "top_industries_bullets": _render_bullets(inputs["top_industries"]),
        "notable_votes_bullets": _render_bullets(inputs["notable_votes"]),
        "revolving_door_bullets": _render_bullets(inputs["revolving_door"]),
        "methodology_version": SYNTHESIS_VERSION,
        "snapshot_date": snapshot_date,
    }

    system_prompt, user_template = _load_prompt()
    user_prompt = _substitute(user_template, variables)
    input_hash = hash_inputs(system_prompt, user_prompt)

    cached = conn.execute(
        "SELECT body FROM synthesis_cache WHERE candidate_id = ? AND input_hash = ?",
        (candidate_id, input_hash),
    ).fetchone()
    if cached:
        return cached["body"]

    model = os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)
    body = _call_anthropic(system_prompt, user_prompt, model)
    if not body:
        return None
    if "[INSUFFICIENT_DATA]" in body:
        # Per the prompt's refusal path — don't cache as a real synthesis.
        return None

    conn.execute(
        """
        INSERT OR REPLACE INTO synthesis_cache
            (candidate_id, body, model_label, generated_at, input_hash, caveat)
        VALUES (?, ?, ?, datetime('now'), ?, ?)
        """,
        (
            candidate_id,
            body,
            f"{model} ({SYNTHESIS_VERSION})",
            input_hash,
            "Generated from publicly disclosed data. See /docs/methodology.md.",
        ),
    )
    conn.commit()
    return body


def run(conn: sqlite3.Connection, district: DistrictConfig) -> int:
    """Generate synthesis for every federal candidate in the district."""
    rows = conn.execute(
        """
        SELECT c.id FROM candidates c
        JOIN races r ON r.id = c.race_id
        WHERE r.district_id = ? AND r.level = 'federal'
        """,
        (district.id,),
    ).fetchall()
    n = 0
    for row in rows:
        result = synthesize_candidate(conn, row["id"])
        if result:
            n += 1
    log_ingestion(conn, "synthesis", "ok", rows_written=n, note=f"district={district.id}")
    return n


if __name__ == "__main__":
    import sys

    from ._common import get_db, load_district_config

    district_id = sys.argv[1] if len(sys.argv) > 1 else "fl-23"
    logging.basicConfig(level=logging.INFO)
    db = get_db()
    cfg = load_district_config(district_id)
    n = run(db, cfg)
    print(f"Synthesis: {n} cards for {district_id}")
