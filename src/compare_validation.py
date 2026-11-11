import csv
import re
from collections import Counter, defaultdict

def read(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

sheet = read("data/processed/validation_labeled.csv")
key = {r["sample_id"]: r["posting_id"] for r in read("data/processed/validation_key.csv")}
taxonomy = {r["skill_id"]: r["canonical_name"] for r in read("data/taxonomy_draft.csv")}

matcher = defaultdict(dict)  # posting_id -> {skill_id: matched_term}
for m in read("data/processed/skill_matches.csv"):
    matcher[m["posting_id"]][m["skill_id"]] = m["matched_term"]


def parse_ids(text):
    ids = [t.strip().upper() for t in re.split(r"[;,]", text or "") if t.strip()]
    ids = [i for i in ids if i != "NONE"]
    return {i for i in ids if i in taxonomy}, [i for i in ids if i not in taxonomy]


relevance_rows = [r for r in sheet if r["relevant_yn"].strip() and r["dead_link"].strip().upper() != "Y"]
labeled = [r for r in relevance_rows if r["full_text_skill_ids"].strip()]
n = len(labeled)
print("Postings with a relevance judgment:", len(relevance_rows), dict(Counter(r["relevant_yn"].strip().upper() for r in relevance_rows)))
print("Postings with skill labels:", n)

tp = true_total = match_total = 0
true_counts, missed, hit = Counter(), Counter(), Counter()
false_pos, unknown = [], []

for r in labeled:
    true, bad = parse_ids(r["full_text_skill_ids"])
    if bad:
        unknown.append((r["sample_id"], bad))
    found = matcher.get(key[r["sample_id"]], {})
    mset = set(found)
    true_total += len(true)
    match_total += len(mset)
    tp += len(true & mset)
    true_counts.update(true)
    hit.update(true & mset)
    missed.update(true - mset)
    for s in mset - true:
        false_pos.append((r["sample_id"], taxonomy[s], found[s]))

print(f"\nSkills per posting: {true_total / n:.1f} in the full text vs {match_total / n:.1f} found by the matcher in the 500-character snippet")
if true_total:
    print(f"Recall: matcher found {tp} of {true_total} labeled skills ({100 * tp / true_total:.0f}%)")
if match_total:
    print(f"Precision: {tp} of {match_total} matcher matches confirmed by your labels ({100 * tp / match_total:.0f}%)")

print("\nMost common skills in the FULL postings (your labels):")
for s, c in true_counts.most_common(10):
    print(f"   {taxonomy[s]:30} in {c} of {n} postings (matcher caught {hit[s]})")

print("\nMatcher matches NOT in your labels (check: wrong match, or did you miss it?):")
for sid, skill, term in false_pos[:25]:
    print(f"   {sid}: {skill} (matched on '{term}')")

print("\nMBA-flavored rows in the full postings:")
for s in ["BP08", "BP09", "BP10"]:
    print(f"   {taxonomy[s]}: {true_counts[s]} of {n}")

if unknown:
    print("\nUnknown skill IDs (typos, fix them in the sheet):", unknown)