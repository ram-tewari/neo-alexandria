"""
Shared fixtures for Phase 7 Collections unit tests.

This module provides fixtures that are shared across multiple Phase 7 collections
unit test files to avoid duplication and ensure consistency.
"""

import pytest


@pytest.fixture
def db_session(test_db):
    """
    Create a database session for Phase 7 collections unit tests.
    
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
    try:
        yield db
    finally:
        db.close()
