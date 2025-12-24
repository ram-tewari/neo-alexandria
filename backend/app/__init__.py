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
from typing import List, Tuple, Optional, Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .shared.database import Base, sync_engine, get_pool_usage_warning, init_database
from .config.settings import get_settings
# Ensure models are imported so Base.metadata is populated for create_all
from .database import models  # noqa: F401
from .routers.curation import router as curation_router
from .routers.classification import router as classification_router
from .routers.authority import router as authority_router
from .routers.graph import router as graph_router
from .routers.recommendation import router as recommendation_router
from .routers.recommendations import router as recommendations_router
from .routers.citations import router as citations_router
from .routers.annotations import router as annotations_router
from .routers.taxonomy import router as taxonomy_router
from .routers.quality import router as quality_router
from .routers.discovery import router as discovery_router
from .routers.monitoring import router as monitoring_router
from .monitoring import setup_monitoring

logger = logging.getLogger(__name__)


def register_all_modules(app: FastAPI) -> None:
    """
    Register all modular vertical slices with the application.
    
    This function dynamically loads and registers:
    1. Module routers (API endpoints)
    2. Module event handlers (for cross-module communication)
    
    Modules are loaded with error handling to ensure application startup
    continues even if individual modules fail to load.
    
    Args:
        app: FastAPI application instance
    """
    logger.info("Starting module registration...")
    
    # Define modules to register: (module_name, import_path, router_name)
    modules: List[Tuple[str, str, str]] = [
        ("collections", "app.modules.collections", "collections_router"),
        ("resources", "app.modules.resources", "resources_router"),
        ("search", "app.modules.search", "search_router"),
    ]
    
    registered_count = 0
    failed_count = 0
    
    for module_name, module_path, router_name in modules:
        try:
            logger.debug(f"Loading module: {module_name}")
            
            # Dynamically import the module
            import importlib
            module = importlib.import_module(module_path)
            
            # Register the router if it exists
            if hasattr(module, router_name):
                router = getattr(module, router_name)
                app.include_router(router)
                logger.info(f"✓ Registered router for module: {module_name}")
            else:
                logger.warning(f"Module {module_name} does not expose {router_name}")
            
            # Register event handlers if the module has them
            if hasattr(module, "register_handlers"):
                register_handlers_func: Callable[[], None] = getattr(module, "register_handlers")
                register_handlers_func()
                logger.info(f"✓ Registered event handlers for module: {module_name}")
            else:
                logger.debug(f"Module {module_name} has no event handlers to register")
            
            registered_count += 1
            
        except Exception as e:
            failed_count += 1
            logger.error(
                f"✗ Failed to register module {module_name}: {e}",
                exc_info=True,
                extra={
                    "module_name": module_name,
                    "module_path": module_path,
                    "error_type": type(e).__name__
                }
            )
            # Continue with other modules even if one fails
    
    logger.info(
        f"Module registration complete: {registered_count} succeeded, {failed_count} failed"
    )


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
    # Initialize database using shared kernel
    # Skip database initialization during tests - test fixtures handle it
    import os
    if os.getenv("TESTING") != "true":
        settings = get_settings()
        init_database(settings.DATABASE_URL, settings.ENV)
    
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
    
    # Register modular vertical slices (Collections, Resources, Search)
    # This must happen before processing requests to ensure event handlers are registered
    logger.info("Registering modular vertical slices...")
    register_all_modules(app)
    
    # Register remaining layered routers (to be migrated in future phases)
    app.include_router(curation_router)
    app.include_router(authority_router)
    app.include_router(classification_router)
    app.include_router(graph_router)
    app.include_router(recommendation_router)
    app.include_router(recommendations_router)
    app.include_router(citations_router)
    app.include_router(annotations_router)
    app.include_router(taxonomy_router)
    app.include_router(quality_router)
    app.include_router(discovery_router)
    app.include_router(monitoring_router)
    
    # Set up performance monitoring
    setup_monitoring(app)
    
    logger.info("Application initialization complete")
    
    return app


app = create_app()


