param(
    [string]$OutputRoot = "build-output\liveos",
    [string]$AppBuildRoot = "build-output\app\dist\CigerTool",
    [string]$ToolsRoot = "tools",
    [string]$IsosRoot = "isos",
    [string]$LegacyIsoLibraryRoot = "iso-library"
)

$ErrorActionPreference = "Stop"

function Write-BuildLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $line = "{0} [{1}] {2}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Level, $Message
    Write-Host $line
    Add-Content -Path $script:LogFile -Value $line
}

function Assert-Path {
    param(
        [Parameter(Mandatory = $true)][string]$PathValue,
        [Parameter(Mandatory = $true)][string]$Description
    )

    if (-not (Test-Path -LiteralPath $PathValue)) {
        throw "$Description bulunamadi: $PathValue"
    }
}

function Ensure-Directory {
    param([Parameter(Mandatory = $true)][string]$PathValue)

    New-Item -ItemType Directory -Force -Path $PathValue | Out-Null
}

function Copy-DirectoryContents {
    param(
        [Parameter(Mandatory = $true)][string]$SourcePath,
        [Parameter(Mandatory = $true)][string]$DestinationPath,
        [Parameter(Mandatory = $true)][string]$Description
    )

    Assert-Path -PathValue $SourcePath -Description $Description
    Ensure-Directory -PathValue $DestinationPath

    $items = @(Get-ChildItem -LiteralPath $SourcePath -Force)
    foreach ($item in $items) {
        Copy-Item -LiteralPath $item.FullName -Destination $DestinationPath -Recurse -Force
    }

    Write-BuildLog ("Kopyalandi | {0} | kaynak={1} | hedef={2} | oge_sayisi={3}" -f $Description, $SourcePath, $DestinationPath, $items.Count)
}

function Copy-OptionalDirectoryContents {
    param(
        [Parameter(Mandatory = $true)][string]$SourcePath,
        [Parameter(Mandatory = $true)][string]$DestinationPath,
        [Parameter(Mandatory = $true)][string]$Description
    )

    if (-not (Test-Path -LiteralPath $SourcePath)) {
        Ensure-Directory -PathValue $DestinationPath
        Write-BuildLog ("Atlandi | {0} | kaynak mevcut degil: {1}" -f $Description, $SourcePath) "WARN"
        return
    }

    Copy-DirectoryContents -SourcePath $SourcePath -DestinationPath $DestinationPath -Description $Description
}

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$resolvedOutputRoot = [System.IO.Path]::GetFullPath((Join-Path $projectRoot $OutputRoot))
$layoutRoot = Join-Path $resolvedOutputRoot "layout"
$manifestRoot = Join-Path $resolvedOutputRoot "manifests"
$artifactLogRoot = Join-Path $projectRoot "artifacts\logs"
Ensure-Directory -PathValue $artifactLogRoot
$script:LogFile = Join-Path $artifactLogRoot "liveos-foundation.log"
Set-Content -Path $script:LogFile -Value ""

$liveOsRoot = Join-Path $layoutRoot "liveos"
$bootRoot = Join-Path $layoutRoot "boot"
$appRoot = Join-Path $layoutRoot "app\CigerTool"
$appScriptsRoot = Join-Path $appRoot "scripts"
$toolsStageRoot = Join-Path $layoutRoot "tools"
$isosStageRoot = Join-Path $layoutRoot "isos"
$legacyIsoStageRoot = Join-Path $layoutRoot "iso-library"

foreach ($path in @($resolvedOutputRoot, $layoutRoot, $manifestRoot, $liveOsRoot, $bootRoot, $appRoot, $appScriptsRoot, $toolsStageRoot, $isosStageRoot, $legacyIsoStageRoot)) {
    Ensure-Directory -PathValue $path
}

$liveOsSourceRoot = Join-Path $projectRoot "liveos"
$shellSourceRoot = Join-Path $liveOsSourceRoot "shell"
$startupSourceRoot = Join-Path $liveOsSourceRoot "startup"
$appSourceRoot = [System.IO.Path]::GetFullPath((Join-Path $projectRoot $AppBuildRoot))
$toolsSourceRoot = [System.IO.Path]::GetFullPath((Join-Path $projectRoot $ToolsRoot))
$isosSourceRoot = [System.IO.Path]::GetFullPath((Join-Path $projectRoot $IsosRoot))
$legacyIsoSourceRoot = [System.IO.Path]::GetFullPath((Join-Path $projectRoot $LegacyIsoLibraryRoot))
$grubSourceRoot = Join-Path $projectRoot "build\assets\grub"
$prebootSourceRoot = Join-Path $projectRoot "build\assets\preboot"
$operationScripts = @(
    "invoke_smart_clone.ps1",
    "invoke_raw_clone.ps1",
    "invoke_boot_fix.ps1"
)

