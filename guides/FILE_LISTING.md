# AutoCrack GUI - File Listing

## Project Root Files

```
autocrack/
├── README.md                    # Main documentation (comprehensive guide)
├── QUICK_START.md              # 5-minute quick start guide
├── PROJECT_MANIFEST.md         # Complete project overview
└── FILE_LISTING.md             # This file
```

## Application Files (autocrack/app/)

### Main Application

```
app/
├── main.py                     # Application entry point (50 lines)
│                               # - PyQt6 application initialization
│                               # - Logging configuration
│                               # - Main window creation
│
├── requirements.txt            # Python dependencies
│                               # - PyQt6==6.6.1
│                               # - PyQt6-Qt6==6.6.1
│                               # - PyQt6-sip==13.6.0
│                               # - gputil==1.4.0
│                               # - psutil==5.9.6
│
└── install.bat                 # Installation helper script
                                # - Python dependency check
                                # - Tool verification
```

### Core Modules (app/core/)

```
core/
├── __init__.py                 # Package initialization
│
├── utils.py                    # Utility functions (250+ lines)
│                               # - Tool path management
│                               # - File utilities
│                               # - Archive validation
│                               # - JSON handling
│                               # - Logging setup
│                               # - Time/size formatting
│                               # Key Classes: None (all functions)
│                               # Key Functions: 20+
│
├── extractor.py                # Archive hash extraction (100+ lines)
│                               # - Archive type detection
│                               # - ZIP/RAR hash extraction
│                               # - Subprocess management
│                               # Key Class: ArchiveExtractor
│                               # Methods:
│                               #  - detect_archive_type()
│                               #  - extract_zip_hash()
│                               #  - extract_rar_hash()
│                               #  - extract_hash()
│                               #  - extract_and_save()
│
├── cleaner.py                  # Hash cleaning & validation (150+ lines)
│                               # - Hash normalization
│                               # - Prefix removal
│                               # - Duplicate removal
│                               # - Format validation
│                               # - Type identification
│                               # Key Class: HashCleaner
│                               # Methods:
│                               #  - remove_filename_prefix()
│                               #  - clean_hash()
│                               #  - validate_hash_format()
│                               #  - extract_hash_type()
│                               #  - clean_and_validate()
│
├── detector.py                 # Hash type detection (150+ lines)
│                               # - Pattern matching
│                               # - Hashcat mode lookup
│                               # - Mode information
│                               # Supported Modes:
│                               #  - RAR5 (13000)
│                               #  - RAR3 (13100)
│                               #  - PKZip2 (17200)
│                               #  - ZIP Encrypted (23001)
│                               #  - PDF (10500)
│                               #  - 7z (11600)
│                               # Key Class: HashModeDetector
│                               # Methods:
│                               #  - detect_hash_type()
│                               #  - get_hashcat_mode()
│                               #  - detect_and_get_mode()
│                               #  - get_mode_info()
│                               #  - list_supported_modes()
│
├── cracker.py                  # Hashcat cracking engine (200+ lines)
│                               # - Command building
│                               # - Attack configuration
│                               # - Process management
│                               # - Output streaming
│                               # - State management
│                               # Attack Modes:
│                               #  - Mode 0: Dictionary
│                               #  - Mode 1: Combination
│                               #  - Mode 3: Brute Force (Mask)
│                               #  - Mode 6: Hybrid (Dict+Mask)
│                               #  - Mode 7: Hybrid (Mask+Dict)
│                               # Key Class: Cracker
│                               # Methods:
│                               #  - build_command()
│                               #  - start_attack()
│                               #  - pause()
│                               #  - resume()
│                               #  - stop()
│                               #  - get_output()
│                               #  - get_state()
│                               # Constants: CrackerState enum
│
├── parser.py                   # Hashcat output parsing (180+ lines)
│                               # - Real-time statistics extraction
│                               # - Speed parsing
│                               # - Progress tracking
│                               # - Temperature monitoring
│                               # - GPU utilization
│                               # Key Class: HashcatOutputParser
│                               # Methods:
│                               #  - parse_speed()
│                               #  - parse_progress()
│                               #  - parse_eta()
│                               #  - parse_temperature()
│                               #  - parse_gpu_util()
│                               #  - parse_status_line()
│                               #  - parse_output()
│
└── session.py                  # Session management (200+ lines)
                                # - Session creation/persistence
                                # - State management
                                # - Progress tracking
                                # - JSON serialization
                                # Key Classes:
                                #  - CrackingSession
                                #  - SessionManager
                                # Methods:
                                #  - to_dict()
                                #  - from_dict()
                                #  - save()
                                #  - load()
                                #  - create_session()
                                #  - load_session()
```

