from __future__ import annotations

import unittest
from pathlib import Path


class PrebootAssetsTests(unittest.TestCase):
    def test_grub_menu_template_exists(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        grub_cfg = project_root / "boot" / "assets" / "preboot" / "grub.cfg"
        self.assertTrue(grub_cfg.exists())
        content = grub_cfg.read_text(encoding="utf-8")
        self.assertIn("CigerTool Workspace", content)
        self.assertIn("/EFI/Microsoft/Boot/bootmgfw.efi", content)
        self.assertIn("/EFI/Microsoft/Boot/BCD", content)
        self.assertIn("/isos/windows", content)
        self.assertIn("Boot Diagnostics", content)

    def test_grub_generator_exists(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        generator = project_root / "build" / "internal" / "render_boot_menu.py"
        self.assertTrue(generator.exists())

    def test_prebuilt_grub_assets_exist(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        asset_root = project_root / "boot" / "assets" / "grub"
        self.assertTrue((asset_root / "bootx64.efi").exists())
        self.assertTrue((asset_root / "grubx64.efi").exists())
        self.assertTrue((asset_root / "grub.cfg").exists())


if __name__ == "__main__":
    unittest.main()
