# ADR-001 — License: GNU AGPL-3.0

**Status:** Accepted
**Date:** 2026-05-12

## Context

DayLight is a civic-transparency project being released as a gift. The license
choice has direct consequences for:

- Whether anyone can fork DayLight, run it as a closed SaaS product, and never
  give changes back to the public.
- Whether a partisan PAC, a campaign-consulting firm, or a single-issue group
  can take the codebase, embed a biased fork as their own "transparency tool,"
  and avoid scrutiny.
- Whether downstream civic-tech projects find the license inviting.

The three plausible choices were MIT/Apache (permissive), GPL-3.0 (copyleft on
distribution), and AGPL-3.0 (copyleft on distribution *and* network use).

## Decision

DayLight is licensed under **GNU AGPL-3.0**.

The methodology document (`/docs/methodology.md`) is separately licensed under
**CC BY-SA 4.0** so other civic-tech projects can adopt and adapt the methodology
without inheriting AGPL on their codebase.

## Rationale

The AGPL's network-use clause is the load-bearing one for this project. A
permissive license would let any well-funded firm wrap DayLight as a closed
service, modify it to bias outputs, and never disclose what they changed. The
AGPL closes that loophole: any networked deployment of a modified DayLight
must publish the modifications under the same license.

GPL-3.0 alone is insufficient because the dominant deployment model for a
civic web app is SaaS, where binaries are never distributed to end users —
GPL's copyleft trigger never fires.

The CC BY-SA 4.0 split on methodology is deliberate. Methodology is a
specification, not code. Forcing AGPL on any project that *uses* the
methodology would have a chilling effect on adoption by civic-tech orgs whose
own codebases are AGPL-incompatible. CC BY-SA is the standard license for
open methodologies and is well-understood by journalists, academics, and
nonprofits.

## Consequences

- **A commercial deployment of DayLight is possible.** AGPL is not
  "non-commercial"; for-profit hosting is allowed as long as modifications are
  released. This matters because some forks may be funded by foundation grants
  that require an LLC structure.

- **Some corporate contributors can't participate.** A handful of large
  companies (notably some at Google and Amazon) prohibit their engineers from
  contributing to AGPL projects. This is an acceptable cost — they were
  unlikely to be the contributors who matter for a civic-data project.

- **Forks of the OpenSecrets-derived data are bound by CC BY-NC-SA 3.0.**
  AGPL applies to the code; OpenSecrets' bulk data carries its own
  non-commercial restriction. See `/docs/research/data-licensing.md`. The
  schema deliberately isolates OpenSecrets-derived columns so a future
  commercial deployment could swap that layer out.

- **AGPL is recognized as an OSI-approved license.** GitHub renders the
  badge correctly and listing on awesome-civictech is unaffected.

## Alternatives considered

- **MIT / Apache 2.0** — rejected. The SaaS-loophole cost outweighs the
  marginal adoption gain. Civic-tech tools that go MIT typically end up
  captured by commercial wrappers (see various paywalled vote-record sites
  built on free data).

- **GPL-3.0** — rejected. Doesn't trigger on the dominant deployment shape
  (network-only). Same cost as AGPL with less protection.

- **No license / All rights reserved** — rejected. Defeats the entire "gift"
  framing.

- **Custom license** — rejected. Custom licenses are an OSI anti-pattern; they
  produce uncertainty and discourage adoption.
