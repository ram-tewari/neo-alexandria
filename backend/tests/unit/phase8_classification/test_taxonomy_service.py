"""
Unit tests for TaxonomyService (Phase 8.5).

Tests cover:
- create_node() with and without parent
- update_node() metadata changes
- delete_node() cascade and reparenting
- move_node() and circular reference prevention
- get_tree() with depth limits
- get_ancestors() and get_descendants()
- classify_resource() and resource counts
- Helper methods (_slugify, _compute_path, _is_descendant)
"""

import pytest
import uuid
from datetime import datetime, timezone

from backend.app.services.taxonomy_service import TaxonomyService
from backend.app.database.models import TaxonomyNode, ResourceTaxonomy, Resource


# ============================================================================
# Helper Method Tests
# ============================================================================

def test_slugify_basic(test_db):
    """Test _slugify() with basic text."""
    db = test_db()
    service = TaxonomyService(db)
    
    assert service._slugify("Machine Learning") == "machine-learning"
    assert service._slugify("Deep Learning & AI") == "deep-learning-ai"
    assert service._slugify("Natural Language Processing") == "natural-language-processing"
    assert service._slugify("Computer Science 101") == "computer-science-101"
    
    db.close()


def test_slugify_special_characters(test_db):
    """Test _slugify() with special characters."""
    db = test_db()
    service = TaxonomyService(db)
    
    assert service._slugify("C++ Programming") == "c-programming"
    assert service._slugify("Data Science @ Scale") == "data-science-scale"
    assert service._slugify("AI/ML Research") == "ai-ml-research"
    assert service._slugify("Test---Multiple---Hyphens") == "test-multiple-hyphens"
    
    db.close()


def test_compute_path_root_node(test_db):
    """Test _compute_path() for root nodes."""
    db = test_db()
    service = TaxonomyService(db)
    
    path = service._compute_path(None, "computer-science")
    assert path == "/computer-science"
    
    db.close()


def test_compute_path_with_parent(test_db):
    """Test _compute_path() with parent node."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create parent node
    parent = service.create_node(name="Computer Science")
    
    # Compute path for child
    path = service._compute_path(parent.id, "machine-learning")
    assert path == "/computer-science/machine-learning"
    
    db.close()


def test_compute_path_invalid_parent(test_db):
    """Test _compute_path() with invalid parent ID."""
    db = test_db()
    service = TaxonomyService(db)
    
    fake_id = uuid.uuid4()
    with pytest.raises(ValueError, match="Parent node.*not found"):
        service._compute_path(fake_id, "test-slug")
    
    db.close()


def test_is_descendant_true(test_db):
    """Test _is_descendant() returns True for actual descendant."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create hierarchy: root -> child -> grandchild
    root = service.create_node(name="Root")
    child = service.create_node(name="Child", parent_id=root.id)
    grandchild = service.create_node(name="Grandchild", parent_id=child.id)
    
    # Test descendant relationships
    assert service._is_descendant(child.id, root.id) == True
    assert service._is_descendant(grandchild.id, root.id) == True
    assert service._is_descendant(grandchild.id, child.id) == True
    
    db.close()


