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

$appCandidates = @(
    (Join-Path $RuntimeRoot "app\CigerTool\CigerTool.exe"),
    (Join-Path $RuntimeRoot "CigerTool\CigerTool.exe")
)

foreach ($candidate in $appCandidates) {
    if (Test-Path -LiteralPath $candidate -PathType Leaf) {
        try {
            $process = Start-Process -FilePath $candidate -WorkingDirectory (Split-Path $candidate -Parent) -PassThru -ErrorAction Stop
            if ($helperReady) {
                Set-CigerToolLiveStatus -RuntimeRoot $RuntimeRoot -Stage "application" -State "ready" -Message "Paketlenmis CigerTool baslatildi." -Extra @{
                    launch_mode = "packaged"
                    process_id = $process.Id
                    target = $candidate
                }
            }
            return [pscustomobject]@{
                Started = $true
                Mode = "packaged"
                ProcessId = $process.Id
                Target = $candidate
            }
        }
        catch {
            if ($helperReady) {
                Set-CigerToolLiveStatus -RuntimeRoot $RuntimeRoot -Stage "application" -State "failed" -Message ("Paketlenmis uygulama baslatilamadi: " + $_.Exception.Message) -Extra @{
                    target = $candidate
                }
                Write-CigerToolLiveConsoleMessage -Level "WARN" -Message ("Paketlenmis uygulama baslatilamadi: " + $_.Exception.Message)
            }
        }
    }
}

$pythonCommand = Get-Command "python.exe" -ErrorAction SilentlyContinue
if ($pythonCommand) {
    try {
        $process = Start-Process -FilePath $pythonCommand.Source -ArgumentList @("-m", "cigertool") -WorkingDirectory $RuntimeRoot -PassThru -ErrorAction Stop
        if ($helperReady) {
            Set-CigerToolLiveStatus -RuntimeRoot $RuntimeRoot -Stage "application" -State "ready" -Message "Python fallback ile CigerTool baslatildi." -Extra @{
                launch_mode = "python"
                process_id = $process.Id
                target = $pythonCommand.Source
            }
        }
        return [pscustomobject]@{
            Started = $true
            Mode = "python"
            ProcessId = $process.Id
            Target = $pythonCommand.Source
        }
    }
    catch {
        if ($helperReady) {
            Set-CigerToolLiveStatus -RuntimeRoot $RuntimeRoot -Stage "application" -State "failed" -Message ("Python fallback baslatilamadi: " + $_.Exception.Message) -Extra @{
                target = $pythonCommand.Source
            }
            Write-CigerToolLiveConsoleMessage -Level "WARN" -Message ("Python fallback baslatilamadi: " + $_.Exception.Message)
        }
    }
}

Write-Warning "CigerTool uygulama giris noktasi cozulmedi. Etkilesimli shell acik kalacak."
if ($helperReady) {
    Set-CigerToolLiveStatus -RuntimeRoot $RuntimeRoot -Stage "application" -State "degraded" -Message "CigerTool uygulama giris noktasi cozulmedi. Recovery shell acik kalacak."
    Write-CigerToolLiveConsoleMessage -Level "WARN" -Message "CigerTool uygulama giris noktasi cozulmedi. Recovery shell acik kalacak."
}
return [pscustomobject]@{
    Started = $false
    Mode = "none"
    ProcessId = $null
    Target = ""
}
