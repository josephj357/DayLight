"""DayLight schema — Pydantic v2 models.

Mirrors /src/schema/schema.sql and /src/schema/types.ts one-to-one.
The FastAPI app in /src/api uses these as response models so the JSON
payload matches what the Next.js frontend expects.

If you change this file, also change schema.sql and types.ts.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


Party = Literal["D", "R", "I", "NPA", "L", "G", "OTHER"]
RaceLevel = Literal["federal", "state", "county", "municipal", "judicial", "special"]
ContributionSource = Literal["fec", "fl_doe", "broward_soe", "senate_lda", "other"]
DonorType = Literal["individual", "pac", "party", "corporate", "other"]
VotePosition = Literal["Yes", "Yea", "Aye", "No", "Nay", "Present", "Not Voting"]


class _CamelModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda name: name[0] + name.title().replace("_", "")[1:] if "_" in name else name,
    )


class SourceLink(_CamelModel):
    label: str
    url: str


class CandidateSummary(_CamelModel):
    id: str
    name: str
    party: str | None = None
    office: str
    district: str | None = None
    incumbent: bool = False
    total_raised: float | None = Field(default=None, alias="totalRaised")
    top_industry: str | None = Field(default=None, alias="topIndustry")
    photo_url: str | None = Field(default=None, alias="photoUrl")


class RaceSummary(_CamelModel):
    race_id: str = Field(alias="raceId")
    office: str
    level: RaceLevel
    district: str | None = None
    cycle: str
    candidates: list[CandidateSummary] = Field(default_factory=list)


class District(_CamelModel):
    id: str
    display_name: str = Field(alias="displayName")
    description: str | None = None
    state: str
    fips_state: str = Field(alias="fipsState")
    plan_id: str | None = Field(default=None, alias="planId")
    snapshot_date: str = Field(alias="snapshotDate")
    config_path: str = Field(alias="configPath")
    races: list[RaceSummary] = Field(default_factory=list)
    zip_codes: list[str] | None = Field(default=None, alias="zipCodes")


class Donor(_CamelModel):
    name: str
    amount: float
    type: DonorType | None = None
    industry: str | None = None
    cycle: str | None = None


class IndustryBreakdown(_CamelModel):
    industry: str
    amount: float
    share: float  # 0..1


class VoteRecord(_CamelModel):
    bill_id: str = Field(alias="billId")
    bill_title: str = Field(alias="billTitle")
    date: str
    vote: VotePosition
    donor_alignment_flag: bool = Field(alias="donorAlignmentFlag", default=False)
    alignment_note: str | None = Field(default=None, alias="alignmentNote")
    source_url: str | None = Field(default=None, alias="sourceUrl")


class RevolvingDoor(_CamelModel):
    organization: str
    role: str
    started_on: str | None = Field(default=None, alias="startedOn")
    contribution_total: float | None = Field(default=None, alias="contributionTotal")
    note: str | None = None


class Synthesis(_CamelModel):
    body: str
    generated_at: str = Field(alias="generatedAt")
    model_label: str | None = Field(default=None, alias="modelLabel")
    caveat: str | None = None


class CandidateDetail(CandidateSummary):
    bio: str | None = None
    top_donors: list[Donor] = Field(default_factory=list, alias="topDonors")
    industry_breakdown: list[IndustryBreakdown] = Field(default_factory=list, alias="industryBreakdown")
    synthesis: Synthesis | None = None
    votes: list[VoteRecord] = Field(default_factory=list)
    revolving_door: list[RevolvingDoor] = Field(default_factory=list, alias="revolvingDoor")
    sources: list[SourceLink] = Field(default_factory=list)
    cycle: str | None = None
    last_updated: str | None = Field(default=None, alias="lastUpdated")
    alignment_score: int | None = Field(default=None, alias="alignmentScore")


class ZipLookupResult(_CamelModel):
    district_id: str = Field(alias="districtId")
