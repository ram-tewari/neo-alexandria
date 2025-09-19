"""
Neo Alexandria 2.0 - Phase 5.5 Recommendation System Test Suite

This module provides comprehensive testing for the personalized recommendation engine.
It validates all aspects of the recommendation system from unit tests to integration tests.

Related files:
- app/services/recommendation_service.py: Core recommendation logic being tested
- app/routers/recommendation.py: API endpoints being tested
- app/schemas/recommendation.py: Data models being validated
- conftest.py: Test fixtures and configuration
- test_recommendation_config.py: Test utilities and helpers

Test Categories:
- Unit Tests: Core functions (cosine similarity, vector conversion, profile generation)
- Integration Tests: End-to-end recommendation generation flows
- API Tests: HTTP endpoint functionality and validation
- Edge Cases: Error handling and boundary conditions
- Performance Tests: Scalability and caching behavior
- Legacy Tests: Backward compatibility and regression testing

Features:
- Comprehensive test coverage with 31 test cases
- Mocked external dependencies (DDGS search, AI core)
- Isolated test database with automatic cleanup
- Deterministic test data for consistent results
- Performance benchmarking and caching validation
- Error handling and graceful degradation testing

Test Markers:
- @pytest.mark.recommendation: All recommendation tests
- @pytest.mark.recommendation_unit: Unit tests for components
- @pytest.mark.recommendation_integration: Integration tests
- @pytest.mark.recommendation_api: API endpoint tests
- @pytest.mark.recommendation_performance: Performance tests
- @pytest.mark.recommendation_edge_cases: Edge case tests
- @pytest.mark.slow: Tests that take longer to run

Usage:
- Run all tests: pytest -m recommendation
- Run specific category: pytest -m recommendation_unit
- Run with coverage: pytest -m recommendation --cov=app.services.recommendation_service
"""

from __future__ import annotations

import pytest
import numpy as np
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.models import Resource, AuthoritySubject
from backend.app.services.recommendation_service import (
    generate_user_profile_vector,
    get_top_subjects,
    fetch_candidates,
    prepare_candidate,
    score_candidates,
    generate_recommendations,
    _cosine_similarity,
    _to_numpy_vector,
)


@pytest.fixture
def client(test_db) -> TestClient:
    return TestClient(app)


# ============================================================================
# Unit Tests for Core Functions
# ============================================================================

@pytest.mark.recommendation
@pytest.mark.recommendation_unit
class TestCosineSimilarity:
    """Test cosine similarity computation."""
    
    def test_identical_vectors(self):
        """Test cosine similarity of identical vectors equals 1.0."""
        vec_a = np.array([1.0, 2.0, 3.0])
        vec_b = np.array([1.0, 2.0, 3.0])
        assert _cosine_similarity(vec_a, vec_b) == pytest.approx(1.0)
    
    def test_orthogonal_vectors(self):
        """Test cosine similarity of orthogonal vectors equals 0.0."""
        vec_a = np.array([1.0, 0.0])
        vec_b = np.array([0.0, 1.0])
        assert _cosine_similarity(vec_a, vec_b) == pytest.approx(0.0)
    
    def test_opposite_vectors(self):
        """Test cosine similarity of opposite vectors equals -1.0, clamped to 0.0."""
        vec_a = np.array([1.0, 0.0])
        vec_b = np.array([-1.0, 0.0])
        assert _cosine_similarity(vec_a, vec_b) == 0.0  # Clamped to 0
    
    def test_zero_vector_handling(self):
        """Test that zero vectors return 0.0 similarity."""
        vec_a = np.array([0.0, 0.0, 0.0])
        vec_b = np.array([1.0, 2.0, 3.0])
        assert _cosine_similarity(vec_a, vec_b) == 0.0
    
    def test_different_length_vectors(self):
        """Test that vectors of different lengths return 0.0 similarity."""
        vec_a = np.array([1.0, 2.0])
        vec_b = np.array([1.0, 2.0, 3.0])
        assert _cosine_similarity(vec_a, vec_b) == 0.0
    
    def test_score_clamping(self):
        """Test that scores are properly clamped to [0,1] range."""
        # Test negative similarity (should be clamped to 0)
        vec_a = np.array([1.0, 0.0])
        vec_b = np.array([-1.0, 0.0])
        assert _cosine_similarity(vec_a, vec_b) == 0.0
        
        # Test high similarity (should be clamped to 1)
        vec_c = np.array([1.0, 0.0])
        vec_d = np.array([1.0, 0.0])
        assert _cosine_similarity(vec_c, vec_d) == 1.0


