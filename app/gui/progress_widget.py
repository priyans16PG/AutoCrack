"""
Progress display widget
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QTextEdit, QGroupBox, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor, QFont, QColor
from gui.theme import Theme, get_font, get_mono_font
from core import utils


class ProgressWidget(QWidget):
    """Widget for displaying cracking progress"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_password = None  # Store password for copy
        self.setup_ui()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Progress bar
        progress_group = QGroupBox("Cracking Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 6px;
                text-align: center;
                background-color: #2d2d2d;
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff3333, stop:1 #ff6666);
                border-radius: 4px;
            }
        """)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QGridLayout()
        
        # Speed
        stats_layout.addWidget(QLabel("Speed:"), 0, 0)
        self.label_speed = QLabel("0 H/s")
        self.label_speed.setFont(get_font(Theme.FONT_SIZE_LARGE, bold=True))
        self.label_speed.setStyleSheet("color: #ff6666;")
        stats_layout.addWidget(self.label_speed, 0, 1)
        
        # ETA
        stats_layout.addWidget(QLabel("ETA:"), 0, 2)
        self.label_eta = QLabel("Calculating...")
        self.label_eta.setFont(get_font(Theme.FONT_SIZE_LARGE, bold=True))
        self.label_eta.setStyleSheet("color: #3399ff;")
        stats_layout.addWidget(self.label_eta, 0, 3)
        
        # GPU Temperature
        stats_layout.addWidget(QLabel("GPU Temp:"), 1, 0)
        self.label_temp = QLabel("N/A")
        self.label_temp.setFont(get_font(Theme.FONT_SIZE_LARGE, bold=True))
        self.label_temp.setStyleSheet("color: #ffcc00;")
        stats_layout.addWidget(self.label_temp, 1, 1)
        
        # GPU Utilization
        stats_layout.addWidget(QLabel("GPU Util:"), 1, 2)
        self.label_gpu_util = QLabel("0%")
        self.label_gpu_util.setFont(get_font(Theme.FONT_SIZE_LARGE, bold=True))
        self.label_gpu_util.setStyleSheet("color: #00cc00;")
        stats_layout.addWidget(self.label_gpu_util, 1, 3)
        
        # Progress percentage
        stats_layout.addWidget(QLabel("Progress:"), 2, 0)
        self.label_progress_pct = QLabel("0 / 0 (0%)")
        self.label_progress_pct.setFont(get_font(Theme.FONT_SIZE_LARGE, bold=True))
        self.label_progress_pct.setStyleSheet("color: #ff3333;")
        stats_layout.addWidget(self.label_progress_pct, 2, 1)
        
        # Current mask/mode
        stats_layout.addWidget(QLabel("Current:"), 2, 2)
        self.label_current = QLabel("-")
        self.label_current.setFont(get_font(Theme.FONT_SIZE_LARGE, bold=True))
        stats_layout.addWidget(self.label_current, 2, 3)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Password found section (hidden initially)
        self.password_group = QGroupBox("Password Found")
        password_layout = QHBoxLayout()
        self.label_password = QLabel("Waiting for password...")
        self.label_password.setFont(get_font(int(Theme.FONT_SIZE_LARGE * 1.5), bold=True))
        self.label_password.setStyleSheet("color: #00ff00; background-color: #1a3a1a; padding: 15px; border-radius: 4px;")
        password_layout.addWidget(self.label_password)
        
        # Copy button
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setFont(get_font(Theme.FONT_SIZE_NORMAL, bold=True))
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #00cc00;
                color: #000000;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00ff00;
            }
            QPushButton:pressed {
                background-color: #00aa00;
            }
        """)
        self.copy_btn.clicked.connect(self.copy_password)
        password_layout.addWidget(self.copy_btn)
        
        self.password_group.setLayout(password_layout)
        self.password_group.setVisible(False)  # Hidden until password found
        layout.addWidget(self.password_group)
        
        # Console output
        console_group = QGroupBox("Console Output")
        console_layout = QVBoxLayout()
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(get_mono_font(9))
        self.console.setMaximumHeight(150)
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a0a;
                color: #00ff00;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New';
                font-size: 9px;
            }
        """)
        console_layout.addWidget(self.console)
        console_group.setLayout(console_layout)
        layout.addWidget(console_group)
        
        self.setLayout(layout)
    
    def update_progress(self, current, total):
        """Update progress bar"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.label_progress_pct.setText(f"{current:,} / {total:,} ({percentage}%)")
    
    def update_speed(self, speed_str):
        """Update speed display"""
        self.label_speed.setText(speed_str)
    
    def update_eta(self, eta_str):
        """Update ETA display"""
        self.label_eta.setText(eta_str)
    
    def update_temperature(self, temp):
        """Update GPU temperature"""
        if temp is not None:
            self.label_temp.setText(f"{temp}°C")
    
    def update_gpu_util(self, util):
        """Update GPU utilization"""
        if util is not None:
            self.label_gpu_util.setText(f"{util}%")
    
    def update_current_mode(self, mode_str):
        """Update current mode/mask display"""
        self.label_current.setText(mode_str)
    
    def add_console_line(self, text, color=None):
        """Add a line to console output"""
        cursor = self.console.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        if color:
            fmt = cursor.charFormat()
            fmt.setForeground(QColor(color))
            cursor.setCharFormat(fmt)
        
        cursor.insertText(text + "\n")
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()
    
    def add_console_error(self, text):
        """Add error line to console"""
        self.add_console_line(text, "#ff3333")
    
    def add_console_success(self, text):
        """Add success line to console"""
        self.add_console_line(text, "#00cc00")
    
    def add_console_warning(self, text):
        """Add warning line to console"""
        self.add_console_line(text, "#ffcc00")
    
    def add_console_info(self, text):
        """Add info line to console"""
        self.add_console_line(text, "#3399ff")
    
    def set_password(self, password):
        """Display found password"""
        self.current_password = password
        self.label_password.setText(f"✓ PASSWORD: {password}")
        self.password_group.setVisible(True)
    
    def copy_password(self):
        """Copy password to clipboard"""
        if self.current_password:
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_password)
            
            # Show feedback
            self.copy_btn.setText("✓ Copied!")
            self.copy_btn.setStyleSheet("""
                QPushButton {
                    background-color: #00aa00;
                    color: #000000;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 20px;
                    font-weight: bold;
                }
            """)
            
            # Reset button text after 2 seconds
            QTimer.singleShot(2000, self.reset_copy_btn)
    
    def reset_copy_btn(self):
        """Reset copy button text"""
        self.copy_btn.setText("Copy")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #00cc00;
                color: #000000;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00ff00;
            }
            QPushButton:pressed {
                background-color: #00aa00;
            }
        """)
    
    def clear_console(self):
        """Clear console output"""
        self.console.clear()
    
    def reset_stats(self):
        """Reset all statistics"""
        self.progress_bar.setValue(0)
        self.label_speed.setText("0 H/s")
        self.label_eta.setText("Calculating...")
        self.label_temp.setText("N/A")
        self.label_gpu_util.setText("0%")
        self.label_progress_pct.setText("0 / 0 (0%)")
        self.label_current.setText("-")
        self.clear_console()
    
    def update_stats(self):
        """Update statistics (called periodically)"""
        pass  # Override in parent to implement actual updates
