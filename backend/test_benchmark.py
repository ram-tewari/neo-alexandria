#!/usr/bin/env python
"""Minimal test to verify benchmark can run."""

print("Test script starting...")

import sys
sys.path.insert(0, ".")

print("Importing database...")
from app.shared.database import init_database, get_sync_db

print("Importing models...")
from app.database.models import DocumentChunk, Resource

print("Initializing database...")
init_database()

print("Getting database session...")
db_gen = get_sync_db()
db = next(db_gen)

print("Querying chunks...")
chunks = db.query(DocumentChunk).limit(5).all()
print(f"Found {len(chunks)} chunks")

print("Querying resources...")
resources = db.query(Resource).limit(5).all()
print(f"Found {len(resources)} resources")

print("\n✅ Test completed successfully!")
