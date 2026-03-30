# CigerTool LiveOS Foundation

This directory defines the new desktop-first runtime boundary for `CigerTool Live`.

The goal of this layer is not to describe WinPE shell overrides. It describes the future live session model for the product.

## Ownership

- `shell/`
  - runtime shell entry points
  - starts the desktop-facing session
- `startup/`
  - session bootstrap
  - CigerTool auto-launch orchestration

## Expected Boot To App Flow

1. Boot menu default entry is `CigerTool Live`.
2. The boot layer hands control to the native live OS runtime.
3. The runtime shell entry point runs `liveos/shell/Start-CigerToolLiveShell.ps1`.
4. The shell entry point starts the session bootstrap in `liveos/startup/Start-CigerToolLiveSession.ps1`.
5. The session bootstrap launches `liveos/startup/Start-CigerToolApp.ps1`.
6. The app launcher starts the packaged `CigerTool.exe` or falls back to `python -m cigertool`.

## Important Rules

- The live OS shell is the product shell boundary.
- CigerTool is an application launched inside that environment, not the shell itself.
- WinPE startup files under `winpe/` are legacy references and must not define the future default architecture.

## Current Stage

Prompt 2 established this folder structure and the startup contracts.

Prompt 3 connected the default boot path into this flow instead of the old installer-first behavior.

Prompt 4 connected CigerTool runtime requirements to this layer:

- runtime root discovery
- operation script staging
- live log location
- app auto-start contract
- tool and ISO root propagation

The remaining work is no longer "make this structure real". The remaining work is product polish and expanding the desktop utility layer on top of this structure.

See also:

- `liveos/startup/README.md`
