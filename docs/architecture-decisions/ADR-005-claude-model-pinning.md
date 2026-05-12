# ADR-005 — Pin the Claude model used for synthesis

**Status:** Accepted
**Date:** 2026-05-12

## Context

DayLight's plain-English synthesis layer makes factual-adjacent claims
("Senator X says Y; their top donor benefits from Z; here's a vote where
they sided with the donor"). Two properties are non-negotiable:

1. **Reproducibility.** Two runs with the same inputs must produce
   functionally equivalent output. Methodology tests assert this.
2. **Political neutrality.** The model used must reliably follow the
   neutrality contract in the system prompt across both parties.

If the model floats freely with whatever Anthropic ships latest, every
upgrade is a potential silent regression on either property.

## Decision

Pin two specific models in `.env.example` and in `/src/ingestion/synthesize.py`:

- **`claude-sonnet-4-5`** for primary synthesis (the user-facing summary card).
- **`claude-haiku-4-5`** for cheap classification tasks (donor → industry
  tagging where the OpenSecrets bulk doesn't cover it).

A model change is an ADR-amending event, not a deploy event.

## Rationale

- **Test stability.** `tests/methodology/test_synthesis_neutrality.py` snapshots
  representative output. A model upgrade that subtly changes phrasing would
  silently break those tests; pinning makes the cause visible.
- **Cost predictability.** Sonnet pricing is stable; auto-upgrading to
  whatever Anthropic ships next could quietly multiply costs for forks.
- **The methodology document references model behavior.** When the
  methodology says "synthesis text never uses partisan loaded language,"
  that's a claim about a specific model under a specific system prompt.
  Pinning makes the claim testable.

## Consequences

- **Forks may diverge.** Some forks will pin newer models. That's fine — the
  methodology doc is the contract, and the test suite enforces it.
- **Model deprecation needs a migration plan.** When a pinned model hits
  end-of-life, the project needs an ADR-005 update + a re-snapshot of the
  neutrality test outputs against the new model + a maintainer-reviewed
  diff before merging.
- **The synthesis prompt template lives in source control.** It's at
  `/src/ingestion/prompts/synthesis_prompt.md` so changes are reviewable.

## Alternatives considered

- **Always use the latest Anthropic model.** Rejected. Silent behavioral
  drift is unacceptable for a project whose entire credibility rests on
  consistent treatment across parties.
- **Use a non-Anthropic model.** Out of scope for v1. Anthropic was chosen
  for its instruction-following on neutrality prompts. A future ADR could
  reconsider; the synthesis layer is intentionally swappable.
- **Don't pin — let operators choose at runtime.** Partially adopted. The
  `ANTHROPIC_MODEL` env var allows override, but the defaults are pinned
  and the methodology tests assert behavior against the pinned models.
