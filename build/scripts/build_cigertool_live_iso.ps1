param(
    [string]$OutputIso = "artifacts\CigerTool-by-hkannq.iso",
    [string]$AppBuildRoot = "build-output\app\dist\CigerTool",
    [switch]$SkipPrebootRequirement
)

$ErrorActionPreference = "Stop"

Write-Host "CigerTool Live transitional build path baslatiliyor."
Write-Host "Bu script, desktop-first boot zincirini kullanir fakat runtime substrate olarak halen gecis donemi image assembly katmanini yeniden kullanir."

$requirePrebootMenu = -not $SkipPrebootRequirement

& (Join-Path $PSScriptRoot "legacy\build_winpe_iso.ps1") `
    -OutputIso $OutputIso `
    -AppBuildRoot $AppBuildRoot `
    -RequirePrebootMenu:$requirePrebootMenu

exit $LASTEXITCODE
