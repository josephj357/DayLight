import { notFound } from "next/navigation";
import Link from "next/link";
import { Building2, Gavel, Landmark, School, Sprout, Vote, MapPin } from "lucide-react";
import { getDistrict, type RaceSummary } from "@/lib/api";
import { CandidateCard } from "@/components/CandidateCard";
import { Disclaimer } from "@/components/Disclaimer";

/** v1 statically pre-renders FL-23. Future: more districts. */
export function generateStaticParams() {
  return [{ district: "fl-23" }];
}

interface PageProps {
  params: { district: string };
}

export default async function DistrictPage({ params }: PageProps) {
  const district = await getDistrict(params.district);
  if (!district) notFound();

  // Stable display order — federal first, then state, county, judicial, special.
  const order: RaceSummary["level"][] = [
    "federal",
    "state",
    "county",
    "municipal",
    "judicial",
    "special",
  ];
  const races = [...district.races].sort(
    (a, b) => order.indexOf(a.level) - order.indexOf(b.level),
  );

  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <header className="border-b border-ink-200 pb-6">
        <p className="text-xs uppercase tracking-[0.18em] text-ink-500 inline-flex items-center gap-1.5">
          <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
          District profile
        </p>
        <h1 className="mt-2 text-3xl sm:text-4xl font-semibold tracking-tight text-ink-900">
          {district.displayName}
        </h1>
        {district.description && (
          <p className="mt-2 max-w-2xl text-ink-600">{district.description}</p>
        )}
        {district.zipCodes && district.zipCodes.length > 0 && (
          <p className="mt-3 text-xs text-ink-500">
            ZIP codes:{" "}
            <span className="text-ink-700">{district.zipCodes.join(", ")}</span>
          </p>
        )}
      </header>

      {/* Race sections */}
      <div className="mt-8 space-y-10">
        {races.map((race) => (
          <RaceSection key={race.raceId} race={race} />
        ))}
      </div>

      <div className="mt-12">
        <Disclaimer variant="block" />
      </div>

      <p className="mt-6 text-sm text-ink-500">
        Don&apos;t see your race? This is v1 — only FL-23 / Broward County is
        live.{" "}
        <Link href="/methodology" className="underline hover:text-ink-900">
          See methodology & how to extend coverage
        </Link>
        .
      </p>
    </div>
  );
}

function RaceSection({ race }: { race: RaceSummary }) {
  return (
    <section aria-labelledby={`race-${race.raceId}`} className="">
      <div className="flex items-center gap-2.5">
        <RaceIcon level={race.level} />
        <h2
          id={`race-${race.raceId}`}
          className="text-lg sm:text-xl font-semibold tracking-tight text-ink-900"
        >
          {race.office}
        </h2>
        {race.district && (
          <span className="text-xs uppercase tracking-wide text-ink-500">
            · {race.district}
          </span>
        )}
        <span className="ml-auto text-xs text-ink-500">
          {race.candidates.length}{" "}
          {race.candidates.length === 1 ? "candidate" : "candidates"}
        </span>
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {race.candidates.map((c) => (
          <CandidateCard key={c.id} candidate={c} />
        ))}
      </div>
    </section>
  );
}

function RaceIcon({ level }: { level: RaceSummary["level"] }) {
  const className =
    "h-5 w-5 text-daylight-700 shrink-0";
  switch (level) {
    case "federal":
      return <Landmark className={className} aria-hidden="true" />;
    case "state":
      return <Building2 className={className} aria-hidden="true" />;
    case "county":
      return <School className={className} aria-hidden="true" />;
    case "judicial":
      return <Gavel className={className} aria-hidden="true" />;
    case "special":
      return <Sprout className={className} aria-hidden="true" />;
    default:
      return <Vote className={className} aria-hidden="true" />;
  }
}
