import json
import glob
from collections import Counter

flags = Counter()
titles = []

for path in sorted(glob.glob("data/raw/adzuna/*.json")):
    with open(path) as f:
        data = json.load(f)
    for job in data.get("results", []):
        flags[str(job.get("salary_is_predicted"))] += 1
        titles.append((data.get("_query"), job.get("title")))

print("salary_is_predicted values:", dict(flags))
print()
for query, title in titles[::40]:
    print(f"[{query}] {title}")