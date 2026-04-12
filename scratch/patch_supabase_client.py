import os

file_path = os.path.join("c:\\Users\\Soundarya N\\Documents\\Travel", "supabase_client.py")

with open(file_path, "r") as f:
    content = f.read()

# Replace direct module calls with session calls
content = content.replace("requests.post", "session.post")
content = content.replace("requests.get", "session.get")
content = content.replace("requests.patch", "session.patch")
content = content.replace("requests.delete", "session.delete")

# Add session setup logic right after headers dictionary definition
setup_code = """
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(
    total=5,
    backoff_factor=0.3,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PATCH", "DELETE"]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)
"""

# Find injection point
injection_str = '    "Prefer": "return=representation"\n}'
if injection_str in content:
    content = content.replace(injection_str, injection_str + "\n\n" + setup_code)

with open(file_path, "w") as f:
    f.write(content)

print(f"Patched {file_path}")
