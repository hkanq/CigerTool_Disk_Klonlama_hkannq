# CigerTool Release Source Model

## Goal

The USB Creator must discover or accept `CigerTool OS` images without depending on one hardcoded image URL.

The release model is manifest-based and supports three locked modes:

- remote manifest
- local override
- manual file selection

## Resolution Strategy

### Mode 1. Remote Manifest

Primary path.

The app loads a remote manifest JSON and learns:

- `channel`
- `version`
- `image_name`
- `image_url`
- `sha256`
- `notes`

Optional but supported:

- `size_bytes`

Recommended for later:

- `schema_version`
- `published_at`
- `min_app_version`

### Mode 2. Local Override

Administrative or service override path.

The override file may:

- replace the manifest URL
- pin a specific channel
- point directly to a local image file
- include `version`, `image_name`, `sha256`, and `notes`

Implemented probe order:

1. `<DataRoot>\Config\release-source.override.json`
2. `<BaseDirectory>\Config\release-source.override.json`
3. `<BaseDirectory>\CigerTool\Config\release-source.override.json`
4. `%ProgramData%\CigerTool\release-source.override.json`

### Mode 3. Manual File Selection

The user can bypass discovery and select an image directly for the current session.

This is required for:

- offline servicing
- local validation
- operator-supplied images

## Precedence Rules

Implemented precedence is:

1. manual file selection for the current session
2. local override if present and enabled
3. remote manifest using the configured default manifest URL
4. cached last-known-good manifest summary when remote refresh fails

This preserves operator control while still giving the shipped app a clean default path.

## Default Configuration Model

The shipped app may include:

- a default manifest URL
- a default channel such as `stable`

The shipped app must not include:

- one hardcoded final image download URL as the only source of truth

The manifest remains the authority for actual image locations.

## Manifest Schema

Example:

```json
{
  "schema_version": 1,
  "channel": "stable",
  "version": "1.0.0",
  "image_name": "CigerTool-OS-1.0.0.img",
  "image_url": "https://downloads.example.com/cigertool/os/1.0.0/CigerTool-OS-1.0.0.img",
  "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
  "notes": "Initial public release",
  "size_bytes": 3221225472
}
```

## Override Schema

Example override manifest redirect:

```json
{
  "enabled": true,
  "channel": "stable",
  "manifest_url": "https://example.invalid/cigertool/releases/stable.json"
}
```

Example override local image:

```json
{
  "enabled": true,
  "channel": "stable",
  "version": "1.0.0-local",
  "image_name": "CigerTool-OS-local.img",
  "image_file": "D:\\Images\\CigerTool-OS-local.img",
  "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
  "notes": "Service bench local image"
}
```

## Cache Behavior

The app writes the last successful manifest resolution to:

- `<DataRoot>\Cache\release-manifest-cache.json`

`DataRoot` depends on deployment mode:

- desktop usually resolves to `%LocalAppData%\CigerTool`
- portable or WinPE-oriented runs prefer `.\Data`
- temp fallback uses `%TEMP%\CigerTool`

## Validation Rules

Before USB writing begins, the app must:

- validate required manifest fields
- resolve a real image file path
- verify SHA-256 when an expected hash exists
- show version and notes to the user
- block writing when checksum validation fails

Implemented checksum behavior:

- remote manifest flow compares against manifest `sha256`
- local override image compares against override `sha256` when provided
- manual flow also checks for sidecar checksum files such as `image.img.sha256` or `image.sha256`
- when no expected hash exists, the app still computes SHA-256 and marks the state as `calculated only`

## Security And Reliability Rules

- prefer HTTPS for remote manifests and image URLs
- cache the last known good release summary
- never trust filename alone; trust checksum verification
- surface manifest and checksum errors clearly in the UI
- keep operator overrides explicit and visible in logs

## Implemented Components

These are concrete services in the repository now:

- `ReleaseSourceResolver`
- manifest parsing models
- local override loader
- release cache handling
- image checksum verification logic

## Current Trade-Off

Trade-off:

- the shipped app can still operate with no default manifest URL configured

Reason:

- the product must support offline servicing and custom operator environments without forcing a single hosted source

Impact:

- release packaging must provide either a real default manifest URL or an operator override file before public distribution