def test_is_descendant_false(test_db):
    """Test _is_descendant() returns False for non-descendants."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create separate branches
    root1 = service.create_node(name="Root 1")
    root2 = service.create_node(name="Root 2")
    child1 = service.create_node(name="Child 1", parent_id=root1.id)
    
    # Test non-descendant relationships
    assert service._is_descendant(root1.id, child1.id) == False  # Parent is not descendant of child
    assert service._is_descendant(root2.id, root1.id) == False  # Separate branches
    assert service._is_descendant(child1.id, root2.id) == False  # Different branches
    
    db.close()


# ============================================================================
# create_node() Tests
# ============================================================================

def test_create_root_node(test_db):
    """Test creating a root node without parent."""
    db = test_db()
    service = TaxonomyService(db)
    
    node = service.create_node(
        name="Computer Science",
        description="CS topics",
        keywords=["programming", "algorithms"],
        allow_resources=True
    )
    
    assert node.id is not None
    assert node.name == "Computer Science"
    assert node.slug == "computer-science"
    assert node.parent_id is None
    assert node.level == 0
    assert node.path == "/computer-science"
    assert node.description == "CS topics"
    assert node.keywords == ["programming", "algorithms"]
    assert node.is_leaf == True
    assert node.allow_resources == True
    assert node.resource_count == 0
    assert node.descendant_resource_count == 0
    
    db.close()


def test_create_child_node(test_db):
    """Test creating a child node with parent."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create parent
    parent = service.create_node(name="Computer Science")
    
    # Create child
    child = service.create_node(
        name="Machine Learning",
        parent_id=parent.id,
        description="ML topics"
    )
    
    assert child.parent_id == parent.id
    assert child.level == 1
    assert child.path == "/computer-science/machine-learning"
    assert child.is_leaf == True
    
    # Verify parent is_leaf updated
    db.refresh(parent)
    assert parent.is_leaf == False
    
    db.close()


def test_create_deep_hierarchy(test_db):
    """Test creating a deep hierarchy (5+ levels)."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create 6-level hierarchy
    level0 = service.create_node(name="Level 0")
    level1 = service.create_node(name="Level 1", parent_id=level0.id)
    level2 = service.create_node(name="Level 2", parent_id=level1.id)
    level3 = service.create_node(name="Level 3", parent_id=level2.id)
    level4 = service.create_node(name="Level 4", parent_id=level3.id)
    level5 = service.create_node(name="Level 5", parent_id=level4.id)
    
    assert level0.level == 0
    assert level1.level == 1
    assert level2.level == 2
    assert level3.level == 3
    assert level4.level == 4
    assert level5.level == 5
    assert level5.path == "/level-0/level-1/level-2/level-3/level-4/level-5"
    
    db.close()


def test_create_node_duplicate_slug(test_db):
    """Test creating node with duplicate slug raises error."""
    db = test_db()
    service = TaxonomyService(db)
    
    service.create_node(name="Machine Learning")
    
    with pytest.raises(ValueError, match="slug.*already exists"):
        service.create_node(name="Machine Learning")
    
    db.close()


def test_create_node_empty_name(test_db):
    """Test creating node with empty name raises error."""
    db = test_db()
    service = TaxonomyService(db)
    
    with pytest.raises(ValueError, match="name cannot be empty"):
        service.create_node(name="")
    
    with pytest.raises(ValueError, match="name cannot be empty"):
        service.create_node(name="   ")
    
    db.close()


def test_create_node_invalid_parent(test_db):
    """Test creating node with invalid parent ID raises error."""
    db = test_db()
    service = TaxonomyService(db)
    
    fake_id = uuid.uuid4()
    with pytest.raises(ValueError, match="Parent node.*not found"):
        service.create_node(name="Test", parent_id=fake_id)
    
    db.close()


# ============================================================================
# update_node() Tests
# ============================================================================

def test_update_node_metadata(test_db):
    """Test updating node metadata without name change."""
    db = test_db()
    service = TaxonomyService(db)
    
    node = service.create_node(
        name="Machine Learning",
        description="Old description",
        keywords=["ml"],
        allow_resources=True
    )
    
    updated = service.update_node(
        node_id=node.id,
        description="New description",
        keywords=["ml", "ai", "deep-learning"],
        allow_resources=False
    )
    
    assert updated.name == "Machine Learning"
    assert updated.slug == "machine-learning"
    assert updated.description == "New description"
    assert updated.keywords == ["ml", "ai", "deep-learning"]
    assert updated.allow_resources == False
    
    db.close()


def test_update_node_name(test_db):
    """Test updating node name (triggers slug and path recalculation)."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create parent and child
    parent = service.create_node(name="Computer Science")
    child = service.create_node(name="Machine Learning", parent_id=parent.id)
    
    # Update child name
    updated = service.update_node(node_id=child.id, name="Deep Learning")
    
    assert updated.name == "Deep Learning"
    assert updated.slug == "deep-learning"
    assert updated.path == "/computer-science/deep-learning"
    
    db.close()


