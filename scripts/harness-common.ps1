# Copyright (c) 2023-2026 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.
#
# Shared helpers for the harness-*.ps1 scripts. Dot-source this file; do not run it.

$script:HarnessInstallUrl = 'https://pkg.harness.io/pkg/ct8onj8YTdaXtKaFsYCRLg/org-marklogic-python-private/python/simple'
# Progress-recommended minimum
$script:HarnessPoetryVersion = '2.5.1'
# Progress-recommended minimum; --uploaded-prior-to accepts a duration such as P7D from pip 26.1.
$script:HarnessMinPip = '26.2.1'
$script:HarnessCooldown = 'P7D'

$script:HarnessProjectDir = Split-Path -Parent $PSScriptRoot

# Sets variables from .env, overriding values already in the session (VS Code injects a copy at terminal start that goes
# stale when the token changes). Parsed rather than executed so the file cannot run code.
function Import-HarnessDotEnv {
    $file = Join-Path $script:HarnessProjectDir '.env'
    if (-not (Test-Path -LiteralPath $file)) { return }
    $expand = [System.Text.RegularExpressions.MatchEvaluator] {
        param($match)
        [Environment]::GetEnvironmentVariable($match.Groups[1].Value)
    }
    foreach ($line in Get-Content -LiteralPath $file) {
        if ($line -notmatch '^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$') { continue }
        $key = $Matches[1]
        $value = $Matches[2].Trim()
        if ($value -match '^"(.*)"$' -or $value -match "^'(.*)'$") { $value = $Matches[1] }
        $value = [regex]::Replace($value, '\$\{([A-Za-z_][A-Za-z0-9_]*)\}', $expand)
        [Environment]::SetEnvironmentVariable($key, $value)
    }
}

function Assert-HarnessCredentials {
    if (-not $env:HARNESS_USEREMAIL -or -not $env:HARNESS_TOKEN) {
        throw 'HARNESS_USEREMAIL and HARNESS_TOKEN must be set (copy .env.example to .env, or set them in CI).'
    }
    $env:POETRY_HTTP_BASIC_HARNESS_USERNAME = $env:HARNESS_USEREMAIL
    $env:POETRY_HTTP_BASIC_HARNESS_PASSWORD = $env:HARNESS_TOKEN
}

# Returns the venv's python path, or $null when the venv does not exist.
function Get-HarnessVenvPython {
    foreach ($relative in '.venv\Scripts\python.exe', '.venv/bin/python') {
        $candidate = Join-Path $script:HarnessProjectDir $relative
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }
    return $null
}

# Throws on a non-zero exit code; never pass secrets in $Arguments because they appear in the error text.
function Invoke-HarnessNative {
    param([string]$Exe, [string[]]$Arguments)
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "'$Exe $($Arguments -join ' ')' failed with exit code $LASTEXITCODE"
    }
}

# Points pip inside the venv at Harness only, with the cool-down applied.
function Write-HarnessPipConfig {
    param([string]$VenvPython)
    $venvDir = Split-Path -Parent (Split-Path -Parent $VenvPython)
    $onWindows = [System.Environment]::OSVersion.Platform -eq 'Win32NT'
    $confPath = Join-Path $venvDir $(if ($onWindows) { 'pip.ini' } else { 'pip.conf' })
    $user = [uri]::EscapeDataString($env:HARNESS_USEREMAIL)
    $token = [uri]::EscapeDataString($env:HARNESS_TOKEN)
    $indexUrl = $script:HarnessInstallUrl.Replace('https://', "https://${user}:${token}@")
    $content = "[global]`nindex-url = $indexUrl`nuploaded-prior-to = $script:HarnessCooldown`n"
    # No BOM: pip's config parser would read it as part of the [global] header.
    [System.IO.File]::WriteAllText($confPath, $content, (New-Object System.Text.UTF8Encoding $false))
}
