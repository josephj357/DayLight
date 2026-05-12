# Claude Code configuration — DayLight

Configuration for future Claude Code sessions working on this repository.

## Behavioral rules (always enforced)

- Do what has been asked; nothing more, nothing less.
- NEVER create files unless absolutely necessary for the goal.
- ALWAYS prefer editing an existing file to creating a new one.
- NEVER proactively create documentation files (*.md) or README files unless explicitly requested.
- NEVER save working notes, drafts, or scratch files to the repo root.
- ALWAYS read a file before editing it.
- NEVER commit secrets, credentials, or `.env` files.

## File organization

- `/src/web/` — Next.js + TypeScript frontend.
- `/src/api/` — FastAPI backend.
- `/src/ingestion/` — Python ingestion scripts (FEC, Congress.gov, state, county).
- `/src/schema/` — schema definitions shared across runtimes (SQLite, TS, Pydantic).
- `/config/districts/` — one YAML per district. The whole project is config-extensible.
- `/docs/` — public-facing docs (methodology, architecture, research, guides).
- `/docs/architecture-decisions/` — ADRs.
- `/docs/research/` — researcher agent's output (data-source mapping per jurisdiction).
- `/tests/` — pytest suite. Fixtures in `/tests/fixtures/`.
- `/scripts/` — utility scripts (`seed.sh` for first-run bootstrap).
- `/data/` — local SQLite database lives here at runtime. Gitignored.

Never save files at the repo root that aren't conventional project artifacts
(README, LICENSE, CONTRIBUTING, etc.).

## Project architecture

- Domain-driven, config-extensible. One YAML file describes one district.
- File size limit: 500 lines.
- Typed interfaces at every boundary (TypeScript on frontend, Pydantic on backend).
- AI synthesis layer is cache-keyed by content hash so identical inputs yield
  identical outputs (and zero new API calls).
- SQLite as the v1 database. Zero infrastructure required for a fork.

### Project config

- Topology: hierarchical
- Max agents: 6 (per `/AGENTS.md`)
- Memory: file-based + per-agent namespaced (no cross-pollution)
- Neutrality: religious. Same scrutiny applied to every party.

## Build and test

```bash
# First-time bootstrap (installs deps, runs ingestion, seeds SQLite).
bash scripts/seed.sh

# Run the backend API (port 8000 by default).
cd src/api && uvicorn main:app --reload

# Run the frontend (port 3000 by default).
cd src/web && npm install && npm run dev

# Run the test suite.
pytest tests/

# Frontend lint + type-check.
cd src/web && npm run lint && npm run type-check
```

- ALWAYS run `pytest tests/` after changing anything in `/src/`, `/config/`, or `/tests/`.
- ALWAYS run `npm run build` in `/src/web/` before committing frontend changes.

## Security rules

- Never hardcode API keys, secrets, or credentials in source files.
- Never commit `.env` files or any file with secrets.
- Validate user input at system boundaries (ZIP lookups especially).
- Sanitize file paths in any district-config loader to prevent directory traversal.
- Treat scraped HTML as untrusted — sanitize before storing.

## Concurrency

When a non-trivial change touches multiple subsystems, batch related
operations into a single message rather than scattering tool calls.

## Swarm orchestration

The swarm config and agent ownership boundaries are documented in
[`/AGENTS.md`](./AGENTS.md). See that file before launching any
multi-agent run against this repository.

## Neutrality enforcement (project-specific)

DayLight applies identical scrutiny to all parties. This is enforced by both
human review and the `tests/methodology/test_synthesis_neutrality.py` red-flag
filter.

Concretely, when generating any user-facing text:

- Never use partisan loaded terms ("radical," "extreme," "MAGA," "woke,"
  "socialist," "fascist," etc.) outside of attributed quotation.
- Apply identical thresholds, formula constants, and visual treatments to
  every politician regardless of party.
- When in doubt, defer to `/docs/methodology.md`.

## Where to find things

- The methodology that decides what we show: `/docs/methodology.md`.
- The data-source map: `/docs/data-sources.md`.
- The architecture overview: `/docs/architecture.md`.
- Why we made specific design choices: `/docs/architecture-decisions/`.
- The agent coordination spec: `/AGENTS.md`.

## Support

- Documentation: in-repo. Start at [`/README.md`](./README.md).
- Issues: open a GitHub issue on this repository.
- Corrections to factual claims: open an issue prefixed `[Correction]`. Do NOT
  PR a correction without an accompanying issue.
