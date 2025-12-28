"""
Curation Module

This module provides content review queue management and batch operations
for maintaining high-quality content in the knowledge base.

Public Interface:
- curation_router: FastAPI router with curation endpoints
- CurationService: Business logic for curation operations
- Schema classes: Request/response models for curation operations

Events Emitted:
- curation.reviewed: When an item is reviewed
- curation.approved: When content is approved
- curation.rejected: When content is rejected

Events Subscribed:
- quality.outlier_detected: Add items to review queue
"""

__version__ = "1.0.0"
__domain__ = "curation"

from .router import curation_router
from .service import CurationService
from .schema import (
    ReviewQueueParams,
    ReviewQueueResponse,
    BatchUpdateRequest,
    BatchUpdateResult,
    QualityAnalysisResponse,
    LowQualityResponse,
    BulkQualityCheckRequest,
)

__all__ = [
    "curation_router",
    "CurationService",
    "ReviewQueueParams",
    "ReviewQueueResponse",
    "BatchUpdateRequest",
    "BatchUpdateResult",
    "QualityAnalysisResponse",
    "LowQualityResponse",
    "BulkQualityCheckRequest",
]
