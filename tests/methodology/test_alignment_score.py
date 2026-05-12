"""Validate the Donor Alignment Score formula.

Properties under test:
  1. Determinism — same inputs produce the same output, every time.
  2. Bounds — score is in [0, 100].
  3. Edge cases — undefined industries are excluded; re-normalization is correct.
  4. Worked example — methodology §3.6 example reproduces in code to the unit.
  5. Symmetry — flipping all vote directions flips the score around 50.
  6. No hidden state — calling the function with no global setup yields the documented number.

Reference implementation: tests/methodology/alignment_score.py
"""
from __future__ import annotations

import pytest

from tests.methodology.alignment_score import (
    AlignmentScoreResult,
    compute_alignment_score,
    top_n_industries,
)


# ---------------------------------------------------------------------------
# 1. Determinism
# ---------------------------------------------------------------------------

def test_determinism_repeated_calls_identical(fec_fixture, bill_industry_map, propublica_fixture):
    map_ = bill_industry_map["bills"]
    votes = propublica_fixture["votes"]
    totals = fec_fixture["industry_totals_career"]
    first = compute_alignment_score(totals, map_, votes)
    for _ in range(50):
        again = compute_alignment_score(totals, map_, votes)
        assert again.score == first.score
        assert again.A == first.A
        assert tuple((i.industry, i.weight, i.a_i, i.included) for i in again.industries) == \
               tuple((i.industry, i.weight, i.a_i, i.included) for i in first.industries)


def test_determinism_input_ordering_irrelevant(fec_fixture, bill_industry_map, propublica_fixture):
    """Re-ordering the inputs must not change the result."""
    map_ = bill_industry_map["bills"]
    totals = fec_fixture["industry_totals_career"]
    votes = list(propublica_fixture["votes"])
    base = compute_alignment_score(totals, map_, votes)
    shuffled = compute_alignment_score(totals, map_, list(reversed(votes)))
    assert base.score == shuffled.score
    assert base.A == shuffled.A


# ---------------------------------------------------------------------------
# 2. Bounds
# ---------------------------------------------------------------------------

def test_score_in_bounds(fec_fixture, bill_industry_map, propublica_fixture):
    r = compute_alignment_score(
        fec_fixture["industry_totals_career"],
        bill_industry_map["bills"],
        propublica_fixture["votes"],
    )
    assert 0 <= r.score <= 100
    assert -1.0 <= r.A <= 1.0


# ---------------------------------------------------------------------------
# 3. Edge cases
# ---------------------------------------------------------------------------

def test_industries_with_fewer_than_three_scored_votes_excluded(fec_fixture, bill_industry_map, propublica_fixture):
    """Lawyers/Law Firms has only 2 scored votes in the fixture — must be excluded."""
    r = compute_alignment_score(
        fec_fixture["industry_totals_career"],
        bill_industry_map["bills"],
        propublica_fixture["votes"],
    )
    excluded_names = set(r.excluded_industries)
    assert "Lawyers/Law Firms" in excluded_names, (
        f"Lawyers/Law Firms should be excluded for low vote count; excluded set was {excluded_names}"
    )


def test_renormalization_sums_to_one(fec_fixture, bill_industry_map, propublica_fixture):
    r = compute_alignment_score(
        fec_fixture["industry_totals_career"],
        bill_industry_map["bills"],
        propublica_fixture["votes"],
    )
    included_weight = sum(i.weight for i in r.industries if i.included)
    assert abs(included_weight - 1.0) < 1e-9, (
        f"Included industry weights should sum to 1.0 after renormalization, got {included_weight}"
    )


def test_non_industry_buckets_not_in_top_n(fec_fixture):
    """`Retired` and `Self-Employed` must never appear in the top-N."""
    top = top_n_industries(fec_fixture["industry_totals_career"], n=5)
    names = {n for n, _ in top}
    assert "Retired" not in names
    assert "Self-Employed" not in names


# ---------------------------------------------------------------------------
# 4. Worked example from methodology §3.6
# ---------------------------------------------------------------------------

