param(
    [string]$RuntimeRoot = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RuntimeRoot)) {
    $RuntimeRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
}

$helperScript = Join-Path $PSScriptRoot "CigerToolLive.Runtime.ps1"
$helperReady = $false
if (Test-Path -LiteralPath $helperScript -PathType Leaf) {
    . $helperScript
    $helperReady = $true
}

$logRoot = Join-Path $RuntimeRoot "liveos\logs"
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null
$statusPath = Join-Path $logRoot "liveos-status.json"

$scriptsCandidates = @(
    (Join-Path $RuntimeRoot "app\CigerTool\scripts"),
    (Join-Path $RuntimeRoot "CigerTool\scripts")
)
$scriptsRoot = $scriptsCandidates | Where-Object { Test-Path -LiteralPath $_ -PathType Container } | Select-Object -First 1
if (-not $scriptsRoot) {
    $scriptsRoot = $scriptsCandidates[0]
}

$toolsRoot = Join-Path $RuntimeRoot "tools"
$isosRoot = Join-Path $RuntimeRoot "isos"

$env:CIGERTOOL_RUNTIME = "liveos"
$env:CIGERTOOL_RUNTIME_ROOT = $RuntimeRoot
$env:CIGERTOOL_SCRIPTS_ROOT = $scriptsRoot
$env:CIGERTOOL_LOG_ROOT = $logRoot
$env:CIGERTOOL_LOG_PATH = Join-Path $logRoot "cigertool.log"
$env:CIGERTOOL_RUNTIME_STATUS_PATH = $statusPath
if (Test-Path -LiteralPath $toolsRoot -PathType Container) {
    $env:CIGERTOOL_TOOLS_ROOT = $toolsRoot
}
if (Test-Path -LiteralPath $isosRoot -PathType Container) {
    $env:CIGERTOOL_ISOS_ROOT = $isosRoot
}

if ($helperReady) {
    Set-CigerToolLiveStatus -RuntimeRoot $RuntimeRoot -Stage "session" -State "starting" -Message "Canli oturum degiskenleri hazirlaniyor." -Extra @{
        log_root = $logRoot
        log_path = $env:CIGERTOOL_LOG_PATH
        scripts_root = $scriptsRoot
        tools_root = $toolsRoot
        isos_root = $isosRoot
    }
}

$appLauncher = Join-Path $PSScriptRoot "Start-CigerToolApp.ps1"
if (-not (Test-Path -LiteralPath $appLauncher -PathType Leaf)) {
    Write-Warning "CigerTool app launcher bulunamadi: $appLauncher"
    if ($helperReady) {
        Set-CigerToolLiveStatus -RuntimeRoot $RuntimeRoot -Stage "session" -State "failed" -Message "App launcher bulunamadi. Recovery shell acik kalacak." -Extra @{
            app_launcher = $appLauncher
        }
    }
    return
}

try {
    $result = & $appLauncher -RuntimeRoot $RuntimeRoot
    if ($helperReady) {
        if ($null -ne $result -and $result.Started) {
            Set-CigerToolLiveStatus -RuntimeRoot $RuntimeRoot -Stage "session" -State "ready" -Message "Canli oturum hazir. CigerTool otomatik baslatildi." -Extra @{
                launch_mode = $result.Mode
                process_id = $result.ProcessId
                target = $result.Target
            }
        }
        else {
            Set-CigerToolLiveStatus -RuntimeRoot $RuntimeRoot -Stage "session" -State "degraded" -Message "Canli oturum acildi fakat CigerTool otomatik baslatilamadi. Recovery shell kullanilabilir."
        }
    }
}
catch {
    Write-Warning ("CigerTool app bootstrap hatasi: " + $_.Exception.Message)
    if ($helperReady) {
        Set-CigerToolLiveStatus -RuntimeRoot $RuntimeRoot -Stage "session" -State "failed" -Message ("CigerTool app bootstrap hatasi: " + $_.Exception.Message)
        Write-CigerToolLiveConsoleMessage -Level "WARN" -Message ("CigerTool app bootstrap hatasi: " + $_.Exception.Message)
    }
}
