# AutoCrack GUI - Project Manifest

## Project Overview

Professional Python desktop application for automating archive password recovery using John the Ripper Jumbo and Hashcat.

**Version:** 1.0.0  
**Platform:** Windows 10/11  
**Python:** 3.12+  
**License:** Educational/Security Testing

---

## Deliverables

### 📁 Project Structure

```
autocrack/
├── README.md                          # Main documentation
├── QUICK_START.md                     # Quick start guide
├── PROJECT_MANIFEST.md                # This file
│
└── app/
    ├── main.py                        # Application entry point
    ├── requirements.txt               # Python dependencies
    ├── install.bat                    # Installation helper script
    │
    ├── tools/                         # External tools (empty, requires download)
    │   ├── hashcat/
    │   │   └── hashcat.exe (NOT INCLUDED)
    │   └── john/run/
    │       ├── zip2john.exe (NOT INCLUDED)
    │       ├── rar2john.exe (NOT INCLUDED)
    │       └── john.exe (NOT INCLUDED)
    │
    ├── core/                          # Core functionality modules
    │   ├── __init__.py
    │   ├── utils.py                   # Utility functions
    │   ├── extractor.py               # Archive hash extraction
    │   ├── cleaner.py                 # Hash cleaning & validation
    │   ├── detector.py                # Hash type detection
    │   ├── cracker.py                 # Hashcat cracking engine
    │   ├── parser.py                  # Output parsing
    │   └── session.py                 # Session management
    │
    ├── gui/                           # GUI modules
    │   ├── __init__.py
    │   ├── main_window.py             # Main application window
    │   ├── progress_widget.py         # Progress display widget
    │   ├── settings_dialog.py         # Settings configuration
    │   └── theme.py                   # Dark theme & styling
    │
    ├── hashes/                        # Extracted hashes storage
    ├── sessions/                      # Session data persistence
    ├── wordlists/                     # Wordlist files (user-provided)
    └── temp/                          # Temporary files
```

---

## Core Modules (app/core/)

### ✅ utils.py (250+ lines)

**Functionality:**

- Tool path management
- File path utilities
- Archive validation
- JSON serialization
- Logging configuration
- Time/size formatting
- Temporary file management

**Key Functions:**

```python
- get_app_path()
- get_tool_path(tool_name)
- ensure_tool_exists(tool_name)
- validate_archive_path(archive_path)
- get_archive_metadata(archive_path)
- format_bytes(bytes_value)
- format_time(seconds)
```

### ✅ extractor.py (100+ lines)

**Functionality:**

- Archive type detection (.zip, .rar, .7z)
- Hash extraction using zip2john/rar2john
- Subprocess management
- Error handling

**Key Classes:**

```python
class ArchiveExtractor:
  - detect_archive_type(archive_path)
  - extract_zip_hash(archive_path)
  - extract_rar_hash(archive_path)
  - extract_hash(archive_path)
  - extract_and_save(archive_path, output_file)
```

### ✅ cleaner.py (150+ lines)

**Functionality:**

- Hash cleaning and normalization
- Filename prefix removal
- Duplicate line removal
- Hash format validation
- Hash type identification

**Key Classes:**

```python
class HashCleaner:
  - remove_filename_prefix(hash_string)
  - clean_hash(raw_hash)
  - validate_hash_format(hash_string)
  - extract_hash_type(hash_string)
  - clean_and_validate(raw_hash)
```

### ✅ detector.py (150+ lines)

**Functionality:**

- Hash type detection (RAR5, RAR3, PKZip2, etc.)
- Hashcat mode mapping
- Hash format pattern matching
- Mode information lookup

**Key Classes:**

```python
class HashModeDetector:
  - detect_hash_type(hash_string)
  - get_hashcat_mode(hash_type)
  - detect_and_get_mode(hash_string)
  - get_mode_info(mode)
  - list_supported_modes()
```

**Supported Modes:**

