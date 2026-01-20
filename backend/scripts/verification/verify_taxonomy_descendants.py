"""
Verification script for TaxonomyService.get_descendants() method.

This script tests the get_descendants() implementation to ensure it:
1. Queries nodes with path LIKE pattern
2. Returns all descendants at any depth
3. Handles nodes with no descendants
"""

import sys
import os
import uuid

# Setup path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(backend_dir)
sys.path.insert(0, parent_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.base import Base
from backend.app.services.taxonomy_service import TaxonomyService


def verify_get_descendants():
    """Verify get_descendants() implementation."""

    # Create in-memory database
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        service = TaxonomyService(db)

        print("=" * 80)
        print("TAXONOMY SERVICE - get_descendants() VERIFICATION")
        print("=" * 80)

        # Test 1: Create hierarchical taxonomy
        print("\n1. Creating hierarchical taxonomy...")
        root = service.create_node(name="Computer Science")
        print(f"   ✓ Created root: {root.name} (path: {root.path})")

        ml = service.create_node(name="Machine Learning", parent_id=root.id)
        print(f"   ✓ Created child: {ml.name} (path: {ml.path})")

        dl = service.create_node(name="Deep Learning", parent_id=ml.id)
        print(f"   ✓ Created grandchild: {dl.name} (path: {dl.path})")

        nlp = service.create_node(name="Natural Language Processing", parent_id=ml.id)
        print(f"   ✓ Created grandchild: {nlp.name} (path: {nlp.path})")

        cv = service.create_node(name="Computer Vision", parent_id=dl.id)
        print(f"   ✓ Created great-grandchild: {cv.name} (path: {cv.path})")

        db_node = service.create_node(name="Databases", parent_id=root.id)
        print(f"   ✓ Created child: {db_node.name} (path: {db_node.path})")

        # Test 2: Get descendants of root (should return all children)
        print("\n2. Testing get_descendants() for root node...")
        descendants = service.get_descendants(root.id)
        print(f"   ✓ Found {len(descendants)} descendants")

        expected_names = {
            "Machine Learning",
            "Deep Learning",
            "Natural Language Processing",
            "Computer Vision",
            "Databases",
        }
        actual_names = {d.name for d in descendants}

        if actual_names == expected_names:
            print(f"   ✓ All expected descendants found: {sorted(actual_names)}")
        else:
            print(f"   ✗ ERROR: Expected {expected_names}, got {actual_names}")
            return False

        # Test 3: Get descendants of middle node
        print("\n3. Testing get_descendants() for middle node (Machine Learning)...")
        ml_descendants = service.get_descendants(ml.id)
        print(f"   ✓ Found {len(ml_descendants)} descendants")

        expected_ml_names = {
            "Deep Learning",
            "Natural Language Processing",
            "Computer Vision",
        }
        actual_ml_names = {d.name for d in ml_descendants}

        if actual_ml_names == expected_ml_names:
            print(f"   ✓ All expected descendants found: {sorted(actual_ml_names)}")
        else:
            print(f"   ✗ ERROR: Expected {expected_ml_names}, got {actual_ml_names}")
            return False

        # Test 4: Get descendants of leaf node (should return empty)
        print("\n4. Testing get_descendants() for leaf node (Databases)...")
        leaf_descendants = service.get_descendants(db_node.id)
        print(f"   ✓ Found {len(leaf_descendants)} descendants")

        if len(leaf_descendants) == 0:
            print("   ✓ Correctly returned empty list for leaf node")
        else:
            print(f"   ✗ ERROR: Expected 0 descendants, got {len(leaf_descendants)}")
            return False

        # Test 5: Verify path pattern matching works correctly
        print("\n5. Verifying path pattern matching...")
        for desc in descendants:
            if not desc.path.startswith(f"{root.path}/"):
                print(
                    f"   ✗ ERROR: Descendant path {desc.path} doesn't start with {root.path}/"
                )
                return False
        print("   ✓ All descendants have correct path prefix")

        # Test 6: Verify ordering (by level and name)
        print("\n6. Verifying ordering (by level and name)...")
        prev_level = -1
        prev_name = ""
        for desc in descendants:
            if desc.level < prev_level:
                print("   ✗ ERROR: Descendants not ordered by level")
                return False
            if desc.level == prev_level and desc.name < prev_name:
                print("   ✗ ERROR: Descendants not ordered by name within same level")
                return False
            prev_level = desc.level
            prev_name = desc.name
        print("   ✓ Descendants correctly ordered by level and name")

        # Test 7: Test with non-existent node
        print("\n7. Testing get_descendants() with non-existent node...")
        try:
            fake_id = uuid.uuid4()
            service.get_descendants(fake_id)
            print("   ✗ ERROR: Should have raised ValueError for non-existent node")
            return False
        except ValueError as e:
            print(f"   ✓ Correctly raised ValueError: {e}")

        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED - get_descendants() implementation is correct!")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = verify_get_descendants()
    sys.exit(0 if success else 1)
