# Contributing to DayLight

Thanks for being here. A few things to get oriented before you open a PR.

## What this project is, what it isn't

DayLight is a **gift**, not a venture. There's no funding round, no roadmap meeting, no product team. The original author (Joshua) built v1 because he wanted it to exist for his own district and decided other people might want the same thing for theirs. Maintenance is **community-driven**.

What that means in practice:

- Pull requests are welcome and read carefully, but there's no SLA on review time.
- "It would be great if DayLight did X" is a fine thing to file as an issue; whether X happens depends on whether someone (you?) builds it.
- The friendliest, highest-impact contribution is almost always **adding a new district**.
- If you want to take a larger stewardship role, see "Becoming a maintainer" below.

## How to add a new district

A district in DayLight is one YAML file in `/config/districts/`. The reference is `/config/districts/fl-23.yml`. Copy it, rename it, and edit.

```yaml
# /config/districts/your-district.yml

# A short, stable identifier. Lowercase, hyphenated.
id: ny-14

# Human-readable name shown in the UI.
name: "New York's 14th Congressional District"

# Geographic and jurisdictional info used by the data layer.
state: NY
fips_state: "36"
counties:
  - bronx
  - queens

# The federal seat anchoring this district view.
federal:
  house_district: "NY-14"
  fec_candidate_search:
    state: NY
    district: "14"

# State-level offices that appear on the ballot for voters in this district.
# Each entry tells the scraper which state portal to hit and how to filter.
state_offices:
  - office: state_senate
    districts: ["10", "13"]
    source: nysenate
  - office: state_assembly
    districts: ["34", "36", "37", "39"]
    source: nyassembly

# County and municipal races. These are the ones nobody else covers well.
local_offices:
  - office: city_council
    source: nyc_campaign_finance_board
  - office: borough_president
    source: nyc_campaign_finance_board
  - office: district_attorney
    source: nyc_campaign_finance_board

# Judges and special districts.
judicial:
  - office: civil_court_judge
    source: nyc_board_of_elections

# Optional. If your jurisdiction has a non-obvious public-records portal,
# document it here so future maintainers can find it.
notes: |
  NYC has a public matching-funds program that adds an extra disclosure
  layer (NYC Campaign Finance Board). Their CSV exports are reliable.
```

After saving the file:

1. Run `bash scripts/seed.sh --district ny-14` to fetch and ingest the data.
2. Run `npm test -- --district ny-14` to confirm the ingestion produced sensible output (donor totals add up, no orphan records).
3. Visit `http://localhost:3000/d/ny-14` to eyeball the result.

If the scrapers in `/src/ingestion/` (specifically `fetch_florida_state.py` and `fetch_broward_local.py`) don't cover your state or county, you'll need to write one. Those two files are intentionally minimal stubs that lock in the function shape — they're the templates to copy.

## Political neutrality contract

DayLight applies identical scrutiny to all parties. **This is the non-negotiable part of contributing.**

PRs will be rejected — regardless of which side they advocate for — if they:

- Introduce partisan framing in labels, summaries, or UI copy ("the corrupt X party," "the reform-minded Y party," etc.).
- Apply different thresholds, prompts, or visual treatments to politicians of different parties.
- Add or weight data sources that are themselves partisan without disclosure.
- Use the AI synthesis layer to characterize one party's behavior in language not also applied to the other.
- Use issues, PRs, or commit messages as a venue for political advocacy.

The neutrality contract is enforced by review, not by automation. Reviewers will ask "would I be comfortable if this exact change were made about the other party?" If the answer is no, the change doesn't ship.

## How to challenge a factual claim

If you believe DayLight is showing something inaccurate about a specific politician, donor, or race, that's a **separate process** from a feature PR.

1. Open a GitHub issue with the prefix `[Correction]` in the title.
2. State what DayLight currently shows, what you believe is correct, and why.
3. Cite sources. Primary sources (FEC filings, state disclosures, court records, official statements) carry more weight than secondary reporting.
4. The maintainer (or a community maintainer) reviews the claim against [`/docs/methodology.md`](./docs/methodology.md) and either:
   - Issues a correction (data fix, methodology fix, or both), or
   - Explains why the existing display is consistent with the methodology and closes the issue.

If a correction reveals a systemic methodology problem — not just a single bad record — the fix lands as a documented methodology update, not a silent edit.

## PR process

**Branch naming:** `feat/short-description`, `fix/short-description`, `district/state-code-number`, or `docs/short-description`.

**Commit messages:** [Conventional Commits](https://www.conventionalcommits.org/). Examples:

```
feat(districts): add NY-14 configuration
fix(ingest): handle FEC pagination on large filings
docs(methodology): clarify industry classification for crypto
```

**What must pass before a PR can merge:**

- `npm run lint` clean
- `npm test` green
- `npm run build` succeeds
- For ingestion changes: a sample run against a fixture in `/tests/fixtures/`
- For methodology changes: a new or updated test in `/tests/methodology/`

**PR description template:**

- What does this change?
- Why?
- If this changes user-visible output, paste a before/after screenshot or sample.
- If this changes the methodology, link to the methodology section affected.
- Confirm: "I've read and agree to the political-neutrality contract."

## Code style

- **TypeScript** — strict mode, no `any` without a comment explaining why.
- **Python** — PEP 8, formatted with `black`, linted with `ruff`.
- **Imports** — sorted and grouped (stdlib, third-party, first-party).
- **File size** — keep files under ~500 lines. Split when they grow.
- **Comments** — explain *why*, not *what*. The code already says what.
- **No dead code** — if a function isn't called, delete it.

## Testing requirements

Anything that touches the methodology — donor aggregation, industry classification, contradiction detection, AI prompts — requires a test. Cosmetic or pure-UI changes do not.

See [`/tests/README.md`](./tests/README.md) for the test layout and conventions.

A few specifics:

- **Fixtures over live data.** Tests use snapshots in `/tests/fixtures/`, not live FEC calls.
- **Determinism.** AI-synthesis tests pin a seed and a model version. If you change the prompt, you'll need to regenerate the snapshot and explain why.
- **No politician-specific assertions.** Tests should validate the methodology, not the conclusion about a specific person. ("Top donors are ordered by amount descending" is fine. "Politician X's top donor is Y" is not — it's brittle and ages badly.)

## Becoming a maintainer

The author is not actively maintaining DayLight. If you want to take on a larger stewardship role — triaging issues, reviewing PRs, planning the next version — please open an issue tagged `[Maintainer Application]`.

A useful application includes:

- A little about who you are and what draws you to this kind of work.
- How much time you can realistically commit.
- Whether you're proposing to maintain the central project, a regional fork, or a specific subsystem (ingestion, methodology, frontend).
- Anything you've already shipped — open-source, journalism, civic tech — that's relevant.

There's no test, no interview loop. The author reviews, asks a few questions, and if it's a fit, hands over the keys.

## Thank you

Seriously. The thing that turns a one-person gift into a useful public good is other people showing up. If you're here, you're the reason this might end up mattering.
