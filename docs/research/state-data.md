# DayLight — Florida State-Level Data Research

This document maps the Florida state-level layer for FL-23: the state House and state Senate districts that overlap the congressional district, the incumbents, where to pull their disclosed donors, and the considerable redistricting caveats that affect any analysis.

---

## 1. How Florida discloses state-legislative campaign finance

Florida campaign-finance disclosure for state-level offices (state House, state Senate, governor, cabinet, statewide judicial, Public Service Commission) is handled by the **Florida Department of State, Division of Elections**. The system has three relevant pieces:

| Piece | URL | What it covers |
|-------|-----|----------------|
| Campaign Finance Database (candidates and committees) | https://dos.elections.myflorida.com/campaign-finance/ | Contributions, expenditures, "other distributions" reported back to **1996**. ⚠ **Cloudflare-challenged 2026-05-12**: direct HTTP requests receive a JS challenge page, not the search form. Programmatic access requires either (a) headed Playwright + cookie-jar persistence or (b) a third-party redistributor. |
| Committee Database | https://dos.elections.myflorida.com/committees/ | PCs (political committees), CCEs (committees of continuous existence), ECOs (electioneering communications organizations) |
| Filing Campaign Reports | https://dos.fl.gov/elections/candidates-committees/campaign-finance/filing-campaign-reports/ | Reporting calendar and per-cycle filing schedules |

**Critical scope limitation**: the FL DoS database covers candidates for **multi-county office** — i.e. state House, state Senate, statewide office. It does **NOT** cover:

