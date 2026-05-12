"""Ingestion orchestrator.

Reads the district config(s), runs each ingestion module in order, populates
SQLite. Idempotent — safe to run repeatedly. Designed to be called from
`scripts/seed.sh` or from cron.

Usage:
    python -m src.ingestion.pipeline                # all districts
    python -m src.ingestion.pipeline --district fl-23   # one district
"""
from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from typing import Callable

from ._common import (
    DistrictConfig,
    get_db,
    list_district_configs,
    load_district_config,
    log_ingestion,
)
from . import (
    fetch_fec,
    fetch_congress,
    load_opensecrets_bulk,
    fetch_florida_state,
    fetch_broward_local,
    synthesize,
)

logger = logging.getLogger("daylight.pipeline")


# Order matters: candidate rows are created by fetch_fec, so it must run first.
# Synthesis runs last because it consumes the structured data the others write.
INGESTION_STEPS: list[tuple[str, Callable[[sqlite3.Connection, DistrictConfig], int]]] = [
    ("fec", fetch_fec.run),
    ("congress_gov", fetch_congress.run),
    ("opensecrets_bulk", load_opensecrets_bulk.run),
    ("florida_state", fetch_florida_state.run),
    ("broward_local", fetch_broward_local.run),
    ("synthesis", synthesize.run),
]


def _seed_zip_routes(conn: sqlite3.Connection, district: DistrictConfig) -> None:
    """Populate zip_district_map from the district YAML."""
    for zip_code in district.zip_codes:
        conn.execute(
            "INSERT OR REPLACE INTO zip_district_map (zip, district_id) VALUES (?, ?)",
            (zip_code, district.id),
        )
    conn.commit()


def _seed_district_row(conn: sqlite3.Connection, district: DistrictConfig) -> None:
    raw = district.raw
    conn.execute(
        """
        INSERT OR REPLACE INTO districts
            (id, display_name, description, state, fips_state, plan_id, snapshot_date, config_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            district.id,
            raw["display_name"],
            raw.get("description"),
            raw["state"],
            raw["fips_state"],
            raw.get("plan_id"),
            raw["snapshot_date"],
            f"/config/districts/{district.id}.yml",
        ),
    )
    conn.commit()


def run_district(conn: sqlite3.Connection, district_id: str) -> dict[str, int]:
    cfg = load_district_config(district_id)
    _seed_district_row(conn, cfg)
    _seed_zip_routes(conn, cfg)

    results: dict[str, int] = {}
    for name, fn in INGESTION_STEPS:
        logger.info("Running ingestion step: %s for %s", name, district_id)
        try:
            n = fn(conn, cfg)
            results[name] = n
        except Exception as e:  # noqa: BLE001 — log and continue
            logger.exception("Ingestion step failed: %s", name)
            log_ingestion(conn, name, "failed", note=str(e))
            results[name] = 0
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run DayLight ingestion.")
    parser.add_argument(
        "--district",
        help="District ID (e.g. 'fl-23'). If omitted, runs every district under /config/districts/.",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )

    conn = get_db()
    districts = [args.district] if args.district else list_district_configs()
    if not districts:
        print("No district configs found in /config/districts/.")
        return 1

    summary: dict[str, dict[str, int]] = {}
    for d in districts:
        summary[d] = run_district(conn, d)

    print("\nIngestion summary:")
    for d, results in summary.items():
        total = sum(results.values())
        print(f"  {d}: {total} rows total")
        for k, v in results.items():
            print(f"    {k:20s} {v} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
