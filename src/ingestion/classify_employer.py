"""Fallback employer → industry classifier.

OpenSecrets is the canonical source for industry classification (their bulk
data carries CRP-curated industry codes). When that bulk data is not loaded
locally, this module provides a much-cruder heuristic classifier so the UI's
"TOP INDUSTRY" / industry-breakdown panels are not empty.

**This is a stopgap, not a methodology equivalent.** Output is written to
`industry_totals` with `source = 'daylight_fallback'` so it's never confused
with OpenSecrets data. The API + UI may choose to display only one source
or label fallback rows explicitly.

How it works: each entry in `_KEYWORD_MAP` is a (substring, industry) pair.
We check the uppercased `raw_employer` against each substring; first match
wins. Order matters — put longer / more specific substrings first.

Industry names are intentionally chosen to align with OpenSecrets' published
taxonomy so an upgrade path (replace fallback rows with real OpenSecrets
rows) is a straight swap.
"""
from __future__ import annotations

import logging
import sqlite3
from collections import defaultdict

from ._common import DistrictConfig, log_ingestion

logger = logging.getLogger(__name__)

# (substring, industry). Order matters — longer + specific first.
_KEYWORD_MAP: list[tuple[str, str]] = [
    # --- Pro-Israel / foreign-policy PACs (industry naming per OpenSecrets) ---
    ("AIPAC", "Pro-Israel"),
    ("J STREET", "Pro-Israel"),
    ("PRO-ISRAEL", "Pro-Israel"),
    ("UNITED DEMOCRACY PROJECT", "Pro-Israel"),

    # --- Major law firms ---
    ("AKERMAN", "Lawyers/Law Firms"),
    ("GREENBERG TRAURIG", "Lawyers/Law Firms"),
    ("HOLLAND & KNIGHT", "Lawyers/Law Firms"),
    ("BAKER & MCKENZIE", "Lawyers/Law Firms"),
    ("LATHAM & WATKINS", "Lawyers/Law Firms"),
    ("SKADDEN", "Lawyers/Law Firms"),
    ("DLA PIPER", "Lawyers/Law Firms"),
    ("KIRKLAND & ELLIS", "Lawyers/Law Firms"),
    ("SIDLEY AUSTIN", "Lawyers/Law Firms"),
    ("MORGAN LEWIS", "Lawyers/Law Firms"),
    ("PANZA MAURER", "Lawyers/Law Firms"),     # FL law firm
    ("WEISS HANDLER", "Lawyers/Law Firms"),    # FL family-law firm
    ("STEARNS WEAVER", "Lawyers/Law Firms"),
    ("CARLTON FIELDS", "Lawyers/Law Firms"),
    (" LLP", "Lawyers/Law Firms"),
    (" P.A.", "Lawyers/Law Firms"),            # Professional Association, common FL legal entity
    # Note: NOT using bare " PA" — it matches " PARTNERS" and mis-routes
    # firms like "BALLARD PARTNERS" to Lawyers. The dotted " P.A." is safe.
    ("ATTORNEY", "Lawyers/Law Firms"),
    ("LAW FIRM", "Lawyers/Law Firms"),
    ("LAW OFFICE", "Lawyers/Law Firms"),
    ("LAW GROUP", "Lawyers/Law Firms"),

    # --- Lobbying firms ---
    ("BALLARD PARTNERS", "Lobbyists"),
    ("BROWNSTEIN HYATT", "Lobbyists"),
    ("AKIN GUMP", "Lobbyists"),
    ("BGR GROUP", "Lobbyists"),
    ("MERCURY PUBLIC AFFAIRS", "Lobbyists"),
    ("CAPITAL CITY CONSULTING", "Lobbyists"),
    ("LOBBYIST", "Lobbyists"),

    # --- Finance / Securities ---
    ("GOLDMAN SACHS", "Securities & Investment"),
    ("MORGAN STANLEY", "Securities & Investment"),
    ("BLACKSTONE", "Securities & Investment"),
    ("CARLYLE", "Securities & Investment"),
    ("KKR", "Securities & Investment"),
    ("CITADEL", "Securities & Investment"),
    ("APOLLO GLOBAL", "Securities & Investment"),
    ("BRIDGEWATER", "Securities & Investment"),
    ("RENAISSANCE TECHNOLOGIES", "Securities & Investment"),
    ("JPMORGAN", "Commercial Banks"),
    ("J.P. MORGAN", "Commercial Banks"),
    ("BANK OF AMERICA", "Commercial Banks"),
    ("WELLS FARGO", "Commercial Banks"),
    ("CITIBANK", "Commercial Banks"),
    ("CITIGROUP", "Commercial Banks"),
    # --- Investment management / private equity (broader patterns) ---
    ("SOUTHOCEAN CAPITAL", "Securities & Investment"),
    ("MERITAGE GROUP", "Securities & Investment"),
    ("CAPITAL PARTNERS", "Securities & Investment"),
    ("CAPITAL MANAGEMENT", "Securities & Investment"),
    ("INVESTMENTS LLC", "Securities & Investment"),
    ("INVESTMENT MANAGEMENT", "Securities & Investment"),
    ("PRIVATE EQUITY", "Securities & Investment"),
    ("HEDGE FUND", "Securities & Investment"),
    ("ASSET MANAGEMENT", "Securities & Investment"),
    # --- Consumer finance / credit / lending (distinct from Securities) ---
    ("ADVANCE FINANCIAL", "Finance/Credit"),
    ("AMSCOT FINANCIAL", "Finance/Credit"),
    ("AMSCOT", "Finance/Credit"),
    ("PAYDAY", "Finance/Credit"),
    ("CONSUMER FINANCE", "Finance/Credit"),
    ("CREDIT UNION", "Credit Unions"),
    # --- Insurance ---
    ("BROWN & BROWN INSURANCE", "Insurance"),
    ("BROWN AND BROWN", "Insurance"),
    ("AIG ", "Insurance"),
    ("STATE FARM", "Insurance"),
    ("ALLSTATE", "Insurance"),
    ("PROGRESSIVE INSURANCE", "Insurance"),
    ("INSURANCE BROKER", "Insurance"),
    ("INSURANCE AGENCY", "Insurance"),
    ("INSURANCE GROUP", "Insurance"),
    ("REINSURANCE", "Insurance"),
    (" INSURANCE", "Insurance"),                # leading space — only "X INSURANCE", not start of word
    # --- Automotive ---
    ("DEALER SERVICES NETWORK", "Automotive"),
    ("AUTO DEALER", "Automotive"),
    ("AUTOMOTIVE", "Automotive"),
    ("FORD MOTOR", "Automotive"),
    ("GENERAL MOTORS", "Automotive"),
    ("TOYOTA", "Automotive"),
    ("HONDA MOTOR", "Automotive"),

    # --- Real estate / development / homebuilding ---
    ("RELATED COMPANIES", "Real Estate"),
    ("BROOKFIELD", "Real Estate"),
    ("TISHMAN SPEYER", "Real Estate"),
    ("LENNAR", "Real Estate"),                 # FL-based homebuilder
    ("PULTE", "Real Estate"),
    ("D.R. HORTON", "Real Estate"),
    ("DR HORTON", "Real Estate"),
    ("TOLL BROTHERS", "Real Estate"),
    ("KB HOME", "Real Estate"),
    ("MERITAGE HOMES", "Real Estate"),
    ("REALTOR", "Real Estate"),
    ("REAL ESTATE", "Real Estate"),
    ("DEVELOPMENT GROUP", "Real Estate"),
    ("PROPERTIES", "Real Estate"),
    ("HOMEBUILDER", "Real Estate"),
    (" HOMES", "Real Estate"),                 # leading space avoids matching "HOMEMAKER"
    ("CONSTRUCTION", "Construction"),
    ("CONTRACTORS", "Construction"),
    ("BUILDERS", "Construction"),

    # --- Healthcare ---
    ("MEMORIAL HEALTHCARE", "Hospitals/Nursing Homes"),
    ("HCA HEALTHCARE", "Hospitals/Nursing Homes"),
    ("HEALTHCARE SYSTEM", "Hospitals/Nursing Homes"),
    ("MEDICAL CENTER", "Hospitals/Nursing Homes"),
    ("PHARMACEUTICAL", "Pharmaceuticals/Health Products"),
    ("PFIZER", "Pharmaceuticals/Health Products"),
    ("MERCK", "Pharmaceuticals/Health Products"),
    ("ELI LILLY", "Pharmaceuticals/Health Products"),
    ("NOVARTIS", "Pharmaceuticals/Health Products"),
    ("ASTRAZENECA", "Pharmaceuticals/Health Products"),
    ("PHYSICIAN", "Health Professionals"),
    ("DOCTOR", "Health Professionals"),
    (" MD", "Health Professionals"),
    ("DENTIST", "Health Professionals"),

    # --- Energy ---
    ("EXXON", "Oil & Gas"),
    ("CHEVRON", "Oil & Gas"),
    ("CONOCOPHILLIPS", "Oil & Gas"),
    ("FLORIDA POWER", "Electric Utilities"),
    ("FPL ", "Electric Utilities"),
    ("DUKE ENERGY", "Electric Utilities"),

    # --- Tech ---
    ("MICROSOFT", "Electronics Mfg & Equip"),
    ("GOOGLE", "Internet"),
    ("ALPHABET", "Internet"),
    ("META PLATFORMS", "Internet"),
    ("FACEBOOK", "Internet"),
    ("AMAZON", "Internet"),
    ("APPLE INC", "Electronics Mfg & Equip"),
    ("ORACLE", "Electronics Mfg & Equip"),

    # --- Retail / Consumer ---
    ("VICTORY WHOLESALE", "Retail Sales"),
    ("WALMART", "Retail Sales"),
    ("TARGET CORP", "Retail Sales"),
    ("HOME DEPOT", "Building Materials & Equipment"),

    # --- Defense / Aerospace ---
    ("LOCKHEED", "Defense Aerospace"),
    ("RAYTHEON", "Defense Aerospace"),
    ("NORTHROP GRUMMAN", "Defense Aerospace"),
    ("GENERAL DYNAMICS", "Defense Aerospace"),
    ("BOEING", "Defense Aerospace"),

    # --- Education ---
    ("UNIVERSITY OF", "Education"),
    ("STATE UNIVERSITY", "Education"),
    ("PUBLIC SCHOOLS", "Education"),
    ("SCHOOL DISTRICT", "Education"),
    ("TEACHER", "Education"),
    ("PROFESSOR", "Education"),

    # --- Non-industry buckets — kept distinct per methodology §2 ---
    ("NOT EMPLOYED", "Retired/Unemployed"),
    ("RETIRED", "Retired/Unemployed"),
    ("HOMEMAKER", "Retired/Unemployed"),
    ("SELF EMPLOYED", "Self-Employed"),
    ("SELF-EMPLOYED", "Self-Employed"),
    ("SELF", "Self-Employed"),
]

