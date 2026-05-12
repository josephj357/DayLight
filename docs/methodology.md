# DayLight Methodology

**Version:** 1.0 (draft for V1, FL-23)
**License:** [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — other civic-tech projects may adopt and adapt this methodology so long as derivatives are shared under the same license and DayLight is credited.
**Last reviewed:** 2026-05-12
**Status:** PRE-PUBLIC. Items marked `[MAINTAINER REVIEW]` need a sign-off before V1 launch.

---

## Who this document is for

A journalist, a high-school civics teacher, a campaign staffer, or a curious voter should be able to read this and answer:

1. Where did every number on a politician's page come from?
2. How was the "Donor Alignment Score" computed?
3. What does DayLight refuse to claim, and why?
4. How do I tell DayLight it got something wrong?

If any of those four questions are unclear after reading this, the document has failed and we want to know. See "How to challenge a specific claim" below.

---

## 1. Data sources (canonical list)

| Layer | Source | What we pull | Refresh cadence |
|-------|--------|--------------|------------------|
| Federal donors | [FEC](https://www.fec.gov/) bulk + API | Itemized contributions ≥ $200, committee-to-committee transfers, PAC donations | Daily during election years, weekly off-cycle |
| Federal donor rollups | [OpenSecrets](https://www.opensecrets.org/) | Industry classifications, top contributor summaries, career totals | Weekly (OpenSecrets' own refresh cycle) |
| Federal votes | [ProPublica Congress API](https://projects.propublica.org/api-docs/congress-api/) | Roll-call votes, bill metadata, member positions | Daily |
| Bill→industry correlation | DayLight curated mapping in `/config/bill_industry_map.yaml` | Which industries are materially affected by each scored bill | Manual, peer-reviewed PR |
| State-level donors | Florida Division of Elections + OpenSecrets state data | State house/senate, governor, AG, CFO, agriculture commissioner | Weekly |
| Local donors | Broward County Supervisor of Elections | County commission, school board, judicial | Scrape on-demand, cached 24h |
| Revolving door | [Senate LDA](https://lda.senate.gov/) lobbying filings + state lobbyist registries | Post-office employment, lobbying registration, board seats | Quarterly |

DayLight stores frozen snapshots of every fetch (`/data/snapshots/<source>/<YYYY-MM-DD>/`). A claim on the live site links to the snapshot it was computed from. If a source corrects its data, our number changes on the next refresh and the old snapshot stays in version control for audit.

---

## 2. Industry classification

We use **OpenSecrets' standard industry taxonomy** without modification. The full code list is published at <https://www.opensecrets.org/industries/slist.php> and OpenSecrets describes their classification methodology at <https://www.opensecrets.org/resources/learn/methodology>.

**Why we don't roll our own:**
- OpenSecrets has 30+ years of classification work and a public methodology.
- A custom taxonomy would invite the exact bias accusation we are trying to defuse.
- Comparable to journalist citations: when our number disagrees with OpenSecrets, both numbers are reproducible and the disagreement is itself a story.

**Where DayLight deviates (and we admit it loudly):**
- For state and local donors not in OpenSecrets' coverage, we apply OpenSecrets' code list manually to employer names using a deterministic rule table (`/config/local_employer_industry_map.yaml`). Every mapping there is a human PR with reviewer sign-off. There is no ML auto-classification.
- When an employer is "Self-Employed" or "Retired," we **do not guess**. These are tallied separately and excluded from industry-concentration math.

---

## 3. Donor Alignment Score

This is the headline number on every politician's page. Below is the entire formula. There are no hidden weights and no proprietary adjustments. If you have a spreadsheet and an afternoon, you can reproduce any score on the site.

### 3.1 Inputs (per candidate)

- **D** = set of top industries by career donor dollars. We take the top **N=5** industries by total contribution. (`N=5` is the default; configurable per district in `/config/<district>.yaml` for future expansion. For V1, FL-23 uses N=5.)
- For each industry `i ∈ D`:
  - `d_i` = total dollars from industry `i` to this candidate's principal campaign committee + leadership PAC (career).
  - `D_total` = sum of `d_i` across the top N industries (NOT total fundraising — see footnote *).
  - `w_i = d_i / D_total` — industry `i`'s share of the top-N donor base.
- **V_i** = the set of scored roll-call votes correlated with industry `i`. Membership is determined by `/config/bill_industry_map.yaml`. Each entry there has a public rationale and a citation to the bill's industry coverage.
- For each vote `v ∈ V_i`:
  - `direction(v) ∈ {+1, -1}` — does a YES vote align with the industry's publicly-stated position? Determined by the position the industry's largest trade association or major industry PAC took on the bill, cited in the YAML. If no industry position can be cited, the vote is **excluded** from scoring.
  - `cast(v) ∈ {+1, -1, 0}` — did this candidate vote YES (+1), NO (-1), or NOT VOTE / PRESENT (0).
  - `agreement(v) = direction(v) * cast(v)` — yields +1 (voted with industry), -1 (voted against industry), or 0 (no vote).

### 3.2 Per-industry alignment

For each industry `i`:

```
a_i = (Σ agreement(v) for v ∈ V_i) / |V_i ≠ 0|
```

That is: the average agreement across non-abstaining votes. Range: `[-1, +1]`.

If `|V_i ≠ 0| < 3` (fewer than 3 scored votes), `a_i` is **undefined** and industry `i` is excluded from the final score. The site shows "insufficient vote record" for that industry and the candidate's overall score is computed over the remaining industries. This is to protect against small-sample noise.

### 3.3 Weighted alignment

```
A = Σ (w_i * a_i)  for industries with defined a_i, re-normalized over those industries
```

(Re-normalization: if industry 3 of 5 is excluded, the remaining four `w_i` are divided by their sum so they total 1.0 before the weighted sum.)

`A` is in `[-1, +1]`.

### 3.4 Final 0–100 score

```
DonorAlignmentScore = round( (A + 1) * 50 )
```

- **100** = perfect alignment with top donor industries on every scored vote.
- **50** = neutral / mixed record.
- **0** = perfect opposition to top donor industries on every scored vote.

### 3.5 What the score is and is NOT

- **It is** a measure of correlation between fundraising and voting, computed from public records.
- **It is NOT** a measure of corruption, character, or causation. A 100 may reflect genuine ideological alignment with the industries that fund them. A 50 may reflect a candidate who funds themselves. A 0 may reflect a candidate whose donors expected one thing and got another.
- The page never uses words like "bought" or "captured." It says, e.g., "Voted with top donor industries 87% of the time." Editorial framing belongs to the reader.

\* **Footnote on `D_total` choice.** We weight only over the top-N industries, not all fundraising. This is deliberate: a candidate's marginal small donors do not buy votes in any plausible model, but the top concentrations of money plausibly correlate with voting. We considered weighting by total receipts (denominator = career total raised) and rejected it because it dilutes the signal for self-funded candidates. We considered weighting by % of vote-scored bills only and rejected it because it punishes candidates with broad portfolios. The current formula is the simplest defensible choice. `[MAINTAINER REVIEW]` — confirm before public launch.

### 3.6 Worked example (synthetic)

Candidate X. Top 5 donor industries (career):

| Industry | $ | `w_i` |
|----------|---|-------|
| Securities & Investment | $400,000 | 0.40 |
| Real Estate | $250,000 | 0.25 |
| Lawyers/Law Firms | $200,000 | 0.20 |
| Health Professionals | $100,000 | 0.10 |
| Pro-Israel | $50,000 | 0.05 |

Scored votes for Securities & Investment (3 in the YAML): voted with industry on 2, against on 1. `a = (1+1-1)/3 = 0.33`.

Real Estate (4 votes): with on 4. `a = 1.00`.
Lawyers (2 votes): only 2 scored, fewer than 3 → **excluded**.
Health Professionals (3 votes): with on 2, against on 1. `a = 0.33`.
Pro-Israel (5 votes): with on 5. `a = 1.00`.

Re-normalize over included industries: weights of 0.40, 0.25, 0.10, 0.05 sum to 0.80. Divide each by 0.80:
- Securities: 0.50
- Real Estate: 0.3125
- Health: 0.125
- Pro-Israel: 0.0625

```
A = 0.50*0.33 + 0.3125*1.00 + 0.125*0.33 + 0.0625*1.00
  = 0.165 + 0.3125 + 0.04125 + 0.0625
  = 0.58125
Score = round((0.58125 + 1) * 50) = round(79.06) = 79
```

The site would display: **"Donor Alignment: 79/100"** with a button "Show the math" that expands the table above and links to every cited bill and roll call.

### 3.7 Determinism

The score is purely arithmetic over fixed inputs. Same fixtures in, same number out. No RNG, no ML, no model temperature. This is asserted in `tests/methodology/test_alignment_score.py`.

---

## 4. Revolving-door detection

We surface a "revolving door" flag on a politician's page when **any** of the following are true and citable:

1. **Post-office employment.** The politician (or their spouse) has worked for, sat on the board of, or consulted for a company or 501(c) that contributed **≥ $10,000 cumulatively** to their campaigns within 5 years of the role beginning. Source: company SEC filings, press releases, LinkedIn (only as a tip — never the sole source), confirmed by a press citation.
2. **Lobbying registration.** The politician is registered as a federal lobbyist per [Senate LDA](https://lda.senate.gov/) or as a state lobbyist per the relevant state registry (for FL: Florida Lobbyist Registration Office). We link the registration filing.
3. **Donor-firm board seats.** The politician sits on the board of any entity (corporate, nonprofit 501(c)(4), trade association) that contributed ≥ $10,000 to their campaigns. Source: company governance disclosures, IRS Form 990 Part VII.

**The $10,000 threshold** is deliberately conservative. We chose it because it is the typical max individual contribution ($3,300 in 2024 + spouse + multiple committees + multiple cycles ≈ $10k) and avoids flagging every small donor's coincidental future employment. `[MAINTAINER REVIEW]` — confirm threshold for V1.

**Important non-flag:** Working in an industry the politician previously regulated, without a direct donor relationship, is **not** auto-flagged. That is normal labor mobility and flagging it without a donor link would generate noise.

We do **not** infer revolving-door status from name matches alone. Every flag has a citation in `/data/revolving_door/<candidate_id>.yaml` with at least one primary source URL.

---

## 5. AI synthesis layer

Each politician page includes a 2–4 sentence plain-English summary of the most notable donor/vote contradictions. This summary is generated by Claude (model pinned in `/config/synthesis_model.yaml`) under strict constraints.

### 5.1 What Claude does

- Reads the structured data (top donors, top industries, alignment score, top "contradiction" votes — i.e., votes against the candidate's top donor industries' stated positions).
- Produces 2–4 sentences describing factually what the data shows.
- Cites every claim with an internal source ID that resolves to a bill, a contribution record, or a published industry position.

### 5.2 What Claude does NOT do

- It does not access the open web during synthesis. Inputs are limited to our frozen, cited data.
- It does not produce editorial conclusions ("X is corrupt", "Y is captured by Wall Street").
- It does not use politically loaded vocabulary. The full red-flag list is in `tests/methodology/red_flags.json` and is enforced by `tests/methodology/test_synthesis_neutrality.py`.
- It does not vary output for the same input. Temperature is pinned to 0 and a seed is set where the API supports it. Same fixtures in → same prose out (within the model provider's determinism guarantees, which we acknowledge are imperfect — see "Limitations" §7).

### 5.3 Political neutrality system prompt

The exact prompt template is maintained at `/src/ingestion/prompts/synthesis_prompt.md` (produced by the backend developer; this methodology references it but does not duplicate it). The prompt must satisfy:

1. **Symmetry clause** — "Apply identical analytic standards to candidates of every party. Do not characterize parties, ideologies, or movements."
2. **Source-only clause** — "Every factual claim must be tied to an input source ID. If you cannot cite, do not claim."
3. **Vocabulary clause** — "Do not use loaded political vocabulary. Prefer neutral verbs (voted, received, served) over evaluative verbs (caved, captured, sold out)."
4. **Refusal clause** — "If inputs are insufficient for a factual sentence, write 'Insufficient data for synthesis.' and stop. Do not improvise."

The prompt is version-controlled. Any change to the prompt triggers `test_synthesis_neutrality.py` and `test_alignment_score.py` (since changing the prompt should not change scores), and requires two-maintainer review.

---

## 6. What DayLight CANNOT see

This list is on the **landing page**. Loud and acknowledged is better than buried.

- **501(c)(4) "dark money."** By law, social welfare 501(c)(4) organizations need not disclose donors. If a (c)(4) spends millions to support a candidate, DayLight sees the (c)(4)'s name on the candidate's expenditure report but cannot see who funded the (c)(4). Same for some 501(c)(6) trade associations.
- **In-kind contributions** that aren't required to be itemized (e.g., volunteer time, free media appearances).
- **Independent expenditures** that don't coordinate with the campaign — Super PAC spending — are reported separately by the FEC and we include them in a clearly labeled "outside spending" section, but we do not include them in the candidate's `D` (donor industry set) used for the alignment score, because the candidate technically did not "receive" that money.
- **Cryptocurrency contributions** below itemization thresholds and certain decentralized funding mechanisms.
- **Foreign-influence vectors** that don't surface in FEC filings — foreign-government PR contracts with US firms employing the candidate's family, equity stakes in US LLCs by foreign nationals, etc. These require investigative journalism we cannot automate.
- **State and local data quality.** Florida is reasonably good for state filings; some other states are years behind. Broward County local data is **scrape-only** and may lag the official record by 1–14 days. The "last refreshed" timestamp on the page is the truth.
- **Bundling.** A donor who personally gave $3,300 but bundled $200,000 from associates is recorded as a $3,300 donor in our data. Bundling is reported separately by candidates for federal races but inconsistently and we treat that data as supplementary, not primary.

If you read the page and think "they look clean," remember: 30% of the money in modern elections is invisible to anyone outside the campaign.

---

## 7. Limitations and known biases in source data

- **FEC reporting lag.** Federal donors are reported quarterly off-year and monthly in-cycle. Q4 2025 data is not visible until ~Feb 2026. The site shows a "data current as of" date.
- **State data quality varies wildly.** Florida is mid-tier; California is excellent; Wyoming and Mississippi are poor. Our coverage promise per state is in `/docs/data-sources.md` (separate document).
- **Local data is often scrape-only.** Broward County for V1. If their site is down, we serve stale data with a banner.
- **ProPublica corrections.** ProPublica occasionally corrects roll-call records. We re-fetch weekly and any score change resulting from a correction is logged in `/data/score_history/<candidate_id>.log`.
- **OpenSecrets refresh cadence.** OpenSecrets updates their rollups on their own schedule (typically every 2–4 weeks). Our career totals may lag theirs by up to a month. We display the OpenSecrets refresh date alongside our number.
- **Model determinism.** Even at temperature 0, hosted LLMs are not bit-for-bit deterministic across infrastructure changes. The synthesis prose may vary by a word or two between runs. The structured inputs (the score, the donor table, the vote list) are fully deterministic.
- **Industry attribution.** OpenSecrets occasionally reclassifies contributors. When they do, our historical scores can shift slightly. We log these shifts.

---

## 8. Political neutrality commitment

> **Identical methodology applied to all candidates regardless of party, ideology, incumbency, or popularity.**

Operational consequences:

- The same scored-bills set is used for every candidate who voted on those bills. We do not handpick bills per candidate.
- The same red-flag vocabulary list applies in synthesis prompts for all candidates.
- Code review: any pull request that introduces candidate-specific or party-specific logic is reverted on sight. The PR template asks "Does this change treat all candidates identically?" — checked by the reviewer.
- The maintainers do not endorse candidates. The project does not accept donations from political committees, candidates, or registered lobbyists. (See `/SECURITY.md` for the funding policy.)

Asymmetric scrutiny will end the project's credibility before it begins. It is the single most important rule.

---

## 9. How to challenge a specific claim

Methodology challenges and data corrections follow a **separate process** from feature requests. They are higher priority and have a named maintainer DRI.

### Two channels:

1. **Email** to `corrections@daylight.[domain]` (set up at launch).
2. **GitHub issue** in this repo with the title prefix `[Correction]`.

### Required information:

- The URL of the page with the claim.
- The specific number or sentence you believe is wrong.
- What you believe the correct value is.
- A primary-source citation supporting your correction (FEC filing URL, ProPublica vote URL, OpenSecrets page, official press release, court document, etc.).

### Maintainer response SLA:

- Acknowledgement: within 48 hours.
- Triage decision (correction issued / methodology explanation / further investigation): within 7 days.
- Correction deployment, if warranted: within 14 days of triage.

If the dispute is about **methodology** (the formula itself) rather than data, the resolution is a PR against this document and `tests/methodology/`, going through full review.

---

## 10. License of methodology

This methodology document is licensed under [Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/). Other civic-tech projects, journalists, and researchers may use and adapt it provided:

1. They credit DayLight as the source.
2. They share derivatives under the same license.
3. They do not imply DayLight endorses their adaptation.

The codebase is separately licensed under AGPL-3.0 (see `/LICENSE`).

---

## Items flagged for maintainer review before public launch

- **§3.5 — denominator choice in `D_total`.** Confirm "weighted only over top-N industries" survives a hostile read.
- **§3.1 — `N=5`.** Confirm the top-N value. Some candidates have very concentrated funding (top 3 = 80% of donors); some are diffuse. Sensitivity analysis pending.
- **§3.2 — minimum 3 scored votes per industry.** Confirm this threshold for V1.
- **§4 — $10,000 revolving-door threshold.** Confirm; could reasonably be $5k or $25k.
- **§5.3 — synthesis prompt.** Awaits final from `/src/ingestion/prompts/synthesis_prompt.md`. This methodology will need a one-line update once that file is final.
- **§9 — corrections email address.** Reserve at launch.
