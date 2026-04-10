import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY missing in .env")
    exit(1)

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
}

print(f"Testing connection to: {url}")

tables = ["destinations", "bookings", "profiles"]

for table in tables:
    try:
        response = requests.get(f"{url}/rest/v1/{table}?select=count", headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"Success: Table '{table}' is accessible.")
        else:
            print(f"Failed: Table '{table}' returned status {response.status_code}")
            print(f"Detail: {response.text}")
    except Exception as e:
        print(f"Error checking table '{table}': {e}")
