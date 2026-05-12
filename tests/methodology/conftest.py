"""Shared fixtures for methodology tests.

All fixtures read from /tests/fixtures/. Nothing here hits a live API.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures"


def _load_json(name: str) -> dict[str, Any]:
    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_yaml(name: str) -> dict[str, Any]:
    # Local import so the test suite can be inspected without PyYAML if needed.
    import yaml  # type: ignore

    with (FIXTURE_DIR / name).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def fec_fixture() -> dict[str, Any]:
    return _load_json("fec_fl23_incumbent.json")


@pytest.fixture(scope="session")
def opensecrets_fixture() -> dict[str, Any]:
    return _load_json("opensecrets_fl23_incumbent.json")


@pytest.fixture(scope="session")
def propublica_fixture() -> dict[str, Any]:
    return _load_json("propublica_fl23_votes.json")


@pytest.fixture(scope="session")
def bill_industry_map() -> dict[str, Any]:
    return _load_yaml("bill_industry_map.yaml")


@pytest.fixture(scope="session")
def district_fl23() -> dict[str, Any]:
    return _load_yaml("district_fl23.yaml")


@pytest.fixture(scope="session")
def synthesis_outputs() -> dict[str, Any]:
    return _load_json("synthesis_outputs.json")


@pytest.fixture(scope="session")
def red_flags() -> dict[str, Any]:
    here = Path(__file__).resolve().parent
    with (here / "red_flags.json").open("r", encoding="utf-8") as f:
        return json.load(f)
