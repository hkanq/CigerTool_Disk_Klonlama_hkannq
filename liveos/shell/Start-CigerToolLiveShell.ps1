param(
    [string]$RuntimeRoot = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RuntimeRoot)) {
    $RuntimeRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
}

$helperScript = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\startup\CigerToolLive.Runtime.ps1"))
$sessionScript = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\startup\Start-CigerToolLiveSession.ps1"))

$shellReady = $false
if (Test-Path -LiteralPath $helperScript -PathType Leaf) {
    . $helperScript
    Set-CigerToolLiveStatus -RuntimeRoot $RuntimeRoot -Stage "shell" -State "starting" -Message "Canli ortam shell zinciri baslatiliyor."
    $shellReady = $true
}

$explorerCommand = Get-Command "explorer.exe" -ErrorAction SilentlyContinue
if ($explorerCommand) {
    try {
        Start-Process -FilePath $explorerCommand.Source | Out-Null
    }
    catch {
        if ($shellReady) {
            Set-CigerToolLiveStatus -RuntimeRoot $RuntimeRoot -Stage "shell" -State "degraded" -Message ("Explorer baslatilamadi: " + $_.Exception.Message)
            Write-CigerToolLiveConsoleMessage -Level "WARN" -Message ("Explorer baslatilamadi: " + $_.Exception.Message)
        }
    }
}

if (-not (Test-Path -LiteralPath $sessionScript -PathType Leaf)) {
    Write-Warning "Live session bootstrap bulunamadi: $sessionScript"
    if ($shellReady) {
        Set-CigerToolLiveStatus -RuntimeRoot $RuntimeRoot -Stage "shell" -State "failed" -Message "Live session bootstrap bulunamadi. Recovery shell acik kalacak." -Extra @{
            bootstrap_path = $sessionScript
        }
        Write-CigerToolLiveConsoleMessage -Level "WARN" -Message "Live session bootstrap bulunamadi. Recovery shell acik kalacak."
    }
    return
}

try {
    & $sessionScript -RuntimeRoot $RuntimeRoot
    if ($shellReady) {
        Set-CigerToolLiveStatus -RuntimeRoot $RuntimeRoot -Stage "shell" -State "ready" -Message "Shell katmani basariyla devreye girdi."
    }
}
catch {
    Write-Warning ("Live shell baslatma hatasi: " + $_.Exception.Message)
    if ($shellReady) {
        Set-CigerToolLiveStatus -RuntimeRoot $RuntimeRoot -Stage "shell" -State "failed" -Message ("Live shell baslatma hatasi: " + $_.Exception.Message)
        Write-CigerToolLiveConsoleMessage -Level "WARN" -Message ("Live shell baslatma hatasi: " + $_.Exception.Message)
    }
}
