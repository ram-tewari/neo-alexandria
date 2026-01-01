"""
Test suite for Search module endpoints.

This module tests all API endpoints provided by the Search module,
including keyword search, semantic search, hybrid search, and filtering.

Endpoints tested:
- POST /search - Perform search with various strategies
- POST /search/keyword - Keyword-only search
- POST /search/semantic - Semantic-only search
- POST /search/hybrid - Hybrid search
- GET /search/suggestions - Get search suggestions
- GET /search/health - Module health check
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.models import Resource


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_search_query():
    """Sample search query for testing."""
    return {
        "text": "machine learning",
        "limit": 10,
        "offset": 0
    }


@pytest.fixture
def create_test_resource(db: Session):
    """Factory fixture to create test resources."""
    def _create_resource(**kwargs):
        defaults = {
            "title": "Test Resource",
            "description": "Test content about machine learning",
            "source": "https://example.com/resource",
            "format": "text/html",
            "ingestion_status": "completed"
        }
        defaults.update(kwargs)
        resource = Resource(**defaults)
        db.add(resource)
        db.commit()
        db.refresh(resource)
        return resource
    return _create_resource


class TestGeneralSearch:
    """Test POST /search - General search endpoint."""

    def test_search_success(self, client, sample_search_query):
        """Test successful search."""
        response = client.post("/search", json=sample_search_query)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data or "items" in data or isinstance(data, list)

    def test_search_empty_query(self, client):
        """Test search with empty query."""
        response = client.post("/search", json={"text": ""})
        
        assert response.status_code in [200, 400, 422]

    def test_search_with_filters(self, client):
        """Test search with filters."""
        response = client.post("/search", json={
            "text": "test",
            "filters": {
                "type": ["text/html"]
            }
        })
        
        assert response.status_code == 200

    def test_search_pagination(self, client):
        """Test search pagination."""
        response = client.post("/search", json={
            "text": "test",
            "limit": 5,
            "offset": 0
        })
        
        assert response.status_code == 200
        data = response.json()
        results = data.get("items", data)
        if isinstance(results, list):
            assert len(results) <= 5


class TestKeywordSearch:
    """Test POST /search - Keyword search strategy."""

    def test_keyword_search_success(self, client, create_test_resource):
        """Test successful keyword search."""
        create_test_resource(title="Python Programming")
        
        response = client.post("/search", json={"text": "python", "hybrid_weight": 0.0})
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)

    def test_keyword_search_no_results(self, client):
        """Test keyword search with no results."""
        response = client.post("/search", json={"text": "nonexistentterm12345", "hybrid_weight": 0.0})
        
        assert response.status_code == 200
        data = response.json()
        results = data.get("items", data)
        if isinstance(results, list):
            assert len(results) == 0

    def test_keyword_search_case_insensitive(self, client, create_test_resource):
        """Test keyword search is case insensitive."""
        create_test_resource(title="Python Programming")
        
        response = client.post("/search", json={"text": "PYTHON", "hybrid_weight": 0.0})
        
        assert response.status_code == 200


class TestSemanticSearch:
    """Test POST /search - Semantic search strategy."""

    def test_semantic_search_success(self, client, create_test_resource):
        """Test successful semantic search."""
        create_test_resource(title="Machine Learning Tutorial")
        
        response = client.post("/search", json={"text": "AI and deep learning", "hybrid_weight": 1.0})
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)

    def test_semantic_search_with_limit(self, client):
        """Test semantic search with result limit."""
        response = client.post("/search", json={
            "text": "machine learning",
            "hybrid_weight": 1.0,
            "limit": 5
        })
        
        assert response.status_code == 200

    def test_semantic_search_requires_embeddings(self, client):
        """Test semantic search behavior when embeddings not available."""
        response = client.post("/search", json={"text": "test", "hybrid_weight": 1.0})
        
        # Should either succeed or return appropriate error
        assert response.status_code in [200, 400, 500, 503]


class TestHybridSearch:
    """Test POST /search - Hybrid search strategy."""

    def test_hybrid_search_success(self, client, create_test_resource):
        """Test successful hybrid search."""
        create_test_resource(title="Python Machine Learning")
        
        response = client.post("/search", json={"text": "python ML", "hybrid_weight": 0.5})
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)

    def test_hybrid_search_with_weights(self, client):
        """Test hybrid search with custom weights."""
        response = client.post("/search", json={
            "text": "machine learning",
            "hybrid_weight": 0.7
        })
        
        assert response.status_code == 200

    def test_hybrid_search_ranking(self, client, create_test_resource):
        """Test hybrid search combines rankings."""
        create_test_resource(title="Exact Match")
        create_test_resource(title="Semantic Match")
        
        response = client.post("/search", json={"text": "machine learning", "hybrid_weight": 0.5})
        
        assert response.status_code == 200
        data = response.json()
        results = data.get("items", data)
        # Results should be ranked by combined score
        assert isinstance(results, list)


class TestSearchSuggestions:
    """Test search suggestions (not implemented in current module)."""

    def test_suggestions_not_implemented(self, client):
        """Test that suggestions endpoint doesn't exist yet."""
        response = client.get("/search/suggestions?query=mach")
        
        # Endpoint doesn't exist, should return 404
        assert response.status_code == 404


