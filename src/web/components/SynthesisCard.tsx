import { Sparkles, Quote } from "lucide-react";
import type { Synthesis } from "@/lib/api";
import { formatDate } from "@/lib/utils";

interface SynthesisCardProps {
  synthesis: Synthesis | undefined;
  candidateName: string;
}

/**
 * THE killer-feature component.
 *
 * Treats the AI synthesis like an editor's note in a longform piece —
 * a deckle-edge serif callout, not a marketing banner. Visual goals:
 *  - Looks editorial. Reads like a thoughtful highlight, not a sales pitch.
 *  - The body uses a serif (Lora-style) for "this matters / read this slowly".
 *  - Clear authorship + caveat — voters need to know it's machine-generated
 *    from public data, not editorial opinion.
 */
export function SynthesisCard({ synthesis, candidateName }: SynthesisCardProps) {
  if (!synthesis) {
    return (
      <section
        aria-labelledby="synthesis-pending"
        className="rounded-2xl border border-ink-200 bg-white p-6 text-sm text-ink-500"
      >
        <h2 id="synthesis-pending" className="font-semibold text-ink-700">
          Plain-English summary
        </h2>
        <p className="mt-2">
          A synthesis for {candidateName} hasn&apos;t been generated yet. Check
          back as the cycle progresses, or open the underlying data below.
        </p>
      </section>
    );
  }

  return (
    <section
      aria-labelledby="synthesis-heading"
      className="relative overflow-hidden rounded-2xl border border-daylight-200 bg-gradient-to-b from-daylight-50 to-white shadow-card"
    >
      {/* gilt accent rule */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-daylight-400 to-transparent" />
      <div className="px-6 pt-5 pb-6 sm:px-8 sm:pt-6 sm:pb-8">
        <div className="flex items-center gap-2 text-daylight-700">
          <Sparkles className="h-4 w-4" aria-hidden="true" />
          <h2
            id="synthesis-heading"
            className="text-[11px] uppercase tracking-[0.18em] font-semibold"
          >
            Plain-English summary
          </h2>
        </div>

        <blockquote className="mt-3 relative">
          <Quote
            className="absolute -top-1 -left-1 h-5 w-5 text-daylight-300"
            aria-hidden="true"
          />
          <p className="synthesis-prose pl-6 text-[17px] sm:text-lg text-ink-900">
            {synthesis.body}
          </p>
        </blockquote>

        <footer className="mt-5 pt-4 border-t border-daylight-200/70 flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 text-xs text-ink-500">
          <span>
            Generated {formatDate(synthesis.generatedAt)}
            {synthesis.modelLabel ? ` · ${synthesis.modelLabel}` : ""}
          </span>
          <span className="max-w-md text-right">
            {synthesis.caveat ??
              "Generated from public data. Causation is not implied. See methodology."}
          </span>
        </footer>
      </div>
    </section>
  );
}
