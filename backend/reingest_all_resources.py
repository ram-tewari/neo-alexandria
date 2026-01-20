"""
Re-ingest all resources to apply improved content extraction.
This will trigger chunking for resources that don't have chunks yet.
"""
import sys
import os
import asyncio
from typing import List

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize database first
from app.shared.database import init_database
from app.config.settings import get_settings

settings = get_settings()
init_database(settings.get_database_url(), settings.ENV)

from app.shared.database import SessionLocal
from app.database.models import Resource
from app.modules.resources.service import process_ingestion
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_resources_needing_chunks():
    """Get all resources that need chunking."""
    db = SessionLocal()
    try:
        # Get resources that:
        # 1. Have a URL (can be re-ingested)
        # 2. Either have no chunks or failed ingestion
        from app.database.models import DocumentChunk
        from sqlalchemy import func, or_
        
        # Subquery to count chunks per resource
        chunk_counts = (
            db.query(
                DocumentChunk.resource_id,
                func.count(DocumentChunk.id).label('chunk_count')
            )
            .group_by(DocumentChunk.resource_id)
            .subquery()
        )
        
        # Get resources with no chunks or failed ingestion
        resources = (
            db.query(Resource)
            .outerjoin(chunk_counts, Resource.id == chunk_counts.c.resource_id)
            .filter(
                Resource.source.isnot(None),  # Has a URL
                or_(
                    chunk_counts.c.chunk_count == None,  # No chunks
                    chunk_counts.c.chunk_count == 0,  # Zero chunks
                    Resource.ingestion_status == 'failed'  # Failed ingestion
                )
            )
            .all()
        )
        
        return resources
    finally:
        db.close()

def reingest_resource(resource_id: str, resource_title: str) -> bool:
    """Re-ingest a single resource."""
    try:
        logger.info(f"[REINGEST] Starting: {resource_title} ({resource_id})")
        
        # Reset ingestion status
        db = SessionLocal()
        try:
            resource = db.query(Resource).filter(Resource.id == resource_id).first()
            if resource:
                resource.ingestion_status = 'pending'
                resource.ingestion_error = None
                db.commit()
        finally:
            db.close()
        
        # Trigger ingestion
        process_ingestion(resource_id)
        
        logger.info(f"[REINGEST] ✅ Completed: {resource_title}")
        return True
        
    except Exception as e:
        logger.error(f"[REINGEST] ❌ Failed: {resource_title} - {e}")
        return False

def main():
    """Re-ingest all resources needing chunks."""
    print("=" * 70)
    print("RE-INGESTION: Applying Improved Content Extraction")
    print("=" * 70)
    
    # Get resources needing chunks
    resources = get_resources_needing_chunks()
    
    if not resources:
        print("\n✅ All resources already have chunks!")
        return
    
    print(f"\n📋 Found {len(resources)} resources needing chunks:")
    for r in resources:
        status = r.ingestion_status or 'unknown'
        print(f"   • {r.title[:60]} - Status: {status}")
    
    print(f"\n⚙️  Starting re-ingestion...")
    print("=" * 70)
    
    success_count = 0
    fail_count = 0
    
    for i, resource in enumerate(resources, 1):
        print(f"\n[{i}/{len(resources)}] Processing: {resource.title[:60]}")
        
        if reingest_resource(str(resource.id), resource.title):
            success_count += 1
        else:
            fail_count += 1
        
        # Small delay to avoid overwhelming the system
        import time
        time.sleep(0.5)
    
    print("\n" + "=" * 70)
    print("RE-INGESTION COMPLETE")
    print("=" * 70)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📊 Total: {len(resources)}")
    
    # Show final stats
    print("\n📊 Checking final chunk statistics...")
    db = SessionLocal()
    try:
        from app.database.models import DocumentChunk
        from sqlalchemy import func
        
        total_resources = db.query(func.count(Resource.id)).scalar()
        resources_with_chunks = (
            db.query(func.count(func.distinct(DocumentChunk.resource_id)))
            .scalar()
        )
        total_chunks = db.query(func.count(DocumentChunk.id)).scalar()
        
        percentage = (resources_with_chunks / total_resources * 100) if total_resources > 0 else 0
        
        print(f"\n📈 Final Statistics:")
        print(f"   Total resources: {total_resources}")
        print(f"   Resources with chunks: {resources_with_chunks} ({percentage:.1f}%)")
        print(f"   Total chunks: {total_chunks}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
