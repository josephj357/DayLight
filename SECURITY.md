# Security policy

## Reporting a vulnerability

Two channels, in order of preference:

1. **GitHub Security Advisory** — open a private advisory at
   <https://github.com/josephj357/DayLight/security/advisories/new>. This is
   the right venue for anything that could affect users of forks or hosted
   instances.

2. **Direct email** — for matters that need to stay private even from a
   draft advisory, email the maintainer. Address is in the GitHub profile of
   the repository owner. Please put `[DayLight security]` in the subject.

Whichever channel you use, please include:

- A description of the vulnerability and its impact.
- The version (commit SHA) you tested against.
- Steps to reproduce or a proof-of-concept.
- Any suggested mitigation.

## What's in scope

- Vulnerabilities in DayLight's own code (`/src/`, `/scripts/`).
- Methodology flaws that would let a contributor systematically bias output
  for or against a party (this is a security-grade concern for this project,
  not merely a quality issue).
- Data-exposure problems — anything that leaks API keys, scraped HTML, or
  ingested data beyond what's intended to be public.

## What's out of scope

- **Factual disputes about specific politicians.** These go through the
  `[Correction]` issue process described in `CONTRIBUTING.md`, not through
  a security advisory.
- **Self-XSS** that requires a user to paste hostile content into their own
  browser console.
- **Issues in third-party data sources** (FEC, Congress.gov, OpenSecrets,
  state portals). Report those to the source maintainer.

## Disclosure timeline

DayLight follows a standard 90-day coordinated-disclosure window:

- **Day 0:** Report received and acknowledged within 5 business days.
- **Day 0–30:** Triage and reproduction. We confirm severity.
- **Day 30–60:** Fix developed and tested.
- **Day 60–90:** Fix released; reporter credited (if they consent).
- **Day 90:** Public disclosure if the issue is unresolved.

We will compress this timeline aggressively if the issue is actively being
exploited or affects deployed forks.

## Supported versions

DayLight is a gift project — there is no formal support contract. That said,
the maintainer will accept security PRs against the current `main` branch
for as long as the project is alive. Forks are responsible for backporting
fixes to their own deployments.

| Version | Supported |
|---------|-----------|
| `main` (latest) | ✓ |
| Tagged release `v0.x` | best-effort |
| Any older tag | community-only |

## Out-of-band: methodology integrity

DayLight's whole value comes from voters trusting that the data is treated
identically across parties. If you discover a systemic methodology bias —
not a single bad record, but a process problem that would produce skewed
output even with correct data — please report it as a security advisory
rather than a normal issue. This category is rare but it's the one we care
about most.
