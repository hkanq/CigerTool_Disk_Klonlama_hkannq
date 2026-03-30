# LiveOS Startup Chain

This file documents the first real boot-to-shell chain used by `CigerTool Live`.

## Current Prompt 3 Boot Flow

1. USB firmware loads the removable media EFI entry.
2. GRUB loads from the preboot layer.
3. Default menu entry is `CigerTool Live`.
4. `CigerTool Live` loads `/EFI/CigerTool/wimboot`.
5. `wimboot` loads:
   - `/EFI/Microsoft/Boot/bootmgfw.efi`
   - `/EFI/Microsoft/Boot/BCD`
   - `/boot/boot.sdi`
   - `/sources/boot.wim`
6. The runtime enters the staged live environment image instead of the Windows Setup chooser path.
7. WinPE bootstrap files act only as a thin compatibility shim:
   - `startnet.cmd` runs `wpeinit`
   - `winpeshl.ini` launches `cmd.exe /k X:\Windows\System32\cigertool-launch.cmd`
8. `cigertool-launch.cmd` starts `X:\CigerToolLive\shell\Start-CigerToolLiveShell.ps1`
9. `Start-CigerToolLiveShell.ps1` initializes the shell layer and starts `Start-CigerToolLiveSession.ps1`
10. `Start-CigerToolLiveSession.ps1` exports runtime variables for the app layer:
   - `CIGERTOOL_RUNTIME=liveos`
   - `CIGERTOOL_RUNTIME_ROOT`
   - `CIGERTOOL_SCRIPTS_ROOT`
   - `CIGERTOOL_LOG_ROOT`
   - optional `CIGERTOOL_TOOLS_ROOT` and `CIGERTOOL_ISOS_ROOT`
11. `Start-CigerToolLiveSession.ps1` calls `Start-CigerToolApp.ps1`
12. `Start-CigerToolApp.ps1` launches the packaged `CigerTool.exe` with a stable working directory

## Why This Removes The Previous Blocker

The previous default path chainloaded platform Windows boot files and could fall into installer-oriented boot behavior. The new default path loads the staged runtime image directly through `wimboot`, so the product no longer depends on Windows Setup UI as the first interaction.

## Prompt 4 Runtime Contract

- CigerTool disk and boot operations no longer assume `build\scripts\...` relative paths.
- Operation scripts are staged into the live runtime under `CigerTool\scripts` or `app\CigerTool\scripts`.
- The application resolves logs, tools, ISO roots, and operation scripts from the live runtime first, then falls back to the repo layout for development.

## Prompt 7 Reliability Contract

Prompt 7 finalized the startup behavior for near-production demo quality.

The startup chain now also writes a runtime status file:

- `liveos/logs/liveos-status.json`

That file records:

- current startup stage
- health state
- last startup message
- runtime root
- log paths
- app launch metadata when available

The application reads this file and surfaces degraded or failed startup states to the user.

## Current Safety Rules

- If CigerTool fails to start, the shell must stay alive.
- The startup path must not reboot just because the app exits or fails.
- Failure should leave an interactive shell available for recovery.
- Recovery shell messaging must point the user to:
  - startup status file
  - runtime log file
