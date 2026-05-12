# Architecture

DayLight is a small, local-first civic-data app. The whole system fits on one
laptop with no managed services. This document covers the major pieces and
how they fit together; for the *why* of specific choices, see the ADRs in
[`./architecture-decisions/`](./architecture-decisions/).

## One-paragraph overview

A nightly (or on-demand) Python pipeline pulls public campaign-finance and
voting data from federal, state, and county sources into a local SQLite
database. A FastAPI service reads from that database and serves a typed JSON
API. A Next.js frontend consumes the API and renders a per-district view of
every race a voter sees on their ballot — with top donors, industry
concentration, vote-vs-donor alignment, and an AI-generated plain-English
summary per candidate.

## Container diagram

```mermaid
flowchart LR
  subgraph external [Public data sources]
    FEC[FEC OpenFEC API]
    CG[Congress.gov API]
    OS[OpenSecrets bulk data<br/>CC BY-NC-SA 3.0]
    FLDOE[Florida Division<br/>of Elections]
    BROW[Broward Co.<br/>Supervisor of Elections]
    LDA[Senate LDA<br/>lobbyist disclosure]
  end

  subgraph local [Local machine / fork]
    direction TB
    INGEST[/src/ingestion<br/>Python] --> DB[(SQLite<br/>/data/daylight.db)]
    DB --> API[/src/api<br/>FastAPI]
    API --> WEB[/src/web<br/>Next.js + TS]
    WEB --> USER([Voter])
    INGEST -.cache.-> CLAUDE[Anthropic API<br/>synthesis layer]
    CLAUDE --> INGEST
  end

  FEC --> INGEST
  CG --> INGEST
  OS --> INGEST
  FLDOE --> INGEST
  BROW --> INGEST
  LDA --> INGEST
```

## The pieces

### 1. Ingestion (`/src/ingestion/`)

Python scripts, one per source. Each is idempotent — running twice produces
the same database state. Responses from external APIs are cached on disk by
content hash so repeated runs cost almost nothing.

| Script | Source | Notes |
|--------|--------|-------|
| `fetch_fec.py` | FEC OpenFEC | Federal contributions. Public domain. |
| `fetch_congress.py` | Congress.gov | Federal voting records. Replaces the discontinued ProPublica Congress API. |
| `load_opensecrets_bulk.py` | OpenSecrets bulk CSVs | Industry classifications. CC BY-NC-SA 3.0 — attributed in UI. |
| `fetch_florida_state.py` | FL Division of Elections | State legislature campaign finance. |
| `fetch_broward_local.py` | Broward Supervisor of Elections | County races. Currently a stub — see source for the scrape contract. |
| `synthesize.py` | Anthropic API | Plain-English synthesis. Cached by input hash. |
| `pipeline.py` | — | Orchestrator. Reads `/config/districts/<id>.yml`, runs the fetchers, populates the DB. |

The pipeline writes ingestion status to the `ingestion_log` table so the
methodology page can show "last refreshed" dates and degrade gracefully when
a source is stale.

### 2. Database (`/data/daylight.db`)

SQLite. Single file. The schema is in [`/src/schema/schema.sql`](../src/schema/schema.sql).

Notable design choices:

- **`source` column on every contribution row.** Federal vs. state vs. county
  data is never silently mixed.
- **OpenSecrets-derived columns are isolated.** Industry rollups live in their
  own table (`industry_totals`) so a future commercial fork can drop the
  CC BY-NC-SA layer without losing the FEC baseline.
- **Bills + bill→industry map are first-class.** The alignment-score formula
  (see methodology §3) needs them, so they're table-backed rather than
  config-only.

The schema is shared across runtimes: SQL for SQLite, TypeScript types in
`/src/schema/types.ts`, Pydantic models in `/src/schema/models.py`. All three
files must stay in sync — integration tests in `/tests/integration/` enforce it.

### 3. API (`/src/api/`)

FastAPI. Three routes for v1:

| Route | Returns |
|-------|---------|
| `GET /districts/{id}` | Full district payload — every race, candidates, summary fields. |
| `GET /candidates/{id}` | Deep candidate detail — donors, industries, votes, synthesis, revolving door. |
| `GET /search/zip/{zip}` | `{ districtId }` or 404 if no mapping. |

The response shapes are pinned in `/src/schema/types.ts` (frontend) and
`/src/schema/models.py` (backend). Changing one without the other will fail
`/tests/integration/test_api.py`.

CORS is permissive in dev (`http://localhost:3000`) and restricted in prod
(set via environment).

### 4. Frontend (`/src/web/`)

Next.js 14 (app router) + TypeScript strict. Three significant routes:

- `/` — landing page with ZIP entry.
- `/district/[district]` — every race on the ballot, grouped by level
  (federal → state → county → judicial → special).
- `/candidate/[id]` — the deep dive. The synthesis card is the visual centerpiece.

The typed API client (`/src/web/lib/api.ts`) falls back to mock fixtures when
the backend is unreachable, so the frontend renders standalone during development.

## Data flow on a typical request

```
1. Voter lands on /, enters ZIP 33064.
2. Frontend calls GET /search/zip/33064 → { districtId: "fl-23" }.
3. Frontend navigates to /district/fl-23.
4. Page server-renders by calling GET /districts/fl-23.
5. Backend reads SQLite, joins races + candidates + summary fields.
6. Voter clicks a candidate → /candidate/<id>.
7. Page calls GET /candidates/<id>.
8. Backend joins candidate + donors + industries + votes + synthesis_cache + revolving_door.
9. Synthesis text is read from cache (no live Anthropic call on page load).
```

## What this is not

- **Not a managed service.** v1 is local-first. Hosting is a separate concern.
- **Not a campaign tool.** The FEC's statutory commercial-use prohibition on
  contributor lists is honored. DayLight surfaces who funded whom; it never
  helps anyone solicit from those funders.
- **Not real-time.** Federal data has a reporting lag (weeks). State and county
  data is often longer. The methodology doc explains this.

## Blind spots (acknowledged loudly)

- **Dark money** — 501(c)(4) "social welfare" groups do not disclose donors by law.
- **In-kind contributions** — inconsistently reported across jurisdictions.
- **Independent expenditures** — Super PACs report separately; integration in v1 is partial.
- **Foreign-origin influence vectors** — covered by FARA but the data quality is uneven.

See [`/docs/research/dark-money.md`](./research/dark-money.md) for the full list.

## Extending the architecture

The two extensions most likely to happen:

1. **Add a new district.** Drop a YAML file in `/config/districts/`. No code changes.
2. **Add a new data source.** Add a fetcher in `/src/ingestion/`, update the
   district YAML's `data_sources` block to point at it, extend the SQLite
   schema if the data doesn't fit existing tables. Document in
   `/docs/data-sources.md`.

Anything beyond those — new scoring formulas, new visualization types, new
deployment targets — should start with a methodology PR and an ADR.
