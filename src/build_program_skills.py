import csv
import re
from pathlib import Path

# Same rules as the posting matcher (extract_skills.py)
EXCLUDE = {"BP08", "BP09"}          # MBA-flavored rows we keep out of the app
SKIP_TERMS = {"rise", "strategy", "metrics"}
CASE_SENSITIVE = {"excel"}


def make_pattern(term):
    if len(term) <= 3:  # short acronyms must be uppercase and not part of an ID
        return re.compile(r"(?<![\w&/\-])" + re.escape(term.upper()) + r"(?![\w&\-])")
    if term in CASE_SENSITIVE:
        return re.compile(r"(?<!\w)" + re.escape(term.capitalize()) + r"s?(?!\w)")
    return re.compile(r"(?<!\w)" + re.escape(term) + r"s?(?!\w)", re.IGNORECASE)


# Taxonomy: id -> name, category, patterns
skills = {}
with open("data/taxonomy_draft.csv", newline="", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        if r["skill_id"] in EXCLUDE:
            continue
        terms = {r["canonical_name"].strip().lower()}
        terms.update(t.strip().lower() for t in r["synonyms"].split(";") if t.strip())
        terms -= SKIP_TERMS
        skills[r["skill_id"]] = {
            "name": r["canonical_name"],
            "category": r["category"],
            "patterns": [make_pattern(t) for t in sorted(terms)],
        }

with open("data/processed/programs.csv", newline="", encoding="utf-8-sig") as f:
    programs = list(csv.DictReader(f))

text_dir = Path("data/processed/program_text")
match_rows = []
info_rows = []
matched_anywhere = set()

for p in programs:
    slug = p["slug"]
    parts = []
    for path in sorted(text_dir.glob("*.txt")):
        if path.stem == slug or path.stem == slug + "_pdf":
            parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    if not parts:
        print(f"WARNING: no text file found for {slug}")
        continue
    text = re.sub(r"\s+", " ", " ".join(parts))

    found = []
    for sid, s in skills.items():
        starts = set()
        for pat in s["patterns"]:
            for m in pat.finditer(text):
                starts.add(m.start())
        if starts:
            matched_anywhere.add(sid)
            found.append((s["name"], len(starts)))
            match_rows.append({
                "slug": slug,
                "skill_id": sid,
                "skill": s["name"],
                "category": s["category"],
                "mentions": len(starts),
            })
    info_rows.append({
        "slug": slug,
        "program": p["program"],
        "family": p["family"],
        "url": p["url"],
    })
    found.sort(key=lambda x: -x[1])
    top = ", ".join(f"{n} ({c})" for n, c in found[:5])
    print(f"{p['program']}: {len(text)} chars, {len(found)} skills. Top: {top}")

Path("data/app").mkdir(exist_ok=True)
with open("data/app/program_skills.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["slug", "skill_id", "skill", "category", "mentions"])
    w.writeheader()
    w.writerows(match_rows)
with open("data/app/program_info.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["slug", "program", "family", "url"])
    w.writeheader()
    w.writerows(info_rows)

print(f"\nSaved {len(match_rows)} program-skill matches for {len(info_rows)} programs")
print(f"Skills found in at least one program: {len(matched_anywhere)} of {len(skills)}")