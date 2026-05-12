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

    # State-level ingestion remains a stub in v1 because the natural source
    # (FL DoS at https://dos.elections.myflorida.com/campaign-finance/) sits
    # behind a Cloudflare managed-challenge page — verified 2026-05-12. Direct
    # HTTP from this codebase returns the JS challenge HTML, not the form.
    #
    # Three viable paths for whoever picks this up:
    #
    # 1. **FollowTheMoney.org API** (most tractable). Free signup at
    #    https://www.followthemoney.org/our-data/apis. Normalized from FL DoS
    #    data, current through 2024. Wire a new fetcher here that hits their
    #    REST endpoint and maps responses into the `contributions` table with
    #    source='fl_doe'. Verify license terms first (research doc has a
    #    [TODO: verify] on redistribution rights).
    #
    # 2. **The Accountability Project bulk** at
    #    https://publicaccountability.org/datasets/40/fl_contribs/. 27M FL
    #    contribution records 1995-2023, normalized. Bulk download is large
    #    (multi-GB) so this is an offline-load pattern, not an API. License
    #    also needs verification.
    #
    # 3. **Headed Playwright against FL DoS directly**. Solves the Cloudflare
    #    challenge but introduces a heavy dependency and may still get
    #    flagged for automated traffic. Last-resort path.
    #
    # All three live in /docs/research/state-data.md — update that doc with
    # what you find when you build one.

    log_ingestion(
        conn,
        "fl_doe",
        "partial",
        note=(
            "FL DoS portal is Cloudflare-challenged; direct scrape blocked. "
            "See fetch_florida_state.py docstring for the three viable paths."
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
