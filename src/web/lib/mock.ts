/**
 * Mock fixtures for local UI development.
 *
 * Used as a fallback when the FastAPI backend is unreachable so the
 * UI renders standalone. NOT a source of truth — backend output wins.
 *
 * Numbers are illustrative placeholders, not real campaign-finance data.
 */

import type {
  District,
  CandidateDetail,
  CandidateSummary,
  RaceSummary,
} from "./api";

function cand(
  id: string,
  name: string,
  party: string,
  office: string,
  opts: Partial<CandidateSummary> = {},
): CandidateSummary {
  return {
    id,
    name,
    party,
    office,
    incumbent: false,
    totalRaised: 0,
    ...opts,
  };
}

function race(
  raceId: string,
  office: string,
  level: RaceSummary["level"],
  candidates: CandidateSummary[],
  district?: string,
): RaceSummary {
  return { raceId, office, level, candidates, district };
}

export function mockDistrict(id: string): District {
  // For now, only fl-23 is fleshed out. Other IDs share the same skeleton.
  return {
    id: id || "fl-23",
    displayName: "Florida — FL-23 (Broward County)",
    description:
      "U.S. House district FL-23 covers most of Broward County. This view stacks every race a FL-23 voter will see — federal down to soil & water conservation.",
    zipCodes: ["33064", "33060", "33062", "33063", "33065", "33066", "33067", "33068"],
    races: [
      race(
        "us-house-fl-23",
        "U.S. House",
        "federal",
        [
          cand("jared-moskowitz", "Jared Moskowitz", "D", "U.S. House FL-23", {
            incumbent: true,
            totalRaised: 3_420_000,
            topIndustry: "Pro-Israel",
          }),
          cand("joe-kaufman", "Joe Kaufman", "R", "U.S. House FL-23", {
            totalRaised: 188_000,
            topIndustry: "Retired",
          }),
        ],
        "FL-23",
      ),
      race(
        "fl-state-house-100",
        "FL State House",
        "state",
        [
          cand("hillary-cassel", "Hillary Cassel", "R", "FL State House HD-101", {
            incumbent: true,
            totalRaised: 412_000,
            topIndustry: "Real estate",
          }),
          cand("debra-tendrich", "Debra Tendrich", "D", "FL State House HD-101", {
            totalRaised: 96_000,
            topIndustry: "Education",
          }),
        ],
        "HD-101",
      ),
      race(
        "fl-state-senate-35",
        "FL State Senate",
        "state",
        [
          cand("rosalind-osgood", "Rosalind Osgood", "D", "FL State Senate SD-32", {
            incumbent: true,
            totalRaised: 521_000,
            topIndustry: "Education",
          }),
        ],
        "SD-32",
      ),
      race(
        "broward-commission-d2",
        "Broward County Commission",
        "county",
        [
          cand("mark-bogen", "Mark Bogen", "D", "Broward Commission Dist. 2", {
            incumbent: true,
            totalRaised: 240_000,
            topIndustry: "Real estate",
          }),
          cand("challenger-bogen", "Open Seat Challenger", "NPA", "Broward Commission Dist. 2", {
            totalRaised: 12_300,
            topIndustry: "Small business",
          }),
        ],
        "Dist. 2",
      ),
      race(
        "broward-school-board-2",
        "Broward School Board",
        "county",
        [
          cand("sarah-leonardi", "Sarah Leonardi", "NPA", "Broward School Board Dist. 3", {
            incumbent: true,
            totalRaised: 78_000,
            topIndustry: "Education",
          }),
          cand("brenda-fam", "Brenda Fam", "NPA", "Broward School Board Dist. 6", {
            incumbent: true,
            totalRaised: 64_500,
            topIndustry: "Lawyers/Law firms",
          }),
        ],
        "At-large",
      ),
      race(
        "circuit-court-17",
        "17th Judicial Circuit Court",
        "judicial",
        [
          cand("judge-alvarado", "Carlos Alvarado", "NPA", "17th Circuit Court Grp. 14", {
            incumbent: true,
            totalRaised: 142_000,
            topIndustry: "Lawyers/Law firms",
          }),
          cand("judge-cohen", "Rachel Cohen", "NPA", "17th Circuit Court Grp. 14", {
            totalRaised: 88_000,
            topIndustry: "Lawyers/Law firms",
          }),
        ],
      ),
      race(
        "county-court-17",
        "Broward County Court",
        "judicial",
        [
          cand("judge-mendez", "Luis Mendez", "NPA", "Broward County Court Grp. 7", {
            incumbent: true,
            totalRaised: 41_000,
            topIndustry: "Lawyers/Law firms",
          }),
        ],
      ),
      race(
        "soil-water-3",
        "Soil & Water Conservation",
        "special",
        [
          cand("swc-jones", "Pat Jones", "NPA", "Soil & Water Cons. Group 3", {
            totalRaised: 0,
            topIndustry: "Volunteer",
          }),
          cand("swc-rivera", "Maria Rivera", "NPA", "Soil & Water Cons. Group 3", {
            totalRaised: 250,
            topIndustry: "Volunteer",
          }),
        ],
      ),
    ],
  };
}

