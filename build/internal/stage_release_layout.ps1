param(
    [string]$WorkspaceWimPath = "inputs\workspace\install.wim",
    [string]$OutputRoot = "build-output\workspace",
    [string]$AppBuildRoot = "build-output\app\dist\CigerTool",
    [string]$PayloadRoot = "workspace\payload",
    [string]$ToolsRoot = "tools",
    [string]$IsoLibraryRoot = "iso-library",
    [int]$ImageIndex = 1,
    [int]$WorkspaceSizeGB = 48,
    [string]$WorkspaceVhdName = "CigerToolWorkspace.vhdx",
    [switch]$PlanOnly
)

$ErrorActionPreference = "Stop"

Write-Host "CigerTool Workspace build pipeline baslatiliyor."
Write-Host "Bu pipeline hazir workspace WIM -> hazir workspace -> USB boot layer modelini kurar."

& (Join-Path $PSScriptRoot "prepare_workspace_runtime.ps1") `
    -WorkspaceWimPath $WorkspaceWimPath `
    -OutputRoot $OutputRoot `
    -AppBuildRoot $AppBuildRoot `
    -PayloadRoot $PayloadRoot `
    -ToolsRoot $ToolsRoot `
    -IsoLibraryRoot $IsoLibraryRoot `
    -ImageIndex $ImageIndex `
    -WorkspaceSizeGB $WorkspaceSizeGB `
    -WorkspaceVhdName $WorkspaceVhdName `
    -PlanOnly:$PlanOnly

& (Join-Path $PSScriptRoot "build_boot_layer.ps1") `
    -MediaRoot (Join-Path $OutputRoot "usb-layout") `
    -WorkspaceLoaderPath "/EFI/Microsoft/Boot/bootmgfw.efi" `
    -WorkspaceVhdPath ("/workspace/" + $WorkspaceVhdName) `
    -RequireMenu
