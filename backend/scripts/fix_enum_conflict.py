#!/usr/bin/env python3
"""
Fix PostgreSQL enum type conflicts for testing.
This script drops and recreates enum types safely.
"""

import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
import os

# Get database URL from environment or use default
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:password@localhost:5432/backend"
)


def fix_enum_conflicts():
    """Drop and recreate enum types to fix conflicts."""
    engine = create_engine(DATABASE_URL)

    enums_to_fix = [
        "read_status",
        "ingestion_status",
        "resource_type",
        "classification_source",
    ]

    print("Connecting to database...")
    with engine.connect() as conn:
        # Start a transaction
        trans = conn.begin()

        try:
            for enum_name in enums_to_fix:
                print(f"Dropping enum type: {enum_name}")
                try:
                    conn.execute(text(f"DROP TYPE IF EXISTS {enum_name} CASCADE"))
                    print(f"  ✓ Dropped {enum_name}")
                except ProgrammingError as e:
                    print(f"  ⚠ Warning dropping {enum_name}: {e}")

            # Commit the transaction
            trans.commit()
            print("\n✅ Successfully fixed enum conflicts!")
            print("You can now run the test suite.")
            return 0

        except Exception as e:
            trans.rollback()
            print(f"\n❌ Error fixing enums: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(fix_enum_conflicts())
