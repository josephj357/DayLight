import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Tailwind class merger. */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/** USD formatter — whole dollars by default. */
export function formatUSD(value: number, opts?: { cents?: boolean }): string {
  const fractionDigits = opts?.cents ? 2 : 0;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  }).format(Number.isFinite(value) ? value : 0);
}

/** Compact USD: $1.2K, $3.4M. */
export function formatUSDCompact(value: number): string {
  if (!Number.isFinite(value)) return "$0";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

/** Percent formatter: 0.123 -> "12.3%". */
export function formatPercent(value: number, digits = 1): string {
  if (!Number.isFinite(value)) return "0%";
  return `${(value * 100).toFixed(digits)}%`;
}

/** ISO date -> "May 12, 2026". */
export function formatDate(iso: string | undefined | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/**
 * Equal-weight party styling. Every party gets the same visual
 * footprint — a small dot + 1-3 letter code. No red/blue dominance.
 */
export type PartyKey = "D" | "R" | "I" | "NPA" | "L" | "G" | "OTHER";

export function partyKey(input: string | undefined | null): PartyKey {
  const v = (input ?? "").trim().toUpperCase();
  if (v.startsWith("D")) return "D";
  if (v.startsWith("R")) return "R";
  if (v === "I" || v.startsWith("IND")) return "I";
  if (v === "NPA") return "NPA";
  if (v === "L" || v.startsWith("LIB")) return "L";
  if (v === "G" || v.startsWith("GRE")) return "G";
  return "OTHER";
}

export function partyDotClass(p: PartyKey): string {
  switch (p) {
    case "D":
      return "bg-party-dem";
    case "R":
      return "bg-party-rep";
    case "I":
    case "NPA":
    case "L":
    case "G":
    case "OTHER":
    default:
      return "bg-party-ind";
  }
}

export function partyLabel(p: PartyKey): string {
  switch (p) {
    case "D":
      return "Dem";
    case "R":
      return "Rep";
    case "I":
      return "Ind";
    case "NPA":
      return "NPA";
    case "L":
      return "Lib";
    case "G":
      return "Grn";
    default:
      return "Other";
  }
}

/** Slugify for IDs / URLs. */
export function slugify(input: string): string {
  return input
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/** Title-case helper for office names. */
export function titleCase(input: string): string {
  return input.replace(/\w\S*/g, (t) =>
    t.charAt(0).toUpperCase() + t.slice(1).toLowerCase()
  );
}
