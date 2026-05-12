# DayLight — Data Sources

Comprehensive map of every public data source required to populate the v1 database for FL-23 and its down-ballot stack (Broward County, FL).

**Scope of v1**: U.S. Rep. Jared Moskowitz (FL-23), the Florida state House and state Senate districts overlapping FL-23, Broward County Commission, Broward County School Board, 17th Judicial Circuit and Broward County Court judges, Broward Soil & Water Conservation District.

**Methodology note**: Every entry below was verified against the source's own public documentation or against credible journalism as of May 2026. Where a value could not be verified, it is marked `[TODO: verify]` rather than guessed. Two formerly central sources (ProPublica Congress API, OpenSecrets API) have been discontinued and are flagged in the gotchas column.

---

## Master table

| # | Source | URL | Access | Auth / rate limit | Format | Freshness / lag | Sample query for FL-23 | Gotchas / limitations |
|---|--------|-----|--------|-------------------|--------|-----------------|------------------------|------------------------|
| 1 | **openFEC API** (Federal Election Commission) | https://api.open.fec.gov/developers/ | Free, public-domain data | API key via api.data.gov. **DEMO_KEY** allowed for testing; signup gives **1,000 req/hour**; emailing `apiinfo@fec.gov` can raise to **7,200 req/hour (120/min)** | JSON | Filings indexed within ~24h of receipt; responses cached up to **1 hour** by API Umbrella (`Cache-Control: max-age=3600`) — data may be stale until the nightly materialized-view refresh | Candidate `H2FL22171` (Moskowitz) → `/v1/candidate/H2FL22171/`; principal committee `C00807628` → `/v1/committee/C00807628/`; itemized receipts → `/v1/schedules/schedule_a/?committee_id=C00807628` | Cache-Control means data can lag up to ~1h on top of the daily refresh. No commercial use of contributor lists (federal restriction at 52 U.S.C. § 30111(a)(4)). |
| 2 | **FEC bulk data** | https://www.fec.gov/data/browse-data/ | Free, public-domain | None required | CSV (pipe-delimited) inside .zip; raw `.fec` filings also available | Updated daily-to-weekly | Download `indiv24.zip` (Schedule A individual contributions 2023-24) and filter by committee `C00807628` | Files are very large (multi-GB for 2-year cycle). Schema docs at fec.gov/campaign-finance-data/contributions-individuals-file-description/. Use bulk for backfill, API for live. |
| 3 | **Congress.gov API** (Library of Congress) | https://api.congress.gov/ | Free | API key via api.data.gov; **5,000 req/hour** | JSON, XML | Updated continuously; House Roll Call Votes endpoint is in **beta** as of May 2025 release, covers votes from 118th Congress (2023) forward | `/v3/member/M001257` for Moskowitz; `/v3/house-vote/{congress}/{session}/{voteNumber}/members` for individual member votes | This is the **replacement** for the discontinued ProPublica Congress API (see row 4). House vote endpoints are still beta — schema may change. Senate roll-call votes are not yet available in the same endpoint; pull from senate.gov directly. |
| 4 | **ProPublica Congress API** | https://projects.propublica.org/api-docs/congress-api/ | **DISCONTINUED** | n/a | n/a | Shut down July 10, 2024 | n/a | **Do not depend on this source.** ProPublica recommended migrating to Congress.gov API. Historical archives may exist via Wayback or third-party mirrors but should not be a primary source. |
| 5 | **OpenSecrets API** | https://www.opensecrets.org/api | **DISCONTINUED** (as of April 15, 2025) | n/a | n/a | n/a | n/a | Per OpenSecrets, "API offerings have been discontinued." Custom data solutions available via `outreach@opensecrets.org`. See row 6 for the still-available alternative. |
| 6 | **OpenSecrets bulk data** | https://www.opensecrets.org/bulk-data | Free for educational / non-commercial use; bulk-data signup required | Email + agreement to ToS | Compressed text (pipe-delimited) | Updated periodically (~monthly during cycles); lag varies | Member CRP-ID for Moskowitz is `N00050596`; bulk files (`cands.txt`, `pacs.txt`, `indivs.txt`) can be filtered by CID | **License: CC BY-NC-SA 3.0 US** (Attribution-NonCommercial-ShareAlike). Revolving Door section is exempted (Columbia Books agreement). Must credit OpenSecrets. ToS forbids using the bulk data to scrape additional data from the site. |
| 7 | **Senate LDA API** (Lobbying Disclosure) | https://lda.gov/api/ (canonical) — legacy: https://lda.senate.gov/api/ | Free | API key recommended; anonymous clients face stricter throttling. Specific rate-limit numbers `[TODO: verify exact limits from API docs]` | JSON (REST) | Filings posted as registered: LD-1 (registration), LD-2 (quarterly activity), LD-203 (semiannual contributions) | `/api/v1/filings/?filing_specific_lobbyist_id=...` or `/api/v1/filings/?client_name=AIPAC` | **Legacy `lda.senate.gov` host retires 06/30/2026** — use `lda.gov`. Documents the *lobbying* layer (who is lobbying whom and for whom), not direct campaign contributions. |
| 8 | **House Lobbying Disclosure** | https://lobbyingdisclosure.house.gov/ | Free | None for search; bulk downloads available | XML + HTML | Quarterly filings | Search "LD-2" filings by registrant or client | House-side filings; the LDA filings are submitted to **both** the Clerk of the House and the Secretary of the Senate, so Senate LDA API is usually sufficient. House site is a useful cross-check. |
| 9 | **Florida Division of Elections — Campaign Finance Database** | https://dos.elections.myflorida.com/campaign-finance/contributions/ | Free | No API key | Tab-delimited text export (importable to CSV) via web query form | Reports filed on state schedule; the database is "an accurate representation of reports filed" — some entered from paper, so lag varies | Query by candidate name "Moskowitz" or committee number; statewide candidates returned | **No formal REST API.** Web form only; tab-delimited export. Covers candidates for **multi-county** office (state House, state Senate, governor, cabinet, PSC, statewide judicial). **Does NOT cover U.S. Senate, U.S. House, or county/municipal candidates.** For local races, see rows 11–12. |
| 10 | **Florida Committee Database** | https://dos.elections.myflorida.com/committees/ | Free | None | HTML + tab-delimited export | Filed per Florida statutory schedule | Search PCs, CCEs, ECOs that supported Moskowitz or any state-level FL-23-overlap candidate | Same scope and "no API" caveat as row 9. State-registered political committees (PCs), committees of continuous existence (CCEs), and electioneering communications organizations (ECOs). |
| 11 | **Broward Supervisor of Elections — VoterFocus campaign-finance portal** | https://www.voterfocus.com/CampaignFinance/candidate_pr.php?c=broward | Free | None | HTML reports (per-filing); some reports filed on paper are PDF-only | Filed on Broward's per-election schedule | Browse all candidates by election cycle; e.g. county commission, school board, judges, soil & water | **No documented API.** Tabular HTML must be scraped. **Paper-filed reports are not searchable inside the portal**, only available as scanned PDFs in the candidate's file — these are a known data-quality gap. |
| 12 | **Broward Supervisor of Elections — public records request** | https://browardvotes.gov/recordsdata/public-records-requests | $20 processing fee per request | (954) 712-1969 / email | Per-request (often Excel / CSV) | On request | "All campaign finance reports filed by candidate X" | Useful as a cross-check when the VoterFocus portal is missing paper filings. Not viable for live ingestion. |
| 13 | **Florida Commission on Ethics — EFDMS** (Electronic Financial Disclosure Management System) | https://disclosure.floridaethics.gov/PublicSearch/Filings | Free | None | HTML + PDF (per-filing); Form 6 is the disclosure for "constitutional officers" and state legislators | Annual filings due July 1 | Search by filer name; Moskowitz historically filed Form 6 as a state legislator (2012-2019) and as Director of FDEM (2019-2021) | Form 6 (legislators / constitutional officers) and Form 1 (most other officials). No bulk API documented — must scrape. Excellent source for **net-worth and outside-income disclosures**, which are separate from campaign finance. |
| 14 | **Florida Senate — district maps** | https://www.flsenate.gov/Session/Redistricting/MapsAndStats | Free | None | PDF, KMZ, shapefile | Updated when legislature passes new maps | Pull the SD-32, SD-35, SD-37 shapefiles for the Broward overlap with FL-23 | **2026 redistricting is in litigation** (DeSantis-signed map passed April 29, 2026, sued May 4, 2026). Boundaries used for FL-23 may shift; the 2022-2030 House plan (`H000H8013`) was still in effect for 2024 elections — verify current effective plan before ingest. |
| 15 | **Florida House — district maps** | https://www.flhouse.gov/contentViewer.aspx?Category=PublicGuide&File=About_The_Representatives_--_House_Districts_Maps.html | Free | None | PDF, shapefile | Same as row 14 | HD-93 through HD-103 substantially overlap Broward County | Same redistricting caveat. |
| 16 | **Broward County GIS — local district maps** | https://www.broward.org/Legislative/Documents/ | Free | None | PDF (MapCongressDist.pdf, MapSenateDist.pdf, MapHouseDist.pdf) | Updated post-redistricting | Reference for which Broward state-house / state-senate districts touch FL-23 | Best plain-English reference for the overlap question. Shapefiles for county commission and school-board districts available on broward.org. |
| 17 | **Ballotpedia** | https://ballotpedia.org/ | Free for reading; commercial use restricted | None | HTML | Editorial review lag (days–weeks) | Ballotpedia article on each race | **Not a primary source.** Useful as a cross-check on election results and incumbency. Has a CC BY-SA 3.0 license but with editorial-content carve-outs; do not redistribute body text without checking. |
| 18 | **FollowTheMoney.org** (National Institute on Money in Politics) | https://www.followthemoney.org/our-data/apis | Free; requires free myFollowTheMoney account | API key per-account; rate limits `[TODO: verify exact thresholds]` | JSON | Current through 2024 election cycle | Query by Entity ID for any FL state legislator | Strong **state-level** coverage where FL Division of Elections is weakest on usability. Their data is sourced from the FL DoS but normalized. License terms `[TODO: verify redistribution rights]`. |
| 19 | **GovTrack.us** | https://www.govtrack.us/congress/members/jared_moskowitz/456893 | Free | None | HTML; data downloads via separate API | Updated daily | Vote record for Moskowitz | Useful cross-reference for federal vote records. Data largely derived from Congress.gov but with friendlier UI. License: CC BY 4.0 for original analysis; underlying gov data is public domain. |
| 20 | **Track AIPAC** (trackaipac.com) | https://www.trackaipac.com/congress | Free | None | HTML | Updated by maintainer | Per-member AIPAC contribution and vote-alignment data | Activist source — useful as a starting hypothesis but **every claim must be traced back to FEC primary data** before publication, per neutrality requirement. |

