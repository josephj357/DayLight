"""Prove that adding a new district via YAML works WITHOUT code changes.

Loads the synthetic test district (tests/fixtures/synthetic_district.yaml), runs
the same validation the production loader will run, asserts the same fields are
present, and confirms it can drive the same downstream code paths.

If this test ever needs a code change to pass for a new district, the
'open-source contributors can fork DayLight for their own district' promise is
broken. That's a serious bug.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures"

REQUIRED_DISTRICT_FIELDS = {
    "district_id",
    "state",
    "top_n_industries",
    "min_scored_votes_per_industry",
    "revolving_door_dollar_threshold",
    "federal_candidates",
}
REQUIRED_CANDIDATE_FIELDS = {
    "candidate_id",
    "opensecrets_id",
    "propublica_id",
    "name",
    "party_label_neutral",
    "office",
}


def _load_district(name: str) -> dict:
    import yaml
    with (FIXTURE_DIR / name).open() as f:
        return yaml.safe_load(f)


@pytest.fixture(params=["district_fl23.yaml", "synthetic_district.yaml"])
def any_district(request) -> dict:
    return _load_district(request.param)


def test_district_has_required_fields(any_district):
    missing = REQUIRED_DISTRICT_FIELDS - set(any_district.keys())
    assert not missing, f"District config missing fields: {missing}"


def test_top_n_is_positive_int(any_district):
    n = any_district["top_n_industries"]
    assert isinstance(n, int) and n > 0


def test_min_scored_votes_is_positive_int(any_district):
    m = any_district["min_scored_votes_per_industry"]
    assert isinstance(m, int) and m > 0


def test_revolving_door_threshold_is_positive_int(any_district):
    t = any_district["revolving_door_dollar_threshold"]
    assert isinstance(t, int) and t > 0


def test_federal_candidates_list_shape(any_district):
    assert isinstance(any_district["federal_candidates"], list)
    for cand in any_district["federal_candidates"]:
        missing = REQUIRED_CANDIDATE_FIELDS - set(cand.keys())
        assert not missing, f"Candidate {cand.get('candidate_id', '?')} missing: {missing}"


def test_party_label_is_neutral(any_district):
    """We deliberately do NOT store party. Bias-free by design."""
    allowed = {"incumbent", "challenger", "open-seat", "third-party-challenger"}
    for cand in any_district["federal_candidates"]:
        label = cand["party_label_neutral"]
        assert label in allowed, (
            f"party_label_neutral={label!r} not in {sorted(allowed)}. "
            "We do NOT store partisan labels in the candidate config."
        )


def test_state_is_two_letter_uppercase(any_district):
    s = any_district["state"]
    assert isinstance(s, str) and len(s) == 2 and s.isupper(), (
        f"state must be a 2-letter uppercase USPS code; got {s!r}"
    )


def test_district_id_format(any_district):
    """district_id is `<STATE>-<NUMBER>` so it's stable in URLs and DB keys."""
    did = any_district["district_id"]
    assert isinstance(did, str) and "-" in did, f"district_id format wrong: {did!r}"
    state_part, num_part = did.split("-", 1)
    assert state_part == any_district["state"], (
        f"district_id prefix ({state_part!r}) must match state ({any_district['state']!r})"
    )
    assert num_part.isdigit() or num_part.isalnum(), (
        f"district_id suffix must be alphanumeric; got {num_part!r}"
    )


def test_synthetic_district_drives_alignment_score_path():
    """Demonstrate that the synthetic district can flow through the same scoring code
    used for FL-23, with no code changes — only YAML."""
    from tests.methodology.alignment_score import compute_alignment_score

    district = _load_district("synthetic_district.yaml")

    # Minimal, deterministic inputs constructed from the district's config:
    industry_totals = {
        "Securities & Investment": 100_000.0,
        "Real Estate":              80_000.0,
        "Pro-Israel":               40_000.0,
        "Lawyers/Law Firms":         5_000.0,  # 4th — won't be top-3 anyway
    }
    bill_map = {
        "x1": {"industry": "Securities & Investment", "direction": 1},
        "x2": {"industry": "Securities & Investment", "direction": 1},
        "y1": {"industry": "Real Estate", "direction": 1},
        "y2": {"industry": "Real Estate", "direction": 1},
        "z1": {"industry": "Pro-Israel", "direction": 1},
        "z2": {"industry": "Pro-Israel", "direction": 1},
    }
    votes = [{"bill_id": b, "position": "Yes"} for b in bill_map]

    r = compute_alignment_score(
        industry_totals,
        bill_map,
        votes,
        top_n=district["top_n_industries"],
        min_scored_votes_per_industry=district["min_scored_votes_per_industry"],
    )
    assert r.score == 100, (
        "Synthetic district with all-aligned votes should yield 100. "
        "If this fails the district config didn't actually flow through the scoring path."
    )
