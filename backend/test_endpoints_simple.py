"""
Simple endpoint testing with inline token generation.
"""
import subprocess
import time
import requests
import sys
from datetime import datetime, timedelta
from jose import jwt

# Configuration
BASE_URL = "http://localhost:8000"
SECRET_KEY = "your-secret-key-here-change-in-production-min-32-chars-long"
ALGORITHM = "HS256"
TEST_USER_EMAIL = "test@example.com"

def generate_token():
    """Generate a fresh access token."""
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = {
        "sub": TEST_USER_EMAIL,
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def test_with_auth():
    """Run tests with authentication."""
    token = generate_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n" + "="*80)
    print("NEO ALEXANDRIA 2.0 - ENDPOINT TESTS")
    print("="*80 + "\n")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test endpoints
    tests = [
        ("GET", "/docs", {}, 200, False),
        ("GET", "/api/auth/me", headers, 200, True),
        ("GET", "/api/resources/", headers, 200, True),
        ("GET", "/api/collections/", headers, 200, True),
        ("GET", "/api/search/?q=test&search_type=keyword", headers, 200, True),
        ("GET", "/api/taxonomy/categories", headers, 200, True),
        ("GET", "/api/authority/", headers, 200, True),
        ("GET", "/api/recommendations/personalized", headers, 200, True),
    ]
    
    for method, endpoint, hdrs, expected, needs_auth in tests:
        try:
            url = f"{BASE_URL}{endpoint}"
            if method == "GET":
                response = requests.get(url, headers=hdrs if needs_auth else {}, timeout=5)
            
            if response.status_code == expected:
                print(f"✓ {method} {endpoint[:50]}")
                tests_passed += 1
            else:
                print(f"✗ {method} {endpoint[:50]} - Expected {expected}, got {response.status_code}")
                tests_failed += 1
        except Exception as e:
            print(f"✗ {method} {endpoint[:50]} - Error: {str(e)[:50]}")
            tests_failed += 1
    
    print(f"\n{'='*80}")
    print(f"Results: {tests_passed} passed, {tests_failed} failed")
    print(f"{'='*80}\n")
    
    return tests_failed == 0

if __name__ == "__main__":
    # Wait for server
    print("Waiting for server...")
    for i in range(30):
        try:
            response = requests.get(f"{BASE_URL}/docs", timeout=1)
            if response.status_code == 200:
                print("Server ready!\n")
                break
        except:
            pass
        time.sleep(1)
    else:
        print("Server not ready")
        sys.exit(1)
    
    success = test_with_auth()
    sys.exit(0 if success else 1)
