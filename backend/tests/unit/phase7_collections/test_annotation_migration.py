"""Test script for annotation migration."""
import sqlite3
import subprocess
import sys

def check_table_exists(db_path, table_name):
    """Check if a table exists in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def drop_table(db_path, table_name):
    """Drop a table from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    conn.close()
    print(f"✓ Dropped table: {table_name}")

def run_alembic_command(command):
    """Run an alembic command."""
    result = subprocess.run(
        [sys.executable, "-m", "alembic"] + command.split(),
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout, result.stderr

def main():
    """Test the annotation migration."""
    db_path = "backend.db"
    
    print("=" * 60)
    print("Testing Annotation Migration")
    print("=" * 60)
    
    # Step 1: Drop annotations table if it exists
    print("\n1. Cleaning up existing annotations table...")
    drop_table(db_path, "annotations")
    assert not check_table_exists(db_path, "annotations"), "Table should not exist"
    print("✓ Table does not exist")
    
    # Step 2: Downgrade to d4a8e9f1b2c3
    print("\n2. Setting migration to d4a8e9f1b2c3...")
    success, stdout, stderr = run_alembic_command("stamp d4a8e9f1b2c3")
    if not success:
        print(f"✗ Failed to stamp: {stderr}")
        return False
    print("✓ Stamped to d4a8e9f1b2c3")
    
    # Step 3: Upgrade to e5b9f2c3d4e5
    print("\n3. Upgrading to e5b9f2c3d4e5...")
    success, stdout, stderr = run_alembic_command("upgrade e5b9f2c3d4e5")
    if not success:
        print(f"✗ Failed to upgrade: {stderr}")
        return False
    print("✓ Upgraded to e5b9f2c3d4e5")
    
    # Step 4: Verify table exists
    print("\n4. Verifying annotations table exists...")
    assert check_table_exists(db_path, "annotations"), "Table should exist after upgrade"
    print("✓ Table exists")
    
    # Step 5: Verify table structure
    print("\n5. Verifying table structure...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(annotations)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    expected_columns = [
        'id', 'resource_id', 'user_id', 'start_offset', 'end_offset',
        'highlighted_text', 'note', 'tags', 'color', 'embedding',
        'context_before', 'context_after', 'is_shared', 'collection_ids',
        'created_at', 'updated_at'
    ]
    
    for col in expected_columns:
        assert col in column_names, f"Column {col} not found"
    print(f"✓ All {len(expected_columns)} columns present")
    
    # Step 6: Verify indexes
    print("\n6. Verifying indexes...")
    cursor.execute("PRAGMA index_list(annotations)")
    indexes = cursor.fetchall()
    index_names = [idx[1] for idx in indexes]
    
    expected_indexes = [
        'idx_annotations_resource',
        'idx_annotations_user',
        'idx_annotations_user_resource',
        'idx_annotations_created'
    ]
    
    for idx in expected_indexes:
        assert idx in index_names, f"Index {idx} not found"
    print(f"✓ All {len(expected_indexes)} indexes present")
    conn.close()
    
    # Step 7: Test downgrade
    print("\n7. Testing downgrade to d4a8e9f1b2c3...")
    success, stdout, stderr = run_alembic_command("downgrade d4a8e9f1b2c3")
    if not success:
        print(f"✗ Failed to downgrade: {stderr}")
        return False
    print("✓ Downgraded to d4a8e9f1b2c3")
    
    # Step 8: Verify table is dropped
    print("\n8. Verifying annotations table is dropped...")
    assert not check_table_exists(db_path, "annotations"), "Table should not exist after downgrade"
    print("✓ Table dropped successfully")
    
    # Step 9: Upgrade back to head
    print("\n9. Upgrading back to head...")
    success, stdout, stderr = run_alembic_command("upgrade head")
    if not success:
        print(f"✗ Failed to upgrade to head: {stderr}")
        return False
    print("✓ Upgraded to head")
    
    # Step 10: Final verification
    print("\n10. Final verification...")
    assert check_table_exists(db_path, "annotations"), "Table should exist"
    print("✓ Table exists")
    
    print("\n" + "=" * 60)
    print("✓ All migration tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
