param(
    [string]$RuntimeRoot = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RuntimeRoot)) {
    $RuntimeRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
}

$helperScript = Join-Path $PSScriptRoot "CigerToolWorkspace.Runtime.ps1"
. $helperScript

function Resolve-WorkspaceMediaRoot {
    $explicit = $env:CIGERTOOL_MEDIA_ROOT
    if (-not [string]::IsNullOrWhiteSpace($explicit) -and (Test-Path -LiteralPath (Join-Path $explicit "CigerTool.workspace.json") -PathType Leaf)) {
        return $explicit
    }

    foreach ($drive in [System.IO.DriveInfo]::GetDrives()) {
        if (-not $drive.IsReady) {
            continue
        }

        $candidate = $drive.RootDirectory.FullName
        if (Test-Path -LiteralPath (Join-Path $candidate "CigerTool.workspace.json") -PathType Leaf) {
            return $candidate.TrimEnd("\")
        }
    }

    return ""
}

$logRoot = if (-not [string]::IsNullOrWhiteSpace($env:ProgramData)) {
    Join-Path $env:ProgramData "CigerToolWorkspace\logs"
}
else {
    Join-Path $RuntimeRoot "logs"
}

$mediaRoot = Resolve-WorkspaceMediaRoot
$appRoot = "C:\Program Files\CigerTool"
$scriptsRoot = Join-Path $appRoot "scripts"

New-Item -ItemType Directory -Force -Path $logRoot | Out-Null

$env:CIGERTOOL_RUNTIME = "workspace"
$env:CIGERTOOL_RUNTIME_ROOT = $RuntimeRoot
$env:CIGERTOOL_LOG_ROOT = $logRoot
$env:CIGERTOOL_LOG_PATH = Join-Path $logRoot "cigertool.log"
$env:CIGERTOOL_RUNTIME_STATUS_PATH = Join-Path $logRoot "workspace-status.json"
$env:CIGERTOOL_WORKSPACE_LOG_PATH = Join-Path $logRoot "workspace-startup.log"
$env:CIGERTOOL_SCRIPTS_ROOT = $scriptsRoot
if (-not [string]::IsNullOrWhiteSpace($mediaRoot)) {
    $env:CIGERTOOL_MEDIA_ROOT = $mediaRoot
    $env:CIGERTOOL_TOOLS_ROOT = Join-Path $mediaRoot "tools"
    $env:CIGERTOOL_ISOS_ROOT = Join-Path $mediaRoot "isos"
}

Write-CigerToolWorkspaceLog -RuntimeRoot $RuntimeRoot -Message "Workspace startup baslatildi."
if ([string]::IsNullOrWhiteSpace($mediaRoot)) {
    Write-CigerToolWorkspaceLog -RuntimeRoot $RuntimeRoot -Level "WARN" -Message "Workspace marker bulunamadi. Media root otomatik algilanamadi."
}
else {
    Write-CigerToolWorkspaceLog -RuntimeRoot $RuntimeRoot -Message ("Media root algilandi: " + $mediaRoot)
}

Set-CigerToolWorkspaceStatus -RuntimeRoot $RuntimeRoot -Stage "workspace" -State "starting" -Message "CigerTool Workspace oturumu baslatiliyor." -Extra @{
    log_root = $logRoot
    media_root = $mediaRoot
    app_root = $appRoot
}

$appCandidates = @(
    (Join-Path $appRoot "CigerTool.exe"),
    (Join-Path $RuntimeRoot "app\CigerTool\CigerTool.exe")
)

foreach ($candidate in $appCandidates) {
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
        Write-CigerToolWorkspaceLog -RuntimeRoot $RuntimeRoot -Level "WARN" -Message ("Uygulama adayi bulunamadi: " + $candidate)
        continue
    }

    try {
        $process = Start-Process -FilePath $candidate -WorkingDirectory (Split-Path $candidate -Parent) -PassThru -ErrorAction Stop
        Write-CigerToolWorkspaceLog -RuntimeRoot $RuntimeRoot -Message ("Paketlenmis CigerTool baslatildi: " + $candidate)
        Set-CigerToolWorkspaceStatus -RuntimeRoot $RuntimeRoot -Stage "workspace" -State "ready" -Message "CigerTool otomatik baslatildi." -Extra @{
            process_id = $process.Id
            target = $candidate
            launch_mode = "packaged"
        }
        return
    }
    catch {
        Write-CigerToolWorkspaceLog -RuntimeRoot $RuntimeRoot -Level "WARN" -Message ("Paketlenmis CigerTool baslatilamadi: " + $_.Exception.Message)
        Write-CigerToolWorkspaceConsoleMessage -Level "WARN" -Message ("Paketlenmis CigerTool baslatilamadi: " + $_.Exception.Message)
    }
}

$pythonCommand = Get-Command "python.exe" -ErrorAction SilentlyContinue
if ($pythonCommand) {
    try {
        $process = Start-Process -FilePath $pythonCommand.Source -ArgumentList @("-m", "cigertool") -WorkingDirectory $appRoot -PassThru -ErrorAction Stop
        Write-CigerToolWorkspaceLog -RuntimeRoot $RuntimeRoot -Message ("Python fallback ile CigerTool baslatildi: " + $pythonCommand.Source)
        Set-CigerToolWorkspaceStatus -RuntimeRoot $RuntimeRoot -Stage "workspace" -State "ready" -Message "Python fallback ile CigerTool baslatildi." -Extra @{
            process_id = $process.Id
            target = $pythonCommand.Source
            launch_mode = "python"
        }
        return
    }
    catch {
        Write-CigerToolWorkspaceLog -RuntimeRoot $RuntimeRoot -Level "WARN" -Message ("Python fallback baslatilamadi: " + $_.Exception.Message)
        Write-CigerToolWorkspaceConsoleMessage -Level "WARN" -Message ("Python fallback baslatilamadi: " + $_.Exception.Message)
    }
}
else {
    Write-CigerToolWorkspaceLog -RuntimeRoot $RuntimeRoot -Level "WARN" -Message "python.exe bulunamadi; fallback calistirilmadi."
}

Set-CigerToolWorkspaceStatus -RuntimeRoot $RuntimeRoot -Stage "workspace" -State "degraded" -Message "CigerTool otomatik baslatilamadi. Masaustu acik kalacak." -Extra @{
    media_root_detected = (-not [string]::IsNullOrWhiteSpace($mediaRoot))
    packaged_candidates = $appCandidates
}
Write-CigerToolWorkspaceConsoleMessage -Level "WARN" -Message "CigerTool otomatik baslatilamadi. Masaustu acik kalacak."