def test_update_node_name_with_descendants(test_db):
    """Test updating node name updates descendant paths."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create hierarchy
    root = service.create_node(name="Science")
    child = service.create_node(name="Physics", parent_id=root.id)
    grandchild = service.create_node(name="Quantum", parent_id=child.id)
    
    # Update child name
    service.update_node(node_id=child.id, name="Modern Physics")
    
    # Verify descendant path updated
    db.refresh(grandchild)
    assert grandchild.path == "/science/modern-physics/quantum"
    
    db.close()


def test_update_node_duplicate_slug(test_db):
    """Test updating node to duplicate slug raises error."""
    db = test_db()
    service = TaxonomyService(db)
    
    service.create_node(name="Machine Learning")
    node2 = service.create_node(name="Deep Learning")
    
    with pytest.raises(ValueError, match="slug.*already exists"):
        service.update_node(node_id=node2.id, name="Machine Learning")
    
    db.close()


def test_update_node_not_found(test_db):
    """Test updating non-existent node raises error."""
    db = test_db()
    service = TaxonomyService(db)
    
    fake_id = uuid.uuid4()
    with pytest.raises(ValueError, match="Node.*not found"):
        service.update_node(node_id=fake_id, name="Test")
    
    db.close()


# ============================================================================
# delete_node() Tests
# ============================================================================

def test_delete_leaf_node(test_db):
    """Test deleting a leaf node without children."""
    db = test_db()
    service = TaxonomyService(db)
    
    node = service.create_node(name="Test Node")
    node_id = node.id
    
    result = service.delete_node(node_id=node_id)
    
    assert result["deleted_count"] == 1
    assert result["reparented_count"] == 0
    
    # Verify node deleted
    deleted = db.query(TaxonomyNode).filter(TaxonomyNode.id == node_id).first()
    assert deleted is None
    
    db.close()


def test_delete_node_with_cascade(test_db):
    """Test deleting node with cascade deletes descendants."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create hierarchy
    root = service.create_node(name="Root")
    child1 = service.create_node(name="Child 1", parent_id=root.id)
    child2 = service.create_node(name="Child 2", parent_id=root.id)
    grandchild = service.create_node(name="Grandchild", parent_id=child1.id)
    
    # Delete root with cascade
    result = service.delete_node(node_id=root.id, cascade=True)
    
    assert result["deleted_count"] == 4  # root + 2 children + 1 grandchild
    assert result["reparented_count"] == 0
    
    # Verify all deleted
    assert db.query(TaxonomyNode).filter(TaxonomyNode.id == root.id).first() is None
    assert db.query(TaxonomyNode).filter(TaxonomyNode.id == child1.id).first() is None
    assert db.query(TaxonomyNode).filter(TaxonomyNode.id == child2.id).first() is None
    assert db.query(TaxonomyNode).filter(TaxonomyNode.id == grandchild.id).first() is None
    
    db.close()


