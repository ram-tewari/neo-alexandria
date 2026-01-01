"""
Anti-Gaslighting Test Suite - Fresh Fixtures

IMPORTANT: This file is built from scratch with NO imports from legacy test code.
All fixtures are self-contained and independent.
"""

# Set TESTING environment variable BEFORE importing app
# This prevents the app from initializing its own database connection
import os
os.environ["TESTING"] = "true"

import pytest
from typing import Generator
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Direct imports from application code only
from app.shared.database import Base
from app.shared.event_bus import event_bus
from app.main import app

# Import all models to register them with SQLAlchemy
# This ensures all tables are created in test database
from app.database.models import (  # noqa: F401
    Resource, Collection, CollectionResource, Annotation,
    Citation, GraphEdge, GraphEmbedding, DiscoveryHypothesis,
    UserProfile, UserInteraction, RecommendationFeedback,
    TaxonomyNode, ResourceTaxonomy,
    AuthoritySubject, AuthorityCreator, AuthorityPublisher,
    User, ClassificationCode,
    ModelVersion, ABTestExperiment
)


# ============================================================================
# Database Fixtures (Fresh Implementation)
# ============================================================================

@pytest.fixture(scope="function")
def db_engine():
    """
    Create a fresh in-memory SQLite engine for each test.
    
    This fixture is function-scoped to ensure complete isolation.
    Uses StaticPool to ensure all connections share the same in-memory database.
    """
    from sqlalchemy.pool import StaticPool
    
    # Use StaticPool to ensure all connections use the same in-memory database
    # This is critical for testing with dependency injection
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # All connections share the same database
        echo=False
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    
    Provides complete isolation - each test gets its own session
    with a fresh database state.
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine,
        expire_on_commit=False  # Prevent lazy loading errors after commit
    )
    
    session = TestingSessionLocal()
    
    # Explicitly ensure all tables exist before yielding session
    # This is critical for in-memory SQLite databases
    Base.metadata.create_all(bind=db_engine)
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ============================================================================
# FastAPI TestClient Fixture (Fresh Implementation)
# ============================================================================

