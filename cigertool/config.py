from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import tempfile


APP_NAME = "CigerTool by hkannq"
ISO_NAME = "CigerTool-by-hkannq.iso"
APP_DIR_NAME = "CigerTool"
COMPANY_NAME = "hkannq"
DEFAULT_THEME = "turkuaz"
DEFAULT_LANGUAGE = "tr"
DEFAULT_LOG_FILENAME = "cigertool.log"
DEFAULT_RUNTIME_STATUS_FILENAME = "liveos-status.json"

RUNTIME_MODE_ENV = "CIGERTOOL_RUNTIME"
RUNTIME_ROOT_ENV = "CIGERTOOL_RUNTIME_ROOT"
RUNTIME_SCRIPTS_ROOT_ENV = "CIGERTOOL_SCRIPTS_ROOT"
RUNTIME_LOG_ROOT_ENV = "CIGERTOOL_LOG_ROOT"
RUNTIME_LOG_PATH_ENV = "CIGERTOOL_LOG_PATH"
RUNTIME_STATUS_PATH_ENV = "CIGERTOOL_RUNTIME_STATUS_PATH"
RUNTIME_TOOLS_ROOT_ENV = "CIGERTOOL_TOOLS_ROOT"
RUNTIME_ISOS_ROOT_ENV = "CIGERTOOL_ISOS_ROOT"
RUNTIME_DEFAULT_BROWSER_ROOT_ENV = "CIGERTOOL_DEFAULT_BROWSER_ROOT"

APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent
TOOLS_ROOT = PROJECT_ROOT / "tools"
ASSETS_ROOT = PROJECT_ROOT / "cigertool" / "assets"
WINPE_ROOT = PROJECT_ROOT / "winpe"
BUILD_ROOT = PROJECT_ROOT / "build"
ARTIFACT_ROOT = PROJECT_ROOT / "artifacts"
ISOS_ROOT = PROJECT_ROOT / "isos"
ISOS_WINDOWS_ROOT = ISOS_ROOT / "windows"
ISOS_LINUX_ROOT = ISOS_ROOT / "linux"
ISOS_TOOLS_ROOT = ISOS_ROOT / "tools"
ISO_LIBRARY_ROOT = ISOS_ROOT
LEGACY_ISO_LIBRARY_ROOT = PROJECT_ROOT / "iso-library"
LOG_PATH = Path(tempfile.gettempdir()) / "cigertool.log"

ADK_ROOT_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit"),
    Path(r"C:\Program Files\Windows Kits\10\Assessment and Deployment Kit"),
]


@dataclass(slots=True)
class AppSettings:
    theme: str = DEFAULT_THEME
    language: str = DEFAULT_LANGUAGE
    dry_run: bool = True
    temp_dir: Path = Path(tempfile.gettempdir()) / "cigertool"


def resolve_adk_root() -> Path | None:
    env_value = os.environ.get("CIGERTOOL_ADK_ROOT")
    if env_value:
        candidate = Path(env_value)
        if candidate.exists():
            return candidate
    for candidate in ADK_ROOT_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def _path_from_env(name: str, *, must_exist: bool = True) -> Path | None:
    value = os.environ.get(name)
    if not value:
        return None

    candidate = Path(value).expanduser()
    if must_exist and not candidate.exists():
        return None
    return candidate.resolve() if candidate.exists() else candidate


def _unique_paths(paths: list[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[str] = set()
    for item in paths:
        rendered = str(item).lower()
        if rendered in seen:
            continue
        seen.add(rendered)
        unique.append(item)
    return unique


def resolve_runtime_mode() -> str:
    configured = os.environ.get(RUNTIME_MODE_ENV)
    if configured:
        return configured.strip().lower()
    if os.environ.get("SYSTEMDRIVE", "").upper() == "X:":
        return "winpe"
    return "windows"


def resolve_runtime_root() -> Path:
    return _path_from_env(RUNTIME_ROOT_ENV) or PROJECT_ROOT


def candidate_script_roots() -> list[Path]:
    runtime_root = resolve_runtime_root()
    env_root = _path_from_env(RUNTIME_SCRIPTS_ROOT_ENV)
    candidates = [
        candidate
        for candidate in [
            env_root,
            runtime_root / APP_DIR_NAME / "scripts",
            runtime_root / "app" / APP_DIR_NAME / "scripts",
            BUILD_ROOT / "scripts",
        ]
        if candidate is not None
    ]
    return _unique_paths(candidates)


def resolve_scripts_root() -> Path:
    for candidate in candidate_script_roots():
        if candidate.exists():
            return candidate.resolve()
    return candidate_script_roots()[0]


def resolve_operation_script(script_name: str) -> Path:
    for root in candidate_script_roots():
        candidate = root / script_name
        if candidate.exists():
            return candidate.resolve()
    searched = ", ".join(str(path) for path in candidate_script_roots())
    raise FileNotFoundError(f"Operasyon scripti bulunamadi: {script_name} | aranan kokler: {searched}")


def resolve_log_root() -> Path:
    explicit_root = _path_from_env(RUNTIME_LOG_ROOT_ENV, must_exist=False)
    if explicit_root is not None:
        return explicit_root

    runtime_root = resolve_runtime_root()
    if resolve_runtime_mode() == "liveos":
        return runtime_root / "liveos" / "logs"
    return Path(tempfile.gettempdir())


def resolve_log_path() -> Path:
    explicit_path = _path_from_env(RUNTIME_LOG_PATH_ENV, must_exist=False)
    if explicit_path is not None:
        return explicit_path
    return resolve_log_root() / DEFAULT_LOG_FILENAME


def resolve_runtime_status_path() -> Path:
    explicit_path = _path_from_env(RUNTIME_STATUS_PATH_ENV, must_exist=False)
    if explicit_path is not None:
        return explicit_path
    return resolve_log_root() / DEFAULT_RUNTIME_STATUS_FILENAME
