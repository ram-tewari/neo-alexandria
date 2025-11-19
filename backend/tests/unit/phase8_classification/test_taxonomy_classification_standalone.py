"""
Standalone verification script for taxonomy resource classification functionality.

Tests:
1. classify_resource() method
2. _update_resource_counts() method
3. Confidence-based review flagging
4. Resource count updates
"""

import sys
import uuid
from datetime import datetime, timezone


from sqlalchemy import create_engine, String, Text, DateTime, Float, JSON, Integer, ForeignKey, func
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase
from typing import List


# Minimal model definitions for testing
class Base(DeclarativeBase):
    pass


class GUID(TypeDecorator):
    """Platform-independent GUID type."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value


class Resource(Base):
    """Minimal Resource model for testing."""
    __tablename__ = "resources"
    
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())


class TaxonomyNode(Base):
    """Minimal TaxonomyNode model for testing."""
    __tablename__ = "taxonomy_nodes"
    
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("taxonomy_nodes.id", ondelete="CASCADE"), nullable=True, index=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    path: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[List[str] | None] = mapped_column(JSON, nullable=True)
    resource_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    descendant_resource_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    is_leaf: Mapped[bool] = mapped_column(Integer, nullable=False, default=1, server_default='1')
    allow_resources: Mapped[bool] = mapped_column(Integer, nullable=False, default=1, server_default='1')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    
    parent: Mapped["TaxonomyNode"] = relationship("TaxonomyNode", remote_side=[id], back_populates="children", foreign_keys=[parent_id])
    children: Mapped[List["TaxonomyNode"]] = relationship("TaxonomyNode", back_populates="parent", cascade="all, delete-orphan", foreign_keys=[parent_id])


class ResourceTaxonomy(Base):
    """Minimal ResourceTaxonomy model for testing."""
    __tablename__ = "resource_taxonomy"
    
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    resource_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    taxonomy_node_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("taxonomy_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, server_default='0.0')
    is_predicted: Mapped[bool] = mapped_column(Integer, nullable=False, default=1, server_default='1')
    predicted_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    needs_review: Mapped[bool] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    review_priority: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    
    resource: Mapped["Resource"] = relationship("Resource")
    taxonomy_node: Mapped["TaxonomyNode"] = relationship("TaxonomyNode")


# Import the actual TaxonomyService
from backend.app.services.taxonomy_service import TaxonomyService


def setup_test_db():
    """Create in-memory test database."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_classify_resource():
    """Test classify_resource() method."""
    print("\n=== Test 1: classify_resource() ===")
    
    db = setup_test_db()
    service = TaxonomyService(db)
    
    # Create taxonomy nodes
    root = service.create_node(name="Computer Science")
    ml_node = service.create_node(name="Machine Learning", parent_id=root.id)
    dl_node = service.create_node(name="Deep Learning", parent_id=ml_node.id)
    
    # Create a test resource
    resource = Resource(
        id=uuid.uuid4(),
        title="Introduction to Neural Networks",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(resource)
    db.commit()
    
    # Classify resource with multiple categories
    classifications = [
        {"taxonomy_node_id": ml_node.id, "confidence": 0.95},
        {"taxonomy_node_id": dl_node.id, "confidence": 0.88},
        {"taxonomy_node_id": root.id, "confidence": 0.65}  # Low confidence
    ]
    
    result = service.classify_resource(
        resource_id=resource.id,
        classifications=classifications,
        predicted_by="test_model_v1.0"
    )
    
    # Verify results
    assert len(result) == 3, f"Expected 3 classifications, got {len(result)}"
    
    # Check high confidence classification
    high_conf = [c for c in result if c.taxonomy_node_id == ml_node.id][0]
    assert high_conf.confidence == 0.95, f"Expected confidence 0.95, got {high_conf.confidence}"
    assert high_conf.is_predicted, "Should be predicted"
    assert high_conf.predicted_by == "test_model_v1.0", f"Expected test_model_v1.0, got {high_conf.predicted_by}"
    assert not high_conf.needs_review, "High confidence should not need review"
    assert high_conf.review_priority is None, "High confidence should have no review priority"
    
    # Check low confidence classification
    low_conf = [c for c in result if c.taxonomy_node_id == root.id][0]
    assert low_conf.confidence == 0.65, f"Expected confidence 0.65, got {low_conf.confidence}"
    assert low_conf.needs_review, "Low confidence should need review"
    assert low_conf.review_priority is not None, "Low confidence should have review priority"
    assert abs(low_conf.review_priority - 0.35) < 0.01, f"Expected review_priority ~0.35, got {low_conf.review_priority}"
    
    print("✓ Classifications created successfully")
    print(f"✓ High confidence (0.95): needs_review={high_conf.needs_review}")
    print(f"✓ Low confidence (0.65): needs_review={low_conf.needs_review}, priority={low_conf.review_priority:.2f}")
    
    db.close()
    return True


def test_remove_existing_predicted():
    """Test that existing predicted classifications are removed."""
    print("\n=== Test 2: Remove Existing Predicted Classifications ===")
    
    db = setup_test_db()
    service = TaxonomyService(db)
    
    # Create taxonomy nodes
    node1 = service.create_node(name="Category 1")
    node2 = service.create_node(name="Category 2")
    
    # Create a test resource
    resource = Resource(
        id=uuid.uuid4(),
        title="Test Resource",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(resource)
    db.commit()
    
    # First classification
    service.classify_resource(
        resource_id=resource.id,
        classifications=[{"taxonomy_node_id": node1.id, "confidence": 0.8}],
        predicted_by="model_v1"
    )
    
    # Verify first classification exists
    count1 = db.query(ResourceTaxonomy).filter(
        ResourceTaxonomy.resource_id == resource.id
    ).count()
    assert count1 == 1, f"Expected 1 classification, got {count1}"
    
    # Second classification (should replace first)
    service.classify_resource(
        resource_id=resource.id,
        classifications=[{"taxonomy_node_id": node2.id, "confidence": 0.9}],
        predicted_by="model_v2"
    )
    
    # Verify only second classification exists
    count2 = db.query(ResourceTaxonomy).filter(
        ResourceTaxonomy.resource_id == resource.id
    ).count()
    assert count2 == 1, f"Expected 1 classification after replacement, got {count2}"
    
    final_class = db.query(ResourceTaxonomy).filter(
        ResourceTaxonomy.resource_id == resource.id
    ).first()
    assert final_class.taxonomy_node_id == node2.id, "Should have node2 classification"
    assert final_class.predicted_by == "model_v2", "Should have model_v2"
    
    print("✓ Existing predicted classifications removed correctly")
    print(f"✓ Final classification: node={final_class.taxonomy_node_id}, model={final_class.predicted_by}")
    
    db.close()
    return True


def test_update_resource_counts():
    """Test _update_resource_counts() method."""
    print("\n=== Test 3: Update Resource Counts ===")
    
    db = setup_test_db()
    service = TaxonomyService(db)
    
    # Create hierarchical taxonomy
    root = service.create_node(name="Science")
    physics = service.create_node(name="Physics", parent_id=root.id)
    quantum = service.create_node(name="Quantum Mechanics", parent_id=physics.id)
    
    # Create resources
    resources = []
    for i in range(3):
        resource = Resource(
            id=uuid.uuid4(),
            title=f"Resource {i+1}",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(resource)
        resources.append(resource)
    db.commit()
    
    # Classify resources at different levels
    # Resource 1 -> root
    service.classify_resource(
        resource_id=resources[0].id,
        classifications=[{"taxonomy_node_id": root.id, "confidence": 0.9}]
    )
    
    # Resource 2 -> physics
    service.classify_resource(
        resource_id=resources[1].id,
        classifications=[{"taxonomy_node_id": physics.id, "confidence": 0.9}]
    )
    
    # Resource 3 -> quantum
    service.classify_resource(
        resource_id=resources[2].id,
        classifications=[{"taxonomy_node_id": quantum.id, "confidence": 0.9}]
    )
    
    # Refresh nodes to get updated counts
    db.refresh(root)
    db.refresh(physics)
    db.refresh(quantum)
    
    # Verify counts
    print(f"Root: direct={root.resource_count}, descendants={root.descendant_resource_count}")
    print(f"Physics: direct={physics.resource_count}, descendants={physics.descendant_resource_count}")
    print(f"Quantum: direct={quantum.resource_count}, descendants={quantum.descendant_resource_count}")
    
    assert root.resource_count == 1, f"Root should have 1 direct resource, got {root.resource_count}"
    assert root.descendant_resource_count == 2, f"Root should have 2 descendant resources, got {root.descendant_resource_count}"
    
    assert physics.resource_count == 1, f"Physics should have 1 direct resource, got {physics.resource_count}"
    assert physics.descendant_resource_count == 1, f"Physics should have 1 descendant resource, got {physics.descendant_resource_count}"
    
    assert quantum.resource_count == 1, f"Quantum should have 1 direct resource, got {quantum.resource_count}"
    assert quantum.descendant_resource_count == 0, f"Quantum should have 0 descendant resources, got {quantum.descendant_resource_count}"
    
    print("✓ Resource counts updated correctly")
    print("✓ Hierarchical count propagation working")
    
    db.close()
    return True


def test_allow_resources_flag():
    """Test that nodes with allow_resources=False are skipped."""
    print("\n=== Test 4: Allow Resources Flag ===")
    
    db = setup_test_db()
    service = TaxonomyService(db)
    
    # Create nodes with different allow_resources settings
    allowed_node = service.create_node(name="Allowed Category", allow_resources=True)
    disallowed_node = service.create_node(name="Disallowed Category", allow_resources=False)
    
    # Create a test resource
    resource = Resource(
        id=uuid.uuid4(),
        title="Test Resource",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(resource)
    db.commit()
    
    # Try to classify with both nodes
    classifications = [
        {"taxonomy_node_id": allowed_node.id, "confidence": 0.9},
        {"taxonomy_node_id": disallowed_node.id, "confidence": 0.9}
    ]
    
    result = service.classify_resource(
        resource_id=resource.id,
        classifications=classifications
    )
    
    # Verify only allowed node was classified
    assert len(result) == 1, f"Expected 1 classification, got {len(result)}"
    assert result[0].taxonomy_node_id == allowed_node.id, "Should only have allowed node"
    
    print("✓ Disallowed nodes skipped correctly")
    print(f"✓ Only {len(result)} classification created (allowed node)")
    
    db.close()
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Taxonomy Resource Classification Verification")
    print("=" * 60)
    
    tests = [
        ("classify_resource()", test_classify_resource),
        ("Remove Existing Predicted", test_remove_existing_predicted),
        ("Update Resource Counts", test_update_resource_counts),
        ("Allow Resources Flag", test_allow_resources_flag)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n✗ {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
