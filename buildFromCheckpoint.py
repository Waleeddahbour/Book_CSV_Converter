import csv

raw_results_file = "llm_raw_results.txt"
final_csv_file = "final_extracted.csv"

csv_rows = []

with open(raw_results_file, "r", encoding="utf-8") as infile:
    lines = infile.readlines()

header = None
for line in lines:
    line = line.strip()
    if not line or line.startswith("#"):  # skip comments and blanks
        continue
    if line.startswith("Page_Numbers"):
        if not header:
            header = line
            csv_rows.append(header)
        continue  # skip extra headers after the first one
    csv_rows.append(line)

with open(final_csv_file, "w", encoding="utf-8", newline='') as outfile:
    for row in csv_rows:
        outfile.write(row + "\n")

print(f"Done! Final CSV built and saved to {final_csv_file}")
