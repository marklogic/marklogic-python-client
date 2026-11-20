# Copyright (c) 2023-2026 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.

<#
.SYNOPSIS
Fails if any version pinned in poetry.lock was uploaded to Harness less than 7 days ago.

.DESCRIPTION
Poetry only applies its cool-down when it resolves, so this verifies the committed lock file.

.PARAMETER Ci
Read HARNESS_USEREMAIL / HARNESS_TOKEN from the environment only (ignore .env).
#>
[CmdletBinding()]
param(
    [switch]$Ci
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'harness-common.ps1')

if (-not $Ci) { Import-HarnessDotEnv }
Assert-HarnessCredentials

Set-Location $script:HarnessProjectDir

$venvPython = Get-HarnessVenvPython
if (-not $venvPython) {
    throw 'No .venv found; run scripts\harness-setup.ps1 first.'
}

$workDir = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName())
New-Item -ItemType Directory -Path $workDir | Out-Null
try {
    $requirements = Join-Path $workDir 'requirements.txt'
    # --without-urls keeps the credentialed index-url from .venv\pip.ini in effect.
    Invoke-HarnessNative $venvPython @(
        '-m', 'poetry', 'export', '--with', 'test,dev', '--without-urls',
        '--format', 'requirements.txt', '--output', $requirements
    )
    Invoke-HarnessNative $venvPython @(
        '-m', 'pip', 'download', '--quiet', '--disable-pip-version-check', '--no-input', '--no-deps',
        '--requirement', $requirements, '--dest', (Join-Path $workDir 'downloads'),
        '--uploaded-prior-to', $script:HarnessCooldown
    )
}
finally {
    Remove-Item -LiteralPath $workDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "OK: every locked package is older than $script:HarnessCooldown."
