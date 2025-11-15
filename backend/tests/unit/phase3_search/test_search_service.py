"""Tests for the enhanced search service with FTS5 functionality."""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from backend.app.database.models import Resource
from backend.app.services.search_service import AdvancedSearchService
from backend.app.schemas.search import SearchQuery, SearchFilters


@pytest.fixture
def sample_resources(test_db):
    """Create sample resources for testing."""
    db = test_db()
    now = datetime.now(timezone.utc)
    
    resources = [
        Resource(
            title="Introduction to Machine Learning",
            description="A comprehensive guide to ML algorithms and AI techniques",
            language="en",
            type="article",
            classification_code="006",
            subject=["Machine Learning", "Artificial Intelligence"],
            read_status="unread",
            quality_score=0.8,
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=5),
        ),
        Resource(
            title="Deep Learning with Python",
            description="Neural networks and deep learning frameworks",
            language="en",
            type="book",
            classification_code="006",
            subject=["Deep Learning", "Python", "Neural Networks"],
            read_status="in_progress",
            quality_score=0.9,
            created_at=now - timedelta(days=20),
            updated_at=now - timedelta(days=2),
        ),
        Resource(
            title="Spanish Linguistics Overview",
            description="Morphology and syntax in Spanish language",
            language="es",
            type="book",
            classification_code="400",
            subject=["Language", "Linguistics", "Spanish"],
            read_status="completed",
            quality_score=0.6,
            created_at=now - timedelta(days=40),
            updated_at=now - timedelta(days=30),
        ),
        Resource(
            title="Natural Language Processing Basics",
            description="Text processing, tokenization, and NLP techniques",
            language="en",
            type="article",
            classification_code="006",
            subject=["Natural Language Processing", "Machine Learning"],
            read_status="unread",
            quality_score=0.7,
            created_at=now - timedelta(days=15),
            updated_at=now - timedelta(days=1),
        ),
    ]
    
    for resource in resources:
        db.add(resource)
    db.commit()
    
    resource_ids = [str(r.id) for r in resources]
    db.close()
    return resource_ids


class TestQueryParsing:
    """Test the query parsing functionality."""
    
    def test_simple_query(self):
        """Test parsing of simple queries."""
        result = AdvancedSearchService.parse_search_query("machine learning")
        assert result == "machine AND learning"
    
    def test_quoted_phrases(self):
        """Test parsing of quoted phrases."""
        result = AdvancedSearchService.parse_search_query('"machine learning"')
        assert result == '"machine learning"'
    
    def test_boolean_operators(self):
        """Test parsing of boolean operators."""
        result = AdvancedSearchService.parse_search_query("AI AND python OR javascript")
        assert result == "AI AND python OR javascript"
    
    def test_field_specific_queries(self):
        """Test field-specific queries."""
        result = AdvancedSearchService.parse_search_query("title:python description:tutorial")
        assert result == "title:python AND description:tutorial"
    
    def test_wildcard_queries(self):
        """Test wildcard queries."""
        result = AdvancedSearchService.parse_search_query("program*")
        assert result == "program*"
    
    def test_complex_query(self):
        """Test complex query with multiple features."""
        result = AdvancedSearchService.parse_search_query('title:"deep learning" AND (python OR tensorflow)')
        # Should preserve structure but normalize operators
        assert "title:\"deep learning\"" in result
        assert "AND" in result
        assert "python" in result
        assert "OR" in result
        assert "tensorflow" in result
    
    def test_empty_query(self):
        """Test empty query handling."""
        result = AdvancedSearchService.parse_search_query("")
        assert result == ""
    
    def test_special_characters(self):
        """Test handling of special characters."""
        result = AdvancedSearchService.parse_search_query("C++ programming")
        assert "C++" in result
        assert "programming" in result


