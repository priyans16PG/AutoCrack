@echo off
REM AutoCrack Installation Script for Windows
REM This script helps set up AutoCrack

echo ======================================
echo   AutoCrack GUI - Installation
echo ======================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found!
    echo Please install Python 3.12+ from https://www.python.org/
    pause
    exit /b 1
)

echo [✓] Python found
echo.

REM Install Python dependencies
echo [*] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo [✓] Dependencies installed
echo.

REM Check for tools
echo [*] Checking external tools...

if not exist "tools\hashcat\hashcat.exe" (
    echo [!] Warning: hashcat.exe not found in tools\hashcat\
    echo    Please download from: https://hashcat.net/hashcat/
)

if not exist "tools\john\run\zip2john.exe" (
    echo [!] Warning: zip2john.exe not found in tools\john\run\
    echo    Please download John the Ripper Jumbo
)

if not exist "tools\john\run\rar2john.exe" (
    echo [!] Warning: rar2john.exe not found in tools\john\run\
    echo    Please download John the Ripper Jumbo
)

echo.
echo ======================================
echo   Installation Complete!
echo ======================================
echo.
echo Next steps:
echo 1. Download tools from:
echo    - Hashcat: https://hashcat.net/hashcat/
echo    - John: https://github.com/openwall/john
echo.
echo 2. Extract tools to:
echo    - tools\hashcat\hashcat.exe
echo    - tools\john\run\*.exe
echo.
echo 3. Run the application:
echo    python main.py
echo.
pause
