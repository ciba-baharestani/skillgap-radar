import os
import json
import time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

# ---- Settings you can change ----
DRY_RUN = False        # True = only print the plan, use NO API calls
MAX_CALLS = 11         # safety cap per run (start with 1, then raise it)
PAGES = [1]           # which result pages to fetch for each search
RESULTS_PER_PAGE = 50
SLEEP_SECONDS = 2
# ---------------------------------

SEARCHES = {
    "Instructional Design": [
        "instructional designer",
        "learning experience designer",
        "curriculum developer",
    ],
    "Learning Analytics": [
        "learning analytics",
        "education data analyst",
        "learning and development analyst",
    ],
    "Ed-Tech Product": [
        "edtech product manager",
        "learning product manager",
        "customer success education",
    ],
    "Corporate L&D": [
        "learning and development specialist",
        "training manager",
        "enablement specialist",
    ],
}

OUT_DIR = "data/raw/adzuna"
os.makedirs(OUT_DIR, exist_ok=True)

calls_made = 0
for family, phrases in SEARCHES.items():
    for phrase in phrases:
        for page in PAGES:
            slug = phrase.replace(" ", "_")
            path = f"{OUT_DIR}/{slug}_p{page}.json"

            if os.path.exists(path):
                print("SKIP (already saved):", path)
                continue

            if DRY_RUN:
                print("WOULD CALL:", phrase, "| page", page)
                continue

            if calls_made >= MAX_CALLS:
                print("Reached MAX_CALLS, stopping.")
                raise SystemExit

            url = f"https://api.adzuna.com/v1/api/jobs/us/search/{page}"
            params = {
                "app_id": APP_ID,
                "app_key": APP_KEY,
                "what": phrase,
                "results_per_page": RESULTS_PER_PAGE,
            }
            response = requests.get(url, params=params)
            calls_made += 1

            if response.status_code != 200:
                print("ERROR", response.status_code, "for", phrase)
                print(response.text[:300])
                raise SystemExit

            data = response.json()
            data["_family"] = family
            data["_query"] = phrase
            data["_page"] = page
            data["_fetched_at"] = datetime.now(timezone.utc).isoformat()

            with open(path, "w") as f:
                json.dump(data, f, indent=2)

            print("SAVED:", phrase, "| postings:", len(data.get("results", [])))
            time.sleep(SLEEP_SECONDS)

print("Done. Calls used this run:", calls_made)