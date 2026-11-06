import csv

with open("data/processed/adzuna_clean.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

for company in ["norstella", "humana", "servpro", "cbre", "colonial life"]:
    group = [r for r in rows if company in r["company"].lower()]
    if not group:
        continue
    text = " ".join(r["description"].lower() for r in group)
    print(f"{company}: {len(group)} listings | "
          f"'remote' in {sum('remote' in r['description'].lower() for r in group)} | "
          f"'on-site/onsite' in {sum(('on-site' in r['description'].lower() or 'onsite' in r['description'].lower()) for r in group)} | "
          f"distinct URLs: {len({r['url'] for r in group})}")