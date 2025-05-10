# gui.py

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget, QFileDialog, QMessageBox
)
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt

from constants import (
    SIDEBAR_STYLE, HEADER_STYLE, CONTENT_STYLE,
    SIDEBAR_WIDTH, HEADER_HEIGHT, HEADER_COLOR, TEXT_COLOR,
    SCREEN_HOME, SCREEN_SCAN, SCREEN_ALERT, SCREEN_LOGS, SCREEN_SETTINGS
)
from ui_frames import HomeFrame, ScanFrame, AlertFrame, LogsFrame, SettingsFrame
from scan_worker import ScanWorker

class MainWindow(QMainWindow):
    def __init__(self, config, db_manager):
        super().__init__()
        self.setWindowTitle("BlackICE Antivirus")
        self.resize(1000, 700)
        self.config = config
        self.db     = db_manager

        central = QWidget(self)
        self.setCentralWidget(central)
        central.setStyleSheet(CONTENT_STYLE)

        sidebar = QWidget()
        sidebar.setFixedWidth(SIDEBAR_WIDTH)
        sidebar.setStyleSheet(SIDEBAR_STYLE)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0,0,0,0)
        sb_layout.setSpacing(10)

        self.btn_home     = QPushButton("Home")
        self.btn_scan     = QPushButton("Scan")
        self.btn_alert    = QPushButton("Alert")
        self.btn_logs     = QPushButton("Logs")
        self.btn_settings = QPushButton("Settings")
        for btn in (self.btn_home,self.btn_scan,self.btn_alert,self.btn_logs,self.btn_settings):
            btn.setFixedHeight(50)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            sb_layout.addWidget(btn)
        sb_layout.addStretch()

        header = QWidget(self)
        header.setFixedHeight(HEADER_HEIGHT)
        header.setStyleSheet(f"background:{HEADER_COLOR};")
        lbl = QPushButton("BlackICE", header)
        lbl.setEnabled(False)
        lbl.setStyleSheet(f"color:{TEXT_COLOR};font-size:20px;border:none;")
        lbl.move(15,(HEADER_HEIGHT-24)//2)

        self.stack = QStackedWidget()
        self.frames = {
            SCREEN_HOME:     HomeFrame(),
            SCREEN_SCAN:     ScanFrame(self.db,self.config),
            SCREEN_ALERT:    AlertFrame(self.db),
            SCREEN_LOGS:     LogsFrame(self.db),
            SCREEN_SETTINGS: SettingsFrame(self.config),
        }
        for f in self.frames.values():
            self.stack.addWidget(f)

        content = QHBoxLayout()
        content.setContentsMargins(0,0,0,0)
        content.addWidget(sidebar)
        content.addWidget(self.stack,1)

        main = QVBoxLayout(central)
        main.setContentsMargins(0,0,0,0)
        main.addWidget(header)
        main.addLayout(content)

        self.btn_home.clicked.connect(lambda: self._switch(SCREEN_HOME))
        self.btn_scan.clicked.connect(lambda: self._switch(SCREEN_SCAN))
        self.btn_alert.clicked.connect(lambda: self._switch(SCREEN_ALERT))
        self.btn_logs.clicked.connect(lambda: self._switch(SCREEN_LOGS))
        self.btn_settings.clicked.connect(lambda: self._switch(SCREEN_SETTINGS))

        scan_frame = self.frames[SCREEN_SCAN]
        scan_frame.btn_file.clicked.connect(self._scan_file)
        scan_frame.btn_folder.clicked.connect(self._scan_folder)

        self.frames[SCREEN_SETTINGS].save_btn.clicked.connect(self._save_settings)

        self._switch(SCREEN_HOME)

    def _switch(self, screen):
        idx = list(self.frames).index(screen)
        self.stack.setCurrentIndex(idx)
        if screen==SCREEN_LOGS:
            self.frames[SCREEN_LOGS].refresh()
        if screen==SCREEN_ALERT:
            self.frames[SCREEN_ALERT].load_alerts()

    def _scan_file(self):
        path,_=QFileDialog.getOpenFileName(self,"Select File")
        if path: self._start_scan(path)

    def _scan_folder(self):
        path=QFileDialog.getExistingDirectory(self,"Select Folder")
        if path: self._start_scan(path)

    def _start_scan(self,target):
        scan_id=self.db.start_scan(target)
        sf=self.frames[SCREEN_SCAN]; af=self.frames[SCREEN_ALERT]
        sf.log.clear(); sf.progress.setValue(0); af.tree.clear()

        w=ScanWorker(target,self.config.get("vt_api_key",""))
        w.log.connect(lambda m:(sf.log.append(m),self.db.add_log(m)))
        w.file_scanned.connect(lambda p,l:(af.add_alert(p,l),self.db.add_alert(scan_id,p,l)))
        w.finished.connect(lambda:(self.db.finish_scan(scan_id),QMessageBox.information(self,"Scan","Completed"),self._switch(SCREEN_ALERT)))
        self._worker=w; w.start()

    def _save_settings(self):
        k=self.frames[SCREEN_SETTINGS].api_input.text().strip()
        self.config.set("vt_api_key",k)
        QMessageBox.information(self,"Settings","API key saved.")

if __name__=="__main__":
    from PySide6.QtWidgets import QApplication
    from config import ConfigManager
    from db_manager import DatabaseManager
    app=QApplication(sys.argv)
    win=MainWindow(ConfigManager(),DatabaseManager())
    win.show()
    sys.exit(app.exec())