def test_delete_node_with_reparenting(test_db):
    """Test deleting node without cascade reparents children."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create hierarchy
    root = service.create_node(name="Root")
    child = service.create_node(name="Child", parent_id=root.id)
    grandchild = service.create_node(name="Grandchild", parent_id=child.id)
    
    # Delete child without cascade
    result = service.delete_node(node_id=child.id, cascade=False)
    
    assert result["deleted_count"] == 1
    assert result["reparented_count"] == 1
    
    # Verify child deleted
    assert db.query(TaxonomyNode).filter(TaxonomyNode.id == child.id).first() is None
    
    # Verify grandchild reparented to root
    db.refresh(grandchild)
    assert grandchild.parent_id == root.id
    assert grandchild.level == 1
    assert grandchild.path == "/root/grandchild"
    
    db.close()


def test_delete_node_with_resources_raises_error(test_db):
    """Test deleting node with assigned resources raises error."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create node and resource
    node = service.create_node(name="Test Node")
    resource = Resource(
        id=uuid.uuid4(),
        title="Test Resource",
        language="en",
        type="article",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(resource)
    db.commit()
    
    # Assign resource to node
    classification = ResourceTaxonomy(
        id=uuid.uuid4(),
        resource_id=resource.id,
        taxonomy_node_id=node.id,
        confidence=0.9,
        is_predicted=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(classification)
    db.commit()
    
    # Try to delete node
    with pytest.raises(ValueError, match="Cannot delete node with.*assigned resources"):
        service.delete_node(node_id=node.id)
    
    db.close()


def test_delete_node_updates_parent_is_leaf(test_db):
    """Test deleting last child updates parent is_leaf flag."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create parent with one child
    parent = service.create_node(name="Parent")
    child = service.create_node(name="Child", parent_id=parent.id)
    
    # Verify parent is not leaf
    db.refresh(parent)
    assert parent.is_leaf == False
    
    # Delete child
    service.delete_node(node_id=child.id)
    
    # Verify parent is now leaf
    db.refresh(parent)
    assert parent.is_leaf == True
    
    db.close()


# ============================================================================
# move_node() Tests
# ============================================================================

def test_move_node_to_new_parent(test_db):
    """Test moving node to a new parent."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create nodes
    parent1 = service.create_node(name="Parent 1")
    parent2 = service.create_node(name="Parent 2")
    child = service.create_node(name="Child", parent_id=parent1.id)
    
    # Move child to parent2
    moved = service.move_node(node_id=child.id, new_parent_id=parent2.id)
    
    assert moved.parent_id == parent2.id
    assert moved.level == 1
    assert moved.path == "/parent-2/child"
    
    # Verify old parent is now leaf
    db.refresh(parent1)
    assert parent1.is_leaf == True
    
    # Verify new parent is not leaf
    db.refresh(parent2)
    assert parent2.is_leaf == False
    
    db.close()


def test_move_node_to_root(test_db):
    """Test moving node to root level."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create parent and child
    parent = service.create_node(name="Parent")
    child = service.create_node(name="Child", parent_id=parent.id)
    
    # Move child to root
    moved = service.move_node(node_id=child.id, new_parent_id=None)
    
    assert moved.parent_id is None
    assert moved.level == 0
    assert moved.path == "/child"
    
    db.close()


def test_move_node_updates_descendants(test_db):
    """Test moving node updates descendant paths and levels."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create hierarchy
    parent1 = service.create_node(name="Parent 1")
    parent2 = service.create_node(name="Parent 2")
    child = service.create_node(name="Child", parent_id=parent1.id)
    grandchild = service.create_node(name="Grandchild", parent_id=child.id)
    
    # Move child to parent2
    service.move_node(node_id=child.id, new_parent_id=parent2.id)
    
    # Verify grandchild updated
    db.refresh(grandchild)
    assert grandchild.level == 2
    assert grandchild.path == "/parent-2/child/grandchild"
    
    db.close()


def test_move_node_circular_reference_prevention(test_db):
    """Test moving node to its own descendant raises error."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create hierarchy
    root = service.create_node(name="Root")
    child = service.create_node(name="Child", parent_id=root.id)
    grandchild = service.create_node(name="Grandchild", parent_id=child.id)
    
    # Try to move root to grandchild (circular reference)
    with pytest.raises(ValueError, match="circular reference"):
        service.move_node(node_id=root.id, new_parent_id=grandchild.id)
    
    # Try to move child to grandchild (circular reference)
    with pytest.raises(ValueError, match="circular reference"):
        service.move_node(node_id=child.id, new_parent_id=grandchild.id)
    
    db.close()


def test_move_node_to_self_raises_error(test_db):
    """Test moving node to itself raises error."""
    db = test_db()
    service = TaxonomyService(db)
    
    node = service.create_node(name="Test Node")
    
    with pytest.raises(ValueError, match="circular reference"):
        service.move_node(node_id=node.id, new_parent_id=node.id)
    
    db.close()


def test_move_node_same_parent_no_change(test_db):
    """Test moving node to same parent returns unchanged."""
    db = test_db()
    service = TaxonomyService(db)
    
    parent = service.create_node(name="Parent")
    child = service.create_node(name="Child", parent_id=parent.id)
    
    original_path = child.path
    
    # Move to same parent
    moved = service.move_node(node_id=child.id, new_parent_id=parent.id)
    
    assert moved.parent_id == parent.id
    assert moved.path == original_path
    
    db.close()


# ============================================================================
# get_tree() Tests
# ============================================================================

def test_get_tree_full(test_db):
    """Test retrieving full taxonomy tree."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create hierarchy
    root1 = service.create_node(name="Root 1")
    root2 = service.create_node(name="Root 2")
    child1 = service.create_node(name="Child 1", parent_id=root1.id)
    child2 = service.create_node(name="Child 2", parent_id=root1.id)
    grandchild = service.create_node(name="Grandchild", parent_id=child1.id)
    
    # Get full tree
    tree = service.get_tree()
    
    assert len(tree) == 2  # Two root nodes
    
    # Find root1 in tree
    root1_tree = next(n for n in tree if n["name"] == "Root 1")
    assert len(root1_tree["children"]) == 2
    
    # Find child1 in tree
    child1_tree = next(c for c in root1_tree["children"] if c["name"] == "Child 1")
    assert len(child1_tree["children"]) == 1
    assert child1_tree["children"][0]["name"] == "Grandchild"
    
    db.close()


def test_get_tree_from_root(test_db):
    """Test retrieving subtree from specific root."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create two separate trees
    root1 = service.create_node(name="Root 1")
    child1 = service.create_node(name="Child 1", parent_id=root1.id)
    
    root2 = service.create_node(name="Root 2")
    child2 = service.create_node(name="Child 2", parent_id=root2.id)
    
    # Get subtree from root1
    tree = service.get_tree(root_id=root1.id)
    
    assert len(tree) == 1
    assert tree[0]["name"] == "Root 1"
    assert len(tree[0]["children"]) == 1
    assert tree[0]["children"][0]["name"] == "Child 1"
    
    db.close()


def test_get_tree_with_max_depth(test_db):
    """Test retrieving tree with depth limit."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create deep hierarchy
    root = service.create_node(name="Root")
    level1 = service.create_node(name="Level 1", parent_id=root.id)
    level2 = service.create_node(name="Level 2", parent_id=level1.id)
    level3 = service.create_node(name="Level 3", parent_id=level2.id)
    
    # Get tree with max_depth=2
    tree = service.get_tree(max_depth=2)
    
    assert len(tree) == 1
    root_tree = tree[0]
    assert root_tree["name"] == "Root"
    assert len(root_tree["children"]) == 1
    
    level1_tree = root_tree["children"][0]
    assert level1_tree["name"] == "Level 1"
    assert len(level1_tree["children"]) == 1
    
    level2_tree = level1_tree["children"][0]
    assert level2_tree["name"] == "Level 2"
    assert len(level2_tree["children"]) == 0  # Depth limit reached
    
    db.close()


def test_get_tree_includes_metadata(test_db):
    """Test tree includes all node metadata."""
    db = test_db()
    service = TaxonomyService(db)
    
    node = service.create_node(
        name="Test Node",
        description="Test description",
        keywords=["test", "node"],
        allow_resources=False
    )
    
    tree = service.get_tree()
    
    assert len(tree) == 1
    node_tree = tree[0]
    
    assert node_tree["id"] == str(node.id)
    assert node_tree["name"] == "Test Node"
    assert node_tree["slug"] == "test-node"
    assert node_tree["level"] == 0
    assert node_tree["path"] == "/test-node"
    assert node_tree["description"] == "Test description"
    assert node_tree["keywords"] == ["test", "node"]
    assert node_tree["resource_count"] == 0
    assert node_tree["descendant_resource_count"] == 0
    assert node_tree["is_leaf"] == True
    assert node_tree["allow_resources"] == False
    
    db.close()


# ============================================================================
# get_ancestors() Tests
# ============================================================================

def test_get_ancestors_basic(test_db):
    """Test retrieving ancestors of a node."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create hierarchy
    root = service.create_node(name="Root")
    child = service.create_node(name="Child", parent_id=root.id)
    grandchild = service.create_node(name="Grandchild", parent_id=child.id)
    
    # Get ancestors of grandchild
    ancestors = service.get_ancestors(grandchild.id)
    
    assert len(ancestors) == 2
    assert ancestors[0].name == "Root"
    assert ancestors[1].name == "Child"
    
    db.close()


def test_get_ancestors_root_node(test_db):
    """Test root node has no ancestors."""
    db = test_db()
    service = TaxonomyService(db)
    
    root = service.create_node(name="Root")
    
    ancestors = service.get_ancestors(root.id)
    
    assert len(ancestors) == 0
    
    db.close()


def test_get_ancestors_deep_hierarchy(test_db):
    """Test ancestors in deep hierarchy."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create 5-level hierarchy
    level0 = service.create_node(name="Level 0")
    level1 = service.create_node(name="Level 1", parent_id=level0.id)
    level2 = service.create_node(name="Level 2", parent_id=level1.id)
    level3 = service.create_node(name="Level 3", parent_id=level2.id)
    level4 = service.create_node(name="Level 4", parent_id=level3.id)
    
    # Get ancestors of level4
    ancestors = service.get_ancestors(level4.id)
    
    assert len(ancestors) == 4
    assert [a.name for a in ancestors] == ["Level 0", "Level 1", "Level 2", "Level 3"]
    
    db.close()


# ============================================================================
# get_descendants() Tests
# ============================================================================

def test_get_descendants_basic(test_db):
    """Test retrieving descendants of a node."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create hierarchy
    root = service.create_node(name="Root")
    child1 = service.create_node(name="Child 1", parent_id=root.id)
    child2 = service.create_node(name="Child 2", parent_id=root.id)
    grandchild = service.create_node(name="Grandchild", parent_id=child1.id)
    
    # Get descendants of root
    descendants = service.get_descendants(root.id)
    
    assert len(descendants) == 3
    names = {d.name for d in descendants}
    assert names == {"Child 1", "Child 2", "Grandchild"}
    
    db.close()


def test_get_descendants_leaf_node(test_db):
    """Test leaf node has no descendants."""
    db = test_db()
    service = TaxonomyService(db)
    
    root = service.create_node(name="Root")
    leaf = service.create_node(name="Leaf", parent_id=root.id)
    
    descendants = service.get_descendants(leaf.id)
    
    assert len(descendants) == 0
    
    db.close()


def test_get_descendants_ordered(test_db):
    """Test descendants are ordered by level and name."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create hierarchy
    root = service.create_node(name="Root")
    child_b = service.create_node(name="Child B", parent_id=root.id)
    child_a = service.create_node(name="Child A", parent_id=root.id)
    grandchild = service.create_node(name="Grandchild", parent_id=child_a.id)
    
    # Get descendants
    descendants = service.get_descendants(root.id)
    
    # Should be ordered by level, then name
    assert descendants[0].level == 1
    assert descendants[1].level == 1
    assert descendants[2].level == 2
    assert descendants[0].name == "Child A"
    assert descendants[1].name == "Child B"
    
    db.close()


# ============================================================================
# classify_resource() Tests
# ============================================================================

def test_classify_resource_basic(test_db):
    """Test basic resource classification."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create taxonomy node
    node = service.create_node(name="Machine Learning")
    
    # Create resource
    resource = Resource(
        id=uuid.uuid4(),
        title="ML Tutorial",
        language="en",
        type="article",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(resource)
    db.commit()
    
    # Classify resource
    classifications = service.classify_resource(
        resource_id=resource.id,
        classifications=[
            {"taxonomy_node_id": node.id, "confidence": 0.95}
        ],
        predicted_by="test_model_v1"
    )
    
    assert len(classifications) == 1
    assert classifications[0].resource_id == resource.id
    assert classifications[0].taxonomy_node_id == node.id
    assert classifications[0].confidence == 0.95
    assert classifications[0].is_predicted == True
    assert classifications[0].predicted_by == "test_model_v1"
    assert classifications[0].needs_review == False
    
    db.close()


def test_classify_resource_multiple_categories(test_db):
    """Test classifying resource with multiple categories."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create taxonomy nodes
    node1 = service.create_node(name="Machine Learning")
    node2 = service.create_node(name="Deep Learning")
    node3 = service.create_node(name="Neural Networks")
    
    # Create resource
    resource = Resource(
        id=uuid.uuid4(),
        title="Test Resource",
        language="en",
        type="article",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(resource)
    db.commit()
    
    # Classify with multiple categories
    classifications = service.classify_resource(
        resource_id=resource.id,
        classifications=[
            {"taxonomy_node_id": node1.id, "confidence": 0.95},
            {"taxonomy_node_id": node2.id, "confidence": 0.88},
            {"taxonomy_node_id": node3.id, "confidence": 0.75}
        ]
    )
    
    assert len(classifications) == 3
    
    db.close()


def test_classify_resource_low_confidence_needs_review(test_db):
    """Test low confidence classifications are flagged for review."""
    db = test_db()
    service = TaxonomyService(db)
    
    node = service.create_node(name="Test Category")
    
    resource = Resource(
        id=uuid.uuid4(),
        title="Test Resource",
        language="en",
        type="article",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(resource)
    db.commit()
    
    # Classify with low confidence
    classifications = service.classify_resource(
        resource_id=resource.id,
        classifications=[
            {"taxonomy_node_id": node.id, "confidence": 0.65}
        ]
    )
    
    assert classifications[0].needs_review == True
    assert classifications[0].review_priority is not None
    assert abs(classifications[0].review_priority - 0.35) < 0.01
    
    db.close()


def test_classify_resource_removes_existing_predicted(test_db):
    """Test new classification removes existing predicted classifications."""
    db = test_db()
    service = TaxonomyService(db)
    
    node1 = service.create_node(name="Category 1")
    node2 = service.create_node(name="Category 2")
    
    resource = Resource(
        id=uuid.uuid4(),
        title="Test Resource",
        language="en",
        type="article",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(resource)
    db.commit()
    
    # First classification
    service.classify_resource(
        resource_id=resource.id,
        classifications=[{"taxonomy_node_id": node1.id, "confidence": 0.8}]
    )
    
    # Second classification (should replace first)
    service.classify_resource(
        resource_id=resource.id,
        classifications=[{"taxonomy_node_id": node2.id, "confidence": 0.9}]
    )
    
    # Verify only second classification exists
    all_classifications = db.query(ResourceTaxonomy).filter(
        ResourceTaxonomy.resource_id == resource.id
    ).all()
    
    assert len(all_classifications) == 1
    assert all_classifications[0].taxonomy_node_id == node2.id
    
    db.close()


def test_classify_resource_skips_disallowed_nodes(test_db):
    """Test classification skips nodes with allow_resources=False."""
    db = test_db()
    service = TaxonomyService(db)
    
    allowed_node = service.create_node(name="Allowed", allow_resources=True)
    disallowed_node = service.create_node(name="Disallowed", allow_resources=False)
    
    resource = Resource(
        id=uuid.uuid4(),
        title="Test Resource",
        language="en",
        type="article",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(resource)
    db.commit()
    
    # Try to classify with both nodes
    classifications = service.classify_resource(
        resource_id=resource.id,
        classifications=[
            {"taxonomy_node_id": allowed_node.id, "confidence": 0.9},
            {"taxonomy_node_id": disallowed_node.id, "confidence": 0.9}
        ]
    )
    
    # Only allowed node should be classified
    assert len(classifications) == 1
    assert classifications[0].taxonomy_node_id == allowed_node.id
    
    db.close()


def test_classify_resource_updates_counts(test_db):
    """Test classification updates resource counts."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create hierarchy
    root = service.create_node(name="Root")
    child = service.create_node(name="Child", parent_id=root.id)
    
    # Create resource
    resource = Resource(
        id=uuid.uuid4(),
        title="Test Resource",
        language="en",
        type="article",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(resource)
    db.commit()
    
    # Classify resource to child
    service.classify_resource(
        resource_id=resource.id,
        classifications=[{"taxonomy_node_id": child.id, "confidence": 0.9}]
    )
    
    # Verify counts updated
    db.refresh(child)
    db.refresh(root)
    
    assert child.resource_count == 1
    assert child.descendant_resource_count == 0
    assert root.resource_count == 0
    assert root.descendant_resource_count == 1
    
    db.close()


def test_classify_resource_invalid_resource(test_db):
    """Test classifying non-existent resource raises error."""
    db = test_db()
    service = TaxonomyService(db)
    
    node = service.create_node(name="Test Node")
    fake_resource_id = uuid.uuid4()
    
    with pytest.raises(ValueError, match="Resource.*not found"):
        service.classify_resource(
            resource_id=fake_resource_id,
            classifications=[{"taxonomy_node_id": node.id, "confidence": 0.9}]
        )
    
    db.close()


def test_classify_resource_invalid_taxonomy_node(test_db):
    """Test classifying with non-existent taxonomy node raises error."""
    db = test_db()
    service = TaxonomyService(db)
    
    resource = Resource(
        id=uuid.uuid4(),
        title="Test Resource",
        language="en",
        type="article",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(resource)
    db.commit()
    
    fake_node_id = uuid.uuid4()
    
    with pytest.raises(ValueError, match="Taxonomy node.*not found"):
        service.classify_resource(
            resource_id=resource.id,
            classifications=[{"taxonomy_node_id": fake_node_id, "confidence": 0.9}]
        )
    
    db.close()


# ============================================================================
# _update_resource_counts() Tests
# ============================================================================

def test_update_resource_counts_hierarchical(test_db):
    """Test resource counts update hierarchically."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create 3-level hierarchy
    root = service.create_node(name="Root")
    child = service.create_node(name="Child", parent_id=root.id)
    grandchild = service.create_node(name="Grandchild", parent_id=child.id)
    
    # Create resources
    resources = []
    for i in range(3):
        resource = Resource(
            id=uuid.uuid4(),
            title=f"Resource {i}",
            language="en",
            type="article",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(resource)
        resources.append(resource)
    db.commit()
    
    # Classify resources at different levels
    # 1 resource to root, 1 to child, 1 to grandchild
    service.classify_resource(
        resource_id=resources[0].id,
        classifications=[{"taxonomy_node_id": root.id, "confidence": 0.9}]
    )
    service.classify_resource(
        resource_id=resources[1].id,
        classifications=[{"taxonomy_node_id": child.id, "confidence": 0.9}]
    )
    service.classify_resource(
        resource_id=resources[2].id,
        classifications=[{"taxonomy_node_id": grandchild.id, "confidence": 0.9}]
    )
    
    # Verify counts
    db.refresh(root)
    db.refresh(child)
    db.refresh(grandchild)
    
    # Root: 1 direct, 2 descendants (child + grandchild)
    assert root.resource_count == 1
    assert root.descendant_resource_count == 2
    
    # Child: 1 direct, 1 descendant (grandchild)
    assert child.resource_count == 1
    assert child.descendant_resource_count == 1
    
    # Grandchild: 1 direct, 0 descendants
    assert grandchild.resource_count == 1
    assert grandchild.descendant_resource_count == 0
    
    db.close()


def test_update_resource_counts_multiple_classifications(test_db):
    """Test resource counts with multi-label classification."""
    db = test_db()
    service = TaxonomyService(db)
    
    # Create nodes
    node1 = service.create_node(name="Category 1")
    node2 = service.create_node(name="Category 2")
    
    # Create resource
    resource = Resource(
        id=uuid.uuid4(),
        title="Test Resource",
        language="en",
        type="article",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(resource)
    db.commit()
    
    # Classify to both nodes
    service.classify_resource(
        resource_id=resource.id,
        classifications=[
            {"taxonomy_node_id": node1.id, "confidence": 0.9},
            {"taxonomy_node_id": node2.id, "confidence": 0.8}
        ]
    )
    
    # Verify both nodes have count of 1
    db.refresh(node1)
    db.refresh(node2)
    
    assert node1.resource_count == 1
    assert node2.resource_count == 1
    
    db.close()
