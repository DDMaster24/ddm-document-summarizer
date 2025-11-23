"""
Desktop Launcher for Document Summarizer
Runs the Flask app in background with system tray icon
"""
import os
import sys
import threading
import webbrowser
import time
from pathlib import Path
import pystray
from PIL import Image, ImageDraw
from werkzeug.serving import make_server

# Import the Flask app
from app import app, cleanup_folders, api_manager

class DocumentSummarizerApp:
    def __init__(self):
        self.server = None
        self.server_thread = None
        self.port = 5000
        self.host = '127.0.0.1'
        self.icon = None
        self.running = False

    def create_icon_image(self):
        """Create a simple icon for the system tray"""
        # Create a simple icon with a document symbol
        width = 64
        height = 64

        # Create an image with a white background
        image = Image.new('RGB', (width, height), 'white')
        dc = ImageDraw.Draw(image)

        # Draw a simple document icon
        # Document outline
        dc.rectangle([10, 5, 54, 59], outline='#4CAF50', width=3, fill='white')
        # Folded corner
        dc.polygon([54, 5, 54, 15, 44, 5], fill='#4CAF50')
        # Lines representing text
        dc.rectangle([18, 20, 46, 23], fill='#666666')
        dc.rectangle([18, 28, 46, 31], fill='#666666')
        dc.rectangle([18, 36, 38, 39], fill='#666666')

        return image

    def open_browser(self):
        """Open the app in the default browser"""
        url = f'http://{self.host}:{self.port}'
        webbrowser.open(url)

    def start_flask_server(self):
        """Start the Flask server in a separate thread"""
        try:
            # Clean up folders
            cleanup_folders()

            # Create the server
            self.server = make_server(self.host, self.port, app, threaded=True)
            self.running = True

            print(f"\n{'='*60}")
            print("📄 Document Summarizer is running...")
            print(f"{'='*60}\n")

            if not api_manager.has_any_provider():
                print("⚠️  No AI provider configured yet!")
                print("The setup wizard will open in your browser.\n")
            else:
                default = api_manager.get_default_provider()
                print(f"✅ Using {default.upper()} as the default AI provider\n")

            print(f"🌐 Access the app at: http://{self.host}:{self.port}")
            print("💡 Use the system tray icon to quit\n")

            # Open browser after a short delay
            time.sleep(2)
            self.open_browser()

            # Start serving
            self.server.serve_forever()

        except Exception as e:
            print(f"Error starting server: {e}")
            self.running = False

    def stop_server(self):
        """Stop the Flask server"""
        if self.server:
            print("\n📄 Shutting down Document Summarizer...")
            self.running = False
            self.server.shutdown()

    def on_open_clicked(self, icon, item):
        """Handle 'Open' menu click"""
        self.open_browser()

    def on_quit_clicked(self, icon, item):
        """Handle 'Quit' menu click"""
        self.stop_server()
        icon.stop()

    def setup_tray_icon(self):
        """Setup the system tray icon"""
        # Create icon image
        icon_image = self.create_icon_image()

        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem('Open Document Summarizer', self.on_open_clicked, default=True),
            pystray.MenuItem('Quit', self.on_quit_clicked)
        )

        # Create icon
        self.icon = pystray.Icon(
            'Document Summarizer',
            icon_image,
            'Document Summarizer',
            menu
        )

    def run(self):
        """Run the application"""
        # Start Flask server in background thread
        self.server_thread = threading.Thread(target=self.start_flask_server, daemon=True)
        self.server_thread.start()

        # Setup and run system tray icon (this blocks until quit)
        self.setup_tray_icon()
        self.icon.run()

        # Wait for server thread to finish
        if self.server_thread.is_alive():
            self.server_thread.join(timeout=2)

def main():
    """Main entry point"""
    # Set the working directory to the script's directory
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        application_path = os.path.dirname(sys.executable)
    else:
        # Running as script
        application_path = os.path.dirname(os.path.abspath(__file__))

    os.chdir(application_path)

    # Create and run the app
    app_instance = DocumentSummarizerApp()
    app_instance.run()

if __name__ == '__main__':
    main()
