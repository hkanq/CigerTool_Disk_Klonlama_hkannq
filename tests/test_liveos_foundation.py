from __future__ import annotations

import unittest
from pathlib import Path


class LiveOsFoundationTests(unittest.TestCase):
    def test_liveos_structure_exists(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        liveos_root = project_root / "liveos"

        self.assertTrue((liveos_root / "README.md").exists())
        self.assertTrue((liveos_root / "shell" / "Start-CigerToolLiveShell.ps1").exists())
        self.assertTrue((liveos_root / "startup" / "Start-CigerToolLiveSession.ps1").exists())
        self.assertTrue((liveos_root / "startup" / "Start-CigerToolApp.ps1").exists())
        self.assertTrue((liveos_root / "startup" / "CigerToolLive.Runtime.ps1").exists())

    def test_liveos_build_script_exists(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        script = project_root / "build" / "scripts" / "build_liveos_foundation.ps1"
        self.assertTrue(script.exists())

    def test_project_script_points_to_launcher(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        pyproject = (project_root / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('cigertool = "cigertool.launcher:main"', pyproject)

    def test_winpe_bootstrap_points_to_live_shell(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        winpeshl = (project_root / "winpe" / "files" / "Windows" / "System32" / "winpeshl.ini").read_text(encoding="utf-8")
        launcher = (project_root / "winpe" / "files" / "Windows" / "System32" / "cigertool-launch.cmd").read_text(encoding="utf-8")

        self.assertIn("cmd.exe", winpeshl)
        self.assertIn("Start-CigerToolLiveShell.ps1", launcher)

    def test_liveos_build_script_stages_runtime_operation_scripts(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        script = (project_root / "build" / "scripts" / "build_liveos_foundation.ps1").read_text(encoding="utf-8")

        self.assertIn("invoke_smart_clone.ps1", script)
        self.assertIn("invoke_raw_clone.ps1", script)
        self.assertIn("invoke_boot_fix.ps1", script)
        self.assertIn("legacy iso-library payload", script)
        self.assertIn("LegacyIsoLibraryRoot", script)

    def test_live_session_exports_runtime_contract_variables(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        session = (project_root / "liveos" / "startup" / "Start-CigerToolLiveSession.ps1").read_text(encoding="utf-8")

        self.assertIn("CIGERTOOL_RUNTIME_ROOT", session)
        self.assertIn("CIGERTOOL_SCRIPTS_ROOT", session)
        self.assertIn("CIGERTOOL_LOG_ROOT", session)
        self.assertIn("CIGERTOOL_RUNTIME_STATUS_PATH", session)

    def test_live_shell_documents_recovery_paths(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        launcher = (project_root / "winpe" / "files" / "Windows" / "System32" / "cigertool-launch.cmd").read_text(encoding="utf-8")

        self.assertIn("liveos-status.json", launcher)
        self.assertIn("cigertool.log", launcher)

    def test_workflows_pin_runner_and_force_node24(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        liveos_workflow = (project_root / ".github" / "workflows" / "build-liveos-foundation.yml").read_text(encoding="utf-8")
        legacy_workflow = (project_root / ".github" / "workflows" / "build-iso.yml").read_text(encoding="utf-8")

        self.assertIn("runs-on: windows-2025", liveos_workflow)
        self.assertIn("FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true", liveos_workflow)
        self.assertIn("Validate LiveOS foundation artifact", liveos_workflow)
        self.assertIn("runs-on: windows-2025", legacy_workflow)
        self.assertIn("FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true", legacy_workflow)


if __name__ == "__main__":
    unittest.main()
