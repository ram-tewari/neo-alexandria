"""
Unit tests for Collection Service features.

Tests cover:
- Aggregate embedding computation
- Resource recommendations
- Collection recommendations
- Hierarchy validation
- Batch resource operations
"""

import uuid
import pytest
import numpy as np

from app.modules.collections.service import CollectionService
from app.modules.collections.model import Collection, CollectionResource
from app.database.models import Resource


class TestAggregateEmbedding:
    """Test aggregate embedding computation."""

    def test_compute_embedding_with_resources(self, db_session):
        """Test computing collection embedding from member resources."""
        service = CollectionService(db_session)

        # Create collection
        collection = Collection(
            name="Test Collection",
            description="Test",
            owner_id="user1",
            visibility="private",
        )
        db_session.add(collection)
        db_session.commit()

        # Create resources with embeddings
        embeddings = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]

        resource_ids = []
        for i, emb in enumerate(embeddings):
            resource = Resource(
                title=f"Resource {i}",
                source=f"http://example.com/{i}",
                type="article",
                embedding=emb,
                quality_score=0.8,
            )
            db_session.add(resource)
            db_session.flush()
            resource_ids.append(resource.id)

            # Add to collection
            assoc = CollectionResource(
                collection_id=collection.id, resource_id=resource.id
            )
            db_session.add(assoc)

        db_session.commit()

        # Compute embedding
        result = service.compute_collection_embedding(collection.id)

        # Verify result
        assert result is not None
        assert len(result) == 3

        # Expected: mean of [1,0,0], [0,1,0], [0,0,1] = [0.33, 0.33, 0.33]
        # Then normalized to unit length
        expected = np.array([1 / 3, 1 / 3, 1 / 3])
        expected = expected / np.linalg.norm(expected)

        np.testing.assert_array_almost_equal(result, expected, decimal=5)

        # Verify stored in database
        db_session.refresh(collection)
        assert collection.embedding is not None
        assert len(collection.embedding) == 3

    def test_compute_embedding_empty_collection(self, db_session):
        """Test computing embedding for empty collection returns None."""
        service = CollectionService(db_session)

        # Create empty collection
        collection = Collection(
            name="Empty Collection",
            description="Test",
            owner_id="user1",
            visibility="private",
        )
        db_session.add(collection)
        db_session.commit()

        # Compute embedding
        result = service.compute_collection_embedding(collection.id)

        # Should return None for empty collection
        assert result is None

        # Verify not stored in database
        db_session.refresh(collection)
        assert collection.embedding is None

    def test_compute_embedding_no_embeddings(self, db_session):
        """Test computing embedding when resources have no embeddings."""
        service = CollectionService(db_session)

        # Create collection
        collection = Collection(
            name="Test Collection",
            description="Test",
            owner_id="user1",
            visibility="private",
        )
        db_session.add(collection)
        db_session.commit()

        # Create resources WITHOUT embeddings
        for i in range(3):
            resource = Resource(
                title=f"Resource {i}",
                source=f"http://example.com/{i}",
                type="article",
                embedding=None,
                quality_score=0.8,
            )
            db_session.add(resource)
            db_session.flush()

            # Add to collection
            assoc = CollectionResource(
                collection_id=collection.id, resource_id=resource.id
            )
            db_session.add(assoc)

        db_session.commit()

        # Compute embedding
        result = service.compute_collection_embedding(collection.id)

        # Should return None when no resources have embeddings
        assert result is None


