"""Quick verification that everything is set up correctly."""

import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

print("Step 1: Importing modules...")
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

print("Step 2: Connecting to database...")
engine = create_engine("sqlite:///./backend.db")
Session = sessionmaker(bind=engine)
db = Session()

print("Step 3: Counting data...")
result = db.execute(text("SELECT COUNT(*) FROM resources"))
resource_count = result.scalar()

result = db.execute(text("SELECT COUNT(*) FROM annotations"))
annotation_count = result.scalar()

print(f"\n✅ SUCCESS")
print(f"Resources: {resource_count}")
print(f"Annotations: {annotation_count}")

if resource_count > 0:
    print("\n✅ Database is seeded and ready!")
else:
    print("\n⚠️  Database is empty. Run: python scripts/seed_audit_data_simple.py")

db.close()
