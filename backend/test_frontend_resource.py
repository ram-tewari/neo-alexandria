"""
Test script to simulate frontend resource creation
"""
import requests
import json

# Test creating a resource like the frontend does
url = "http://localhost:8000/resources/"

payload = {
    "url": "https://www.postman.com/api-platform/api-documentation/",
    "title": "Postman API Documentation",
    "description": "API documentation platform",
    "type": "webpage"
}

print("Testing resource creation endpoint...")
print(f"POST {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Could not connect to backend at http://localhost:8000")
    print("Please make sure the backend is running:")
    print("  cd backend")
    print("  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
