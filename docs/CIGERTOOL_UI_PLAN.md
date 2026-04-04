# CigerTool UI Plan

## UI Direction

The application foundation uses a left-sidebar navigation shell with a bright main workspace.

Visual goals:

- service-product feel rather than developer-tool feel
- clean hierarchy on laptop screens
- scalable module growth without redesigning navigation
- readable at common Windows 10/11 resolutions

## Layout Structure

### Sidebar

Contains:

- product branding
- primary navigation
- active environment profile summary

Why sidebar instead of tab strip:

- scales more cleanly as modules grow
- keeps module discovery stable inside both desktop and future WinPE contexts
- supports descriptive subtitles for non-expert users

### Content Header

Contains:

- current module title
- current module subtitle
- build-readiness badge

### Content Surface

Each module renders inside a shared content surface with rounded card sections.

## Module Screens

### Dashboard

- top-level product summary
- key readiness cards
- highlighted operational notes
- recent event feed from the logging system

### Cloning

- raw and smart clone readiness cards
- source/target selection
- suitability analysis result card
- safety guidance and future execution notes

### Disks

- runtime system profile
- ready volume inventory
- diagnostics-oriented notes for later physical disk integration

### Tools

- bundled tool cards
- availability-aware launch action
- explicit launch policy messaging

### USB Creator

- release-source overview
- manifest/local/manual source refresh controls
- image download and checksum actions
- USB target selection and destructive write confirmation
- post-write oriented status messaging

### Logs

- structured log list
- manual refresh action

### Settings

- language
- channel
- manifest URL
- Turkish defaults
- single-file publishing preference

## Styling Direction

The first UI foundation uses:

- slate-blue navigation
- soft white content panels
- teal accent

This avoids generic dark-only tooling aesthetics while still feeling structured and professional.

## Future UI Work

Prompt 4 and later should build on this shell rather than replace it.

Expected future UI improvements:

- richer physical disk tables
- guided multi-step clone execution flows
- USB target selection and progress UX
- searchable log filters
- editable settings with validation

## Boundary

This UI plan is a shell plan, not a final visual polish pass. The goal of this prompt is stable structure, not final pixel perfection.
