"""
Simple script to create a resource and check if chunking happens.
"""

import requests
import time
import psycopg2

BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcl9pZCI6ImIzYjA3ZTMwLTk2ZWYtNGRmNi04MjAwLTY5YzBmM2VhOTM2MSIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJ0aWVyIjoicHJlbWl1bSIsInNjb3BlcyI6W10sImV4cCI6MTc2ODkyNTE2MSwidHlwZSI6ImFjY2VzcyJ9.jyV84j-iJSiSqAA-2IF31rlBepYkAmZtrd9PhhBGWlc"
DB_CONNECTION = "postgresql://postgres:devpassword@localhost:5432/neo_alexandria_dev"

print("="*80)
print("CHUNKING DEBUG TEST")
print("="*80)

# Create resource
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
resource_data = {
    "url": "https://example.com/chunking-debug-test",
    "title": "Chunking Debug Test",
    "content": "Machine learning is transforming technology. " * 100  # Repeat to ensure enough content
}

print("\n1. Creating resource...")
try:
    resp = requests.post(
        f"{BASE_URL}/resources/",
        headers=headers,
        json=resource_data,
        timeout=30
    )
    print(f"   Status: {resp.status_code}")
    if resp.status_code in [200, 201, 202]:
        data = resp.json()
        resource_id = data.get("id")
        print(f"   Resource ID: {resource_id}")
        print(f"   Ingestion status: {data.get('ingestion_status')}")
        
        # Wait for ingestion
        print("\n2. Waiting 10 seconds for background ingestion...")
        time.sleep(10)
        
        # Check database
        print("\n3. Checking database for chunks...")
        conn = psycopg2.connect(DB_CONNECTION)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM document_chunks WHERE resource_id = %s",
            (resource_id,)
        )
        chunk_count = cursor.fetchone()[0]
        print(f"   Chunks for this resource: {chunk_count}")
        
        cursor.execute("SELECT COUNT(*) FROM document_chunks")
        total_chunks = cursor.fetchone()[0]
        print(f"   Total chunks in database: {total_chunks}")
        
        cursor.close()
        conn.close()
        
        if chunk_count > 0:
            print("\n✅ SUCCESS! Chunking is working!")
        else:
            print("\n❌ FAILED! No chunks created.")
            print("\nPossible issues:")
            print("  - Background task not executing")
            print("  - Chunking code has a bug")
            print("  - Check server logs for errors")
    else:
        print(f"   Error: {resp.text}")
except Exception as e:
    print(f"   Error: {e}")