export function mockCandidate(id: string): CandidateDetail {
  // Default fleshed-out fixture is the incumbent; other IDs reuse with name swap.
  const isMoskowitz = id === "jared-moskowitz" || id === "";
  const base: CandidateSummary = isMoskowitz
    ? {
        id: "jared-moskowitz",
        name: "Jared Moskowitz",
        party: "D",
        office: "U.S. House FL-23",
        district: "FL-23",
        incumbent: true,
        totalRaised: 3_420_000,
        topIndustry: "Pro-Israel",
      }
    : {
        id,
        name: id
          .split("-")
          .map((p) => p.charAt(0).toUpperCase() + p.slice(1))
          .join(" "),
        party: "NPA",
        office: "Down-ballot race",
        incumbent: false,
        totalRaised: 0,
      };

  return {
    ...base,
    bio:
      "Representative for Florida's 23rd congressional district. Former Florida Division of Emergency Management director. This page summarizes publicly disclosed campaign finance and votes.",
    cycle: "2024",
    lastUpdated: "2026-04-30",
    topDonors: [
      { name: "Pro-Israel America PAC", amount: 412_500, type: "pac", industry: "Pro-Israel" },
      { name: "NorPAC", amount: 188_300, type: "pac", industry: "Pro-Israel" },
      { name: "Blackstone Group", amount: 96_200, type: "corporate", industry: "Real estate" },
      { name: "AIPAC affiliated donors", amount: 81_700, type: "individual", industry: "Pro-Israel" },
      { name: "Florida Power & Light PAC", amount: 64_400, type: "pac", industry: "Electric utilities" },
    ],
    industryBreakdown: [
      { industry: "Pro-Israel", amount: 902_000, share: 0.28 },
      { industry: "Real estate", amount: 412_000, share: 0.13 },
      { industry: "Lawyers/Law firms", amount: 318_000, share: 0.10 },
      { industry: "Securities & investment", amount: 244_000, share: 0.075 },
      { industry: "Electric utilities", amount: 188_000, share: 0.058 },
      { industry: "Health professionals", amount: 144_000, share: 0.045 },
      { industry: "Other", amount: 1_212_000, share: 0.372 },
    ],
    synthesis: {
      body:
        "Rep. Moskowitz campaigns on a strong-defense, pro-Israel platform. His single largest donor cluster — pro-Israel PACs and associated individual donors — accounts for roughly 28% of disclosed contributions this cycle. On the May 2024 supplemental aid package that included $14B for Israeli defense, he voted Yea. On a separate vote to condition aid on humanitarian access, he voted Nay. Real-estate-linked donors are his second-largest cluster; he co-sponsored a bill expanding the 1031 like-kind exchange treatment that benefits real-estate investors. None of this is unusual for an incumbent in this district — but it is the alignment voters should know about before voting.",
      generatedAt: "2026-04-30T12:00:00Z",
      modelLabel: "synthesis-v1",
      caveat:
        "Generated from public FEC and ProPublica data. Causation is not implied. See methodology.",
    },
    votes: [
      {
        billId: "HR-815-118",
        billTitle: "Israel Security Supplemental Appropriations (HR 815)",
        date: "2024-04-20",
        vote: "Yea",
        donorAlignmentFlag: true,
        alignmentNote: "Aligned with top donor cluster (pro-Israel PACs).",
        sourceUrl: "https://www.congress.gov/bill/118th-congress/house-bill/815",
      },
      {
        billId: "HR-7691-118",
        billTitle: "Condition Foreign Aid on Humanitarian Access Amendment",
        date: "2024-04-19",
        vote: "Nay",
        donorAlignmentFlag: true,
        alignmentNote: "Vote opposed conditioning aid donor cluster opposes.",
        sourceUrl: "https://www.congress.gov/bill/118th-congress/house-bill/7691",
      },
      {
        billId: "HR-3938-118",
        billTitle: "Build the Wall and Deport Them All Act (procedural)",
        date: "2024-03-12",
        vote: "Nay",
        donorAlignmentFlag: false,
        sourceUrl: "https://www.congress.gov/",
      },
      {
        billId: "HR-3935-118",
        billTitle: "FAA Reauthorization Act of 2024",
        date: "2024-05-15",
        vote: "Yea",
        donorAlignmentFlag: false,
        sourceUrl: "https://www.congress.gov/",
      },
    ],
    revolvingDoor: isMoskowitz
      ? [
          {
            organization: "Disney World (former lobbyist for)",
            role: "Lobbyist, 2014–2018",
            contributionTotal: 22_400,
            note:
              "Disney-affiliated donors have given $22.4K across career to candidate committee.",
          },
        ]
      : [],
    sources: [
      {
        label: "FEC candidate page",
        url: "https://www.fec.gov/data/candidate/H2FL23139/",
      },
      {
        label: "ProPublica Congress profile",
        url: "https://projects.propublica.org/represent/members/M001257",
      },
      {
        label: "OpenSecrets profile",
        url: "https://www.opensecrets.org/members-of-congress/jared-moskowitz/summary?cid=N00046752",
      },
    ],
  };
}
