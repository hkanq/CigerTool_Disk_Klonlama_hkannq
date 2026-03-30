from __future__ import annotations

import logging

from ..config import resolve_operation_script
from ..models import Disk, PartitionRole, PlanStep


class BootRepairService:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def plan(self, disk: Disk) -> list[PlanStep]:
        efi = next((part for part in disk.partitions if part.role is PartitionRole.EFI), None)
        windows = next((part for part in disk.partitions if part.can_host_windows and part.drive_letter), None)
        script_path = resolve_operation_script("invoke_boot_fix.ps1")
        if efi and windows:
            return [
                PlanStep(
                    "EFI ve BCD onarimi",
                    [
                        "powershell",
                        "-NoProfile",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        str(script_path),
                        "-WindowsDrive",
                        windows.drive_letter,
                        "-EfiDisk",
                        str(disk.number),
                    ],
                    destructive=True,
                )
            ]
        return [
            PlanStep(
                "MBR boot onarimi",
                    [
                        "powershell",
                        "-NoProfile",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        str(script_path),
                        "-WindowsDrive",
                        windows.drive_letter if windows else "C",
                        "-MbrDisk",
                    str(disk.number),
                ],
                destructive=True,
            )
        ]
