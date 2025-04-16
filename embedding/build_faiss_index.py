import json
import faiss
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np

# ==== Settings ====
input_dir = Path("data/chunks_by_section")
output_dir = Path("vector_store")
output_dir.mkdir(parents=True, exist_ok=True)

model_name = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

all_texts = []
all_meta = []
section_map = {}

for fname in ["BNS_sections.json", "BNSS_sections.json", "BSA_sections.json"]:
    path = input_dir / fname
    if not path.exists():
        print(f"[!] Missing: {fname}")
        continue

    with open(path, "r", encoding="utf-8") as f:
        sections = json.load(f)

    for item in sections:
        all_texts.append(item["text"])
        all_meta.append(item)
        section_map[item["section_id"]] = {
            "source": item["source"],
            "title": item.get("title", ""),
            "text": item["text"]
        }

# === Generate Embeddings ===
print(f"Generating embeddings for {len(all_texts)} sections...")
embeddings = model.encode(all_texts, show_progress_bar=True, convert_to_numpy=True)

# === Build FAISS index ===
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# === Save vector index and metadata ===
faiss.write_index(index, str(output_dir / "legal_index.faiss"))

with open(output_dir / "section_map.json", "w", encoding="utf-8") as f:
    json.dump(section_map, f, indent=2, ensure_ascii=False)

print(f"[✓] FAISS index + metadata saved in '{output_dir}/'")