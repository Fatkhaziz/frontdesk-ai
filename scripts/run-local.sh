#!/usr/bin/env bash
set +vx
set -euo pipefail
# One startup path: rebuild current source and preserve the spending guard.
exec bash "$(dirname "$0")/launch-showcase.sh" "$@"
