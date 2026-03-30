from __future__ import annotations

from pathlib import Path
import subprocess

from ..models import ToolEntry
from .system_service import SystemEnvironmentService


class ToolLaunchError(RuntimeError):
    pass


class ToolLauncherService:
    def __init__(self, system_service: SystemEnvironmentService) -> None:
        self.system_service = system_service

    def launch(self, tool: ToolEntry) -> None:
        if tool.internal_page:
            raise ToolLaunchError("Uygulama ici araclar UI launcher uzerinden acilmalidir.")
        if not tool.launch_path:
            raise ToolLaunchError("Secilen arac icin calistirilabilir dosya tanimli degil.")

        command = [tool.launch_path, *tool.launch_args]
        working_directory = self.resolve_working_directory(tool)
        try:
            subprocess.Popen(command, cwd=str(working_directory))
        except OSError as exc:
            raise ToolLaunchError(str(exc)) from exc

    def open_tool_directory(self, tool: ToolEntry) -> None:
        directory = self.resolve_working_directory(tool)
        try:
            subprocess.Popen(["explorer.exe", str(directory)], cwd=str(directory))
        except OSError as exc:
            raise ToolLaunchError(str(exc)) from exc

    def resolve_working_directory(self, tool: ToolEntry) -> Path:
        candidates: list[Path] = []
        if tool.working_directory:
            candidates.append(Path(tool.working_directory))
        if tool.launch_path:
            launch_candidate = Path(tool.launch_path)
            if launch_candidate.exists():
                candidates.append(launch_candidate.parent)
        if tool.manifest_path:
            manifest_candidate = Path(tool.manifest_path)
            if manifest_candidate.exists():
                candidates.append(manifest_candidate.parent)
        if tool.source_root:
            candidates.append(Path(tool.source_root))
        candidates.append(self.system_service.runtime_root())

        for candidate in candidates:
            if candidate.exists():
                return candidate.resolve()
        return self.system_service.runtime_root()
