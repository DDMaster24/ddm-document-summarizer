# Building Document Summarizer for Windows

This guide explains how to build a Windows installer for Document Summarizer.

## What You'll Get

After following these steps, you'll have:
- `DocumentSummarizerSetup.exe` - A professional Windows installer
- Users can download this file from your website
- Double-click to install → Creates desktop icon → No Python needed!

## Prerequisites

### Required (on Windows machine):
1. **Python 3.8+** - Download from https://python.org
2. **Git** (to clone the repo) - Or just download as ZIP

### Required for Installer (one-time setup):
3. **Inno Setup 6** - Download from https://jrsoftware.org/isdl.php
   - Free and open source
   - Creates professional Windows installers
   - Install with default settings

## Build Steps

### Option 1: Automated Build (Recommended)

1. Open Command Prompt or PowerShell in the project directory
2. Run the build script:
   ```cmd
   build_windows.bat
   ```
3. Wait 3-5 minutes for the build to complete
4. Find your installer at: `installer_output\DocumentSummarizerSetup.exe`

That's it! The script handles everything automatically.

### Option 2: Manual Build

If you want to understand each step:

#### Step 1: Setup Environment
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### Step 2: Create Icon
```cmd
python create_icon.py
```
This creates `icon.ico` (the app icon)

#### Step 3: Build Executable
```cmd
pyinstaller DocumentSummarizer.spec --clean
```
This creates `dist\DocumentSummarizer.exe` (standalone executable)

#### Step 4: Create Installer
```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```
This creates `installer_output\DocumentSummarizerSetup.exe` (the installer)

## Testing the Build

### Test the Executable (before creating installer)
1. Go to `dist\` folder
2. Double-click `DocumentSummarizer.exe`
3. System tray icon should appear
4. Browser should open automatically
5. Test the setup wizard and summarization

### Test the Installer
1. Go to `installer_output\`
2. Double-click `DocumentSummarizerSetup.exe`
3. Follow the installation wizard
4. Test the installed application

## Distributing Your App

Once you have `DocumentSummarizerSetup.exe`, you can:

1. **Upload to your website:**
   ```html
   <a href="downloads/DocumentSummarizerSetup.exe" download>
     Download Document Summarizer for Windows
   </a>
   ```

2. **File sharing services:**
   - Google Drive
   - Dropbox
   - Your own server

3. **GitHub Releases:**
   - Create a release on GitHub
   - Upload the installer as an asset

## What Users Will Experience

1. **Download** `DocumentSummarizerSetup.exe` from your website
2. **Run** the installer
3. **Click** through the installation wizard
4. **Choose** to create desktop icon (optional)
5. **Launch** the app from desktop or Start Menu
6. **Setup** their API key in the browser
7. **Start** summarizing documents!

## Customization

### Change App Name/Version
Edit `installer.iss`:
```iss
#define MyAppName "Your App Name"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Company"
#define MyAppURL "https://yourwebsite.com"
```

### Change App Icon
Replace `icon.ico` with your own icon, or modify `create_icon.py`

### Change Installation Location
Edit `installer.iss`:
```iss
DefaultDirName={autopf}\YourAppName
```

## Troubleshooting

### "Python not found"
- Install Python from python.org
- Make sure "Add Python to PATH" was checked during installation

### "Inno Setup not found"
- Download from https://jrsoftware.org/isdl.php
- Install with default settings
- Or manually compile using Inno Setup IDE

### "Module not found" errors
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

### Executable won't run
- Test on a different Windows machine
- Check Windows Defender / antivirus didn't block it
- Run from command line to see error messages:
  ```cmd
  dist\DocumentSummarizer.exe
  ```

### Large file size
- Normal! The executable includes Python and all libraries
- Typical size: 80-150 MB
- This is why users don't need Python installed

## File Structure After Build

```
document_summarizer/
├── dist/
│   └── DocumentSummarizer.exe    (Standalone executable)
├── build/                         (Build artifacts - can delete)
├── installer_output/
│   └── DocumentSummarizerSetup.exe (Final installer - distribute this!)
├── icon.ico                       (App icon)
├── icon.png                       (Icon preview)
└── ... (source files)
```

## Notes

- **Build on Windows**: Must build the Windows installer on a Windows machine
- **File size**: The installer will be ~80-150 MB (includes Python runtime)
- **No Python needed**: Users don't need Python installed
- **Portable**: Each installation is independent with its own config
- **Updates**: Build a new installer for each version update

## Support

If you encounter issues:
1. Check the error messages carefully
2. Make sure all prerequisites are installed
3. Try the manual build steps to see where it fails
4. Check that all source files are present
