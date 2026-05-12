"""Validate that DayLight's donor-to-industry mappings align with OpenSecrets'
standard taxonomy.

Per /docs/methodology.md §2 we adopt OpenSecrets' taxonomy unmodified. The test
guards against three failure modes:

  1. An industry appears in our FEC rollup that isn't in OpenSecrets' code list.
  2. The "Retired" / "Self-Employed" buckets are NOT mixed into industry-concentration math.
  3. Industry code prefixes follow OpenSecrets' convention (single letter A-Z + 2 digits).
"""
from __future__ import annotations

import re


_CODE_RE = re.compile(r"^[A-Z]\d{2}$")


def test_all_industries_have_opensecrets_code(opensecrets_fixture):
    """Every industry row in the OpenSecrets fixture has a well-formed code."""
    for row in opensecrets_fixture["industries"]:
        code = row["industry_code"]
        assert _CODE_RE.match(code), f"Industry code {code!r} doesn't match OpenSecrets convention."


def test_fec_industries_are_subset_of_opensecrets(fec_fixture, opensecrets_fixture):
    """Industry names we emit must exist in OpenSecrets' taxonomy."""
    opensecrets_names = {row["industry_name"] for row in opensecrets_fixture["industries"]}
    fec_names = set(fec_fixture["industry_totals_career"].keys())
    extra = fec_names - opensecrets_names
    assert not extra, (
        f"DayLight emitted industry names not in OpenSecrets taxonomy: {sorted(extra)}. "
        "Add them to OpenSecrets-mapping config or fix the ingestion classifier."
    )


def test_non_industry_buckets_are_separated(fec_fixture):
    """`Retired` and `Self-Employed` must be present but classified separately.

    Per methodology §2, these are excluded from industry-concentration math so the
    UI doesn't show 'Retired' as if it were an industry.
    """
    industries = fec_fixture["industry_totals_career"]
    assert "Retired" in industries, "Expected 'Retired' bucket to be present for transparency."
    assert "Self-Employed" in industries, "Expected 'Self-Employed' bucket to be present for transparency."

    # The pipeline that produces the top-N must drop these — verified in alignment_score.top_n_industries.
    from tests.methodology.alignment_score import NON_INDUSTRY_BUCKETS, top_n_industries
    assert "Retired" in NON_INDUSTRY_BUCKETS
    assert "Self-Employed" in NON_INDUSTRY_BUCKETS
    top = top_n_industries(industries, n=10)
    for name, _ in top:
        assert name not in NON_INDUSTRY_BUCKETS, (
            f"top_n_industries leaked a non-industry bucket: {name}"
        )


def test_taxonomy_source_url_recorded(opensecrets_fixture):
    """The OpenSecrets snapshot must record the taxonomy version + source URL.

    This is required for the 'How was this computed?' link on every page.
    """
    assert opensecrets_fixture.get("industry_taxonomy_version")
    url = opensecrets_fixture.get("taxonomy_source_url", "")
    assert url.startswith("https://www.opensecrets.org/"), (
        f"Taxonomy source URL must point to OpenSecrets; got {url!r}"
    )


def test_industry_totals_internally_consistent(opensecrets_fixture):
    """For each industry row, indivs + pacs must equal career_total (within $1)."""
    for row in opensecrets_fixture["industries"]:
        s = row["indivs"] + row["pacs"]
        assert abs(s - row["career_total"]) <= 1.0, (
            f"Industry {row['industry_name']}: indivs+pacs={s} differs from career_total={row['career_total']}"
        )
