"""
Migration verification script for Phase 11 deployment.

Verifies that all required tables and indexes were created successfully.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, inspect
from backend.app.config.settings import get_settings


def verify_migration():
    """
    Verify that Phase 11 migration created all required tables and indexes.
    
    Returns:
        True if verification passed, False otherwise
    """
    try:
        settings = get_settings()
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        
        print("Verifying Phase 11 migration...")
        print()
        
        # Required tables
        required_tables = [
            'users',
            'user_profiles',
            'user_interactions',
            'recommendation_feedback'
        ]
        
        # Required indexes
        required_indexes = {
            'users': ['ix_users_email', 'ix_users_username'],
            'user_profiles': ['idx_user_profiles_user'],
            'user_interactions': [
                'ix_user_interactions_user_id',
                'ix_user_interactions_resource_id',
                'idx_user_interactions_user_resource',
                'idx_user_interactions_timestamp'
            ],
            'recommendation_feedback': [
                'idx_recommendation_feedback_user',
                'idx_recommendation_feedback_resource',
                'idx_recommendation_feedback_strategy'
            ]
        }
        
        all_passed = True
        
        # Check tables
        print("Checking tables...")
        existing_tables = inspector.get_table_names()
        
        for table in required_tables:
            if table in existing_tables:
                print(f"  [OK] {table}")
            else:
                print(f"  [MISSING] {table}")
                all_passed = False
        
        print()
        
        # Check indexes
        print("Checking indexes...")
        for table, indexes in required_indexes.items():
            if table not in existing_tables:
                print(f"  [MISSING] {table} - TABLE MISSING, skipping index checks")
                all_passed = False
                continue
            
            existing_indexes = [idx['name'] for idx in inspector.get_indexes(table)]
            
            for index in indexes:
                if index in existing_indexes:
                    print(f"  [OK] {table}.{index}")
                else:
                    print(f"  [MISSING] {table}.{index}")
                    all_passed = False
        
        print()
        
        # Check columns for key tables
        print("Checking key columns...")
        
        if 'user_profiles' in existing_tables:
            columns = [col['name'] for col in inspector.get_columns('user_profiles')]
            required_columns = [
                'id', 'user_id', 'diversity_preference', 'novelty_preference',
                'recency_bias', 'total_interactions'
            ]
            
            for col in required_columns:
                if col in columns:
                    print(f"  [OK] user_profiles.{col}")
                else:
                    print(f"  [MISSING] user_profiles.{col}")
                    all_passed = False
        
        if 'user_interactions' in existing_tables:
            columns = [col['name'] for col in inspector.get_columns('user_interactions')]
            required_columns = [
                'id', 'user_id', 'resource_id', 'interaction_type',
                'interaction_strength', 'is_positive'
            ]
            
            for col in required_columns:
                if col in columns:
                    print(f"  [OK] user_interactions.{col}")
                else:
                    print(f"  [MISSING] user_interactions.{col}")
                    all_passed = False
        
        print()
        
        return all_passed
    
    except Exception as e:
        print(f"[ERROR] Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Migration Verification Script - Phase 11")
    print("=" * 60)
    print()
    
    passed = verify_migration()
    
    if passed:
        print("=" * 60)
        print("[OK] All verification checks passed!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("=" * 60)
        print("[ERROR] Verification failed!")
        print("=" * 60)
        sys.exit(1)
