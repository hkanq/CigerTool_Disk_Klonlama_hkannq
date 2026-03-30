# Product Vision

## Decision Summary

CigerTool by hkannq is no longer a WinPE-first recovery USB project.

The product target is now a branded, desktop-first live Windows experience that boots from USB and feels like a lightweight but real maintenance OS. CigerTool launches automatically inside that environment as a normal application, while the same USB also provides an ISO Library and bundled utilities.

This changes the primary architectural goal from:

- "boot WinPE and run the app as the shell"

to:

- "boot into a usable live Windows desktop environment and run CigerTool inside it"

## Target User Experience

### Intended boot flow

1. User boots from the USB device.
2. A branded boot menu appears.
3. Default entry is `CigerTool Live`.
4. The system enters a minimal but desktop-capable Windows environment.
5. CigerTool launches automatically.
6. The user can use the desktop, open files, run tools, and optionally boot other ISOs.

### Expected boot menu entries

- `CigerTool Live`
- `ISO Library`
- `Diagnostics / Utilities`

### Things the user should not see

- Windows Setup chooser
- installer-first workflows
- broken shell fallbacks
- reboot loops after Windows logo
- product behavior that feels like an ADK experiment instead of a finished tool

## Product Pillars

### 1. Live desktop environment

A lightweight Windows-based live runtime must provide:

- a desktop-like session
- file explorer access
- basic shell usability
- stable startup and shutdown behavior

### 2. CigerTool application

The main app remains the center of the product and must provide:

- disk inspection
- cloning and migration workflows
- boot repair planning and execution
- health / SMART visibility
- file management access
- logs and diagnostics

### 3. Bundled tool ecosystem

The product must include or support:

- preloaded diagnostics and recovery tools
- a launcher experience
- a clear place for user-added tools

### 4. ISO Library

The same USB must support user-added ISO files for:

- Windows installers / recovery media
- Linux live systems
- utility / rescue media

This should feel integrated, categorized, and productized rather than bolted on.

### 5. Branded product experience

The final system should feel intentional:

- clean boot flow
- branded menu wording
- consistent naming
- understandable recovery behavior
- coherent docs and staging

## Non-Goals

These are explicitly not the product target:

- shipping "just WinPE with a custom shell"
- relying on Windows Setup as the primary live runtime
- endless patching of setup-chain quirks instead of correcting the architecture
- treating build scripts as the product

## Success Criteria

The product direction is considered aligned when all of the following are true:

- USB boots into a desktop-capable Windows live session
- CigerTool auto-starts reliably
- user can access files and tools without fighting the environment
- ISO Library works from the same USB
- the boot path avoids Windows Setup chooser behavior
- the repo structure clearly separates product logic from runtime / boot assembly

## Implications For Development

- Reusable app logic should be preserved where possible.
- WinPE-only assumptions should no longer define the architecture.
- Product assembly, runtime environment, and boot logic need clearer boundaries.
- Progress must remain resumable through explicit status and planning documents.
