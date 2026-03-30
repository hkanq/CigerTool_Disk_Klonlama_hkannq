function Write-CigerToolLiveConsoleMessage {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [string]$Level = "INFO"
    )

    Write-Host ("[CigerTool Live][{0}] {1}" -f $Level.ToUpperInvariant(), $Message)
}

function Get-CigerToolLiveStatusPath {
    param([Parameter(Mandatory = $true)][string]$RuntimeRoot)

    $explicit = $env:CIGERTOOL_RUNTIME_STATUS_PATH
    if (-not [string]::IsNullOrWhiteSpace($explicit)) {
        return $explicit
    }

    return (Join-Path $RuntimeRoot "liveos\logs\liveos-status.json")
}

function Set-CigerToolLiveStatus {
    param(
        [Parameter(Mandatory = $true)][string]$RuntimeRoot,
        [Parameter(Mandatory = $true)][string]$Stage,
        [Parameter(Mandatory = $true)][string]$State,
        [Parameter(Mandatory = $true)][string]$Message,
        [hashtable]$Extra = @{}
    )

    $statusPath = Get-CigerToolLiveStatusPath -RuntimeRoot $RuntimeRoot
    $statusDir = Split-Path -Path $statusPath -Parent
    New-Item -ItemType Directory -Force -Path $statusDir | Out-Null

    $existing = @{}
    if (Test-Path -LiteralPath $statusPath -PathType Leaf) {
        try {
            $raw = Get-Content -Raw -LiteralPath $statusPath | ConvertFrom-Json -ErrorAction Stop
            if ($raw -is [System.Collections.IDictionary]) {
                foreach ($property in $raw.Keys) {
                    $existing[$property] = $raw[$property]
                }
            }
            elseif ($raw.PSObject) {
                foreach ($property in $raw.PSObject.Properties) {
                    $existing[$property.Name] = $property.Value
                }
            }
        }
        catch {
        }
    }

    $payload = [ordered]@{
        product = "CigerTool Live"
        stage = $Stage
        state = $State
        message = $Message
        runtime_root = $RuntimeRoot
        updated_at = (Get-Date).ToString("o")
    }

    foreach ($pair in $existing.GetEnumerator()) {
        if (-not $payload.Contains($pair.Key)) {
            $payload[$pair.Key] = $pair.Value
        }
    }

    foreach ($pair in $Extra.GetEnumerator()) {
        $payload[$pair.Key] = $pair.Value
    }

    $payload | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $statusPath -Encoding utf8
}
