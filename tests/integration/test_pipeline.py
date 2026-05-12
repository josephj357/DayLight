"""End-to-end ingestion-pipeline smoke test against frozen API fixtures.

The actual ingestion code lives in /src/ingestion/ and is owned by backend-dev.
This test simulates the full pipeline by:

  1. Reading the frozen API fixtures (FEC, OpenSecrets, ProPublica).
  2. Writing them into a temp SQLite database via the schema in conftest.py.
  3. Computing the Donor Alignment Score from the DB state.
  4. Asserting the score is in range, deterministic, and traceable to source rows.

When /src/ingestion/pipeline.py exists, swap the inline reads here for a call to
pipeline.run() against a fixture-mode flag. The assertions remain the same.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from tests.methodology.alignment_score import compute_alignment_score

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures"


def _industry_totals_from_db(conn: sqlite3.Connection, cand_id: str) -> dict[str, float]:
    rows = conn.execute(
        "SELECT industry, career_total FROM industry_totals WHERE candidate_id = ?",
        (cand_id,),
    ).fetchall()
    return {industry: amount for industry, amount in rows}


def _votes_from_db(conn: sqlite3.Connection, cand_id: str) -> list[dict[str, str]]:
    rows = conn.execute(
        "SELECT bill_id, position FROM votes WHERE candidate_id = ? ORDER BY roll_call",
        (cand_id,),
    ).fetchall()
    return [{"bill_id": b, "position": p} for b, p in rows]


def _bill_map_from_db(conn: sqlite3.Connection) -> dict[str, dict[str, object]]:
    rows = conn.execute("SELECT bill_id, industry, direction FROM bill_industry_map").fetchall()
    return {b: {"industry": i, "direction": d} for b, i, d in rows}


# ---------------------------------------------------------------------------

def test_pipeline_runs_end_to_end(seeded_db, fl23_candidate_id):
    industry_totals = _industry_totals_from_db(seeded_db, fl23_candidate_id)
    votes = _votes_from_db(seeded_db, fl23_candidate_id)
    bill_map = _bill_map_from_db(seeded_db)
    result = compute_alignment_score(industry_totals, bill_map, votes)
    assert 0 <= result.score <= 100


def test_pipeline_is_deterministic(seeded_db, fl23_candidate_id):
    industry_totals = _industry_totals_from_db(seeded_db, fl23_candidate_id)
    votes = _votes_from_db(seeded_db, fl23_candidate_id)
    bill_map = _bill_map_from_db(seeded_db)
    a = compute_alignment_score(industry_totals, bill_map, votes)
    b = compute_alignment_score(industry_totals, bill_map, votes)
    assert a == b


def test_pipeline_excludes_low_vote_industries(seeded_db, fl23_candidate_id):
    industry_totals = _industry_totals_from_db(seeded_db, fl23_candidate_id)
    votes = _votes_from_db(seeded_db, fl23_candidate_id)
    bill_map = _bill_map_from_db(seeded_db)
    result = compute_alignment_score(industry_totals, bill_map, votes)
    assert "Lawyers/Law Firms" in result.excluded_industries


def test_pipeline_score_matches_direct_fixture_calc(seeded_db, fl23_candidate_id):
    """Score derived via DB round-trip must match score derived directly from fixtures."""
    industry_totals_db = _industry_totals_from_db(seeded_db, fl23_candidate_id)
    votes_db = _votes_from_db(seeded_db, fl23_candidate_id)
    bill_map_db = _bill_map_from_db(seeded_db)
    via_db = compute_alignment_score(industry_totals_db, bill_map_db, votes_db)

    with (FIXTURE_DIR / "fec_fl23_incumbent.json").open() as f:
        fec = json.load(f)
    with (FIXTURE_DIR / "propublica_fl23_votes.json").open() as f:
        pp = json.load(f)
    import yaml
    with (FIXTURE_DIR / "bill_industry_map.yaml").open() as f:
        bim = yaml.safe_load(f)["bills"]
    direct = compute_alignment_score(fec["industry_totals_career"], bim, pp["votes"])
    assert via_db.score == direct.score
    assert via_db.A == pytest.approx(direct.A)


def test_pipeline_every_vote_resolves_to_a_known_bill(seeded_db, fl23_candidate_id):
    """A vote row in the DB whose bill_id is missing from the bill_industry_map is fine —
    it just means that vote isn't scored — but every bill_industry_map entry must have a
    corresponding vote row (otherwise our scored-bills config is stale)."""
    bill_map = _bill_map_from_db(seeded_db)
    votes = _votes_from_db(seeded_db, fl23_candidate_id)
    vote_bill_ids = {v["bill_id"] for v in votes}
    missing_votes = [b for b in bill_map if b not in vote_bill_ids]
    assert not missing_votes, (
        f"bill_industry_map references bills with no recorded vote for FL-23: {missing_votes}. "
        "Either ProPublica is stale, or the map references the wrong chamber/session."
    )


def test_pipeline_inserts_match_fixture_counts(seeded_db, fl23_candidate_id):
    """Make sure seeding actually loaded everything (guards against silent fixture drift)."""
    industries = seeded_db.execute(
        "SELECT COUNT(*) FROM industry_totals WHERE candidate_id = ?", (fl23_candidate_id,)
    ).fetchone()[0]
    votes = seeded_db.execute(
        "SELECT COUNT(*) FROM votes WHERE candidate_id = ?", (fl23_candidate_id,)
    ).fetchone()[0]
    bills = seeded_db.execute("SELECT COUNT(*) FROM bill_industry_map").fetchone()[0]
    assert industries == 10, f"Expected 10 industry rows from FEC fixture, got {industries}"
    assert votes == 17, f"Expected 17 vote rows from ProPublica fixture, got {votes}"
    assert bills == 17, f"Expected 17 bill→industry map entries, got {bills}"
