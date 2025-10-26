// DOM Elements
const form = document.getElementById('summarizerForm');
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const fileName = document.getElementById('fileName');
const manualText = document.getElementById('manualText');
const submitBtn = document.getElementById('submitBtn');
const btnText = document.getElementById('btnText');
const btnLoader = document.getElementById('btnLoader');
const resultSection = document.getElementById('resultSection');
const errorSection = document.getElementById('errorSection');
const summaryText = document.getElementById('summaryText');
const errorText = document.getElementById('errorText');
const downloadBtn = document.getElementById('downloadBtn');

let currentDownloadFilename = '';

// File input change handler
fileInput.addEventListener('change', (e) => {
    handleFileSelect(e.target.files[0]);
});

// Click on upload area to trigger file input
uploadArea.addEventListener('click', (e) => {
    if (e.target.tagName !== 'LABEL') {
        fileInput.click();
    }
});

// Drag and drop handlers
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        // Set the file to the input
        fileInput.files = files;
        handleFileSelect(file);
    }
});

// Handle file selection
function handleFileSelect(file) {
    if (file) {
        fileName.textContent = `Selected: ${file.name}`;
        fileName.classList.add('show');
        // Clear manual text if file is selected
        manualText.value = '';
    }
}

// Clear file selection when typing in textarea
manualText.addEventListener('input', () => {
    if (manualText.value.trim()) {
        fileInput.value = '';
        fileName.classList.remove('show');
    }
});

// Form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Hide previous results/errors
    resultSection.style.display = 'none';
    errorSection.style.display = 'none';

    // Validate input
    const hasFile = fileInput.files.length > 0;
    const hasText = manualText.value.trim().length > 0;

    if (!hasFile && !hasText) {
        showError('Please upload a file or enter some text to summarize.');
        return;
    }

    // Show loading state
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'block';

    try {
        // Prepare form data
        const formData = new FormData(form);

        // Send request
        const response = await fetch('/summarize', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Show success result
            showResult(data.summary, data.download_filename);
        } else {
            // Show error
            showError(data.error || 'An error occurred while summarizing the document.');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
    }
});

// Show result
function showResult(summary, downloadFilename) {
    summaryText.textContent = summary;
    currentDownloadFilename = downloadFilename;
    resultSection.style.display = 'block';
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Show error
function showError(message) {
    errorText.textContent = message;
    errorSection.style.display = 'block';
    errorSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Download button handler
downloadBtn.addEventListener('click', () => {
    if (currentDownloadFilename) {
        window.location.href = `/download/${currentDownloadFilename}`;
    }
});

// Check API status on load
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/health');
        const data = await response.json();

        if (!data.api_configured) {
            console.warn('Groq API not configured. Please set up your API key in .env file.');
        }
    } catch (error) {
        console.error('Health check failed:', error);
    }
});
