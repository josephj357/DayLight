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
    classify_employer,
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
    # Fallback industry classifier runs AFTER OpenSecrets bulk so it never
    # overwrites real OpenSecrets data (different source=, different row).
    ("industry_classifier", classify_employer.run),
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


def _slug(s: str) -> str:
    # Match fetch_fec.py's race-id slugging exactly so race_shells and the FEC
    # fetcher converge on the same id (otherwise we get a duplicate U.S. House
    # row — one from each path). Keep dots; fetch_fec doesn't strip them.
    return s.lower().replace(" ", "-").replace(",", "")


def _seed_race_shells(conn: sqlite3.Connection, district: DistrictConfig) -> int:
    """Create empty race rows for every office listed in the district YAML.

    This runs BEFORE the fetchers so that races without an ingestion path
    (state, county, judicial, special — all currently stubs) still appear in
    the UI as "office exists, donor data pending." The federal fetcher will
    then upsert into the same rows when it runs.
    """
    rows = 0
    sections: list[tuple[str, list[dict]]] = [
        ("federal", district.federal),
        ("state", district.state_offices),
        ("county", district.county_offices),
        ("judicial", district.judicial_offices),
        ("special", district.special_offices),
    ]
    for level, offices in sections:
        for idx, office in enumerate(offices):
            office_name = office.get("office")
            district_label = office.get("district_label", "")
            cycle = str(office.get("cycle", district.cycle))
            if not office_name:
                continue
            race_id = f"{district.id}/{_slug(office_name)}-{_slug(district_label)}"
            conn.execute(
                """
                INSERT OR IGNORE INTO races
                    (id, district_id, office, level, district_label, cycle, ballot_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (race_id, district.id, office_name, level, district_label, cycle, idx),
            )
            rows += 1
    conn.commit()
    log_ingestion(conn, "race_shells", "ok", rows_written=rows, note=f"district={district.id}")
    return rows


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
    race_rows = _seed_race_shells(conn, cfg)

    results: dict[str, int] = {"race_shells": race_rows}
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
