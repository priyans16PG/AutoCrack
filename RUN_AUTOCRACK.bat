@echo off
REM AutoCrack GUI Launcher
REM Starts the application with proper configuration

cd /d "%~dp0"
cd app

echo ============================================
echo   AutoCrack GUI - Archive Password Recovery
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found!
    echo Please install Python 3.12+
    pause
    exit /b 1
)

REM Run the application
echo Starting AutoCrack GUI...
python main.py

if errorlevel 1 (
    echo.
    echo Error: Application failed to start
    pause
)
