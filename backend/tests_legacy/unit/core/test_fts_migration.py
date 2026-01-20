"""Tests for FTS5 migration and index functionality."""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import text

from backend.app.database.models import Resource
from backend.app.services.search_service import _detect_fts5, _fts_index_ready


class TestFtsDetection:
    """Test FTS5 detection functionality."""

    def test_detect_fts5_sqlite_with_fts5(self, test_db):
        """Test FTS5 detection when available."""
        db = test_db()

        # Mock connection to return FTS5 in compile options
        mock_conn = MagicMock()
        mock_conn.dialect.name = "sqlite"
        mock_conn.exec_driver_sql.return_value.fetchall.return_value = [
            ("ENABLE_FTS5",),
            ("OTHER_OPTION",),
        ]

        with patch.object(db, "connection", return_value=mock_conn):
            result = _detect_fts5(db)
            assert result is True

        db.close()

    def test_detect_fts5_sqlite_without_fts5(self, test_db):
        """Test FTS5 detection when not available."""
        db = test_db()

        # Reset the global state first
        from backend.app.services.search_service import _fts_support

        _fts_support.checked = False
        _fts_support.available = False

        # Mock connection to return no FTS5 in compile options
        mock_conn = MagicMock()
        mock_conn.dialect.name = "sqlite"

        # First call returns compile options without FTS5
        # Second call (fallback table creation) fails
        mock_conn.exec_driver_sql.side_effect = [
            MagicMock(fetchall=lambda: [("OTHER_OPTION",)]),
            Exception("FTS5 not available"),
        ]

        with patch.object(db, "connection", return_value=mock_conn):
            result = _detect_fts5(db)
            assert result is False

        db.close()

    def test_detect_fts5_non_sqlite(self, test_db):
        """Test FTS5 detection with non-SQLite database."""
        db = test_db()

        # Mock connection to return PostgreSQL dialect
        mock_conn = MagicMock()
        mock_conn.dialect.name = "postgresql"

        with patch.object(db, "connection", return_value=mock_conn):
            # Reset the global state first
            from backend.app.services.search_service import _fts_support

            _fts_support.checked = False
            _fts_support.available = False

            result = _detect_fts5(db)
            assert result is False

        db.close()

    def test_detect_fts5_connection_error(self, test_db):
        """Test FTS5 detection with connection error."""
        db = test_db()

        # Mock connection to raise exception
        mock_conn = MagicMock()
        mock_conn.dialect.name = "sqlite"
        mock_conn.exec_driver_sql.side_effect = Exception("Connection error")

        with patch.object(db, "connection", return_value=mock_conn):
            # Reset the global state first
            from backend.app.services.search_service import _fts_support

            _fts_support.checked = False
            _fts_support.available = False

            result = _detect_fts5(db)
            assert result is False

        db.close()


