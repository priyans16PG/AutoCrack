# AutoCrack GUI - Development Guide

## Architecture Overview

### Design Pattern: MVC + Threading

```
┌─────────────────────────────────────────────┐
│           GUI Layer (PyQt6)                 │
│    ┌──────────────────────────────────┐    │
│    │     MainWindow (MVC View)        │    │
│    │  - File Selection UI             │    │
│    │  - Progress Display              │    │
│    │  - Attack Controls               │    │
│    └──────────────────────────────────┘    │
│                    │                        │
│                    ▼                        │
│    ┌──────────────────────────────────┐    │
│    │    ProgressWidget, Dialogs       │    │
│    │    (Sub-components)              │    │
│    └──────────────────────────────────┘    │
└─────────────────────────────────────────────┘
            │                    │
            ▼                    ▼
    ┌──────────────────┐  ┌──────────────────┐
    │  Core Logic      │  │  CrackerThread   │
    │  (Models)        │  │  (Background)    │
    │  - Extractor     │  │  - Async Process │
    │  - Cleaner       │  │  - Output Parse  │
    │  - Detector      │  │  - State Mgmt    │
    │  - Cracker       │  │                  │
    │  - Parser        │  │                  │
    │  - Session       │  │                  │
    └──────────────────┘  └──────────────────┘
            │                    │
            └────────┬───────────┘
                     ▼
        ┌──────────────────────────┐
        │   External Tools         │
        │  - Hashcat (GPU)         │
        │  - John the Ripper       │
        │  - System (zip/rar)      │
        └──────────────────────────┘
```

## Module Dependencies

```
main.py (Entry Point)
    └── MainWindow (gui/main_window.py)
        ├── Theme (gui/theme.py)
        ├── ProgressWidget (gui/progress_widget.py)
        ├── SettingsDialog (gui/settings_dialog.py)
        └── Core Modules:
            ├── ArchiveExtractor (core/extractor.py)
            │   └── utils
            ├── HashCleaner (core/cleaner.py)
            ├── HashModeDetector (core/detector.py)
            ├── Cracker (core/cracker.py)
            │   └── HashcatOutputParser (core/parser.py)
            ├── SessionManager (core/session.py)
            │   └── utils
            └── utils (core/utils.py)
```

## Data Flow

### Attack Workflow

```
1. User selects archive file
   │
   ▼
2. ArchiveExtractor.extract_hash()
   └─ Runs: zip2john.exe or rar2john.exe
   │
   ▼
3. HashCleaner.clean_and_validate()
   └─ Removes prefixes, validates format
   │
   ▼
4. HashModeDetector.detect_and_get_mode()
   └─ Identifies hash type → Hashcat mode
   │
   ▼
5. User configures attack (mask, mode, etc.)
   │
   ▼
6. Cracker.start_attack()
   └─ Builds hashcat command, starts process
   │
   ▼
7. CrackerThread reads output
   │
   ▼
8. HashcatOutputParser.parse_status_line()
   │
   ▼
9. MainWindow.update_display()
   └─ Updates UI with statistics
   │
   ▼
10. Password found or attack stopped
```

## Extension Points

### Adding New Attack Modes

**File:** `core/cracker.py`

```python
def build_command(self, ...):
    # Add new mode handling
    elif self.attack_mode == '8':  # New mode
        cmd.append('--custom-option')
        cmd.append(custom_value)
```

### Adding New Hash Types

**File:** `core/detector.py`

```python
# Add to HASH_MODE_MAP
HASH_MODE_MAP = {
    'newtype': 12345,  # New hash type
}

# Add to HASH_PATTERNS
HASH_PATTERNS = {
    'newtype': r'^\$newtype\$',  # Pattern regex
}
```

### Adding New GUI Features

**File:** `gui/main_window.py` or new file

```python
# Create new dialog/widget
class NewFeatureDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

# Add to MainWindow
def show_new_feature(self):
    dialog = NewFeatureDialog(self)
    dialog.exec()
```

## Configuration Management

### Session Persistence

```json
{
  "session_id": "session_20260527_123456_789012",
  "archive_path": "C:\\path\\to\\archive.zip",
  "hash_file": "C:\\path\\to\\hash.txt",
  "hash_type": "pkzip2",
  "hash_mode": 17200,
  "attack_mode": "3",
  "mask": "?d?d?d?d",
  "increment": true,
  "status": "running",
  "progress": 45.5,
  "speed": "1.23G/s",
  "eta": 3600
}
```

### Logging

```
autocrack.log
    └─ Timestamps
    └─ Log Levels: DEBUG, INFO, WARNING, ERROR
    └─ Module names
    └─ Function calls
```

## Performance Optimization Tips

### 1. Hash Extraction

- Preprocess archives in parallel (future)
- Cache known hashes

### 2. Cracking

- Use GPU device selection wisely
- Monitor memory usage
- Implement early termination conditions

### 3. UI Responsiveness

- Keep heavy operations in threads
- Use queues for communication
- Don't update UI too frequently

### 4. Memory Management

- Clean temporary files regularly
- Use generators for large wordlists
- Monitor GPU VRAM usage

## Testing Strategy

### Unit Tests (Future)

```python
# Test each core module independently
- test_extractor.py
- test_cleaner.py
- test_detector.py
- test_parser.py
```

