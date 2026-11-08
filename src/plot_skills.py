import csv
import os
from collections import Counter, defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

with open("data/processed/adzuna_dedup.csv", newline="", encoding="utf-8") as f:
    postings = list(csv.DictReader(f))
with open("data/processed/skill_matches.csv", newline="", encoding="utf-8") as f:
    matches = list(csv.DictReader(f))

n_by_family = Counter(p["family"] for p in postings)
counts = defaultdict(Counter)
with_any = defaultdict(set)
for m in matches:
    counts[m["family"]][m["skill"]] += 1
    with_any[m["family"]].add(m["posting_id"])

families = sorted(n_by_family)
fig, axes = plt.subplots(2, 2, figsize=(13, 8))

for ax, fam in zip(axes.ravel(), families):
    top = counts[fam].most_common(6)[::-1]
    names = [t[0] for t in top]
    values = [100 * t[1] / n_by_family[fam] for t in top]
    bars = ax.barh(names, values)
    for bar, t in zip(bars, top):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2,
                f"  {t[1]}", va="center", fontsize=8)
    ax.set_xlim(0, max(values) * 1.2)
    ax.set_title(f"{fam} (n={n_by_family[fam]}; {len(with_any[fam])} postings had a match)", fontsize=10)
    ax.set_xlabel("% of postings mentioning the skill")

total_with = sum(len(v) for v in with_any.values())
total = sum(n_by_family.values())
fig.suptitle("Taxonomy skills visible in Adzuna job postings (first 500 characters only)", fontsize=13)
fig.text(0.5, 0.01,
         f"Only {total_with} of {total} distinct postings ({100 * total_with / total:.0f}%) contain any taxonomy skill; "
         "descriptions are truncated, so tools listed in requirements are mostly invisible.",
         ha="center", fontsize=9)
plt.tight_layout(rect=[0, 0.04, 1, 0.95])

os.makedirs("figures", exist_ok=True)
plt.savefig("figures/top_skills_by_family.png", dpi=150)
print("Saved figures/top_skills_by_family.png")