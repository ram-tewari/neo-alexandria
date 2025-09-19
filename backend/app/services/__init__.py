"""
Neo Alexandria 2.0 - Service Layer

This package contains the business logic services for Neo Alexandria 2.0.
Services handle core functionality including resource management, AI processing,
authority control, classification, and quality assessment.

Services:
- quality_service: Content quality analysis and scoring
- classification_service: UDC-inspired classification system
- authority_service: Subject, creator, and publisher normalization
- resource_service: Core resource CRUD operations and ingestion
- ai_core: AI-powered content processing and embeddings
- search_service: Advanced search and discovery
- graph_service: Knowledge graph and relationship analysis
- recommendation_service: Personalized content recommendations
- curation_service: Content review and quality control
"""

__all__ = [
    "quality_service",
    "classification_service",
    "authority_service",
    "resource_service",
]