### GUI Modules (app/gui/)

```
gui/
├── __init__.py                 # Package initialization
│
├── theme.py                    # Dark theme & styling (200+ lines)
│                               # - Color definitions
│                               # - Font configuration
│                               # - Complete QSS stylesheet
│                               # - Border radius constants
│                               # Color Palette:
│                               #  - Primary BG: #1e1e1e (dark)
│                               #  - Accent: #ff3333 (red)
│                               #  - Text: #ffffff (white)
│                               #  - Secondary: #2d2d2d
│                               # Key Classes: Theme
│                               # Functions:
│                               #  - get_stylesheet()
│                               #  - get_font()
│                               #  - get_mono_font()
│
├── progress_widget.py          # Progress display widget (200+ lines)
│                               # - Progress bar
│                               # - Statistics display
│                               # - Console output
│                               # - Color-coded logging
│                               # Key Class: ProgressWidget
│                               # Methods:
│                               #  - update_progress()
│                               #  - update_speed()
│                               #  - update_eta()
│                               #  - update_temperature()
│                               #  - add_console_line()
│                               #  - add_console_error()
│                               #  - add_console_success()
│
├── settings_dialog.py          # Settings configuration (200+ lines)
│                               # - Attack mode selection
│                               # - Mask configuration
│                               # - Password length settings
│                               # - GPU device selection
│                               # - Wordlist file picker
│                               # Key Class: SettingsDialog
│                               # Methods:
│                               #  - get_settings()
│                               #  - set_settings()
│                               #  - browse_wordlist()
│
└── main_window.py              # Main application window (400+ lines)
                                # - File selection (browse + drag/drop)
                                # - Hash extraction workflow
                                # - Attack control (start/pause/resume/stop)
                                # - Real-time progress tracking
                                # - Threaded cracking
                                # Key Classes:
                                #  - MainWindow (main UI)
                                #  - CrackerThread (worker thread)
                                # Methods:
                                #  - browse_archive()
                                #  - load_archive()
                                #  - extract_and_clean_hash()
                                #  - start_attack()
                                #  - pause_attack()
                                #  - resume_attack()
                                #  - stop_attack()
                                #  - update_display()
```

### Storage Directories (app/)

```
app/
├── hashes/                     # Extracted hash storage
│                               # - Raw hashes
│                               # - Cleaned hashes
│
├── sessions/                   # Session data persistence
│                               # - JSON session files
│                               # - Progress snapshots
│
├── temp/                       # Temporary files
│                               # - Intermediate hashes
│                               # - Working files
│
└── wordlists/                  # User wordlist storage
                                # - Dictionary files
                                # - Custom wordlists
```

### External Tools (app/tools/) - NOT INCLUDED

```
app/tools/
├── hashcat/
│   └── hashcat.exe            # Hashcat GPU password cracker
│                               # Download: https://hashcat.net/hashcat/
│                               # Required: v6.2+
│                               # For: GPU-accelerated cracking
│
└── john/run/
    ├── zip2john.exe           # ZIP hash extraction tool
    │                           # From: John the Ripper Jumbo
    ├── rar2john.exe           # RAR hash extraction tool
    │                           # From: John the Ripper Jumbo
    └── john.exe               # CPU password cracker
                                # From: John the Ripper Jumbo
                                # For: CPU fallback (optional)
```

---

## Documentation Files

### Root Documentation

