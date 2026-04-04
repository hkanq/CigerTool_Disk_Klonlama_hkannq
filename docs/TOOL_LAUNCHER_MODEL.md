# CigerTool Tool Launcher Model

## Purpose

This document defines how CigerTool discovers, shows, and launches bundled or system tools.

The design goal is to make tool integration configurable, safe, and easy to extend.

## Catalog Strategy

Tool definitions are loaded from a JSON catalog file.

Current default path:

- `tools/catalog/default-tools.json`

The app copies this catalog into its output as:

- `tools.catalog.json`

This keeps tool definitions outside hardcoded source logic and makes later updates easier.

## Tool Definition Fields

The current model supports:

- `id`
- `name`
- `category`
- `description`
- `executablePath`
- `arguments`
- `availableInWinPe`
- `isBundled`

## Path Resolution Rules

The launcher currently resolves tools in this order:

1. Absolute paths are used directly.
2. Relative paths are treated as app-relative bundled paths.
3. Bare executable names are searched through `PATH`, `Windows`, and `System32`.

This lets the same catalog describe:

- bundled portable tools
- built-in Windows tools
- support utilities already present on the machine

## Availability Model

Each tool is surfaced to the UI with resolved runtime status:

- resolved executable path
- whether the file exists
- whether the current profile may launch it
- a human-readable availability message

Missing tools do not crash the app.

Instead, the UI shows state such as:

- missing executable
- blocked in WinPE profile
- bundled path detected
- available on this system

## Launch Behavior

When the user launches a tool:

1. CigerTool checks `Exists` and `CanLaunch`.
2. If unavailable, the app returns a safe user-visible message and logs the attempt.
3. If available, the app starts the process through Windows shell execution.
4. Success or failure is written to the log system.

## Logging Events

The current launcher writes structured events for:

- `tools.catalog.error`
- `tools.launch.unavailable`
- `tools.launch.success`
- `tools.launch.failure`

This makes tool operations visible both in the UI and in file-backed logs.

## Bundled Tool Packaging Direction

The catalog already supports later bundling of portable tools under the app folder.

Recommended direction:

- keep tool payloads under a predictable app-relative subfolder
- describe them in JSON instead of branching logic in code
- allow WinPE suitability to be declared per tool

## Current Boundary

This prompt does not yet implement:

- signature verification for bundled tools
- download/update logic for tool packages
- tool-specific health checks beyond executable existence
- license management workflow

## Recorded Trade-Off

Trade-off:

- the current launcher validates executable presence and profile eligibility, but not deeper package integrity

Reason:

- the immediate product need is a stable and extensible launch framework without introducing unnecessary runtime dependencies

Impact:

- later packaging prompts should add stronger validation for shipped third-party tools
