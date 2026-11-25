#!/usr/bin/env bash
set +vx
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f .env ]]; then
  echo 'Missing project .env. Configure it before starting.' >&2
  exit 1
fi
set -a
source .env
set +a
if [[ -n "${XAI_API_KEY:-}" && -n "${XAI_MODEL:-}" ]]; then
  export QUESTION_MODE=ai
fi
exec .venv/bin/python -m backend.local
