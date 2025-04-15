from pathlib import Path
import re

# Folder where cleaned text files are
input_dir = Path("data/txt")
files_to_clean = ["BNS_cleaned.txt", "BNSS_cleaned.txt", "BSA_cleaned.txt"]

for file_name in files_to_clean:
    file_path = input_dir / file_name
    output_path = input_dir / f"{file_name.replace('_cleaned', '_final')}"

    if not file_path.exists():
        print(f"[!] Skipping missing file: {file_path.name}")
        continue

    text = file_path.read_text(encoding="utf-8")

    # Remove standalone page numbers (e.g., a line with just "15")
    cleaned_lines = []
    for line in text.splitlines():
        if re.fullmatch(r"\d+", line.strip()):
            continue  # Skip pure numbers
        cleaned_lines.append(line)

    # Join lines back
    cleaned_text = "\n".join(cleaned_lines)

    # Save cleaned version
    output_path.write_text(cleaned_text, encoding="utf-8")
    print(f"[✓] Cleaned and saved: {output_path.name}")
