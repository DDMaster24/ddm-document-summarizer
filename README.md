# 📄 Document Summarizer

A simple, user-friendly application that helps you quickly summarize documents and text using AI. Perfect for researchers, students, and anyone who needs to digest large amounts of text quickly!

## Features

- **Multiple Input Methods**:
  - Upload PDF files
  - Upload Word documents (.docx)
  - Upload text files (.txt)
  - Copy and paste text directly
  - Type text manually

- **Flexible Output**:
  - Download summaries as PDF
  - Download summaries as Word documents

- **Easy to Use**:
  - Clean, intuitive interface
  - Drag-and-drop file upload
  - Large buttons and text (elderly-friendly)
  - Works in your web browser

- **Fast & Free**:
  - Uses Groq AI (free tier)
  - Processes documents in seconds
  - No heavy processing on your computer
  - 30 free requests per minute

## Requirements

- Python 3.8 or higher
- Internet connection (for AI processing)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Quick Start

### For Windows Users

1. **Download the project** to your computer
2. **Double-click** `start.bat`
3. Follow the on-screen instructions
4. Your browser will open automatically!

### For Mac/Linux Users

1. **Download the project** to your computer
2. **Double-click** `start.sh` (or run `./start.sh` in terminal)
3. Follow the on-screen instructions
4. Your browser will open automatically!

## First-Time Setup

### Step 1: Get Your Free API Key

1. Go to [https://console.groq.com](https://console.groq.com)
2. Click "Sign Up" to create a free account
3. After logging in, click "API Keys" in the left menu
4. Click "Create API Key"
5. Give it a name (e.g., "Document Summarizer")
6. Copy the API key that appears

### Step 2: Configure the Application

1. When you first run the startup script, it will create a `.env` file
2. Open the `.env` file (it will open automatically on Windows)
3. Replace `your_groq_api_key_here` with your actual API key
4. Save the file

Your `.env` file should look like this:
```
GROQ_API_KEY=gsk_abc123xyz...
```

### Step 3: Run the Application

1. Run the startup script again (`start.bat` or `start.sh`)
2. Wait for the browser to open
3. You're ready to summarize documents!

## How to Use

1. **Choose Your Input**:
   - **Option 1**: Drag and drop a file, or click "Choose File"
   - **Option 2**: Paste or type text in the text area

2. **Select Output Format**:
   - Click PDF or Word icon

3. **Click "Summarize Document"**:
   - Wait a few seconds for the AI to process
   - The summary will appear on screen

4. **Download Your Summary**:
   - Click the "Download Summary" button
   - The file will download to your computer

## Tips for Best Results

- **Document Length**: Works best with documents up to 6,000 words
- **Longer Documents**: For very long documents, the text may be truncated (you'll see a notice)
- **File Quality**: Make sure PDFs have readable text (not just images)
- **Clear Text**: Better quality input = better quality summary

## Troubleshooting

### "Python is not installed"
- Download Python from [https://www.python.org/downloads/](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"

### "Failed to install packages"
- Make sure you have an internet connection
- Try running the startup script again
- If problems persist, run: `pip install -r requirements.txt`

### "Groq API key not configured"
- Make sure you created a `.env` file
- Check that your API key is correct (no extra spaces)
- Make sure the file is named `.env` (not `.env.txt`)

### "Error calling Groq API"
- Check your internet connection
- Make sure your API key is valid
- You might have hit the rate limit (wait a minute and try again)

### "Could not extract text from PDF"
- The PDF might be image-based (scanned document)
- Try converting it to a text-based PDF first
- Or copy the text manually into the text area

### Browser doesn't open automatically
- Manually open your browser and go to: `http://localhost:5000`

## Manual Installation (Alternative Method)

If the startup scripts don't work, you can set up manually:

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env and add your Groq API key

# 5. Run the application
python app.py

# 6. Open browser to http://localhost:5000
```

## Stopping the Application

- Press `Ctrl+C` in the terminal/command prompt
- Or simply close the terminal window

## About Groq

Groq is a fast AI platform that provides free API access:
- **Free Tier**: 30 requests per minute (plenty for personal use!)
- **Fast**: Responses in 2-3 seconds
- **High Quality**: Uses advanced Llama AI models
- **No Credit Card**: Free tier doesn't require payment info

## Privacy & Security

- Your documents are sent to Groq's servers for processing
- Groq's privacy policy: [https://groq.com/privacy-policy/](https://groq.com/privacy-policy/)
- For sensitive documents, consider using a local AI solution (contact developer)
- Files are temporarily stored on your computer and deleted after processing

## Project Structure

```
document_summerizer/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                   # API key configuration (you create this)
├── .env.example          # Template for .env file
├── start.sh              # Startup script for Mac/Linux
├── start.bat             # Startup script for Windows
├── templates/
│   └── index.html        # Web interface
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── script.js     # Frontend logic
├── uploads/              # Temporary file storage (auto-created)
└── outputs/              # Generated summaries (auto-created)
```

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Make sure you followed all setup steps
3. Check that Python and all dependencies are installed
4. Verify your Groq API key is correct

## Future Enhancements

Potential features for future versions:
- Support for more file formats (RTF, EPUB, etc.)
- Batch processing multiple documents
- Summary length customization
- Multiple language support
- Offline mode with local AI models

## License

This project is created for personal use. Feel free to modify and share!

---

Made with ❤️ for Grandpa | Powered by [Groq AI](https://groq.com)