class TestResourceRecommendations:
    """Test resource recommendations based on collection embedding."""

    def test_find_similar_resources(self, db_session):
        """Test finding resources similar to collection."""
        service = CollectionService(db_session)

        # Create collection with embedding
        collection = Collection(
            name="ML Collection",
            description="Machine Learning",
            owner_id="user1",
            visibility="private",
            embedding=[1.0, 0.0, 0.0],  # Normalized
        )
        db_session.add(collection)
        db_session.commit()

        # Create similar resource (high similarity)
        similar_resource = Resource(
            title="Similar ML Paper",
            source="http://example.com/similar",
            type="article",
            embedding=[0.9, 0.1, 0.0],  # Close to collection
            quality_score=0.9,
        )
        db_session.add(similar_resource)

        # Create dissimilar resource (low similarity)
        dissimilar_resource = Resource(
            title="Unrelated Paper",
            source="http://example.com/dissimilar",
            type="article",
            embedding=[0.0, 0.0, 1.0],  # Far from collection
            quality_score=0.8,
        )
        db_session.add(dissimilar_resource)
        db_session.commit()

        # Find similar resources
        results = service.find_similar_resources(
            collection_id=collection.id, owner_id="user1", limit=10, min_similarity=0.5
        )

        # Should find similar resource but not dissimilar one
        assert len(results) == 1
        assert results[0]["resource_id"] == similar_resource.id
        assert results[0]["similarity_score"] > 0.8

    def test_exclude_collection_resources(self, db_session):
        """Test excluding resources already in collection."""
        service = CollectionService(db_session)

        # Create collection
        collection = Collection(
            name="Test Collection",
            description="Test",
            owner_id="user1",
            visibility="private",
            embedding=[1.0, 0.0, 0.0],
        )
        db_session.add(collection)
        db_session.commit()

        # Create resource in collection
        in_collection = Resource(
            title="In Collection",
            source="http://example.com/in",
            type="article",
            embedding=[0.95, 0.05, 0.0],
            quality_score=0.9,
        )
        db_session.add(in_collection)
        db_session.flush()

        assoc = CollectionResource(
            collection_id=collection.id, resource_id=in_collection.id
        )
        db_session.add(assoc)

        # Create resource not in collection
        not_in_collection = Resource(
            title="Not In Collection",
            source="http://example.com/not-in",
            type="article",
            embedding=[0.9, 0.1, 0.0],
            quality_score=0.9,
        )
        db_session.add(not_in_collection)
        db_session.commit()

        # Find similar resources with exclusion
        results = service.find_similar_resources(
            collection_id=collection.id,
            owner_id="user1",
            limit=10,
            min_similarity=0.5,
            exclude_collection_resources=True,
        )

        # Should only find resource not in collection
        assert len(results) == 1
        assert results[0]["resource_id"] == not_in_collection.id

    def test_no_embedding_raises_error(self, db_session):
        """Test that finding similar resources without embedding raises error."""
        service = CollectionService(db_session)

        # Create collection without embedding
        collection = Collection(
            name="No Embedding",
            description="Test",
            owner_id="user1",
            visibility="private",
            embedding=None,
        )
        db_session.add(collection)
        db_session.commit()

        # Should raise error
        with pytest.raises(ValueError, match="no embedding"):
            service.find_similar_resources(
                collection_id=collection.id, owner_id="user1"
            )


class TestCollectionRecommendations:
    """Test collection recommendations based on embedding similarity."""

    def test_find_similar_collections(self, db_session):
        """Test finding collections similar to source collection."""
        service = CollectionService(db_session)

        # Create source collection
        source = Collection(
            name="ML Collection",
            description="Machine Learning",
            owner_id="user1",
            visibility="private",
            embedding=[1.0, 0.0, 0.0],
        )
        db_session.add(source)

        # Create similar collection
        similar = Collection(
            name="AI Collection",
            description="Artificial Intelligence",
            owner_id="user2",
            visibility="public",
            embedding=[0.9, 0.1, 0.0],
        )
        db_session.add(similar)

        # Create dissimilar collection
        dissimilar = Collection(
            name="Biology Collection",
            description="Biology",
            owner_id="user2",
            visibility="public",
            embedding=[0.0, 0.0, 1.0],
        )
        db_session.add(dissimilar)
        db_session.commit()

        # Find similar collections
        results = service.find_similar_collections(
            collection_id=source.id, owner_id="user1", limit=10, min_similarity=0.5
        )

        # Should find similar collection but not dissimilar one
        assert len(results) == 1
        assert results[0]["collection_id"] == similar.id
        assert results[0]["similarity_score"] > 0.8

    def test_visibility_filtering(self, db_session):
        """Test that visibility is respected in recommendations."""
        service = CollectionService(db_session)

        # Create source collection
        source = Collection(
            name="Source",
            description="Test",
            owner_id="user1",
            visibility="private",
            embedding=[1.0, 0.0, 0.0],
        )
        db_session.add(source)

        # Create private collection from another user (should not appear)
        private_other = Collection(
            name="Private Other",
            description="Test",
            owner_id="user2",
            visibility="private",
            embedding=[0.95, 0.05, 0.0],
        )
        db_session.add(private_other)

        # Create public collection (should appear)
        public = Collection(
            name="Public",
            description="Test",
            owner_id="user2",
            visibility="public",
            embedding=[0.9, 0.1, 0.0],
        )
        db_session.add(public)
        db_session.commit()

        # Find similar collections
        results = service.find_similar_collections(
            collection_id=source.id, owner_id="user1", limit=10, min_similarity=0.5
        )

        # Should only find public collection
        assert len(results) == 1
        assert results[0]["collection_id"] == public.id


