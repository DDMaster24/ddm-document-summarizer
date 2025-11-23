# GitHub Actions Build Guide

This guide explains how to use GitHub Actions to automatically build Windows installers in the cloud.

## 🎯 What This Does

GitHub Actions will automatically:
1. ✅ Spin up a fresh Windows machine in the cloud
2. ✅ Install Python and all dependencies
3. ✅ Build your executable with PyInstaller
4. ✅ Create a professional installer with Inno Setup
5. ✅ Give you the finished `.exe` file to download

**No Windows machine needed on your end!** GitHub does all the work.

## 📋 Two Workflows Included

### 1. **Build Workflow** (`build-windows.yml`)
- Triggers: Every push to `main` or `master` branch
- Also: Manual trigger button in GitHub UI
- Creates: Build artifacts you can download

### 2. **Release Workflow** (`release.yml`)
- Triggers: When you create a version tag (e.g., `v1.0.0`)
- Creates: Public GitHub Release with installer attached
- Perfect for: Distributing to users

## 🚀 Quick Start

### First Time Setup

1. **Make sure your code is ready:**
   ```bash
   cd /home/darius/Projects/pdf-summarizer/document_summerizer
   git status
   ```

2. **Add and commit everything:**
   ```bash
   git add .
   git commit -m "Add GitHub Actions workflows for Windows build"
   ```

3. **Push to GitHub:**
   ```bash
   git push origin main
   ```

4. **Watch the magic happen:**
   - Go to https://github.com/DDMaster24/document_summerizer
   - Click the **"Actions"** tab
   - You'll see the workflow running (yellow circle 🟡)
   - Wait 5-10 minutes for it to complete (green checkmark ✅)

5. **Download your installer:**
   - Click on the completed workflow
   - Scroll to bottom → **Artifacts** section
   - Download `DocumentSummarizer-Windows-Installer`
   - Unzip it → You have `DocumentSummarizerSetup.exe`!

## 📦 Creating Official Releases

When you're ready to publish a version for users:

### Option 1: Command Line

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

### Option 2: GitHub UI

1. Go to your repo → **Releases**
2. Click **"Create a new release"**
3. Click **"Choose a tag"** → Type `v1.0.0` → **"Create new tag"**
4. Click **"Publish release"**

### What Happens Next:

1. GitHub Actions starts building (5-10 min)
2. A new **Release** appears with:
   - Version number (v1.0.0)
   - Release notes (auto-generated)
   - **`DocumentSummarizerSetup.exe`** attached
3. Users can download directly from your Releases page!

## 📥 Where Users Download From

After creating a release, share this link:

```
https://github.com/DDMaster24/document_summerizer/releases/latest
```

Users will see a big download button for `DocumentSummarizerSetup.exe`

## 🔧 Manual Trigger (Testing)

Want to test the build without pushing code?

1. Go to your repo → **Actions** tab
2. Click **"Build Windows Installer"** (left sidebar)
3. Click **"Run workflow"** button (right side)
4. Click the green **"Run workflow"** button
5. Wait for it to complete
6. Download the artifact

## 📊 Understanding the Build Process

### What Happens in GitHub's Cloud:

```
1. 🖥️  GitHub spins up Windows Server 2022
2. 🐍 Installs Python 3.11
3. 📦 Installs your dependencies (Flask, Gemini, etc.)
4. 🎨 Generates the app icon
5. 🔨 Runs PyInstaller → Creates DocumentSummarizer.exe
6. 📋 Installs Inno Setup
7. 📦 Runs Inno Setup → Creates DocumentSummarizerSetup.exe
8. ✅ Uploads the installer for you to download
9. 🗑️  Destroys the virtual machine
```

**Total time:** 5-10 minutes
**Cost to you:** $0 (GitHub Actions is free for public repos!)

## 🎯 Workflow Triggers

### Build Workflow Triggers On:
- ✅ Push to `main` or `master` branch
- ✅ Pull requests to `main` or `master`
- ✅ Manual button click (workflow_dispatch)

### Release Workflow Triggers On:
- ✅ Creating a tag like `v1.0.0`, `v2.1.3`, etc.

## 💡 Pro Tips

### Versioning Strategy

```bash
# First release
git tag v1.0.0

# Bug fix
git tag v1.0.1

# New feature
git tag v1.1.0

# Major update
git tag v2.0.0
```

### Test Before Release

1. Push to `main` → Download artifact → Test installer
2. If it works → Create release tag
3. Users get the tested installer

### Private Repo?

If your repo is private:
- GitHub Actions is free for 2,000 minutes/month
- Each build takes ~10 minutes
- = ~200 builds/month for free

## 🔍 Troubleshooting

### "Workflow not running?"

Check:
- Did you push to the `main` or `master` branch?
- Is the `.github/workflows/` folder in your repo?
- Are the YAML files there?

### "Build failed?"

1. Click on the failed workflow
2. Click on the failed step (red X)
3. Read the error message
4. Common issues:
   - Missing file: Add it to git
   - Syntax error in Python: Fix it
   - Import error: Add to requirements.txt

### "Can't find the artifact?"

- Wait for workflow to finish (green checkmark)
- Scroll to bottom of workflow page
- Look for "Artifacts" section
- Click to download

## 📝 Customization

### Change App Info

Edit `installer.iss`:
```iss
#define MyAppName "Your App Name"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Company"
```

### Change Triggers

Edit `.github/workflows/build-windows.yml`:
```yaml
on:
  push:
    branches: [ "main", "develop" ]  # Add more branches
```

## 🎉 Success Checklist

After your first successful build:

- [ ] Workflow completed successfully (green checkmark)
- [ ] Downloaded the installer artifact
- [ ] Tested the installer on Windows
- [ ] Created a release tag (v1.0.0)
- [ ] Release appeared with installer attached
- [ ] Shared the release link with users

## 🌐 Embed Download Button on Website

Once you have a release:

```html
<!-- Simple Link -->
<a href="https://github.com/DDMaster24/document_summerizer/releases/latest/download/DocumentSummarizerSetup.exe">
  Download Document Summarizer for Windows
</a>

<!-- Button Style -->
<a href="https://github.com/DDMaster24/document_summerizer/releases/latest/download/DocumentSummarizerSetup.exe"
   style="background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
  📥 Download for Windows (Free)
</a>
```

## 🚀 Next Steps

1. **Push your code** to trigger first build
2. **Test the artifact** to make sure it works
3. **Create v1.0.0 tag** for first official release
4. **Share the release link** with your grandpa!

---

**Questions?** Check the Actions tab in GitHub - the logs show exactly what's happening at each step!
