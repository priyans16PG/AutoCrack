# AutoCrack GUI - Archive Password Recovery

A professional Python desktop application for automating archive password recovery using John the Ripper Jumbo and Hashcat.

## Features

✅ **Archive Support**

- ZIP files (.pkzip2 format)
- RAR files (RAR3 and RAR5)
- 7z support (future)

✅ **Automatic Hash Extraction**

- Uses `zip2john` for ZIP archives
- Uses `rar2john` for RAR archives
- Automatic format detection

✅ **Intelligent Hash Processing**

- Automatic hash cleaning and validation
- Hash type detection
- Correct Hashcat mode selection

✅ **Multiple Attack Modes**

- Brute Force (Mask Attack)
- Dictionary (Wordlist)
- Hybrid (Dictionary + Mask)
- Increment Mode support

✅ **Real-Time Monitoring**

- Live speed display
- Progress tracking with percentage
- ETA calculation
- GPU temperature monitoring
- GPU utilization display

✅ **Attack Control**

- Start/Pause/Resume/Stop controls
- Session management and restoration
- GPU device selection

✅ **Professional UI**

- Dark modern theme with red accents
- Drag & drop file support
- Console output with colored logging
- Real-time statistics display

## System Requirements

### Hardware

- NVIDIA GPU (recommended for GPU acceleration)
- 4GB+ RAM
- 1GB+ free disk space

### Software

- Windows 10/11
- Python 3.12+
- Hashcat (included)
- John the Ripper Jumbo (included)

## Installation

### 1. Clone/Download the Project

