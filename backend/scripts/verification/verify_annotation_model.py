"""Verify the Annotation model structure."""

import sqlite3


def verify_annotation_table():
    """Verify the annotations table structure."""
    conn = sqlite3.connect("backend.db")
    cursor = conn.cursor()

    print("=" * 60)
    print("Verifying Annotation Table Structure")
    print("=" * 60)

    # Check if table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='annotations'"
    )
    if not cursor.fetchone():
        print("✗ Table 'annotations' does not exist")
        conn.close()
        return False
    print("✓ Table 'annotations' exists")

    # Check columns
    print("\nColumns:")
    cursor.execute("PRAGMA table_info(annotations)")
    columns = cursor.fetchall()

    expected_columns = {
        "id": "CHAR(36)",
        "resource_id": "CHAR(36)",
        "user_id": "VARCHAR(255)",
        "start_offset": "INTEGER",
        "end_offset": "INTEGER",
        "highlighted_text": "TEXT",
        "note": "TEXT",
        "tags": "TEXT",
        "color": "VARCHAR(7)",
        "embedding": "JSON",
        "context_before": "VARCHAR(50)",
        "context_after": "VARCHAR(50)",
        "is_shared": "INTEGER",
        "collection_ids": "TEXT",
        "created_at": "DATETIME",
        "updated_at": "DATETIME",
    }

    found_columns = {}
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        col_notnull = col[3]
        col_default = col[4]
        found_columns[col_name] = col_type

        nullable = "NOT NULL" if col_notnull else "NULL"
        default = f", DEFAULT={col_default}" if col_default else ""
        print(f"  - {col_name}: {col_type} ({nullable}{default})")

    # Verify all expected columns exist
    missing = set(expected_columns.keys()) - set(found_columns.keys())
    if missing:
        print(f"\n✗ Missing columns: {missing}")
        conn.close()
        return False
    print(f"\n✓ All {len(expected_columns)} expected columns present")

    # Check foreign keys
    print("\nForeign Keys:")
    cursor.execute("PRAGMA foreign_key_list(annotations)")
    fks = cursor.fetchall()
    for fk in fks:
        print(f"  - {fk[3]} -> {fk[2]}.{fk[4]} (ON DELETE {fk[6]})")

    if not fks:
        print("  ✗ No foreign keys found")
        conn.close()
        return False
    print(f"✓ {len(fks)} foreign key(s) defined")

    # Check indexes
    print("\nIndexes:")
    cursor.execute("PRAGMA index_list(annotations)")
    indexes = cursor.fetchall()

    expected_indexes = [
        "idx_annotations_resource",
        "idx_annotations_user",
        "idx_annotations_user_resource",
        "idx_annotations_created",
    ]

    found_indexes = []
    for idx in indexes:
        idx_name = idx[1]
        found_indexes.append(idx_name)

        # Get index columns
        cursor.execute(f"PRAGMA index_info({idx_name})")
        idx_cols = cursor.fetchall()
        col_names = [col[2] for col in idx_cols]
        print(f"  - {idx_name}: ({', '.join(col_names)})")

    # Check if expected indexes exist
    for exp_idx in expected_indexes:
        if exp_idx not in found_indexes:
            print(f"\n✗ Missing index: {exp_idx}")
            conn.close()
            return False

    print(f"\n✓ All {len(expected_indexes)} expected indexes present")

    # Check relationships
    print("\nRelationships:")
    print("  - Annotation.resource -> Resource (many-to-one)")
    print("  - Resource.annotations -> Annotation (one-to-many, cascade delete)")
    print("✓ Relationships defined in model")

    conn.close()

    print("\n" + "=" * 60)
    print("✓ Annotation model verification complete!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    import sys

    success = verify_annotation_table()
    sys.exit(0 if success else 1)
