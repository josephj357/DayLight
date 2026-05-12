"""Federal Election Commission ingestion.

Source: https://api.open.fec.gov/v1/ — public domain, free, requires API key.
Statutory note: contributor data may NOT be used to solicit donations or sold
as a contributor list (52 U.S.C. § 30111(a)(4)). DayLight does neither.

What we pull (per federal candidate in the district config):
- Candidate metadata (FEC candidate ID, principal committee, totals).
- Top contributors by employer.
- Contributions by industry (career rollup).

We do NOT pull individual contributor rows for v1. That dataset is large and
the per-candidate rollups already give us what the UI needs.
"""
from __future__ import annotations

import logging
import os
import sqlite3
from typing import Any

from ._common import DistrictConfig, cached_get, log_ingestion

logger = logging.getLogger(__name__)

FEC_BASE = "https://api.open.fec.gov/v1"


def _api_key() -> str | None:
    return os.environ.get("FEC_API_KEY") or None


def _fetch_candidate_totals(candidate_id: str, cycle: str) -> dict[str, Any] | None:
    key = _api_key()
    if not key:
        logger.warning("FEC_API_KEY not set; skipping FEC pull.")
        return None
    return cached_get(
        f"{FEC_BASE}/candidate/{candidate_id}/totals/",
        params={"api_key": key, "cycle": cycle},
    )


def _fetch_principal_committee(candidate_id: str, cycle: str) -> str | None:
    """Find the principal campaign committee ID for a candidate.

    FEC's schedule_a/by_employer endpoint only exists at the committee level,
    so we need to look up the committee before we can query by employer.
    """
    key = _api_key()
    if not key:
        return None
    data = cached_get(
        f"{FEC_BASE}/candidate/{candidate_id}/committees/",
        params={"api_key": key, "cycle": cycle, "designation": "P"},
    )
    if not data or not data.get("results"):
        return None
    # Designation "P" = principal campaign committee; take the first.
    for committee in data["results"]:
        if committee.get("designation") == "P":
            return committee.get("committee_id")
    return data["results"][0].get("committee_id")


def _fetch_top_contributors_by_employer(committee_id: str, cycle: str) -> dict[str, Any] | None:
    key = _api_key()
    if not key:
        return None
    # FEC's by_employer aggregation lives under /schedules/, filtered by committee_id.
    # The candidate/{id}/schedule_a/by_employer and committee/{id}/schedule_a/by_employer
    # paths exist in the docs but return 404 in practice — only /schedules/schedule_a/by_employer
    # actually serves data.
    return cached_get(
        f"{FEC_BASE}/schedules/schedule_a/by_employer/",
        params={
            "api_key": key,
            "committee_id": committee_id,
            "cycle": cycle,
            "per_page": 20,
            "sort": "-total",
        },
    )


def _ensure_candidate_row(
    conn: sqlite3.Connection,
    district_id: str,
    race: dict[str, Any],
    candidate: dict[str, Any],
    cycle: str,
) -> str:
    """Idempotent upsert of a federal candidate row.

    Returns the candidate_id used in the candidates table.
    """
    office = race.get("office", "U.S. House")
    district_label = race.get("district_label", "")
    race_id = f"{district_id}/{office.lower().replace(' ', '-')}-{district_label.lower()}"

    # Race row
    conn.execute(
        """
        INSERT OR IGNORE INTO races (id, district_id, office, level, district_label, cycle, ballot_order)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (race_id, district_id, office, "federal", district_label, cycle, 0),
    )

    name_slug = candidate["name"].lower().replace(" ", "-").replace(",", "")
    cand_id = f"{race_id}/{name_slug}"
    conn.execute(
        """
        INSERT OR REPLACE INTO candidates
            (id, race_id, name, party, incumbent, fec_candidate_id, bioguide_id, cycle)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            cand_id,
            race_id,
            candidate["name"],
            candidate.get("party"),
            1,
            candidate.get("fec_candidate_id"),
            candidate.get("bioguide_id"),
            cycle,
        ),
    )
    return cand_id


def run(conn: sqlite3.Connection, district: DistrictConfig) -> int:
    """Run FEC ingestion for one district. Returns rows written."""
    rows_written = 0
    for race in district.federal:
        incumbent = race.get("incumbent") or {}
        fec_id = incumbent.get("fec_candidate_id")
        if not fec_id:
            logger.info("No fec_candidate_id in district config; skipping race.")
            continue

        cycle = race.get("cycle", district.cycle)
        cand_id = _ensure_candidate_row(conn, district.id, race, incumbent, cycle)

        totals = _fetch_candidate_totals(fec_id, cycle)
        if totals and totals.get("results"):
            row = totals["results"][0]
            conn.execute(
                "UPDATE candidates SET total_raised = ? WHERE id = ?",
                (row.get("receipts"), cand_id),
            )
            rows_written += 1

        committee_id = _fetch_principal_committee(fec_id, cycle)
        if not committee_id:
            logger.info("No principal committee for %s in cycle %s; skipping employer rollup.", fec_id, cycle)
        else:
            contributors = _fetch_top_contributors_by_employer(committee_id, cycle)
            if contributors and contributors.get("results"):
                for entry in contributors["results"]:
                    employer = entry.get("employer")
                    total = entry.get("total")
                    if not employer or total is None:
                        continue
                    conn.execute(
                        """
                        INSERT INTO contributions
                            (candidate_id, amount, cycle, source, raw_employer)
                        VALUES (?, ?, ?, 'fec', ?)
                        """,
                        (cand_id, total, cycle, employer),
                    )
                    rows_written += 1

    conn.commit()
    log_ingestion(conn, "fec", "ok", rows_written=rows_written, note=f"district={district.id}")
    return rows_written


if __name__ == "__main__":
    import sys

    from ._common import get_db, load_district_config

    district_id = sys.argv[1] if len(sys.argv) > 1 else "fl-23"
    logging.basicConfig(level=logging.INFO)
    db = get_db()
    cfg = load_district_config(district_id)
    n = run(db, cfg)
    print(f"FEC ingestion: {n} rows for {district_id}")