- RAR5 (Mode 13000)
- RAR3 (Mode 13100)
- ZIP/PKWARE (Mode 17200)
- ZIP Encrypted (Mode 23001)
- PDF (Mode 10500)
- 7z (Mode 11600)

### ✅ cracker.py (200+ lines)

**Functionality:**

- Hashcat command building
- Attack mode configuration
- Process management
- Output streaming
- State management (pause/resume/stop)

**Key Classes:**

```python
class Cracker:
  - build_command(mask, wordlist, increment, device_id, rules, hybrid)
  - start_attack(mask, wordlist, increment, device_id, rules, hybrid)
  - pause()
  - resume()
  - stop()
  - get_output()
  - get_state()
  - is_running()
  - is_completed()
```

**Attack Modes:**

- Mode 0: Dictionary
- Mode 1: Combination
- Mode 3: Brute Force (Mask)
- Mode 6: Hybrid (Dict + Mask)
- Mode 7: Hybrid (Mask + Dict)

### ✅ parser.py (180+ lines)

**Functionality:**

- Hashcat output parsing
- Real-time statistics extraction
- Speed parsing
- Progress tracking
- Temperature monitoring
- GPU utilization parsing

**Key Classes:**

```python
class HashcatOutputParser:
  - parse_speed(line)
  - parse_progress(line)
  - parse_eta(line)
  - parse_temperature(line)
  - parse_gpu_util(line)
  - parse_recovered(line)
  - parse_candidate(line)
  - parse_status_line(line)
  - parse_hash_found(line)
  - parse_output(output_text)
```

### ✅ session.py (200+ lines)

**Functionality:**

- Session creation and persistence
- Session restoration
- State management
- Progress tracking
- JSON serialization

**Key Classes:**

```python
class CrackingSession:
  - to_dict()
  - from_dict(data)
  - update(**kwargs)
  - save()
  - load(session_id)

class SessionManager:
  - create_session(session_id)
  - load_session(session_id)
  - get_session(session_id)
  - list_sessions()
  - delete_session(session_id)
  - save_all()
```

---

## GUI Modules (app/gui/)

### ✅ theme.py (200+ lines)

**Functionality:**

- Dark modern theme definition
- Color scheme (Red accents on dark background)
- Font configuration
- Complete stylesheet generation
- UI element styling

**Features:**

- 20+ color definitions
- Font management
- Border radius constants
- QSS stylesheet for all widgets

### ✅ progress_widget.py (200+ lines)

**Functionality:**

- Real-time progress display
- Statistics visualization
- Console output with color coding
- Speed/ETA/Temperature monitoring

**Key Components:**

- Progress bar
- Statistics display (Speed, ETA, Temp, GPU Util)
- Console output area
- Status updates

### ✅ settings_dialog.py (200+ lines)

**Functionality:**

- Attack configuration
- Mask selection and customization
- Password length settings
- GPU device selection
- Wordlist file selection

**Features:**

- Predefined mask presets
- Custom mask input
- Min/Max length controls
- Increment mode toggle

### ✅ main_window.py (400+ lines)

**Functionality:**

- Main application window
- File selection and drag-drop
- Hash extraction workflow
- Attack control (start/pause/resume/stop)
- Real-time updates
- Threading for non-blocking UI

**Key Features:**

- Archive file browser
- Drag & drop support
- Archive metadata display
- Hash status display
- Attack mode selection
- Live progress tracking
- Console output with colors
- GPU statistics monitoring

**Components:**

- Left control panel
- Right progress panel
- Threaded cracker worker
- Signal/slot communication

---

## Python Dependencies (requirements.txt)

```
PyQt6==6.6.1                    # GUI Framework
PyQt6-Qt6==6.6.1                # Qt runtime
PyQt6-sip==13.6.0               # Python bindings
gputil==1.4.0                   # GPU utilities
psutil==5.9.6                   # System utilities
```

---

## Key Features Implemented

### 1. ✅ File Selection

- Browse dialog
- Drag & drop support
- Archive validation
- Metadata display

