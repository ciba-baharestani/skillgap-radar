import glob
import os
import re
from bs4 import BeautifulSoup

OUT_DIR = "data/processed/program_text"
os.makedirs(OUT_DIR, exist_ok=True)

STRICT = ["script", "style", "noscript", "svg", "nav", "footer", "header", "form"]
LIGHT = ["script", "style", "noscript", "svg"]

PATTERNS = {
    "price": r"\$\s?\d[\d,]*(?:\.\d\d)?",
    "credits": r"\b\d{1,2}\s*(?:credit|credits|credit hours|credit-hours)\b",
    "duration": r"\b\d{1,2}\s*(?:weeks?|months?|semesters?)\b",
}


def extract_text(html, strip_tags):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(strip_tags):
        tag.decompose()
    text = soup.get_text("\n", strip=True)
    return soup, re.sub(r"\n{2,}", "\n", text)


for path in sorted(glob.glob("data/raw/programs/*.html")):
    slug = os.path.basename(path).replace(".html", "")
    with open(path, encoding="utf-8") as f:
        html = f.read()

    mode = "strict"
    soup, text = extract_text(html, STRICT)
    if len(text) < 500:
        mode = "light (fallback)"
        soup, text = extract_text(html, LIGHT)

    title = soup.title.get_text(strip=True) if soup.title else ""
    h1 = soup.find("h1")
    h1_text = h1.get_text(" ", strip=True) if h1 else ""

    with open(f"{OUT_DIR}/{slug}.txt", "w", encoding="utf-8") as out:
        out.write(text)

    print("=" * 70)
    print(slug, "| text length:", len(text), "| cleanup:", mode)
    print("title:", " ".join(title.split())[:100])
    print("h1:   ", h1_text[:100])
    for label, pattern in PATTERNS.items():
        hits = []
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            start = max(0, m.start() - 40)
            hits.append(text[start:m.end() + 40].replace("\n", " "))
            if len(hits) == 2:
                break
        print(f"{label}:", hits if hits else "none found")