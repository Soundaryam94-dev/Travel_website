import os
import requests
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

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
    # Stateless in this implementation, could call logout endpoint if we saved user tokens, 
    # but not strictly necessary for this simple demo using Service Role proxy.
    pass

def get_destinations():
    res = requests.get(f"{url}/rest/v1/destinations?select=*", headers=headers)
    return SupabaseResponse(data=res.json())

def get_destination_by_id(dest_id):
    res = requests.get(f"{url}/rest/v1/destinations?id=eq.{dest_id}&select=*", headers=headers)
    data = res.json()
    return SupabaseResponse(data=data[0] if data else None)

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
    requests.post(f"{url}/rest/v1/bookings", headers=headers, json=data)

def get_user_bookings(user_id):
    res = requests.get(f"{url}/rest/v1/bookings?user_id=eq.{user_id}&select=*,destinations(title,location)", headers=headers)
    return SupabaseResponse(data=res.json())

def get_all_bookings():
    res = requests.get(f"{url}/rest/v1/bookings?select=*,profiles(full_name),destinations(title)", headers=headers)
    return SupabaseResponse(data=res.json())

def add_destination(title, description, location, price, image_url):
    data = {
        "title": title,
        "description": description,
        "location": location,
        "price": price,
        "image_url": image_url
    }
    requests.post(f"{url}/rest/v1/destinations", headers=headers, json=data)

def update_destination(dest_id, title, description, location, price, image_url):
    data = {
        "title": title,
        "description": description,
        "location": location,
        "price": price,
        "image_url": image_url
    }
    requests.patch(f"{url}/rest/v1/destinations?id=eq.{dest_id}", headers=headers, json=data)

def delete_destination(dest_id):
    requests.delete(f"{url}/rest/v1/destinations?id=eq.{dest_id}", headers=headers)

def get_user_profile(user_id):
    res = requests.get(f"{url}/rest/v1/profiles?id=eq.{user_id}&select=*", headers=headers)
    data = res.json()
    return SupabaseResponse(data=data[0] if data else {})
