"""
Tests for search domain objects.

This module tests the SearchQuery, SearchResult, and SearchResults
domain objects, verifying validation, business logic, and API compatibility.
"""

import pytest
from backend.app.domain.search import (
    SearchQuery,
    SearchResult,
    SearchResults,
)


class TestSearchQuery:
    """Tests for SearchQuery value object."""

    def test_create_valid_query_defaults(self):
        """Test creating a valid query with default parameters."""
        query = SearchQuery(query_text="machine learning")

        assert query.query_text == "machine learning"
        assert query.limit == 20
        assert query.enable_reranking is True
        assert query.adaptive_weights is True
        assert query.search_method == "hybrid"

    def test_create_valid_query_custom_params(self):
        """Test creating a valid query with custom parameters."""
        query = SearchQuery(
            query_text="neural networks",
            limit=50,
            enable_reranking=False,
            adaptive_weights=False,
            search_method="dense",
        )

        assert query.query_text == "neural networks"
        assert query.limit == 50
        assert query.enable_reranking is False
        assert query.adaptive_weights is False
        assert query.search_method == "dense"

    def test_query_text_allows_empty(self):
        """Test that empty query_text is allowed for filter-based searches."""
        query = SearchQuery(query_text="")
        assert query.query_text == ""

    def test_query_text_allows_whitespace(self):
        """Test that whitespace-only query_text is allowed for filter-based searches."""
        query = SearchQuery(query_text="   ")
        assert query.query_text == "   "

    def test_limit_validation_zero(self):
        """Test that limit of 0 raises ValueError."""
        with pytest.raises(ValueError, match="limit must be positive"):
            SearchQuery(query_text="test", limit=0)

    def test_limit_validation_negative(self):
        """Test that negative limit raises ValueError."""
        with pytest.raises(ValueError, match="limit must be positive"):
            SearchQuery(query_text="test", limit=-5)

    def test_search_method_validation_invalid(self):
        """Test that invalid search_method raises ValueError."""
        with pytest.raises(ValueError, match="search_method must be one of"):
            SearchQuery(query_text="test", search_method="invalid_method")

    def test_search_method_validation_valid_methods(self):
        """Test that all valid search methods are accepted."""
        valid_methods = ["hybrid", "fts5", "dense", "sparse", "three_way"]

        for method in valid_methods:
            query = SearchQuery(query_text="test", search_method=method)
            assert query.search_method == method

    def test_is_short_query_default_threshold(self):
        """Test is_short_query with default threshold (3 words)."""
        short_query = SearchQuery(query_text="machine learning")
        long_query = SearchQuery(query_text="deep learning neural networks")

        assert short_query.is_short_query() is True
        assert long_query.is_short_query() is False

    def test_is_short_query_custom_threshold(self):
        """Test is_short_query with custom threshold."""
        query = SearchQuery(query_text="machine learning algorithms")

        assert query.is_short_query(threshold=2) is False
        assert query.is_short_query(threshold=3) is True
        assert query.is_short_query(threshold=5) is True

    def test_is_long_query_default_threshold(self):
        """Test is_long_query with default threshold (10 words)."""
        short_query = SearchQuery(query_text="machine learning")
        long_query = SearchQuery(
            query_text="deep learning neural networks for natural language processing and computer vision applications"
        )

        assert short_query.is_long_query() is False
        assert long_query.is_long_query() is True

    def test_is_long_query_custom_threshold(self):
        """Test is_long_query with custom threshold."""
        query = SearchQuery(query_text="machine learning algorithms for classification")

        assert query.is_long_query(threshold=3) is True
        assert query.is_long_query(threshold=10) is False

    def test_is_medium_query_default_thresholds(self):
        """Test is_medium_query with default thresholds."""
        short_query = SearchQuery(query_text="AI")
        medium_query = SearchQuery(
            query_text="machine learning algorithms for classification"
        )
        long_query = SearchQuery(
            query_text="deep learning neural networks for natural language processing and computer vision applications"
        )

        assert short_query.is_medium_query() is False
        assert medium_query.is_medium_query() is True
        assert long_query.is_medium_query() is False

    def test_is_medium_query_custom_thresholds(self):
        """Test is_medium_query with custom thresholds."""
        query = SearchQuery(query_text="machine learning algorithms")

        assert query.is_medium_query(short_threshold=2, long_threshold=5) is True
        assert query.is_medium_query(short_threshold=3, long_threshold=5) is False

    def test_get_word_count(self):
        """Test get_word_count returns correct count."""
        query1 = SearchQuery(query_text="AI")
        query2 = SearchQuery(query_text="machine learning")
        query3 = SearchQuery(query_text="deep learning neural networks")

        assert query1.get_word_count() == 1
        assert query2.get_word_count() == 2
        assert query3.get_word_count() == 4

    def test_is_single_word(self):
        """Test is_single_word identifies single-word queries."""
        single = SearchQuery(query_text="AI")
        multiple = SearchQuery(query_text="machine learning")

        assert single.is_single_word() is True
        assert multiple.is_single_word() is False

    def test_get_query_length(self):
        """Test get_query_length returns character count."""
        query = SearchQuery(query_text="machine learning")

        assert query.get_query_length() == len("machine learning")

    def test_to_dict(self):
        """Test conversion to dictionary."""
        query = SearchQuery(
            query_text="test query",
            limit=30,
            enable_reranking=False,
            adaptive_weights=True,
            search_method="dense",
        )

        result = query.to_dict()

        assert result == {
            "query_text": "test query",
            "limit": 30,
            "enable_reranking": False,
            "adaptive_weights": True,
            "search_method": "dense",
        }

    def test_equality(self):
        """Test equality comparison."""
        query1 = SearchQuery(query_text="test", limit=20)
        query2 = SearchQuery(query_text="test", limit=20)
        query3 = SearchQuery(query_text="different", limit=20)

        assert query1 == query2
        assert query1 != query3


