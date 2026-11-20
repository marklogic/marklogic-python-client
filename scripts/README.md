# Scripts

Helpers for installing this project's dependencies from the private Harness Python registry (the public PyPI registry
is not used) with a 7-day supply-chain cool-down. Each script exists as PowerShell (`.ps1`) and bash (`.sh`).

| Script | Purpose |
|---|---|
| `harness-setup` | Creates and configures `.venv`, installs Poetry, and installs the project dependencies. Safe to re-run. |
| `harness-cooldown-check` | Fails if any version pinned in `poetry.lock` was uploaded less than 7 days ago. |
| `harness-common` | Shared helpers sourced by the other two. Do not run it directly. |

Run the scripts from anywhere; they resolve the project root themselves. For the full onboarding steps see
[Local setup with the Harness registry](../CONTRIBUTING.md#local-setup-with-the-harness-registry).

## Credentials

The scripts need `HARNESS_USEREMAIL` and `HARNESS_TOKEN`.

- **Local development:** put them in `.env` (copy `.env.example`). Values in `.env` override variables already set in
  your session, so a stale token from an older terminal is replaced. The file is parsed, not executed.
- **CI:** pass `-Ci` (PowerShell) or `--ci` (bash) and set the variables in the environment; `.env` is ignored. In
  Jenkins, map the read-only service-account credential to these two variables.

The scripts also set `POETRY_HTTP_BASIC_HARNESS_USERNAME` and `POETRY_HTTP_BASIC_HARNESS_PASSWORD` from them, which is
how Poetry authenticates to the source named `harness` in `pyproject.toml`. The token is never passed as a command-line
argument.

## harness-setup

    .\scripts\harness-setup.ps1 [-Ci] [-Lock]
    ./scripts/harness-setup.sh [--ci] [--lock]

Steps:

1. Create `.venv` if it does not exist. Set `PYTHON` to choose the interpreter.
2. Write the venv's pip config (`.venv/pip.ini` on Windows, `.venv/pip.conf` elsewhere) with the Harness index URL and
   `uploaded-prior-to = P7D`. It contains your token and lives in the git-ignored `.venv`.
3. Upgrade pip to at least 26.2.1, the minimum Progress recommends (pip accepts a duration such as `P7D` from 26.1).
4. Install the pinned Poetry version and `poetry-plugin-export` into the venv.
5. With `-Lock` / `--lock`, run `poetry lock`.
6. Run `poetry install`.

Use `-Lock` / `--lock` only when `pyproject.toml` changed and Poetry reports that it no longer matches `poetry.lock`.
For adding or updating dependencies use `poetry add` / `poetry update`.

A venv that was created before this setup may still hold packages installed from PyPI. Delete `.venv` and re-run the
script for a clean, Harness-only environment.

## harness-cooldown-check

    .\scripts\harness-cooldown-check.ps1 [-Ci]
    ./scripts/harness-cooldown-check.sh [--ci]

Poetry applies its cool-down (`solver.min-release-age` in `poetry.toml`) only when it resolves versions, not when it
installs from an existing lock file. This script exports `poetry.lock` and runs `pip download --uploaded-prior-to P7D`
against Harness, so it fails if any pinned version is too new. Run it after any change to `poetry.lock` and in CI.

If it fails, run `poetry lock --regenerate` and check again. It requires the venv from `harness-setup`.

## Changing the pinned versions

The Poetry version (`HARNESS_POETRY_VERSION` / `$script:HarnessPoetryVersion`), the minimum pip version, the cool-down
duration and the registry URL are defined at the top of `harness-common.sh` and `harness-common.ps1`. Keep the two files
in sync, and keep the Poetry version in line with `requires-poetry` in `pyproject.toml`.

## Troubleshooting

- `HARNESS_USEREMAIL and HARNESS_TOKEN must be set`: `.env` is missing or empty, or `-Ci` / `--ci` was used without the
  variables in the environment.
- `No matching distribution found ... (from versions: none)`: pip hides the HTTP error. `401` means the token or email is
  wrong or expired; `403` means the token is valid but its scope, or your Harness role, does not allow viewing and
  downloading from the MarkLogic organization's registry.
- `pyproject.toml changed significantly since poetry.lock was last generated`: run the setup script with `-Lock` /
  `--lock`.
