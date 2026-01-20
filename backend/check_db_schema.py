#!/usr/bin/env python3
"""Check database schema"""

from app.shared.database import init_database
from sqlalchemy import inspect

init_database()

# Import after init
from app.shared.database import sync_engine

# Check tables
insp = inspect(sync_engine)
tables = insp.get_table_names()
print(f"Found {len(tables)} tables:")
for table in sorted(tables):
    print(f"  - {table}")

# Check resources table columns
if 'resources' in tables:
    print("\nResources table columns:")
    columns = insp.get_columns('resources')
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
    
    # Check if curation_status exists
    col_names = [c['name'] for c in columns]
    if 'curation_status' in col_names:
        print("\n✓ curation_status column EXISTS")
    else:
        print("\n✗ curation_status column MISSING")
