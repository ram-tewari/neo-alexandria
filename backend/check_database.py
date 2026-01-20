"""
Quick script to check database for chunks and recent resources.
"""

import psycopg2
from datetime import datetime

# Use correct password from settings
DB_CONNECTION = "postgresql://postgres:devpassword@localhost:5432/neo_alexandria_dev"

def check_database():
    """Check database for chunks and resources"""
    print("\n" + "="*80)
    print("DATABASE INSPECTION")
    print("="*80 + "\n")
    
    try:
        conn = psycopg2.connect(DB_CONNECTION)
        cursor = conn.cursor()
        
        # Check total chunks
        print("1. Checking document chunks...")
        cursor.execute("SELECT COUNT(*) FROM document_chunks;")
        chunk_count = cursor.fetchone()[0]
        print(f"   Total chunks in database: {chunk_count}")
        
        # Check chunks per resource
        if chunk_count > 0:
            cursor.execute("""
                SELECT resource_id, COUNT(*) as chunk_count 
                FROM document_chunks 
                GROUP BY resource_id 
                ORDER BY chunk_count DESC 
                LIMIT 5;
            """)
            print("\n   Chunks per resource (top 5):")
            for resource_id, count in cursor.fetchall():
                print(f"     - {resource_id}: {count} chunks")
        
        # Check recent resources
        print("\n2. Checking recent resources...")
        cursor.execute("""
            SELECT id, title, ingestion_status, created_at 
            FROM resources 
            ORDER BY created_at DESC 
            LIMIT 5;
        """)
        print("   Recent resources:")
        for resource_id, title, status, created_at in cursor.fetchall():
            print(f"     - {title[:50]:50s} | Status: {status:10s} | Created: {created_at}")
        
        # Check if any resources have content
        print("\n3. Checking resource content...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM resources 
            WHERE description IS NOT NULL 
            AND LENGTH(description) > 100;
        """)
        content_count = cursor.fetchone()[0]
        print(f"   Resources with substantial content: {content_count}")
        
        cursor.close()
        conn.close()
        
        # Analysis
        print("\n" + "="*80)
        print("ANALYSIS")
        print("="*80)
        
        if chunk_count == 0:
            print("\n❌ NO CHUNKS FOUND")
            print("\nPossible causes:")
            print("  1. Server not restarted after chunking fixes")
            print("  2. All resources created before chunking was fixed")
            print("  3. Chunking code has a bug preventing execution")
            print("  4. Background tasks not running")
            
            print("\nRecommended actions:")
            print("  1. Restart server: uvicorn app.main:app --reload")
            print("  2. Create new test resource: python test_chunking_verification.py")
            print("  3. Check server logs for chunking errors")
        else:
            print(f"\n✅ CHUNKS FOUND: {chunk_count} total")
            print("   Chunking system is working!")
        
        return chunk_count > 0
        
    except Exception as e:
        print(f"\n❌ Database error: {e}")
        print("\nMake sure:")
        print("  - PostgreSQL is running")
        print("  - Database 'neo_alexandria' exists")
        print("  - Connection string is correct")
        return False


if __name__ == "__main__":
    check_database()
