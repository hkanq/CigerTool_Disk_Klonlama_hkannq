# Architecture Rewrite Plan

## Prompt 1 And Prompt 2 Scope

This document started as the architecture assessment for Prompt 1. It now also records the Prompt 2 repository reset that introduced the first explicit desktop-first foundation structure.

## Current Architecture Snapshot

The current repository has four major layers:

### 1. Application layer

- `cigertool/ui/`
- `cigertool/services/`
- `cigertool/models.py`
- `cigertool/app_context.py`
- `cigertool/commands.py`

This is a PySide6 desktop application with domain-ish service logic for:

- disk discovery
- clone planning
- SMART snapshots
- ISO discovery and profiling
- tools discovery
- execution of external scripts

### 2. Build and runtime assembly layer

- `build/scripts/build_app.ps1`
- `build/scripts/build_winpe_iso.ps1`
- `build/scripts/install_adk.ps1`

This layer currently assumes a Windows ADK + WinPE workflow. It builds the app, stages WinPE media, mounts `boot.wim`, injects packages and startup files, then assembles an ISO.

### 3. Boot and multiboot layer

- `build/scripts/build_preboot_menu.ps1`
- `build/scripts/generate_grub_menu.py`
- `build/assets/grub/`
- `build/assets/preboot/`

This layer builds a GRUB-based preboot menu and ISO Library behavior.

### 4. WinPE startup override layer

- `winpe/files/Windows/System32/startnet.cmd`
- `winpe/files/Windows/System32/winpeshl.ini`
- `winpe/files/Windows/System32/cigertool-launch.cmd`

This layer forces WinPE to run CigerTool as the shell.

## Key Architectural Problem

The current repo has a solid application core and a partially useful preboot layer, but its runtime assembly path is fundamentally built around WinPE and boot-manager chaining. That is the wrong substrate for the new product target.

The repo is currently optimized for:

- injecting CigerTool into WinPE
- booting through WinPE / Windows boot assets
- treating shell override as the product runtime

The new product requires:

- a desktop-capable live Windows environment
- app autostart inside that environment
- a product shell experience rather than a WinPE shell hack

## Classification

## Preserve

These parts are valuable and should remain central unless later evidence proves otherwise.

### Application/domain logic

- `cigertool/models.py`
- `cigertool/services/clone_service.py`
- `cigertool/services/disk_service.py`
- `cigertool/services/smart_service.py`
- `cigertool/services/tools_service.py`
- `cigertool/services/multiboot_service.py`
- `cigertool/services/execution_service.py`
- `cigertool/commands.py`
- `cigertool/logger.py`
- `cigertool/app_context.py`

Why preserve:

- these files encode product behavior rather than WinPE boot assumptions
- clone analysis and ISO profiling logic are directly reusable
- command execution and logging primitives remain relevant in any Windows-based live runtime

### Existing tests worth keeping

- `tests/test_clone_service.py`
- `tests/test_disk_service.py`
- `tests/test_multiboot_service.py`
- `tests/test_generate_grub_menu.py`

Why preserve:

- they protect logic that remains product-relevant after the runtime rewrite

## Preserve, But Adapt

These parts are useful, but their integration model must change.

### UI layer

- `cigertool/ui/main_window.py`
- `cigertool/ui/workers.py`
- `cigertool/ui/style.py`

Why adapt:

- the app UI itself is reusable
- the product now needs a better relationship between "app window" and "desktop environment"
- some UI wording and surrounding flows still assume a narrower WinPE maintenance context

### Boot repair and execution boundary

- `cigertool/services/boot_service.py`
- `build/scripts/invoke_boot_fix.ps1`

Why adapt:

- the capability is still useful
- the execution assumptions may need to change in the new runtime

### App packaging

- `build/scripts/build_app.ps1`

Why adapt:

- PyInstaller packaging remains useful
- the app package target should become part of a larger product assembly pipeline, not only a WinPE payload

### Preboot / ISO Library assets