Assert-Path -PathValue $liveOsSourceRoot -Description "liveos kaynak kok dizini"
Assert-Path -PathValue $shellSourceRoot -Description "liveos shell dizini"
Assert-Path -PathValue $startupSourceRoot -Description "liveos startup dizini"
Assert-Path -PathValue $appSourceRoot -Description "paketlenmis CigerTool uygulamasi"

Copy-DirectoryContents -SourcePath $shellSourceRoot -DestinationPath (Join-Path $liveOsRoot "shell") -Description "liveos shell assetleri"
Copy-DirectoryContents -SourcePath $startupSourceRoot -DestinationPath (Join-Path $liveOsRoot "startup") -Description "liveos startup assetleri"
Copy-Item -LiteralPath (Join-Path $liveOsSourceRoot "README.md") -Destination (Join-Path $liveOsRoot "README.md") -Force
Write-BuildLog "liveos README staged."

Copy-DirectoryContents -SourcePath $appSourceRoot -DestinationPath $appRoot -Description "CigerTool uygulama paketi"
foreach ($scriptName in $operationScripts) {
    $sourceScript = Join-Path $projectRoot ("build\scripts\" + $scriptName)
    Assert-Path -PathValue $sourceScript -Description ("operasyon scripti " + $scriptName)
    Copy-Item -LiteralPath $sourceScript -Destination (Join-Path $appScriptsRoot $scriptName) -Force
    Write-BuildLog ("Operasyon scripti staged | kaynak={0} | hedef={1}" -f $sourceScript, (Join-Path $appScriptsRoot $scriptName))
}
Copy-OptionalDirectoryContents -SourcePath $toolsSourceRoot -DestinationPath $toolsStageRoot -Description "tools payload"
Copy-OptionalDirectoryContents -SourcePath $isosSourceRoot -DestinationPath $isosStageRoot -Description "isos payload"
Copy-OptionalDirectoryContents -SourcePath $legacyIsoSourceRoot -DestinationPath $legacyIsoStageRoot -Description "legacy iso-library payload"
Copy-DirectoryContents -SourcePath $grubSourceRoot -DestinationPath (Join-Path $bootRoot "grub") -Description "GRUB boot assetleri"
Copy-DirectoryContents -SourcePath $prebootSourceRoot -DestinationPath (Join-Path $bootRoot "preboot") -Description "preboot menu assetleri"

foreach ($subdir in @("windows", "linux", "tools")) {
    Ensure-Directory -PathValue (Join-Path $isosStageRoot $subdir)
}

$manifest = [ordered]@{
    product = [ordered]@{
        name = "CigerTool by hkannq"
        mode = "liveos-foundation"
        default_boot_entry = "CigerTool Live"
    }
    boot = [ordered]@{
        boot_menu_builder = "build/scripts/build_preboot_menu.ps1"
        grub_menu_generator = "build/scripts/generate_grub_menu.py"
        staged_grub_assets = "boot/grub"
        staged_preboot_assets = "boot/preboot"
        legacy_fallback_entry = "Legacy WinPE"
    }
    liveos = [ordered]@{
        shell_entry_point = "liveos/shell/Start-CigerToolLiveShell.ps1"
        session_entry_point = "liveos/startup/Start-CigerToolLiveSession.ps1"
        application_launcher = "liveos/startup/Start-CigerToolApp.ps1"
        startup_status_file = "liveos/logs/liveos-status.json"
        runtime_log_file = "liveos/logs/cigertool.log"
    }
    application = [ordered]@{
        python_entry_point = "cigertool.launcher:main"
        packaged_executable = "app/CigerTool/CigerTool.exe"
        operations_scripts = "app/CigerTool/scripts"
    }
    data = [ordered]@{
        tools_root = "tools"
        isos_root = "isos"
        iso_sections = @("windows", "linux", "tools")
        legacy_iso_root = "iso-library"
    }
    legacy = [ordered]@{
        winpe_build_script = "build/scripts/legacy/build_winpe_iso.ps1"
        adk_installer = "build/scripts/legacy/install_adk.ps1"
        winpe_startup_root = "winpe/files"
    }
}

$manifestPath = Join-Path $manifestRoot "liveos-foundation.json"
$manifest | ConvertTo-Json -Depth 8 | Set-Content -Path $manifestPath -Encoding utf8
Write-BuildLog ("Manifest yazildi: {0}" -f $manifestPath)
Write-BuildLog ("LiveOS foundation staging hazirlandi: {0}" -f $resolvedOutputRoot)
