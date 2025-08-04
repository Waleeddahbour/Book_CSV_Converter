import os
import time
import base64
import openai
from tqdm import tqdm
import re

IMAGE_DIR =      "pdf_images_numbered"
FINAL_CSV =      "final_extracted.csv"       
RESULTS_FILE =   "llm_raw_results.txt"  # Raw results file to store LLM responses
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"  # Set your OpenAI API key here
MODEL =          "gpt-4o"               # <- Adjust model as needed, e.g., "gpt-4o-mini". gpt-4o is recommended for image based inputs.  

BATCH_SIZE = 12     # Number of images to process in each batch
BATCH_DELAY = 30    # Delay between batches in seconds
MAX_RETRIES = 5     # Maximum number of retries for LLM requests
RETRY_DELAY = 60    # Delay between retries in seconds

PROMPT_TEMPLATE = """
You are an expert chef extracting unstructured content from scanned cookbook images.

Your goal is to identify and extract every **distinct content section**: recipes, notes, essays, history, general information, or any other major block, as they appear on the page. 
usually there is no indicators; use your best judgment as an expert chef to determine the boundaries of each section.
For each output row, match the content to the **exact page number(s)**. If a section spans multiple consecutive pages, use a comma-separated list (e.g., "5,6,7").
Page numbers are written on the top of each image, so you can easily see which page each image corresponds to.
The most important thing do not summaraize or paraphrase the content; copy it as-is, and use your best judgement as a high level expert chef in placeing them under the correct column(Header).

**Section boundaries:**  
- Start a new section/row for every visually or logically distinct block: headings, note, separate recipes, essays, or visually separated lists.
- When a section spans multiple pages, merge its content into one row, listing all page numbers.
- **Do NOT merge multiple notes, recipes, or unrelated content into a single row.**
- For correct page referencing, always use the actual page numbers for each image, in the Page_Numbers field. The order of images you receive will always match the order of pages.



**Rules:**
- Write extracted content in a CSV format containting 10 columns. like the example below.
- Use double quotes to enclose all fields, even if they do not contain commas.
- Use a comma to separate fields.
- Use a semicolon to separate items in multi-item fields (e.g., Ingredients, Instructions
- ALL fields must in two double quotes **(i.e, ""history of egg, is ancient...."")**, even if they do not contain commas.
- Do not summarize or condense content; extract it as-is.
- Use the exact text for section titles, recipe names, instructions, and notes.
- For fields like Ingredients, Instructions; join items with a semicolon.
- All fields must be present for every row; use empty string ("") if not applicable.
- **Never merge multiple unrelated Section_Type,Section_Title,Recipe_Name,Servings,Ingredients,Instructions,Notes,General_Information, and History into a single row. **Err on the side of splitting too much rather than too little.

**Section Types:**
- "Recipe": Typically has a title, ingredient list (with quantities), and instructions.
- "General_Information": Narrative, essay, or explanatory text, it could be about the recipe or information in general.
- "History": Historical or cultural context related to the content.



For each section, output a single row in a CSV file with these columns (in this exact order):
Page_Numbers,Section_Type,Section_Title,Recipe_Name,Servings,Ingredients,Instructions,Notes,General_Information,History

"Page_Numbers": Comma-separated list of all page numbers where the section appears (e.g., "2,3").
"Section_Type": One of ["Recipe", "History", "General_Information"].
"Section_Title": Section heading.
"Recipe_Name": Recipe title if a recipe, else "".
"Servings": Serving info (e.g., "Serves 2-4"), else "".
"Ingredients": List of ingredient strings (e.g., ["2 cups flour", "1/2 spoon of salt"]), else "".
"Instructions": List of steps or a single string, else "".
"Notes": Notes, comments, as a single string (often boxed, highlighted or bold don't mix them with titles use your best judgement) at the end of the section if it is provided, else "".
"General_Information": Background or introductory text, as a single string, else "".
"History": Historical or cultural context text, as a single string, else "".

Use a comma-separated list for Page_Numbers (e.g., "2,3").
For multi-item fields (ingredients, instructions, history), use a semicolon to separate each item.

**Output ONLY a valid CSV file with a header and one row per section, in the correct reading order.**


**example output**

Page_Numbers,Section_Type,Section_Title,Recipe_Name,Servings,Ingredients,Instructions,Notes,General_Information,History
"1,2,3",""Recipe"",""Chocolate Cake"",""Chocolate Cake"",""Serves 8","2 cups flour;1 cup sugar;2 eggs"",""Preheat oven to 350°F;Mix dry ingredients;Bake for 30 minutes"",""Use dark chocolate for richer flavor"",""Chocolate cake is a classic dessert enjoyed worldwide."",""The history of chocolate dates back to ancient Mesoamerica, where it was consumed as a bitter beverage.""
image:
"""


