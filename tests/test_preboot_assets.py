from __future__ import annotations

import unittest
from pathlib import Path


class PrebootAssetsTests(unittest.TestCase):
    def test_grub_menu_template_exists(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        grub_cfg = project_root / "build" / "assets" / "preboot" / "grub.cfg"
        self.assertTrue(grub_cfg.exists())
        content = grub_cfg.read_text(encoding="utf-8")
        self.assertIn("dynamic menu placeholder", content)
        self.assertIn("/isos/windows", content)

    def test_grub_generator_exists(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        generator = project_root / "build" / "scripts" / "generate_grub_menu.py"
        self.assertTrue(generator.exists())

    def test_prebuilt_grub_assets_exist(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        asset_root = project_root / "build" / "assets" / "grub"
        self.assertTrue((asset_root / "bootx64.efi").exists())
        self.assertTrue((asset_root / "grubx64.efi").exists())
        self.assertTrue((asset_root / "grub.cfg").exists())


if __name__ == "__main__":
    unittest.main()
