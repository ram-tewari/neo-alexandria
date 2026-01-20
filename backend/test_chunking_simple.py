"""
Simple direct test of chunking functionality
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_chunking():
    print("="*60)
    print("🧪 CHUNKING FUNCTIONALITY TEST")
    print("="*60)
    
    # Test 1: Import and create chunking service
    print("\n📦 Test 1: Import ChunkingService")
    try:
        from app.modules.resources.service import ChunkingService
        print("✅ ChunkingService imported successfully")
    except Exception as e:
        print(f"❌ Failed to import: {e}")
        return False
    
    # Test 2: Check configuration
    print("\n⚙️  Test 2: Check Configuration")
    try:
        from app.config.settings import get_settings
        settings = get_settings()
        
        chunk_enabled = getattr(settings, 'CHUNK_ON_RESOURCE_CREATE', False)
        strategy = getattr(settings, 'CHUNKING_STRATEGY', 'semantic')
        chunk_size = getattr(settings, 'CHUNK_SIZE', 500)
        overlap = getattr(settings, 'CHUNK_OVERLAP', 50)
        
        print(f"   CHUNK_ON_RESOURCE_CREATE: {chunk_enabled}")
        print(f"   CHUNKING_STRATEGY: {strategy}")
        print(f"   CHUNK_SIZE: {chunk_size}")
        print(f"   CHUNK_OVERLAP: {overlap}")
        
        if chunk_enabled:
            print("✅ Chunking is ENABLED")
        else:
            print("⚠️  Chunking is DISABLED (set CHUNK_ON_RESOURCE_CREATE=true)")
            
    except Exception as e:
        print(f"❌ Configuration check failed: {e}")
        return False
    
    # Test 3: Test chunking logic directly
    print("\n🔧 Test 3: Test Chunking Logic")
    try:
        from app.modules.resources.service import ChunkingService
        from app.shared.database import SessionLocal
        
        # Get a database session using SessionLocal directly
        from sqlalchemy.orm import sessionmaker
        from app.shared.database import sync_engine
        
        Session = sessionmaker(bind=sync_engine)
        db = Session()
        
        # Create service
        service = ChunkingService(
            db=db,
            strategy="semantic",
            chunk_size=500,
            overlap=50
        )
        print("✅ ChunkingService created")
        
        # Test content
        test_content = """
        This is a comprehensive test of the chunking system. We need to ensure that the chunking
        service can properly break down long documents into manageable chunks. This is critical
        for the RAG (Retrieval Augmented Generation) system to work effectively.
        
        The chunking system should handle various types of content including technical documentation,
        research papers, and general articles. It needs to respect sentence boundaries and maintain
        context across chunks with appropriate overlap.
        
        Performance is also important. The system should be able to chunk documents quickly without
        blocking the main application thread. Error handling must be robust to prevent failures
        from cascading to other parts of the system.
        
        Testing is essential to verify that all these requirements are met. We need to test both
        the happy path and edge cases to ensure reliability in production environments.
        
        Additional content to make this longer and create multiple chunks. The system needs to
        handle documents of various sizes and complexities. Edge cases include very short documents,
        very long documents, documents with unusual formatting, and documents in different languages.
        
        Quality assurance is critical. We must verify that chunks maintain semantic coherence,
        that overlap works correctly, and that metadata is properly stored. Performance benchmarks
        should show that chunking completes in reasonable time even for large documents.
        """ * 3
        
        print(f"   Content length: {len(test_content)} characters")
        
        # Perform chunking with a valid UUID
        import uuid
        resource_id = str(uuid.uuid4())
        print(f"   Using resource_id: {resource_id}")
        
        chunks = service.chunk_resource(
            resource_id=resource_id,
            content=test_content
        )
        
        print(f"✅ Chunking completed successfully!")
        print(f"   Created {len(chunks)} chunks")
        
        if len(chunks) > 0:
            print(f"\n📄 Chunk Details:")
            for i, chunk in enumerate(chunks[:3]):  # Show first 3
                print(f"   Chunk {i+1}:")
                print(f"      Position: {chunk.position}")
                print(f"      Tokens: {chunk.token_count}")
                print(f"      Content preview: {chunk.content[:100]}...")
            
            if len(chunks) > 3:
                print(f"   ... and {len(chunks) - 3} more chunks")
        
        db.close()
        return len(chunks) > 0
        
    except Exception as e:
        print(f"❌ Chunking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chunking()
    
    print("\n" + "="*60)
    if success:
        print("✅ CHUNKING WORKS!")
        print("="*60)
        sys.exit(0)
    else:
        print("❌ CHUNKING FAILED - Check errors above")
        print("="*60)
        sys.exit(1)
