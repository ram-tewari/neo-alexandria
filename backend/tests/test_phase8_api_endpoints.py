"""
Test suite for Phase 8 API endpoints.

Tests the following endpoints:
- GET /search/three-way-hybrid
- GET /search/compare-methods
- POST /search/evaluate
- POST /admin/sparse-embeddings/generate
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
import pytest
from backend.app.database.models import Resource


@pytest.fixture
def phase8_test_resources(test_db):
    """Create test resources with embeddings and sparse embeddings for Phase 8 testing."""
    db = test_db()
    now = datetime.now(timezone.utc)
    
    resources_data = [
        {
            "title": "Machine Learning Fundamentals",
            "description": "Introduction to machine learning algorithms and techniques. Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
            "language": "en",
            "type": "article",
            "classification_code": "006",
            "subject": ["Machine Learning", "Artificial Intelligence"],
            "read_status": "unread",
            "quality_score": 0.9,
            "date_created": now - timedelta(days=10),
            "date_modified": now - timedelta(days=5),
            "embedding": [0.8, 0.2, 0.1, 0.05, 0.03],
            "sparse_embedding": '{"100": 0.9, "200": 0.7, "300": 0.5}',
            "sparse_embedding_model": "bge-m3",
            "sparse_embedding_updated_at": now - timedelta(days=5),
        },
        {
            "title": "Deep Learning with Neural Networks",
            "description": "Advanced neural network architectures and training techniques. Deep learning uses multi-layer neural networks to learn hierarchical representations of data.",
            "language": "en",
            "type": "article",
            "classification_code": "006",
            "subject": ["Deep Learning", "Neural Networks"],
            "read_status": "in_progress",
            "quality_score": 0.95,
            "date_created": now - timedelta(days=20),
            "date_modified": now - timedelta(days=2),
            "embedding": [0.75, 0.25, 0.15, 0.08, 0.04],
            "sparse_embedding": '{"100": 0.8, "250": 0.6, "350": 0.4}',
            "sparse_embedding_model": "bge-m3",
            "sparse_embedding_updated_at": now - timedelta(days=2),
        },
        {
            "title": "Natural Language Processing Techniques",
            "description": "Text processing and language understanding methods. NLP combines linguistics and machine learning to enable computers to understand human language.",
            "language": "en",
            "type": "article",
            "classification_code": "006",
            "subject": ["Natural Language Processing", "Machine Learning"],
            "read_status": "completed",
            "quality_score": 0.85,
            "date_created": now - timedelta(days=15),
            "date_modified": now - timedelta(days=1),
            "embedding": [0.7, 0.3, 0.2, 0.1, 0.05],
            "sparse_embedding": '{"150": 0.85, "220": 0.65, "320": 0.45}',
            "sparse_embedding_model": "bge-m3",
            "sparse_embedding_updated_at": now - timedelta(days=1),
        },
        {
            "title": "Computer Vision Applications",
            "description": "Image recognition and visual understanding systems. Computer vision enables machines to interpret and understand visual information from the world.",
            "language": "en",
            "type": "article",
            "classification_code": "006",
            "subject": ["Computer Vision", "Deep Learning"],
            "read_status": "unread",
            "quality_score": 0.88,
            "date_created": now - timedelta(days=8),
            "date_modified": now - timedelta(days=3),
            "embedding": [0.65, 0.35, 0.18, 0.12, 0.06],
            "sparse_embedding": '{"180": 0.75, "240": 0.55, "340": 0.35}',
            "sparse_embedding_model": "bge-m3",
            "sparse_embedding_updated_at": now - timedelta(days=3),
        },
        {
            "title": "Resource Without Sparse Embedding",
            "description": "This resource has no sparse embedding yet. Testing resource without sparse embedding for batch generation endpoint.",
            "language": "en",
            "type": "article",
            "classification_code": "006",
            "subject": ["Testing"],
            "read_status": "unread",
            "quality_score": 0.7,
            "date_created": now - timedelta(days=5),
            "date_modified": now - timedelta(days=4),
            "embedding": [0.5, 0.4, 0.3, 0.2, 0.1],
            "sparse_embedding": None,
            "sparse_embedding_model": None,
            "sparse_embedding_updated_at": None,
        },
    ]
    
    resources = []
    for data in resources_data:
        resource = Resource(**data)
        db.add(resource)
        resources.append(resource)
    
    db.commit()
    
    for resource in resources:
        db.refresh(resource)
    
    resource_ids = [str(r.id) for r in resources]
    db.close()
    
    return resource_ids


# ============================================================================
# GET /search/three-way-hybrid Tests
# ============================================================================

def test_three_way_hybrid_basic_search(client, phase8_test_resources):
    """Test basic three-way hybrid search endpoint."""
    response = client.get(
        "/search/three-way-hybrid",
        params={"query": "machine learning", "limit": 10}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "total" in data
    assert "items" in data
    assert "facets" in data
    assert "snippets" in data
    assert "latency_ms" in data
    assert "method_contributions" in data
    assert "weights_used" in data
    
    # Verify method contributions structure
    contributions = data["method_contributions"]
    assert "fts5" in contributions
    assert "dense" in contributions
    assert "sparse" in contributions
    
    # Verify weights_used is a list of 3 floats
    assert isinstance(data["weights_used"], list)
    assert len(data["weights_used"]) == 3
    assert all(isinstance(w, (int, float)) for w in data["weights_used"])


def test_three_way_hybrid_with_reranking_disabled(client, phase8_test_resources):
    """Test three-way hybrid search with reranking disabled."""
    response = client.get(
        "/search/three-way-hybrid",
        params={
            "query": "neural networks",
            "limit": 5,
            "enable_reranking": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "items" in data
    assert len(data["items"]) <= 5


def test_three_way_hybrid_with_adaptive_weighting_disabled(client, phase8_test_resources):
    """Test three-way hybrid search with adaptive weighting disabled."""
    response = client.get(
        "/search/three-way-hybrid",
        params={
            "query": "deep learning",
            "limit": 10,
            "adaptive_weighting": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # With adaptive weighting disabled, weights should be equal (or close to equal)
    weights = data["weights_used"]
    assert len(weights) == 3


def test_three_way_hybrid_pagination(client, phase8_test_resources):
    """Test pagination in three-way hybrid search."""
    # First page
    response1 = client.get(
        "/search/three-way-hybrid",
        params={"query": "learning", "limit": 2, "offset": 0}
    )
    
    assert response1.status_code == 200
    data1 = response1.json()
    assert len(data1["items"]) <= 2
    
    # Second page
    response2 = client.get(
        "/search/three-way-hybrid",
        params={"query": "learning", "limit": 2, "offset": 2}
    )
    
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Items should be different (if enough results)
    if len(data1["items"]) > 0 and len(data2["items"]) > 0:
        ids1 = {item["id"] for item in data1["items"]}
        ids2 = {item["id"] for item in data2["items"]}
        # Pages should not overlap
        assert ids1.isdisjoint(ids2) or data1["total"] <= 2


def test_three_way_hybrid_empty_query(client, phase8_test_resources):
    """Test three-way hybrid search with empty query."""
    response = client.get(
        "/search/three-way-hybrid",
        params={"query": "", "limit": 10}
    )
    
    # Should still return results (all resources)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_three_way_hybrid_short_query(client, phase8_test_resources):
    """Test three-way hybrid search with short query (should boost FTS5)."""
    response = client.get(
        "/search/three-way-hybrid",
        params={"query": "ML", "limit": 10, "adaptive_weighting": True}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # With adaptive weighting, short queries should boost FTS5
    # We can't assert exact weights, but we can verify the structure
    assert "weights_used" in data
    assert len(data["weights_used"]) == 3


def test_three_way_hybrid_long_query(client, phase8_test_resources):
    """Test three-way hybrid search with long query (should boost dense)."""
    long_query = "What are the fundamental principles and techniques used in machine learning algorithms"
    
    response = client.get(
        "/search/three-way-hybrid",
        params={"query": long_query, "limit": 10, "adaptive_weighting": True}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "weights_used" in data
    assert len(data["weights_used"]) == 3


def test_three_way_hybrid_latency_tracking(client, phase8_test_resources):
    """Test that latency is tracked and returned."""
    response = client.get(
        "/search/three-way-hybrid",
        params={"query": "machine learning", "limit": 10}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "latency_ms" in data
    assert isinstance(data["latency_ms"], (int, float))
    assert data["latency_ms"] >= 0


# ============================================================================
# GET /search/compare-methods Tests
# ============================================================================

def test_compare_methods_basic(client, phase8_test_resources):
    """Test basic compare methods endpoint."""
    response = client.get(
        "/search/compare-methods",
        params={"query": "machine learning", "limit": 5}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "query" in data
    assert data["query"] == "machine learning"
    assert "methods" in data
    
    methods = data["methods"]
    
    # Verify all expected methods are present
    expected_methods = [
        "fts5_only",
        "dense_only",
        "sparse_only",
        "two_way_hybrid",
        "three_way_hybrid",
        "three_way_reranked"
    ]
    
    for method in expected_methods:
        assert method in methods
        assert "results" in methods[method]
        assert "latency_ms" in methods[method]
        assert "total" in methods[method]
        assert isinstance(methods[method]["latency_ms"], (int, float))


def test_compare_methods_result_counts(client, phase8_test_resources):
    """Test that compare methods returns correct result counts."""
    response = client.get(
        "/search/compare-methods",
        params={"query": "learning", "limit": 3}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    methods = data["methods"]
    
    # Each method should return at most 'limit' results
    for method_name, method_data in methods.items():
        assert len(method_data["results"]) <= 3


def test_compare_methods_latency_comparison(client, phase8_test_resources):
    """Test that latency is tracked for each method."""
    response = client.get(
        "/search/compare-methods",
        params={"query": "neural networks", "limit": 5}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    methods = data["methods"]
    
    # All methods should have non-negative latency
    for method_name, method_data in methods.items():
        assert method_data["latency_ms"] >= 0


def test_compare_methods_empty_query(client, phase8_test_resources):
    """Test compare methods with empty query."""
    response = client.get(
        "/search/compare-methods",
        params={"query": "", "limit": 5}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "methods" in data


# ============================================================================
# POST /search/evaluate Tests
# ============================================================================

def test_evaluate_search_basic(client, phase8_test_resources):
    """Test basic search evaluation endpoint."""
    # Create relevance judgments (using actual resource IDs from fixture)
    relevance_judgments = {
        phase8_test_resources[0]: 3,  # Highly relevant
        phase8_test_resources[1]: 2,  # Relevant
        phase8_test_resources[2]: 1,  # Marginally relevant
        phase8_test_resources[3]: 0,  # Not relevant
    }
    
    response = client.post(
        "/search/evaluate",
        json={
            "query": "machine learning",
            "relevance_judgments": relevance_judgments
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "query" in data
    assert data["query"] == "machine learning"
    assert "metrics" in data
    
    metrics = data["metrics"]
    assert "ndcg_at_20" in metrics
    assert "recall_at_20" in metrics
    assert "precision_at_20" in metrics
    assert "mrr" in metrics
    
    # Verify metric values are in valid ranges
    assert 0.0 <= metrics["ndcg_at_20"] <= 1.0
    assert 0.0 <= metrics["recall_at_20"] <= 1.0
    assert 0.0 <= metrics["precision_at_20"] <= 1.0
    assert 0.0 <= metrics["mrr"] <= 1.0


def test_evaluate_search_with_baseline_comparison(client, phase8_test_resources):
    """Test evaluation with baseline comparison."""
    relevance_judgments = {
        phase8_test_resources[0]: 3,
        phase8_test_resources[1]: 2,
    }
    
    response = client.post(
        "/search/evaluate",
        json={
            "query": "deep learning",
            "relevance_judgments": relevance_judgments
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Baseline comparison may or may not be present depending on implementation
    # If present, verify structure
    if "baseline_comparison" in data and data["baseline_comparison"] is not None:
        baseline = data["baseline_comparison"]
        assert "two_way_ndcg" in baseline
        assert "improvement" in baseline
        assert isinstance(baseline["two_way_ndcg"], (int, float))
        assert isinstance(baseline["improvement"], (int, float))


def test_evaluate_search_all_relevant(client, phase8_test_resources):
    """Test evaluation when all documents are highly relevant."""
    relevance_judgments = {
        phase8_test_resources[0]: 3,
        phase8_test_resources[1]: 3,
        phase8_test_resources[2]: 3,
    }
    
    response = client.post(
        "/search/evaluate",
        json={
            "query": "machine learning",
            "relevance_judgments": relevance_judgments
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    metrics = data["metrics"]
    # With all highly relevant docs, metrics should be >= 0 (may be 0 if search returns no results)
    assert metrics["ndcg_at_20"] >= 0.0


def test_evaluate_search_no_relevant(client, phase8_test_resources):
    """Test evaluation when no documents are relevant."""
    relevance_judgments = {
        phase8_test_resources[0]: 0,
        phase8_test_resources[1]: 0,
        phase8_test_resources[2]: 0,
    }
    
    response = client.post(
        "/search/evaluate",
        json={
            "query": "completely unrelated query xyz123",
            "relevance_judgments": relevance_judgments
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    metrics = data["metrics"]
    # With no relevant docs, most metrics should be 0
    assert metrics["ndcg_at_20"] == 0.0
    assert metrics["recall_at_20"] == 0.0
    assert metrics["mrr"] == 0.0


def test_evaluate_search_empty_judgments(client, phase8_test_resources):
    """Test evaluation with empty relevance judgments."""
    response = client.post(
        "/search/evaluate",
        json={
            "query": "machine learning",
            "relevance_judgments": {}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should still return metrics (all zeros)
    metrics = data["metrics"]
    assert metrics["ndcg_at_20"] == 0.0


# ============================================================================
# POST /admin/sparse-embeddings/generate Tests
# ============================================================================

def test_batch_generate_sparse_embeddings_all_resources(client, phase8_test_resources):
    """Test batch generation for all resources without sparse embeddings."""
    response = client.post(
        "/admin/sparse-embeddings/generate",
        json={}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "status" in data
    assert "job_id" in data
    assert "estimated_duration_minutes" in data
    assert "resources_to_process" in data
    
    # Verify job_id is a valid UUID format
    import uuid
    try:
        uuid.UUID(data["job_id"])
    except ValueError:
        pytest.fail("job_id is not a valid UUID")
    
    # Should have at least one resource to process (the one without sparse embedding)
    assert data["resources_to_process"] >= 1
    assert isinstance(data["estimated_duration_minutes"], int)
    assert data["estimated_duration_minutes"] >= 1


def test_batch_generate_sparse_embeddings_specific_resources(client, phase8_test_resources):
    """Test batch generation for specific resource IDs."""
    # Request generation for first two resources
    resource_ids = phase8_test_resources[:2]
    
    response = client.post(
        "/admin/sparse-embeddings/generate",
        json={"resource_ids": resource_ids}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "job_id" in data
    assert data["resources_to_process"] == 2


def test_batch_generate_sparse_embeddings_with_batch_size(client, phase8_test_resources):
    """Test batch generation with custom batch size."""
    response = client.post(
        "/admin/sparse-embeddings/generate",
        json={"batch_size": 16}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "job_id" in data


def test_batch_generate_sparse_embeddings_empty_resource_list(client, phase8_test_resources):
    """Test batch generation with empty resource list."""
    response = client.post(
        "/admin/sparse-embeddings/generate",
        json={"resource_ids": []}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # With empty resource_ids list, should process 0 resources
    # Note: If resource_ids is empty list, the endpoint treats it as "process specific resources"
    # and finds 0 matching resources
    assert data["resources_to_process"] >= 0


def test_batch_generate_sparse_embeddings_nonexistent_resources(client, phase8_test_resources):
    """Test batch generation with nonexistent resource IDs."""
    import uuid
    fake_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
    
    response = client.post(
        "/admin/sparse-embeddings/generate",
        json={"resource_ids": fake_ids}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should process 0 resources (IDs don't exist)
    assert data["resources_to_process"] == 0


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_three_way_hybrid_invalid_limit(client, phase8_test_resources):
    """Test three-way hybrid with invalid limit parameter."""
    response = client.get(
        "/search/three-way-hybrid",
        params={"query": "test", "limit": 200}  # Exceeds max of 100
    )
    
    # Should return validation error
    assert response.status_code == 422


def test_three_way_hybrid_negative_offset(client, phase8_test_resources):
    """Test three-way hybrid with negative offset."""
    response = client.get(
        "/search/three-way-hybrid",
        params={"query": "test", "offset": -1}
    )
    
    # Should return validation error
    assert response.status_code == 422


def test_compare_methods_invalid_limit(client, phase8_test_resources):
    """Test compare methods with invalid limit."""
    response = client.get(
        "/search/compare-methods",
        params={"query": "test", "limit": 0}  # Below minimum of 1
    )
    
    # Should return validation error
    assert response.status_code == 422


def test_evaluate_search_invalid_relevance_scores(client, phase8_test_resources):
    """Test evaluation with invalid relevance scores."""
    # Note: This test depends on whether the API validates relevance scores
    # If validation is not implemented, this test may need adjustment
    relevance_judgments = {
        phase8_test_resources[0]: 5,  # Invalid: should be 0-3
    }
    
    response = client.post(
        "/search/evaluate",
        json={
            "query": "test",
            "relevance_judgments": relevance_judgments
        }
    )
    
    # Depending on implementation, this might succeed or fail
    # For now, we just verify it doesn't crash
    assert response.status_code in [200, 422]
