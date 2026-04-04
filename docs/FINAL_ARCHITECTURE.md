# CigerTool Final Architecture

## Locked Foundation

The following product decisions are treated as fixed:

- C# is the application language
- No Python in the final shipped product
- Single-file output is preferred where practical
- The desktop app also owns USB creation
- CigerTool OS is based on a user-supplied Windows 10 PE base
- The OS experience must be visual, fast, and desktop-like
- Turkish defaults are required
- `\isos` is a required part of the USB/OS concept

## Repository Cleanup Baseline

The repository has now been reset to remove conflicting Python-era metadata and to expose a single canonical structure for the final product family.

Cleanup rules applied:

- remove obsolete language and packaging paths that conflict with the locked C# direction
- do not preserve dead experiments without a clear reuse case
- keep WinPE integration assets separate from application logic
- keep USB creation logic separate from OS integration logic
- avoid duplicate implementation paths for the same responsibility

## Technology Direction

### UI Stack

- `.NET 8`
- `WPF`
- MVVM-style presentation structure with explicit application services

Reasoning:

- WPF is mature, stable on Windows 10/11, and practical for a polished desktop UI
- It avoids the packaging and dependency complexity that newer Windows UI stacks can introduce in controlled service environments such as WinPE
- Self-contained single-file publishing is well understood in this stack

### Architectural Layers

The codebase should be split into clear layers instead of placing all logic inside the UI project.

#### Presentation Layer

Owns:

- application shell
- navigation
- views and view models
- visual styling
- user interaction state

#### Application Layer

Owns:

- use cases
- workflow orchestration
- validation pipelines
- progress reporting contracts
- runtime policy decisions

#### Domain Layer

Owns:

- disk, partition, clone-job, release, and tool models
- business rules
- eligibility checks
- risk classification

#### Infrastructure Layer

Owns:

- Windows disk access
- filesystem inspection
- process execution
- manifest download
- checksum verification
- logging sinks
- environment detection

## Application Architecture

### Main UI Modules

#### Dashboard

Shows runtime state, recent logs, attached disks, important warnings, and quick actions.

#### Cloning

Hosts raw clone and smart clone workflows with guided source/target selection, safety checks, execution, and verification.

#### Disks

Shows disk inventory, partition layout, filesystem details, capacity, and diagnostic state.

#### Tools

Lists bundled tools with descriptions, launch rules, and environment availability.

#### USB Creator

Creates a CigerTool OS USB from a discovered release manifest, a local override source, or a manually selected image.

#### Logs

Shows operation history, live progress details, and exportable log bundles.

#### Settings

Stores channel choice, UI preferences, logging preferences, release-source defaults, and safety-related defaults.

### Core Runtime Services

The first implementation wave should organize services around stable responsibilities.

- `EnvironmentProfileService`
  Detects whether the app runs on normal Windows or inside WinPE and exposes capability flags.
- `DiskInventoryService`
  Enumerates physical disks, partitions, filesystems, and mount relationships.
- `ClonePlanner`
  Builds a validated plan before any data movement begins.
- `RawCloneService`
  Executes sector-based disk copy operations.
- `SmartCloneService`
  Executes filesystem-aware migration when the source layout is supported.
- `CloneVerificationService`
  Performs post-run checks and captures evidence in logs.
- `UsbCreationService`
  Handles device selection, release resolution, image validation, and USB writing.
- `ReleaseSourceResolver`
  Applies remote manifest, local override, and manual file selection rules.
- `BundledToolCatalogService`
  Discovers and launches approved bundled tools.
- `OperationLogService`
  Writes structured logs and prepares support bundles.
- `SettingsService`
  Loads and persists application settings.

### Environment Profiles

The app should use one product codebase with environment-aware behavior.

#### Desktop Profile

- Full settings persistence
- USB creation enabled
- Live-system cloning allowed as best-effort
- Recommend CigerTool OS for cloning the currently running system disk

#### WinPE Profile

- Auto-start optimized
- Temporary-path aware logging
- No first-run prompts
- Tool availability filtered to WinPE-safe tools
- Cloning workflow biased toward offline servicing

## Cloning Architecture

### Raw Clone

Use case:

- full sector-based copy
- source and target are treated as block devices
- target must satisfy size and layout constraints

Execution shape:

1. Inspect source and target
2. Validate administrator privileges and exclusive-access requirements
3. Confirm target overwrite intent
4. Stream sectors in controlled blocks with progress and cancellation support
5. Record validation and result logs
6. Optionally run lightweight verification

### Smart Clone

Use case:

- move used data rather than copying every sector
- allow source-to-smaller-target scenarios when the actual layout fits

Execution shape:

