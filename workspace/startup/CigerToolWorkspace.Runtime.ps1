function Write-CigerToolWorkspaceConsoleMessage {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [string]$Level = "INFO"
    )

    Write-Host ("[CigerTool Workspace][{0}] {1}" -f $Level.ToUpperInvariant(), $Message)
}

function Get-CigerToolWorkspaceLogPath {
    param([Parameter(Mandatory = $true)][string]$RuntimeRoot)

    if (-not [string]::IsNullOrWhiteSpace($env:CIGERTOOL_WORKSPACE_LOG_PATH)) {
        return $env:CIGERTOOL_WORKSPACE_LOG_PATH
    }

    if (-not [string]::IsNullOrWhiteSpace($env:ProgramData)) {
        return (Join-Path $env:ProgramData "CigerToolWorkspace\logs\workspace-startup.log")
    }

    return (Join-Path $RuntimeRoot "logs\workspace-startup.log")
}

function Write-CigerToolWorkspaceLog {
    param(
        [Parameter(Mandatory = $true)][string]$RuntimeRoot,
        [Parameter(Mandatory = $true)][string]$Message,
        [string]$Level = "INFO"
    )

    $logPath = Get-CigerToolWorkspaceLogPath -RuntimeRoot $RuntimeRoot
    $logDir = Split-Path -Path $logPath -Parent
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null

    $line = "{0} [{1}] {2}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Level.ToUpperInvariant(), $Message
    Add-Content -LiteralPath $logPath -Value $line
}

function Get-CigerToolWorkspaceStatusPath {
    param([Parameter(Mandatory = $true)][string]$RuntimeRoot)

    if (-not [string]::IsNullOrWhiteSpace($env:CIGERTOOL_RUNTIME_STATUS_PATH)) {
        return $env:CIGERTOOL_RUNTIME_STATUS_PATH
    }

    if (-not [string]::IsNullOrWhiteSpace($env:ProgramData)) {
        return (Join-Path $env:ProgramData "CigerToolWorkspace\logs\workspace-status.json")
    }

    return (Join-Path $RuntimeRoot "logs\workspace-status.json")
}

function Set-CigerToolWorkspaceStatus {
    param(
        [Parameter(Mandatory = $true)][string]$RuntimeRoot,
        [Parameter(Mandatory = $true)][string]$Stage,
        [Parameter(Mandatory = $true)][string]$State,
        [Parameter(Mandatory = $true)][string]$Message,
        [hashtable]$Extra = @{}
    )

    $statusPath = Get-CigerToolWorkspaceStatusPath -RuntimeRoot $RuntimeRoot
    $statusDir = Split-Path -Path $statusPath -Parent
    New-Item -ItemType Directory -Force -Path $statusDir | Out-Null

    $payload = [ordered]@{
        product = "CigerTool Workspace"
        stage = $Stage
        state = $State
        message = $Message
        runtime_root = $RuntimeRoot
        updated_at = (Get-Date).ToString("o")
    }

    foreach ($pair in $Extra.GetEnumerator()) {
        $payload[$pair.Key] = $pair.Value
    }

    $payload | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $statusPath -Encoding utf8
    Write-CigerToolWorkspaceLog -RuntimeRoot $RuntimeRoot -Message ("status={0} stage={1} message={2}" -f $State, $Stage, $Message) -Level $State
}
