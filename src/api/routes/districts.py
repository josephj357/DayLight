"""GET /districts/{id} and GET /search/zip/{zip} routes."""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

# Import shared schema models from /src/schema/.
SCHEMA_DIR = Path(__file__).resolve().parent.parent.parent / "schema"
sys.path.insert(0, str(SCHEMA_DIR.parent))
from schema.models import (  # noqa: E402  (path setup happens above)
    CandidateSummary,
    District,
    RaceSummary,
    ZipLookupResult,
)

from ..db import fetchall, fetchone

router = APIRouter()


def _candidate_summary(row) -> CandidateSummary:
    return CandidateSummary(
        id=row["id"],
        name=row["name"],
        party=row["party"],
        office=row["office"],
        district=row["district_label"],
        incumbent=bool(row["incumbent"]),
        totalRaised=row["total_raised"],
        topIndustry=row["top_industry"] if "top_industry" in row.keys() else None,
        photoUrl=row["photo_url"],
    )


@router.get("/districts/{district_id}", response_model=District)
def get_district(district_id: str) -> District:
    district_row = fetchone(
        """
        SELECT id, display_name, description, state, fips_state, plan_id, snapshot_date, config_path
        FROM districts WHERE id = ?
        """,
        (district_id,),
    )
    if not district_row:
        raise HTTPException(status_code=404, detail=f"District {district_id} not found")

    race_rows = fetchall(
        """
        SELECT id, office, level, district_label, cycle
        FROM races WHERE district_id = ?
        ORDER BY
            CASE level
              WHEN 'federal' THEN 0
              WHEN 'state' THEN 1
              WHEN 'county' THEN 2
              WHEN 'municipal' THEN 3
              WHEN 'judicial' THEN 4
              WHEN 'special' THEN 5
              ELSE 6
            END,
            ballot_order, id
        """,
        (district_id,),
    )

    races: list[RaceSummary] = []
    for race in race_rows:
        candidate_rows = fetchall(
            """
            SELECT c.id, c.name, c.party, c.incumbent, c.total_raised, c.photo_url,
                   r.office, r.district_label
            FROM candidates c
            JOIN races r ON r.id = c.race_id
            WHERE c.race_id = ?
            ORDER BY c.incumbent DESC, c.name
            """,
            (race["id"],),
        )
        candidates = [_candidate_summary(c) for c in candidate_rows]
        races.append(
            RaceSummary(
                raceId=race["id"],
                office=race["office"],
                level=race["level"],
                district=race["district_label"],
                cycle=race["cycle"],
                candidates=candidates,
            )
        )

    zip_rows = fetchall(
        "SELECT zip FROM zip_district_map WHERE district_id = ? ORDER BY zip",
        (district_id,),
    )

    return District(
        id=district_row["id"],
        displayName=district_row["display_name"],
        description=district_row["description"],
        state=district_row["state"],
        fipsState=district_row["fips_state"],
        planId=district_row["plan_id"],
        snapshotDate=district_row["snapshot_date"],
        configPath=district_row["config_path"],
        races=races,
        zipCodes=[z["zip"] for z in zip_rows] or None,
    )


@router.get("/search/zip/{zip_code}", response_model=ZipLookupResult | None)
def resolve_zip(zip_code: str) -> ZipLookupResult | None:
    # Defensive: only allow 5-digit US ZIPs through to the DB.
    if not zip_code.isdigit() or len(zip_code) != 5:
        return None
    row = fetchone("SELECT district_id FROM zip_district_map WHERE zip = ?", (zip_code,))
    if not row:
        return None
    return ZipLookupResult(districtId=row["district_id"])
