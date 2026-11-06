import csv
from collections import Counter

with open("data/processed/adzuna_clean.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

groups = {}
for r in rows:
    key = (r["title"].lower().strip(), r["company"].lower().strip(), r["description"].strip())
    groups.setdefault(key, []).append(r)

dedup = []
for members in groups.values():
    first = dict(members[0])
    first["n_listings"] = len(members)
    first["n_locations"] = len({m["location"] for m in members})
    dedup.append(first)

with open("data/processed/adzuna_dedup.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(dedup[0].keys()))
    writer.writeheader()
    writer.writerows(dedup)

print("Listings before:", len(rows), "| Distinct postings after:", len(dedup))
print()
fam_n = Counter(r["family"] for r in dedup)
fam_listings = Counter()
fam_salary = Counter()
for r in dedup:
    fam_listings[r["family"]] += r["n_listings"]
    if r["salary_stated"] == "True":
        fam_salary[r["family"]] += 1
for fam in fam_n:
    print(f"{fam}: {fam_n[fam]} distinct ({fam_listings[fam]} listings), {fam_salary[fam]} with a stated salary")
print("Total stated salaries:", sum(fam_salary.values()))
print("Low-confidence postings:", sum(r["low_confidence"] == "True" for r in dedup))