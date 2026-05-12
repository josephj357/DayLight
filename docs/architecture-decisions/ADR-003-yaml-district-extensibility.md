# ADR-003 — YAML district extensibility (one file = one district)

**Status:** Accepted
**Date:** 2026-05-12

## Context

DayLight ships with FL-23 as the reference district. The intended path to
broader coverage is *forking*: voters, journalists, or civic-tech volunteers
in other districts add their own.

The configuration model has to make adding a district a low-effort task. If a
new district requires changes to code, schema, scrapers, or the frontend,
adoption stalls. If a new district is one file in a known location, adoption
is friction-free.

## Decision

Each district is described by a single YAML file in `/config/districts/<id>.yml`.
The file enumerates:

- The federal seat anchoring the district.
- All overlapping state-legislature districts.
- All county/municipal offices on the local ballot.
- All judicial races.
- All special-district seats.
- ZIP codes that should route to this district.
- Per-district data-source URLs and modes (API / scrape / bulk).
- Methodology knobs that may legitimately vary by district (top-N industries,
  vote-count threshold, revolving-door dollar floor).

Code changes are not required to add a district unless the new district
requires a data source not already supported in `/src/ingestion/`.

## Rationale

- **One file is the smallest possible unit of contribution.** A new
  contributor can land their first PR with one YAML file and not touch any
  Python or TypeScript.
- **YAML is right for this shape.** Mostly-static descriptive data with
  occasional inline comments. JSON would lose the comment affordance; TOML
  doesn't compose nested lists well; JSON5 isn't widely supported.
- **Methodology knobs in the same file as the district** keeps "what we
  changed for this district and why" co-located. Hiding knobs in a separate
  file would invite undocumented drift.
- **Per-district data-source pointers** mean the ingestion layer doesn't
  need a centralized registry of every jurisdiction's quirks. The YAML
  carries it.

## Consequences

- **Ingestion scripts read the YAML, not hard-coded constants.** Adding a
  new state's data source means: write the fetcher, register it under
  `data_sources.<jurisdiction>.<source>`, point the district YAML at it.
- **Schema must support unknown future race types.** The `level` enum is
  intentionally broad (`federal | state | county | municipal | judicial |
  special`). Adding a new level requires a migration; adding new offices
  inside an existing level does not.
- **The methodology test suite must run against every district config.**
  `/tests/integration/test_district_config.py` does exactly this: loads
  every YAML and verifies the methodology produces a sensible score.
- **Forking guide is the primary onboarding doc.** When someone wants to
  add their district, they go to `/docs/forking-guide.md`, not the README.

## Alternatives considered

- **Database-driven district configuration.** Rejected. Configuration in a
  database is harder to PR against. Reviewers want diffs of YAML, not SQL
  migrations.
- **Code-generated district configs from a script.** Rejected. Adds a build
  step. Discourages hand-edits and `[TODO: verify]` annotations.
- **One YAML per office, not per district.** Rejected. Lots of cross-cutting
  fields (ZIP routing, snapshot date) would have to be duplicated.