---

## Coverage gaps documented elsewhere

The following are explicitly **not** in the table above because they cannot be fully populated from public APIs. See `/docs/research/dark-money.md` for the full discussion:

- 501(c)(4) "social welfare" donors (hidden by federal law).
- Shell-company pass-throughs to super PACs (only the final layer is disclosed).
- In-kind contributions in some local jurisdictions.
- Independent expenditures that fall below disclosure thresholds or are timed to avoid them.

---

## Update cadence recommendations (v1)

| Tier | Sources | Suggested ingest cadence |
|------|---------|--------------------------|
| Federal hot | openFEC API (candidate, committee, schedule A/B) | Daily |
| Federal warm | Congress.gov API (votes, bills, member metadata) | Daily |
| Federal backfill | FEC bulk data | Once at onboarding; refresh quarterly |
| State | FL DoS campaign finance, FL Ethics EFDMS | Weekly (no push API; must poll) |
| Local | Broward VoterFocus | Weekly during cycle, monthly off-cycle |
| Lobbying | Senate LDA API | Weekly |
| Reference | District shapefiles, member metadata | On redistricting events or annually |

---

## Sources

- openFEC API documentation: https://api.open.fec.gov/developers/
- openFEC GitHub: https://github.com/fecgov/openFEC
- api.data.gov rate-limit defaults: https://api.data.gov/docs/developer-manual/
- Congress.gov API: https://api.congress.gov/
- Congress.gov API GitHub: https://github.com/LibraryOfCongress/api.congress.gov/
- House Roll Call Votes launch announcement: https://blogs.loc.gov/law/2025/05/introducing-house-roll-call-votes-in-the-congress-gov-api/
- ProPublica Congress API shutdown: https://projects.propublica.org/api-docs/congress-api/
- OpenSecrets API status: https://www.opensecrets.org/api
- OpenSecrets bulk data ToS: https://www.opensecrets.org/open-data/terms-of-service
- Senate LDA API: https://lda.senate.gov/api/ and https://lda.gov/api/
- Senate LDA API docs: https://lda.gov/api/redoc/v1/
- Florida Division of Elections Campaign Finance Database: https://dos.fl.gov/elections/candidates-committees/campaign-finance/campaign-finance-database/
- Florida Committee Database: https://dos.elections.myflorida.com/committees/
- Broward Supervisor of Elections: https://browardvotes.gov/
- Broward VoterFocus portal: https://www.voterfocus.com/CampaignFinance/candidate_pr.php?c=broward
- Florida Commission on Ethics EFDMS: https://disclosure.floridaethics.gov/PublicSearch/Filings
- Florida Senate redistricting: https://www.flsenate.gov/Session/Redistricting
- Broward County legislative maps: https://www.broward.org/Legislative/Documents/
- FollowTheMoney.org APIs: https://www.followthemoney.org/our-data/apis
- 2026 Florida redistricting (Wikipedia): https://en.wikipedia.org/wiki/2026_Florida_redistricting
