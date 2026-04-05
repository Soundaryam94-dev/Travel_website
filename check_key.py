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

print(f"Checking Supabase Project: {url}")
# Try to get the destinations table or just ping the REST root
try:
    response = requests.get(f"{url}/rest/v1/", headers=headers, timeout=5)
    if response.status_code == 200:
        print("✅ SUCCESS! The API key and URL are valid.")
    else:
        print(f"❌ FAILED! Response Code: {response.status_code}")
        print(f"Details: {response.text}")
except Exception as e:
    print(f"❌ ERROR connecting to Supabase: {e}")