- U.S. House and U.S. Senate (use FEC)
- County office (county commission, school board, sheriff, clerk, property appraiser, supervisor of elections, etc. — use Broward SOE / VoterFocus)
- Municipal office (city commission, mayor — use the individual city's filing officer)

Source: https://dos.fl.gov/elections/candidates-committees/campaign-finance/campaign-finance-database/

### Data format / programmatic access

- **No documented REST API.** All access is via web query form.
- Query results are downloadable as a **tab-delimited text file** (easy to import as CSV).
- Update cadence: the database is described as "an accurate representation of reports filed" — some filings are submitted electronically (immediate), others are key-entered from paper (variable lag). No formal SLA.

### Alternative aggregators

- **The Accountability Project** (https://publicaccountability.org/datasets/40/fl_contribs/) — provides FL campaign contributions 1995-2023 (~27M records). Sourced from FL DoS. License `[TODO: verify redistribution rights]`.
- **FollowTheMoney.org** (https://www.followthemoney.org/our-data/apis) — National Institute on Money in Politics. Provides a free API after myFollowTheMoney signup. Current through 2024. License `[TODO: verify]`.
- **Transparency USA** (https://www.transparencyusa.org/fl) — also normalized; useful UI for state-level filings.

**2026-05-12 verification note**: We confirmed the FL DoS portal is Cloudflare-protected. Implementation should NOT assume direct HTTP works. See `/src/ingestion/fetch_florida_state.py` for the three viable paths (FollowTheMoney → Accountability Project bulk → headed Playwright as a last resort).

For DayLight v1, the **pragmatic recommendation** updated post-verification: **FollowTheMoney.org's free API is the most tractable starting point** — it's normalized FL DoS data without the Cloudflare hurdle. Cross-checks against FL DoS would require headed-browser machinery and aren't worth it for v1 scope.

---

## 2. Which state House and state Senate districts overlap FL-23 post-2022 redistricting?

This question has two layers and one large active caveat.

### Layer 1 — Congressional FL-23 boundaries (the 2022-effective map)

Under the map signed by Gov. DeSantis on April 22, 2022 (after he vetoed the legislature's first version on March 29, 2022; the legislature reconvened in special session and approved DeSantis's version April 20-21, 2022), **FL-23** includes:

- Boca Raton (Palm Beach County)
- Coral Springs, Parkland, most of Deerfield Beach, parts of Fort Lauderdale, parts of Pompano Beach (Broward County)
- Margate (Broward)

Source: https://en.wikipedia.org/wiki/Florida%27s_23rd_congressional_district (cross-checked against Ballotpedia: https://ballotpedia.org/Florida%27s_23rd_Congressional_District)

This was a successor (after 2020 redistricting) to the **prior FL-22**.

### Layer 2 — Overlapping state legislative districts

Based on the Broward County GIS maps (https://www.broward.org/Legislative/Documents/), the following state legislative districts touch the Broward portion of FL-23. Palm Beach County overlap (the Boca Raton portion) requires a separate cross-walk against Palm Beach County GIS.

**Florida State Senate (post-2022 plan, in effect for 2024 elections):**

| District | Incumbent (2024) | Notes |
|----------|------------------|-------|
| SD-30 | Sen. Tina Polsky (D) | District renumbered from prior SD-29 in 2022 cycle. Source: https://en.wikipedia.org/wiki/Tina_Polsky |
| SD-32 | Sen. Rosalind Osgood (D), Fort Lauderdale | Boundaries shifted south in 2022 redistricting. Source: https://www.flsenate.gov/Senators/s32 |
| SD-35 | Sen. Barbara Sharief (D) won general 2024-11-05 against Vincent Parlatore (R). Successor to Sen. Lauren Book (term-limited Nov 2024). Source: https://ballotpedia.org/Florida_State_Senate_District_35 |
| SD-37 | Sen. Jason Pizzo (D) — won general 2024-11-05 against Imtiaz Mohammad. Note Pizzo's district sits mostly in Miami-Dade with small Broward overlap. Source: https://ballotpedia.org/Florida_State_Senate_District_37 |

The Broward County GIS map lists Senate districts 30, 32, 35, and 37 as present in Broward.

**Florida State House (post-2022 plan, in effect for 2024 elections):**

Districts 93 through 103 substantially cover Broward. Verified incumbents (as of search results):

| District | Incumbent (2024) | Source |
|----------|------------------|--------|
| HD-96 | Rep. Christine Hunschofsky (D) — represented since 2020 | Ballotpedia |
| HD-97 | Rep. Dan Daley (D) — represented since 2019 special election | Ballotpedia |
| HD-98 | Rep. Patricia H. Williams (D) | Broward County legislative documents |
| HD-99 | Rep. Daryl Campbell (D) | Ballotpedia |
| HD-100 | Rep. Chip LaMarca (R) | Ballotpedia / Broward documents |
| HD-101 | Rep. Hillary Cassel (R as of party switch in 2024 — verify) `[TODO: verify current party affiliation; she switched parties in late 2024]` | Broward documents |
| HD-102 | Rep. Michael "Mike" Gottlieb (D) | Broward documents |
| HD-103 | Rep. Robin Bartleman (D) | Broward documents |

`[TODO: verify HD-93, HD-94, HD-95 — search did not return clean Broward-overlap-confirming results for these.]`

The list of which of these HDs **substantially overlap FL-23** vs only marginally touching it requires a shapefile intersect that DayLight should compute from:
- FL House plan `H000H8013`: https://www.flsenate.gov/PublishedContent/Session/Redistricting/Plans/H000H8013/Maps/30x40_Statewide_Map_H000H8013.pdf
- Broward GIS legislative maps: https://www.broward.org/Legislative/Documents/

---

## 3. Where to pull this data programmatically

Per (1) above, there is **no REST API** for FL Division of Elections campaign finance. The realistic pipeline:

```
For each state legislator in the FL-23 overlap set:
  1. Look up canonical name + filing committee at dos.elections.myflorida.com
  2. Submit query to https://dos.elections.myflorida.com/campaign-finance/contributions/
     with parameters for candidate, cycle, date range
  3. Download tab-delimited export
  4. Parse, dedupe, store
  5. Cross-check totals against FollowTheMoney.org API (Entity ID lookup)
```

The FL DoS query form's URL parameters are stable enough to script. `[TODO: verify the exact query-parameter schema by inspecting the form HTML at ingest time and capture as ADR.]`

### Recommended cadence

Weekly during active reporting periods; monthly otherwise. State filings come in waves around statutory reporting deadlines, so a poll-based scraper aligned with the FL filing calendar (https://dos.fl.gov/elections/candidates-committees/campaign-finance/filing-campaign-reports/) is the right shape.

---

## 4. The redistricting caveat (this is large and ongoing)

Florida is in the middle of an **active redistricting fight** as of May 2026, which has direct implications for any analysis of "who represents FL-23":

- **Congressional map**: On January 7, 2026, Gov. DeSantis called a special session to redraw the congressional map. The Florida Legislature passed a new map on April 29, 2026 (House 83-28, Senate 21-17, both largely party-line). DeSantis signed it. On **May 4, 2026**, the first lawsuit was filed alleging the map violates Florida's Fair Districts Amendment. Plaintiffs and DeSantis reportedly agree the new map breaks the FL Constitution in some respects but dispute whether it applies anyway in light of recent SCOTUS doctrine (Louisiana v. Callais).
- Sources:
  - https://en.wikipedia.org/wiki/2026_Florida_redistricting
  - https://floridaphoenix.com/2026/05/04/desantis-new-congressional-map-faces-first-legal-challenge/
  - https://www.npr.org/2026/04/29/nx-s1-5804703/florida-redistricting-voting-map-republicans-house-seats
  - https://floridaphoenix.com/2026/05/06/desantis-plaintiffs-agree-new-map-breaks-fl-constitution-does-it-apply-anyway/
- The 2026 redistricting is **congressional only**; state legislative maps remain on the 2022 plan. But the elimination of (or boundary shift around) what was Sheila Cherfilus-McCormick's FL-20 has knock-on effects for Broward representation more broadly.

**What DayLight should do**:

1. Pin every analysis to a specific district plan version (e.g. `"plan_id": "FL-CONG-2022-04-22"` or `"plan_id": "FL-CONG-2026-04-29"`).
2. Track which plan is currently in legal effect for each upcoming election and update prominently when courts rule.
3. For "who represents you" lookups, default to whatever plan is in effect for the **next** election, not the prior one — users want forward-looking information.
4. Add a banner / disclosure to any FL-23 page noting the live litigation when boundaries are unstable.

---

## 5. Disclosed donors — incumbent state-level overview

This section lists **starting points** for donor research on each FL-23-overlap incumbent. DayLight v1 must pull the actual numbers from FL DoS at ingest time; only the queryable identity is listed here.

| Office | Incumbent | FL DoS search start point |
|--------|-----------|---------------------------|
| FL Sen SD-30 | Tina Polsky | Search "Polsky, Tina" at dos.elections.myflorida.com/campaign-finance/contributions/ |
| FL Sen SD-32 | Rosalind Osgood | Search "Osgood, Rosalind" |
| FL Sen SD-35 | Barbara Sharief (incoming, won Nov 2024) | Search "Sharief, Barbara" |
| FL Sen SD-37 | Jason Pizzo | Search "Pizzo, Jason" |
| FL House HD-96 | Christine Hunschofsky | Search "Hunschofsky, Christine" |
| FL House HD-97 | Dan Daley | Search "Daley, Daniel" |
| FL House HD-98 | Patricia H. Williams | Search "Williams, Patricia" |
| FL House HD-99 | Daryl Campbell | Search "Campbell, Daryl" |
| FL House HD-100 | Chip LaMarca | Search "LaMarca, Chip" |
| FL House HD-101 | Hillary Cassel | Search "Cassel, Hillary" |
| FL House HD-102 | Michael "Mike" Gottlieb | Search "Gottlieb, Michael" |
| FL House HD-103 | Robin Bartleman | Search "Bartleman, Robin" |

Each of these candidates also typically has affiliated **PCs** (political committees) registered separately at https://dos.elections.myflorida.com/committees/. The candidate's direct campaign is the surface; the PC layer is where larger checks land. DayLight should ingest both layers and surface them as linked.

---

## 6. State-level financial disclosure (Form 6 / Form 1)

Beyond campaign finance, Florida requires **financial disclosure** of personal finances by state legislators (Form 6, the more comprehensive one) and many local officials (Form 1, less comprehensive).

- Filing system: https://disclosure.floridaethics.gov/PublicSearch/Filings (EFDMS — Electronic Financial Disclosure Management System)
- Form 6 instructions: https://disclosure.floridaethics.gov/2025/form/6/instructions/print
- This is **separate** from campaign finance — it discloses outside income, real-property holdings, liabilities, securities, etc.
- Useful for DayLight as a layer answering "what financial interests does this politician have outside their campaign account?" — particularly relevant for vote-vs-donor analysis when the legislator has personal business interests in a sector that lobbies them.

Moskowitz, during his time as a state legislator (2012-2019, Florida House District 97/96 successor districts) and as Director of FDEM (Florida Division of Emergency Management, 2019-2021), would have filed Form 6 annually. These historical filings are searchable in EFDMS. `[TODO: verify the EFDMS API status — no documented public API; expect HTML scraping required.]`

---

## 7. Open verification items

- `[TODO: verify]` Which HDs (93–103) **substantially** overlap FL-23 vs only graze it. Need shapefile intersect.
- `[TODO: verify]` Hillary Cassel's current party affiliation post any 2024 switch.
- `[TODO: verify]` HD-93, HD-94, HD-95 incumbents — search did not surface clean confirmations.
- `[TODO: verify]` Palm Beach County state-house districts that touch the Boca Raton portion of FL-23.
- `[TODO: verify]` FL DoS query-form URL parameter schema for stable scripting (capture in an ADR after first ingest).
- `[TODO: verify]` Whether the 2026 congressional map litigation moves to a stay or injunction that changes the effective plan before any DayLight-relevant election date.

---

## Sources

- Florida Division of Elections Campaign Finance: https://dos.fl.gov/elections/candidates-committees/campaign-finance/
- Campaign Finance Database (contributions): https://dos.elections.myflorida.com/campaign-finance/contributions/
- Committee Database: https://dos.elections.myflorida.com/committees/
- Florida Senate redistricting: https://www.flsenate.gov/Session/Redistricting
- FL House plan H000H8013: https://www.flsenate.gov/PublishedContent/Session/Redistricting/Plans/H000H8013/Maps/30x40_Statewide_Map_H000H8013.pdf
- Broward County GIS legislative maps: https://www.broward.org/Legislative/Documents/
- FL Senator profiles: https://www.flsenate.gov/Senators/
- 2026 Florida redistricting: https://en.wikipedia.org/wiki/2026_Florida_redistricting
- First lawsuit on 2026 map: https://floridaphoenix.com/2026/05/04/desantis-new-congressional-map-faces-first-legal-challenge/
- Florida Phoenix on constitutional question: https://floridaphoenix.com/2026/05/06/desantis-plaintiffs-agree-new-map-breaks-fl-constitution-does-it-apply-anyway/
- Florida Commission on Ethics EFDMS: https://disclosure.floridaethics.gov/PublicSearch/Filings
- FollowTheMoney APIs: https://www.followthemoney.org/our-data/apis
- The Accountability Project FL dataset: https://publicaccountability.org/datasets/40/fl_contribs/
