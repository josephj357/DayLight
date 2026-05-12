# DayLight — Federal Data Deep Dive: FL-23 (Rep. Jared Moskowitz)

This document maps the federal data layer for the v1 launch district. Every factual claim is cited to a primary source; activist or partisan sources are flagged. Same standard would apply to every member regardless of party — see neutrality methodology in `/docs/methodology.md`.

---

## 1. Canonical IDs for Rep. Jared Moskowitz

These are the join keys for every federal dataset DayLight ingests.

| System | ID | Source |
|--------|----|--------|
| FEC Candidate ID | `H2FL22171` | https://www.fec.gov/data/candidate/H2FL22171/ |
| FEC Principal Campaign Committee ID | `C00807628` (Jared Moskowitz For Congress, registered March 6, 2022) | https://www.fec.gov/data/committee/C00807628/ |
| FEC Joint Fundraising Committee | `C00824243` (Jared Moskowitz Victory Fund) | https://www.fec.gov/data/committee/C00824243/ |
| FEC Leadership PAC | "The MPIRE Strikes PAC" (committee ID `[TODO: verify exact FEC ID]`) | https://floridapolitics.com/archives/685210-jared-moskowitz-adds-380k-in-q2-as-gop-challengers-jockey-for-primary-edge/ |
| OpenSecrets CRP ID | `N00050596` | https://www.opensecrets.org/members-of-congress/jared-moskowitz/summary?cid=N00050596 |
| GovTrack ID | `456893` | https://www.govtrack.us/congress/members/jared_moskowitz/456893 |
| Bioguide ID (Congress.gov) | `M001257` `[TODO: verify against api.congress.gov/v3/member]` | n/a |
| House.gov page | https://moskowitz.house.gov/ | (canonical office) |

These five IDs are the only ones DayLight needs to fully join the federal layer.

---

## 2. Most reliable source for career donor totals

**Primary source**: the **FEC openFEC API** itself, querying Schedule A (individual contributions) and Schedule B (disbursements) for committee `C00807628`. Career totals require summing across all cycles since Moskowitz first filed as a federal candidate (2022).

- Endpoint pattern: `https://api.open.fec.gov/v1/committee/C00807628/schedules/schedule_a/`
- For aggregated by-industry totals, FEC does not classify contributions by industry; **industry codes are added by OpenSecrets** via their CID-based normalization. This is why career-by-industry analysis is harder after the OpenSecrets API shutdown (April 15, 2025).

**Pragmatic stack for DayLight v1**:

1. Primary numbers (raw totals, donor names, dates, amounts): FEC openFEC API or FEC bulk files.
2. Industry / sector classification: OpenSecrets **bulk data** (CC BY-NC-SA 3.0 US) using CID `N00050596`.
3. Cross-check: floridapolitics.com quarterly reporting for sanity-checking quarterly haul numbers.

**Verified quarterly / cycle numbers** (cited to primary FEC filings via journalism):

- Q3 2023: ~$120,000 raised; ~$426,000 cycle-to-date. Source: https://floridapolitics.com/archives/641935-jared-moskowitz-vastly-outpaces-republican-field-with-120k-haul-in-q3/
- Q2 2024: ~$380,000 raised. Source: https://floridapolitics.com/archives/685210-jared-moskowitz-adds-380k-in-q2-as-gop-challengers-jockey-for-primary-edge/

Career total `[TODO: verify total receipts across 2021-22 and 2023-24 cycles from FEC `/committee/C00807628/totals/` endpoint at ingest time]`.

---

## 3. The AIPAC / United Democracy Project angle

This is the single most consequential donor relationship in Moskowitz's federal profile. It is also one of the most-covered, so DayLight's job is to **report the disclosed numbers and let the user draw their own conclusion** — not to characterize.

### What is publicly disclosed

- **AIPAC PAC** (FEC committee `[TODO: verify AIPAC PAC FEC committee ID — there are multiple AIPAC-related committees]`) is registered as a connected PAC and discloses its candidate contributions on Schedule B. This is the **traceable** layer.
- **United Democracy Project (UDP)**, FEC committee `C00799031`, is a super PAC affiliated with AIPAC. It does **independent expenditures** — both for and against candidates — which are disclosed on Schedule E. UDP donors are disclosed on its own Schedule A. Sources:
  - https://www.fec.gov/data/committee/C00799031/
  - https://www.opensecrets.org/political-action-committees-pacs/united-democracy-project/C00799031/summary/2022
  - https://www.factcheck.org/2022/08/united-democracy-project/

### Verified numbers for Moskowitz

