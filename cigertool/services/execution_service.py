from __future__ import annotations

from collections.abc import Callable

from ..commands import CommandRunner
from ..models import OperationPlan


class ExecutionService:
    def __init__(self, runner: CommandRunner) -> None:
        self.runner = runner

    def run_plan(self, plan: OperationPlan, callback: Callable[[str], None] | None = None) -> None:
        for index, step in enumerate(plan.steps, start=1):
            if callback:
                callback(f"[{index}/{len(plan.steps)}] {step.title}")
            try:
                if callback:
                    self.runner.run_streaming(step.command, shell=step.shell, on_line=callback)
                else:
                    self.runner.run(step.command, shell=step.shell)
            except Exception as exc:
                message = f"{step.title} adiminda hata: {exc}"
                if callback:
                    callback(message)
                raise RuntimeError(message) from exc
