@echo off
echo =====================================
echo Reddit Helper Helper - Quick Setup
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✓ Python found
python --version

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Check if installation was successful
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Try running: pip install --upgrade pip
    pause
    exit /b 1
)

echo.
echo ✓ Dependencies installed successfully!
echo.
echo =====================================
echo Setup Complete!
echo =====================================
echo.
echo To run the application:
echo   python reddithelper.py
echo.
echo Or double-click: run.bat
echo.
pause