- 2022 cycle: Moskowitz received approximately **$28,900** from AIPAC. Source: https://www.opensecrets.org/members-of-congress/industries?cid=N00050596 (cycle=2022 view).
- 2024 cycle (full): Pro-Israel contributions to Moskowitz totaled approximately **$354,598**, of which AIPAC PAC accounted for approximately **$322,798**. Source: https://www.opensecrets.org/members-of-congress/jared-moskowitz/industries?cid=N00050596&cycle=2024
- Cumulative (career, as of 2024): activist site Track AIPAC reports a total of **"at least $138,400 from the Israel lobby"** for Moskowitz (note: this figure does NOT reconcile with the OpenSecrets 2024-cycle total of $354,598; the discrepancy is either a different scope of "Israel lobby" or a reporting-period difference). **`[TODO: verify which cycles / which committees Track AIPAC includes in their $138,400 figure].`** Source: https://x.com/TrackAIPAC/status/1777163983067501045
- UDP independent expenditures targeted at FL-23: `[TODO: verify whether UDP spent for/against Moskowitz in 2022 primary; UDP's 2022 expenditures were concentrated in MD-04, MI-10, MI-11, NC-01 — sources do not confirm FL-23 IE activity].`

### What this tells DayLight, factually

- Pro-Israel PACs are Moskowitz's single largest disclosed industry contributor in the 2023-2024 cycle.
- AIPAC has formally endorsed him for re-election (source: https://floridapolitics.com/archives/656916-aipac-endorses-jared-moskowitz-for-re-election/).
- Moskowitz has publicly defended his alignment in his own words ("I was just going to be a 'yes' next to Israel") — source: https://thehill.com/homenews/4284352-florida-democrat-says-hell-vote-for-israel-aid-bill-despite-irs-cuts-i-am-not-going-to-take-the-bait/

This pattern of high-disclosure, candidate-acknowledged alignment is what DayLight should surface for **every member**, regardless of party or issue. The same depth of analysis would apply to (e.g.) a Republican member's relationship to the oil & gas industry, a Democratic member's relationship to organized labor, or any other member-industry pairing.

---

## 4. Vote-vs-donor alignment: documented cases

DayLight's "contradictions" feature requires linking a vote to a contributor relationship. For Moskowitz, two well-documented votes are useful test cases (test cases — not editorial conclusions):

### Case A — November 2, 2023: H.R. 6126 (Israel Security Supplemental Appropriations Act, 2024)

- **Vote**: Moskowitz voted **YES**. The bill paired $14.3B in aid to Israel with cuts to IRS funding. It passed 226-196 with 12 Democrats joining Republicans. Moskowitz was one of the "Tax Cheat Twelve" per The American Prospect's characterization.
- **Donor context**: AIPAC PAC was Moskowitz's largest pro-Israel contributor in the 2023-24 cycle (~$322,798 disclosed contribution stream).
- **What Moskowitz said publicly**: he criticized the bill's structure but voted yes, citing his family's Holocaust history as motivation.
- Sources:
  - https://thehill.com/homenews/house/4291422-these-12-democrats-bucked-their-party-to-support-gops-israel-aid-bill/
  - https://prospect.org/2023/11/02/11-02-2023-israel-palestine-democrats-irs-funding/
  - https://thehill.com/homenews/4284352-florida-democrat-says-hell-vote-for-israel-aid-bill-despite-irs-cuts-i-am-not-going-to-take-the-bait/
  - https://rules.house.gov/bill/118/hr-Israel-Supplemental
- **DayLight framing**: factual report of the vote + the disclosed donor relationship + the candidate's own stated reasoning. No editorial conclusion. Reader decides.

### Case B — Track AIPAC's bill-co-sponsorship claim

Per AIPAC's own communications, Moskowitz "led on eight AIPAC-supported bills, and co-sponsored 26 bills and 28 resolutions" backed by the group, including H. Res. 888 (Reaffirming the State of Israel's Right to Exist), which passed 412-1 in November 2023.

- Source for the AIPAC count: https://floridapolitics.com/archives/656916-aipac-endorses-jared-moskowitz-for-re-election/
- DayLight must independently verify each of these 8 + 26 + 28 = 62 bills/resolutions against Congress.gov's bills endpoint before publishing the claim. **`[TODO: verify the eight AIPAC-supported bills Moskowitz led; cross-reference against Congress.gov sponsor/cosponsor data].`**

---

## 5. Federal vote-record source

