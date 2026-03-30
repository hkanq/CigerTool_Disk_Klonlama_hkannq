# Roadmap

## Overview

This roadmap follows the staged prompt contract, with light adaptation allowed if the repo state demands it. The core rule is that each stage must leave the repo resumable and ready for the next prompt.

## Progress Snapshot

2026-03-30 itibariyla Prompt 1'den Prompt 7'ye kadar olan plan uygulanmistir.

Roadmap bundan sonra yeni bir rewrite sirasi degil, tamamlanan asamalarin referans kaydi olarak okunmalidir. Sonraki calisma alanlari saha smoke testleri, release hazirligi ve bugfix turlari olacaktir.

## Stage 1 - Prompt 1

### Goal

- align on final product direction
- inspect the current repository
- classify reusable vs replaceable components
- create resumability docs
- define a migration plan

### Deliverables

- `docs/PRODUCT_VISION.md`
- `docs/ROADMAP.md`
- `docs/ARCHITECTURE_REWRITE_PLAN.md`
- `docs/STATUS.md`

### Exit criteria

- current architecture is documented
- major risks are identified
- next stage is concrete and ready

## Stage 2 - Prompt 2

### Goal

- execute the architecture reset at the repository level
- define the new product structure for `CigerTool Live`
- stop treating WinPE shelling as the primary product model
- establish the new runtime / boot / app boundaries

### Deliverables

- initial repo structure for the new live-environment direction
- updated docs reflecting the new structure
- legacy WinPE assumptions marked as deprecated or isolated

### Exit criteria

- the repo has a clear product architecture target
- future implementation can proceed without boot/runtime ambiguity

## Stage 3 - Prompt 3

### Goal

- implement the first working desktop-first live environment path
- make boot stop falling into Windows Setup chooser behavior
- establish a reliable startup chain into the intended live environment
- auto-launch CigerTool inside that environment

### Deliverables

- first boot path for `CigerTool Live`
- auto-start mechanism
- early runtime logging / diagnostics

### Exit criteria

- default boot path lands in the intended environment
- the current reboot-loop / setup-chain failure mode is removed or bypassed

## Stage 4 - Prompt 4

### Goal

- wire the core disk features into the new environment
- preserve or adapt reusable service logic
- restore real value inside the new runtime

### Deliverables

- disk scan in the live environment
- clone / migration path reconnected
- boot repair integration reviewed for the new runtime

### Exit criteria

- the environment is no longer just a shell bootstrap; it runs meaningful product workflows

## Stage 5 - Prompt 5

### Goal

- add the bundled tools ecosystem
- define launcher and explorer strategy
- integrate diagnostics and portable tools cleanly

### Deliverables

- tools launcher strategy
- file access / explorer plan
- bundled tools integration

### Exit criteria

- the product feels like a real maintenance desktop, not just one app on a runtime

## Stage 6 - Prompt 6

### Goal

- rebuild ISO Library integration around the new product shape
- refine discovery, categorization, fallback behavior, and boot polish

### Deliverables

- product-level ISO Library behavior
- safe handling of unsupported or partial ISO profiles
- clearer categorized UX

### Exit criteria

- ISO Library is part of the product experience, not a sidecar experiment

## Stage 7 - Prompt 7

### Goal

- polish the experience
- improve resilience and startup behavior
- finalize logs, branding, error handling, and demo readiness

### Deliverables

- startup reliability improvements
- recovery and failure-path polish
- product-level branding pass

### Exit criteria

- production-grade demo quality
- clean staged story from boot to app usage

## Cross-Stage Rules

- avoid uncontrolled rewrites
- preserve reusable logic where valuable
- isolate or retire structurally wrong assumptions
- update `docs/STATUS.md` at the end of each stage
- keep the repo resumable after interruption
