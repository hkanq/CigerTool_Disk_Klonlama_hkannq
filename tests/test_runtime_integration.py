from __future__ import annotations

import os
import tempfile
import unittest
import json
from pathlib import Path
from unittest import mock

from cigertool.config import resolve_log_path, resolve_operation_script, resolve_runtime_status_path, resolve_scripts_root
from cigertool.models import CloneAnalysis, CloneMode, Disk, DiskBus, OperationPlan, Partition, PlanRisk, PlanStep, WINDOWS_BASIC_GUID, WINDOWS_EFI_GUID
from cigertool.services.boot_service import BootRepairService
from cigertool.services.clone_service import CloneService
from cigertool.services.execution_service import ExecutionService
from cigertool.services.system_service import SystemEnvironmentService


class DummyLogger:
    def info(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def error(self, *args, **kwargs):
        return None


class FailingRunner:
    def run_streaming(self, *args, **kwargs):
        raise RuntimeError("komut patladi")


class RuntimeIntegrationTests(unittest.TestCase):
    def _source_disk(self) -> Disk:
        return Disk(
            number=0,
            path="\\\\.\\PhysicalDrive0",
            friendly_name="Kaynak Disk",
            serial="SRC",
            bus_type=DiskBus.SATA,
            size_bytes=256 * 1024**3,
            partition_style="GPT",
            health_status="Healthy",
            operational_status="Online",
            partitions=[
                Partition(0, 1, 260 * 1024**2, fs_type="FAT32", gpt_type=WINDOWS_EFI_GUID, used_bytes=120 * 1024**2),
                Partition(
                    0,
                    2,
                    160 * 1024**3,
                    fs_type="NTFS",
                    drive_letter="C",
                    gpt_type=WINDOWS_BASIC_GUID,
                    used_bytes=70 * 1024**3,
                    is_boot=True,
                    is_system=True,
                ),
            ],
        )

    def _target_disk(self) -> Disk:
        return Disk(
            number=1,
            path="\\\\.\\PhysicalDrive1",
            friendly_name="Hedef Disk",
            serial="DST",
            bus_type=DiskBus.SATA,
            size_bytes=120 * 1024**3,
            partition_style="GPT",
            health_status="Healthy",
            operational_status="Online",
            partitions=[],
        )

    def test_runtime_script_resolution_prefers_live_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            scripts_root = Path(temp_dir) / "scripts"
            scripts_root.mkdir(parents=True, exist_ok=True)
            script_path = scripts_root / "invoke_smart_clone.ps1"
            script_path.write_text("# runtime script", encoding="utf-8")

            with mock.patch.dict(os.environ, {"CIGERTOOL_SCRIPTS_ROOT": str(scripts_root)}, clear=False):
                self.assertEqual(resolve_scripts_root(), scripts_root.resolve())
                self.assertEqual(resolve_operation_script("invoke_smart_clone.ps1"), script_path.resolve())

    def test_clone_plan_uses_runtime_staged_script(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            scripts_root = Path(temp_dir) / "scripts"
            scripts_root.mkdir(parents=True, exist_ok=True)
            smart_clone = scripts_root / "invoke_smart_clone.ps1"
            smart_clone.write_text("# smart clone", encoding="utf-8")

            with mock.patch.dict(os.environ, {"CIGERTOOL_SCRIPTS_ROOT": str(scripts_root)}, clear=False):
                service = CloneService(DummyLogger())
                analysis = service.analyze(self._source_disk(), self._target_disk())
                plan = service.build_plan(analysis, CloneMode.SMART)

            self.assertEqual(plan.steps[0].command[5], str(smart_clone.resolve()))

    def test_boot_plan_uses_runtime_staged_script(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            scripts_root = Path(temp_dir) / "scripts"
            scripts_root.mkdir(parents=True, exist_ok=True)
            boot_fix = scripts_root / "invoke_boot_fix.ps1"
            boot_fix.write_text("# boot fix", encoding="utf-8")

            with mock.patch.dict(os.environ, {"CIGERTOOL_SCRIPTS_ROOT": str(scripts_root)}, clear=False):
                service = BootRepairService(DummyLogger())
                steps = service.plan(self._source_disk())

            self.assertEqual(steps[0].command[5], str(boot_fix.resolve()))

    def test_system_service_prefers_runtime_tools_and_isos(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_root = Path(temp_dir)
            tools_root = runtime_root / "tools"
            windows_isos = runtime_root / "isos" / "windows"
            tools_root.mkdir(parents=True, exist_ok=True)
            windows_isos.mkdir(parents=True, exist_ok=True)

            env = {
                "CIGERTOOL_RUNTIME": "liveos",
                "CIGERTOOL_RUNTIME_ROOT": str(runtime_root),
            }
            with mock.patch.dict(os.environ, env, clear=False):
                service = SystemEnvironmentService()
                tool_roots = service.tool_roots()
                iso_roots = service.iso_roots()
                browser_root = service.default_file_browser_root()

            self.assertIn(tools_root.resolve(), tool_roots)
            self.assertIn(windows_isos.resolve(), iso_roots)
            self.assertEqual(browser_root, runtime_root.resolve())

    def test_log_path_prefers_runtime_log_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_root = Path(temp_dir) / "logs"
            with mock.patch.dict(os.environ, {"CIGERTOOL_LOG_ROOT": str(log_root)}, clear=False):
                self.assertEqual(resolve_log_path(), log_root / "cigertool.log")

    def test_runtime_status_path_prefers_runtime_log_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_root = Path(temp_dir) / "logs"
            with mock.patch.dict(os.environ, {"CIGERTOOL_LOG_ROOT": str(log_root)}, clear=False):
                self.assertEqual(resolve_runtime_status_path(), log_root / "liveos-status.json")

    def test_system_service_reads_runtime_status_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            status_path = Path(temp_dir) / "liveos-status.json"
            payload = {"stage": "session", "state": "ready", "message": "Hazir"}
            status_path.write_text(json.dumps(payload), encoding="utf-8")

            with mock.patch.dict(os.environ, {"CIGERTOOL_RUNTIME_STATUS_PATH": str(status_path)}, clear=False):
                data = SystemEnvironmentService.read_runtime_status()

            self.assertEqual(data["stage"], "session")
            self.assertEqual(data["state"], "ready")

    def test_execution_service_wraps_step_error_with_step_title(self) -> None:
        source = self._source_disk()
        target = self._target_disk()
        analysis = CloneAnalysis(
            source_disk=source,
            target_disk=target,
            source_used_bytes=10,
            target_usable_bytes=20,
            fits_raw=True,
            fits_smart=True,
            recommended_mode=CloneMode.SMART,
        )
        plan = OperationPlan(
            mode=CloneMode.SMART,
            title="Test plan",
            summary="Test",
            warnings=[],
            steps=[PlanStep(title="Kritik adim", command=["powershell", "-NoProfile"])],
            risk=PlanRisk.LOW,
            analysis=analysis,
        )

        service = ExecutionService(FailingRunner())  # type: ignore[arg-type]
        with self.assertRaises(RuntimeError) as context:
            service.run_plan(plan)

        self.assertIn("Kritik adim adiminda hata", str(context.exception))


if __name__ == "__main__":
    unittest.main()
