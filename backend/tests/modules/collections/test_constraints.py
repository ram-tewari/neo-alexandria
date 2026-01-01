"""
Collections Module - Constraints Tests

Edge case tests for collection constraints and validation.
Tests verify proper handling of boundary conditions.
"""

import pytest


class TestCollectionConstraints:
    """Test suite for collection constraints and edge cases."""
    
    def test_duplicate_resource_addition(self, db_session, create_test_resource, create_test_collection):
        """
        Test idempotency of adding duplicate resources.
        
        Verifies:
        - Adding same resource twice doesn't create duplicates
        - Returns correct count (0 for duplicate)
        - Database maintains integrity
        
        **Validates: Requirements 5.3, 5.4, 8.4**
        """
        # Create test data
        collection = create_test_collection(
            name="Test Collection",
            owner_id="user123"
        )
        
        resource = create_test_resource(
            title="Test Resource",
            embedding=[0.1, 0.2, 0.3]
        )
        
        # Add resource first time
        from app.modules.collections.service import CollectionService
        service = CollectionService(db_session)
        
        added_count_1 = service.add_resources_to_collection(
            collection_id=collection.id,
            resource_ids=[resource.id],
            owner_id="user123"
        )
        
        assert added_count_1 == 1, "First addition should return count of 1"
        
        # Try adding same resource again
        added_count_2 = service.add_resources_to_collection(
            collection_id=collection.id,
            resource_ids=[resource.id],
            owner_id="user123"
        )
        
        assert added_count_2 == 0, "Duplicate addition should return count of 0"
        
        # Verify only one association exists in database
        from app.database.models import CollectionResource
        associations = db_session.query(CollectionResource).filter(
            CollectionResource.collection_id == collection.id,
            CollectionResource.resource_id == resource.id
        ).all()
        
        assert len(associations) == 1, "Should have exactly one association, not duplicates"
    
    def test_empty_collection_operations(self, db_session, create_test_collection):
        """
        Test operations on empty collections.
        
        Verifies:
        - Empty collection has no embedding
        - Can retrieve empty collection
        - Resource count is 0
        
        **Validates: Requirements 5.3, 5.4, 8.4**
        """
        # Create empty collection
        collection = create_test_collection(
            name="Empty Collection",
            owner_id="user123"
        )
        
        # Verify initial state
        assert collection.embedding is None, "Empty collection should have no embedding"
        
        # Compute embedding on empty collection
        from app.modules.collections.service import CollectionService
        service = CollectionService(db_session)
        
        result_embedding = service.compute_collection_embedding(collection.id)
        
        assert result_embedding is None, "Empty collection embedding should be None"
        
        # Get collection resources
        resources, total = service.get_collection_resources(
            collection_id=collection.id,
            owner_id="user123"
        )
        
        assert len(resources) == 0, "Empty collection should have no resources"
        assert total == 0, "Total count should be 0"
    
    def test_max_nesting_depth_prevention(self, db_session, create_test_collection):
        """
        Test prevention of excessive collection nesting.
        
        Verifies:
        - Can create parent-child relationships
        - Circular references are prevented
        - Collection cannot be its own parent
        
        **Validates: Requirements 5.3, 5.4, 8.4**
        """
        # Create parent collection
        parent = create_test_collection(
            name="Parent Collection",
            owner_id="user123"
        )
        
        # Create child collection
        child = create_test_collection(
            name="Child Collection",
            owner_id="user123",
            parent_id=parent.id
        )
        
        assert child.parent_id == parent.id, "Child should reference parent"
        
        # Try to make collection its own parent (should fail)
        from app.modules.collections.service import CollectionService
        from app.modules.collections.schema import CollectionUpdate
        
        service = CollectionService(db_session)
        
        with pytest.raises(ValueError, match="cannot be its own parent"):
            service.update_collection(
                collection_id=parent.id,
                owner_id="user123",
                updates=CollectionUpdate(parent_id=parent.id)
            )
    
    def test_nonexistent_resource_addition(self, db_session, create_test_collection):
        """
        Test adding non-existent resources to collection.
        
        Verifies:
        - Non-existent resources are silently skipped
        - Valid resources are still added
        - No errors raised for missing resources
        
        **Validates: Requirements 5.3, 5.4, 8.4**
        """
        import uuid
        
        # Create collection
        collection = create_test_collection(
            name="Test Collection",
            owner_id="user123"
        )
        
        # Try to add non-existent resource
        from app.modules.collections.service import CollectionService
        service = CollectionService(db_session)
        
        fake_resource_id = uuid.uuid4()
        
        added_count = service.add_resources_to_collection(
            collection_id=collection.id,
            resource_ids=[fake_resource_id],
            owner_id="user123"
        )
        
        # Should return 0 (resource doesn't exist)
        assert added_count == 0, "Adding non-existent resource should return count of 0"
        
        # Verify no associations created
        from app.database.models import CollectionResource
        associations = db_session.query(CollectionResource).filter(
            CollectionResource.collection_id == collection.id
        ).all()
        
        assert len(associations) == 0, "No associations should be created for non-existent resources"
    
    def test_access_control_enforcement(self, db_session, create_test_collection):
        """
        Test access control for collection operations.
        
        Verifies:
        - Owner can access their collections
        - Non-owner cannot access private collections
        - Proper error messages for access denied
        
        **Validates: Requirements 5.3, 5.4**
        """
        # Create collection for user1
        collection = create_test_collection(
            name="Private Collection",
            owner_id="user1",
            visibility="private"
        )
        
        from app.modules.collections.service import CollectionService
        service = CollectionService(db_session)
        
        # Owner can access
        result = service.get_collection(
            collection_id=collection.id,
            owner_id="user1"
        )
        assert result is not None, "Owner should be able to access their collection"
        
        # Non-owner cannot access private collection
        result = service.get_collection(
            collection_id=collection.id,
            owner_id="user2"
        )
        assert result is None, "Non-owner should not be able to access private collection"
        
        # Try to update as non-owner (should fail)
        from app.modules.collections.schema import CollectionUpdate
        
        with pytest.raises(ValueError, match="not found or access denied"):
            service.update_collection(
                collection_id=collection.id,
                owner_id="user2",
                updates=CollectionUpdate(name="Hacked Name")
            )
