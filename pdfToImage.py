from pdf2image import convert_from_path
import os

PDF_FILE = "book.pdf" # Path to the input PDF file, Replace with your actual PDF file path
IMAGE_DIR = "pdf_images"
DPI = 300

os.makedirs(IMAGE_DIR, exist_ok=True)

from PyPDF2 import PdfReader
num_pages = len(PdfReader(PDF_FILE).pages)

print("Converting PDF to images (JPEG)...")
for page in range(1, num_pages + 1):
    images = convert_from_path(PDF_FILE, dpi=DPI, first_page=page, last_page=page)
    img = images[0].convert("RGB")
    img_path = os.path.join(IMAGE_DIR, f"page{page}.jpg")
    img.save(img_path, "JPEG", quality=95)
    print(f"Saved {img_path}")       