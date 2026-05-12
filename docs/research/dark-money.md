# DayLight — What We Can't See (Dark Money & Disclosure Gaps)

Acknowledging blind spots builds trust. This document maps the political money DayLight **cannot** show users, and explains why. Every gap below is grounded in current law and credible journalism — not speculation.

A user reading a DayLight politician profile should understand: **the disclosed picture is a partial picture**. We will show that picture as accurately as possible and we will flag, on every relevant page, the categories of money that are legally hidden from us.

---

## 1. 501(c)(4) "social welfare" organizations

This is the largest single category of dark money in U.S. politics.

### How it works (legal mechanism)

Section 501(c)(4) of the U.S. Internal Revenue Code lets "social welfare" nonprofits engage in political activity — including running ads that name candidates — **without disclosing donors**, as long as politics is not the organization's "primary activity." The "primary activity" line is generally interpreted as up to 49% political activity.

A 501(c)(4) files an IRS Form 990 annually, which shows aggregate revenue and major program expenses but **does not** name contributors (Schedule B donor names are redacted on the public version).

### What we can see vs. can't see

**Can see**:
- Aggregate revenue, expenditures, and high-level program categories from Form 990.
- Independent expenditures (IEs) that a (c)(4) reports to the FEC when those IEs cross the federal reporting threshold (express advocacy or electioneering communications within statutory windows).
- The specific funder of a *specific communication* if the FEC's narrow disclosure rule applies — i.e., a donor who gave specifically to fund a particular ad.

**Can't see**:
- The names of donors who contributed to the (c)(4)'s general fund.
- The actual pass-through chain when a (c)(4) makes a contribution to a super PAC (we see the (c)(4) name on the super PAC's Schedule A, but not the (c)(4)'s upstream donors).

### Scale (2024 cycle)

Per the Brennan Center for Justice, **dark money hit a record $1.9 billion in 2024 federal races**. Per OpenSecrets, in the 2024 election cycle, shell companies and 501(c) nonprofits that did not disclose their funding sources gave **$1.3 billion to super PACs** — more than the prior two cycles combined.

Sources:
- https://www.brennancenter.org/our-work/research-reports/dark-money-hit-record-high-19-billion-2024-federal-races
- https://www.opensecrets.org/dark-money/basics
- https://www.skadden.com/insights/publications/2023/03/complying-with-the-rules-governing-501c4-organizations-key-issues
- https://harmoncurran.com/fec-issues-new-guidance-on-501c4-independent-expenditure-reporting/

### How DayLight should handle it

- On every politician page, include a "What we can't see" section noting any 501(c)(4) activity that benefited the politician (positive IEs from disclosed (c)(4)s) **and** flagging that the funders of those (c)(4)s are not disclosed by law.
- Do **not** speculate about who is behind a (c)(4). Report only what the (c)(4) itself disclosed about itself.
- If investigative journalism has identified specific donors of a (c)(4) via leaks, lawsuits, or other lawful disclosures, cite the journalism — don't restate it as DayLight's own finding.

---

## 2. Dark-money pass-throughs (the chained-LLC problem)

