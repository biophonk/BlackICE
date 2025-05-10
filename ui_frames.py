# ui_frames.py

from PySide6 import QtWidgets, QtGui, QtCore
from constants import CONTENT_STYLE, TEXT_COLOR, COLOR_HIGH, COLOR_MEDIUM, COLOR_LOW, COLOR_UNKNOWN, COLOR_CLEAN

class HomeFrame(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(CONTENT_STYLE)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(15)

        title = QtWidgets.QLabel("BlackICE")
        title.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        title.setStyleSheet(f"color:{TEXT_COLOR};font-size:32px;font-weight:bold;")
        layout.addWidget(title)

        desc = QtWidgets.QLabel("Scanning and Detecting")
        desc.setWordWrap(True)
        desc.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        desc.setStyleSheet(f"color:{TEXT_COLOR};font-size:18px;")
        layout.addWidget(desc)

        layout.addStretch()


class ScanFrame(QtWidgets.QWidget):
    def __init__(self, db_manager, config):
        super().__init__()
        self.db = db_manager
        self.config = config
        self.setStyleSheet(CONTENT_STYLE)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(10)

        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_file = QtWidgets.QPushButton("Scan File")
        self.btn_folder = QtWidgets.QPushButton("Scan Folder")
        for btn in (self.btn_file, self.btn_folder):
            btn.setFixedHeight(40)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            btn.setStyleSheet(f"color:{TEXT_COLOR};font-size:14px;border:1px solid {TEXT_COLOR};border-radius:5px;")
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)

        self.progress = QtWidgets.QProgressBar()
        layout.addWidget(self.progress)

        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet(f"background:#1e1e1e;color:{TEXT_COLOR};")
        layout.addWidget(self.log)


class AlertFrame(QtWidgets.QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setStyleSheet(CONTENT_STYLE)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(10)

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Path", "Level"])
        hdr = self.tree.header()
        hdr.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)           # Path stretches
        hdr.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)             # Level fixed width
        hdr.resizeSection(1, 24)                                              # 24px for the color square
        layout.addWidget(self.tree)

    def add_alert(self, path: str, level: str):
        item = QtWidgets.QTreeWidgetItem([path, ""])
        item.setTextAlignment(0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        color_map = {
            "High":    COLOR_HIGH,
            "Medium":  COLOR_MEDIUM,
            "Low":     COLOR_LOW,
            "Unknown": COLOR_UNKNOWN,
            "Clean":   COLOR_CLEAN,
        }
        badge = QtWidgets.QLabel()
        badge.setFixedSize(16,16)
        badge.setStyleSheet(f"background:{color_map.get(level,'#888')};border-radius:2px;")
        self.tree.addTopLevelItem(item)
        self.tree.setItemWidget(item,1,badge)

    def load_alerts(self):
        self.tree.clear()
        for rec in self.db.get_alerts():
            self.add_alert(rec["path"], rec["level"])


class LogsFrame(QtWidgets.QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setStyleSheet(CONTENT_STYLE)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(10)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID","Timestamp","Path","Result"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.table)

    def refresh(self):
        recs = self.db.get_scan_logs()
        self.table.setRowCount(len(recs))
        for i, r in enumerate(recs):
            self.table.setItem(i,0,QtWidgets.QTableWidgetItem(str(r["id"])))
            self.table.setItem(i,1,QtWidgets.QTableWidgetItem(r["start_time"]))
            self.table.setItem(i,2,QtWidgets.QTableWidgetItem(r["path"]))
            self.table.setItem(i,3,QtWidgets.QTableWidgetItem(r.get("result","")))


class SettingsFrame(QtWidgets.QWidget):
    def __init__(self, config_manager):
        super().__init__()
        self.cfg = config_manager
        self.setStyleSheet(CONTENT_STYLE)

        layout = QtWidgets.QFormLayout(self)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(10)

        self.api_input = QtWidgets.QLineEdit(self.cfg.get("vt_api_key",""))
        self.api_input.setStyleSheet(f"color:{TEXT_COLOR};font-size:14px;")
        layout.addRow("VirusTotal API Key:", self.api_input)

        self.save_btn = QtWidgets.QPushButton("Save Settings")
        self.save_btn.setFixedHeight(35)
        self.save_btn.setStyleSheet(f"color:{TEXT_COLOR};font-size:14px;border:1px solid {TEXT_COLOR};border-radius:5px;")
        layout.addRow(self.save_btn)
        self.save_btn.clicked.connect(self.save)

    def save(self):
        self.cfg.set("vt_api_key", self.api_input.text())