- Primary: **Congress.gov API** — House Roll Call Votes endpoint (in beta as of May 2025), covers 118th Congress (2023) forward.
- Member-vote endpoint: `/v3/house-vote/{congress}/{session}/{voteNumber}/members`
- For votes prior to 2023, use **GovTrack** as cross-reference (CC BY 4.0).
- Senate roll-call votes are **not** yet on the new Congress.gov endpoint and must be pulled from senate.gov XML feeds directly — not relevant for Moskowitz (House member) but flagged for when DayLight extends to Senate races.

---

## 6. Lobbying-layer cross-reference

The Senate LDA API (https://lda.gov/api/) discloses **who lobbied which member's office** via the LD-2 quarterly reports. DayLight should ingest these as a parallel layer to direct campaign contributions because:

1. Lobbying disclosures are often a leading indicator of issue alignment (a client's lobbyist filed an LD-2 listing a specific bill → that bill's vote alignment is meaningful).
2. The LD-203 contributions report discloses *lobbyist* personal political contributions, which sometimes flow to specific members.

For Moskowitz, useful queries:
- All LD-2 filings naming "Office of Rep. Jared Moskowitz" or "Rep. Moskowitz" as a contacted entity.
- All LD-203 contributions from registered lobbyists to committee `C00807628`.
- `[TODO: verify whether LD-2 contact reporting includes individual member offices at the granularity DayLight needs, or only chamber-level / committee-level disclosures.]`

---

## 7. Open verification items

These are items flagged for the engineer who builds the federal ingest:

- `[TODO: verify]` The MPIRE Strikes PAC — confirm FEC committee ID and whether it has independent expenditures linked to Moskowitz's own race (leadership PACs typically support *other* candidates).
- `[TODO: verify]` Bioguide ID `M001257` against Congress.gov API.
- `[TODO: verify]` Whether UDP made independent expenditures in FL-23 in 2022 or 2024 (Schedule E filings of committee `C00799031`).
- `[TODO: verify]` Whether AIPAC PAC's FEC ID is `C00797670` (the most likely candidate) — pull directly from openFEC `/committee/?q=AIPAC`.
- `[TODO: verify]` Reconcile Track AIPAC's $138,400 claim with OpenSecrets' $354,598 figure — these may reflect different scopes (PAC-only vs PAC+bundled+IE).
- `[TODO: verify]` Moskowitz's career total receipts across all cycles from `/committee/C00807628/totals/`.

---

## Sources

- FEC candidate page: https://www.fec.gov/data/candidate/H2FL22171/
- FEC committee page: https://www.fec.gov/data/committee/C00807628/
- FEC Jared Moskowitz Victory Fund: https://www.fec.gov/data/committee/C00824243/
- OpenSecrets summary: https://www.opensecrets.org/members-of-congress/jared-moskowitz/summary?cid=N00050596
- OpenSecrets industries (2024 cycle): https://www.opensecrets.org/members-of-congress/jared-moskowitz/industries?cid=N00050596&cycle=2024
- United Democracy Project FEC profile: https://www.fec.gov/data/committee/C00799031/
- FactCheck on UDP: https://www.factcheck.org/2022/08/united-democracy-project/
- AIPAC endorsement of Moskowitz: https://floridapolitics.com/archives/656916-aipac-endorses-jared-moskowitz-for-re-election/
- Israel aid vote coverage: https://thehill.com/homenews/house/4291422-these-12-democrats-bucked-their-party-to-support-gops-israel-aid-bill/
- Moskowitz's own statement on vote: https://thehill.com/homenews/4284352-florida-democrat-says-hell-vote-for-israel-aid-bill-despite-irs-cuts-i-am-not-going-to-take-the-bait/
- The American Prospect "Tax Cheat Twelve": https://prospect.org/2023/11/02/11-02-2023-israel-palestine-democrats-irs-funding/
- H.R. 6126 (Israel Security Supplemental): https://rules.house.gov/bill/118/hr-Israel-Supplemental
- Track AIPAC claim: https://x.com/TrackAIPAC/status/1777163983067501045
- ProPublica Congress API discontinuation: https://projects.propublica.org/api-docs/congress-api/
- Congress.gov House Roll Call Votes (beta) launch: https://blogs.loc.gov/law/2025/05/introducing-house-roll-call-votes-in-the-congress-gov-api/
- Senate LDA API: https://lda.gov/api/
- Moskowitz Q3 2023 fundraising: https://floridapolitics.com/archives/641935-jared-moskowitz-vastly-outpaces-republican-field-with-120k-haul-in-q3/
- Moskowitz Q2 2024 fundraising: https://floridapolitics.com/archives/685210-jared-moskowitz-adds-380k-in-q2-as-gop-challengers-jockey-for-primary-edge/