A common dark-money pattern: a donor contributes to a 501(c)(4), the (c)(4) contributes to a super PAC, the super PAC runs ads. Or: a donor sets up a single-purpose LLC, the LLC contributes to a super PAC, the LLC dissolves after the cycle. In both cases, the final-layer disclosure (super PAC's Schedule A) names only the immediate giver, not the ultimate beneficial owner.

### What we can see vs. can't see

**Can see**:
- The chain from super PAC back **one** step.
- The LLC's existence and (usually) state of registration via state corporate records.

**Can't see**:
- The beneficial owner of an LLC in most states. (The federal Corporate Transparency Act required beneficial-ownership disclosure to FinCEN, but enforcement and public access have been turbulent — `[TODO: verify current CTA enforcement status in 2026].`)
- The original natural-person donor when a (c)(4) is in the chain.

### How DayLight should handle it

- When the immediate donor on a super PAC's Schedule A is an LLC or a (c)(4), label it clearly as such on the page.
- If state corporate records identify the LLC's filer/agent, surface that information with the appropriate caveat ("filer of record, not necessarily beneficial owner").
- Never present an LLC contribution as if it were from an individual donor. The contribution is from "Acme Holdings LLC" — that is the disclosed fact; everything else is inference.

---

## 3. In-kind contributions

Direct cash contributions are itemized. **In-kind** contributions — campaign infrastructure, polling, opposition research, list rentals, mailing services, ad production, food and venue for events — are also reportable, but the level of detail varies and the **disclosed value** is set by the donor, not the market.

### What we can see vs. can't see

**Can see**:
- The fact of an in-kind contribution and its self-reported value (FEC Schedule A and Schedule B with type code).
- The category (e.g., "polling," "mailing services").

**Can't see**:
- Whether the self-reported value matches market value.
- The detailed scope (e.g., "polling" might mean 1 poll or 10).
- In some local jurisdictions, in-kind contributions below a certain value threshold are not itemized at all.

### How DayLight should handle it

- Surface in-kind contributions clearly in any donor list, marked as in-kind.
- Note in the methodology that values are self-reported.

---

## 4. Independent expenditures (IEs) — what's visible and the timing gap

Independent expenditures **are** disclosed when they cross statutory thresholds. The gap is in the **timing** and in IEs that fall just below thresholds or just outside statutory electioneering-communication windows.

### What we can see vs. can't see

**Can see (federal)**:
- Express-advocacy IEs disclosed on FEC Schedule E.
- Electioneering communications (broadcast, cable, or satellite ads naming a federal candidate within 30 days of a primary or 60 days of a general) disclosed on FEC Form 9.
- The super PAC or (c)(4) that ran the ad.

**Can't see**:
- IEs that are designed to fall just below the disclosure threshold.
- "Issue ads" that intentionally avoid express advocacy ("call Senator X and tell him to vote no on…") and avoid the electioneering window — these can be invisible.
- Online ads where platforms' transparency varies (Meta and Google have ad libraries; smaller platforms often don't).

Per the Brennan Center, "Dark money groups also increasingly run ads, including many online ads, that are worded and timed such that they do not trigger FEC disclosure requirements."

### How DayLight should handle it

- Pull Schedule E data and surface IE totals by spender on each politician's page.
- Add a clear note: "Some online and issue advertising may have benefited or opposed this candidate without triggering disclosure. The total below reflects only disclosed independent expenditures."
- Where Meta and Google ad libraries are useful cross-references, link out (Google Political Advertising Transparency Report, Meta Ad Library).

---

## 5. Foreign-influence vectors

The Foreign Agents Registration Act (FARA) requires registration of agents of foreign principals who engage in U.S. political activities. FARA filings are public at https://www.justice.gov/nsd-fara. The Lobbying Disclosure Act (LDA) similarly captures domestic lobbying, but **foreign lobbying via U.S.-citizen lobbyists for domestic affiliates of foreign entities** can sit in a gray zone between the two.

### What we can see vs. can't see

**Can see**:
- FARA registrations and supplemental filings.
- LDA filings naming foreign-affiliated clients.

**Can't see**:
- Foreign money that flows through U.S.-citizen intermediaries to U.S. (c)(4)s and onward to super PACs (foreign contributions to U.S. elections are illegal at the federal level; in-practice tracing is impossible when intermediaries are present and not flagged).
- Foreign-government strategic communications campaigns that don't involve traditional "lobbying" (e.g., earned-media campaigns, think-tank funding).

### How DayLight should handle it

- For politicians who are members of foreign-affairs committees or who have prominent positions on foreign-policy issues, surface relevant FARA registrations that touched their office (LDA also captures these via LD-2 contact-reporting).
- Be very careful with the framing — foreign-influence claims are easily weaponized. Stick to **disclosed filings** and don't extrapolate.

---

## 6. State and local gaps specific to Florida

