import csv
import re
from collections import Counter, defaultdict

SKIP_TERMS = {"rise", "strategy", "metrics"}   # noisy synonyms, edit freely
CASE_SENSITIVE = {"excel"}                      # avoid the verb "excel"

with open("data/taxonomy_draft.csv", newline="", encoding="utf-8") as f:
    taxonomy = list(csv.DictReader(f))
with open("data/processed/adzuna_dedup.csv", newline="", encoding="utf-8") as f:
    postings = list(csv.DictReader(f))

info = {row["skill_id"]: row for row in taxonomy}


def build_patterns(row):
    terms = [row["canonical_name"]] + [s.strip() for s in row["synonyms"].split(";") if s.strip()]
    patterns = []
    for term in terms:
        low = term.lower()
        if low in SKIP_TERMS:
            continue
        if len(term) <= 3:
            # short acronyms: capitals only, and not inside things like "R&D"
            rx = re.compile(r"(?<![\w&/\-])" + re.escape(term.upper()) + r"(?![\w&\-])")
        elif low in CASE_SENSITIVE:
            rx = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)")
        else:
            rx = re.compile(r"(?<!\w)" + re.escape(term) + r"s?(?!\w)", re.IGNORECASE)
        patterns.append((term, rx))
    return patterns


patterns = {sid: build_patterns(row) for sid, row in info.items()}

found_by_posting = {}
match_rows = []
for p in postings:
    text = p["title"] + " . " + p["description"]
    found = {}
    for sid, pats in patterns.items():
        for term, rx in pats:
            if rx.search(text):
                found[sid] = term
                break
    found_by_posting[p["id"]] = found
    for sid, term in found.items():
        match_rows.append({
            "posting_id": p["id"],
            "family": p["family"],
            "skill_id": sid,
            "skill": info[sid]["canonical_name"],
            "category": info[sid]["category"],
            "matched_term": term,
        })

with open("data/processed/skill_matches.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(match_rows[0].keys()))
    writer.writeheader()
    writer.writerows(match_rows)

by_family = defaultdict(list)
for p in postings:
    by_family[p["family"]].append(p)

all_matched = set()
for fam, plist in by_family.items():
    n = len(plist)
    counts = Counter()
    with_any = 0
    total = 0
    for p in plist:
        found = found_by_posting[p["id"]]
        with_any += bool(found)
        total += len(found)
        counts.update(found.keys())
    all_matched.update(counts.keys())
    print(f"\n{fam}: {n} postings | {with_any} with at least one skill | avg {total / n:.1f} skills per posting")
    for sid, c in counts.most_common(8):
        print(f"   {info[sid]['canonical_name']:30} {c:>3} ({100 * c / n:.0f}%)")

never = [info[s]["canonical_name"] for s in info if s not in all_matched]
print(f"\nSkills never matched ({len(never)} of {len(info)}):", ", ".join(never))
print("Saved data/processed/skill_matches.csv with", len(match_rows), "matches")