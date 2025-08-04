import csv
import sys

# ---- Configuration ----
input_file = 'YOUR_FILE_PATH.csv'           # <-- Change this to your file name
base, ext = os.path.splitext(input_file)
output_file = base + '_corrected' + ext     # <-- Output file name, e.g., 'YOUR_FILE_PATH_corrected.csv'

expected_cols = 10                            # <-- Number of columns expected (set to your CSV's header)

# ---- Fix CSV ----
with open(input_file, 'r', encoding='utf-8', errors='replace') as infile:
    reader = csv.reader(infile, delimiter=',', quotechar='"')
    rows = list(reader)

corrected_rows = []
for row in rows:
    if len(row) < expected_cols:
        row += [''] * (expected_cols - len(row))  # Pad if too short
    elif len(row) > expected_cols:
        # Merge any extra columns into the last column (comma-separated)
        row = row[:expected_cols-1] + [",".join(row[expected_cols-1:])]
    corrected_rows.append(row)

with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerows(corrected_rows)

print(f"Done! Corrected CSV saved as {output_file}")