- `build/scripts/build_preboot_menu.ps1`
- `build/scripts/generate_grub_menu.py`
- `build/assets/grub/`
- `build/assets/preboot/`

Why adapt:

- the ISO Library remains a required product feature
- the menu flow should no longer treat WinPE boot manager as the primary runtime handoff
- `build_preboot_menu.ps1` currently has explicit `winpebootx64.efi` and BCD-store assumptions that need to be redirected toward `CigerTool Live`

## Replace

These areas are tightly coupled to the old architecture and should not remain the product backbone.

### WinPE runtime assembly

- `build/scripts/build_winpe_iso.ps1`
- `build/scripts/install_adk.ps1`
- `winpe/files/`
- current `docs/WINPE_BUILD.md` assumptions

Why replace:

- they are centered on ADK / WinPE staging, `copype`, `boot.wim`, DISM package injection, and `winpeshl` shell takeover
- that is precisely the architecture the new product direction rejects as the primary runtime

### Workflow naming and build intent

- `.github/workflows/build-iso.yml`

Why replace or refactor:

- the workflow is explicitly named and structured around `build-winpe-iso`
- the future pipeline should describe product assembly for `CigerTool Live`, not only WinPE ISO construction

## Retire Or De-emphasize

These items are not immediately deleted in Prompt 1, but should be treated as legacy or transitional.

- existing README sections that still describe the product as WinPE-first
- `docs/MIMARI.md` and `docs/WINPE_BUILD.md` as authoritative architecture docs
- `tests/test_preboot_assets.py` in its current shape if it only validates legacy preboot assumptions

## Target Architecture Direction

The future product should be split conceptually into these layers:

### 1. Product application core

- the existing `cigertool/` application logic
- reused services and tests

### 2. Live runtime environment layer

- scripts and assets for building a desktop-capable live Windows environment
- session startup logic
- app autostart logic
- desktop basics / explorer / bundled tool integration

### 3. Boot layer

- branded boot menu
- default `CigerTool Live` entry
- ISO Library boot entries
- fallback / diagnostics entries

### 4. Product assembly layer

- product packaging and media layout
- integration of app package, runtime environment, tools, and ISO Library
- CI pipeline for product artifacts

Prompt 2 established the first repository structure that implements these boundaries.

## Prompt 2 Execution Result

Prompt 2 completed the repository-level architecture reset without attempting the full live OS implementation.

### What changed structurally

- introduced `liveos/` as a first-class runtime layer
- added explicit shell and startup contracts under:
  - `liveos/shell/`
  - `liveos/startup/`
- introduced `build/scripts/build_liveos_foundation.ps1` as the new product-oriented staging path
- extracted the old WinPE build scripts into `build/scripts/legacy/`
- left compatibility wrappers at:
  - `build/scripts/build_winpe_iso.ps1`
  - `build/scripts/install_adk.ps1`
- changed the packaged app entrypoint to `cigertool.launcher:main`
- renamed the GRUB default product entry from `CigerTool (WinPE)` to `CigerTool Live`
- changed the default CI path to a LiveOS foundation build workflow and demoted the old WinPE ISO workflow to a legacy path

### New repository boundaries after Prompt 2

#### Boot layer

- `build/assets/grub/`
- `build/assets/preboot/`
- `build/scripts/build_preboot_menu.ps1`
- `build/scripts/generate_grub_menu.py`

#### Live OS layer

- `liveos/README.md`
- `liveos/shell/Start-CigerToolLiveShell.ps1`
- `liveos/startup/Start-CigerToolLiveSession.ps1`
- `liveos/startup/Start-CigerToolApp.ps1`

#### Application layer

- `cigertool/`
- `cigertool/launcher.py`
- `cigertool/__main__.py`

#### Product assembly layer

- `build/scripts/build_app.ps1`
- `build/scripts/build_liveos_foundation.ps1`
- `.github/workflows/build-liveos-foundation.yml`

