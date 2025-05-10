from PySide6.QtGui import QColor

# Цвета
BACKGROUND_COLOR   = "#242424"  # rgb(36,36,36)
SIDEBAR_COLOR      = "#141414"  # rgb(20,20,20)
HEADER_COLOR       = "#141414"  # rgb(20,20,20)
TEXT_COLOR         = "#FFFFFF"  # rgb(255,255,255)

TREE_BG_COLOR      = "#1e1e1e"
BUTTON_HOVER_COLOR = "#1e1e1e"
PROGRESS_BG_COLOR  = "#1e1e1e"
PROGRESS_BORDER    = "#555"

COLOR_HIGH         = "#d90000"  # rgb(217,0,0)
COLOR_MEDIUM       = "#e39b00"  # rgb(227,155,0)
COLOR_LOW          = "#f2e401"  # rgb(242,228,1)
COLOR_UNKNOWN      = "#00bdf2"  # rgb(0,189,242)
COLOR_CLEAN        = "#23f200"  # rgb(35,242,0)

LEVEL_COLORS = {
    "High":    COLOR_HIGH,
    "Medium":  COLOR_MEDIUM,
    "Low":     COLOR_LOW,
    "Unknown": COLOR_UNKNOWN,
    "Clean":   COLOR_CLEAN,
}

PALETTE = {
    "background": QColor(BACKGROUND_COLOR),
    "sidebar":    QColor(SIDEBAR_COLOR),
    "header":     QColor(HEADER_COLOR),
    "text":       QColor(TEXT_COLOR),
}

# Экраны
SCREEN_HOME     = "Home"
SCREEN_SCAN     = "Scan"
SCREEN_ALERT    = "Alert"
SCREEN_LOGS     = "Logs"
SCREEN_SETTINGS = "Settings"

# Размеры
SIDEBAR_WIDTH = 120
HEADER_HEIGHT = 50

# Стили
WINDOW_STYLE = f"""
QMainWindow {{ background-color: {BACKGROUND_COLOR}; }}
"""

SIDEBAR_STYLE = f"""
QFrame {{
  background-color: {SIDEBAR_COLOR};
}}
QPushButton {{
  color: {TEXT_COLOR};
  background: transparent;
  border: none;
  text-align: left;
  padding-left: 20px;
  font-size: 14px;
}}
QPushButton:hover {{ background-color: {BUTTON_HOVER_COLOR}; }}
QPushButton:checked {{ background-color: {COLOR_UNKNOWN}; }}
"""

HEADER_STYLE = f"""
QFrame {{ background-color: {HEADER_COLOR}; }}
QLabel {{
  color: {TEXT_COLOR};
  font-size: 18px;
  padding-left: 15px;
}}
"""

CONTENT_STYLE = f"""
QWidget {{
  background-color: {BACKGROUND_COLOR};
  color: {TEXT_COLOR};
}}
QTreeWidget, QTableWidget {{
  background-color: {TREE_BG_COLOR};
  color: {TEXT_COLOR};
  font-size: 12px;
}}
QProgressBar {{
  background-color: {PROGRESS_BG_COLOR};
  border: 1px solid {PROGRESS_BORDER};
  border-radius: 5px;
  text-align: center;
}}
QProgressBar::chunk {{
  background-color: {COLOR_UNKNOWN};
  border-radius: 5px;
}}
"""
