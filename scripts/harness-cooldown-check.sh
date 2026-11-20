#!/usr/bin/env bash
# Copyright (c) 2023-2026 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.
#
# Fails if any version pinned in poetry.lock was uploaded to Harness less than 7 days ago.
# Poetry only applies its cool-down when it resolves, so this verifies the committed lock file.
#
# Usage: scripts/harness-cooldown-check.sh [--ci]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/harness-common.sh"

if [[ "${1:-}" != "--ci" ]]; then
  harness_load_dotenv
fi
harness_require_credentials

cd "$HARNESS_PROJECT_DIR"

venv_python="$(harness_venv_python)"
if [[ -z "$venv_python" ]]; then
  echo "No .venv found; run scripts/harness-setup.sh first." >&2
  exit 1
fi

work_dir="$(mktemp -d)"
trap 'rm -rf "$work_dir"' EXIT

# --without-urls keeps the credentialed index-url from .venv/pip.conf in effect.
"$venv_python" -m poetry export --with test,dev --without-urls --format requirements.txt \
  --output "$work_dir/requirements.txt"

"$venv_python" -m pip download --quiet --disable-pip-version-check --no-input --no-deps \
  --requirement "$work_dir/requirements.txt" --dest "$work_dir/downloads" \
  --uploaded-prior-to "$HARNESS_COOLDOWN"

echo "OK: every locked package is older than $HARNESS_COOLDOWN."