#### Legacy transitional layer

- `build/scripts/legacy/build_winpe_iso.ps1`
- `build/scripts/legacy/install_adk.ps1`
- `winpe/files/`
- `.github/workflows/build-iso.yml`

## Prompt 3 Execution Result

Prompt 3 converted the default boot model from "chain into platform Windows boot files and hope the right UI appears" into an explicit live-runtime startup chain.

### What was blocking before

The previous default path for `CigerTool Live` still depended on chainloading platform EFI files. In practice that could fall into Windows Setup chooser behavior or reboot-oriented installer flow because the first interaction was still driven by Windows boot UI instead of the product runtime contract.

### What changed in Prompt 3

- the GRUB `CigerTool Live` entry now uses `wimboot` to load the staged runtime image directly
- the default entry now targets:
  - `/EFI/CigerTool/wimboot`
  - `/EFI/Microsoft/Boot/BCD`
  - `/boot/boot.sdi`
  - `/sources/boot.wim`
- the previous direct default chainload path to platform boot files was removed from the GRUB entry
- the mounted runtime image now receives:
  - `liveos/shell/`
  - `liveos/startup/`
- the WinPE startup files now act only as a thin bootstrap into the new `liveos` shell contract
- the startup scripts were changed so shell failure falls back to an interactive environment instead of crashing the session
- a product-facing transitional build entry was introduced at `build/scripts/build_cigertool_live_iso.ps1`

### Current Prompt 3 startup chain

1. GRUB default entry: `CigerTool Live`
2. `wimboot` loads the staged runtime image directly
3. `startnet.cmd` runs `wpeinit`
4. `winpeshl.ini` launches `cmd.exe /k X:\Windows\System32\cigertool-launch.cmd`
5. `cigertool-launch.cmd` starts `X:\CigerToolLive\shell\Start-CigerToolLiveShell.ps1`
6. `Start-CigerToolLiveShell.ps1` starts `Start-CigerToolLiveSession.ps1`
7. `Start-CigerToolLiveSession.ps1` starts `Start-CigerToolApp.ps1`
8. `Start-CigerToolApp.ps1` attempts to launch the packaged app

### Current interpretation

This is a transitional live-environment implementation. It is not yet the final polished desktop substrate, but it is designed to bypass Windows Setup UI as the default product path and keep the runtime alive even if app startup fails.

## Deprecated Or Transitional Paths After Prompt 2

These paths are still present, but they are now explicitly transitional and must not drive the future default architecture:

- `build/scripts/legacy/build_winpe_iso.ps1`
- `build/scripts/legacy/install_adk.ps1`
- `winpe/files/`
- `docs/WINPE_BUILD.md`
- `docs/MIMARI.md`
- `.github/workflows/build-iso.yml`

The wrappers at `build/scripts/build_winpe_iso.ps1` and `build/scripts/install_adk.ps1` are compatibility shims only.

## Immediate Migration Strategy

### Prompt 1

- document current state
- classify components
- create resumability docs

### Prompt 2

- define the new repository structure
- isolate legacy WinPE path
- introduce new live-environment architecture concepts
- add the first liveos startup and shell contracts
- create a product-oriented build foundation path

### Prompt 3

- build the first desktop-first runtime path
- replace setup-chain behavior with intended product entry

## Major Risks And Open Questions

### 1. Live Windows substrate choice

The product direction is clear, but the exact Windows-based live runtime substrate still needs a concrete implementation decision in Prompt 3.

### 2. Licensing and redistribution constraints

Any real live Windows desktop approach will need explicit handling of licensing, redistribution, and image-origin assumptions.

### 3. Writable USB product design

The final USB must support:

- boot assets
- app/runtime assets
- bundled tools
- user-added ISOs

That storage layout needs to be part of the new architecture, not an afterthought.

### 4. Startup reliability

The repo must avoid falling back into:

- Windows Setup chooser
- boot manager ambiguity
- reboot loops

