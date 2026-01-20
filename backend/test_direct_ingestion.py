"""
Test ingestion by calling process_ingestion directly (synchronously).
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize database first
from app.shared.database import init_database
from app.config.settings import get_settings

settings = get_settings()
init_database(settings.get_database_url(), settings.ENV)

from app.shared.database import SessionLocal
from app.modules.resources.service import create_pending_resource, process_ingestion
import time

def test_direct_ingestion():
    """Test ingestion by calling it directly."""
    print("=" * 60)
    print("DIRECT INGESTION TEST")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Create a resource
        print("\n📝 Creating resource...")
        payload = {
            "url": "https://www.postman.com/api-platform/api-documentation/",
            "title": "Postman API Documentation Test",
            "description": "Testing chunking with real content from Postman's API documentation page."
        }
        
        resource = create_pending_resource(db, payload)
        resource_id = str(resource.id)
        print(f"✅ Resource created: {resource_id}")
        print(f"   Status: {resource.ingestion_status}")
        
        # Run ingestion synchronously
        print(f"\n⚙️  Running ingestion...")
        process_ingestion(resource_id)
        
        # Check result
        print(f"\n🔍 Checking result...")
        db.refresh(resource)
        print(f"   Ingestion status: {resource.ingestion_status}")
        
        if resource.ingestion_status == "completed":
            print("✅ Ingestion completed!")
            
            # Check for chunks
            from app.database.models import DocumentChunk
            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.resource_id == resource.id
            ).all()
            
            print(f"\n📦 Chunks created: {len(chunks)}")
            if chunks:
                for chunk in chunks[:3]:  # Show first 3
                    print(f"   • Chunk {chunk.chunk_index}: {len(chunk.content)} chars")
                
                print("\n" + "=" * 60)
                print("✅ TEST PASSED: Chunking works!")
                print("=" * 60)
                return True
            else:
                print("\n❌ No chunks created (check logs)")
                return False
        else:
            print(f"❌ Ingestion failed: {resource.ingestion_error}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_direct_ingestion()
    sys.exit(0 if success else 1)
