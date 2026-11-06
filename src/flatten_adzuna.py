import csv
import glob
import json
import re
from collections import Counter

KEEP_TERMS = [
    "instruction", "learning", "training", "trainer", "curricul", "educat",
    "enablement", "l&d", "talent development", "course", "academic",
    "teach", "e-learning", "elearning", "lms",
]
DROP_TERMS = ["leader in training", "trainee"]


def clean(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


rows = {}
for path in sorted(glob.glob("data/raw/adzuna/*.json")):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for job in data.get("results", []):
        jid = str(job.get("id"))
        if jid in rows:
            rows[jid]["also_found_by"] += " | " + (data.get("_query") or "")
            continue
        rows[jid] = {
            "id": jid,
            "family": data.get("_family"),
            "query": data.get("_query"),
            "also_found_by": "",
            "title": clean(job.get("title")),
            "company": clean((job.get("company") or {}).get("display_name")),
            "location": clean((job.get("location") or {}).get("display_name")),
            "category": clean((job.get("category") or {}).get("label")),
            "created": job.get("created", ""),
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
            "salary_is_predicted": job.get("salary_is_predicted"),
            "description": clean(job.get("description")),
            "url": job.get("redirect_url", ""),
        }

for r in rows.values():
    t = r["title"].lower()
    r["title_match"] = any(k in t for k in KEEP_TERMS) and not any(d in t for d in DROP_TERMS)

with open("data/processed/adzuna_postings.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(next(iter(rows.values())).keys()))
    writer.writeheader()
    writer.writerows(rows.values())

dropped = [r for r in rows.values() if not r["title_match"]]
dropped.sort(key=lambda r: (r["family"] or "", r["title"].lower()))
with open("data/processed/adzuna_dropped_review.txt", "w", encoding="utf-8") as f:
    for i, r in enumerate(dropped, 1):
        f.write(f'{i:3}. [{r["family"]}] {r["title"]} | {r["company"]}\n')

print("Unique postings:", len(rows))
kept_by_family = Counter(r["family"] for r in rows.values() if r["title_match"])
all_by_family = Counter(r["family"] for r in rows.values())
for fam in all_by_family:
    print(f"  {fam}: kept {kept_by_family[fam]} of {all_by_family[fam]}")
print("Kept:", sum(kept_by_family.values()), "| Dropped (to review):", len(dropped))
print("Review list: data/processed/adzuna_dropped_review.txt")