"""Test configuration and fixtures for Phase 1 tests."""

import pytest
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import patch
import logging

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.database.base import Base, get_db, get_sync_db
from backend.app.main import app

# Configure logging for database initialization
logger = logging.getLogger(__name__)


def ensure_database_schema(engine):
    """
    Ensure database schema is current before tests run.
    
    This helper verifies that all model fields exist in the database schema
    and creates/updates tables as needed. It handles:
    - Creating all tables if they don't exist
    - Applying Alembic migrations to ensure schema is current
    - Verifying critical fields (sparse_embedding, description, publisher)
    - Applying schema updates for test databases
    
    Args:
        engine: SQLAlchemy engine instance
    """
    try:
        # First, ensure all tables exist
        Base.metadata.create_all(engine)
        
        # Apply Alembic migrations to ensure schema is current
        try:
            from alembic import command
            from alembic.config import Config
            import os
            
            # Get the backend directory path
            backend_dir = Path(__file__).parent.parent
            alembic_ini_path = backend_dir / "alembic.ini"
            
            if alembic_ini_path.exists():
                # Create Alembic config
                alembic_cfg = Config(str(alembic_ini_path))
                
                # Set the database URL for this test engine
                alembic_cfg.set_main_option("sqlalchemy.url", str(engine.url))
                
                # Apply all migrations up to head
                with engine.begin() as connection:
                    alembic_cfg.attributes['connection'] = connection
                    command.upgrade(alembic_cfg, "head")
                
                logger.info("Alembic migrations applied successfully")
            else:
                logger.warning(f"Alembic config not found at {alembic_ini_path}")
        except Exception as migration_error:
            logger.warning(f"Could not apply Alembic migrations: {migration_error}")
            # Continue without migrations - tables are already created
        
        # Verify critical Resource model fields exist
        inspector = inspect(engine)
        
        if 'resources' in inspector.get_table_names():
            columns = {col['name'] for col in inspector.get_columns('resources')}
            required_fields = {'sparse_embedding', 'description', 'publisher'}
            missing_fields = required_fields - columns
            
            if missing_fields:
                logger.warning(f"Missing fields in resources table after migrations: {missing_fields}")
                # Drop and recreate to ensure schema is current
                Base.metadata.drop_all(engine)
                Base.metadata.create_all(engine)
                logger.info("Database schema recreated with current model definitions")
            else:
                logger.debug("All required Resource fields verified in database schema")
        else:
            logger.info("Resources table created")
            
    except Exception as e:
        logger.error(f"Error ensuring database schema: {e}")
        # Fallback: try to create all tables
        try:
            Base.metadata.create_all(engine)
        except Exception as create_error:
            logger.error(f"Failed to create tables: {create_error}")
            raise


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def test_db():
    """
    Create a file-based SQLite database for testing with current schema.
    
    This fixture:
    - Creates a temporary SQLite database file
    - Ensures all tables are created with current model definitions
    - Verifies critical fields exist (sparse_embedding, description, publisher)
    - Provides session factory for test database operations
    - Cleans up database file after tests complete
    """
    import tempfile
    import os
    
    # Create a temporary file for the database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        engine = create_engine(f"sqlite:///{temp_db.name}", echo=False)
        
        # Use the database initialization helper to ensure schema is current
        ensure_database_schema(engine)
        
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
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
    finally:
        # Clean up the temporary database file
        try:
            os.unlink(temp_db.name)
        except OSError:
            pass


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
def db_session(test_db):
    """
    Create a database session for unit tests.
    
    This fixture provides a session that can be used in unit tests
    that need database access. It uses the test_db fixture to ensure
    proper schema initialization.
    """
    session = test_db()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def seeded_resources(test_db):
    """Create seeded resources for testing."""
    from datetime import datetime, timezone, timedelta
    from backend.app.database.models import Resource
    
    TestingSessionLocal = test_db
    db = TestingSessionLocal()
    now = datetime.now(timezone.utc)
    items = []
    for i in range(10):
        r = Resource(
            title=f"Item {i}",
            description=f"Desc {i}",
            language="en" if i % 2 == 0 else "es",
            type="article",
            classification_code="000" if i % 2 == 0 else "400",  # Updated to new codes
            subject=["Artificial Intelligence", "Machine Learning"] if i % 2 == 0 else ["Language", "Linguistics"],
            read_status="unread" if i < 5 else "in_progress",
            quality_score=0.3 + i * 0.08,
            date_created=now - timedelta(days=30 - i),
            date_modified=now - timedelta(days=15 - i),
        )
        db.add(r)
        items.append(r)
    db.commit()
    for r in items:
        db.refresh(r)
    yield [str(r.id) for r in items]
    # Cleanup
    for r in items:
        db.delete(r)
    db.commit()


# ============================================================================
# Phase 5.5 Recommendation Testing Fixtures
# ============================================================================

