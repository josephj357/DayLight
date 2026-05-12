/**
 * Typed API client for the DayLight backend (FastAPI, /src/api).
 *
 * INTEGRATION NOTE for backend-dev:
 * The shapes below are the contract this UI consumes. If /src/schema/types.ts
 * is produced by the architect, we should swap these for those imports.
 * For v1 the routes assumed are:
 *   GET /districts/{id}         -> District
 *   GET /candidates/{id}        -> CandidateDetail
 *   GET /search/zip/{zip}       -> { districtId: string }
 *
 * The client falls back to the local mock fixtures when the backend is
 * unreachable so the UI can be developed standalone.
 */

import { mockDistrict, mockCandidate } from "./mock";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

/* ------------------------- shared types ------------------------- */

export type Party = "D" | "R" | "I" | "NPA" | "L" | "G" | "OTHER" | string;

export interface SourceLink {
  label: string;
  url: string;
}

export interface RaceSummary {
  raceId: string;
  office: string;
  district?: string;
  level: "federal" | "state" | "county" | "municipal" | "judicial" | "special";
  candidates: CandidateSummary[];
}

export interface CandidateSummary {
  id: string;
  name: string;
  party: Party;
  office: string;
  district?: string;
  incumbent: boolean;
  totalRaised?: number;
  topIndustry?: string;
  photoUrl?: string;
}

export interface District {
  id: string;
  displayName: string;
  description?: string;
  races: RaceSummary[];
  zipCodes?: string[];
}

export interface Donor {
  name: string;
  amount: number;
  type?: "individual" | "pac" | "party" | "corporate" | "other";
  industry?: string;
  cycle?: string;
}

export interface IndustryBreakdown {
  industry: string;
  amount: number;
  share: number;
}

export interface VoteRecord {
  billId: string;
  billTitle: string;
  date: string;
  vote: "Yea" | "Nay" | "Present" | "No Vote";
  donorAlignmentFlag: boolean;
  alignmentNote?: string;
  sourceUrl?: string;
}

export interface SponsoredBill {
  billId: string;
  title: string;
  introducedDate?: string;
  status?: string;
  sourceUrl?: string;
  policyArea?: string;
}

export interface RevolvingDoor {
  organization: string;
  role: string;
  startedOn?: string;
  contributionTotal?: number;
  note?: string;
}

export interface Synthesis {
  body: string;
  generatedAt: string;
  modelLabel?: string;
  caveat?: string;
}

export interface CandidateDetail extends CandidateSummary {
  bio?: string;
  topDonors: Donor[];
  industryBreakdown: IndustryBreakdown[];
  synthesis?: Synthesis;
  votes: VoteRecord[];
  sponsoredBills: SponsoredBill[];
  revolvingDoor: RevolvingDoor[];
  sources: SourceLink[];
  cycle?: string;
  lastUpdated?: string;
}

/* ------------------------- fetch helpers ------------------------- */

async function safeFetch<T>(path: string, fallback: T): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      next: { revalidate: 300 },
      headers: { Accept: "application/json" },
    });
    if (!res.ok) return fallback;
    return (await res.json()) as T;
  } catch {
    return fallback;
  }
}

/* ------------------------- public API ------------------------- */

export async function getDistrict(id: string): Promise<District> {
  return safeFetch<District>(
    `/districts/${encodeURIComponent(id)}`,
    mockDistrict(id),
  );
}

export async function getCandidate(id: string): Promise<CandidateDetail> {
  return safeFetch<CandidateDetail>(
    `/candidates/${encodeURIComponent(id)}`,
    mockCandidate(id),
  );
}

/** ZIP -> district routing. v1 only knows 33064 (and nearby) -> fl-23. */
export async function resolveZip(
  zip: string,
): Promise<{ districtId: string } | null> {
  const trimmed = zip.trim();
  const staticMap: Record<string, string> = {
    "33064": "fl-23",
    "33060": "fl-23",
    "33062": "fl-23",
    "33063": "fl-23",
    "33065": "fl-23",
    "33066": "fl-23",
    "33067": "fl-23",
    "33068": "fl-23",
  };
  const fallback = staticMap[trimmed] ? { districtId: staticMap[trimmed] } : null;
  return safeFetch<{ districtId: string } | null>(
    `/search/zip/${encodeURIComponent(trimmed)}`,
    fallback,
  );
}
