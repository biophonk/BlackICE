import sys
import os
import ctypes

from PySide6.QtCore import QLibraryInfo
from PySide6.QtWidgets import QApplication

from constants import WINDOW_STYLE, SIDEBAR_STYLE, HEADER_STYLE, CONTENT_STYLE
from config import ConfigManager
from db_manager import DatabaseManager
from gui import MainWindow

def _get_short_path(path: str) -> str:
    buf = ctypes.create_unicode_buffer(260)
    ctypes.windll.kernel32.GetShortPathNameW(path, buf, len(buf))
    return buf.value

def main():
    # 1) Путь к Qt-плагинам
    try:
        plugins_dir = QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)
    except AttributeError:
        plugins_dir = QLibraryInfo.location(QLibraryInfo.PluginsPath)
    try:
        plugins_dir = _get_short_path(plugins_dir)
    except Exception:
        pass
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugins_dir

    # 2) Запуск приложения
    app = QApplication(sys.argv)
    app.setStyleSheet(WINDOW_STYLE + SIDEBAR_STYLE + HEADER_STYLE + CONTENT_STYLE)

    cfg = ConfigManager()
    db  = DatabaseManager(cfg.get("db_path"))

    window = MainWindow(config=cfg, db_manager=db)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
