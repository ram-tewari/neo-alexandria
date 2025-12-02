"""
Fixtures for Phase 3 Search integration tests.

Provides fixtures specific to search integration testing.
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock

from backend.app.domain.search import SearchResult
# Import from new module location
try:
    from backend.app.modules.search import SearchService
except ImportError:
    # Fallback to old location for backward compatibility
    from backend.app.services.search_service import SearchService


@pytest.fixture
def search_test_resources(db_session):
    """
    Create test resources for search integration testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        List of resources with embeddings for search
    """
    from backend.app.database.models import Resource
    from datetime import datetime, timezone, timedelta
    
    now = datetime.now(timezone.utc)
    resources = []
    
    test_data = [
        {
            "title": "Machine Learning Fundamentals",
            "description": "Introduction to machine learning concepts and algorithms",
            "subject": ["Machine Learning", "Artificial Intelligence"],
            "quality_score": 0.9,
            "embedding": [0.9, 0.1, 0.0, 0.0, 0.0]
        },
        {
            "title": "Deep Learning with Python",
            "description": "Practical guide to deep learning using Python",
            "subject": ["Deep Learning", "Python", "Neural Networks"],
            "quality_score": 0.85,
            "embedding": [0.8, 0.2, 0.0, 0.0, 0.0]
        },
        {
            "title": "Natural Language Processing",
            "description": "Text processing and language understanding",
            "subject": ["NLP", "Machine Learning", "Linguistics"],
            "quality_score": 0.8,
            "embedding": [0.7, 0.3, 0.0, 0.0, 0.0]
        },
        {
            "title": "Computer Vision Applications",
            "description": "Image recognition and computer vision techniques",
            "subject": ["Computer Vision", "Deep Learning"],
            "quality_score": 0.75,
            "embedding": [0.6, 0.4, 0.0, 0.0, 0.0]
        }
    ]
    
    for i, data in enumerate(test_data):
        resource = Resource(
            id=uuid4(),
            title=data["title"],
            description=data["description"],
            subject=data["subject"],
            source=f"https://example.com/search-test-{i+1}",
            type="article",
            language="en",
            classification_code="006",
            quality_score=data["quality_score"],
            quality_overall=data["quality_score"],
            embedding=data["embedding"],
            date_created=now - timedelta(days=10-i),
            date_modified=now - timedelta(days=5-i),
            ingestion_status="completed"
        )
        db_session.add(resource)
        resources.append(resource)
    
    db_session.commit()
    
    for resource in resources:
        db_session.refresh(resource)
    
    yield resources
    
    # Cleanup
    for resource in resources:
        db_session.delete(resource)
    db_session.commit()


@pytest.fixture
def sample_search_result_domain_object() -> SearchResult:
    """
    Create a sample SearchResult domain object for testing.
    
    Returns:
        SearchResult with typical search result
    """
    return SearchResult(
        resource_id=str(uuid4()),
        score=0.92,
        rank=1,
        title="Machine Learning Fundamentals",
        search_method="hybrid",
        metadata={
            "snippet": "Introduction to machine learning concepts...",
            "query": "machine learning"
        }
    )


@pytest.fixture
def mock_search_service_with_domain_objects(sample_search_result_domain_object):
    """
    Create a mock SearchService that returns domain objects.
    
    Args:
        sample_search_result_domain_object: SearchResult fixture
        
    Returns:
        Mock SearchService
    """
    mock_service = Mock(spec=SearchService)
    
    # Configure mock to return list of SearchResult domain objects
    mock_service.search.return_value = [sample_search_result_domain_object]
    mock_service.hybrid_search.return_value = [sample_search_result_domain_object]
    mock_service.semantic_search.return_value = [sample_search_result_domain_object]
    mock_service.keyword_search.return_value = [sample_search_result_domain_object]
    
    return mock_service
