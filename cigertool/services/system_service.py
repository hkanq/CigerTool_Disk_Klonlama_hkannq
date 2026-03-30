from __future__ import annotations

import os
import json
from pathlib import Path

from ..config import (
    APP_DIR_NAME,
    RUNTIME_DEFAULT_BROWSER_ROOT_ENV,
    RUNTIME_ISOS_ROOT_ENV,
    RUNTIME_TOOLS_ROOT_ENV,
    ISOS_LINUX_ROOT,
    ISOS_TOOLS_ROOT,
    ISOS_WINDOWS_ROOT,
    LEGACY_ISO_LIBRARY_ROOT,
    TOOLS_ROOT,
    resolve_log_path,
    resolve_log_root,
    resolve_runtime_status_path,
    resolve_adk_root,
    resolve_runtime_mode,
    resolve_runtime_root,
    resolve_scripts_root,
)


class SystemEnvironmentService:
    @staticmethod
    def is_winpe() -> bool:
        return os.environ.get("SYSTEMDRIVE", "").upper() == "X:"

    @staticmethod
    def adk_installed() -> bool:
        return resolve_adk_root() is not None

    @staticmethod
    def runtime_mode() -> str:
        return resolve_runtime_mode()

    @staticmethod
    def runtime_root() -> Path:
        return resolve_runtime_root()

    @staticmethod
    def scripts_root() -> Path:
        return resolve_scripts_root()

    @staticmethod
    def log_path() -> Path:
        return resolve_log_path()

    @staticmethod
    def log_root() -> Path:
        return resolve_log_root()

    @staticmethod
    def runtime_status_path() -> Path:
        return resolve_runtime_status_path()

    @staticmethod
    def read_runtime_status() -> dict:
        path = resolve_runtime_status_path()
        if not path.exists():
            return {}
        try:
            content = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return content if isinstance(content, dict) else {}

    @staticmethod
    def removable_roots() -> list[Path]:
        roots = []
        for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
            root = Path(f"{letter}:\\")
            if root.exists():
                roots.append(root)
        return roots

    @classmethod
    def _unique_existing_paths(cls, candidates: list[Path]) -> list[Path]:
        roots: list[Path] = []
        for candidate in candidates:
            if candidate.exists():
                roots.append(candidate.resolve())
        unique: list[Path] = []
        seen: set[str] = set()
        for item in roots:
            rendered = str(item).lower()
            if rendered in seen:
                continue
            seen.add(rendered)
            unique.append(item)
        return unique

    @staticmethod
    def _path_from_env(name: str) -> Path | None:
        value = os.environ.get(name)
        if not value:
            return None
        return Path(value).expanduser()

    @classmethod
    def tool_roots(cls) -> list[Path]:
        runtime_root = cls.runtime_root()
        env_root = cls._path_from_env(RUNTIME_TOOLS_ROOT_ENV)
        return cls._unique_existing_paths(
            [
                candidate
                for candidate in [
                    env_root,
                    runtime_root / "tools",
                    runtime_root / APP_DIR_NAME / "tools",
                    TOOLS_ROOT,
                    Path(f"X:\\{APP_DIR_NAME}\\tools"),
                    Path("X:\\tools"),
                    *(root / "tools" for root in cls.removable_roots()),
                ]
                if candidate is not None
            ]
        )

    @classmethod
    def iso_roots(cls) -> list[Path]:
        runtime_root = cls.runtime_root()
        env_root = cls._path_from_env(RUNTIME_ISOS_ROOT_ENV)
        candidate_roots = [
            env_root / "windows" if env_root else None,
            env_root / "linux" if env_root else None,
            env_root / "tools" if env_root else None,
            runtime_root / "isos" / "windows",
            runtime_root / "isos" / "linux",
            runtime_root / "isos" / "tools",
            runtime_root / "iso-library",
            ISOS_WINDOWS_ROOT,
            ISOS_LINUX_ROOT,
            ISOS_TOOLS_ROOT,
            LEGACY_ISO_LIBRARY_ROOT,
            *(root / "isos" / "windows" for root in cls.removable_roots()),
            *(root / "isos" / "linux" for root in cls.removable_roots()),
            *(root / "isos" / "tools" for root in cls.removable_roots()),
            *(root / "iso-library" for root in cls.removable_roots()),
        ]
        return cls._unique_existing_paths([candidate for candidate in candidate_roots if candidate is not None])

    @classmethod
    def default_file_browser_root(cls) -> Path:
        env_root = cls._path_from_env(RUNTIME_DEFAULT_BROWSER_ROOT_ENV)
        for candidate in [
            env_root,
            cls.runtime_root(),
            *cls.removable_roots(),
            Path.home(),
        ]:
            if candidate is not None and candidate.exists():
                return candidate.resolve()
        return Path.home()
