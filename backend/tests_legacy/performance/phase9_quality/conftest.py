"""
Shared fixtures for Phase 9 Quality performance tests.

This module provides fixtures specific to quality performance testing.
"""

import pytest
from sqlalchemy.orm import Session
from backend.app.services.quality_service import QualityService


@pytest.fixture
def quality_service(db_session: Session):
    """
    Create a QualityService instance for performance testing.

    Args:
        db_session: Database session fixture

    Returns:
        QualityService instance configured for performance testing
    """
    return QualityService(db_session)
