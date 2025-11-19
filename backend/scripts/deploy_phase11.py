"""
Phase 11 deployment script.

Orchestrates the complete deployment process:
1. Backup database
2. Run migration
3. Verify migration
4. Test rollback capability
"""

import subprocess
import sys
import time
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))


def run_command(cmd, description, cwd=None):
    """
    Run a shell command and report results.
    
    Args:
        cmd: Command to run (list or string)
        description: Description of what the command does
        cwd: Working directory (default: backend_dir)
        
    Returns:
        True if command succeeded, False otherwise
    """
    if cwd is None:
        cwd = backend_dir
    
    print(f"\n{description}...")
    print(f"Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=isinstance(cmd, str)
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode == 0:
            print(f"[OK] {description} completed successfully")
            return True
        else:
            print(f"[ERROR] {description} failed with exit code {result.returncode}")
            return False
    
    except Exception as e:
        print(f"[ERROR] Error running command: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the complete Phase 11 deployment process."""
    print("=" * 60)
    print("Phase 11 Deployment Script")
    print("Hybrid Recommendation Engine")
    print("=" * 60)
    print()
    
    start_time = time.time()
    
    # Step 1: Backup database
    print("\n" + "=" * 60)
    print("STEP 1: Backup Database")
    print("=" * 60)
    
    if not run_command(
        [sys.executable, "scripts/backup_database.py"],
        "Creating database backup"
    ):
        print("\n[ERROR] Deployment aborted: Backup failed")
        return False
    
    # Step 2: Run migration
    print("\n" + "=" * 60)
    print("STEP 2: Run Migration")
    print("=" * 60)
    
    migration_start = time.time()
    
    if not run_command(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        "Running Alembic migration"
    ):
        print("\n[ERROR] Deployment aborted: Migration failed")
        return False
    
    migration_duration = time.time() - migration_start
    print(f"\nMigration completed in {migration_duration:.2f} seconds")
    
    if migration_duration > 60:
        print("[WARNING] Migration took longer than expected (>60 seconds)")
    
    # Step 3: Verify migration
    print("\n" + "=" * 60)
    print("STEP 3: Verify Migration")
    print("=" * 60)
    
    if not run_command(
        [sys.executable, "scripts/verify_migration.py"],
        "Verifying migration results"
    ):
        print("\n[ERROR] Deployment aborted: Verification failed")
        print("\nAttempting rollback...")
        run_command(
            [sys.executable, "-m", "alembic", "downgrade", "-1"],
            "Rolling back migration"
        )
        return False
    
    # Step 4: Test rollback capability
    print("\n" + "=" * 60)
    print("STEP 4: Test Rollback Capability")
    print("=" * 60)
    print("\nSkipping actual rollback test to preserve migration.")
    print("To test rollback manually, run: alembic downgrade -1")
    print("Then re-apply with: alembic upgrade head")
    
    # Summary
    total_duration = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETE")
    print("=" * 60)
    print(f"\nTotal deployment time: {total_duration:.2f} seconds")
    print(f"Migration time: {migration_duration:.2f} seconds")
    print("\nTables created:")
    print("  - users")
    print("  - user_profiles")
    print("  - user_interactions")
    print("  - recommendation_feedback")
    print("\nNext steps:")
    print("  1. Train initial NCF model: python scripts/train_ncf_model.py")
    print("  2. Set up monitoring dashboards")
    print("  3. Test API endpoints")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
