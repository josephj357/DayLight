import Link from "next/link";
import { ArrowRight, Eye, EyeOff, GitFork } from "lucide-react";
import { ZipForm } from "./_components/ZipForm";

export default function LandingPage() {
  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-b from-daylight-50 via-white to-white border-b border-ink-200">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
          <p className="text-xs uppercase tracking-[0.2em] text-daylight-700 font-semibold">
            Civic transparency · open source · AGPL-3.0
          </p>
          <h1 className="mt-4 text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight text-ink-900 max-w-3xl">
            See who funds the politicians on{" "}
            <span className="text-daylight-700">YOUR ballot.</span>
          </h1>
          <p className="mt-5 text-lg text-ink-600 max-w-2xl">
            Federal down to school board. We surface the donor patterns,
            industry concentration, and donor-vote alignment that nobody else
            clearly shows for down-ballot races.
          </p>

          <div className="mt-8 max-w-xl">
            <ZipForm />
            <p className="mt-2 text-xs text-ink-500">
              v1 covers ZIP 33064 — Broward County, FL-23 + every down-ballot
              race a voter there sees.
            </p>
          </div>

          <div className="mt-6">
            <Link
              href="/district/fl-23"
              className="inline-flex items-center gap-1.5 text-sm font-medium text-daylight-700 hover:text-daylight-900"
            >
              Skip the form, see FL-23 now
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
        </div>
      </section>

      {/* Three cards: what / can't / fork */}
      <section className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid gap-5 sm:grid-cols-3">
          <FeatureCard
            icon={<Eye className="h-5 w-5" aria-hidden="true" />}
            title="What this shows"
            body="Top donors, industry concentration, donor-vote alignment flags, revolving-door ties, and a plain-English summary that connects them."
          />
          <FeatureCard
            icon={<EyeOff className="h-5 w-5" aria-hidden="true" />}
            title="What this can't see"
            body="Dark money under 501(c)(4)s, certain independent expenditures, and bundled donations laundered through shell entities are not in the public record."
          />
          <FeatureCard
            icon={<GitFork className="h-5 w-5" aria-hidden="true" />}
            title="How to fork it for your district"
            body="The data pipeline and UI are open source. Drop in your state's filings and you have a transparency portal for your county tomorrow."
            href="https://github.com/orka-labs/daylight"
            cta="See it on GitHub"
          />
        </div>
      </section>

      {/* Closing */}
      <section className="border-t border-ink-200 bg-white">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-12 text-center">
          <p className="text-sm text-ink-600">
            Built as a gift by the Orka Labs community. Free to use, free to
            fork. AGPL-3.0.
          </p>
        </div>
      </section>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  body,
  href,
  cta,
}: {
  icon: React.ReactNode;
  title: string;
  body: string;
  href?: string;
  cta?: string;
}) {
  return (
    <article className="rounded-xl border border-ink-200 bg-white p-6 shadow-card flex flex-col">
      <div className="flex items-center gap-2 text-daylight-700">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-daylight-100 ring-1 ring-daylight-300">
          {icon}
        </span>
        <h2 className="text-sm font-semibold tracking-tight text-ink-900">
          {title}
        </h2>
      </div>
      <p className="mt-3 text-sm text-ink-600 flex-1">{body}</p>
      {href && cta && (
        <a
          href={href}
          target="_blank"
          rel="noreferrer"
          className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-daylight-700 hover:text-daylight-900"
        >
          {cta}
          <ArrowRight className="h-4 w-4" aria-hidden="true" />
        </a>
      )}
    </article>
  );
}
