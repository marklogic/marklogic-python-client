#!/usr/bin/env bash
# Copyright (c) 2023-2026 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.
#
# Sets up the project .venv so every dependency comes from the Harness Python registry.
# Safe to re-run.
#
# Usage: scripts/harness-setup.sh [--ci] [--lock]
#   --ci    read HARNESS_USEREMAIL / HARNESS_TOKEN from the environment only (ignore .env)
#   --lock  run "poetry lock" before installing (needed once after the Harness source was added)
# Set PYTHON to choose the interpreter used to create the venv.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/harness-common.sh"

ci=false
lock=false
for arg in "$@"; do
  case "$arg" in
    --ci) ci=true ;;
    --lock) lock=true ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done

if [[ "$ci" == false ]]; then
  harness_load_dotenv
fi
harness_require_credentials

cd "$HARNESS_PROJECT_DIR"

venv_python="$(harness_venv_python)"
if [[ -z "$venv_python" ]]; then
  python="${PYTHON:-$(command -v python3 || command -v python)}"
  "$python" -m venv .venv
  venv_python="$(harness_venv_python)"
fi

harness_write_pip_config "$venv_python"

# A new venv's bundled pip may predate --uploaded-prior-to (older pip ignores the config key), so upgrade it first.
"$venv_python" -m pip install --quiet --disable-pip-version-check "pip>=$HARNESS_MIN_PIP"
"$venv_python" -m pip install --quiet --disable-pip-version-check \
  "poetry==$HARNESS_POETRY_VERSION" poetry-plugin-export

if [[ "$lock" == true ]]; then
  "$venv_python" -m poetry lock
fi
"$venv_python" -m poetry install --no-interaction

echo "Done. Activate the venv, then run: poetry run pytest"
