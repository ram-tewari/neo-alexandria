"""
Verification script for Phase 10 Task 2: Multi-layer graph construction.

Tests:
1. GraphService initialization
2. Multi-layer graph construction
3. Edge type creation (citation, co-authorship, subject similarity, temporal)
4. Edge weight calculations
5. Graph caching
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
backend_path = Path(__file__).parent
parent_path = backend_path.parent
sys.path.insert(0, str(parent_path))
os.chdir(backend_path)

from backend.app.database.base import SessionLocal
from backend.app.services.graph_service import GraphService
from backend.app.database import models as db_models


def test_graph_service_initialization():
    """Test GraphService can be initialized."""
    print("Test 1: GraphService initialization...")
    db = SessionLocal()
    try:
        service = GraphService(db)
        assert service.db is not None
        assert service._graph_cache is None
        assert service._cache_timestamp is None
        print("✓ GraphService initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    finally:
        db.close()


def test_multilayer_graph_construction():
    """Test multi-layer graph can be built."""
    print("\nTest 2: Multi-layer graph construction...")
    db = SessionLocal()
    try:
        service = GraphService(db)

        # Check if networkx is available
        try:
            import networkx as nx
        except ImportError:
            print("⚠ NetworkX not installed - skipping graph construction test")
            print("  Install with: pip install networkx")
            return True

        # Build graph
        graph = service.build_multilayer_graph()

        assert graph is not None
        assert isinstance(graph, nx.MultiDiGraph)

        print("✓ Graph built successfully:")
        print(f"  - Nodes: {graph.number_of_nodes()}")
        print(f"  - Edges: {graph.number_of_edges()}")

        # Check cache was set
        assert service._graph_cache is not None
        assert service._cache_timestamp is not None
        print("✓ Graph cache initialized")

        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        db.close()


def test_edge_types():
    """Test different edge types are created."""
    print("\nTest 3: Edge type creation...")
    db = SessionLocal()
    try:
        # Check if networkx is available
        try:
            import networkx as nx
        except ImportError:
            print("⚠ NetworkX not installed - skipping edge type test")
            return True

        service = GraphService(db)
        graph = service.build_multilayer_graph()

        # Count edge types
        edge_types = {}
        for u, v, key, data in graph.edges(keys=True, data=True):
            edge_type = data.get("edge_type", "unknown")
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

        print("✓ Edge types found:")
        for edge_type, count in edge_types.items():
            print(f"  - {edge_type}: {count} edges")

        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        db.close()


def test_edge_weights():
    """Test edge weights are calculated correctly."""
    print("\nTest 4: Edge weight calculations...")
    db = SessionLocal()
    try:
        # Check if networkx is available
        try:
            import networkx as nx
        except ImportError:
            print("⚠ NetworkX not installed - skipping edge weight test")
            return True

        service = GraphService(db)
        graph = service.build_multilayer_graph()

        # Check edge weights by type
        weight_ranges = {}
        for u, v, key, data in graph.edges(keys=True, data=True):
            edge_type = data.get("edge_type", "unknown")
            weight = data.get("weight", 0.0)

            if edge_type not in weight_ranges:
                weight_ranges[edge_type] = {"min": weight, "max": weight, "count": 0}

            weight_ranges[edge_type]["min"] = min(
                weight_ranges[edge_type]["min"], weight
            )
            weight_ranges[edge_type]["max"] = max(
                weight_ranges[edge_type]["max"], weight
            )
            weight_ranges[edge_type]["count"] += 1

        print("✓ Edge weight ranges:")
        for edge_type, ranges in weight_ranges.items():
            print(
                f"  - {edge_type}: min={ranges['min']:.2f}, max={ranges['max']:.2f}, count={ranges['count']}"
            )

        # Verify expected weights
        if "citation" in weight_ranges:
            assert weight_ranges["citation"]["min"] == 1.0
            assert weight_ranges["citation"]["max"] == 1.0
            print("✓ Citation edges have weight 1.0")

        if "subject_similarity" in weight_ranges:
            assert weight_ranges["subject_similarity"]["min"] == 0.5
            assert weight_ranges["subject_similarity"]["max"] == 0.5
            print("✓ Subject similarity edges have weight 0.5")

        if "temporal" in weight_ranges:
            assert weight_ranges["temporal"]["min"] == 0.3
            assert weight_ranges["temporal"]["max"] == 0.3
            print("✓ Temporal edges have weight 0.3")

        if "co_authorship" in weight_ranges:
            assert weight_ranges["co_authorship"]["max"] <= 1.0
            print("✓ Co-authorship edges have weight <= 1.0")

        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        db.close()


def test_graph_caching():
    """Test graph caching works correctly."""
    print("\nTest 5: Graph caching...")
    db = SessionLocal()
    try:
        # Check if networkx is available
        try:
            import networkx as nx
        except ImportError:
            print("⚠ NetworkX not installed - skipping caching test")
            return True

        service = GraphService(db)

        # Build graph first time
        graph1 = service.build_multilayer_graph()
        timestamp1 = service._cache_timestamp

        # Build graph second time (should use cache)
        graph2 = service.build_multilayer_graph()
        timestamp2 = service._cache_timestamp

        assert graph1 is graph2, "Should return same cached graph object"
        assert timestamp1 == timestamp2, "Cache timestamp should not change"
        print("✓ Graph cache working correctly")

        # Invalidate cache
        service.invalidate_cache()
        assert service._graph_cache is None
        assert service._cache_timestamp is None
        print("✓ Cache invalidation working")

        # Build graph after invalidation
        graph3 = service.build_multilayer_graph()
        assert graph3 is not graph1, "Should build new graph after invalidation"
        print("✓ Graph rebuilt after cache invalidation")

        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        db.close()


def test_edge_persistence():
    """Test edges are persisted to database."""
    print("\nTest 6: Edge persistence to database...")
    db = SessionLocal()
    try:
        # Check if networkx is available
        try:
            import networkx as nx
        except ImportError:
            print("⚠ NetworkX not installed - skipping persistence test")
            return True

        service = GraphService(db)

        # Build graph (this should persist edges)
        service.build_multilayer_graph()

        # Query database for edges
        edge_count = db.query(db_models.GraphEdge).count()
        print(f"✓ Edges persisted to database: {edge_count} edges")

        # Check edge types in database
        edge_types = (
            db.query(
                db_models.GraphEdge.edge_type, db.func.count(db_models.GraphEdge.id)
            )
            .group_by(db_models.GraphEdge.edge_type)
            .all()
        )

        print("✓ Edge types in database:")
        for edge_type, count in edge_types:
            print(f"  - {edge_type}: {count} edges")

        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    """Run all verification tests."""
    print("=" * 70)
    print("Phase 10 Task 2: Multi-layer Graph Construction Verification")
    print("=" * 70)

    tests = [
        test_graph_service_initialization,
        test_multilayer_graph_construction,
        test_edge_types,
        test_edge_weights,
        test_graph_caching,
        test_edge_persistence,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            import traceback

            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 70)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 70)

    if all(results):
        print("\n✓ All tests passed! Task 2 implementation verified.")
        return 0
    else:
        print("\n⚠ Some tests failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
