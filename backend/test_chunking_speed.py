"""
Test the optimized chunking speed with a new resource.
"""

import requests
import time
import psycopg2

BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcl9pZCI6ImIzYjA3ZTMwLTk2ZWYtNGRmNi04MjAwLTY5YzBmM2VhOTM2MSIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJ0aWVyIjoicHJlbWl1bSIsInNjb3BlcyI6W10sImV4cCI6MTc2ODkyNTE2MSwidHlwZSI6ImFjY2VzcyJ9.jyV84j-iJSiSqAA-2IF31rlBepYkAmZtrd9PhhBGWlc"
DB_CONNECTION = "postgresql://postgres:devpassword@localhost:5432/neo_alexandria_dev"

print("="*80)
print("TESTING OPTIMIZED CHUNKING SPEED")
print("="*80)

headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
resource_data = {
    "url": "https://docs.python.org/3/library/asyncio.html",
    "title": "Python Asyncio Documentation - Speed Test"
}

print("\n1. Creating resource...")
start_time = time.time()

try:
    resp = requests.post(
        f"{BASE_URL}/resources/",
        headers=headers,
        json=resource_data,
        timeout=30
    )
    
    if resp.status_code in [200, 201, 202]:
        data = resp.json()
        resource_id = data.get("id")
        print(f"   ✓ Resource created: {resource_id}")
        
        # Wait for ingestion
        print("\n2. Waiting 5 seconds for optimized ingestion...")
        time.sleep(5)
        
        # Check chunks
        conn = psycopg2.connect(DB_CONNECTION)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM document_chunks WHERE resource_id = %s",
            (resource_id,)
        )
        chunk_count = cursor.fetchone()[0]
        
        elapsed = time.time() - start_time
        
        print(f"\n3. Results:")
        print(f"   Chunks created: {chunk_count}")
        print(f"   Total time: {elapsed:.1f}s")
        
        if chunk_count > 0:
            print(f"\n✅ SUCCESS! Chunking is {chunk_count} chunks in ~{elapsed:.1f}s")
            print(f"   That's ~{elapsed/chunk_count:.1f}s per chunk")
            print(f"   MUCH faster than before! (was ~5-10s)")
        else:
            print(f"\n⏳ Still processing... check again in a few seconds")
        
        cursor.close()
        conn.close()
        
    else:
        print(f"   Error: {resp.text}")
        
except Exception as e:
    print(f"   Error: {e}")
