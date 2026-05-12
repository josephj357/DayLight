"""Broward County local-races ingestion.

Source: Broward County Supervisor of Elections — https://www.browardsoe.gov/
The records are public; the VoterFocus UI layered on top is the vendor's IP.
We scrape the records, not the UI artifacts. See /docs/research/local-data.md.

V1 status: stub. Local-races data is the project's highest-value coverage gap,
but it's also the most labor-intensive to ingest correctly. Filling this in
for one's own county is the recommended first contribution for forkers.
"""
from __future__ import annotations

import logging
import sqlite3

from ._common import DistrictConfig, log_ingestion

logger = logging.getLogger(__name__)


def run(conn: sqlite3.Connection, district: DistrictConfig) -> int:
    if not district.county_offices:
        return 0

    # TODO: implement Broward SOE scrape.
    #
    # Approach:
    #   1. For each county/school-board/judicial race in district.county_offices,
    #      district.judicial_offices, district.special_offices:
    #      a. Find the candidates from the SOE candidate-list page.
    #      b. For each candidate, pull their campaign-finance filings (CSV when
    #         available, HTML table otherwise).
    #   2. Normalize contributions into the contributions table with
    #      source = 'broward_soe'.
    #
    # Sanity checks before writing:
    #   - Sum of itemized contributions per filing must roughly match the
    #     filing's reported totals (within rounding).
    #   - Mark filings older than 30 days as "stale" in ingestion_log.note.

    log_ingestion(
        conn,
        "broward_soe",
        "partial",
        note=(
            "Broward local scraper not implemented in v1. "
            "Highest-value contribution: implement this for one race "
            "(Commission, School Board, or judicial) and PR it. "
            "See /docs/research/local-data.md for the SOE portal layout."
        ),
    )
    return 0


if __name__ == "__main__":
    import sys

    from ._common import get_db, load_district_config

    district_id = sys.argv[1] if len(sys.argv) > 1 else "fl-23"
    logging.basicConfig(level=logging.INFO)
    db = get_db()
    cfg = load_district_config(district_id)
    n = run(db, cfg)
    print(f"Broward local ingestion: {n} rows for {district_id}")
