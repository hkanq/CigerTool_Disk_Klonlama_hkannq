from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileSystemModel,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from ..app_context import AppContext
from ..config import APP_NAME, LEGACY_ISO_LIBRARY_ROOT
from ..logger import tail_log
from ..models import CloneMode, Disk, IsoEntry, OperationPlan, ToolEntry, human_bytes
from .style import STYLE_SHEET
from .workers import TaskRunner


class MainWindow(QMainWindow):
    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self.context = context
        self.task_runner = TaskRunner()
        self.disks: list[Disk] = []
        self.current_plan: OperationPlan | None = None
        self.cached_tools: list[ToolEntry] = []
        self.cached_isos: list[IsoEntry] = []
        self.cached_startup_status: dict[str, Any] = {}
        self._last_startup_warning_key = ""
        self.setWindowTitle(APP_NAME)
        self.resize(1480, 940)
        self.setStyleSheet(STYLE_SHEET)
        self._build_ui()
        self.refresh_all()

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(16)

        content = self._build_pages()
        sidebar = self._build_sidebar()
        root_layout.addWidget(sidebar, 0)
        root_layout.addWidget(content, 1)
        self.setCentralWidget(root)

        self.refresh_action = QAction("Yenile", self)
        self.refresh_action.triggered.connect(self.refresh_all)
        self.menuBar().addAction(self.refresh_action)

    def _build_sidebar(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("Card")
        frame.setFixedWidth(260)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title = QLabel("CigerTool")
        title.setObjectName("Title")
        subtitle = QLabel("Canli ortamda clone, recovery, tanilama ve ISO kutuphanesi")
        subtitle.setObjectName("Subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.nav = QListWidget()
        for item in [
            "Disk Tara",
            "Klonla",
            "Boot Repair",
            "Disk Sagligi",
            "Benchmark",
            "Dosya Yoneticisi",
            "ISO Yonetimi",
            "Arac Kutusu",
            "Ayarlar",
            "Loglar",
        ]:
            QListWidgetItem(item, self.nav)
        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)  # type: ignore[attr-defined]
        layout.addWidget(self.nav, 1)

        self.refresh_button = QPushButton("Diskleri Yenile")
        self.refresh_button.setProperty("accent", True)
        self.refresh_button.clicked.connect(self.refresh_all)
        layout.addWidget(self.refresh_button)

        self.refresh_progress = QProgressBar()
        self.refresh_progress.setRange(0, 0)
        self.refresh_progress.hide()
        layout.addWidget(self.refresh_progress)

        self.winpe_label = QLabel("")
        self.winpe_label.setObjectName("Subtitle")
        layout.addWidget(self.winpe_label)
        return frame

    def _build_pages(self) -> QWidget:
        wrapper = QFrame()
        wrapper.setObjectName("Card")
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(18, 18, 18, 18)

        self.pages = QStackedWidget()
        pages = [
            self._build_dashboard_page(),
            self._build_clone_page(),
            self._build_boot_page(),
            self._build_smart_page(),
            self._build_benchmark_page(),
            self._build_files_page(),
            self._build_multiboot_page(),
            self._build_tools_page(),
            self._build_settings_page(),
            self._build_logs_page(),
        ]
        for page in pages:
            self.pages.addWidget(page)
        self.internal_tool_pages = {
            "dashboard": 0,
            "clone": 1,
            "boot": 2,
            "smart": 3,
            "benchmark": 4,
            "files": 5,
            "isos": 6,
            "tools": 7,
            "settings": 8,
            "logs": 9,
        }
        layout.addWidget(self.pages)
        return wrapper

    def _build_dashboard_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.dashboard_summary = QTextEdit()
        self.dashboard_summary.setReadOnly(True)
        self.disk_table = QTableWidget(0, 6)
        self.disk_table.setHorizontalHeaderLabels(["Disk", "Boyut", "Bus", "Model", "Seri", "Kullanilan"])
        layout.addWidget(self.dashboard_summary)
        layout.addWidget(self.disk_table, 1)
        return page

    def _build_clone_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        header = QLabel("Clone Wizard")
        header.setObjectName("Title")
        layout.addWidget(header)

        controls = QGridLayout()
        self.source_combo = QComboBox()
        self.target_combo = QComboBox()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["SMART CLONE", "RAW CLONE", "SYSTEM CLONE"])
        self.dry_run = QCheckBox("Dry-run / Simulasyon")
        self.dry_run.setChecked(True)
        self.analyze_button = QPushButton("Analiz Et")
        self.analyze_button.setProperty("accent", True)
        self.run_button = QPushButton("Clone Baslat")
        self.run_button.setProperty("danger", True)
        self.run_button.setEnabled(False)
        self.analyze_button.clicked.connect(self.analyze_clone)
        self.run_button.clicked.connect(self.run_clone)

        controls.addWidget(QLabel("Kaynak Disk"), 0, 0)
        controls.addWidget(self.source_combo, 0, 1)
        controls.addWidget(QLabel("Hedef Disk"), 1, 0)
        controls.addWidget(self.target_combo, 1, 1)
        controls.addWidget(QLabel("Clone Modu"), 2, 0)
        controls.addWidget(self.mode_combo, 2, 1)
        controls.addWidget(self.dry_run, 3, 0, 1, 2)
        controls.addWidget(self.analyze_button, 4, 0)
        controls.addWidget(self.run_button, 4, 1)
        layout.addLayout(controls)

        self.clone_summary = QTextEdit()
        self.clone_summary.setReadOnly(True)
        self.clone_recommendation = QLabel("")
        self.clone_recommendation.setObjectName("Subtitle")
        self.clone_progress = QProgressBar()
        self.clone_progress.setRange(0, 0)
        self.clone_progress.hide()
        self.clone_log = QTextEdit()
        self.clone_log.setReadOnly(True)
        layout.addWidget(self.clone_summary)
        layout.addWidget(self.clone_recommendation)
        layout.addWidget(self.clone_progress)
        layout.addWidget(self.clone_log, 1)
        return page

    def _build_boot_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Boot Repair")
        title.setObjectName("Title")
        self.boot_combo = QComboBox()
        self.boot_button = QPushButton("Boot Fix Hazirla")
        self.boot_button.clicked.connect(self.prepare_boot_fix)
        self.boot_output = QTextEdit()
        self.boot_output.setReadOnly(True)
        layout.addWidget(title)
        layout.addWidget(self.boot_combo)
        layout.addWidget(self.boot_button)
        layout.addWidget(self.boot_output, 1)
        return page

    def _build_smart_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Disk Sagligi ve Sistem Bilgisi")
        title.setObjectName("Title")
        self.smart_output = QTextEdit()
        self.smart_output.setReadOnly(True)
        layout.addWidget(title)
        layout.addWidget(self.smart_output, 1)
        return page

    def _build_benchmark_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Benchmark")
        title.setObjectName("Title")
        self.benchmark_summary = QTextEdit()
        self.benchmark_summary.setReadOnly(True)
        self.benchmark_launch = QPushButton("Benchmark Aracini Ac")
        self.benchmark_launch.clicked.connect(self.launch_benchmark_tool)
        layout.addWidget(title)
        layout.addWidget(self.benchmark_summary, 1)
        layout.addWidget(self.benchmark_launch)
        return page

    def _build_files_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Dosya Yoneticisi")
        title.setObjectName("Title")
        splitter = QSplitter()
        default_root = self.context.system_service.default_file_browser_root()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(str(default_root))
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(str(default_root)))
        self.file_preview = QTextEdit()
        self.file_preview.setReadOnly(True)
        self.file_tree.clicked.connect(self.preview_file)
        splitter.addWidget(self.file_tree)
        splitter.addWidget(self.file_preview)
        splitter.setSizes([480, 600])
        layout.addWidget(title)
        layout.addWidget(splitter, 1)
        return page

    def _build_multiboot_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("ISO Yonetimi")
        title.setObjectName("Title")
        info = QLabel("/isos/windows, /isos/linux ve /isos/tools otomatik taranir. Legacy iso-library okunur ama varsayilan yol degildir.")
        info.setObjectName("Subtitle")
        self.iso_table = QTableWidget(0, 8)
        self.iso_table.setHorizontalHeaderLabels(["ISO", "Durum", "Kutuphane", "Kategori", "Profil", "Boot", "Boyut", "Yol"])
        self.iso_table.itemSelectionChanged.connect(self._update_iso_details)
        self.iso_details = QTextEdit()
        self.iso_details.setReadOnly(True)
        layout.addWidget(title)
        layout.addWidget(info)
        layout.addWidget(self.iso_table, 1)
        layout.addWidget(self.iso_details)
        return page

    def _build_tools_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Arac Kutusu")
        title.setObjectName("Title")
        self.tools_table = QTableWidget(0, 6)
        self.tools_table.setHorizontalHeaderLabels(["Arac", "Katman", "Kategori", "Durum", "Kaynak", "Aciklama"])
        self.tools_table.itemSelectionChanged.connect(self._update_tool_details)
        self.tool_details = QTextEdit()
        self.tool_details.setReadOnly(True)
        actions = QHBoxLayout()
        self.tools_launch_button = QPushButton("Araci / Ozelligi Ac")
        self.tools_launch_button.clicked.connect(self.launch_selected_tool)
        self.tools_folder_button = QPushButton("Klasoru Ac")
        self.tools_folder_button.clicked.connect(self.open_selected_tool_directory)
        self.shell_button = QPushButton("Terminal Ac")
        self.shell_button.clicked.connect(lambda: self._launch_path("cmd.exe"))
        actions.addWidget(self.tools_launch_button)
        actions.addWidget(self.tools_folder_button)
        actions.addWidget(self.shell_button)
        layout.addWidget(title)
        layout.addWidget(self.tools_table, 1)
        layout.addWidget(self.tool_details)
        layout.addLayout(actions)
        return page

    def _build_settings_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Ayarlar")
        title.setObjectName("Title")
        self.settings_summary = QTextEdit()
        self.settings_summary.setReadOnly(True)
        layout.addWidget(title)
        layout.addWidget(self.settings_summary, 1)
        return page

    def _build_logs_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("Loglar")
        title.setObjectName("Title")
        actions = QHBoxLayout()
        self.log_refresh_button = QPushButton("Logu Yenile")
        self.log_refresh_button.clicked.connect(self.refresh_all)
        self.log_folder_button = QPushButton("Log Klasorunu Ac")
        self.log_folder_button.clicked.connect(self.open_log_directory)
        actions.addWidget(self.log_refresh_button)
        actions.addWidget(self.log_folder_button)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(title)
        layout.addLayout(actions)
        layout.addWidget(self.log_view, 1)
        return page

    def refresh_all(self) -> None:
        self._set_refresh_state(True)
        signals = self.task_runner.submit(lambda emit: self._load_snapshot())
        signals.result.connect(self._apply_snapshot)
        signals.failed.connect(self._refresh_failed)
        signals.finished.connect(lambda: self._set_refresh_state(False))

    def _refresh_disks(self) -> None:
        for combo in [self.source_combo, self.target_combo, self.boot_combo]:
            combo.clear()
        self.disk_table.setRowCount(len(self.disks))
        for row, disk in enumerate(self.disks):
            self.disk_table.setItem(row, 0, QTableWidgetItem(f"Disk {disk.number}"))
            self.disk_table.setItem(row, 1, QTableWidgetItem(human_bytes(disk.size_bytes)))
            self.disk_table.setItem(row, 2, QTableWidgetItem(disk.bus_type.value))
            self.disk_table.setItem(row, 3, QTableWidgetItem(disk.friendly_name))
            self.disk_table.setItem(row, 4, QTableWidgetItem(disk.serial or "-"))
            self.disk_table.setItem(row, 5, QTableWidgetItem(human_bytes(disk.used_bytes)))
            label = f"Disk {disk.number} - {disk.friendly_name} - {human_bytes(disk.size_bytes)}"
            self.source_combo.addItem(label, disk.number)
            self.target_combo.addItem(label, disk.number)
            self.boot_combo.addItem(label, disk.number)
        if len(self.disks) > 1:
            self.source_combo.setCurrentIndex(0)
            self.target_combo.setCurrentIndex(1)

    def _refresh_dashboard(self) -> None:
        startup_state = self.cached_startup_status.get("state", "bilinmiyor")
        startup_message = self.cached_startup_status.get("message", "Startup durumu henuz raporlanmadi.")
        lines = [
            "CigerTool by hkannq durum ozeti",
            "",
            f"Tespit edilen disk sayisi: {len(self.disks)}",
            f"ISO kutuphanesi sayisi: {len(self.cached_isos)}",
            f"Arac sayisi: {len(self.cached_tools)}",
            f"Startup durumu: {startup_state}",
            f"Startup notu: {startup_message}",
            "Odak senaryo: buyuk HDD -> kucuk SSD Smart Clone",
            "Runtime: canli ortam kabugu + otomatik uygulama baslatma",
            "Multiboot: /isos/windows, /isos/linux ve /isos/tools klasorleri taranir.",
            "Not: Smart Clone dosya-bazli tasima + resize + boot fix mantigi ile planlanir.",
        ]
        self.dashboard_summary.setText("\n".join(lines))

    def analyze_clone(self) -> None:
        source = self._selected_disk(self.source_combo)
        target = self._selected_disk(self.target_combo)
        if source is None or target is None:
            QMessageBox.warning(self, "Eksik Secim", "Kaynak ve hedef disk secilmeli.")
            return
        try:
            analysis = self.context.clone_service.analyze(source, target)
            mode = self._selected_mode()
            self.current_plan = self.context.clone_service.build_plan(analysis, mode)
        except Exception as exc:
            self.current_plan = None
            self.clone_summary.setText(str(exc))
            self.clone_recommendation.setText("")
            self.run_button.setEnabled(False)
            self._show_error("Clone Analizi", str(exc))
            return

        assert self.current_plan is not None
        recommended_map = {
            CloneMode.SMART: "SMART CLONE",
            CloneMode.RAW: "RAW CLONE",
            CloneMode.SYSTEM: "SYSTEM CLONE",
        }
        recommended_text = recommended_map.get(analysis.recommended_mode) if analysis.recommended_mode else "Yok"
        selected_text = recommended_map.get(mode, mode.value.upper())
        self.clone_recommendation.setText(
            f"Onerilen yontem: {recommended_text} | Secilen: {selected_text} | "
            f"Hedef kapasite: {human_bytes(analysis.target_usable_bytes)}"
        )
        lines = [self.current_plan.summary, "", "Analiz:"]
        lines.append(f"- Kaynakta kullanilan veri: {human_bytes(analysis.source_used_bytes)}")
        lines.append(f"- System Clone gereksinimi: {human_bytes(analysis.required_system_bytes)}")
        lines.append(f"- Smart Clone gereksinimi: {human_bytes(analysis.required_smart_bytes)}")
        lines.append("")
        lines.append("Uyarilar:")
        lines.extend(f"- {item}" for item in self.current_plan.warnings)
        lines.append("")
        lines.append("Adimlar:")
        lines.extend(f"{index}. {step.title}" for index, step in enumerate(self.current_plan.steps, start=1))
        self.clone_summary.setText("\n".join(lines))
        self.run_button.setEnabled(True)

    def run_clone(self) -> None:
        if not self.current_plan:
            return
        confirm = QMessageBox.question(
            self,
            "Son Onay",
            "Hedef diskteki veri silinebilir. Clone islemini baslatmak istiyor musunuz?",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self.context.runner.dry_run = self.dry_run.isChecked()
        self.run_button.setEnabled(False)
        self.clone_progress.show()
        self.clone_log.clear()
        signals = self.task_runner.submit(
            lambda emit: self.context.execution_service.run_plan(self.current_plan, callback=emit)
        )
        signals.message.connect(self.clone_log.append)
        signals.failed.connect(self._clone_failed)
        signals.finished.connect(self._clone_finished)

    def _clone_failed(self, message: str) -> None:
        self.clone_progress.hide()
        self.run_button.setEnabled(True)
        self.clone_log.append(f"HATA: {message}")
        self._show_error("Clone Hatasi", message)

    def _clone_finished(self) -> None:
        self.clone_progress.hide()
        self.run_button.setEnabled(True)
        self.clone_log.append("Islem tamamlandi. Gerekirse Boot Repair ekranini kullanin.")

    def prepare_boot_fix(self) -> None:
        disk = self._selected_disk(self.boot_combo)
        if disk is None:
            return
        steps = self.context.boot_service.plan(disk)
        text = "\n".join(
            f"- {step.title}: {' '.join(step.command) if isinstance(step.command, list) else step.command}"
            for step in steps
        )
        self.boot_output.setText(text)

    def preview_file(self) -> None:
        path = Path(self.file_model.filePath(self.file_tree.currentIndex()))
        if path.is_file():
            try:
                self.file_preview.setText(path.read_text(encoding="utf-8", errors="replace")[:20000])
            except Exception as exc:
                self.file_preview.setText(str(exc))

    def _set_file_browser_root(self, root_path: str) -> None:
        path = Path(root_path)
        if not path.exists():
            return
        self.file_model.setRootPath(str(path))
        self.file_tree.setRootIndex(self.file_model.index(str(path)))

    def _selected_disk(self, combo: QComboBox) -> Disk | None:
        data = combo.currentData()
        return self.context.disk_service.find_disk(self.disks, int(data)) if data is not None else None

    def _selected_mode(self) -> CloneMode:
        text = self.mode_combo.currentText()
        if text.startswith("RAW"):
            return CloneMode.RAW
        if text.startswith("SYSTEM"):
            return CloneMode.SYSTEM
        return CloneMode.SMART

    def _load_snapshot(self) -> dict[str, Any]:
        disks = self.context.disk_service.scan_disks()
        return {
            "disks": disks,
            "tools": self.context.tools_service.list_tools(),
            "isos": self.context.multiboot_service.scan_isos(self.context.system_service.iso_roots()),
            "smart": self.context.smart_service.snapshot(),
            "log": tail_log(),
            "startup_status": self.context.system_service.read_runtime_status(),
            "is_winpe": self.context.system_service.is_winpe(),
            "runtime_mode": self.context.system_service.runtime_mode(),
            "runtime_root": str(self.context.system_service.runtime_root()),
            "scripts_root": str(self.context.system_service.scripts_root()),
            "log_path": str(self.context.system_service.log_path()),
            "log_root": str(self.context.system_service.log_root()),
            "runtime_status_path": str(self.context.system_service.runtime_status_path()),
            "browser_root": str(self.context.system_service.default_file_browser_root()),
            "adk_installed": self.context.system_service.adk_installed(),
            "tool_roots": [str(path) for path in self.context.system_service.tool_roots()],
            "iso_roots": [str(path) for path in self.context.system_service.iso_roots()],
        }

    def _apply_snapshot(self, snapshot: dict[str, Any]) -> None:
        self.disks = snapshot["disks"]
        self.cached_tools = snapshot["tools"]
        self.cached_isos = snapshot["isos"]
        self.cached_startup_status = snapshot.get("startup_status", {}) or {}
        self._refresh_disks()
        self._refresh_dashboard()
        self._refresh_tools_from_items(self.cached_tools)
        self._refresh_multiboot_from_items(self.cached_isos)
        self._refresh_benchmark_from_tools(self.cached_tools)
        self._refresh_settings(snapshot)
        self._set_file_browser_root(snapshot["browser_root"])
        self.smart_output.setText(str(snapshot["smart"]))
        self.log_view.setText(snapshot["log"])
        runtime_labels = {
            "liveos": "Canli Ortam",
            "winpe": "Gecis Katmani",
            "windows": "Windows",
        }
        runtime_text = runtime_labels.get(snapshot["runtime_mode"], snapshot["runtime_mode"])
        self.winpe_label.setText(
            f"Ortam: {runtime_text} | "
            f"Log: {Path(snapshot['log_path']).name}"
        )
        self._maybe_show_startup_warning()
        if self.nav.currentRow() < 0:
            self.nav.setCurrentRow(0)

    def _refresh_tools_from_items(self, tools: list[ToolEntry]) -> None:
        self.tools_table.setRowCount(len(tools))
        for row, tool in enumerate(tools):
            self.tools_table.setItem(row, 0, QTableWidgetItem(tool.name))
            self.tools_table.setItem(row, 1, QTableWidgetItem(tool.layer))
            self.tools_table.setItem(row, 2, QTableWidgetItem(tool.category))
            self.tools_table.setItem(row, 3, QTableWidgetItem("Hazir" if tool.is_launchable else "Bekleniyor"))
            self.tools_table.setItem(row, 4, QTableWidgetItem(tool.source_root or "-"))
            self.tools_table.setItem(row, 5, QTableWidgetItem(tool.description))
        self._update_tool_details()

    def _refresh_multiboot_from_items(self, isos: list[IsoEntry]) -> None:
        self.iso_table.setRowCount(len(isos))
        for row, item in enumerate(isos):
            self.iso_table.setItem(row, 0, QTableWidgetItem(item.name))
            self.iso_table.setItem(row, 1, QTableWidgetItem(item.status_label))
            self.iso_table.setItem(row, 2, QTableWidgetItem(item.library_label))
            self.iso_table.setItem(row, 3, QTableWidgetItem(item.category.value))
            self.iso_table.setItem(row, 4, QTableWidgetItem(item.profile.value))
            self.iso_table.setItem(row, 5, QTableWidgetItem(item.boot_strategy.value))
            self.iso_table.setItem(row, 6, QTableWidgetItem(human_bytes(item.size_bytes)))
            self.iso_table.setItem(row, 7, QTableWidgetItem(item.path))
        self._update_iso_details()

    def _refresh_benchmark_from_tools(self, tools: list[ToolEntry]) -> None:
        benchmarks = [tool for tool in tools if tool.category == "Benchmark"]
        lines = [
            "Benchmark ozeti",
            "",
            f"Bulunan benchmark araci: {len(benchmarks)}",
        ]
        for tool in benchmarks:
            lines.append(f"- {tool.name}: {'Hazir' if tool.launch_path else 'Eksik'}")
        if not benchmarks:
            lines.append("- Benchmark araci bulunamadi. /tools altina eklenebilir.")
        self.benchmark_summary.setText("\n".join(lines))

    def _refresh_settings(self, snapshot: dict[str, Any]) -> None:
        lines = [
            "CigerTool ayar ve ortam ozeti",
            "",
            f"Runtime modu: {snapshot['runtime_mode']}",
            f"Runtime koku: {snapshot['runtime_root']}",
            f"Operasyon scriptleri: {snapshot['scripts_root']}",
            f"Startup durum dosyasi: {snapshot['runtime_status_path']}",
            f"Log dosyasi: {snapshot['log_path']}",
            f"Log kok dizini: {snapshot['log_root']}",
            f"Dosya yoneticisi koku: {snapshot['browser_root']}",
            "",
            f"WinPE: {'Evet' if snapshot['is_winpe'] else 'Hayir'}",
            f"ADK kurulu: {'Evet' if snapshot['adk_installed'] else 'Hayir'}",
            "",
            f"Startup state: {self.cached_startup_status.get('state', '-')}",
            f"Startup stage: {self.cached_startup_status.get('stage', '-')}",
            f"Startup mesaj: {self.cached_startup_status.get('message', '-')}",
            "",
            "Tool roots:",
            *[f"- {item}" for item in snapshot["tool_roots"]],
            "",
            "ISO roots:",
            *[f"- {item}" for item in snapshot["iso_roots"]],
            "",
            f"Legacy kutuphane: {LEGACY_ISO_LIBRARY_ROOT}",
        ]
        self.settings_summary.setText("\n".join(lines))

    def _refresh_failed(self, message: str) -> None:
        self._show_error("Disk Tarama Hatasi", message)

    def _set_refresh_state(self, busy: bool) -> None:
        self.refresh_progress.setVisible(busy)
        self.refresh_button.setEnabled(not busy)
        self.refresh_action.setEnabled(not busy)
        self.analyze_button.setEnabled(not busy)
        self.boot_button.setEnabled(not busy)
        self.benchmark_launch.setEnabled(not busy)
        self.tools_launch_button.setEnabled(not busy)
        self.tools_folder_button.setEnabled(not busy)
        self.log_refresh_button.setEnabled(not busy)
        self.log_folder_button.setEnabled(not busy)

    def _show_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)

    def _maybe_show_startup_warning(self) -> None:
        state = str(self.cached_startup_status.get("state", "")).lower()
        message = str(self.cached_startup_status.get("message", "")).strip()
        warning_key = f"{state}|{message}"
        if warning_key == self._last_startup_warning_key:
            return
        if state not in {"degraded", "failed"} or not message:
            return
        self._last_startup_warning_key = warning_key
        QMessageBox.warning(
            self,
            "Startup Uyarisi",
            f"Canli oturum acildi ancak startup tam saglikli degil.\n\n{message}",
        )

    def _update_iso_details(self) -> None:
        row = self.iso_table.currentRow()
        if row < 0 or row >= len(self.cached_isos):
            self.iso_details.setText("Bir ISO secildiginde profil, notlar ve boot stratejisi burada gorunur.")
            return
        item = self.cached_isos[row]
        lines = [
            f"ISO: {item.name}",
            f"Durum: {item.status_label}",
            f"Kutuphane bolumu: {item.library_label}",
            f"Kategori: {item.category.value}",
            f"Profil: {item.profile.value}",
            f"Boot stratejisi: {item.boot_strategy.value}",
            f"Boyut: {human_bytes(item.size_bytes)}",
            f"Yol: {item.path}",
        ]
        if item.source_root:
            lines.append(f"Kaynak kok: {item.source_root}")
        if item.relative_path:
            lines.append(f"Goreli yol: {item.relative_path}")
        if item.failure_reason:
            lines.append(f"Boot hatasi sebebi: {item.failure_reason}")
        if item.kernel_path:
            lines.append(f"Kernel: {item.kernel_path}")
        if item.initrd_path:
            lines.append(f"Initrd: {item.initrd_path}")
        if item.efi_boot_path:
            lines.append(f"EFI boot: {item.efi_boot_path}")
        if item.companion_config:
            lines.append(f"Ozel config: {item.companion_config}")
        if item.notes:
            lines.append("")
            lines.append("Notlar:")
            lines.extend(f"- {note}" for note in item.notes)
        self.iso_details.setText("\n".join(lines))

    def launch_selected_tool(self) -> None:
        tool = self._selected_tool()
        if tool is None:
            self._show_error("Arac Kutusu", "Lutfen bir arac secin.")
            return
        if tool.internal_page:
            page_index = self.internal_tool_pages.get(tool.internal_page)
            if page_index is None:
                self._show_error("Arac Kutusu", f"Tanimli olmayan uygulama ici hedef: {tool.internal_page}")
                return
            self.nav.setCurrentRow(page_index)
            return
        if not tool.is_launchable:
            self._show_error("Arac Kutusu", "Secilen arac icin calistirilabilir dosya bulunamadi.")
            return
        try:
            self.context.tool_launcher_service.launch(tool)
        except Exception as exc:
            self._show_error("Arac Kutusu", str(exc))

    def open_log_directory(self) -> None:
        try:
            subprocess.Popen(
                ["explorer.exe", str(self.context.system_service.log_root())],
                cwd=str(self.context.system_service.runtime_root()),
            )
        except Exception as exc:
            self._show_error("Loglar", str(exc))

    def launch_benchmark_tool(self) -> None:
        tool = next((item for item in self.cached_tools if item.category == "Benchmark" and item.launch_path), None)
        if not tool:
            self._show_error("Benchmark", "Calistirilabilir benchmark araci bulunamadi.")
            return
        try:
            self.context.tool_launcher_service.launch(tool)
        except Exception as exc:
            self._show_error("Benchmark", str(exc))

    def open_selected_tool_directory(self) -> None:
        tool = self._selected_tool()
        if tool is None:
            self._show_error("Arac Kutusu", "Lutfen bir arac secin.")
            return
        try:
            if tool.internal_page:
                self._show_error("Arac Kutusu", "Uygulama ici araclarin ayri bir klasoru yoktur.")
                return
            self.context.tool_launcher_service.open_tool_directory(tool)
        except Exception as exc:
            self._show_error("Arac Kutusu", str(exc))

    def _selected_tool(self) -> ToolEntry | None:
        row = self.tools_table.currentRow()
        if row < 0 or row >= len(self.cached_tools):
            return None
        return self.cached_tools[row]

    def _update_tool_details(self) -> None:
        tool = self._selected_tool()
        if tool is None:
            self.tool_details.setText("Bir arac secildiginde launcher ayrintilari burada gorunur.")
            return

        launch_target = tool.internal_page if tool.internal_page else (tool.launch_path or "Bulunamadi")
        lines = [
            f"Arac: {tool.name}",
            f"Katman: {tool.layer}",
            f"Kategori: {tool.category}",
            f"Durum: {'Hazir' if tool.is_launchable else 'Eksik'}",
            f"Kaynak kok: {tool.source_root or '-'}",
            f"Calistirma hedefi: {launch_target}",
            f"Calisma dizini: {tool.working_directory or '-'}",
            f"Manifest: {tool.manifest_path or '-'}",
            "",
            tool.description,
        ]
        if tool.launch_args:
            lines.insert(7, f"Argumanlar: {' '.join(tool.launch_args)}")
        if tool.internal_page:
            lines.append("")
            lines.append("Bu giris, uygulama ici bir araca yonlendirir.")
        self.tool_details.setText("\n".join(lines))

    def _launch_path(self, path: str | None) -> None:
        if not path:
            self._show_error("Calistirma Hatasi", "Calistirilacak yol bulunamadi.")
            return
        try:
            working_directory = str(self.context.system_service.runtime_root())
            if Path(path).exists():
                subprocess.Popen([path], cwd=working_directory)
            else:
                subprocess.Popen(path, cwd=working_directory)
        except Exception as exc:
            self._show_error("Calistirma Hatasi", str(exc))
