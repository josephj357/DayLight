import Link from "next/link";
import { BookOpen, ExternalLink } from "lucide-react";

/**
 * Methodology page.
 *
 * V1 embeds a hardcoded summary; the canonical document lives at
 * /docs/methodology.md (produced by the tester/docs agent). When that
 * file is rendered server-side, swap the static blocks below for the
 * generated MDX/Markdown — keep the page route stable.
 */
export default function MethodologyPage() {
  return (
    <div className="mx-auto max-w-prose px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex items-center gap-2 text-daylight-700">
        <BookOpen className="h-4 w-4" aria-hidden="true" />
        <p className="text-xs uppercase tracking-[0.18em] font-semibold">
          Methodology
        </p>
      </div>
      <h1 className="mt-3 text-3xl sm:text-4xl font-semibold tracking-tight text-ink-900">
        How DayLight works (and what it can&apos;t see)
      </h1>
      <p className="mt-3 text-ink-600">
        Plain-English explanation of where the data comes from, how the
        synthesis is generated, and where the gaps are. The full document
        lives in{" "}
        <a
          href="https://github.com/orka-labs/daylight/blob/main/docs/methodology.md"
          target="_blank"
          rel="noreferrer"
          className="underline hover:text-ink-900 inline-flex items-center gap-1"
        >
          docs/methodology.md
          <ExternalLink className="h-3 w-3" aria-hidden="true" />
        </a>
        .
      </p>

      <article className="mt-8 space-y-8 text-[15px] leading-7 text-ink-800">
        <section>
          <h2 className="text-lg font-semibold text-ink-900">Data sources</h2>
          <ul className="mt-2 list-disc list-outside pl-5 space-y-1">
            <li>
              <strong>FEC</strong> — federal candidate filings (Form 3, Form 3X)
              for U.S. House races.
            </li>
            <li>
              <strong>ProPublica Congress API</strong> — roll-call votes and
              member metadata.
            </li>
            <li>
              <strong>OpenSecrets</strong> — industry rollups for individual and
              PAC donors.
            </li>
            <li>
              <strong>Florida Division of Elections</strong> — state House,
              state Senate, county commission, school board, judicial, and soil
              & water conservation filings.
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-ink-900">
            Donor-vote alignment flag
          </h2>
          <p className="mt-2">
            A vote is flagged when the bill subject matches an industry that
            constitutes a top-5 donor cluster for the candidate this cycle.
            Matching is conservative — explicit subject tags only — to avoid
            over-flagging.
          </p>
          <p className="mt-2">
            A flag does <em>not</em> imply causation. It implies a pattern that
            voters should weigh.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-ink-900">Synthesis</h2>
          <p className="mt-2">
            The plain-English summary on each candidate page is generated from
            structured facts (top donors, top industries, flagged votes,
            revolving-door affiliations). It is templated and grounded — every
            claim links back to a public source. We deliberately avoid
            interpretive language and stick to the factual pattern.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-ink-900">What we can&apos;t see</h2>
          <ul className="mt-2 list-disc list-outside pl-5 space-y-1">
            <li>
              <strong>Dark money</strong> through 501(c)(4) social-welfare
              groups, which are not required to disclose donors.
            </li>
            <li>
              Certain <strong>independent expenditures</strong> made without
              coordination.
            </li>
            <li>
              <strong>Bundled donations</strong> laundered through shell
              entities or strawman donors — visible only if/when the FEC
              pursues enforcement.
            </li>
            <li>
              <strong>In-kind</strong> contributions from media outlets and
              issue ads that don&apos;t name a candidate.
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-ink-900">
            How to extend coverage
          </h2>
          <p className="mt-2">
            The ingestion pipeline reads from per-state adapters under{" "}
            <code className="font-mono text-sm">/src/ingestion/</code>. To add
            your state, write an adapter that produces the canonical schema in{" "}
            <code className="font-mono text-sm">/src/schema/</code> and point a
            new district config at it.
          </p>
          <p className="mt-3">
            <Link
              href="https://github.com/orka-labs/daylight"
              className="underline hover:text-ink-900"
            >
              Fork the repo on GitHub →
            </Link>
          </p>
        </section>
      </article>
    </div>
  );
}
