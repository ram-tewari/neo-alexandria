"""
Three-Way Hybrid Search Integration Tests

Tests for three-way hybrid search combining FTS5, dense vectors, and sparse vectors.
"""

import time
from sqlalchemy.orm import Session

from app.services.search_service import AdvancedSearchService
from app.modules.search.schema import SearchQuery


class TestThreeWayHybridSearch:
    """Test three-way hybrid search functionality."""

    def test_three_way_search_basic(self, db_session: Session, create_test_resource):
        """Test basic three-way hybrid search returns results."""
        # Create test resources
        create_test_resource(
            title="Machine Learning Basics",
            description="Introduction to machine learning algorithms and neural networks",
        )
        create_test_resource(
            title="Deep Learning Tutorial",
            description="Advanced deep learning techniques using PyTorch and TensorFlow",
        )
        create_test_resource(
            title="Data Science Overview",
            description="Data science fundamentals including statistics and visualization",
        )

        # Execute three-way search
        query = SearchQuery(text="machine learning", limit=10, offset=0)
        resources, total, facets, snippets, metadata = (
            AdvancedSearchService.search_three_way_hybrid(
                db=db_session,
                query=query,
                enable_reranking=False,
                adaptive_weighting=True,
            )
        )

        # Verify results
        assert isinstance(resources, list)
        assert isinstance(total, int)
        assert isinstance(metadata, dict)

        # Verify metadata structure
        assert "latency_ms" in metadata
        assert "method_contributions" in metadata
        assert "weights_used" in metadata
        assert "timing" in metadata

        # Verify method contributions
        contributions = metadata["method_contributions"]
        assert "fts5" in contributions
        assert "dense" in contributions
        assert "sparse" in contributions

        # Verify weights sum to 1.0
        weights = metadata["weights_used"]
        assert len(weights) == 3
        assert abs(sum(weights) - 1.0) < 0.001

    def test_query_adaptive_weighting_short_query(self, db_session: Session):
        """Test that short queries boost FTS5 weight."""
        # Short query (≤3 words)
        weights = AdvancedSearchService._compute_adaptive_weights("ML basics")

        # FTS5 weight (index 0) should be highest
        assert weights[0] > weights[1]
        assert weights[0] > weights[2]

        # Weights should sum to 1.0
        assert abs(sum(weights) - 1.0) < 0.001

    def test_query_adaptive_weighting_long_query(self, db_session: Session):
        """Test that long queries boost dense vector weight."""
        # Long query (>10 words)
        long_query = "What are the fundamental principles and best practices for implementing machine learning algorithms in production environments"
        weights = AdvancedSearchService._compute_adaptive_weights(long_query)

        # Dense weight (index 1) should be highest
        assert weights[1] > weights[0]
        assert weights[1] > weights[2]

        # Weights should sum to 1.0
        assert abs(sum(weights) - 1.0) < 0.001

    def test_query_adaptive_weighting_technical_query(self, db_session: Session):
        """Test that technical queries boost sparse vector weight."""
        # Technical query with code symbols
        technical_query = "def train_model(x, y): return model.fit(x, y)"
        weights = AdvancedSearchService._compute_adaptive_weights(technical_query)

        # Sparse weight (index 2) should be boosted
        assert weights[2] > 1.0 / 3  # Greater than equal weight

        # Weights should sum to 1.0
        assert abs(sum(weights) - 1.0) < 0.001

    def test_query_adaptive_weighting_question_query(self, db_session: Session):
        """Test that question queries boost dense vector weight."""
        # Question query
        question_query = "How does gradient descent work in neural networks?"
        weights = AdvancedSearchService._compute_adaptive_weights(question_query)

        # Dense weight (index 1) should be boosted
        assert weights[1] > 1.0 / 3  # Greater than equal weight

        # Weights should sum to 1.0
        assert abs(sum(weights) - 1.0) < 0.001

    def test_three_way_search_with_reranking(
        self, db_session: Session, create_test_resource
    ):
        """Test three-way search with reranking enabled."""
        # Create test resources
        create_test_resource(
            title="Python Programming",
            description="Learn Python programming language basics",
        )
        create_test_resource(
            title="Java Development",
            description="Java programming and development practices",
        )

        # Execute with reranking
        query = SearchQuery(text="python programming", limit=10, offset=0)
        resources, total, facets, snippets, metadata = (
            AdvancedSearchService.search_three_way_hybrid(
                db=db_session,
                query=query,
                enable_reranking=True,
                adaptive_weighting=True,
            )
        )

        # Verify reranking timing is included
        assert "timing" in metadata
        assert "rerank_ms" in metadata["timing"]

    def test_three_way_search_without_adaptive_weighting(
        self, db_session: Session, create_test_resource
    ):
        """Test three-way search with equal weights."""
        # Create test resource
        create_test_resource(
            title="Test Resource", description="Test content for search"
        )

        # Execute without adaptive weighting
        query = SearchQuery(text="test", limit=10, offset=0)
        resources, total, facets, snippets, metadata = (
            AdvancedSearchService.search_three_way_hybrid(
                db=db_session,
                query=query,
                enable_reranking=False,
                adaptive_weighting=False,
            )
        )

        # Verify equal weights
        weights = metadata["weights_used"]
        assert len(weights) == 3
        assert abs(weights[0] - 1.0 / 3) < 0.001
        assert abs(weights[1] - 1.0 / 3) < 0.001
        assert abs(weights[2] - 1.0 / 3) < 0.001

    def test_three_way_search_pagination(
        self, db_session: Session, create_test_resource
    ):
        """Test pagination in three-way search."""
        # Create multiple test resources
        for i in range(15):
            create_test_resource(
                title=f"Resource {i}", description=f"Content about topic {i}"
            )

        # Test first page
        query1 = SearchQuery(text="resource", limit=5, offset=0)
        resources1, total1, _, _, _ = AdvancedSearchService.search_three_way_hybrid(
            db=db_session, query=query1, enable_reranking=False, adaptive_weighting=True
        )

        # Test second page
        query2 = SearchQuery(text="resource", limit=5, offset=5)
        resources2, total2, _, _, _ = AdvancedSearchService.search_three_way_hybrid(
            db=db_session, query=query2, enable_reranking=False, adaptive_weighting=True
        )

        # Verify pagination
        assert len(resources1) <= 5
        assert len(resources2) <= 5
        assert total1 == total2  # Total should be same

        # Verify different results
        ids1 = {str(r.id) for r in resources1}
        ids2 = {str(r.id) for r in resources2}
        assert ids1 != ids2  # Different pages should have different results

    def test_three_way_search_empty_query(self, db_session: Session):
        """Test three-way search with empty query."""
        query = SearchQuery(text="", limit=10, offset=0)
        resources, total, facets, snippets, metadata = (
            AdvancedSearchService.search_three_way_hybrid(
                db=db_session,
                query=query,
                enable_reranking=False,
                adaptive_weighting=True,
            )
        )

        # Should return empty results
        assert resources == []
        assert total == 0

    def test_three_way_search_no_matches(
        self, db_session: Session, create_test_resource
    ):
        """Test three-way search with query that matches nothing."""
        # Create resource with specific content
        create_test_resource(
            title="Python Tutorial", description="Learn Python programming"
        )

        # Query for something completely different
        query = SearchQuery(text="quantum physics relativity", limit=10, offset=0)
        resources, total, facets, snippets, metadata = (
            AdvancedSearchService.search_three_way_hybrid(
                db=db_session,
                query=query,
                enable_reranking=False,
                adaptive_weighting=True,
            )
        )

        # May return empty or very low relevance results
        assert isinstance(resources, list)
        assert isinstance(total, int)


