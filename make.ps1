#requires -Version 5.1
<#
.SYNOPSIS
    Pipeline runner for Windows PowerShell (Makefile-equivalent).

.DESCRIPTION
    Runs the 4-step pipeline (extract_schema -> scan_pii -> profile_stats -> build_scorecard)
    in one command. Use this on Windows when GNU `make` is not available.

.PARAMETER Target
    Pipeline target: all, install, schema, scan, profile, scorecard,
    verify-pii, check-help, clean, help.

.PARAMETER InputFile
    Path to the source Excel file. Default: data\student_fixed_report.xlsx

.PARAMETER OutDir
    Path to the output directory. Default: outputs

.PARAMETER K
    k-anonymity threshold. Default: 5

.EXAMPLE
    .\make.ps1 all
    .\make.ps1 schema -InputFile data\my_data.xlsx
    .\make.ps1 clean
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('help', 'all', 'install', 'schema', 'scan', 'profile', 'scorecard', 'verify-pii', 'check-help', 'clean')]
    [string]$Target = 'help',

    [string]$InputFile = 'data\student_fixed_report.xlsx',
    [string]$OutDir = 'outputs',
    [int]$K = 5,
    [string]$Python = 'python'
)

$ErrorActionPreference = 'Stop'

$schemaFile  = Join-Path $OutDir 'schema_summary.json'
$piiFile     = Join-Path $OutDir 'pii_scan_report.txt'
$profileFile = Join-Path $OutDir 'profile_stats.json'
$scoreFile   = Join-Path $OutDir 'data_quality_scorecard.html'

function Show-Help {
    Write-Host ""
    Write-Host "Data Profiling Workflow - Pipeline targets" -ForegroundColor Cyan
    Write-Host "==========================================="
    Write-Host "  .\make.ps1 install      Install Python dependencies"
    Write-Host "  .\make.ps1 all          Run full pipeline (schema -> scan -> profile -> scorecard)"
    Write-Host "  .\make.ps1 schema       Build schema summary"
    Write-Host "  .\make.ps1 scan         PII scan (strict mode)"
    Write-Host "  .\make.ps1 profile      Build profile statistics"
    Write-Host "  .\make.ps1 scorecard    Build scorecard HTML"
    Write-Host "  .\make.ps1 verify-pii   Run PII scan in strict mode (fail on hit)"
    Write-Host "  .\make.ps1 check-help   Test --help for every script"
    Write-Host "  .\make.ps1 clean        Delete outputs/"
    Write-Host ""
    Write-Host "Variables (override via flags):" -ForegroundColor Yellow
    Write-Host "  -InputFile $InputFile"
    Write-Host "  -OutDir    $OutDir"
    Write-Host "  -K         $K"
    Write-Host ""
}

function Invoke-Script {
    param([string[]]$Arguments)
    & $Python @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Script failed: $($Arguments -join ' ')" }
}

function Invoke-Install {
    Invoke-Script @('-m', 'pip', 'install', '-r', 'requirements.txt')
}

function Invoke-Schema {
    if (-not (Test-Path $InputFile)) { throw "Input file not found: $InputFile" }
    Invoke-Script @('scripts/01_extract_schema.py', '--input', $InputFile, '--output', $schemaFile, '-k', $K)
}

function Invoke-Scan {
    if (-not (Test-Path $schemaFile)) { Invoke-Schema }
    Invoke-Script @('scripts/02_scan_pii.py', '--input', $schemaFile, '--report', $piiFile, '--strict')
}

function Invoke-ProfileStats {
    if (-not (Test-Path $InputFile)) { throw "Input file not found: $InputFile" }
    Invoke-Script @('scripts/03_profile_stats.py', '--input', $InputFile, '--output', $profileFile, '-k', $K)
}

function Invoke-Scorecard {
    if (-not (Test-Path $schemaFile))  { Invoke-Schema }
    if (-not (Test-Path $profileFile)) { Invoke-ProfileStats }
    Invoke-Script @('scripts/04_build_scorecard.py', '--schema', $schemaFile, '--profile', $profileFile, '--output', $scoreFile)
}

function Invoke-All {
    Invoke-Schema
    Invoke-Scan
    Invoke-ProfileStats
    Invoke-Scorecard
    Write-Host ""
    Write-Host "Pipeline complete - outputs in $OutDir\" -ForegroundColor Green
}

function Invoke-CheckHelp {
    $scripts = @(
        'scripts/01_extract_schema.py',
        'scripts/02_scan_pii.py',
        'scripts/03_profile_stats.py',
        'scripts/04_build_scorecard.py',
        '.github/scripts/scan_committed_files.py'
    )
    $allOk = $true
    foreach ($s in $scripts) {
        Write-Host "--- $s ---"
        & $Python $s --help > $null 2>&1
        if ($LASTEXITCODE -eq 0) { Write-Host "OK" -ForegroundColor Green }
        else                     { Write-Host "FAIL" -ForegroundColor Red; $allOk = $false }
    }
    if (-not $allOk) { exit 1 }
}

function Invoke-Clean {
    if (Test-Path $OutDir) {
        Get-ChildItem $OutDir -File -Include *.json, *.html, *.txt -ErrorAction SilentlyContinue |
            Remove-Item -Force
        Write-Host "Cleaned $OutDir\"
    } else {
        Write-Host "$OutDir\ does not exist - skipping"
    }
}

switch ($Target) {
    'help'        { Show-Help }
    'install'     { Invoke-Install }
    'schema'      { Invoke-Schema }
    'scan'        { Invoke-Scan }
    'profile'     { Invoke-ProfileStats }
    'scorecard'   { Invoke-Scorecard }
    'all'         { Invoke-All }
    'verify-pii'  { Invoke-Scan; Write-Host "PII scan passed (strict mode)" -ForegroundColor Green }
    'check-help'  { Invoke-CheckHelp }
    'clean'       { Invoke-Clean }
}
