"""
Taxonomy Module

This module handles ML-based classification and taxonomy management for Neo Alexandria 2.0.
It provides automatic resource classification, taxonomy tree management, and active learning
capabilities.

Public Interface:
    - taxonomy_router: FastAPI router with all taxonomy endpoints
    - TaxonomyService: Core taxonomy management service
    - MLClassificationService: ML-based classification service
    - ClassificationService: Classification coordination service
    - Schema classes for requests/responses

Events Emitted:
    - resource.classified: When a resource is classified
    - taxonomy.node_created: When a taxonomy node is added
    - taxonomy.model_trained: When ML model is retrained

Events Subscribed:
    - resource.created: Auto-classify new resources
"""

from .router import taxonomy_router
from .service import TaxonomyService
from .ml_service import MLClassificationService
from .classification_service import ClassificationService
from .schema import (
    TaxonomyNodeCreate,
    TaxonomyNodeUpdate,
    TaxonomyNodeResponse,
    TaxonomyTreeResponse,
    ClassificationRequest,
    ClassificationResponse,
    TrainingRequest,
    TrainingResponse,
    ActiveLearningRequest,
    ActiveLearningResponse,
)

__version__ = "1.0.0"
__domain__ = "taxonomy"

__all__ = [
    "taxonomy_router",
    "TaxonomyService",
    "MLClassificationService",
    "ClassificationService",
    "TaxonomyNodeCreate",
    "TaxonomyNodeUpdate",
    "TaxonomyNodeResponse",
    "TaxonomyTreeResponse",
    "ClassificationRequest",
    "ClassificationResponse",
    "TrainingRequest",
    "TrainingResponse",
    "ActiveLearningRequest",
    "ActiveLearningResponse",
]
