"""
Simple script to test RAG quality after chunking fixes.
Verifies that chunks are being retrieved and used for context.
"""

import requests
import json

BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcl9pZCI6ImIzYjA3ZTMwLTk2ZWYtNGRmNi04MjAwLTY5YzBmM2VhOTM2MSIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJ0aWVyIjoicHJlbWl1bSIsInNjb3BlcyI6W10sImV4cCI6MTc2ODkyNTE2MSwidHlwZSI6ImFjY2VzcyJ9.jyV84j-iJSiSqAA-2IF31rlBepYkAmZtrd9PhhBGWlc"


def test_rag_search():
    """Test that search returns results with context from chunks"""
    print("\n" + "="*80)
    print("RAG QUALITY TEST")
    print("="*80 + "\n")
    
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    # Test semantic search (should use chunks if available)
    search_data = {
        "query": "machine learning algorithms",
        "search_type": "semantic",
        "limit": 5
    }
    
    try:
        print("Testing semantic search...")
        resp = requests.post(
            f"{BASE_URL}/search/",
            headers=headers,
            json=search_data,
            timeout=30
        )
        
        if resp.status_code == 200:
            results = resp.json()
            print(f"✓ Search successful")
            print(f"  Results returned: {len(results.get('results', []))}")
            
            # Check if results have context (from chunks)
            if results.get('results'):
                first_result = results['results'][0]
                print(f"\n  First result:")
                print(f"    Title: {first_result.get('title', 'N/A')}")
                print(f"    Score: {first_result.get('score', 'N/A')}")
                print(f"    Has context: {'context' in first_result}")
                
                if 'context' in first_result:
                    context = first_result['context']
                    print(f"    Context length: {len(context)} chars")
                    print(f"    Context preview: {context[:100]}...")
                    print("\n✅ RAG WORKING - Context retrieved from chunks")
                    return True
                else:
                    print("\n⚠️  RAG PARTIAL - Results returned but no context")
                    print("    This may indicate chunks exist but aren't being used for retrieval")
                    return False
            else:
                print("\n⚠️  No results returned")
                return False
        else:
            print(f"✗ Search failed with status {resp.status_code}")
            print(f"  Response: {resp.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_hybrid_search():
    """Test hybrid search (keyword + semantic)"""
    print("\n" + "-"*80)
    print("Testing hybrid search...")
    
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    search_data = {
        "query": "neural networks deep learning",
        "search_type": "hybrid",
        "limit": 3
    }
    
    try:
        resp = requests.post(
            f"{BASE_URL}/search/",
            headers=headers,
            json=search_data,
            timeout=30
        )
        
        if resp.status_code == 200:
            results = resp.json()
            print(f"✓ Hybrid search successful")
            print(f"  Results: {len(results.get('results', []))}")
            return True
        else:
            print(f"✗ Hybrid search failed: {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run RAG quality tests"""
    
    # Check server
    try:
        resp = requests.get(f"{BASE_URL}/docs", timeout=5)
        if resp.status_code != 200:
            print("✗ Server is not running")
            return False
    except:
        print("✗ Server is not running")
        return False
    
    print("✓ Server is ready\n")
    
    # Run tests
    semantic_ok = test_rag_search()
    hybrid_ok = test_hybrid_search()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if semantic_ok and hybrid_ok:
        print("\n✅ RAG QUALITY: GOOD")
        print("   - Chunks are being used for context retrieval")
        print("   - Both semantic and hybrid search working")
        return True
    elif semantic_ok or hybrid_ok:
        print("\n⚠️  RAG QUALITY: PARTIAL")
        print("   - Some search methods working")
        print("   - May need further optimization")
        return True
    else:
        print("\n❌ RAG QUALITY: NEEDS WORK")
        print("   - Search not returning results with context")
        print("   - Check if chunks are being created")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
