"""Test configuration and fixtures for Phase 1 tests."""

import pytest
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.database.base import Base, get_db, get_sync_db
from backend.app.main import app


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def test_db():
    """Create a file-based SQLite database for testing."""
    import tempfile
    import os
    
    # Create a temporary file for the database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        engine = create_engine(f"sqlite:///{temp_db.name}", echo=False)
        Base.metadata.create_all(engine)
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
        import numpy as np
        
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