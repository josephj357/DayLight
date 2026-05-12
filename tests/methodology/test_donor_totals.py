"""Validate that DayLight's calculated career donor totals match OpenSecrets
published totals within tolerance, for FL-23 candidates.

Tolerance policy (per /docs/methodology.md §1, §7):
    abs(daylight - opensecrets) <= max($1,000, 0.5% of opensecrets total)

Rationale:
    OpenSecrets refreshes on its own cadence (2-4 weeks). Our FEC ingestion may be
    a few days ahead or behind. A flat $1,000 floor covers rounding and late-itemized
    contributions; the 0.5% ceiling scales for large career totals where $1,000 is
    less than the natural reporting noise.

Tests run against FROZEN JSON fixtures, never live APIs.
"""
from __future__ import annotations

import pytest


ABSOLUTE_TOLERANCE_USD = 1000.0
RELATIVE_TOLERANCE = 0.005  # 0.5%


def _tolerance(reference_total: float) -> float:
    return max(ABSOLUTE_TOLERANCE_USD, reference_total * RELATIVE_TOLERANCE)


def test_industry_career_totals_match_opensecrets(fec_fixture, opensecrets_fixture):
    """Every industry rollup in our FEC-derived totals matches OpenSecrets within tolerance."""
    daylight_industry_totals = fec_fixture["industry_totals_career"]
    opensecrets_by_industry = {
        row["industry_name"]: row["career_total"]
        for row in opensecrets_fixture["industries"]
    }

    mismatches: list[tuple[str, float, float, float]] = []
    for industry, opensecrets_total in opensecrets_by_industry.items():
        assert industry in daylight_industry_totals, (
            f"DayLight is missing industry {industry!r} present in OpenSecrets fixture."
        )
        daylight_total = daylight_industry_totals[industry]
        tol = _tolerance(opensecrets_total)
        if abs(daylight_total - opensecrets_total) > tol:
            mismatches.append((industry, daylight_total, opensecrets_total, tol))

    assert not mismatches, (
        "Industry totals exceed tolerance against OpenSecrets:\n"
        + "\n".join(
            f"  {ind}: daylight={d:.2f} opensecrets={o:.2f} tol={t:.2f}"
            for ind, d, o, t in mismatches
        )
    )


def test_career_total_matches_opensecrets(fec_fixture, opensecrets_fixture):
    """Sum of itemized contributions matches OpenSecrets career total within tolerance."""
    daylight_total = fec_fixture["career_totals"]["career_individual_itemized"]
    opensecrets_total = opensecrets_fixture["career_total_individual_itemized"]
    tol = _tolerance(opensecrets_total)
    assert abs(daylight_total - opensecrets_total) <= tol, (
        f"Career itemized totals diverge: daylight={daylight_total:.2f} "
        f"opensecrets={opensecrets_total:.2f} tol={tol:.2f}"
    )


def test_no_negative_industry_totals(fec_fixture):
    """Negative dollar totals indicate a sign error in the ingestion pipeline."""
    for industry, amount in fec_fixture["industry_totals_career"].items():
        assert amount >= 0, f"Industry {industry!r} has negative total {amount}"


def test_top_contributors_sum_does_not_exceed_career_total(fec_fixture):
    """Top contributor employer rollup must not exceed the candidate's itemized total."""
    top_sum = sum(row["amount"] for row in fec_fixture["top_contributors_by_employer"])
    career = fec_fixture["career_totals"]["career_individual_itemized"]
    assert top_sum <= career, (
        f"Top contributors sum ({top_sum:.2f}) exceeds career itemized total ({career:.2f}); "
        "ingestion likely double-counted committee-to-committee transfers."
    )


@pytest.mark.parametrize("industry_name", [
    "Lawyers/Law Firms",
    "Securities & Investment",
    "Pro-Israel",
    "Real Estate",
    "Health Professionals",
])
def test_critical_industries_present(fec_fixture, industry_name):
    """The top-5 industries we display on FL-23 incumbent's page must exist in our data."""
    assert industry_name in fec_fixture["industry_totals_career"], (
        f"Top-displayed industry {industry_name!r} missing from FEC-derived totals."
    )
