"""
Test creating a resource via the API endpoint
This simulates what the frontend does
"""
import sys
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment before importing app
import os
os.environ["DATABASE_URL"] = "postgresql://postgres:devpassword@localhost:5432/neo_alexandria_dev"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=== Testing Resource Creation via API ===\n")

# First, login to get a token
print("Step 1: Logging in...")
login_payload = {
    "username": "test@example.com",
    "password": "testpassword123"
}

login_response = client.post("/auth/login", data=login_payload)
print(f"Login Status: {login_response.status_code}")

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.json()}")
    print("\nTrying to create a test user first...")
    
    # Try to register a user
    register_payload = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    register_response = client.post("/auth/register", json=register_payload)
    print(f"Register Status: {register_response.status_code}")
    
    if register_response.status_code in [200, 201]:
        print("✓ User registered, logging in again...")
        login_response = client.post("/auth/login", data=login_payload)
        print(f"Login Status: {login_response.status_code}")

if login_response.status_code == 200:
    token_data = login_response.json()
    access_token = token_data.get("access_token")
    print(f"✓ Logged in successfully\n")
    
    # Create a resource with authentication
    payload = {
        "url": "https://example.com/test-article",
        "title": "Test Article",
        "description": "A test article for debugging"
    }

    print(f"Step 2: Creating resource")
    print(f"POST /resources")
    print(f"Payload: {payload}\n")

    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/resources", json=payload, headers=headers)
else:
    print("❌ Could not authenticate, skipping resource creation")
    sys.exit(1)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}\n")

if response.status_code in [200, 202]:
    resource_id = response.json()["id"]
    print(f"Resource created with ID: {resource_id}")
    print("Waiting 5 seconds for background ingestion...")
    time.sleep(5)
    
    # Check resource status
    print(f"\nGET /resources/{resource_id}")
    get_response = client.get(f"/resources/{resource_id}")
    print(f"Status Code: {get_response.status_code}")
    
    if get_response.status_code == 200:
        resource_data = get_response.json()
        print(f"\nResource Status: {resource_data.get('ingestion_status')}")
        print(f"Title: {resource_data.get('title')}")
        print(f"Description: {resource_data.get('description', 'None')[:100]}...")
        
        if resource_data.get('ingestion_error'):
            print(f"\n❌ Ingestion Error: {resource_data['ingestion_error']}")
    else:
        print(f"Error: {get_response.json()}")
else:
    print(f"❌ Failed to create resource: {response.json()}")