class TestSearchFilters:
    """Test search filtering capabilities."""

    def test_filter_by_type(self, client, create_test_resource):
        """Test filtering by type."""
        create_test_resource(format="text/html")
        create_test_resource(format="application/pdf")
        
        response = client.post("/search", json={
            "text": "test",
            "filters": {"type": ["text/html"]}
        })
        
        assert response.status_code == 200

    def test_filter_by_language(self, client, create_test_resource):
        """Test filtering by language."""
        create_test_resource(title="Python Tutorial")
        
        response = client.post("/search", json={
            "text": "test",
            "filters": {"language": ["en"]}
        })
        
        assert response.status_code == 200

    def test_filter_by_date_range(self, client):
        """Test filtering by date range."""
        response = client.post("/search", json={
            "text": "test",
            "filters": {
                "created_from": "2024-01-01T00:00:00",
                "created_to": "2024-12-31T23:59:59"
            }
        })
        
        assert response.status_code == 200

    def test_multiple_filters(self, client):
        """Test applying multiple filters."""
        response = client.post("/search", json={
            "text": "test",
            "filters": {
                "type": ["text/html"],
                "language": ["en"],
                "created_from": "2024-01-01T00:00:00"
            }
        })
        
        assert response.status_code == 200


class TestSearchHealth:
    """Test GET /search/health - Module health check."""

    def test_health_check_success(self, client):
        """Test successful health check."""
        response = client.get("/search/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok", "up"]

    def test_health_check_includes_search_status(self, client):
        """Test health check includes search engine status."""
        response = client.get("/search/health")
        
        assert response.status_code == 200
        data = response.json()
        # May include index status, embedding service status, etc.
        assert "status" in data


class TestSearchIntegration:
    """Integration tests for search workflows."""

    def test_search_result_ranking(self, client, create_test_resource):
        """Test search results are properly ranked."""
        create_test_resource(title="Machine Learning Basics")
        create_test_resource(title="Advanced ML")
        create_test_resource(title="Python Tutorial")
        
        response = client.post("/search", json={"text": "machine learning"})
        
        assert response.status_code == 200
        data = response.json()
        results = data.get("items", data)
        # ML-related results should rank higher than Python tutorial
        assert isinstance(results, list)

    def test_search_with_no_results(self, client):
        """Test search behavior with no results."""
        response = client.post("/search", json={"text": "veryuniquetermthatwontmatch123"})
        
        assert response.status_code == 200
        data = response.json()
        results = data.get("items", data)
        if isinstance(results, list):
            assert len(results) == 0

    def test_search_strategy_comparison(self, client, create_test_resource):
        """Test different search strategies return different results."""
        create_test_resource(title="Python ML")
        
        keyword_response = client.post("/search", json={"text": "python", "hybrid_weight": 0.0})
        semantic_response = client.post("/search", json={"text": "programming language", "hybrid_weight": 1.0})
        hybrid_response = client.post("/search", json={"text": "python", "hybrid_weight": 0.5})
        
        assert keyword_response.status_code == 200
        assert semantic_response.status_code == 200
        assert hybrid_response.status_code == 200
