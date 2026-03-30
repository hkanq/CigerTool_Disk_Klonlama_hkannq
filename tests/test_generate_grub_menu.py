from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class GenerateGrubMenuTests(unittest.TestCase):
    def test_generated_menu_uses_workspace_entry_and_dynamic_iso_scanning(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        script = project_root / "build" / "internal" / "render_boot_menu.py"

        with tempfile.TemporaryDirectory() as tmp:
            media_root = Path(tmp) / "media"
            output = media_root / "EFI" / "CigerTool" / "grub.cfg"
            media_root.mkdir(parents=True)

            subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--media-root",
                    str(media_root),
                    "--output",
                    str(output),
                    "--workspace-loader-path",
                    "/EFI/Microsoft/Boot/bootmgfw.efi",
                    "--workspace-bcd-path",
                    "/EFI/Microsoft/Boot/BCD",
                    "--workspace-vhd-path",
                    "/workspace/CigerToolWorkspace.vhdx",
                    "--wimboot-path",
                    "/EFI/CigerTool/wimboot",
                ],
                check=True,
                cwd=project_root,
            )

            content = output.read_text(encoding="utf-8")
            self.assertIn('menuentry "CigerTool Workspace"', content)
            self.assertIn('submenu "ISO Library"', content)
            self.assertIn('menuentry "ISO Library kullanimi"', content)
            self.assertIn('/isos/windows/*.iso', content)
            self.assertIn('/isos/linux/*.iso', content)
            self.assertIn('/isos/tools/*.iso', content)
            self.assertIn("/workspace/CigerToolWorkspace.vhdx", content)
            self.assertIn("/EFI/Microsoft/Boot/BCD", content)
            self.assertIn("chainloader /EFI/Microsoft/Boot/bootmgfw.efi", content)
            self.assertIn("search --no-floppy --set=cg_root --file /CigerTool.workspace.json", content)
            self.assertIn('submenu "Boot Diagnostics"', content)
            self.assertIn("Setup veya OOBE kullanmaz", content)
            self.assertIn('regexp --set=1 cg_iso_title', content)
            self.assertIn("uygun kernel bulunamadi", content)
            self.assertIn("uygun boot dosyalari bulunamadi", content)
            self.assertNotIn('menuentry "CigerTool Live"', content)


if __name__ == "__main__":
    unittest.main()
