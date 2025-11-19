"""
Neo Alexandria 2.0 - Phase 7 Collection Tests

Test suite for collection management functionality.
"""

import pytest

from backend.app.database.models import Resource
from backend.app.services.collection_service import CollectionService


# db_session fixture is now in integration/conftest.py


@pytest.fixture
def sample_resources(db_session):
    """Create sample resources for testing."""
    resources = []
    for i in range(5):
        resource = Resource(
            title=f"Test Resource {i}",
            source=f"https://example.com/resource{i}",
            read_status="unread",
            quality_score=0.8,
            embedding=[0.1 * i, 0.2 * i, 0.3 * i]  # Simple test embeddings
        )
        db_session.add(resource)
        resources.append(resource)
    
    db_session.commit()
    for r in resources:
        db_session.refresh(r)
    
    return resources


class TestCollectionCreation:
    """Test collection creation and validation."""
    
    def test_create_collection(self, db_session):
        """Test creating a basic collection."""
        service = CollectionService(db_session)
        
        collection = service.create_collection(
            owner_id="user123",
            name="My Collection",
            description="Test collection",
            visibility="private"
        )
        
        assert collection.id is not None
        assert collection.name == "My Collection"
        assert collection.owner_id == "user123"
        assert collection.visibility == "private"
    
    def test_create_collection_with_parent(self, db_session):
        """Test creating a nested collection."""
        service = CollectionService(db_session)
        
        # Create parent
        parent = service.create_collection(
            owner_id="user123",
            name="Parent Collection",
            visibility="private"
        )
        
        # Create child
        child = service.create_collection(
            owner_id="user123",
            name="Child Collection",
            visibility="private",
            parent_id=str(parent.id)
        )
        
        assert child.parent_id == parent.id
    
    def test_create_collection_invalid_name(self, db_session):
        """Test validation of collection name."""
        service = CollectionService(db_session)
        
        with pytest.raises(ValueError, match="at least 1 character"):
            service.create_collection(
                owner_id="user123",
                name="",
                visibility="private"
            )
    
    def test_create_collection_invalid_visibility(self, db_session):
        """Test validation of visibility value."""
        service = CollectionService(db_session)
        
        with pytest.raises(ValueError, match="Visibility must be one of"):
            service.create_collection(
                owner_id="user123",
                name="Test",
                visibility="invalid"
            )


class TestCollectionAccess:
    """Test collection access control."""
    
    def test_get_private_collection_as_owner(self, db_session):
        """Test accessing private collection as owner."""
        service = CollectionService(db_session)
        
        collection = service.create_collection(
            owner_id="user123",
            name="Private Collection",
            visibility="private"
        )
        
        retrieved = service.get_collection(str(collection.id), "user123")
        assert retrieved.id == collection.id
    
    def test_get_private_collection_as_non_owner(self, db_session):
        """Test accessing private collection as non-owner."""
        service = CollectionService(db_session)
        
        collection = service.create_collection(
            owner_id="user123",
            name="Private Collection",
            visibility="private"
        )
        
        with pytest.raises(ValueError, match="Access denied"):
            service.get_collection(str(collection.id), "user456")
    
    def test_get_public_collection(self, db_session):
        """Test accessing public collection."""
        service = CollectionService(db_session)
        
        collection = service.create_collection(
            owner_id="user123",
            name="Public Collection",
            visibility="public"
        )
        
        # Should be accessible to anyone
        retrieved = service.get_collection(str(collection.id), "user456")
        assert retrieved.id == collection.id


