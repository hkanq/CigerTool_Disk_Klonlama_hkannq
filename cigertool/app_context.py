from __future__ import annotations

from dataclasses import dataclass

from .commands import CommandRunner
from .logger import get_logger
from .services.boot_service import BootRepairService
from .services.clone_service import CloneService
from .services.disk_service import DiskService
from .services.execution_service import ExecutionService
from .services.multiboot_service import MultibootService
from .services.smart_service import SmartService
from .services.system_service import SystemEnvironmentService
from .services.tool_launcher_service import ToolLauncherService
from .services.tools_service import ToolsCatalogService


@dataclass(slots=True)
class AppContext:
    runner: CommandRunner
    disk_service: DiskService
    clone_service: CloneService
    boot_service: BootRepairService
    smart_service: SmartService
    tools_service: ToolsCatalogService
    tool_launcher_service: ToolLauncherService
    multiboot_service: MultibootService
    system_service: SystemEnvironmentService
    execution_service: ExecutionService


def create_context(dry_run: bool = False) -> AppContext:
    logger = get_logger()
    system_service = SystemEnvironmentService()
    runner = CommandRunner(logger, dry_run=dry_run, default_cwd=system_service.runtime_root())
    return AppContext(
        runner=runner,
        disk_service=DiskService(runner, logger),
        clone_service=CloneService(logger),
        boot_service=BootRepairService(logger),
        smart_service=SmartService(runner, logger),
        tools_service=ToolsCatalogService(system_service),
        tool_launcher_service=ToolLauncherService(system_service),
        multiboot_service=MultibootService(logger),
        system_service=system_service,
        execution_service=ExecutionService(runner),
    )
