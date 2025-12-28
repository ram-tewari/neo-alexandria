"""
Annotations Module - Text highlights and notes on resources.

This module provides functionality for creating, managing, and searching
annotations on resource content.

Public Interface:
- annotations_router: FastAPI router with all annotation endpoints
- AnnotationService: Business logic for annotation management
- Schema classes: Pydantic models for API validation

Version: 1.0.0
Domain: annotations
"""

from .router import router as annotations_router
from .service import AnnotationService
from .schema import (
    AnnotationCreate,
    AnnotationUpdate,
    AnnotationResponse,
    AnnotationListResponse,
    AnnotationSearchResult,
    AnnotationSearchResponse,
)

__version__ = "1.0.0"
__domain__ = "annotations"

__all__ = [
    "annotations_router",
    "AnnotationService",
    "AnnotationCreate",
    "AnnotationUpdate",
    "AnnotationResponse",
    "AnnotationListResponse",
    "AnnotationSearchResult",
    "AnnotationSearchResponse",
]

