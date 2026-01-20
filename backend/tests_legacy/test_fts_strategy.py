"""
Test full-text search strategy pattern (Phase 13)

This module tests the database-agnostic full-text search abstraction layer
that supports both SQLite FTS5 and PostgreSQL tsvector/tsquery.
"""

import pytest
from sqlalchemy.orm import Session

from backend.app.services.search_service import (
    FullTextSearchStrategy,
    SQLiteFTS5Strategy,
    PostgreSQLFullTextStrategy,
)
from backend.app.database.models import Resource
from backend.app.database.base import get_database_type
from backend.app.schemas.search import SearchFilters


def test_fts_strategy_abstract_class():
    """Test that FullTextSearchStrategy is abstract and cannot be instantiated."""
    with pytest.raises(TypeError):
        FullTextSearchStrategy(None)  # type: ignore


def test_sqlite_fts5_strategy_initialization(db_session: Session):
    """Test SQLiteFTS5Strategy can be initialized."""
    strategy = SQLiteFTS5Strategy(db_session)
    assert strategy is not None
    assert strategy.db == db_session


def test_postgresql_strategy_initialization(db_session: Session):
    """Test PostgreSQLFullTextStrategy can be initialized."""
    strategy = PostgreSQLFullTextStrategy(db_session)
    assert strategy is not None
    assert strategy.db == db_session


def test_sqlite_fts5_strategy_availability(db_session: Session):
    """Test SQLiteFTS5Strategy availability detection."""
    strategy = SQLiteFTS5Strategy(db_session)

    # Availability depends on whether FTS5 is compiled and index exists
    # This test just verifies the method runs without error
    is_available = strategy.is_available()
    assert isinstance(is_available, bool)


def test_postgresql_strategy_availability(db_session: Session):
    """Test PostgreSQLFullTextStrategy availability detection."""
    strategy = PostgreSQLFullTextStrategy(db_session)

    # Availability depends on database type and search_vector column existence
    is_available = strategy.is_available()
    assert isinstance(is_available, bool)

    # For SQLite test database, PostgreSQL strategy should not be available
    db_type = get_database_type(
        db_session.bind.url.render_as_string(hide_password=True)
    )
    if db_type == "sqlite":
        assert is_available is False


def test_strategy_search_returns_correct_structure(db_session: Session):
    """Test that strategy search methods return the correct tuple structure."""
    # Create a test resource
    resource = Resource(
        title="Test Resource for FTS",
        description="This is a test resource for full-text search testing",
        type="article",
    )
    db_session.add(resource)
    db_session.commit()

    # Try SQLite strategy
    sqlite_strategy = SQLiteFTS5Strategy(db_session)
    if sqlite_strategy.is_available():
        results, total, scores, snippets = sqlite_strategy.search(
            "test resource", filters=None, limit=10, offset=0
        )

        assert isinstance(results, list)
        assert isinstance(total, int)
        assert isinstance(scores, dict)
        assert isinstance(snippets, dict)

    # Try PostgreSQL strategy
    pg_strategy = PostgreSQLFullTextStrategy(db_session)
    if pg_strategy.is_available():
        results, total, scores, snippets = pg_strategy.search(
            "test resource", filters=None, limit=10, offset=0
        )

        assert isinstance(results, list)
        assert isinstance(total, int)
        assert isinstance(scores, dict)
        assert isinstance(snippets, dict)


def test_strategy_search_with_filters(db_session: Session):
    """Test that strategy search methods respect filters."""
    # Create test resources
    resource1 = Resource(
        title="Python Programming",
        description="Learn Python programming",
        type="book",
        language="en",
    )
    resource2 = Resource(
        title="Java Programming",
        description="Learn Java programming",
        type="article",
        language="en",
    )
    db_session.add_all([resource1, resource2])
    db_session.commit()

    # Create filters
    filters = SearchFilters(type=["book"])

    # Try with available strategy
    sqlite_strategy = SQLiteFTS5Strategy(db_session)
    if sqlite_strategy.is_available():
        results, total, scores, snippets = sqlite_strategy.search(
            "programming", filters=filters, limit=10, offset=0
        )

        # Results should only include books
        for resource in results:
            assert resource.type == "book"


def test_strategy_search_empty_query(db_session: Session):
    """Test that strategy handles empty query gracefully."""
    sqlite_strategy = SQLiteFTS5Strategy(db_session)

    if sqlite_strategy.is_available():
        results, total, scores, snippets = sqlite_strategy.search(
            "", filters=None, limit=10, offset=0
        )

        # Empty query should return empty results
        assert results == []
        assert total == 0
        assert scores == {}
        assert snippets == {}


def test_strategy_search_pagination(db_session: Session):
    """Test that strategy search respects pagination parameters."""
    # Create multiple test resources
    for i in range(5):
        resource = Resource(
            title=f"Test Resource {i}",
            description=f"Description for test resource {i}",
            type="article",
        )
        db_session.add(resource)
    db_session.commit()

    sqlite_strategy = SQLiteFTS5Strategy(db_session)
    if sqlite_strategy.is_available():
        # Get first page
        results_page1, total, _, _ = sqlite_strategy.search(
            "test resource", filters=None, limit=2, offset=0
        )

        # Get second page
        results_page2, _, _, _ = sqlite_strategy.search(
            "test resource", filters=None, limit=2, offset=2
        )

        # Pages should have different results
        assert len(results_page1) <= 2
        assert len(results_page2) <= 2

        if len(results_page1) > 0 and len(results_page2) > 0:
            page1_ids = {r.id for r in results_page1}
            page2_ids = {r.id for r in results_page2}
            assert page1_ids.isdisjoint(page2_ids)


def test_postgresql_strategy_not_available_on_sqlite(db_session: Session):
    """Test that PostgreSQL strategy correctly reports unavailable on SQLite."""
    db_type = get_database_type(
        db_session.bind.url.render_as_string(hide_password=True)
    )

    if db_type == "sqlite":
        pg_strategy = PostgreSQLFullTextStrategy(db_session)
        assert pg_strategy.is_available() is False

        # Search should return empty results when not available
        results, total, scores, snippets = pg_strategy.search(
            "test query", filters=None, limit=10, offset=0
        )

        assert results == []
        assert total == 0
        assert scores == {}
        assert snippets == {}
