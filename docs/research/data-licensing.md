# DayLight — Data Licensing & Redistribution Compliance

DayLight is released under AGPL-3.0 as a gift to voters. The **code** license is settled. The **data** license is per-source and varies considerably. This document audits every v1 data source for legal redistribution compliance, flagging any source that would constrain DayLight's mission.

This document is **not legal advice.** Where DayLight's intended use is close to a license boundary, the maintainer should obtain written confirmation from the data provider before relying on the data in production.

---

## TL;DR — the three rules

1. **Federal government data is safe.** FEC, Congress.gov, Senate LDA, FARA — all are public-domain works of the U.S. government and may be freely redistributed.
2. **State and local government data is usually safe** in Florida (FL has a strong public-records statute, chapter 119), but specific filing systems may add restrictions on bulk redistribution. Verify per source.
3. **Third-party aggregators (OpenSecrets, FollowTheMoney, Ballotpedia) carry licenses we must respect** — typically CC BY-NC-SA, which constrains commercial use and requires share-alike. DayLight being AGPL-3.0 / non-commercial-by-mission is compatible in spirit, but the maintainer must verify the legal compatibility for any commercial-adjacent activity (e.g. a future hosted-service variant).

---

## Per-source license audit

| Source | License / legal status | Attribution required? | Redistribution allowed? | Commercial use? | DayLight compatible? |
|--------|------------------------|------------------------|-------------------------|------------------|----------------------|
| **FEC (openFEC API + bulk)** | U.S. government work; public domain under 17 U.S.C. § 105 | No legal requirement, but attribution is standard practice | Yes | Yes, with one restriction (see below) | **Yes — primary source.** |
| **Congress.gov API** | U.S. government work; public domain | Same | Yes | Yes | **Yes.** |
| **Senate LDA / lda.gov API** | U.S. government work (filed under HLOGA s.209); public domain | Same | Yes | Yes | **Yes.** |
| **House Lobbying Disclosure** | U.S. government work; public domain | Same | Yes | Yes | **Yes.** |
| **DOJ FARA** | U.S. government work; public domain | Same | Yes | Yes | **Yes.** |
| **Florida Division of Elections — Campaign Finance Database** | Florida public records (FL Stat. ch. 119) | No formal requirement; cite as good practice | Yes | Yes | **Yes — primary state source.** |
| **Florida Committee Database** | Same | Same | Yes | Yes | **Yes.** |
| **Florida Commission on Ethics — EFDMS** | Same | Same | Yes | Yes | **Yes.** |
| **Broward Supervisor of Elections / VoterFocus portal** | Florida public records via county filing officer | Same | Yes (data itself); the **VoterFocus presentation layer** is a private vendor product — the underlying records are public, but the vendor's UI and code aren't being licensed | Yes (data) | **Yes for data; do not redistribute VoterFocus HTML/screenshots as if they were ours.** |
| **OpenSecrets API** (discontinued April 15, 2025) | n/a | n/a | n/a | n/a | n/a |
| **OpenSecrets bulk data** | **CC BY-NC-SA 3.0 US** (Attribution-NonCommercial-ShareAlike) | **Yes — must credit OpenSecrets** | Yes, with conditions | **Non-commercial only** | **Conditional — see detailed section below.** |
| **OpenSecrets Revolving Door section** | **Exempted** from the bulk-data CC license per OpenSecrets' agreement with Columbia Books | n/a (proprietary) | No | No | **No — do not redistribute revolving-door data.** |
| **FollowTheMoney.org** | License `[TODO: verify exact terms]` | Likely required | `[TODO: verify]` | `[TODO: verify]` | **Conditional pending verification.** |
| **ProPublica Congress API** (discontinued July 10, 2024) | Was CC BY-NC-ND when active; now historical | n/a | n/a | n/a | n/a |
| **GovTrack.us** | CC BY 4.0 for GovTrack's own analysis; underlying government data is public domain | **Yes for GovTrack analysis** | Yes | Yes | **Yes, with attribution for any GovTrack-original analysis used.** |
| **Ballotpedia** | CC BY-SA 3.0 with editorial-content carve-outs | **Yes** | Conditional — share-alike applies to derived text | Yes | **Use only as cross-reference; do not embed Ballotpedia body text into DayLight pages.** |
| **The Accountability Project / publicaccountability.org** | License `[TODO: verify]` | Likely required | `[TODO: verify]` | `[TODO: verify]` | **Conditional pending verification.** |
| **Transparency USA** | License `[TODO: verify]` | Likely required | `[TODO: verify]` | `[TODO: verify]` | **Conditional pending verification.** |

---

## Detailed analysis of high-impact licenses

### 1. FEC data — the one restriction

FEC data is in the public domain under 17 U.S.C. § 105 (works of the U.S. government are not subject to domestic copyright). The single statutory restriction:

> **Contributor lists may not be used for commercial purposes or to solicit donations.** (52 U.S.C. § 30111(a)(4))

