import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
# Using the service key for update permission
key = os.environ.get("SUPABASE_SERVICE_KEY")

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# New high-quality Goa image
new_image_url = "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=800&q=80"

print(f"Updating Goa Beach Escape image...")
# Match by title
res = requests.patch(
    f"{url}/rest/v1/destinations?title=eq.Goa%20Beach%20Escape",
    json={"image_url": new_image_url},
    headers=headers
)

if res.status_code in [200, 201, 204]:
    print("Successfully updated Goa Beach image!")
else:
    print(f"Error updating image: {res.status_code}")
    print(res.text)
