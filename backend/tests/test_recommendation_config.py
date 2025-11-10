"""
Neo Alexandria 2.0 - Phase 5.5 Recommendation System Test Configuration

This module provides test configuration, utilities, and helpers specifically
for testing the recommendation system functionality. It includes test markers,
fixtures, and assertion utilities to support comprehensive testing.

Related files:
- test_phase55_recommendations.py: Main test suite that uses these utilities
- conftest.py: Core test fixtures and configuration
- pytest.ini: Pytest configuration with recommendation markers

Features:
- Test markers for organized test execution
- Helper utilities for recommendation testing
- Mock data generators for consistent test scenarios
- Performance testing utilities and timers
- Assertion helpers for recommendation validation
- Test data fixtures for various scenarios

Test Markers:
- recommendation: All recommendation system tests
- recommendation_unit: Unit tests for individual components
- recommendation_integration: Integration tests for complete flows
- recommendation_api: API endpoint tests
- recommendation_performance: Performance and scalability tests
- recommendation_edge_cases: Error handling and boundary tests

Utilities:
- RecommendationTestHelper: Core testing utilities and validators
- Mock data generators: Deterministic test data creation
- Performance timers: Benchmarking and timing utilities
- Assertion helpers: Specialized validation functions

Usage:
- Import utilities in test files for consistent testing patterns
- Use markers to organize and filter test execution
- Leverage helper functions for common test scenarios
- Apply assertion helpers for recommendation-specific validation
"""

import pytest
from typing import Dict, List, Any


# ============================================================================
# Test Markers and Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with recommendation-specific markers."""
    config.addinivalue_line(
        "markers", "recommendation: Tests for the recommendation system"
    )
    config.addinivalue_line(
        "markers", "recommendation_unit: Unit tests for recommendation components"
    )
    config.addinivalue_line(
        "markers", "recommendation_integration: Integration tests for recommendation system"
    )
    config.addinivalue_line(
        "markers", "recommendation_api: API endpoint tests for recommendations"
    )
    config.addinivalue_line(
        "markers", "recommendation_performance: Performance tests for recommendations"
    )
    config.addinivalue_line(
        "markers", "recommendation_edge_cases: Edge case and error handling tests"
    )


# ============================================================================
# Test Utilities
# ============================================================================

class RecommendationTestHelper:
    """Helper class for recommendation testing utilities."""
    
    @staticmethod
    def create_mock_embedding(text: str, dimensions: int = 5) -> List[float]:
        """Create a deterministic mock embedding for testing."""
        import hashlib
        
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        embedding = []
        for i in range(dimensions):
            val = (hash_bytes[i % len(hash_bytes)] - 128) / 128.0
            embedding.append(val)
        
        return embedding
    
    @staticmethod
    def create_mock_search_results(keyword: str, count: int = 5) -> List[Dict[str, str]]:
        """Create mock search results based on keyword."""
        base_results = [
            {
                "url": f"https://example.com/{keyword.lower().replace(' ', '-')}-article-1",
                "title": f"Article about {keyword}",
                "body": f"Comprehensive guide to {keyword} concepts and applications",
            },
            {
                "url": f"https://example.com/{keyword.lower().replace(' ', '-')}-tutorial",
                "title": f"{keyword} Tutorial",
                "body": f"Learn {keyword} from scratch with practical examples",
            },
            {
                "url": f"https://example.com/{keyword.lower().replace(' ', '-')}-research",
                "title": f"Latest {keyword} Research",
                "body": f"Cutting-edge research and developments in {keyword}",
            },
            {
                "url": f"https://example.com/{keyword.lower().replace(' ', '-')}-guide",
                "title": f"Complete {keyword} Guide",
                "body": f"Everything you need to know about {keyword}",
            },
            {
                "url": f"https://example.com/{keyword.lower().replace(' ', '-')}-best-practices",
                "title": f"{keyword} Best Practices",
                "body": f"Industry best practices and tips for {keyword}",
            },
        ]
        
        return base_results[:count]
    
    @staticmethod
    def validate_recommendation_structure(recommendation: Dict[str, Any]) -> bool:
        """Validate that a recommendation has the correct structure."""
        required_fields = ["url", "title", "snippet", "relevance_score", "reasoning"]
        
        for field in required_fields:
            if field not in recommendation:
                return False
        
        # Validate types
        if not isinstance(recommendation["url"], str):
            return False
        if not isinstance(recommendation["title"], str):
            return False
        if not isinstance(recommendation["snippet"], str):
            return False
        if not isinstance(recommendation["relevance_score"], (int, float)):
            return False
        if not isinstance(recommendation["reasoning"], list):
            return False
        
        # Validate score range
        if not (0.0 <= recommendation["relevance_score"] <= 1.0):
            return False
        
        return True
    
    @staticmethod
    def validate_recommendation_list(recommendations: List[Dict[str, Any]]) -> bool:
        """Validate a list of recommendations."""
        if not isinstance(recommendations, list):
            return False
        
        for rec in recommendations:
            if not RecommendationTestHelper.validate_recommendation_structure(rec):
                return False
        
        # Check ordering (should be descending by relevance_score)
        if len(recommendations) > 1:
            scores = [rec["relevance_score"] for rec in recommendations]
            if scores != sorted(scores, reverse=True):
                return False
        
        return True


