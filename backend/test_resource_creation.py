#!/usr/bin/env python3
"""Quick test to debug resource creation issue"""

import sys
from sqlalchemy.orm import Session
from app.shared.database import init_database, SessionLocal
from app.modules.resources.service import create_pending_resource

def test_create_resource():
    """Test creating a resource directly"""
    # Initialize database
    init_database()
    
    # Import SessionLocal after init
    from app.shared.database import SessionLocal as SL
    
    # Create session
    db: Session = SL()
    
    try:
        # Test payload
        payload = {
            "url": "https://www.postman.com/api-platform/api-documentation/",
            "title": "Test Resource"
        }
        
        print(f"Creating resource with payload: {payload}")
        resource = create_pending_resource(db, payload)
        print(f"✓ Resource created successfully: {resource.id}")
        print(f"  Title: {resource.title}")
        print(f"  Source: {resource.source}")
        print(f"  Status: {resource.ingestion_status}")
        
    except Exception as e:
        print(f"✗ Error creating resource: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    test_create_resource()
