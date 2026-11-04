import csv
import json
import os
import re

with open("data/onet_occupations.csv", newline="", encoding="utf-8") as f:
    occupations = list(csv.DictReader(f))

os.makedirs("data/processed", exist_ok=True)
skill_rows, tech_rows = [], []

for occ in occupations:
    code = occ["onet_code"]
    base = {"family": occ["family"], "onet_code": code, "onet_title": occ["onet_title"]}

    with open(f"data/raw/onet/details/{code}_skills.json", encoding="utf-8") as f:
        for el in json.load(f).get("element", []):
            skill_rows.append({**base, "skill": el.get("name"), "importance": el.get("importance")})

    with open(f"data/raw/onet/details/{code}_technology_skills.json", encoding="utf-8") as f:
        for cat in json.load(f).get("category", []):
            for ex in cat.get("example", []):
                tech_rows.append({**base, "category": cat.get("title"), "example": ex.get("title")})

def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

write_csv("data/processed/onet_skills.csv", skill_rows)
write_csv("data/processed/onet_tech.csv", tech_rows)
print("onet_skills.csv rows:", len(skill_rows))
print("onet_tech.csv rows:", len(tech_rows))

# Top 3 generic skills per occupation
print()
for occ in occupations:
    rows = [r for r in skill_rows if r["onet_code"] == occ["onet_code"]]
    rows.sort(key=lambda r: r["importance"] or 0, reverse=True)
    top = ", ".join(f'{r["skill"]} ({r["importance"]})' for r in rows[:3])
    print(f'{occ["onet_title"]}: {top}')

# Coverage check: which taxonomy skills appear in O*NET tool examples?
examples = {r["example"].lower() for r in tech_rows if r["example"]}
text = " | ".join(sorted(examples))

def found(term):
    term = term.lower().strip()
    if not term:
        return False
    if len(term) <= 3:
        return term in examples
    return re.search(r"\b" + re.escape(term) + r"\b", text) is not None

with open("data/taxonomy_draft.csv", newline="", encoding="utf-8") as f:
    taxonomy = list(csv.DictReader(f))

matched = []
for row in taxonomy:
    terms = [row["canonical_name"]] + row["synonyms"].split(";")
    hit = next((t for t in terms if found(t)), None)
    if hit:
        matched.append(f'{row["canonical_name"]} (matched "{hit}")')

print()
print(f"Taxonomy skills found in O*NET tool names: {len(matched)} of {len(taxonomy)}")
for m in matched:
    print("  ", m)