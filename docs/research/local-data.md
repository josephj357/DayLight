# DayLight — Local Data Research (Broward County)

This is where DayLight provides the **most value** to voters, because local campaign-finance information is genuinely scarce and hard to navigate. Voters can look up their congressmember's funding on OpenSecrets in five minutes; finding the same for their county-court judge is a multi-hour data scavenger hunt for most people.

Scope: Broward County Commission, Broward School Board, 17th Judicial Circuit Court and Broward County Court judges, Broward Soil & Water Conservation District. All are on the FL-23 ballot (or partially so).

---

## 1. Where is local campaign finance disclosed?

For all **county-level** offices in Broward (county commission, school board, sheriff, clerk, property appraiser, supervisor of elections, judges of the 17th Judicial Circuit and County Court, soil & water conservation district):

- **Filing officer**: Broward County Supervisor of Elections (BCSOE) — https://browardvotes.gov/
- **Public search portal**: BCSOE uses **VoterFocus** (a third-party vendor product, voterfocus.com) for the campaign finance public face.
  - Candidate reports: https://www.voterfocus.com/CampaignFinance/candidate_pr.php?c=broward
  - Committee/PAC search: subset of same site
- **Public records office**: $20 processing fee per request, (954) 712-1969 or email. https://browardvotes.gov/recordsdata/public-records-requests

For **municipal** offices (city of Fort Lauderdale, Coral Springs, Pompano Beach, Margate, Deerfield Beach, Parkland, etc. — all of which overlap FL-23), the filing officer is the **city clerk**, not BCSOE. This means city-commission and mayoral campaign finance is fragmented across ~30+ Broward municipalities, each with its own filing process. DayLight v1 may scope **out** municipal races and focus on county + state + federal; this is a real gap to acknowledge to users.

---

## 2. VoterFocus: data quality and API status

### What it has

- Per-candidate, per-cycle, per-report views of campaign treasurer reports.
- All Broward county-level candidates back through several cycles.
- Itemized contributions with name, address, amount, date, occupation.
- Itemized expenditures.

### What it lacks

- **No documented public API.** The site is dynamic HTML — scraping is required.
- **Paper-filed reports are not in the searchable database.** Per BCSOE's own committee-reporting guidelines, when reports are filed on paper, "the transactions are not available in the search facility, though paper reports are uploaded and available for review under each candidate's finance section." This means an unknown subset of contributions is **PDF-only**, requiring OCR.
- **No bulk export** (no "download all 2024 county commission filings as CSV" function visible).
- **No documented stable identifiers** for candidates across cycles (e.g. a candidate running in 2020 and 2024 may have different internal IDs).

### Implication for DayLight

- Build a scraper, not an API client.
- Add OCR for PDF paper filings.
- Maintain a **candidate identity resolution** layer to reconcile the same person across cycles (probable name+address+office tuple matching).
- Acknowledge the paper-filing gap in any per-candidate page: "X% of this candidate's filings were submitted on paper and may not reflect all transactions until manually transcribed."

---

## 3. Broward County Commission (the executive layer)

The Broward County Commission has **nine members** elected by district in partisan elections; each must reside in their district. Source: https://www.broward.org/Commission/Pages/default.aspx

Verified seats as of search results:

| District | Commissioner | Source |
|----------|--------------|--------|
| 2 | Mark D. Bogen | https://www.broward.org/Commission/ — also serves as Mayor in rotation |
| 4 | Lamar P. Fisher | https://www.broward.org/Commission/ |
| 5 | Steve Geller | https://www.broward.org/Commission/ — was up for re-election 2024 |

`[TODO: verify districts 1, 3, 6, 7, 8, 9 commissioners and the 2024 election outcomes for any seats up that cycle.]`

Map of 2024 Commission districts: https://browardvotes.gov/sites/default/files/2024elections/Broward-County-Commission-Districts.pdf

**Campaign finance ingestion**: VoterFocus per commissioner. The BCSOE candidate-information page lists current and announced candidates: https://browardvotes.gov/candidate-information/announced-candidates

### Known issue: vendor contributions to school-board PCs

Local journalism has documented a pattern where school-board members operate **political committees** that receive contributions from vendors with active or pending contracts before the school board — example: contributions from healthcare and tech vendor associates to Board Member Allen Zeman's PC. Source: https://redbroward.com/2025/11/18/pac-operated-by-broward-school-board-member-allen-zeman-received-large-contributions-from-vendors-seeking-contracts-with-school-district/