1. Read disk and partition layout
2. Check supported filesystem and partition rules
3. Measure used space and required system partitions
4. Build a target-fit plan
5. Warn or block if fit, bootability, or metadata recreation is unsafe
6. Create target layout
7. Copy data and required boot/system structures
8. Verify the result and capture logs

### Smart Clone Generation 1 Boundary

To stay maintainable, the first smart clone implementation should be Windows-centric rather than pretending to support every filesystem from day one.

Generation 1 should target:

- GPT and MBR disks commonly used by Windows systems
- NTFS system/data partitions first
- predictable recovery/system partition recreation rules

Unsupported or high-risk layouts should be rejected early or redirected to raw clone.

## CigerTool OS Architecture

### Ownership Boundary

This repository does not build Windows 10 PE. It defines how the CigerTool payload integrates into a WinPE base prepared by the user.

### What The Project Supplies

- the CigerTool application bundle
- startup integration assets
- configuration files
- tool packaging layout
- documentation for expected WinPE shell behavior

### What The User-Supplied WinPE Base Must Provide

- Windows 10 PE base image
- Turkish defaults
- graphical shell capability suitable for a desktop-style experience
- a supported startup hook such as `winpeshl.ini` or equivalent shell launch path
- access to the USB volume that stores the CigerTool payload and `\isos`

### Recommended USB / OS Layout

```text
\
|-- CigerTool\
|   |-- App\
|   |   `-- CigerTool.exe
|   |-- Config\
|   |   |-- appsettings.json
|   |   `-- release-source.override.json
|   |-- Logs\
|   |-- Tools\
|   `-- Runtime\
`-- isos\
    |-- windows\
    |-- linux\
    `-- tools\
```

Notes:

- `CigerTool.exe` is the primary UI entry point
- `release-source.override.json` is optional and useful in service or offline deployments
- `Logs` may be stored on a writable persistent location when available
- `\isos` is mandatory even before the future ISO workflow is fully implemented

### Startup Integration Direction

Recommended startup behavior:

1. The supplied WinPE base initializes its shell
2. A lightweight launcher or shell startup entry launches `CigerTool\App\CigerTool.exe`
3. CigerTool detects WinPE mode and opens directly to the service-oriented shell experience

Important rule:

- keep shell bootstrap minimal
- do not build product logic into `startnet.cmd`
- keep business logic in the app, not in scattered boot scripts

## Repository Direction

The cleaned repository baseline uses the following canonical structure.

```text
app/
  CigerTool.App/
core/
  CigerTool.Application/
  CigerTool.Domain/
  CigerTool.Infrastructure/
usb/
  CigerTool.Usb/
os/
  integration/
  layout/
tools/
  catalog/
  packages/
build/
  packaging/
  scripts/
docs/
tests/
  CigerTool.Application.Tests/
  CigerTool.Domain.Tests/
  CigerTool.Infrastructure.Tests/
```

### Directory Roles

#### `app/`

WPF shell, views, view models, styling, and application startup.

Canonical project root:

- `app/CigerTool.App`

Expected internal areas:

- `Assets`
- `Styles`
- `Views`
- `ViewModels`

#### `core/`

Reusable product logic.

Canonical project roots:

- `core/CigerTool.Domain`
- `core/CigerTool.Application`
- `core/CigerTool.Infrastructure`

#### `usb/`

USB creation and release-source logic.

Canonical project root:

- `usb/CigerTool.Usb`

#### `os/`

WinPE integration definitions, startup assets, and payload layout contracts. Not a WinPE build system.

Canonical areas:

- `os/integration`
- `os/layout`

#### `tools/`

Bundled tool manifests, packaging metadata, and launcher definitions. Third-party binaries should be managed intentionally, not scattered through the repo.

Canonical areas:

- `tools/catalog`
- `tools/packages`

#### `build/`

Packaging, publishing, signing, and CI helper scripts for the app and integration bundles.

Canonical areas:

- `build/scripts`
- `build/packaging`

#### `docs/`

Architecture, product, release, and operational documentation.

#### `tests/`

Unit, integration, and later hardware-sensitive test harnesses.

Canonical areas:

- `tests/CigerTool.Domain.Tests`
- `tests/CigerTool.Application.Tests`
- `tests/CigerTool.Infrastructure.Tests`

## Build And Packaging Direction

- publish the app as self-contained single-file where practical
- keep large external tools and optional assets outside the single executable when that is cleaner
- package WinPE integration assets separately from the user-supplied WinPE base
- never tie releases to a single hardcoded image URL

## Cleanup Outcome

The repository now has one intended path for each major responsibility:

- UI shell lives under `app`
- reusable business logic lives under `core`
- USB writing and release resolution live under `usb`
- WinPE startup and payload layout live under `os`
- bundled tool metadata lives under `tools`
- packaging helpers live under `build`

This avoids legacy ambiguity before the .NET solution is introduced.
