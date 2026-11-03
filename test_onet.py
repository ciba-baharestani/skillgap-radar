import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ONET_API_KEY")

url = "https://api-v2.onetcenter.org/online/search"
headers = {"X-API-Key": api_key, "Accept": "application/json"}
params = {"keyword": "instructional designer", "end": 5}

response = requests.get(url, headers=headers, params=params)
print("Status:", response.status_code)

data = response.json()

os.makedirs("data/raw/samples", exist_ok=True)
with open("data/raw/samples/onet_sample.json", "w") as f:
    json.dump(data, f, indent=2)

for occ in data.get("occupation", []):
    print(occ.get("code"), "-", occ.get("title"))