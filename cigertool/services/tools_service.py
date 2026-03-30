from __future__ import annotations

from pathlib import Path
import json

from ..models import ToolEntry
from .system_service import SystemEnvironmentService


class ToolsCatalogService:
    MANIFEST_NAME = "cigertool-tool.json"
    LAYER_ORDER = {"CORE": 0, "PRELOADED": 1, "USER": 2}

    def __init__(self, system_service: SystemEnvironmentService) -> None:
        self.system_service = system_service

    def list_tools(self) -> list[ToolEntry]:
        manifest_entries = self._manifest_tools()
        preloaded = self._preloaded_tools()
        items = self._core_tools() + manifest_entries + preloaded + self._user_tools(manifest_entries + preloaded)
        deduped = self._dedupe_entries(items)
        return sorted(
            deduped,
            key=lambda item: (
                self.LAYER_ORDER.get(item.layer, 99),
                item.category.lower(),
                item.name.lower(),
            ),
        )

    @staticmethod
    def _core_tools() -> list[ToolEntry]:
        return [
            ToolEntry("Clone Wizard", "CORE", "Disk klonlama ve tasima sihirbazi.", bundled=True, layer="CORE", internal_page="clone"),
            ToolEntry("SMART Viewer", "CORE", "Disk saglik ve sicaklik ozeti.", bundled=True, layer="CORE", internal_page="smart"),
            ToolEntry("Dosya Yoneticisi", "CORE", "USB ve disk icerigini gezmek icin yerlesik yonetici.", bundled=True, layer="CORE", internal_page="files"),
            ToolEntry("Boot Repair", "CORE", "EFI ve MBR onarim plani.", bundled=True, layer="CORE", internal_page="boot"),
            ToolEntry("ISO Library", "CORE", "Kullanici ISO kutuphanesi tarama ve acilis bilgileri.", bundled=True, layer="CORE", internal_page="isos"),
            ToolEntry("Log Viewer", "CORE", "Canli ortam loglarini izlemek icin yerlesik gorunum.", bundled=True, layer="CORE", internal_page="logs"),
            ToolEntry("Terminal", "CORE", "Ileri seviye komut satiri araclari icin shell erisimi.", launch_path="cmd.exe", bundled=True, layer="CORE"),
        ]

    def _manifest_tools(self) -> list[ToolEntry]:
        entries: list[ToolEntry] = []
        for root in self.system_service.tool_roots():
            for manifest_path in sorted(root.rglob(self.MANIFEST_NAME)):
                try:
                    entry = self._load_manifest_entry(root, manifest_path)
                except Exception:
                    continue
                if entry is not None:
                    entries.append(entry)
        return entries

    def _load_manifest_entry(self, root: Path, manifest_path: Path) -> ToolEntry | None:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        name = str(payload.get("name") or "").strip()
        if not name:
            return None

        manifest_dir = manifest_path.parent
        entry_name = str(payload.get("entry") or "").strip()
        entry_path: str | None = None
        if entry_name:
            candidate = manifest_dir / entry_name
            entry_path = str(candidate.resolve()) if candidate.exists() else str(candidate)

        working_directory: str | None = None
        working_dir_value = str(payload.get("working_directory") or "").strip()
        if working_dir_value:
            working_directory = str((manifest_dir / working_dir_value).resolve()) if not Path(working_dir_value).is_absolute() else working_dir_value
        elif entry_path:
            working_directory = str(Path(entry_path).parent)

        arguments = payload.get("arguments") or []
        if not isinstance(arguments, list):
            arguments = []

        category = str(payload.get("category") or "User Tool").strip() or "User Tool"
        description = str(payload.get("description") or f"Kullanici araci: {name}").strip()
        layer = str(payload.get("layer") or "USER").strip().upper() or "USER"
        bundled = bool(payload.get("bundled", layer != "USER"))
        internal_page = str(payload.get("internal_page") or "").strip() or None

        if entry_path and not Path(entry_path).exists():
            description += " Giris dosyasi bulunamazsa manifesti ve entry alanini kontrol edin."

        return ToolEntry(
            name=name,
            category=category,
            description=description,
            launch_path=entry_path,
            launch_args=[str(item) for item in arguments],
            working_directory=working_directory,
            internal_page=internal_page,
            manifest_path=str(manifest_path),
            bundled=bundled,
            layer=layer,
            source_root=str(root),
        )

    def _preloaded_tools(self) -> list[ToolEntry]:
        expected = [
            ("Google Chrome Portable", "Browser", "Portable tarayici.", ("browser", "chrome-portable"), "ChromePortable.exe"),
            ("CPU-Z Portable", "Diagnostics", "Donanim ozeti ve CPU/RAM bilgisi.", ("diagnostics", "cpu-z"), "cpuz_x64.exe"),
            ("Disk Benchmark Tool", "Benchmark", "Disk hiz testi araci.", ("benchmark", "disk-benchmark"), "benchmark.exe"),
            ("System Info Tool", "Diagnostics", "Sistem ozeti ve bilesen bilgisi.", ("diagnostics", "system-info"), "systeminfo.exe"),
            ("Network Tools", "Network", "Ag teshis ve baglanti araclari.", ("network", "network-tools"), "nettools.exe"),
            ("Partition Tool", "Storage", "Bolumleme ve disk duzenleme yardimcisi.", ("storage", "partition-tool"), "partition-tool.exe"),
        ]
        entries: list[ToolEntry] = []
        for name, category, description, path_parts, filename in expected:
            launch_path, source_root = self._resolve_tool(path_parts, filename)
            entries.append(
                ToolEntry(
                    name=name,
                    category=category,
                    description=description if launch_path else description + " Bulunamazsa tools klasorundeki ilgili kategoriye eklenebilir.",
                    launch_path=launch_path,
                    working_directory=str(Path(launch_path).parent) if launch_path else None,
                    bundled=bool(launch_path),
                    layer="PRELOADED",
                    source_root=source_root,
                )
            )
        return entries

    def _user_tools(self, reserved_entries: list[ToolEntry]) -> list[ToolEntry]:
        entries: list[ToolEntry] = []
        seen: set[str] = set()
        reserved_paths = {item.launch_path.lower() for item in reserved_entries if item.launch_path}
        reserved_dirs = {str(Path(item.launch_path).parent).lower() for item in reserved_entries if item.launch_path}

        for root in self.system_service.tool_roots():
            for path in root.rglob("*.exe"):
                key = str(path).lower()
                if key in seen or key in reserved_paths:
                    continue
                if str(path.parent).lower() in reserved_dirs:
                    continue
                seen.add(key)
                category = self._categorize_path(root, path)
                entries.append(
                    ToolEntry(
                        name=path.stem,
                        category=category,
                        description=f"Kullanici araci: {path.name}",
                        launch_path=str(path.resolve()),
                        working_directory=str(path.parent.resolve()),
                        bundled=False,
                        layer="USER",
                        source_root=str(root),
                    )
                )
        return entries

    def _resolve_tool(self, path_parts: tuple[str, ...], filename: str) -> tuple[str | None, str | None]:
        for root in self.system_service.tool_roots():
            candidates = [
                root.joinpath(*path_parts, filename),
                root / path_parts[-1] / filename,
                root / filename,
            ]
            for candidate in candidates:
                if candidate.exists():
                    return str(candidate.resolve()), str(root.resolve())
        return None, None

    def _dedupe_entries(self, items: list[ToolEntry]) -> list[ToolEntry]:
        deduped: list[ToolEntry] = []
        seen: set[str] = set()
        for item in items:
            key = self._dedupe_key(item)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(item)
        return deduped

    @staticmethod
    def _dedupe_key(item: ToolEntry) -> str:
        if item.internal_page:
            return f"internal:{item.internal_page.lower()}"
        if item.launch_path:
            return f"path:{item.launch_path.lower()}"
        if item.manifest_path:
            return f"manifest:{item.manifest_path.lower()}"
        return f"name:{item.layer.lower()}:{item.name.lower()}"

    @staticmethod
    def _categorize_path(root: Path, path: Path) -> str:
        try:
            relative_parts = [part.lower() for part in path.relative_to(root).parts]
        except ValueError:
            return ToolsCatalogService._categorize_name(path.name)

        if relative_parts:
            category_part = relative_parts[0]
            mapping = {
                "browser": "Browser",
                "diagnostics": "Diagnostics",
                "benchmark": "Benchmark",
                "storage": "Storage",
                "network": "Network",
                "user": "User Tool",
            }
            if category_part in mapping:
                return mapping[category_part]
        return ToolsCatalogService._categorize_name(path.name)

    @staticmethod
    def _categorize_name(name: str) -> str:
        lowered = name.lower()
        if any(token in lowered for token in ("cpu", "info", "hwinfo", "speccy")):
            return "Diagnostics"
        if any(token in lowered for token in ("bench", "crystal", "mark")):
            return "Benchmark"
        if any(token in lowered for token in ("disk", "part", "gpt", "mbr")):
            return "Storage"
        if any(token in lowered for token in ("net", "wifi", "ip", "rdp", "putty")):
            return "Network"
        if any(token in lowered for token in ("chrome", "firefox", "browser")):
            return "Browser"
        return "User Tool"
