"""
Simple end-to-end test for chunking functionality.
Creates a resource and verifies chunks are created.
"""
import requests
import time
import sqlite3
import sys

# Configuration
API_BASE = "http://127.0.0.1:8000"
DB_PATH = "backend.db"

def get_auth_token():
    """Get authentication token."""
    try:
        with open("test_token.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("❌ test_token.txt not found. Please create it with a valid token.")
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
        "description": """This is a substantial test document that should trigger automatic chunking. 
        The chunking system is designed to break down large documents into smaller, manageable pieces 
        for better retrieval and processing. This content is long enough to create multiple chunks 
        when processed by the semantic chunking algorithm. Each chunk should be stored in the 
        document_chunks table with proper metadata and associations to the parent resource. 
        The system uses sentence boundaries to create semantically coherent chunks that preserve 
        meaning and context. This approach ensures that retrieved chunks are useful and meaningful 
        for downstream tasks like question answering and summarization."""
    }
    
    response = requests.post(f"{API_BASE}/resources", json=payload, headers=headers)
    
    if response.status_code in [200, 201, 202]:
        resource = response.json()
        resource_id = resource.get("id")
        print(f"✅ Resource created: {resource_id}")
        print(f"   Title: {resource.get('title')}")
        print(f"   Status: {response.status_code} - {resource.get('status', resource.get('ingestion_status'))}")
        return resource_id
    else:
        print(f"❌ Failed to create resource: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def check_chunks_in_db(resource_id):
    """Check if chunks were created in the database."""
    print(f"\n🔍 Checking database for chunks...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check total chunks
        cursor.execute("SELECT COUNT(*) FROM document_chunks WHERE resource_id = ?", (resource_id,))
        chunk_count = cursor.fetchone()[0]
        
        if chunk_count > 0:
            print(f"✅ Found {chunk_count} chunks in database")
            
            # Get chunk details
            cursor.execute("""
                SELECT chunk_index, LENGTH(content), chunk_metadata 
                FROM document_chunks 
                WHERE resource_id = ? 
                ORDER BY chunk_index
            """, (resource_id,))
            
            chunks = cursor.fetchall()
            print(f"\n📊 Chunk details:")
            for idx, length, metadata in chunks:
                print(f"   Chunk {idx}: {length} characters")
            
            conn.close()
            return True
        else:
            print(f"❌ No chunks found for resource {resource_id}")
            
            # Check if resource exists
            cursor.execute("SELECT id, title, ingestion_status FROM resources WHERE id = ?", (resource_id,))
            resource = cursor.fetchone()
            if resource:
                print(f"   Resource exists: {resource[1]} (status: {resource[2]})")
            else:
                print(f"   Resource not found in database")
            
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    """Run the end-to-end chunking test."""
    print("=" * 60)
    print("CHUNKING END-TO-END TEST")
    print("=" * 60)
    
    # Get token
    token = get_auth_token()
    
    # Create resource
    resource_id = create_test_resource(token)
    if not resource_id:
        print("\n❌ TEST FAILED: Could not create resource")
        sys.exit(1)
    
    # Wait for processing (chunking should happen immediately via event)
    print("\n⏳ Waiting 5 seconds for ingestion and chunking to complete...")
    time.sleep(5)
    
    # Check chunks
    success = check_chunks_in_db(resource_id)
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED: Chunking is working!")
    else:
        print("❌ TEST FAILED: No chunks were created")
        print("\nPossible issues:")
        print("1. Event handlers not registered")
        print("2. CHUNK_ON_RESOURCE_CREATE is disabled")
        print("3. Content too short (< 100 chars)")
        print("4. Chunking service error (check server logs)")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
