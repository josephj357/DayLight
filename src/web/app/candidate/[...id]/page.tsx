import Link from "next/link";
import { notFound } from "next/navigation";
import { ChevronLeft, ExternalLink, ShieldCheck, AlertTriangle } from "lucide-react";
import { getCandidate, type SponsoredBill, type VoteRecord } from "@/lib/api";
import { DonorBarChart, IndustryDonut } from "@/components/DonorChart";
import { SynthesisCard } from "@/components/SynthesisCard";
import { RevolvingDoorBadge } from "@/components/RevolvingDoorBadge";
import { Disclaimer } from "@/components/Disclaimer";
import {
  cn,
  formatDate,
  formatUSD,
  formatUSDCompact,
  partyDotClass,
  partyKey,
  partyLabel,
} from "@/lib/utils";

interface PageProps {
  params: { id: string[] | string };
}

export default async function CandidatePage({ params }: PageProps) {
  // Candidate IDs contain slashes (e.g. "fl-23/u.s.-house-fl-23/jared-moskowitz")
  // so the route is a catch-all and params.id arrives as an array of segments.
  const idArr = Array.isArray(params.id) ? params.id : [params.id];
  const candidateId = idArr.map((s) => decodeURIComponent(s)).join("/");
  const c = await getCandidate(candidateId);
  if (!c) notFound();
  const p = partyKey(c.party);

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
      <Link
        href={
          c.district
            ? `/district/${c.district.toLowerCase().startsWith("fl-23") ? "fl-23" : "fl-23"}`
            : "/district/fl-23"
        }
        className="inline-flex items-center gap-1 text-sm text-ink-500 hover:text-ink-900"
      >
        <ChevronLeft className="h-4 w-4" aria-hidden="true" />
        Back to district
      </Link>

      {/* Header */}
      <header className="mt-3 border-b border-ink-200 pb-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span
                className={cn(
                  "inline-block h-2 w-2 rounded-full",
                  partyDotClass(p),
                )}
                aria-hidden="true"
              />
              <span className="text-[11px] uppercase tracking-wide text-ink-500">
                {partyLabel(p)}
              </span>
              {c.incumbent && (
                <span className="inline-flex items-center gap-1 rounded-full bg-daylight-100 text-daylight-800 px-2 py-0.5 text-[11px] font-medium ring-1 ring-daylight-300">
                  <ShieldCheck className="h-3 w-3" aria-hidden="true" />
                  Incumbent
                </span>
              )}
              <RevolvingDoorBadge entries={c.revolvingDoor} />
            </div>
            <h1 className="mt-2 text-3xl sm:text-4xl font-semibold tracking-tight text-ink-900">
              {c.name}
            </h1>
            <p className="mt-1 text-ink-600">{c.office}</p>
          </div>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-right text-sm">
            <div>
              <dt className="text-[11px] uppercase tracking-wide text-ink-500">
                Total raised
              </dt>
              <dd className="font-semibold text-ink-900 tabular-nums">
                {typeof c.totalRaised === "number"
                  ? formatUSDCompact(c.totalRaised)
                  : "—"}
              </dd>
            </div>
            <div>
              <dt className="text-[11px] uppercase tracking-wide text-ink-500">
                Cycle
              </dt>
              <dd className="font-semibold text-ink-900 tabular-nums">
                {c.cycle ?? "—"}
              </dd>
            </div>
          </dl>
        </div>
        {c.bio && (
          <p className="mt-4 max-w-3xl text-ink-600 text-[15px]">{c.bio}</p>
        )}
      </header>

      {/* Synthesis: hero feature */}
      <div className="mt-8">
        <SynthesisCard synthesis={c.synthesis} candidateName={c.name} />
      </div>

      {/* Donors + industry side by side */}
      <section
        aria-labelledby="donors-heading"
        className="mt-10 grid gap-6 lg:grid-cols-2"
      >
        <article className="rounded-2xl border border-ink-200 bg-white p-5 shadow-card">
          <header className="flex items-baseline justify-between gap-3">
            <h2 id="donors-heading" className="text-base font-semibold text-ink-900">
              Top 5 donors
            </h2>
            <span className="text-xs text-ink-500">Disclosed contributions</span>
          </header>
          <div className="mt-4">
            <DonorBarChart donors={c.topDonors} />
          </div>
          <Disclaimer className="mt-3" />
        </article>

        <article className="rounded-2xl border border-ink-200 bg-white p-5 shadow-card">
          <header className="flex items-baseline justify-between gap-3">
            <h2 className="text-base font-semibold text-ink-900">
              Industry concentration
            </h2>
            <span className="text-xs text-ink-500">% of disclosed total</span>
          </header>
          <div className="mt-4">
            <IndustryDonut breakdown={c.industryBreakdown} />
          </div>
        </article>
      </section>

      {/* Votes */}
      <section
        aria-labelledby="votes-heading"
        className="mt-10 rounded-2xl border border-ink-200 bg-white shadow-card overflow-hidden"
      >
        <header className="px-5 pt-5 pb-3 flex items-baseline justify-between gap-3 border-b border-ink-100">
          <h2 id="votes-heading" className="text-base font-semibold text-ink-900">
            Vote history
          </h2>
          <span className="text-xs text-ink-500">
            Flag = vote aligned with top-donor cluster
          </span>
        </header>
        <VotesTable votes={c.votes} />
      </section>

      {/* Sponsored bills */}
      <section
        aria-labelledby="sponsored-heading"
        className="mt-10 rounded-2xl border border-ink-200 bg-white shadow-card overflow-hidden"
      >
        <header className="px-5 pt-5 pb-3 border-b border-ink-100">
          <h2 id="sponsored-heading" className="text-base font-semibold text-ink-900">
            Sponsored legislation
          </h2>
          <p className="text-[11px] text-ink-500 mt-0.5">
            Bills authored by this member (not cosponsored). Source: Congress.gov.
          </p>
        </header>
        <SponsoredBillsList bills={c.sponsoredBills ?? []} />
      </section>

      {/* Sources */}
      <section
        aria-labelledby="sources-heading"
        className="mt-10 rounded-2xl border border-ink-200 bg-ink-50 p-5"
      >
        <h2
          id="sources-heading"
          className="text-sm font-semibold text-ink-900 uppercase tracking-wide"
        >
          Sources
        </h2>
        <ul className="mt-2 space-y-1 text-sm">
          {c.sources.map((s) => (
            <li key={s.url}>
              <a
                href={s.url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 text-ink-700 hover:text-ink-950 underline-offset-2 hover:underline"
              >
                <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
                {s.label}
              </a>
            </li>
          ))}
        </ul>
        {c.lastUpdated && (
          <p className="mt-3 text-xs text-ink-500">
            Last refreshed {formatDate(c.lastUpdated)}.
          </p>
        )}
      </section>
    </div>
  );
}