# Initialize OpenAI client (openai>=1.0.0)
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

def extract_page_number(filename):
    """
    Extract page number from filename like page123.jpg -> 123
    """
    match = re.search(r'page(\d+)\.jpg', filename, re.IGNORECASE)
    return int(match.group(1)) if match else float('inf')  # Put non-matching files at the end

def get_image_files(image_dir, max_pages=None, extensions=('.jpg', '.jpeg', '.png')):
    """
    Get images ordered numerically by page number, even with gaps.
    """
    files = [f for f in os.listdir(image_dir) if f.lower().endswith(extensions)]')]
    files = sorted(files, key=extract_page_number)
    images = [os.path.join(image_dir, f) for f in files]
    return images

def batch_images(image_files, batch_size):
    """
    Yield batches of images and their starting page index (1-based).
    """
    for i in range(0, len(image_files), batch_size):
        yield image_files[i:i + batch_size], i+1

def clean_llm_csv(llm_response):
    """
    Extract the CSV content, removing any LLM commentary or stray output above/below.
    """
    lines = llm_response.strip().splitlines()
    # Find the header line (should always start with 'Page_Numbers')
    header_idx = next((i for i, line in enumerate(lines) if line.strip().startswith("Page_Numbers")), None)
    if header_idx is None:
        return ""  # No CSV found

    # Optionally, stop at the first empty line after the CSV (in case LLM adds explanation at end)
    content_lines = []
    for line in lines[header_idx:]:
        if line.strip() == "":
            break
        content_lines.append(line)
    return "\n".join(content_lines)

def main():
    image_files = get_image_files(IMAGE_DIR, max_pages=len(os.listdir(IMAGE_DIR)))
    image_files = image_files[:len(image_files) - len(image_files) % BATCH_SIZE]  # Ensure we have a full batch
    # image_files = image_files[-4:]                   # For testing, use only the last 4 images, adjust as needed.
    batches = list(batch_images(image_files, BATCH_SIZE))
    print(f"Total images found: {len(image_files)}")


    print("\n=== DEBUG: List of all batches and their images ===")
    for idx, (batch_imgs, batch_start) in enumerate(batches):
        imgs_display = [os.path.basename(i) for i in batch_imgs]
        # Only print if batch has images
        if imgs_display:
            first_page = extract_page_number(imgs_display[0])
            last_page = extract_page_number(imgs_display[-1])
            print(f"batch {idx+1} (pages {first_page}-{last_page}):")
            print(imgs_display)
            print()
    print("=== END DEBUG ===\n")

    all_csv_rows = []
    header_written = False

    with open(RESULTS_FILE, "w", encoding="utf-8") as out_f:
        for batch_imgs, batch_start in tqdm(batches, desc="LLM Processing"):
            print(f"Processing batch: start={batch_start}, num_images={len(batch_imgs)}, images={batch_imgs}", end="\n")

            start_page = batch_start
            end_page = batch_start + len(batch_imgs) - 1
            prompt = PROMPT_TEMPLATE
            message_content = [{"type": "text", "text": prompt}]

            for img_path in batch_imgs:
                with open(img_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode()
                message_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                })
            # --- Retry logic ---
            for attempt in range(MAX_RETRIES):
                try:
                    response = openai_client.chat.completions.create(
                        model=MODEL,
                        messages=[{"role": "user", "content": message_content}],
                        max_tokens=4069,
                        temperature=0,
                    )
                    llm_csv = response.choices[0].message.content
                    cleaned_csv = clean_llm_csv(llm_csv)
                    if cleaned_csv:
                        out_f.write(f"# BATCH {start_page}-{end_page}\n")
                        out_f.write(cleaned_csv.strip() + "\n\n")
                        out_f.flush()
                        # For final CSV: accumulate rows, skip duplicate header
                        for i, row in enumerate(cleaned_csv.splitlines()):
                            if i == 0 and header_written:
                                continue  # skip header
                            all_csv_rows.append(row)
                        header_written = True
                    break  # Success
                except Exception as e:
                    print(f"Error processing batch {start_page}-{end_page} (attempt {attempt+1}): {e}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY * (attempt + 1))
                    else:
                        print(f"Failed batch {start_page}-{end_page} after {MAX_RETRIES} attempts.")

    # write merged CSV (all rows)
    if all_csv_rows:
        with open(FINAL_CSV, "w", encoding="utf-8") as csv_f:
            csv_f.write("\n".join(all_csv_rows))
        print(f"✅ All extracted CSV rows saved to {FINAL_CSV}")

if __name__ == "__main__":
    main()