class TestResourceMembership:
    """Test adding and removing resources from collections."""
    
    def test_add_resources(self, db_session, sample_resources):
        """Test adding resources to a collection."""
        service = CollectionService(db_session)
        
        collection = service.create_collection(
            owner_id="user123",
            name="Test Collection",
            visibility="private"
        )
        
        resource_ids = [str(r.id) for r in sample_resources[:3]]
        
        updated = service.add_resources(
            collection_id=str(collection.id),
            user_id="user123",
            resource_ids=resource_ids
        )
        
        assert len(updated.resources) == 3
    
    def test_add_resources_duplicate(self, db_session, sample_resources):
        """Test adding duplicate resources (should be idempotent)."""
        service = CollectionService(db_session)
        
        collection = service.create_collection(
            owner_id="user123",
            name="Test Collection",
            visibility="private"
        )
        
        resource_ids = [str(sample_resources[0].id)]
        
        # Add once
        service.add_resources(
            collection_id=str(collection.id),
            user_id="user123",
            resource_ids=resource_ids
        )
        
        # Add again (should not duplicate)
        updated = service.add_resources(
            collection_id=str(collection.id),
            user_id="user123",
            resource_ids=resource_ids
        )
        
        assert len(updated.resources) == 1
    
    def test_remove_resources(self, db_session, sample_resources):
        """Test removing resources from a collection."""
        service = CollectionService(db_session)
        
        collection = service.create_collection(
            owner_id="user123",
            name="Test Collection",
            visibility="private"
        )
        
        resource_ids = [str(r.id) for r in sample_resources[:3]]
        
        # Add resources
        service.add_resources(
            collection_id=str(collection.id),
            user_id="user123",
            resource_ids=resource_ids
        )
        
        # Remove one resource
        updated = service.remove_resources(
            collection_id=str(collection.id),
            user_id="user123",
            resource_ids=[resource_ids[0]]
        )
        
        assert len(updated.resources) == 2
    
    def test_add_resources_non_owner(self, db_session, sample_resources):
        """Test that non-owners cannot add resources."""
        service = CollectionService(db_session)
        
        collection = service.create_collection(
            owner_id="user123",
            name="Test Collection",
            visibility="private"
        )
        
        resource_ids = [str(sample_resources[0].id)]
        
        with pytest.raises(ValueError, match="Access denied"):
            service.add_resources(
                collection_id=str(collection.id),
                user_id="user456",
                resource_ids=resource_ids
            )


class TestCollectionEmbedding:
    """Test aggregate embedding computation."""
    
    def test_recompute_embedding(self, db_session, sample_resources):
        """Test computing aggregate embedding from resources."""
        service = CollectionService(db_session)
        
        collection = service.create_collection(
            owner_id="user123",
            name="Test Collection",
            visibility="private"
        )
        
        # Add resources with embeddings
        resource_ids = [str(r.id) for r in sample_resources[:3]]
        service.add_resources(
            collection_id=str(collection.id),
            user_id="user123",
            resource_ids=resource_ids
        )
        
        # Recompute embedding
        service.recompute_embedding(str(collection.id))
        
        # Refresh collection
        db_session.refresh(collection)
        
        # Should have an embedding now
        assert collection.embedding is not None
        assert len(collection.embedding) > 0
    
    def test_recompute_embedding_empty_collection(self, db_session):
        """Test embedding computation for empty collection."""
        service = CollectionService(db_session)
        
        collection = service.create_collection(
            owner_id="user123",
            name="Empty Collection",
            visibility="private"
        )
        
        # Recompute embedding (should be None)
        service.recompute_embedding(str(collection.id))
        
        # Refresh collection
        db_session.refresh(collection)
        
        assert collection.embedding is None


class TestCollectionRecommendations:
    """Test collection-based recommendations."""
    
    def test_get_recommendations(self, db_session, sample_resources):
        """Test getting recommendations for a collection."""
        service = CollectionService(db_session)
        
        # Create collection with some resources
        collection = service.create_collection(
            owner_id="user123",
            name="Test Collection",
            visibility="private"
        )
        
        resource_ids = [str(r.id) for r in sample_resources[:2]]
        service.add_resources(
            collection_id=str(collection.id),
            user_id="user123",
            resource_ids=resource_ids
        )
        
        # Recompute embedding
        service.recompute_embedding(str(collection.id))
        
        # Get recommendations
        recommendations = service.get_collection_recommendations(
            collection_id=str(collection.id),
            user_id="user123",
            limit=5
        )
        
        assert "resource_recommendations" in recommendations
        assert "collection_recommendations" in recommendations
    
    def test_get_recommendations_no_embedding(self, db_session):
        """Test recommendations for collection without embedding."""
        service = CollectionService(db_session)
        
        collection = service.create_collection(
            owner_id="user123",
            name="Empty Collection",
            visibility="private"
        )
        
        recommendations = service.get_collection_recommendations(
            collection_id=str(collection.id),
            user_id="user123",
            limit=5
        )
        
        assert len(recommendations["resource_recommendations"]) == 0
        assert len(recommendations["collection_recommendations"]) == 0


