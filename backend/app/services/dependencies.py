"""
Neo Alexandria 2.0 - Service Dependencies with Caching

This module provides cached service dependencies to avoid expensive initialization
on every request. Services like AI models, classifiers, and authority control
are cached using @lru_cache for optimal performance.

Related files:
- app/services/ai_core.py: AI processing service
- app/services/authority_service.py: Authority control service
- app/services/classification_service.py: Classification service
- app/services/quality_service.py: Quality analysis service
"""

from functools import lru_cache

from .ai_core import AICore
from .authority_service import AuthorityControl
from .classification_service import PersonalClassification
from .quality_service import ContentQualityAnalyzer


@lru_cache(maxsize=1)
def get_ai_core() -> AICore:
    """
    Get cached AI core service instance.
    
    The AI core service is expensive to initialize due to model loading,
    so we cache it as a singleton.
    
    Returns:
        AICore: Cached AI service instance
    """
    return AICore()


@lru_cache(maxsize=1)
def get_classification_service() -> PersonalClassification:
    """
    Get cached classification service instance.
    
    The classification service is stateless and can be safely cached.
    
    Returns:
        PersonalClassification: Cached classification service instance
    """
    return PersonalClassification()


@lru_cache(maxsize=1)
def get_quality_analyzer() -> ContentQualityAnalyzer:
    """
    Get cached quality analyzer service instance.
    
    The quality analyzer is stateless and can be safely cached.
    
    Returns:
        ContentQualityAnalyzer: Cached quality analyzer instance
    """
    return ContentQualityAnalyzer()


def get_authority_control(db_session) -> AuthorityControl:
    """
    Get authority control service instance.
    
    Note: Authority control requires a database session, so it cannot be
    cached globally. Each request gets a fresh instance with the current
    database session.
    
    Args:
        db_session: Database session for authority operations
        
    Returns:
        AuthorityControl: Authority control service instance
    """
    return AuthorityControl(db_session)
