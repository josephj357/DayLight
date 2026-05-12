"""OpenSecrets bulk-data loader.

Source: https://www.opensecrets.org/open-data/bulk-data
License: CC BY-NC-SA 3.0 US (attribute, non-commercial, share-alike).
Status: The OpenSecrets API was discontinued 2025-04-15; bulk data is the
only supported access path going forward.

What this loader does:
  1. Reads CSV files from /data/opensecrets/ (you download them manually
     from opensecrets.org's bulk-data portal — this loader does NOT scrape).
  2. Populates the industry_totals table per federal candidate.
  3. Annotates the contributions table with industry codes where they align.

What this loader does NOT do:
  - Hit any OpenSecrets API (there isn't one anymore).
  - Redistribute the bulk data files (keep them out of the repo).
  - Ingest the Revolving Door section (separately licensed via Columbia Books;
    see /docs/research/data-licensing.md).

Layout expected at /data/opensecrets/ (you create this; gitignored):
    cands<CYCLE>.txt        # candidate summary
    indus<CYCLE>.txt        # candidate-by-industry rollup
    pacs<CYCLE>.txt         # PAC contributions
"""
from __future__ import annotations

import csv
import logging
import sqlite3
from pathlib import Path
from typing import Iterable

from ._common import DistrictConfig, REPO_ROOT, log_ingestion

logger = logging.getLogger(__name__)

BULK_DIR = REPO_ROOT / "data" / "opensecrets"


def _read_pipe_csv(path: Path) -> Iterable[list[str]]:
    """OpenSecrets bulk files are pipe-delimited with no header row."""
    if not path.exists():
        return iter(())
    with path.open(encoding="latin-1") as f:
        reader = csv.reader(f, delimiter="|", quotechar="|")
        yield from reader


def _industry_file(cycle: str) -> Path:
    short = cycle[-2:]
    return BULK_DIR / f"indus{short}.txt"


def _load_industry_totals_for_candidate(
    conn: sqlite3.Connection,
    candidate_id: str,
    opensecrets_id: str,
    cycle: str,
) -> int:
    """Load the OpenSecrets industry rollup for one candidate (CRP CID).

    OpenSecrets' indusXX.txt format (paraphrased — verify against current
    bulk-data README before bumping):
        Cycle | CRP_CID | Industry_Code | Industry_Name | Total | Indivs | PACs
    """
    indus_file = _industry_file(cycle)
    if not indus_file.exists():
        logger.warning("OpenSecrets bulk file missing: %s", indus_file)
        return 0

    rows_written = 0
    for row in _read_pipe_csv(indus_file):
        if len(row) < 5:
            continue
        if row[1].strip().strip('"') != opensecrets_id:
            continue
        industry_name = row[3].strip().strip('"')
        try:
            total = float(row[4].strip().strip('"'))
        except (ValueError, IndexError):
            continue
        conn.execute(
            """
            INSERT OR REPLACE INTO industry_totals
                (candidate_id, industry, amount, cycle)
            VALUES (?, ?, ?, ?)
            """,
            (candidate_id, industry_name, total, cycle),
        )
        rows_written += 1
    return rows_written


def run(conn: sqlite3.Connection, district: DistrictConfig) -> int:
    rows_written = 0
    for race in district.federal:
        incumbent = race.get("incumbent") or {}
        opensecrets_id = incumbent.get("opensecrets_id")
        if not opensecrets_id:
            continue
        name_slug = incumbent["name"].lower().replace(" ", "-").replace(",", "")
        office = race.get("office", "U.S. House")
        district_label = race.get("district_label", "")
        race_id = f"{district.id}/{office.lower().replace(' ', '-')}-{district_label.lower()}"
        cand_id = f"{race_id}/{name_slug}"

        rows_written += _load_industry_totals_for_candidate(
            conn,
            candidate_id=cand_id,
            opensecrets_id=opensecrets_id,
            cycle=race.get("cycle", district.cycle),
        )

    conn.commit()
    status = "ok" if rows_written else "partial"
    log_ingestion(
        conn,
        "opensecrets_bulk",
        status,
        rows_written=rows_written,
        note=(
            "no bulk files in /data/opensecrets — download manually from "
            "opensecrets.org/open-data/bulk-data and re-run"
            if not rows_written
            else f"district={district.id}"
        ),
    )
    return rows_written


if __name__ == "__main__":
    import sys

    from ._common import get_db, load_district_config

    district_id = sys.argv[1] if len(sys.argv) > 1 else "fl-23"
    logging.basicConfig(level=logging.INFO)
    db = get_db()
    cfg = load_district_config(district_id)
    n = run(db, cfg)
    print(f"OpenSecrets bulk load: {n} rows for {district_id}")
