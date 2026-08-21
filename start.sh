#!/usr/bin/env bash
# C.A.R.N.I.V.A.L launcher — creates a venv on first run, then starts the dashboard.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "[carnival] creating virtualenv (.venv)…"
  python3 -m venv .venv
  ./.venv/bin/pip install --quiet --upgrade pip
  ./.venv/bin/pip install --quiet -r requirements.txt
fi

if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo "[carnival] created .env from template — add your GEMINI_API_KEY there."
fi

exec ./.venv/bin/python main.py "$@"