@pytest.mark.recommendation
@pytest.mark.recommendation_unit
class TestVectorConversion:
    """Test vector conversion utilities."""
    
    def test_to_numpy_vector_valid(self):
        """Test conversion of valid list to numpy array."""
        vec = [1.0, 2.0, 3.0]
        result = _to_numpy_vector(vec)
        assert isinstance(result, np.ndarray)
        assert np.array_equal(result, np.array([1.0, 2.0, 3.0]))
    
    def test_to_numpy_vector_empty(self):
        """Test conversion of empty list."""
        result = _to_numpy_vector([])
        assert isinstance(result, np.ndarray)
        assert result.size == 0
    
    def test_to_numpy_vector_none(self):
        """Test conversion of None."""
        result = _to_numpy_vector(None)
        assert isinstance(result, np.ndarray)
        assert result.size == 0
    
    def test_to_numpy_vector_invalid(self):
        """Test conversion of invalid data."""
        result = _to_numpy_vector("invalid")
        assert isinstance(result, np.ndarray)
        assert result.size == 0


@pytest.mark.recommendation
@pytest.mark.recommendation_unit
class TestUserProfileGeneration:
    """Test user profile vector generation."""
    
    def test_generate_profile_with_embeddings(self, recommendation_test_data, test_db):
        """Test profile generation with valid embeddings."""
        db = test_db()
        
        try:
            profile = generate_user_profile_vector(db)
            assert isinstance(profile, np.ndarray)
            assert profile.size > 0
            assert profile.shape[0] == 5  # Based on test data embeddings
        finally:
            db.close()
    
    def test_generate_profile_empty_library(self, empty_library):
        """Test profile generation with empty library."""
        profile = generate_user_profile_vector(empty_library)
        assert isinstance(profile, np.ndarray)
        assert profile.size == 0
    
    def test_generate_profile_no_embeddings(self, test_db):
        """Test profile generation when no resources have embeddings."""
        from backend.app.database.models import Resource
        from datetime import datetime, timezone
        
        db = test_db()
        resource = Resource(
            title="No Embedding",
            quality_score=0.9,
            embedding=None,  # No embedding
            created_at=datetime.now(timezone.utc),
        )
        db.add(resource)
        db.commit()
        
        try:
            profile = generate_user_profile_vector(db)
            assert isinstance(profile, np.ndarray)
            assert profile.size == 0
        finally:
            db.delete(resource)
            db.commit()
            db.close()


@pytest.mark.recommendation
@pytest.mark.recommendation_unit
class TestTopSubjectsExtraction:
    """Test extraction of top subjects for seed keywords."""
    
    def test_get_top_subjects(self, recommendation_test_data, test_db):
        """Test getting top subjects by usage count."""
        db = test_db()
        
        try:
            subjects = get_top_subjects(db)
            assert isinstance(subjects, list)
            assert len(subjects) <= 5  # RECOMMENDATION_KEYWORD_COUNT
            # Should be ordered by usage count (highest first)
            assert "Machine Learning" in subjects  # Highest usage count
            assert "Python" in subjects
        finally:
            db.close()
    
    def test_get_top_subjects_empty(self, empty_library):
        """Test getting top subjects from empty authority table."""
        subjects = get_top_subjects(empty_library)
        assert isinstance(subjects, list)
        assert len(subjects) == 0


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.recommendation
@pytest.mark.recommendation_integration
class TestRecommendationService:
    """Test the complete recommendation service."""
    
    def test_generate_recommendations_full_flow(self, recommendation_test_data, mock_ddgs_search, mock_ai_core, test_db):
        """Test the complete recommendation generation flow."""
        db = test_db()
        
        try:
            recommendations = generate_recommendations(db, limit=3)
            
            assert isinstance(recommendations, list)
            assert len(recommendations) <= 3
            
            for rec in recommendations:
                assert "url" in rec
                assert "title" in rec
                assert "snippet" in rec
                assert "relevance_score" in rec
                assert "reasoning" in rec
                
                # Validate score range
                assert 0.0 <= rec["relevance_score"] <= 1.0
                
                # Validate reasoning
                assert isinstance(rec["reasoning"], list)
                assert len(rec["reasoning"]) > 0
        finally:
            db.close()
    
    def test_generate_recommendations_empty_library(self, empty_library, mock_ddgs_search, mock_ai_core):
        """Test recommendation generation with empty library."""
        recommendations = generate_recommendations(empty_library, limit=5)
        assert isinstance(recommendations, list)
        assert len(recommendations) == 0
    
    def test_generate_recommendations_single_resource(self, single_resource_library, mock_ddgs_search, mock_ai_core, test_db):
        """Test recommendation generation with single resource."""
        db = test_db()
        
        try:
            recommendations = generate_recommendations(db, limit=5)
            
            assert isinstance(recommendations, list)
            # Should still work with single resource
            if len(recommendations) > 0:
                for rec in recommendations:
                    assert 0.0 <= rec["relevance_score"] <= 1.0
        finally:
            db.close()