This is a first-class architecture constraint, not a later polish issue.

## Prompt 4 Execution Result

Prompt 4 completed the first core product integration pass inside the new runtime model.

### What was still missing after Prompt 3

Prompt 3 established the boot path and startup chain, but the runtime still had three important gaps:

- clone and boot repair actions still assumed repo-relative `build\scripts\...` paths
- logs, tools, and ISO roots were not yet modeled as live-runtime resources
- the UI still behaved too much like a repo/dev environment instead of a live product runtime

### What changed in Prompt 4

- runtime-aware config helpers were added for:
  - runtime mode
  - runtime root
  - scripts root
  - log root / log path
- the command runner now supports a default working directory tied to the runtime root
- clone and boot repair services now resolve operation scripts from the live runtime first and fall back to the repo layout only for development
- the live session startup exports runtime contract variables such as:
  - `CIGERTOOL_RUNTIME`
  - `CIGERTOOL_RUNTIME_ROOT`
  - `CIGERTOOL_SCRIPTS_ROOT`
  - `CIGERTOOL_LOG_ROOT`
- the live app launcher now starts the packaged app with a stable working directory
- the live staging pipeline now copies:
  - `invoke_smart_clone.ps1`
  - `invoke_raw_clone.ps1`
  - `invoke_boot_fix.ps1`
  into the staged application layout
- the transitional image assembly path also now stages those scripts into the runtime image
- the main UI now surfaces runtime information and uses the runtime root as the preferred file-browser root

### Current interpretation after Prompt 4

The project is still using a transitional Windows image assembly substrate, but the application core is no longer wired like a repo-only tool. It now has an explicit live-runtime contract for scripts, logs, tools, ISO roots, and startup.

This means Prompts 1 to 4 now form a coherent chain:

1. product direction defined
2. architecture reset and layer boundaries introduced
3. default boot path redirected into the live startup chain
4. core application services reconnected inside that runtime

## Prompt 5 Recommendation

Prompt 5 should now focus on the bundled tools and desktop utility layer.

Prompt 5 should:

- strengthen the tools launcher experience
- improve explorer / file access behavior
- define a cleaner portable-tools runtime contract
- integrate browser / diagnostics / utility workflows
- make the environment feel more like a usable maintenance desktop beyond the main app

## Prompt 5 Execution Result

Prompt 5 completed the first bundled-tools integration pass.

### What was still missing after Prompt 4

After Prompt 4, the runtime could boot and CigerTool could run meaningful disk workflows, but the tools layer still had three structural gaps:

- the `tools/` directory had no strong product-level layout contract
- the launcher could not cleanly distinguish app-internal tools from portable external apps
- portable applications had no metadata format for arguments, working directory, or clearer display names

### What changed in Prompt 5

- the tools model now supports:
  - launch arguments
  - working directory
  - internal application page targets
  - manifest path metadata
- a dedicated `ToolLauncherService` was introduced for external portable apps
- the tools catalog now supports `cigertool-tool.json` manifests
- the tools catalog now recognizes the new categorized layout:
  - `tools/browser/`
  - `tools/diagnostics/`
  - `tools/benchmark/`
  - `tools/storage/`
  - `tools/network/`
  - `tools/user/`
- the UI tools page now behaves as a real launcher:
  - launches internal product tools by navigating to the relevant page
  - launches external portable apps through the launcher service
  - exposes tool details and an "open folder" action
- a tools template manifest and category-level docs were added under `tools/`

### Current interpretation after Prompt 5

The runtime is still not the final polished desktop substrate, but it now has a real tools layer contract:

- internal tools
- preloaded portable tools
- user-added portable apps

This means the product now has an explicit application layer, runtime layer, and tools layer rather than one monolithic app shell.

## Prompt 6 Recommendation

Prompt 6 should now focus on ISO Library integration and polish.

Prompt 6 should:

- refine user-added ISO discovery
- improve category and support-state behavior
- tighten safe fallback handling for unsupported media
- polish the boot/menu and app-side ISO Library experience

