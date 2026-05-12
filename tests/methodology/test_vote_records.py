"""Validate that sampled congressional votes in our pipeline match ProPublica records exactly.

Unlike donor totals (which have a tolerance), vote positions are categorical and must match
EXACTLY. A wrong vote is a factual error that has no rounding excuse.

Tests run against FROZEN JSON fixtures.
"""
from __future__ import annotations

import pytest

VALID_POSITIONS = {"Yes", "Aye", "No", "Nay", "Not Voting", "Present"}


def test_every_vote_has_required_fields(propublica_fixture):
    required = {"bill_id", "roll_call", "position", "date"}
    for v in propublica_fixture["votes"]:
        missing = required - set(v.keys())
        assert not missing, f"Vote {v.get('bill_id', '?')} missing fields: {missing}"


def test_every_position_is_valid_value(propublica_fixture):
    """Position must be one of the ProPublica documented categorical values."""
    for v in propublica_fixture["votes"]:
        assert v["position"] in VALID_POSITIONS, (
            f"Vote {v['bill_id']} has invalid position {v['position']!r}; "
            f"must be one of {sorted(VALID_POSITIONS)}"
        )


def test_no_duplicate_roll_calls(propublica_fixture):
    """Two records for the same roll call would corrupt alignment math."""
    seen: set[int] = set()
    dups: list[int] = []
    for v in propublica_fixture["votes"]:
        rc = v["roll_call"]
        if rc in seen:
            dups.append(rc)
        seen.add(rc)
    assert not dups, f"Duplicate roll_call entries: {dups}"


def test_no_duplicate_bill_ids(propublica_fixture):
    """Same bill cited twice means we'd double-weight it in the score."""
    seen: set[str] = set()
    dups: list[str] = []
    for v in propublica_fixture["votes"]:
        if v["bill_id"] in seen:
            dups.append(v["bill_id"])
        seen.add(v["bill_id"])
    assert not dups, f"Duplicate bill_id entries: {dups}"


def test_dates_are_iso_format(propublica_fixture):
    import datetime as _dt
    for v in propublica_fixture["votes"]:
        try:
            _dt.date.fromisoformat(v["date"])
        except ValueError as exc:
            pytest.fail(f"Vote {v['bill_id']} has non-ISO date {v['date']!r}: {exc}")


@pytest.mark.parametrize(
    "bill_id,expected_position",
    [
        ("hr1234-118", "Yes"),
        ("hr3456-118", "No"),
        ("hr1213-118", "No"),
        ("hr1718-118", "Yes"),
    ],
)
def test_known_votes_match_propublica_exactly(propublica_fixture, bill_id, expected_position):
    """Spot-check that specific votes match the upstream record exactly.

    In production, the parametrize list would be expanded with every roll call we
    cite on the public site. Fixture-based version uses the synthetic record we froze.
    """
    found = next((v for v in propublica_fixture["votes"] if v["bill_id"] == bill_id), None)
    assert found is not None, f"Bill {bill_id} not in fixture; refresh required."
    assert found["position"] == expected_position, (
        f"Bill {bill_id}: fixture says {found['position']!r}, expected {expected_position!r}"
    )


def test_every_scored_vote_maps_to_a_known_industry(propublica_fixture, bill_industry_map):
    """A vote we display cannot reference an industry the bill map doesn't define."""
    bills = bill_industry_map["bills"]
    for v in propublica_fixture["votes"]:
        if v["bill_id"] not in bills:
            # Not every fetched vote needs to be in the scored map, but if industry_tags
            # claims an industry, the bill map must agree.
            continue
        mapped_industry = bills[v["bill_id"]]["industry"]
        tagged = v.get("industry_tags", [])
        assert mapped_industry in tagged, (
            f"Bill {v['bill_id']}: map says {mapped_industry!r}, ProPublica tags say {tagged!r}"
        )
