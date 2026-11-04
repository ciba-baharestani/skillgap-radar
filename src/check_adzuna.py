import json
import glob

files = sorted(glob.glob("data/raw/adzuna/*.json"))
seen = {}
total = 0
with_salary = 0
desc_lengths = []

for path in files:
    with open(path) as f:
        data = json.load(f)
    results = data.get("results", [])
    print(f"{data.get('_query')}: {len(results)} postings (Adzuna total matches: {data.get('count')})")
    for job in results:
        total += 1
        seen.setdefault(job.get("id"), []).append(data.get("_query"))
        if job.get("salary_min") or job.get("salary_max"):
            with_salary += 1
        desc_lengths.append(len(job.get("description", "")))

print()
print("Total postings:", total)
print("Unique postings:", len(seen))
print("Duplicates:", total - len(seen))
print("Postings with salary:", with_salary)
print("Average description length:", round(sum(desc_lengths) / len(desc_lengths)))
