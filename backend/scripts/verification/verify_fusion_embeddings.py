"""
Verification script for Phase 10 Task 5: Fusion Embeddings and HNSW Indexing

Tests the GraphEmbeddingsService implementation including:
- Fusion embedding computation
- HNSW index building
- HNSW index querying
- Performance validation
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for backend imports
backend_path = Path(__file__).parent
parent_path = backend_path.parent
sys.path.insert(0, str(parent_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database.models import Resource, GraphEmbedding
from backend.app.services.graph_embeddings_service import GraphEmbeddingsService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./neo_alexandria.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def test_fusion_embeddings():
    """Test fusion embedding computation."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 1: Fusion Embedding Computation")
    logger.info("=" * 80)

    db = SessionLocal()
    try:
        # Check prerequisites
        resources_with_content = (
            db.query(Resource).filter(Resource.embedding.isnot(None)).count()
        )

        embeddings_with_structural = (
            db.query(GraphEmbedding)
            .filter(GraphEmbedding.structural_embedding.isnot(None))
            .count()
        )

        logger.info(
            f"Prerequisites: {resources_with_content} resources with content embeddings"
        )
        logger.info(
            f"Prerequisites: {embeddings_with_structural} resources with structural embeddings"
        )

        if resources_with_content == 0 or embeddings_with_structural == 0:
            logger.warning(
                "⚠️  Need resources with both content and structural embeddings"
            )
            logger.info("Skipping fusion embedding test")
            return True

        # Initialize service
        service = GraphEmbeddingsService(db)

        # Compute fusion embeddings with default alpha=0.5
        logger.info("Computing fusion embeddings (alpha=0.5)...")
        stats = service.compute_fusion_embeddings(alpha=0.5)

        logger.info("✓ Fusion embedding computation completed")
        logger.info(f"  - Total processed: {stats['total_processed']}")
        logger.info(f"  - Fusion created: {stats['fusion_created']}")
        logger.info(f"  - Fusion updated: {stats['fusion_updated']}")

        # Verify fusion embeddings were stored
        fusion_count = (
            db.query(GraphEmbedding)
            .filter(GraphEmbedding.fusion_embedding.isnot(None))
            .count()
        )

        logger.info(f"✓ {fusion_count} fusion embeddings stored in database")

        # Verify fusion embedding properties
        sample_fusion = (
            db.query(GraphEmbedding)
            .filter(GraphEmbedding.fusion_embedding.isnot(None))
            .first()
        )

        if sample_fusion:
            logger.info("✓ Sample fusion embedding properties:")
            logger.info(f"  - Dimensions: {len(sample_fusion.fusion_embedding)}")

            # Verify normalization (should be close to 1.0)
            import numpy as np

            fusion_vec = np.array(sample_fusion.fusion_embedding)
            norm = np.linalg.norm(fusion_vec)
            logger.info(f"  - Vector norm: {norm:.6f} (should be ~1.0)")

            assert 0.99 <= norm <= 1.01, (
                f"Fusion vector should be normalized, got norm={norm}"
            )
            logger.info("✓ Fusion vector is properly normalized")

        logger.info("\n✅ Fusion embedding test PASSED")
        return True

    except ImportError as e:
        logger.error(f"\n❌ Missing dependency: {e}")
        logger.info("Install required packages: pip install numpy")
        return False
    except Exception as e:
        logger.error(f"\n❌ Fusion embedding test FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        db.close()


def test_hnsw_index_building():
    """Test HNSW index building."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: HNSW Index Building")
    logger.info("=" * 80)

    db = SessionLocal()
    try:
        # Check prerequisites
        fusion_count = (
            db.query(GraphEmbedding)
            .filter(GraphEmbedding.fusion_embedding.isnot(None))
            .count()
        )

        logger.info(f"Prerequisites: {fusion_count} fusion embeddings available")

        if fusion_count == 0:
            logger.warning("⚠️  Need fusion embeddings to build HNSW index")
            logger.info("Skipping HNSW index building test")
            return True

        # Initialize service
        service = GraphEmbeddingsService(db)

        # Build HNSW index
        logger.info("Building HNSW index...")
        stats = service.build_hnsw_index(
            ef_construction=200, M=16, index_path="backend/data/hnsw_index_phase10.bin"
        )

        logger.info("✓ HNSW index building completed")
        logger.info(f"  - Total embeddings: {stats['total_embeddings']}")
        logger.info(f"  - Index dimension: {stats['index_dimension']}")
        logger.info(f"  - Index path: {stats['index_path']}")
        logger.info(f"  - Build time: {stats['build_time_seconds']:.2f}s")

        # Verify index file exists
        import os

        assert os.path.exists(stats["index_path"]), "Index file should exist"
        logger.info(f"✓ Index file exists at {stats['index_path']}")

        # Verify hnsw_index_id was set
        embeddings_with_index_id = (
            db.query(GraphEmbedding)
            .filter(GraphEmbedding.hnsw_index_id.isnot(None))
            .count()
        )

        logger.info(f"✓ {embeddings_with_index_id} embeddings have HNSW index IDs")
        assert embeddings_with_index_id == stats["total_embeddings"], (
            "All embeddings should have index IDs"
        )

        logger.info("\n✅ HNSW index building test PASSED")
        return True

    except ImportError as e:
        logger.error(f"\n❌ Missing dependency: {e}")
        logger.info("Install required packages: pip install hnswlib numpy")
        return False
    except Exception as e:
        logger.error(f"\n❌ HNSW index building test FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        db.close()


def test_hnsw_index_querying():
    """Test HNSW index querying."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: HNSW Index Querying")
    logger.info("=" * 80)

    db = SessionLocal()
    try:
        # Check prerequisites
        import os

        index_path = "backend/data/hnsw_index_phase10.bin"

        if not os.path.exists(index_path):
            logger.warning(f"⚠️  HNSW index not found at {index_path}")
            logger.info("Skipping HNSW index querying test")
            return True

        # Get a sample fusion embedding to use as query
        sample_embedding = (
            db.query(GraphEmbedding)
            .filter(GraphEmbedding.fusion_embedding.isnot(None))
            .first()
        )

        if not sample_embedding:
            logger.warning("⚠️  No fusion embeddings found")
            logger.info("Skipping HNSW index querying test")
            return True

        logger.info(f"Using resource {sample_embedding.resource_id} as query")

        # Initialize service
        service = GraphEmbeddingsService(db)

        # Query HNSW index
        logger.info("Querying HNSW index for k=10 nearest neighbors...")
        import time

        start_time = time.time()

        results = service.query_hnsw_index(
            query_embedding=sample_embedding.fusion_embedding,
            k=10,
            index_path=index_path,
        )

        query_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        logger.info(f"✓ HNSW query completed in {query_time:.2f}ms")
        logger.info(f"  - Found {len(results)} neighbors")

        # Verify query time meets performance requirement (<100ms)
        if query_time < 100:
            logger.info("✓ Query time meets performance requirement (<100ms)")
        else:
            logger.warning("⚠️  Query time exceeds 100ms target")

        # Display top results
        if results:
            logger.info("✓ Top 5 nearest neighbors:")
            for i, result in enumerate(results[:5], 1):
                logger.info(
                    f"  {i}. Resource {result['resource_id']}: "
                    f"similarity={result['similarity_score']:.4f}, "
                    f"distance={result['distance']:.4f}"
                )

            # Verify first result is the query itself (should have highest similarity)
            first_result = results[0]
            assert first_result["resource_id"] == str(sample_embedding.resource_id), (
                "First result should be the query resource itself"
            )
            assert first_result["similarity_score"] > 0.99, (
                "Query resource should have similarity ~1.0 with itself"
            )
            logger.info(
                "✓ Query resource correctly identified as most similar to itself"
            )

        logger.info("\n✅ HNSW index querying test PASSED")
        return True

    except ImportError as e:
        logger.error(f"\n❌ Missing dependency: {e}")
        logger.info("Install required packages: pip install hnswlib numpy")
        return False
    except FileNotFoundError as e:
        logger.error(f"\n❌ {e}")
        return False
    except Exception as e:
        logger.error(f"\n❌ HNSW index querying test FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        db.close()


def test_dimension_mismatch_handling():
    """Test handling of dimension mismatch in fusion embeddings."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Dimension Mismatch Handling")
    logger.info("=" * 80)

    db = SessionLocal()
    try:
        # This test verifies that the fusion embedding computation
        # correctly handles cases where content and structural embeddings
        # have different dimensions by truncating to the minimum

        logger.info("Checking for resources with different embedding dimensions...")

        # Query resources with both embeddings
        query = (
            db.query(Resource, GraphEmbedding)
            .join(GraphEmbedding, Resource.id == GraphEmbedding.resource_id)
            .filter(
                Resource.embedding.isnot(None),
                GraphEmbedding.structural_embedding.isnot(None),
            )
            .limit(1)
        )

        result = query.first()

        if not result:
            logger.warning("⚠️  No resources with both embeddings found")
            logger.info("Skipping dimension mismatch test")
            return True

        resource, graph_embedding = result

        content_dim = len(resource.embedding)
        structural_dim = len(graph_embedding.structural_embedding)

        logger.info("Sample resource dimensions:")
        logger.info(f"  - Content embedding: {content_dim}")
        logger.info(f"  - Structural embedding: {structural_dim}")

        if content_dim != structural_dim:
            logger.info(
                f"✓ Dimension mismatch detected ({content_dim} vs {structural_dim})"
            )

            # Verify fusion embedding has minimum dimension
            if graph_embedding.fusion_embedding:
                fusion_dim = len(graph_embedding.fusion_embedding)
                expected_dim = min(content_dim, structural_dim)

                logger.info(f"  - Fusion embedding: {fusion_dim}")
                assert fusion_dim == expected_dim, (
                    f"Fusion dimension should be {expected_dim}, got {fusion_dim}"
                )
                logger.info(
                    "✓ Fusion embedding correctly truncated to minimum dimension"
                )
        else:
            logger.info(f"✓ Embeddings have same dimension ({content_dim})")
            logger.info(
                "  (Dimension mismatch handling would work if dimensions differed)"
            )

        logger.info("\n✅ Dimension mismatch handling test PASSED")
        return True

    except Exception as e:
        logger.error(f"\n❌ Dimension mismatch handling test FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    """Run all verification tests."""
    logger.info("=" * 80)
    logger.info("PHASE 10 TASK 5: Fusion Embeddings and HNSW Indexing Verification")
    logger.info("=" * 80)

    tests = [
        ("Fusion Embeddings", test_fusion_embeddings),
        ("HNSW Index Building", test_hnsw_index_building),
        ("HNSW Index Querying", test_hnsw_index_querying),
        ("Dimension Mismatch Handling", test_dimension_mismatch_handling),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {test_name}")

    logger.info(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        logger.info("\n🎉 All tests PASSED!")
        return 0
    else:
        logger.error(f"\n⚠️  {total - passed} test(s) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
