from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class GenerateGrubMenuTests(unittest.TestCase):
    def test_generated_menu_contains_iso_library_sections_and_failure_reasons(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        script = project_root / "build" / "scripts" / "generate_grub_menu.py"

        with tempfile.TemporaryDirectory() as tmp:
            media_root = Path(tmp) / "media"
            (media_root / "isos" / "windows").mkdir(parents=True)
            (media_root / "isos" / "linux").mkdir(parents=True)
            (media_root / "isos" / "tools").mkdir(parents=True)
            (media_root / "iso-library").mkdir(parents=True)
            (media_root / "isos" / "windows" / "Windows11.iso").write_bytes(b"x")
            (media_root / "isos" / "linux" / "mystery.iso").write_bytes(b"x")
            (media_root / "isos" / "tools" / "rescue.iso").write_bytes(b"x")
            (media_root / "isos" / "tools" / "rescue.cigertool.json").write_text(
                '{"efi_boot_path":"/EFI/custom/bootx64.efi"}',
                encoding="utf-8",
            )
            (media_root / "iso-library" / "random.iso").write_bytes(b"x")
            output = media_root / "EFI" / "CigerTool" / "grub.cfg"

            subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--media-root",
                    str(media_root),
                    "--output",
                    str(output),
                    "--wimboot-path",
                    "/EFI/CigerTool/wimboot",
                ],
                check=True,
                cwd=project_root,
            )

            content = output.read_text(encoding="utf-8")
            self.assertIn('menuentry "CigerTool Live"', content)
            self.assertIn('submenu "ISO Library"', content)
            self.assertIn('submenu "Windows ISO\'lari"', content)
            self.assertIn('submenu "Arac ve Kurtarma ISO\'lari"', content)
            self.assertIn('submenu "Desteklenmeyen ISO\'lar"', content)
            self.assertIn("newc:boot.wim:/sources/boot.wim", content)
            self.assertIn("(loop)/EFI/custom/bootx64.efi", content)
            self.assertIn("missing boot files", content)
            self.assertIn("unsupported kernel", content)
            self.assertIn("incompatible ISO type", content)


if __name__ == "__main__":
    unittest.main()
