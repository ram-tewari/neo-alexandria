"""
Tests for transaction isolation and concurrency handling.

This module tests the PostgreSQL-specific transaction isolation features
including READ COMMITTED isolation level, retry logic for serialization errors,
and SELECT FOR UPDATE row-level locking.
"""

import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy import select

from backend.app.database.base import (
    get_database_type,
    retry_on_serialization_error,
    with_row_lock,
    with_row_lock_sync,
    is_serialization_error,
    get_pool_status,
)
from backend.app.database.models import Resource


class TestDatabaseType:
    """Test database type detection."""

    def test_get_database_type_sqlite(self):
        """Test detection of SQLite database."""
        db_type = get_database_type("sqlite:///test.db")
        assert db_type == "sqlite"

    def test_get_database_type_postgresql(self):
        """Test detection of PostgreSQL database."""
        db_type = get_database_type("postgresql://user:pass@localhost/db")
        assert db_type == "postgresql"

    def test_get_database_type_unsupported(self):
        """Test error on unsupported database type."""
        with pytest.raises(ValueError, match="Unsupported database type"):
            get_database_type("mysql://user:pass@localhost/db")


class TestSerializationErrorDetection:
    """Test serialization error detection."""

    def test_is_serialization_error_deadlock(self):
        """Test detection of deadlock error."""
        error = OperationalError("statement", {}, Exception("deadlock detected"))
        assert is_serialization_error(error) is True

    def test_is_serialization_error_serialization_failure(self):
        """Test detection of serialization failure."""
        error = OperationalError(
            "statement", {}, Exception("could not serialize access")
        )
        assert is_serialization_error(error) is True

    def test_is_serialization_error_error_code(self):
        """Test detection by error code."""
        error = OperationalError("statement", {}, Exception("ERROR 40001"))
        assert is_serialization_error(error) is True

    def test_is_serialization_error_other_error(self):
        """Test non-serialization error."""
        error = OperationalError("statement", {}, Exception("connection refused"))
        assert is_serialization_error(error) is False


class TestRetryDecorator:
    """Test retry decorator for serialization errors."""

    @pytest.mark.anyio
    async def test_retry_decorator_success_first_try(self):
        """Test successful operation on first try."""
        call_count = 0

        @retry_on_serialization_error(max_retries=3)
        async def test_operation():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await test_operation()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.anyio
    async def test_retry_decorator_success_after_retry(self):
        """Test successful operation after retry."""
        call_count = 0

        @retry_on_serialization_error(max_retries=3)
        async def test_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise OperationalError("statement", {}, Exception("deadlock detected"))
            return "success"

        result = await test_operation()
        assert result == "success"
        assert call_count == 2

    @pytest.mark.anyio
    async def test_retry_decorator_exhausted_retries(self):
        """Test exhausted retries raises error."""
        call_count = 0

        @retry_on_serialization_error(max_retries=3)
        async def test_operation():
            nonlocal call_count
            call_count += 1
            raise OperationalError("statement", {}, Exception("deadlock detected"))

        with pytest.raises(OperationalError):
            await test_operation()

        assert call_count == 3

    @pytest.mark.anyio
    async def test_retry_decorator_non_serialization_error(self):
        """Test non-serialization error is not retried."""
        call_count = 0

        @retry_on_serialization_error(max_retries=3)
        async def test_operation():
            nonlocal call_count
            call_count += 1
            raise OperationalError("statement", {}, Exception("connection refused"))

        with pytest.raises(OperationalError):
            await test_operation()

        # Should fail immediately without retry
        assert call_count == 1

    def test_retry_decorator_sync_success(self):
        """Test synchronous retry decorator."""
        call_count = 0

        @retry_on_serialization_error(max_retries=3)
        def test_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise OperationalError("statement", {}, Exception("deadlock detected"))
            return "success"

        result = test_operation()
        assert result == "success"
        assert call_count == 2


