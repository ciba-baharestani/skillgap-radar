import csv
import os
import re
import time
import requests

# Optional: put your email here so site owners can contact you
HEADERS = {"User-Agent": "SkillGapRadar-student-project (bootcamp final project)"}
SLEEP_SECONDS = 3

OUT_DIR = "data/raw/programs"
os.makedirs(OUT_DIR, exist_ok=True)

with open("data/program_urls.csv", newline="", encoding="utf-8") as f:
    programs = list(csv.DictReader(f))

for p in programs:
    slug = re.sub(r"[^a-z0-9]+", "_", p["program"].lower()).strip("_")
    path = f"{OUT_DIR}/{slug}.html"

    if os.path.exists(path):
        print("SKIP (already saved):", slug)
        continue

    try:
        response = requests.get(p["url"], headers=HEADERS, timeout=30)
    except Exception as e:
        print("ERROR:", slug, "|", str(e)[:150])
        time.sleep(SLEEP_SECONDS)
        continue

    if response.status_code != 200:
        print("HTTP", response.status_code, ":", slug)
        time.sleep(SLEEP_SECONDS)
        continue

    with open(path, "w", encoding="utf-8") as out:
        out.write(response.text)

    print("SAVED:", slug, "|", len(response.text), "characters")
    time.sleep(SLEEP_SECONDS)

print("Done.")