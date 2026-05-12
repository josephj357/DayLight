# AGENTS.md — DayLight swarm coordination

This file describes the 6-agent setup used to build DayLight v1, and how future
contributors can run a similar swarm to extend it. It's specifically for AI-agent
coordination (claude-flow / Claude Code Task tool); humans reading this for
ordinary contributing should look at [CONTRIBUTING.md](./CONTRIBUTING.md) instead.

## The six agents

| # | Role | Owns (paths) | Notes |
|---|------|--------------|-------|
| 1 | **system-architect** | `/AGENTS.md`, `/CLAUDE.md`, `/docs/architecture.md`, `/docs/architecture-decisions/`, `/src/schema/`, `/config/districts/<district>.yml` | Queen of the swarm. Defines schema and ADRs. |
| 2 | **researcher** | `/docs/data-sources.md`, `/docs/research/` | Maps every public data source. Verifies API status, license, freshness. |
| 3 | **backend-dev** | `/src/ingestion/`, `/src/api/`, `/scripts/seed.sh`, `/.env.example`, `/.gitignore` | Python ingestion + FastAPI. |
| 4 | **coder** (frontend) | `/src/web/` | Next.js + TypeScript. UI lives here. |
| 5 | **tester** | `/tests/`, `/docs/methodology.md` | Methodology spec + the test suite that validates it. |
| 6 | **api-docs** | `/README.md`, `/CONTRIBUTING.md`, `/CODE_OF_CONDUCT.md`, `/SECURITY.md`, `/docs/forking-guide.md`, `/docs/launch-checklist.md` | User-facing documentation. |

The path ownership boundaries are strict — agents do not edit files outside
their assigned scope. This is what lets the swarm run in parallel without
write conflicts.

## How to run the swarm

You can run the swarm to extend DayLight in two common shapes:

### Shape A — add a new district

This is the friendliest extension. Only the architect + researcher + tester
agents need to do meaningful work; backend, frontend, and docs are largely
unchanged.

```bash
# 1. Initialize.
npx @claude-flow/cli@latest swarm init \
  --topology hierarchical \
  --max-agents 4 \
  --strategy specialized

# 2. Spawn (use Claude Code's Task tool, not the CLI alone).
#    - system-architect: produce /config/districts/<your-district>.yml
#    - researcher: produce /docs/research/<your-state>-data.md
#    - tester: extend /tests/fixtures/ and validate methodology against the new district
#    - api-docs: update README acknowledgments + screenshot
```

### Shape B — extend the methodology

When you're changing how DayLight scores donor alignment, classifies industries,
or generates synthesis, the tester agent is the lead. Run:

```bash
# tester is queen here, architect and backend-dev are workers.
# Tester produces the methodology change first, then the others adapt.
```

## Coordination rules

- **One agent, one set of paths.** Cross-cutting changes happen by handoff,
  not parallel writes to the same file.
- **No agent pushes to GitHub.** Agents write locally; the maintainer
  commits and pushes after review.
- **Neutrality enforcement is a tester concern.** Any other agent that
  introduces partisan language is reverted, regardless of intent.
- **`[TODO: verify]` is preferred to guessing.** If an agent doesn't know
  a boundary or an ID, it marks the field for verification rather than
  asserting it.
- **Files stay under 500 lines.** This is in the project's `CLAUDE.md` and
  applies to every agent's output.

## Shared memory conventions

Agents that run via claude-flow share namespaced memory. The conventions are:

| Namespace | What lives there |
|-----------|------------------|
| `daylight/schema` | Current schema version + recent changes. Architect writes, others read. |
| `daylight/sources` | Data-source status (which APIs are live, rate limits, license). Researcher writes. |
| `daylight/methodology` | Score formula constants + neutrality flag list. Tester writes. |
| `daylight/districts` | Per-district config snapshots so cross-district work doesn't lose context. |

## When the swarm shouldn't run

There are categories of contribution where spawning a swarm is overkill or
actively harmful:

- **Single-file UI fixes** — just edit the file.
- **Adding a new ZIP-code mapping** — single edit to one YAML file.
- **Methodology corrections that affect public-facing claims** — these need
  a human reviewer, not an agent. The methodology is the moat.

## Auditing agent output

The maintainer reviews agent diffs the same way they'd review a junior
contributor's PR: read the diff, sample-check a few claims against the cited
sources, run the test suite, and reject changes that introduce partisan
framing or unverified factual claims.
