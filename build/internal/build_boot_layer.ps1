param(
    [Parameter(Mandatory = $true)][string]$MediaRoot,
    [string]$ArtifactRoot = "artifacts",
    [string]$WorkspaceLoaderPath = "/EFI/Microsoft/Boot/bootmgfw.efi",
    [string]$WorkspaceBcdPath = "/EFI/Microsoft/Boot/BCD",
    [string]$WorkspaceVhdPath = "/workspace/CigerToolWorkspace.vhdx",
    [switch]$RequireMenu
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

function Convert-GrubPathToWindowsPath {
    param(
        [Parameter(Mandatory = $true)][string]$MediaRoot,
        [Parameter(Mandatory = $true)][string]$GrubPath
    )

    $trimmed = $GrubPath.Trim("/")
    if ([string]::IsNullOrWhiteSpace($trimmed)) {
        return $MediaRoot
    }

    return Join-Path $MediaRoot ($trimmed -replace "/", "\")
}

function Resolve-Wimboot {
    param(
        [string]$ProjectRoot,
        [string]$MediaRoot
    )

    $candidates = @(
        (Join-Path $ProjectRoot "boot\assets\preboot\wimboot"),
        (Join-Path $ProjectRoot "tools\boot\wimboot"),
        (Join-Path $MediaRoot "tools\boot\wimboot")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    $target = Join-Path $ProjectRoot "boot\assets\preboot\wimboot"
    try {
        Invoke-WebRequest -Uri "https://github.com/ipxe/wimboot/releases/latest/download/wimboot" -OutFile $target
        Write-BuildLog "wimboot indirildi: $target"
        return $target
    }
    catch {
        Write-BuildLog "wimboot indirilemedi: $($_.Exception.Message)" "WARN"
        return $null
    }
}

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$artifactDir = Join-Path $projectRoot $ArtifactRoot
New-Item -ItemType Directory -Force -Path $artifactDir | Out-Null
$script:LogFile = Join-Path $artifactDir "preboot-menu.log"
Set-Content -Path $script:LogFile -Value ""

$mediaPath = [System.IO.Path]::GetFullPath((Resolve-Path $MediaRoot).Path)
$grubAssetRoot = Join-Path $projectRoot "boot\assets\grub"
$vendorGrubEfi = Join-Path $grubAssetRoot "grubx64.efi"
$vendorBootEfi = Join-Path $grubAssetRoot "bootx64.efi"
$vendorSupportCfg = Join-Path $grubAssetRoot "grub.cfg"
$efiTargetDir = Join-Path $mediaPath "EFI\CigerTool"
$efiBootDir = Join-Path $mediaPath "EFI\Boot"
$bootGrubDir = Join-Path $mediaPath "boot\grub"
$efiDynamicCfg = Join-Path $efiTargetDir "grub.cfg"
$efiTargetPath = Join-Path $efiTargetDir "grubx64.efi"
$efiBootPath = Join-Path $efiBootDir "bootx64.efi"
$efiBootGrubPath = Join-Path $efiBootDir "grubx64.efi"
$bootGrubCfg = Join-Path $bootGrubDir "grub.cfg"
$bootManifestPath = Join-Path $efiTargetDir "boot-manifest.json"

foreach ($required in @($vendorGrubEfi, $vendorBootEfi, $vendorSupportCfg)) {
    if (-not (Test-Path -LiteralPath $required)) {
        $message = "Boot asset bulunamadi: $required"
        if ($RequireMenu) {
            throw $message
        }
        Write-BuildLog $message "WARN"
        return $false
    }
}

foreach ($path in @($efiTargetDir, $efiBootDir, $bootGrubDir)) {
    New-Item -ItemType Directory -Force -Path $path | Out-Null
}

Copy-Item -LiteralPath $vendorGrubEfi -Destination $efiTargetPath -Force
Copy-Item -LiteralPath $vendorBootEfi -Destination $efiBootPath -Force
Copy-Item -LiteralPath $vendorGrubEfi -Destination $efiBootGrubPath -Force
Copy-Item -LiteralPath $vendorSupportCfg -Destination (Join-Path $efiBootDir "grub.cfg") -Force
Copy-Item -LiteralPath $vendorSupportCfg -Destination $bootGrubCfg -Force
Write-BuildLog "GRUB EFI assetleri media root altina kopyalandi."

$wimbootSource = Resolve-Wimboot -ProjectRoot $projectRoot -MediaRoot $mediaPath
$wimbootGrubPath = ""
if ($wimbootSource -and (Test-Path -LiteralPath $wimbootSource)) {
    $wimbootTarget = Join-Path $efiTargetDir "wimboot"
    Copy-Item -LiteralPath $wimbootSource -Destination $wimbootTarget -Force
    $wimbootGrubPath = "/EFI/CigerTool/wimboot"
    Write-BuildLog "ISO Library icin wimboot staged: $wimbootTarget"
} else {
    Write-BuildLog "wimboot bulunamadi. Windows ISO fallback sadece EFI chainload ile kalacak." "WARN"
}

$renderScript = Join-Path $projectRoot "build\internal\render_boot_menu.py"
$generatorOutput = & python $renderScript `
    --media-root $mediaPath `
    --output $efiDynamicCfg `
    --workspace-loader-path $WorkspaceLoaderPath `
    --workspace-bcd-path $WorkspaceBcdPath `
    --workspace-vhd-path $WorkspaceVhdPath `
    --wimboot-path $wimbootGrubPath 2>&1 | ForEach-Object { $_.ToString() }
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $efiDynamicCfg)) {
    throw "Workspace pre-boot menusu uretilemedi."
}

foreach ($line in $generatorOutput) {
    if (-not [string]::IsNullOrWhiteSpace($line)) {
        Write-BuildLog "GRUB output: $line"
    }
}

$bootManifest = [ordered]@{
    product = "CigerTool Workspace"
    generated_at = (Get-Date).ToString("o")
    media_root = $mediaPath
    grub_cfg = $efiDynamicCfg
    workspace = [ordered]@{
        loader_path = $WorkspaceLoaderPath
        loader_present = (Test-Path -LiteralPath (Convert-GrubPathToWindowsPath -MediaRoot $mediaPath -GrubPath $WorkspaceLoaderPath))
        bcd_path = $WorkspaceBcdPath
        bcd_present = (Test-Path -LiteralPath (Convert-GrubPathToWindowsPath -MediaRoot $mediaPath -GrubPath $WorkspaceBcdPath))
        vhd_path = $WorkspaceVhdPath
        vhd_present = (Test-Path -LiteralPath (Convert-GrubPathToWindowsPath -MediaRoot $mediaPath -GrubPath $WorkspaceVhdPath))
        marker_present = (Test-Path -LiteralPath (Join-Path $mediaPath "CigerTool.workspace.json"))
    }
    iso_library = [ordered]@{
        windows_root = "/isos/windows"
        linux_root = "/isos/linux"
        tools_root = "/isos/tools"
        windows_present = (Test-Path -LiteralPath (Join-Path $mediaPath "isos\windows"))
        linux_present = (Test-Path -LiteralPath (Join-Path $mediaPath "isos\linux"))
        tools_present = (Test-Path -LiteralPath (Join-Path $mediaPath "isos\tools"))
        wimboot_path = $wimbootGrubPath
        wimboot_present = [bool]$wimbootGrubPath
    }
}
$bootManifest | ConvertTo-Json -Depth 6 | Set-Content -Path $bootManifestPath -Encoding utf8
Write-BuildLog "Boot manifest yazildi: $bootManifestPath"

Write-BuildLog "Workspace pre-boot menu hazirlandi: $efiDynamicCfg"
return $true