class TestSearchResult:
    """Tests for SearchResult value object."""

    def test_create_valid_result_defaults(self):
        """Test creating a valid result with default parameters."""
        result = SearchResult(resource_id="res_123", score=0.95, rank=1)

        assert result.resource_id == "res_123"
        assert result.score == 0.95
        assert result.rank == 1
        assert result.title == ""
        assert result.search_method == "unknown"
        assert result.metadata == {}

    def test_create_valid_result_with_optional_fields(self):
        """Test creating a valid result with optional fields."""
        metadata = {"source": "dense_search", "distance": 0.05}
        result = SearchResult(
            resource_id="res_123",
            score=0.95,
            rank=1,
            title="Machine Learning Paper",
            search_method="dense",
            metadata=metadata,
        )

        assert result.title == "Machine Learning Paper"
        assert result.search_method == "dense"
        assert result.metadata == metadata

    def test_resource_id_validation_empty(self):
        """Test that empty resource_id raises ValueError."""
        with pytest.raises(ValueError, match="resource_id cannot be empty"):
            SearchResult(resource_id="", score=0.95, rank=1)

    def test_resource_id_validation_whitespace(self):
        """Test that whitespace-only resource_id raises ValueError."""
        with pytest.raises(ValueError, match="resource_id cannot be empty"):
            SearchResult(resource_id="   ", score=0.95, rank=1)

    def test_score_validation_negative(self):
        """Test that negative score raises ValueError."""
        with pytest.raises(ValueError, match="score must be non-negative"):
            SearchResult(resource_id="res_123", score=-0.1, rank=1)

    def test_score_validation_zero_allowed(self):
        """Test that score of 0.0 is valid."""
        result = SearchResult(resource_id="res_123", score=0.0, rank=1)
        assert result.score == 0.0

    def test_rank_validation_zero(self):
        """Test that rank of 0 raises ValueError."""
        with pytest.raises(ValueError, match="rank must be positive"):
            SearchResult(resource_id="res_123", score=0.95, rank=0)

    def test_rank_validation_negative(self):
        """Test that negative rank raises ValueError."""
        with pytest.raises(ValueError, match="rank must be positive"):
            SearchResult(resource_id="res_123", score=0.95, rank=-1)

    def test_is_high_score_default_threshold(self):
        """Test is_high_score with default threshold (0.8)."""
        high_result = SearchResult("res_1", 0.85, 1)
        low_result = SearchResult("res_2", 0.75, 2)

        assert high_result.is_high_score() is True
        assert low_result.is_high_score() is False

    def test_is_high_score_custom_threshold(self):
        """Test is_high_score with custom threshold."""
        result = SearchResult("res_1", 0.75, 1)

        assert result.is_high_score(threshold=0.7) is True
        assert result.is_high_score(threshold=0.8) is False

    def test_is_low_score_default_threshold(self):
        """Test is_low_score with default threshold (0.3)."""
        low_result = SearchResult("res_1", 0.25, 1)
        high_result = SearchResult("res_2", 0.35, 2)

        assert low_result.is_low_score() is True
        assert high_result.is_low_score() is False

    def test_is_low_score_custom_threshold(self):
        """Test is_low_score with custom threshold."""
        result = SearchResult("res_1", 0.35, 1)

        assert result.is_low_score(threshold=0.4) is True
        assert result.is_low_score(threshold=0.3) is False

    def test_is_top_result_default_k(self):
        """Test is_top_result with default k (5)."""
        top_result = SearchResult("res_1", 0.95, 3)
        not_top_result = SearchResult("res_2", 0.75, 6)

        assert top_result.is_top_result() is True
        assert not_top_result.is_top_result() is False

    def test_is_top_result_custom_k(self):
        """Test is_top_result with custom k."""
        result = SearchResult("res_1", 0.85, 3)

        assert result.is_top_result(top_k=2) is False
        assert result.is_top_result(top_k=5) is True

    def test_get_metadata_value(self):
        """Test get_metadata_value retrieves values."""
        metadata = {"source": "dense", "distance": 0.05}
        result = SearchResult("res_1", 0.95, 1, metadata=metadata)

        assert result.get_metadata_value("source") == "dense"
        assert result.get_metadata_value("distance") == 0.05
        assert result.get_metadata_value("missing") is None
        assert result.get_metadata_value("missing", "default") == "default"

    def test_has_metadata(self):
        """Test has_metadata checks for key existence."""
        metadata = {"source": "dense"}
        result = SearchResult("res_1", 0.95, 1, metadata=metadata)

        assert result.has_metadata("source") is True
        assert result.has_metadata("missing") is False

    def test_to_dict(self):
        """Test conversion to dictionary."""
        metadata = {"source": "dense"}
        result = SearchResult(
            resource_id="res_123",
            score=0.95,
            rank=1,
            title="Test Title",
            search_method="dense",
            metadata=metadata,
        )

        data = result.to_dict()

        assert data == {
            "resource_id": "res_123",
            "score": 0.95,
            "rank": 1,
            "title": "Test Title",
            "search_method": "dense",
            "metadata": {"source": "dense"},
        }

    def test_equality(self):
        """Test equality comparison."""
        result1 = SearchResult("res_1", 0.95, 1)
        result2 = SearchResult("res_1", 0.95, 1)
        result3 = SearchResult("res_2", 0.95, 1)

        assert result1 == result2
        assert result1 != result3


