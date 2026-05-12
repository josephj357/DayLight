"""Shape contract tests for the FastAPI endpoints exposed by /src/api/.

We do NOT import /src/api/ here — at the time these tests were written that
package may not exist yet. Instead, we validate the response SHAPE that the API
must produce for FL-23, using a synthesized response built from the same fixtures
the real API will read. When /src/api/app.py exists, replace `_build_response()`
with a `TestClient(app).get(...)` call. The schema assertions remain the same.

The contract:
  GET /districts/FL-23 returns a JSON document with:
    - district_id (str)
    - state (str)
    - candidates (list of CandidatePublicView)
  Each CandidatePublicView has:
    - candidate_id (str)
    - name (str)
    - office (str)
    - donor_alignment_score (int, 0..100)
    - top_industries (list[Industry], length <= top_n)
    - excluded_industries (list[str])
    - data_as_of (ISO 8601 date)
    - methodology_url (str pointing to /docs/methodology.md anchor)
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pytest

from tests.methodology.alignment_score import compute_alignment_score

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures"

REQUIRED_DISTRICT_KEYS = {"district_id", "state", "candidates"}
REQUIRED_CANDIDATE_KEYS = {
    "candidate_id",
    "name",
    "office",
    "donor_alignment_score",
    "top_industries",
    "excluded_industries",
    "data_as_of",
    "methodology_url",
}
REQUIRED_INDUSTRY_KEYS = {"industry", "career_total", "weight", "a_i", "included"}


def _load(name: str):
    with (FIXTURE_DIR / name).open() as f:
        if name.endswith(".json"):
            return json.load(f)
        import yaml
        return yaml.safe_load(f)


def _build_response() -> dict:
    """Synthesize the response /api/districts/FL-23 must produce from the same fixtures."""
    fec = _load("fec_fl23_incumbent.json")
    pp = _load("propublica_fl23_votes.json")
    bim = _load("bill_industry_map.yaml")["bills"]
    district = _load("district_fl23.yaml")
    cand = district["federal_candidates"][0]

    result = compute_alignment_score(fec["industry_totals_career"], bim, pp["votes"])
    top_industries_payload = [
        {
            "industry": r.industry,
            "career_total": fec["industry_totals_career"][r.industry],
            "weight": r.weight,
            "a_i": r.a_i,
            "included": r.included,
        }
        for r in result.industries
    ]
    return {
        "district_id": district["district_id"],
        "state": district["state"],
        "candidates": [
            {
                "candidate_id": cand["candidate_id"],
                "name": cand["name"],
                "office": cand["office"],
                "donor_alignment_score": result.score,
                "top_industries": top_industries_payload,
                "excluded_industries": list(result.excluded_industries),
                "data_as_of": fec["_fixture_metadata"]["snapshot_date"],
                "methodology_url": "/docs/methodology.md#3-donor-alignment-score",
            }
        ],
    }


# ---------------------------------------------------------------------------

def test_district_response_has_required_keys():
    resp = _build_response()
    assert REQUIRED_DISTRICT_KEYS <= set(resp.keys())


def test_candidate_response_has_required_keys():
    resp = _build_response()
    for c in resp["candidates"]:
        missing = REQUIRED_CANDIDATE_KEYS - set(c.keys())
        assert not missing, f"Candidate {c.get('candidate_id')} missing keys: {missing}"


def test_score_is_int_in_range():
    resp = _build_response()
    for c in resp["candidates"]:
        s = c["donor_alignment_score"]
        assert isinstance(s, int), f"Score must be int, got {type(s).__name__}"
        assert 0 <= s <= 100, f"Score out of range: {s}"


def test_industry_entries_have_required_shape():
    resp = _build_response()
    for c in resp["candidates"]:
        for ind in c["top_industries"]:
            missing = REQUIRED_INDUSTRY_KEYS - set(ind.keys())
            assert not missing, f"Industry entry missing keys: {missing}"


def test_data_as_of_is_iso_date():
    resp = _build_response()
    for c in resp["candidates"]:
        # Should not raise.
        dt.date.fromisoformat(c["data_as_of"])


def test_methodology_url_points_to_docs():
    resp = _build_response()
    for c in resp["candidates"]:
        assert c["methodology_url"].startswith("/docs/methodology.md"), (
            f"methodology_url must point to /docs/methodology.md, got {c['methodology_url']!r}"
        )


def test_top_industries_is_a_list():
    resp = _build_response()
    for c in resp["candidates"]:
        assert isinstance(c["top_industries"], list)


def test_excluded_industries_is_a_list_of_strings():
    resp = _build_response()
    for c in resp["candidates"]:
        excluded = c["excluded_industries"]
        assert isinstance(excluded, list)
        assert all(isinstance(x, str) for x in excluded)


def test_fl23_response_is_jsonable():
    """The response must serialize to JSON cleanly (no Python-specific types leaking)."""
    resp = _build_response()
    s = json.dumps(resp)
    round_tripped = json.loads(s)
    assert round_tripped == resp
