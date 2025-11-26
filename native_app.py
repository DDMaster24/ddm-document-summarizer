"""
Native Desktop Application for Document Summarizer
Built with CustomTkinter for a modern, professional look
"""
import os
import sys
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from typing import Optional
import PyPDF2
import pdfplumber
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY

from api_manager import APIKeyManager, get_config_dir
from ai_providers import get_provider

# Configure CustomTkinter theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# App colors - Professional theme with black, white, blue, green
COLORS = {
    "bg_primary": "#FFFFFF",
    "bg_secondary": "#F5F7FA",
    "text_primary": "#1A1A2E",
    "text_secondary": "#4A5568",
    "accent_blue": "#2563EB",
    "accent_green": "#059669",
    "border": "#E2E8F0",
    "success": "#10B981",
    "error": "#EF4444",
    "hover_blue": "#1D4ED8",
}


class DocumentSummarizerApp(TkinterDnD.Tk):
    """Main application window"""

    def __init__(self):
        super().__init__()

        self.title("Document Summarizer")
        self.geometry("900x700")
        self.minsize(800, 600)
        self.configure(bg=COLORS["bg_primary"])

        # Initialize API manager
        self.api_manager = APIKeyManager()

        # Track current file
        self.current_file_path: Optional[str] = None
        self.extracted_text: Optional[str] = None

        # Create main container
        self.main_container = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"])
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Check if setup is needed
        if not self.api_manager.has_any_provider():
            self.show_setup_view()
        else:
            self.show_main_view()

    def clear_container(self):
        """Clear all widgets from main container"""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # ===================== SETUP VIEW =====================

    def show_setup_view(self):
        """Show the setup wizard for first-time configuration"""
        self.clear_container()

        # Center frame
        center_frame = ctk.CTkFrame(self.main_container, fg_color=COLORS["bg_primary"])
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Header
        header_label = ctk.CTkLabel(
            center_frame,
            text="Document Summarizer",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        header_label.pack(pady=(0, 10))

        subtitle_label = ctk.CTkLabel(
            center_frame,
            text="Setup your AI provider to get started",
            font=ctk.CTkFont(size=16),
            text_color=COLORS["text_secondary"]
        )
        subtitle_label.pack(pady=(0, 40))

        # Setup form frame
        form_frame = ctk.CTkFrame(center_frame, fg_color=COLORS["bg_secondary"], corner_radius=12)
        form_frame.pack(padx=40, pady=20, fill="x")

        # Step indicator
        step_label = ctk.CTkLabel(
            form_frame,
            text="Step 1: Choose your AI Provider",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        step_label.pack(pady=(30, 20), padx=40)

        # Provider selection
        self.provider_var = ctk.StringVar(value="gemini")

        provider_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        provider_frame.pack(pady=10, padx=40, fill="x")

        gemini_radio = ctk.CTkRadioButton(
            provider_frame,
            text="Google Gemini (Recommended - Free tier available)",
            variable=self.provider_var,
            value="gemini",
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["hover_blue"]
        )
        gemini_radio.pack(anchor="w", pady=5)

        groq_radio = ctk.CTkRadioButton(
            provider_frame,
            text="Groq (Alternative - Fast inference)",
            variable=self.provider_var,
            value="groq",
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["hover_blue"]
        )
        groq_radio.pack(anchor="w", pady=5)

        # Step 2
        step2_label = ctk.CTkLabel(
            form_frame,
            text="Step 2: Enter your API Key",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        step2_label.pack(pady=(30, 10), padx=40)

        # API key entry
        self.api_key_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Paste your API key here...",
            width=400,
            height=45,
            font=ctk.CTkFont(size=14),
            show="*"
        )
        self.api_key_entry.pack(pady=10, padx=40)

        # Help text
        help_text = ctk.CTkLabel(
            form_frame,
            text="Get your free Gemini API key at: ai.google.dev",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        help_text.pack(pady=(5, 20), padx=40)

        # Status label for feedback
        self.setup_status_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"]
        )
        self.setup_status_label.pack(pady=(0, 10), padx=40)

        # Buttons frame
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=(10, 30), padx=40, fill="x")

        # Test connection button
        test_btn = ctk.CTkButton(
            button_frame,
            text="Test Connection",
            width=150,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["bg_primary"],
            text_color=COLORS["accent_blue"],
            border_width=2,
            border_color=COLORS["accent_blue"],
            hover_color=COLORS["bg_secondary"],
            command=self.test_api_connection
        )
        test_btn.pack(side="left", padx=(0, 10))

        # Save & Continue button
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save & Continue",
            width=180,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent_green"],
            hover_color="#047857",
            command=self.save_setup
        )
        save_btn.pack(side="left")

    def test_api_connection(self):
        """Test the API connection"""
        provider = self.provider_var.get()
        api_key = self.api_key_entry.get().strip()

        if not api_key:
            self.setup_status_label.configure(text="Please enter an API key", text_color=COLORS["error"])
            return

        self.setup_status_label.configure(text="Testing connection...", text_color=COLORS["text_secondary"])
        self.update()

        # Test in background thread
        def test():
            try:
                provider_instance = get_provider(provider, api_key)
                if provider_instance and provider_instance.test_connection():
                    self.after(0, lambda: self.setup_status_label.configure(
                        text="Connection successful!", text_color=COLORS["success"]
                    ))
                else:
                    self.after(0, lambda: self.setup_status_label.configure(
                        text="Connection failed. Please check your API key.", text_color=COLORS["error"]
                    ))
            except Exception as e:
                self.after(0, lambda: self.setup_status_label.configure(
                    text=f"Error: {str(e)[:50]}", text_color=COLORS["error"]
                ))

        threading.Thread(target=test, daemon=True).start()

    def save_setup(self):
        """Save the setup configuration"""
        provider = self.provider_var.get()
        api_key = self.api_key_entry.get().strip()

        if not api_key:
            self.setup_status_label.configure(text="Please enter an API key", text_color=COLORS["error"])
            return

        try:
            self.api_manager.add_provider(provider, api_key, set_as_default=True)
            self.show_main_view()
        except Exception as e:
            self.setup_status_label.configure(text=f"Error saving: {str(e)}", text_color=COLORS["error"])

    # ===================== MAIN VIEW =====================

    def show_main_view(self):
        """Show the main summarizer view"""
        self.clear_container()

        # Header bar
        header_bar = ctk.CTkFrame(self.main_container, fg_color=COLORS["bg_primary"], height=60)
        header_bar.pack(fill="x", padx=30, pady=(20, 0))
        header_bar.pack_propagate(False)

        # App title
        title_label = ctk.CTkLabel(
            header_bar,
            text="Document Summarizer",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(side="left", pady=10)

        # Settings button
        settings_btn = ctk.CTkButton(
            header_bar,
            text="Settings",
            width=100,
            height=36,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["bg_secondary"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["border"],
            command=self.show_settings_view
        )
        settings_btn.pack(side="right", pady=10)

        # Provider indicator
        default_provider = self.api_manager.get_default_provider()
        provider_label = ctk.CTkLabel(
            header_bar,
            text=f"Using: {default_provider.upper() if default_provider else 'Not configured'}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        provider_label.pack(side="right", padx=20, pady=10)

        # Main content area
        content_frame = ctk.CTkFrame(self.main_container, fg_color=COLORS["bg_primary"])
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Left panel - Input
        left_panel = ctk.CTkFrame(content_frame, fg_color=COLORS["bg_secondary"], corner_radius=12)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        input_header = ctk.CTkLabel(
            left_panel,
            text="Input Document",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        input_header.pack(pady=(20, 15), padx=20, anchor="w")

        # Drop zone
        self.drop_zone = ctk.CTkFrame(
            left_panel,
            fg_color=COLORS["bg_primary"],
            corner_radius=10,
            border_width=2,
            border_color=COLORS["border"]
        )
        self.drop_zone.pack(fill="x", padx=20, pady=(0, 15), ipady=30)

        # Register drop zone for drag and drop
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.on_file_drop)

        self.drop_label = ctk.CTkLabel(
            self.drop_zone,
            text="Drag & drop a file here\nor",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        )
        self.drop_label.pack(pady=(20, 10))

        browse_btn = ctk.CTkButton(
            self.drop_zone,
            text="Browse Files",
            width=140,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["hover_blue"],
            command=self.browse_file
        )
        browse_btn.pack(pady=(0, 5))

        formats_label = ctk.CTkLabel(
            self.drop_zone,
            text="Supported: PDF, DOCX, TXT",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        formats_label.pack(pady=(5, 15))

        # File info label
        self.file_info_label = ctk.CTkLabel(
            left_panel,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["accent_green"]
        )
        self.file_info_label.pack(pady=(0, 10), padx=20, anchor="w")

        # Or paste text
        or_label = ctk.CTkLabel(
            left_panel,
            text="Or paste text directly:",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"]
        )
        or_label.pack(pady=(10, 5), padx=20, anchor="w")

        self.text_input = ctk.CTkTextbox(
            left_panel,
            height=120,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["bg_primary"],
            border_width=1,
            border_color=COLORS["border"]
        )
        self.text_input.pack(fill="x", padx=20, pady=(0, 15))

        # Output format selection
        format_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        format_frame.pack(fill="x", padx=20, pady=(5, 15))

        format_label = ctk.CTkLabel(
            format_frame,
            text="Output Format:",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_primary"]
        )
        format_label.pack(side="left")

        self.format_var = ctk.StringVar(value="pdf")

        pdf_radio = ctk.CTkRadioButton(
            format_frame,
            text="PDF",
            variable=self.format_var,
            value="pdf",
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["accent_blue"]
        )
        pdf_radio.pack(side="left", padx=(20, 10))

        word_radio = ctk.CTkRadioButton(
            format_frame,
            text="Word",
            variable=self.format_var,
            value="word",
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["accent_blue"]
        )
        word_radio.pack(side="left")

        # Summarize button
        self.summarize_btn = ctk.CTkButton(
            left_panel,
            text="Summarize Document",
            width=200,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["accent_green"],
            hover_color="#047857",
            command=self.summarize_document
        )
        self.summarize_btn.pack(pady=(10, 25))

        # Right panel - Output
        right_panel = ctk.CTkFrame(content_frame, fg_color=COLORS["bg_secondary"], corner_radius=12)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

        output_header = ctk.CTkLabel(
            right_panel,
            text="Summary Output",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        output_header.pack(pady=(20, 15), padx=20, anchor="w")

        # Status label
        self.status_label = ctk.CTkLabel(
            right_panel,
            text="Upload a document or paste text to get started",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(pady=(0, 10), padx=20, anchor="w")

        # Summary text area
        self.summary_output = ctk.CTkTextbox(
            right_panel,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["bg_primary"],
            border_width=1,
            border_color=COLORS["border"]
        )
        self.summary_output.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Export button
        self.export_btn = ctk.CTkButton(
            right_panel,
            text="Export Summary",
            width=160,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["hover_blue"],
            state="disabled",
            command=self.export_summary
        )
        self.export_btn.pack(pady=(5, 25))

        # Store reference for export
        self.current_summary = None
        self.original_filename = "document"

    def on_file_drop(self, event):
        """Handle file drop event"""
        file_path = event.data
        # Clean up the path (remove braces on Windows)
        file_path = file_path.strip('{}')
        self.load_file(file_path)

    def browse_file(self):
        """Open file browser dialog"""
        file_path = filedialog.askopenfilename(
            title="Select Document",
            filetypes=[
                ("All Supported", "*.pdf *.docx *.doc *.txt"),
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.docx *.doc"),
                ("Text Files", "*.txt")
            ]
        )
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str):
        """Load and process a file"""
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File not found")
            return

        ext = file_path.rsplit('.', 1)[-1].lower()
        if ext not in ['pdf', 'docx', 'doc', 'txt']:
            messagebox.showerror("Error", "Unsupported file format. Please use PDF, DOCX, or TXT.")
            return

        self.current_file_path = file_path
        filename = os.path.basename(file_path)
        self.original_filename = filename
        self.file_info_label.configure(text=f"Loaded: {filename}")

        # Extract text
        self.status_label.configure(text="Extracting text from document...")
        self.update()

        def extract():
            try:
                text = self.extract_text(file_path, filename)
                self.extracted_text = text
                self.after(0, lambda: self.status_label.configure(
                    text=f"Ready to summarize ({len(text)} characters extracted)"
                ))
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(
                    text=f"Error: {str(e)}",
                ))
                self.after(0, lambda: messagebox.showerror("Extraction Error", str(e)))

        threading.Thread(target=extract, daemon=True).start()

    def extract_text(self, file_path: str, filename: str) -> str:
        """Extract text from document"""
        ext = filename.rsplit('.', 1)[-1].lower()

        if ext == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext in ['docx', 'doc']:
            return self.extract_text_from_docx(file_path)
        elif ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise Exception(f"Unsupported file type: {ext}")

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                raise Exception("Could not extract text from PDF")

        return text.strip()

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from Word document"""
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)

    def summarize_document(self):
        """Summarize the loaded document or pasted text"""
        # Get text from file or text input
        text = self.extracted_text or self.text_input.get("1.0", "end-1c").strip()

        if not text or len(text) < 50:
            messagebox.showwarning("Warning", "Please provide more text to summarize (at least 50 characters).")
            return

        # Check if provider is configured
        provider_name = self.api_manager.get_default_provider()
        if not provider_name:
            messagebox.showerror("Error", "No AI provider configured. Please go to Settings.")
            return

        api_key = self.api_manager.get_api_key(provider_name)
        if not api_key:
            messagebox.showerror("Error", f"API key not found for {provider_name}")
            return

        # Update UI
        self.summarize_btn.configure(state="disabled", text="Summarizing...")
        self.status_label.configure(text="Generating summary...")
        self.summary_output.delete("1.0", "end")
        self.update()

        def do_summarize():
            try:
                provider = get_provider(provider_name, api_key)
                summary = provider.summarize(text)
                self.current_summary = summary

                self.after(0, lambda: self.summary_output.insert("1.0", summary))
                self.after(0, lambda: self.status_label.configure(text="Summary generated successfully!"))
                self.after(0, lambda: self.export_btn.configure(state="normal"))
                self.after(0, lambda: self.summarize_btn.configure(state="normal", text="Summarize Document"))

            except Exception as e:
                self.after(0, lambda: self.status_label.configure(text=f"Error: {str(e)}"))
                self.after(0, lambda: self.summarize_btn.configure(state="normal", text="Summarize Document"))
                self.after(0, lambda: messagebox.showerror("Summarization Error", str(e)))

        threading.Thread(target=do_summarize, daemon=True).start()

    def export_summary(self):
        """Export the summary to a file"""
        if not self.current_summary:
            return

        output_format = self.format_var.get()
        default_ext = ".pdf" if output_format == "pdf" else ".docx"
        base_name = self.original_filename.rsplit('.', 1)[0] if '.' in self.original_filename else self.original_filename

        file_path = filedialog.asksaveasfilename(
            title="Save Summary",
            defaultextension=default_ext,
            initialfile=f"summary_{base_name}",
            filetypes=[
                ("PDF Files", "*.pdf") if output_format == "pdf" else ("Word Documents", "*.docx"),
            ]
        )

        if not file_path:
            return

        try:
            if output_format == "pdf":
                self.create_pdf_output(self.current_summary, file_path)
            else:
                self.create_docx_output(self.current_summary, file_path)

            messagebox.showinfo("Success", f"Summary saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def create_pdf_output(self, summary: str, output_path: str):
        """Create PDF file with summary"""
        doc = SimpleDocTemplate(
            output_path, pagesize=letter,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=18
        )

        elements = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

        # Add title
        title_style = styles['Heading1']
        title = Paragraph(f"Summary of {self.original_filename}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Add summary text
        summary_style = styles['BodyText']
        summary_style.alignment = TA_JUSTIFY

        for para in summary.split('\n'):
            if para.strip():
                p = Paragraph(para, summary_style)
                elements.append(p)
                elements.append(Spacer(1, 12))

        doc.build(elements)

    def create_docx_output(self, summary: str, output_path: str):
        """Create Word document with summary"""
        doc = Document()
        doc.add_heading(f"Summary of {self.original_filename}", 0)

        for para in summary.split('\n'):
            if para.strip():
                doc.add_paragraph(para)

        doc.save(output_path)

    # ===================== SETTINGS VIEW =====================

    def show_settings_view(self):
        """Show settings panel"""
        self.clear_container()

        # Header
        header_frame = ctk.CTkFrame(self.main_container, fg_color=COLORS["bg_primary"], height=60)
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        header_frame.pack_propagate(False)

        back_btn = ctk.CTkButton(
            header_frame,
            text="< Back",
            width=80,
            height=36,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["bg_secondary"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["border"],
            command=self.show_main_view
        )
        back_btn.pack(side="left", pady=10)

        title_label = ctk.CTkLabel(
            header_frame,
            text="Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(side="left", padx=20, pady=10)

        # Content frame
        content_frame = ctk.CTkFrame(self.main_container, fg_color=COLORS["bg_primary"])
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # API Providers section
        providers_frame = ctk.CTkFrame(content_frame, fg_color=COLORS["bg_secondary"], corner_radius=12)
        providers_frame.pack(fill="x", pady=(0, 20))

        providers_header = ctk.CTkLabel(
            providers_frame,
            text="Configured AI Providers",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        providers_header.pack(pady=(20, 15), padx=20, anchor="w")

        # List providers
        providers = self.api_manager.list_providers()

        if providers:
            for prov in providers:
                prov_frame = ctk.CTkFrame(providers_frame, fg_color=COLORS["bg_primary"], corner_radius=8)
                prov_frame.pack(fill="x", padx=20, pady=5)

                name_label = ctk.CTkLabel(
                    prov_frame,
                    text=f"{prov['name'].upper()}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS["text_primary"]
                )
                name_label.pack(side="left", padx=15, pady=12)

                if prov['is_default']:
                    default_badge = ctk.CTkLabel(
                        prov_frame,
                        text="DEFAULT",
                        font=ctk.CTkFont(size=10, weight="bold"),
                        text_color=COLORS["bg_primary"],
                        fg_color=COLORS["accent_green"],
                        corner_radius=4
                    )
                    default_badge.pack(side="left", padx=5, pady=12)

                key_preview = ctk.CTkLabel(
                    prov_frame,
                    text=prov['api_key_preview'],
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS["text_secondary"]
                )
                key_preview.pack(side="left", padx=10, pady=12)

                # Remove button
                remove_btn = ctk.CTkButton(
                    prov_frame,
                    text="Remove",
                    width=70,
                    height=30,
                    font=ctk.CTkFont(size=12),
                    fg_color=COLORS["error"],
                    hover_color="#DC2626",
                    command=lambda p=prov['name']: self.remove_provider(p)
                )
                remove_btn.pack(side="right", padx=10, pady=12)

                if not prov['is_default']:
                    set_default_btn = ctk.CTkButton(
                        prov_frame,
                        text="Set Default",
                        width=90,
                        height=30,
                        font=ctk.CTkFont(size=12),
                        fg_color=COLORS["accent_blue"],
                        hover_color=COLORS["hover_blue"],
                        command=lambda p=prov['name']: self.set_default_provider(p)
                    )
                    set_default_btn.pack(side="right", padx=5, pady=12)
        else:
            no_providers_label = ctk.CTkLabel(
                providers_frame,
                text="No providers configured",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"]
            )
            no_providers_label.pack(pady=20, padx=20)

        # Spacer
        ctk.CTkFrame(providers_frame, height=20, fg_color="transparent").pack()

        # Add new provider section
        add_frame = ctk.CTkFrame(content_frame, fg_color=COLORS["bg_secondary"], corner_radius=12)
        add_frame.pack(fill="x")

        add_header = ctk.CTkLabel(
            add_frame,
            text="Add New Provider",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        add_header.pack(pady=(20, 15), padx=20, anchor="w")

        # Provider selection
        input_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.new_provider_var = ctk.StringVar(value="gemini")

        provider_label = ctk.CTkLabel(input_frame, text="Provider:", font=ctk.CTkFont(size=13))
        provider_label.pack(side="left")

        gemini_radio = ctk.CTkRadioButton(
            input_frame, text="Gemini", variable=self.new_provider_var, value="gemini",
            font=ctk.CTkFont(size=13), fg_color=COLORS["accent_blue"]
        )
        gemini_radio.pack(side="left", padx=(15, 10))

        groq_radio = ctk.CTkRadioButton(
            input_frame, text="Groq", variable=self.new_provider_var, value="groq",
            font=ctk.CTkFont(size=13), fg_color=COLORS["accent_blue"]
        )
        groq_radio.pack(side="left")

        # API key input
        key_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        key_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.new_api_key_entry = ctk.CTkEntry(
            key_frame,
            placeholder_text="Enter API key...",
            width=350,
            height=40,
            font=ctk.CTkFont(size=13),
            show="*"
        )
        self.new_api_key_entry.pack(side="left", padx=(0, 10))

        add_btn = ctk.CTkButton(
            key_frame,
            text="Add Provider",
            width=120,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["accent_green"],
            hover_color="#047857",
            command=self.add_new_provider
        )
        add_btn.pack(side="left")

    def remove_provider(self, provider_name: str):
        """Remove a provider"""
        if messagebox.askyesno("Confirm", f"Remove {provider_name.upper()} provider?"):
            self.api_manager.remove_provider(provider_name)
            if not self.api_manager.has_any_provider():
                self.show_setup_view()
            else:
                self.show_settings_view()

    def set_default_provider(self, provider_name: str):
        """Set a provider as default"""
        self.api_manager.set_default_provider(provider_name)
        self.show_settings_view()

    def add_new_provider(self):
        """Add a new provider"""
        provider = self.new_provider_var.get()
        api_key = self.new_api_key_entry.get().strip()

        if not api_key:
            messagebox.showwarning("Warning", "Please enter an API key")
            return

        try:
            self.api_manager.add_provider(provider, api_key, set_as_default=False)
            self.show_settings_view()
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    """Main entry point"""
    app = DocumentSummarizerApp()
    app.mainloop()


if __name__ == '__main__':
    main()
