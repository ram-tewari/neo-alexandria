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

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .database.base import Base, sync_engine, get_pool_usage_warning
# Ensure models are imported so Base.metadata is populated for create_all
from .database import models  # noqa: F401
from .routers.resources import router as resources_router
from .routers.curation import router as curation_router
from .routers.search import router as search_router
from .routers.classification import router as classification_router
from .routers.authority import router as authority_router
from .routers.graph import router as graph_router
from .routers.recommendation import router as recommendation_router
from .routers.recommendations import router as recommendations_router
from .routers.citations import router as citations_router
from .routers.collections import router as collections_router
from .routers.annotations import router as annotations_router
from .routers.taxonomy import router as taxonomy_router
from .routers.quality import router as quality_router
from .routers.discovery import router as discovery_router
from .routers.monitoring import router as monitoring_router
from .monitoring import setup_monitoring

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    Startup:
    - Register event hooks for automatic data consistency
    - Initialize Redis cache connection
    - Log event system initialization
    
    Shutdown:
    - Clean up resources if needed
    """
    # Startup
    logger.info("Starting Neo Alexandria 2.0...")
    
    # Initialize Redis cache connection
    try:
        from .cache.redis_cache import cache
        if cache.ping():
            logger.info("Redis cache connection established successfully")
        else:
            logger.warning("Redis cache connection failed - caching will be disabled")
    except Exception as e:
        logger.warning(f"Redis cache initialization failed: {e} - caching will be disabled")
    
    # Register event hooks for automatic data consistency
    try:
        from .events.hooks import register_all_hooks
        register_all_hooks()
        logger.info("Event system initialized - all hooks registered for automatic data consistency")
    except Exception as e:
        logger.error(f"Failed to register event hooks: {e}", exc_info=True)
    
    logger.info("Neo Alexandria 2.0 startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Neo Alexandria 2.0...")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    
    Sets up the application with:
    - Database table creation for SQLite environments
    - All feature routers (resources, curation, search, authority, classification)
    - Application metadata and versioning
    - Event system and Redis cache initialization via lifespan
    
    Returns:
        FastAPI: Configured application instance ready for deployment
    """
    app = FastAPI(
        title="Neo Alexandria 2.0",
        version="0.4.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware to allow frontend connections
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add connection pool monitoring middleware
    @app.middleware("http")
    async def monitor_connection_pool(request: Request, call_next):
        """
        Middleware to monitor database connection pool usage.
        
        Checks pool usage before processing each request and logs warnings
        when pool capacity exceeds 90%. This helps identify potential
        connection exhaustion issues before they cause request failures.
        """
        # Check pool usage before request
        warning = get_pool_usage_warning()
        if warning:
            logger.warning(
                f"Connection pool near capacity: {warning['pool_usage_percent']:.1f}% "
                f"({warning['checked_out']}/{warning['total_capacity']} connections in use)",
                extra=warning
            )
        
        # Process request
        response = await call_next(request)
        
        return response
    
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
    app.include_router(recommendations_router)
    app.include_router(citations_router)
    app.include_router(collections_router)
    app.include_router(annotations_router)
    app.include_router(taxonomy_router)
    app.include_router(quality_router)
    app.include_router(discovery_router)
    app.include_router(monitoring_router)
    
    # Set up performance monitoring
    setup_monitoring(app)
    
    return app


app = create_app()


