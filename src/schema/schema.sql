-- DayLight v1 schema (SQLite).
--
-- Design notes:
--  - One row per (candidate, cycle) — politicians can run multiple times.
--  - `source` column on contributions tells us which jurisdiction the row came from
--    (fec / fl_doe / broward_soe / etc.) so we never silently mix federal and state data.
--  - OpenSecrets-derived fields (industry classifications, donor-industry rollups) live
--    in their own tables so a future build can drop the CC BY-NC-SA layer without
--    losing the FEC-public-domain baseline.
--  - `party` is stored as an opaque short code. No D/R asymmetry anywhere in the schema.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS districts (
    id              TEXT PRIMARY KEY,            -- e.g. "fl-23"
    display_name    TEXT NOT NULL,               -- "Florida's 23rd Congressional District"
    description     TEXT,
    state           TEXT NOT NULL,               -- two-letter FIPS state abbreviation
    fips_state      TEXT NOT NULL,
    plan_id         TEXT,                        -- redistricting plan identifier
    snapshot_date   TEXT NOT NULL,               -- ISO date this district's data is pinned to
    config_path     TEXT NOT NULL                -- relative path to the YAML that defined this district
);

CREATE TABLE IF NOT EXISTS races (
    id              TEXT PRIMARY KEY,            -- e.g. "fl-23/us-house-23"
    district_id     TEXT NOT NULL REFERENCES districts(id),
    office          TEXT NOT NULL,               -- "U.S. House", "State Senate", "County Commission" etc.
    level           TEXT NOT NULL CHECK (level IN ('federal','state','county','municipal','judicial','special')),
    district_label  TEXT,                        -- "23", "SD-37", "Seat 3", "Group 24"
    cycle           TEXT NOT NULL,               -- "2024", "2026"
    ballot_order    INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_races_district ON races(district_id);

CREATE TABLE IF NOT EXISTS politicians (
    id                  TEXT PRIMARY KEY,        -- internal stable ID
    name                TEXT NOT NULL,
    bioguide_id         TEXT,                    -- federal politicians only
    fec_candidate_id    TEXT,                    -- federal
    current_office      TEXT
);
CREATE INDEX IF NOT EXISTS idx_politicians_bioguide ON politicians(bioguide_id);
CREATE INDEX IF NOT EXISTS idx_politicians_fec ON politicians(fec_candidate_id);

CREATE TABLE IF NOT EXISTS candidates (
    id              TEXT PRIMARY KEY,            -- "fl-23/us-house-23/moskowitz-jared"
    race_id         TEXT NOT NULL REFERENCES races(id),
    politician_id   TEXT REFERENCES politicians(id),
    name            TEXT NOT NULL,
    party           TEXT,                        -- opaque short code: D, R, I, NPA, L, G, OTHER
    incumbent       INTEGER NOT NULL DEFAULT 0,  -- 0 or 1
    fec_candidate_id TEXT,
    bioguide_id     TEXT,
    photo_url       TEXT,
    total_raised    REAL,
    cycle           TEXT NOT NULL,
    bio             TEXT
);
CREATE INDEX IF NOT EXISTS idx_candidates_race ON candidates(race_id);
CREATE INDEX IF NOT EXISTS idx_candidates_politician ON candidates(politician_id);

CREATE TABLE IF NOT EXISTS donors (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    type        TEXT CHECK (type IN ('individual','pac','party','corporate','other')),
    ein         TEXT,
    employer    TEXT,
    occupation  TEXT
);
CREATE INDEX IF NOT EXISTS idx_donors_name ON donors(name);

CREATE TABLE IF NOT EXISTS contributions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id    TEXT NOT NULL REFERENCES candidates(id),
    donor_id        INTEGER REFERENCES donors(id),
    amount          REAL NOT NULL,
    date            TEXT,                        -- ISO date
    cycle           TEXT,
    source          TEXT NOT NULL CHECK (source IN ('fec','fl_doe','broward_soe','senate_lda','other')),
    transaction_id  TEXT,
    industry        TEXT,                        -- OpenSecrets taxonomy (CC BY-NC-SA 3.0 — attribute)
    raw_employer    TEXT
);
CREATE INDEX IF NOT EXISTS idx_contrib_candidate ON contributions(candidate_id);
CREATE INDEX IF NOT EXISTS idx_contrib_donor ON contributions(donor_id);

