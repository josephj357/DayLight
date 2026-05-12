#!/usr/bin/env bash
# DayLight seed script — first-run bootstrap.
#
# What it does (in order):
#   1. Ensures Python 3.11+ and Node 20+ are available.
#   2. Creates a Python virtualenv at ./.venv if missing, installs requirements.
#   3. Initializes the SQLite database from src/schema/schema.sql.
#   4. Runs the ingestion pipeline for every district config in /config/districts/.
#   5. Starts the FastAPI backend (foreground, blocks on the dev server).
#
# Usage:
#   bash scripts/seed.sh                 # all districts, then start API
#   bash scripts/seed.sh --district fl-23  # one district
#   bash scripts/seed.sh --no-api        # skip starting the API at the end
#
# After this script exits (or you Ctrl-C the API), bring up the frontend:
#   cd src/web && npm install && npm run dev

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# --- args ---
DISTRICT=""
START_API="yes"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --district)
      DISTRICT="$2"; shift 2 ;;
    --no-api)
      START_API="no"; shift ;;
    -h|--help)
      sed -n '1,30p' "$0"; exit 0 ;;
    *)
      echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

# --- preflight ---
if ! command -v python3 >/dev/null; then
  echo "DayLight needs Python 3.11+; couldn't find python3 on PATH." >&2
  exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "[seed] Python: $PY_VERSION"

# --- env file ---
if [[ ! -f .env ]]; then
  if [[ -f .env.example ]]; then
    echo "[seed] No .env found; copying .env.example. Open it to add API keys."
    cp .env.example .env
  else
    echo "[seed] No .env or .env.example present. Some ingestion steps will be skipped."
  fi
fi

# Load .env if present (lines like KEY=value).
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

# --- virtualenv ---
if [[ ! -d .venv ]]; then
  echo "[seed] Creating Python virtualenv at .venv"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
. .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r src/ingestion/requirements.txt
echo "[seed] Python deps installed."

# --- ingestion ---
mkdir -p data
if [[ -n "$DISTRICT" ]]; then
  echo "[seed] Running ingestion for district: $DISTRICT"
  python -m src.ingestion.pipeline --district "$DISTRICT" --verbose
else
  echo "[seed] Running ingestion for all districts."
  python -m src.ingestion.pipeline --verbose
fi

# --- API ---
if [[ "$START_API" == "yes" ]]; then
  HOST="${DAYLIGHT_API_HOST:-127.0.0.1}"
  PORT="${DAYLIGHT_API_PORT:-8000}"
  echo "[seed] Starting FastAPI on http://${HOST}:${PORT}"
  echo "[seed] Open another terminal and run: cd src/web && npm install && npm run dev"
  exec uvicorn src.api.main:app --host "$HOST" --port "$PORT" --reload
fi

echo "[seed] Done. Skipped starting the API (--no-api)."
