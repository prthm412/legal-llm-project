import fitz  # PyMuPDF
from pathlib import Path
from tqdm import tqdm

# Define input and output folders
input_folder = Path("data")
output_folder = Path("data/txt")
output_folder.mkdir(parents=True, exist_ok=True)

# List your law files
law_files = {
    "BNS": "BNS_2023.pdf",
    "BNSS": "BNSS_2023.pdf",
    "BSA": "BSA_2023.pdf"
}

# Convert each PDF
for law_code, filename in law_files.items():
    pdf_path = input_folder / filename
    txt_path = output_folder / f"{law_code}.txt"

    print(f"Converting {filename}...")
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in tqdm(doc, desc=f"{law_code}"):
        full_text += page.get_text()

    txt_path.write_text(full_text, encoding="utf-8")
    print(f"Saved to: {txt_path}\n")
