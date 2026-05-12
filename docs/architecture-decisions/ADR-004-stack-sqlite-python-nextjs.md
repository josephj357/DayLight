# ADR-004 — Stack: SQLite + Python ingestion + FastAPI + Next.js

**Status:** Accepted
**Date:** 2026-05-12

## Context

DayLight is a forkable, gift-shaped project. The constraints on the technology
stack are unusual:

- **Zero infrastructure cost** to evaluate or fork. A volunteer with a laptop
  has to be able to clone and run the whole thing in under 10 minutes.
- **No managed services.** A maintainer should not have to provision Postgres,
  Redis, or anything else on day one.
- **Languages familiar to civic-tech and journalism communities.** Not
  niche stacks.
- **Long-term maintainability without an active maintainer.** Boring tech is
  better than cutting-edge tech.

## Decision

- **Database:** SQLite (single file, `/data/daylight.db`).
- **Ingestion:** Python 3.11+ with `requests`, `pydantic`, `beautifulsoup4`,
  `pyyaml`, `anthropic`, `sqlite-utils`.
- **API:** FastAPI + Uvicorn.
- **Frontend:** Next.js 14 (app router) + TypeScript strict + Tailwind +
  Recharts.
- **AI synthesis:** Anthropic API, model pinned to `claude-sonnet-4-5` for
  primary synthesis and `claude-haiku-4-5` for cheap classification tasks.

## Rationale

- **SQLite removes the operational floor.** No DB to provision, no migrations
  to coordinate, no `docker-compose` requirement. A fork can run on someone's
  laptop indefinitely. If a future operator needs Postgres, the migration
  path is well-trodden.
- **Python is the lingua franca of civic-tech ingestion.** Most existing FEC
  and OpenSecrets tooling is Python. Journalists who can already code mostly
  code in Python.
- **FastAPI is a small, well-typed framework that Pydantic-models naturally.**
  The schema-shared-across-runtimes design (`schema.sql`, `types.ts`,
  `models.py`) is enforced because Pydantic is on both ends.
- **Next.js is the default React shape.** Static generation works for
  district pages, which removes a class of caching problems.
- **Pinning the Claude model is required for reproducibility.** Methodology
  tests need to assert that synthesis output is stable across runs.

## Consequences

- **Concurrent writes to SQLite are a real constraint** at higher scale, but
  irrelevant at v1 scale (a small ingestion process and a handful of read
  clients).
- **No background job system in v1.** Ingestion is a script you run; the API
  is a separate process. If scheduling is needed, cron is sufficient.
- **Anthropic API key is required for full functionality.** The synthesis
  layer degrades gracefully (cards show a "synthesis not yet generated"
  state) but the killer feature is missing without it.
- **The data layer is portable.** SQLite + plain-text schema means anyone
  can inspect `daylight.db` with the `sqlite3` CLI or DB Browser. No
  proprietary tooling required.
- **A future fork could swap the stack** without rewriting the methodology
  or the data sources. The schema is the durable artifact; the stack is
  implementation detail.

## Alternatives considered

- **Postgres** — rejected for v1. Real for serious operators, overkill for
  forks and demos.
- **Node-only stack (TypeScript end-to-end with Drizzle or Prisma).**
  Rejected. The civic-tech ingestion ecosystem is Python. Forcing Node
  would shrink the contributor pool meaningfully.
- **Go for the API.** Rejected. Smaller civic-tech contributor pool. No
  meaningful performance win at v1 scale.
- **Static-site-only build with no backend.** Rejected. Synthesis caching
  needs a backend, and the search/zip lookup is awkward at build-time only.