```bash
git clone <repository>
cd autocrack/app
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install External Tools

#### Option A: Automated Download

Place these executables in the `tools/` directory:

- `tools/hashcat/hashcat.exe`
- `tools/john/run/zip2john.exe`
- `tools/john/run/rar2john.exe`
- `tools/john/run/john.exe`

#### Option B: Manual Setup

1. Download Hashcat from: https://hashcat.net/hashcat/
2. Download John the Ripper from: https://github.com/openwall/john
3. Extract executables to the appropriate folders

### 4. Run the Application

```bash
python main.py
```

## Usage Guide

### Basic Workflow

#### 1. **Select Archive**

- Click "Browse" button or drag & drop an archive file
- Supported formats: `.zip`, `.rar`, `.7z`
- File metadata will be displayed

#### 2. **Extract Hash**

- Click "Extract & Clean Hash" button
- Application will:
  - Detect archive type
  - Extract password hash using john tools
  - Clean and validate the hash
  - Identify hash type and Hashcat mode

#### 3. **Configure Attack**

- **Attack Mode**: Select from:
  - Brute Force (Mask) - Default
  - Dictionary (Wordlist)
  - Hybrid attacks
- **Mask Configuration**:
  - Use preset masks (Numeric, Lowercase, etc.)
  - Or enter custom mask
  - Set password length range
  - Enable/disable increment mode

#### 4. **Start Attack**

- Click "▶ Start Attack"
- Monitor progress in real-time:
  - Attack speed
  - Progress percentage
  - Time estimate
  - GPU stats

#### 5. **Control Attack**

- **Pause**: ⏸ Temporarily suspend the attack
- **Resume**: ▶ Continue from where paused
- **Stop**: ⏹ Terminate the attack

### Attack Modes Explained

#### Brute Force (Mask Attack)

Most common for quick recovery of numeric/simple passwords.

**Mask Syntax:**

- `?d` - Digit (0-9)
- `?l` - Lowercase (a-z)
- `?u` - Uppercase (A-Z)
- `?s` - Special characters
- `?a` - All characters
- `?h` - Hex (0-9a-f)
- `?b` - Byte (all 256)

**Examples:**

```
?d?d?d?d          # 4 digits (0000-9999)
?u?l?l?l?d?d      # Uppercase + 3 lowercase + 2 digits
hiii?d?d          # Literal "hiii" + 2 digits
```

**Length Control:**

- Min Length: 4
- Max Length: 8
- With Increment: Tries lengths 4, 5, 6, 7, 8

#### Dictionary Attack

Best for common passwords or when using word lists.

1. Select wordlist file
2. Hashcat will try each word

#### Hybrid Attacks

Combine dictionary with mask attack.

**Dict + Mask**: Appends mask patterns to dictionary words
**Mask + Dict**: Prepends mask patterns to dictionary words

### Advanced Settings

Click "Advanced Settings..." for more options:

- GPU Device Selection
- Custom rules
- Session management

## File Structure

```
autocrack/
├── app/
│   ├── main.py                 # Entry point
│   ├── requirements.txt         # Python dependencies
│   │
│   ├── tools/
│   │   ├── hashcat/
│   │   │   └── hashcat.exe
│   │   └── john/run/
│   │       ├── zip2john.exe
│   │       ├── rar2john.exe
│   │       └── john.exe
│   │
│   ├── core/
│   │   ├── extractor.py        # Hash extraction
│   │   ├── cleaner.py          # Hash cleaning
│   │   ├── detector.py         # Hash type detection
│   │   ├── cracker.py          # Cracking engine
│   │   ├── parser.py           # Output parsing
│   │   ├── session.py          # Session management
│   │   └── utils.py            # Utilities
│   │
│   ├── gui/
│   │   ├── main_window.py      # Main window
│   │   ├── progress_widget.py  # Progress display
│   │   ├── settings_dialog.py  # Settings dialog
│   │   └── theme.py            # Theme/styling
│   │
│   ├── hashes/                 # Extracted hashes
│   ├── sessions/               # Session data
│   ├── wordlists/              # Wordlist files
│   └── temp/                   # Temporary files
```

## Hash Types and Modes

| Format          | Type     | Hashcat Mode | Support    |
| --------------- | -------- | ------------ | ---------- |
| RAR5            | $rar5$   | 13000        | ✅ Full    |
| RAR3            | $rar3$   | 13100        | ✅ Full    |
| ZIP (PKWARE)    | $pkzip2$ | 17200        | ✅ Full    |
| ZIP (Encrypted) | $zip$    | 23001        | ⚠️ Limited |
| PDF             | $pdf$    | 10500        | 🔜 Soon    |
| 7z              | $7z$     | 11600        | 🔜 Soon    |

## Performance Tips

### GPU Optimization

1. Ensure NVIDIA GPU drivers are updated
2. Select correct GPU device (usually 1)
3. Use GPU acceleration for faster cracking

### Mask Selection

1. Use specific masks for known patterns
2. Start with shorter length ranges
3. Use increment mode for progressive search

### Wordlist Selection

1. Use curated wordlists for known words
2. Common passwords lists are most effective
3. Combine with mask for hybrid attacks

## Troubleshooting

### Error: "Hashcat not found"

- Ensure `tools/hashcat/hashcat.exe` exists
- Check NVIDIA GPU drivers are installed
- Verify Hashcat is compatible with your GPU

### Error: "zip2john/rar2john not found"

- Ensure `tools/john/run/` contains all john executables
- Download John the Ripper Jumbo and extract binaries

### GUI Not Responding

- This is normal during hash extraction
- Application uses threading for non-blocking operations
- Wait for operation to complete

### Password Not Found

- Try different mask patterns
- Verify archive is password-protected
- Check if hash was properly extracted

### GPU Not Detected

- Install NVIDIA GPU drivers
- Ensure GPU is CUDA-capable
- Check GPU device ID in settings

## Supported Password Patterns

### Numeric

- 4-digit PIN: `?d?d?d?d`
- 6-digit code: `?d?d?d?d?d?d`

### Alphanumeric

- Lowercase: `?l?l?l?l?l?l`
- Uppercase: `?u?u?u?u`
- Mixed: `?u?l?l?l?d?d`

### With Literals

- WiFi pattern: `WiFi?d?d?d?d`
- Custom prefix: `MyPass?d?d?d`

## Known Limitations

1. Only NVIDIA GPU supported (CPU mode available but slow)
2. Requires Hashcat 6.2+ for GPU acceleration
3. Some complex RAR files may not be supported
4. Limited to symmetric encryption

## Future Features

- 🔜 Telegram bot control
- 🔜 Remote cracking support
- 🔜 Distributed cracking
- 🔜 AI password prediction
- 🔜 Automatic rule generation
- 🔜 More archive formats (PDF, Office)
- 🔜 Portable executable build

## FAQ

**Q: Is this legal?**
A: Yes, if used on your own files. Only use on archives you own or have permission to crack.

**Q: How fast will it crack?**
A: Speed depends on GPU and password complexity. NVIDIA GPUs can try billions of combinations per second.

**Q: Can I use CPU instead of GPU?**
A: Yes, modify `device_id` in settings, but GPU is much faster.

**Q: What if password contains special characters?**
A: Use `?s` for special characters or `?a` for all characters.

**Q: Can I save my progress?**
A: Yes, sessions are automatically saved and can be resumed.

## Performance Benchmarks

### NVIDIA RTX 3080

- Numeric (4 digits): < 1 second
- Alphanumeric (6 chars): ~2-3 seconds
- Complex (8+ chars): 1-10 minutes

### NVIDIA GTX 1080

- Numeric (4 digits): < 1 second
- Alphanumeric (6 chars): ~5 seconds
- Complex (8+ chars): 5-20 minutes

_Note: Times vary based on GPU generation and password entropy_

## Credits

Built with:

- **PyQt6** - GUI Framework
- **Hashcat** - GPU Password Cracking
- **John the Ripper** - Hash extraction & CPU cracking
- **Python 3.12+** - Programming Language

## License

This project is provided as-is for educational and authorized security testing purposes.

## Support

For issues or questions:

1. Check the Troubleshooting section
2. Review logs in `autocrack.log`
3. Verify tool versions and GPU compatibility

## Version History

### v1.0.0 (Initial Release)

- ZIP and RAR support
- Multiple attack modes
- GPU acceleration
- Real-time monitoring
- Session management

---

**AutoCrack GUI v1.0.0** - Archive Password Recovery Made Easy
