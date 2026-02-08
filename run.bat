@echo off
echo Starting Reddit Helper Helper...
python reddithelper.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start application
    echo Make sure you ran setup.bat first
    echo.
    pause
)