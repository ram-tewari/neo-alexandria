"""
Shared fixtures for Phase 9 Quality unit tests.

This module provides fixtures that are shared across multiple Phase 9 quality
unit test files to avoid duplication and ensure consistency.
"""

import pytest
from sqlalchemy.orm import Session
from backend.app.services.quality_service import QualityService


@pytest.fixture
def db_session(test_db):
    """
    Create a database session for Phase 9 quality unit tests.
    
    This fixture provides a database session that is properly cleaned up
    after each test to ensure test isolation.
    
    Args:
        test_db: Test database fixture from main conftest.py
        
    Returns:
        SQLAlchemy Session
        
    Yields:
        Database session for the test
    """
    db = test_db()
    yield db
    db.close()


@pytest.fixture
def quality_service(db_session: Session):
    """
    Create a QualityService instance for testing.
    
    Provides a properly configured QualityService with a test database
    session for unit testing quality assessment functionality.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        QualityService instance configured for testing
    """
    return QualityService(db_session)
