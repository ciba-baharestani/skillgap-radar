import os
import csv
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ONET_API_KEY")
HEADERS = {"X-API-Key": API_KEY, "Accept": "application/json"}
BASE = "https://api-v2.onetcenter.org/online/occupations"

REPORTS = ["skills", "technology_skills"]

OUT_DIR = "data/raw/onet/details"
os.makedirs(OUT_DIR, exist_ok=True)

with open("data/onet_occupations.csv", newline="", encoding="utf-8") as f:
    occupations = list(csv.DictReader(f))

for occ in occupations:
    code = occ["onet_code"]
    for report in REPORTS:
        path = f"{OUT_DIR}/{code}_{report}.json"
        if os.path.exists(path):
            print("SKIP (already saved):", path)
            continue

        url = f"{BASE}/{code}/details/{report}"
        response = requests.get(url, headers=HEADERS, params={"end": 200})

        if response.status_code == 422:
            print("NO DATA (422):", code, report, response.text[:150])
            continue
        if response.status_code != 200:
            print("ERROR", response.status_code, "for", code, report)
            print(response.text[:300])
            raise SystemExit

        data = response.json()
        with open(path, "w") as out:
            json.dump(data, out, indent=2)

        parts = {k: len(v) for k, v in data.items() if isinstance(v, list)}
        items = [v for v in data.values() if isinstance(v, list) and v]
        first = str(items[0][0])[:250] if items else ""
        print("SAVED:", code, report, "| total:", data.get("total"), "| has next page:", "next" in data)
        print("   first item:", first)
        time.sleep(0.5)

print("Done.")