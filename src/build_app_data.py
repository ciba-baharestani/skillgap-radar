import csv
from collections import Counter
from pathlib import Path

# Skills we keep out of the app (MBA-flavored rows we decided not to show)
EXCLUDE = {"BP08", "BP09"}

with open("data/processed/adzuna_dedup.csv", newline="", encoding="utf-8-sig") as f:
    postings = list(csv.DictReader(f))

if not postings or "family" not in postings[0]:
    print("No 'family' column in adzuna_dedup.csv. Columns are:")
    print(list(postings[0].keys()) if postings else "file is empty")
    raise SystemExit

# How many distinct postings each family has
totals = Counter(p["family"] for p in postings)

# Count each skill once per posting
seen = set()
counts = Counter()
info = {}
with open("data/processed/skill_matches.csv", newline="", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        if r["skill_id"] in EXCLUDE:
            continue
        key = (r["posting_id"], r["skill_id"])
        if key in seen:
            continue
        seen.add(key)
        counts[(r["family"], r["skill_id"])] += 1
        info[r["skill_id"]] = (r["skill"], r["category"])

rows = []
for (family, skill_id), n in counts.items():
    skill, category = info[skill_id]
    rows.append({
        "family": family,
        "skill_id": skill_id,
        "skill": skill,
        "category": category,
        "postings": n,
        "family_postings": totals[family],
        "share": round(n / totals[family], 3),
    })
rows.sort(key=lambda r: (r["family"], -r["postings"]))

Path("data/app").mkdir(exist_ok=True)
with open("data/app/skill_counts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved data/app/skill_counts.csv with {len(rows)} rows")
for r in rows[:8]:
    print(r["family"], "|", r["skill"], "|", r["postings"], "of", r["family_postings"])