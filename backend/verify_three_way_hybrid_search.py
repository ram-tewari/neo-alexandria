"""
Verification script for three-way hybrid search implementation.

This script verifies that the search_three_way_hybrid method is properly
implemented and can be called successfully.
"""

import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, '.')

from backend.app.database.models import Resource, Base
from backend.app.services.search_service import AdvancedSearchService
from backend.app.schemas.search import SearchQuery, SearchFilters

def verify_three_way_hybrid_search():
    """Verify three-way hybrid search implementation."""
    
    print("=" * 80)
    print("Three-Way Hybrid Search Verification")
    print("=" * 80)
    
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Test 1: Verify method exists
        print("\n1. Checking if search_three_way_hybrid method exists...")
        assert hasattr(AdvancedSearchService, 'search_three_way_hybrid')
        print("   ✓ Method exists")
        
        # Test 2: Verify helper methods exist
        print("\n2. Checking helper methods...")
        assert hasattr(AdvancedSearchService, '_analyze_query')
        print("   ✓ _analyze_query exists")
        assert hasattr(AdvancedSearchService, '_search_sparse')
        print("   ✓ _search_sparse exists")
        assert hasattr(AdvancedSearchService, '_fetch_resources_ordered')
        print("   ✓ _fetch_resources_ordered exists")
        
        # Test 3: Test query analysis
        print("\n3. Testing query analysis...")
        
        # Short query
        analysis = AdvancedSearchService._analyze_query("machine learning")
        assert analysis['word_count'] == 2
        assert analysis['is_short'] == True
        assert analysis['is_long'] == False
        print("   ✓ Short query detection works")
        
        # Long query
        analysis = AdvancedSearchService._analyze_query("How does gradient descent work in deep neural networks for image classification")
        assert analysis['word_count'] == 12
        assert analysis['is_short'] == False
        assert analysis['is_long'] == True
        print("   ✓ Long query detection works")
        
        # Question query
        analysis = AdvancedSearchService._analyze_query("What is machine learning?")
        assert analysis['is_question'] == True
        print("   ✓ Question query detection works")
        
        # Technical query (code)
        analysis = AdvancedSearchService._analyze_query("def fibonacci(n): return n")
        assert analysis['is_technical'] == True
        print("   ✓ Technical query detection works (code)")
        
        # Technical query (math)
        analysis = AdvancedSearchService._analyze_query("solve equation x^2 + 5x + 6 = 0")
        assert analysis['is_technical'] == True
        print("   ✓ Technical query detection works (math)")
        
        # Test 4: Test search_three_way_hybrid with empty database
        print("\n4. Testing search_three_way_hybrid with empty database...")
        query = SearchQuery(
            text="test query",
            filters=SearchFilters(),
            limit=20,
            offset=0
        )
        
        results = AdvancedSearchService.search_three_way_hybrid(
            db,
            query,
            enable_reranking=False,
            adaptive_weighting=True
        )
        
        # Should return 5-tuple
        assert len(results) == 5
        resources, total, facets, snippets, metadata = results
        
        assert isinstance(resources, list)
        assert isinstance(total, int)
        assert isinstance(snippets, dict)
        assert isinstance(metadata, dict)
        print("   ✓ Method returns correct structure")
        
        # Check metadata structure
        assert 'latency_ms' in metadata
        assert 'method_contributions' in metadata
        assert 'weights_used' in metadata
        print("   ✓ Metadata contains required fields")
        
        # Check method contributions
        contributions = metadata['method_contributions']
        assert 'fts5' in contributions
        assert 'dense' in contributions
        assert 'sparse' in contributions
        print("   ✓ Method contributions tracked")
        
        # Check weights
        weights = metadata['weights_used']
        assert len(weights) == 3
        assert all(isinstance(w, float) for w in weights)
        print("   ✓ Weights are properly formatted")
        
        # Test 5: Test _fetch_resources_ordered
        print("\n5. Testing _fetch_resources_ordered...")
        ordered = AdvancedSearchService._fetch_resources_ordered(db, [])
        assert ordered == []
        print("   ✓ Empty list handling works")
        
        # Test 6: Test _search_sparse
        print("\n6. Testing _search_sparse...")
        sparse_results = AdvancedSearchService._search_sparse(db, "test query", limit=10)
        assert isinstance(sparse_results, list)
        print("   ✓ Sparse search returns list")
        
        print("\n" + "=" * 80)
        print("✓ All verification tests passed!")
        print("=" * 80)
        
        return True
        
    except AssertionError as e:
        print(f"\n✗ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    success = verify_three_way_hybrid_search()
    sys.exit(0 if success else 1)
