import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time

# === Configuration ===
law_queries = {
    "BSA": [
        "section 27 Indian Evidence Act",
        "section 32 Indian Evidence Act",
        "section 114 Indian Evidence Act",
        "section 65B Indian Evidence Act"
    ]
}

base_search_url = "https://indiankanoon.org/search/?formInput="
base_domain = "https://indiankanoon.org"
headers = {"User-Agent": "Mozilla/5.0"}

case_limit_per_query = 5  # Adjust for more/fewer cases per search

for law_code, queries in law_queries.items():
    out_dir = Path(f"court_cases/full_raw/{law_code}")
    out_dir.mkdir(parents=True, exist_ok=True)
    case_num = 1
    for query in queries:
        print(f"\n[🔍] Searching: {query}")
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
            if count >= case_limit_per_query:
                break
            href = link["href"]
            if href in seen:
                continue
            seen.add(href)

            case_url = base_domain + href
            try:
                case_page = requests.get(case_url, headers=headers)
                case_soup = BeautifulSoup(case_page.text, "html.parser")
                # Try <pre>, else fallback to <body>
                content_tag = case_soup.find("pre")
                if content_tag:
                    text = content_tag.get_text()
                else:
                    main_div = case_soup.find("body")
                    if main_div:
                        text = main_div.get_text(separator="\n", strip=True)
                    else:
                        text = ""
                if text.strip():
                    filename = out_dir / f"case_{case_num}.txt"
                    filename.write_text(text.strip(), encoding="utf-8")
                    print(f"    ✅ Saved: {filename.name}")
                    case_num += 1
                    count += 1
                time.sleep(1.5)
            except Exception as e:
                print(f"    [!] Error fetching case: {e}")
