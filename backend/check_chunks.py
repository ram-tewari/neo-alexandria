"""Quick check for chunks in database"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.config.settings import get_settings

settings = get_settings()
engine = create_engine(settings.get_database_url())

with engine.connect() as conn:
    # Count total chunks
    result = conn.execute(text('SELECT COUNT(*) as count FROM document_chunks'))
    total = result.scalar()
    print(f"Total chunks in database: {total}")
    
    if total > 0:
        # Show recent chunks
        result = conn.execute(text('''
            SELECT resource_id, position, token_count, 
                   substr(content, 1, 50) as preview,
                   created_at
            FROM document_chunks 
            ORDER BY created_at DESC 
            LIMIT 5
        '''))
        
        print("\nRecent chunks:")
        for row in result:
            print(f"  Resource: {row[0]}")
            print(f"  Position: {row[1]}, Tokens: {row[2]}")
            print(f"  Preview: {row[3]}...")
            print(f"  Created: {row[4]}")
            print()