class TestHierarchyValidation:
    """Test hierarchy validation to prevent circular references."""

    def test_valid_parent_assignment(self, db_session):
        """Test that valid parent assignment is allowed."""
        service = CollectionService(db_session)

        # Create parent and child collections
        parent = Collection(
            name="Parent", description="Test", owner_id="user1", visibility="private"
        )
        db_session.add(parent)

        child = Collection(
            name="Child", description="Test", owner_id="user1", visibility="private"
        )
        db_session.add(child)
        db_session.commit()

        # Validate parent assignment
        is_valid, error_msg = service.validate_parent_hierarchy(child.id, parent.id)

        assert is_valid is True
        assert error_msg == ""

    def test_self_parent_rejected(self, db_session):
        """Test that collection cannot be its own parent."""
        service = CollectionService(db_session)

        # Create collection
        collection = Collection(
            name="Test", description="Test", owner_id="user1", visibility="private"
        )
        db_session.add(collection)
        db_session.commit()

        # Try to set as own parent
        is_valid, error_msg = service.validate_parent_hierarchy(
            collection.id, collection.id
        )

        assert is_valid is False
        assert "cannot be its own parent" in error_msg

    def test_circular_reference_rejected(self, db_session):
        """Test that circular references are detected and rejected."""
        service = CollectionService(db_session)

        # Create chain: A -> B -> C
        collection_a = Collection(
            name="A", description="Test", owner_id="user1", visibility="private"
        )
        db_session.add(collection_a)
        db_session.flush()

        collection_b = Collection(
            name="B",
            description="Test",
            owner_id="user1",
            visibility="private",
            parent_id=collection_a.id,
        )
        db_session.add(collection_b)
        db_session.flush()

        collection_c = Collection(
            name="C",
            description="Test",
            owner_id="user1",
            visibility="private",
            parent_id=collection_b.id,
        )
        db_session.add(collection_c)
        db_session.commit()

        # Try to set C as parent of A (would create cycle: A -> B -> C -> A)
        is_valid, error_msg = service.validate_parent_hierarchy(
            collection_a.id, collection_c.id
        )

        assert is_valid is False
        assert "circular reference" in error_msg

    def test_deep_hierarchy_allowed(self, db_session):
        """Test that deep but non-circular hierarchies are allowed."""
        service = CollectionService(db_session)

        # Create chain: A -> B -> C -> D
        prev_id = None
        collections = []

        for name in ["A", "B", "C", "D"]:
            collection = Collection(
                name=name,
                description="Test",
                owner_id="user1",
                visibility="private",
                parent_id=prev_id,
            )
            db_session.add(collection)
            db_session.flush()
            collections.append(collection)
            prev_id = collection.id

        db_session.commit()

        # Create new collection E and try to set D as parent (valid)
        collection_e = Collection(
            name="E", description="Test", owner_id="user1", visibility="private"
        )
        db_session.add(collection_e)
        db_session.commit()

        is_valid, error_msg = service.validate_parent_hierarchy(
            collection_e.id, collections[-1].id
        )

        assert is_valid is True
        assert error_msg == ""


