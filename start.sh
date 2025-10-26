#!/bin/bash

# Document Summarizer Startup Script for Mac/Linux

echo "=========================================="
echo "📄 Document Summarizer Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if [ ! -f "venv/.requirements_installed" ]; then
    echo "📥 Installing required packages (this may take a few minutes)..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install packages"
        read -p "Press Enter to exit..."
        exit 1
    fi
    touch venv/.requirements_installed
    echo "✅ Packages installed successfully"
    echo ""
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "=========================================="
    echo "🔑 IMPORTANT: API Key Setup Required"
    echo "=========================================="
    echo ""
    echo "1. Go to: https://console.groq.com"
    echo "2. Sign up for a FREE account"
    echo "3. Create an API key"
    echo "4. Open the .env file and paste your API key"
    echo ""
    echo "The .env file is located in:"
    echo "$(pwd)/.env"
    echo ""
    read -p "Press Enter once you've added your API key..."
fi

# Start the application
echo ""
echo "=========================================="
echo "🚀 Starting Document Summarizer..."
echo "=========================================="
echo ""

# Open browser after a delay
(sleep 3 && python3 -m webbrowser http://localhost:5000) &

# Run the Flask app
python3 app.py

# Deactivate virtual environment on exit
deactivate
