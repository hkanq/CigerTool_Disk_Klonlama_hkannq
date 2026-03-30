# Legacy Build Scripts

This folder contains the transitional WinPE-centric build scripts that powered the old product direction.

These scripts are intentionally preserved for reference and controlled fallback usage, but they are no longer the default architecture path for the repository.

Legacy scripts currently kept here:

- `build_winpe_iso.ps1`
- `install_adk.ps1`

The new architecture should build toward:

- boot layer assets
- live OS session startup
- application packaging
- product assembly for `CigerTool Live`
