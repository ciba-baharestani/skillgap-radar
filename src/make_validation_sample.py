import csv
import random
from collections import defaultdict

random.seed(7)
QUOTA = {"Instructional Design": 8, "Corporate L&D": 8, "Learning Analytics": 7, "Ed-Tech Product": 7}
SPARES = 2

with open("data/processed/adzuna_dedup.csv", newline="", encoding="utf-8") as f:
    postings = list(csv.DictReader(f))
with open("data/taxonomy_draft.csv", newline="", encoding="utf-8") as f:
    taxonomy = list(csv.DictReader(f))

by_family = defaultdict(list)
for p in postings:
    by_family[p["family"]].append(p)

main, spare = [], []
for fam, n in QUOTA.items():
    pool = by_family[fam][:]
    random.shuffle(pool)
    main += pool[:n]
    spare += pool[n:n + SPARES]
random.shuffle(main)
random.shuffle(spare)

sheet, key = [], []
for i, p in enumerate(main + spare, 1):
    sid = f"V{i:02d}"
    batch = "main" if i <= len(main) else "spare"
    sheet.append({
        "sample_id": sid, "batch": batch, "family": p["family"],
        "title": p["title"], "company": p["company"], "url": p["url"],
        "relevant_yn": "", "dead_link": "", "full_text_skill_ids": "", "notes": "",
    })
    key.append({"sample_id": sid, "posting_id": p["id"]})

def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

write("data/processed/validation_sheet.csv", sheet)
write("data/processed/validation_key.csv", key)

with open("data/processed/validation_skill_reference.txt", "w", encoding="utf-8") as f:
    for row in taxonomy:
        f.write(f'{row["skill_id"]:6} {row["canonical_name"]}  ({row["synonyms"]})\n')

print("Main sample:", len(main), "| spares:", len(spare))
print("Files: validation_sheet.csv (you fill this in), validation_key.csv (leave alone), validation_skill_reference.txt")