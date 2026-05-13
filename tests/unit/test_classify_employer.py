"""Tests for the fallback employer classifier.

This isn't a methodology equivalent of OpenSecrets — but the keyword map IS
load-bearing for the user-facing Industry Concentration panel, so
regressions are visible. The tests below pin a handful of known mappings
plus the most-recently-fixed bug (" PA" no longer mis-routes " PARTNERS"
firms to Lawyers).
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make src/ingestion importable when running pytest from repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from ingestion.classify_employer import classify  # noqa: E402


def test_unknown_employer_returns_none():
    assert classify("ACME UNKNOWN CORP") is None
    assert classify("") is None
    assert classify(None) is None


def test_non_industry_buckets_are_classified():
    assert classify("NOT EMPLOYED") == "Retired/Unemployed"
    assert classify("RETIRED") == "Retired/Unemployed"
    assert classify("HOMEMAKER") == "Retired/Unemployed"
    assert classify("SELF") == "Self-Employed"
    assert classify("SELF-EMPLOYED") == "Self-Employed"


def test_lobbying_firms_route_to_lobbyists_not_lawyers():
    # Regression: bare " PA" used to match " PARTNERS" and mis-route these
    # to Lawyers/Law Firms. Lock the correct routing in.
    assert classify("BALLARD PARTNERS") == "Lobbyists"
    assert classify("CAPITAL CITY CONSULTING") == "Lobbyists"


def test_securities_partners_route_correctly():
    # "X CAPITAL PARTNERS" should be Securities & Investment, not Lawyers.
    assert classify("SOUTHOCEAN CAPITAL PARTNERS") == "Securities & Investment"
    assert classify("MERITAGE GROUP LP") == "Securities & Investment"


def test_law_firms_with_dotted_pa_or_llp():
    assert classify("PANZA MAURER P.A.") == "Lawyers/Law Firms"
    assert classify("WACHTELL LIPTON LLP") == "Lawyers/Law Firms"
    assert classify("GREENBERG TRAURIG") == "Lawyers/Law Firms"


def test_finance_credit_distinct_from_securities():
    # Consumer lending != investment management.
    assert classify("ADVANCE FINANCIAL") == "Finance/Credit"
    assert classify("AMSCOT FINANCIAL") == "Finance/Credit"


def test_insurance_classification():
    assert classify("BROWN & BROWN INSURANCE") == "Insurance"
    assert classify("STATE FARM") == "Insurance"


def test_real_estate_and_construction():
    assert classify("LENNAR CORP") == "Real Estate"
    assert classify("PULTE HOMES") == "Real Estate"
    assert classify("AAA CONSTRUCTION") == "Construction"


def test_automotive():
    assert classify("DEALER SERVICES NETWORK, INC") == "Automotive"
    assert classify("TOYOTA MOTOR SALES") == "Automotive"


def test_pro_israel_keywords():
    # Religiously neutral methodology: industry name follows the OpenSecrets
    # taxonomy ("Pro-Israel"). Same row would exist for any other foreign-
    # policy industry once we add equivalent keywords.
    assert classify("AIPAC") == "Pro-Israel"
    assert classify("J STREET") == "Pro-Israel"


def test_case_insensitive():
    assert classify("ballard partners") == classify("BALLARD PARTNERS")
    assert classify("Lennar Corp") == classify("LENNAR CORP")


def test_substring_match_works():
    # "AKERMAN LLP" should hit AKERMAN first (more specific than " LLP").
    assert classify("AKERMAN LLP") == "Lawyers/Law Firms"
    # And a bare " LLP" suffix should still classify even if firm is unknown.
    assert classify("OBSCURE & UNKNOWN LLP") == "Lawyers/Law Firms"
