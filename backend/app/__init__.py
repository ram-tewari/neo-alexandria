"""
Neo Alexandria 2.0 - FastAPI Application Factory

This module creates and configures the FastAPI application instance for Neo Alexandria 2.0.
It sets up the application with all necessary routers and database initialization.

Related files:
- app/database/base.py: Database engine and session configuration
- app/database/models.py: SQLAlchemy models for all entities
- app/routers/: API endpoint routers for different features
- app/config/settings.py: Application configuration management

The application includes the following feature modules:
- Resources: URL ingestion and CRUD operations
- Curation: Review queue and batch operations
- Search: Full-text search with FTS5 and faceting
- Authority: Subject, creator, and publisher normalization
- Classification: Personal classification system with UDC-inspired codes
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database.base import Base, sync_engine
# Ensure models are imported so Base.metadata is populated for create_all
from .database import models  # noqa: F401
from .routers.resources import router as resources_router
from .routers.curation import router as curation_router
from .routers.search import router as search_router
from .routers.classification import router as classification_router
from .routers.authority import router as authority_router
from .routers.graph import router as graph_router
from .routers.recommendation import router as recommendation_router
from .routers.citations import router as citations_router
from .routers.collections import router as collections_router
from .routers.annotations import router as annotations_router
from .routers.taxonomy import router as taxonomy_router
from .monitoring import setup_monitoring


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    
    Sets up the application with:
    - Database table creation for SQLite environments
    - All feature routers (resources, curation, search, authority, classification)
    - Application metadata and versioning
    
    Returns:
        FastAPI: Configured application instance ready for deployment
    """
    app = FastAPI(title="Neo Alexandria 2.0", version="0.4.0")
    
    # Add CORS middleware to allow frontend connections
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Ensure tables exist for SQLite environments without migrations
    try:
        Base.metadata.create_all(bind=sync_engine)
    except Exception:
        pass
    app.include_router(resources_router)
    app.include_router(curation_router)
    app.include_router(search_router)
    app.include_router(authority_router)
    app.include_router(classification_router)
    app.include_router(graph_router)
    app.include_router(recommendation_router)
    app.include_router(citations_router)
    app.include_router(collections_router)
    app.include_router(annotations_router)
    app.include_router(taxonomy_router)
    
    # Set up performance monitoring
    setup_monitoring(app)
    
    return app


app = create_app()


