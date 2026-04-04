param(
    [string]$Configuration = "Release"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Path (Split-Path -Path $PSScriptRoot -Parent) -Parent
$projectPath = Join-Path $repoRoot "app\CigerTool.App\CigerTool.App.csproj"

$sdkList = & dotnet --list-sdks
if ([string]::IsNullOrWhiteSpace(($sdkList | Out-String))) {
    throw ".NET SDK bulunamadi. En az .NET 8 SDK yukleyin ve tekrar deneyin."
}

$profiles = @(
    "standard-x64-single-file",
    "winpe-x64-single-file"
)

foreach ($artifactRoot in @(
    (Join-Path $repoRoot "artifacts\app"),
    (Join-Path $repoRoot "artifacts\winpe")
)) {
    if (Test-Path $artifactRoot) {
        Get-ChildItem -Path $artifactRoot -Force | Remove-Item -Recurse -Force
    }
    else {
        New-Item -ItemType Directory -Path $artifactRoot | Out-Null
    }
}

foreach ($profile in $profiles) {
    & dotnet publish $projectPath -c $Configuration -p:PublishProfile=$profile
    if ($LASTEXITCODE -ne 0) {
        throw "Publish basarisiz oldu: $profile"
    }
}

Get-ChildItem -Path (Join-Path $repoRoot "artifacts") -Recurse -Filter *.pdb -File | Remove-Item -Force

Write-Host "Publish tamamlandi."
Write-Host "Standard: $repoRoot\artifacts\app\CigerTool.exe"
Write-Host "WinPE:    $repoRoot\artifacts\winpe\CigerTool.WinPE.exe"
