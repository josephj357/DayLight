# Forking DayLight for your district

This is the *long* version of "fork it for your district." If you're a
developer who wants to make DayLight work for your community, this is the
guide for you. Plan on ~4-12 hours of focused work for a first-pass district
that mirrors what FL-23 ships out of the box, plus more if your state or
county requires custom scrapers.

## Before you start

Confirm these three things:

1. **You actually live in or know the district.** DayLight depends on local
   knowledge — which races appear on the ballot, which judicial groups are
   contested, what the local school-board layout looks like. Forking
   "blind" produces incomplete configs.

2. **Your jurisdiction's data is reachable.** Federal data is universal
   (FEC + Congress.gov). State data quality varies wildly. County data is
   often the bottleneck. Spend 30 minutes on your county Supervisor of
   Elections (or equivalent) website to confirm campaign-finance filings
   are downloadable.

3. **You're OK with the AGPL-3.0 license.** Any hosted version of your
   fork must be open-source under AGPL-3.0. See ADR-001 for the reasoning.

## The two paths

### Path A — Add a district to the central project

The friendliest path: open a PR against `josephj357/DayLight` with your
district's YAML and any state/county scrapers you wrote. The central
project becomes a multi-district hub.

Use this path when:
- Your district is in a state/county that doesn't have unique data
  pipeline needs.
- You're comfortable with the central project's neutrality contract and
  review cadence.

### Path B — Stand up your own hosted instance

You clone DayLight, configure it for your district, and host it
independently (yourdistrict.daylight.example, your-org.org/transparency,
whatever). Your fork can take its own brand and editorial choices.

Use this path when:
- Your district needs a custom data pipeline that isn't a fit for the
  central project (e.g., a unique state portal, foreign-language
  localization).
- You want to maintain it as part of an existing civic-tech org.

AGPL-3.0 applies either way: hosted modifications must be published.

## Step-by-step (either path)

### 1. Create the district config

```bash
cp config/districts/fl-23.yml config/districts/YOUR-DISTRICT.yml
```

Edit the file. The structure is documented inline in `fl-23.yml` and
`CONTRIBUTING.md`. The most important fields:

| Field | What to fill in |
|-------|-----------------|
| `id` | Lowercase hyphenated ID. `ca-12`, `tx-32`, `ny-14`. |
| `display_name` | Plain English. "California's 12th Congressional District." |
| `state`, `fips_state` | Two-letter and FIPS state code. |
| `snapshot_date` | Today's date. Update when you refresh. |
| `zip_codes` | The ZIPs in your district. Use [USPS lookup][usps] cross-referenced with [house.gov][hgov]. |
| `federal` | Your U.S. House race. Look up FEC and bioguide IDs in the linked sources. |
| `state` | Every state-legislature district that *overlaps* yours. |
| `county` | Every county/municipal office on the local ballot. |
| `judicial` | Every judicial race. Local judges are often the highest-value coverage. |
| `special` | Soil & Water, water management, library boards, mosquito control — these all show up. |

Mark anything you can't verify as `# TODO: verify`. Better to ship with
`TODO`s than with bad data.

[usps]: https://tools.usps.com/zip-code-lookup.htm
[hgov]: https://www.house.gov/representatives/find-your-representative

### 2. Confirm data sources

For each level (federal/state/county/judicial), confirm where the data lives
and update the `data_sources` block in the YAML.

- **Federal:** FEC + Congress.gov. Same for everyone.
- **State:** find your state's campaign-finance disclosure portal. Examples:
  Florida → FL Division of Elections. California → CalAccess. Texas → Texas
  Ethics Commission. About half of these have CSV exports; the rest require
  parsing HTML.
- **County/local:** your county Supervisor of Elections (or Clerk, or Board
  of Elections — varies). Quality varies dramatically.

If your state/county isn't covered by the existing scrapers in
`/src/ingestion/`, you'll need to write one. Use `fetch_florida_state.py`
as a structural template. Keep the function shape:

```python
def run(conn: sqlite3.Connection, district: DistrictConfig) -> int:
    """Returns rows written."""
```

### 3. Wire up `pipeline.py`

If you added a new scraper, register it in `INGESTION_STEPS` in
`src/ingestion/pipeline.py`. Order matters: candidate rows are created by
the FEC step first, so anything that joins to candidates must run after it.

### 4. Run the seed script

```bash
bash scripts/seed.sh --district YOUR-DISTRICT
```

This will:
1. Install Python deps.
2. Initialize SQLite at `data/daylight.db`.
3. Run every ingestion step for your district.
4. Start the FastAPI backend on port 8000.

In another terminal:

```bash
cd src/web && npm install && npm run dev
# Open http://localhost:3000
```

Enter a ZIP in your district. You should land on the district view with
every race populated.

### 5. Run the test suite

```bash
pytest tests/
```

The methodology tests run against frozen fixtures and should pass even with
no live data. The `test_district_config.py` integration test confirms your
new YAML is well-formed and the methodology produces a sane score.

If a methodology test fails on your district's data, that's a real signal
— either your data is malformed, or you've discovered an edge case the
methodology doesn't handle. Open an issue.

### 6. Iterate on the synthesis prompt

The AI synthesis card is the killer UX. Read `/src/ingestion/prompts/synthesis_prompt.md`
carefully. Test the output on three candidates from different parties and
confirm it reads identically in tone for all three.

If you find synthesis output that violates the neutrality contract, that's
a methodology issue, not a typo. Open an issue with `[Correction]` and the
example output before pushing changes.

## Cost ceiling

A bare-minimum hosted fork (one district, monthly ingestion refresh,
no traffic):

| Item | Monthly cost |
|------|--------------|
| Vercel free tier (frontend) | $0 |
| Fly.io / Render small instance (backend) | $5–$10 |
| Anthropic API for synthesis | $5–$30 |
| Domain | $1 amortized |
| **Total** | **$11–$41** |

At ~10,000 monthly visitors with cached synthesis, costs roughly double.

## Privacy and legal

DayLight surfaces public records. The FEC, your state, and your county
publish this data; DayLight just re-renders it. Three things to know:

1. **FEC contributor data may not be used to solicit donations or sold as a
   contributor list** (52 U.S.C. § 30111(a)(4)). DayLight's display
   complies; if you build something on top, make sure yours does too.

2. **Defamation law applies to your *characterization* of the data, not the
   data itself.** Methodology adherence is your shield — apply the same
   formulas, the same neutrality, the same disclosure to everyone. The
   methodology test suite enforces this.

3. **OpenSecrets bulk data is CC BY-NC-SA 3.0 US.** Attribute, don't use
   commercially without a separate agreement, share-alike. The schema
   isolates these columns; a future commercial deployment can drop them
   without losing the rest.

## What you don't have to do

- You don't need to host the data. SQLite is fine for a year+.
- You don't need to ingest history. Current cycle is enough.
- You don't need to cover every race on day one. Federal + one or two
  down-ballot races is a real shipping milestone. Add the rest over time.
- You don't need to write your own methodology. Use ours, or fork the
  methodology doc (it's CC BY-SA 4.0 — adapt freely).

## Getting help

Open an issue tagged `[Forking]` with your state, your district, and the
specific question. We'll try to point you at the right primary source or
the right existing scraper.
