#!/usr/bin/env bash
# Copyright (c) 2023-2026 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.
#
# Shared helpers for the harness-*.sh scripts. Source this file; do not execute it.

# Jenkins runs sh steps with -x, which would echo the expanded token.
set +x

HARNESS_INSTALL_URL="https://pkg.harness.io/pkg/ct8onj8YTdaXtKaFsYCRLg/org-marklogic-python-private/python/simple"
# Progress-recommended minimum
HARNESS_POETRY_VERSION="2.5.1"
# Progress-recommended minimum; --uploaded-prior-to accepts a duration such as P7D from pip 26.1.
HARNESS_MIN_PIP="26.2.1"
HARNESS_COOLDOWN="P7D"

HARNESS_PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Exports variables from .env, overriding values already in the environment (VS Code injects a copy at terminal start
# that goes stale when the token changes). Parsed rather than sourced so the file cannot run code.
harness_load_dotenv() {
  local file="$HARNESS_PROJECT_DIR/.env" line key value ref ref_value
  [[ -f "$file" ]] || return 0
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    [[ "$line" =~ ^[[:space:]]*(export[[:space:]]+)?([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*=(.*)$ ]] || continue
    key="${BASH_REMATCH[2]}"
    value="${BASH_REMATCH[3]}"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    if [[ "$value" =~ ^\"(.*)\"$ || "$value" =~ ^\'(.*)\'$ ]]; then
      value="${BASH_REMATCH[1]}"
    fi
    while [[ "$value" =~ \$\{([A-Za-z_][A-Za-z0-9_]*)\} ]]; do
      ref="${BASH_REMATCH[1]}"
      ref_value="${!ref-}"
      value="${value//"\${$ref}"/"$ref_value"}"
    done
    export "$key=$value"
  done < "$file"
}

harness_require_credentials() {
  if [[ -z "${HARNESS_USEREMAIL:-}" || -z "${HARNESS_TOKEN:-}" ]]; then
    echo "HARNESS_USEREMAIL and HARNESS_TOKEN must be set (copy .env.example to .env, or export them in CI)." >&2
    return 1
  fi
  export POETRY_HTTP_BASIC_HARNESS_USERNAME="$HARNESS_USEREMAIL"
  export POETRY_HTTP_BASIC_HARNESS_PASSWORD="$HARNESS_TOKEN"
}

# Prints the venv's python path, or nothing when the venv does not exist.
harness_venv_python() {
  local venv_dir="$HARNESS_PROJECT_DIR/.venv"
  if [[ -x "$venv_dir/bin/python" ]]; then
    echo "$venv_dir/bin/python"
  elif [[ -x "$venv_dir/Scripts/python.exe" ]]; then
    echo "$venv_dir/Scripts/python.exe"
  fi
}

# Usage: harness_urlencode <python> <value>
harness_urlencode() {
  printf '%s' "$2" | "$1" -c 'import sys, urllib.parse as u; print(u.quote(sys.stdin.read(), safe=""))'
}

# Points pip inside the venv at Harness only, with the cool-down applied. Usage: harness_write_pip_config <venv python>
harness_write_pip_config() {
  local venv_python="$1" venv_dir conf_name="pip.conf" user token
  venv_dir="$(dirname "$(dirname "$venv_python")")"
  [[ "$venv_python" == *Scripts* ]] && conf_name="pip.ini"
  user="$(harness_urlencode "$venv_python" "$HARNESS_USEREMAIL")"
  token="$(harness_urlencode "$venv_python" "$HARNESS_TOKEN")"
  (
    umask 077
    cat > "$venv_dir/$conf_name" <<EOF
[global]
index-url = ${HARNESS_INSTALL_URL/https:\/\//https://$user:$token@}
uploaded-prior-to = $HARNESS_COOLDOWN
EOF
  )
}
