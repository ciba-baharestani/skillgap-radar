import csv
from collections import Counter

with open("data/processed/validation_labeled.csv", newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

counts = Counter()
for r in rows:
    seen = set()
    for item in (r["notes"] or "").split(";"):
        item = item.strip().lower()
        if item:
            seen.add(item)
    counts.update(seen)

print("Distinct notes:", len(counts), "| postings with notes:", sum(bool(r["notes"].strip()) for r in rows))
print("\nNotes appearing in 2+ postings:")
for item, c in counts.most_common():
    if c >= 2:
        print(f"   {c}x {item}")
print("\nAll other notes (singles):")
print("   " + "; ".join(sorted(i for i, c in counts.items() if c == 1)))
