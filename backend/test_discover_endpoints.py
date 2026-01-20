"""Discover what endpoints are actually registered."""
import requests

BASE_URL = "http://localhost:8000"

# Try different auth endpoint variations
endpoints_to_try = [
    "/auth/register",
    "/api/auth/register",
    "/auth/token",
    "/api/auth/token",
    "/auth/me",
    "/api/auth/me",
]

print("Testing endpoint variations:\n")
for endpoint in endpoints_to_try:
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json={}, timeout=2)
        print(f"{endpoint}: {response.status_code}")
    except Exception as e:
        print(f"{endpoint}: ERROR - {str(e)[:50]}")

# Get OpenAPI spec to see registered routes
try:
    response = requests.get(f"{BASE_URL}/openapi.json")
    if response.status_code == 200:
        spec = response.json()
        print("\n\nRegistered auth-related paths:")
        for path in spec.get("paths", {}).keys():
            if "auth" in path.lower():
                print(f"  {path}")
except Exception as e:
    print(f"\nCouldn't fetch OpenAPI spec: {e}")
