param(
    [string]$AdkUrl = "https://go.microsoft.com/fwlink/?linkid=2289980",
    [string]$WinPeUrl = "https://go.microsoft.com/fwlink/?linkid=2289981",
    [string]$InstallRoot = "C:\Program Files (x86)\Windows Kits\10"
)

$legacyScript = Join-Path $PSScriptRoot "legacy\install_adk.ps1"
Write-Warning "install_adk.ps1 is a legacy WinPE/ADK helper. It is kept only for the transitional WinPE build path."

& $legacyScript `
    -AdkUrl $AdkUrl `
    -WinPeUrl $WinPeUrl `
    -InstallRoot $InstallRoot

exit $LASTEXITCODE
