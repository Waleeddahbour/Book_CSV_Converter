import pandas as pd
import os

CSV_PATH = "final_extracted.csv" # Path to the input CSV file
IMG_DIR = "pdf_images_numbered_base64" # Directory containing the base64 encoded images

Original_Filename = os.path.splitstext(CSV_PATH)[0] # Extract the base filename without extension

Output_DIR = "CSVs_with_images" # Directory to save the output CSV files
os.makedirs(Output_DIR, exist_ok=True) # Create the output directory if it does not exist

OUT_CSV = os.path.join(Output_DIR, f"{Original_Filename}.csv") # Output CSV file with full page images

df = pd.read_csv(CSV_PATH)

def get_base64_for_pages(page_numbers):
    """
    Given a string of comma-separated page numbers, retrieve the corresponding
    base64-encoded images from IMG_DIR and return them as a list.
    If a file is missing, append an empty string for that page.
    """
    images = []
    for page in str(page_numbers).split(","): # Split the string into individual page numbers
        page = page.strip() # Remove any leading/trailing whitespace
        if not page.isdigit():
            continue    # Skip if the page number is not a digit
        fname = f"page{int(page)}.txt" # Construct the filename based on the page number
        fpath = os.path.join(IMG_DIR, fname) # construct the full path to the image file
        if os.path.isfile(fpath): # Check if the file exists
            with open(fpath, "r", encoding="utf-8") as f: # Open the file and read its content
                images.append(f.read().strip()) # Append the base64 content to the list
        else:
            images.append("") # Append an empty string if the file does not exist
    return images

# Apply the function to the 'Page_Numbers' column and create a new column 'full_page_image'
df["full_page_image"] = df["Page_Numbers"].apply(get_base64_for_pages) 

df.to_csv(OUT_CSV, index=False)
print(f"Saved with images: {OUT_CSV}")
