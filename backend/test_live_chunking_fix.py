"""
Test the content extraction fix with a live server.
Verifies that the Postman documentation URL creates multiple chunks.
"""
import requests
import time
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_URL = "https://www.postman.com/api-platform/api-documentation/"

# Load auth token
with open("test_token.txt", "r") as f:
    TOKEN = f.read().strip()

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_live_chunking():
    """Test chunking with live server."""
    print("=" * 70)
    print("LIVE CHUNKING TEST - Content Extraction Fix Verification")
    print("=" * 70)
    
    # Step 1: Create resource
    print(f"\n📝 Step 1: Creating resource with URL...")
    print(f"   URL: {TEST_URL}")
    
    payload = {
        "url": TEST_URL,
        "title": "Postman API Documentation - Live Test",
        "description": "Testing improved content extraction with live server"
    }
    
    response = requests.post(
        f"{BASE_URL}/resources",
        headers=HEADERS,
        json=payload
    )
    
    if response.status_code != 201:
        print(f"❌ Failed to create resource: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    resource = response.json()
    resource_id = resource["id"]
    print(f"✅ Resource created: {resource_id}")
    print(f"   Status: {resource.get('ingestion_status', 'unknown')}")
    
    # Step 2: Wait for ingestion
    print(f"\n⏳ Step 2: Waiting for ingestion to complete...")
    max_wait = 30  # seconds
    waited = 0
    
    while waited < max_wait:
        response = requests.get(
            f"{BASE_URL}/resources/{resource_id}",
            headers=HEADERS
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get resource: {response.status_code}")
            return False
        
        resource = response.json()
        status = resource.get("ingestion_status", "unknown")
        
        if status == "completed":
            print(f"✅ Ingestion completed in {waited} seconds")
            break
        elif status == "failed":
            print(f"❌ Ingestion failed: {resource.get('ingestion_error', 'unknown')}")
            return False
        
        time.sleep(2)
        waited += 2
        print(f"   Still processing... ({waited}s)")
    
    if waited >= max_wait:
        print(f"❌ Timeout waiting for ingestion")
        return False
    
    # Step 3: Check chunks
    print(f"\n📦 Step 3: Checking chunks...")
    response = requests.get(
        f"{BASE_URL}/resources/{resource_id}/chunks",
        headers=HEADERS
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get chunks: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    chunks = response.json()
    chunk_count = len(chunks)
    
    print(f"\n📊 Results:")
    print(f"   Total chunks: {chunk_count}")
    
    if chunk_count == 0:
        print(f"❌ No chunks created!")
        return False
    
    # Show chunk details
    for i, chunk in enumerate(chunks[:5]):  # Show first 5
        content_length = len(chunk.get("content", ""))
        print(f"   • Chunk {i}: {content_length} characters")
    
    if chunk_count > 5:
        print(f"   ... and {chunk_count - 5} more chunks")
    
    # Verify fix worked
    print(f"\n🔍 Verification:")
    if chunk_count >= 5:
        print(f"✅ PASS: Multiple chunks created ({chunk_count} chunks)")
        print(f"✅ Content extraction fix is working!")
        print(f"\n" + "=" * 70)
        print(f"✅ TEST PASSED: Chunking works with live server!")
        print("=" * 70)
        return True
    else:
        print(f"⚠️  WARNING: Only {chunk_count} chunk(s) created")
        print(f"   Expected: 5+ chunks for this URL")
        print(f"   This might indicate the fix didn't apply")
        return False

if __name__ == "__main__":
    try:
        success = test_live_chunking()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
