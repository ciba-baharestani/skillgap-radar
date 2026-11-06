import csv

NUMBERS = [25, 47, 50, 29, 33, 35, 49, 84, 92, 109]

with open("data/processed/adzuna_postings.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

dropped = [r for r in rows if r["title_match"] == "False"]
dropped.sort(key=lambda r: (r["family"] or "", r["title"].lower()))
print("Dropped postings:", len(dropped), "(should be 121)\n")

for n in NUMBERS:
    r = dropped[n - 1]
    print("=" * 70)
    print(f'#{n} (id {r["id"]}) [{r["family"]}] {r["title"]} | {r["company"]}')
    print("category:", r["category"], "| location:", r["location"])
    print(r["description"])