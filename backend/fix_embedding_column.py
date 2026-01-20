#!/usr/bin/env python3
"""Fix embedding column type mismatch"""

from app.shared.database import init_database
from sqlalchemy import text

init_database()
from app.shared.database import sync_engine

with sync_engine.connect() as conn:
    # Change embedding column from ARRAY to JSON
    try:
        conn.execute(text("""
            ALTER TABLE resources 
            ALTER COLUMN embedding TYPE JSON USING embedding::text::json
        """))
        conn.commit()
        print("✓ Changed embedding column to JSON type")
    except Exception as e:
        print(f"✗ Error changing embedding type: {e}")

print("\nDone!")
