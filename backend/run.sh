#!/usr/bin/env bash
# Investor — launch script. Binds to 0.0.0.0 so the app is reachable on your LAN.
# Usage: ./run.sh   (or: ./run.sh --port 9000)
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

PORT=8000
while [[ $# -gt 0 ]]; do
  case "$1" in
    --port) PORT="$2"; shift 2;;
    *) echo "Unknown arg: $1" >&2; exit 1;;
  esac
done

# Create/activate a local venv if needed.
if [[ ! -d .venv ]]; then
  echo "Creating virtualenv…"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

if [[ ! -f .venv/installed.lock ]]; then
  echo "Installing dependencies…"
  pip install -q -r requirements.txt
  touch .venv/installed.lock
fi

echo "Investor running at http://0.0.0.0:${PORT}  (open http://localhost:${PORT})"
exec python -m app.main --port "$PORT" 2>/dev/null || exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
