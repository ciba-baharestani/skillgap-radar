import csv
import re

with open("data/processed/adzuna_dedup.csv", newline="", encoding="utf-8") as f:
    postings = list(csv.DictReader(f))

texts = [p["title"] + " . " + p["description"] for p in postings]
print("Postings:", len(texts), "\n")

probes = ["python", "sql", "canvas", "moodle", "storyline", "articulate", "tableau",
          "power bi", "lms", "learning management", "scorm", "xapi", "addie",
          "stakeholder", "subject matter", "assessment", "needs analysis",
          "e-learning", "online course"]
for w in probes:
    n = sum(w in t.lower() for t in texts)
    print(f"{w:22} appears in {n} postings")


def show(pattern, label, limit=5, flags=0):
    print(f"\n--- contexts for {label} ---")
    shown = 0
    for t in texts:
        m = re.search(pattern, t, flags)
        if m:
            s = max(0, m.start() - 50)
            print("  ...", t[s:m.end() + 50].replace("\n", " "), "...")
            shown += 1
            if shown == limit:
                break


show(r"(?<![\w&/])R(?![\w&])", "R (capital)")
show(r"budget", "budget", flags=re.IGNORECASE)
show(r"reporting", "reporting", flags=re.IGNORECASE)