from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import logging
import subprocess
from collections.abc import Callable


@dataclass(slots=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


class CommandError(RuntimeError):
    pass


class CommandRunner:
    def __init__(
        self,
        logger: logging.Logger,
        dry_run: bool = False,
        default_cwd: str | Path | None = None,
    ) -> None:
        self.logger = logger
        self.dry_run = dry_run
        self.default_cwd = Path(default_cwd) if default_cwd else None

    def run(
        self,
        command: list[str] | str,
        *,
        shell: bool = False,
        check: bool = True,
        cwd: str | Path | None = None,
        dry_run: bool | None = None,
    ) -> CommandResult:
        active_dry_run = self.dry_run if dry_run is None else dry_run
        active_cwd = Path(cwd) if cwd else self.default_cwd
        rendered = command if isinstance(command, str) else " ".join(command)
        rendered_cwd = str(active_cwd) if active_cwd else ""
        self.logger.info("Komut: %s", rendered)
        if active_dry_run:
            return CommandResult(0, "", f"[DRY-RUN] {rendered}")

        completed = subprocess.run(
            command,
            shell=shell,
            cwd=str(active_cwd) if active_cwd else None,
            text=True,
            capture_output=True,
            check=False,
        )
        result = CommandResult(completed.returncode, completed.stdout or "", completed.stderr or "")
        if result.stdout.strip():
            self.logger.info("Komut stdout: %s", result.stdout.strip())
        if result.stderr.strip():
            self.logger.warning("Komut stderr: %s", result.stderr.strip())
        if check and completed.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or rendered
            if rendered_cwd:
                raise CommandError(f"Komut basarisiz (cwd={rendered_cwd}): {detail}")
            raise CommandError(f"Komut basarisiz: {detail}")
        return result

    def powershell_json(self, script: str) -> object:
        wrapper = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            script,
        ]
        result = self.run(wrapper, dry_run=False)
        output = result.stdout.strip() or "null"
        return json.loads(output)

    def run_streaming(
        self,
        command: list[str] | str,
        *,
        shell: bool = False,
        check: bool = True,
        cwd: str | Path | None = None,
        dry_run: bool | None = None,
        on_line: Callable[[str], None] | None = None,
    ) -> CommandResult:
        active_dry_run = self.dry_run if dry_run is None else dry_run
        active_cwd = Path(cwd) if cwd else self.default_cwd
        rendered = command if isinstance(command, str) else " ".join(command)
        rendered_cwd = str(active_cwd) if active_cwd else ""
        self.logger.info("Komut: %s", rendered)
        if active_dry_run:
            text = f"[DRY-RUN] {rendered}"
            if on_line:
                on_line(text)
            return CommandResult(0, text, "")

        process = subprocess.Popen(
            command,
            shell=shell,
            cwd=str(active_cwd) if active_cwd else None,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
        )
        output_lines: list[str] = []
        assert process.stdout is not None
        for line in process.stdout:
            cleaned = line.rstrip()
            output_lines.append(cleaned)
            if on_line and cleaned:
                on_line(cleaned)

        process.wait()
        stdout = "\n".join(output_lines)
        result = CommandResult(process.returncode, stdout, "")
        if check and process.returncode != 0:
            detail = result.stdout.strip() or rendered
            if rendered_cwd:
                raise CommandError(f"Komut basarisiz (cwd={rendered_cwd}): {detail}")
            raise CommandError(f"Komut basarisiz: {detail}")
        return result