@pytest.fixture(scope="function")
def test_user(db_session: Session) -> User:
    """
    Create a test user for authentication.
    
    This user is created before the test client is initialized,
    ensuring it exists when authentication dependencies are called.
    
    Uses a fixed UUID that matches the one returned by _get_current_user_id()
    in the recommendation router.
    """
    from uuid import UUID
    
    # Use the same fixed UUID as _get_current_user_id returns
    user = User(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        email="test@example.com",
        username="testuser",
        hashed_password="test_hash",
        full_name="Test User",
        role="user",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def client(db_session: Session, test_user: User) -> Generator[TestClient, None, None]:
    """
    Create a TestClient with database dependency override.
    
    Overrides the app's get_db dependency to use our test session.
    Also overrides authentication to use the test_user.
    """
    from app.shared.database import get_sync_db, get_db
    
    def override_get_sync_db():
        try:
            yield db_session
        finally:
            pass
    
    async def override_get_async_db():
        try:
            yield db_session
        finally:
            pass
    
    # Override both sync and async database dependencies
    app.dependency_overrides[get_sync_db] = override_get_sync_db
    app.dependency_overrides[get_db] = override_get_async_db
    
    # Override authentication dependencies for modules that need it
    try:
        from app.modules.recommendations.router import _get_current_user_id
        # Capture the user ID value to avoid lazy loading issues
        user_id_value = test_user.id
        app.dependency_overrides[_get_current_user_id] = lambda db=None: user_id_value
    except ImportError:
        pass
    
    try:
        from app.modules.annotations.router import _get_current_user_id as annotations_get_user
        app.dependency_overrides[annotations_get_user] = lambda: str(test_user.id)
    except ImportError:
        pass
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ============================================================================
# Event Bus Fixtures (Fresh Implementation)
# ============================================================================

@pytest.fixture(scope="function")
def mock_event_bus():
    """
    Create a mock/spy for the event bus emit method.
    
    This allows tests to verify that events are emitted without
    actually triggering event handlers.
    
    Usage:
        def test_resource_creation(client, mock_event_bus):
            response = client.post("/resources", json={...})
            
            # Verify event was emitted
            mock_event_bus.assert_called_with(
                "resource.created",
                {"resource_id": "...", ...}
            )
    """
    original_emit = event_bus.emit
    mock_emit = MagicMock(wraps=original_emit)
    
    # Track emitted events for tests that need to inspect them
    emitted_events = []
    
    def track_emit(event_name, data, **kwargs):
        # Create a simple event object
        class Event:
            def __init__(self, name, data):
                self.name = name
                self.data = data
        
        emitted_events.append(Event(event_name, data))
        return original_emit(event_name, data, **kwargs)
    
    mock_emit.side_effect = track_emit
    mock_emit.emitted_events = emitted_events
    
    with patch.object(event_bus, 'emit', mock_emit):
        yield mock_emit


@pytest.fixture(scope="function")
def clean_event_bus():
    """
    Provide a clean event bus state for each test.
    
    Clears all handlers and history before and after the test.
    """
    # Clear before test
    event_bus.clear_handlers()
    event_bus.clear_history()
    event_bus.reset_metrics()
    
    yield event_bus
    
    # Clear after test
    event_bus.clear_handlers()
    event_bus.clear_history()
    event_bus.reset_metrics()


# ============================================================================
# Test User Fixture
# ============================================================================
# ML Inference Mocking Fixtures (Task 2.1)
# ============================================================================

@pytest.fixture(scope="session")
def mock_ml_inference():
    """
    Mock ML model inference for all tests.
    
    Mocks:
        - sentence_transformers.SentenceTransformer.encode
        - transformers.pipeline.__call__
        
    Returns:
        Dict with mock objects for test customization
    """
    # Create mock objects without importing the actual modules
    mock_encoder = MagicMock()
    mock_encoder.encode.return_value = [[0.1, 0.2, 0.3]]  # Default embedding
    
    mock_pipe = MagicMock()
    mock_pipe.return_value = [{"label": "LABEL_0", "score": 0.95}]
    
    # Return mocks that can be used to patch in individual tests
    return {
        "sentence_transformer": mock_encoder,
        "pipeline": mock_pipe
    }


# ============================================================================
# Test Data Factory Fixtures (Fresh Implementation)
# ============================================================================

@pytest.fixture(scope="function")
def create_test_resource(db_session: Session):
    """
    Factory fixture for creating test resources.
    
    Returns a function that creates resources with sensible defaults.
    """
    
    def _create_resource(**kwargs):
        defaults = {
            "title": "Test Resource",
            "description": "A test resource for unit testing",
            "source": "https://example.com/test",
            "ingestion_status": "pending",
            "quality_score": 0.0,
        }
        defaults.update(kwargs)
        
        resource = Resource(**defaults)
        db_session.add(resource)
        db_session.commit()
        db_session.refresh(resource)
        
        return resource
    
    return _create_resource


@pytest.fixture(scope="function")
def create_test_category(db_session: Session):
    """
    Factory fixture for creating test taxonomy categories.
    
    Returns a function that creates and returns a TaxonomyNode instance.
    """
    
    def _create_category(name: str = "Test Category", parent_id=None, **kwargs):
        defaults = {
            "name": name,
            "slug": name.lower().replace(" ", "-"),
            "parent_id": parent_id,
            "level": 0,
            "path": f"/{name.lower().replace(' ', '-')}",
            "is_leaf": True,
            "allow_resources": True,
        }
        defaults.update(kwargs)
        
        category = TaxonomyNode(**defaults)
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        
        return category
    
    return _create_category


@pytest.fixture(scope="function")
def create_test_collection(db_session: Session):
    """
    Factory fixture for creating test collections.
    
    Returns a function that creates and returns a Collection instance.
    """
    
    def _create_collection(
        name: str = "Test Collection",
        description: str = None,
        owner_id: str = "test_user",
        **kwargs
    ):
        defaults = {
            "name": name,
            "description": description,
            "owner_id": owner_id,
            "visibility": "private",
        }
        defaults.update(kwargs)
        
        collection = Collection(**defaults)
        db_session.add(collection)
        db_session.commit()
        db_session.refresh(collection)
        
        return collection
    
    return _create_collection


@pytest.fixture(scope="function")
def create_test_annotation(db_session: Session, create_test_resource):
    """
    Factory fixture for creating test annotations.
    
    Returns a function that creates and returns an Annotation instance.
    """
    
    def _create_annotation(
        resource_id=None,
        user_id: str = "test_user",
        highlighted_text: str = "Test annotation",
        start_offset: int = 0,
        end_offset: int = 10,
        **kwargs
    ):
        # Create a test resource if resource_id not provided
        if resource_id is None:
            resource = create_test_resource()
            resource_id = resource.id
        
        defaults = {
            "resource_id": resource_id,
            "user_id": user_id,
            "highlighted_text": highlighted_text,
            "start_offset": start_offset,
            "end_offset": end_offset,
            "color": "#FFFF00",
        }
        defaults.update(kwargs)
        
        annotation = Annotation(**defaults)
        db_session.add(annotation)
        db_session.commit()
        db_session.refresh(annotation)
        
        return annotation
    
    return _create_annotation


@pytest.fixture(scope="function")
def mock_embedding_service(mock_ml_inference):
    """
    Mock embedding service that uses mock_ml_inference.
    
    Returns:
        Mock embedding service with generate_embedding method
    """
    mock_service = MagicMock()
    mock_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
    return mock_service


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test(db_session: Session):
    """
    Automatic cleanup after each test.
    
    This runs after every test to ensure clean state.
    """
    yield
    
    # Rollback any uncommitted changes
    db_session.rollback()
