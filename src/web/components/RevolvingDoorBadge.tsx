"use client";

import * as React from "react";
import * as Popover from "@radix-ui/react-popover";
import { DoorOpen, ExternalLink } from "lucide-react";
import type { RevolvingDoor } from "@/lib/api";
import { formatUSD } from "@/lib/utils";

interface RevolvingDoorBadgeProps {
  entries: RevolvingDoor[];
}

/**
 * Revolving-door flag.
 *
 * Render as a single quiet badge in the candidate header. Clicking it
 * opens a Radix popover with the list of organizations + roles + the
 * career-contribution totals tying them back to the candidate.
 *
 * Why this is a separate component: the data is sparse — most down-ballot
 * candidates have none — but when it exists, voters should not have to
 * scroll past charts to find it.
 */
export function RevolvingDoorBadge({ entries }: RevolvingDoorBadgeProps) {
  if (!entries || entries.length === 0) return null;

  const total = entries.reduce(
    (sum, e) => sum + (e.contributionTotal ?? 0),
    0,
  );

  return (
    <Popover.Root>
      <Popover.Trigger asChild>
        <button
          type="button"
          className="inline-flex items-center gap-1.5 rounded-full bg-flag-alignment/10 text-flag-alignment ring-1 ring-flag-alignment/40 px-2.5 py-1 text-[11px] font-medium hover:bg-flag-alignment/15 focus:outline-none focus-visible:ring-2"
          aria-label={`${entries.length} revolving-door tie${entries.length > 1 ? "s" : ""} — open details`}
        >
          <DoorOpen className="h-3 w-3" aria-hidden="true" />
          Revolving-door tie{entries.length > 1 ? "s" : ""}
          <span className="text-ink-500 font-normal">
            · {formatUSD(total)}
          </span>
        </button>
      </Popover.Trigger>
      <Popover.Portal>
        <Popover.Content
          sideOffset={8}
          className="z-50 w-[min(92vw,22rem)] rounded-xl border border-ink-200 bg-white p-4 shadow-lg"
        >
          <div className="flex items-start gap-2">
            <DoorOpen className="h-4 w-4 text-flag-alignment mt-0.5" aria-hidden="true" />
            <div className="min-w-0">
              <p className="text-sm font-semibold text-ink-900">
                Revolving-door affiliations
              </p>
              <p className="mt-0.5 text-xs text-ink-500">
                Organizations the candidate has lobbied for, sat on the board of,
                or otherwise been compensated by — with totals of related
                campaign contributions back to them.
              </p>
            </div>
          </div>
          <ul className="mt-3 space-y-3 text-sm">
            {entries.map((e, i) => (
              <li
                key={`${e.organization}-${i}`}
                className="border-t border-ink-100 pt-3 first:border-t-0 first:pt-0"
              >
                <p className="font-medium text-ink-900">{e.organization}</p>
                <p className="text-xs text-ink-600">{e.role}</p>
                {typeof e.contributionTotal === "number" && (
                  <p className="mt-1 text-xs text-flag-alignment">
                    {formatUSD(e.contributionTotal)} contributed back to candidate
                  </p>
                )}
                {e.note && (
                  <p className="mt-1 text-xs text-ink-500">{e.note}</p>
                )}
              </li>
            ))}
          </ul>
          <p className="mt-3 text-[11px] text-ink-500 inline-flex items-center gap-1">
            <ExternalLink className="h-3 w-3" aria-hidden="true" />
            Sourced from lobbying disclosures and FEC filings.
          </p>
          <Popover.Arrow className="fill-white" />
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  );
}
