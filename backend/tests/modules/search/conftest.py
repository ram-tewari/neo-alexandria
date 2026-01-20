"""
Fixtures for search module tests.
"""

import pytest
import uuid

from app.database.models import (
    Resource,
    DocumentChunk,
    GraphEntity,
    GraphRelationship,
)


@pytest.fixture
def sample_resource_with_chunks(db_session):
    """Create a sample resource with chunks for testing."""
    # Create resource
    resource = Resource(
        id=uuid.uuid4(),
        title="Machine Learning Fundamentals",
        source="https://example.com/ml",
        type="article",
        description="Machine learning is a subset of artificial intelligence. Neural networks are powerful models.",
    )
    db_session.add(resource)
    db_session.flush()

    # Create chunks with embedding IDs
    chunk1 = DocumentChunk(
        id=uuid.uuid4(),
        resource_id=resource.id,
        content="Machine learning is a subset of artificial intelligence.",
        chunk_index=0,
        embedding_id=uuid.uuid4(),
        chunk_metadata={"page": 1},
    )
    chunk2 = DocumentChunk(
        id=uuid.uuid4(),
        resource_id=resource.id,
        content="Neural networks are powerful models.",
        chunk_index=1,
        embedding_id=uuid.uuid4(),
        chunk_metadata={"page": 1},
    )
    db_session.add(chunk1)
    db_session.add(chunk2)
    db_session.commit()

    return {"resource": resource, "chunks": [chunk1, chunk2]}


@pytest.fixture
def sample_graph_data(db_session, sample_resource_with_chunks):
    """Create sample graph entities and relationships."""
    chunk1 = sample_resource_with_chunks["chunks"][0]

    # Create entities
    entity1 = GraphEntity(
        id=uuid.uuid4(),
        name="Machine Learning",
        type="Concept",
        description="A subset of AI",
    )
    entity2 = GraphEntity(
        id=uuid.uuid4(),
        name="Neural Networks",
        type="Concept",
        description="Powerful ML models",
    )
    db_session.add(entity1)
    db_session.add(entity2)
    db_session.flush()

    # Create relationship
    relationship = GraphRelationship(
        id=uuid.uuid4(),
        source_entity_id=entity1.id,
        target_entity_id=entity2.id,
        relation_type="EXTENDS",
        weight=0.9,
        provenance_chunk_id=chunk1.id,
    )
    db_session.add(relationship)
    db_session.commit()

    return {"entities": [entity1, entity2], "relationship": relationship}
