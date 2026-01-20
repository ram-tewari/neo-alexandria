"""
Test script to verify document chunking fixes.
Creates a test resource and verifies chunks are created and stored.
"""

import requests
import time
import psycopg2
from typing import Optional, Tuple

BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcl9pZCI6ImIzYjA3ZTMwLTk2ZWYtNGRmNi04MjAwLTY5YzBmM2VhOTM2MSIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJ0aWVyIjoicHJlbWl1bSIsInNjb3BlcyI6W10sImV4cCI6MTc2ODkyNTE2MSwidHlwZSI6ImFjY2VzcyJ9.jyV84j-iJSiSqAA-2IF31rlBepYkAmZtrd9PhhBGWlc"

# Database connection string - update if needed
DB_CONNECTION = "postgresql://postgres:postgres@localhost:5432/neo_alexandria"


def create_test_resource() -> Optional[str]:
    """
    Create a test resource with substantial content for chunking.
    
    Returns:
        Resource ID if successful, None otherwise
    """
    print("\n" + "="*80)
    print("CREATING TEST RESOURCE")
    print("="*80 + "\n")
    
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    # Create resource with substantial content for chunking
    resource_data = {
        "url": "https://example.com/chunking-test",
        "title": "Chunking Test Resource",
        "description": "A test resource with substantial content to verify chunking functionality. " * 10,
        "content": """
        This is a comprehensive test document for verifying the document chunking system.
        
        Machine learning is a subset of artificial intelligence that focuses on developing
        algorithms and statistical models that enable computer systems to improve their
        performance on a specific task through experience. The fundamental premise of
        machine learning is that systems can learn from data, identify patterns, and make
        decisions with minimal human intervention.
        
        There are three main types of machine learning: supervised learning, unsupervised
        learning, and reinforcement learning. Supervised learning involves training a model
        on labeled data, where the correct output is known. Unsupervised learning works with
        unlabeled data to discover hidden patterns or structures. Reinforcement learning
        involves an agent learning to make decisions by performing actions and receiving
        feedback in the form of rewards or penalties.
        
        Deep learning, a subset of machine learning, uses neural networks with multiple
        layers to progressively extract higher-level features from raw input. Convolutional
        neural networks (CNNs) excel at image recognition tasks, while recurrent neural
        networks (RNNs) and transformers are particularly effective for sequential data
        like text and time series.
        
        Natural language processing (NLP) is another important application area of machine
        learning. It enables computers to understand, interpret, and generate human language.
        Modern NLP systems use transformer architectures like BERT and GPT, which have
        revolutionized tasks such as translation, summarization, and question answering.
        
        The training process for machine learning models involves several key steps:
        data collection and preprocessing, feature engineering, model selection, training,
        validation, and deployment. Proper data preprocessing is crucial, as the quality
        of input data directly affects model performance. Common preprocessing steps include
        normalization, handling missing values, and encoding categorical variables.
        
        Model evaluation is performed using various metrics depending on the task. For
        classification, common metrics include accuracy, precision, recall, and F1 score.
        For regression tasks, metrics like mean squared error (MSE) and R-squared are used.
        Cross-validation techniques help ensure that models generalize well to unseen data.
        
        Overfitting and underfitting are common challenges in machine learning. Overfitting
        occurs when a model learns the training data too well, including noise and outliers,
        leading to poor performance on new data. Underfitting happens when a model is too
        simple to capture the underlying patterns in the data. Regularization techniques
        like L1 and L2 regularization help prevent overfitting.
        
        The field of machine learning continues to evolve rapidly, with new architectures
        and techniques being developed regularly. Recent advances include few-shot learning,
        transfer learning, and federated learning, which address challenges related to
        limited labeled data, computational efficiency, and privacy concerns.
        """ * 3  # Repeat to ensure enough content for multiple chunks
    }
    
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
            print(f"✓ Resource created successfully")
            print(f"  Resource ID: {resource_id}")
            print(f"  Status: {data.get('status')}")
            print(f"  Ingestion Status: {data.get('ingestion_status')}")
            return resource_id
        else:
            print(f"✗ Failed to create resource: {resp.status_code}")
            print(f"  Response: {resp.text[:200]}")
            return None
            
    except Exception as e:
        print(f"✗ Error creating resource: {e}")
        return None


