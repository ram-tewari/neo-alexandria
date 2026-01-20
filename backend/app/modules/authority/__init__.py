"""
Authority Module

This module provides subject authority control and classification tree management.
It handles normalization of subjects, creators, and publishers with canonical forms,
variants, and usage tracking.

Public Interface:
- authority_router: FastAPI router for authority endpoints
- AuthorityControl: Service for authority control operations
- PersonalClassification: Service for classification tree management
- Schema classes: SubjectSuggestionResponse, ClassificationTreeNode, ClassificationTreeResponse

Events Emitted:
- None (read-only module)

Events Subscribed:
- None (read-only module)
"""

__version__ = "1.0.0"
__domain__ = "authority"

from .router import router as authority_router
from .service import AuthorityControl, PersonalClassification
from .schema import (
    SubjectSuggestionResponse,
    ClassificationTreeNode,
    ClassificationTreeResponse,
)

__all__ = [
    "authority_router",
    "AuthorityControl",
    "PersonalClassification",
    "SubjectSuggestionResponse",
    "ClassificationTreeNode",
    "ClassificationTreeResponse",
]
