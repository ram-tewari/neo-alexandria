"""
Test chunking by waiting for ingestion to complete.
"""
import requests
import time
import sqlite3
import sys

# Configuration
API_BASE = "http://127.0.0.1:8000"
DB_PATH = "backend.db"
MAX_WAIT_SECONDS = 30

def get_auth_token():
    """Get authentication token."""
    try:
        with open("test_token.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("❌ test_token.txt not found")
        sys.exit(1)

def create_test_resource(token):
    """Create a test resource via API."""
    print("\n📝 Creating test resource...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": f"https://example.com/chunking-test-{int(time.time())}",
        "title": "Chunking Test Resource",
        "description": """This is a substantial test document for chunking verification. 
        The content should be long enough to create multiple chunks when processed."""
    }
    
    response = requests.post(f"{API_BASE}/resources", json=payload, headers=headers)
    
    if response.status_code in [200, 201, 202]:
        resource = response.json()
        resource_id = resource.get("id")
        print(f"✅ Resource created: {resource_id}")
        return resource_id
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return None

def wait_for_ingestion(resource_id, max_wait=MAX_WAIT_SECONDS):
    """Wait for ingestion to complete."""
    print(f"\n⏳ Waiting for ingestion to complete (max {max_wait}s)...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        cursor.execute(
            "SELECT ingestion_status FROM resources WHERE id = ?",
            (resource_id,)
        )
        result = cursor.fetchone()
        
        if result:
            status = result[0]
            elapsed = int(time.time() - start_time)
            print(f"   [{elapsed}s] Status: {status}")
            
            if status == "completed":
                conn.close()
                print("✅ Ingestion completed!")
                return True
            elif status == "failed":
                conn.close()
                print("❌ Ingestion failed!")
                return False
        
        time.sleep(1)
    
    conn.close()
    print(f"⏱️  Timeout after {max_wait}s")
    return False

def check_chunks(resource_id):
    """Check if chunks were created."""
    print(f"\n🔍 Checking for chunks...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT COUNT(*) FROM document_chunks WHERE resource_id = ?",
        (resource_id,)
    )
    chunk_count = cursor.fetchone()[0]
    
    if chunk_count > 0:
        print(f"✅ Found {chunk_count} chunks!")
        
        cursor.execute("""
            SELECT chunk_index, LENGTH(content) 
            FROM document_chunks 
            WHERE resource_id = ? 
            ORDER BY chunk_index
        """, (resource_id,))
        
        chunks = cursor.fetchall()
        print(f"\n📊 Chunk details:")
        for idx, length in chunks:
            print(f"   Chunk {idx}: {length} characters")
        
        conn.close()
        return True
    else:
        print(f"❌ No chunks found")
        conn.close()
        return False

def main():
    print("=" * 60)
    print("CHUNKING TEST - WAIT FOR INGESTION")
    print("=" * 60)
    
    token = get_auth_token()
    resource_id = create_test_resource(token)
    
    if not resource_id:
        print("\n❌ TEST FAILED: Could not create resource")
        sys.exit(1)
    
    if not wait_for_ingestion(resource_id):
        print("\n❌ TEST FAILED: Ingestion did not complete")
        sys.exit(1)
    
    success = check_chunks(resource_id)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED: Chunking works!")
    else:
        print("❌ TEST FAILED: No chunks created")
        print("\nCheck server logs for chunking errors")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