# ============================================================================
# Fixture Utilities
# ============================================================================

@pytest.fixture
def recommendation_helper():
    """Provide recommendation test helper utilities."""
    return RecommendationTestHelper


@pytest.fixture
def mock_embedding_generator():
    """Mock embedding generator that creates deterministic embeddings."""
    def generate_embedding(text: str) -> List[float]:
        return RecommendationTestHelper.create_mock_embedding(text)
    
    return generate_embedding


@pytest.fixture
def mock_search_provider():
    """Mock search provider that returns deterministic results."""
    def search(keyword: str, max_results: int = 10) -> List[Dict[str, str]]:
        return RecommendationTestHelper.create_mock_search_results(keyword, max_results)
    
    return search


# ============================================================================
# Test Data Generators
# ============================================================================

@pytest.fixture
def sample_authority_subjects():
    """Sample authority subjects for testing."""
    return [
        ("Machine Learning", 100),
        ("Python", 80),
        ("Artificial Intelligence", 60),
        ("Data Science", 40),
        ("Neural Networks", 30),
        ("Deep Learning", 25),
        ("Natural Language Processing", 20),
        ("Computer Vision", 15),
        ("Statistics", 10),
        ("Mathematics", 5),
    ]


@pytest.fixture
def sample_resources_data():
    """Sample resource data for testing."""
    return [
        {
            "title": "Advanced Machine Learning Techniques",
            "description": "Comprehensive guide to modern ML algorithms",
            "subject": ["Machine Learning", "Artificial Intelligence"],
            "quality_score": 0.95,
            "embedding": [0.9, 0.1, 0.0, 0.0, 0.0],
        },
        {
            "title": "Python for Data Science",
            "description": "Learn Python programming for data analysis",
            "subject": ["Python", "Data Science"],
            "quality_score": 0.92,
            "embedding": [0.8, 0.2, 0.0, 0.0, 0.0],
        },
        {
            "title": "Deep Learning Fundamentals",
            "description": "Introduction to neural networks and deep learning",
            "subject": ["Deep Learning", "Neural Networks"],
            "quality_score": 0.88,
            "embedding": [0.7, 0.3, 0.0, 0.0, 0.0],
        },
        {
            "title": "Natural Language Processing Basics",
            "description": "Text processing and language models",
            "subject": ["Natural Language Processing", "Machine Learning"],
            "quality_score": 0.85,
            "embedding": [0.6, 0.4, 0.0, 0.0, 0.0],
        },
        {
            "title": "Computer Vision Applications",
            "description": "Image recognition and computer vision",
            "subject": ["Computer Vision", "Deep Learning"],
            "quality_score": 0.82,
            "embedding": [0.5, 0.5, 0.0, 0.0, 0.0],
        },
    ]


# ============================================================================
# Performance Testing Utilities
# ============================================================================

@pytest.fixture
def performance_timer():
    """Utility for measuring test performance."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def duration(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


# ============================================================================
# Test Assertion Helpers
# ============================================================================

def assert_recommendation_quality(recommendations: List[Dict[str, Any]], min_score: float = 0.0):
    """Assert that recommendations meet quality standards."""
    assert isinstance(recommendations, list), "Recommendations should be a list"
    
    for rec in recommendations:
        assert RecommendationTestHelper.validate_recommendation_structure(rec), \
            f"Invalid recommendation structure: {rec}"
        assert rec["relevance_score"] >= min_score, \
            f"Recommendation score {rec['relevance_score']} below minimum {min_score}"


def assert_no_duplicate_urls(recommendations: List[Dict[str, Any]]):
    """Assert that there are no duplicate URLs in recommendations."""
    urls = [rec["url"] for rec in recommendations]
    assert len(urls) == len(set(urls)), "Duplicate URLs found in recommendations"


def assert_reasoning_contains_keywords(recommendations: List[Dict[str, Any]], expected_keywords: List[str]):
    """Assert that reasoning contains expected keywords."""
    for rec in recommendations:
        reason_text = " ".join(rec["reasoning"])
        assert any(keyword in reason_text for keyword in expected_keywords), \
            f"Expected keywords {expected_keywords} not found in reasoning: {reason_text}"


def assert_scores_ordered(recommendations: List[Dict[str, Any]]):
    """Assert that recommendations are ordered by relevance score (descending)."""
    if len(recommendations) > 1:
        scores = [rec["relevance_score"] for rec in recommendations]
        assert scores == sorted(scores, reverse=True), \
            "Recommendations not ordered by relevance score"
