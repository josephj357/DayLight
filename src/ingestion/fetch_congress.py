"""Congress.gov ingestion (Library of Congress).

Source: https://api.congress.gov/v3/ — public-domain government data.

This module replaces the discontinued ProPublica Congress API (shut down
2024-07-10). Per /docs/research/data-licensing.md, the substitution is
clean: Congress.gov is the canonical upstream that ProPublica was wrapping.

What we pull per federal candidate (v1):
- Member metadata (bioguide ID, terms).
- Sponsored legislation (bills the member authored).

What we deliberately do NOT pull in v1:
- Roll-call votes. Congress.gov's `house-roll-call-vote` endpoint returns
  an error in practice (verified 2026-05-12). Vote ingestion is parked
  until a working upstream is identified (clerk.house.gov bulk XML is the
  most likely candidate).
- Cosponsored bills. Modeling cosponsorship correctly requires a
  separate `bill_cosponsors` table that doesn't exist in v1 — sponsored
  bills alone are the more direct "what the politician chose to push"
  signal anyway.
"""
from __future__ import annotations

import logging
import os
import sqlite3
from typing import Any

from ._common import DistrictConfig, cached_get, log_ingestion

logger = logging.getLogger(__name__)

CONGRESS_BASE = "https://api.congress.gov/v3"


def _api_key() -> str | None:
    return os.environ.get("CONGRESS_GOV_API_KEY") or None


def _fetch_member(bioguide_id: str) -> dict[str, Any] | None:
    key = _api_key()
    if not key:
        logger.warning("CONGRESS_GOV_API_KEY not set; skipping Congress.gov pull.")
        return None
    return cached_get(
        f"{CONGRESS_BASE}/member/{bioguide_id}",
        params={"api_key": key, "format": "json"},
    )


def _fetch_sponsored_legislation(bioguide_id: str, limit: int = 50) -> dict[str, Any] | None:
    key = _api_key()
    if not key:
        return None
    return cached_get(
        f"{CONGRESS_BASE}/member/{bioguide_id}/sponsored-legislation",
        params={"api_key": key, "format": "json", "limit": limit},
    )


def _ensure_politician(
    conn: sqlite3.Connection,
    bioguide_id: str,
    name: str,
    current_office: str | None = None,
) -> str:
    """Idempotent upsert of a politician row, return its id."""
    politician_id = f"politician:bioguide:{bioguide_id}"
    conn.execute(
        """
        INSERT OR IGNORE INTO politicians (id, name, bioguide_id, current_office)
        VALUES (?, ?, ?, ?)
        """,
        (politician_id, name, bioguide_id, current_office),
    )
    return politician_id


def _ensure_bill(
    conn: sqlite3.Connection,
    bill: dict[str, Any],
    sponsor_politician_id: str | None = None,
) -> str | None:
    """Upsert a bill row. Returns the bill_id or None if input is malformed."""
    bill_type = (bill.get("type") or "").lower()
    number = bill.get("number")
    congress = bill.get("congress")
    if not bill_type or number is None or congress is None:
        return None
    bill_id = f"{bill_type}-{number}-{congress}"

    latest_action_text = None
    la = bill.get("latestAction")
    if isinstance(la, dict):
        latest_action_text = la.get("text")

    conn.execute(
        """
        INSERT OR REPLACE INTO bills
            (id, congress, bill_type, number, title, summary, sponsor_id,
             introduced_date, status, congress_gov_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            bill_id,
            int(congress),
            bill_type,
            int(number),
            bill.get("title"),
            bill.get("policyArea", {}).get("name") if isinstance(bill.get("policyArea"), dict) else None,
            sponsor_politician_id,
            bill.get("introducedDate"),
            latest_action_text,
            bill.get("url"),
        ),
    )
    return bill_id


def run(conn: sqlite3.Connection, district: DistrictConfig) -> int:
    rows_written = 0
    for race in district.federal:
        incumbent = race.get("incumbent") or {}
        bioguide = incumbent.get("bioguide_id")
        if not bioguide:
            continue

        member = _fetch_member(bioguide)
        if not member:
            logger.warning("Member fetch failed for bioguide=%s", bioguide)
            continue

        politician_id = _ensure_politician(
            conn,
            bioguide_id=bioguide,
            name=incumbent.get("name", bioguide),
            current_office=race.get("office"),
        )

        # Attach the politician_id to the candidate row (set if currently NULL).
        # Candidate row is created by fetch_fec.run, which must have already
        # executed per INGESTION_STEPS ordering.
        conn.execute(
            """
            UPDATE candidates
            SET politician_id = COALESCE(politician_id, ?), bioguide_id = ?
            WHERE bioguide_id = ? OR fec_candidate_id = ?
            """,
            (
                politician_id,
                bioguide,
                bioguide,
                incumbent.get("fec_candidate_id") or "",
            ),
        )

        sponsored = _fetch_sponsored_legislation(bioguide, limit=50)
        if not sponsored:
            logger.warning("No sponsored-legislation payload for bioguide=%s", bioguide)
            continue

        for bill in (sponsored.get("sponsoredLegislation") or []):
            if _ensure_bill(conn, bill, sponsor_politician_id=politician_id):
                rows_written += 1

    conn.commit()
    log_ingestion(conn, "congress_gov", "ok", rows_written=rows_written, note=f"district={district.id}")
    return rows_written


if __name__ == "__main__":
    import sys

    from ._common import get_db, load_district_config

    district_id = sys.argv[1] if len(sys.argv) > 1 else "fl-23"
    logging.basicConfig(level=logging.INFO)
    db = get_db()
    cfg = load_district_config(district_id)
    n = run(db, cfg)
    print(f"Congress.gov ingestion: {n} rows for {district_id}")
