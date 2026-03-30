param(
    [string]$OutputIso = "artifacts\CigerTool-by-hkannq.iso",
    [string]$AppBuildRoot = "build-output\app\dist\CigerTool",
    [switch]$RequirePrebootMenu
)

$legacyScript = Join-Path $PSScriptRoot "legacy\build_winpe_iso.ps1"
Write-Warning "build_winpe_iso.ps1 is a legacy WinPE build path. Use build_liveos_foundation.ps1 for the desktop-first architecture."

& $legacyScript `
    -OutputIso $OutputIso `
    -AppBuildRoot $AppBuildRoot `
    -RequirePrebootMenu:$RequirePrebootMenu

exit $LASTEXITCODE
