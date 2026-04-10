import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

data = {
    "title": "Test Destination",
    "description": "Verification of CMS functionality",
    "location": "Test Location",
    "price": 99.99,
    "image_url": "https://example.com/image.jpg"
}

print("Attempting to add a destination...")
res = requests.post(f"{url}/rest/v1/destinations", headers=headers, json=data)
print(f"Status: {res.status_code}")
print(f"Response: {res.text}")

if res.status_code == 201:
    print("SUCCESS: Destination added.")
    # Now clean up
    new_id = res.json()[0]['id']
    print(f"Cleaning up test destination (ID: {new_id})...")
    requests.delete(f"{url}/rest/v1/destinations?id=eq.{new_id}", headers=headers)
else:
    print("FAILED: Could not add destination.")
