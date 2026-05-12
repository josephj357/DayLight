/**
 * DayLight schema — TypeScript types.
 *
 * Mirrors /src/schema/schema.sql and /src/schema/models.py one-to-one.
 * Frontend imports these via /src/web/lib/api.ts. Backend serializes Pydantic
 * models with field names that match these exactly.
 *
 * If you change this file, also change schema.sql and models.py — or the
 * integration tests in /tests/integration/ will fail.
 */

export type Party = "D" | "R" | "I" | "NPA" | "L" | "G" | "OTHER";

export type RaceLevel =
  | "federal"
  | "state"
  | "county"
  | "municipal"
  | "judicial"
  | "special";

export type ContributionSource =
  | "fec"
  | "fl_doe"
  | "broward_soe"
  | "senate_lda"
  | "other";

export type DonorType =
  | "individual"
  | "pac"
  | "party"
  | "corporate"
  | "other";

export type VotePosition =
  | "Yes"
  | "Yea"
  | "Aye"
  | "No"
  | "Nay"
  | "Present"
  | "Not Voting";

export interface SourceLink {
  label: string;
  url: string;
}

export interface District {
  id: string;
  displayName: string;
  description?: string;
  state: string;
  fipsState: string;
  planId?: string;
  snapshotDate: string;
  configPath: string;
  races: RaceSummary[];
  zipCodes?: string[];
}

export interface RaceSummary {
  raceId: string;
  office: string;
  level: RaceLevel;
  district?: string;
  cycle: string;
  candidates: CandidateSummary[];
}

export interface CandidateSummary {
  id: string;
  name: string;
  party?: Party | string;
  office: string;
  district?: string;
  incumbent: boolean;
  totalRaised?: number;
  topIndustry?: string;
  photoUrl?: string;
}

export interface Donor {
  name: string;
  amount: number;
  type?: DonorType;
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
  vote: VotePosition;
  donorAlignmentFlag: boolean;
  alignmentNote?: string;
  sourceUrl?: string;
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
  revolvingDoor: RevolvingDoor[];
  sources: SourceLink[];
  cycle?: string;
  lastUpdated?: string;
  alignmentScore?: number;
}
