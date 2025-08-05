# Cookbook PDF Extraction & Image Pipeline

This repo contains Python scripts for processing cookbook PDFs, extracting structured recipe data with LLMs, and attaching full-page images (optionally as base64) for downstream applications and visualization.

---

## Pipeline Overview

1. **pdfToImage.py**: Converts PDF pages to images.
2. **burnPageNum.py**: Burns page numbers onto images for LLM reference.
3. **convert64.py**: Converts images to base64-encoded text files.
4. **chatExtraction.py**: Sends images to OpenAI’s GPT-4o for content extraction and outputs a CSV.
5. **fixCSV.py**: Fixes malformed CSV rows to ensure proper structure.
6. **addImages.py**: Attaches base64 images to CSV rows for each page number.
7. **readCSV.py**: Streamlit app to visualize the CSV results and images.

8. **buildFromCheckpoint.py**: Rebuilds the CSV from raw LLM extraction results if needed.


---

## 1. pdfToImage.py

- **Function:** Converts every page of a PDF (`book.pdf`) into a high-quality JPEG image in the `pdf_images/` folder.
- **Usage:**
  ```bash
  python pdfToImage.py
  ```

- **Dependencies:**
  - pdf2image
  - PyPDF2
  - Pillow

---

## Configuration

- Edit `PDF_FILE` in scripts if your PDF is not named `book.pdf`.

---

## Scripts

### 2. burnPageNum.py

- **Function:** Draws page numbers at the top of each image in `pdf_images/`, saving them into `pdf_images_numbered/`.
- **Usage:**
  ```bash
  python burnPageNum.py
  ```
- **Dependencies:**
  - Pillow
  - re

- **Note:**  
  If you have a custom `.ttf` font, set `FONT_PATH` in the script.

---

### 3. convert64.py

- **Function:** Converts each numbered image into a base64 string, saving as `.txt` in `pdf_images_numbered_base64/`.
- **Usage:**
  ```bash
  python convert64.py
  ```
- **Dependencies:**
  - base64
  - pathlib
  - os

---

### 4. chatExtraction.py

- **Function:** Batch-sends images to OpenAI GPT-4o for extracting structured recipe and section data into a CSV.
- **Usage:**
  1. Set your OpenAI API key in `OPENAI_API_KEY`.
  2. Adjust `MODEL` as desired.
  3. Run:
     ```bash
     python chatExtraction.py
     ```
- **Dependencies:**
  - openai >= 1.0.0
  - tqdm
  - base64
  - re
  - os, time

- **Output:**
  - `final_extracted.csv`
  - `llm_raw_results.txt`

---

### 5. fixCSV.py

- **Function:** Fixes malformed CSV files, ensuring every row has the same number of columns (default: 10).
- **Usage:**
  1. Set `input_file` to your CSV.
  2. Run:
     ```bash
     python fixCSV.py
     ```
- **Dependencies:**
  - csv
  - os
  - sys

---

### 6. addImages.py

- **Function:** Adds a column with full-page base64 images to the extracted CSV, matching page numbers.
- **Usage:**
  1. Place `final_extracted.csv` and `pdf_images_numbered_base64/` in the project root.
  2. Run:
     ```bash
     python addImages.py
     ```
- **Dependencies:**
  - pandas
  - os

---

### 7. readCSV.py

- **Function:** Streamlit web app to explore the extracted CSV and preview full-page images inline.
- **Usage:**
  1. Set `latest_csv` in the script.
  2. Run:
     ```bash
     streamlit run readCSV.py
     ```
- **Dependencies:**
  - streamlit
  - pandas
  - base64
  - ast


### 8. buildFromCheckpoint.py

- **Function:**  
  Builds `final_extracted.csv` from `llm_raw_results.txt` in case extraction was interrupted, or you need to re-generate the CSV from raw results. Skips comment lines and blank lines; only the first header is included.

- **Usage:**
  ```bash
  python buildFromCheckpoint.py
  ```

- **Dependencies:**
  - csv
  - (standard Python only; uses no external libraries)

- **Inputs/Outputs:**
  - **Input:** `llm_raw_results.txt`
  - **Output:** `final_extracted.csv`


---

## Directory Structure

```
.
├── book.pdf
├── pdf_images/
├── pdf_images_numbered/
├── pdf_images_numbered_base64/
├── final_extracted.csv
├── CSVs_with_images/
├── [all .py scripts]
```

---

## Setup & Installation

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install system dependencies for `pdf2image` (if not present)

**Linux:**
```bash
sudo apt-get install poppler-utils
```

**Mac:**
```bash
brew install poppler
```

**Windows:**  
- Download [Poppler for Windows]([http://blog.alivate.com.au/poppler-windows/](https://github.com/oschwartz10612/poppler-windows)) or from [the official releases](https://github.com/oschwartz10612/poppler-windows/releases/).
- Extract the downloaded ZIP (e.g., to `C:\poppler`).
- Add the `bin` folder (e.g., `C:\poppler\bin`) to your Windows PATH environment variable.
  - You can do this via Control Panel → System → Advanced system settings → Environment Variables.

Now you can use `pdf2image` scripts on Windows as well.

---
