#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f .env ]]; then
  echo 'Missing project .env. Configure it before starting.' >&2
  exit 1
fi
set -a
source .env
set +a
exec .venv/bin/python -m backend.local
