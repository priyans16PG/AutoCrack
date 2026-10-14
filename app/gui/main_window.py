"""
Main application window
"""
import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QProgressBar, QTextEdit, QFileDialog, QMessageBox,
    QSplitter, QGroupBox, QSpinBox, QCheckBox, QComboBox, QDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QDropEvent, QDragEnterEvent, QIcon
from PyQt6.QtCore import QMimeData
from gui.theme import Theme, get_stylesheet, get_font
from gui.progress_widget import ProgressWidget
from gui.settings_dialog import SettingsDialog
from core.extractor import ArchiveExtractor
from core.cleaner import HashCleaner
from core.detector import HashModeDetector
from core.cracker import Cracker, CrackerState
from core.parser import HashcatOutputParser
from core import utils
import logging

logger = logging.getLogger(__name__)


class CrackerThread(QThread):
    """Thread for running cracker in background"""
    
    progress_update = pyqtSignal(dict)
    finished = pyqtSignal(str)
    password_found = pyqtSignal(str)
    error = pyqtSignal(str)
    output = pyqtSignal(str)
    
    def __init__(self, cracker):
        super().__init__()
        self.cracker = cracker
        self.running = True
    
    def run(self):
        """Run the cracker thread"""
        try:
            logger.info("[CRACKER_THREAD] Starting cracker thread")
            last_output = ""
            password = None
            while self.running and self.cracker.is_running():
                # Get output from queue
                outputs = self.cracker.get_output()
                
                for output_type, data in outputs:
                    if output_type == 'stdout':
                        self.output.emit(data)
                        last_output = data
                        logger.info(f"[CRACKER_THREAD] Output: {data[:100]}")
                        
                        # Parse stats from output lines
                        progress_data = {}
                        
                        # Try to parse all stats from the line
                        # Parse speed
                        speed = self.cracker.parser.parse_speed(data)
                        if speed and speed != "0 H/s":
                            progress_data['speed'] = speed
                            logger.info(f"[CRACKER_THREAD] Speed: {speed}")
                        
                        # Parse progress
                        progress = self.cracker.parser.parse_progress(data)
                        if progress:
                            progress_data['progress'] = progress
                            logger.info(f"[CRACKER_THREAD] Progress: {progress['percentage']}%")
                        
                        # Parse ETA
                        eta = self.cracker.parser.parse_eta(data)
                        if eta and eta > 0:
                            progress_data['eta'] = eta
                            logger.info(f"[CRACKER_THREAD] ETA: {eta}s")
                        
                        # Parse temperature
                        temp = self.cracker.parser.parse_temperature(data)
                        if temp and temp > 0:
                            progress_data['temperature'] = temp
                            logger.info(f"[CRACKER_THREAD] Temp: {temp}°C")
                        
                        # Parse GPU util
                        util = self.cracker.parser.parse_gpu_util(data)
                        if util and util > 0:
                            progress_data['gpu_util'] = util
                            logger.info(f"[CRACKER_THREAD] GPU Util: {util}%")
                        
                        # Only emit if we have data
                        if progress_data:
                            self.progress_update.emit(progress_data)
                    
                    elif output_type == 'password':
                        logger.info(f"[CRACKER_THREAD] Password found: {data}")
                        password = data
                        self.password_found.emit(data)
                        # Set progress to 100% when password found
                        self.progress_update.emit({'progress': {'percentage': 100, 'current': 1, 'total': 1}})
                    elif output_type == 'stderr':
                        logger.error(f"[CRACKER_THREAD] Error: {data}")
                        self.error.emit(data)
                
                # Small delay to avoid busy waiting
                self.msleep(100)
            
            logger.info("[CRACKER_THREAD] Cracker no longer running")
            
            # Drain any remaining output from queue
            logger.info("[CRACKER_THREAD] Draining remaining queue items...")
            remaining_outputs = self.cracker.get_output()
            for output_type, data in remaining_outputs:
                if output_type == 'password':
                    logger.info(f"[CRACKER_THREAD] Password found (from queue drain): {data}")
                    password = data
                    self.password_found.emit(data)
                    self.progress_update.emit({'progress': {'percentage': 100, 'current': 1, 'total': 1}})
                elif output_type == 'stdout':
                    self.output.emit(data)
                elif output_type == 'stderr':
                    self.error.emit(data)
            
            # Check final state
            if self.cracker.is_completed():
                if self.cracker.state == CrackerState.COMPLETED:
                    logger.info("[CRACKER_THREAD] Completed successfully")
                    # Only emit finished if we found a password
                    if password:
                        self.finished.emit(password)
                    else:
                        self.finished.emit("Cracking completed!")
                else:
                    logger.error(f"[CRACKER_THREAD] Final state: {self.cracker.state}")
                    self.error.emit("Cracking failed or was stopped")
        
        except Exception as e:
            logger.error(f"[CRACKER_THREAD] Exception: {e}")
            self.error.emit(str(e))
    
    def stop(self):
        """Stop the thread"""
        self.running = False


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.setWindowTitle("AutoCrack GUI - Archive & PDF Password Recovery")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize components
        self.extractor = ArchiveExtractor()
        self.cleaner = HashCleaner()
        self.detector = HashModeDetector()
        self.parser = HashcatOutputParser()
        self.cracker = None
        self.cracker_thread = None
        
        # Current state
        self.archive_path = None
        self.hash_file = None
        self.cleaned_hash = None
        self.hash_type = None
        self.hash_mode = None
        self.password_found = None
        
        # Setup UI
        self.setup_ui()
        self.apply_stylesheet()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
    
    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Left panel - Controls
        left_panel = self.create_left_panel()
        
        # Right panel - Progress and output
        right_panel = self.progress_widget = ProgressWidget()
        
        # Split view
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def create_left_panel(self):
        """Create left control panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # File Selection
        file_group = QGroupBox("Archive Selection")
        file_layout = QVBoxLayout()
        
        file_h = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("Drag & drop archive/PDF or click Browse...")
        self.file_path.setReadOnly(True)
        file_h.addWidget(self.file_path)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_archive)
        file_h.addWidget(browse_btn)
        
        file_layout.addLayout(file_h)
        
        self.file_info = QTextEdit()
        self.file_info.setReadOnly(True)
        self.file_info.setMaximumHeight(80)
        file_layout.addWidget(self.file_info)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Hash Status
        hash_group = QGroupBox("Hash Status")
        hash_layout = QVBoxLayout()
        
        self.hash_status = QTextEdit()
        self.hash_status.setReadOnly(True)
        self.hash_status.setMaximumHeight(60)
        hash_layout.addWidget(self.hash_status)
        
        extract_btn = QPushButton("Extract & Clean Hash")
        extract_btn.clicked.connect(self.extract_and_clean_hash)
        hash_layout.addWidget(extract_btn)
        
        hash_group.setLayout(hash_layout)
        layout.addWidget(hash_group)
        
        # Attack Settings (simplified)
        attack_group = QGroupBox("Attack Settings")
        attack_layout = QVBoxLayout()
        
        attack_mode_layout = QHBoxLayout()
        attack_mode_layout.addWidget(QLabel("Mode:"))
        self.attack_mode = QComboBox()
        self.attack_mode.addItem("Brute Force (Mask)", "3")
        self.attack_mode.addItem("Dictionary", "0")
        self.attack_mode.addItem("Hybrid (Dict+Mask)", "6")
        self.attack_mode.addItem("Hybrid (Mask+Dict)", "7")
        self.attack_mode.currentIndexChanged.connect(self.on_attack_mode_changed)
        attack_mode_layout.addWidget(self.attack_mode)
        attack_layout.addLayout(attack_mode_layout)
        
        mask_layout = QHBoxLayout()
        mask_layout.addWidget(QLabel("Mask:"))
        self.mask_input = QLineEdit()
        self.mask_input.setText("?d")
        self.mask_input.setPlaceholderText("e.g., ?d?d?d?d")
        mask_layout.addWidget(self.mask_input)
        attack_layout.addLayout(mask_layout)
        
        # Wordlist configuration
        self.wordlist_path = None
        wordlist_layout = QHBoxLayout()
        wordlist_layout.addWidget(QLabel("Wordlist:"))
        self.wordlist_input = QLineEdit()
        self.wordlist_input.setPlaceholderText("Select wordlist...")
        self.wordlist_input.setReadOnly(True)
        wordlist_layout.addWidget(self.wordlist_input)
        
        wordlist_btn = QPushButton("...")
        wordlist_btn.setMaximumWidth(40)
        wordlist_btn.clicked.connect(self.browse_wordlist)
        wordlist_layout.addWidget(wordlist_btn)
        attack_layout.addLayout(wordlist_layout)

        # Quick preset buttons
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Quick Presets:"))
        
        nums_btn = QPushButton("Numbers")
        nums_btn.clicked.connect(lambda: self.set_mask("?d?d?d?d?d?d"))
        preset_layout.addWidget(nums_btn)
        
        chars_btn = QPushButton("Letters")
        chars_btn.clicked.connect(lambda: self.set_mask("?l?l?l?l?l?l"))
        preset_layout.addWidget(chars_btn)
        
        all_btn = QPushButton("All Chars")
        all_btn.clicked.connect(lambda: self.set_mask("?a?a?a?a?a?a?a"))
        preset_layout.addWidget(all_btn)
        
        attack_layout.addLayout(preset_layout)
        
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Length:"))
        self.min_length = QSpinBox()
        self.min_length.setValue(4)
        self.min_length.setMinimum(1)
        length_layout.addWidget(self.min_length)
        length_layout.addWidget(QLabel("-"))
        self.max_length = QSpinBox()
        self.max_length.setValue(8)
        self.max_length.setMinimum(1)
        length_layout.addWidget(self.max_length)
        attack_layout.addLayout(length_layout)
        
        self.use_increment = QCheckBox("Use Increment")
        self.use_increment.setChecked(True)
        attack_layout.addWidget(self.use_increment)
        
        settings_btn = QPushButton("Advanced Settings...")
        settings_btn.clicked.connect(self.show_settings)
        attack_layout.addWidget(settings_btn)
        
        attack_group.setLayout(attack_layout)
        layout.addWidget(attack_group)
        
        # Control Buttons
        button_layout = QVBoxLayout()
        
        self.start_btn = QPushButton("▶ Start Attack")
        self.start_btn.setStyleSheet("background-color: #00cc00; color: black; font-weight: bold; padding: 10px;")
        self.start_btn.clicked.connect(self.start_attack)
        button_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.pause_attack)
        button_layout.addWidget(self.pause_btn)
        
        self.resume_btn = QPushButton("▶ Resume")
        self.resume_btn.setEnabled(False)
        self.resume_btn.clicked.connect(self.resume_attack)
        button_layout.addWidget(self.resume_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("background-color: #ff3333; color: white; font-weight: bold; padding: 10px;")
        self.stop_btn.clicked.connect(self.stop_attack)
        button_layout.addWidget(self.stop_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        panel.setLayout(layout)
        return panel
    
    def apply_stylesheet(self):
        """Apply dark theme stylesheet"""
        self.setStyleSheet(get_stylesheet())
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.load_archive(files[0])
    
    def browse_archive(self):
        """Browse for archive file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Archive File",
            str(Path.home() / "Desktop"),
            "Supported Files (*.zip *.rar *.7z *.pdf);;Archive Files (*.zip *.rar *.7z);;PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            self.load_archive(file_path)
    
    def load_archive(self, path):
        """Load archive file"""
        try:
            archive_path = utils.validate_archive_path(path)
            self.archive_path = archive_path
            self.file_path.setText(str(archive_path))
            
            # Show metadata
            metadata = utils.get_archive_metadata(archive_path)
            info_text = f"Name: {metadata['name']}\n"
            info_text += f"Type: {metadata['extension']}\n"
            info_text += f"Size: {utils.format_bytes(metadata['size'])}"
            self.file_info.setText(info_text)
            
            self.progress_widget.add_console_info(f"Loaded archive: {metadata['name']}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load archive: {e}")
            self.progress_widget.add_console_error(f"Error: {e}")
    
    def on_attack_mode_changed(self):
        """Update UI based on selected attack mode"""
        mode = self.attack_mode.currentData()
        # Enable wordlist for Dictionary (0), Hybrid (6), Hybrid (7)
        needs_wordlist = mode in ['0', '6', '7']
        self.wordlist_input.setEnabled(needs_wordlist)
        
        # Enable mask for Brute Force (3), Hybrid (6), Hybrid (7)
        needs_mask = mode in ['3', '6', '7']
        self.mask_input.setEnabled(needs_mask)
        self.min_length.setEnabled(needs_mask)
        self.max_length.setEnabled(needs_mask)

    def browse_wordlist(self):
        """Browse for a wordlist file"""
        from PyQt6.QtWidgets import QFileDialog
        
        # Default to the wordlists folder
        wordlists_dir = str(Path(__file__).parent.parent / 'wordlists')
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Wordlist",
            wordlists_dir,
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            self.wordlist_path = file_path
            self.wordlist_input.setText(Path(file_path).name)
            self.logger.info(f"[MAIN_WINDOW] Selected wordlist: {file_path}")

    def extract_and_clean_hash(self):
        """Extract and clean hash from archive"""
        if not self.archive_path:
            QMessageBox.warning(self, "Warning", "Please select an archive file first")
            return
        
        try:
            self.progress_widget.add_console_info("Extracting hash...")
            
            # Extract and save
            self.hash_file, raw_hash = self.extractor.extract_and_save(self.archive_path)
            self.progress_widget.add_console_success("Hash extracted")
            
            # Clean
            self.progress_widget.add_console_info("Cleaning hash...")
            self.cleaned_hash = self.cleaner.clean_and_validate(raw_hash)
            self.logger.info(f"[MAIN_WINDOW] Cleaned hash received: {self.cleaned_hash[:50]}...")
            
            # Save cleaned hash to file for Hashcat
            from pathlib import Path
            cleaned_hash_file = Path(self.hash_file).parent / (Path(self.hash_file).stem.replace('_raw', '_clean') + '.txt')
            with open(cleaned_hash_file, 'w') as f:
                f.write(self.cleaned_hash)
            self.hash_file = str(cleaned_hash_file)
            self.logger.info(f"[MAIN_WINDOW] Saved cleaned hash to: {self.hash_file}")
            
            # Detect type
            self.logger.info(f"[MAIN_WINDOW] Attempting to detect hash type...")
            self.hash_type, self.hash_mode = self.detector.detect_and_get_mode(self.cleaned_hash)
            
            # Update UI
            status_text = f"Type: {self.hash_type}\n"
            status_text += f"Mode: {self.hash_mode}\n"
            status_text += f"Hash: {self.cleaned_hash[:50]}..."
            self.hash_status.setText(status_text)
            
            self.progress_widget.add_console_success(f"Hash cleaned! Type: {self.hash_type}, Mode: {self.hash_mode}")
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"[MAIN_WINDOW] Exception during extraction: {error_msg}", exc_info=True)
            
            # Provide more helpful error messages
            detailed_msg = error_msg
            if "Empty hash input" in error_msg or "not be password-protected" in error_msg:
                detailed_msg = f"⚠ {error_msg}\n\nPossible causes:\n- Archive is not password-protected\n- Not a valid RAR/ZIP archive\n- File is corrupted or unrecognized format"
            elif "not found" in error_msg.lower():
                detailed_msg = f"⚠ {error_msg}\n\nMake sure you selected a valid archive file."
            else:
                detailed_msg = f"⚠ Extraction failed: {error_msg}"
            
            QMessageBox.critical(self, "Extraction Error", detailed_msg)
            self.progress_widget.add_console_error(f"Extraction Error: {error_msg}")
            self.progress_widget.add_console_info("Please verify the archive file and try again.")
    
    def show_settings(self):
        """Show advanced settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            pass  # Settings applied in dialog
    
    def set_mask(self, mask):
        """Set mask for quick presets"""
        self.mask_input.setText(mask)
        self.progress_widget.add_console_info(f"Mask set to: {mask}")
    
    def start_attack(self):
        """Start cracking attack"""
        if not self.hash_file:
            QMessageBox.warning(self, "Warning", "Please extract hash first")
            return
        
        try:
            # Create cracker
            self.cracker = Cracker(self.hash_file, self.hash_mode)
            
            # Get settings
            attack_mode = self.attack_mode.currentData()
            mask = self.mask_input.text().strip() if attack_mode in ['3', '6', '7'] else None
            wordlist = self.wordlist_path if attack_mode in ['0', '6', '7'] else None
            
            # Use better default mask if empty or too short
            if attack_mode == '3' and (not mask or len(mask) < 4):
                mask = '?a?a?a?a?a?a?a'  # 7 char default with all types: lowercase+uppercase+digits+symbols
                self.logger.info(f"Using default mask: {mask}")
                self.progress_widget.add_console_info(f"Using default mask: {mask} (all character types, length 7)")
            
            if attack_mode in ['0', '6', '7'] and not wordlist:
                QMessageBox.warning(self, "Warning", "Please select a wordlist file for this attack mode.")
                return
            
            # Start attack
            self.cracker.start_attack(mask=mask, wordlist=wordlist, increment=self.use_increment.isChecked())
            
            # Start thread
            self.cracker_thread = CrackerThread(self.cracker)
            self.cracker_thread.output.connect(self.on_cracker_output)
            self.cracker_thread.error.connect(self.on_cracker_error)
            self.cracker_thread.progress_update.connect(self.on_progress_update)
            self.cracker_thread.password_found.connect(self.on_password_found)
            self.cracker_thread.finished.connect(self.on_cracker_finished)
            self.cracker_thread.start()
            
            # Update UI
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            
            self.update_timer.start(500)
            self.progress_widget.add_console_info("Attack started...")
            
        except Exception as e:
            self.logger.error(f"[MAIN_WINDOW] Attack start error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start attack: {e}")
            self.progress_widget.add_console_error(f"Error: {e}")
    
    def pause_attack(self):
        """Pause attack"""
        if self.cracker:
            self.cracker.pause()
            self.pause_btn.setEnabled(False)
            self.resume_btn.setEnabled(True)
            self.progress_widget.add_console_warning("Attack paused")
    
    def resume_attack(self):
        """Resume attack"""
        if self.cracker:
            self.cracker.resume()
            self.resume_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.progress_widget.add_console_warning("Attack resumed")
    
    def stop_attack(self):
        """Stop attack"""
        if self.cracker:
            self.cracker.stop()
            self.update_timer.stop()
            
            if self.cracker_thread:
                self.cracker_thread.stop()
                self.cracker_thread.wait()
            
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.resume_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            
            self.progress_widget.add_console_warning("Attack stopped")
    
    def on_cracker_output(self, line):
        """Handle cracker output"""
        self.progress_widget.add_console_line(line, "#00ff00")
    
    def on_cracker_error(self, error):
        """Handle cracker error"""
        self.progress_widget.add_console_error(error)
    
    def on_progress_update(self, progress_data):
        """Handle progress update from cracker thread"""
        try:
            # Update progress bar
            if 'progress' in progress_data:
                prog = progress_data['progress']
                percentage = int(prog.get('percentage', 0))
                self.progress_widget.progress_bar.setValue(min(percentage, 100))
                current = prog.get('current', 0)
                total = prog.get('total', 0)
                if total > 0:
                    self.progress_widget.label_progress_pct.setText(
                        f"{current:,} / {total:,} ({percentage}%)"
                    )
                self.logger.info(f"[MAIN_WINDOW] Progress: {percentage}%")
            
            # Update speed
            if 'speed' in progress_data:
                self.progress_widget.label_speed.setText(str(progress_data['speed']))
            
            # Update ETA
            if 'eta' in progress_data:
                eta_seconds = int(progress_data['eta'])
                hours = eta_seconds // 3600
                minutes = (eta_seconds % 3600) // 60
                seconds = eta_seconds % 60
                if hours > 0:
                    eta_str = f"{hours}h {minutes}m {seconds}s"
                elif minutes > 0:
                    eta_str = f"{minutes}m {seconds}s"
                else:
                    eta_str = f"{seconds}s"
                self.progress_widget.label_eta.setText(eta_str)
            
            # Update temperature
            if 'temperature' in progress_data:
                temp = int(progress_data['temperature'])
                self.progress_widget.label_temp.setText(f"{temp}°C")
            
            # Update GPU util
            if 'gpu_util' in progress_data:
                util = int(progress_data['gpu_util'])
                self.progress_widget.label_gpu_util.setText(f"{util}%")
        except Exception as e:
            self.logger.error(f"[MAIN_WINDOW] Error updating progress: {e}")
    
    def on_password_found(self, password):
        """Handle password found during cracking"""
        self.password_found = password
        self.progress_widget.add_console_success(f"PASSWORD FOUND: {password}")
        self.progress_widget.set_password(password)  # Display in prominent section
        self.logger.info(f"[MAIN_WINDOW] Password found: {password}")
    
    def on_cracker_finished(self, message):
        """Handle cracker finished"""
        # If we already found a password, don't override
        if self.password_found and self.password_found != "":
            QMessageBox.information(self, "Success", f"Password found: {self.password_found}")
        else:
            self.progress_widget.add_console_info(message)
        
        self.update_timer.stop()
    
    def update_display(self):
        """Update display with latest stats"""
        if self.cracker and self.cracker.is_running():
            # Get latest output
            outputs = self.cracker.get_output()
            for output_type, data in outputs:
                if output_type == 'stdout':
                    # Parse stats
                    parsed = self.parser.parse_status_line(data)
                    if parsed:
                        if 'speed' in parsed:
                            self.progress_widget.update_speed(parsed['speed'])
                        if 'progress' in parsed:
                            prog = parsed['progress']
                            self.progress_widget.update_progress(prog['current'], prog['total'])
                        if 'eta' in parsed:
                            self.progress_widget.update_eta(utils.format_time(parsed['eta']))
                        if 'temperature' in parsed:
                            self.progress_widget.update_temperature(parsed['temperature'])
                        if 'gpu_util' in parsed:
                            self.progress_widget.update_gpu_util(parsed['gpu_util'])