# Industries we should not display in "top 5" rollups (methodology §2 excludes
# them from concentration math). Kept here in sync with that doc.
NON_INDUSTRY_BUCKETS = {"Retired/Unemployed", "Self-Employed"}


def classify(raw_employer: str | None) -> str | None:
    """Return an industry label for the given raw employer, or None."""
    if not raw_employer:
        return None
    needle = raw_employer.upper()
    for kw, industry in _KEYWORD_MAP:
        if kw in needle:
            return industry
    return None


def run(conn: sqlite3.Connection, district: DistrictConfig) -> int:
    """Roll up `contributions` by industry using the fallback classifier.

    Only writes rows tagged `source='daylight_fallback'`. If OpenSecrets bulk
    data is later loaded, those rows can coexist (different `source` value in
    the primary key) and the API can choose which to surface.
    """
    rows = conn.execute(
        """
        SELECT candidate_id, raw_employer, amount, cycle
        FROM contributions
        WHERE candidate_id IN (
            SELECT c.id FROM candidates c
            JOIN races r ON r.id = c.race_id
            WHERE r.district_id = ?
        )
        """,
        (district.id,),
    ).fetchall()

    totals: dict[tuple[str, str, str | None], float] = defaultdict(float)
    for row in rows:
        industry = classify(row["raw_employer"])
        if not industry:
            continue
        key = (row["candidate_id"], industry, row["cycle"])
        totals[key] += float(row["amount"] or 0.0)

    written = 0
    for (cand_id, industry, cycle), amount in totals.items():
        conn.execute(
            """
            INSERT OR REPLACE INTO industry_totals
                (candidate_id, industry, amount, cycle, source)
            VALUES (?, ?, ?, ?, 'daylight_fallback')
            """,
            (cand_id, industry, amount, cycle),
        )
        written += 1
    conn.commit()
    log_ingestion(
        conn,
        "industry_classifier",
        "ok",
        rows_written=written,
        note=(
            f"district={district.id}; source=daylight_fallback "
            f"(NOT a methodology equivalent of OpenSecrets — see /docs/methodology.md)"
        ),
    )
    return written


if __name__ == "__main__":
    import sys

    from ._common import get_db, load_district_config

    district_id = sys.argv[1] if len(sys.argv) > 1 else "fl-23"
    logging.basicConfig(level=logging.INFO)
    db = get_db()
    cfg = load_district_config(district_id)
    n = run(db, cfg)
    print(f"Industry classifier (fallback): {n} rows for {district_id}")
