"""DayLight FastAPI application entry.

Run locally:
    uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000

Run via the script:
    bash scripts/seed.sh   (then it stays up)
"""
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import candidates, districts

app = FastAPI(
    title="DayLight API",
    description=(
        "Read-only API for the DayLight civic-transparency project. "
        "Serves district + candidate views over public campaign-finance and "
        "voting data. See https://github.com/josephj357/DayLight."
    ),
    version="0.1.0",
)


def _cors_origins() -> list[str]:
    env = os.environ.get("DAYLIGHT_CORS_ORIGINS")
    if env:
        return [o.strip() for o in env.split(",") if o.strip()]
    return ["http://localhost:3000", "http://127.0.0.1:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_methods=["GET"],
    allow_headers=["Accept", "Content-Type"],
    allow_credentials=False,
)

app.include_router(districts.router)
app.include_router(candidates.router)


@app.get("/", include_in_schema=False)
def root() -> dict:
    return {
        "name": "DayLight API",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "routes": ["/districts/{id}", "/candidates/{id}", "/search/zip/{zip}"],
    }


@app.get("/healthz", include_in_schema=False)
def healthz() -> dict:
    return {"status": "ok"}