### 2. ✅ Hash Extraction

- ZIP support (zip2john)
- RAR support (rar2john)
- Error handling
- Progress feedback

### 3. ✅ Hash Cleaning

- Automatic prefix removal
- Duplicate removal
- Format validation
- Type detection

### 4. ✅ Hash Mode Detection

- Pattern matching
- Hashcat mode lookup
- Type identification
- Mode information

### 5. ✅ Attack Modes

- Brute Force (Mask)
- Dictionary
- Hybrid (Dict+Mask)
- Hybrid (Mask+Dict)
- Increment mode

### 6. ✅ Real-Time Monitoring

- Speed tracking
- Progress percentage
- ETA calculation
- GPU temperature
- GPU utilization

### 7. ✅ Attack Control

- Start/Stop
- Pause/Resume
- State management
- Safe shutdown

### 8. ✅ Session Management

- Session saving
- Session restoration
- State persistence
- Progress tracking

### 9. ✅ Threading

- Non-blocking UI
- Background cracking
- Output streaming
- Clean shutdown

### 10. ✅ Professional UI

- Dark modern theme
- Red accent colors
- Responsive design
- Color-coded console
- Real-time updates

---

## Usage Examples

### Example 1: Crack 4-digit PIN on ZIP

```python
# Programmatic usage
from core.extractor import ArchiveExtractor
from core.cleaner import HashCleaner
from core.detector import HashModeDetector
from core.cracker import Cracker

# Extract
extractor = ArchiveExtractor()
hash_file, raw_hash = extractor.extract_and_save("archive.zip")

# Clean
cleaner = HashCleaner()
cleaned_hash = cleaner.clean_and_validate(raw_hash)

# Detect
detector = HashModeDetector()
hash_type, mode = detector.detect_and_get_mode(cleaned_hash)

# Crack
cracker = Cracker(hash_file, mode)
cracker.start_attack(mask="?d?d?d?d", increment=False)

# Monitor
while cracker.is_running():
    outputs = cracker.get_output()
    for output_type, data in outputs:
        print(f"{output_type}: {data}")
```

### Example 2: Dictionary Attack

```python
cracker = Cracker("hash.txt", 17200)
cracker.start_attack(attack_mode='0', wordlist="wordlist.txt")
```

### Example 3: Hybrid Attack

```python
cracker = Cracker("hash.txt", 13000)
cracker.start_attack(
    attack_mode='6',  # Dict + Mask
    wordlist="passwords.txt",
    mask="?d?d?d"
)
```

---

## Supported Masks

