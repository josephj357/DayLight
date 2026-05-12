"""Shared fixtures for integration tests.

Use a TEMPORARY SQLite file seeded from JSON fixtures. Never mock the database;
this is real SQL exercised against a real DB engine, just one that lives for the
duration of the test session.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures"


def _load_json(name: str) -> dict[str, Any]:
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_yaml(name: str) -> dict[str, Any]:
    import yaml  # type: ignore
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


SCHEMA_SQL = """
CREATE TABLE candidates (
    candidate_id     TEXT PRIMARY KEY,
    opensecrets_id   TEXT,
    propublica_id    TEXT,
    name             TEXT NOT NULL,
    office           TEXT NOT NULL,
    state            TEXT NOT NULL,
    district         TEXT
);

CREATE TABLE industry_totals (
    candidate_id     TEXT NOT NULL REFERENCES candidates(candidate_id),
    industry         TEXT NOT NULL,
    career_total     REAL NOT NULL,
    PRIMARY KEY (candidate_id, industry)
);

CREATE TABLE votes (
    candidate_id     TEXT NOT NULL REFERENCES candidates(candidate_id),
    bill_id          TEXT NOT NULL,
    roll_call        INTEGER NOT NULL,
    position         TEXT NOT NULL,
    vote_date        TEXT NOT NULL,
    PRIMARY KEY (candidate_id, bill_id)
);

CREATE TABLE bill_industry_map (
    bill_id          TEXT PRIMARY KEY,
    industry         TEXT NOT NULL,
    direction        INTEGER NOT NULL CHECK (direction IN (-1, 1)),
    rationale        TEXT,
    source_url       TEXT
);

CREATE TABLE district_config (
    district_id      TEXT PRIMARY KEY,
    state            TEXT NOT NULL,
    top_n            INTEGER NOT NULL,
    min_scored_votes INTEGER NOT NULL,
    revolving_door_threshold INTEGER NOT NULL
);

CREATE INDEX idx_votes_bill ON votes(bill_id);
CREATE INDEX idx_industry_totals_industry ON industry_totals(industry);
"""


def _seed_db(conn: sqlite3.Connection) -> None:
    fec = _load_json("fec_fl23_incumbent.json")
    pp = _load_json("propublica_fl23_votes.json")
    bim = _load_yaml("bill_industry_map.yaml")
    district = _load_yaml("district_fl23.yaml")

    cand = district["federal_candidates"][0]
    conn.execute(
        "INSERT INTO candidates(candidate_id, opensecrets_id, propublica_id, name, office, state, district) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            cand["candidate_id"],
            cand["opensecrets_id"],
            cand["propublica_id"],
            cand["name"],
            cand["office"],
            district["state"],
            str(district["congressional_district"]),
        ),
    )
    for industry, amount in fec["industry_totals_career"].items():
        conn.execute(
            "INSERT INTO industry_totals(candidate_id, industry, career_total) VALUES (?, ?, ?)",
            (cand["candidate_id"], industry, amount),
        )
    for v in pp["votes"]:
        conn.execute(
            "INSERT INTO votes(candidate_id, bill_id, roll_call, position, vote_date) VALUES (?, ?, ?, ?, ?)",
            (cand["candidate_id"], v["bill_id"], v["roll_call"], v["position"], v["date"]),
        )
    for bill_id, entry in bim["bills"].items():
        conn.execute(
            "INSERT INTO bill_industry_map(bill_id, industry, direction, rationale, source_url) "
            "VALUES (?, ?, ?, ?, ?)",
            (bill_id, entry["industry"], entry["direction"], entry.get("rationale"), entry.get("source_url")),
        )
    conn.execute(
        "INSERT INTO district_config(district_id, state, top_n, min_scored_votes, revolving_door_threshold) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            district["district_id"],
            district["state"],
            district["top_n_industries"],
            district["min_scored_votes_per_industry"],
            district["revolving_door_dollar_threshold"],
        ),
    )
    conn.commit()


@pytest.fixture
def seeded_db(tmp_path) -> sqlite3.Connection:
    """A temp SQLite file seeded from /tests/fixtures/. Tear down at end of test."""
    db_path = tmp_path / "daylight_test.db"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA_SQL)
    _seed_db(conn)
    yield conn
    conn.close()


@pytest.fixture
def fl23_candidate_id() -> str:
    return "H2FL23001"
