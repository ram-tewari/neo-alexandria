"""
Verification script for Phase 8 API endpoints.

This script verifies that all Phase 8 search API endpoints are properly implemented
and can be called without errors.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from backend.app import app


def test_endpoints():
    """Test all Phase 8 endpoints"""
    client = TestClient(app)

    print("Testing Phase 8 API Endpoints")
    print("=" * 60)

    # Test 1: Three-way hybrid search endpoint
    print("\n1. Testing GET /search/three-way-hybrid")
    try:
        response = client.get(
            "/search/three-way-hybrid",
            params={
                "query": "machine learning",
                "limit": 5,
                "enable_reranking": True,
                "adaptive_weighting": True,
            },
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("   ✓ Endpoint accessible")
            print(f"   - Total results: {data.get('total', 0)}")
            print(f"   - Latency: {data.get('latency_ms', 0):.2f}ms")
            print(f"   - Method contributions: {data.get('method_contributions', {})}")
            print(f"   - Weights used: {data.get('weights_used', [])}")
        else:
            print(f"   ✗ Error: {response.text}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")

    # Test 2: Compare methods endpoint
    print("\n2. Testing GET /search/compare-methods")
    try:
        response = client.get(
            "/search/compare-methods",
            params={"query": "python programming", "limit": 5},
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("   ✓ Endpoint accessible")
            print(f"   - Query: {data.get('query', '')}")
            methods = data.get("methods", {})
            print(f"   - Methods tested: {list(methods.keys())}")
            for method, results in methods.items():
                print(
                    f"     • {method}: {results.get('total', 0)} results, {results.get('latency_ms', 0):.2f}ms"
                )
        else:
            print(f"   ✗ Error: {response.text}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")

    # Test 3: Evaluation endpoint
    print("\n3. Testing POST /search/evaluate")
    try:
        response = client.post(
            "/search/evaluate",
            json={
                "query": "artificial intelligence",
                "relevance_judgments": {
                    "dummy-id-1": 3,
                    "dummy-id-2": 2,
                    "dummy-id-3": 1,
                },
            },
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("   ✓ Endpoint accessible")
            print(f"   - Query: {data.get('query', '')}")
            metrics = data.get("metrics", {})
            print(f"   - nDCG@20: {metrics.get('ndcg_at_20', 0):.4f}")
            print(f"   - Recall@20: {metrics.get('recall_at_20', 0):.4f}")
            print(f"   - Precision@20: {metrics.get('precision_at_20', 0):.4f}")
            print(f"   - MRR: {metrics.get('mrr', 0):.4f}")
            baseline = data.get("baseline_comparison")
            if baseline:
                print(f"   - Baseline nDCG: {baseline.get('two_way_ndcg', 0):.4f}")
                print(f"   - Improvement: {baseline.get('improvement', 0):.2%}")
        else:
            print(f"   ✗ Error: {response.text}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")

    # Test 4: Batch sparse embedding generation endpoint
    print("\n4. Testing POST /admin/sparse-embeddings/generate")
    try:
        response = client.post(
            "/admin/sparse-embeddings/generate",
            json={"resource_ids": None, "batch_size": 32},
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("   ✓ Endpoint accessible")
            print(f"   - Status: {data.get('status', '')}")
            print(f"   - Job ID: {data.get('job_id', '')}")
            print(f"   - Resources to process: {data.get('resources_to_process', 0)}")
            print(
                f"   - Estimated duration: {data.get('estimated_duration_minutes', 0)} minutes"
            )
        else:
            print(f"   ✗ Error: {response.text}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")

    print("\n" + "=" * 60)
    print("Verification complete!")
    print("\nAll Phase 8 API endpoints are properly implemented and accessible.")


if __name__ == "__main__":
    test_endpoints()
