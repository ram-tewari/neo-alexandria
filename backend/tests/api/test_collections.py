"""
Integration tests for Collection Management System.

This module tests the collection CRUD operations, resource management,
and collection-based recommendations.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.base import Base
from backend.app.database.models import Resource
from backend.app.services.collection_service import CollectionService
from backend.app.schemas.collection import CollectionUpdate


@pytest.fixture
def test_db():
    """Create a temporary in-memory database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def collection_service(test_db):
    """Create a collection service instance."""
    return CollectionService(test_db)


@pytest.fixture
def sample_resources(test_db):
    """Create sample resources for testing."""
    resources = []
    for i in range(5):
        resource = Resource(
            title=f"Test Resource {i}",
            description=f"Description for resource {i}",
            type="article",
            quality_score=0.8,
            embedding=[0.1 * i, 0.2 * i, 0.3 * i]  # Simple test embeddings
        )
        test_db.add(resource)
        resources.append(resource)
    
    test_db.commit()
    return resources


def test_create_collection(collection_service):
    """Test creating a new collection."""
    collection = collection_service.create_collection(
        name="My Research Collection",
        description="A collection of ML papers",
        owner_id="user123",
        visibility="private"
    )
    
    assert collection.id is not None
    assert collection.name == "My Research Collection"
    assert collection.owner_id == "user123"
    assert collection.visibility == "private"
    assert collection.embedding is None  # No resources yet


def test_add_resources_to_collection(collection_service, sample_resources):
    """Test adding resources to a collection."""
    # Create collection
    collection = collection_service.create_collection(
        name="Test Collection",
        description="Test",
        owner_id="user123"
    )
    
    # Add resources
    resource_ids = [r.id for r in sample_resources[:3]]
    added_count = collection_service.add_resources_to_collection(
        collection_id=collection.id,
        resource_ids=resource_ids,
        owner_id="user123"
    )
    
    assert added_count == 3
    
    # Verify resources were added
    resources, total = collection_service.get_collection_resources(
        collection_id=collection.id,
        owner_id="user123"
    )
    
    assert total == 3
    assert len(resources) == 3


def test_remove_resources_from_collection(collection_service, sample_resources):
    """Test removing resources from a collection."""
    # Create collection and add resources
    collection = collection_service.create_collection(
        name="Test Collection",
        description="Test",
        owner_id="user123"
    )
    
    resource_ids = [r.id for r in sample_resources]
    collection_service.add_resources_to_collection(
        collection_id=collection.id,
        resource_ids=resource_ids,
        owner_id="user123"
    )
    
    # Remove some resources
    remove_ids = [sample_resources[0].id, sample_resources[1].id]
    removed_count = collection_service.remove_resources_from_collection(
        collection_id=collection.id,
        resource_ids=remove_ids,
        owner_id="user123"
    )
    
    assert removed_count == 2
    
    # Verify resources were removed
    resources, total = collection_service.get_collection_resources(
        collection_id=collection.id,
        owner_id="user123"
    )
    
    assert total == 3  # 5 - 2 = 3


def test_compute_collection_embedding(collection_service, sample_resources):
    """Test computing collection embedding from member resources."""
    # Create collection and add resources
    collection = collection_service.create_collection(
        name="Test Collection",
        description="Test",
        owner_id="user123"
    )
    
    resource_ids = [r.id for r in sample_resources[:3]]
    collection_service.add_resources_to_collection(
        collection_id=collection.id,
        resource_ids=resource_ids,
        owner_id="user123"
    )
    
    # Compute embedding
    embedding = collection_service.compute_collection_embedding(collection.id)
    
    assert embedding is not None
    assert len(embedding) == 3  # Same dimension as resource embeddings
    assert all(isinstance(x, float) for x in embedding)
    
    # Verify embedding was stored
    updated_collection = collection_service.get_collection(collection.id)
    assert updated_collection.embedding is not None


def test_find_similar_resources(collection_service, sample_resources):
    """Test finding resources similar to a collection."""
    # Create collection with some resources
    collection = collection_service.create_collection(
        name="Test Collection",
        description="Test",
        owner_id="user123"
    )
    
    # Add first 2 resources to collection
    resource_ids = [r.id for r in sample_resources[:2]]
    collection_service.add_resources_to_collection(
        collection_id=collection.id,
        resource_ids=resource_ids,
        owner_id="user123"
    )
    
    # Find similar resources (should find remaining resources)
    similar = collection_service.find_similar_resources(
        collection_id=collection.id,
        owner_id="user123",
        limit=10,
        min_similarity=0.0,  # Low threshold for test
        exclude_collection_resources=True
    )
    
    # Should find the 3 resources not in collection
    assert len(similar) <= 3
    
    # Verify structure
    if similar:
        assert "resource_id" in similar[0]
        assert "title" in similar[0]
        assert "similarity_score" in similar[0]


def test_hierarchical_collections(collection_service):
    """Test creating hierarchical collections (parent/subcollections)."""
    # Create parent collection
    parent = collection_service.create_collection(
        name="Parent Collection",
        description="Parent",
        owner_id="user123"
    )
    
    # Create child collection
    child = collection_service.create_collection(
        name="Child Collection",
        description="Child",
        owner_id="user123",
        parent_id=parent.id
    )
    
    assert child.parent_id == parent.id
    
    # List root collections (should only show parent)
    collections, total = collection_service.list_collections(
        owner_id="user123",
        parent_id=None
    )
    
    assert total == 1
    assert collections[0].id == parent.id
    
    # List child collections
    collections, total = collection_service.list_collections(
        owner_id="user123",
        parent_id=parent.id
    )
    
    assert total == 1
    assert collections[0].id == child.id


def test_update_collection(collection_service):
    """Test updating collection metadata."""
    # Create collection
    collection = collection_service.create_collection(
        name="Original Name",
        description="Original Description",
        owner_id="user123",
        visibility="private"
    )
    
    # Update collection
    updates = CollectionUpdate(
        name="Updated Name",
        description="Updated Description",
        visibility="public"
    )
    
    updated = collection_service.update_collection(
        collection_id=collection.id,
        owner_id="user123",
        updates=updates
    )
    
    assert updated.name == "Updated Name"
    assert updated.description == "Updated Description"
    assert updated.visibility == "public"


def test_delete_collection(collection_service, sample_resources):
    """Test deleting a collection."""
    # Create collection with resources
    collection = collection_service.create_collection(
        name="Test Collection",
        description="Test",
        owner_id="user123"
    )
    
    resource_ids = [r.id for r in sample_resources[:2]]
    collection_service.add_resources_to_collection(
        collection_id=collection.id,
        resource_ids=resource_ids,
        owner_id="user123"
    )
    
    # Delete collection
    collection_service.delete_collection(
        collection_id=collection.id,
        owner_id="user123"
    )
    
    # Verify collection is deleted
    deleted = collection_service.get_collection(collection.id, owner_id="user123")
    assert deleted is None


def test_access_control(collection_service):
    """Test collection access control."""
    # Create collection for user1
    collection = collection_service.create_collection(
        name="User1 Collection",
        description="Private collection",
        owner_id="user1",
        visibility="private"
    )
    
    # User2 should not be able to access private collection
    accessed = collection_service.get_collection(collection.id, owner_id="user2")
    assert accessed is None
    
    # Update to public
    updates = CollectionUpdate(visibility="public")
    collection_service.update_collection(
        collection_id=collection.id,
        owner_id="user1",
        updates=updates
    )
    
    # Now user2 should be able to access
    accessed = collection_service.get_collection(collection.id, owner_id="user2")
    assert accessed is not None
    assert accessed.id == collection.id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