class TestSnippetGeneration:
    """Test snippet generation functionality."""
    
    def test_basic_snippet(self):
        """Test basic snippet generation."""
        text = "This is a comprehensive guide to machine learning algorithms and artificial intelligence techniques."
        query = "machine learning"
        snippet = AdvancedSearchService.generate_snippets(text, query)
        
        # Should contain either "machine" or "learning" (the algorithm picks first token)
        assert "machine" in snippet.lower() or "learning" in snippet.lower()
        assert "<mark>" in snippet
        assert "</mark>" in snippet
    
    def test_snippet_with_context(self):
        """Test snippet generation with surrounding context."""
        text = "In this chapter, we will explore various machine learning algorithms including supervised and unsupervised learning methods."
        query = "algorithms"
        snippet = AdvancedSearchService.generate_snippets(text, query)
        
        assert "algorithms" in snippet.lower()
        assert len(snippet) > len("algorithms")
    
    def test_snippet_truncation(self):
        """Test snippet truncation for long text."""
        text = "A" * 500 + " machine learning " + "B" * 500
        query = "machine learning"
        snippet = AdvancedSearchService.generate_snippets(text, query)
        
        assert len(snippet) < len(text)
        # Should contain either "machine" or "learning" (the algorithm picks first token)
        assert "machine" in snippet.lower() or "learning" in snippet.lower()
    
    def test_empty_text(self):
        """Test snippet generation with empty text."""
        snippet = AdvancedSearchService.generate_snippets("", "test")
        assert snippet == ""
    
    def test_empty_query(self):
        """Test snippet generation with empty query."""
        text = "This is some sample text for testing."
        snippet = AdvancedSearchService.generate_snippets(text, "")
        assert len(snippet) <= 200
        assert "…" in snippet or len(snippet) == len(text)


class TestRanking:
    """Test the ranking algorithm."""
    
    def test_ranking_with_quality_boost(self):
        """Test ranking considers quality score."""
        # Create mock resources with different quality scores
        high_quality = Resource(
            id="1",
            title="High Quality Resource",
            quality_score=0.9,
            updated_at=datetime.now(timezone.utc),
            classification_code="006"
        )
        low_quality = Resource(
            id="2", 
            title="Low Quality Resource",
            quality_score=0.3,
            updated_at=datetime.now(timezone.utc),
            classification_code="006"
        )
        
        bm25_map = {"1": 1.0, "2": 1.0}  # Same BM25 score
        ranked = AdvancedSearchService.rank_results([low_quality, high_quality], bm25_map, None)
        
        # High quality should rank higher
        assert ranked[0].id == "1"
        assert ranked[1].id == "2"
    
    def test_ranking_with_recency_boost(self):
        """Test ranking considers recency."""
        now = datetime.now(timezone.utc)
        recent = Resource(
            id="1",
            title="Recent Resource",
            quality_score=0.5,
            updated_at=now - timedelta(days=1),
            classification_code="006"
        )
        old = Resource(
            id="2",
            title="Old Resource", 
            quality_score=0.5,
            updated_at=now - timedelta(days=200),
            classification_code="006"
        )
        
        bm25_map = {"1": 1.0, "2": 1.0}
        ranked = AdvancedSearchService.rank_results([old, recent], bm25_map, None)
        
        # Recent should rank higher
        assert ranked[0].id == "1"
        assert ranked[1].id == "2"
    
    def test_ranking_with_classification_boost(self):
        """Test ranking considers classification relevance."""
        target_resource = Resource(
            id="1",
            title="Target Resource",
            quality_score=0.5,
            updated_at=datetime.now(timezone.utc),
            classification_code="006"
        )
        other_resource = Resource(
            id="2",
            title="Other Resource",
            quality_score=0.5,
            updated_at=datetime.now(timezone.utc),
            classification_code="400"
        )
        
        bm25_map = {"1": 1.0, "2": 1.0}
        filters = SearchFilters(classification_code=["006"])
        ranked = AdvancedSearchService.rank_results([other_resource, target_resource], bm25_map, filters)
        
        # Target classification should rank higher
        assert ranked[0].id == "1"
        assert ranked[1].id == "2"


class TestFtsSearch:
    """Test FTS search functionality."""
    
    @patch('backend.app.services.search_service._detect_fts5')
    @patch('backend.app.services.search_service._fts_index_ready')
    def test_fts_search_fallback(self, mock_fts_ready, mock_detect_fts, test_db, sample_resources):
        """Test fallback to LIKE search when FTS5 is not available."""
        mock_detect_fts.return_value = False
        mock_fts_ready.return_value = False
        
        db = test_db()
        query = SearchQuery(text="machine learning", limit=10)
        
        result = AdvancedSearchService.search(db, query)
        items, total, facets, snippets = result
        
        # Should return results using LIKE search
        assert total >= 0
        assert isinstance(items, list)
        assert isinstance(snippets, dict)
        db.close()
    
    @patch('backend.app.services.search_service._detect_fts5')
    @patch('backend.app.services.search_service._fts_index_ready')
    def test_fts_search_with_mock_connection(self, mock_fts_ready, mock_detect_fts, test_db, sample_resources):
        """Test FTS search with mocked database connection."""
        mock_detect_fts.return_value = True
        mock_fts_ready.return_value = True
        
        db = test_db()
        
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        # Mock FTS query results
        mock_cursor.fetchall.return_value = [
            ("resource_id_1", 1.0),
            ("resource_id_2", 2.0)
        ]
        mock_cursor.scalar.return_value = 2
        
        mock_conn.execute.return_value = mock_cursor
        mock_conn.exec_driver_sql.return_value = mock_cursor
        
        with patch.object(db, 'connection', return_value=mock_conn):
            with patch.object(db, 'query') as mock_query:
                # Mock the ORM query chain
                mock_query_result = MagicMock()
                mock_query_result.filter.return_value = mock_query_result
                mock_query_result.all.return_value = []
                mock_query.return_value = mock_query_result
                
                query = SearchQuery(text="machine learning", limit=10)
                result = AdvancedSearchService.search(db, query)
                
                # Should return 4-tuple with snippets
                assert len(result) == 4
                items, total, facets, snippets = result
                assert isinstance(snippets, dict)
        
        db.close()


