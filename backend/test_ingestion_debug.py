"""
Debug script to test resource ingestion
"""
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.shared.database import init_database
from app.modules.resources.service import create_pending_resource, process_ingestion

def test_ingestion():
    """Test resource creation and ingestion"""
    
    # Initialize database
    print("=== Initializing database ===")
    init_database()
    
    # Import SessionLocal after init
    from app.shared.database import SessionLocal
    
    # Create session
    db = SessionLocal()
    
    try:
        # Create pending resource
        print("\n=== Creating pending resource ===")
        payload = {
            "url": "https://www.postman.com/api-platform/api-documentation/",
            "title": "Postman API Documentation"
        }
        
        resource = create_pending_resource(db, payload)
        print(f"Resource created: {resource.id}")
        print(f"Status: {resource.ingestion_status}")
        print(f"Title: {resource.title}")
        print(f"Source: {resource.source}")
        
        # Run ingestion synchronously
        print("\n=== Starting ingestion ===")
        process_ingestion(
            str(resource.id),
            archive_root=None,
            ai=None,
            engine_url=None
        )
        
        print("\n=== Ingestion completed ===")
        
        # Check final status
        db.refresh(resource)
        print(f"Final status: {resource.ingestion_status}")
        print(f"Final title: {resource.title}")
        print(f"Description: {resource.description[:100] if resource.description else 'None'}...")
        print(f"Quality score: {resource.quality_score}")
        
    except Exception as e:
        print(f"\n=== ERROR ===")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_ingestion()
