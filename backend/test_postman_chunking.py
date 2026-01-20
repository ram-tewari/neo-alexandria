"""
Test chunking with real Postman API documentation URL.
"""

import requests
import time
import psycopg2

BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcl9pZCI6ImIzYjA3ZTMwLTk2ZWYtNGRmNi04MjAwLTY5YzBmM2VhOTM2MSIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJ0aWVyIjoicHJlbWl1bSIsInNjb3BlcyI6W10sImV4cCI6MTc2ODkyNTE2MSwidHlwZSI6ImFjY2VzcyJ9.jyV84j-iJSiSqAA-2IF31rlBepYkAmZtrd9PhhBGWlc"
DB_CONNECTION = "postgresql://postgres:devpassword@localhost:5432/neo_alexandria_dev"

print("="*80)
print("CHUNKING TEST - Postman API Documentation")
print("="*80)

# Create resource with Postman URL
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
resource_data = {
    "url": "https://www.postman.com/api-platform/api-documentation/",
    "title": "Postman API Documentation"
}

print("\n1. Creating resource from Postman URL...")
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
        print(f"   ✓ Resource ID: {resource_id}")
        print(f"   ✓ Ingestion status: {data.get('ingestion_status')}")
        
        # Wait for ingestion
        print("\n2. Waiting 15 seconds for background ingestion...")
        for i in range(15, 0, -1):
            print(f"   {i}...", end="\r")
            time.sleep(1)
        print("   Done!    ")
        
        # Check database
        print("\n3. Checking database for chunks...")
        conn = psycopg2.connect(DB_CONNECTION)
        cursor = conn.cursor()
        
        # Check chunks for this resource
        cursor.execute(
            "SELECT COUNT(*) FROM document_chunks WHERE resource_id = %s",
            (resource_id,)
        )
        chunk_count = cursor.fetchone()[0]
        print(f"   Chunks for this resource: {chunk_count}")
        
        # Check total chunks
        cursor.execute("SELECT COUNT(*) FROM document_chunks")
        total_chunks = cursor.fetchone()[0]
        print(f"   Total chunks in database: {total_chunks}")
        
        # If chunks exist, show sample
        if chunk_count > 0:
            cursor.execute(
                """SELECT content, chunk_index, chunk_metadata 
                   FROM document_chunks 
                   WHERE resource_id = %s 
                   ORDER BY chunk_index 
                   LIMIT 3""",
                (resource_id,)
            )
            print("\n   Sample chunks:")
            for content, idx, metadata in cursor.fetchall():
                print(f"     [{idx}] {content[:80]}...")
                print(f"          Metadata: {metadata}")
        
        cursor.close()
        conn.close()
        
        # Results
        print("\n" + "="*80)
        print("RESULTS")
        print("="*80)
        
        if chunk_count > 0:
            print(f"\n✅ SUCCESS! Chunking is working!")
            print(f"   - Created {chunk_count} chunks for this resource")
            print(f"   - Total chunks in database: {total_chunks}")
            print("\n🎉 RAG system is now functional!")
        else:
            print(f"\n❌ FAILED! No chunks created.")
            print("\n⚠️  Check server logs for errors:")
            print("   - Look for 'Chunking failed for resource'")
            print("   - Look for 'Successfully chunked resource'")
            print("   - Check for any exceptions during ingestion")
            
    else:
        print(f"   ✗ Error: {resp.text}")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
