# CigerTool Product Vision

## Product Family

CigerTool is a two-part product family built around disk service, migration, and recovery workflows.

### 1. CigerTool App

A Windows desktop application that runs on normal Windows 10/11 installations and later also inside CigerTool OS.

Required product areas:

- Dashboard
- Cloning
- Disks
- Tools
- USB Creator
- Logs
- Settings

### 2. CigerTool OS

A Windows 10 PE based service environment that boots from USB, auto-launches CigerTool, and provides a lightweight desktop-style workspace for maintenance tasks.

Important boundary:

- The WinPE base is supplied externally by the user.
- This repository defines integration, packaging, startup behavior, and layout.
- This repository does not build the WinPE base itself.

## Product Intent

CigerTool should feel like a polished end-user service product rather than a collection of scripts. The user experience must stay visual, approachable, and safe even when the underlying work is technical and high-risk.

## Primary User Outcomes

- Clone a disk safely with guided validation
- Inspect disks, partitions, and health information
- Launch bundled service tools from one place
- Create a CigerTool OS USB without separate flasher software
- Boot into a controlled WinPE environment for safer offline cloning

## Experience Principles

### Visual First

- The app must be fully graphical
- The OS experience must not feel terminal-first
- Non-expert users should be able to complete common flows

### Safe By Default

- High-risk actions must be validated before execution
- Live-system cloning must be treated as best-effort
- The app should recommend CigerTool OS for cloning the current system disk

### One Product, Two Contexts

- The same product identity should exist on normal Windows and in WinPE
- Runtime behavior may adapt to the environment, but the user should not learn two separate products

### Portable Distribution

- Single-file app publishing is preferred where practical
- Release discovery must use a manifest-based system rather than hardcoded image URLs

### Turkish Defaults

- Turkish should be the default locale and default UX language for the first product generation
- First-run questions should be avoided, especially in CigerTool OS

## Generation 1 Non-Goals

- Building or replacing the Windows 10 PE base
- Acting as a general-purpose Windows installer
- Replacing a future dedicated multiboot manager with a rushed first implementation
- Shipping a terminal-oriented recovery toolkit

## Success Criteria For The Architecture Phase

- The product family is clearly defined
- The repository direction is aligned to the final C# product
- The WinPE ownership boundary is explicit
- The release-source model is defined without hardcoded image URLs
- Later prompts can implement features without re-opening the core architecture
