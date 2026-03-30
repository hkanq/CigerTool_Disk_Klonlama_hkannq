Prebuilt GRUB EFI assets for the final CigerTool boot layer.

Source:
- `grubx64.efi` extracted from Debian Bookworm package `grub-efi-amd64-bin_2.06-13+deb12u1_amd64.deb`

Notes:
- `bootx64.efi` is duplicated from `grubx64.efi` so removable-media UEFI fallback enters the CigerTool boot menu.
- `grub.cfg` is only a compatibility shim that forwards to the generated `/EFI/CigerTool/grub.cfg`.
- These assets are part of the final boot architecture, not a legacy WinPE path.