class TestBatchOperations:
    """Test batch resource operations."""

    def test_batch_add_resources(self, db_session):
        """Test adding multiple resources in batch."""
        service = CollectionService(db_session)

        # Create collection
        collection = Collection(
            name="Test Collection",
            description="Test",
            owner_id="user1",
            visibility="private",
        )
        db_session.add(collection)
        db_session.commit()

        # Create resources
        resource_ids = []
        for i in range(5):
            resource = Resource(
                title=f"Resource {i}",
                source=f"http://example.com/{i}",
                type="article",
                quality_score=0.8,
            )
            db_session.add(resource)
            db_session.flush()
            resource_ids.append(resource.id)

        db_session.commit()

        # Batch add resources
        result = service.add_resources_batch(
            collection_id=collection.id, resource_ids=resource_ids, owner_id="user1"
        )

        # Verify results
        assert result["added"] == 5
        assert result["skipped"] == 0
        assert result["invalid"] == 0

        # Verify associations created
        associations = (
            db_session.query(CollectionResource)
            .filter(CollectionResource.collection_id == collection.id)
            .all()
        )

        assert len(associations) == 5

    def test_batch_add_with_duplicates(self, db_session):
        """Test batch add skips duplicates."""
        service = CollectionService(db_session)

        # Create collection
        collection = Collection(
            name="Test Collection",
            description="Test",
            owner_id="user1",
            visibility="private",
        )
        db_session.add(collection)
        db_session.commit()

        # Create resources
        resource_ids = []
        for i in range(3):
            resource = Resource(
                title=f"Resource {i}",
                source=f"http://example.com/{i}",
                type="article",
                quality_score=0.8,
            )
            db_session.add(resource)
            db_session.flush()
            resource_ids.append(resource.id)

        db_session.commit()

        # Add first 2 resources
        service.add_resources_batch(
            collection_id=collection.id, resource_ids=resource_ids[:2], owner_id="user1"
        )

        # Try to add all 3 (first 2 are duplicates)
        result = service.add_resources_batch(
            collection_id=collection.id, resource_ids=resource_ids, owner_id="user1"
        )

        # Should add 1 new, skip 2 duplicates
        assert result["added"] == 1
        assert result["skipped"] == 2
        assert result["invalid"] == 0

    def test_batch_add_exceeds_limit(self, db_session):
        """Test batch add rejects more than 100 resources."""
        service = CollectionService(db_session)

        # Create collection
        collection = Collection(
            name="Test Collection",
            description="Test",
            owner_id="user1",
            visibility="private",
        )
        db_session.add(collection)
        db_session.commit()

        # Try to add 101 resources
        resource_ids = [uuid.uuid4() for _ in range(101)]

        with pytest.raises(ValueError, match="exceed 100"):
            service.add_resources_batch(
                collection_id=collection.id, resource_ids=resource_ids, owner_id="user1"
            )

    def test_batch_remove_resources(self, db_session):
        """Test removing multiple resources in batch."""
        service = CollectionService(db_session)

        # Create collection
        collection = Collection(
            name="Test Collection",
            description="Test",
            owner_id="user1",
            visibility="private",
        )
        db_session.add(collection)
        db_session.commit()

        # Create and add resources
        resource_ids = []
        for i in range(5):
            resource = Resource(
                title=f"Resource {i}",
                source=f"http://example.com/{i}",
                type="article",
                quality_score=0.8,
            )
            db_session.add(resource)
            db_session.flush()
            resource_ids.append(resource.id)

            assoc = CollectionResource(
                collection_id=collection.id, resource_id=resource.id
            )
            db_session.add(assoc)

        db_session.commit()

        # Batch remove 3 resources
        result = service.remove_resources_batch(
            collection_id=collection.id, resource_ids=resource_ids[:3], owner_id="user1"
        )

        # Verify results
        assert result["removed"] == 3
        assert result["not_found"] == 0

        # Verify associations removed
        remaining = (
            db_session.query(CollectionResource)
            .filter(CollectionResource.collection_id == collection.id)
            .count()
        )

        assert remaining == 2

    def test_batch_remove_nonexistent(self, db_session):
        """Test batch remove handles nonexistent resources."""
        service = CollectionService(db_session)

        # Create collection
        collection = Collection(
            name="Test Collection",
            description="Test",
            owner_id="user1",
            visibility="private",
        )
        db_session.add(collection)
        db_session.commit()

        # Try to remove resources that don't exist
        fake_ids = [uuid.uuid4() for _ in range(3)]

        result = service.remove_resources_batch(
            collection_id=collection.id, resource_ids=fake_ids, owner_id="user1"
        )

        # Should report all as not found
        assert result["removed"] == 0
        assert result["not_found"] == 3
