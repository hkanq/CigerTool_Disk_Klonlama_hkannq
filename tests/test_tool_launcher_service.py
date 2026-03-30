from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from cigertool.models import ToolEntry
from cigertool.services.tool_launcher_service import ToolLaunchError, ToolLauncherService


class FakeSystemService:
    def __init__(self, runtime_root: Path) -> None:
        self._runtime_root = runtime_root

    def runtime_root(self) -> Path:
        return self._runtime_root


class ToolLauncherServiceTests(unittest.TestCase):
    def test_launches_portable_tool_with_working_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_root = Path(temp_dir)
            tool_dir = runtime_root / "tools" / "browser" / "chrome-portable"
            tool_dir.mkdir(parents=True, exist_ok=True)
            exe_path = tool_dir / "ChromePortable.exe"
            exe_path.write_text("", encoding="utf-8")

            tool = ToolEntry(
                name="Google Chrome Portable",
                category="Browser",
                description="Portable tarayici.",
                launch_path=str(exe_path),
                launch_args=["--incognito"],
                working_directory=str(tool_dir),
                layer="PRELOADED",
            )

            service = ToolLauncherService(FakeSystemService(runtime_root))
            with mock.patch("cigertool.services.tool_launcher_service.subprocess.Popen") as popen:
                service.launch(tool)

            popen.assert_called_once_with([str(exe_path), "--incognito"], cwd=str(tool_dir.resolve()))

    def test_raises_when_tool_has_no_launch_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = ToolLauncherService(FakeSystemService(Path(temp_dir)))
            with self.assertRaises(ToolLaunchError):
                service.launch(ToolEntry(name="Eksik", category="User Tool", description="Eksik arac."))


if __name__ == "__main__":
    unittest.main()
