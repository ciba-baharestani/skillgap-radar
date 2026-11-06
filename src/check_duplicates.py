import csv
from collections import defaultdict

with open("data/processed/adzuna_clean.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

groups = defaultdict(list)
for r in rows:
    groups[(r["title"].lower().strip(), r["company"].lower().strip())].append(r)

dup_groups = {k: v for k, v in groups.items() if len(v) > 1}
extra = sum(len(v) - 1 for v in dup_groups.values())

print("Kept postings:", len(rows))
print("Unique (title, company) pairs:", len(groups))
print("Groups with more than one posting:", len(dup_groups))
print("Extra rows that would be removed:", extra)
print()

for (title, company), v in sorted(dup_groups.items(), key=lambda x: -len(x[1]))[:12]:
    same_text = len({r["description"][:150] for r in v}) == 1
    locations = sorted({r["location"] for r in v})[:3]
    print(f"{len(v)}x {title} | {company} | identical text: {same_text} | e.g. {locations}")