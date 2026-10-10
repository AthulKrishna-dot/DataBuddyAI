#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}/../../databuddy-ai"
BASE_PATH="${BASE_PATH:-}"
BASE_PATH="${BASE_PATH#/}"
BASE_PATH="${BASE_PATH%/}"

cd "$APP_DIR"

streamlit_args=(
  --server.port "${PORT:-5000}"
  --server.address 0.0.0.0
  --server.headless true
)

if [[ -n "$BASE_PATH" ]]; then
  streamlit_args+=(--server.baseUrlPath "$BASE_PATH")
fi

exec python -m streamlit run app.py "${streamlit_args[@]}"
