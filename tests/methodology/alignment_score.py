"""Pure-Python reference implementation of the Donor Alignment Score (methodology §3).

This implementation lives in /tests/methodology/ (not /src/) because the tester
agent is forbidden from writing under /src/. It serves two roles:

1. The arithmetic specification of the score as documented in /docs/methodology.md.
2. The oracle that /src/ must match. When backend-dev implements the real scorer in
   /src/scoring/, this module's outputs are the regression target.

NOTHING here is random. Same inputs → same output, byte-for-byte.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


_POSITION_TO_CAST = {
    "Yes": 1,
    "Aye": 1,
    "No": -1,
    "Nay": -1,
    "Not Voting": 0,
    "Present": 0,
}


# Industries that represent "no employer information" — methodology §2 excludes them
# from industry-concentration math.
NON_INDUSTRY_BUCKETS = {"Retired", "Self-Employed"}


@dataclass(frozen=True)
class IndustryAlignment:
    industry: str
    weight: float                # w_i after re-normalization, or pre-norm if undefined
    raw_weight: float            # w_i before re-normalization
    n_scored_votes: int
    n_non_abstain: int
    a_i: float | None            # None if insufficient votes
    included: bool


@dataclass(frozen=True)
class AlignmentScoreResult:
    score: int                   # 0-100
    A: float                     # -1 .. +1
    industries: tuple[IndustryAlignment, ...]
    excluded_industries: tuple[str, ...]


def _cast_for_position(position: str) -> int:
    if position not in _POSITION_TO_CAST:
        raise ValueError(f"Unknown ProPublica position value: {position!r}")
    return _POSITION_TO_CAST[position]


def top_n_industries(
    industry_totals_career: Mapping[str, float],
    n: int = 5,
    drop_buckets: Iterable[str] = NON_INDUSTRY_BUCKETS,
) -> list[tuple[str, float]]:
    """Return the top N industries by career dollars, deterministically sorted.

    Ties are broken by industry name (ascending) so the same fixtures always yield
    the same ordering.
    """
    drop = set(drop_buckets)
    items = [(name, amount) for name, amount in industry_totals_career.items() if name not in drop]
    items.sort(key=lambda kv: (-kv[1], kv[0]))
    return items[:n]


def compute_alignment_score(
    industry_totals_career: Mapping[str, float],
    bill_industry_map: Mapping[str, Mapping[str, object]],
    votes: Iterable[Mapping[str, object]],
    *,
    top_n: int = 5,
    min_scored_votes_per_industry: int = 3,
) -> AlignmentScoreResult:
    """Compute the Donor Alignment Score per /docs/methodology.md §3.

    Parameters
    ----------
    industry_totals_career
        Mapping of industry name -> career dollar total. Source: OpenSecrets industry
        rollup (see fixtures/opensecrets_fl23_incumbent.json).
    bill_industry_map
        Mapping of bill_id -> {"industry": str, "direction": +1 or -1, ...}. Source:
        /config/bill_industry_map.yaml.
    votes
        Iterable of vote records with keys 'bill_id' and 'position'. Source:
        ProPublica Congress API.
    top_n
        Top-N industries to include. Default 5 (methodology §3.1).
    min_scored_votes_per_industry
        Minimum non-abstaining votes required to include an industry. Default 3
        (methodology §3.2).
    """
    top = top_n_industries(industry_totals_career, n=top_n)
    if not top:
        raise ValueError("No industries available after dropping non-industry buckets.")

    d_total = sum(amount for _, amount in top)
    raw_weights = {name: amount / d_total for name, amount in top}

    # Group votes by industry via the bill map.
    votes_by_industry: dict[str, list[int]] = {name: [] for name, _ in top}
    for vote in votes:
        bill_id = vote["bill_id"]
        if bill_id not in bill_industry_map:
            continue
        entry = bill_industry_map[bill_id]
        industry = entry["industry"]
        if industry not in votes_by_industry:
            continue
        direction = int(entry["direction"])
        cast = _cast_for_position(vote["position"])
        agreement = direction * cast  # +1, -1, or 0
        votes_by_industry[industry].append(agreement)

    industry_results: list[IndustryAlignment] = []
    excluded: list[str] = []

    for name, _ in top:
        agreements = votes_by_industry.get(name, [])
        non_abstain = [a for a in agreements if a != 0]
        if len(non_abstain) < min_scored_votes_per_industry:
            industry_results.append(
                IndustryAlignment(
                    industry=name,
                    weight=0.0,
                    raw_weight=raw_weights[name],
                    n_scored_votes=len(agreements),
                    n_non_abstain=len(non_abstain),
                    a_i=None,
                    included=False,
                )
            )
            excluded.append(name)
        else:
            a_i = sum(non_abstain) / len(non_abstain)
            industry_results.append(
                IndustryAlignment(
                    industry=name,
                    weight=raw_weights[name],   # will re-normalize below
                    raw_weight=raw_weights[name],
                    n_scored_votes=len(agreements),
                    n_non_abstain=len(non_abstain),
                    a_i=a_i,
                    included=True,
                )
            )

    included = [r for r in industry_results if r.included]
    if not included:
        # No industry had enough scored votes — alignment is undefined; document a
        # neutral 50 with empty result set rather than raising, so the UI can show
        # "insufficient data" gracefully.
        return AlignmentScoreResult(score=50, A=0.0, industries=tuple(industry_results), excluded_industries=tuple(excluded))

    sum_raw = sum(r.raw_weight for r in included)
    renormalized: list[IndustryAlignment] = []
    for r in industry_results:
        if not r.included:
            renormalized.append(r)
            continue
        renormalized.append(
            IndustryAlignment(
                industry=r.industry,
                weight=r.raw_weight / sum_raw,
                raw_weight=r.raw_weight,
                n_scored_votes=r.n_scored_votes,
                n_non_abstain=r.n_non_abstain,
                a_i=r.a_i,
                included=True,
            )
        )

    A = sum(r.weight * (r.a_i or 0.0) for r in renormalized if r.included)
    score = round((A + 1.0) * 50.0)

    return AlignmentScoreResult(
        score=score,
        A=A,
        industries=tuple(renormalized),
        excluded_industries=tuple(excluded),
    )