class TestFtsIndexReady:
    """Test FTS index readiness detection."""

    def test_fts_index_ready_when_available(self, test_db):
        """Test FTS index detection when tables exist."""
        db = test_db()

        # Mock connection to return both required tables
        mock_conn = MagicMock()
        mock_conn.dialect.name = "sqlite"
        mock_conn.exec_driver_sql.return_value.fetchall.return_value = [
            ("resources_fts",),
            ("resources_fts_doc",),
        ]

        with patch.object(db, "connection", return_value=mock_conn):
            result = _fts_index_ready(db)
            assert result is True

        db.close()

    def test_fts_index_ready_when_missing(self, test_db):
        """Test FTS index detection when tables are missing."""
        db = test_db()

        # Mock connection to return no tables
        mock_conn = MagicMock()
        mock_conn.dialect.name = "sqlite"
        mock_conn.exec_driver_sql.return_value.fetchall.return_value = []

        with patch.object(db, "connection", return_value=mock_conn):
            result = _fts_index_ready(db)
            assert result is False

        db.close()

    def test_fts_index_ready_partial_tables(self, test_db):
        """Test FTS index detection when only some tables exist."""
        db = test_db()

        # Mock connection to return only one table
        mock_conn = MagicMock()
        mock_conn.dialect.name = "sqlite"
        mock_conn.exec_driver_sql.return_value.fetchall.return_value = [
            ("resources_fts",)
        ]

        with patch.object(db, "connection", return_value=mock_conn):
            result = _fts_index_ready(db)
            assert result is False

        db.close()

    def test_fts_index_ready_non_sqlite(self, test_db):
        """Test FTS index detection with non-SQLite database."""
        db = test_db()

        # Mock connection to return PostgreSQL dialect
        mock_conn = MagicMock()
        mock_conn.dialect.name = "postgresql"

        with patch.object(db, "connection", return_value=mock_conn):
            result = _fts_index_ready(db)
            assert result is False

        db.close()

    def test_fts_index_ready_connection_error(self, test_db):
        """Test FTS index detection with connection error."""
        db = test_db()

        # Mock connection to raise exception
        mock_conn = MagicMock()
        mock_conn.dialect.name = "sqlite"
        mock_conn.exec_driver_sql.side_effect = Exception("Connection error")

        with patch.object(db, "connection", return_value=mock_conn):
            result = _fts_index_ready(db)
            assert result is False

        db.close()


