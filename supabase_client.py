import os
import requests
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
# Use Service Key for backend operations if available, otherwise fallback to Publishable Key
key: str = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY/SUPABASE_SERVICE_KEY must be set in environment variables")

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    
class SupabaseResponse:
    def __init__(self, data=None, error=None, user=None):
        self.data = data
        self.error = error
        self.user = user

def sign_up(email, password, full_name):
    # Gotrue signup
    res = requests.post(f"{url}/auth/v1/signup", headers=headers, json={
        "email": email,
        "password": password,
        "data": {"full_name": full_name}
    })
    data = res.json()
    if res.ok:
        u = DotDict(data.get("user", {}))
        u.user_metadata = u.get("user_metadata", {})
        return SupabaseResponse(user=u)
    else:
        raise Exception(data.get("msg", "Signup failed"))

def sign_in(email, password):
    res = requests.post(f"{url}/auth/v1/token?grant_type=password", headers=headers, json={
        "email": email,
        "password": password
    })
    data = res.json()
    if res.ok:
        u = DotDict(data.get("user", {}))
        u.user_metadata = u.get("user_metadata", {})
        return SupabaseResponse(user=u)
    else:
        raise Exception(data.get("error_description", "Invalid credentials"))

def sign_out():
    # Stateless in this implementation
    pass

def get_destinations():
    res = requests.get(f"{url}/rest/v1/destinations?select=*", headers=headers)
    return SupabaseResponse(data=res.json())

def get_destination_by_id(dest_id):
    res = requests.get(f"{url}/rest/v1/destinations?id=eq.{dest_id}&select=*", headers=headers)
    data = res.json()
    target_data = data[0] if isinstance(data, list) and len(data) > 0 else None
    return SupabaseResponse(data=target_data)

def create_booking(user_id, destination_id, check_in, check_out, travelers, total_price):
    data = {
        "user_id": user_id,
        "destination_id": destination_id,
        "check_in": check_in,
        "check_out": check_out,
        "num_travelers": travelers,
        "total_price": total_price,
        "status": "pending"
    }
    res = requests.post(f"{url}/rest/v1/bookings", headers=headers, json=data)
    if not res.ok:
        error_msg = res.json().get("message", "Failed to create booking")
        raise Exception(f"Supabase Error: {error_msg}")

def get_user_bookings(user_id):
    res = requests.get(f"{url}/rest/v1/bookings?user_id=eq.{user_id}&select=*,destinations(title,location)", headers=headers)
    data = res.json()
    return SupabaseResponse(data=data if isinstance(data, list) else [])

def get_all_bookings():
    res = requests.get(f"{url}/rest/v1/bookings?select=*,profiles(full_name),destinations(title)", headers=headers)
    data = res.json()
    return SupabaseResponse(data=data if isinstance(data, list) else [])

def add_destination(title, description, location, price, image_url):
    data = {
        "title": title,
        "description": description,
        "location": location,
        "price": price,
        "image_url": image_url
    }
    res = requests.post(f"{url}/rest/v1/destinations", headers=headers, json=data)
    if not res.ok:
        error_msg = res.json().get("message", "Failed to add destination")
        raise Exception(f"Supabase Error: {error_msg}")

def update_destination(dest_id, title, description, location, price, image_url):
    data = {
        "title": title,
        "description": description,
        "location": location,
        "price": price,
        "image_url": image_url
    }
    res = requests.patch(f"{url}/rest/v1/destinations?id=eq.{dest_id}", headers=headers, json=data)
    if not res.ok:
        error_msg = res.json().get("message", "Failed to update destination")
        raise Exception(f"Supabase Error: {error_msg}")

def delete_destination(dest_id):
    res = requests.delete(f"{url}/rest/v1/destinations?id=eq.{dest_id}", headers=headers)
    if not res.ok:
        error_msg = res.json().get("message", "Failed to delete destination")
        raise Exception(f"Supabase Error: {error_msg}")

def get_user_profile(user_id):
    res = requests.get(f"{url}/rest/v1/profiles?id=eq.{user_id}&select=*", headers=headers)
    data = res.json()
    target_data = data[0] if isinstance(data, list) and len(data) > 0 else {}
    return SupabaseResponse(data=target_data)

def get_all_users():
    res = requests.get(f"{url}/rest/v1/profiles?select=*", headers=headers)
    return SupabaseResponse(data=res.json())

def update_user_role(user_id, role):
    data = {"role": role}
    res = requests.patch(f"{url}/rest/v1/profiles?id=eq.{user_id}", headers=headers, json=data)
    if not res.ok:
        error_msg = res.json().get("message", "Failed to update user role")
        raise Exception(f"Supabase Error: {error_msg}")