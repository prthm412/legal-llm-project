import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import json

# === Configuration ===
section_limit_per_law = 10
case_limit_per_section = 3
headers = {"User-Agent": "Mozilla/5.0"}
base_search_url = "https://indiankanoon.org/search/?formInput="
base_domain = "https://indiankanoon.org"

json_paths = {
    "BNS": "data/chunks_by_section/BNS_sections.json",
    "BNSS": "data/chunks_by_section/BNSS_sections.json",
    "BSA": "data/chunks_by_section/BSA_sections.json"
}

law_names = {
    "BNS": "Bharatiya Nyaya Sanhita",
    "BNSS": "Bharatiya Nagarik Suraksha Sanhita",
    "BSA": "Bharatiya Sakshya Adhiniyam"
}

for law_code, json_file in json_paths.items():
    print(f"\n📚 Collecting cases for: {law_code}")
    with open(json_file, "r", encoding="utf-8") as f:
        sections = json.load(f)

    used = set()
    selected = []

    for entry in sections:
        sec_no = entry["section_id"].split("_")[-1]
        if sec_no not in used:
            selected.append(sec_no)
            used.add(sec_no)
        if len(selected) >= section_limit_per_law:
            break

    folder = Path(f"court_cases/raw/{law_code}")
    folder.mkdir(parents=True, exist_ok=True)

    for sec_no in selected:
        query = f"Section {sec_no} {law_names[law_code]}"
        print(f"  🔍 Searching: {query}")

        search_url = base_search_url + query.replace(" ", "%20")
        try:
            res = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.select("a[href^='/doc/']")
        except Exception as e:
            print(f"  [!] Failed to search: {e}")
            continue

        seen = set()
        count = 0

        for link in links:
            if count >= case_limit_per_section:
                break
            href = link["href"]
            if href in seen:
                continue
            seen.add(href)

            case_url = base_domain + href
            try:
                case_page = requests.get(case_url, headers=headers)
                case_soup = BeautifulSoup(case_page.text, "html.parser")
                content_tag = case_soup.find("pre")
                if content_tag:
                    text = content_tag.get_text()
                    file_name = f"section_{sec_no}_case_{count+1}.txt"
                    out_file = folder / file_name
                    out_file.write_text(text.strip(), encoding="utf-8")
                    print(f"    ✅ Saved: {file_name}")
                    count += 1
                time.sleep(1.5)
            except Exception as e:
                print(f"    [!] Error fetching case: {e}")
