"""
Simple Search Test - Verify search infrastructure works

This script does a basic sanity check:
1. Connects to database
2. Counts resources and annotations
3. Tries a simple search
4. Reports results
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Resource, Annotation
from app.modules.search.service import SearchService
from app.domain.search import SearchQuery

def main():
    print("=" * 60)
    print("SIMPLE SEARCH TEST")
    print("=" * 60)
    
    # Connect to database
    engine = create_engine("sqlite:///./backend.db")
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Count data
        resource_count = db.query(Resource).count()
        annotation_count = db.query(Annotation).count()
        
        print(f"\n✓ Database connected")
        print(f"  Resources: {resource_count}")
        print(f"  Annotations: {annotation_count}")
        
        if resource_count == 0:
            print("\n❌ No resources found!")
            print("Run: python scripts/seed_audit_data_simple.py")
            return
        
        # Try a simple search
        print(f"\n{'=' * 60}")
        print("TESTING BASIC SEARCH")
        print(f"{'=' * 60}")
        
        search_service = SearchService(db)
        query = SearchQuery(
            query_text="python",
            limit=5,
            search_method="fts5"
        )
        
        print(f"Query: '{query.query_text}'")
        
        try:
            resources, total, _, _ = search_service.search(query)
            print(f"\n✓ Search executed successfully")
            print(f"  Results: {len(resources)}")
            print(f"  Total: {total}")
            
            if len(resources) > 0:
                print(f"\n  Top result:")
                print(f"    Title: {resources[0].title}")
                print(f"    ID: {resources[0].id}")
            else:
                print(f"\n  ⚠️  No results (expected for unindexed DB)")
                
        except Exception as e:
            print(f"\n❌ Search failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return
        
        # Try hybrid search
        print(f"\n{'=' * 60}")
        print("TESTING HYBRID SEARCH")
        print(f"{'=' * 60}")
        
        query2 = SearchQuery(
            query_text="async programming",
            limit=5,
            search_method="hybrid"
        )
        
        print(f"Query: '{query2.query_text}'")
        
        try:
            resources2, total2, _, _ = search_service.hybrid_search(query2, hybrid_weight=0.5)
            print(f"\n✓ Hybrid search executed successfully")
            print(f"  Results: {len(resources2)}")
            print(f"  Total: {total2}")
            
            if len(resources2) > 0:
                print(f"\n  Top result:")
                print(f"    Title: {resources2[0].title}")
                print(f"    ID: {resources2[0].id}")
            else:
                print(f"\n  ⚠️  No results (expected for unindexed DB)")
                
        except Exception as e:
            print(f"\n❌ Hybrid search failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return
        
        print(f"\n{'=' * 60}")
        print("✅ ALL TESTS PASSED")
        print(f"{'=' * 60}")
        print("\nSearch infrastructure is working!")
        print("Zero results are expected for an unindexed database.")
        print("The important thing is that searches execute without errors.")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
