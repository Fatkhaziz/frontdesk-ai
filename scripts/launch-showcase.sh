#!/usr/bin/env bash
# Run in the configured checkout. No credentials are printed or copied.
set +vx
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f .env || ! -x .venv/bin/python ]]; then
  echo 'Use the existing configured FrontDesk AI checkout with .env and .venv.' >&2
  exit 1
fi
set -a
source .env
set +a
export QUESTION_MODE=ai DRAFT_AI_ENABLED=1 AI_CALL_LIMIT=200
export AI_AUTHORIZED_REMAINING_USD=4.97 AI_PREPARATION_BUDGET_USD=1.00 AI_PRESENTATION_RESERVE_USD=3.50
.venv/bin/python -m backend.verify_integration --apply-pending
.venv/bin/python -m backend.practice "${1:---practice}"
npm run build --prefix frontend
exec .venv/bin/python -m backend.local