### Integration Tests (Future)

```python
# Test complete workflows
- test_full_crack_workflow.py
- test_session_persistence.py
```

### Manual Testing

1. Test with known passwords
2. Test error handling (missing tools, invalid archives)
3. Test UI responsiveness during cracking
4. Test pause/resume functionality

## Debugging

### Enable Debug Logging

```python
# In main.py or utils.py
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

**UI Freezes During Hash Extraction**

- Normal behavior (blocking operation)
- Future: Implement in separate thread

**Hashcat Not Found**

- Check: `tools/hashcat/hashcat.exe` exists
- Check: GPU drivers installed
- Check: Windows PATH (alternative)

**No GPU Detected**

- Check: NVIDIA GPU drivers
- Check: CUDA toolkit installed
- Check: GPU device ID correct

## Code Style Guidelines

### File Organization

```python
# 1. Imports
import sys
from pathlib import Path

# 2. Logging setup
logger = logging.getLogger(__name__)

# 3. Constants
CONSTANT_VALUE = 100

# 4. Classes
class MyClass:
    def __init__(self):
        pass

# 5. Functions
def my_function():
    pass

# 6. Main
if __name__ == '__main__':
    pass
```

### Naming Conventions

- **Classes:** PascalCase (`HashCleaner`, `ProgressWidget`)
- **Functions:** snake_case (`extract_hash()`, `update_display()`)
- **Constants:** UPPER_CASE (`HASH_MODE_MAP`, `BORDER_RADIUS`)
- **Private:** Leading underscore (`_read_output()`)

### Documentation

```python
def extract_hash(self, archive_path):
    """Extract hash from archive (auto-detect type)

    Args:
        archive_path (str/Path): Path to archive file

    Returns:
        str: Raw hash string

    Raises:
        FileNotFoundError: If archive not found
        ValueError: If unsupported format
    """
```

## Future Enhancement Roadmap

### Phase 2 (Next Version)

- [ ] Multi-GPU support
- [ ] Distributed cracking
- [ ] More archive formats (PDF, 7z, Office)
- [ ] Rule-based attacks
- [ ] Automatic wordlist generation
- [ ] Performance benchmarking tool

### Phase 3 (Enterprise)

- [ ] Web interface
- [ ] Telegram bot control
- [ ] Cloud integration
- [ ] Advanced analytics
- [ ] Distributed computing support
- [ ] API interface

### Phase 4 (AI Integration)

- [ ] Neural network prediction
- [ ] Pattern recognition
- [ ] Auto-mask suggestion
- [ ] Probability-based optimization

## Building Executable

### Using PyInstaller

```bash
pip install pyinstaller
pyinstaller --onefile --windowed \
    --icon=icon.ico \
    --add-data "tools:tools" \
    main.py
```

### Portable Build

```bash
# Include all dependencies in single folder
# Include tools/hashcat and tools/john
# Create standalone package
```

## Security Considerations

### Input Validation

- ✅ Archive path validation
- ✅ Hash format validation
- ✅ Command injection prevention (using subprocess)

### Future Improvements

- [ ] Sanitize user input more strictly
- [ ] Implement rate limiting
- [ ] Add permission checks
- [ ] Encrypt session files

## Performance Benchmarks

### Current Performance

```
Machine: NVIDIA RTX 3080
Mode: Brute Force, ?d?d?d?d
Time: ~0.05 seconds
Speed: 50+ billion/second

Expected scales:
- Longer passwords: Linear time increase
- Larger character sets: Exponential time increase
- Dictionary: Linear with wordlist size
```

### Optimization Opportunities

1. Batch hash operations
2. Parallel wordlist processing
3. GPU memory optimization
4. Caching frequently used hashes
5. Intelligent mask ordering

## Deployment

### System Requirements

- Windows 10/11 (64-bit)
- Python 3.12+
- NVIDIA GPU (optional, for acceleration)
- 4GB RAM minimum
- 1GB free disk space

### Installation Package

```
AutoCrack-GUI-1.0.0.zip
├── autocrack/
│   ├── app/
│   ├── README.md
│   ├── QUICK_START.md
│   └── ...
```

## Maintenance

### Regular Tasks

- [ ] Update dependencies monthly
- [ ] Review and fix bugs
- [ ] Update documentation
- [ ] Test with new Hashcat versions
- [ ] Monitor performance metrics

### Version Control

```
v1.0.0 - Initial Release
  ├── ZIP and RAR support
  ├── Multiple attack modes
  ├── GPU acceleration
  └── Real-time monitoring

v1.1.0 - Improvements (Next)
  ├── [ ] Multi-GPU support
  ├── [ ] More formats
  └── [ ] Performance gains
```

## Resources

### External Documentation

- PyQt6: https://doc.qt.io/qt-6/
- Hashcat: https://hashcat.net/wiki/
- John: https://www.openwall.com/john/doc/

### Developer Tools

- PyCharm IDE
- Qt Designer (for UI)
- GPUtil documentation
- psutil documentation

## Contact & Support

For questions about:

- **Core logic**: Check `core/` modules
- **UI design**: Check `gui/` modules
- **Deployment**: Check `install.bat`
- **Usage**: Check `README.md` or `QUICK_START.md`

---

**AutoCrack GUI Development Guide v1.0**  
Last Updated: 2026-05-27
