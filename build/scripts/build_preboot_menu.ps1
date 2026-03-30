param(
    [Parameter(Mandatory = $true)][string]$MediaRoot,
    [string]$ArtifactRoot = "artifacts",
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

function Assert-Path {
    param(
        [Parameter(Mandatory = $true)][string]$PathValue,
        [Parameter(Mandatory = $true)][string]$Description
    )
    if (-not (Test-Path $PathValue)) {
        throw "$Description bulunamadi: $PathValue"
    }
}

function Get-BcdIdentifier {
    param([string]$Text)
    $match = [regex]::Match($Text, "{[^}]+}")
    if (-not $match.Success) {
        throw "BCD girdisi olusturuldu ama kimlik ayiklanamadi: $Text"
    }
    return $match.Value
}

function Add-UefiBootMenuEntry {
    param(
        [string]$StorePath,
        [string]$EfiRelativePath
    )

    if (-not (Test-Path $StorePath)) {
        Write-BuildLog "UEFI BCD store bulunamadi, menu girdisi atlandi: $StorePath" "WARN"
        return $false
    }

    $createOutput = & bcdedit /store $StorePath /create /d "ISO Library" /application BOOTAPP 2>&1 | Out-String
    $identifier = Get-BcdIdentifier $createOutput
    & bcdedit /store $StorePath /set $identifier device boot | Out-Null
    & bcdedit /store $StorePath /set $identifier path $EfiRelativePath | Out-Null
    & bcdedit /store $StorePath /set "{bootmgr}" displaybootmenu yes | Out-Null
    & bcdedit /store $StorePath /displayorder $identifier /addlast | Out-Null
    & bcdedit /store $StorePath /timeout 8 | Out-Null
    Write-BuildLog "UEFI boot menusune ISO Library girdisi eklendi: $identifier"
    return $true
}

function Resolve-Wimboot {
    param(
        [string]$ProjectRoot,
        [string]$MediaRoot
    )
    $candidates = @(
        (Join-Path $ProjectRoot "build\assets\preboot\wimboot"),
        (Join-Path $ProjectRoot "tools\boot\wimboot"),
        (Join-Path $MediaRoot "tools\boot\wimboot")
    )
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    $target = Join-Path $ProjectRoot "build\assets\preboot\wimboot"
    try {
        Invoke-WebRequest -Uri "https://github.com/ipxe/wimboot/releases/latest/download/wimboot" -OutFile $target
        Write-BuildLog "wimboot indirildi: $target"
        return $target
    } catch {
        Write-BuildLog "wimboot indirilemedi: $($_.Exception.Message)" "WARN"
        return $null
    }
}

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$artifactDir = Join-Path $projectRoot $ArtifactRoot
New-Item -ItemType Directory -Force -Path $artifactDir | Out-Null
$script:LogFile = Join-Path $artifactDir "preboot-menu.log"
Set-Content -Path $script:LogFile -Value ""

$grubAssetRoot = Join-Path $projectRoot "build\assets\grub"
$vendorGrubEfi = Join-Path $grubAssetRoot "grubx64.efi"
$vendorBootEfi = Join-Path $grubAssetRoot "bootx64.efi"
$vendorSupportCfg = Join-Path $grubAssetRoot "grub.cfg"
foreach ($item in @(
    @{ Path = $vendorGrubEfi; Description = "Prebuilt GRUB EFI binary" },
    @{ Path = $vendorBootEfi; Description = "Prebuilt removable GRUB EFI binary" },
    @{ Path = $vendorSupportCfg; Description = "GRUB support config" }
)) {
    if (-not (Test-Path $item.Path)) {
        $message = "$($item.Description) bulunamadi: $($item.Path)"
        if ($RequireMenu) {
            throw $message
        }
        Write-BuildLog $message "WARN"
        return $false
    }
}

$mediaPath = (Resolve-Path $MediaRoot).Path
$efiTargetDir = Join-Path $mediaPath "EFI\CigerTool"
$efiBootDir = Join-Path $mediaPath "EFI\Boot"
$efiDebianDir = Join-Path $mediaPath "EFI\debian"
$bootGrubDir = Join-Path $mediaPath "boot\grub"
$bootGrubArchDir = Join-Path $bootGrubDir "x86_64-efi"
$efiTargetPath = Join-Path $efiTargetDir "grubx64.efi"
$efiDynamicCfg = Join-Path $efiTargetDir "grub.cfg"
$efiBootFallback = Join-Path $efiTargetDir "platformbootx64.efi"
$efiBootPath = Join-Path $efiBootDir "bootx64.efi"
$efiBootGrubPath = Join-Path $efiBootDir "grubx64.efi"
$efiBootCfg = Join-Path $efiBootDir "grub.cfg"
$efiDebianCfg = Join-Path $efiDebianDir "grub.cfg"
$bootGrubCfg = Join-Path $bootGrubDir "grub.cfg"
$bootGrubArchCfg = Join-Path $bootGrubArchDir "grub.cfg"
foreach ($path in @($efiTargetDir, $efiBootDir, $efiDebianDir, $bootGrubDir, $bootGrubArchDir)) {
    New-Item -ItemType Directory -Force -Path $path | Out-Null
}

if ((Test-Path $efiBootPath) -and -not (Test-Path $efiBootFallback)) {
    Copy-Item -Path $efiBootPath -Destination $efiBootFallback -Force
    Write-BuildLog "Platform fallback bootx64.efi yedeklendi: $efiBootFallback"
}

Copy-Item -Path $vendorGrubEfi -Destination $efiTargetPath -Force
Copy-Item -Path $vendorBootEfi -Destination $efiBootPath -Force
Copy-Item -Path $vendorGrubEfi -Destination $efiBootGrubPath -Force
Copy-Item -Path $vendorSupportCfg -Destination $efiBootCfg -Force
Copy-Item -Path $vendorSupportCfg -Destination $efiDebianCfg -Force
Copy-Item -Path $vendorSupportCfg -Destination $bootGrubCfg -Force
Copy-Item -Path $vendorSupportCfg -Destination $bootGrubArchCfg -Force
Write-BuildLog "Prebuilt GRUB EFI binary ve destek dosyalari medyaya kopyalandi."

$wimbootSource = Resolve-Wimboot -ProjectRoot $projectRoot -MediaRoot $mediaPath
$wimbootTarget = Join-Path $efiTargetDir "wimboot"
$wimbootGrubPath = ""
if (-not $wimbootSource -or -not (Test-Path $wimbootSource)) {
    throw "wimboot bulunamadi. CigerTool Live varsayilan boot yolu dogrudan boot.wim yuklemesi gerektirir."
}

Copy-Item -Path $wimbootSource -Destination $wimbootTarget -Force
$wimbootGrubPath = "/EFI/CigerTool/wimboot"

$renderScript = Join-Path $projectRoot "build\scripts\generate_grub_menu.py"
$generatorOutput = & python $renderScript --media-root $mediaPath --output $efiDynamicCfg --wimboot-path $wimbootGrubPath 2>&1 | ForEach-Object { $_.ToString() }
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $efiDynamicCfg)) {
    throw "Dinamik GRUB menu uretilemedi."
}
foreach ($line in $generatorOutput) {
    if (-not [string]::IsNullOrWhiteSpace($line)) {
        Write-BuildLog "GRUB profil: $line"
    }
}
Write-BuildLog "Dinamik GRUB menu hazirlandi: $efiDynamicCfg"

$bcdStore = Join-Path $mediaPath "EFI\Microsoft\Boot\BCD"
$added = Add-UefiBootMenuEntry -StorePath $bcdStore -EfiRelativePath "\EFI\CigerTool\grubx64.efi"
if (-not $added -and $RequireMenu) {
    throw "UEFI boot menusu olusturulamadi."
}

return $true
