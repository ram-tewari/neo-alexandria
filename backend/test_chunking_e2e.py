"""
End-to-end test: Create resource via API and verify chunks are created
"""
import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def wait_for_server(max_attempts=10):
    """Wait for server to be ready"""
    print("⏳ Waiting for server to start...")
    for i in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/api/monitoring/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Server is ready!")
                return True
        except Exception as e:
            print(f"   Attempt {i+1}/{max_attempts}: {str(e)[:50]}")
        time.sleep(2)
    return False

def create_test_user():
    """Create test user and get token"""
    print("\n👤 Creating test user...")
    
    user_data = {
        "email": "chunking_test@example.com",
        "password": "testpass123",
        "full_name": "Chunking Test User"
    }
    
    # Try to register (may already exist)
    try:
        requests.post(f"{BASE_URL}/api/auth/register", json=user_data, timeout=5)
    except:
        pass
    
    # Login
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]},
        timeout=5
    )
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print(f"✅ Got auth token")
        return token
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        return None

def create_resource_with_chunking(token):
    """Create a resource with substantial content for chunking"""
    print("\n📝 Creating resource with substantial content...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create content long enough to trigger chunking
    content = """
    This is a comprehensive test of the document chunking system in Neo Alexandria 2.0.
    The chunking system is designed to break down large documents into manageable pieces
    that can be efficiently processed and retrieved by the RAG (Retrieval Augmented Generation) system.
    
    The system uses semantic chunking by default, which respects sentence boundaries and maintains
    context across chunks through configurable overlap. This ensures that information is not lost
    at chunk boundaries and that the system can effectively retrieve relevant context.
    
    Performance is a key consideration. The chunking process must be fast enough to not block
    the main application thread, while still producing high-quality chunks that maintain semantic
    coherence. The system uses efficient algorithms to process documents quickly.
    
    Error handling is robust. If chunking fails for any reason, the resource creation process
    continues successfully. This ensures that the system remains available even when individual
    components encounter issues. Failures are logged for debugging purposes.
    
    The chunking system supports multiple strategies including semantic chunking based on sentence
    boundaries and fixed-size chunking for cases where semantic analysis is not appropriate.
    Future enhancements will include AST-based chunking for source code files.
    
    Testing is comprehensive. The system includes unit tests for individual components, integration
    tests for the complete pipeline, and end-to-end tests that verify the entire workflow from
    resource creation through chunk storage and retrieval.
    
    Quality assurance processes ensure that chunks maintain proper metadata including position,
    token count, and parent-child relationships. This metadata is essential for effective retrieval
    and for maintaining the document structure during reconstruction.
    """ * 3  # Repeat to make it longer
    
    resource_data = {
        "url": f"https://example.com/chunking-e2e-test-{int(time.time())}",
        "title": "End-to-End Chunking Test",
        "description": content
    }
    
    print(f"   Content length: {len(content)} characters")
    
    response = requests.post(
        f"{BASE_URL}/api/resources/",
        json=resource_data,
        headers=headers,
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        resource = response.json()
        resource_id = resource.get("id")
        print(f"✅ Resource created: {resource_id}")
        print(f"   Title: {resource.get('title')}")
        return resource_id
    else:
        print(f"❌ Resource creation failed: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        return None

def check_chunks(token, resource_id, max_attempts=5):
    """Check if chunks were created for the resource"""
    print(f"\n🔍 Checking for chunks (resource: {resource_id})...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for attempt in range(max_attempts):
        print(f"   Attempt {attempt + 1}/{max_attempts}...")
        
        try:
            # Try to get chunks via API endpoint
            response = requests.get(
                f"{BASE_URL}/api/resources/{resource_id}/chunks",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                chunks = response.json()
                chunk_count = len(chunks) if isinstance(chunks, list) else chunks.get('total', 0)
                
                if chunk_count > 0:
                    print(f"✅ Found {chunk_count} chunks!")
                    
                    # Show first few chunks
                    if isinstance(chunks, list):
                        for i, chunk in enumerate(chunks[:3]):
                            print(f"\n   Chunk {i+1}:")
                            print(f"      Position: {chunk.get('position')}")
                            print(f"      Tokens: {chunk.get('token_count')}")
                            content_preview = chunk.get('content', '')[:80]
                            print(f"      Preview: {content_preview}...")
                    
                    return True
                else:
                    print(f"   No chunks yet...")
            else:
                print(f"   Endpoint returned {response.status_code}")
        except Exception as e:
            print(f"   Error checking chunks: {e}")
        
        if attempt < max_attempts - 1:
            print(f"   Waiting 2 seconds before retry...")
            time.sleep(2)
    
    print(f"❌ No chunks found after {max_attempts} attempts")
    return False

def main():
    print("="*60)
    print("END-TO-END CHUNKING TEST")
    print("="*60)
    
    # Step 1: Wait for server
    if not wait_for_server():
        print("\n❌ Server not responding")
        print("Make sure the server is running:")
        print("  cd backend && uvicorn app.main:app --reload")
        return 1
    
    # Step 2: Get auth token
    token = create_test_user()
    if not token:
        print("\n❌ Could not get auth token")
        return 1
    
    # Step 3: Create resource
    resource_id = create_resource_with_chunking(token)
    if not resource_id:
        print("\n❌ Could not create resource")
        return 1
    
    # Step 4: Check for chunks
    chunks_created = check_chunks(token, resource_id)
    
    # Summary
    print("\n" + "="*60)
    if chunks_created:
        print("SUCCESS! CHUNKING WORKS END-TO-END!")
        print("="*60)
        print("\nVerified:")
        print("  [OK] Server running")
        print("  [OK] Resource created")
        print("  [OK] Chunks generated and stored")
        print("  [OK] Chunks retrievable via API")
        return 0
    else:
        print("CHUNKING NOT WORKING")
        print("="*60)
        print("\nWhat worked:")
        print("  [OK] Server running")
        print("  [OK] Resource created")
        print("  [FAIL] Chunks NOT created")
        print("\nCheck server logs for errors related to:")
        print("  - 'Registering resource handlers'")
        print("  - 'Emitted resource.created event'")
        print("  - 'Triggering automatic chunking'")
        return 1

if __name__ == "__main__":
    sys.exit(main())
