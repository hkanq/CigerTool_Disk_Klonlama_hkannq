from __future__ import annotations

from pathlib import Path
import logging

from .config import resolve_log_path


def get_logger() -> logging.Logger:
    logger = logging.getLogger("cigertool")
    if logger.handlers:
        return logger

    log_path = resolve_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def tail_log(lines: int = 200) -> str:
    path = Path(resolve_log_path())
    if not path.exists():
        return ""
    content = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(content[-lines:])
