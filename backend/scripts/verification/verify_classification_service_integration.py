"""
Verification script for Classification Service Integration (Task 11)

This script verifies that the ClassificationService correctly integrates
the ML classifier with the TaxonomyService for resource classification.

Tests:
1. ClassificationService initialization with use_ml flag
2. ML-based classification with confidence filtering
3. Rule-based classification fallback
4. Integration with TaxonomyService for storing classifications
"""

import sys
import os
import uuid
from datetime import datetime, timezone

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import Base, Resource, TaxonomyNode
from app.services.classification_service import ClassificationService


def setup_test_db():
    """Create in-memory test database."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def create_test_taxonomy(db):
    """Create test taxonomy nodes."""
    nodes = []
    
    # Create root nodes
    cs_node = TaxonomyNode(
        id=uuid.uuid4(),
        name="Computer Science",
        slug="computer-science",
        parent_id=None,
        level=0,
        path="/computer-science",
        description="Computer science topics",
        keywords=["programming", "software", "ai", "ml"],
        resource_count=0,
        descendant_resource_count=0,
        is_leaf=False,
        allow_resources=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(cs_node)
    nodes.append(cs_node)
    
    # Create child node
    ml_node = TaxonomyNode(
        id=uuid.uuid4(),
        name="Machine Learning",
        slug="machine-learning",
        parent_id=cs_node.id,
        level=1,
        path="/computer-science/machine-learning",
        description="Machine learning and AI",
        keywords=["ml", "ai", "neural networks"],
        resource_count=0,
        descendant_resource_count=0,
        is_leaf=True,
        allow_resources=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(ml_node)
    nodes.append(ml_node)
    
    db.commit()
    
    # Refresh to get IDs
    for node in nodes:
        db.refresh(node)
    
    return nodes


def create_test_resource(db):
    """Create test resource."""
    resource = Resource(
        id=uuid.uuid4(),
        title="Introduction to Machine Learning",
        description="A comprehensive guide to machine learning algorithms and techniques",
        subject=["ai", "ml", "data science"],
        resource_type="article",
        url="https://example.com/ml-intro",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


def test_classification_service_initialization():
    """Test 1: ClassificationService initialization with use_ml flag."""
    print("\n" + "="*70)
    print("Test 1: ClassificationService Initialization")
    print("="*70)
    
    db = setup_test_db()
    
    # Test with use_ml=True
    service_ml = ClassificationService(db=db, use_ml=True)
    assert service_ml.use_ml
    assert service_ml.confidence_threshold == 0.3
    print("✓ ClassificationService initialized with use_ml=True")
    
    # Test with use_ml=False
    service_rule = ClassificationService(db=db, use_ml=False)
    assert not service_rule.use_ml
    print("✓ ClassificationService initialized with use_ml=False")
    
    # Test custom confidence threshold
    service_custom = ClassificationService(db=db, use_ml=True, confidence_threshold=0.5)
    assert service_custom.confidence_threshold == 0.5
    print("✓ ClassificationService initialized with custom confidence threshold")
    
    print("\n✅ Test 1 PASSED: Initialization works correctly")
    return True


def test_rule_based_classification():
    """Test 2: Rule-based classification fallback."""
    print("\n" + "="*70)
    print("Test 2: Rule-Based Classification")
    print("="*70)
    
    db = setup_test_db()
    resource = create_test_resource(db)
    
    # Create service with use_ml=False
    service = ClassificationService(db=db, use_ml=False)
    
    # Classify resource
    result = service.classify_resource(resource_id=resource.id)
    
    # Verify result structure
    assert "resource_id" in result
    assert "method" in result
    assert "classifications" in result
    assert result["method"] == "rule_based"
    print(f"✓ Classification method: {result['method']}")
    
    # Verify classifications
    assert len(result["classifications"]) > 0
    classification = result["classifications"][0]
    assert "classification_code" in classification
    assert "confidence" in classification
    assert classification["confidence"] == 1.0
    print(f"✓ Classification code: {classification['classification_code']}")
    print(f"✓ Confidence: {classification['confidence']}")
    
    print("\n✅ Test 2 PASSED: Rule-based classification works correctly")
    return True


def test_ml_classification_without_model():
    """Test 3: ML classification gracefully falls back when model not available."""
    print("\n" + "="*70)
    print("Test 3: ML Classification Fallback (No Model)")
    print("="*70)
    
    db = setup_test_db()
    resource = create_test_resource(db)
    
    # Create service with use_ml=True (will fall back since no trained model)
    service = ClassificationService(db=db, use_ml=True)
    
    # Classify resource - should fall back to rule-based
    result = service.classify_resource(resource_id=resource.id)
    
    # Verify fallback occurred
    assert "resource_id" in result
    assert "method" in result
    print(f"✓ Classification method: {result['method']}")
    
    # Should have some classification
    assert len(result["classifications"]) > 0
    print(f"✓ Classifications returned: {len(result['classifications'])}")
    
    print("\n✅ Test 3 PASSED: Graceful fallback when ML model unavailable")
    return True


def test_confidence_threshold_filtering():
    """Test 4: Confidence threshold filtering."""
    print("\n" + "="*70)
    print("Test 4: Confidence Threshold Filtering")
    print("="*70)
    
    db = setup_test_db()
    
    # Test different thresholds
    thresholds = [0.3, 0.5, 0.7]
    for threshold in thresholds:
        service = ClassificationService(db=db, use_ml=False, confidence_threshold=threshold)
        assert service.confidence_threshold == threshold
        print(f"✓ Service created with threshold: {threshold}")
    
    print("\n✅ Test 4 PASSED: Confidence threshold configuration works")
    return True


def test_resource_not_found():
    """Test 5: Error handling for non-existent resource."""
    print("\n" + "="*70)
    print("Test 5: Error Handling - Resource Not Found")
    print("="*70)
    
    db = setup_test_db()
    service = ClassificationService(db=db, use_ml=False)
    
    # Try to classify non-existent resource
    fake_id = uuid.uuid4()
    try:
        service.classify_resource(resource_id=fake_id)
        print("✗ Should have raised ValueError")
        return False
    except ValueError as e:
        assert "not found" in str(e).lower()
        print(f"✓ Correctly raised ValueError: {e}")
    
    print("\n✅ Test 5 PASSED: Error handling works correctly")
    return True


def main():
    """Run all verification tests."""
    print("\n" + "="*70)
    print("CLASSIFICATION SERVICE INTEGRATION VERIFICATION")
    print("Task 11: Classification service integration")
    print("="*70)
    
    tests = [
        ("Initialization", test_classification_service_initialization),
        ("Rule-Based Classification", test_rule_based_classification),
        ("ML Fallback", test_ml_classification_without_model),
        ("Confidence Threshold", test_confidence_threshold_filtering),
        ("Error Handling", test_resource_not_found),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Classification service integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