This is the "sale or use restriction." It's a federal statutory prohibition, not a license term. It means:

- DayLight **can** display individual contributor names and amounts publicly for transparency purposes — this is the original transparency rationale and is well-established as compliant.
- DayLight **cannot** sell or rent contributor lists, use them to solicit donations to DayLight itself, or repackage them for commercial fundraising lists.

Reference: https://www.fec.gov/help-candidates-and-committees/filing-reports/individual-contributions/ (and 52 U.S.C. § 30111(a)(4))

**DayLight implication**: We're fine for the v1 use case. If DayLight ever adds a donation-solicitation feature for itself, we cannot use FEC contributor data to seed it.

### 2. Congress.gov API — terms

The Congress.gov API is operated by the Library of Congress. The data is U.S. government work and in the public domain. The api.congress.gov site itself has a "Legal" link with the Library of Congress's standard terms; the data redistribution rights are **not constrained** beyond the general api.data.gov terms (which themselves do not restrict redistribution).

Reference: https://api.congress.gov/ ; https://www.congress.gov/help/using-data-offsite

**DayLight implication**: Safe.

### 3. OpenSecrets bulk data — the most important nuance

OpenSecrets bulk data is **DayLight's only realistic path** to industry-classified campaign finance (matching donors to sectors like "pro-Israel," "lawyers/lobbyists," "oil & gas," etc.). The FEC does **not** classify contributions by industry; that classification is OpenSecrets' work product, and it is what gives DayLight the analytic ability to say "this politician's top industry is X."

OpenSecrets bulk data is licensed **CC BY-NC-SA 3.0 US**. This means:

- **BY (Attribution)**: every page that uses OpenSecrets-derived data must credit OpenSecrets. The standard credit line per OpenSecrets' ToS: "Source: OpenSecrets.org" with a link to opensecrets.org.
- **NC (Non-Commercial)**: the data may not be used for commercial purposes. DayLight being AGPL-3.0, open-source, released as a gift, and non-commercial in mission is on the right side of this line — but anything that monetizes the dataset (paid API, hosted service with fees, ad-supported deployment) is on the wrong side.
- **SA (ShareAlike)**: any derivative dataset DayLight produces from OpenSecrets bulk data must be released under the same CC BY-NC-SA 3.0 license. This is a **substantive constraint**: a portion of DayLight's data layer (the industry-classified portion) is effectively dual-licensed — DayLight's *code* is AGPL-3.0, but the *industry-classification overlay* must be redistributed under CC BY-NC-SA 3.0.

References:
- https://www.opensecrets.org/bulk-data
- https://www.opensecrets.org/open-data/terms-of-service
- https://creativecommons.org/licenses/by-nc-sa/3.0/us/

**DayLight implications and recommendations**:

1. **Add an OpenSecrets credit on every politician page that uses their industry classification.** Suggested: at the bottom of any "by industry" section: "Industry classification by OpenSecrets.org (CC BY-NC-SA 3.0)."
2. **Segregate the data layer.** Store FEC-derived raw data and OpenSecrets-derived industry classifications in separate tables / namespaces so it's always clear which fields are subject to the NC-SA constraint.
3. **If DayLight ever moves toward any commercial deployment** (a hosted SaaS, a paid tier, anything ad-supported), OpenSecrets data must be removed or relicensed via a commercial agreement (contact `outreach@opensecrets.org`).
4. **Do not use the Revolving Door section.** OpenSecrets' agreement with Columbia Books explicitly excludes Revolving Door data from the CC license. If DayLight wants revolving-door information, build our own from FARA + LDA + employment-disclosure data.
5. **Do not use the bulk data to scrape additional fields from OpenSecrets' website.** The ToS forbids this explicitly.

### 4. Ballotpedia — the trap

Ballotpedia is **tempting** for cross-referencing election results, incumbent biographies, and ballot composition. Two cautions:

- Ballotpedia is licensed **CC BY-SA 3.0** with **editorial-content carve-outs**. The text of Ballotpedia articles can be reused with attribution and share-alike, but specific editorial features (e.g., their endorsement summaries, their issue-position analyses) are sometimes carved out.
- The share-alike obligation means any DayLight page that **directly incorporates** Ballotpedia text becomes itself CC BY-SA 3.0 in that portion.

**DayLight implication**: use Ballotpedia as a research starting point and a cross-reference, but **do not embed Ballotpedia body text directly into DayLight pages**. Cite it as a source, link to it, but write our own descriptions.

### 5. The state public-records baseline

Florida has one of the strongest public-records statutes in the U.S. (FL Stat. ch. 119, the "Sunshine Law"). Records of state and local agencies — including campaign-finance filings and financial disclosures — are generally public and freely redistributable. There is **no Florida statute** restricting redistribution of campaign-finance records analogous to FEC's federal contributor-list restriction.

