# CigerTool Deployment

## Goal

This document describes how `CigerTool App` should be packaged and deployed for:

- standalone Windows desktop use
- later drop-in use inside an external Windows 10 PE environment

This document does not define WinPE image construction.

## Publish Strategy

The app is prepared for two self-contained single-file publish variants from the same codebase.

### Standard Desktop Publish

- publish profile: `standard-x64-single-file`
- output root: `artifacts/app/`
- executable: `CigerTool.exe`
- profile flavor: `Standard`

### WinPE-Oriented Publish

- publish profile: `winpe-x64-single-file`
- output root: `artifacts/winpe/`
- executable: `CigerTool.WinPE.exe`
- profile flavor: `WinPE`
- includes `winpe.mode`, `portable.mode`, and `Config\appsettings.override.json`

Common publish properties:

- runtime: `win-x64`
- self-contained: `true`
- single-file: `true`
- trimming: `false`
- ready-to-run: `false`
- native libraries: self-extract enabled

Recommended publish command:

```powershell
dotnet publish app/CigerTool.App/CigerTool.App.csproj -c Release -p:PublishProfile=standard-x64-single-file
dotnet publish app/CigerTool.App/CigerTool.App.csproj -c Release -p:PublishProfile=winpe-x64-single-file
```

Or:

```powershell
powershell -ExecutionPolicy Bypass -File build/scripts/Publish-CigerTool.ps1
```

## Deployment Model

Single-file does not mean single artifact only.

The executable is single-file, but deployment intentionally keeps configuration and catalog files external so operators can update them safely:

- `appsettings.json`
- `tools.catalog.json`
- optional `Config\appsettings.override.json`
- optional `Config\release-source.override.json`
- optional bundled tool files under `Tools\`

## Recommended Standalone Layout

```text
CigerTool/
  CigerTool.exe
  appsettings.json
  tools.catalog.json
  portable.mode                  (optional)
  Config/
    appsettings.override.json    (optional)
    release-source.override.json (optional)
  Tools/
    ...
  Data/                          (optional for portable mode)
```

## Recommended WinPE-Oriented Layout

```text
CigerTool/
  CigerTool.WinPE.exe
  appsettings.json
  tools.catalog.json
  winpe.mode
  portable.mode
  Config/
    appsettings.override.json
    release-source.override.json (optional)
  Tools/
    ...
  Data/                          (recommended)
```

## Writable Runtime Layout

At runtime the app resolves a writable `DataRoot` and creates:

```text
<DataRoot>/
  Cache/
  Config/
  Downloads/
  Logs/
```

Resolution order:

- desktop prefers `%LocalAppData%\CigerTool`
- portable or WinPE-oriented mode prefers `.\Data`
- temporary fallback uses `%TEMP%\CigerTool`

Portable mode can be activated by:

- a `portable.mode` marker next to the executable
- `CIGERTOOL_PORTABLE=1`

WinPE-safe profile behavior can be activated by:

- a `winpe.mode` marker next to the executable
- `CIGERTOOL_FORCE_WINPE=1`

## Bundled Tool Layout

Bundled tool paths should resolve relative to the app root or the `Tools\` folder.

Recommended pattern:

```text
Tools/
  CrystalDiskInfo/
    DiskInfo64.exe
```

The tool catalog can use these runtime tokens:

- `{BaseDirectory}`
- `{ToolsDirectory}`
- `{LogDirectory}`
- `{DataRoot}`

This avoids hardcoded user-profile paths and keeps the same tool catalog usable across deployment modes.

## Configuration Rules

- ship a baseline `appsettings.json`
- keep operator-specific overrides in `Config\`
- do not hardcode a final image URL in source code
- use the manifest-based release source system for USB Creator

## Logging Rules

Logs are written under the resolved writable data root:

- text log: `<DataRoot>\Logs\cigertool.log`
- structured log: `<DataRoot>\Logs\cigertool.jsonl`

Crash reporting uses the same resolved log strategy.

## Startup Behavior

The app should start cleanly even when optional components are absent.

Expected startup behavior:

- create writable runtime directories
- run startup self-check
- show shell without blocking on USB enumeration
- use defaults when optional config files are missing
- show missing bundled tools as unavailable rather than crashing

## Build Differences

### Standard Desktop Build

- executable name is `CigerTool.exe`
- uses normal desktop profile detection
- keeps full feature surface enabled

### WinPE-Oriented Build

- executable name is `CigerTool.WinPE.exe`
- ships with a `winpe.mode` marker so the same codebase starts in WinPE-safe profile behavior
- also ships with `portable.mode` so writable paths prefer app-local `Data\`
- ships with `Config\appsettings.override.json` to label the app as `CigerTool WinPE`

## How To Run

### Standard Desktop Build

- open `artifacts/app/CigerTool.exe`
- or launch from PowerShell:

```powershell
.\artifacts\app\CigerTool.exe
```

### WinPE-Oriented Build

- copy the `artifacts/winpe/` folder into the external WinPE environment
- launch `CigerTool.WinPE.exe`
- or from WinPE shell:

```cmd
start "" X:\CigerTool\CigerTool.WinPE.exe
```

## Current Limitation

This repository now contains publish-ready project settings and documentation, but this environment does not currently have a `.NET SDK`, so the publish command could not be executed in this prompt.
