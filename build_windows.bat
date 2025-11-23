@echo off
REM Build script for Document Summarizer Windows Installer
REM This script automates the entire build process

echo ============================================
echo  Building Document Summarizer for Windows
echo ============================================
echo.

REM Step 1: Check if Python is installed
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)
echo    OK: Python found
echo.

REM Step 2: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [2/6] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo    OK: Virtual environment created
) else (
    echo [2/6] Virtual environment already exists
)
echo.

REM Step 3: Activate virtual environment and install dependencies
echo [3/6] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo    OK: Dependencies installed
echo.

REM Step 4: Generate icon
echo [4/6] Generating application icon...
if not exist "icon.ico" (
    python create_icon.py
    if errorlevel 1 (
        echo ERROR: Failed to create icon
        pause
        exit /b 1
    )
) else (
    echo    OK: Icon already exists
)
echo.

REM Step 5: Build executable with PyInstaller
echo [5/6] Building executable with PyInstaller...
echo    This may take a few minutes...
pyinstaller DocumentSummarizer.spec --clean --noconfirm
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)
echo    OK: Executable built successfully
echo.

REM Step 6: Check for Inno Setup and build installer
echo [6/6] Building Windows installer...
set INNO_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if exist %INNO_PATH% (
    %INNO_PATH% installer.iss
    if errorlevel 1 (
        echo ERROR: Inno Setup build failed
        pause
        exit /b 1
    )
    echo.
    echo ============================================
    echo  BUILD SUCCESSFUL!
    echo ============================================
    echo.
    echo Installer location:
    echo %CD%\installer_output\DocumentSummarizerSetup.exe
    echo.
    echo You can now:
    echo 1. Test the installer on your machine
    echo 2. Upload it to your website for distribution
    echo.
) else (
    echo.
    echo WARNING: Inno Setup not found at %INNO_PATH%
    echo.
    echo The executable has been built successfully at:
    echo %CD%\dist\DocumentSummarizer.exe
    echo.
    echo To create the installer:
    echo 1. Download Inno Setup from: https://jrsoftware.org/isdl.php
    echo 2. Install it
    echo 3. Run this script again OR
    echo 4. Open installer.iss in Inno Setup and click "Compile"
    echo.
)

pause
