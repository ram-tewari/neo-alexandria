"""
Fixtures for Phase 11 Recommendations integration tests.

Provides fixtures specific to recommendation integration testing.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import Mock

from backend.app.domain.recommendation import Recommendation
# Import from old location for backward compatibility
try:
    from backend.app.services.recommendation_service import RecommendationService
except ImportError:
    # Service may have been moved to modules - use mock spec instead
    RecommendationService = type('RecommendationService', (), {})


@pytest.fixture
def recommendation_test_user(db_session):
    """
    Create a test user for recommendation integration testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        User with profile
    """
    from backend.app.database.models import User, UserProfile
    
    user = User(
        id=uuid4(),
        email="recommendation-test@example.com",
        username="rec_test_user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create user profile
    profile = UserProfile(
        user_id=user.id,
        diversity_preference=0.5,
        novelty_preference=0.3,
        recency_bias=0.5,
        total_interactions=0
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    
    yield {"user": user, "profile": profile}
    
    # Cleanup
    db_session.delete(profile)
    db_session.delete(user)
    db_session.commit()


@pytest.fixture
def recommendation_test_resources_with_embeddings(db_session):
    """
    Create test resources with embeddings for recommendation testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        List of resources with embeddings
    """
    from backend.app.database.models import Resource
    
    resources = []
    test_data = [
        {
            "title": "Advanced Machine Learning",
            "description": "Deep dive into ML algorithms",
            "subject": ["Machine Learning", "AI"],
            "quality_overall": 0.9,
            "embedding": [0.9] * 768
        },
        {
            "title": "Python Programming Guide",
            "description": "Comprehensive Python tutorial",
            "subject": ["Python", "Programming"],
            "quality_overall": 0.85,
            "embedding": [0.8] * 768
        },
        {
            "title": "Data Science Handbook",
            "description": "Complete guide to data science",
            "subject": ["Data Science", "Statistics"],
            "quality_overall": 0.88,
            "embedding": [0.85] * 768
        }
    ]
    
    for i, data in enumerate(test_data):
        resource = Resource(
            id=uuid4(),
            title=data["title"],
            description=data["description"],
            subject=data["subject"],
            source=f"https://example.com/rec-test-{i+1}",
            type="article",
            language="en",
            quality_overall=data["quality_overall"],
            quality_score=data["quality_overall"],
            embedding=data["embedding"],
            publication_year=2020 + i,
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
def sample_recommendation_domain_object() -> Recommendation:
    """
    Create a sample Recommendation domain object for testing.
    
    Returns:
        Recommendation with typical values
    """
    from backend.app.domain.recommendation import RecommendationScore
    
    recommendation_score = RecommendationScore(
        score=0.88,
        confidence=0.82,
        rank=1
    )
    
    return Recommendation(
        resource_id=str(uuid4()),
        user_id=str(uuid4()),
        recommendation_score=recommendation_score,
        strategy="hybrid",
        reason="Recommended based on your interest in machine learning",
        metadata={
            "content_similarity": 0.85,
            "graph_score": 0.78,
            "quality_score": 0.9,
            "recency_boost": 0.05
        }
    )


@pytest.fixture
def sample_recommendations_list() -> list:
    """
    Create a list of Recommendation domain objects for testing.
    
    Returns:
        List of Recommendation objects
    """
    from backend.app.domain.recommendation import RecommendationScore
    
    recommendations = []
    strategies = ["content", "graph", "hybrid"]
    
    for i in range(3):
        recommendation_score = RecommendationScore(
            score=0.9 - (i * 0.05),
            confidence=0.85 - (i * 0.05),
            rank=i + 1
        )
        
        rec = Recommendation(
            resource_id=str(uuid4()),
            user_id=str(uuid4()),
            recommendation_score=recommendation_score,
            strategy=strategies[i],
            reason=f"Recommendation {i+1} based on {strategies[i]} strategy",
            metadata={
                "content_similarity": 0.85 - (i * 0.05),
                "quality_score": 0.9 - (i * 0.02)
            }
        )
        recommendations.append(rec)
    
    return recommendations


@pytest.fixture
def mock_recommendation_service_with_domain_objects(sample_recommendations_list):
    """
    Create a mock RecommendationService that returns domain objects.
    
    Args:
        sample_recommendations_list: List of Recommendation fixtures
        
    Returns:
        Mock RecommendationService
    """
    mock_service = Mock(spec=RecommendationService)
    
    # Configure mock to return Recommendation domain objects
    mock_service.get_recommendations.return_value = sample_recommendations_list
    mock_service.generate_recommendation.return_value = sample_recommendations_list[0]
    mock_service.get_personalized_recommendations.return_value = sample_recommendations_list
    
    return mock_service


@pytest.fixture
def user_interactions_for_recommendations(db_session, recommendation_test_user, recommendation_test_resources_with_embeddings):
    """
    Create user interactions for recommendation testing.
    
    Args:
        db_session: Database session fixture
        recommendation_test_user: User fixture
        recommendation_test_resources_with_embeddings: Resources fixture
        
    Returns:
        List of user interactions
    """
    from backend.app.database.models import UserInteraction
    
    user = recommendation_test_user["user"]
    resources = recommendation_test_resources_with_embeddings
    
    interactions = []
    for i, resource in enumerate(resources[:2]):  # Interact with first 2 resources
        interaction = UserInteraction(
            user_id=user.id,
            resource_id=resource.id,
            interaction_type="view",
            interaction_strength=0.5 + (i * 0.1),
            dwell_time=30 + (i * 10),
            scroll_depth=0.7 + (i * 0.1),
            is_positive=1,
            confidence=0.6,
            interaction_timestamp=datetime.utcnow()
        )
        db_session.add(interaction)
        interactions.append(interaction)
    
    db_session.commit()
    
    for interaction in interactions:
        db_session.refresh(interaction)
    
    yield interactions
    
    # Cleanup
    for interaction in interactions:
        db_session.delete(interaction)
    db_session.commit()
