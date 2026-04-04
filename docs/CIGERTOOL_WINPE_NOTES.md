# CigerTool WinPE Notes

## Locked Boundary

`CigerTool OS` uses a Windows 10 PE base supplied externally by the user.

This repository must not:

- build WinPE
- install or require Windows ADK
- generate `boot.wim`
- construct the OS image

This repository is responsible only for:

- the `CigerTool` application
- app folder layout guidance
- startup/autolaunch guidance
- bundled tool layout guidance
- `\isos` folder expectations

## App Readiness For WinPE

The app is now shaped for later WinPE drop-in use because it:

- uses C# only
- has no Python dependency
- does not assume a normal installer
- tolerates missing optional components
- supports app-local writable storage
- keeps tool paths configurable
- does not require first-run questions

The repo also now defines a dedicated WinPE-oriented publish variant from the same codebase:

- `artifacts/winpe/CigerTool.WinPE.exe`
- `winpe.mode`
- `portable.mode`
- `Config\appsettings.override.json`

## Recommended Runtime Layout Inside WinPE

If the app is embedded into the external WinPE environment, the recommended runtime layout is:

```text
X:\CigerTool\
  CigerTool.WinPE.exe
  appsettings.json
  tools.catalog.json
  winpe.mode
  portable.mode
  Config\
  Tools\
  Data\                       (optional but recommended when writable)
```

If the external WinPE process instead launches the app from the boot media, keep the same relative layout under a single `CigerTool` folder.

## Recommended USB Media Layout

At the USB root, keep:

```text
\CigerTool\
\isos\
```

`\isos` is mandatory for the product line and must remain available for future ISO or multiboot workflows.

## Startup Integration Guidance

The WinPE integration should auto-launch CigerTool after WinPE initialization.

Recommended pattern:

1. run `wpeinit`
2. start `CigerTool.exe` from the prepared app location

Example direction for the external WinPE integrator:

```cmd
wpeinit
start "" X:\CigerTool\CigerTool.WinPE.exe
```

If the app lives on the boot media instead of `X:\`, the external integration layer should detect the correct media drive letter first and then launch the same relative app path.

## Writable Data Behavior In WinPE

In WinPE-oriented environments the app prefers app-local storage first:

- `.\Data\Logs`
- `.\Data\Cache`
- `.\Data\Downloads`
- `.\Data\Config`

If app-local storage is not writable, the app falls back to:

- `%TEMP%\CigerTool`

This is important because WinPE environments may have different writable-drive behavior.

## Optional Component Behavior

The app now fails gracefully when optional files are missing:

- missing `appsettings.json` falls back to defaults
- missing `tools.catalog.json` falls back to the built-in catalog
- missing bundled tools show as unavailable
- missing override files are ignored

## Tool Packaging Notes

Bundled tools should live under `Tools\` next to the executable and should be referenced through the JSON tool catalog.

Practical guidance:

- keep tool folders self-contained
- avoid installers
- prefer portable executables
- keep licensing and version tracking outside the runtime code path

## Release-Source Notes In WinPE

USB Creator still uses the same three modes in WinPE-oriented deployments:

- remote manifest
- local override
- manual image selection

Override files can be supplied through the writable config root or the app-local `Config\` folder.

## Current Limitation

These notes prepare the app for WinPE integration, but this prompt deliberately does not build or modify a WinPE base.