- **501(c)(4) state-level**: Florida law does not require additional donor disclosure from (c)(4)s beyond what federal law requires. Unlike New York and Connecticut, which have additional state-level (c)(4) disclosure when those groups engage in state political activity.
- **PCs vs ECOs vs CCEs in Florida**: PCs (political committees) disclose donors. ECOs (electioneering communications organizations) disclose donors but only for spending on electioneering communications. CCEs (committees of continuous existence) — these were largely phased out / replaced; check the current Florida statutes for the live entity types `[TODO: verify which entity types are active in current FL chapter 106 statutes].`
- **Local PCs in Broward**: Some PCs that operate at the county level register at BCSOE / VoterFocus, but **larger PCs operating across counties register at FL DoS**. This creates a small jurisdictional gap where a county-level vendor-to-officeholder PC chain may have pieces in multiple filing systems. DayLight needs to query both layers.

---

## 7. Things we can almost see (data exists but is hard)

These are not strictly "dark money" — disclosure exists — but the data is so hard to use that in practice most voters never see it. DayLight should commit to reducing these to "visible":

- **Self-funded loans**: a candidate's loan to their own campaign appears on Schedule A. Whether that loan is later repaid (i.e., whether donors effectively reimbursed the candidate) requires longitudinal tracking across cycles.
- **Bundlers**: registered bundlers are disclosed (per HLOGA), but only at thresholds and only for committees who comply. The gap between formal bundlers and informal fundraising networks is large.
- **PAC-to-PAC contributions**: legal but obfuscating. Tracing donor → PAC → joint fundraising committee → candidate is multi-step and most users never do it.

---

## 8. What DayLight commits to (the "trust contract")

This is the public commitment DayLight makes to voters about disclosure honesty:

1. **Every politician page will name the disclosure system that supplies its data.** No mystery sourcing.
2. **Every politician page will include a "What we can't see" section** linking to this document and listing the specific categories of unseen money plausibly relevant to the politician's race.
3. **We will never speculate about hidden donors.** When journalism has identified them via independent reporting, we'll link the journalism with attribution — we won't restate it as our own finding.
4. **We will apply the same disclosure scrutiny to every politician regardless of party.** Same depth, same caveats, same framing.

---

## 9. Open verification items

- `[TODO: verify]` Current FinCEN beneficial-ownership disclosure status (Corporate Transparency Act enforcement in 2026).
- `[TODO: verify]` Active entity types under Florida chapter 106 (PC, ECO, CCE, ICO) — confirm current taxonomy.
- `[TODO: verify]` Whether Google and Meta political-ad libraries have stable APIs DayLight can ingest for FL-23 ads.
- `[TODO: verify]` Whether the FEC has updated its 501(c)(4) Schedule E independent-expenditure guidance since 2024.

---

## Sources

- Brennan Center on 2024 dark money: https://www.brennancenter.org/our-work/research-reports/dark-money-hit-record-high-19-billion-2024-federal-races
- OpenSecrets Dark Money Basics: https://www.opensecrets.org/dark-money/basics
- Wikipedia Dark money overview: https://en.wikipedia.org/wiki/Dark_money
- Skadden on 501(c)(4) compliance: https://www.skadden.com/insights/publications/2023/03/complying-with-the-rules-governing-501c4-organizations-key-issues
- ProPublica on IRS 501(c)(4) enforcement: https://www.propublica.org/article/irs-political-dark-money-groups-501c4-tax-regulation
- Harmon Curran on FEC IE guidance for (c)(4)s: https://harmoncurran.com/fec-issues-new-guidance-on-501c4-independent-expenditure-reporting/
- Issue One methodology: https://issueone.org/dark-money-illuminated-report-methodology/
- DOJ FARA: https://www.justice.gov/nsd-fara
- LDA / lobbying: https://lda.gov/
- Skadden on shadow canvassing: https://clsbluesky.law.columbia.edu/2025/02/06/skadden-discusses-shadow-canvassing-by-501c4-organizations/
