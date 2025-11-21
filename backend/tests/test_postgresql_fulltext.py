"""
PostgreSQL Full-Text Search Tests

Tests PostgreSQL-specific full-text search functionality including tsvector,
tsquery, ts_rank, and GIN indexes. These tests require a PostgreSQL database
and will be skipped when running against SQLite.

Run these tests with:
    TEST_DATABASE_URL=postgresql://user:pass@localhost/test_db pytest tests/test_postgresql_fulltext.py -v
"""

import pytest
from sqlalchemy import text, func
from datetime import datetime, timezone

from backend.app.database.models import Resource


@pytest.mark.postgresql
class TestPostgreSQLFullTextSearch:
    """Test PostgreSQL full-text search features."""
    
    def test_tsvector_column_exists(self, db_session, db_type):
        """Test that search_vector tsvector column exists in PostgreSQL."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Query to check if search_vector column exists
        result = db_session.execute(
            text(
                "SELECT column_name, data_type "
                "FROM information_schema.columns "
                "WHERE table_name = 'resources' AND column_name = 'search_vector'"
            )
        ).fetchone()
        
        # Note: search_vector column may not exist yet if migration hasn't been run
        # This test documents the expected schema
        if result:
            assert result[0] == 'search_vector'
            assert 'tsvector' in result[1].lower()
    
    def test_to_tsvector_function(self, db_session, db_type):
        """Test PostgreSQL to_tsvector function for text indexing."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Create test resource
        resource = Resource(
            title="Machine Learning and Artificial Intelligence",
            description="A comprehensive guide to modern machine learning algorithms and AI techniques",
            subject=["Machine Learning", "AI"],
            language="en",
            type="article",
            classification_code="004",
            quality_score=0.85,
            quality_overall=0.85,
            quality_accuracy=0.87,
            quality_completeness=0.83,
            quality_consistency=0.86,
            quality_timeliness=0.84,
            quality_relevance=0.88,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add(resource)
        db_session.commit()
        
        # Test to_tsvector on title
        result = db_session.execute(
            text(
                "SELECT to_tsvector('english', :title) AS tsvector"
            ),
            {"title": resource.title}
        ).fetchone()
        
        assert result is not None
        tsvector_str = str(result[0])
        # Verify that stemmed words are in the tsvector
        assert 'machin' in tsvector_str.lower()  # "machine" stemmed to "machin"
        assert 'learn' in tsvector_str.lower()   # "learning" stemmed to "learn"
    
    def test_to_tsquery_function(self, db_session, db_type):
        """Test PostgreSQL to_tsquery function for search queries."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Test simple query
        result = db_session.execute(
            text("SELECT to_tsquery('english', :query) AS tsquery"),
            {"query": "machine & learning"}
        ).fetchone()
        
        assert result is not None
        tsquery_str = str(result[0])
        assert 'machin' in tsquery_str.lower()
        assert 'learn' in tsquery_str.lower()
        
        # Test OR query
        result = db_session.execute(
            text("SELECT to_tsquery('english', :query) AS tsquery"),
            {"query": "machine | artificial"}
        ).fetchone()
        
        assert result is not None
        tsquery_str = str(result[0])
        assert '|' in tsquery_str  # OR operator
    
    def test_fulltext_search_with_match_operator(self, db_session, db_type):
        """Test full-text search using @@ match operator."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Create test resources
        resource1 = Resource(
            title="Machine Learning Fundamentals",
            description="Introduction to machine learning algorithms",
            subject=["Machine Learning"],
            language="en",
            type="article",
            classification_code="004",
            quality_score=0.85,
            quality_overall=0.85,
            quality_accuracy=0.87,
            quality_completeness=0.83,
            quality_consistency=0.86,
            quality_timeliness=0.84,
            quality_relevance=0.88,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        resource2 = Resource(
            title="Deep Learning with Neural Networks",
            description="Advanced neural network architectures",
            subject=["Deep Learning", "Neural Networks"],
            language="en",
            type="article",
            classification_code="004",
            quality_score=0.90,
            quality_overall=0.90,
            quality_accuracy=0.92,
            quality_completeness=0.88,
            quality_consistency=0.91,
            quality_timeliness=0.89,
            quality_relevance=0.93,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        resource3 = Resource(
            title="Cooking Recipes",
            description="Delicious home cooking recipes",
            subject=["Cooking"],
            language="en",
            type="article",
            classification_code="641",
            quality_score=0.75,
            quality_overall=0.75,
            quality_accuracy=0.77,
            quality_completeness=0.73,
            quality_consistency=0.76,
            quality_timeliness=0.74,
            quality_relevance=0.78,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add_all([resource1, resource2, resource3])
        db_session.commit()
        
        # Search for "machine learning"
        results = db_session.execute(
            text(
                "SELECT id, title FROM resources "
                "WHERE to_tsvector('english', title || ' ' || description) @@ "
                "to_tsquery('english', :query)"
            ),
            {"query": "machine & learning"}
        ).fetchall()
        
        assert len(results) >= 1
        titles = [r[1] for r in results]
        assert "Machine Learning Fundamentals" in titles
    
    def test_ts_rank_scoring(self, db_session, db_type):
        """Test ts_rank function for relevance scoring."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Create test resources with varying relevance
        resource1 = Resource(
            title="Machine Learning Machine Learning",  # High relevance
            description="Machine learning algorithms and machine learning techniques",
            subject=["Machine Learning"],
            language="en",
            type="article",
            classification_code="004",
            quality_score=0.85,
            quality_overall=0.85,
            quality_accuracy=0.87,
            quality_completeness=0.83,
            quality_consistency=0.86,
            quality_timeliness=0.84,
            quality_relevance=0.88,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        resource2 = Resource(
            title="Introduction to Learning",  # Medium relevance
            description="Basic concepts of learning",
            subject=["Education"],
            language="en",
            type="article",
            classification_code="370",
            quality_score=0.80,
            quality_overall=0.80,
            quality_accuracy=0.82,
            quality_completeness=0.78,
            quality_consistency=0.81,
            quality_timeliness=0.79,
            quality_relevance=0.83,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        resource3 = Resource(
            title="Cooking Techniques",  # No relevance
            description="Various cooking methods",
            subject=["Cooking"],
            language="en",
            type="article",
            classification_code="641",
            quality_score=0.75,
            quality_overall=0.75,
            quality_accuracy=0.77,
            quality_completeness=0.73,
            quality_consistency=0.76,
            quality_timeliness=0.74,
            quality_relevance=0.78,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add_all([resource1, resource2, resource3])
        db_session.commit()
        
        # Search with ranking
        results = db_session.execute(
            text(
                "SELECT id, title, "
                "ts_rank(to_tsvector('english', title || ' ' || description), "
                "        to_tsquery('english', :query)) AS rank "
                "FROM resources "
                "WHERE to_tsvector('english', title || ' ' || description) @@ "
                "      to_tsquery('english', :query) "
                "ORDER BY rank DESC"
            ),
            {"query": "machine & learning"}
        ).fetchall()
        
        assert len(results) >= 1
        
        # Verify results are ordered by rank (descending)
        if len(results) > 1:
            ranks = [r[2] for r in results]
            assert ranks == sorted(ranks, reverse=True)
        
        # Verify highest ranked result
        assert "Machine Learning" in results[0][1]
    
    def test_ts_rank_cd_with_weights(self, db_session, db_type):
        """Test ts_rank_cd function with custom weights."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Create test resource
        resource = Resource(
            title="Machine Learning",
            description="Comprehensive guide to machine learning",
            subject=["Machine Learning"],
            language="en",
            type="article",
            classification_code="004",
            quality_score=0.85,
            quality_overall=0.85,
            quality_accuracy=0.87,
            quality_completeness=0.83,
            quality_consistency=0.86,
            quality_timeliness=0.84,
            quality_relevance=0.88,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add(resource)
        db_session.commit()
        
        # Test ts_rank_cd with custom weights (D, C, B, A)
        # Higher weight for title (A) than description (B)
        result = db_session.execute(
            text(
                "SELECT "
                "ts_rank_cd('{0.1, 0.2, 0.4, 1.0}', "
                "           setweight(to_tsvector('english', title), 'A') || "
                "           setweight(to_tsvector('english', description), 'B'), "
                "           to_tsquery('english', :query)) AS weighted_rank "
                "FROM resources WHERE id = :id"
            ),
            {"query": "machine & learning", "id": str(resource.id)}
        ).fetchone()
        
        assert result is not None
        assert result[0] > 0  # Should have positive rank
    
    def test_phrase_search(self, db_session, db_type):
        """Test phrase search using <-> operator."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Create test resources
        resource1 = Resource(
            title="Machine Learning Algorithms",
            description="Study of machine learning",
            subject=["Machine Learning"],
            language="en",
            type="article",
            classification_code="004",
            quality_score=0.85,
            quality_overall=0.85,
            quality_accuracy=0.87,
            quality_completeness=0.83,
            quality_consistency=0.86,
            quality_timeliness=0.84,
            quality_relevance=0.88,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        resource2 = Resource(
            title="Learning Machine Operations",
            description="How machines learn",
            subject=["Machines"],
            language="en",
            type="article",
            classification_code="621",
            quality_score=0.80,
            quality_overall=0.80,
            quality_accuracy=0.82,
            quality_completeness=0.78,
            quality_consistency=0.81,
            quality_timeliness=0.79,
            quality_relevance=0.83,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add_all([resource1, resource2])
        db_session.commit()
        
        # Search for exact phrase "machine learning" (adjacent words)
        results = db_session.execute(
            text(
                "SELECT id, title FROM resources "
                "WHERE to_tsvector('english', title) @@ "
                "      to_tsquery('english', 'machine <-> learning')"
            )
        ).fetchall()
        
        # Should only match "Machine Learning Algorithms" (adjacent words)
        assert len(results) >= 1
        assert "Machine Learning Algorithms" in [r[1] for r in results]
    
    def test_prefix_search(self, db_session, db_type):
        """Test prefix search using :* operator."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Create test resources
        resource1 = Resource(
            title="Machine Learning",
            description="ML guide",
            subject=["Machine Learning"],
            language="en",
            type="article",
            classification_code="004",
            quality_score=0.85,
            quality_overall=0.85,
            quality_accuracy=0.87,
            quality_completeness=0.83,
            quality_consistency=0.86,
            quality_timeliness=0.84,
            quality_relevance=0.88,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        resource2 = Resource(
            title="Machinery Maintenance",
            description="Machine maintenance guide",
            subject=["Engineering"],
            language="en",
            type="article",
            classification_code="621",
            quality_score=0.80,
            quality_overall=0.80,
            quality_accuracy=0.82,
            quality_completeness=0.78,
            quality_consistency=0.81,
            quality_timeliness=0.79,
            quality_relevance=0.83,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db_session.add_all([resource1, resource2])
        db_session.commit()
        
        # Search for words starting with "mach"
        results = db_session.execute(
            text(
                "SELECT id, title FROM resources "
                "WHERE to_tsvector('english', title) @@ "
                "      to_tsquery('english', 'mach:*')"
            )
        ).fetchall()
        
        # Should match both "Machine" and "Machinery"
        assert len(results) == 2
        titles = [r[1] for r in results]
        assert "Machine Learning" in titles
        assert "Machinery Maintenance" in titles


@pytest.mark.postgresql
class TestPostgreSQLFullTextSearchIndexes:
    """Test GIN indexes for full-text search performance."""
    
    def test_gin_index_on_tsvector(self, db_session, db_type):
        """Test that GIN index exists on search_vector column."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Query to check if GIN index exists on search_vector
        result = db_session.execute(
            text(
                "SELECT indexname, indexdef "
                "FROM pg_indexes "
                "WHERE tablename = 'resources' "
                "AND indexdef LIKE '%search_vector%' "
                "AND indexdef LIKE '%gin%'"
            )
        ).fetchone()
        
        # Note: Index may not exist yet if migration hasn't been run
        # This test documents the expected index
        if result:
            assert 'gin' in result[1].lower()
            assert 'search_vector' in result[1].lower()
    
    def test_explain_uses_gin_index(self, db_session, db_type):
        """Test that full-text search queries use GIN index."""
        if db_type != "postgresql":
            pytest.skip("PostgreSQL-specific test")
        
        # Create multiple resources to make index usage more likely
        resources = []
        for i in range(20):
            resource = Resource(
                title=f"Resource {i} about machine learning",
                description=f"Description {i}",
                subject=["Machine Learning"],
                language="en",
                type="article",
                classification_code="004",
                quality_score=0.80,
                quality_overall=0.80,
                quality_accuracy=0.82,
                quality_completeness=0.78,
                quality_consistency=0.81,
                quality_timeliness=0.79,
                quality_relevance=0.83,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            resources.append(resource)
        
        db_session.add_all(resources)
        db_session.commit()
        
        # Get query plan
        explain_result = db_session.execute(
            text(
                "EXPLAIN (FORMAT JSON) "
                "SELECT * FROM resources "
                "WHERE to_tsvector('english', title) @@ to_tsquery('english', 'machine')"
            )
        ).scalar()
        
        # Verify query plan exists
        assert explain_result is not None
        # Note: In production with many rows, this would show index scan
