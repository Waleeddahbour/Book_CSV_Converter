import os
from PIL import Image, ImageDraw, ImageFont
import re

# === CONFIGURATION ===
INPUT_DIR = "pdf_images"              # Folder with images
OUTPUT_DIR = "pdf_images_numbered"    # Folder to save new images
FONT_SIZE = 48
TOP_PADDING = 40                      # distance from the top of the image to the text
FONT_PATH = None                 # Or a path to your preferred .ttf

def burn_page_number(image_path, output_path, page_number, font_size=FONT_SIZE, top_padding=TOP_PADDING, font_path=FONT_PATH):
    """
    Opens an image, draws the page number at the top, and saves it.
    :param image_path: Path to the input image file.
    :param output_path: Path to save the modified image.
    :param page_number: The page number to burn into the image.
    :param font_size: Size of the font for the page number.
    :param top_padding: Distance from the top of the image to the text.
    :param font_path: Path to the .ttf font file to use, or None to use default.
    """
    img = Image.open(image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)


    # Load the font
    if font_path is None:
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(font_path, font_size)

    # Prepare the text and its position
    text = f"Page {page_number}"
    text_width, text_height = draw.textsize(text, font=font) # Mesures of the text size
    x = (img.width - text_width) // 2   # Center the text horizontally
    y = top_padding                # Position the text at the top with padding

    # Semi-transparent white rectangle for contrast
    rect_height = text_height + 16
    rect_width = text_width + 32
    rect_x0 = x - 16
    rect_y0 = y - 8
    rectangle = Image.new("RGBA", (rect_width, rect_height), (255,255,255,180))
    img.paste(rectangle, (rect_x0, rect_y0), rectangle)

    # Draw text
    draw.text((x, y), text, font=font, fill=(0,0,0,255))
    img.convert("RGB").save(output_path)

def extract_page_number(filename):
    """ 
    Tries to extract the page number from the filename, like 'page1.png'.
    Returns the page number as an integer or None if not found."""
    match = re.search(r'page(\d+)', filename, re.IGNORECASE)
    return int(match.group(1)) if match else None

# Ensure the output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Process each image in the input directory
for fname in os.listdir(INPUT_DIR):
    # Process only image files
    if fname.lower().endswith((".png", ".jpg", ".jpeg")):
        page_num = extract_page_number(fname)
        if page_num is not None:
            in_path = os.path.join(INPUT_DIR, fname)
            out_path = os.path.join(OUTPUT_DIR, fname)
            burn_page_number(in_path, out_path, page_num)
            print(f"✅ Burned Page {page_num} on {fname}")
        else:
            print(f"❌ Could not extract page number from {fname}")
