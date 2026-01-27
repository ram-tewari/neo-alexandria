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
from typing import List, Tuple, Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .shared.database import Base, sync_engine, get_pool_usage_warning, init_database
from .config.settings import get_settings

# Ensure models are imported so Base.metadata is populated for create_all
# Only import in non-test mode to avoid circular dependencies during test discovery
import os

if os.getenv("TESTING") != "true" and os.getenv("PYTEST_CURRENT_TEST") is None:
    from .database import models  # noqa: F401
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
    
    # Get deployment mode
    from app.config.settings import get_settings
    settings = get_settings()
    deployment_mode = settings.MODE
    
    logger.info(f"Deployment mode: {deployment_mode}")

    # Define modules to register: (module_name, import_path, router_names)
    # router_names can be a single string or a list of strings for modules with multiple routers
    # Phase 13.5 modules (completed)
    base_modules: List[Tuple[str, str, List[str]]] = [
        ("collections", "app.modules.collections", ["collections_router"]),
        ("resources", "app.modules.resources", ["resources_router"]),
        ("search", "app.modules.search", ["search_router"]),
        # Phase 14 modules (completed)
        ("annotations", "app.modules.annotations", ["annotations_router"]),
        ("scholarly", "app.modules.scholarly", ["scholarly_router"]),
        ("authority", "app.modules.authority", ["authority_router"]),
        ("curation", "app.modules.curation", ["curation_router"]),
        ("quality", "app.modules.quality", ["quality_router"]),
        ("taxonomy", "app.modules.taxonomy", ["taxonomy_router"]),
        (
            "graph",
            "app.modules.graph",
            ["graph_router", "citations_router", "discovery_router"],
        ),
        # Phase 17 modules (in progress)
        ("auth", "app.modules.auth", ["router"]),
        # Phase 20 modules (in progress)
        ("planning", "app.modules.planning", ["router"]),
        ("mcp", "app.modules.mcp", ["router"]),
    ]
    
    # Modules that require torch (only load in EDGE mode)
    edge_only_modules: List[Tuple[str, str, List[str]]] = [
        ("recommendations", "app.modules.recommendations", ["recommendations_router"]),
    ]
    
    # Modules that require redis (only load in EDGE mode or when redis is available)
    redis_modules: List[Tuple[str, str, List[str]]] = [
        ("monitoring", "app.modules.monitoring", ["monitoring_router"]),
    ]
    
    # Build final module list based on deployment mode
    modules = base_modules.copy()
    
    if deployment_mode == "EDGE":
        # Edge mode: Load all modules including ML-heavy ones
        modules.extend(edge_only_modules)
        modules.extend(redis_modules)
        logger.info("Edge mode: Loading all modules including ML-heavy modules")
    else:
        # Cloud mode: Skip torch-dependent modules, add ingestion router
        logger.info("Cloud mode: Skipping torch-dependent modules (recommendations)")
        # Try to load redis modules but don't fail if redis unavailable
        modules.extend(redis_modules)
        
        # Add Phase 19 ingestion router for cloud API
        try:
            from app.routers.ingestion import router as ingestion_router
            app.include_router(ingestion_router)
            logger.info("✓ Registered ingestion router for cloud API")
        except Exception as e:
            logger.warning(f"Could not load ingestion router: {e}")

    registered_count = 0
    failed_count = 0
    handler_count = 0
    total_routers = 0

    for module_name, module_path, router_names in modules:
        try:
            logger.debug(f"Loading module: {module_name}")

            # Dynamically import the module
            import importlib

            module = importlib.import_module(module_path)

            # Get module version if available
            module_version = getattr(module, "__version__", "unknown")

            # Register all routers for this module
            routers_registered = 0
            for router_name in router_names:
                if hasattr(module, router_name):
                    router = getattr(module, router_name)
                    app.include_router(router)
                    routers_registered += 1
                    total_routers += 1
                else:
                    logger.warning(
                        f"Module {module_name} does not expose {router_name}"
                    )

            if routers_registered > 0:
                logger.info(
                    f"✓ Registered {routers_registered} router(s) for module: {module_name} (v{module_version})"
                )

            # Register event handlers if the module has them
            if hasattr(module, "register_handlers"):
                register_handlers_func: Callable[[], None] = getattr(
                    module, "register_handlers"
                )
                register_handlers_func()
                handler_count += 1
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
                    "error_type": type(e).__name__,
                },
            )
            # Continue with other modules even if one fails

    logger.info(
        f"Module registration complete: {registered_count} modules registered, "
        f"{total_routers} routers registered, "
        f"{handler_count} event handler sets registered, {failed_count} failed"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.

    Startup:
    - Warmup embedding model to avoid cold start latency
    - Register event hooks for automatic data consistency
    - Initialize Redis cache connection
    - Log event system initialization

    Shutdown:
    - Clean up resources if needed
    """
    # Startup
    logger.info("Starting Neo Alexandria 2.0...")

    # Warmup embedding model to avoid cold start latency
    try:
        from .shared.embeddings import EmbeddingService
        
        embedding_service = EmbeddingService()
        if embedding_service.warmup():
            logger.info("✓ Embedding model warmed up successfully")
        else:
            logger.warning("⚠ Embedding model warmup failed - first encoding may be slow")
    except Exception as e:
        logger.warning(f"Embedding model warmup failed: {e} - first encoding may be slow")

    # Initialize Redis cache connection
    try:
        from .shared.cache import cache

        if cache.ping():
            logger.info("Redis cache connection established successfully")
        else:
            logger.warning("Redis cache connection failed - caching will be disabled")
    except Exception as e:
        logger.warning(
            f"Redis cache initialization failed: {e} - caching will be disabled"
        )

    # Register event hooks for automatic data consistency
    try:
        from .events.hooks import register_all_hooks

        register_all_hooks()
        logger.info(
            "Event system initialized - all hooks registered for automatic data consistency"
        )
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
        init_database(settings.get_database_url(), settings.ENV)

    app = FastAPI(title="Neo Alexandria 2.0", version="0.4.0", lifespan=lifespan)

    # Add CORS middleware to allow frontend connections
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add authentication middleware
    @app.middleware("http")
    async def authentication_middleware(request: Request, call_next):
        """
        Middleware to enforce authentication on all endpoints except excluded paths.

        Excluded paths:
        - /auth/* - Authentication endpoints
        - /docs - API documentation
        - /openapi.json - OpenAPI schema
        - /monitoring/health - Health check endpoint
        - /api/v1/ingestion/health - Ingestion health check
        - /api/v1/ingestion/worker/status - Worker status monitoring
        - /api/v1/ingestion/jobs/history - Job history monitoring
        - Test mode (TESTING=true environment variable)
        - OPTIONS requests (CORS preflight)
        """
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Skip authentication in test mode
        import os

        if os.getenv("TESTING", "").lower() in ("true", "1", "yes"):
            return await call_next(request)

        from .shared.security import get_current_user
        from fastapi import HTTPException, status

        # Define excluded paths
        excluded_paths = [
            "/docs",
            "/openapi.json",
            "/redoc",
            "/api/monitoring/health",  # Health check endpoint (with /api prefix)
            "/api/v1/ingestion/health",  # Ingestion health check
            "/api/v1/ingestion/worker/status",  # Worker status (public for monitoring)
            "/api/v1/ingestion/jobs/history",  # Job history (public for monitoring)
        ]

        # Check if path is excluded
        path = request.url.path
        is_excluded = any(
            path.startswith(excluded) for excluded in excluded_paths
        ) or path.startswith("/auth/") or path.startswith("/api/auth/")

        if not is_excluded:
            # Require authentication for all other endpoints
            try:
                # Extract token from Authorization header
                authorization = request.headers.get("Authorization")
                if not authorization or not authorization.startswith("Bearer "):
                    from fastapi.responses import JSONResponse
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Not authenticated"},
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                token = authorization.split(" ")[1]

                # Validate token and get user
                user = await get_current_user(token)

                # Store user in request state for downstream use
                request.state.user = user

            except HTTPException as http_exc:
                # Convert HTTPException to JSONResponse
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=http_exc.status_code,
                    content={"detail": http_exc.detail},
                    headers=http_exc.headers,
                )
            except Exception as e:
                logger.error(f"Authentication error: {e}")
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Could not validate credentials"},
                    headers={"WWW-Authenticate": "Bearer"},
                )

        # Process request with error handling
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(
                f"Request processing error in authentication middleware: {e}",
                exc_info=True,
                extra={"path": request.url.path, "method": request.method}
            )
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )

    # Add rate limiting middleware
    @app.middleware("http")
    async def rate_limiting_middleware(request: Request, call_next):
        """
        Middleware to enforce rate limiting on authenticated requests.

        Excluded paths:
        - /monitoring/health - Health check endpoint
        - /api/v1/ingestion/health - Ingestion health check
        - /api/v1/ingestion/worker/status - Worker status monitoring
        - /api/v1/ingestion/jobs/history - Job history monitoring

        Rate limit headers are added to all responses.
        """
        from .shared.rate_limiter import rate_limiter
        from fastapi import HTTPException, status

        # Define excluded paths
        excluded_paths = [
            "/api/monitoring/health",  # Health check endpoint (with /api prefix)
            "/api/v1/ingestion/health",  # Ingestion health check
            "/api/v1/ingestion/worker/status",  # Worker status
            "/api/v1/ingestion/jobs/history",  # Job history
        ]

        # Check if path is excluded
        path = request.url.path
        is_excluded = any(path.startswith(excluded) for excluded in excluded_paths)

        # Initialize rate limit headers
        rate_limit_headers = {}

        if not is_excluded and hasattr(request.state, "user"):
            # Apply rate limiting for authenticated requests
            try:
                user = request.state.user
                allowed, headers = await rate_limiter.check_rate_limit(
                    user_id=user.user_id, tier=user.tier, endpoint=path
                )

                rate_limit_headers = headers

                if not allowed:
                    # Rate limit exceeded
                    reset_time = headers.get("X-RateLimit-Reset", "60")
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Please try again later.",
                        headers={**headers, "Retry-After": reset_time},
                    )

            except HTTPException:
                # Re-raise HTTP exceptions
                raise
            except Exception as e:
                logger.warning(f"Rate limiting error: {e} - allowing request")
                # Fail open if rate limiting fails

        # Process request with error handling
        try:
            response = await call_next(request)
            
            # Add rate limit headers to response
            for header_name, header_value in rate_limit_headers.items():
                response.headers[header_name] = header_value
            
            return response
        except HTTPException:
            # Re-raise HTTP exceptions (already handled)
            raise
        except Exception as e:
            logger.error(
                f"Request processing error in rate limiting middleware: {e}",
                exc_info=True,
                extra={"path": request.url.path, "method": request.method}
            )
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )

    # Add connection pool monitoring middleware
    # Track request count for sampling
    _pool_check_counter = {"count": 0}
    
    @app.middleware("http")
    async def monitor_connection_pool(request: Request, call_next):
        """
        Middleware to monitor database connection pool usage.

        Checks pool usage periodically (every 10 requests) to reduce overhead.
        Logs warnings when pool capacity exceeds 90%.
        """
        # Only check pool every 10 requests to reduce overhead
        _pool_check_counter["count"] += 1
        should_check = _pool_check_counter["count"] % 10 == 0
        
        if should_check:
            # Check pool usage before request (with error handling)
            try:
                warning = get_pool_usage_warning()
                if warning:
                    logger.warning(
                        f"Connection pool near capacity: {warning['pool_usage_percent']:.1f}% "
                        f"({warning['checked_out']}/{warning['total_capacity']} connections in use)",
                        extra=warning,
                    )
            except Exception as e:
                # Don't fail request if pool monitoring fails
                logger.error(f"Connection pool monitoring error: {e}")

        # Process request with error handling
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(
                f"Request processing error in connection pool middleware: {e}",
                exc_info=True,
                extra={"path": request.url.path, "method": request.method}
            )
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )

    # Ensure tables exist for SQLite environments without migrations
    try:
        Base.metadata.create_all(bind=sync_engine)
    except Exception:
        pass

    # Register modular vertical slices (Collections, Resources, Search, and Phase 14 modules)
    # This must happen before processing requests to ensure event handlers are registered
    logger.info("Registering modular vertical slices...")
    register_all_modules(app)

    # Set up performance monitoring
    setup_monitoring(app)

    logger.info("Application initialization complete")

    return app


# Never create app at module level - always use create_app() function
# This prevents circular imports and blocking during test discovery
app = None
