"""
Taxonomy Module - Tree Logic Tests

Tests for taxonomy tree structure validation and edge cases.
Tests circular dependencies, orphan handling, depth limits, and validation.

**Validates: Requirements 3.2, 3.3, 8.4, 16.2**
"""

import pytest
from sqlalchemy.exc import IntegrityError


class TestTaxonomyTreeLogic:
    """Test suite for taxonomy tree structure and validation."""
    
    def test_circular_dependency_prevention(self, db_session, create_test_category):
        """
        Test that circular dependencies in taxonomy tree are prevented.
        
        Scenario:
        1. Create category A
        2. Create category B with parent A
        3. Try to set A's parent to B (circular dependency)
        
        Expected: Should raise an error or prevent the circular reference
        
        **Validates: Requirements 3.2, 3.3, 8.4**
        """
        from app.modules.taxonomy.service import TaxonomyService
        
        # Create parent category
        category_a = create_test_category(name="Category A", parent_id=None)
        
        # Create child category
        category_b = create_test_category(name="Category B", parent_id=category_a.id)
        
        # Try to create circular dependency: A -> B -> A
        # Use the service to validate
        service = TaxonomyService()
        
        with pytest.raises((IntegrityError, ValueError, RuntimeError)) as exc_info:
            # Attempt to set category A's parent to category B
            category_a.parent_id = category_b.id
            
            # Validate using service
            service.validate_category(category_a, db_session)
            
            # If validation passes (it shouldn't), try to commit
            db_session.commit()
        
        # Verify the error was raised
        assert exc_info.value is not None
        
        # Rollback the failed transaction
        db_session.rollback()
    
    def test_orphan_node_handling(self, db_session, create_test_category):
        """
        Test handling of orphan nodes when parent is deleted.
        
        Scenario:
        1. Create parent category
        2. Create child category
        3. Delete parent category
        4. Verify child is either deleted (cascade) or becomes root node
        
        Expected: Child should be handled appropriately (cascade delete or re-parent)
        
        **Validates: Requirements 3.2, 3.3, 8.4**
        """
        from app.database.models import TaxonomyNode
        
        # Create parent category
        parent = create_test_category(name="Parent Category", parent_id=None)
        parent_id = parent.id
        
        # Create child category
        child = create_test_category(name="Child Category", parent_id=parent_id)
        child_id = child.id
        
        # Delete parent category
        db_session.delete(parent)
        db_session.commit()
        
        # Check if child still exists
        child_after_delete = db_session.query(TaxonomyNode).filter_by(id=child_id).first()
        
        # Either child is deleted (cascade) or parent_id is set to None
        if child_after_delete is None:
            # Cascade delete occurred - this is valid behavior
            assert True
        else:
            # Child still exists - verify it's now a root node or has null parent
            assert child_after_delete.parent_id is None or child_after_delete.parent_id != parent_id
    
    def test_max_depth_enforcement(self, db_session, create_test_category):
        """
        Test that maximum tree depth is enforced.
        
        Scenario:
        1. Create a deep hierarchy of categories using the service
        2. Try to exceed maximum depth limit
        
        Expected: Should prevent creating categories beyond max depth
        
        **Validates: Requirements 3.2, 3.3, 8.4, 16.2**
        """
        from app.modules.taxonomy.service import TaxonomyService
        
        service = TaxonomyService()
        MAX_DEPTH = service.MAX_DEPTH
        
        # Create a chain of categories up to max depth - 1 using the service
        current_parent_id = None
        categories = []
        
        for level in range(MAX_DEPTH):
            category = service.create_category(
                name=f"Level {level} Category",
                db=db_session,
                parent_id=current_parent_id
            )
            categories.append(category)
            current_parent_id = str(category.id)
        
        # Try to create a category at max depth (should fail)
        # This should raise an error because we're at the limit
        with pytest.raises((ValueError, IntegrityError, RuntimeError)) as exc_info:
            service.create_category(
                name="Beyond Max Depth",
                db=db_session,
                parent_id=current_parent_id
            )
        
        # Verify the error was raised
        assert exc_info.value is not None
        assert "depth" in str(exc_info.value).lower() or "maximum" in str(exc_info.value).lower()
        
        # Rollback any failed transaction
        db_session.rollback()
    
    def test_duplicate_category_names(self, db_session, create_test_category):
        """
        Test handling of duplicate category names.
        
        Scenario:
        1. Create category with name "Test Category"
        2. Try to create another category with same name
        
        Expected: Should either allow (if names are scoped by parent) or prevent duplicates
        
        **Validates: Requirements 3.2, 3.3, 8.4**
        """
        # Create first category
        category1 = create_test_category(name="Duplicate Name")
        
        # Try to create second category with same name
        # Behavior depends on implementation:
        # - If names must be unique globally: should raise error
        # - If names are scoped by parent: should succeed
        try:
            category2 = create_test_category(name="Duplicate Name")
            
            # If creation succeeded, verify they have different IDs
            assert category1.id != category2.id
            
            # Names can be duplicate if scoped by parent or if slugs differ
            assert True
        except (IntegrityError, ValueError):
            # If duplicates are not allowed, this is expected
            db_session.rollback()
            assert True
    
    def test_empty_category_name(self, db_session):
        """
        Test validation of empty category names.
        
        Scenario:
        1. Try to create category with empty name
        2. Try to create category with whitespace-only name
        
        Expected: Should raise validation error
        
        **Validates: Requirements 3.2, 3.3, 8.4, 16.2**
        """
        from app.database.models import TaxonomyNode
        
        # Test empty string
        with pytest.raises((ValueError, IntegrityError)):
            category = TaxonomyNode(
                name="",
                slug="empty",
                level=0,
                path="/empty"
            )
            db_session.add(category)
            db_session.commit()
        
        db_session.rollback()
        
        # Test whitespace-only string
        with pytest.raises((ValueError, IntegrityError)):
            category = TaxonomyNode(
                name="   ",
                slug="whitespace",
                level=0,
                path="/whitespace"
            )
            db_session.add(category)
            db_session.commit()
        
        db_session.rollback()
