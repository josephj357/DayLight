"""Florida state-level campaign-finance ingestion.

Source: Florida Division of Elections — https://dos.fl.gov/elections/
The state's campaign-finance database doesn't expose a public REST API. It
serves searchable HTML forms and CSV exports.

V1 status: stub. The actual scraper is left for a contributor who lives in
Florida and can verify the exports against the current DoS portal. The
function shape is locked in so the pipeline doesn't break; it just logs
that data is unavailable until the scraper is filled in.

Forking-for-your-state guidance:
  - Almost every state has a campaign-finance disclosure portal.
  - About half of them publish CSV exports.
  - The rest require parsing HTML or PDFs.
  - Write a state-specific module in this directory and wire it into pipeline.py.
"""
from __future__ import annotations

import logging
import sqlite3

from ._common import DistrictConfig, log_ingestion

logger = logging.getLogger(__name__)


def run(conn: sqlite3.Connection, district: DistrictConfig) -> int:
    """Run state-level ingestion for one district.

    Returns rows written. For v1 this returns 0 and logs that state data
    is not yet ingested for the district.
    """
    if district.state != "FL":
        logger.info(
            "fetch_florida_state called for non-FL district %s; skipping.",
            district.id,
        )
        log_ingestion(conn, "fl_doe", "partial", note="non-FL district")
        return 0

    # TODO: implement Florida DoS scrape.
    # Phases:
    #   1. Build the DoS search-form URL for each state-office race in district.state_offices.
    #   2. Submit the form, parse the CSV export (or HTML table).
    #   3. Normalize donors -> donors table, contributions -> contributions table
    #      with source = 'fl_doe'.
    #
    # The DoS search URL pattern is documented in /docs/research/state-data.md.
    # That doc also flags the 2026 redistricting litigation — be careful with
    # district boundaries until the courts settle.

    log_ingestion(
        conn,
        "fl_doe",
        "partial",
        note=(
            "Florida state scraper not implemented in v1. "
            "See /docs/research/state-data.md for the DoS portal URL pattern."
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
    print(f"Florida state ingestion: {n} rows for {district_id}")