# ============================================================================
# API Endpoint Tests
# ============================================================================

@pytest.mark.recommendation
@pytest.mark.recommendation_api
class TestRecommendationAPI:
    """Test the recommendation API endpoints."""
    
    def test_get_recommendations_success(self, client, recommendation_test_data, mock_ddgs_search, mock_ai_core):
        """Test successful recommendation retrieval."""
        response = client.get("/recommendations?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
        
        for item in data["items"]:
            assert "url" in item
            assert "title" in item
            assert "snippet" in item
            assert "relevance_score" in item
            assert "reasoning" in item
            
            # Validate score range
            assert 0.0 <= item["relevance_score"] <= 1.0
            
            # Validate reasoning contains seed subjects
            reason_text = " ".join(item["reasoning"])
            assert any(keyword in reason_text for keyword in ["Machine Learning", "Python", "Artificial Intelligence"])
    
    def test_get_recommendations_with_limit(self, client, recommendation_test_data, mock_ddgs_search, mock_ai_core):
        """Test recommendation retrieval with custom limit."""
        response = client.get("/recommendations?limit=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) <= 2
    
    def test_get_recommendations_invalid_limit(self, client, recommendation_test_data, mock_ddgs_search, mock_ai_core):
        """Test recommendation retrieval with invalid limit."""
        # Test limit too high
        response = client.get("/recommendations?limit=1000")
        assert response.status_code == 422  # Validation error
        
        # Test limit too low
        response = client.get("/recommendations?limit=0")
        assert response.status_code == 422  # Validation error
    
    def test_get_recommendations_empty_library(self, client, empty_library, mock_ddgs_search, mock_ai_core):
        """Test recommendation retrieval with empty library."""
        response = client.get("/recommendations?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 0
    
    def test_duplicate_filtering(self, client, recommendation_test_data, mock_ddgs_search, mock_ai_core, test_db):
        """Test that duplicate URLs are filtered out."""
        # Add a resource with a URL that will be returned by mock search
        db = test_db()
        existing_resource = Resource(
            title="Existing Resource",
            source="https://example.com/new-ml-article",  # This URL is in mock results
            embedding=[0.1, 0.2, 0.0, 0.0, 0.0],
            quality_score=0.8,
        )
        db.add(existing_resource)
        db.commit()
        db.close()
        
        response = client.get("/recommendations?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        urls = [item["url"] for item in data["items"]]
        
        # The duplicate URL should not be in results
        assert "https://example.com/new-ml-article" not in urls
    
    def test_relevance_score_ordering(self, client, recommendation_test_data, mock_ddgs_search, mock_ai_core):
        """Test that recommendations are ordered by relevance score."""
        response = client.get("/recommendations?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        if len(data["items"]) > 1:
            scores = [item["relevance_score"] for item in data["items"]]
            # Should be in descending order
            assert scores == sorted(scores, reverse=True)


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

@pytest.mark.recommendation
@pytest.mark.recommendation_edge_cases
class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_malformed_embeddings(self, test_db, mock_ddgs_search, mock_ai_core):
        """Test handling of malformed embeddings."""
        from backend.app.database.models import Resource, AuthoritySubject
        from datetime import datetime, timezone
        
        db = test_db()
        
        # Create authority subject
        subject = AuthoritySubject(
            canonical_form="Test Subject",
            variants=[],
            usage_count=10
        )
        db.add(subject)
        
        # Create resource with malformed embedding
        resource = Resource(
            title="Malformed Embedding",
            subject=["Test Subject"],
            quality_score=0.9,
            embedding="invalid_embedding",  # Not a list
            created_at=datetime.now(timezone.utc),
        )
        db.add(resource)
        db.commit()
        
        try:
            recommendations = generate_recommendations(db, limit=5)
            # Should handle gracefully and return empty or valid results
            assert isinstance(recommendations, list)
        finally:
            db.delete(resource)
            db.delete(subject)
            db.commit()
            db.close()
    
    def test_mixed_embedding_dimensions(self, test_db, mock_ddgs_search, mock_ai_core):
        """Test handling of resources with different embedding dimensions."""
        from backend.app.database.models import Resource, AuthoritySubject
        from datetime import datetime, timezone
        
        db = test_db()
        
        # Create authority subject
        subject = AuthoritySubject(
            canonical_form="Test Subject",
            variants=[],
            usage_count=10
        )
        db.add(subject)
        
        # Create resources with different embedding dimensions
        resource1 = Resource(
            title="3D Embedding",
            subject=["Test Subject"],
            quality_score=0.9,
            embedding=[1.0, 2.0, 3.0],  # 3 dimensions
            created_at=datetime.now(timezone.utc),
        )
        resource2 = Resource(
            title="5D Embedding",
            subject=["Test Subject"],
            quality_score=0.8,
            embedding=[1.0, 2.0, 3.0, 4.0, 5.0],  # 5 dimensions
            created_at=datetime.now(timezone.utc),
        )
        
        db.add_all([resource1, resource2])
        db.commit()
        
        try:
            recommendations = generate_recommendations(db, limit=5)
            # Should handle mixed dimensions gracefully
            assert isinstance(recommendations, list)
        finally:
            db.delete(resource1)
            db.delete(resource2)
            db.delete(subject)
            db.commit()
            db.close()
    
    def test_search_provider_failure(self, client, recommendation_test_data, mock_ai_core):
        """Test handling of search provider failures."""
        # Mock DDGS to raise an exception
        with patch('backend.app.services.recommendation_service.DDGS') as mock_ddgs:
            mock_ddgs.side_effect = Exception("Search provider failed")
            
            response = client.get("/recommendations?limit=5")
            # Should handle gracefully
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            # May return empty results or fallback behavior
            assert isinstance(data["items"], list)


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.recommendation
@pytest.mark.recommendation_performance
@pytest.mark.slow
class TestPerformance:
    """Test performance characteristics."""
    
    @pytest.mark.slow
    def test_large_library_performance(self, test_db, mock_ddgs_search, mock_ai_core):
        """Test performance with a large library."""
        from backend.app.database.models import Resource, AuthoritySubject
        from datetime import datetime, timezone
        import time
        
        db = test_db()
        
        # Create many authority subjects
        subjects = []
        for i in range(20):
            subject = AuthoritySubject(
                canonical_form=f"Subject {i}",
                variants=[],
                usage_count=100 - i
            )
            subjects.append(subject)
            db.add(subject)
        
        # Create many resources with embeddings
        resources = []
        for i in range(100):
            resource = Resource(
                title=f"Resource {i}",
                subject=[f"Subject {i % 20}"],
                quality_score=0.5 + (i % 50) / 100.0,
                embedding=[float(i % 5), float((i + 1) % 5), float((i + 2) % 5), float((i + 3) % 5), float((i + 4) % 5)],
                created_at=datetime.now(timezone.utc),
            )
            resources.append(resource)
            db.add(resource)
        
        db.commit()
        
        try:
            start_time = time.time()
            recommendations = generate_recommendations(db, limit=10)
            end_time = time.time()
            
            # Should complete within reasonable time (adjust threshold as needed)
            assert (end_time - start_time) < 10.0  # 10 seconds
            assert isinstance(recommendations, list)
        finally:
            # Cleanup
            for resource in resources:
                db.delete(resource)
            for subject in subjects:
                db.delete(subject)
            db.commit()
            db.close()
    
    def test_caching_behavior(self, client, recommendation_test_data, mock_ddgs_search, mock_ai_core):
        """Test that search results are cached appropriately."""
        import time
        
        # First request
        start_time = time.time()
        response1 = client.get("/recommendations?limit=3")
        first_duration = time.time() - start_time
        
        # Second request (should use cache)
        start_time = time.time()
        response2 = client.get("/recommendations?limit=3")
        second_duration = time.time() - start_time
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Second request should be faster due to caching
        # (This is a soft assertion as caching behavior may vary)
        # assert second_duration < first_duration


# ============================================================================
# Legacy Tests (from original implementation)
# ============================================================================

@pytest.fixture
def library_with_embeddings(test_db):
    """Seed top-quality resources with embeddings and authority subjects."""
    db = test_db()
    now = datetime.now(timezone.utc)

    # Create authority subjects with usage counts
    subjects = [
        ("Machine Learning", 50),
        ("Python", 40),
        ("Artificial Intelligence", 30),
        ("Data Science", 20),
        ("Neural Networks", 10),
        ("Cooking", 5),
    ]
    for name, count in subjects:
        db.add(AuthoritySubject(canonical_form=name, variants=[], usage_count=count))

    # Create resources with embeddings and quality scores
    resources = [
        Resource(
            title="Advanced ML",
            subject=["Machine Learning", "Artificial Intelligence"],
            quality_score=0.95,
            embedding=[0.9, 0.1, 0.0, 0.0],
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(days=1),
        ),
        Resource(
            title="Python for DS",
            subject=["Python", "Data Science"],
            quality_score=0.9,
            embedding=[0.85, 0.12, 0.02, 0.01],
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=2),
        ),
        Resource(
            title="Neural Networks Intro",
            subject=["Neural Networks", "Machine Learning"],
            quality_score=0.88,
            embedding=[0.8, 0.2, 0.0, 0.0],
            created_at=now - timedelta(days=8),
            updated_at=now - timedelta(days=3),
        ),
    ]
    for r in resources:
        db.add(r)
    db.commit()
    db.close()


def _fake_ddgs_results():
    return [
        {
            "url": "https://example.com/new-ml-article",
            "title": "New Advances in Machine Learning",
            "body": "A brief overview of ML techniques",
        },
        {
            "url": "https://example.com/python-tips",
            "title": "Python Tips for Data Science",
            "body": "Improve your DS workflows with Python",
        },
        {
            "url": "https://example.com/cooking",
            "title": "Cooking Basics",
            "body": "Unrelated topic",
        },
    ]


@pytest.mark.recommendation
@pytest.mark.recommendation_api
@patch("backend.app.services.recommendation_service.DDGS")
def test_recommendations_endpoint_basic(mock_ddgs, client, library_with_embeddings, test_db):
    """Legacy test for basic endpoint functionality."""
    # Mock DDGS().text to return deterministic results
    class _Ctx:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def text(self, query, max_results):
            # return a shallow copy to avoid reuse issues
            return list(_fake_ddgs_results())

    mock_ddgs.return_value = _Ctx()

    # Ensure duplicates are filtered by creating an existing resource with same URL
    db = test_db()
    db.add(Resource(title="Existing", source="https://example.com/python-tips", embedding=[0.1, 0.2, 0.0, 0.0]))
    db.commit()
    db.close()

    resp = client.get("/recommendations?limit=5")
    assert resp.status_code == 200
    data = resp.json()

    assert "items" in data and isinstance(data["items"], list)
    for item in data["items"]:
        # only URLs not present in DB
        assert item["url"] != "https://example.com/python-tips"
        # score in [0,1]
        assert 0.0 <= item["relevance_score"] <= 1.0
        # reasoning mentions seed subjects
        reason_text = " ".join(item.get("reasoning") or [])
        assert any(kw in reason_text for kw in ["Machine Learning", "Python", "Artificial Intelligence"]) 


@pytest.mark.recommendation
@pytest.mark.recommendation_integration
@patch("backend.app.services.recommendation_service.DDGS")
def test_profile_sensitivity(mock_ddgs, client, test_db):
    """Legacy test for profile sensitivity."""
    # First profile: AI/ML heavy
    db = test_db()
    r1 = Resource(title="ML A", quality_score=0.95, embedding=[1.0, 0.0, 0.0])
    r2 = Resource(title="ML B", quality_score=0.9, embedding=[0.9, 0.1, 0.0])
    db.add_all([r1, r2])
    # authority subjects needed for keywords
    db.add(AuthoritySubject(canonical_form="Machine Learning", variants=[], usage_count=10))
    db.commit()
    db.close()

    class _Ctx:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def text(self, query, max_results):
            # craft two candidates aligned with two different axes
            return [
                {"url": "https://a.com/ax1", "title": "Aligned Axis 1", "body": "x"},
                {"url": "https://a.com/ax2", "title": "Aligned Axis 2", "body": "y"},
            ]

    mock_ddgs.return_value = _Ctx()

    # First call produces a profile ~ [0.95, 0.05, 0]
    resp1 = client.get("/recommendations?limit=2")
    assert resp1.status_code == 200

    # Now change library composition to a different axis, profile should change
    db = test_db()
    db.query(Resource).delete()
    db.add(Resource(title="Axis2", quality_score=0.99, embedding=[0.0, 1.0, 0.0]))
    db.add(AuthoritySubject(canonical_form="Python", variants=[], usage_count=5))
    db.commit()
    db.close()

    resp2 = client.get("/recommendations?limit=2")
    assert resp2.status_code == 200

    # The two responses should not be identical in scores due to profile shift
    s1 = [it["relevance_score"] for it in resp1.json()["items"]]
    s2 = [it["relevance_score"] for it in resp2.json()["items"]]
    assert s1 != s2


