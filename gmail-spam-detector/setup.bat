@echo off
REM Setup Script for Gmail Spam Detection System
REM This script automates the installation process

echo ============================================================
echo Gmail Spam Detection System - Setup Script
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/4] Python found
python --version

echo.
echo [2/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully!

echo.
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated!

echo.
echo [4/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Get credentials.json from Google Cloud Console
echo 2. Run: python setup_checker.py
echo 3. Run: python main.py
echo.
echo Virtual environment is activated. To deactivate, type: deactivate
echo.
pause
