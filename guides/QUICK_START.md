# AutoCrack GUI - Quick Start Guide

## 5-Minute Setup

### 1. Installation

```bash
# Navigate to app directory
cd app

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Tools

Download these and place in correct folders:

- **Hashcat**: `tools/hashcat/hashcat.exe`
  - Download: https://hashcat.net/hashcat/
- **John the Ripper**: Extract binaries to `tools/john/run/`
  - Download: https://github.com/openwall/john
  - You need: `zip2john.exe`, `rar2john.exe`, `john.exe`

### 3. First Run

```bash
python main.py
```

## Quick Workflow

### Example: Crack a ZIP file with 4-digit PIN

1. **Select File**
   - Click "Browse" and select your password-protected ZIP file
   - Or drag & drop the file

2. **Extract Hash**
   - Click "Extract & Clean Hash"
   - Wait for completion (should show hash type)

3. **Configure Attack**
   - Mask: `?d?d?d?d` (for 4 digits)
   - Length: Min=4, Max=4
   - Mode: "Brute Force (Mask)"

4. **Start**
   - Click "▶ Start Attack"
   - Watch progress in real-time
   - Password will show when found

**Total Time**: ~1-2 seconds on modern GPU!

## Common Mask Patterns

| Pattern | Description       | Example        |
| ------- | ----------------- | -------------- |
| `?d`    | Any digit         | 5              |
| `?l`    | Lowercase letter  | a-z            |
| `?u`    | Uppercase letter  | A-Z            |
| `?s`    | Special character | !@#$%          |
| `?a`    | All characters    | Combo of above |

## Common Scenarios

### Scenario 1: 6-digit password

```
Mask: ?d?d?d?d?d?d
Min: 6, Max: 6
Time: ~2-5 minutes
```

### Scenario 2: 4-letter lowercase

```
Mask: ?l?l?l?l
Min: 4, Max: 4
Time: ~10-20 seconds
```

### Scenario 3: Mixed case with numbers

```
Mask: ?u?l?l?l?d?d
Min: 6, Max: 6
Time: ~5-15 minutes
```

### Scenario 4: Dictionary attack

```
Attack Mode: Dictionary
Select wordlist file
Time: Depends on wordlist size
```

## Tips for Success

✅ **Do:**

- Start with specific masks if you know password pattern
- Use shorter length ranges for faster results
- Enable increment mode for flexible length search
- Save/monitor your session

❌ **Don't:**

- Use overly broad character sets for long passwords
- Try cracking very long passwords with brute force
- Forget to select correct GPU device

## Keyboard Shortcuts

| Key     | Action       |
| ------- | ------------ |
| `Enter` | Start attack |
| `Space` | Pause/Resume |
| `ESC`   | Stop attack  |

## Performance

**Expected speeds on NVIDIA RTX 3080:**

- Numeric: 50+ billion attempts/second
- Lowercase: 10+ billion attempts/second
- Mixed: 1-2 billion attempts/second

**Calculation:**

- 4 digits = 10,000 possible combinations = <0.1 seconds
- 6 digits = 1,000,000 combinations = <0.05 seconds
- 8 digits = 100,000,000 combinations = ~2 seconds

## Troubleshooting

### No GPU detected

```
Solution: Install NVIDIA GPU drivers (CUDA toolkit)
https://developer.nvidia.com/cuda-downloads
```

### "Tool not found" error

```
Solution: Check that all executables are in tools/ folder
- tools/hashcat/hashcat.exe
- tools/john/run/zip2john.exe
- tools/john/run/rar2john.exe
```

### Archive shows no hash

```
Solution: Archive may not be password-protected
- Ensure you set a password when creating archive
- Try with a known password-protected file first
```

## Getting Help

1. Check main log file: `autocrack.log`
2. Review README.md for detailed information
3. Verify all tool paths are correct

## Next Steps

Once comfortable with basic workflow:

1. Explore "Advanced Settings" for more options
2. Try different attack modes
3. Create custom wordlists for targeted attacks
4. Learn more mask patterns and combinations

---

**Happy cracking! 🚀**
