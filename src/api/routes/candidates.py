"""GET /candidates/{id} — deep candidate view."""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

SCHEMA_DIR = Path(__file__).resolve().parent.parent.parent / "schema"
sys.path.insert(0, str(SCHEMA_DIR.parent))
from schema.models import (  # noqa: E402
    CandidateDetail,
    Donor,
    IndustryBreakdown,
    RevolvingDoor,
    SourceLink,
    Synthesis,
    VoteRecord,
)

from ..db import fetchall, fetchone

router = APIRouter()


def _top_donors(candidate_id: str) -> list[Donor]:
    rows = fetchall(
        """
        SELECT
            COALESCE(d.name, c.raw_employer) AS name,
            SUM(c.amount) AS amount,
            COALESCE(d.type, 'other') AS type,
            c.industry AS industry,
            c.cycle AS cycle
        FROM contributions c
        LEFT JOIN donors d ON d.id = c.donor_id
        WHERE c.candidate_id = ?
        GROUP BY name, type, industry, cycle
        ORDER BY amount DESC
        LIMIT 5
        """,
        (candidate_id,),
    )
    return [
        Donor(
            name=r["name"] or "Unknown",
            amount=float(r["amount"] or 0.0),
            type=r["type"],
            industry=r["industry"],
            cycle=r["cycle"],
        )
        for r in rows
    ]


def _industry_breakdown(candidate_id: str) -> list[IndustryBreakdown]:
    rows = fetchall(
        """
        SELECT industry, amount FROM industry_totals
        WHERE candidate_id = ?
        ORDER BY amount DESC
        """,
        (candidate_id,),
    )
    total = sum(float(r["amount"] or 0.0) for r in rows) or 1.0
    return [
        IndustryBreakdown(
            industry=r["industry"],
            amount=float(r["amount"] or 0.0),
            share=float(r["amount"] or 0.0) / total,
        )
        for r in rows
    ]


def _votes(candidate_id: str) -> list[VoteRecord]:
    rows = fetchall(
        """
        SELECT v.bill_id, b.title, v.date, v.position, v.donor_alignment_flag,
               v.alignment_note, v.source_url
        FROM votes v
        JOIN bills b ON b.id = v.bill_id
        WHERE v.candidate_id = ?
        ORDER BY v.date DESC
        LIMIT 20
        """,
        (candidate_id,),
    )
    return [
        VoteRecord(
            billId=r["bill_id"],
            billTitle=r["title"] or r["bill_id"],
            date=r["date"],
            vote=r["position"],
            donorAlignmentFlag=bool(r["donor_alignment_flag"]),
            alignmentNote=r["alignment_note"],
            sourceUrl=r["source_url"],
        )
        for r in rows
    ]


def _revolving_door(candidate_id: str) -> list[RevolvingDoor]:
    rows = fetchall(
        """
        SELECT organization, role, started_on, contribution_total, note
        FROM revolving_door WHERE candidate_id = ?
        ORDER BY contribution_total DESC
        """,
        (candidate_id,),
    )
    return [
        RevolvingDoor(
            organization=r["organization"],
            role=r["role"],
            startedOn=r["started_on"],
            contributionTotal=float(r["contribution_total"]) if r["contribution_total"] else None,
            note=r["note"],
        )
        for r in rows
    ]


def _synthesis(candidate_id: str) -> Synthesis | None:
    row = fetchone(
        "SELECT body, model_label, generated_at, caveat FROM synthesis_cache WHERE candidate_id = ?",
        (candidate_id,),
    )
    if not row:
        return None
    return Synthesis(
        body=row["body"],
        generatedAt=row["generated_at"],
        modelLabel=row["model_label"],
        caveat=row["caveat"],
    )


def _sources(candidate_id: str) -> list[SourceLink]:
    rows = fetchall(
        "SELECT label, url FROM source_links WHERE entity_type = 'candidate' AND entity_id = ?",
        (candidate_id,),
    )
    return [SourceLink(label=r["label"], url=r["url"]) for r in rows]


@router.get("/candidates/{candidate_id}", response_model=CandidateDetail)
def get_candidate(candidate_id: str) -> CandidateDetail:
    row = fetchone(
        """
        SELECT c.id, c.name, c.party, c.incumbent, c.total_raised, c.photo_url,
               c.bio, c.cycle, r.office, r.district_label
        FROM candidates c
        JOIN races r ON r.id = c.race_id
        WHERE c.id = ?
        """,
        (candidate_id,),
    )
    if not row:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

    return CandidateDetail(
        id=row["id"],
        name=row["name"],
        party=row["party"],
        office=row["office"],
        district=row["district_label"],
        incumbent=bool(row["incumbent"]),
        totalRaised=row["total_raised"],
        photoUrl=row["photo_url"],
        bio=row["bio"],
        cycle=row["cycle"],
        topDonors=_top_donors(candidate_id),
        industryBreakdown=_industry_breakdown(candidate_id),
        synthesis=_synthesis(candidate_id),
        votes=_votes(candidate_id),
        revolvingDoor=_revolving_door(candidate_id),
        sources=_sources(candidate_id),
    )
