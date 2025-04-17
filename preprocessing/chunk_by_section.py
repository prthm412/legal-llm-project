import re
import json
from pathlib import Path

# Input/output
input_dir = Path("data/txt")
output_dir = Path("data/chunks_by_section")
output_dir.mkdir(parents=True, exist_ok=True)

files = {
    "BNS": "BNS_final.txt",
    "BNSS": "BNSS_final.txt",
    "BSA": "BSA_final.txt"
}

# Regex pattern to find start of sections
SECTION_PATTERN = re.compile(r"\n(\d+)\.\s+([^\n]*)")

for code, filename in files.items():
    path = input_dir / filename
    if not path.exists():
        print(f"[!] Skipping missing file: {filename}")
        continue

    text = path.read_text(encoding="utf-8")

    # Find section starts
    matches = list(SECTION_PATTERN.finditer(text))
    print(f"[✓] Found {len(matches)} sections in {code}")

    sections = []

    for i, match in enumerate(matches):
        section_num = match.group(1)
        section_title = match.group(2).strip()

        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        section_text = text[start:end].strip()

        sections.append({
            "source": code,
            "section_id": f"{code}_{section_num}",
            "title": section_title,
            "text": section_text
        })

    out_path = output_dir / f"{code}_sections.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(sections, f, indent=2, ensure_ascii=False)

    print(f"[✓] Saved {len(sections)} chunks to {out_path.name}")