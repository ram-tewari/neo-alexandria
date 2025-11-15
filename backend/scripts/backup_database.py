"""
Database backup script for Phase 11 deployment.

Creates a backup of the production database before running migrations.
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

from backend.app.config.settings import get_settings


def backup_database():
    """
    Create a backup of the database file.
    
    Returns:
        Path to backup file or None if backup failed
    """
    try:
        settings = get_settings()
        db_url = settings.DATABASE_URL
        
        # Extract database file path from URL
        # Format: sqlite:///path/to/db.db
        if db_url.startswith("sqlite:///"):
            db_path = db_url.replace("sqlite:///", "")
            
            # Handle relative paths
            if not os.path.isabs(db_path):
                db_path = os.path.join(backend_dir, db_path)
            
            if not os.path.exists(db_path):
                print(f"Database file not found: {db_path}")
                return None
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(backend_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            db_filename = os.path.basename(db_path)
            backup_filename = f"{db_filename}.backup_{timestamp}"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Copy database file
            print(f"Creating backup: {db_path} -> {backup_path}")
            shutil.copy2(db_path, backup_path)
            
            # Verify backup
            if os.path.exists(backup_path):
                backup_size = os.path.getsize(backup_path)
                original_size = os.path.getsize(db_path)
                
                if backup_size == original_size:
                    print(f"[OK] Backup created successfully: {backup_path}")
                    print(f"  Size: {backup_size:,} bytes")
                    return backup_path
                else:
                    print(f"[ERROR] Backup size mismatch!")
                    print(f"  Original: {original_size:,} bytes")
                    print(f"  Backup: {backup_size:,} bytes")
                    return None
            else:
                print(f"[ERROR] Backup file not created")
                return None
        
        else:
            print(f"Unsupported database type: {db_url}")
            print("This script only supports SQLite databases")
            return None
    
    except Exception as e:
        print(f"[ERROR] Error creating backup: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("Database Backup Script - Phase 11 Deployment")
    print("=" * 60)
    print()
    
    backup_path = backup_database()
    
    if backup_path:
        print()
        print("=" * 60)
        print("Backup completed successfully!")
        print("=" * 60)
        sys.exit(0)
    else:
        print()
        print("=" * 60)
        print("Backup failed!")
        print("=" * 60)
        sys.exit(1)
