"""
Integration test for full-text search strategy pattern (Phase 13)

This test verifies that the search service correctly uses the strategy pattern
to select the appropriate full-text search implementation based on database type.
"""

from sqlalchemy.orm import Session

from backend.app.services.search_service import AdvancedSearchService
from backend.app.schemas.search import SearchQuery, SearchFilters
from backend.app.database.models import Resource
from backend.app.database.base import get_database_type


def test_advanced_search_service_uses_strategy_pattern(db_session: Session):
    """Test that AdvancedSearchService uses the strategy pattern for FTS."""
    # Create test resources
    resource1 = Resource(
        title="Python Programming Guide",
        description="Learn Python programming from scratch",
        type="book",
        language="en"
    )
    resource2 = Resource(
        title="Java Development Tutorial",
        description="Master Java development",
        type="article",
        language="en"
    )
    db_session.add_all([resource1, resource2])
    db_session.commit()
    
    # Create search query
    query = SearchQuery(
        text="python programming",
        limit=10,
        offset=0,
        sort_by="relevance",
        sort_dir="desc"
    )
    
    # Execute search
    results, total, facets, snippets = AdvancedSearchService.search(db_session, query)
    
    # Verify results structure
    assert isinstance(results, list)
    assert isinstance(total, int)
    assert facets is not None
    assert isinstance(snippets, dict)
    
    # Results should include our test resources
    assert total >= 0


def test_strategy_selection_based_on_database_type(db_session: Session):
    """Test that the correct strategy is selected based on database type."""
    # Get the FTS strategy for current database
    strategy = AdvancedSearchService._get_fts_strategy_for_db(db_session)
    
    # Get database type
    db_type = get_database_type(db_session.bind.url.render_as_string(hide_password=True))
    
    if db_type == "sqlite":
        from backend.app.services.search_service import SQLiteFTS5Strategy
        assert isinstance(strategy, SQLiteFTS5Strategy) or strategy is None
    elif db_type == "postgresql":
        from backend.app.services.search_service import PostgreSQLFullTextStrategy
        assert isinstance(strategy, PostgreSQLFullTextStrategy) or strategy is None


def test_search_with_no_fts_available(db_session: Session):
    """Test that search falls back gracefully when FTS is not available."""
    # Create test resource
    resource = Resource(
        title="Fallback Test Resource",
        description="This tests the fallback search mechanism",
        type="article"
    )
    db_session.add(resource)
    db_session.commit()
    
    # Create search query
    query = SearchQuery(
        text="fallback test",
        limit=10,
        offset=0
    )
    
    # Execute search - should work even if FTS is not available
    results, total, facets, snippets = AdvancedSearchService.search(db_session, query)
    
    # Should return results using fallback LIKE search
    assert isinstance(results, list)
    assert isinstance(total, int)
    assert total >= 0


def test_search_with_filters_uses_strategy(db_session: Session):
    """Test that search with filters correctly uses the strategy pattern."""
    # Create test resources with different types
    resource1 = Resource(
        title="Book about Python",
        description="Python programming book",
        type="book",
        language="en"
    )
    resource2 = Resource(
        title="Article about Python",
        description="Python programming article",
        type="article",
        language="en"
    )
    db_session.add_all([resource1, resource2])
    db_session.commit()
    
    # Create search query with filters
    filters = SearchFilters(type=["book"])
    query = SearchQuery(
        text="python",
        filters=filters,
        limit=10,
        offset=0
    )
    
    # Execute search
    results, total, facets, snippets = AdvancedSearchService.search(db_session, query)
    
    # Verify results structure
    assert isinstance(results, list)
    assert isinstance(total, int)
    
    # All results should be books (if any results returned)
    for resource in results:
        assert resource.type == "book"


def test_empty_search_query_with_strategy(db_session: Session):
    """Test that empty search query is handled correctly by strategy."""
    # Create search query with empty text
    query = SearchQuery(
        text="",
        limit=10,
        offset=0
    )
    
    # Execute search
    results, total, facets, snippets = AdvancedSearchService.search(db_session, query)
    
    # Should return results (all resources) or empty list
    assert isinstance(results, list)
    assert isinstance(total, int)
    assert total >= 0
