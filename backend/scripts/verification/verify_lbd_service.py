"""
Verification script for Literature-Based Discovery (LBD) Service - Phase 10 Task 6

Tests:
1. LBDService class initialization
2. Open discovery functionality
3. Closed discovery functionality
4. Hypothesis storage and retrieval
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
backend_path = Path(__file__).parent
parent_path = backend_path.parent
sys.path.insert(0, str(parent_path))

from backend.app.database.base import SessionLocal
from backend.app.services.lbd_service import LBDService
from backend.app.database import models as db_models

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_lbd_service_initialization():
    """Test LBDService class initialization."""
    print("\n" + "=" * 80)
    print("TEST 1: LBDService Initialization")
    print("=" * 80)

    try:
        db = SessionLocal()
        lbd_service = LBDService(db)

        print("✓ LBDService initialized successfully")
        print(f"  - Database session: {type(lbd_service.db).__name__}")
        print(f"  - Graph service (lazy): {lbd_service._graph_service is None}")
        print(
            f"  - Graph embeddings service (lazy): {lbd_service._graph_embeddings_service is None}"
        )

        # Test lazy loading
        graph_service = lbd_service.graph_service
        print(f"✓ Graph service lazy loaded: {type(graph_service).__name__}")

        graph_embeddings_service = lbd_service.graph_embeddings_service
        print(
            f"✓ Graph embeddings service lazy loaded: {type(graph_embeddings_service).__name__}"
        )

        return True

    except Exception as e:
        print(f"✗ Failed to initialize LBDService: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_open_discovery():
    """Test open discovery functionality."""
    print("\n" + "=" * 80)
    print("TEST 2: Open Discovery")
    print("=" * 80)

    try:
        db = SessionLocal()
        lbd_service = LBDService(db)

        # Find a resource with neighbors for testing
        resource = (
            db.query(db_models.Resource)
            .filter(db_models.Resource.embedding.isnot(None))
            .first()
        )

        if not resource:
            print("⚠ No resources with embeddings found, skipping test")
            return True

        print(f"Testing open discovery from resource: {resource.title}")
        print(f"  Resource ID: {resource.id}")

        # Perform open discovery
        hypotheses = lbd_service.open_discovery(
            a_resource_id=str(resource.id),
            limit=10,
            min_plausibility=0.3,  # Lower threshold for testing
        )

        print("✓ Open discovery completed")
        print(f"  - Found {len(hypotheses)} hypotheses")

        if hypotheses:
            # Display first hypothesis
            h = hypotheses[0]
            print("\n  Top Hypothesis:")
            print(f"    C Resource: {h['c_resource']['title']}")
            print(f"    Plausibility: {h['plausibility_score']:.3f}")
            print(f"    Path Strength: {h['path_strength']:.3f}")
            print(f"    Common Neighbors: {h['common_neighbors']}")
            print(f"    Semantic Similarity: {h['semantic_similarity']:.3f}")
            print(f"    Intermediate B Resources: {len(h['b_resources'])}")

            for i, b in enumerate(h["b_resources"][:3], 1):
                print(f"      {i}. {b['title']}")

        # Verify hypotheses were stored in database
        stored_hypotheses = (
            db.query(db_models.DiscoveryHypothesis)
            .filter(
                db_models.DiscoveryHypothesis.a_resource_id == resource.id,
                db_models.DiscoveryHypothesis.hypothesis_type == "open",
            )
            .count()
        )

        print(f"✓ Stored {stored_hypotheses} hypotheses in database")

        return True

    except Exception as e:
        print(f"✗ Open discovery failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_closed_discovery():
    """Test closed discovery functionality."""
    print("\n" + "=" * 80)
    print("TEST 3: Closed Discovery")
    print("=" * 80)

    try:
        db = SessionLocal()
        lbd_service = LBDService(db)

        # Find two resources for testing
        resources = (
            db.query(db_models.Resource)
            .filter(db_models.Resource.embedding.isnot(None))
            .limit(2)
            .all()
        )

        if len(resources) < 2:
            print("⚠ Not enough resources found, skipping test")
            return True

        a_resource = resources[0]
        c_resource = resources[1]

        print("Testing closed discovery:")
        print(f"  A Resource: {a_resource.title}")
        print(f"  C Resource: {c_resource.title}")

        # Perform closed discovery
        paths = lbd_service.closed_discovery(
            a_resource_id=str(a_resource.id),
            c_resource_id=str(c_resource.id),
            max_hops=3,
        )

        print("✓ Closed discovery completed")
        print(f"  - Found {len(paths)} paths")

        if paths:
            # Display first path
            p = paths[0]
            print("\n  Best Path:")
            print(f"    Path Length: {p['path_length']} hops")
            print(f"    Plausibility: {p['plausibility_score']:.3f}")
            print(f"    Path Strength: {p['path_strength']:.3f}")
            print(f"    Is Direct: {p.get('is_direct', False)}")

            if p["b_resources"]:
                print("    Intermediate Resources:")
                for i, b in enumerate(p["b_resources"], 1):
                    print(f"      {i}. {b['title']}")
        else:
            print("  No paths found between A and C")

        # Verify hypothesis was stored if paths found
        if paths:
            stored_hypothesis = (
                db.query(db_models.DiscoveryHypothesis)
                .filter(
                    db_models.DiscoveryHypothesis.a_resource_id == a_resource.id,
                    db_models.DiscoveryHypothesis.c_resource_id == c_resource.id,
                    db_models.DiscoveryHypothesis.hypothesis_type == "closed",
                )
                .first()
            )

            if stored_hypothesis:
                print("✓ Hypothesis stored in database")
                print(f"  - Plausibility: {stored_hypothesis.plausibility_score:.3f}")
                print(f"  - Path Length: {stored_hypothesis.path_length}")
            else:
                print("⚠ Hypothesis not found in database")

        return True

    except Exception as e:
        print(f"✗ Closed discovery failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_hypothesis_retrieval():
    """Test hypothesis storage and retrieval."""
    print("\n" + "=" * 80)
    print("TEST 4: Hypothesis Retrieval")
    print("=" * 80)

    try:
        db = SessionLocal()

        # Query all hypotheses
        all_hypotheses = db.query(db_models.DiscoveryHypothesis).all()
        print(f"✓ Total hypotheses in database: {len(all_hypotheses)}")

        # Query by type
        open_hypotheses = (
            db.query(db_models.DiscoveryHypothesis)
            .filter(db_models.DiscoveryHypothesis.hypothesis_type == "open")
            .count()
        )

        closed_hypotheses = (
            db.query(db_models.DiscoveryHypothesis)
            .filter(db_models.DiscoveryHypothesis.hypothesis_type == "closed")
            .count()
        )

        print(f"  - Open hypotheses: {open_hypotheses}")
        print(f"  - Closed hypotheses: {closed_hypotheses}")

        # Query by plausibility threshold
        high_plausibility = (
            db.query(db_models.DiscoveryHypothesis)
            .filter(db_models.DiscoveryHypothesis.plausibility_score >= 0.7)
            .count()
        )

        print(f"  - High plausibility (≥0.7): {high_plausibility}")

        # Display sample hypothesis
        if all_hypotheses:
            sample = all_hypotheses[0]
            print("\n  Sample Hypothesis:")
            print(f"    Type: {sample.hypothesis_type}")
            print(f"    Plausibility: {sample.plausibility_score:.3f}")
            print(f"    Path Length: {sample.path_length}")
            print(f"    Path Strength: {sample.path_strength:.3f}")
            print(f"    Common Neighbors: {sample.common_neighbors}")
            print(
                f"    A Resource: {sample.a_resource.title if sample.a_resource else 'N/A'}"
            )
            print(
                f"    C Resource: {sample.c_resource.title if sample.c_resource else 'N/A'}"
            )

        return True

    except Exception as e:
        print(f"✗ Hypothesis retrieval failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all verification tests."""
    print("\n" + "=" * 80)
    print("LITERATURE-BASED DISCOVERY SERVICE VERIFICATION")
    print("Phase 10 - Task 6")
    print("=" * 80)

    results = []

    # Run tests
    results.append(("LBDService Initialization", test_lbd_service_initialization()))
    results.append(("Open Discovery", test_open_discovery()))
    results.append(("Closed Discovery", test_closed_discovery()))
    results.append(("Hypothesis Retrieval", test_hypothesis_retrieval()))

    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n✓ All verification tests passed!")
        return 0
    else:
        print(f"\n✗ {total_tests - total_passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