class TestHierarchyValidation:
    """Test hierarchical collection validation."""
    
    def test_validate_hierarchy_none_parent(self, db_session):
        """Test that None parent_id is valid (top-level collection)."""
        service = CollectionService(db_session)
        
        collection = service.create_collection(
            owner_id="user123",
            name="Top Level",
            visibility="private"
        )
        
        # Should return True for None parent
        result = service.validate_hierarchy(str(collection.id), None)
        assert result is True
    
    def test_validate_hierarchy_valid_parent(self, db_session):
        """Test that valid parent assignment works."""
        service = CollectionService(db_session)
        
        parent = service.create_collection(
            owner_id="user123",
            name="Parent",
            visibility="private"
        )
        
        child = service.create_collection(
            owner_id="user123",
            name="Child",
            visibility="private"
        )
        
        # Should return True for valid parent
        result = service.validate_hierarchy(str(child.id), str(parent.id))
        assert result is True
    
    def test_prevent_circular_reference_direct(self, db_session):
        """Test that direct circular references are prevented (A -> A)."""
        service = CollectionService(db_session)
        
        collection = service.create_collection(
            owner_id="user123",
            name="Collection",
            visibility="private"
        )
        
        # Try to make collection its own parent
        with pytest.raises(ValueError, match="Circular reference"):
            service.validate_hierarchy(str(collection.id), str(collection.id))
    
    def test_prevent_circular_reference_two_level(self, db_session):
        """Test that circular references are prevented (A -> B -> A)."""
        service = CollectionService(db_session)
        
        # Create parent and child
        parent = service.create_collection(
            owner_id="user123",
            name="Parent",
            visibility="private"
        )
        
        child = service.create_collection(
            owner_id="user123",
            name="Child",
            visibility="private",
            parent_id=str(parent.id)
        )
        
        # Try to make parent a child of child (circular reference)
        with pytest.raises(ValueError, match="Circular reference"):
            service.update_collection(
                collection_id=str(parent.id),
                user_id="user123",
                updates={"parent_id": str(child.id)}
            )
    
    def test_prevent_circular_reference_multi_level(self, db_session):
        """Test that circular references are prevented in deep hierarchies (A -> B -> C -> A)."""
        service = CollectionService(db_session)
        
        # Create a 3-level hierarchy
        level1 = service.create_collection(
            owner_id="user123",
            name="Level 1",
            visibility="private"
        )
        
        level2 = service.create_collection(
            owner_id="user123",
            name="Level 2",
            visibility="private",
            parent_id=str(level1.id)
        )
        
        level3 = service.create_collection(
            owner_id="user123",
            name="Level 3",
            visibility="private",
            parent_id=str(level2.id)
        )
        
        # Try to make level1 a child of level3 (circular reference)
        with pytest.raises(ValueError, match="Circular reference"):
            service.validate_hierarchy(str(level1.id), str(level3.id))
    
    def test_hierarchy_depth_limit(self, db_session):
        """Test that hierarchy traversal is limited to prevent infinite loops."""
        service = CollectionService(db_session)
        
        # Create a 10-level hierarchy (this should work fine)
        collections = []
        parent_id = None
        
        for i in range(10):
            collection = service.create_collection(
                owner_id="user123",
                name=f"Level {i+1}",
                visibility="private",
                parent_id=parent_id
            )
            collections.append(collection)
            parent_id = str(collection.id)
        
        # Verify the 10-level hierarchy was created successfully
        assert len(collections) == 10
        
        # The depth limit is for traversal safety, not hierarchy depth restriction
        # Creating an 11th level should work as long as traversal doesn't exceed limit
        level11 = service.create_collection(
            owner_id="user123",
            name="Level 11",
            visibility="private",
            parent_id=parent_id
        )
        assert level11.parent_id == collections[-1].id
    
    def test_valid_multi_level_hierarchy(self, db_session):
        """Test that valid multi-level hierarchies work correctly."""
        service = CollectionService(db_session)
        
        # Create a 3-level hierarchy
        level1 = service.create_collection(
            owner_id="user123",
            name="Level 1",
            visibility="private"
        )
        
        level2 = service.create_collection(
            owner_id="user123",
            name="Level 2",
            visibility="private",
            parent_id=str(level1.id)
        )
        
        level3 = service.create_collection(
            owner_id="user123",
            name="Level 3",
            visibility="private",
            parent_id=str(level2.id)
        )
        
        # Verify the hierarchy
        assert level3.parent_id == level2.id
        assert level2.parent_id == level1.id
        assert level1.parent_id is None
    
    def test_reparent_collection(self, db_session):
        """Test moving a collection to a different parent."""
        service = CollectionService(db_session)
        
        # Create two potential parents and a child
        parent1 = service.create_collection(
            owner_id="user123",
            name="Parent 1",
            visibility="private"
        )
        
        parent2 = service.create_collection(
            owner_id="user123",
            name="Parent 2",
            visibility="private"
        )
        
        child = service.create_collection(
            owner_id="user123",
            name="Child",
            visibility="private",
            parent_id=str(parent1.id)
        )
        
        # Move child to parent2
        updated = service.update_collection(
            collection_id=str(child.id),
            user_id="user123",
            updates={"parent_id": str(parent2.id)}
        )
        
        assert updated.parent_id == parent2.id
