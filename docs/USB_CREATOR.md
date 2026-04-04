# CigerTool USB Creator

## Purpose

`CigerTool App` can create a bootable `CigerTool OS` USB without using Rufus or a separate flasher tool.

Important boundary:

- the app writes a prebuilt image
- the image is discovered or selected through the release-source system
- the image is not built in this repository
- the Windows 10 PE base remains external and user-supplied

## Implemented Components

The USB Creator now includes:

- release-source resolver
- manifest parser
- local override loader
- manual image selection flow
- image downloader
- checksum verifier
- USB device discovery
- raw disk writer
- post-write validation
- WPF UI integration

## Release Modes

### Remote Manifest

- uses the configured default manifest URL
- reads `channel`, `version`, `image_name`, `image_url`, `sha256`, `notes`, and optional `size_bytes`
- caches the last successful resolution

### Local Override

- probes writable and deployment-friendly override locations
- can redirect to another manifest URL
- can point directly to a local image file
- can include override metadata such as `version`, `image_name`, `sha256`, and `notes`

### Manual File Selection

- user selects an already downloaded image for the current session
- sidecar `.sha256` files are used when available
- if no expected hash exists, the app still calculates SHA-256 and marks the state clearly

## Storage Model

USB Creator now uses the app's resolved writable `DataRoot`.

Key locations:

- downloads: `<DataRoot>\Downloads\<channel>\<version>\`
- cached manifest summary: `<DataRoot>\Cache\release-manifest-cache.json`
- override config: `<DataRoot>\Config\release-source.override.json`

This keeps the feature usable in:

- standard desktop deployments
- portable/app-local deployments
- future WinPE-style drop-in deployments

## Override Probe Order

The current implementation probes these locations in order:

1. `<DataRoot>\Config\release-source.override.json`
2. `<BaseDirectory>\Config\release-source.override.json`
3. `<BaseDirectory>\CigerTool\Config\release-source.override.json`
4. `%ProgramData%\CigerTool\release-source.override.json`

## Download And Preparation

For manifest-based sources, the app can:

- download the image into the app-managed downloads root
- keep temporary downloads isolated until checksum passes
- reuse a previously downloaded matching file when available

## Checksum Rules

The implemented checksum logic behaves as follows:

- manifest SHA-256 mismatch blocks writing
- override SHA-256 mismatch blocks writing
- manual image with sidecar mismatch blocks writing
- manual image without expected hash remains `calculated only`

This preserves offline/manual servicing while still surfacing integrity limits honestly.

## USB Device Detection

The app detects candidate USB targets by:

- querying Windows disk inventory through WMI
- filtering for USB or removable-disk candidates
- mapping each physical disk to mounted logical volumes
- blocking any detected system disk from write eligibility

Startup note:

- USB device scanning is not performed during initial app composition
- scanning only runs when the user refreshes the device list

## Write Flow

The implemented write path is:

1. resolve or select the image
2. download if necessary
3. verify checksum
4. require administrator context
5. require explicit destructive confirmation
6. block system-disk writes
7. block targets smaller than the image
8. dismount mounted volumes on the selected USB device
9. write the image to the physical drive
10. read back the written byte range and calculate SHA-256 again
11. compare the device hash to the source image hash

## Logging

USB Creator writes structured log events for:

- release refresh
- override usage
- remote manifest failure
- cached fallback usage
- device refresh
- image download start and finish
- checksum verification
- raw write start and finish
- post-write validation failure

## Current Guardrails

- no hardcoded final image URL dependency
- no silent use of unsafe targets
- no system disk writing
- no write when checksum validation mismatches
- no assumption that network is always available
- no WinPE build ownership

## Current Trade-Off

Trade-off:

- the implementation uses Windows-native raw disk access and WMI discovery because the app must stay standalone

Reason:

- the product must not depend on a separate flasher app

Impact:

- real-device validation is still required before production release
- this prompt improved the code paths and deployment model, but it could not run hardware validation in this environment
