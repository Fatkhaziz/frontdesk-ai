#!/usr/bin/env bash
# One setup command after pulling this release. Never changes the paid-call cap.
set -euo pipefail
set +x
cd "$(dirname "$0")/.."
if [[ ! -f .env ]]; then
  echo 'The existing project .env is required. Use your configured Mac checkout.' >&2
  exit 1
fi
if ! command -v node >/dev/null 2>&1 && [[ -f "$HOME/.nvm/nvm.sh" ]]; then
  source "$HOME/.nvm/nvm.sh"
fi
command -v npm >/dev/null 2>&1 || { echo 'Node.js/npm is required.' >&2; exit 1; }
[[ -x .venv/bin/python ]] || python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm ci --prefix frontend --no-audit --no-fund
npm run build --prefix frontend
set -a
source .env
set +a
if [[ -n "${XAI_API_KEY:-}" && -n "${XAI_MODEL:-}" ]]; then
  export QUESTION_MODE=ai
fi
.venv/bin/python -m backend.verify_integration --apply-pending
if [[ "${1:-}" == '--with-examples' ]]; then
  .venv/bin/python -m scripts.seed_showcase --confirm-synthetic
fi
echo 'Setup complete. AI attempt cap was preserved. Starting the local app on port 8000.'
exec .venv/bin/python -m backend.local
