"""
Test script to diagnose resource creation endpoint issue.
Run with: python test_resource_endpoint.py
"""
import requests
import json

# Test payload
payload = {
    "url": "https://www.postman.com/api-platform/api-documentation/",
    "title": "Test Resource"
}

print("Testing POST /resources endpoint...")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(
        "http://localhost:8000/resources",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    try:
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response Text: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
