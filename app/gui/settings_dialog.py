"""
Settings and attack configuration dialog
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QComboBox, QCheckBox, QPushButton, QGroupBox, QGridLayout,
    QFileDialog, QRadioButton, QButtonGroup, QMessageBox
)
from PyQt6.QtCore import Qt
from gui.theme import Theme, get_font
from core.cache import CacheManager
from pathlib import Path


class SettingsDialog(QDialog):
    """Dialog for configuring attack settings"""
    
    ATTACK_MODES = {
        '0': 'Dictionary (Wordlist)',
        '1': 'Combination',
        '3': 'Brute Force (Mask)',
        '6': 'Hybrid (Dict + Mask)',
        '7': 'Hybrid (Mask + Dict)',
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Attack Settings")
        self.setGeometry(100, 100, 500, 600)
        self.cache_manager = CacheManager()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout()
        
        # Attack Mode Selection
        attack_group = QGroupBox("Attack Mode")
        attack_layout = QVBoxLayout()
        
        self.attack_mode_group = QButtonGroup()
        self.attack_radios = {}
        
        for mode_id, mode_name in self.ATTACK_MODES.items():
            radio = QRadioButton(f"{mode_name} (Mode {mode_id})")
            self.attack_mode_group.addButton(radio, int(mode_id))
            self.attack_radios[mode_id] = radio
            attack_layout.addWidget(radio)
        
        # Select brute force by default
        self.attack_radios['3'].setChecked(True)
        attack_group.setLayout(attack_layout)
        layout.addWidget(attack_group)
        
        # Mask settings
        mask_group = QGroupBox("Mask Configuration")
        mask_layout = QGridLayout()
        
        mask_layout.addWidget(QLabel("Predefined Masks:"), 0, 0)
        self.mask_preset = QComboBox()
        self.mask_preset.addItem("Select Mask...", "")
        self.mask_preset.addItem("Numeric (?d)", "?d")
        self.mask_preset.addItem("Lowercase (?l)", "?l")
        self.mask_preset.addItem("Uppercase (?u)", "?u")
        self.mask_preset.addItem("Mixed (?a)", "?a")
        self.mask_preset.addItem("Alphanumeric (?h)", "?h")
        self.mask_preset.addItem("Special (?s)", "?s")
        self.mask_preset.addItem("All (?b)", "?b")
        self.mask_preset.currentIndexChanged.connect(self.on_mask_preset_changed)
        mask_layout.addWidget(self.mask_preset, 0, 1)
        
        mask_layout.addWidget(QLabel("Custom Mask:"), 1, 0)
        self.mask_custom = QLineEdit()
        self.mask_custom.setPlaceholderText("e.g., hiii?d?d or ?u?l?l?l?d")
        mask_layout.addWidget(self.mask_custom, 1, 1)
        
        # Password length
        mask_layout.addWidget(QLabel("Min Length:"), 2, 0)
        self.length_min = QSpinBox()
        self.length_min.setMinimum(1)
        self.length_min.setMaximum(128)
        self.length_min.setValue(4)
        mask_layout.addWidget(self.length_min, 2, 1)
        
        mask_layout.addWidget(QLabel("Max Length:"), 3, 0)
        self.length_max = QSpinBox()
        self.length_max.setMinimum(1)
        self.length_max.setMaximum(128)
        self.length_max.setValue(8)
        mask_layout.addWidget(self.length_max, 3, 1)
        
        self.use_increment = QCheckBox("Use Increment Mode")
        self.use_increment.setChecked(True)
        mask_layout.addWidget(self.use_increment, 4, 0, 1, 2)
        
        mask_group.setLayout(mask_layout)
        layout.addWidget(mask_group)
        
        # Wordlist settings
        wordlist_group = QGroupBox("Wordlist Configuration")
        wordlist_layout = QVBoxLayout()
        
        wordlist_h_layout = QHBoxLayout()
        wordlist_h_layout.addWidget(QLabel("Wordlist File:"))
        self.wordlist_path = QLineEdit()
        self.wordlist_path.setPlaceholderText("Select a wordlist file...")
        wordlist_h_layout.addWidget(self.wordlist_path)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_wordlist)
        wordlist_h_layout.addWidget(browse_btn)
        wordlist_layout.addLayout(wordlist_h_layout)
        
        wordlist_group.setLayout(wordlist_layout)
        layout.addWidget(wordlist_group)
        
        # GPU Settings
        gpu_group = QGroupBox("GPU Settings")
        gpu_layout = QGridLayout()
        
        gpu_layout.addWidget(QLabel("Device ID:"), 0, 0)
        self.device_id = QSpinBox()
        self.device_id.setMinimum(1)
        self.device_id.setMaximum(16)
        self.device_id.setValue(1)
        gpu_layout.addWidget(self.device_id, 0, 1)
        
        gpu_group.setLayout(gpu_layout)
        layout.addWidget(gpu_group)
        
        # Cache Management
        cache_group = QGroupBox("Cache & Storage")
        cache_layout = QVBoxLayout()
        
        cache_info_layout = QHBoxLayout()
        cache_info_layout.addWidget(QLabel("Cache Size:"))
        self.cache_size_label = QLabel()
        cache_info_layout.addWidget(self.cache_size_label)
        cache_info_layout.addStretch()
        cache_layout.addLayout(cache_info_layout)
        
        cache_button_layout = QHBoxLayout()
        
        refresh_cache_btn = QPushButton("Refresh")
        refresh_cache_btn.clicked.connect(self.update_cache_size_display)
        cache_button_layout.addWidget(refresh_cache_btn)
        
        clear_cache_btn = QPushButton("🗑️ Clear Cache")
        clear_cache_btn.setStyleSheet("background-color: #ff9900; color: black;")
        clear_cache_btn.clicked.connect(self.clear_cache)
        cache_button_layout.addWidget(clear_cache_btn)
        
        cache_layout.addLayout(cache_button_layout)
        
        self.cache_status_label = QLabel()
        cache_layout.addWidget(self.cache_status_label)
        
        cache_group.setLayout(cache_layout)
        layout.addWidget(cache_group)
        
        # Now update cache display after all widgets are created
        self.update_cache_size_display()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def on_mask_preset_changed(self, index):
        """Handle mask preset selection"""
        mask = self.mask_preset.currentData()
        if mask:
            self.mask_custom.setText(mask)
    
    def browse_wordlist(self):
        """Browse for wordlist file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Wordlist File",
            str(Path.home() / "Desktop"),
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.wordlist_path.setText(file_path)
    
    def get_settings(self):
        """Get configured settings"""
        return {
            'attack_mode': str(self.attack_mode_group.checkedId()),
            'mask': self.mask_custom.text(),
            'length_min': self.length_min.value(),
            'length_max': self.length_max.value(),
            'increment': self.use_increment.isChecked(),
            'wordlist': self.wordlist_path.text(),
            'device_id': self.device_id.value(),
        }
    
    def set_settings(self, settings):
        """Set dialog settings from dictionary"""
        if 'attack_mode' in settings:
            mode_id = int(settings['attack_mode'])
            self.attack_mode_group.button(mode_id).setChecked(True)
        
        if 'mask' in settings:
            self.mask_custom.setText(settings['mask'])
        
        if 'length_min' in settings:
            self.length_min.setValue(settings['length_min'])
        
        if 'length_max' in settings:
            self.length_max.setValue(settings['length_max'])
        
        if 'increment' in settings:
            self.use_increment.setChecked(settings['increment'])
        
        if 'wordlist' in settings:
            self.wordlist_path.setText(settings['wordlist'])
        
        if 'device_id' in settings:
            self.device_id.setValue(settings['device_id'])
    
    def update_cache_size_display(self):
        """Update cache size label"""
        try:
            size_formatted, size_bytes = self.cache_manager.get_cache_size_formatted()
            self.cache_size_label.setText(f"<b>{size_formatted}</b>")
            if size_bytes == 0:
                self.cache_status_label.setText("✓ Cache is empty")
                self.cache_status_label.setStyleSheet("color: #00cc00;")
            else:
                self.cache_status_label.setText(f"Click 'Clear Cache' to free up {size_formatted}")
                self.cache_status_label.setStyleSheet("color: #ffaa00;")
        except Exception as e:
            self.cache_size_label.setText("N/A")
            self.cache_status_label.setText(f"Error: {str(e)}")
            self.cache_status_label.setStyleSheet("color: #ff3333;")
    
    def clear_cache(self):
        """Clear application cache"""
        try:
            result = self.cache_manager.clear_cache()
            
            if result['errors']:
                error_text = "\n".join(result['errors'][:3])
                if len(result['errors']) > 3:
                    error_text += f"\n... and {len(result['errors']) - 3} more"
                QMessageBox.warning(
                    self,
                    "Partial Cleanup",
                    f"Cleared {result['cleared_count']} files ({result['cleared_size_formatted']})\n\n"
                    f"Some errors occurred:\n{error_text}"
                )
            else:
                QMessageBox.information(
                    self,
                    "Cache Cleared",
                    f"Successfully cleared {result['cleared_count']} cache files\n"
                    f"Freed up: {result['cleared_size_formatted']}"
                )
            
            # Update display
            self.update_cache_size_display()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear cache: {e}")