class TestSearchIntegration:
    """Test integrated search functionality."""
    
    def test_search_with_filters(self, test_db, sample_resources):
        """Test search with various filters."""
        db = test_db()
        
        filters = SearchFilters(
            classification_code=["006"],
            language=["en"],
            min_quality=0.7
        )
        query = SearchQuery(text="learning", filters=filters, limit=10)
        
        result = AdvancedSearchService.search(db, query)
        items, total, facets, snippets = result
        
        # All results should meet filter criteria
        for item in items:
            assert item.classification_code == "006"
            assert item.language == "en"
            assert item.quality_score >= 0.7
        
        db.close()
    
    def test_search_without_text(self, test_db, sample_resources):
        """Test search without text query (structured search only)."""
        db = test_db()
        
        filters = SearchFilters(type=["article"])
        query = SearchQuery(filters=filters, limit=10)
        
        result = AdvancedSearchService.search(db, query)
        items, total, facets, snippets = result
        
        # Should return all articles
        for item in items:
            assert item.type == "article"
        
        db.close()
    
    def test_search_pagination(self, test_db, sample_resources):
        """Test search pagination."""
        db = test_db()
        
        query = SearchQuery(limit=2, offset=0)
        result1 = AdvancedSearchService.search(db, query)
        items1, total1, facets1, snippets1 = result1
        
        query.offset = 2
        result2 = AdvancedSearchService.search(db, query)
        items2, total2, facets2, snippets2 = result2
        
        # Should have different results
        ids1 = {item.id for item in items1}
        ids2 = {item.id for item in items2}
        assert ids1.isdisjoint(ids2)
        
        db.close()
    
    def test_search_sorting(self, test_db, sample_resources):
        """Test search sorting options."""
        db = test_db()
        
        # Test sorting by quality score
        query = SearchQuery(sort_by="quality_score", sort_dir="desc", limit=10)
        result = AdvancedSearchService.search(db, query)
        items, total, facets, snippets = result
        
        # Should be sorted by quality score descending
        for i in range(len(items) - 1):
            assert items[i].quality_score >= items[i + 1].quality_score
        
        db.close()


class TestFacets:
    """Test facet computation."""
    
    def test_facets_computation(self, test_db, sample_resources):
        """Test that facets are computed correctly."""
        db = test_db()
        
        query = SearchQuery(limit=10)
        result = AdvancedSearchService.search(db, query)
        items, total, facets, snippets = result
        
        # Check that all expected facet types are present
        assert hasattr(facets, 'classification_code')
        assert hasattr(facets, 'type')
        assert hasattr(facets, 'language')
        assert hasattr(facets, 'read_status')
        assert hasattr(facets, 'subject')
        
        # Check that facets contain expected values
        classification_codes = [bucket.key for bucket in facets.classification_code]
        assert "006" in classification_codes
        assert "400" in classification_codes
        
        db.close()
    
    def test_facets_with_filters(self, test_db, sample_resources):
        """Test facets respect applied filters."""
        db = test_db()
        
        filters = SearchFilters(language=["en"])
        query = SearchQuery(filters=filters, limit=10)
        result = AdvancedSearchService.search(db, query)
        items, total, facets, snippets = result
        
        # Language facet should only show English
        languages = [bucket.key for bucket in facets.language]
        assert "en" in languages
        assert "es" not in languages
        
        db.close()


