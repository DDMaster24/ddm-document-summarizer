"""
Document Summarizer - Native Desktop Application
Professional multi-provider AI document summarization tool
Built with CustomTkinter for a modern, polished interface
"""
import os
import sys
import threading
import webbrowser
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
from ai_providers import get_provider, get_all_providers, get_provider_info, PROVIDERS

# Configure CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Professional color palette
class Colors:
    # Primary colors
    BG_PRIMARY = "#FFFFFF"
    BG_SECONDARY = "#F8FAFC"
    BG_TERTIARY = "#F1F5F9"

    # Text colors
    TEXT_PRIMARY = "#0F172A"
    TEXT_SECONDARY = "#475569"
    TEXT_MUTED = "#94A3B8"

    # Accent colors
    BLUE_PRIMARY = "#2563EB"
    BLUE_HOVER = "#1D4ED8"
    BLUE_LIGHT = "#DBEAFE"

    GREEN_PRIMARY = "#059669"
    GREEN_HOVER = "#047857"
    GREEN_LIGHT = "#D1FAE5"

    # Status colors
    SUCCESS = "#10B981"
    ERROR = "#EF4444"
    WARNING = "#F59E0B"

    # Border & dividers
    BORDER = "#E2E8F0"
    DIVIDER = "#CBD5E1"

    # Provider brand colors
    PROVIDER_COLORS = {
        "gemini": "#4285F4",
        "openai": "#10A37F",
        "claude": "#CC785C",
        "groq": "#F55036",
        "grok": "#000000",
    }


