import csv
import os
import re
from bs4 import BeautifulSoup

TEXT_DIR = "data/processed/program_text"

PATTERNS = {
    "price_hint": r"\$\s?\d[\d,]*(?:\.\d\d)?",
    "credits_hint": r"\b\d{1,2}\s*(?:credit|credits|credit hours|credit-hours|cr)\b",
    "duration_hint": r"\b\d{1,2}\s*(?:weeks?|months?|semesters?)\b",
}


def first_match(pattern, text):
    m = re.search(pattern, text, flags=re.IGNORECASE)
    return m.group(0) if m else ""


with open("data/program_urls.csv", newline="", encoding="utf-8") as f:
    programs = list(csv.DictReader(f))

rows = []
for p in programs:
    slug = re.sub(r"[^a-z0-9]+", "_", p["program"].lower()).strip("_")

    with open(f"{TEXT_DIR}/{slug}.txt", encoding="utf-8") as f:
        text = f.read()
    extra = f"{TEXT_DIR}/{slug}_pdf.txt"
    has_pdf = os.path.exists(extra)
    if has_pdf:
        with open(extra, encoding="utf-8") as f:
            text += "\n" + f.read()

    with open(f"data/raw/programs/{slug}.html", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    title = " ".join(soup.title.get_text().split()).split(" | ")[0] if soup.title else ""

    row = {
        "slug": slug,
        "family": p["family"],
        "program": p["program"],
        "page_title": title,
        "url": p["url"],
        "text_chars": len(text),
        "manual_pdf_added": has_pdf,
    }
    for label, pattern in PATTERNS.items():
        row[label] = first_match(pattern, text)
    rows.append(row)

with open("data/processed/programs.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print("Saved data/processed/programs.csv with", len(rows), "programs\n")
for r in rows:
    print(f'{r["slug"]:34} {r["text_chars"]:>6} chars | price: {r["price_hint"] or "-":9} | credits: {r["credits_hint"] or "-":11} | duration: {r["duration_hint"] or "-"}')