@pytest.fixture
def recommendation_test_data(test_db):
    """Create comprehensive test data for recommendation system testing."""
    from datetime import datetime, timezone, timedelta
    from backend.app.database.models import Resource, AuthoritySubject
    
    db = test_db()
    now = datetime.now(timezone.utc)
    
    # Create authority subjects with varying usage counts
    subjects_data = [
        ("Machine Learning", 100),
        ("Python", 80),
        ("Artificial Intelligence", 60),
        ("Data Science", 40),
        ("Neural Networks", 30),
        ("Deep Learning", 25),
        ("Natural Language Processing", 20),
        ("Computer Vision", 15),
        ("Statistics", 10),
        ("Mathematics", 5),
    ]
    
    authority_subjects = []
    for name, count in subjects_data:
        subject = AuthoritySubject(
            canonical_form=name,
            variants=[name.lower(), name.replace(" ", "_")],
            usage_count=count
        )
        db.add(subject)
        authority_subjects.append(subject)
    
    # Create high-quality resources with embeddings
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
            "subject": ["Deep Learning", "Neural Networks"],
            "quality_score": 0.88,
            "embedding": [0.7, 0.3, 0.0, 0.0, 0.0],
        },
        {
            "title": "Natural Language Processing Basics",
            "description": "Text processing and language models",
            "subject": ["Natural Language Processing", "Machine Learning"],
            "quality_score": 0.85,
            "embedding": [0.6, 0.4, 0.0, 0.0, 0.0],
        },
        {
            "title": "Computer Vision Applications",
            "description": "Image recognition and computer vision",
            "subject": ["Computer Vision", "Deep Learning"],
            "quality_score": 0.82,
            "embedding": [0.5, 0.5, 0.0, 0.0, 0.0],
        },
        # Lower quality resources
        {
            "title": "Basic Statistics",
            "description": "Introduction to statistical concepts",
            "subject": ["Statistics", "Mathematics"],
            "quality_score": 0.6,
            "embedding": [0.1, 0.1, 0.8, 0.0, 0.0],
        },
        {
            "title": "Cooking Basics",
            "description": "Unrelated topic for testing",
            "subject": ["Cooking", "Food"],
            "quality_score": 0.3,
            "embedding": [0.0, 0.0, 0.0, 0.0, 1.0],
        },
    ]
    
    resources = []
    for i, data in enumerate(resources_data):
        resource = Resource(
            title=data["title"],
            description=data["description"],
            subject=data["subject"],
            quality_score=data["quality_score"],
            embedding=data["embedding"],
            language="en",
            type="article",
            classification_code="004",
            read_status="unread",
            created_at=now - timedelta(days=10 - i),
            updated_at=now - timedelta(days=5 - i),
        )
        db.add(resource)
        resources.append(resource)
    
    db.commit()
    
    # Refresh all objects
    for subject in authority_subjects:
        db.refresh(subject)
    for resource in resources:
        db.refresh(resource)
    
    yield {
        "authority_subjects": authority_subjects,
        "resources": resources,
        "high_quality_resources": resources[:5],  # Top 5 by quality
        "low_quality_resources": resources[5:],   # Lower quality
    }
    
    # Cleanup
    for resource in resources:
        db.delete(resource)
    for subject in authority_subjects:
        db.delete(subject)
    db.commit()
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
    
    # Try to patch DDGS if it exists in recommendation_service
    # If it doesn't exist, skip the patch (recommendation service may not use DDGS)
    try:
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
    except AttributeError:
        # DDGS doesn't exist in recommendation_service, yield None
        # Tests using this fixture should handle None gracefully
        yield None


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
# Task 10: Improved Test Fixture Reliability
# ============================================================================

@pytest.fixture
def valid_resource(test_db):
    """
    Create a comprehensive resource fixture with all required fields populated.
    
    This fixture provides a resource with:
    - Non-zero quality_score (0.85)
    - Valid dense embedding (384-dimensional)
    - Valid sparse embedding (JSON string format)
    - All commonly tested fields populated
    - Proper session management (refreshed after commit)
    
    Requirements: 6.1, 6.2, 6.3, 6.4
    """
    from datetime import datetime, timezone
    from backend.app.database.models import Resource
    import json
    
    db = test_db()
    
    # Create resource with all commonly tested fields
    resource = Resource(
        # Core Dublin Core fields
        title="Comprehensive Test Resource",
        description="A detailed test resource with all fields populated for reliable testing",
        creator="Test Author",
        publisher="Test Publisher",
        contributor="Test Contributor",
        type="article",
        format="text/html",
        language="en",
        source="https://example.com/test-resource",
        identifier="test-resource-001",
        
        # Multi-valued fields
        subject=["Machine Learning", "Artificial Intelligence", "Data Science"],
        relation=["related-resource-001", "related-resource-002"],
        
        # Classification and status
        classification_code="004",  # Computer science
        read_status="unread",
        
        # Quality scores - non-zero for realistic testing
        quality_score=0.85,
        quality_accuracy=0.88,
        quality_completeness=0.90,
        quality_consistency=0.82,
        quality_timeliness=0.85,
        quality_relevance=0.87,
        quality_overall=0.85,
        quality_last_computed=datetime.now(timezone.utc),
        quality_computation_version="1.0",
        
        # Valid embeddings for vector operations
        embedding=[0.1] * 384,  # 384-dimensional dense embedding
        sparse_embedding=json.dumps({"1": 0.5, "42": 0.3, "100": 0.2}),  # Valid sparse embedding
        sparse_embedding_model="bge-m3",
        
        # Ingestion workflow - completed successfully
        ingestion_status="completed",
        ingestion_error=None,
        ingestion_started_at=datetime.now(timezone.utc),
        ingestion_completed_at=datetime.now(timezone.utc),
        
        # Scholarly metadata
        authors=json.dumps([{"name": "Test Author", "affiliation": "Test University"}]),
        affiliations=json.dumps(["Test University", "Research Institute"]),
        doi="10.1234/test.2024.001",
        publication_year=2024,
        journal="Test Journal of Computer Science",
        
        # Content structure
        equation_count=5,
        table_count=3,
        figure_count=2,
        reference_count=25,
        
        # Metadata quality
        metadata_completeness_score=0.95,
        extraction_confidence=0.92,
        requires_manual_review=False,
        
        # Quality outlier detection
        is_quality_outlier=False,
        outlier_score=None,
        needs_quality_review=False,
        
        # Summary quality
        summary_coherence=0.88,
        summary_consistency=0.85,
        summary_fluency=0.90,
        summary_relevance=0.87,
        
        # Timestamps
        date_created=datetime.now(timezone.utc),
        date_modified=datetime.now(timezone.utc),
    )
    
    db.add(resource)
    db.commit()
    db.refresh(resource)  # Keep object attached to session
    
    yield resource
    
    # Cleanup
    try:
        db.delete(resource)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


