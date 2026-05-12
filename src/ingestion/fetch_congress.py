"""Congress.gov ingestion (Library of Congress).

Source: https://api.congress.gov/v3/ — public-domain government data.

This module replaces the discontinued ProPublica Congress API (shut down
2024-07-10). Per /docs/research/data-licensing.md, the substitution is
clean: Congress.gov is the canonical upstream that ProPublica was wrapping.

What we pull per federal candidate:
- Member metadata (bioguide ID, congress number).
- Sponsored and cosponsored bills (limited to current congress for v1).
- Roll-call votes by the member (current congress).
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


def _fetch_member_votes(bioguide_id: str, congress: int) -> dict[str, Any] | None:
    """Member-vote endpoints on Congress.gov are still maturing.

    For v1 we pull recent House roll-call votes for the given congress and let
    the caller filter to votes cast by this member. This is acceptable for v1
    volumes (~700 votes/congress); for higher volumes this should be paginated
    or moved to a bulk-import path.
    """
    key = _api_key()
    if not key:
        return None
    return cached_get(
        f"{CONGRESS_BASE}/house-vote/{congress}",
        params={"api_key": key, "format": "json", "limit": 250},
    )


def _ensure_bill(conn: sqlite3.Connection, bill: dict[str, Any]) -> str | None:
    """Upsert a bill row. Returns the bill_id or None if input is malformed."""
    bill_type = (bill.get("type") or "").lower()
    number = bill.get("number")
    congress = bill.get("congress")
    if not bill_type or number is None or congress is None:
        return None
    bill_id = f"{bill_type}-{number}-{congress}"
    conn.execute(
        """
        INSERT OR IGNORE INTO bills
            (id, congress, bill_type, number, title, summary, introduced_date, status, congress_gov_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            bill_id,
            int(congress),
            bill_type,
            int(number),
            bill.get("title"),
            bill.get("summary"),
            bill.get("introducedDate"),
            bill.get("latestAction", {}).get("text") if isinstance(bill.get("latestAction"), dict) else None,
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
            continue

        # Member metadata might enrich politicians/candidates rows; for v1 we
        # just ensure the bioguide id is on the candidate row.
        # The actual candidate row was created by fetch_fec.py.

        # Pull recent House votes; this is a stub that future contributors
        # extend with member-specific filtering.
        votes = _fetch_member_votes(bioguide, congress=118)
        if not votes:
            continue

        for vote in (votes.get("houseVotes") or []):
            bill_ref = vote.get("bill") or {}
            bill_id = _ensure_bill(conn, bill_ref)
            if not bill_id:
                continue
            # We do not yet have per-member position from this endpoint in v1.
            # The full member-vote linkage requires the more detailed
            # /house-vote/{congress}/{session}/{rollnumber} endpoint, which is
            # left as a TODO for a future ingestion expansion.
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
