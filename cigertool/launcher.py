from __future__ import annotations

import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

from .app_context import create_context
from .config import APP_NAME, resolve_log_path
from .logger import get_logger
from .ui.main_window import MainWindow


def _show_fatal_dialog(message: str, details: str = "") -> None:
    dialog = QMessageBox()
    dialog.setIcon(QMessageBox.Icon.Critical)
    dialog.setWindowTitle(APP_NAME)
    dialog.setText(message)
    dialog.setInformativeText(f"Detaylar log dosyasina yazildi:\n{resolve_log_path()}")
    if details:
        dialog.setDetailedText(details)
    dialog.exec()


def _install_exception_hook() -> None:
    logger = get_logger()
    previous_hook = sys.excepthook

    def _hook(exc_type, exc_value, exc_traceback) -> None:
        rendered = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error("Beklenmeyen uygulama hatasi:\n%s", rendered)
        _show_fatal_dialog("CigerTool beklenmeyen bir hatayla karsilasti.", rendered)
        if previous_hook is not None:
            previous_hook(exc_type, exc_value, exc_traceback)

    sys.excepthook = _hook


def main() -> None:
    logger = get_logger()
    app = QApplication(sys.argv)
    app.setApplicationDisplayName(APP_NAME)
    _install_exception_hook()
    try:
        context = create_context()
        logger.info("CigerTool baslatiliyor | runtime=%s | log=%s", context.system_service.runtime_mode(), resolve_log_path())
        window = MainWindow(context)
        window.show()
    except Exception as exc:
        rendered = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        logger.error("Baslangic sirasinda kritik hata:\n%s", rendered)
        _show_fatal_dialog("CigerTool baslatilamadi.", rendered)
        sys.exit(1)
    sys.exit(app.exec())