| Mask | Character Set      |
| ---- | ------------------ |
| `?d` | Digits (0-9)       |
| `?l` | Lowercase (a-z)    |
| `?u` | Uppercase (A-Z)    |
| `?s` | Special (!@#$%...) |
| `?a` | All (?l?u?d?s)     |
| `?h` | Hex (0-9a-f)       |
| `?b` | Byte (0-255)       |

### Mask Examples:

```
?d?d?d?d          → 0000-9999 (numeric, 4 chars)
?u?l?l?l?d?d      → Aaaa00 format
hiii?d?d          → hiii00-hiii99
?a?a?a?a?a?a      → All chars, 6 length
```

---

## Performance Metrics

### Expected Performance (NVIDIA RTX 3080)

- **Numeric**: 50+ billion attempts/second
- **Lowercase**: 10+ billion attempts/second
- **Mixed**: 1-2 billion attempts/second

### Estimated Crack Times

| Password   | Mask             | Length | Time   |
| ---------- | ---------------- | ------ | ------ |
| 1234       | ?d?d?d?d         | 4      | <0.1s  |
| 123456     | ?d?d?d?d?d?d     | 6      | <0.05s |
| abcd1234   | ?l?l?l?l?d?d?d?d | 8      | ~2s    |
| Dictionary | English wordlist | -      | 5-30m  |

---

## File Statistics

| Module             | Lines      | Functions/Classes     | Purpose            |
| ------------------ | ---------- | --------------------- | ------------------ |
| utils.py           | 250+       | 15 functions          | Utilities          |
| extractor.py       | 100+       | 1 class, 5 methods    | Hash extraction    |
| cleaner.py         | 150+       | 1 class, 6 methods    | Hash cleaning      |
| detector.py        | 150+       | 1 class, 5 methods    | Hash detection     |
| cracker.py         | 200+       | 1 class, 10 methods   | Cracking engine    |
| parser.py          | 180+       | 1 class, 12 methods   | Output parsing     |
| session.py         | 200+       | 2 classes, 12 methods | Session management |
| theme.py           | 200+       | 1 class, 2 functions  | Theming            |
| progress_widget.py | 200+       | 1 class, 15 methods   | Progress UI        |
| settings_dialog.py | 200+       | 1 class, 5 methods    | Settings UI        |
| main_window.py     | 400+       | 1 class, 20+ methods  | Main UI            |
| **TOTAL**          | **~2100+** | **50+**               | **Complete app**   |

---

## Installation Requirements

### Minimum

- Python 3.12+
- PyQt6 + dependencies
- Windows 10 or 11

### Recommended

- NVIDIA GPU (CUDA-capable)
- 4GB RAM
- SSD for faster temp file operations
- NVIDIA GPU drivers (latest)

### External Tools (Download Separately)

- Hashcat 6.2+ (GPU acceleration)
- John the Ripper Jumbo (Hash extraction)

---

## Known Limitations

1. Windows only (can be adapted to Linux/Mac)
2. Requires NVIDIA GPU for acceleration
3. Requires manual download of external tools
4. Limited to single system (can be extended for distributed)
5. UI may be unresponsive during initial hash extraction

---

## Future Enhancement Opportunities

1. 🔜 CPU-only fallback mode
2. 🔜 Multi-GPU support
3. 🔜 Distributed cracking
4. 🔜 Custom rule generation
5. 🔜 Advanced wordlist analysis
6. 🔜 Portable executable
7. 🔜 Dark/Light theme toggle
8. 🔜 More archive formats
9. 🔜 Telegram bot control
10. 🔜 Web interface

---

## Documentation Files

1. **README.md** - Main comprehensive documentation
2. **QUICK_START.md** - 5-minute setup and usage guide
3. **PROJECT_MANIFEST.md** - This file, complete project overview

---

## Quality Metrics

✅ **Code Organization**

- Modular architecture
- Clear separation of concerns
- Reusable components

✅ **Error Handling**

- Try-catch blocks
- User-friendly error messages
- Graceful degradation

✅ **Logging**

- Debug logging throughout
- Log file persistence
- Console output

✅ **Threading**

- Non-blocking UI
- Safe worker threads
- Proper shutdown

✅ **UI/UX**

- Professional dark theme
- Intuitive workflow
- Real-time feedback
- Responsive controls

---

## Getting Started

1. **Installation**

   ```bash
   cd app
   pip install -r requirements.txt
   python install.bat
   ```

2. **Download Tools**
   - Hashcat: https://hashcat.net/hashcat/
   - John: https://github.com/openwall/john

3. **First Run**

   ```bash
   python main.py
   ```

4. **Select Archive** → **Extract Hash** → **Configure Attack** → **Start**

---

## Technical Highlights

- **Async Processing**: Non-blocking UI with QThread
- **Stream Parsing**: Real-time output parsing with regex
- **Session Persistence**: JSON-based state management
- **Modular Design**: Each component is independently testable
- **Error Recovery**: Graceful handling of tool failures
- **GPU Integration**: Direct Hashcat GPU acceleration
- **Professional UI**: PyQt6 with custom dark theme

---

**Project Status:** ✅ Complete MVP v1.0  
**Ready for:** Production use (with caution), Educational purposes, Security testing  
**Last Updated:** 2026-05-27  
**Maintainer:** AutoCrack Development Team

---
