"""
Neo Alexandria 2.0 - Phase 5.5 Recommendation System Test Suite

This module provides unit testing for the recommendation service utility functions.

Related files:
- app/services/recommendation_service.py: Core recommendation logic being tested

Test Categories:
- Unit Tests: Core functions (cosine similarity, vector conversion, profile generation)

Test Markers:
- @pytest.mark.recommendation: All recommendation tests
- @pytest.mark.recommendation_unit: Unit tests for components

Usage:
- Run all tests: pytest -m recommendation
- Run specific category: pytest -m recommendation_unit
- Run with coverage: pytest -m recommendation --cov=app.services.recommendation_service
"""

from __future__ import annotations

import pytest
import numpy as np
from datetime import datetime, timezone

from backend.app.database.models import Resource, AuthoritySubject
from backend.app.services.recommendation_service import (
    generate_user_profile_vector,
    get_top_subjects,
    _cosine_similarity,
    _to_numpy_vector,
)


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


