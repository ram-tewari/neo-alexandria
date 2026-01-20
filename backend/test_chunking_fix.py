"""
Test chunking fix - verify that resources are being chunked properly
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcl9pZCI6ImIzYjA3ZTMwLTk2ZWYtNGRmNi04MjAwLTY5YzBmM2VhOTM2MSIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJ0aWVyIjoicHJlbWl1bSIsInNjb3BlcyI6W10sImV4cCI6MTc2ODkyNTE2MSwidHlwZSI6ImFjY2VzcyJ9.jyV84j-iJSiSqAA-2IF31rlBepYkAmZtrd9PhhBGWlc"


def test_chunking():
    """Test that chunking is working"""
    print("\n" + "="*80)
    print("TESTING CHUNKING FIX")
    print("="*80 + "\n")
    
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    # Create a resource with substantial content
    resource_data = {
        "url": "https://example.com/test-chunking-fix",
        "title": "Test Chunking Fix",
        "content": """
        This is a test document to verify that chunking is working properly.
        
        Machine learning is a subset of artificial intelligence that enables systems 
        to learn and improve from experience without being explicitly programmed. 
        It focuses on the development of computer programs that can access data and 
        use it to learn for themselves.

        The process of learning begins with observations or data, such as examples, 
        direct experience, or instruction, in order to look for patterns in data and 
        make better decisions in the future based on the examples that we provide. 
        The primary aim is to allow the computers learn automatically without human 
        intervention or assistance and adjust actions accordingly.

        There are several types of machine learning algorithms. Supervised learning 
        involves training on labeled data. Unsupervised learning finds patterns in 
        unlabeled data. Reinforcement learning uses rewards and penalties to guide 
        learning.

        Deep learning is a subset of machine learning that uses neural networks with 
        multiple layers. These deep neural networks can learn complex patterns and 
        representations from large amounts of data. Applications include image 
        recognition, natural language processing, and speech recognition.
        """,
        "type": "article",
    }
    
    print("1. Creating resource...")
    try:
        resp = requests.post(
            f"{BASE_URL}/resources/",
            json=resource_data,
            headers=headers,
            timeout=30
        )
        
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code in [201, 202]:
            data = resp.json()
            resource_id = data.get("id")
            print(f"   ✅ Resource created: {resource_id}")
            
            # Wait for ingestion to complete
            print("\n2. Waiting for ingestion to complete (10 seconds)...")
            time.sleep(10)
            
            # Check database for chunks
            print("\n3. Checking database for chunks...")
            from app.shared.database import get_sync_db, init_database
            from app.database.models import DocumentChunk, Resource
            
            init_database()
            db = next(get_sync_db())
            
            try:
                chunk_count = db.query(DocumentChunk).filter_by(resource_id=resource_id).count()
                
                if chunk_count > 0:
                    print(f"   ✅ SUCCESS: Found {chunk_count} chunks in database!")
                    
                    # Show sample chunk
                    sample = db.query(DocumentChunk).filter_by(resource_id=resource_id).first()
                    print(f"\n   Sample chunk:")
                    print(f"   - Index: {sample.chunk_index}")
                    print(f"   - Content: {sample.content[:100]}...")
                    print(f"   - Metadata: {sample.chunk_metadata}")
                    
                    return True
                else:
                    print(f"   ❌ FAIL: No chunks found in database")
                    
                    # Check resource status
                    resource = db.query(Resource).filter_by(id=resource_id).first()
                    if resource:
                        print(f"\n   Resource status:")
                        print(f"   - Ingestion status: {resource.ingestion_status}")
                        print(f"   - Ingestion error: {resource.ingestion_error}")
                    
                    return False
                    
            finally:
                db.close()
        else:
            print(f"   ❌ Resource creation failed: {resp.status_code}")
            try:
                error = resp.json()
                print(f"   Error: {error}")
            except:
                print(f"   Response: {resp.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_chunking()
    
    print("\n" + "="*80)
    print("TEST RESULT")
    print("="*80)
    
    if success:
        print("✅ CHUNKING IS WORKING!")
        sys.exit(0)
    else:
        print("❌ CHUNKING IS STILL BROKEN")
        print("\nPossible issues:")
        print("1. ChunkingService import missing")
        print("2. CHUNK_ON_RESOURCE_CREATE not enabled")
        print("3. Ingestion pipeline failing")
        print("4. Database transaction not committing")
        sys.exit(1)
