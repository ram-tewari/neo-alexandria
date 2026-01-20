"""
Quick endpoint test - tests a few key endpoints from each module
"""

import requests
import time

BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcl9pZCI6ImIzYjA3ZTMwLTk2ZWYtNGRmNi04MjAwLTY5YzBmM2VhOTM2MSIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJ0aWVyIjoicHJlbWl1bSIsInNjb3BlcyI6W10sImV4cCI6MTc2ODkyNTE2MSwidHlwZSI6ImFjY2VzcyJ9.jyV84j-iJSiSqAA-2IF31rlBepYkAmZtrd9PhhBGWlc"

def test_endpoint(name, method, path, data=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{path}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            resp = requests.post(url, json=data, headers=headers, timeout=10)
        
        status = "✓" if resp.status_code < 400 else "✗"
        print(f"{status} {name:40s} {resp.status_code:3d} {method:4s} {path}")
        return resp.status_code < 400
    except Exception as e:
        print(f"✗ {name:40s} ERR {method:4s} {path} - {str(e)[:50]}")
        return False

print("\n" + "="*80)
print("NEO ALEXANDRIA 2.0 - QUICK ENDPOINT TEST")
print("="*80 + "\n")

passed = 0
total = 0

# Test key endpoints from each module
tests = [
    ("Health Check", "GET", "/api/monitoring/health"),
    ("Performance Stats", "GET", "/api/monitoring/performance"),
    ("Get Current User", "GET", "/auth/me"),
    ("List Resources", "GET", "/resources/"),
    ("Keyword Search", "GET", "/search/?q=test"),
    ("List Collections", "GET", "/collections/"),
    ("List Categories", "GET", "/taxonomy/categories"),
    ("List Entities", "GET", "/api/graph/entities"),
]

for name, method, path in tests:
    total += 1
    if test_endpoint(name, method, path):
        passed += 1
    time.sleep(0.3)  # Small delay between requests

print(f"\n{'='*80}")
print(f"Results: {passed}/{total} passed ({passed/total*100:.1f}%)")
print(f"{'='*80}\n")
