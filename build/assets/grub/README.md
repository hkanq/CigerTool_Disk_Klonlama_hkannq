Prebuilt GRUB EFI assets for the CigerTool boot layer.

Source:
- `grubx64.efi` extracted from Debian Bookworm package `grub-efi-amd64-bin_2.06-13+deb12u1_amd64.deb`

Notes:
- `bootx64.efi` is intentionally duplicated from the vendored `grubx64.efi` so removable-media UEFI fallback boot enters the CigerTool preboot menu.
- `grub.cfg` is a small compatibility shim that forwards to the dynamically generated `/EFI/CigerTool/grub.cfg`.
- The older WinPE-first boot path is now considered legacy; these assets remain reusable for the desktop-first live boot layer.