```
autocrack/
├── README.md                   # Main documentation (1000+ lines)
│                               # - Feature overview
│                               # - System requirements
│                               # - Installation guide
│                               # - Complete usage manual
│                               # - Hash types & modes
│                               # - Performance tips
│                               # - Troubleshooting
│                               # - FAQ section
│
├── QUICK_START.md              # Quick start guide (200+ lines)
│                               # - 5-minute setup
│                               # - Common scenarios
│                               # - Quick examples
│                               # - Tips for success
│                               # - Keyboard shortcuts
│
└── PROJECT_MANIFEST.md         # Project overview (500+ lines)
                                # - Complete file structure
                                # - Module descriptions
                                # - API documentation
                                # - Feature matrix
                                # - Code statistics
```

---

## File Summary

### Total Statistics

- **Total Python Files:** 12 core files
- **Total Lines of Code:** 2100+ lines
- **Core Modules:** 7 files
- **GUI Modules:** 5 files
- **Documentation Files:** 4 files
- **Total Documentation:** 2000+ lines

### Code Breakdown

| Module             | Type | Lines | Purpose         |
| ------------------ | ---- | ----- | --------------- |
| utils.py           | Core | 250+  | Utilities       |
| extractor.py       | Core | 100+  | Hash extraction |
| cleaner.py         | Core | 150+  | Hash cleaning   |
| detector.py        | Core | 150+  | Hash detection  |
| cracker.py         | Core | 200+  | Cracking engine |
| parser.py          | Core | 180+  | Output parsing  |
| session.py         | Core | 200+  | Sessions        |
| theme.py           | GUI  | 200+  | Theming         |
| progress_widget.py | GUI  | 200+  | UI component    |
| settings_dialog.py | GUI  | 200+  | UI component    |
| main_window.py     | GUI  | 400+  | Main UI         |
| main.py            | App  | 50+   | Entry point     |

---

## Getting Started with Files

### 1. Installation & Setup

1. Read: [README.md](README.md)
2. Run: `app/install.bat`
3. Read: [QUICK_START.md](QUICK_START.md)

### 2. First Run

```bash
cd app
python main.py
```

### 3. Development

- Core logic: `app/core/` modules
- UI code: `app/gui/` modules
- Entry point: `app/main.py`

### 4. Understanding the Code

1. Start: `core/utils.py` - Utilities
2. Flow: `core/extractor.py` → `core/cleaner.py` → `core/detector.py`
3. Cracking: `core/cracker.py` + `core/parser.py`
4. UI: `gui/main_window.py` (orchestrates all)

---

## Dependencies

### Python Packages (requirements.txt)

- PyQt6 6.6.1 - GUI Framework
- gputil 1.4.0 - GPU monitoring
- psutil 5.9.6 - System utilities

### External Tools (Not Included)

- Hashcat 6.2+ - GPU password cracking
- John the Ripper Jumbo - Hash extraction

### System

- Windows 10/11
- Python 3.12+
- NVIDIA GPU (recommended)

---

## Key Capabilities by File

| Capability           | File(s)                            |
| -------------------- | ---------------------------------- |
| Archive Selection    | main_window.py                     |
| Drag & Drop          | main_window.py                     |
| Hash Extraction      | extractor.py                       |
| Hash Cleaning        | cleaner.py                         |
| Type Detection       | detector.py                        |
| Mode Selection       | detector.py                        |
| Attack Configuration | settings_dialog.py, main_window.py |
| Command Building     | cracker.py                         |
| Process Management   | cracker.py                         |
| Output Parsing       | parser.py                          |
| Progress Display     | progress_widget.py                 |
| Session Management   | session.py                         |
| Dark Theme           | theme.py                           |
| Threading            | main_window.py                     |
| Error Handling       | All files                          |
| Logging              | utils.py, main.py                  |

---

## Next Steps

1. **Install**: Follow `app/install.bat`
2. **Download Tools**: Get Hashcat and John
3. **Read**: [QUICK_START.md](QUICK_START.md)
4. **Run**: `python main.py`
5. **Crack**: Select archive → Extract → Attack

---

**AutoCrack GUI v1.0.0** - Complete File Listing
Generated: 2026-05-27
