#!/usr/bin/env bash
set -euo pipefail

# System deps (macOS): brew install tesseract poppler

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FASTAPI_DIR="$ROOT_DIR/fastapi"
WEB_APP_DIR="$ROOT_DIR/web-app"

cleanup() {
  trap - EXIT INT TERM
  kill 0 2>/dev/null || true
}

trap cleanup EXIT INT TERM

if [[ ! -d "$FASTAPI_DIR/.venv" ]]; then
  echo "Creating Python virtual environment in fastapi/.venv..."
  python3 -m venv "$FASTAPI_DIR/.venv"
  "$FASTAPI_DIR/.venv/bin/pip" install -r "$FASTAPI_DIR/requirements.txt"
  "$FASTAPI_DIR/.venv/bin/playwright" install chromium
fi

if [[ ! -f "$FASTAPI_DIR/.env" ]]; then
  echo "Warning: fastapi/.env not found. Copy fastapi/.env.example and set OPENAI_API_KEY."
fi

if [[ ! -d "$WEB_APP_DIR/node_modules" ]]; then
  echo "Installing Next.js dependencies..."
  npm install --prefix "$WEB_APP_DIR"
fi

echo "Starting FastAPI on http://localhost:8000"
(
  cd "$FASTAPI_DIR"
  source .venv/bin/activate
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
) &

echo "Starting Next.js on http://localhost:3000"
(
  cd "$WEB_APP_DIR"
  npm run dev
) &

wait
