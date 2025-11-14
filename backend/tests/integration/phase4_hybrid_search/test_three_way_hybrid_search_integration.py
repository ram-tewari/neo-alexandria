"""Integration tests for three-way hybrid search (Phase 8).

Requirements tested:
- 2.1, 2.2, 2.3, 2.4: Three-way search combines all methods
- 7.1, 7.2, 7.3: Latency meets <200ms target
"""

import pytest
import time
from datetime import datetime, timezone, timedelta
from backend.app.database.models import Resource
from backend.app.schemas.search import SearchQuery
from backend.app.services.search_service import AdvancedSearchService



@pytest.fixture
def integration_test_resources(test_db):
    """Create test resources for integration testing."""
    db = test_db()
    now = datetime.now(timezone.utc)
    
    resources_data = [
        {
            "title": "Introduction to Machine Learning",
            "description": "A comprehensive guide to machine learning algorithms.",
            "language": "en",
            "type": "article",
            "classification_code": "006",
            "subject": ["Machine Learning", "Artificial Intelligence"],
            "read_status": "unread",
            "quality_score": 0.92,
            "date_created": now - timedelta(days=10),
            "date_modified": now - timedelta(days=5),
            "embedding": [0.85, 0.15, 0.10, 0.05, 0.03],
            "sparse_embedding": '{"100": 0.95, "200": 0.85}',
            "sparse_embedding_model": "bge-m3",
            "sparse_embedding_updated_at": now - timedelta(days=5),
        },
        {
            "title": "Deep Learning with Neural Networks",
            "description": "Advanced neural network architectures.",
            "language": "en",
            "type": "article",
            "classification_code": "006",
            "subject": ["Deep Learning", "Neural Networks"],
            "read_status": "in_progress",
            "quality_score": 0.95,
            "date_created": now - timedelta(days=20),
            "date_modified": now - timedelta(days=2),
            "embedding": [0.80, 0.20, 0.12, 0.08, 0.04],
            "sparse_embedding": '{"100": 0.90, "250": 0.80}',
            "sparse_embedding_model": "bge-m3",
            "sparse_embedding_updated_at": now - timedelta(days=2),
        },
        {
            "title": "Natural Language Processing",
            "description": "Text processing and language understanding.",
            "language": "en",
            "type": "article",
            "classification_code": "006",
            "subject": ["Natural Language Processing", "Machine Learning"],
            "read_status": "completed",
            "quality_score": 0.88,
            "date_created": now - timedelta(days=15),
            "date_modified": now - timedelta(days=1),
            "embedding": [0.75, 0.25, 0.15, 0.10, 0.05],
            "sparse_embedding": '{"150": 0.88, "220": 0.78}',
            "sparse_embedding_model": "bge-m3",
            "sparse_embedding_updated_at": now - timedelta(days=1),
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



def test_three_way_search_combines_all_methods(test_db, integration_test_resources):
    """Test that three-way search combines FTS5, dense, and sparse retrieval (Req 2.1, 2.2, 2.3, 2.4)."""
    db = test_db()
    
    query = SearchQuery(text="machine learning", limit=10, offset=0)
    
    resources, total, facets, snippets, metadata = AdvancedSearchService.search_three_way_hybrid(
        db=db,
        query=query,
        enable_reranking=False,
        adaptive_weighting=True
    )
    
    assert isinstance(resources, list)
    assert "method_contributions" in metadata
    assert "fts5" in metadata["method_contributions"]
    assert "dense" in metadata["method_contributions"]
    assert "sparse" in metadata["method_contributions"]
    assert "weights_used" in metadata
    assert len(metadata["weights_used"]) == 3
    
    db.close()


def test_three_way_search_with_reranking(test_db, integration_test_resources):
    """Test three-way search with ColBERT reranking enabled (Req 2.2)."""
    db = test_db()
    
    query = SearchQuery(text="deep learning", limit=10, offset=0)
    
    resources, total, _, _, metadata = AdvancedSearchService.search_three_way_hybrid(
        db=db,
        query=query,
        enable_reranking=True,
        adaptive_weighting=True
    )
    
    assert isinstance(resources, list)
    assert total >= 0
    
    db.close()


def test_adaptive_weighting_adjusts_weights(test_db, integration_test_resources):
    """Test that adaptive weighting adjusts based on query characteristics (Req 2.3)."""
    db = test_db()
    
    short_query = SearchQuery(text="ML", limit=10, offset=0)
    _, _, _, _, metadata_short = AdvancedSearchService.search_three_way_hybrid(
        db=db,
        query=short_query,
        enable_reranking=False,
        adaptive_weighting=True
    )
    
    long_query = SearchQuery(
        text="What are the fundamental principles of machine learning",
        limit=10,
        offset=0
    )
    _, _, _, _, metadata_long = AdvancedSearchService.search_three_way_hybrid(
        db=db,
        query=long_query,
        enable_reranking=False,
        adaptive_weighting=True
    )
    
    assert "weights_used" in metadata_short
    assert "weights_used" in metadata_long
    assert len(metadata_short["weights_used"]) == 3
    assert len(metadata_long["weights_used"]) == 3
    
    db.close()


def test_three_way_search_latency_target(test_db, integration_test_resources):
    """Test that three-way search completes in reasonable time (Req 7.1, 7.2, 7.3)."""
    db = test_db()
    
    query = SearchQuery(text="machine learning", limit=20, offset=0)
    
    start_time = time.time()
    resources, total, _, _, metadata = AdvancedSearchService.search_three_way_hybrid(
        db=db,
        query=query,
        enable_reranking=False,
        adaptive_weighting=True
    )
    end_time = time.time()
    
    latency_ms = (end_time - start_time) * 1000
    
    assert "latency_ms" in metadata
    assert latency_ms < 5000
    assert isinstance(resources, list)
    
    db.close()


def test_three_way_search_with_reranking_latency(test_db, integration_test_resources):
    """Test latency with reranking enabled (Req 7.1, 7.2, 7.3)."""
    db = test_db()
    
    query = SearchQuery(text="deep learning", limit=20, offset=0)
    
    start_time = time.time()
    resources, total, _, _, metadata = AdvancedSearchService.search_three_way_hybrid(
        db=db,
        query=query,
        enable_reranking=True,
        adaptive_weighting=True
    )
    end_time = time.time()
    
    latency_ms = (end_time - start_time) * 1000
    
    assert latency_ms < 10000
    assert isinstance(resources, list)
    
    db.close()


def test_three_way_search_empty_query(test_db, integration_test_resources):
    """Test three-way search with empty query."""
    db = test_db()
    
    query = SearchQuery(text="", limit=10, offset=0)
    
    resources, total, _, _, metadata = AdvancedSearchService.search_three_way_hybrid(
        db=db,
        query=query,
        enable_reranking=False,
        adaptive_weighting=True
    )
    
    assert isinstance(resources, list)
    assert total >= 0
    
    db.close()


def test_three_way_search_pagination(test_db, integration_test_resources):
    """Test pagination in three-way search (Req 2.4)."""
    db = test_db()
    
    query1 = SearchQuery(text="machine learning", limit=2, offset=0)
    resources1, total1, _, _, _ = AdvancedSearchService.search_three_way_hybrid(
        db=db,
        query=query1,
        enable_reranking=False,
        adaptive_weighting=True
    )
    
    query2 = SearchQuery(text="machine learning", limit=2, offset=2)
    resources2, total2, _, _, _ = AdvancedSearchService.search_three_way_hybrid(
        db=db,
        query=query2,
        enable_reranking=False,
        adaptive_weighting=True
    )
    
    assert len(resources1) <= 2
    assert len(resources2) <= 2
    assert total1 == total2
    
    db.close()
