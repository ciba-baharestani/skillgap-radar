import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
app_id = os.getenv("ADZUNA_APP_ID")
app_key = os.getenv("ADZUNA_APP_KEY")

url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
params = {
    "app_id": app_id,
    "app_key": app_key,
    "what": "instructional designer",
    "results_per_page": 20,
}

response = requests.get(url, params=params)
print("Status:", response.status_code)

data = response.json()

os.makedirs("data/raw/samples", exist_ok=True)
with open("data/raw/samples/adzuna_sample.json", "w") as f:
    json.dump(data, f, indent=2)

print("Total postings found:", data.get("count"))
print("Saved", len(data.get("results", [])), "postings")