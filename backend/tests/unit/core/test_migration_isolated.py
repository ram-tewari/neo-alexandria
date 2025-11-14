"""Test annotation migration in isolation with a test database."""
import os
import sqlite3
import subprocess
import sys
import tempfile
import shutil

def run_alembic_with_test_db(db_path, command):
    """Run alembic command with a test database."""
    env = os.environ.copy()
    env['DATABASE_URL'] = f'sqlite:///{db_path}'
    
    result = subprocess.run(
        [sys.executable, "-m", "alembic"] + command.split(),
        capture_output=True,
        text=True,
        env=env
    )
    return result.returncode == 0, result.stdout, result.stderr

def check_table_exists(db_path, table_name):
    """Check if a table exists."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def main():
    """Test migration with a fresh test database."""
    print("=" * 60)
    print("Testing Annotation Migration (Isolated)")
    print("=" * 60)
    
    # Create a temporary directory for test database
    test_dir = tempfile.mkdtemp()
    test_db = os.path.join(test_dir, "test.db")
    
    try:
        # Copy the current database to test location (to get existing schema)
        if os.path.exists("backend.db"):
            shutil.copy("backend.db", test_db)
            print(f"\n✓ Created test database: {test_db}")
        else:
            print("\n✗ backend.db not found")
            return False
        
        # Drop annotations table if it exists
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS annotations")
        conn.commit()
        conn.close()
        print("✓ Dropped annotations table from test database")
        
        # Set to previous migration
        print("\n1. Setting migration to d4a8e9f1b2c3...")
        success, stdout, stderr = run_alembic_with_test_db(test_db, "stamp d4a8e9f1b2c3")
        if not success:
            print(f"✗ Failed: {stderr}")
            return False
        print("✓ Stamped to d4a8e9f1b2c3")
        
        # Upgrade to new migration
        print("\n2. Upgrading to e5b9f2c3d4e5...")
        success, stdout, stderr = run_alembic_with_test_db(test_db, "upgrade e5b9f2c3d4e5")
        if not success:
            print(f"✗ Failed: {stderr}")
            return False
        print("✓ Upgraded to e5b9f2c3d4e5")
        
        # Verify table exists
        print("\n3. Verifying table exists...")
        if not check_table_exists(test_db, "annotations"):
            print("✗ Table does not exist")
            return False
        print("✓ Table exists")
        
        # Test downgrade
        print("\n4. Testing downgrade...")
        success, stdout, stderr = run_alembic_with_test_db(test_db, "downgrade d4a8e9f1b2c3")
        if not success:
            print(f"✗ Failed: {stderr}")
            return False
        print("✓ Downgraded to d4a8e9f1b2c3")
        
        # Verify table is dropped
        print("\n5. Verifying table is dropped...")
        if check_table_exists(test_db, "annotations"):
            print("✗ Table still exists")
            return False
        print("✓ Table dropped")
        
        # Upgrade again
        print("\n6. Upgrading again to e5b9f2c3d4e5...")
        success, stdout, stderr = run_alembic_with_test_db(test_db, "upgrade e5b9f2c3d4e5")
        if not success:
            print(f"✗ Failed: {stderr}")
            return False
        print("✓ Upgraded to e5b9f2c3d4e5")
        
        # Final verification
        print("\n7. Final verification...")
        if not check_table_exists(test_db, "annotations"):
            print("✗ Table does not exist")
            return False
        print("✓ Table exists")
        
        print("\n" + "=" * 60)
        print("✓ All migration tests passed!")
        print("=" * 60)
        return True
        
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print("\n✓ Cleaned up test directory")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
