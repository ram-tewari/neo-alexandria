"""
Test resource creation and chunking
"""

import requests
import time

BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcl9pZCI6ImIzYjA3ZTMwLTk2ZWYtNGRmNi04MjAwLTY5YzBmM2VhOTM2MSIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJ0aWVyIjoicHJlbWl1bSIsInNjb3BlcyI6W10sImV4cCI6MTc2ODkyNTE2MSwidHlwZSI6ImFjY2VzcyJ9.jyV84j-iJSiSqAA-2IF31rlBepYkAmZtrd9PhhBGWlc"

def test_resource_creation():
    """Test creating a resource with content"""
    print("\n" + "="*80)
    print("TESTING RESOURCE CREATION AND CHUNKING")
    print("="*80 + "\n")
    
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    # Create a resource with substantial content
    resource_data = {
        "title": "Machine Learning Fundamentals",
        "url": "https://example.com/ml-fundamentals",
        "content": """
        Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on the development of computer programs that can access data and use it to learn for themselves.

        The process of learning begins with observations or data, such as examples, direct experience, or instruction, in order to look for patterns in data and make better decisions in the future based on the examples that we provide. The primary aim is to allow the computers learn automatically without human intervention or assistance and adjust actions accordingly.

        There are several types of machine learning algorithms:

        1. Supervised Learning: The algorithm learns from labeled training data, helping predict outcomes for unforeseen data. Common algorithms include linear regression, logistic regression, decision trees, and neural networks.

        2. Unsupervised Learning: The algorithm learns from unlabeled data, finding hidden patterns or intrinsic structures. Common algorithms include k-means clustering, hierarchical clustering, and principal component analysis.

        3. Reinforcement Learning: The algorithm learns through trial and error, receiving rewards or penalties for actions. It's commonly used in robotics, gaming, and navigation.

        Deep learning is a subset of machine learning that uses neural networks with multiple layers. These deep neural networks can learn complex patterns and representations from large amounts of data. Applications include image recognition, natural language processing, and speech recognition.

        Key concepts in machine learning include:
        - Training data: The dataset used to train the model
        - Features: Input variables used for prediction
        - Labels: Output variables (in supervised learning)
        - Model: The mathematical representation learned from data
        - Overfitting: When a model performs well on training data but poorly on new data
        - Underfitting: When a model is too simple to capture patterns in the data

        Machine learning has numerous applications across industries, including healthcare (disease diagnosis), finance (fraud detection), retail (recommendation systems), and autonomous vehicles.
        """,
        "resource_type": "article",
        "tags": ["machine-learning", "ai", "deep-learning", "algorithms"]
    }
    
    print("Creating resource...")
    try:
        resp = requests.post(
            f"{BASE_URL}/resources/",
            json=resource_data,
            headers=headers,
            timeout=30
        )
        
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 201:
            data = resp.json()
            resource_id = data.get("id")
            print(f"[OK] Resource created successfully!")
            print(f"Resource ID: {resource_id}")
            print(f"Title: {data.get('title')}")
            
            # Wait a bit for chunking to complete
            print("\nWaiting 3 seconds for chunking to complete...")
            time.sleep(3)
            
            # Check if chunks were created
            print("\nChecking for chunks...")
            chunks_resp = requests.get(
                f"{BASE_URL}/resources/{resource_id}/chunks",
                headers=headers,
                timeout=10
            )
            
            if chunks_resp.status_code == 200:
                chunks = chunks_resp.json()
                print(f"[OK] Found {len(chunks)} chunks!")
                if chunks:
                    print(f"\nFirst chunk preview:")
                    print(f"  Content: {chunks[0].get('content', '')[:100]}...")
                    print(f"  Index: {chunks[0].get('chunk_index')}")
                return True
            else:
                print(f"[FAIL] Could not retrieve chunks: {chunks_resp.status_code}")
                print(f"Response: {chunks_resp.text[:200]}")
                return False
        else:
            print(f"[FAIL] Resource creation failed: {resp.status_code}")
            try:
                error = resp.json()
                print(f"Error: {error}")
            except:
                print(f"Response: {resp.text[:200]}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")
        return False


def check_database_chunks():
    """Check chunks directly in database"""
    print("\n" + "="*80)
    print("CHECKING DATABASE FOR CHUNKS")
    print("="*80 + "\n")
    
    try:
        from app.shared.database import get_sync_db, init_database
        from app.database.models import DocumentChunk, Resource
        
        init_database()
        db = next(get_sync_db())
        
        try:
            resource_count = db.query(Resource).count()
            chunk_count = db.query(DocumentChunk).count()
            
            print(f"Resources in database: {resource_count}")
            print(f"Chunks in database: {chunk_count}")
            
            if chunk_count > 0:
                print("\n[OK] Chunks found in database!")
                # Show sample chunk
                sample = db.query(DocumentChunk).first()
                print(f"\nSample chunk:")
                print(f"  ID: {sample.id}")
                print(f"  Resource ID: {sample.resource_id}")
                print(f"  Index: {sample.chunk_index}")
                print(f"  Content: {sample.content[:100]}...")
                return True
            else:
                print("\n[FAIL] No chunks found in database!")
                return False
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] Could not check database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test resource creation
    creation_success = test_resource_creation()
    
    # Check database
    db_success = check_database_chunks()
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Resource Creation: {'[OK]' if creation_success else '[FAIL]'}")
    print(f"Database Chunks: {'[OK]' if db_success else '[FAIL]'}")
    print()
