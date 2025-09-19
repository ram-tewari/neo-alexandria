"""Tests for the enhanced search API endpoint with FTS5 and snippets."""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from backend.app.database.models import Resource


@pytest.fixture
def search_test_data(test_db):
    """Create test data for search API tests."""
    db = test_db()
    now = datetime.now(timezone.utc)
    
    resources = [
        Resource(
            title="Advanced Machine Learning Techniques",
            description="Comprehensive guide to modern ML algorithms including deep learning, neural networks, and AI applications",
            language="en",
            type="book",
            classification_code="006",
            subject=["Machine Learning", "Artificial Intelligence", "Deep Learning"],
            read_status="unread",
            quality_score=0.9,
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=1),
            embedding=[0.1, 0.2, 0.3, 0.4, 0.5],  # Add embedding for hybrid search
        ),
        Resource(
            title="Python Programming for Data Science",
            description="Learn Python programming with focus on data analysis, machine learning libraries, and scientific computing",
            language="en",
            type="article",
            classification_code="006",
            subject=["Python", "Data Science", "Programming"],
            read_status="in_progress",
            quality_score=0.8,
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=3),
            embedding=[0.2, 0.3, 0.4, 0.5, 0.6],  # Add embedding for hybrid search
        ),
        Resource(
            title="Natural Language Processing Fundamentals",
            description="Introduction to NLP concepts, text processing, tokenization, and language models",
            language="en",
            type="book",
            classification_code="006",
            subject=["Natural Language Processing", "Text Processing", "Linguistics"],
            read_status="completed",
            quality_score=0.7,
            created_at=now - timedelta(days=20),
            updated_at=now - timedelta(days=15),
            embedding=[0.3, 0.4, 0.5, 0.6, 0.7],  # Add embedding for hybrid search
        ),
        Resource(
            title="Spanish Language Learning Guide",
            description="Complete guide to learning Spanish language, grammar, vocabulary, and conversation skills",
            language="es",
            type="book",
            classification_code="400",
            subject=["Spanish", "Language Learning", "Grammar"],
            read_status="unread",
            quality_score=0.6,
            created_at=now - timedelta(days=30),
            updated_at=now - timedelta(days=25),
            embedding=[0.4, 0.5, 0.6, 0.7, 0.8],  # Add embedding for hybrid search
        ),
    ]
    
    for resource in resources:
        db.add(resource)
    db.commit()
    
    resource_ids = [str(r.id) for r in resources]
    db.close()
    return resource_ids


