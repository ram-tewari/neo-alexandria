"""
Shared fixtures for module endpoint tests.

This module provides common test fixtures for all module endpoint tests,
including database sessions, test clients, and factory fixtures.
"""

import pytest
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.database.base import Base

# Import all models to ensure they're registered with Base.metadata
from app.database.models import Collection, Resource
from app.main import app


@pytest.fixture(scope="function")
def db() -> Session:
    """
    Create a fresh database session for each test.
    Uses PostgreSQL for realistic testing with proper database features.

    Yields:
        Session: SQLAlchemy database session
    """
    import os

    # Get database URL from environment or use default PostgreSQL test database
    db_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/backend_test",
    )

    # Create engine
    engine = create_engine(db_url, echo=False)

    # Drop and recreate schema for clean state
    with engine.begin() as connection:
        connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))
        connection.execute(text("GRANT ALL ON SCHEMA public TO PUBLIC"))
        connection.execute(text("GRANT ALL ON SCHEMA public TO postgres"))

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()  # Rollback any uncommitted changes
        session.close()
        # Clean up tables after test
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(db: Session):
    """
    Create test client with database session override.

    Args:
        db: Database session fixture

    Yields:
        TestClient: FastAPI test client
    """
    from app.shared.database import get_db, get_sync_db

    def override_get_db():
        try:
            yield db
        finally:
            pass

    def override_get_sync_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_sync_db] = override_get_sync_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_collection_data():
    """
    Sample collection data for testing.
    Matches CollectionCreate schema requirements.
    """
    return {
        "name": "Test Collection",
        "description": "A test collection for testing purposes",
        "owner_id": "test-user-123",
        "visibility": "private",
    }


@pytest.fixture
def create_test_collection(db: Session):
    """
    Factory fixture to create test collections.

    Usage:
        collection = create_test_collection(name="My Collection")

    Args:
        db: Database session

    Returns:
        Callable that creates collections
    """
    created_collections = []

    def _create_collection(**kwargs):
        defaults = {
            "name": f"Collection-{uuid.uuid4()}",
            "description": "Test collection",
            "owner_id": "test-user-123",
            "visibility": "private",
        }
        defaults.update(kwargs)

        collection = Collection(**defaults)
        db.add(collection)
        db.commit()
        db.refresh(collection)

        created_collections.append(collection)
        return collection

    yield _create_collection

    # Cleanup
    for collection in created_collections:
        try:
            db.delete(collection)
        except Exception:
            pass
    try:
        db.commit()
    except Exception:
        db.rollback()


@pytest.fixture
def create_test_resource(db: Session):
    """
    Factory fixture to create test resources.

    Usage:
        resource = create_test_resource(title="My Resource")

    Args:
        db: Database session

    Returns:
        Callable that creates resources
    """
    created_resources = []

    def _create_resource(**kwargs):
        defaults = {
            "title": f"Test Resource {uuid.uuid4()}",
            "description": "A test resource for testing purposes",
            "source": f"https://example.com/resource-{uuid.uuid4()}",
            "ingestion_status": "completed",
            "quality_score": 0.8,
        }
        defaults.update(kwargs)

        resource = Resource(**defaults)
        db.add(resource)
        db.commit()
        db.refresh(resource)

        created_resources.append(resource)
        return resource

    yield _create_resource

    # Cleanup
    for resource in created_resources:
        try:
            db.delete(resource)
        except Exception:
            pass
    try:
        db.commit()
    except Exception:
        db.rollback()
