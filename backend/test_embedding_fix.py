#!/usr/bin/env python3
"""
Quick test to verify embedding column fix
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database.models import Resource
from app.shared.database import Base
import uuid
from datetime import datetime, timezone

def test_embedding_fix():
    """Test that we can create a resource with embedding=None"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL", "postgresql://neo_alexandria:neo_alexandria@localhost:5432/neo_alexandria")
    
    # Create engine and session
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Force metadata refresh
    Base.metadata.drop_all(bind=engine, tables=[Resource.__table__])
    Base.metadata.create_all(bind=engine, tables=[Resource.__table__])
    
    session = SessionLocal()
    
    try:
        # Test creating a resource
        resource = Resource(
            title="Test Resource",
            source="https://example.com/test",
            embedding=None,  # This should work now
        )
        
        session.add(resource)
        session.commit()
        
        print(f"✅ SUCCESS: Created resource {resource.id} with embedding=None")
        
        # Verify it was saved correctly
        saved_resource = session.query(Resource).filter(Resource.id == resource.id).first()
        print(f"✅ VERIFIED: Retrieved resource with embedding={saved_resource.embedding}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        session.rollback()
        return False
        
    finally:
        session.close()

if __name__ == "__main__":
    success = test_embedding_fix()
    sys.exit(0 if success else 1)