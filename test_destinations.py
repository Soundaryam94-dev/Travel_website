import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
}

print(f"Testing destinations endpoint...")
res = requests.get(f"{url}/rest/v1/destinations?select=*", headers=headers)
print(f"Status: {res.status_code}")
if res.status_code == 200:
    print(f"Data count: {len(res.json())}")
else:
    print(f"Error: {res.text}")