def wait_for_ingestion(resource_id: str, max_wait: int = 60) -> bool:
    """
    Wait for resource ingestion to complete.
    
    Args:
        resource_id: Resource ID to check
        max_wait: Maximum seconds to wait
        
    Returns:
        True if ingestion completed, False otherwise
    """
    print(f"\nWaiting for ingestion to complete (max {max_wait}s)...")
    
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            resp = requests.get(
                f"{BASE_URL}/resources/{resource_id}/status",
                headers=headers,
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("ingestion_status", "unknown")
                
                if status == "completed":
                    print(f"✓ Ingestion completed")
                    return True
                elif status == "failed":
                    print(f"✗ Ingestion failed")
                    print(f"  Error: {data.get('ingestion_error', 'Unknown error')}")
                    return False
                else:
                    print(f"  Status: {status}... waiting")
            
        except Exception as e:
            print(f"  Error checking status: {e}")
        
        time.sleep(2)
    
    print(f"✗ Timeout waiting for ingestion")
    return False


def verify_chunks_in_database(resource_id: str) -> Tuple[int, bool]:
    """
    Verify chunks were created in the database.
    
    Args:
        resource_id: Resource ID to check
        
    Returns:
        Tuple of (chunk_count, success)
    """
    print("\n" + "="*80)
    print("VERIFYING CHUNKS IN DATABASE")
    print("="*80 + "\n")
    
    try:
        conn = psycopg2.connect(DB_CONNECTION)
        cursor = conn.cursor()
        
        # Count chunks for this resource
        cursor.execute(
            "SELECT COUNT(*) FROM document_chunks WHERE resource_id = %s",
            (resource_id,)
        )
        chunk_count = cursor.fetchone()[0]
        
        # Get sample chunk data
        cursor.execute(
            """
            SELECT id, chunk_index, LENGTH(content) as content_length, chunk_metadata
            FROM document_chunks
            WHERE resource_id = %s
            ORDER BY chunk_index
            LIMIT 5
            """,
            (resource_id,)
        )
        sample_chunks = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        print(f"Chunk Count: {chunk_count}")
        
        if chunk_count > 0:
            print(f"\n✓ Chunks found in database!")
            print(f"\nSample chunks:")
            for chunk_id, idx, length, metadata in sample_chunks:
                print(f"  - Chunk {idx}: {length} characters")
                if metadata and "embedding_generated" in metadata:
                    print(f"    Embedding: {'✓' if metadata['embedding_generated'] else '✗'}")
            
            return chunk_count, True
        else:
            print(f"\n✗ No chunks found in database")
            return 0, False
            
    except Exception as e:
        print(f"✗ Error querying database: {e}")
        return 0, False


def main():
    """Run chunking verification test"""
    print("\n" + "="*80)
    print("DOCUMENT CHUNKING VERIFICATION TEST")
    print("="*80)
    
    # Check server
    try:
        resp = requests.get(f"{BASE_URL}/docs", timeout=5)
        if resp.status_code != 200:
            print("\n✗ Server is not running")
            print("Please start the server with: uvicorn app.main:app --reload")
            return False
    except:
        print("\n✗ Server is not running")
        return False
    
    print("✓ Server is ready\n")
    
    # Create test resource
    resource_id = create_test_resource()
    if not resource_id:
        print("\n❌ TEST FAILED - Could not create resource")
        return False
    
    # Wait for ingestion
    if not wait_for_ingestion(resource_id, max_wait=60):
        print("\n⚠️  Ingestion did not complete - checking chunks anyway")
    
    # Verify chunks in database
    chunk_count, success = verify_chunks_in_database(resource_id)
    
    # Print final result
    print("\n" + "="*80)
    print("FINAL RESULT")
    print("="*80)
    
    if success and chunk_count > 0:
        print(f"\n✅ CHUNKING TEST PASSED")
        print(f"   - Resource created: {resource_id}")
        print(f"   - Chunks created: {chunk_count}")
        print(f"   - Context Precision should now be > 0.000")
        return True
    else:
        print(f"\n❌ CHUNKING TEST FAILED")
        print(f"   - Resource created: {resource_id}")
        print(f"   - Chunks created: {chunk_count}")
        print(f"   - Expected: > 0 chunks")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