## Prompt 6 Execution Result

Prompt 6 completed the first product-level ISO Library integration pass.

### What was still missing after Prompt 5

After Prompt 5, ISO discovery still worked mostly as a technical helper, not as a polished product layer:

- category detection was heavily path/name heuristic driven
- user-added ISO roots and legacy roots were not modeled explicitly
- the GRUB menu was effectively a flat list of entries
- unsupported ISO media were listed, but the overall fallback behavior was not clearly structured as a product contract

### What changed in Prompt 6

- the ISO model now records:
  - source root
  - library root
  - library section
  - relative path inside the library
- ISO discovery now understands:
  - `isos/windows`
  - `isos/linux`
  - `isos/tools`
  - legacy `iso-library/`
- legacy `iso-library/` subfolders are mapped into the new primary sections when possible
- duplicate ISO scan results are filtered out
- sidecar overrides remain supported and now produce clearer notes in the catalog
- the GRUB menu now renders a top-level `ISO Library` submenu
- ISO entries are grouped into product-facing sections:
  - Windows
  - Linux
  - tools / rescue
  - legacy
  - other
  - unsupported
- unsupported ISO entries now resolve to safe fallback entries instead of risky blind boot attempts
- EFI chainload entries can now use sidecar-provided custom EFI paths
- the app-side ISO management page now shows the library section and source/relative-path details
- the staged liveos manifest now records the expected ISO section layout

### Current interpretation after Prompt 6

The product now has a coherent ISO Library contract across both layers:

- app catalog layer
- boot menu layer

This means Prompts 1 to 6 now form a continuous architecture chain:

1. product vision defined
2. repository structure reset
3. default boot redirected into the live startup chain
4. core disk functionality reconnected to the live runtime
5. bundled tools layer formalized
6. ISO Library layer formalized with safe fallback behavior

## Prompt 7 Recommendation

Prompt 7 should now focus on polish, resilience, and demo-grade behavior.

Prompt 7 should:

- improve startup reliability and recovery behavior
- strengthen error reporting and user-facing diagnostics
- refine branding and UX consistency across the live environment
- harden log handling and failure fallback paths
- move the whole product toward production-grade demo readiness

## Prompt 7 Execution Result

Prompt 7 completed the planned product rewrite sequence by hardening the startup and runtime experience for near-production demo use.

### What was still missing after Prompt 6

After Prompt 6, the architecture was feature-complete for the planned scope, but resilience still depended too much on implicit behavior:

- startup failures were mostly warnings rather than structured runtime state
- recovery shell behavior existed, but did not clearly guide the user to logs and status
- the application could still fail early without a product-facing crash path
- the UI did not surface runtime startup health clearly enough

### What changed in Prompt 7

- a shared startup helper was introduced under:
  - `liveos/startup/CigerToolLive.Runtime.ps1`
- the startup chain now writes a structured status file:
  - `liveos/logs/liveos-status.json`
- shell, session, and application startup each record:
  - current stage
  - current state
  - human-readable message
  - runtime metadata
- the WinPE compatibility bootstrap now behaves more like a recovery console and explicitly points to:
  - runtime log file
  - startup status file
- the Python launcher now installs a global exception hook and logs unexpected failures before showing a user-visible dialog
- command execution errors now preserve more context, including working directory and step-level failure attribution
- the UI now surfaces startup state and degraded/failure warnings instead of hiding them in logs only
- the liveos build manifest now records the runtime log and startup status file contract

### Current interpretation after Prompt 7

The repository now satisfies the planned 1-7 staged migration path:

1. product direction established
2. architecture reset completed
3. desktop-first boot path established
4. core disk workflows integrated
5. tools layer formalized
6. ISO Library layer formalized
7. startup reliability, recovery, and UX hardened

At this point, remaining work is no longer "rewrite the architecture." It is field validation, release preparation, and iterative bug-fixing on top of the new architecture.
