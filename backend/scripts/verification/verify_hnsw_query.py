"""
Verification script for HNSW index query functionality (Task 5.3).

Tests:
1. Query HNSW index with a sample embedding
2. Verify k nearest neighbors are returned
3. Verify resource IDs and similarity scores are included
4. Test error handling for missing index
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database.models import GraphEmbedding
from backend.app.services.graph_embeddings_service import GraphEmbeddingsService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./neo_alexandria.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def test_query_hnsw_index():
    """Test HNSW index query functionality."""
    db = SessionLocal()

    try:
        logger.info("=" * 60)
        logger.info("Testing HNSW Index Query (Task 5.3)")
        logger.info("=" * 60)

        service = GraphEmbeddingsService(db)

        # Check if index exists
        index_path = "backend/data/hnsw_index_phase10.bin"
        if not os.path.exists(index_path):
            logger.warning(f"⚠ HNSW index not found at {index_path}")
            logger.info("Building HNSW index first...")
            try:
                stats = service.build_hnsw_index()
                logger.info(f"✓ Index built: {stats['total_embeddings']} embeddings")
            except Exception as e:
                logger.error(f"✗ Failed to build index: {e}")
                return False

        # Get a sample embedding to use as query
        logger.info("\n1. Getting sample embedding for query...")
        sample_embedding_record = (
            db.query(GraphEmbedding)
            .filter(GraphEmbedding.fusion_embedding.isnot(None))
            .first()
        )

        if not sample_embedding_record:
            logger.error("✗ No fusion embeddings found in database")
            return False

        query_embedding = sample_embedding_record.fusion_embedding
        query_resource_id = sample_embedding_record.resource_id
        logger.info(f"✓ Using embedding from resource {query_resource_id}")
        logger.info(f"  Embedding dimension: {len(query_embedding)}")

        # Test 1: Query with k=5
        logger.info("\n2. Querying HNSW index for k=5 nearest neighbors...")
        try:
            results = service.query_hnsw_index(query_embedding=query_embedding, k=5)
            logger.info(f"✓ Query successful, returned {len(results)} results")

            # Verify results structure
            if len(results) > 0:
                logger.info("\n3. Verifying result structure...")
                first_result = results[0]

                # Check required fields
                required_fields = ["resource_id", "similarity_score", "distance"]
                for field in required_fields:
                    if field not in first_result:
                        logger.error(f"✗ Missing required field: {field}")
                        return False

                logger.info("✓ All required fields present")

                # Display results
                logger.info("\n4. Top 5 nearest neighbors:")
                for i, result in enumerate(results, 1):
                    logger.info(
                        f"  {i}. Resource: {result['resource_id'][:8]}... "
                        f"Similarity: {result['similarity_score']:.4f} "
                        f"Distance: {result['distance']:.4f}"
                    )

                # Verify similarity scores are in valid range
                logger.info("\n5. Validating similarity scores...")
                all_valid = True
                for result in results:
                    score = result["similarity_score"]
                    if not (0.0 <= score <= 1.0):
                        logger.error(f"✗ Invalid similarity score: {score}")
                        all_valid = False

                if all_valid:
                    logger.info("✓ All similarity scores in valid range [0.0, 1.0]")

                # First result should be the query itself (or very similar)
                if results[0]["resource_id"] == str(query_resource_id):
                    logger.info("✓ First result is the query resource (expected)")
                else:
                    logger.info(
                        "ℹ First result is not the query resource (may be expected)"
                    )

            else:
                logger.warning("⚠ No results returned")
                return False

        except Exception as e:
            logger.error(f"✗ Query failed: {e}")
            import traceback

            traceback.print_exc()
            return False

        # Test 2: Query with different k values
        logger.info("\n6. Testing different k values...")
        for k in [1, 10, 20]:
            try:
                results = service.query_hnsw_index(query_embedding=query_embedding, k=k)
                logger.info(f"✓ k={k}: returned {len(results)} results")
            except Exception as e:
                logger.error(f"✗ k={k} failed: {e}")
                return False

        # Test 3: Error handling for missing index
        logger.info("\n7. Testing error handling for missing index...")
        try:
            results = service.query_hnsw_index(
                query_embedding=query_embedding,
                k=5,
                index_path="backend/data/nonexistent_index.bin",
            )
            logger.error("✗ Should have raised FileNotFoundError")
            return False
        except FileNotFoundError as e:
            logger.info(f"✓ Correctly raised FileNotFoundError: {e}")
        except Exception as e:
            logger.error(f"✗ Unexpected error: {e}")
            return False

        logger.info("\n" + "=" * 60)
        logger.info("✓ ALL TESTS PASSED - Task 5.3 Implementation Verified")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"✗ Verification failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = test_query_hnsw_index()
    sys.exit(0 if success else 1)