class TestSearchResults:
    """Tests for SearchResults value object."""

    def test_create_valid_results(self):
        """Test creating valid search results."""
        query = SearchQuery(query_text="test")
        results = [
            SearchResult("res_1", 0.95, 1),
            SearchResult("res_2", 0.85, 2),
        ]

        search_results = SearchResults(
            results=results, query=query, total_results=2, search_time_ms=45.5
        )

        assert len(search_results.results) == 2
        assert search_results.query == query
        assert search_results.total_results == 2
        assert search_results.search_time_ms == 45.5
        assert search_results.reranked is False

    def test_create_with_reranked_flag(self):
        """Test creating results with reranked flag."""
        query = SearchQuery(query_text="test")
        results = [SearchResult("res_1", 0.95, 1)]

        search_results = SearchResults(
            results=results,
            query=query,
            total_results=1,
            search_time_ms=45.5,
            reranked=True,
        )

        assert search_results.reranked is True

    def test_validation_negative_total_results(self):
        """Test that negative total_results raises ValueError."""
        query = SearchQuery(query_text="test")
        results = [SearchResult("res_1", 0.95, 1)]

        with pytest.raises(ValueError, match="total_results must be non-negative"):
            SearchResults(
                results=results, query=query, total_results=-1, search_time_ms=45.5
            )

    def test_validation_negative_search_time(self):
        """Test that negative search_time_ms raises ValueError."""
        query = SearchQuery(query_text="test")
        results = [SearchResult("res_1", 0.95, 1)]

        with pytest.raises(ValueError, match="search_time_ms must be non-negative"):
            SearchResults(
                results=results, query=query, total_results=1, search_time_ms=-10.0
            )

    def test_get_top_k(self):
        """Test get_top_k returns results sorted by rank."""
        query = SearchQuery(query_text="test")
        results = [
            SearchResult("res_1", 0.75, 3),
            SearchResult("res_2", 0.95, 1),
            SearchResult("res_3", 0.85, 2),
            SearchResult("res_4", 0.65, 4),
        ]

        search_results = SearchResults(
            results=results, query=query, total_results=4, search_time_ms=45.5
        )

        top_2 = search_results.get_top_k(2)
        assert len(top_2) == 2
        assert top_2[0].rank == 1
        assert top_2[1].rank == 2

    def test_get_top_k_invalid(self):
        """Test get_top_k with invalid k raises ValueError."""
        query = SearchQuery(query_text="test")
        results = [SearchResult("res_1", 0.95, 1)]

        search_results = SearchResults(
            results=results, query=query, total_results=1, search_time_ms=45.5
        )

        with pytest.raises(ValueError, match="k must be positive"):
            search_results.get_top_k(0)

    def test_get_high_score_results(self):
        """Test get_high_score_results filters by score."""
        query = SearchQuery(query_text="test")
        results = [
            SearchResult("res_1", 0.95, 1),
            SearchResult("res_2", 0.75, 2),
            SearchResult("res_3", 0.85, 3),
        ]

        search_results = SearchResults(
            results=results, query=query, total_results=3, search_time_ms=45.5
        )

        high_score = search_results.get_high_score_results()
        assert len(high_score) == 2
        assert all(r.score >= 0.8 for r in high_score)

    def test_get_by_method(self):
        """Test get_by_method filters by search method."""
        query = SearchQuery(query_text="test")
        results = [
            SearchResult("res_1", 0.95, 1, search_method="dense"),
            SearchResult("res_2", 0.85, 2, search_method="fts5"),
            SearchResult("res_3", 0.75, 3, search_method="dense"),
        ]

        search_results = SearchResults(
            results=results, query=query, total_results=3, search_time_ms=45.5
        )

        dense_results = search_results.get_by_method("dense")
        assert len(dense_results) == 2
        assert all(r.search_method == "dense" for r in dense_results)

    def test_has_results(self):
        """Test has_results checks for non-empty results."""
        query = SearchQuery(query_text="test")

        with_results = SearchResults(
            results=[SearchResult("res_1", 0.95, 1)],
            query=query,
            total_results=1,
            search_time_ms=45.5,
        )

        without_results = SearchResults(
            results=[], query=query, total_results=0, search_time_ms=45.5
        )

        assert with_results.has_results() is True
        assert without_results.has_results() is False

    def test_get_result_count(self):
        """Test get_result_count returns correct count."""
        query = SearchQuery(query_text="test")
        results = [
            SearchResult("res_1", 0.95, 1),
            SearchResult("res_2", 0.85, 2),
        ]

        search_results = SearchResults(
            results=results, query=query, total_results=2, search_time_ms=45.5
        )

        assert search_results.get_result_count() == 2

    def test_get_average_score(self):
        """Test get_average_score calculates correctly."""
        query = SearchQuery(query_text="test")
        results = [
            SearchResult("res_1", 0.9, 1),
            SearchResult("res_2", 0.8, 2),
            SearchResult("res_3", 0.7, 3),
        ]

        search_results = SearchResults(
            results=results, query=query, total_results=3, search_time_ms=45.5
        )

        avg = search_results.get_average_score()
        assert avg == pytest.approx(0.8, rel=1e-9)

    def test_get_average_score_empty_results(self):
        """Test get_average_score returns 0.0 for empty results."""
        query = SearchQuery(query_text="test")

        search_results = SearchResults(
            results=[], query=query, total_results=0, search_time_ms=45.5
        )

        assert search_results.get_average_score() == 0.0

    def test_get_score_distribution(self):
        """Test get_score_distribution returns correct counts."""
        query = SearchQuery(query_text="test")
        results = [
            SearchResult("res_1", 0.95, 1),  # high
            SearchResult("res_2", 0.85, 2),  # high
            SearchResult("res_3", 0.55, 3),  # medium
            SearchResult("res_4", 0.65, 4),  # medium
            SearchResult("res_5", 0.25, 5),  # low
        ]

        search_results = SearchResults(
            results=results, query=query, total_results=5, search_time_ms=45.5
        )

        distribution = search_results.get_score_distribution()
        assert distribution == {"low": 1, "medium": 2, "high": 2}

    def test_to_dict_api_compatibility(self):
        """Test to_dict provides API-compatible format."""
        query = SearchQuery(query_text="test query", limit=30)
        results = [
            SearchResult("res_1", 0.95, 1, title="Result 1"),
            SearchResult("res_2", 0.85, 2, title="Result 2"),
        ]

        search_results = SearchResults(
            results=results,
            query=query,
            total_results=2,
            search_time_ms=45.5,
            reranked=True,
        )

        data = search_results.to_dict()

        assert "results" in data
        assert len(data["results"]) == 2
        assert data["results"][0]["resource_id"] == "res_1"
        assert "query" in data
        assert data["query"]["query_text"] == "test query"
        assert data["total_results"] == 2
        assert data["search_time_ms"] == 45.5
        assert data["reranked"] is True
        assert "metadata" in data
        assert data["metadata"]["result_count"] == 2
        assert data["metadata"]["has_results"] is True

    def test_from_dict(self):
        """Test from_dict creates valid SearchResults."""
        data = {
            "results": [
                {
                    "resource_id": "res_1",
                    "score": 0.95,
                    "rank": 1,
                    "title": "Result 1",
                    "search_method": "dense",
                    "metadata": {},
                },
                {
                    "resource_id": "res_2",
                    "score": 0.85,
                    "rank": 2,
                    "title": "Result 2",
                    "search_method": "fts5",
                    "metadata": {},
                },
            ],
            "query": {
                "query_text": "test query",
                "limit": 30,
                "enable_reranking": True,
                "adaptive_weights": False,
                "search_method": "hybrid",
            },
            "total_results": 2,
            "search_time_ms": 45.5,
            "reranked": True,
        }

        search_results = SearchResults.from_dict(data)

        assert len(search_results.results) == 2
        assert search_results.results[0].resource_id == "res_1"
        assert search_results.query.query_text == "test query"
        assert search_results.query.limit == 30
        assert search_results.total_results == 2
        assert search_results.search_time_ms == 45.5
        assert search_results.reranked is True

    def test_round_trip_serialization(self):
        """Test that to_dict/from_dict round-trip works correctly."""
        query = SearchQuery(query_text="test", limit=25)
        results = [
            SearchResult("res_1", 0.95, 1, title="Result 1"),
            SearchResult("res_2", 0.85, 2, title="Result 2"),
        ]

        original = SearchResults(
            results=results,
            query=query,
            total_results=2,
            search_time_ms=45.5,
            reranked=True,
        )

        # Convert to dict and back
        data = original.to_dict()
        restored = SearchResults.from_dict(data)

        # Verify core attributes match
        assert len(restored.results) == len(original.results)
        assert restored.query.query_text == original.query.query_text
        assert restored.total_results == original.total_results
        assert restored.search_time_ms == original.search_time_ms
        assert restored.reranked == original.reranked


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
