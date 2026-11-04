import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ONET_API_KEY")
HEADERS = {"X-API-Key": API_KEY, "Accept": "application/json"}
URL = "https://api-v2.onetcenter.org/online/search"

KEYWORDS = [
    "data scientist",
    "business intelligence analyst",
    "operations research analyst",
    "project management specialist",
    "computer and information systems managers",
    "market research analyst",
]

OUT_DIR = "data/raw/onet"
os.makedirs(OUT_DIR, exist_ok=True)

for kw in KEYWORDS:
    response = requests.get(URL, headers=HEADERS, params={"keyword": kw, "end": 8})
    if response.status_code != 200:
        print("ERROR", response.status_code, "for", kw)
        print(response.text[:300])
        break

    data = response.json()
    slug = kw.replace(" ", "_")
    with open(f"{OUT_DIR}/search_{slug}.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n== {kw} ==")
    for occ in data.get("occupation", []):
        print(" ", occ.get("code"), "-", occ.get("title"))

    time.sleep(0.5)