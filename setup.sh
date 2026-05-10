#!/usr/bin/env bash
# One-shot local setup: creates a Python venv, installs backend deps, installs frontend deps.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Error: $PYTHON_BIN not found. Install Python 3.10+." >&2
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  echo "Error: node not found. Install Node 18+." >&2
  exit 1
fi

echo "==> Setting up backend"
cd "$ROOT_DIR/backend"
if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements.txt
deactivate

echo "==> Setting up frontend"
cd "$ROOT_DIR/frontend"
npm install

echo
echo "Done. Start the app with: ./run.sh"
