import csv
from collections import defaultdict

with open("data/processed/onet_tech.csv", newline="", encoding="utf-8") as f:
    tech = list(csv.DictReader(f))

with open("data/taxonomy_draft.csv", newline="", encoding="utf-8") as f:
    taxonomy = list(csv.DictReader(f))

known = set()
for row in taxonomy:
    known.add(row["canonical_name"].lower())
    known.update(s.strip().lower() for s in row["synonyms"].split(";") if s.strip())

occs = defaultdict(set)
for r in tech:
    occs[r["example"]].add(r["onet_title"])

rows = [
    (len(v), name) for name, v in occs.items()
    if len(v) >= 2 and name.lower() not in known
]
rows.sort(key=lambda x: (-x[0], x[1].lower()))

print("Tools in 2+ occupations, not yet in taxonomy:", len(rows))
print()
for count, name in rows[:50]:
    print(count, "-", name)