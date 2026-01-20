"""
Detailed database check showing ingestion progress.
"""

import psycopg2

DB_CONNECTION = "postgresql://postgres:devpassword@localhost:5432/neo_alexandria_dev"

def check_progress():
    """Check ingestion progress"""
    print("\n" + "="*80)
    print("NEO ALEXANDRIA - INGESTION PROGRESS")
    print("="*80 + "\n")
    
    try:
        conn = psycopg2.connect(DB_CONNECTION)
        cursor = conn.cursor()
        
        # Total resources
        cursor.execute("SELECT COUNT(*) FROM resources;")
        total_resources = cursor.fetchone()[0]
        print(f"📚 Total Resources: {total_resources}")
        
        # Resources by status
        cursor.execute("""
            SELECT ingestion_status, COUNT(*) 
            FROM resources 
            GROUP BY ingestion_status;
        """)
        print("\n📊 Resources by Status:")
        for status, count in cursor.fetchall():
            print(f"   {status}: {count}")
        
        # Total chunks
        cursor.execute("SELECT COUNT(*) FROM document_chunks;")
        total_chunks = cursor.fetchone()[0]
        print(f"\n📦 Total Chunks: {total_chunks}")
        
        # Resources with chunks
        cursor.execute("""
            SELECT COUNT(DISTINCT resource_id) 
            FROM document_chunks;
        """)
        resources_with_chunks = cursor.fetchone()[0]
        print(f"✅ Resources with Chunks: {resources_with_chunks}/{total_resources}")
        
        # Top 5 resources by chunk count
        cursor.execute("""
            SELECT r.title, COUNT(dc.id) as chunk_count
            FROM resources r
            LEFT JOIN document_chunks dc ON r.id = dc.resource_id
            GROUP BY r.id, r.title
            ORDER BY chunk_count DESC
            LIMIT 5;
        """)
        print("\n🏆 Top 5 Resources by Chunks:")
        for title, count in cursor.fetchall():
            print(f"   {count:3d} chunks - {title[:60]}")
        
        # Recent resources
        cursor.execute("""
            SELECT title, ingestion_status, created_at
            FROM resources
            ORDER BY created_at DESC
            LIMIT 5;
        """)
        print("\n🕐 Recent Resources:")
        for title, status, created_at in cursor.fetchall():
            print(f"   [{status:10s}] {title[:60]}")
        
        cursor.close()
        conn.close()
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        if total_chunks > 0:
            avg_chunks = total_chunks / resources_with_chunks if resources_with_chunks > 0 else 0
            print(f"\n✅ System is operational!")
            print(f"   Average chunks per resource: {avg_chunks:.1f}")
            print(f"   Chunking coverage: {resources_with_chunks}/{total_resources} ({resources_with_chunks/total_resources*100:.1f}%)")
        else:
            print(f"\n⏳ Ingestion in progress...")
            print(f"   Wait a few more minutes for chunks to be created")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Database error: {e}")
        return False


if __name__ == "__main__":
    check_progress()
