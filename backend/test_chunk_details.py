"""
Check chunk details to understand why only 1 chunk is created.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import get_settings
import psycopg2
import re

def check_chunk_details():
    """Check chunk details."""
    print("=" * 60)
    print("CHUNK DETAILS ANALYSIS")
    print("=" * 60)
    
    settings = get_settings()
    db_url = settings.get_database_url()
    
    # Parse PostgreSQL URL
    match = re.match(r'postgresql(?:\+asyncpg)?://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
    if not match:
        print(f"❌ Could not parse database URL")
        return
    
    user, password, host, port, dbname = match.groups()
    
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname
    )
    cursor = conn.cursor()
    
    # Get chunking settings
    print(f"\n⚙️  Chunking Configuration:")
    print(f"   Strategy: {settings.CHUNKING_STRATEGY}")
    print(f"   Chunk Size: {settings.CHUNK_SIZE}")
    print(f"   Overlap: {settings.CHUNK_OVERLAP}")
    print(f"   Enabled: {settings.CHUNK_ON_RESOURCE_CREATE}")
    
    # Get resources with completed ingestion
    cursor.execute("""
        SELECT id, title, identifier
        FROM resources
        WHERE ingestion_status = 'completed'
        ORDER BY created_at DESC
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    if not result:
        print("\n❌ No completed resources found")
        conn.close()
        return
    
    resource_id, title, identifier = result
    print(f"\n📄 Analyzing: {title}")
    print(f"   Resource ID: {resource_id}")
    print(f"   Archive: {identifier}")
    
    # Get chunks for this resource
    cursor.execute("""
        SELECT id, chunk_index, LENGTH(content) as content_length, chunk_metadata
        FROM document_chunks
        WHERE resource_id = %s
        ORDER BY chunk_index
    """, (resource_id,))
    
    chunks = cursor.fetchall()
    print(f"\n📦 Chunks: {len(chunks)}")
    
    for chunk_id, idx, length, metadata in chunks:
        print(f"   Chunk {idx}: {length} characters")
        if metadata:
            print(f"      Metadata: {metadata}")
    
    # Try to read the archived content to see actual length
    if identifier:
        import pathlib
        archive_path = pathlib.Path(identifier)
        if archive_path.exists():
            try:
                # Look for text file
                text_file = archive_path / "content.txt"
                if text_file.exists():
                    with open(text_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print(f"\n📝 Original Content Length: {len(content)} characters")
                    print(f"   Words (approx): {len(content.split())}")
                    print(f"   Expected chunks (size={settings.CHUNK_SIZE}): ~{len(content) // settings.CHUNK_SIZE}")
                else:
                    print(f"\n⚠️  Text file not found at: {text_file}")
            except Exception as e:
                print(f"\n⚠️  Could not read archive: {e}")
        else:
            print(f"\n⚠️  Archive path does not exist: {archive_path}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    if len(chunks) == 1:
        print("⚠️  ISSUE: Only 1 chunk created")
        print("\nPossible reasons:")
        print(f"1. Content shorter than chunk size ({settings.CHUNK_SIZE} chars)")
        print("2. Chunking strategy not splitting properly")
        print("3. Content has no sentence boundaries (for semantic chunking)")
    else:
        print(f"✅ Multiple chunks created: {len(chunks)}")
    print("=" * 60)

if __name__ == "__main__":
    check_chunk_details()
