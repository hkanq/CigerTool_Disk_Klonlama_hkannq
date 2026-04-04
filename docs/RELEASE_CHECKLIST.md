# Release Checklist

## Scope

This checklist covers release-readiness for `CigerTool App`.

It does not cover building the WinPE base.

## Configuration

- set a real default manifest URL in `appsettings.json` or provide an operator override file
- verify `defaultChannel` is correct for the release channel
- verify `tools.catalog.json` matches the bundled tool set
- confirm Turkish-first defaults remain enabled

## Build And Publish

- publish `standard-x64-single-file`
- publish `winpe-x64-single-file`
- confirm `appsettings.json` is copied to both publish outputs
- confirm `tools.catalog.json` is copied to both publish outputs
- confirm optional `Config\` and `Tools\` folders can sit beside the executable
- verify `artifacts/app/CigerTool.exe` starts on a clean Windows 10/11 machine
- verify `artifacts/winpe/CigerTool.WinPE.exe` starts with WinPE-safe profile behavior

## Startup And Runtime

- verify startup self-check completes
- verify logs are written to the expected resolved path
- verify portable mode works with `portable.mode`
- verify standard mode uses `%LocalAppData%\CigerTool`
- verify temporary fallback works when the preferred location is not writable

## UI And Navigation

- verify shell renders correctly at common laptop resolutions
- verify high DPI readability at 125% and 150%
- verify each module opens without blocking the shell
- verify missing optional files do not crash startup

## Disk And Clone

- verify disk inventory appears on target machines
- verify raw clone suitability rules block undersized targets
- verify smart clone suitability states show clear warnings
- verify desktop mode blocks active system disk as the target

## Tools

- verify missing bundled tools only show unavailable status
- verify bundled relative tool paths resolve correctly
- verify tool launches are written to logs

## USB Creator

- verify remote manifest flow
- verify local override manifest flow
- verify local override image flow
- verify manual image selection flow
- verify checksum verified, calculated-only, and mismatch states
- verify USB target safety blocking
- verify destructive confirmation messaging
- verify post-write validation on real hardware

## Logging And Error Handling

- verify text log output
- verify JSONL structured log output
- verify user-friendly crash reporting
- verify common network and file errors are surfaced cleanly

## WinPE Handoff

- verify app-local deployment layout matches `docs/CIGERTOOL_WINPE_NOTES.md`
- verify startup/autolaunch instructions are packaged for the external WinPE integrator
- verify `\isos` guidance is included in delivery notes

## Current Blockers Outside This Prompt

- this environment has no `.NET SDK`, so build and publish could not be executed here
- real USB hardware validation still needs a test machine
- final release packaging still needs a real manifest endpoint or override package
