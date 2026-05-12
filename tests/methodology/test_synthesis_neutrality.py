"""Assert that AI synthesis output does NOT contain partisan loaded language.

Red-flag terms are maintained in tests/methodology/red_flags.json. The match policy
is case-insensitive, whole-word. A term wrapped in attributed quotation may be
exempted in a future iteration — see red_flags.json `_exceptions` field — but the
current default test runs on raw synthesis text WITHOUT exemptions to keep the bar
high. If a synthesis is genuinely quoting a primary source, that flow goes through
a different output path that isn't subjected to this filter.
"""
from __future__ import annotations

import re
from typing import Iterable

import pytest


def _compile_pattern(terms: Iterable[str]) -> re.Pattern[str]:
    # Escape and join with alternation. Use \b at start; require either word
    # boundary or end-of-string at end so multi-word terms ("deep state") work.
    parts = [r"\b" + re.escape(t) + r"(?=\b|$)" for t in terms]
    return re.compile("|".join(parts), re.IGNORECASE)


def _find_violations(text: str, terms: list[str]) -> list[str]:
    pattern = _compile_pattern(terms)
    return [m.group(0) for m in pattern.finditer(text)]


# ---------------------------------------------------------------------------
# Red-flag list integrity
# ---------------------------------------------------------------------------

def test_red_flag_list_is_nonempty(red_flags):
    assert isinstance(red_flags["terms"], list)
    assert len(red_flags["terms"]) >= 20, (
        "Red-flag list looks suspiciously short — keep coverage broad across the political spectrum."
    )


def test_red_flag_list_includes_required_canonical_terms(red_flags):
    """The terms explicitly mentioned in the project brief MUST be present."""
    required = {"radical", "extreme", "MAGA", "woke", "socialist", "fascist", "communist"}
    present = {t.lower() for t in red_flags["terms"]}
    missing = required - present
    assert not missing, f"Required canonical red-flag terms missing: {sorted(missing)}"


def test_red_flag_list_balanced_across_ideological_directions(red_flags):
    """Sanity check: the list must flag loaded language from across the political spectrum.

    Operationalized as: at least one term commonly used as a right-wing slur AND at
    least one term commonly used as a left-wing slur are present.
    """
    terms_lc = {t.lower() for t in red_flags["terms"]}
    right_leaning_slurs = {"libtard", "snowflake", "groomer", "thug"}
    left_leaning_slurs = {"maga", "fascist", "nazi"}
    assert right_leaning_slurs & terms_lc, (
        "Red-flag list lacks any term commonly used as a right-wing slur — "
        "violates the symmetry commitment."
    )
    assert left_leaning_slurs & terms_lc, (
        "Red-flag list lacks any term commonly used as a left-wing slur — "
        "violates the symmetry commitment."
    )


# ---------------------------------------------------------------------------
# Compliant outputs must pass
# ---------------------------------------------------------------------------

def test_all_compliant_outputs_pass(synthesis_outputs, red_flags):
    terms = red_flags["terms"]
    failures: list[tuple[str, list[str]]] = []
    for text in synthesis_outputs["compliant"]:
        hits = _find_violations(text, terms)
        if hits:
            failures.append((text, hits))
    assert not failures, (
        "Compliant fixture outputs unexpectedly tripped the red-flag filter:\n"
        + "\n".join(f"  text={t!r}\n  hits={h}" for t, h in failures)
    )


# ---------------------------------------------------------------------------
# Non-compliant outputs MUST be caught (proves the test isn't vacuously passing)
# ---------------------------------------------------------------------------

def test_every_noncompliant_output_is_caught(synthesis_outputs, red_flags):
    terms = red_flags["terms"]
    misses: list[str] = []
    for text in synthesis_outputs["noncompliant"]:
        hits = _find_violations(text, terms)
        if not hits:
            misses.append(text)
    assert not misses, (
        "Non-compliant fixture outputs slipped past the red-flag filter — "
        "filter is broken or list is incomplete:\n" + "\n".join(f"  {m!r}" for m in misses)
    )


# ---------------------------------------------------------------------------
# Parametric: every individual noncompliant string is rejected
# ---------------------------------------------------------------------------

@pytest.fixture
def noncompliant_examples(synthesis_outputs):
    return list(synthesis_outputs["noncompliant"])


def test_each_noncompliant_example_individually(noncompliant_examples, red_flags):
    terms = red_flags["terms"]
    for text in noncompliant_examples:
        hits = _find_violations(text, terms)
        assert hits, f"Expected red-flag hits in: {text!r}"


# ---------------------------------------------------------------------------
# Whole-word matching: 'extreme' must not flag 'extremely' (we want to catch the
# editorial use, not the adverb in 'extremely close vote'). This is a known
# tension we accept; the test documents the choice.
# ---------------------------------------------------------------------------

def test_whole_word_matching_does_not_flag_extremely(red_flags):
    """'extremely' is a legitimate adverb; we deliberately allow it."""
    terms = red_flags["terms"]
    sample = "The vote was extremely close, decided by a 217-216 margin."
    hits = _find_violations(sample, terms)
    assert not hits, (
        f"Whole-word matching should not flag 'extremely' as 'extreme'; got {hits}"
    )


def test_whole_word_matching_flags_bare_extreme(red_flags):
    """But the editorial 'extreme' on its own SHOULD be flagged."""
    terms = red_flags["terms"]
    sample = "Took an extreme position on immigration."
    hits = _find_violations(sample, terms)
    assert any(h.lower() == "extreme" for h in hits), (
        f"Bare 'extreme' should be flagged; got {hits}"
    )


def test_attribution_is_documented_not_implemented(red_flags):
    """Documentation guardrail: the exemption mechanism is acknowledged but NOT yet
    implemented. The point of this test is to FAIL LOUDLY if a future contributor
    silently turns on attribution-bypass without updating the methodology doc.
    """
    exceptions = red_flags.get("_exceptions", [])
    assert exceptions, "Missing _exceptions documentation in red_flags.json"
    joined = " ".join(exceptions).lower()
    assert "WITHOUT exemptions".lower() in joined, (
        "red_flags.json `_exceptions` must explicitly state that the current "
        "default runs WITHOUT exemptions. Update both file and methodology if changing."
    )