function SponsoredBillsList({ bills }: { bills: SponsoredBill[] }) {
  if (!bills || bills.length === 0) {
    return (
      <p className="px-5 py-6 text-sm text-ink-500">
        No sponsored bills found for this member in the current data window.
      </p>
    );
  }
  return (
    <ul className="divide-y divide-ink-100">
      {bills.map((b) => (
        <li key={b.billId} className="px-5 py-3 flex items-start gap-3">
          <span className="mt-0.5 inline-flex items-center rounded bg-ink-100 px-1.5 py-0.5 text-[10px] font-mono uppercase text-ink-700">
            {b.billId}
          </span>
          <div className="min-w-0 flex-1">
            <p className="text-sm text-ink-900">{b.title}</p>
            {(b.introducedDate || b.policyArea) && (
              <p className="text-[11px] text-ink-500 mt-0.5">
                {b.introducedDate && <>Introduced {formatDate(b.introducedDate)}</>}
                {b.introducedDate && b.policyArea && " · "}
                {b.policyArea}
              </p>
            )}
          </div>
          {b.sourceUrl && (
            <a
              href={b.sourceUrl}
              target="_blank"
              rel="noreferrer"
              className="ml-auto text-[11px] text-ink-500 hover:text-ink-900 inline-flex items-center gap-0.5 whitespace-nowrap"
              aria-label={`Open ${b.billId} on Congress.gov`}
            >
              <ExternalLink className="h-3 w-3" aria-hidden="true" />
              source
            </a>
          )}
        </li>
      ))}
    </ul>
  );
}

function VotesTable({ votes }: { votes: VoteRecord[] }) {
  if (votes.length === 0) {
    return (
      <p className="px-5 py-6 text-sm text-ink-500">
        No vote history available — this office may not have a public roll-call
        record (most local/judicial races don&apos;t).
      </p>
    );
  }
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead className="bg-ink-50 text-left text-[11px] uppercase tracking-wide text-ink-500">
          <tr>
            <th className="px-5 py-2 font-medium">Bill</th>
            <th className="px-5 py-2 font-medium">Date</th>
            <th className="px-5 py-2 font-medium">Vote</th>
            <th className="px-5 py-2 font-medium">Alignment</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-ink-100">
          {votes.map((v) => (
            <tr key={v.billId} className="align-top">
              <td className="px-5 py-3 max-w-md">
                <p className="font-medium text-ink-900">{v.billTitle}</p>
                <p className="text-[11px] text-ink-500">{v.billId}</p>
              </td>
              <td className="px-5 py-3 text-ink-700 tabular-nums whitespace-nowrap">
                {formatDate(v.date)}
              </td>
              <td className="px-5 py-3">
                <VoteBadge vote={v.vote} />
              </td>
              <td className="px-5 py-3">
                {v.donorAlignmentFlag ? (
                  <div className="inline-flex items-start gap-1.5 text-flag-alignment">
                    <AlertTriangle
                      className="h-3.5 w-3.5 mt-0.5 shrink-0"
                      aria-hidden="true"
                    />
                    <span className="text-xs">
                      {v.alignmentNote ?? "Aligned with top-donor cluster."}
                    </span>
                  </div>
                ) : (
                  <span className="text-xs text-ink-500">No flag.</span>
                )}
                {v.sourceUrl && (
                  <a
                    href={v.sourceUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-1 inline-flex items-center gap-1 text-[11px] text-ink-500 hover:text-ink-900"
                  >
                    <ExternalLink className="h-3 w-3" aria-hidden="true" />
                    Source
                  </a>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function VoteBadge({ vote }: { vote: VoteRecord["vote"] }) {
  const styles: Record<VoteRecord["vote"], string> = {
    Yea: "bg-ink-100 text-ink-900 ring-ink-300",
    Nay: "bg-ink-100 text-ink-900 ring-ink-300",
    Present: "bg-ink-50 text-ink-600 ring-ink-200",
    "No Vote": "bg-ink-50 text-ink-500 ring-ink-200",
  };
  return (
    <span
      className={cn(
        "inline-block rounded-full px-2 py-0.5 text-[11px] font-medium ring-1 tabular-nums",
        styles[vote],
      )}
    >
      {vote}
    </span>
  );
}

// keep an explicit reference so formatUSD isn't tree-shaken out by future edits.
const _kept = formatUSD;
void _kept;
