import os
import base64
import pathlib

# Define source and destination directories
source_dir = "pdf_images_numbered"  # Replace with your source directory path
output_dir = "pdf_images_numbered_base64"  # Replace with your output directory path

# Create output directory if it doesn't exist
pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

# Supported image extensions
image_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".gif")

# Iterate through files in the source directory
for filename in os.listdir(source_dir):
    if filename.lower().endswith(image_extensions):
        # Read the image file
        file_path = os.path.join(source_dir, filename)
        with open(file_path, "rb") as image_file:
            # Convert image to Base64
            base64_string = base64.b64encode(image_file.read()).decode("utf-8")
        
        # Define output file path (e.g., image1.jpg -> image1.txt)
        output_filename = os.path.splitext(filename)[0] + ".txt"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save Base64 string to a text file
        with open(output_path, "w") as output_file:
            output_file.write(base64_string)
        
        print(f"Converted {filename} to Base64 and saved as {output_filename}")

print("Conversion complete!")