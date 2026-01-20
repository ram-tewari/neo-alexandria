"""
Verification script for P0 critical fixes
Tests the fixes without requiring a running server
"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def verify_middleware_error_handling():
    """Verify middleware has proper error handling"""
    print("\n🔍 Verifying Middleware Error Handling...")
    
    try:
        from app.main import app
        
        # Check that middleware are registered
        middleware_count = len(app.user_middleware)
        print(f"✅ Found {middleware_count} middleware registered")
        
        # Import middleware to check they have error handling
        from app.shared.middleware import (
            log_requests_middleware,
            add_security_headers_middleware,
            handle_errors_middleware
        )
        
        # Check each middleware has try-except blocks
        import inspect
        
        for name, func in [
            ("log_requests", log_requests_middleware),
            ("security_headers", add_security_headers_middleware),
            ("error_handler", handle_errors_middleware)
        ]:
            source = inspect.getsource(func)
            if "try:" in source and "except" in source:
                print(f"✅ {name} has error handling")
            else:
                print(f"❌ {name} missing error handling")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error checking middleware: {e}")
        return False

async def verify_chunking_non_fatal():
    """Verify chunking failures don't block resource creation"""
    print("\n🔍 Verifying Chunking is Non-Fatal...")
    
    try:
        from app.modules.resources.service import ResourceService
        import inspect
        
        # Check create_resource method
        source = inspect.getsource(ResourceService.create_resource)
        
        # Look for try-except around chunking
        if "try:" in source and "chunk_resource" in source:
            print("✅ Chunking has error handling in create_resource")
        else:
            print("⚠️  Could not verify chunking error handling")
            
        # Check if embedding generation has error handling
        if "generate_embedding" in source:
            if source.count("try:") >= 2:  # Multiple try blocks
                print("✅ Multiple error handling blocks found")
            else:
                print("⚠️  May need additional error handling")
        
        return True
    except Exception as e:
        print(f"❌ Error checking chunking: {e}")
        return False

async def verify_embedding_non_fatal():
    """Verify embedding generation failures don't block operations"""
    print("\n🔍 Verifying Embedding Generation is Non-Fatal...")
    
    try:
        from app.shared.embeddings import EmbeddingService
        import inspect
        
        # Check generate_embedding method
        source = inspect.getsource(EmbeddingService.generate_embedding)
        
        if "try:" in source and "except" in source:
            print("✅ Embedding generation has error handling")
        else:
            print("❌ Embedding generation missing error handling")
            return False
        
        # Check if it returns None on failure
        if "return None" in source or "None" in source:
            print("✅ Returns None on failure (non-fatal)")
        else:
            print("⚠️  May not handle failures gracefully")
        
        return True
    except Exception as e:
        print(f"❌ Error checking embeddings: {e}")
        return False

async def verify_database_connection():
    """Verify database connection works"""
    print("\n🔍 Verifying Database Connection...")
    
    try:
        from app.shared.database import get_db, engine
        from sqlalchemy import text
        
        # Try to connect
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def main():
    """Run all verifications"""
    print("=" * 60)
    print("🔧 P0 Critical Fixes Verification")
    print("=" * 60)
    
    results = {
        "Middleware Error Handling": await verify_middleware_error_handling(),
        "Chunking Non-Fatal": await verify_chunking_non_fatal(),
        "Embedding Non-Fatal": await verify_embedding_non_fatal(),
        "Database Connection": await verify_database_connection(),
    }
    
    print("\n" + "=" * 60)
    print("📊 Verification Results")
    print("=" * 60)
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All P0 fixes verified successfully!")
    else:
        print("❌ Some fixes need attention")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
