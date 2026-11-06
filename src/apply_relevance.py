import csv
import random
from collections import Counter

EXTRA_DROP = ["machine learning", "deep learning"]

# Postings rescued by manual review (Adzuna ids). Edit this set.
RESCUE_IDS = {
    "5780055185",  # Digital Promise, Director Edtech R&D
    "5943785471",  # Kforce, Business Data Analyst IV (learning analytics)
    "5682095059",  # Aline, Manager Customer Success (customer education)
    "5937815752",  # Stanford GSE, Research Data Analyst 2
    "5939304125",  # UIUC Gies, Data Analyst
    "5945464487",  # WGU, IAR Data Analyst (unclear from snippet)
    "5945545983",  # WGU, Lead IAR Data Analyst (unclear from snippet)
    
}

LOW_CONFIDENCE = {
    "5937815752",  # Stanford GSE
    "5939304125",  # UIUC Gies
    "5945464487",  # WGU IAR Data Analyst
    "5945545983",  # WGU Lead IAR Data Analyst
}

with open("data/processed/adzuna_postings.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

for r in rows:
    if r["title_match"] == "True" and not any(d in r["title"].lower() for d in EXTRA_DROP):
        r["relevance"] = "title keyword"
    elif r["id"] in RESCUE_IDS:
        r["relevance"] = "manual rescue"
    else:
        r["relevance"] = "dropped"
    r["low_confidence"] = r["id"] in LOW_CONFIDENCE
    r["salary_stated"] = bool(
        r["salary_is_predicted"] == "0" and (r["salary_min"] or r["salary_max"])
    )

kept = [r for r in rows if r["relevance"] != "dropped"]

with open("data/processed/adzuna_clean.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(kept[0].keys()))
    writer.writeheader()
    writer.writerows(kept)

print("Total:", len(rows), "| Kept:", len(kept), "| Dropped:", len(rows) - len(kept))
print("Manual rescues:", sum(r["relevance"] == "manual rescue" for r in kept))
print("Low-confidence rescues:", sum(r["low_confidence"] for r in kept))
print()
kept_fam = Counter(r["family"] for r in kept)
sal_fam = Counter(r["family"] for r in kept if r["salary_stated"])
for fam, n in kept_fam.items():
    print(f"{fam}: {n} postings, {sal_fam[fam]} with a stated salary")

print()
print("Random spot-check of 15 postings kept by title keyword:")
random.seed(2)
pool = [r for r in kept if r["relevance"] == "title keyword"]
for r in random.sample(pool, 15):
    print(f'  [{r["family"]}] {r["title"]} | {r["company"]}')

    print()
print("Kept titles containing engineer/software/scientist:")
for r in kept:
    if any(w in r["title"].lower() for w in ["engineer", "software", "scientist"]):
        print(f'  [{r["family"]}] {r["title"]} | {r["company"]}')
        