@pytest.fixture
def resource_with_file(test_db, tmp_path):
    """
    Create a resource fixture with an actual archive directory on disk.
    
    This fixture:
    - Creates a temporary archive directory with test files using tmp_path
    - Sets resource.identifier to the archive path
    - Creates required archive files (raw.html, text.txt, meta.json)
    - Ensures files exist and are readable
    - Cleans up files after test
    
    Requirements: 6.3
    """
    from datetime import datetime, timezone
    from backend.app.database.models import Resource
    import json
    
    db = test_db()
    
    # Create archive directory structure
    archive_dir = tmp_path / "test_archive"
    archive_dir.mkdir(exist_ok=True)
    
    # Create required archive files
    (archive_dir / "raw.html").write_text("<html><body>Test content</body></html>")
    (archive_dir / "text.txt").write_text("Test content extracted from HTML")
    (archive_dir / "meta.json").write_text(json.dumps({
        "url": "https://example.com/test",
        "title": "Resource with File",
        "extracted_at": datetime.now(timezone.utc).isoformat()
    }))
    
    # Create resource with identifier pointing to archive
    resource = Resource(
        title="Resource with File",
        description="Test resource with an actual archive directory on disk",
        publisher="Test Publisher",
        type="article",
        language="en",
        source="https://example.com/test",
        
        # Identifier stores the archive path
        identifier=str(archive_dir),
        
        # Other required fields
        subject=["Testing", "File Management"],
        quality_score=0.80,
        embedding=[0.1] * 384,
        sparse_embedding=json.dumps({"1": 0.5}),
        
        ingestion_status="completed",
        ingestion_completed_at=datetime.now(timezone.utc),
        
        classification_code="004",
        read_status="unread",
        
        date_created=datetime.now(timezone.utc),
        date_modified=datetime.now(timezone.utc),
    )
    
    db.add(resource)
    db.commit()
    db.refresh(resource)
    
    yield resource
    
    # Cleanup
    try:
        db.delete(resource)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
        # File cleanup is handled by tmp_path fixture


@pytest.fixture
def valid_ingestion_resource(test_db):
    """
    Create a resource fixture that will succeed during ingestion.
    
    This fixture provides a resource with:
    - Valid data that won't cause ingestion failures
    - Proper URL format
    - All required fields for successful processing
    - Expected 'completed' status after ingestion
    
    Requirements: 6.1, 6.5
    """
    from datetime import datetime, timezone
    from backend.app.database.models import Resource
    import json
    
    db = test_db()
    
    resource = Resource(
        # Valid URL for ingestion
        source="https://example.com/valid-article",
        identifier="valid-article-001",
        
        # Core fields
        title="Valid Ingestion Test Article",
        description="An article with valid data for successful ingestion testing",
        publisher="Reliable Publisher",
        creator="Test Author",
        type="article",
        language="en",
        
        # Multi-valued fields
        subject=["Computer Science", "Software Engineering"],
        
        # Quality and classification
        quality_score=0.75,
        classification_code="004",
        read_status="unread",
        
        # Valid embeddings
        embedding=[0.1] * 384,
        sparse_embedding=json.dumps({"1": 0.5, "10": 0.3}),
        sparse_embedding_model="bge-m3",
        
        # Ingestion status - will be updated during processing
        ingestion_status="pending",
        ingestion_error=None,
        
        # Timestamps
        date_created=datetime.now(timezone.utc),
        date_modified=datetime.now(timezone.utc),
    )
    
    db.add(resource)
    db.commit()
    db.refresh(resource)
    
    yield resource
    
    # Cleanup
    try:
        db.delete(resource)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()