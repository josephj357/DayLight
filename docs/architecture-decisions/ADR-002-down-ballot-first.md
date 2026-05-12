# ADR-002 — Down-ballot first

**Status:** Accepted
**Date:** 2026-05-12

## Context

When designing a voter-transparency tool, the obvious starting point is
federal: U.S. House and Senate races have the most data, the most press
attention, and the most existing tools (OpenSecrets, Vote Smart, ProPublica
historically, Congress.gov).

DayLight deliberately inverts that priority: v1 emphasizes the *down-ballot*
stack — state legislature, county commission, school board, judges, soil &
water districts — over the federal race that anchors a district.

## Decision

DayLight v1 ships a single congressional district (FL-23) but covers the
entire down-ballot stack a voter in that district would see on their ballot.
Federal coverage is present but not the primary differentiator.

## Rationale

Three reasons drove this:

1. **The federal-tool market is saturated.** OpenSecrets has 20+ years of brand
   and the canonical donor data. Competing on federal alone is a losing race.
   The marginal value of one more federal-only tool is near zero.

2. **The down-ballot market is empty.** Almost no public-facing tool clearly
   shows who's funding a county commission race, a school board contest, a
   judicial election. Yet these are the races where small dollar amounts
   produce disproportionate influence and where voters are most uninformed.
   The marginal value of *any* clear tool here is high.

3. **Down-ballot information is genuinely scarce.** Federal data is APIs and
   bulk files. State data is portals. County data is HTML pages and PDFs.
   The technical lift to make local data usable is the project's actual moat
   — and it's where a curious volunteer in another district can fork DayLight
   for their own community and immediately add real public value.

## Consequences

- **The frontend has to handle race heterogeneity gracefully.** A federal House
  race, a nonpartisan judicial election, and a soil-and-water seat are very
  different shapes. The schema's `level` and `office` fields and the
  `RaceLevel` enum exist to make this clean.

- **Ingestion is significantly more complex per district.** Most of the work
  is the local scrapers, not the FEC pull. Forking DayLight for a new district
  is therefore mostly a state-and-county scraping job, not a federal-data
  rewiring job. The forking guide reflects this.

- **The "Pulled from public data nobody else aggregates" framing is the
  marketing line.** It's true, it's accurate, and it's what makes the project
  worth releasing as a gift.

- **Federal data is the easy validation surface.** Because OpenSecrets and
  Congress.gov are well-known, the federal layer of DayLight is what an
  early reviewer (journalist, civic-tech researcher) can sanity-check
  quickly. That builds trust in the harder-to-verify down-ballot layer.

## Alternatives considered

- **Federal-only v1, expand to local later.** Rejected. The "expand later"
  step rarely happens; v1 sets the project's identity. If federal is the
  identity, the project becomes a worse-OpenSecrets and dies.

- **Pure local (skip federal entirely).** Rejected. The federal race is the
  voter's entry point into the district view. Skipping it makes the product
  feel incomplete and removes the easy validation surface above.

- **Cover everything for one state instead of one district.** Rejected for v1.
  Cost is much higher; demo value is lower. State-wide is a fork target after
  v1 ships.