class DocumentSummarizerApp(TkinterDnD.Tk):
    """Main application window with professional UI"""

    def __init__(self):
        super().__init__()

        self.title("Document Summarizer")
        self.geometry("1100x750")
        self.minsize(900, 650)
        self.configure(bg=Colors.BG_PRIMARY)

        # Initialize API manager
        self.api_manager = APIKeyManager()

        # Track current state
        self.current_file_path: Optional[str] = None
        self.extracted_text: Optional[str] = None
        self.current_summary: Optional[str] = None
        self.original_filename: str = "document"

        # Create main container
        self.main_container = ctk.CTkFrame(self, fg_color=Colors.BG_PRIMARY, corner_radius=0)
        self.main_container.pack(fill="both", expand=True)

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

        # Main setup container with max width
        setup_wrapper = ctk.CTkFrame(self.main_container, fg_color=Colors.BG_PRIMARY)
        setup_wrapper.pack(fill="both", expand=True)

        # Scrollable frame for setup content
        setup_frame = ctk.CTkFrame(setup_wrapper, fg_color=Colors.BG_PRIMARY, width=600)
        setup_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Header
        header_frame = ctk.CTkFrame(setup_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 30))

        title_label = ctk.CTkLabel(
            header_frame,
            text="Document Summarizer",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        title_label.pack()

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Connect your AI provider to get started",
            font=ctk.CTkFont(size=16),
            text_color=Colors.TEXT_SECONDARY
        )
        subtitle_label.pack(pady=(8, 0))

        # Provider selection card
        provider_card = ctk.CTkFrame(setup_frame, fg_color=Colors.BG_SECONDARY, corner_radius=16)
        provider_card.pack(fill="x", pady=(0, 20))

        provider_header = ctk.CTkLabel(
            provider_card,
            text="Choose AI Provider",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        provider_header.pack(pady=(24, 16), padx=24, anchor="w")

        # Provider buttons
        providers_frame = ctk.CTkFrame(provider_card, fg_color="transparent")
        providers_frame.pack(fill="x", padx=24, pady=(0, 24))

        self.selected_provider = ctk.StringVar(value="gemini")
        self.provider_buttons = {}

        all_providers = get_all_providers()
        row = 0
        col = 0

        for provider_name, info in all_providers.items():
            btn_frame = ctk.CTkFrame(providers_frame, fg_color="transparent")
            btn_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

            btn = ctk.CTkButton(
                btn_frame,
                text=info['display_name'],
                width=170,
                height=50,
                font=ctk.CTkFont(size=14),
                fg_color=Colors.BG_PRIMARY,
                text_color=Colors.TEXT_PRIMARY,
                border_width=2,
                border_color=Colors.BORDER,
                hover_color=Colors.BLUE_LIGHT,
                corner_radius=10,
                command=lambda p=provider_name: self.select_provider(p)
            )
            btn.pack(fill="x")
            self.provider_buttons[provider_name] = btn

            col += 1
            if col >= 3:
                col = 0
                row += 1

        # Configure grid columns
        for i in range(3):
            providers_frame.columnconfigure(i, weight=1)

        # Select default
        self.select_provider("gemini")

        # API Key input card
        key_card = ctk.CTkFrame(setup_frame, fg_color=Colors.BG_SECONDARY, corner_radius=16)
        key_card.pack(fill="x", pady=(0, 20))

        key_header = ctk.CTkLabel(
            key_card,
            text="Enter API Key",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        key_header.pack(pady=(24, 8), padx=24, anchor="w")

        self.api_help_label = ctk.CTkLabel(
            key_card,
            text="Get your free API key from Google AI Studio",
            font=ctk.CTkFont(size=13),
            text_color=Colors.TEXT_SECONDARY
        )
        self.api_help_label.pack(padx=24, anchor="w")

        # API key entry with show/hide
        key_entry_frame = ctk.CTkFrame(key_card, fg_color="transparent")
        key_entry_frame.pack(fill="x", padx=24, pady=(12, 8))

        self.api_key_entry = ctk.CTkEntry(
            key_entry_frame,
            placeholder_text="Paste your API key here...",
            height=50,
            font=ctk.CTkFont(size=14),
            show="*",
            border_width=2,
            border_color=Colors.BORDER,
            corner_radius=10
        )
        self.api_key_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.show_key_var = ctk.BooleanVar(value=False)
        show_key_btn = ctk.CTkButton(
            key_entry_frame,
            text="Show",
            width=70,
            height=50,
            font=ctk.CTkFont(size=13),
            fg_color=Colors.BG_TERTIARY,
            text_color=Colors.TEXT_SECONDARY,
            hover_color=Colors.BORDER,
            corner_radius=10,
            command=self.toggle_key_visibility
        )
        show_key_btn.pack(side="right")

        # Get API key link
        self.get_key_link = ctk.CTkButton(
            key_card,
            text="Get API Key",
            font=ctk.CTkFont(size=13, underline=True),
            fg_color="transparent",
            text_color=Colors.BLUE_PRIMARY,
            hover_color=Colors.BG_TERTIARY,
            height=30,
            command=self.open_api_key_url
        )
        self.get_key_link.pack(padx=24, anchor="w", pady=(0, 20))

        # Model selection
        model_frame = ctk.CTkFrame(key_card, fg_color="transparent")
        model_frame.pack(fill="x", padx=24, pady=(0, 24))

        model_label = ctk.CTkLabel(
            model_frame,
            text="Select Model:",
            font=ctk.CTkFont(size=14),
            text_color=Colors.TEXT_PRIMARY
        )
        model_label.pack(side="left")

        self.model_dropdown = ctk.CTkComboBox(
            model_frame,
            values=["Gemini 2.5 Pro (Best Quality)"],
            width=280,
            height=40,
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=13),
            border_width=2,
            border_color=Colors.BORDER,
            button_color=Colors.BLUE_PRIMARY,
            button_hover_color=Colors.BLUE_HOVER,
            corner_radius=10
        )
        self.model_dropdown.pack(side="left", padx=(15, 0))

        # Update model dropdown for selected provider
        self.update_model_dropdown("gemini")

        # Status label
        self.setup_status_label = ctk.CTkLabel(
            setup_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color=Colors.TEXT_SECONDARY
        )
        self.setup_status_label.pack(pady=(0, 15))

        # Action buttons
        button_frame = ctk.CTkFrame(setup_frame, fg_color="transparent")
        button_frame.pack(fill="x")

        test_btn = ctk.CTkButton(
            button_frame,
            text="Test Connection",
            width=160,
            height=50,
            font=ctk.CTkFont(size=15),
            fg_color=Colors.BG_PRIMARY,
            text_color=Colors.BLUE_PRIMARY,
            border_width=2,
            border_color=Colors.BLUE_PRIMARY,
            hover_color=Colors.BLUE_LIGHT,
            corner_radius=12,
            command=self.test_api_connection
        )
        test_btn.pack(side="left", padx=(0, 15))

        save_btn = ctk.CTkButton(
            button_frame,
            text="Save & Continue",
            width=200,
            height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=Colors.GREEN_PRIMARY,
            hover_color=Colors.GREEN_HOVER,
            corner_radius=12,
            command=self.save_setup
        )
        save_btn.pack(side="left")

    def select_provider(self, provider_name: str):
        """Handle provider selection"""
        self.selected_provider.set(provider_name)

        # Update button styles
        for name, btn in self.provider_buttons.items():
            if name == provider_name:
                color = Colors.PROVIDER_COLORS.get(name, Colors.BLUE_PRIMARY)
                btn.configure(
                    fg_color=color,
                    text_color=Colors.BG_PRIMARY,
                    border_color=color
                )
            else:
                btn.configure(
                    fg_color=Colors.BG_PRIMARY,
                    text_color=Colors.TEXT_PRIMARY,
                    border_color=Colors.BORDER
                )

        # Update help text and model dropdown
        info = get_provider_info(provider_name)
        if info:
            self.api_help_label.configure(text=info['api_key_help'])
            self.update_model_dropdown(provider_name)

    def update_model_dropdown(self, provider_name: str):
        """Update the model dropdown for selected provider"""
        info = get_provider_info(provider_name)
        if info:
            models = list(info['models'].values())
            self.model_dropdown.configure(values=models)
            # Set default model
            default_model = info['default_model']
            if default_model in info['models']:
                self.model_dropdown.set(info['models'][default_model])

    def get_selected_model_id(self) -> str:
        """Get the model ID from the display name"""
        provider_name = self.selected_provider.get()
        info = get_provider_info(provider_name)
        if info:
            display_name = self.model_dropdown.get()
            for model_id, name in info['models'].items():
                if name == display_name:
                    return model_id
        return None

    def toggle_key_visibility(self):
        """Toggle API key visibility"""
        if self.api_key_entry.cget("show") == "*":
            self.api_key_entry.configure(show="")
        else:
            self.api_key_entry.configure(show="*")

    def open_api_key_url(self):
        """Open the API key URL in browser"""
        provider_name = self.selected_provider.get()
        info = get_provider_info(provider_name)
        if info:
            webbrowser.open(info['api_key_url'])

    def test_api_connection(self):
        """Test the API connection"""
        provider = self.selected_provider.get()
        api_key = self.api_key_entry.get().strip()
        model = self.get_selected_model_id()

        if not api_key:
            self.setup_status_label.configure(text="Please enter an API key", text_color=Colors.ERROR)
            return

        self.setup_status_label.configure(text="Testing connection...", text_color=Colors.TEXT_SECONDARY)
        self.update()

        def test():
            try:
                provider_instance = get_provider(provider, api_key, model)
                if provider_instance and provider_instance.test_connection():
                    self.after(0, lambda: self.setup_status_label.configure(
                        text="Connection successful!", text_color=Colors.SUCCESS
                    ))
                else:
                    self.after(0, lambda: self.setup_status_label.configure(
                        text="Connection failed. Please check your API key.", text_color=Colors.ERROR
                    ))
            except Exception as e:
                self.after(0, lambda: self.setup_status_label.configure(
                    text=f"Error: {str(e)[:60]}", text_color=Colors.ERROR
                ))

        threading.Thread(target=test, daemon=True).start()

    def save_setup(self):
        """Save the setup configuration"""
        provider = self.selected_provider.get()
        api_key = self.api_key_entry.get().strip()
        model = self.get_selected_model_id()

        if not api_key:
            self.setup_status_label.configure(text="Please enter an API key", text_color=Colors.ERROR)
            return

        try:
            self.api_manager.add_provider(provider, api_key, model, set_as_default=True)
            self.show_main_view()
        except Exception as e:
            self.setup_status_label.configure(text=f"Error saving: {str(e)}", text_color=Colors.ERROR)

    # ===================== MAIN VIEW =====================

    def show_main_view(self):
        """Show the main summarizer view"""
        self.clear_container()

        # Header bar
        header_bar = ctk.CTkFrame(self.main_container, fg_color=Colors.BG_PRIMARY, height=70)
        header_bar.pack(fill="x", padx=0, pady=0)
        header_bar.pack_propagate(False)

        # Header content
        header_content = ctk.CTkFrame(header_bar, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30)

        # Left side - Logo and title
        left_header = ctk.CTkFrame(header_content, fg_color="transparent")
        left_header.pack(side="left", fill="y")

        title_label = ctk.CTkLabel(
            left_header,
            text="Document Summarizer",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        title_label.pack(side="left", pady=20)

        # Right side - Provider info and settings
        right_header = ctk.CTkFrame(header_content, fg_color="transparent")
        right_header.pack(side="right", fill="y")

        # Current provider/model display
        provider_name = self.api_manager.get_default_provider()
        model = self.api_manager.get_model(provider_name)
        info = get_provider_info(provider_name) if provider_name else None

        if info:
            display_name = info['display_name']
            model_display = info['models'].get(model, model) if model else "Default"
            provider_color = Colors.PROVIDER_COLORS.get(provider_name, Colors.BLUE_PRIMARY)

            provider_badge = ctk.CTkFrame(right_header, fg_color=provider_color, corner_radius=8)
            provider_badge.pack(side="left", padx=(0, 15), pady=18)

            provider_text = ctk.CTkLabel(
                provider_badge,
                text=f"{display_name}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=Colors.BG_PRIMARY
            )
            provider_text.pack(padx=12, pady=6)

            model_label = ctk.CTkLabel(
                right_header,
                text=model_display,
                font=ctk.CTkFont(size=12),
                text_color=Colors.TEXT_SECONDARY
            )
            model_label.pack(side="left", padx=(0, 20), pady=20)

        settings_btn = ctk.CTkButton(
            right_header,
            text="Settings",
            width=100,
            height=38,
            font=ctk.CTkFont(size=13),
            fg_color=Colors.BG_SECONDARY,
            text_color=Colors.TEXT_PRIMARY,
            hover_color=Colors.BG_TERTIARY,
            corner_radius=10,
            command=self.show_settings_view
        )
        settings_btn.pack(side="right", pady=16)

        # Divider
        divider = ctk.CTkFrame(self.main_container, fg_color=Colors.BORDER, height=1)
        divider.pack(fill="x")

        # Main content area
        content_frame = ctk.CTkFrame(self.main_container, fg_color=Colors.BG_SECONDARY)
        content_frame.pack(fill="both", expand=True)

        # Two-panel layout
        panels_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        panels_frame.pack(fill="both", expand=True, padx=30, pady=25)

        # Left panel - Input
        left_panel = ctk.CTkFrame(panels_frame, fg_color=Colors.BG_PRIMARY, corner_radius=16)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self._create_input_panel(left_panel)

        # Right panel - Output
        right_panel = ctk.CTkFrame(panels_frame, fg_color=Colors.BG_PRIMARY, corner_radius=16)
        right_panel.pack(side="right", fill="both", expand=True, padx=(12, 0))

        self._create_output_panel(right_panel)

    def _create_input_panel(self, parent):
        """Create the input panel"""
        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 16))

        title = ctk.CTkLabel(
            header,
            text="Input Document",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        title.pack(anchor="w")

        # Drop zone
        self.drop_zone = ctk.CTkFrame(
            parent,
            fg_color=Colors.BG_SECONDARY,
            corner_radius=12,
            border_width=2,
            border_color=Colors.BORDER
        )
        self.drop_zone.pack(fill="x", padx=24, pady=(0, 16))

        # Register drag and drop
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.on_file_drop)

        drop_content = ctk.CTkFrame(self.drop_zone, fg_color="transparent")
        drop_content.pack(expand=True, pady=30)

        # Drop icon (using text)
        drop_icon = ctk.CTkLabel(
            drop_content,
            text="[ + ]",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=Colors.TEXT_MUTED
        )
        drop_icon.pack()

        self.drop_label = ctk.CTkLabel(
            drop_content,
            text="Drag & drop your document here",
            font=ctk.CTkFont(size=15),
            text_color=Colors.TEXT_SECONDARY
        )
        self.drop_label.pack(pady=(10, 15))

        browse_btn = ctk.CTkButton(
            drop_content,
            text="Browse Files",
            width=140,
            height=42,
            font=ctk.CTkFont(size=14),
            fg_color=Colors.BLUE_PRIMARY,
            hover_color=Colors.BLUE_HOVER,
            corner_radius=10,
            command=self.browse_file
        )
        browse_btn.pack()

        formats_label = ctk.CTkLabel(
            drop_content,
            text="PDF, DOCX, TXT supported",
            font=ctk.CTkFont(size=12),
            text_color=Colors.TEXT_MUTED
        )
        formats_label.pack(pady=(12, 0))

        # File info
        self.file_info_label = ctk.CTkLabel(
            parent,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=Colors.SUCCESS
        )
        self.file_info_label.pack(padx=24, anchor="w")

        # Or divider
        or_frame = ctk.CTkFrame(parent, fg_color="transparent")
        or_frame.pack(fill="x", padx=24, pady=12)

        or_line1 = ctk.CTkFrame(or_frame, fg_color=Colors.BORDER, height=1)
        or_line1.pack(side="left", fill="x", expand=True)

        or_label = ctk.CTkLabel(
            or_frame,
            text="OR",
            font=ctk.CTkFont(size=12),
            text_color=Colors.TEXT_MUTED
        )
        or_label.pack(side="left", padx=15)

        or_line2 = ctk.CTkFrame(or_frame, fg_color=Colors.BORDER, height=1)
        or_line2.pack(side="left", fill="x", expand=True)

        # Text input
        text_label = ctk.CTkLabel(
            parent,
            text="Paste text directly",
            font=ctk.CTkFont(size=14),
            text_color=Colors.TEXT_PRIMARY
        )
        text_label.pack(padx=24, anchor="w", pady=(0, 8))

        self.text_input = ctk.CTkTextbox(
            parent,
            height=100,
            font=ctk.CTkFont(size=13),
            fg_color=Colors.BG_SECONDARY,
            border_width=1,
            border_color=Colors.BORDER,
            corner_radius=10
        )
        self.text_input.pack(fill="x", padx=24, pady=(0, 16))

        # Output format
        format_frame = ctk.CTkFrame(parent, fg_color="transparent")
        format_frame.pack(fill="x", padx=24, pady=(0, 20))

        format_label = ctk.CTkLabel(
            format_frame,
            text="Export Format:",
            font=ctk.CTkFont(size=14),
            text_color=Colors.TEXT_PRIMARY
        )
        format_label.pack(side="left")

        self.format_var = ctk.StringVar(value="pdf")

        pdf_radio = ctk.CTkRadioButton(
            format_frame,
            text="PDF",
            variable=self.format_var,
            value="pdf",
            font=ctk.CTkFont(size=13),
            fg_color=Colors.BLUE_PRIMARY,
            hover_color=Colors.BLUE_HOVER
        )
        pdf_radio.pack(side="left", padx=(20, 15))

        word_radio = ctk.CTkRadioButton(
            format_frame,
            text="Word",
            variable=self.format_var,
            value="word",
            font=ctk.CTkFont(size=13),
            fg_color=Colors.BLUE_PRIMARY,
            hover_color=Colors.BLUE_HOVER
        )
        word_radio.pack(side="left")

        # Summarize button
        self.summarize_btn = ctk.CTkButton(
            parent,
            text="Summarize Document",
            height=54,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=Colors.GREEN_PRIMARY,
            hover_color=Colors.GREEN_HOVER,
            corner_radius=12,
            command=self.summarize_document
        )
        self.summarize_btn.pack(fill="x", padx=24, pady=(0, 24))

    def _create_output_panel(self, parent):
        """Create the output panel"""
        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 16))

        title = ctk.CTkLabel(
            header,
            text="Summary Output",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        title.pack(side="left")

        # Status
        self.status_label = ctk.CTkLabel(
            parent,
            text="Upload a document or paste text to get started",
            font=ctk.CTkFont(size=13),
            text_color=Colors.TEXT_SECONDARY
        )
        self.status_label.pack(padx=24, anchor="w", pady=(0, 12))

        # Summary output
        self.summary_output = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(size=14),
            fg_color=Colors.BG_SECONDARY,
            border_width=1,
            border_color=Colors.BORDER,
            corner_radius=10
        )
        self.summary_output.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # Export button
        self.export_btn = ctk.CTkButton(
            parent,
            text="Export Summary",
            height=48,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=Colors.BLUE_PRIMARY,
            hover_color=Colors.BLUE_HOVER,
            corner_radius=12,
            state="disabled",
            command=self.export_summary
        )
        self.export_btn.pack(fill="x", padx=24, pady=(0, 24))

    def on_file_drop(self, event):
        """Handle file drop"""
        file_path = event.data.strip('{}')
        self.load_file(file_path)

    def browse_file(self):
        """Open file browser"""
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
        """Load and extract text from file"""
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File not found")
            return

        ext = file_path.rsplit('.', 1)[-1].lower()
        if ext not in ['pdf', 'docx', 'doc', 'txt']:
            messagebox.showerror("Error", "Unsupported format. Use PDF, DOCX, or TXT.")
            return

        self.current_file_path = file_path
        filename = os.path.basename(file_path)
        self.original_filename = filename
        self.file_info_label.configure(text=f"Loaded: {filename}")
        self.status_label.configure(text="Extracting text...")
        self.update()

        def extract():
            try:
                text = self.extract_text(file_path, filename)
                self.extracted_text = text
                char_count = len(text)
                self.after(0, lambda: self.status_label.configure(
                    text=f"Ready to summarize ({char_count:,} characters)"
                ))
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(text=f"Error: {str(e)}"))

        threading.Thread(target=extract, daemon=True).start()

    def extract_text(self, file_path: str, filename: str) -> str:
        """Extract text from document"""
        ext = filename.rsplit('.', 1)[-1].lower()

        if ext == 'pdf':
            return self._extract_pdf(file_path)
        elif ext in ['docx', 'doc']:
            return self._extract_docx(file_path)
        elif ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        raise Exception(f"Unsupported: {ext}")

    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        return text.strip()

    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        doc = Document(file_path)
        return '\n'.join([p.text for p in doc.paragraphs])

    def summarize_document(self):
        """Summarize the document"""
        text = self.extracted_text or self.text_input.get("1.0", "end-1c").strip()

        if not text or len(text) < 50:
            messagebox.showwarning("Warning", "Please provide more text (at least 50 characters).")
            return

        provider_name = self.api_manager.get_default_provider()
        if not provider_name:
            messagebox.showerror("Error", "No AI provider configured.")
            return

        api_key = self.api_manager.get_api_key(provider_name)
        model = self.api_manager.get_model(provider_name)

        self.summarize_btn.configure(state="disabled", text="Summarizing...")
        self.status_label.configure(text="Generating summary...")
        self.summary_output.delete("1.0", "end")
        self.update()

        def do_summarize():
            try:
                provider = get_provider(provider_name, api_key, model)
                summary = provider.summarize(text)
                self.current_summary = summary

                self.after(0, lambda: self.summary_output.insert("1.0", summary))
                self.after(0, lambda: self.status_label.configure(text="Summary generated!"))
                self.after(0, lambda: self.export_btn.configure(state="normal"))
                self.after(0, lambda: self.summarize_btn.configure(state="normal", text="Summarize Document"))
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(text=f"Error: {str(e)}"))
                self.after(0, lambda: self.summarize_btn.configure(state="normal", text="Summarize Document"))

        threading.Thread(target=do_summarize, daemon=True).start()

    def export_summary(self):
        """Export summary to file"""
        if not self.current_summary:
            return

        output_format = self.format_var.get()
        ext = ".pdf" if output_format == "pdf" else ".docx"
        base = self.original_filename.rsplit('.', 1)[0]

        file_path = filedialog.asksaveasfilename(
            title="Save Summary",
            defaultextension=ext,
            initialfile=f"summary_{base}",
            filetypes=[("PDF Files", "*.pdf") if output_format == "pdf" else ("Word Documents", "*.docx")]
        )

        if not file_path:
            return

        try:
            if output_format == "pdf":
                self._create_pdf(self.current_summary, file_path)
            else:
                self._create_docx(self.current_summary, file_path)
            messagebox.showinfo("Success", f"Saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _create_pdf(self, summary: str, path: str):
        """Create PDF"""
        doc = SimpleDocTemplate(path, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

        elements = []
        elements.append(Paragraph(f"Summary of {self.original_filename}", styles['Heading1']))
        elements.append(Spacer(1, 12))

        for para in summary.split('\n'):
            if para.strip():
                elements.append(Paragraph(para, styles['BodyText']))
                elements.append(Spacer(1, 12))

        doc.build(elements)

    def _create_docx(self, summary: str, path: str):
        """Create DOCX"""
        doc = Document()
        doc.add_heading(f"Summary of {self.original_filename}", 0)
        for para in summary.split('\n'):
            if para.strip():
                doc.add_paragraph(para)
        doc.save(path)

    # ===================== SETTINGS VIEW =====================

    def show_settings_view(self):
        """Show settings panel"""
        self.clear_container()

        # Header
        header = ctk.CTkFrame(self.main_container, fg_color=Colors.BG_PRIMARY, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30)

        back_btn = ctk.CTkButton(
            header_content,
            text="< Back",
            width=80,
            height=38,
            font=ctk.CTkFont(size=13),
            fg_color=Colors.BG_SECONDARY,
            text_color=Colors.TEXT_PRIMARY,
            hover_color=Colors.BG_TERTIARY,
            corner_radius=10,
            command=self.show_main_view
        )
        back_btn.pack(side="left", pady=16)

        title = ctk.CTkLabel(
            header_content,
            text="Settings",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        title.pack(side="left", padx=20, pady=20)

        # Divider
        ctk.CTkFrame(self.main_container, fg_color=Colors.BORDER, height=1).pack(fill="x")

        # Content
        content = ctk.CTkScrollableFrame(self.main_container, fg_color=Colors.BG_SECONDARY)
        content.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(content, fg_color="transparent", width=700)
        inner.pack(pady=30)

        # Configured providers
        providers_card = ctk.CTkFrame(inner, fg_color=Colors.BG_PRIMARY, corner_radius=16, width=700)
        providers_card.pack(fill="x", pady=(0, 20))

        providers_header = ctk.CTkLabel(
            providers_card,
            text="Configured Providers",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        providers_header.pack(pady=(24, 16), padx=24, anchor="w")

        providers = self.api_manager.list_providers()

        if providers:
            for prov in providers:
                prov_frame = ctk.CTkFrame(providers_card, fg_color=Colors.BG_SECONDARY, corner_radius=10)
                prov_frame.pack(fill="x", padx=24, pady=6)

                info = get_provider_info(prov['name'])
                color = Colors.PROVIDER_COLORS.get(prov['name'], Colors.BLUE_PRIMARY)

                # Provider badge
                badge = ctk.CTkFrame(prov_frame, fg_color=color, corner_radius=6, width=10)
                badge.pack(side="left", fill="y", padx=(0, 0))

                details = ctk.CTkFrame(prov_frame, fg_color="transparent")
                details.pack(side="left", fill="x", expand=True, padx=15, pady=12)

                name_row = ctk.CTkFrame(details, fg_color="transparent")
                name_row.pack(fill="x")

                name_label = ctk.CTkLabel(
                    name_row,
                    text=info['display_name'] if info else prov['name'],
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color=Colors.TEXT_PRIMARY
                )
                name_label.pack(side="left")

                if prov['is_default']:
                    default_badge = ctk.CTkLabel(
                        name_row,
                        text="DEFAULT",
                        font=ctk.CTkFont(size=10, weight="bold"),
                        text_color=Colors.BG_PRIMARY,
                        fg_color=Colors.GREEN_PRIMARY,
                        corner_radius=4
                    )
                    default_badge.pack(side="left", padx=10)

                model_name = "Default model"
                if prov['model'] and info:
                    model_name = info['models'].get(prov['model'], prov['model'])

                model_label = ctk.CTkLabel(
                    details,
                    text=f"Model: {model_name}  |  Key: {prov['api_key_preview']}",
                    font=ctk.CTkFont(size=12),
                    text_color=Colors.TEXT_SECONDARY
                )
                model_label.pack(anchor="w")

                # Action buttons
                actions = ctk.CTkFrame(prov_frame, fg_color="transparent")
                actions.pack(side="right", padx=15, pady=12)

                if not prov['is_default']:
                    set_default_btn = ctk.CTkButton(
                        actions,
                        text="Set Default",
                        width=90,
                        height=32,
                        font=ctk.CTkFont(size=12),
                        fg_color=Colors.BLUE_PRIMARY,
                        hover_color=Colors.BLUE_HOVER,
                        corner_radius=8,
                        command=lambda p=prov['name']: self._set_default(p)
                    )
                    set_default_btn.pack(side="left", padx=(0, 8))

                remove_btn = ctk.CTkButton(
                    actions,
                    text="Remove",
                    width=80,
                    height=32,
                    font=ctk.CTkFont(size=12),
                    fg_color=Colors.ERROR,
                    hover_color="#DC2626",
                    corner_radius=8,
                    command=lambda p=prov['name']: self._remove_provider(p)
                )
                remove_btn.pack(side="left")
        else:
            no_providers = ctk.CTkLabel(
                providers_card,
                text="No providers configured",
                font=ctk.CTkFont(size=14),
                text_color=Colors.TEXT_SECONDARY
            )
            no_providers.pack(pady=20)

        ctk.CTkFrame(providers_card, fg_color="transparent", height=24).pack()

        # Add new provider
        add_card = ctk.CTkFrame(inner, fg_color=Colors.BG_PRIMARY, corner_radius=16, width=700)
        add_card.pack(fill="x")

        add_header = ctk.CTkLabel(
            add_card,
            text="Add New Provider",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        add_header.pack(pady=(24, 16), padx=24, anchor="w")

        # Provider selection
        provider_select_frame = ctk.CTkFrame(add_card, fg_color="transparent")
        provider_select_frame.pack(fill="x", padx=24, pady=(0, 12))

        self.new_provider_var = ctk.StringVar(value="gemini")

        all_providers = get_all_providers()
        col = 0
        for name, info in all_providers.items():
            rb = ctk.CTkRadioButton(
                provider_select_frame,
                text=info['display_name'],
                variable=self.new_provider_var,
                value=name,
                font=ctk.CTkFont(size=13),
                fg_color=Colors.BLUE_PRIMARY
            )
            rb.grid(row=0, column=col, padx=10, pady=5, sticky="w")
            col += 1

        # API key and model
        input_frame = ctk.CTkFrame(add_card, fg_color="transparent")
        input_frame.pack(fill="x", padx=24, pady=(0, 24))

        self.new_api_key_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter API key...",
            width=350,
            height=45,
            font=ctk.CTkFont(size=13),
            show="*",
            border_width=2,
            border_color=Colors.BORDER,
            corner_radius=10
        )
        self.new_api_key_entry.pack(side="left", padx=(0, 12))

        add_btn = ctk.CTkButton(
            input_frame,
            text="Add Provider",
            width=130,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=Colors.GREEN_PRIMARY,
            hover_color=Colors.GREEN_HOVER,
            corner_radius=10,
            command=self._add_provider
        )
        add_btn.pack(side="left")

    def _set_default(self, provider_name: str):
        """Set provider as default"""
        self.api_manager.set_default_provider(provider_name)
        self.show_settings_view()

    def _remove_provider(self, provider_name: str):
        """Remove a provider"""
        if messagebox.askyesno("Confirm", f"Remove {provider_name}?"):
            self.api_manager.remove_provider(provider_name)
            if not self.api_manager.has_any_provider():
                self.show_setup_view()
            else:
                self.show_settings_view()

    def _add_provider(self):
        """Add a new provider"""
        provider = self.new_provider_var.get()
        api_key = self.new_api_key_entry.get().strip()

        if not api_key:
            messagebox.showwarning("Warning", "Please enter an API key")
            return

        info = get_provider_info(provider)
        default_model = info['default_model'] if info else None

        try:
            self.api_manager.add_provider(provider, api_key, default_model, set_as_default=False)
            self.show_settings_view()
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    """Main entry point"""
    app = DocumentSummarizerApp()
    app.mainloop()


if __name__ == '__main__':
    main()
