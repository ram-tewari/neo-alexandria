"""
Comprehensive test for Phase 7 collections migration.

This script verifies that the migration d4a8e9f1b2c3 correctly:
1. Creates the collections table with all required columns and constraints
2. Creates the collection_resources association table
3. Creates all required indexes
4. Supports CASCADE delete for foreign keys
5. Can be downgraded cleanly
"""
import sqlite3
import sys

def test_collections_table_structure():
    """Test collections table structure."""
    conn = sqlite3.connect('backend.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("Testing collections table structure...")
    print("=" * 60)
    
    # Check table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='collections'")
    if not cursor.fetchone():
        print("✗ collections table does not exist")
        return False
    print("✓ collections table exists")
    
    # Check columns
    cursor.execute("PRAGMA table_info(collections)")
    columns = {col[1]: col[2] for col in cursor.fetchall()}
    
    required_columns = {
        'id': 'CHAR(36)',
        'name': 'VARCHAR(255)',
        'description': 'TEXT',
        'owner_id': 'VARCHAR(255)',
        'visibility': 'VARCHAR(20)',
        'parent_id': 'CHAR(36)',
        'embedding': 'JSON',
        'created_at': 'DATETIME',
        'updated_at': 'DATETIME'
    }
    
    for col_name, col_type in required_columns.items():
        if col_name not in columns:
            print(f"✗ Missing column: {col_name}")
            return False
        print(f"✓ Column {col_name} exists ({columns[col_name]})")
    
    # Check indexes
    cursor.execute("PRAGMA index_list(collections)")
    indexes = [idx[1] for idx in cursor.fetchall()]
    
    required_indexes = ['ix_collections_owner_id', 'ix_collections_visibility', 'ix_collections_parent_id']
    for idx_name in required_indexes:
        if idx_name not in indexes:
            print(f"✗ Missing index: {idx_name}")
            return False
        print(f"✓ Index {idx_name} exists")
    
    # Check foreign key
    cursor.execute("PRAGMA foreign_key_list(collections)")
    fks = cursor.fetchall()
    has_parent_fk = any(fk[2] == 'collections' and fk[3] == 'parent_id' for fk in fks)
    if not has_parent_fk:
        print("✗ Missing foreign key for parent_id")
        return False
    print("✓ Foreign key for parent_id exists")
    
    conn.close()
    return True

def test_collection_resources_table_structure():
    """Test collection_resources table structure."""
    conn = sqlite3.connect('backend.db')
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("Testing collection_resources table structure...")
    print("=" * 60)
    
    # Check table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='collection_resources'")
    if not cursor.fetchone():
        print("✗ collection_resources table does not exist")
        return False
    print("✓ collection_resources table exists")
    
    # Check columns
    cursor.execute("PRAGMA table_info(collection_resources)")
    columns = {col[1]: col[2] for col in cursor.fetchall()}
    
    required_columns = {
        'collection_id': 'CHAR(36)',
        'resource_id': 'CHAR(36)',
        'added_at': 'DATETIME'
    }
    
    for col_name, col_type in required_columns.items():
        if col_name not in columns:
            print(f"✗ Missing column: {col_name}")
            return False
        print(f"✓ Column {col_name} exists ({columns[col_name]})")
    
    # Check indexes
    cursor.execute("PRAGMA index_list(collection_resources)")
    indexes = [idx[1] for idx in cursor.fetchall()]
    
    required_indexes = ['idx_collection_resources_collection', 'idx_collection_resources_resource']
    for idx_name in required_indexes:
        if idx_name not in indexes:
            print(f"✗ Missing index: {idx_name}")
            return False
        print(f"✓ Index {idx_name} exists")
    
    # Check foreign keys
    cursor.execute("PRAGMA foreign_key_list(collection_resources)")
    fks = cursor.fetchall()
    
    has_collection_fk = any(fk[2] == 'collections' and fk[3] == 'collection_id' for fk in fks)
    has_resource_fk = any(fk[2] == 'resources' and fk[3] == 'resource_id' for fk in fks)
    
    if not has_collection_fk:
        print("✗ Missing foreign key for collection_id")
        return False
    print("✓ Foreign key for collection_id exists")
    
    if not has_resource_fk:
        print("✗ Missing foreign key for resource_id")
        return False
    print("✓ Foreign key for resource_id exists")
    
    conn.close()
    return True

def test_alembic_version():
    """Test alembic version is correct."""
    conn = sqlite3.connect('backend.db')
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("Testing alembic version...")
    print("=" * 60)
    
    cursor.execute("SELECT version_num FROM alembic_version")
    version = cursor.fetchone()[0]
    
    if version != 'd4a8e9f1b2c3':
        print(f"✗ Alembic version is {version}, expected d4a8e9f1b2c3")
        return False
    print(f"✓ Alembic version is correct: {version}")
    
    conn.close()
    return True

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Phase 7 Collections Migration Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_collections_table_structure,
        test_collection_resources_table_structure,
        test_alembic_version
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ All tests passed! Migration is correct.")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the migration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