class TestThreeWaySearchPerformance:
    """Test performance targets for three-way hybrid search."""

    def test_search_latency_target(self, db_session: Session, create_test_resource):
        """Test that three-way search meets latency target (<150ms for retrieval)."""
        # Create test resources
        for i in range(20):
            create_test_resource(
                title=f"Document {i}",
                description=f"Content about machine learning and AI topic {i}",
            )

        # Execute search and measure time
        query = SearchQuery(text="machine learning", limit=20, offset=0)
        start_time = time.time()
        resources, total, facets, snippets, metadata = (
            AdvancedSearchService.search_three_way_hybrid(
                db=db_session,
                query=query,
                enable_reranking=False,
                adaptive_weighting=True,
            )
        )
        elapsed_ms = (time.time() - start_time) * 1000

        # Verify latency is reasonable (relaxed for test environment)
        # Target is <150ms but allow up to 500ms in test environment
        assert elapsed_ms < 500, f"Search took {elapsed_ms}ms, expected <500ms"

        # Verify metadata latency is tracked
        assert metadata["latency_ms"] > 0

    def test_rrf_fusion_latency(self, db_session: Session, create_test_resource):
        """Test that RRF fusion is fast (<5ms target)."""
        # Create test resources
        for i in range(10):
            create_test_resource(title=f"Test {i}", description=f"Content {i}")

        # Execute search
        query = SearchQuery(text="test", limit=10, offset=0)
        resources, total, facets, snippets, metadata = (
            AdvancedSearchService.search_three_way_hybrid(
                db=db_session,
                query=query,
                enable_reranking=False,
                adaptive_weighting=True,
            )
        )

        # Verify RRF timing
        rrf_time = metadata["timing"]["rrf_ms"]

        # RRF should be very fast (allow up to 50ms in test environment)
        assert rrf_time < 50, f"RRF took {rrf_time}ms, expected <50ms"


class TestQueryAnalysis:
    """Test query analysis for adaptive weighting."""

    def test_analyze_short_query(self):
        """Test analysis of short queries."""
        analysis = AdvancedSearchService._analyze_query("ML AI")

        assert analysis["word_count"] == 2
        assert analysis["is_short"] is True
        assert analysis["is_long"] is False
        assert analysis["is_technical"] is False
        assert analysis["is_question"] is False

    def test_analyze_long_query(self):
        """Test analysis of long queries."""
        long_query = "What are the best practices for implementing machine learning models in production environments with high availability"
        analysis = AdvancedSearchService._analyze_query(long_query)

        assert analysis["word_count"] > 10
        assert analysis["is_short"] is False
        assert analysis["is_long"] is True
        assert analysis["is_question"] is True

    def test_analyze_technical_query(self):
        """Test analysis of technical queries."""
        technical_query = "def train(x, y): model.fit(x, y)"
        analysis = AdvancedSearchService._analyze_query(technical_query)

        assert analysis["is_technical"] is True

    def test_analyze_question_query(self):
        """Test analysis of question queries."""
        for starter in ["who", "what", "when", "where", "why", "how"]:
            query = f"{starter} is machine learning"
            analysis = AdvancedSearchService._analyze_query(query)
            assert analysis["is_question"] is True
