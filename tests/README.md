# DayLight tests

DayLight's tests have two jobs:

1. **Validate methodology** — every public number is reproducible and matches the
   methodology document in `/docs/methodology.md`.
2. **Smoke-test integration** — the ingestion pipeline and the API produce the
   right shapes, deterministically.

**Tests never hit live APIs.** Everything reads from `/tests/fixtures/`.

---

## Layout

```
tests/
├── README.md                     ← this file
├── conftest.py                   ← puts project root on sys.path
├── fixtures/                     ← frozen JSON / YAML for FL-23 + a synthetic district
│   ├── fec_fl23_incumbent.json
│   ├── opensecrets_fl23_incumbent.json
│   ├── propublica_fl23_votes.json
│   ├── bill_industry_map.yaml
│   ├── district_fl23.yaml
│   ├── synthetic_district.yaml
│   └── synthesis_outputs.json
├── methodology/
│   ├── alignment_score.py        ← pure-Python reference implementation
│   ├── conftest.py
│   ├── red_flags.json            ← loaded political vocabulary
│   ├── test_donor_totals.py
│   ├── test_vote_records.py
│   ├── test_industry_classification.py
│   ├── test_alignment_score.py
│   └── test_synthesis_neutrality.py
└── integration/
    ├── conftest.py               ← temp SQLite seeded from fixtures
    ├── test_pipeline.py
    ├── test_api.py
    └── test_district_config.py
```

---

## Running

```bash
# Requires: pytest, PyYAML
pip install pytest pyyaml

# All tests
pytest tests/

# One suite
pytest tests/methodology/
pytest tests/integration/

# One file
pytest tests/methodology/test_alignment_score.py -v

# One test
pytest tests/methodology/test_alignment_score.py::test_worked_example_from_methodology_section_3_6 -v
```

The tests are deterministic. If `pytest tests/` is green twice in a row on the
same commit, it stays green forever (until a fixture or the methodology
deliberately changes).

---

## What each suite validates

### `tests/methodology/`

| File | Asserts |
|------|---------|
| `test_donor_totals.py` | Our career donor totals match the OpenSecrets fixture within tolerance (max($1,000, 0.5%)). Industry rollups present. No double-counting. |
| `test_vote_records.py` | ProPublica positions are categorically valid, no duplicate roll calls or bill IDs, ISO dates, every scored vote maps to an industry the bill map agrees with. |
| `test_industry_classification.py` | Industry codes match OpenSecrets' convention, "Retired"/"Self-Employed" are kept out of industry math, taxonomy source URL is recorded. |
| `test_alignment_score.py` | Determinism, [0..100] bounds, exclusion of low-vote industries, re-normalization correctness, worked example from methodology §3.6 reproduces, symmetry around 50. |
| `test_synthesis_neutrality.py` | Red-flag vocabulary never appears in compliant outputs, always appears in non-compliant outputs (proves filter is not vacuously passing), red-flag list is symmetric across the political spectrum. |

### `tests/integration/`

| File | Asserts |
|------|---------|
| `test_pipeline.py` | A temp SQLite DB seeded from fixtures yields the same alignment score as direct fixture computation, end-to-end. |
| `test_api.py` | The `/districts/FL-23` response has the documented shape (required keys, types, JSON-serializable). |
| `test_district_config.py` | A brand-new district added via YAML alone (no code changes) drives the same scoring path as FL-23. Party labels are stored neutrally. State codes/IDs are well-formed. |

---

## Extending for a new district

Forking DayLight for your district is supposed to require **zero code changes**.
The flow is:

1. **Identify the FEC candidate IDs, OpenSecrets IDs, ProPublica member IDs** for
   every candidate on the ballot in your district.
2. **Create `/config/<district>.yaml`** following the shape of
   `tests/fixtures/district_fl23.yaml`. Set:
   - `district_id` (e.g. `CA-12`)
   - `state`
   - `top_n_industries` (5 is the V1 default)
   - `min_scored_votes_per_industry` (3 is the V1 default)
   - `revolving_door_dollar_threshold` (10000 is the V1 default)
   - `federal_candidates: [...]`, `state_candidates: [...]`, `local_candidates: [...]`
3. **Add a frozen fixture for each candidate** in `tests/fixtures/` mirroring the
   FL-23 examples. Naming convention: `<source>_<district>_<role>.json` (e.g.
   `fec_ca12_incumbent.json`).
4. **Add a parametrized case to `tests/integration/test_district_config.py`** if
   the new district has district-specific behavior worth covering. In most
   cases the existing parametric coverage is enough.
5. **Run `pytest tests/` locally and confirm green.**
6. **Open a PR** — the maintainer reviews the YAML and citations, not your code.

If a new district legitimately requires code changes (e.g. a state lobbyist
registry not yet supported by the ingestion pipeline), that goes through a
normal feature PR against `/src/` and is reviewed by backend-dev. Adding the
district itself, after the source is supported, remains a code-free PR.

---

## What's NOT here yet (deliberate)

These are owned by other agents and will plug in as the project grows. The
tests here describe the contract those agents must satisfy.

- **Live-API smoke tests** — gated behind `--run-live` (not implemented). CI
  must never run live calls.
- **End-to-end UI tests** — front-end agent owns these.
- **Performance / load tests** — out of scope for V1.
- **Security tests** — out of scope here; `npx @claude-flow/cli@latest security scan`
  per `/CLAUDE.md` is the canonical security pass.

---

## Bug? Methodology disagreement?

- **Correction to a claim** (a number you believe is wrong): see
  `/docs/methodology.md` §9 — separate process from feature PRs.
- **Bug in the test suite itself**: regular GitHub issue, no special prefix.
- **Methodology change**: PR against `/docs/methodology.md` AND
  `/tests/methodology/`. Both must move together.
