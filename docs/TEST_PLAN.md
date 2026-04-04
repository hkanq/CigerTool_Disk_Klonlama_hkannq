# Test Plan

## Goal

This plan defines the validation needed before calling `CigerTool App` release-ready.

## Environment Note

This repository currently cannot run `dotnet build` or `dotnet test` in this environment because the `.NET SDK` is not installed.

The plan below is therefore the intended test matrix, not a completed execution report.

## Automated Test Focus

Priority automated coverage should include:

- startup diagnostics result construction
- runtime path resolution for standard, portable, and WinPE-like profiles
- settings override merge behavior
- release-source precedence and cache fallback behavior
- clone suitability calculations for raw and smart clone modes
- tool catalog path resolution and launch eligibility

## Desktop Manual Smoke Tests

Run on Windows 10 and Windows 11:

- app starts and shell opens cleanly
- each module can be opened from navigation
- dashboard self-check and recent events populate
- settings page shows resolved storage paths
- logs page shows both text and JSONL paths

## Responsiveness Tests

- cold start on a normal laptop
- confirm startup does not block on USB enumeration
- confirm navigation does not rebuild already-open pages unnecessarily
- confirm large log history does not freeze the shell

## Error Handling Tests

- missing `appsettings.json`
- missing `tools.catalog.json`
- missing bundled tool executable
- invalid release override file
- offline network during manifest refresh
- checksum mismatch during image verification
- non-admin raw write attempt

## USB Creator Manual Tests

- remote manifest refresh
- local override manifest refresh
- local override image path
- manual image selection
- image download success path
- image checksum mismatch path
- removable USB detection
- system disk block
- target-too-small block
- write and post-write validation on real removable media

## Tool Launcher Tests

- built-in Windows tool launch
- bundled tool launch when executable exists
- missing tool availability status
- WinPE-blocked tool visibility and messaging

## Clone Planning Tests

- raw clone with equal or larger target
- raw clone with smaller target
- smart clone with sufficient smaller target
- smart clone with insufficient target
- active desktop system disk used as target
- WinPE profile suitability messaging

## Display And UX Tests

- 1366x768
- 1920x1080
- 125% DPI
- 150% DPI
- keyboard navigation basics

## WinPE-Adjacent Validation

Without building WinPE in this repo, validate the app bundle in a PE-like drop-in context:

- run from an app-local folder with `portable.mode`
- confirm logs/cache/downloads use `.\Data`
- confirm missing optional tools do not crash the app
- confirm release override under `.\Data\Config\` is detected

## Exit Criteria

The app can be considered release-candidate quality when:

- publish output is generated successfully on an SDK-enabled machine
- smoke tests pass on Windows 10 and Windows 11
- USB Creator completes at least one real-device write and validation pass
- no critical startup or data-loss bugs remain open