class TestEnhancedSearchEndpoint:
    """Test the enhanced search endpoint with FTS5 and snippets."""
    
    def test_basic_search_with_snippets(self, client, search_test_data):
        """Test basic search returns snippets."""
        response = client.post("/search", json={
            "text": "machine learning",
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "total" in data
        assert "items" in data
        assert "facets" in data
        assert "snippets" in data
        
        # Check snippets are present
        assert isinstance(data["snippets"], dict)
        for item in data["items"]:
            assert str(item["id"]) in data["snippets"]
            snippet = data["snippets"][str(item["id"])]
            assert isinstance(snippet, str)
    
    def test_phrase_search(self, client, search_test_data):
        """Test phrase search with quotes."""
        response = client.post("/search", json={
            "text": '"machine learning"',
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find resources with the phrase
        assert data["total"] >= 1
        for item in data["items"]:
            snippet = data["snippets"][str(item["id"])]
            # Snippet should contain either "machine" or "learning" 
            assert "machine" in snippet.lower() or "learning" in snippet.lower()
    
    def test_boolean_search(self, client, search_test_data):
        """Test boolean search with AND/OR operators."""
        # Test AND search
        response = client.post("/search", json={
            "text": "python AND programming",
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find resources with both terms
        if data["total"] > 0:
            for item in data["items"]:
                snippet = data["snippets"][str(item["id"])]
                assert "python" in snippet.lower() or "programming" in snippet.lower()
        
        # Test OR search
        response = client.post("/search", json={
            "text": "spanish OR linguistics",
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find resources with either term
        assert data["total"] >= 1
    
    def test_field_specific_search(self, client, search_test_data):
        """Test field-specific search queries."""
        response = client.post("/search", json={
            "text": "title:python AND description:data",
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find resources matching field-specific criteria
        for item in data["items"]:
            snippet = data["snippets"][str(item["id"])]
            # Should contain relevant terms
            assert "python" in item["title"].lower() or "data" in snippet.lower()
    
    def test_wildcard_search(self, client, search_test_data):
        """Test wildcard search functionality."""
        # First test basic search to ensure it works
        response = client.post("/search", json={
            "text": "learn",
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1, f"Basic search for 'learn' should find results, got {data['total']}"
        
        # Now test wildcard search
        response = client.post("/search", json={
            "text": "learn*",
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Debug: print response if no results
        if data["total"] == 0:
            print(f"Wildcard search response: {data}")
        
        # Should find resources with words starting with "learn"
        assert data["total"] >= 1, f"Expected to find resources with 'learn*', but got {data['total']} results"
        
        for item in data["items"]:
            snippet = data["snippets"][str(item["id"])]
            # Should contain learning-related terms in snippet or title/description
            text_to_check = (snippet + " " + item["title"] + " " + (item["description"] or "")).lower()
            assert "learn" in text_to_check, f"Expected 'learn' in text, got: {text_to_check[:100]}..."
    
    def test_search_with_filters_and_snippets(self, client, search_test_data):
        """Test search with filters still returns snippets."""
        response = client.post("/search", json={
            "text": "learning",
            "filters": {
                "classification_code": ["006"],
                "language": ["en"],
                "min_quality": 0.7
            },
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Check filters are applied
        for item in data["items"]:
            assert item["classification_code"] == "006"
            assert item["language"] == "en"
            assert item["quality_score"] >= 0.7
        
        # Check snippets are still present
        assert isinstance(data["snippets"], dict)
        for item in data["items"]:
            assert str(item["id"]) in data["snippets"]
    
    def test_search_sorting_with_snippets(self, client, search_test_data):
        """Test search sorting options with snippets."""
        response = client.post("/search", json={
            "text": "programming",
            "sort_by": "quality_score",
            "sort_dir": "desc",
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Check sorting is applied
        if len(data["items"]) > 1:
            for i in range(len(data["items"]) - 1):
                assert data["items"][i]["quality_score"] >= data["items"][i + 1]["quality_score"]
        
        # Check snippets are present
        assert isinstance(data["snippets"], dict)
    
    def test_search_without_text_query(self, client, search_test_data):
        """Test structured search without text query."""
        response = client.post("/search", json={
            "filters": {
                "type": ["book"],
                "language": ["en"]
            },
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return only books in English
        for item in data["items"]:
            assert item["type"] == "book"
            assert item["language"] == "en"
        
        # Should still have snippets (fallback)
        assert isinstance(data["snippets"], dict)
    
    def test_search_pagination_with_snippets(self, client, search_test_data):
        """Test search pagination maintains snippets."""
        # First page
        response1 = client.post("/search", json={
            "text": "learning",
            "limit": 2,
            "offset": 0
        })
        
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Second page
        response2 = client.post("/search", json={
            "text": "learning",
            "limit": 2,
            "offset": 2
        })
        
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Should have different items
        ids1 = {item["id"] for item in data1["items"]}
        ids2 = {item["id"] for item in data2["items"]}
        assert ids1.isdisjoint(ids2)
        
        # Both should have snippets
        assert isinstance(data1["snippets"], dict)
        assert isinstance(data2["snippets"], dict)
    
    def test_search_error_handling(self, client, search_test_data):
        """Test search error handling."""
        # Test invalid limit
        response = client.post("/search", json={
            "text": "test",
            "limit": 101  # Over maximum
        })
        
        assert response.status_code == 422
        
        # Test invalid offset
        response = client.post("/search", json={
            "text": "test",
            "offset": -1  # Negative
        })
        
        assert response.status_code == 422
    
    def test_search_facets_with_snippets(self, client, search_test_data):
        """Test that facets are computed correctly with snippets."""
        response = client.post("/search", json={
            "text": "programming",
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Check facets structure
        facets = data["facets"]
        assert "classification_code" in facets
        assert "type" in facets
        assert "language" in facets
        assert "read_status" in facets
        assert "subject" in facets
        
        # Check snippets are present
        assert isinstance(data["snippets"], dict)
    
    @patch('backend.app.services.search_service._detect_fts5')
    @patch('backend.app.services.search_service._fts_index_ready')
    def test_fallback_search_behavior(self, mock_fts_ready, mock_detect_fts, client, search_test_data):
        """Test fallback behavior when FTS5 is not available."""
        mock_detect_fts.return_value = False
        mock_fts_ready.return_value = False
        
        response = client.post("/search", json={
            "text": "machine learning",
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should still return results with snippets
        assert "total" in data
        assert "items" in data
        assert "snippets" in data
        assert isinstance(data["snippets"], dict)
    
    def test_complex_query_combinations(self, client, search_test_data):
        """Test complex query combinations."""
        response = client.post("/search", json={
            "text": 'title:"machine learning" AND (python OR programming)',
            "filters": {
                "classification_code": ["006"],
                "min_quality": 0.6
            },
            "sort_by": "relevance",
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return results with snippets
        assert isinstance(data["snippets"], dict)
        for item in data["items"]:
            assert item["classification_code"] == "006"
            assert item["quality_score"] >= 0.6
            assert str(item["id"]) in data["snippets"]


class TestSearchPerformance:
    """Test search performance characteristics."""
    
    def test_large_result_set_handling(self, client, search_test_data):
        """Test handling of large result sets."""
        response = client.post("/search", json={
            "text": "learning",  # Should match multiple resources
            "limit": 100,  # Large limit
            "offset": 0
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should handle large limits gracefully
        assert len(data["items"]) <= 100
        assert isinstance(data["snippets"], dict)
    
    def test_empty_search_results(self, client, search_test_data):
        """Test handling of empty search results."""
        response = client.post("/search", json={
            "text": "nonexistentterm12345",
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return empty results gracefully
        assert data["total"] == 0
        assert data["items"] == []
        assert data["snippets"] == {}
        assert isinstance(data["facets"], dict)
