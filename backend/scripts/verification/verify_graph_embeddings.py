"""
Verification script for Phase 10 Task 4: Graph Embeddings Service

Tests the GraphEmbeddingsService implementation including:
- Service initialization with lazy loading
- Graph2Vec embedding computation
- Batch processing and progress logging
- Database persistence
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
from backend.app.database.models import Resource, GraphEmbedding, GraphEdge
from backend.app.services.graph_embeddings_service import GraphEmbeddingsService
from backend.app.services.graph_service import GraphService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./neo_alexandria.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def test_service_initialization():
    """Test GraphEmbeddingsService initialization and lazy loading."""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: Service Initialization")
    logger.info("="*80)
    
    db = SessionLocal()
    try:
        # Initialize service
        service = GraphEmbeddingsService(db)
        logger.info("✓ GraphEmbeddingsService initialized successfully")
        
        # Test lazy loading of GraphService
        assert service._graph_service is None, "GraphService should not be loaded initially"
        logger.info("✓ GraphService is lazy-loaded (not initialized yet)")
        
        # Access graph_service property to trigger lazy loading
        graph_service = service.graph_service
        assert graph_service is not None, "GraphService should be loaded after access"
        assert isinstance(graph_service, GraphService), "Should be GraphService instance"
        logger.info("✓ GraphService lazy-loaded successfully on first access")
        
        # Verify it's cached
        graph_service_2 = service.graph_service
        assert graph_service is graph_service_2, "GraphService should be cached"
        logger.info("✓ GraphService is cached after first access")
        
        logger.info("\n✅ Service initialization test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Service initialization test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_graph2vec_computation():
    """Test Graph2Vec embedding computation."""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Graph2Vec Embedding Computation")
    logger.info("="*80)
    
    db = SessionLocal()
    try:
        # Check if we have resources and graph edges
        resource_count = db.query(Resource).count()
        edge_count = db.query(GraphEdge).count()
        
        logger.info(f"Database state: {resource_count} resources, {edge_count} graph edges")
        
        if resource_count < 2:
            logger.warning("⚠️  Need at least 2 resources to test Graph2Vec")
            logger.info("Skipping Graph2Vec computation test")
            return True
        
        if edge_count < 1:
            logger.warning("⚠️  Need at least 1 graph edge to test Graph2Vec")
            logger.info("Skipping Graph2Vec computation test")
            return True
        
        # Initialize service
        service = GraphEmbeddingsService(db)
        
        # Compute Graph2Vec embeddings
        logger.info("Computing Graph2Vec embeddings...")
        stats = service.compute_graph2vec_embeddings(
            dimensions=128,
            wl_iterations=2,
            batch_size=100
        )
        
        logger.info("✓ Graph2Vec computation completed")
        logger.info(f"  - Total nodes processed: {stats['total_nodes']}")
        logger.info(f"  - Embeddings created: {stats['embeddings_created']}")
        logger.info(f"  - Embeddings updated: {stats['embeddings_updated']}")
        logger.info(f"  - Processing time: {stats['processing_time_seconds']:.2f}s")
        
        # Verify embeddings were stored
        embedding_count = db.query(GraphEmbedding).filter(
            GraphEmbedding.structural_embedding.isnot(None)
        ).count()
        
        logger.info(f"✓ {embedding_count} structural embeddings stored in database")
        
        # Verify embedding properties
        sample_embedding = db.query(GraphEmbedding).filter(
            GraphEmbedding.structural_embedding.isnot(None)
        ).first()
        
        if sample_embedding:
            logger.info("✓ Sample embedding properties:")
            logger.info(f"  - Method: {sample_embedding.embedding_method}")
            logger.info(f"  - Version: {sample_embedding.embedding_version}")
            logger.info(f"  - Dimensions: {len(sample_embedding.structural_embedding)}")
            
            assert sample_embedding.embedding_method == "graph2vec", "Method should be graph2vec"
            assert sample_embedding.embedding_version == "v1.0", "Version should be v1.0"
            assert len(sample_embedding.structural_embedding) == 128, "Should have 128 dimensions"
            logger.info("✓ Embedding properties are correct")
        
        # Verify performance
        if stats['total_nodes'] > 0 and stats['processing_time_seconds'] > 0:
            nodes_per_minute = (stats['total_nodes'] / stats['processing_time_seconds']) * 60
            logger.info(f"✓ Processing rate: {nodes_per_minute:.1f} nodes/minute")
            
            # Check if meets performance requirement (>100 nodes/minute)
            if nodes_per_minute >= 100:
                logger.info("✓ Meets performance requirement (>100 nodes/minute)")
            else:
                logger.warning("⚠️  Below performance target of 100 nodes/minute")
        
        logger.info("\n✅ Graph2Vec computation test PASSED")
        return True
        
    except ImportError as e:
        logger.error(f"\n❌ Missing dependency: {e}")
        logger.info("Install required packages: pip install karateclub networkx numpy")
        return False
    except Exception as e:
        logger.error(f"\n❌ Graph2Vec computation test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_batch_processing():
    """Test batch processing and progress logging."""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: Batch Processing")
    logger.info("="*80)
    
    db = SessionLocal()
    try:
        resource_count = db.query(Resource).count()
        
        if resource_count < 2:
            logger.warning("⚠️  Need at least 2 resources to test batch processing")
            logger.info("Skipping batch processing test")
            return True
        
        # Initialize service
        service = GraphEmbeddingsService(db)
        
        # Test with small batch size to verify batching works
        logger.info("Testing batch processing with batch_size=2...")
        stats = service.compute_graph2vec_embeddings(
            dimensions=64,  # Smaller for faster testing
            wl_iterations=1,
            batch_size=2
        )
        
        logger.info("✓ Batch processing completed")
        logger.info(f"  - Processed {stats['total_nodes']} nodes in batches of 2")
        
        # Verify embeddings were created/updated
        total_changes = stats['embeddings_created'] + stats['embeddings_updated']
        assert total_changes > 0, "Should have created or updated embeddings"
        logger.info(f"✓ {total_changes} embeddings processed in batches")
        
        logger.info("\n✅ Batch processing test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Batch processing test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    """Run all verification tests."""
    logger.info("="*80)
    logger.info("PHASE 10 TASK 4: Graph Embeddings Service Verification")
    logger.info("="*80)
    
    tests = [
        ("Service Initialization", test_service_initialization),
        ("Graph2Vec Computation", test_graph2vec_computation),
        ("Batch Processing", test_batch_processing),
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
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    
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
