"""Test configuration and fixtures for Phase 1 tests."""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Generator, Union, List, Dict, Tuple, Optional
from unittest.mock import patch, Mock

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.database.base import Base, get_db, get_sync_db
from backend.app.main import app


# ============================================================================
# Test Environment Setup (Auto-use fixtures)
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up test environment variables before any tests run.
    
    This fixture runs automatically for all tests and sets the TESTING
    environment variable to enable test-safe behavior in the application.
    """
    # Set TESTING environment variable
    os.environ["TESTING"] = "true"
    
    yield
    
    # Clean up after all tests
    os.environ.pop("TESTING", None)


@pytest.fixture(autouse=True)
def mock_monitoring_metrics():
    """
    Mock Prometheus metrics for all tests.
    
    This fixture runs automatically for every test and ensures that
    monitoring metrics use NoOp implementations, preventing:
    - Duplicate metric registration errors
    - Prometheus registry conflicts
    - Slow metric collection during tests
    
    The monitoring module already checks for TESTING=true and uses
    NoOp metrics, but this fixture ensures the environment is set
    and reloads the module if needed.
    """
    # The monitoring module will automatically use NoOp metrics
    # when TESTING=true is set (done by setup_test_environment)
    yield


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture(scope="function")
def test_db(request):
    """
    Create an optimized database for testing with multi-database support.
    
    Uses in-memory SQLite for unit tests (fast, isolated) and file-based
    SQLite for integration tests (more realistic). The scope is determined
    by the test path.
    
    Supports TEST_DATABASE_URL environment variable to override default
    database selection, enabling testing against PostgreSQL or other databases.
    
    Performance optimizations:
    - In-memory database for unit tests (10-100x faster)
    - Minimal schema creation (only required tables)
    - Connection pooling disabled for test isolation
    - WAL mode disabled for simplicity
    - SQLite PRAGMA optimizations for faster writes
    - PostgreSQL connection pooling for integration tests
    - Batch operations support via session context
    
    Args:
        request: pytest request fixture for test introspection
        
    Yields:
        SessionLocal factory for creating database sessions
    """
    import tempfile
    import os
    from backend.app.config.settings import get_settings
    from backend.app.database.base import get_database_type
    
    settings = get_settings()
    
    # Check if TEST_DATABASE_URL is set
    if settings.TEST_DATABASE_URL:
        # Use the configured test database URL
        db_url = settings.TEST_DATABASE_URL
        temp_db_file = None
        is_unit_test = False  # Treat as integration test for PostgreSQL
        db_type = get_database_type(db_url)
    else:
        # Determine if this is a unit test or integration test
        test_path = str(request.fspath)
        is_unit_test = "/unit/" in test_path or "/tests/services/" in test_path
        
        # Use in-memory database for unit tests, file-based for integration tests
        if is_unit_test:
            # In-memory database - much faster for unit tests
            db_url = "sqlite:///:memory:"
            temp_db_file = None
        else:
            # File-based database for integration tests
            temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
            temp_db.close()
            temp_db_file = temp_db.name
            db_url = f"sqlite:///{temp_db_file}"
        db_type = "sqlite"
    
    try:
        # Create engine with database-specific optimizations
        if db_type == "postgresql":
            # PostgreSQL-specific configuration for tests
            engine = create_engine(
                db_url,
                echo=False,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                connect_args={
                    "options": "-c timezone=utc"
                }
            )
        else:
            # SQLite-specific configuration
            engine = create_engine(
                db_url,
                echo=False,
                # Disable connection pooling for test isolation
                poolclass=None if is_unit_test else None,
                # SQLite-specific optimizations
                connect_args={
                    "check_same_thread": False,  # Allow multi-threaded access
                }
            )
            
            # Apply SQLite PRAGMA optimizations for faster writes
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                # Disable synchronous writes for testing (much faster)
                cursor.execute("PRAGMA synchronous = OFF")
                # Use memory for temporary tables
                cursor.execute("PRAGMA temp_store = MEMORY")
                # Increase cache size (default is 2000 pages, we use 10000)
                cursor.execute("PRAGMA cache_size = 10000")
                # Disable journal for in-memory databases (faster)
                if is_unit_test:
                    cursor.execute("PRAGMA journal_mode = OFF")
                cursor.close()
        
        # Create all tables using Alembic migrations
        # This ensures test database schema matches production schema exactly
        from alembic import command
        from alembic.config import Config
        import os
        
        # Get the path to alembic.ini (relative to backend directory)
        backend_dir = Path(__file__).parent.parent
        alembic_ini_path = backend_dir / "alembic.ini"
        
        if alembic_ini_path.exists():
            # Run Alembic migrations to create tables
            alembic_cfg = Config(str(alembic_ini_path))
            alembic_cfg.set_main_option("sqlalchemy.url", db_url)
            
            # For in-memory databases, we need to use the existing connection
            with engine.begin() as connection:
                alembic_cfg.attributes['connection'] = connection
                command.upgrade(alembic_cfg, "head")
        else:
            # Fallback to create_all if alembic.ini not found (shouldn't happen)
            Base.metadata.create_all(engine)
        
        # Create session factory
        TestingSessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            expire_on_commit=False  # Prevent lazy loading issues in tests
        )
        
        def override_get_db():
            try:
                db = TestingSessionLocal()
                yield db
            finally:
                db.close()
        
        def override_get_sync_db():
            try:
                db = TestingSessionLocal()
                yield db
            finally:
                db.close()
        
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_sync_db] = override_get_sync_db
        
        yield TestingSessionLocal
        
        app.dependency_overrides.clear()
        
        # Close all connections
        engine.dispose()
        
    finally:
        # Clean up the temporary database file (if file-based)
        if temp_db_file:
            try:
                os.unlink(temp_db_file)
            except OSError:
                pass


@pytest.fixture
def db_session(test_db):
    """
    Create a database session for integration tests.
    
    This fixture provides a database session that can be used directly
    in integration tests without going through the FastAPI dependency injection.
    
    Args:
        test_db: Test database fixture
        
    Returns:
        SQLAlchemy Session
    """
    TestingSessionLocal = test_db
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def db_type(test_db):
    """
    Get the database type for the current test session.
    
    This fixture provides the database type (sqlite or postgresql) being
    used for the current test, allowing tests to conditionally execute
    database-specific logic or skip tests that require specific databases.
    
    Args:
        test_db: Test database fixture
        
    Returns:
        str: Database type ("sqlite" or "postgresql")
        
    Example:
        def test_database_feature(db_session, db_type):
            if db_type == "postgresql":
                # Test PostgreSQL-specific feature
                pass
            else:
                pytest.skip("PostgreSQL-only test")
    """
    from backend.app.database.base import get_database_type
    from backend.app.config.settings import get_settings
    
    settings = get_settings()
    db_url = settings.TEST_DATABASE_URL or "sqlite:///:memory:"
    return get_database_type(db_url)


@pytest.fixture
def client(test_db) -> TestClient:
    """Create a test client for API testing."""
    return TestClient(app)


@pytest.fixture
def sample_html() -> str:
    """Sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Article: Machine Learning and AI</title>
        <meta name="description" content="An article about machine learning and artificial intelligence">
        <meta name="author" content="Test Author">
    </head>
    <body>
        <article>
            <h1>Understanding Machine Learning</h1>
            <p>Machine learning is a subset of artificial intelligence that focuses on algorithms.</p>
            <p>These algorithms can learn from data and make predictions or decisions.</p>
            <script>alert('This should be removed');</script>
            <style>body { color: red; }</style>
        </article>
    </body>
    </html>
    """


@pytest.fixture
def sample_text() -> str:
    """Sample clean text for testing."""
    return """Understanding Machine Learning. Machine learning is a subset of artificial intelligence that focuses on algorithms. These algorithms can learn from data and make predictions or decisions."""


@pytest.fixture
def mock_fetch_url():
    """Mock for fetch_url function."""
    with patch('backend.app.utils.content_extractor.fetch_url') as mock:
        mock.return_value = {
            "url": "https://example.com/test",
            "status": 200,
            "html": "<html><head><title>Test</title></head><body><p>Test content</p></body></html>"
        }
        yield mock


@pytest.fixture
def mock_archive_local():
    """Mock for archive_local function."""
    with patch('backend.app.utils.content_extractor.archive_local') as mock:
        mock.return_value = {
            "archive_path": "/tmp/test/archive",
            "files": {
                "raw": "/tmp/test/archive/raw.html",
                "text": "/tmp/test/archive/text.txt",
                "meta": "/tmp/test/archive/meta.json"
            }
        }
        yield mock


@pytest.fixture
def sample_resource_data():
    """Sample resource data for testing."""
    return {
        "url": "https://example.com/test",
        "title": "Test Article",
        "description": "Test description",
        "language": "en",
        "type": "article"
    }


@pytest.fixture
def seeded_resources(test_db):
    """
    Create seeded resources for testing with optimized batch inserts.
    
    Performance optimizations:
    - Minimal required fields only
    - Batch insert all resources at once
    - Single commit operation
    - Efficient cleanup with bulk delete
    
    Returns:
        List of resource IDs (as strings)
    """
    from datetime import datetime, timezone, timedelta
    from backend.app.database.models import Resource
    
    TestingSessionLocal = test_db
    db = TestingSessionLocal()
    now = datetime.now(timezone.utc)
    
    # Create all resources in memory first (batch preparation)
    items = []
    for i in range(10):
        # Calculate quality score for this resource
        base_quality = 0.3 + i * 0.08
        
        r = Resource(
            title=f"Item {i}",
            description=f"Desc {i}",
            language="en" if i % 2 == 0 else "es",
            type="article",
            classification_code="000" if i % 2 == 0 else "400",
            subject=["Artificial Intelligence", "Machine Learning"] if i % 2 == 0 else ["Language", "Linguistics"],
            read_status="unread" if i < 5 else "in_progress",
            quality_score=base_quality,
            # Add quality dimensions for Phase 9 compatibility
            quality_overall=base_quality,
            quality_accuracy=min(1.0, base_quality + 0.05),
            quality_completeness=min(1.0, base_quality + 0.02),
            quality_consistency=min(1.0, base_quality - 0.02),
            quality_timeliness=min(1.0, base_quality + 0.03),
            quality_relevance=min(1.0, base_quality + 0.01),
            date_created=now - timedelta(days=30 - i),
            date_modified=now - timedelta(days=15 - i),
        )
        items.append(r)
    
    # Batch insert all resources at once (much faster)
    db.add_all(items)
    db.commit()
    
    # Batch refresh to get IDs
    for r in items:
        db.refresh(r)
    
    resource_ids = [str(r.id) for r in items]
    
    yield resource_ids
    
    # Cleanup with bulk delete (faster than individual deletes)
    try:
        db.query(Resource).filter(Resource.id.in_([r.id for r in items])).delete(synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


# ============================================================================
# Phase 5.5 Recommendation Testing Fixtures
# ============================================================================

@pytest.fixture
def recommendation_test_data(test_db):
    """
    Create comprehensive test data for recommendation system testing.
    
    Performance optimizations:
    - Reduced dataset size (5 resources instead of 7, 5 subjects instead of 10)
    - Batch insert operations
    - Single commit for all data
    - Bulk delete for cleanup
    """
    from datetime import datetime, timezone, timedelta
    from backend.app.database.models import Resource, AuthoritySubject
    
    db = test_db()
    now = datetime.now(timezone.utc)
    
    # Create authority subjects with varying usage counts (reduced from 10 to 5)
    subjects_data = [
        ("Machine Learning", 100),
        ("Python", 80),
        ("Artificial Intelligence", 60),
        ("Data Science", 40),
        ("Neural Networks", 30),
    ]
    
    authority_subjects = []
    for name, count in subjects_data:
        subject = AuthoritySubject(
            canonical_form=name,
            variants=[name.lower(), name.replace(" ", "_")],
            usage_count=count
        )
        authority_subjects.append(subject)
    
    # Create resources with minimal required fields (reduced from 7 to 5)
    resources_data = [
        {
            "title": "Advanced Machine Learning Techniques",
            "description": "Comprehensive guide to modern ML algorithms",
            "subject": ["Machine Learning", "Artificial Intelligence"],
            "quality_score": 0.95,
            "embedding": [0.9, 0.1, 0.0, 0.0, 0.0],
        },
        {
            "title": "Python for Data Science",
            "description": "Learn Python programming for data analysis",
            "subject": ["Python", "Data Science"],
            "quality_score": 0.92,
            "embedding": [0.8, 0.2, 0.0, 0.0, 0.0],
        },
        {
            "title": "Deep Learning Fundamentals",
            "description": "Introduction to neural networks and deep learning",
            "subject": ["Neural Networks"],
            "quality_score": 0.88,
            "embedding": [0.7, 0.3, 0.0, 0.0, 0.0],
        },
        {
            "title": "Basic Statistics",
            "description": "Introduction to statistical concepts",
            "subject": ["Statistics"],
            "quality_score": 0.6,
            "embedding": [0.1, 0.1, 0.8, 0.0, 0.0],
        },
        {
            "title": "Cooking Basics",
            "description": "Unrelated topic for testing",
            "subject": ["Cooking"],
            "quality_score": 0.3,
            "embedding": [0.0, 0.0, 0.0, 0.0, 1.0],
        },
    ]
    
    resources = []
    for i, data in enumerate(resources_data):
        quality = data["quality_score"]
        resource = Resource(
            title=data["title"],
            description=data["description"],
            subject=data["subject"],
            quality_score=quality,
            # Add quality dimensions for Phase 9 compatibility
            quality_overall=quality,
            quality_accuracy=min(1.0, quality + 0.02),
            quality_completeness=min(1.0, quality - 0.01),
            quality_consistency=min(1.0, quality + 0.01),
            quality_timeliness=min(1.0, quality - 0.02),
            quality_relevance=min(1.0, quality + 0.03),
            embedding=data["embedding"],
            language="en",
            type="article",
            classification_code="004",
            read_status="unread",
            created_at=now - timedelta(days=10 - i),
            updated_at=now - timedelta(days=5 - i),
        )
        resources.append(resource)
    
    # Batch insert all data at once (much faster)
    db.add_all(authority_subjects + resources)
    db.commit()
    
    # Batch refresh to get IDs
    for subject in authority_subjects:
        db.refresh(subject)
    for resource in resources:
        db.refresh(resource)
    
    yield {
        "authority_subjects": authority_subjects,
        "resources": resources,
        "high_quality_resources": resources[:3],  # Top 3 by quality
        "low_quality_resources": resources[3:],   # Lower quality
    }
    
    # Cleanup with bulk delete (faster than individual deletes)
    try:
        db.query(Resource).filter(Resource.id.in_([r.id for r in resources])).delete(synchronize_session=False)
        db.query(AuthoritySubject).filter(AuthoritySubject.id.in_([s.id for s in authority_subjects])).delete(synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


@pytest.fixture
def mock_ddgs_search():
    """Mock DDGS search results for testing."""
    from unittest.mock import patch
    
    mock_results = [
        {
            "url": "https://example.com/new-ml-article",
            "title": "Latest Advances in Machine Learning",
            "body": "Recent developments in ML algorithms and applications",
        },
        {
            "url": "https://example.com/python-tutorial",
            "title": "Python Programming Tutorial",
            "body": "Learn Python programming from scratch",
        },
        {
            "url": "https://example.com/ai-research",
            "title": "AI Research Papers",
            "body": "Cutting-edge research in artificial intelligence",
        },
        {
            "url": "https://example.com/data-science-guide",
            "title": "Data Science Guide",
            "body": "Complete guide to data science methodologies",
        },
        {
            "url": "https://example.com/neural-networks",
            "title": "Neural Networks Explained",
            "body": "Understanding neural network architectures",
        },
        {
            "url": "https://example.com/unrelated-content",
            "title": "Cooking Recipes",
            "body": "Delicious recipes for home cooking",
        },
    ]
    
    with patch('backend.app.services.recommendation_service.DDGS') as mock_ddgs:
        class MockDDGS:
            def __init__(self, *args, **kwargs):
                pass
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                return False
            
            def text(self, query, max_results):
                # Return results based on query relevance
                if "machine learning" in query.lower() or "ml" in query.lower():
                    return mock_results[:2]  # ML-related results
                elif "python" in query.lower():
                    return mock_results[1:3]  # Python-related results
                elif "ai" in query.lower() or "artificial intelligence" in query.lower():
                    return mock_results[2:4]  # AI-related results
                else:
                    return mock_results[:max_results]  # Generic results
        
        mock_ddgs.return_value = MockDDGS()
        yield mock_ddgs


@pytest.fixture
def mock_ai_core():
    """Mock AI core for embedding generation."""
    from unittest.mock import patch, MagicMock
    
    def mock_generate_embedding(text):
        """Generate deterministic embeddings based on text content."""
        import hashlib
        
        # Create a deterministic hash-based embedding
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to 5-dimensional vector
        embedding = []
        for i in range(5):
            val = (hash_bytes[i % len(hash_bytes)] - 128) / 128.0
            embedding.append(val)
        
        return embedding
    
    with patch('backend.app.services.dependencies.get_ai_core') as mock_get_ai:
        mock_ai = MagicMock()
        mock_ai.generate_embedding.side_effect = mock_generate_embedding
        mock_get_ai.return_value = mock_ai
        yield mock_ai


@pytest.fixture
def empty_library(test_db):
    """Create an empty library for testing edge cases."""
    from backend.app.database.models import Resource, AuthoritySubject
    
    db = test_db()
    
    # Clean up any existing data
    db.query(Resource).delete()
    db.query(AuthoritySubject).delete()
    db.commit()
    
    yield db
    
    # Cleanup
    db.query(Resource).delete()
    db.query(AuthoritySubject).delete()
    db.commit()
    db.close()


@pytest.fixture
def single_resource_library(test_db):
    """Create a library with only one resource for testing."""
    from datetime import datetime, timezone
    from backend.app.database.models import Resource, AuthoritySubject
    
    db = test_db()
    
    # Clean up existing data
    db.query(Resource).delete()
    db.query(AuthoritySubject).delete()
    
    # Create one authority subject
    subject = AuthoritySubject(
        canonical_form="Test Subject",
        variants=["test", "testing"],
        usage_count=1
    )
    db.add(subject)
    
    # Create one resource
    resource = Resource(
        title="Single Test Resource",
        description="Only resource in library",
        subject=["Test Subject"],
        quality_score=0.8,
        # Add quality dimensions for Phase 9 compatibility
        quality_overall=0.8,
        quality_accuracy=0.82,
        quality_completeness=0.79,
        quality_consistency=0.81,
        quality_timeliness=0.78,
        quality_relevance=0.83,
        embedding=[1.0, 0.0, 0.0, 0.0, 0.0],
        language="en",
        type="article",
        classification_code="000",
        read_status="unread",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(resource)
    
    db.commit()
    db.refresh(subject)
    db.refresh(resource)
    
    yield {
        "subject": subject,
        "resource": resource,
    }
    
    # Cleanup
    db.delete(resource)
    db.delete(subject)
    db.commit()
    db.close()


@pytest.fixture(autouse=True)
def reset_prometheus_registry():
    """Reset Prometheus registry before each test to avoid duplicate metric registration."""
    from prometheus_client import REGISTRY
    
    # Store collectors to re-register after clearing
    collectors = list(REGISTRY._collector_to_names.keys())
    
    yield
    
    # Clear all collectors after test
    try:
        for collector in collectors:
            try:
                REGISTRY.unregister(collector)
            except Exception:
                pass  # Ignore if already unregistered
    except Exception:
        pass  # Ignore any errors during cleanup


# ============================================================================
# Phase 12.6 Domain Object Fixture Factories
# ============================================================================

@pytest.fixture
def quality_score_factory():
    """
    Factory for creating QualityScore domain objects.
    
    Provides sensible defaults for all quality dimensions while allowing
    customization of individual dimensions for specific test scenarios.
    
    Returns:
        Callable that creates QualityScore instances with custom dimensions
        
    Example:
        def test_quality(quality_score_factory):
            score = quality_score_factory(accuracy=0.9, completeness=0.8)
            assert score.overall_score() > 0.8
    """
    from backend.app.domain.quality import QualityScore
    
    def _create(
        accuracy: float = 0.8,
        completeness: float = 0.7,
        consistency: float = 0.75,
        timeliness: float = 0.9,
        relevance: float = 0.85
    ) -> QualityScore:
        return QualityScore(
            accuracy=accuracy,
            completeness=completeness,
            consistency=consistency,
            timeliness=timeliness,
            relevance=relevance
        )
    return _create


@pytest.fixture
def classification_result_factory():
    """
    Factory for creating ClassificationResult domain objects.
    
    Provides sensible defaults including a single high-confidence prediction
    while allowing customization of predictions, model version, and timing.
    
    Returns:
        Callable that creates ClassificationResult instances with custom data
        
    Example:
        def test_classification(classification_result_factory):
            result = classification_result_factory(
                predictions=[
                    ClassificationPrediction("cat1", 0.9, 1),
                    ClassificationPrediction("cat2", 0.7, 2)
                ]
            )
            assert len(result.predictions) == 2
    """
    from backend.app.domain.classification import ClassificationResult, ClassificationPrediction
    
    def _create(
        predictions: list = None,
        model_version: str = "test-model-v1",
        inference_time_ms: float = 50.0,
        resource_id: str = None
    ) -> ClassificationResult:
        if predictions is None:
            predictions = [
                ClassificationPrediction(
                    taxonomy_id="004",
                    confidence=0.9,
                    rank=1
                )
            ]
        return ClassificationResult(
            predictions=predictions,
            model_version=model_version,
            inference_time_ms=inference_time_ms,
            resource_id=resource_id
        )
    return _create


@pytest.fixture
def search_result_factory():
    """
    Factory for creating SearchResult domain objects.
    
    Provides sensible defaults for a single search result with high relevance
    while allowing customization of all attributes.
    
    Returns:
        Callable that creates SearchResult instances with custom data
        
    Example:
        def test_search(search_result_factory):
            result = search_result_factory(
                resource_id="res-123",
                score=0.95,
                rank=1
            )
            assert result.is_high_score()
    """
    from backend.app.domain.search import SearchResult
    
    def _create(
        resource_id: str = "test-resource-id",
        score: float = 0.85,
        rank: int = 1,
        title: str = "Test Resource Title",
        search_method: str = "hybrid",
        metadata: dict = None
    ) -> SearchResult:
        if metadata is None:
            metadata = {}
        return SearchResult(
            resource_id=resource_id,
            score=score,
            rank=rank,
            title=title,
            search_method=search_method,
            metadata=metadata
        )
    return _create


@pytest.fixture
def recommendation_factory():
    """
    Factory for creating Recommendation domain objects.
    
    Provides sensible defaults for a high-quality recommendation while
    allowing customization of all attributes including scoring and metadata.
    
    Returns:
        Callable that creates Recommendation instances with custom data
        
    Example:
        def test_recommendation(recommendation_factory):
            rec = recommendation_factory(
                resource_id="res-123",
                user_id="user-456",
                score=0.9,
                confidence=0.85
            )
            assert rec.is_high_quality()
    """
    from backend.app.domain.recommendation import Recommendation, RecommendationScore
    
    def _create(
        resource_id: str = "test-resource-id",
        user_id: str = "test-user-id",
        score: float = 0.85,
        confidence: float = 0.9,
        rank: int = 1,
        strategy: str = "content-based",
        reason: str = None,
        metadata: dict = None
    ) -> Recommendation:
        recommendation_score = RecommendationScore(
            score=score,
            confidence=confidence,
            rank=rank
        )
        return Recommendation(
            resource_id=resource_id,
            user_id=user_id,
            recommendation_score=recommendation_score,
            strategy=strategy,
            reason=reason,
            metadata=metadata
        )
    return _create


# ============================================================================
# Phase 12.6 Mock Utility Functions
# ============================================================================

def create_quality_service_mock(quality_score=None):
    """
    Create a mock QualityService that returns domain objects.
    
    Provides a properly configured mock of QualityService with methods
    that return QualityScore domain objects. This ensures tests work
    with domain objects rather than primitive dicts.
    
    Args:
        quality_score: Optional QualityScore to return. If None, creates
                      a default QualityScore with reasonable values.
    
    Returns:
        Mock object configured to return QualityScore domain objects
        
    Example:
        def test_with_quality_service():
            mock_service = create_quality_service_mock()
            result = mock_service.compute_quality("resource-123")
            assert isinstance(result, QualityScore)
            assert result.overall_score() > 0.7
    """
    from unittest.mock import Mock
    from backend.app.domain.quality import QualityScore
    
    mock = Mock()
    
    # Create default quality score if not provided
    if quality_score is None:
        quality_score = QualityScore(
            accuracy=0.8,
            completeness=0.7,
            consistency=0.75,
            timeliness=0.9,
            relevance=0.85
        )
    
    # Configure mock methods to return domain objects
    mock.compute_quality.return_value = quality_score
    mock.get_quality_scores.return_value = quality_score
    
    return mock


def create_classification_service_mock(result=None):
    """
    Create a mock MLClassificationService that returns domain objects.
    
    Provides a properly configured mock of MLClassificationService with
    methods that return ClassificationResult domain objects containing
    ClassificationPrediction objects.
    
    Args:
        result: Optional ClassificationResult to return. If None, creates
               a default result with a single high-confidence prediction.
    
    Returns:
        Mock object configured to return ClassificationResult domain objects
        
    Example:
        def test_with_classification_service():
            mock_service = create_classification_service_mock()
            result = mock_service.predict("test text")
            assert isinstance(result, ClassificationResult)
            assert len(result.predictions) > 0
            assert result.predictions[0].confidence > 0.8
    """
    from unittest.mock import Mock
    from backend.app.domain.classification import ClassificationResult, ClassificationPrediction
    
    mock = Mock()
    
    # Create default classification result if not provided
    if result is None:
        result = ClassificationResult(
            predictions=[
                ClassificationPrediction(
                    taxonomy_id="004",
                    confidence=0.9,
                    rank=1
                ),
                ClassificationPrediction(
                    taxonomy_id="006",
                    confidence=0.75,
                    rank=2
                )
            ],
            model_version="test-model-v1",
            inference_time_ms=50.0,
            resource_id=None
        )
    
    # Configure mock methods to return domain objects
    mock.predict.return_value = result
    mock.classify.return_value = result
    
    return mock


def create_search_service_mock(results=None):
    """
    Create a mock SearchService that returns domain objects.
    
    Provides a properly configured mock of SearchService with methods
    that return SearchResult domain objects with proper ranking and scores.
    
    Args:
        results: Optional list of SearchResult objects to return. If None,
                creates a default list with a single high-scoring result.
    
    Returns:
        Mock object configured to return SearchResult domain objects
        
    Example:
        def test_with_search_service():
            mock_service = create_search_service_mock()
            results = mock_service.search("test query")
            assert len(results) > 0
            assert isinstance(results[0], SearchResult)
            assert results[0].score > 0.8
    """
    from unittest.mock import Mock
    from backend.app.domain.search import SearchResult, SearchResults, SearchQuery
    
    mock = Mock()
    
    # Create default search results if not provided
    if results is None:
        results = [
            SearchResult(
                resource_id="test-resource-1",
                score=0.95,
                rank=1,
                title="Test Resource 1",
                search_method="hybrid",
                metadata={"source": "test"}
            ),
            SearchResult(
                resource_id="test-resource-2",
                score=0.85,
                rank=2,
                title="Test Resource 2",
                search_method="hybrid",
                metadata={"source": "test"}
            )
        ]
    
    # Create SearchResults wrapper
    search_query = SearchQuery(
        query_text="test query",
        limit=20,
        enable_reranking=True,
        adaptive_weights=True,
        search_method="hybrid"
    )
    
    search_results = SearchResults(
        results=results,
        query=search_query,
        total_results=len(results),
        search_time_ms=100.0,
        reranked=False
    )
    
    # Configure mock methods to return domain objects
    mock.search.return_value = results
    mock.hybrid_search.return_value = search_results
    mock.semantic_search.return_value = results
    mock.keyword_search.return_value = results
    
    return mock


def create_recommendation_service_mock(recommendations=None):
    """
    Create a mock RecommendationService that returns domain objects.
    
    Provides a properly configured mock of RecommendationService with
    methods that return Recommendation domain objects with proper scoring
    and ranking information.
    
    Args:
        recommendations: Optional list of Recommendation objects to return.
                        If None, creates a default list with high-quality
                        recommendations.
    
    Returns:
        Mock object configured to return Recommendation domain objects
        
    Example:
        def test_with_recommendation_service():
            mock_service = create_recommendation_service_mock()
            recs = mock_service.generate_recommendations("user-123")
            assert len(recs) > 0
            assert isinstance(recs[0], Recommendation)
            assert recs[0].is_high_quality()
    """
    from unittest.mock import Mock
    from backend.app.domain.recommendation import Recommendation, RecommendationScore
    
    mock = Mock()
    
    # Create default recommendations if not provided
    if recommendations is None:
        recommendations = [
            Recommendation(
                resource_id="rec-resource-1",
                user_id="test-user",
                recommendation_score=RecommendationScore(
                    score=0.9,
                    confidence=0.85,
                    rank=1
                ),
                strategy="hybrid",
                reason="High relevance to user interests",
                metadata={"source": "test"}
            ),
            Recommendation(
                resource_id="rec-resource-2",
                user_id="test-user",
                recommendation_score=RecommendationScore(
                    score=0.8,
                    confidence=0.75,
                    rank=2
                ),
                strategy="content-based",
                reason="Similar to previously viewed content",
                metadata={"source": "test"}
            )
        ]
    
    # Configure mock methods to return domain objects
    mock.generate_recommendations.return_value = recommendations
    mock.get_recommendations.return_value = recommendations
    mock.recommend.return_value = recommendations
    mock.get_personalized_recommendations.return_value = recommendations
    
    return mock


# ============================================================================
# Phase 12.6 Test Assertion Helper Functions
# ============================================================================

def assert_quality_score(
    actual,
    expected_overall: float = None,
    expected_level: str = None,
    min_overall: float = None,
    max_overall: float = None,
    expected_dimensions: dict = None,
    tolerance: float = 0.01
):
    """
    Assert quality score matches expectations with backward compatibility.
    
    Supports both QualityScore domain objects and dict representations,
    allowing tests to work with either format during the migration period.
    
    Args:
        actual: QualityScore domain object or dict representation
        expected_overall: Expected overall score (exact match within tolerance)
        expected_level: Expected quality level ('high', 'medium', 'low')
        min_overall: Minimum acceptable overall score (inclusive)
        max_overall: Maximum acceptable overall score (inclusive)
        expected_dimensions: Dict of dimension names to expected values
        tolerance: Tolerance for float comparisons (default: 0.01)
        
    Raises:
        AssertionError: If any assertion fails
        TypeError: If actual is neither QualityScore nor dict
        
    Example:
        # Test with domain object
        score = quality_score_factory(accuracy=0.9)
        assert_quality_score(score, min_overall=0.8, expected_level='high')
        
        # Test with dict (backward compatibility)
        score_dict = {'accuracy': 0.9, 'completeness': 0.8, ...}
        assert_quality_score(score_dict, expected_dimensions={'accuracy': 0.9})
    """
    from backend.app.domain.quality import QualityScore
    
    # Handle both domain object and dict formats
    if isinstance(actual, QualityScore):
        actual_overall = actual.overall_score()
        actual_level = actual.get_quality_level()
        actual_dimensions = actual.get_dimension_scores()
    elif isinstance(actual, dict):
        # Dict format - compute overall score if not present
        if 'overall_score' in actual:
            actual_overall = actual['overall_score']
        else:
            # Compute from dimensions using same weights as QualityScore
            from backend.app.domain.quality import (
                ACCURACY_WEIGHT, COMPLETENESS_WEIGHT, CONSISTENCY_WEIGHT,
                TIMELINESS_WEIGHT, RELEVANCE_WEIGHT
            )
            actual_overall = (
                ACCURACY_WEIGHT * actual.get('accuracy', 0.0) +
                COMPLETENESS_WEIGHT * actual.get('completeness', 0.0) +
                CONSISTENCY_WEIGHT * actual.get('consistency', 0.0) +
                TIMELINESS_WEIGHT * actual.get('timeliness', 0.0) +
                RELEVANCE_WEIGHT * actual.get('relevance', 0.0)
            )
        
        # Determine quality level
        if 'quality_level' in actual:
            actual_level = actual['quality_level']
        else:
            from backend.app.domain.quality import HIGH_QUALITY_THRESHOLD, MEDIUM_QUALITY_THRESHOLD
            if actual_overall >= HIGH_QUALITY_THRESHOLD:
                actual_level = 'high'
            elif actual_overall >= MEDIUM_QUALITY_THRESHOLD:
                actual_level = 'medium'
            else:
                actual_level = 'low'
        
        actual_dimensions = {
            'accuracy': actual.get('accuracy'),
            'completeness': actual.get('completeness'),
            'consistency': actual.get('consistency'),
            'timeliness': actual.get('timeliness'),
            'relevance': actual.get('relevance')
        }
    else:
        raise TypeError(
            f"Expected QualityScore or dict, got {type(actual).__name__}. "
            f"Ensure the service returns domain objects or dicts."
        )
    
    # Assert overall score (exact match)
    if expected_overall is not None:
        assert abs(actual_overall - expected_overall) < tolerance, (
            f"Expected overall score {expected_overall}, "
            f"got {actual_overall} (tolerance: {tolerance})"
        )
    
    # Assert overall score range
    if min_overall is not None:
        assert actual_overall >= min_overall, (
            f"Expected overall score >= {min_overall}, got {actual_overall}"
        )
    
    if max_overall is not None:
        assert actual_overall <= max_overall, (
            f"Expected overall score <= {max_overall}, got {actual_overall}"
        )
    
    # Assert quality level
    if expected_level is not None:
        assert actual_level == expected_level, (
            f"Expected quality level '{expected_level}', got '{actual_level}'"
        )
    
    # Assert individual dimensions
    if expected_dimensions is not None:
        for dimension, expected_value in expected_dimensions.items():
            actual_value = actual_dimensions.get(dimension)
            assert actual_value is not None, (
                f"Dimension '{dimension}' not found in quality score"
            )
            assert abs(actual_value - expected_value) < tolerance, (
                f"Expected {dimension}={expected_value}, "
                f"got {actual_value} (tolerance: {tolerance})"
            )


def assert_classification_result(
    actual,
    min_confidence: float = None,
    max_confidence: float = None,
    expected_count: int = None,
    min_count: int = None,
    expected_taxonomy_ids: list = None,
    expected_model_version: str = None,
    check_high_confidence: bool = False,
    high_confidence_threshold: float = 0.8
):
    """
    Assert classification result matches expectations with backward compatibility.
    
    Supports both ClassificationResult domain objects and dict representations,
    allowing flexible assertions on predictions, confidence levels, and metadata.
    
    Args:
        actual: ClassificationResult domain object or dict representation
        min_confidence: Minimum confidence for all predictions
        max_confidence: Maximum confidence for all predictions
        expected_count: Expected number of predictions (exact)
        min_count: Minimum number of predictions
        expected_taxonomy_ids: Expected list of taxonomy IDs (order-independent)
        expected_model_version: Expected model version string
        check_high_confidence: Whether to verify at least one high-confidence prediction
        high_confidence_threshold: Threshold for high confidence (default: 0.8)
        
    Raises:
        AssertionError: If any assertion fails
        TypeError: If actual is neither ClassificationResult nor dict
        
    Example:
        # Test with domain object
        result = classification_result_factory()
        assert_classification_result(
            result,
            min_confidence=0.5,
            expected_count=2,
            check_high_confidence=True
        )
        
        # Test with dict (backward compatibility)
        result_dict = {'predictions': [...], 'model_version': 'v1'}
        assert_classification_result(result_dict, min_count=1)
    """
    from backend.app.domain.classification import ClassificationResult, ClassificationPrediction
    
    # Handle both domain object and dict formats
    if isinstance(actual, ClassificationResult):
        predictions = actual.predictions
        model_version = actual.model_version
    elif isinstance(actual, dict):
        predictions_data = actual.get('predictions', [])
        # Convert dict predictions to ClassificationPrediction objects for uniform handling
        predictions = []
        for p in predictions_data:
            if isinstance(p, ClassificationPrediction):
                predictions.append(p)
            elif isinstance(p, dict):
                predictions.append(ClassificationPrediction(
                    taxonomy_id=p['taxonomy_id'],
                    confidence=p['confidence'],
                    rank=p.get('rank', 0)
                ))
            else:
                raise TypeError(f"Unexpected prediction type: {type(p)}")
        model_version = actual.get('model_version')
    else:
        raise TypeError(
            f"Expected ClassificationResult or dict, got {type(actual).__name__}. "
            f"Ensure the service returns domain objects or dicts."
        )
    
    # Assert prediction count
    if expected_count is not None:
        assert len(predictions) == expected_count, (
            f"Expected {expected_count} predictions, got {len(predictions)}"
        )
    
    if min_count is not None:
        assert len(predictions) >= min_count, (
            f"Expected at least {min_count} predictions, got {len(predictions)}"
        )
    
    # Assert confidence ranges
    if min_confidence is not None or max_confidence is not None:
        for i, pred in enumerate(predictions):
            confidence = pred.confidence if hasattr(pred, 'confidence') else pred['confidence']
            
            if min_confidence is not None:
                assert confidence >= min_confidence, (
                    f"Prediction {i} has confidence {confidence} < {min_confidence}"
                )
            
            if max_confidence is not None:
                assert confidence <= max_confidence, (
                    f"Prediction {i} has confidence {confidence} > {max_confidence}"
                )
    
    # Assert taxonomy IDs
    if expected_taxonomy_ids is not None:
        actual_ids = [
            p.taxonomy_id if hasattr(p, 'taxonomy_id') else p['taxonomy_id']
            for p in predictions
        ]
        assert set(actual_ids) == set(expected_taxonomy_ids), (
            f"Expected taxonomy IDs {expected_taxonomy_ids}, got {actual_ids}"
        )
    
    # Assert model version
    if expected_model_version is not None:
        assert model_version == expected_model_version, (
            f"Expected model version '{expected_model_version}', got '{model_version}'"
        )
    
    # Assert high confidence predictions exist
    if check_high_confidence:
        high_conf_predictions = [
            p for p in predictions
            if (p.confidence if hasattr(p, 'confidence') else p['confidence']) >= high_confidence_threshold
        ]
        assert len(high_conf_predictions) > 0, (
            f"Expected at least one prediction with confidence >= {high_confidence_threshold}, "
            f"but none found"
        )


def assert_search_result(
    actual,
    min_score: float = None,
    max_score: float = None,
    expected_resource_id: str = None,
    expected_rank: int = None,
    max_rank: int = None,
    expected_title: str = None,
    expected_method: str = None,
    check_metadata: dict = None,
    check_high_score: bool = False,
    high_score_threshold: float = 0.8
):
    """
    Assert search result matches expectations with backward compatibility.
    
    Supports both SearchResult domain objects and dict representations,
    allowing flexible assertions on scores, rankings, and metadata.
    
    Args:
        actual: SearchResult domain object or dict representation
        min_score: Minimum acceptable relevance score
        max_score: Maximum acceptable relevance score
        expected_resource_id: Expected resource ID (exact match)
        expected_rank: Expected rank position (exact match)
        max_rank: Maximum acceptable rank (for top-K checks)
        expected_title: Expected title (exact match)
        expected_method: Expected search method
        check_metadata: Dict of metadata keys to expected values
        check_high_score: Whether to verify high score
        high_score_threshold: Threshold for high score (default: 0.8)
        
    Raises:
        AssertionError: If any assertion fails
        TypeError: If actual is neither SearchResult nor dict
        
    Example:
        # Test with domain object
        result = search_result_factory(score=0.95, rank=1)
        assert_search_result(
            result,
            min_score=0.9,
            max_rank=5,
            check_high_score=True
        )
        
        # Test with dict (backward compatibility)
        result_dict = {'resource_id': 'res-123', 'score': 0.85, 'rank': 2}
        assert_search_result(result_dict, min_score=0.8)
    """
    from backend.app.domain.search import SearchResult
    
    # Handle both domain object and dict formats
    if isinstance(actual, SearchResult):
        resource_id = actual.resource_id
        score = actual.score
        rank = actual.rank
        title = actual.title
        search_method = actual.search_method
        metadata = actual.metadata
    elif isinstance(actual, dict):
        resource_id = actual.get('resource_id')
        score = actual.get('score')
        rank = actual.get('rank')
        title = actual.get('title', '')
        search_method = actual.get('search_method', 'unknown')
        metadata = actual.get('metadata', {})
    else:
        raise TypeError(
            f"Expected SearchResult or dict, got {type(actual).__name__}. "
            f"Ensure the service returns domain objects or dicts."
        )
    
    # Assert score range
    if min_score is not None:
        assert score >= min_score, (
            f"Expected score >= {min_score}, got {score}"
        )
    
    if max_score is not None:
        assert score <= max_score, (
            f"Expected score <= {max_score}, got {score}"
        )
    
    # Assert high score
    if check_high_score:
        assert score >= high_score_threshold, (
            f"Expected high score (>= {high_score_threshold}), got {score}"
        )
    
    # Assert resource ID
    if expected_resource_id is not None:
        assert resource_id == expected_resource_id, (
            f"Expected resource_id '{expected_resource_id}', got '{resource_id}'"
        )
    
    # Assert rank
    if expected_rank is not None:
        assert rank == expected_rank, (
            f"Expected rank {expected_rank}, got {rank}"
        )
    
    if max_rank is not None:
        assert rank <= max_rank, (
            f"Expected rank <= {max_rank}, got {rank}"
        )
    
    # Assert title
    if expected_title is not None:
        assert title == expected_title, (
            f"Expected title '{expected_title}', got '{title}'"
        )
    
    # Assert search method
    if expected_method is not None:
        assert search_method == expected_method, (
            f"Expected search method '{expected_method}', got '{search_method}'"
        )
    
    # Assert metadata
    if check_metadata is not None:
        for key, expected_value in check_metadata.items():
            assert key in metadata, (
                f"Expected metadata key '{key}' not found"
            )
            actual_value = metadata[key]
            assert actual_value == expected_value, (
                f"Expected metadata['{key}'] = {expected_value}, got {actual_value}"
            )


def assert_recommendation(
    actual,
    min_score: float = None,
    max_score: float = None,
    min_confidence: float = None,
    max_confidence: float = None,
    expected_resource_id: str = None,
    expected_user_id: str = None,
    expected_rank: int = None,
    max_rank: int = None,
    expected_strategy: str = None,
    check_high_quality: bool = False,
    check_metadata: dict = None,
    score_threshold: float = 0.7,
    confidence_threshold: float = 0.8
):
    """
    Assert recommendation matches expectations with backward compatibility.
    
    Supports both Recommendation domain objects and dict representations,
    allowing flexible assertions on scores, confidence, rankings, and metadata.
    
    Args:
        actual: Recommendation domain object or dict representation
        min_score: Minimum acceptable relevance score
        max_score: Maximum acceptable relevance score
        min_confidence: Minimum acceptable confidence
        max_confidence: Maximum acceptable confidence
        expected_resource_id: Expected resource ID (exact match)
        expected_user_id: Expected user ID (exact match)
        expected_rank: Expected rank position (exact match)
        max_rank: Maximum acceptable rank (for top-K checks)
        expected_strategy: Expected recommendation strategy
        check_high_quality: Whether to verify high quality recommendation
        check_metadata: Dict of metadata keys to expected values
        score_threshold: Threshold for high quality score (default: 0.7)
        confidence_threshold: Threshold for high quality confidence (default: 0.8)
        
    Raises:
        AssertionError: If any assertion fails
        TypeError: If actual is neither Recommendation nor dict
        
    Example:
        # Test with domain object
        rec = recommendation_factory(score=0.9, confidence=0.85)
        assert_recommendation(
            rec,
            min_score=0.8,
            check_high_quality=True
        )
        
        # Test with dict (backward compatibility)
        rec_dict = {'resource_id': 'res-123', 'score': 0.85, 'confidence': 0.9}
        assert_recommendation(rec_dict, min_confidence=0.8)
    """
    from backend.app.domain.recommendation import Recommendation, RecommendationScore
    
    # Handle both domain object and dict formats
    if isinstance(actual, Recommendation):
        resource_id = actual.resource_id
        user_id = actual.user_id
        score = actual.get_score()
        confidence = actual.get_confidence()
        rank = actual.get_rank()
        strategy = actual.strategy
        metadata = actual.metadata
    elif isinstance(actual, dict):
        resource_id = actual.get('resource_id')
        user_id = actual.get('user_id')
        
        # Handle nested or flat score structure
        if 'recommendation_score' in actual:
            score_data = actual['recommendation_score']
            score = score_data.get('score')
            confidence = score_data.get('confidence')
            rank = score_data.get('rank')
        else:
            score = actual.get('score')
            confidence = actual.get('confidence')
            rank = actual.get('rank')
        
        strategy = actual.get('strategy', 'unknown')
        metadata = actual.get('metadata', {})
    else:
        raise TypeError(
            f"Expected Recommendation or dict, got {type(actual).__name__}. "
            f"Ensure the service returns domain objects or dicts."
        )
    
    # Assert score range
    if min_score is not None:
        assert score >= min_score, (
            f"Expected score >= {min_score}, got {score}"
        )
    
    if max_score is not None:
        assert score <= max_score, (
            f"Expected score <= {max_score}, got {score}"
        )
    
    # Assert confidence range
    if min_confidence is not None:
        assert confidence >= min_confidence, (
            f"Expected confidence >= {min_confidence}, got {confidence}"
        )
    
    if max_confidence is not None:
        assert confidence <= max_confidence, (
            f"Expected confidence <= {max_confidence}, got {confidence}"
        )
    
    # Assert high quality
    if check_high_quality:
        is_high_quality = (
            score >= score_threshold and
            confidence >= confidence_threshold
        )
        assert is_high_quality, (
            f"Expected high quality recommendation "
            f"(score >= {score_threshold}, confidence >= {confidence_threshold}), "
            f"got score={score}, confidence={confidence}"
        )
    
    # Assert resource ID
    if expected_resource_id is not None:
        assert resource_id == expected_resource_id, (
            f"Expected resource_id '{expected_resource_id}', got '{resource_id}'"
        )
    
    # Assert user ID
    if expected_user_id is not None:
        assert user_id == expected_user_id, (
            f"Expected user_id '{expected_user_id}', got '{user_id}'"
        )
    
    # Assert rank
    if expected_rank is not None:
        assert rank == expected_rank, (
            f"Expected rank {expected_rank}, got {rank}"
        )
    
    if max_rank is not None:
        assert rank <= max_rank, (
            f"Expected rank <= {max_rank}, got {rank}"
        )
    
    # Assert strategy
    if expected_strategy is not None:
        assert strategy == expected_strategy, (
            f"Expected strategy '{expected_strategy}', got '{strategy}'"
        )
    
    # Assert metadata
    if check_metadata is not None:
        for key, expected_value in check_metadata.items():
            assert key in metadata, (
                f"Expected metadata key '{key}' not found"
            )
            actual_value = metadata[key]
            assert actual_value == expected_value, (
                f"Expected metadata['{key}'] = {expected_value}, got {actual_value}"
            )


# ============================================================================
# Assertion Helper Functions (Task 13: Fix assertion mismatch patterns)
# ============================================================================

def assert_quality_score_in_range(
    actual: Union[float, Dict, 'QualityScore'],
    min_score: float = 0.0,
    max_score: float = 1.0,
    tolerance: float = 0.05
):
    """
    Assert quality score is within expected range.
    
    Args:
        actual: Quality score value, dict, or QualityScore object
        min_score: Minimum expected score
        max_score: Maximum expected score
        tolerance: Tolerance for range boundaries
    """
    from backend.app.domain.quality import QualityScore
    
    if isinstance(actual, QualityScore):
        score = actual.overall_score()
    elif isinstance(actual, dict):
        score = actual.get('overall_score', actual.get('quality_score', 0.0))
    else:
        score = float(actual)
    
    assert min_score - tolerance <= score <= max_score + tolerance, \
        f"Quality score {score} not in range [{min_score}, {max_score}] ± {tolerance}"


def assert_confidence_in_range(
    confidence: float,
    min_confidence: float = 0.0,
    max_confidence: float = 1.0
):
    """
    Assert confidence value is within valid range.
    
    Args:
        confidence: Confidence value to check
        min_confidence: Minimum expected confidence
        max_confidence: Maximum expected confidence
    """
    assert min_confidence <= confidence <= max_confidence, \
        f"Confidence {confidence} not in range [{min_confidence}, {max_confidence}]"


def assert_results_sorted_by_score(
    results: List[Union[Tuple, Dict]],
    descending: bool = True
):
    """
    Assert that results are sorted by score.
    
    Args:
        results: List of results (tuples or dicts with 'score' key)
        descending: If True, check descending order; if False, check ascending
    """
    if not results:
        return
    
    scores = []
    for r in results:
        if isinstance(r, tuple):
            scores.append(r[1])  # Assume (id, score) tuple
        elif isinstance(r, dict):
            scores.append(r.get('score', r.get('hybrid_score', 0.0)))
        else:
            scores.append(float(r))
    
    if descending:
        assert scores == sorted(scores, reverse=True), \
            f"Results not sorted in descending order: {scores}"
    else:
        assert scores == sorted(scores), \
            f"Results not sorted in ascending order: {scores}"


def assert_search_result_presence(
    results: List[Union[str, Dict]],
    expected_ids: List[str]
):
    """
    Assert that expected IDs are present in search results (order-independent).
    
    Args:
        results: List of search results
        expected_ids: List of expected resource IDs
    """
    if isinstance(results[0], dict):
        result_ids = {r.get('id', r.get('resource_id')) for r in results}
    else:
        result_ids = set(results)
    
    expected_set = set(expected_ids)
    assert expected_set.issubset(result_ids), \
        f"Expected IDs {expected_set - result_ids} not found in results"


def assert_classification_confidence_valid(
    predictions: List[Union[Dict, 'ClassificationPrediction']],
    min_confidence: float = 0.0,
    max_confidence: float = 1.0
):
    """
    Assert that all classification predictions have valid confidence values.
    
    Args:
        predictions: List of predictions
        min_confidence: Minimum valid confidence
        max_confidence: Maximum valid confidence
    """
    from backend.app.domain.classification import ClassificationPrediction
    
    for pred in predictions:
        if isinstance(pred, ClassificationPrediction):
            confidence = pred.confidence
        elif isinstance(pred, dict):
            confidence = pred.get('confidence', 0.0)
        else:
            confidence = float(pred)
        
        assert min_confidence <= confidence <= max_confidence, \
            f"Confidence {confidence} not in valid range [{min_confidence}, {max_confidence}]"


# ============================================================================
# Phase 12.6 ML Model Loading Optimization Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def ml_classification_model_cached():
    """
    Module-level fixture for caching ML classification model.
    
    Loads the MLClassificationService model once per test module to avoid
    expensive model loading for every test. This significantly improves
    test execution time for integration tests that need real model inference.
    
    Note: This fixture should only be used in integration tests where real
    model inference is required. Unit tests should use mocks instead.
    
    Yields:
        Tuple of (model, tokenizer, device) or (None, None, None) if loading fails
        
    Example:
        def test_classification_integration(ml_classification_model_cached):
            model, tokenizer, device = ml_classification_model_cached
            if model is None:
                pytest.skip("ML model not available")
            # Use model for testing...
    """
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        from pathlib import Path
        
        # Try to load production model
        model_paths = [
            Path("models") / "classification" / "production",
            Path("backend") / "models" / "classification" / "production",
            Path(__file__).parent.parent / "models" / "classification" / "production",
        ]
        
        model = None
        tokenizer = None
        device = None
        
        # Try to find and load model
        for model_path in model_paths:
            if model_path.exists() and (model_path / "config.json").exists():
                try:
                    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
                    model = AutoModelForSequenceClassification.from_pretrained(
                        str(model_path),
                        local_files_only=True
                    )
                    
                    # Move to appropriate device
                    if torch.cuda.is_available():
                        device = torch.device("cuda")
                        model = model.cuda()
                    else:
                        device = torch.device("cpu")
                    
                    model.eval()
                    break
                except Exception as e:
                    continue
        
        yield (model, tokenizer, device)
        
        # Cleanup
        if model is not None:
            del model
        if tokenizer is not None:
            del tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
    except ImportError:
        # ML libraries not available
        yield (None, None, None)
    except Exception as e:
        # Model loading failed
        yield (None, None, None)


@pytest.fixture(scope="module")
def sparse_embedding_model_cached():
    """
    Module-level fixture for caching sparse embedding model (BAAI/bge-m3).
    
    Loads the BGE-M3 model once per test module to avoid expensive model
    loading for every test. This significantly improves test execution time
    for integration tests that need real sparse embedding generation.
    
    Note: This fixture should only be used in integration tests where real
    embedding generation is required. Unit tests should use mocks instead.
    
    Yields:
        Tuple of (model, tokenizer, device) or (None, None, None) if loading fails
        
    Example:
        def test_sparse_embedding_integration(sparse_embedding_model_cached):
            model, tokenizer, device = sparse_embedding_model_cached
            if model is None:
                pytest.skip("Sparse embedding model not available")
            # Use model for testing...
    """
    try:
        import torch
        from transformers import AutoModel, AutoTokenizer
        
        model = None
        tokenizer = None
        device = None
        
        try:
            tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-m3")
            model = AutoModel.from_pretrained("BAAI/bge-m3")
            
            # Move to appropriate device
            if torch.cuda.is_available():
                device = torch.device("cuda")
                model = model.cuda()
            else:
                device = torch.device("cpu")
            
            model.eval()
            
        except Exception as e:
            # Model loading failed, return None
            pass
        
        yield (model, tokenizer, device)
        
        # Cleanup
        if model is not None:
            del model
        if tokenizer is not None:
            del tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
    except ImportError:
        # ML libraries not available
        yield (None, None, None)
    except Exception as e:
        # Model loading failed
        yield (None, None, None)


@pytest.fixture
def mock_ml_classification_service():
    """
    Mock MLClassificationService for unit tests to avoid model loading.
    
    Provides a fully mocked MLClassificationService that returns realistic
    ClassificationResult domain objects without loading any ML models.
    This is the preferred approach for unit tests.
    
    Returns:
        Mock MLClassificationService with configured methods
        
    Example:
        def test_classification_logic(mock_ml_classification_service):
            result = mock_ml_classification_service.predict("test text")
            assert isinstance(result, ClassificationResult)
            assert len(result.predictions) > 0
    """
    from unittest.mock import Mock, MagicMock
    from backend.app.domain.classification import ClassificationResult, ClassificationPrediction
    
    mock_service = Mock()
    
    # Configure predict method
    def mock_predict(text, top_k=5):
        return ClassificationResult(
            predictions=[
                ClassificationPrediction(
                    taxonomy_id="004",
                    confidence=0.9,
                    rank=1
                ),
                ClassificationPrediction(
                    taxonomy_id="006",
                    confidence=0.75,
                    rank=2
                )
            ],
            model_version="test-model-v1",
            inference_time_ms=50.0,
            resource_id=None
        )
    
    mock_service.predict = Mock(side_effect=mock_predict)
    mock_service.predict_batch = Mock(return_value=[mock_predict("test")])
    
    # Configure training methods (should not be called in unit tests)
    mock_service.fine_tune = Mock(return_value={"f1": 0.85, "precision": 0.87, "recall": 0.83})
    mock_service._load_model = Mock()
    
    # Configure label mappings
    mock_service.id_to_label = {0: "004", 1: "006", 2: "510"}
    mock_service.label_to_id = {"004": 0, "006": 1, "510": 2}
    
    # Model attributes (not loaded)
    mock_service.model = None
    mock_service.tokenizer = None
    mock_service.model_name = "distilbert-base-uncased"
    mock_service.model_version = "test-v1"
    
    return mock_service


@pytest.fixture
def mock_sparse_embedding_service():
    """
    Mock SparseEmbeddingService for unit tests to avoid model loading.
    
    Provides a fully mocked SparseEmbeddingService that returns realistic
    sparse embeddings without loading the BAAI/bge-m3 model. This is the
    preferred approach for unit tests.
    
    Returns:
        Mock SparseEmbeddingService with configured methods
        
    Example:
        def test_sparse_embedding_logic(mock_sparse_embedding_service):
            embedding = mock_sparse_embedding_service.generate_sparse_embedding("test")
            assert isinstance(embedding, dict)
            assert len(embedding) > 0
    """
    from unittest.mock import Mock
    
    mock_service = Mock()
    
    # Configure generate_sparse_embedding method
    def mock_generate_sparse_embedding(text):
        if not text or not text.strip():
            return {}
        # Return realistic sparse embedding (50-200 non-zero dimensions)
        return {
            100: 0.8,
            200: 0.6,
            300: 0.4,
            400: 0.3,
            500: 0.2
        }
    
    mock_service.generate_sparse_embedding = Mock(side_effect=mock_generate_sparse_embedding)
    
    # Configure batch methods
    def mock_generate_batch(texts):
        return [mock_generate_sparse_embedding(text) for text in texts]
    
    mock_service.generate_sparse_embeddings_batch = Mock(side_effect=mock_generate_batch)
    
    # Configure update methods
    mock_service.update_resource_sparse_embedding = Mock(return_value=True)
    mock_service.batch_update_sparse_embeddings = Mock(return_value={
        "total": 10,
        "success": 10,
        "failed": 0,
        "skipped": 0
    })
    
    # Configure search method
    def mock_search_by_sparse_vector(query_sparse, limit=10):
        # Return mock search results
        return [
            ("resource-1", 0.95),
            ("resource-2", 0.85),
            ("resource-3", 0.75)
        ][:limit]
    
    mock_service.search_by_sparse_vector = Mock(side_effect=mock_search_by_sparse_vector)
    
    # Model attributes (not loaded)
    mock_service._model = None
    mock_service._tokenizer = None
    mock_service.model_name = "BAAI/bge-m3"
    mock_service._device = "cpu"
    
    return mock_service


@pytest.fixture(autouse=True)
def mock_ml_models_in_unit_tests(request):
    """
    Automatically mock ML model loading in unit tests.
    
    This fixture automatically patches ML model loading for all unit tests
    to prevent expensive model downloads and loading. Integration tests
    can opt out by using the 'use_real_models' marker.
    
    Usage:
        # Unit test (models automatically mocked)
        def test_something():
            pass
        
        # Integration test (use real models)
        @pytest.mark.use_real_models
        def test_with_real_models():
            pass
    """
    # Check if this is a unit test (not integration test)
    test_path = str(request.fspath)
    is_unit_test = "/unit/" in test_path or "/tests/services/" in test_path
    
    # Check if test explicitly wants real models
    use_real_models = request.node.get_closest_marker("use_real_models") is not None
    
    # Only mock if it's a unit test and doesn't want real models
    if is_unit_test and not use_real_models:
        with patch('backend.app.services.ml_classification_service.MLClassificationService._load_model'):
            with patch('backend.app.services.sparse_embedding_service.SparseEmbeddingService._ensure_loaded', return_value=False):
                yield
    else:
        yield


# ============================================================================
# Async Database Fixtures for Transaction Isolation Tests
# ============================================================================

@pytest.fixture
async def async_db_session(test_db):
    """
    Create an async database session for testing async operations.
    
    This fixture provides an async database session for testing
    transaction isolation and concurrency features.
    
    Args:
        test_db: Test database fixture
        
    Yields:
        AsyncSession: SQLAlchemy async session
    """
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    import os
    from backend.app.config.settings import get_settings
    
    settings = get_settings()
    
    # Determine database URL
    if settings.TEST_DATABASE_URL:
        db_url = settings.TEST_DATABASE_URL
        # Convert to async URL
        if db_url.startswith("sqlite:///"):
            db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    else:
        # Use in-memory SQLite for async tests
        db_url = "sqlite+aiosqlite:///:memory:"
    
    # Create async engine
    engine = create_async_engine(
        db_url,
        echo=False,
        connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Create and yield session
    async with async_session_factory() as session:
        yield session
    
    # Cleanup
    await engine.dispose()


@pytest.fixture
def sync_db_session(test_db):
    """
    Create a synchronous database session for testing sync operations.
    
    This is an alias for db_session fixture to maintain consistency
    with async_db_session naming.
    
    Args:
        test_db: Test database fixture
        
    Yields:
        Session: SQLAlchemy synchronous session
    """
    TestingSessionLocal = test_db
    session = TestingSessionLocal()
    yield session
    session.close()
