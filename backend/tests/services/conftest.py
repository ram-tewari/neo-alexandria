"""
Shared fixtures for service layer tests.

This module provides fixtures that are shared across multiple service test files
to avoid duplication and ensure consistency.
"""

import pytest
from datetime import datetime, timedelta, timezone
from backend.app.database.models import Resource


@pytest.fixture
def sample_resources(test_db):
    """
    Create sample resources for search and service testing.
    
    Creates a diverse set of resources with different languages, types,
    classifications, and quality scores for comprehensive testing.
    
    Args:
        test_db: Test database fixture from main conftest.py
        
    Returns:
        List of resource IDs (as strings)
    """
    db = test_db()
    now = datetime.now(timezone.utc)
    
    resources = [
        Resource(
            title="Introduction to Machine Learning",
            description="A comprehensive guide to ML algorithms and AI techniques",
            language="en",
            type="article",
            classification_code="006",
            subject=["Machine Learning", "Artificial Intelligence"],
            read_status="unread",
            quality_score=0.8,
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=5),
        ),
        Resource(
            title="Deep Learning with Python",
            description="Neural networks and deep learning frameworks",
            language="en",
            type="book",
            classification_code="006",
            subject=["Deep Learning", "Python", "Neural Networks"],
            read_status="in_progress",
            quality_score=0.9,
            created_at=now - timedelta(days=20),
            updated_at=now - timedelta(days=2),
        ),
        Resource(
            title="Spanish Linguistics Overview",
            description="Morphology and syntax in Spanish language",
            language="es",
            type="book",
            classification_code="400",
            subject=["Linguistics", "Spanish Language"],
            read_status="completed",
            quality_score=0.75,
            created_at=now - timedelta(days=30),
            updated_at=now - timedelta(days=15),
        ),
        Resource(
            title="Natural Language Processing Basics",
            description="Text processing, tokenization, and NLP techniques",
            language="en",
            type="article",
            classification_code="006",
            subject=["Natural Language Processing", "Machine Learning"],
            read_status="unread",
            quality_score=0.7,
            created_at=now - timedelta(days=15),
            updated_at=now - timedelta(days=1),
        ),
    ]
    
    for resource in resources:
        db.add(resource)
    db.commit()
    
    resource_ids = [str(r.id) for r in resources]
    db.close()
    return resource_ids
