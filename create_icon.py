"""
Generate application icon for Document Summarizer
Run this once to create the icon.ico file
"""
from PIL import Image, ImageDraw, ImageFont

def create_app_icon():
    """Create a professional-looking app icon"""
    # Create multiple sizes for the .ico file
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    images = []

    for size in sizes:
        width, height = size

        # Create an image with gradient background
        image = Image.new('RGB', (width, height), 'white')
        dc = ImageDraw.Draw(image)

        # Draw gradient background (green theme)
        for i in range(height):
            # Gradient from light green to darker green
            r = int(76 - (i / height) * 20)
            g = int(175 - (i / height) * 30)
            b = int(80 - (i / height) * 20)
            dc.rectangle([0, i, width, i+1], fill=(r, g, b))

        # Calculate sizes based on icon size
        margin = int(width * 0.15)
        doc_width = width - (2 * margin)
        doc_height = int(height * 0.7)
        doc_x = margin
        doc_y = int((height - doc_height) / 2)

        # Draw document shape (white paper)
        # Main document body
        dc.rectangle(
            [doc_x, doc_y, doc_x + doc_width, doc_y + doc_height],
            fill='white',
            outline='#333333',
            width=max(1, int(width / 32))
        )

        # Folded corner
        fold_size = int(doc_width * 0.2)
        dc.polygon([
            (doc_x + doc_width - fold_size, doc_y),
            (doc_x + doc_width, doc_y + fold_size),
            (doc_x + doc_width, doc_y)
        ], fill='#E0E0E0', outline='#333333')

        dc.line([
            (doc_x + doc_width - fold_size, doc_y),
            (doc_x + doc_width, doc_y + fold_size)
        ], fill='#333333', width=max(1, int(width / 64)))

        # Draw text lines on the document
        line_margin = int(doc_width * 0.15)
        line_width = doc_width - (2 * line_margin)
        line_height = max(2, int(height / 64))
        line_spacing = int(height / 20)
        start_y = doc_y + int(doc_height * 0.3)

        # Draw 4-5 lines depending on icon size
        num_lines = 4 if width < 64 else 5
        for i in range(num_lines):
            y = start_y + (i * line_spacing)
            if y + line_height < doc_y + doc_height - margin:
                # Make some lines shorter
                if i == num_lines - 1:
                    line_width = int(line_width * 0.6)
                dc.rectangle(
                    [doc_x + line_margin, y, doc_x + line_margin + line_width, y + line_height],
                    fill='#666666'
                )

        images.append(image)

    # Save as .ico file
    images[0].save(
        'icon.ico',
        format='ICO',
        sizes=[(img.width, img.height) for img in images],
        append_images=images[1:]
    )

    print("✅ Icon created successfully: icon.ico")

    # Also save as PNG for reference
    images[0].save('icon.png', format='PNG')
    print("✅ PNG version created: icon.png")

if __name__ == '__main__':
    create_app_icon()
