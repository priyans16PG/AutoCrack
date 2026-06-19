"""
Theme and styling for the GUI
"""
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt


class Theme:
    """Application theme colors and styles"""
    
    # Colors
    BG_PRIMARY = QColor("#1e1e1e")      # Dark background
    BG_SECONDARY = QColor("#2d2d2d")    # Slightly lighter background
    BG_TERTIARY = QColor("#3d3d3d")     # Even lighter background
    
    ACCENT_PRIMARY = QColor("#ff3333")  # Red accent
    ACCENT_SECONDARY = QColor("#ff6666") # Light red
    ACCENT_DARK = QColor("#cc0000")     # Dark red
    
    TEXT_PRIMARY = QColor("#ffffff")    # White text
    TEXT_SECONDARY = QColor("#b0b0b0")  # Gray text
    TEXT_DISABLED = QColor("#707070")   # Disabled text
    
    SUCCESS = QColor("#00cc00")         # Green for success
    WARNING = QColor("#ffcc00")         # Yellow for warning
    ERROR = QColor("#ff3333")           # Red for error
    INFO = QColor("#3399ff")            # Blue for info
    
    BORDER = QColor("#404040")          # Border color
    
    # Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_MONO = "Courier New"
    
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_LARGE = 12
    FONT_SIZE_XLARGE = 14
    FONT_SIZE_SMALL = 9
    
    # Border radius
    BORDER_RADIUS = 8
    BORDER_RADIUS_SMALL = 4


def get_stylesheet():
    """Get complete stylesheet for the application"""
    return """
    QWidget {
        background-color: #1e1e1e;
        color: #ffffff;
        font-family: 'Segoe UI';
        font-size: 10px;
    }
    
    QMainWindow {
        background-color: #1e1e1e;
        border: 1px solid #404040;
    }
    
    QLabel {
        color: #ffffff;
    }
    
    QLineEdit {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #404040;
        border-radius: 4px;
        padding: 6px;
        selection-background-color: #ff3333;
    }
    
    QLineEdit:focus {
        border: 2px solid #ff3333;
    }
    
    QPushButton {
        background-color: #ff3333;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 11px;
    }
    
    QPushButton:hover {
        background-color: #ff6666;
    }
    
    QPushButton:pressed {
        background-color: #cc0000;
    }
    
    QPushButton:disabled {
        background-color: #606060;
        color: #808080;
    }
    
    QComboBox {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #404040;
        border-radius: 4px;
        padding: 6px;
    }
    
    QComboBox:focus {
        border: 2px solid #ff3333;
    }
    
    QComboBox::drop-down {
        border: none;
        padding-right: 10px;
    }
    
    QComboBox::down-arrow {
        image: none;
        width: 0px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #2d2d2d;
        color: #ffffff;
        selection-background-color: #ff3333;
        border: 1px solid #404040;
    }
    
    QSpinBox, QDoubleSpinBox {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #404040;
        border-radius: 4px;
        padding: 4px;
    }
    
    QSpinBox::up-button, QDoubleSpinBox::up-button {
        border: none;
        background-color: #3d3d3d;
    }
    
    QSpinBox::down-button, QDoubleSpinBox::down-button {
        border: none;
        background-color: #3d3d3d;
    }
    
    QProgressBar {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 4px;
        text-align: center;
        color: #ffffff;
        height: 24px;
    }
    
    QProgressBar::chunk {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                         stop:0 #ff3333, 
                                         stop:1 #ff6666);
        border-radius: 2px;
    }
    
    QTextEdit {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 1px solid #404040;
        border-radius: 4px;
        padding: 8px;
    }
    
    QPlainTextEdit {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 1px solid #404040;
        border-radius: 4px;
        padding: 8px;
    }
    
    QScrollBar:vertical {
        background-color: #2d2d2d;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #505050;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #ff3333;
    }
    
    QScrollBar:horizontal {
        background-color: #2d2d2d;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #505050;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #ff3333;
    }
    
    QGroupBox {
        color: #ffffff;
        border: 1px solid #404040;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 10px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px 0 3px;
    }
    
    QTabWidget::pane {
        border: 1px solid #404040;
    }
    
    QTabBar::tab {
        background-color: #2d2d2d;
        color: #ffffff;
        padding: 8px 20px;
        border: 1px solid #404040;
        border-bottom: none;
        margin-right: 2px;
    }
    
    QTabBar::tab:selected {
        background-color: #ff3333;
    }
    
    QDialog {
        background-color: #1e1e1e;
    }
    
    QCheckBox {
        color: #ffffff;
        spacing: 5px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
    }
    
    QCheckBox::indicator:unchecked {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 3px;
    }
    
    QCheckBox::indicator:checked {
        background-color: #ff3333;
        border: 1px solid #ff3333;
        border-radius: 3px;
    }
    
    QRadioButton {
        color: #ffffff;
        spacing: 5px;
    }
    
    QRadioButton::indicator {
        width: 18px;
        height: 18px;
    }
    
    QRadioButton::indicator:unchecked {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 9px;
    }
    
    QRadioButton::indicator:checked {
        background-color: #ff3333;
        border: 1px solid #ff3333;
        border-radius: 9px;
    }
    
    QMenuBar {
        background-color: #2d2d2d;
        color: #ffffff;
        border-bottom: 1px solid #404040;
    }
    
    QMenuBar::item:selected {
        background-color: #ff3333;
    }
    
    QMenu {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #404040;
    }
    
    QMenu::item:selected {
        background-color: #ff3333;
    }
    """


def get_font(size=Theme.FONT_SIZE_NORMAL, bold=False, family=Theme.FONT_FAMILY):
    """Get a QFont with specified properties"""
    font = QFont(family, size)
    font.setBold(bold)
    return font


def get_mono_font(size=Theme.FONT_SIZE_NORMAL, bold=False):
    """Get a monospace QFont"""
    return get_font(size, bold, Theme.FONT_MONO)