class TestRowLocking:
    """Test row-level locking with SELECT FOR UPDATE."""

    @pytest.mark.anyio
    async def test_with_row_lock_async(self, async_db_session):
        """Test async row locking."""
        # Create a test resource
        resource = Resource(title="Test Resource", type="article")
        async_db_session.add(resource)
        await async_db_session.commit()
        await async_db_session.refresh(resource)

        # Lock the resource (no need for begin() as session already has transaction)
        locked_resource = await with_row_lock(async_db_session, Resource, resource.id)

        assert locked_resource is not None
        assert locked_resource.id == resource.id
        assert locked_resource.title == "Test Resource"

    @pytest.mark.anyio
    async def test_with_row_lock_not_found(self, async_db_session):
        """Test row locking with non-existent record."""
        import uuid

        locked_resource = await with_row_lock(async_db_session, Resource, uuid.uuid4())

        assert locked_resource is None

    @pytest.mark.anyio
    async def test_with_row_lock_invalid_mode(self, async_db_session):
        """Test row locking with invalid lock mode."""
        resource = Resource(title="Test Resource", type="article")
        async_db_session.add(resource)
        await async_db_session.commit()
        await async_db_session.refresh(resource)

        # Invalid lock mode should raise ValueError regardless of database type
        with pytest.raises(ValueError, match="Unsupported lock_mode"):
            await with_row_lock(
                async_db_session, Resource, resource.id, lock_mode="invalid"
            )

    def test_with_row_lock_sync(self, sync_db_session):
        """Test synchronous row locking."""
        # Create a test resource
        resource = Resource(title="Test Resource", type="article")
        sync_db_session.add(resource)
        sync_db_session.commit()
        sync_db_session.refresh(resource)

        # Lock the resource (no need for begin() as session already has transaction)
        locked_resource = with_row_lock_sync(sync_db_session, Resource, resource.id)

        assert locked_resource is not None
        assert locked_resource.id == resource.id
        assert locked_resource.title == "Test Resource"


class TestPoolStatus:
    """Test connection pool status reporting."""

    def test_pool_status_includes_isolation_level(self):
        """Test that pool status includes isolation level for PostgreSQL."""
        pool_status = get_pool_status()

        assert "database_type" in pool_status
        assert pool_status["database_type"] in ["sqlite", "postgresql"]

        # PostgreSQL should include isolation level
        if pool_status["database_type"] == "postgresql":
            assert "isolation_level" in pool_status
            assert pool_status["isolation_level"] == "READ COMMITTED"
            assert "statement_timeout_ms" in pool_status
            assert pool_status["statement_timeout_ms"] == 30000

    def test_pool_status_structure(self):
        """Test pool status has expected structure."""
        pool_status = get_pool_status()

        # Common fields
        assert "database_type" in pool_status
        assert "size" in pool_status
        assert "max_overflow" in pool_status
        assert "checked_in" in pool_status
        assert "checked_out" in pool_status
        assert "overflow" in pool_status
        assert "total_capacity" in pool_status
        assert "pool_usage_percent" in pool_status
        assert "connections_available" in pool_status


class TestConcurrentUpdates:
    """Test concurrent update scenarios."""

    @pytest.mark.anyio
    async def test_concurrent_updates_with_retry(self, async_db_session):
        """Test that retry decorator handles concurrent updates."""
        # Create a test resource
        resource = Resource(title="Test Resource", type="article")
        async_db_session.add(resource)
        await async_db_session.commit()
        await async_db_session.refresh(resource)

        update_count = 0

        @retry_on_serialization_error(max_retries=3)
        async def update_resource():
            nonlocal update_count
            update_count += 1

            # Simulate update operation
            stmt = select(Resource).where(Resource.id == resource.id)
            result = await async_db_session.execute(stmt)
            res = result.scalar_one()
            res.title = f"Updated {update_count}"
            await async_db_session.commit()
            return res

        # Execute update
        updated = await update_resource()
        assert updated.title == "Updated 1"
        assert update_count == 1