class TestFtsMigrationIntegration:
    """Test FTS migration integration with actual database."""

    def test_migration_creates_tables(self, test_db):
        """Test that migration creates FTS tables when FTS5 is available."""
        db = test_db()

        # Mock FTS5 detection to always return True for testing
        with patch(
            "backend.app.services.search_service._detect_fts5", return_value=True
        ):
            # Check if FTS5 is available
            if not _detect_fts5(db):
                pytest.skip("FTS5 not available in this SQLite build")

        # Run the migration
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "migration", "backend/alembic/versions/20250910_add_fts_and_triggers.py"
        )
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)

        # Execute the migration upgrade
        migration.upgrade()

        # Check that tables were created
        conn = db.connection()
        tables = conn.execute(
            text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('resources_fts', 'resources_fts_doc')
        """)
        ).fetchall()

        table_names = {row[0] for row in tables}
        assert "resources_fts" in table_names
        assert "resources_fts_doc" in table_names

        db.close()

    def test_migration_populates_existing_data(self, test_db):
        """Test that migration populates FTS index with existing data."""
        db = test_db()

        # Mock FTS5 detection to always return True for testing
        with patch(
            "backend.app.services.search_service._detect_fts5", return_value=True
        ):
            # Check if FTS5 is available
            if not _detect_fts5(db):
                pytest.skip("FTS5 not available in this SQLite build")

        # Create test resource
        resource = Resource(
            title="Test Resource",
            description="Test description for FTS indexing",
            language="en",
            type="article",
            classification_code="000",
            subject=["test"],
            read_status="unread",
            quality_score=0.5,
        )
        db.add(resource)
        db.commit()

        # Run the migration
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "migration", "backend/alembic/versions/20250910_add_fts_and_triggers.py"
        )
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        migration.upgrade()

        # Check that data was indexed
        conn = db.connection()
        fts_count = conn.execute(text("SELECT COUNT(*) FROM resources_fts")).scalar()
        doc_count = conn.execute(
            text("SELECT COUNT(*) FROM resources_fts_doc")
        ).scalar()

        assert fts_count > 0
        assert doc_count > 0
        assert fts_count == doc_count  # Should be 1:1 mapping

        db.close()

    def test_migration_triggers_work(self, test_db):
        """Test that migration triggers work for new data."""
        db = test_db()

        # Mock FTS5 detection to always return True for testing
        with patch(
            "backend.app.services.search_service._detect_fts5", return_value=True
        ):
            # Check if FTS5 is available
            if not _detect_fts5(db):
                pytest.skip("FTS5 not available in this SQLite build")

        # Run the migration first
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "migration", "backend/alembic/versions/20250910_add_fts_and_triggers.py"
        )
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        migration.upgrade()

        # Create new resource (should trigger FTS insertion)
        resource = Resource(
            title="New Test Resource",
            description="New test description for FTS indexing",
            language="en",
            type="article",
            classification_code="000",
            subject=["new", "test"],
            read_status="unread",
            quality_score=0.6,
        )
        db.add(resource)
        db.commit()

        # Check that data was automatically indexed
        conn = db.connection()
        fts_count = conn.execute(text("SELECT COUNT(*) FROM resources_fts")).scalar()
        doc_count = conn.execute(
            text("SELECT COUNT(*) FROM resources_fts_doc")
        ).scalar()

        assert fts_count > 0
        assert doc_count > 0

        # Test FTS search
        results = conn.execute(
            text("""
            SELECT d.resource_id 
            FROM resources_fts r
            JOIN resources_fts_doc d ON d.rowid = r.rowid
            WHERE r MATCH 'new'
        """)
        ).fetchall()

        assert len(results) > 0
        assert str(resource.id) in [row[0] for row in results]

        db.close()

    def test_migration_update_triggers_work(self, test_db):
        """Test that update triggers work for FTS synchronization."""
        db = test_db()

        # Mock FTS5 detection to always return True for testing
        with patch(
            "backend.app.services.search_service._detect_fts5", return_value=True
        ):
            # Check if FTS5 is available
            if not _detect_fts5(db):
                pytest.skip("FTS5 not available in this SQLite build")

        # Run the migration first
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "migration", "backend/alembic/versions/20250910_add_fts_and_triggers.py"
        )
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        migration.upgrade()

        # Create test resource
        resource = Resource(
            title="Original Title",
            description="Original description",
            language="en",
            type="article",
            classification_code="000",
            subject=["original"],
            read_status="unread",
            quality_score=0.5,
        )
        db.add(resource)
        db.commit()

        # Update the resource
        resource.title = "Updated Title"
        resource.description = "Updated description"
        db.commit()

        # Check that FTS was updated
        conn = db.connection()
        results = conn.execute(
            text("""
            SELECT r.title, r.description
            FROM resources_fts r
            JOIN resources_fts_doc d ON d.rowid = r.rowid
            WHERE d.resource_id = :resource_id
        """),
            {"resource_id": str(resource.id)},
        ).fetchall()

        assert len(results) == 1
        assert results[0][0] == "Updated Title"
        assert results[0][1] == "Updated description"

        db.close()

    def test_migration_delete_triggers_work(self, test_db):
        """Test that delete triggers work for FTS cleanup."""
        db = test_db()

        # Mock FTS5 detection to always return True for testing
        with patch(
            "backend.app.services.search_service._detect_fts5", return_value=True
        ):
            # Check if FTS5 is available
            if not _detect_fts5(db):
                pytest.skip("FTS5 not available in this SQLite build")

        # Run the migration first
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "migration", "backend/alembic/versions/20250910_add_fts_and_triggers.py"
        )
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        migration.upgrade()

        # Create test resource
        resource = Resource(
            title="To Be Deleted",
            description="This will be deleted",
            language="en",
            type="article",
            classification_code="000",
            subject=["delete"],
            read_status="unread",
            quality_score=0.5,
        )
        db.add(resource)
        db.commit()

        resource_id = str(resource.id)

        # Delete the resource
        db.delete(resource)
        db.commit()

        # Check that FTS data was cleaned up
        conn = db.connection()
        fts_count = conn.execute(
            text("""
            SELECT COUNT(*) FROM resources_fts r
            JOIN resources_fts_doc d ON d.rowid = r.rowid
            WHERE d.resource_id = :resource_id
        """),
            {"resource_id": resource_id},
        ).scalar()

        doc_count = conn.execute(
            text("""
            SELECT COUNT(*) FROM resources_fts_doc
            WHERE resource_id = :resource_id
        """),
            {"resource_id": resource_id},
        ).scalar()

        assert fts_count == 0
        assert doc_count == 0

        db.close()
