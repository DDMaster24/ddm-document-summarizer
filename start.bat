@echo off
REM Document Summarizer Startup Script for Windows

title Document Summarizer
color 0A

echo ==========================================
echo 📄 Document Summarizer Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed!
    echo Please install Python from https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
python --version
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
    echo.
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
if not exist "venv\.requirements_installed" (
    echo 📥 Installing required packages (this may take a few minutes)...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install packages
        pause
        exit /b 1
    )
    type nul > venv\.requirements_installed
    echo ✅ Packages installed successfully
    echo.
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  No .env file found!
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo ==========================================
    echo 🔑 IMPORTANT: API Key Setup Required
    echo ==========================================
    echo.
    echo 1. Go to: https://console.groq.com
    echo 2. Sign up for a FREE account
    echo 3. Create an API key
    echo 4. Open the .env file and paste your API key
    echo.
    echo The .env file is located in:
    echo %CD%\.env
    echo.
    echo Opening the .env file now...
    timeout /t 2 >nul
    notepad .env
    echo.
    pause
)

REM Start the application
echo.
echo ==========================================
echo 🚀 Starting Document Summarizer...
echo ==========================================
echo.
echo The browser will open automatically in a few seconds...
echo.

REM Open browser after a delay
timeout /t 3 >nul
start http://localhost:5000

REM Run the Flask app
python app.py

REM Deactivate virtual environment on exit
call venv\Scripts\deactivate.bat

pause