This is the **canonical local "vote-vs-donor contradiction" pattern** DayLight should detect: PC-to-vendor cross-reference where vendor names match contract recipients. Detecting it requires joining:

1. Member's affiliated PC (filed at FL DoS or, if locally registered, at BCSOE/VoterFocus).
2. School district contract awards (https://www.browardschools.com — `[TODO: verify whether Broward Schools publishes contract awards in a structured feed]`).

The same pattern applies to county commission and vendor / developer contributions to candidate-affiliated PCs.

---

## 4. Broward County School Board

Nine seats: Districts 1–8 plus one At-Large (Seat 9). Five seats were up in 2024 (Districts 1, 2, 3, 5, At-Large 9).

Verified 2024 outcomes:

| Seat | Winner (2024 primary) | Notes |
|------|-----------------------|-------|
| District 1 | Maura McCarthy Bulman | Defeated incumbent Daniel Foganholi; out-fundraised him ~6:1 |
| District 2 | Rebecca Thompson | Defeated incumbent Torey Alston (DeSantis appointee) |
| District 3 | Sarah Leonardi (incumbent) | Defeated Jason Loring |
| District 5 | Jeff Holness (incumbent) | Defeated Windsor Ferguson Jr. |
| At-Large 9 | Debra Hixon (incumbent) | Defeated Tom Vasquez |

Sources:
- https://ballotpedia.org/Broward_County_Public_Schools,_Florida,_elections_(2024)
- https://www.wlrn.org/government-politics/2024-08-19/broward-election-primary-school-board

`[TODO: verify]` Districts 4, 6, 7, 8 incumbents (not up in 2024 cycle; check next cycle).

Allen Zeman's PC reporting (referenced above) is a documented case study. Source: https://redbroward.com/2025/11/18/pac-operated-by-broward-school-board-member-allen-zeman-received-large-contributions-from-vendors-seeking-contracts-with-school-district/

---

## 5. Judges — 17th Judicial Circuit Court and Broward County Court

Broward County is the **17th Judicial Circuit** of Florida. Per the court's own site (https://www.17th.flcourts.org/judges-and-judicial-staff/):

- 58 Circuit Court judges
- 33 County Court judges
- 11 General Magistrates

### Special considerations for judicial campaigns

Judicial campaigns in Florida are governed by **Canon 7** of Florida's Code of Judicial Conduct, which restricts the kinds of statements a judicial candidate can make. Judges are elected in **nonpartisan** races. Many judicial elections are uncontested — when a sitting judge has no opponent at the filing deadline, they don't appear on the ballot at all.

### Filing officer

Same as other county offices: Broward Supervisor of Elections via VoterFocus. Search interface at https://www.voterfocus.com/CampaignFinance/candidate_pr.php?c=broward — filter by office type.

### Donor patterns to watch for

This is the area where DayLight can add the most analytic value at the local level. Documented patterns to surface (without editorializing):

1. **Lawyers and law firms**: judicial contributions overwhelmingly come from the legal community. Showing the **firms** that contributed to a judge — and surfacing whether those firms have appeared before that judge — is a transparency win. (Court appearances data: `[TODO: verify whether Broward Clerk's case data has firm-of-record fields searchable by judge].`)
2. **PAC-style contributions to judicial campaigns**: rare but real; flag any non-individual, non-law-firm contributors.
3. **Self-funding**: judicial candidates frequently self-fund a large share. Surfacing the self-funded fraction is useful.

### Open verification

- `[TODO: verify]` Current list of contested judicial seats up in 2024 / 2026 in the 17th Circuit and Broward County Court.
- `[TODO: verify]` Whether judges' Form 6 financial disclosures (filed at https://disclosure.floridaethics.gov/) include the same level of detail as legislators'.

---

## 6. Broward Soil & Water Conservation District

The Soil & Water Conservation District is an elected body — five seats (Groups 1–5), nonpartisan, with very low ballot recognition. Most voters have no idea who they're voting for in this race. **High DayLight value: low information density × on the ballot = exactly the user need.**

Recent candidates (from VoterFocus searches): Beau Simon, Susan Coyle, Robert W. Sutton, Benjamin E. Groenevelt, Teresa G. Sutton, Mark E. Kleiman, Carla L. Minyan, Jeffrey Yurgealitis Sr., Ronald J. Mitcham, Gary J. Rito, Paul E. Brewer, Stephen M. Nieset, Laurence N. Kaldor. Source: https://www.voterfocus.com/CampaignFinance/candidate_pr.php?el=149&c=broward

Filing requirements: same as other Broward candidates; campaign treasurer and depository forms before any contribution or expenditure. Source: https://browardvotes.gov/candidate-information/become-candidate

District info: https://www.browardsoilandwater.org/

### Specific data-quality caveat

Soil & water races are so low-budget that many candidates raise **under $500 total** and qualify for waived reporting in some cycles. DayLight should show the absence of disclosed data as a fact, not a gap — "Candidate X reported under $500 in contributions and was not required to itemize." This is honest and protects political neutrality.

---

## 7. Municipal offices — out of scope for v1, but flag for users

Cities inside FL-23 with their own elected officials whose campaign finance is filed at the **city clerk**, not at BCSOE:

- Boca Raton (Palm Beach County — separate filing)
- Coral Springs
- Parkland
- Deerfield Beach
- Fort Lauderdale
- Pompano Beach
- Margate

Recommendation: v1 surfaces "Your municipal officials' campaign finance is filed at your city clerk — link to the city clerk's office" rather than attempting ingestion. This is honest about scope without misleading users into thinking it's a comprehensive picture.

---

## 8. Cross-reference: VoterFocus and FL DoS overlap

Some Broward candidates have committees that **also** register at the state level (e.g. a state legislator who lives in Broward — their candidate committee is at FL DoS, but if they also operate a political committee for soft money, that PC may file in different places depending on its scope). DayLight should treat the FL DoS + Broward VoterFocus join carefully and dedupe by candidate identity, not by filing.

---

## 9. Recommended ingest pipeline for Broward layer

```
For each Broward elected office in the FL-23 universe:
  1. Identify all current officeholders + announced challengers (browardvotes.gov)
  2. For each, fetch all campaign treasurer reports from VoterFocus
  3. For each PDF-only filing, OCR + structured-extract
  4. Normalize donor names (entity resolution)
  5. Cross-reference donor names against:
     - Vendor lists (Broward County procurement, Broward Schools procurement)
     - Law firm databases (Florida Bar lookup) for judicial races
     - FEC committee names (for cross-jurisdiction donors)
  6. Surface findings on the per-politician page
```

---

## 10. Open verification items

- `[TODO: verify]` Districts 1, 3, 6, 7, 8, 9 of Broward County Commission — current incumbents.
- `[TODO: verify]` Hillary Cassel's current party affiliation (federal vs state distinction).
- `[TODO: verify]` Whether Broward County Clerk's case data exposes firm-of-record per judge in a queryable format.
- `[TODO: verify]` Whether Broward County or Broward Schools publishes contract awards in a structured (machine-readable) feed.
- `[TODO: verify]` The complete list of Broward municipalities inside FL-23 and which Palm Beach County municipalities are also in-scope.
- `[TODO: verify]` Whether VoterFocus has a non-public API contract option (some VoterFocus jurisdictions do).

---

## Sources

- Broward Supervisor of Elections: https://browardvotes.gov/
- Broward VoterFocus campaign finance: https://www.voterfocus.com/CampaignFinance/candidate_pr.php?c=broward
- Broward SOE Committee Reporting Guidelines: https://browardvotes.gov/candidates/committee-reporting-guidelines
- Broward SOE Public Records Requests: https://browardvotes.gov/recordsdata/public-records-requests
- Broward County Commission: https://www.broward.org/Commission/Pages/default.aspx
- Broward County Commission Districts 2024 map: https://browardvotes.gov/sites/default/files/2024elections/Broward-County-Commission-Districts.pdf
- 17th Judicial Circuit: https://www.17th.flcourts.org/judges-and-judicial-staff/
- Ballotpedia Broward Schools 2024: https://ballotpedia.org/Broward_County_Public_Schools,_Florida,_elections_(2024)
- WLRN on Broward 2024 school board: https://www.wlrn.org/government-politics/2024-08-19/broward-election-primary-school-board
- Red Broward on Allen Zeman PC: https://redbroward.com/2025/11/18/pac-operated-by-broward-school-board-member-allen-zeman-received-large-contributions-from-vendors-seeking-contracts-with-school-district/
- Broward Soil & Water Conservation District: https://www.browardsoilandwater.org/
- Florida Commission on Ethics EFDMS: https://disclosure.floridaethics.gov/PublicSearch/Filings
