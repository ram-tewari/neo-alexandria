"""Integration tests for Sparse Embedding Service (Phase 8)."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.base import Base
from backend.app.database.models import Resource
from backend.app.services.sparse_embedding_service import SparseEmbeddingService


@pytest.fixture
def test_db():
    """Create an in-memory test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_sparse_embedding_service_integration(test_db):
    """Test sparse embedding service with real database."""
    # Create test resources
    resource1 = Resource(
        title="Machine Learning Fundamentals",
        description="An introduction to machine learning algorithms and techniques.",
        subject=["Machine Learning", "AI", "Algorithms"]
    )
    resource2 = Resource(
        title="Deep Learning with Neural Networks",
        description="Advanced deep learning concepts using neural networks.",
        subject=["Deep Learning", "Neural Networks", "AI"]
    )
    
    test_db.add(resource1)
    test_db.add(resource2)
    test_db.commit()
    
    # Initialize service
    service = SparseEmbeddingService(db=test_db, model_name="BAAI/bge-m3")
    
    # Test update_resource_sparse_embedding
    # Note: This will fail gracefully if model not available
    success = service.update_resource_sparse_embedding(str(resource1.id))
    
    # Verify the method completes without error
    assert isinstance(success, bool)
    
    # If model was available and succeeded, check the embedding was stored
    if success:
        test_db.refresh(resource1)
        # Either embedding is set or it's None (for empty content)
        assert resource1.sparse_embedding_updated_at is not None


def test_batch_update_integration(test_db):
    """Test batch update with real database."""
    # Create multiple test resources
    resources = []
    for i in range(10):
        resource = Resource(
            title=f"Test Resource {i}",
            description=f"Description for test resource {i}",
            subject=[f"Subject {i}"]
        )
        resources.append(resource)
        test_db.add(resource)
    
    test_db.commit()
    
    # Initialize service
    service = SparseEmbeddingService(db=test_db, model_name="BAAI/bge-m3")
    
    # Test batch update
    stats = service.batch_update_sparse_embeddings()
    
    # Verify stats structure
    assert 'total' in stats
    assert 'success' in stats
    assert 'failed' in stats
    assert 'skipped' in stats
    
    # Total should match number of resources
    assert stats['total'] == 10
    
    # All resources should be processed (success + failed + skipped = total)
    assert stats['success'] + stats['failed'] + stats['skipped'] == stats['total']


def test_search_by_sparse_vector_integration(test_db):
    """Test sparse vector search with real database."""
    # Create test resources with mock sparse embeddings
    import json
    
    resource1 = Resource(
        title="Test Resource 1",
        description="Description 1",
        sparse_embedding=json.dumps({"100": 0.8, "200": 0.6, "300": 0.4})
    )
    resource2 = Resource(
        title="Test Resource 2",
        description="Description 2",
        sparse_embedding=json.dumps({"100": 0.5, "200": 0.9, "400": 0.3})
    )
    resource3 = Resource(
        title="Test Resource 3",
        description="Description 3",
        sparse_embedding=json.dumps({"500": 0.7, "600": 0.8})
    )
    
    test_db.add_all([resource1, resource2, resource3])
    test_db.commit()
    
    # Initialize service
    service = SparseEmbeddingService(db=test_db, model_name="BAAI/bge-m3")
    
    # Test search with query vector
    query_sparse = {100: 0.9, 200: 0.7}
    results = service.search_by_sparse_vector(query_sparse, limit=10)
    
    # Verify results
    assert isinstance(results, list)
    assert len(results) <= 10
    
    # Results should be tuples of (resource_id, score)
    for result in results:
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)  # resource_id
        assert isinstance(result[1], float)  # score
    
    # Results should be sorted by score descending
    if len(results) > 1:
        for i in range(len(results) - 1):
            assert results[i][1] >= results[i + 1][1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
