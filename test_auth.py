#!/usr/bin/env python3
"""
Quick authentication test script for Neo Alexandria API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def create_test_user():
    """Create a test user directly in the database"""
    print("Creating test user...")
    # This would need database access
    print("Note: User creation requires database access")
    print("Using default test credentials: admin@test.com / admin123")

def login(username, password):
    """Login and get access token"""
    print(f"\n1. Logging in as {username}...")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": username,
            "password": password
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        tokens = response.json()
        print("✓ Login successful!")
        print(f"  Access token: {tokens['access_token'][:50]}...")
        print(f"  Expires in: {tokens['expires_in']} seconds")
        return tokens['access_token']
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

def test_authenticated_request(token):
    """Test an authenticated API request"""
    print("\n2. Testing authenticated request...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to list resources
    response = requests.get(f"{BASE_URL}/resources", headers=headers)
    
    if response.status_code == 200:
        print("✓ Authenticated request successful!")
        data = response.json()
        print(f"  Found {data.get('total', 0)} resources")
        return True
    else:
        print(f"✗ Request failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def test_unauthenticated_request():
    """Test that unauthenticated requests are blocked"""
    print("\n3. Testing unauthenticated request (should fail)...")
    
    response = requests.get(f"{BASE_URL}/resources")
    
    if response.status_code == 401:
        print("✓ Correctly blocked unauthenticated request")
        return True
    else:
        print(f"✗ Unexpected response: {response.status_code}")
        return False

def main():
    print("=" * 60)
    print("Neo Alexandria Authentication Test")
    print("=" * 60)
    
    # Test credentials
    username = "admin@test.com"
    password = "admin123"
    
    # Test unauthenticated request
    test_unauthenticated_request()
    
    # Login
    token = login(username, password)
    
    if token:
        # Test authenticated request
        test_authenticated_request(token)
        
        print("\n" + "=" * 60)
        print("Authentication working! Use this token for API requests:")
        print(f"Authorization: Bearer {token}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Authentication failed. You may need to:")
        print("1. Create a user in the database")
        print("2. Check if the auth module is properly loaded")
        print("3. Verify the database connection")
        print("=" * 60)

if __name__ == "__main__":
    main()
