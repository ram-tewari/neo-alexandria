"""
Neo Alexandria 2.0 - Database Configuration and Session Management

This module provides the core database infrastructure for Neo Alexandria 2.0.
It sets up SQLAlchemy async engine, session management, and declarative base class.

Related files:
- app/config/settings.py: Database URL and environment configuration
- app/database/models.py: SQLAlchemy models that inherit from Base
- app/routers/: API endpoints that use get_db() dependency
- alembic/: Database migration scripts

Features:
- Cross-database compatibility (SQLite, PostgreSQL) with async support
- Automatic table creation for development environments
- Async session lifecycle management with dependency injection
- Event listeners for robust table creation in test environments
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Session as OrmSession, sessionmaker
from sqlalchemy import create_engine, event
from typing import AsyncGenerator

from ..config.settings import get_settings

# Get settings instance
settings = get_settings()

# Convert sync DATABASE_URL to async format
def get_async_database_url() -> str:
    """Convert synchronous DATABASE_URL to async format."""
    url = settings.DATABASE_URL
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///")
    elif url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://")
    elif url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
    return url

# Create async engine with optimized connection pool
async_engine = create_async_engine(
    get_async_database_url(),
    echo=True if settings.ENV == "dev" else False,
    pool_size=20,              # Base connections
    max_overflow=40,           # Additional connections (total: 60)
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True,        # Health check before using connection
    echo_pool=True             # Log pool events for monitoring
)

# Create async sessionmaker
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Keep sync engine for background tasks and migrations
# Optimized connection pool configuration for high concurrency
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=True if settings.ENV == "dev" else False,
    pool_size=20,              # Base connections
    max_overflow=40,           # Additional connections (total: 60)
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True,        # Health check before using connection
    echo_pool=True             # Log pool events for monitoring
)

# Create sync sessionmaker for background tasks
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)


class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base class.
    
    All database models inherit from this base class to ensure consistent
    metadata management and table creation across the application.
    """
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database dependency for FastAPI dependency injection.
    
    Provides an async database session that is automatically created and closed
    for each request. Ensures table creation for SQLite environments
    and handles connection lifecycle management.
    
    Yields:
        AsyncSession: SQLAlchemy async database session
    """
    async with AsyncSessionLocal() as session:
        # Ensure metadata exists for this connection (esp. sqlite in-memory)
        try:
            async with session.bind.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception:
            pass
        yield session


def get_sync_db():
    """
    Synchronous database dependency for background tasks.
    
    Provides a synchronous database session for background processing
    where async context is not available.
    
    Yields:
        Session: SQLAlchemy synchronous database session
    """
    db = SessionLocal()
    try:
        # Ensure metadata exists for this connection (esp. sqlite in-memory)
        try:
            Base.metadata.create_all(bind=db.get_bind())
        except Exception:
            pass
        yield db
    finally:
        db.close()


# Ensure tables exist for any Session bind (helps in-memory SQLite tests)
@event.listens_for(OrmSession, "before_flush")
def _ensure_tables_before_flush(session: OrmSession, flush_context, instances):  # type: ignore[no-redef]
    """
    Event listener to ensure tables exist before any flush operation.
    
    This is particularly useful for in-memory SQLite databases used in tests,
    where tables need to be created on-demand for each session.
    """
    try:
        bind = session.get_bind()
        if bind is not None:
            Base.metadata.create_all(bind=bind)
    except Exception:
        # Best-effort; ignore if fails
        pass


def get_pool_status() -> dict:
    """
    Get connection pool statistics for monitoring.
    
    Returns detailed metrics about the current state of the database
    connection pool, including active connections, available connections,
    and overflow usage.
    
    Returns:
        dict: Connection pool statistics with the following keys:
            - size: Total pool size (base connections)
            - checked_in: Number of connections available in the pool
            - checked_out: Number of connections currently in use
            - overflow: Number of overflow connections in use
            - total: Total connections (checked_in + checked_out + overflow)
    """
    pool = sync_engine.pool
    return {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total": pool.size() + pool.overflow()
    }
