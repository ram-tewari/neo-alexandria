"""
Comprehensive test to verify chunking actually works
Tests the complete chunking pipeline
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_chunking_service_directly():
    """Test 1: ChunkingService works directly"""
    print("\n" + "="*60)
    print("🔍 Test 1: ChunkingService Direct Test")
    print("="*60)
    
    try:
        from app.modules.resources.service import ChunkingService
        from app.shared.database import SessionLocal
        
        db = SessionLocal()
        
        # Create chunking service
        service = ChunkingService(
            db=db,
            strategy="semantic",
            chunk_size=500,
            overlap=50
        )
        
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
        """ * 3  # Repeat to make it longer
        
        print(f"📝 Test content length: {len(test_content)} characters")
        
        # Perform chunking
        resource_id = "test-resource-123"
        chunks = service.chunk_resource(
            resource_id=resource_id,
            content=test_content
        )
        
        print(f"✅ Chunking succeeded!")
        print(f"   Created {len(chunks)} chunks")
        
        if len(chunks) > 0:
            print(f"   First chunk preview: {chunks[0].content[:100]}...")
            print(f"   Chunk metadata: position={chunks[0].position}, tokens={chunks[0].token_count}")
            
        db.close()
        return len(chunks) > 0
        
    except Exception as e:
        print(f"❌ Chunking failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_resource_creation_with_chunking():
    """Test 2: Resource creation triggers chunking"""
    print("\n" + "="*60)
    print("🔍 Test 2: Resource Creation with Chunking")
    print("="*60)
    
    try:
        from app.modules.resources.service import create_pending_resource
        from app.shared.database import SessionLocal
        from app.database.models import DocumentChunk
        from sqlalchemy import select
        
        db = SessionLocal()
        
        # Create resource with substantial content
        test_content = """
        This is a test resource with enough content to trigger chunking. The content needs to be
        substantial enough to create multiple chunks. We're testing the complete pipeline from
        resource creation through to chunk storage in the database.
        
        The system should automatically detect that this resource has enough content and trigger
        the chunking process. The chunks should then be stored in the document_chunks table with
        proper metadata including position, token count, and parent-child relationships.
        
        This test verifies that the event-driven architecture works correctly, with the resource
        creation event triggering the chunking handler, which then processes the content and
        stores the results.
        """ * 5  # Make it longer
        
        payload = {
            "url": f"https://example.com/chunking-test-{int(time.time())}",
            "title": "Chunking Test Resource",
            "description": test_content
        }
        
        print(f"📝 Creating resource with {len(test_content)} character description...")
        
        resource = create_pending_resource(db, payload)
        resource_id = str(resource.id)
        
        print(f"✅ Resource created: {resource_id}")
        print(f"   Title: {resource.title}")
        
        # Wait a moment for async chunking to complete
        print("⏳ Waiting 2 seconds for chunking to complete...")
        time.sleep(2)
        
        # Check if chunks were created
        result = db.execute(
            select(DocumentChunk).filter(DocumentChunk.resource_id == resource_id)
        )
        chunks = result.scalars().all()
        
        print(f"\n📊 Chunking Results:")
        print(f"   Chunks found: {len(chunks)}")
        
        if len(chunks) > 0:
            print(f"   ✅ Chunking worked!")
            for i, chunk in enumerate(chunks[:3]):  # Show first 3
                print(f"   Chunk {i+1}: position={chunk.position}, tokens={chunk.token_count}")
                print(f"            preview: {chunk.content[:80]}...")
        else:
            print(f"   ⚠️  No chunks found - checking why...")
            
            # Check if chunking is enabled
            from app.config.settings import get_settings
            settings = get_settings()
            print(f"   CHUNK_ON_RESOURCE_CREATE: {getattr(settings, 'CHUNK_ON_RESOURCE_CREATE', 'NOT SET')}")
            print(f"   CHUNK_ON_CREATE: {getattr(settings, 'CHUNK_ON_CREATE', 'NOT SET')}")
        
        db.close()
        return len(chunks) > 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chunking_configuration():
    """Test 3: Check chunking configuration"""
    print("\n" + "="*60)
    print("🔍 Test 3: Chunking Configuration Check")
    print("="*60)
    
    try:
        from app.config.settings import get_settings
        
        settings = get_settings()
        
        print("📋 Chunking Settings:")
        print(f"   CHUNK_ON_RESOURCE_CREATE: {getattr(settings, 'CHUNK_ON_RESOURCE_CREATE', 'NOT SET')}")
        print(f"   CHUNK_ON_CREATE: {getattr(settings, 'CHUNK_ON_CREATE', 'NOT SET')}")
        print(f"   CHUNKING_STRATEGY: {getattr(settings, 'CHUNKING_STRATEGY', 'NOT SET')}")
        print(f"   CHUNK_SIZE: {getattr(settings, 'CHUNK_SIZE', 'NOT SET')}")
        print(f"   CHUNK_OVERLAP: {getattr(settings, 'CHUNK_OVERLAP', 'NOT SET')}")
        
        # Check if chunking is enabled
        chunk_enabled = getattr(settings, 'CHUNK_ON_RESOURCE_CREATE', False) or getattr(settings, 'CHUNK_ON_CREATE', False)
        
        if chunk_enabled:
            print(f"\n✅ Chunking is ENABLED")
        else:
            print(f"\n⚠️  Chunking is DISABLED")
            print(f"   To enable, set CHUNK_ON_RESOURCE_CREATE=true in .env")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration check failed: {e}")
        return False

def test_event_handler_exists():
    """Test 4: Verify event handler is registered"""
    print("\n" + "="*60)
    print("🔍 Test 4: Event Handler Registration")
    print("="*60)
    
    try:
        from app.shared.event_bus import event_bus
        
        # Check if resource.created handler exists
        handlers = event_bus._handlers.get("resource.created", [])
        
        print(f"📋 Handlers for 'resource.created' event: {len(handlers)}")
        
        for i, handler in enumerate(handlers):
            handler_name = handler.__name__ if hasattr(handler, '__name__') else str(handler)
            print(f"   Handler {i+1}: {handler_name}")
        
        if len(handlers) > 0:
            print(f"\n✅ Event handlers are registered")
            return True
        else:
            print(f"\n⚠️  No handlers found for resource.created")
            return False
            
    except Exception as e:
        print(f"❌ Handler check failed: {e}")
        return False

def main():
    print("="*60)
    print("🧪 COMPREHENSIVE CHUNKING VERIFICATION")
    print("="*60)
    
    results = {}
    
    # Test 1: Direct chunking service
    results["ChunkingService Direct"] = test_chunking_service_directly()
    
    # Test 2: Configuration
    results["Configuration"] = test_chunking_configuration()
    
    # Test 3: Event handlers
    results["Event Handlers"] = test_event_handler_exists()
    
    # Test 4: End-to-end with resource creation
    results["Resource Creation Pipeline"] = test_resource_creation_with_chunking()
    
    # Summary
    print("\n" + "="*60)
    print("📊 FINAL RESULTS")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED - CHUNKING WORKS!")
    else:
        print("⚠️  SOME TESTS FAILED - CHECK DETAILS ABOVE")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
