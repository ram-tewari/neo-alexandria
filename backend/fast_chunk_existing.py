"""
Fast chunking for existing resources - SKIP slow AI operations.
Only does: fetch content → extract text → chunk → store
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.shared.database import init_database
from app.config.settings import get_settings

settings = get_settings()
init_database(settings.get_database_url(), settings.ENV)

from app.shared.database import SessionLocal
from app.database.models import Resource, DocumentChunk
from app.utils.content_extractor import fetch_url, extract_from_fetched
from app.modules.resources.service import ChunkingService
from sqlalchemy import func
import logging

logging.basicConfig(level=logging.WARNING)  # Reduce noise
logger = logging.getLogger(__name__)

def fast_chunk_resource(resource_id: str, url: str, title: str) -> tuple[bool, int]:
    """Fast chunking - skip AI operations."""
    try:
        # 1. Fetch content
        fetched = fetch_url(url, timeout=10.0)
        
        # 2. Extract text
        extracted = extract_from_fetched(fetched)
        text = extracted.get('text', '')
        
        if not text or len(text) < 100:
            return False, 0
        
        # 3. Chunk the text
        db = SessionLocal()
        try:
            chunking_service = ChunkingService(db, strategy="semantic")
            chunks = chunking_service.chunk_resource(
                resource_id=resource_id,
                content=text,
                chunk_metadata={"source": "fast_rechunk"}
            )
            db.commit()
            return True, len(chunks)
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed {title}: {e}")
        return False, 0

def main():
    print("=" * 60)
    print("FAST CHUNKING - Existing Resources")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Get resources without chunks that have URLs
        chunk_counts = (
            db.query(
                DocumentChunk.resource_id,
                func.count(DocumentChunk.id).label('chunk_count')
            )
            .group_by(DocumentChunk.resource_id)
            .subquery()
        )
        
        resources = (
            db.query(Resource)
            .outerjoin(chunk_counts, Resource.id == chunk_counts.c.resource_id)
            .filter(
                Resource.source.isnot(None),
                (chunk_counts.c.chunk_count == None) | (chunk_counts.c.chunk_count == 0)
            )
            .all()
        )
        
        if not resources:
            print("\n✅ All resources already have chunks!")
            return
        
        print(f"\n📋 Found {len(resources)} resources without chunks")
        print(f"⚡ Starting FAST chunking (no AI, just chunk)...\n")
        
        success = 0
        failed = 0
        total_chunks = 0
        
        for i, r in enumerate(resources, 1):
            title_short = r.title[:50] if r.title else "Untitled"
            print(f"[{i}/{len(resources)}] {title_short}...", end=" ", flush=True)
            
            ok, chunks = fast_chunk_resource(str(r.id), r.source, r.title)
            
            if ok:
                print(f"✅ {chunks} chunks")
                success += 1
                total_chunks += chunks
            else:
                print(f"❌ failed")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"✅ Success: {success}")
        print(f"❌ Failed: {failed}")
        print(f"📦 Total chunks created: {total_chunks}")
        
        # Final stats
        total_res = db.query(func.count(Resource.id)).scalar()
        res_with_chunks = db.query(func.count(func.distinct(DocumentChunk.resource_id))).scalar()
        all_chunks = db.query(func.count(DocumentChunk.id)).scalar()
        
        pct = (res_with_chunks / total_res * 100) if total_res > 0 else 0
        
        print(f"\n📊 Final: {res_with_chunks}/{total_res} resources ({pct:.1f}%) with {all_chunks} chunks")
        print("=" * 60)
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
