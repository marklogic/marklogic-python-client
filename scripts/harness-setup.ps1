# Copyright (c) 2023-2026 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.

<#
.SYNOPSIS
Sets up the project .venv so every dependency comes from the Harness Python registry. Safe to re-run.

.PARAMETER Ci
Read HARNESS_USEREMAIL / HARNESS_TOKEN from the environment only (ignore .env).

.PARAMETER Lock
Run "poetry lock" before installing (needed once after the Harness source was added).

.NOTES
Set the PYTHON environment variable to choose the interpreter used to create the venv.
#>
[CmdletBinding()]
param(
    [switch]$Ci,
    [switch]$Lock
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'harness-common.ps1')

if (-not $Ci) { Import-HarnessDotEnv }
Assert-HarnessCredentials

Set-Location $script:HarnessProjectDir

$venvPython = Get-HarnessVenvPython
if (-not $venvPython) {
    $python = if ($env:PYTHON) { $env:PYTHON } else { 'python' }
    Invoke-HarnessNative $python @('-m', 'venv', '.venv')
    $venvPython = Get-HarnessVenvPython
}

Write-HarnessPipConfig $venvPython

# A new venv's bundled pip may predate --uploaded-prior-to (older pip ignores the config key), so upgrade it first.
Invoke-HarnessNative $venvPython @('-m', 'pip', 'install', '--quiet', '--disable-pip-version-check', "pip>=$script:HarnessMinPip")
Invoke-HarnessNative $venvPython @(
    '-m', 'pip', 'install', '--quiet', '--disable-pip-version-check',
    "poetry==$script:HarnessPoetryVersion", 'poetry-plugin-export'
)

if ($Lock) {
    Invoke-HarnessNative $venvPython @('-m', 'poetry', 'lock')
}
Invoke-HarnessNative $venvPython @('-m', 'poetry', 'install', '--no-interaction')

Write-Host 'Done. Activate the venv (.\.venv\Scripts\Activate.ps1), then run: poetry run pytest'
