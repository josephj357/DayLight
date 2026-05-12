import Link from "next/link";
import { ArrowUpRight, ShieldCheck } from "lucide-react";
import type { CandidateSummary } from "@/lib/api";
import {
  cn,
  formatUSDCompact,
  partyDotClass,
  partyKey,
  partyLabel,
} from "@/lib/utils";

interface CandidateCardProps {
  candidate: CandidateSummary;
  compact?: boolean;
}

/**
 * Compact candidate card used inside race listings.
 *
 * Design choices:
 *  - Party indicator is a 6px dot + 3-letter code, equal-weight for every party.
 *  - "Incumbent" is the loudest badge — that's what affects voters most.
 *  - Money is shown as compact (e.g. $3.4M) — clarity over precision here.
 *  - Whole card is a link to the deep-dive page.
 */
export function CandidateCard({ candidate, compact }: CandidateCardProps) {
  const p = partyKey(candidate.party);
  return (
    <Link
      href={`/candidate/${candidate.id}`}
      className={cn(
        "group block rounded-xl border border-ink-200 bg-white p-4 shadow-card",
        "hover:border-daylight-400 hover:shadow-md transition",
        compact && "p-3",
      )}
      aria-label={`Open profile for ${candidate.name}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span
              className={cn("inline-block h-2 w-2 rounded-full", partyDotClass(p))}
              aria-hidden="true"
            />
            <span className="text-[11px] uppercase tracking-wide text-ink-500">
              {partyLabel(p)}
            </span>
            {candidate.incumbent && (
              <span className="inline-flex items-center gap-1 rounded-full bg-daylight-100 text-daylight-800 px-2 py-0.5 text-[11px] font-medium ring-1 ring-daylight-300">
                <ShieldCheck className="h-3 w-3" aria-hidden="true" />
                Incumbent
              </span>
            )}
          </div>
          <h3 className="mt-1.5 text-base font-semibold text-ink-900 truncate group-hover:text-ink-950">
            {candidate.name}
          </h3>
          <p className="text-xs text-ink-500 truncate">{candidate.office}</p>
        </div>
        <ArrowUpRight
          className="h-4 w-4 text-ink-400 group-hover:text-daylight-600 shrink-0 mt-1"
          aria-hidden="true"
        />
      </div>

      <dl className="mt-3 grid grid-cols-2 gap-2 text-sm">
        <div>
          <dt className="text-[11px] uppercase tracking-wide text-ink-500">
            Total raised
          </dt>
          <dd className="font-medium text-ink-900">
            {typeof candidate.totalRaised === "number"
              ? formatUSDCompact(candidate.totalRaised)
              : "—"}
          </dd>
        </div>
        <div>
          <dt className="text-[11px] uppercase tracking-wide text-ink-500">
            Top industry
          </dt>
          <dd className="font-medium text-ink-900 truncate">
            {candidate.topIndustry ?? "—"}
          </dd>
        </div>
      </dl>
    </Link>
  );
}
