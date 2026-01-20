#!/usr/bin/env python3
"""Add missing curation columns to resources table"""

from app.shared.database import init_database
from sqlalchemy import text

init_database()
from app.shared.database import sync_engine

with sync_engine.connect() as conn:
    # Add curation_status column
    try:
        conn.execute(text("""
            ALTER TABLE resources 
            ADD COLUMN curation_status VARCHAR NOT NULL DEFAULT 'pending'
        """))
        conn.commit()
        print("✓ Added curation_status column")
    except Exception as e:
        if "already exists" in str(e):
            print("✓ curation_status column already exists")
        else:
            print(f"✗ Error adding curation_status: {e}")
    
    # Add assigned_curator column
    try:
        conn.execute(text("""
            ALTER TABLE resources 
            ADD COLUMN assigned_curator VARCHAR(255)
        """))
        conn.commit()
        print("✓ Added assigned_curator column")
    except Exception as e:
        if "already exists" in str(e):
            print("✓ assigned_curator column already exists")
        else:
            print(f"✗ Error adding assigned_curator: {e}")
    
    # Create index on assigned_curator
    try:
        conn.execute(text("""
            CREATE INDEX idx_resources_assigned_curator 
            ON resources(assigned_curator)
        """))
        conn.commit()
        print("✓ Created index on assigned_curator")
    except Exception as e:
        if "already exists" in str(e):
            print("✓ Index already exists")
        else:
            print(f"✗ Error creating index: {e}")

print("\nDone!")
