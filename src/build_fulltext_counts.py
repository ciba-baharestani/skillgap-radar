import csv
import re
from collections import Counter
from pathlib import Path

# Skills we keep out of the app (MBA-flavored rows we decided not to show)
EXCLUDE = {"BP08", "BP09"}

# All skills from the taxonomy: id -> (name, category)
with open("data/taxonomy_draft.csv", newline="", encoding="utf-8-sig") as f:
    skills = {
        r["skill_id"]: (r["canonical_name"], r["category"])
        for r in csv.DictReader(f)
        if r["skill_id"] not in EXCLUDE
    }

n_labeled = Counter()   # postings read in full, per family
counts = Counter()      # (family, skill_id) -> postings mentioning it
unknown = Counter()     # IDs in the labels that are not in the taxonomy

with open("data/processed/validation_labeled.csv", newline="", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        ids_raw = (r.get("full_text_skill_ids") or "").strip()
        if not ids_raw:
            continue  # not read in full (relevance check only)
        if (r.get("relevant_yn") or "").strip().upper() == "N":
            continue  # not a learning or ed-tech role
        family = r["family"].strip()
        n_labeled[family] += 1
        ids = {i for i in re.split(r"[;,\s]+", ids_raw.upper()) if i and i != "NONE"}
        for sid in ids:
            if sid in EXCLUDE:
                continue
            if sid not in skills:
                unknown[sid] += 1
                continue
            counts[(family, sid)] += 1

rows = []
for family in sorted(n_labeled):
    family_rows = []
    for sid, (name, category) in skills.items():
        n = counts[(family, sid)]
        family_rows.append({
            "family": family,
            "skill_id": sid,
            "skill": name,
            "category": category,
            "postings": n,
            "family_labeled": n_labeled[family],
            "share": round(n / n_labeled[family], 3),
        })
    family_rows.sort(key=lambda r: (-r["postings"], r["skill"]))
    rows.extend(family_rows)

Path("data/app").mkdir(exist_ok=True)
with open("data/app/fulltext_counts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved data/app/fulltext_counts.csv with {len(rows)} rows")
for family in sorted(n_labeled):
    print(f"\n{family}: {n_labeled[family]} postings read in full")
    top = [r for r in rows if r["family"] == family and r["postings"] > 0][:5]
    for r in top:
        print(f"   {r['skill']}: {r['postings']}")
if unknown:
    print("\nIDs in your labels that are not in the taxonomy:", dict(unknown))