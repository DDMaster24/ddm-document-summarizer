# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working Preferences

**DO NOT create .md or guide files.** If the user needs to do something manually (configuration, setup steps, etc.), communicate it directly in the chat. Act as a side assistant, not a documentation generator.

## Project Overview

A Flask-based web application that summarizes documents (PDF, DOCX, TXT) or pasted text using AI APIs (primarily Google Gemini). Outputs summaries as downloadable PDF or Word documents.

**Target Audience**: Designed for ease of use, including elderly users (large buttons, simple interface).

**Key Feature**: Multi-provider API key management with setup wizard and settings page for easy configuration.

## Development Setup

### Initial Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
# OR use the startup script
./start.sh  # Linux/Mac
```

**First-time users** will be redirected to a setup wizard in the browser to configure their API key.

### Running the Application

**As Web App (Development):**
```bash
# Linux/WSL
./start.sh

# Or manually
source venv/bin/activate
python app.py
```

**As Desktop App (Production):**
```bash
python desktop_launcher.py
```
- Runs in system tray
- Auto-opens browser
- No console window

Application runs on `http://localhost:5000`

## Building Windows Installer

The application can be packaged as a professional Windows desktop app with installer.

### Quick Build (Windows only)

```cmd
build_windows.bat
```

This creates `DocumentSummarizerSetup.exe` that users can download and install.

### What You Need (One-time setup)
- Python 3.8+
- Inno Setup 6 (free): https://jrsoftware.org/isdl.php

### Build Output
- `dist/DocumentSummarizer.exe` - Standalone executable
- `installer_output/DocumentSummarizerSetup.exe` - Installer to distribute

See `BUILD_README.md` for detailed build instructions.

## Architecture

### Multi-Module Architecture

The application is split into multiple modules for better maintainability:

**app.py** - Main Flask application with routes and document processing
**api_manager.py** - API key storage and management (stores in config.json)
**ai_providers.py** - AI provider abstraction layer (Gemini, Groq)
**desktop_launcher.py** - Desktop app wrapper with system tray functionality (for Windows build)

### Core Components

1. **API Key Management System** (api_manager.py):
   - Stores multiple API keys in `config.json` (base64 encoded)
   - Supports multiple providers (Gemini, Groq)
   - Tracks default provider
   - Provides key preview masking for security

2. **AI Provider Abstraction** (ai_providers.py):
   - `GeminiProvider`: Uses Google's Gemini 1.5 Flash model (recommended)
   - `GroqProvider`: Legacy support for Groq's llama model
   - `get_provider()`: Factory function to instantiate providers
   - Each provider implements `summarize()` and `test_connection()` methods

3. **Text Extraction Pipeline** (app.py):
   - `extract_text_from_pdf()`: Uses pdfplumber (primary) with PyPDF2 fallback
   - `extract_text_from_docx()`: Extracts from Word documents
   - `extract_text_from_txt()`: Reads plain text files
   - `extract_text()`: Router function based on file extension

4. **Output Generation** (app.py):
   - `create_pdf_output()`: Uses ReportLab to generate formatted PDFs
   - `create_docx_output()`: Creates Word documents using python-docx

### Flask Routes

**User-Facing Routes:**
- `GET /`: Main interface (redirects to /setup if not configured)
- `GET /setup`: Setup wizard for first-time configuration
- `GET /settings`: Settings page to manage API keys
- `POST /summarize`: Process document/text and return summary
- `GET /download/<filename>`: Download generated summary file

**API Routes (used by frontend):**
- `POST /api/test-key`: Validate an API key
- `POST /api/setup`: Save initial configuration
- `GET /api/providers`: List configured providers
- `POST /api/add-provider`: Add new provider/API key
- `POST /api/remove-provider`: Remove a provider
- `POST /api/set-default`: Set default provider
- `GET /health`: Health check endpoint

### Request Flows

**First-Time Setup Flow:**
```
User starts app → No config.json → Redirect to /setup
    ↓
User selects provider (Gemini/Groq)
    ↓
User enters API key
    ↓
POST /api/test-key (validates key)
    ↓
POST /api/setup (saves to config.json)
    ↓
Redirect to main app
```

**Summarization Flow:**
```
User uploads file/pastes text
    ↓
POST /summarize
    ↓
Extract text (if file)
    ↓
Get default provider from config.json
    ↓
Call AI provider's summarize() method
    ↓
Generate PDF/DOCX output
    ↓
Return summary + download filename
    ↓
User clicks download → GET /download/<filename>
```

### File System

- `uploads/`: Temporary storage for uploaded files (cleaned up after processing)
- `outputs/`: Generated summary files (cleaned on startup via cleanup_folders())
- `config.json`: Stores API keys and provider configuration (NOT in git)
- Files are cleaned up immediately after text extraction to save space

### Frontend Structure

- `templates/index.html`: Main UI (drag-drop, text input, format selection)
- `templates/setup.html`: Setup wizard for first-time configuration
- `templates/settings.html`: Settings page for managing API keys
- `static/css/style.css`: Styling (large buttons for accessibility)
- `static/js/script.js`: Client-side file handling and AJAX requests

## Key Configuration

- **Max file size**: 16MB (app.config['MAX_CONTENT_LENGTH'])
- **Supported formats**: PDF, DOCX, DOC, TXT
- **Default AI Provider**: Gemini 1.5 Flash (recommended)
  - Model: gemini-1.5-flash
  - Free tier: 15 requests/minute, 1M tokens/day
  - Input truncation: 30,000 characters
- **Alternative Provider**: Groq
  - Model: llama-3.1-70b-versatile
  - Free tier: 30 requests/minute
  - Input truncation: 24,000 characters
- **Minimum text length**: 50 characters

## Important Notes

- **No .env file needed**: API keys are managed through the web UI and stored in `config.json`
- **Multi-provider support**: Can configure multiple AI providers and switch between them
- **Portable**: Each installation has its own `config.json`, making it easy to deploy on multiple machines
- **Security**: API keys are base64 encoded in config.json (add config.json to .gitignore)
- **Privacy**: Documents are sent to the selected AI provider's servers for processing
- Files are deleted after processing; summaries are cleaned on restart
- The setup wizard will automatically appear on first launch if no config exists