CREATE TABLE IF NOT EXISTS industry_totals (
    candidate_id    TEXT NOT NULL REFERENCES candidates(id),
    industry        TEXT NOT NULL,
    amount          REAL NOT NULL,
    cycle           TEXT,
    PRIMARY KEY (candidate_id, industry, cycle)
);

CREATE TABLE IF NOT EXISTS bills (
    id              TEXT PRIMARY KEY,            -- "hr-815-118"
    congress        INTEGER NOT NULL,
    bill_type       TEXT,                        -- "hr", "s", "hres" etc.
    number          INTEGER,
    title           TEXT,
    summary         TEXT,
    sponsor_id      TEXT REFERENCES politicians(id),
    introduced_date TEXT,
    status          TEXT,
    congress_gov_url TEXT
);

CREATE TABLE IF NOT EXISTS bill_industry_map (
    bill_id     TEXT NOT NULL REFERENCES bills(id),
    industry    TEXT NOT NULL,
    direction   INTEGER NOT NULL CHECK (direction IN (-1, 1)),
    rationale   TEXT,
    source_url  TEXT,
    PRIMARY KEY (bill_id, industry)
);

CREATE TABLE IF NOT EXISTS votes (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id            TEXT NOT NULL REFERENCES candidates(id),
    bill_id                 TEXT NOT NULL REFERENCES bills(id),
    position                TEXT NOT NULL CHECK (position IN ('Yes','Yea','Aye','No','Nay','Present','Not Voting')),
    date                    TEXT NOT NULL,
    donor_alignment_flag    INTEGER DEFAULT 0,
    alignment_note          TEXT,
    source_url              TEXT
);
CREATE INDEX IF NOT EXISTS idx_votes_candidate ON votes(candidate_id);
CREATE INDEX IF NOT EXISTS idx_votes_bill ON votes(bill_id);

CREATE TABLE IF NOT EXISTS synthesis_cache (
    candidate_id    TEXT PRIMARY KEY REFERENCES candidates(id),
    body            TEXT NOT NULL,
    model_label     TEXT,
    generated_at    TEXT NOT NULL,
    input_hash      TEXT NOT NULL,
    caveat          TEXT
);

CREATE TABLE IF NOT EXISTS revolving_door (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id        TEXT NOT NULL REFERENCES candidates(id),
    organization        TEXT NOT NULL,
    role                TEXT NOT NULL,
    started_on          TEXT,
    contribution_total  REAL,
    note                TEXT,
    source_url          TEXT
);
CREATE INDEX IF NOT EXISTS idx_rdoor_candidate ON revolving_door(candidate_id);

CREATE TABLE IF NOT EXISTS source_links (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type     TEXT NOT NULL CHECK (entity_type IN ('district','race','candidate','vote','contribution')),
    entity_id       TEXT NOT NULL,
    label           TEXT NOT NULL,
    url             TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sources_entity ON source_links(entity_type, entity_id);

CREATE TABLE IF NOT EXISTS zip_district_map (
    zip         TEXT PRIMARY KEY,
    district_id TEXT NOT NULL REFERENCES districts(id)
);

CREATE TABLE IF NOT EXISTS ingestion_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source          TEXT NOT NULL,
    started_at      TEXT NOT NULL,
    finished_at     TEXT,
    status          TEXT,                        -- ok / partial / failed
    rows_written    INTEGER,
    note            TEXT
);