def test_worked_example_from_methodology_section_3_6():
    """Reproduce the synthetic Candidate X example verbatim. Expected score: 79."""
    industry_totals = {
        "Securities & Investment": 400_000.0,
        "Real Estate":             250_000.0,
        "Lawyers/Law Firms":       200_000.0,
        "Health Professionals":    100_000.0,
        "Pro-Israel":               50_000.0,
    }
    # Direction +1 for all (industry favored YES). Votes constructed so a_i match §3.6:
    #   Securities (3 votes): Yes, Yes, No  -> +1, +1, -1 -> a = 1/3
    #   Real Estate (4 votes): all Yes      -> a = 1.0
    #   Lawyers (2 votes): both Yes         -> EXCLUDED (n<3)
    #   Health (3 votes): Yes, Yes, No      -> a = 1/3
    #   Pro-Israel (5 votes): all Yes       -> a = 1.0
    bill_map = {
        # Securities
        "s1": {"industry": "Securities & Investment", "direction": 1},
        "s2": {"industry": "Securities & Investment", "direction": 1},
        "s3": {"industry": "Securities & Investment", "direction": 1},
        # Real Estate
        "r1": {"industry": "Real Estate", "direction": 1},
        "r2": {"industry": "Real Estate", "direction": 1},
        "r3": {"industry": "Real Estate", "direction": 1},
        "r4": {"industry": "Real Estate", "direction": 1},
        # Lawyers (only 2 — should be excluded)
        "l1": {"industry": "Lawyers/Law Firms", "direction": 1},
        "l2": {"industry": "Lawyers/Law Firms", "direction": 1},
        # Health
        "h1": {"industry": "Health Professionals", "direction": 1},
        "h2": {"industry": "Health Professionals", "direction": 1},
        "h3": {"industry": "Health Professionals", "direction": 1},
        # Pro-Israel
        "p1": {"industry": "Pro-Israel", "direction": 1},
        "p2": {"industry": "Pro-Israel", "direction": 1},
        "p3": {"industry": "Pro-Israel", "direction": 1},
        "p4": {"industry": "Pro-Israel", "direction": 1},
        "p5": {"industry": "Pro-Israel", "direction": 1},
    }
    votes = [
        {"bill_id": "s1", "position": "Yes"},
        {"bill_id": "s2", "position": "Yes"},
        {"bill_id": "s3", "position": "No"},

        {"bill_id": "r1", "position": "Yes"},
        {"bill_id": "r2", "position": "Yes"},
        {"bill_id": "r3", "position": "Yes"},
        {"bill_id": "r4", "position": "Yes"},

        {"bill_id": "l1", "position": "Yes"},
        {"bill_id": "l2", "position": "Yes"},

        {"bill_id": "h1", "position": "Yes"},
        {"bill_id": "h2", "position": "Yes"},
        {"bill_id": "h3", "position": "No"},

        {"bill_id": "p1", "position": "Yes"},
        {"bill_id": "p2", "position": "Yes"},
        {"bill_id": "p3", "position": "Yes"},
        {"bill_id": "p4", "position": "Yes"},
        {"bill_id": "p5", "position": "Yes"},
    ]
    r: AlignmentScoreResult = compute_alignment_score(industry_totals, bill_map, votes)
    assert "Lawyers/Law Firms" in r.excluded_industries
    assert r.score == 79, (
        f"Methodology §3.6 worked example must produce 79; got {r.score} (A={r.A!r}). "
        "If this fails, the docs and the implementation disagree — fix one to match the other."
    )


# ---------------------------------------------------------------------------
# 5. Symmetry
# ---------------------------------------------------------------------------

def test_symmetry_score_flips_around_fifty():
    """If we flip every industry's direction, the score should be (100 - original)."""
    industry_totals = {
        "Securities & Investment": 400_000.0,
        "Real Estate":             250_000.0,
        "Health Professionals":    100_000.0,
        "Pro-Israel":               50_000.0,
        "Lawyers/Law Firms":       200_000.0,
    }
    base_map = {
        "a1": {"industry": "Securities & Investment", "direction": 1},
        "a2": {"industry": "Securities & Investment", "direction": 1},
        "a3": {"industry": "Securities & Investment", "direction": 1},
        "b1": {"industry": "Real Estate", "direction": 1},
        "b2": {"industry": "Real Estate", "direction": 1},
        "b3": {"industry": "Real Estate", "direction": 1},
        "c1": {"industry": "Health Professionals", "direction": 1},
        "c2": {"industry": "Health Professionals", "direction": 1},
        "c3": {"industry": "Health Professionals", "direction": 1},
        "d1": {"industry": "Pro-Israel", "direction": 1},
        "d2": {"industry": "Pro-Israel", "direction": 1},
        "d3": {"industry": "Pro-Israel", "direction": 1},
        "e1": {"industry": "Lawyers/Law Firms", "direction": 1},
        "e2": {"industry": "Lawyers/Law Firms", "direction": 1},
        "e3": {"industry": "Lawyers/Law Firms", "direction": 1},
    }
    votes = [{"bill_id": bid, "position": "Yes"} for bid in base_map]
    r1 = compute_alignment_score(industry_totals, base_map, votes)
    flipped_map = {bid: {**e, "direction": -e["direction"]} for bid, e in base_map.items()}
    r2 = compute_alignment_score(industry_totals, flipped_map, votes)
    assert r1.score + r2.score == 100, (
        f"Symmetry violated: original={r1.score}, flipped={r2.score}"
    )


# ---------------------------------------------------------------------------
# 6. No hidden state / no randomness
# ---------------------------------------------------------------------------

def test_no_randomness_across_python_sessions(fec_fixture, bill_industry_map, propublica_fixture):
    """Two independent computations in two distinct dicts give identical results."""
    a = compute_alignment_score(
        dict(fec_fixture["industry_totals_career"]),
        dict(bill_industry_map["bills"]),
        [dict(v) for v in propublica_fixture["votes"]],
    )
    b = compute_alignment_score(
        dict(fec_fixture["industry_totals_career"]),
        dict(bill_industry_map["bills"]),
        [dict(v) for v in propublica_fixture["votes"]],
    )
    assert a == b


# ---------------------------------------------------------------------------
# 7. Position-value handling
# ---------------------------------------------------------------------------

def test_unknown_position_raises():
    industry_totals = {"X": 100.0, "Y": 100.0, "Z": 100.0, "W": 100.0, "V": 100.0}
    bill_map = {"b1": {"industry": "X", "direction": 1}}
    with pytest.raises(ValueError, match="Unknown ProPublica position"):
        compute_alignment_score(industry_totals, bill_map, [{"bill_id": "b1", "position": "Maybe"}])
