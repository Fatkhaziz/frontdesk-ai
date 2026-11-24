#!/usr/bin/env bash
# Real Supabase + real Auth, with paid inference disabled only for this process.
set +vx
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f .env ]]; then
  echo 'Existing .env is required; no configuration file was created.' >&2
  exit 1
fi
set -a
source .env
set +a
if [[ "${AI_CALL_LIMIT:-10}" != '10' ]]; then
  echo 'Expected the preserved 10-attempt cap. Stopped without changing it.' >&2
  exit 1
fi
unset TESTING FRONTDESK_REHEARSAL
export XAI_API_KEY=''
export DRAFT_AI_ENABLED=0
printf '%s\n' 'Real Supabase setup: paid AI paused for this process; .env and the 10-attempt cap are unchanged.'
.venv/bin/python -m backend.local &
setup_server_pid=$!
trap 'kill "$setup_server_pid" 2>/dev/null || true' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
.venv/bin/python -m scripts.inspect_live_setup --server-pid "$setup_server_pid"
printf '%s\n' 'Open http://127.0.0.1:8000/ and sign in privately with your real confirmed Supabase owner account.'
printf '%s\n' 'Keep this Terminal open. No question or drafting request has been sent.'
wait "$setup_server_pid"
