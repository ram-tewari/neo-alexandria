"""
Simple test: Check if any chunks exist in the database.
Uses PostgreSQL connection from settings.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import get_settings
import psycopg2

def check_database():
    """Check database for resources and chunks."""
    print("=" * 60)
    print("DATABASE CHUNK CHECK (PostgreSQL)")
    print("=" * 60)
    
    settings = get_settings()
    db_url = settings.get_database_url()
    
    # Parse PostgreSQL URL
    # Format: postgresql://user:pass@host:port/dbname or postgresql+asyncpg://...
    import re
    match = re.match(r'postgresql(?:\+asyncpg)?://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
    if not match:
        print(f"❌ Could not parse database URL: {db_url}")
        return
    
    user, password, host, port, dbname = match.groups()
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname
        )
        cursor = conn.cursor()
        
        # Check total resources
        cursor.execute("SELECT COUNT(*) FROM resources")
        resource_count = cursor.fetchone()[0]
        print(f"\n📊 Total resources: {resource_count}")
        
        # Check resources with completed ingestion
        cursor.execute("SELECT COUNT(*) FROM resources WHERE ingestion_status = 'completed'")
        completed_count = cursor.fetchone()[0]
        print(f"✅ Completed ingestion: {completed_count}")
        
        # Check total chunks
        cursor.execute("SELECT COUNT(*) FROM document_chunks")
        chunk_count = cursor.fetchone()[0]
        print(f"📦 Total chunks: {chunk_count}")
        
        if chunk_count > 0:
            # Show chunk distribution
            cursor.execute("""
                SELECT r.title, COUNT(c.id) as chunk_count
                FROM resources r
                JOIN document_chunks c ON r.id = c.resource_id
                GROUP BY r.id, r.title
                ORDER BY chunk_count DESC
                LIMIT 5
            """)
            
            print(f"\n📋 Resources with chunks:")
            for title, count in cursor.fetchall():
                print(f"   • {title[:50]}: {count} chunks")
        
        # Check recent resources
        cursor.execute("""
            SELECT id, title, ingestion_status, created_at
            FROM resources
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        print(f"\n🕐 Recent resources:")
        for res_id, title, status, created in cursor.fetchall():
            print(f"   • {title[:40]}: {status}")
            
            # Check if this resource has chunks
            cursor.execute("SELECT COUNT(*) FROM document_chunks WHERE resource_id = %s", (res_id,))
            chunks = cursor.fetchone()[0]
            if chunks > 0:
                print(f"     └─ {chunks} chunks ✅")
        
        conn.close()
        
        print("\n" + "=" * 60)
        if chunk_count > 0:
            print("✅ CHUNKING IS WORKING - Chunks found in database!")
        else:
            print("❌ NO CHUNKS FOUND")
            print("\nPossible reasons:")
            print("1. Ingestion hasn't completed yet (check ingestion_status)")
            print("2. CHUNK_ON_RESOURCE_CREATE is disabled")
            print("3. Chunking code has errors (check server logs)")
            print("4. Content too short (< 100 chars)")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