**DayLight implication**: FL state and Broward county records are safe for redistribution, including for any future deployment scenario. Verified for v1 scope. Source: https://www.flsec.state.fl.us/ (for chapter 119 reference materials).

### 6. VoterFocus and other vendor presentation layers

VoterFocus is a private SaaS vendor used by many Florida (and other state) supervisors of elections. The **records** displayed by VoterFocus are public — they are public records filed with the SOE — and DayLight can redistribute the records freely. The **vendor's UI, screenshots, branding, and any structured data formats they may have implemented** are the vendor's IP. DayLight should:

- Scrape the records (the underlying public data).
- Store and republish the records as data.
- Not redistribute VoterFocus HTML, screenshots, or proprietary formats.
- Not redistribute Broward-specific structures that VoterFocus has added beyond the underlying public records.

This is a normal scrape-a-vendor-frontend-for-public-data pattern; the underlying records are what we're redistributing.

---

## Concerning constraints the maintainer should know

The maintainer should specifically be aware of these:

1. **The OpenSecrets share-alike obligation is real and meaningful.** It bifurcates DayLight's data layer into "AGPL-3.0 (code) + freely redistributable public-record data" and "CC BY-NC-SA 3.0 (industry classifications from OpenSecrets)." Architecturally, these need to be separable so that a future DayLight deployment scenario can drop the OpenSecrets overlay if needed without losing the rest.
2. **The OpenSecrets API discontinuation in April 2025 changes the landscape.** DayLight depends on OpenSecrets **bulk data** for industry classification — bulk is still available, but the loss of the live API means DayLight must build periodic-refresh ingestion rather than live-query patterns. Plan for this in the v1 architecture.
3. **The ProPublica Congress API discontinuation in July 2024 also changes the landscape.** DayLight should standardize on the Congress.gov API (Library of Congress) from day one. Do not build against the ProPublica spec.
4. **FollowTheMoney, Transparency USA, and The Accountability Project all have license terms that must be verified before bulk ingestion.** Until verified, treat them as cross-references rather than as authoritative data layers.
5. **Florida's 2026 redistricting litigation may, depending on how it's resolved, retroactively affect which district maps DayLight should treat as authoritative for the next election.** This is a data-currency question rather than a licensing question, but it's worth noting in any "as of [date]" disclaimers.
6. **FEC's commercial-use prohibition for contributor lists is statutory.** If DayLight ever takes commercial form, that's a federal-statute issue, not just a license question. Document this clearly in any commercial-conversion conversation.

---

## Required attribution snippets

For consistency, here are the standard attribution lines DayLight should include where appropriate:

- **FEC**: "Source: U.S. Federal Election Commission (open.fec.gov). FEC data is in the public domain."
- **Congress.gov**: "Source: Congress.gov, Library of Congress (api.congress.gov). U.S. government work in the public domain."
- **OpenSecrets**: "Industry classification source: OpenSecrets.org. Licensed CC BY-NC-SA 3.0 US."
- **Florida Division of Elections**: "Source: Florida Department of State, Division of Elections (dos.fl.gov)."
- **Broward Supervisor of Elections / VoterFocus**: "Source: Broward County Supervisor of Elections via VoterFocus public campaign-finance portal."
- **GovTrack**: "Analysis source: GovTrack.us. CC BY 4.0."

---

## Open verification items

- `[TODO: verify]` FollowTheMoney.org's data redistribution license / terms.
- `[TODO: verify]` The Accountability Project's data license.
- `[TODO: verify]` Transparency USA's data license.
- `[TODO: verify]` Current FEC guidance on the contributor-list commercial-use prohibition; confirm no rule changes since 2024.
- `[TODO: verify]` Whether the Congress.gov API's legal page has any redistribution language we should comply with beyond the public-domain baseline.
- `[TODO: verify]` Whether VoterFocus has any ToS we should acknowledge for the scraping pattern (the underlying public records being our target, not the VoterFocus UI).

---

## Sources

- 17 U.S.C. § 105 (government works): https://www.law.cornell.edu/uscode/text/17/105
- 52 U.S.C. § 30111(a)(4) (FEC sale or use): https://www.law.cornell.edu/uscode/text/52/30111
- FEC LICENSE.md: https://github.com/fecgov/FEC/blob/master/LICENSE.md
- OpenSecrets bulk data: https://www.opensecrets.org/bulk-data
- OpenSecrets ToS: https://www.opensecrets.org/open-data/terms-of-service
- OpenSecrets API status: https://www.opensecrets.org/api
- CC BY-NC-SA 3.0 US: https://creativecommons.org/licenses/by-nc-sa/3.0/us/
- ProPublica Congress API discontinuation: https://projects.propublica.org/api-docs/congress-api/
- Congress.gov data offsite use: https://www.congress.gov/help/using-data-offsite
- Florida Sunshine Law (FL Stat. ch. 119): https://www.flsenate.gov/Laws/Statutes/2024/Chapter119
