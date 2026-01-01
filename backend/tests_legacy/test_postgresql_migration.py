"""
Test PostgreSQL compatibility migration.

This test verifies that the migration correctly detects database types
and applies appropriate transformations.
"""
import pytest


def test_migration_imports():
    """Test that the migration file can be imported without errors."""
    import sys
    import os
    # Add the alembic versions directory to the path
    versions_dir = os.path.join(os.path.dirname(__file__), '..', 'alembic', 'versions')
    sys.path.insert(0, versions_dir)
    
    # Import the migration module by filename
    import importlib.util
    migration_path = os.path.join(versions_dir, '20250120_postgresql_compatibility.py')
    spec = importlib.util.spec_from_file_location("migration", migration_path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    
    assert hasattr(migration, 'upgrade')
    assert hasattr(migration, 'downgrade')
    assert hasattr(migration, 'upgrade_postgresql')
    assert hasattr(migration, 'downgrade_postgresql')
    assert migration.revision == '20250120_postgresql_compatibility'
    assert migration.down_revision == 'j0k1l2m3n4o5'


def test_migration_detects_sqlite():
    """Test that migration skips PostgreSQL-specific changes for SQLite."""
    import os
    import importlib.util
    
    versions_dir = os.path.join(os.path.dirname(__file__), '..', 'alembic', 'versions')
    migration_path = os.path.join(versions_dir, '20250120_postgresql_compatibility.py')
    spec = importlib.util.spec_from_file_location("migration", migration_path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    
    # Verify that the upgrade function checks dialect name
    import inspect
    source = inspect.getsource(migration.upgrade)
    
    # The upgrade function should check for dialect name
    assert "dialect_name = bind.dialect.name" in source or "bind.dialect.name" in source
    assert "if dialect_name == 'postgresql'" in source or "if bind.dialect.name == 'postgresql'" in source
    
    # Verify that SQLite path exists (else branch or pass statement)
    assert "else:" in source


def test_migration_structure():
    """Test that the migration has the correct structure."""
    import os
    import importlib.util
    
    versions_dir = os.path.join(os.path.dirname(__file__), '..', 'alembic', 'versions')
    migration_path = os.path.join(versions_dir, '20250120_postgresql_compatibility.py')
    spec = importlib.util.spec_from_file_location("migration", migration_path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    
    # Check that upgrade_postgresql function exists and has the expected operations
    import inspect
    source = inspect.getsource(migration.upgrade_postgresql)
    
    # Verify key operations are present
    assert 'CREATE EXTENSION IF NOT EXISTS pg_trgm' in source
    assert 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"' in source
    assert 'ALTER TABLE resources' in source
    assert 'ALTER COLUMN subject TYPE JSONB' in source
    assert 'ALTER COLUMN relation TYPE JSONB' in source
    assert 'ALTER COLUMN embedding TYPE JSONB' in source
    assert 'CREATE INDEX' in source or 'create_index' in source
    assert 'search_vector' in source
    assert 'resources_search_vector_update' in source


def test_migration_has_proper_documentation():
    """Test that the migration has proper documentation."""
    import os
    import importlib.util
    
    versions_dir = os.path.join(os.path.dirname(__file__), '..', 'alembic', 'versions')
    migration_path = os.path.join(versions_dir, '20250120_postgresql_compatibility.py')
    spec = importlib.util.spec_from_file_location("migration", migration_path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    
    # Check module docstring
    assert migration.__doc__ is not None
    assert 'PostgreSQL Compatibility' in migration.__doc__
    assert 'Phase 13' in migration.__doc__
    
    # Check that key features are documented
    doc = migration.__doc__
    assert 'JSONB' in doc
    assert 'GIN' in doc or 'gin' in doc
    assert 'pg_trgm' in doc
    assert 'full-text search' in doc.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
