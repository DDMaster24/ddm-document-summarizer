# Quick Setup Guide for Grandpa 👴

## What You Need

1. A computer with internet
2. 10 minutes of time
3. This folder on your computer

## Step-by-Step Setup (First Time Only)

### Step 1: Install Python (If You Don't Have It)

1. Go to: **https://www.python.org/downloads/**
2. Click the big yellow "Download Python" button
3. Run the installer
4. **IMPORTANT**: Check the box that says "Add Python to PATH"
5. Click "Install Now"
6. Wait for it to finish, then click "Close"

### Step 2: Get Your Free AI Key

1. Go to: **https://console.groq.com**
2. Click "Sign Up" (it's free!)
3. Fill in your email and create a password
4. Check your email and verify your account
5. After logging in, click "API Keys" on the left side
6. Click the "Create API Key" button
7. Give it a name like "My Summarizer"
8. **Copy the key** that appears (it looks like: gsk_abc123xyz...)
9. Keep this window open, you'll need this key in a moment

### Step 3: Start the Application

**On Windows:**
- Find the file called `start.bat` in this folder
- Double-click it

**On Mac:**
- Find the file called `start.sh` in this folder
- Double-click it

### Step 4: Add Your API Key

1. A file will open (called `.env`)
2. You'll see: `GROQ_API_KEY=your_groq_api_key_here`
3. Replace `your_groq_api_key_here` with the key you copied
4. It should look like: `GROQ_API_KEY=gsk_abc123xyz...`
5. Save the file (File → Save)
6. Close the file

### Step 5: Start Again

- Run `start.bat` (Windows) or `start.sh` (Mac) again
- Your web browser will open automatically
- You're done with setup!

## How to Use (Every Time)

### Starting the Application

1. Double-click `start.bat` (Windows) or `start.sh` (Mac)
2. Wait for your browser to open
3. You'll see the Document Summarizer page

### Summarizing a Document

1. **Upload a file**:
   - Drag and drop your PDF or Word file
   - OR click "Choose File" to select it

2. **Or paste text**:
   - Click in the big text box
   - Paste your text (Ctrl+V or Cmd+V)

3. **Choose your output**:
   - Click PDF or Word (whichever you prefer)

4. **Click "Summarize Document"**
   - Wait a few seconds
   - Your summary will appear!

5. **Download your summary**:
   - Click the "Download Summary" button
   - The file will be in your Downloads folder

### Stopping the Application

- Close the black/terminal window that appeared
- OR press Ctrl+C in that window

## Common Questions

**Q: Do I need to do the setup every time?**
A: No! Setup is only needed the first time. After that, just double-click `start.bat` or `start.sh`

**Q: Will this cost money?**
A: No! Groq gives you 30 free summaries per minute. That's plenty for your needs!

**Q: Do I need internet?**
A: Yes, the AI processing happens online. But your files stay private!

**Q: What files can I use?**
A: PDF, Word documents (.docx), and text files (.txt)

**Q: Can I use this offline?**
A: Not with the current setup, but we can add that later if needed!

**Q: Where do my summaries go?**
A: They download to your Downloads folder, just like any other download!

## Need Help?

If something doesn't work:
1. Make sure you have internet
2. Check that you copied the API key correctly (no extra spaces!)
3. Try closing everything and starting again
4. Call me, and I'll help you!

---

Remember: After the first-time setup, you just need to:
1. Double-click the start file
2. Upload your document
3. Click summarize
4. Download your summary

That's it! Easy as pie! 🥧
