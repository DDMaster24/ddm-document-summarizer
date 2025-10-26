import os
import io
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from groq import Groq
import PyPDF2
import pdfplumber
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY
import shutil

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Create necessary folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Initialize Groq client
groq_api_key = os.getenv('GROQ_API_KEY')
if not groq_api_key:
    print("WARNING: GROQ_API_KEY not set. Please set it in .env file")
    client = None
else:
    client = Groq(api_key=groq_api_key)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    text = ""
    try:
        # Try pdfplumber first (better for complex PDFs)
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"pdfplumber failed, trying PyPDF2: {e}")
        # Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e2:
            print(f"PyPDF2 also failed: {e2}")
            raise Exception("Could not extract text from PDF")

    return text.strip()

def extract_text_from_docx(file_path):
    """Extract text from Word document"""
    doc = Document(file_path)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return '\n'.join(text)

def extract_text_from_txt(file_path):
    """Extract text from text file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_text(file_path, filename):
    """Extract text based on file type"""
    ext = filename.rsplit('.', 1)[1].lower()

    if ext == 'pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['docx', 'doc']:
        return extract_text_from_docx(file_path)
    elif ext == 'txt':
        return extract_text_from_txt(file_path)
    else:
        raise Exception(f"Unsupported file type: {ext}")

def summarize_text(text):
    """Summarize text using Groq API"""
    if not client:
        raise Exception("Groq API key not configured. Please add your API key to .env file")

    try:
        # Truncate text if too long (Groq has token limits)
        max_chars = 24000  # Roughly 6000 tokens
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[Text truncated due to length...]"

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates clear, concise summaries of documents. Provide a well-structured summary with key points and main ideas."
                },
                {
                    "role": "user",
                    "content": f"Please provide a comprehensive summary of the following text:\n\n{text}"
                }
            ],
            model="llama-3.1-70b-versatile",  # Fast and good quality
            temperature=0.3,
            max_tokens=2000
        )

        return chat_completion.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error calling Groq API: {str(e)}")

def create_pdf_output(summary, original_filename):
    """Create PDF file with summary"""
    output_filename = f"summary_{original_filename.rsplit('.', 1)[0]}.pdf"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

    # Create PDF
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

    # Add title
    title_style = styles['Heading1']
    title = Paragraph(f"Summary of {original_filename}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Add summary text
    summary_style = styles['BodyText']
    summary_style.alignment = TA_JUSTIFY

    # Split summary into paragraphs
    for para in summary.split('\n'):
        if para.strip():
            p = Paragraph(para, summary_style)
            elements.append(p)
            elements.append(Spacer(1, 12))

    # Build PDF
    doc.build(elements)

    return output_path

def create_docx_output(summary, original_filename):
    """Create Word document with summary"""
    output_filename = f"summary_{original_filename.rsplit('.', 1)[0]}.docx"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

    # Create Word document
    doc = Document()

    # Add title
    doc.add_heading(f"Summary of {original_filename}", 0)

    # Add summary text
    for para in summary.split('\n'):
        if para.strip():
            doc.add_paragraph(para)

    # Save document
    doc.save(output_path)

    return output_path

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    """Handle summarization request"""
    try:
        text_to_summarize = ""
        original_filename = "document"

        # Check if text was pasted/typed
        if 'manual_text' in request.form and request.form['manual_text'].strip():
            text_to_summarize = request.form['manual_text'].strip()
            original_filename = "manual_input.txt"

        # Check if file was uploaded
        elif 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                original_filename = filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Extract text from file
                text_to_summarize = extract_text(filepath, filename)

                # Clean up uploaded file
                os.remove(filepath)
            else:
                return jsonify({'error': 'Invalid file type. Please upload PDF, Word, or text file.'}), 400
        else:
            return jsonify({'error': 'No input provided. Please upload a file or paste text.'}), 400

        # Check if text is not empty
        if not text_to_summarize or len(text_to_summarize.strip()) < 50:
            return jsonify({'error': 'Text is too short to summarize. Please provide more content.'}), 400

        # Summarize the text
        summary = summarize_text(text_to_summarize)

        # Get output format preference
        output_format = request.form.get('output_format', 'pdf')

        # Generate output file
        if output_format == 'word':
            output_path = create_docx_output(summary, original_filename)
        else:
            output_path = create_pdf_output(summary, original_filename)

        # Return success with download info
        return jsonify({
            'success': True,
            'summary': summary,
            'download_filename': os.path.basename(output_path),
            'output_format': output_format
        })

    except Exception as e:
        print(f"Error in summarize: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    """Download generated summary file"""
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], secure_filename(filename))
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    api_configured = groq_api_key is not None and groq_api_key != ""
    return jsonify({
        'status': 'healthy',
        'api_configured': api_configured
    })

# Clean up old files on startup
def cleanup_folders():
    """Clean up upload and output folders"""
    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

if __name__ == '__main__':
    cleanup_folders()
    print("\n" + "="*60)
    print("📄 Document Summarizer is starting...")
    print("="*60)

    if not groq_api_key:
        print("\n⚠️  WARNING: Groq API key not found!")
        print("Please create a .env file with your API key:")
        print("   GROQ_API_KEY=your_key_here")
        print("\nGet your free API key at: https://console.groq.com")
        print("="*60 + "\n")
    else:
        print("\n✅ Groq API configured successfully!")
        print("="*60 + "\n")

    print("🌐 Open your browser and go to: http://localhost:5000")
    print("\n💡 Press Ctrl+C to stop the server\n")

    app.run(debug=False, host='0.0.0.0', port=5000)