class TestThreeWayHybridSearch:
    """Test three-way hybrid search functionality (Phase 8)."""
    
    def test_three_way_hybrid_search_basic(self, test_db, sample_resources):
        """Test basic three-way hybrid search functionality."""
        db = test_db()
        
        query = SearchQuery(
            text="machine learning",
            limit=10,
            offset=0
        )
        
        # Call three-way hybrid search
        result = AdvancedSearchService.search_three_way_hybrid(
            db=db,
            query=query,
            enable_reranking=False,
            adaptive_weighting=True
        )
        
        # Unpack results (5-tuple with metadata)
        resources, total, facets, snippets, metadata = result
        
        # Check that we got results
        assert isinstance(resources, list)
        assert isinstance(total, int)
        assert isinstance(metadata, dict)
        
        # Check metadata structure
        assert 'latency_ms' in metadata
        assert 'method_contributions' in metadata
        assert 'weights_used' in metadata
        
        # Check method contributions
        assert 'fts5' in metadata['method_contributions']
        assert 'dense' in metadata['method_contributions']
        assert 'sparse' in metadata['method_contributions']
        
        # Check weights are normalized (sum to ~1.0)
        weights = metadata['weights_used']
        assert len(weights) == 3
        assert abs(sum(weights) - 1.0) < 0.01  # Allow small floating point error
        
        db.close()
    
    def test_query_analysis_short(self):
        """Test query analysis for short queries."""
        analysis = AdvancedSearchService._analyze_query("ML AI")
        
        assert analysis['word_count'] == 2
        assert analysis['is_short'] is True
        assert analysis['is_long'] is False
        assert analysis['is_question'] is False
        assert analysis['is_technical'] is False
    
    def test_query_analysis_long(self):
        """Test query analysis for long queries."""
        query = "How does gradient descent work in deep neural networks for optimization and training"
        analysis = AdvancedSearchService._analyze_query(query)
        
        assert analysis['word_count'] > 10
        assert analysis['is_short'] is False
        assert analysis['is_long'] is True
        assert analysis['is_question'] is True
        assert analysis['is_technical'] is False
    
    def test_query_analysis_technical_code(self):
        """Test query analysis for technical code queries."""
        query = "def fibonacci(n): return n if n <= 1"
        analysis = AdvancedSearchService._analyze_query(query)
        
        assert analysis['is_technical'] is True
    
    def test_query_analysis_technical_math(self):
        """Test query analysis for technical math queries."""
        query = "integral of x^2 + 5x"
        analysis = AdvancedSearchService._analyze_query(query)
        
        assert analysis['is_technical'] is True
    
    def test_three_way_hybrid_with_empty_query(self, test_db):
        """Test three-way hybrid search with empty query."""
        db = test_db()
        
        query = SearchQuery(
            text="",
            limit=10
        )
        
        result = AdvancedSearchService.search_three_way_hybrid(
            db=db,
            query=query,
            enable_reranking=False,
            adaptive_weighting=True
        )
        
        resources, total, facets, snippets, metadata = result
        
        # Should return empty results gracefully
        assert isinstance(resources, list)
        assert isinstance(metadata, dict)
        
        db.close()
    
    def test_three_way_hybrid_fallback(self, test_db, sample_resources):
        """Test that three-way hybrid falls back gracefully when services unavailable."""
        db = test_db()
        
        query = SearchQuery(
            text="machine learning",
            limit=10
        )
        
        # The search should work even if Phase 8 services are not fully available
        # (it will fall back to two-way hybrid)
        result = AdvancedSearchService.search_three_way_hybrid(
            db=db,
            query=query,
            enable_reranking=False,
            adaptive_weighting=True
        )
        
        resources, total, facets, snippets, metadata = result
        
        # Should return results (either three-way or fallback)
        assert isinstance(resources, list)
        assert isinstance(metadata, dict)
        assert 'latency_ms' in metadata
        
        db.close()
    
    def test_fetch_resources_ordered(self, test_db, sample_resources):
        """Test that _fetch_resources_ordered preserves order."""
        db = test_db()
        
        # Get resource IDs in specific order
        resource_ids = sample_resources[:3]
        reversed_ids = list(reversed(resource_ids))
        
        # Fetch in reversed order
        resources = AdvancedSearchService._fetch_resources_ordered(
            db=db,
            resource_ids=reversed_ids,
            filters=None
        )
        
        # Check that order is preserved
        fetched_ids = [str(r.id) for r in resources]
        assert fetched_ids == reversed_ids
        
        db.close()
    
    def test_search_sparse_empty_query(self, test_db):
        """Test sparse search with empty query."""
        db = test_db()
        
        results = AdvancedSearchService._search_sparse(
            db=db,
            query="",
            limit=100
        )
        
        # Should return empty list gracefully
        assert results == []
        
        db.close()
