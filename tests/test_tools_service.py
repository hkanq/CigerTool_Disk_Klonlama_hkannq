from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from cigertool.services.tools_service import ToolsCatalogService


class FakeSystemService:
    def __init__(self, roots: list[Path], runtime_root: Path | None = None) -> None:
        self._roots = roots
        self._runtime_root = runtime_root or (roots[0] if roots else Path.cwd())

    def tool_roots(self) -> list[Path]:
        return self._roots

    def runtime_root(self) -> Path:
        return self._runtime_root


class ToolsCatalogServiceTests(unittest.TestCase):
    def test_manifest_defined_portable_tool_is_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            tool_dir = root / "diagnostics" / "hwinfo"
            tool_dir.mkdir(parents=True, exist_ok=True)
            exe_path = tool_dir / "HWiNFO64.exe"
            exe_path.write_text("", encoding="utf-8")
            manifest_path = tool_dir / "cigertool-tool.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "name": "HWiNFO Portable",
                        "category": "Diagnostics",
                        "description": "Donanim ozeti.",
                        "entry": "HWiNFO64.exe",
                        "arguments": ["/portable"],
                        "working_directory": ".",
                    }
                ),
                encoding="utf-8",
            )

            service = ToolsCatalogService(FakeSystemService([root]))
            tools = service.list_tools()

            hwinfo = next(item for item in tools if item.name == "HWiNFO Portable")
            self.assertEqual(hwinfo.launch_path, str(exe_path.resolve()))
            self.assertEqual(hwinfo.launch_args, ["/portable"])
            self.assertEqual(hwinfo.manifest_path, str(manifest_path))
            self.assertTrue(hwinfo.is_launchable)

    def test_preloaded_tools_resolve_from_categorized_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            chrome_dir = root / "browser" / "chrome-portable"
            chrome_dir.mkdir(parents=True, exist_ok=True)
            chrome_exe = chrome_dir / "ChromePortable.exe"
            chrome_exe.write_text("", encoding="utf-8")

            service = ToolsCatalogService(FakeSystemService([root]))
            tools = service.list_tools()

            chrome = next(item for item in tools if item.name == "Google Chrome Portable")
            self.assertEqual(chrome.launch_path, str(chrome_exe.resolve()))
            self.assertEqual(chrome.category, "Browser")
            self.assertEqual(chrome.layer, "PRELOADED")

    def test_core_tools_are_launchable_via_internal_pages(self) -> None:
        service = ToolsCatalogService(FakeSystemService([]))
        tools = service.list_tools()

        clone_wizard = next(item for item in tools if item.name == "Clone Wizard")
        iso_library = next(item for item in tools if item.name == "ISO Library")
        log_viewer = next(item for item in tools if item.name == "Log Viewer")

        self.assertEqual(clone_wizard.internal_page, "clone")
        self.assertEqual(iso_library.internal_page, "isos")
        self.assertEqual(log_viewer.internal_page, "logs")
        self.assertTrue(clone_wizard.is_launchable)


if __name__ == "__main__":
    unittest.main()
