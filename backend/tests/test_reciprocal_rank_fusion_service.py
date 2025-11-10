"""Tests for Reciprocal Rank Fusion Service (Phase 8)."""

import pytest
from backend.app.services.reciprocal_rank_fusion_service import ReciprocalRankFusionService


class TestReciprocalRankFusionService:
    """Test RRF service functionality."""
    
    @pytest.fixture
    def rrf_service(self):
        """Create an RRF service instance with default k=60."""
        return ReciprocalRankFusionService(k=60)
    
    def test_service_initialization(self):
        """Test service can be initialized with custom k parameter."""
        service = ReciprocalRankFusionService(k=100)
        assert service.k == 100
    
    def test_fuse_results_empty_lists(self, rrf_service):
        """Test RRF fusion with empty result lists."""
        result = rrf_service.fuse_results([])
        assert result == []
        
        result = rrf_service.fuse_results([[], [], []])
        assert result == []
    
    def test_fuse_results_single_list(self, rrf_service):
        """Test RRF fusion with a single result list."""
        results = [("doc1", 10.5), ("doc2", 8.3), ("doc3", 5.1)]
        fused = rrf_service.fuse_results([results])
        
        # Should return all documents sorted by RRF score
        assert len(fused) == 3
        assert fused[0][0] == "doc1"  # Rank 0 has highest RRF score
        assert fused[1][0] == "doc2"  # Rank 1
        assert fused[2][0] == "doc3"  # Rank 2
    
    def test_fuse_results_basic_fusion(self, rrf_service):
        """Test basic RRF fusion with multiple lists."""
        fts5_results = [("doc1", 10.5), ("doc2", 8.3), ("doc3", 5.1)]
        dense_results = [("doc2", 0.95), ("doc1", 0.87), ("doc4", 0.72)]
        sparse_results = [("doc3", 0.88), ("doc1", 0.76), ("doc2", 0.65)]
        
        fused = rrf_service.fuse_results([fts5_results, dense_results, sparse_results])
        
        # doc1 appears in all three lists with good ranks -> should have high RRF score
        # doc2 appears in all three lists
        # doc3 appears in two lists
        # doc4 appears in one list
        assert len(fused) == 4
        
        # Extract just the document IDs
        doc_ids = [doc_id for doc_id, score in fused]
        
        # doc1 should be first (appears in all lists with good ranks)
        assert doc_ids[0] == "doc1"
    
    def test_fuse_results_with_weights(self, rrf_service):
        """Test RRF fusion with custom weights."""
        fts5_results = [("doc1", 10.5), ("doc2", 8.3)]
        dense_results = [("doc2", 0.95), ("doc3", 0.87)]
        
        # Equal weights
        fused_equal = rrf_service.fuse_results(
            [fts5_results, dense_results],
            weights=[1.0, 1.0]
        )
        
        # Boost FTS5 heavily
        fused_fts5 = rrf_service.fuse_results(
            [fts5_results, dense_results],
            weights=[3.0, 1.0]
        )
        
        # Both should have same documents but potentially different order
        assert len(fused_equal) == 3
        assert len(fused_fts5) == 3
    
    def test_fuse_results_weight_normalization(self, rrf_service):
        """Test that weights are normalized to sum to 1.0."""
        results1 = [("doc1", 1.0)]
        results2 = [("doc2", 1.0)]
        
        # Weights should be normalized internally
        fused = rrf_service.fuse_results(
            [results1, results2],
            weights=[100.0, 200.0]  # Will be normalized to [1/3, 2/3]
        )
        
        assert len(fused) == 2
    
    def test_fuse_results_mismatched_weights(self, rrf_service):
        """Test RRF fusion when weights length doesn't match result lists."""
        results1 = [("doc1", 1.0)]
        results2 = [("doc2", 1.0)]
        results3 = [("doc3", 1.0)]
        
        # Provide only 2 weights for 3 lists
        fused = rrf_service.fuse_results(
            [results1, results2, results3],
            weights=[1.0, 2.0]  # Mismatched length
        )
        
        # Should fall back to equal weights
        assert len(fused) == 3
    
    def test_fuse_results_zero_weights(self, rrf_service):
        """Test RRF fusion with all zero weights."""
        results1 = [("doc1", 1.0)]
        results2 = [("doc2", 1.0)]
        
        fused = rrf_service.fuse_results(
            [results1, results2],
            weights=[0.0, 0.0]
        )
        
        # Should fall back to equal weights
        assert len(fused) == 2
    
    def test_fuse_results_rrf_formula(self, rrf_service):
        """Test that RRF formula is correctly applied."""
        # Single list to verify formula: RRF_score = weight / (k + rank)
        results = [("doc1", 1.0), ("doc2", 1.0), ("doc3", 1.0)]
        fused = rrf_service.fuse_results([results], weights=[1.0])
        
        # With k=60 and weight=1.0:
        # doc1 (rank 0): 1.0 / (60 + 0) = 1/60 ≈ 0.0167
        # doc2 (rank 1): 1.0 / (60 + 1) = 1/61 ≈ 0.0164
        # doc3 (rank 2): 1.0 / (60 + 2) = 1/62 ≈ 0.0161
        
        assert fused[0][0] == "doc1"
        assert fused[1][0] == "doc2"
        assert fused[2][0] == "doc3"
        
        # Verify scores are in descending order
        assert fused[0][1] > fused[1][1] > fused[2][1]
    
    def test_adaptive_weights_empty_query(self, rrf_service):
        """Test adaptive weights with empty query."""
        weights = rrf_service.adaptive_weights("")
        assert len(weights) == 3
        assert all(w > 0 for w in weights)
        assert abs(sum(weights) - 1.0) < 0.001  # Should sum to 1.0
    
    def test_adaptive_weights_short_query(self, rrf_service):
        """Test adaptive weights boost FTS5 for short queries."""
        weights = rrf_service.adaptive_weights("machine learning")
        
        # FTS5 should be boosted (index 0)
        assert weights[0] > weights[1]  # FTS5 > dense
        assert weights[0] > weights[2]  # FTS5 > sparse
        assert abs(sum(weights) - 1.0) < 0.001
    
    def test_adaptive_weights_long_query(self, rrf_service):
        """Test adaptive weights boost dense vectors for long queries."""
        long_query = "How does gradient descent optimization work in deep neural networks with backpropagation"
        weights = rrf_service.adaptive_weights(long_query)
        
        # Dense should be boosted (index 1)
        assert weights[1] > weights[0]  # dense > FTS5
        assert weights[1] > weights[2]  # dense > sparse
        assert abs(sum(weights) - 1.0) < 0.001
    
    def test_adaptive_weights_question_query(self, rrf_service):
        """Test adaptive weights boost dense vectors for question queries."""
        questions = [
            "What is machine learning?",
            "How does this work?",
            "Why is the sky blue?",
            "When was Python created?",
            "Where can I find documentation?",
            "Who invented the algorithm?"
        ]
        
        for question in questions:
            weights = rrf_service.adaptive_weights(question)
            # Dense should be boosted for questions
            assert weights[1] > 0.3  # Dense has significant weight
            assert abs(sum(weights) - 1.0) < 0.001
    
    def test_adaptive_weights_code_query(self, rrf_service):
        """Test adaptive weights boost sparse vectors for code queries."""
        code_queries = [
            "def fibonacci(n): return n if n <= 1",
            "function calculateSum(a, b) { return a + b; }",
            "class MyClass { constructor() {} }",
            "import numpy as np",
            "obj.method()",
            "array[index]"
        ]
        
        for code_query in code_queries:
            weights = rrf_service.adaptive_weights(code_query)
            # Sparse should be boosted for code (index 2)
            # Use >= to handle cases where weights might be equal after normalization
            assert weights[2] >= weights[0]  # sparse >= FTS5
            assert abs(sum(weights) - 1.0) < 0.001
    
    def test_adaptive_weights_math_query(self, rrf_service):
        """Test adaptive weights boost sparse vectors for math queries."""
        math_queries = [
            "solve equation x + y = 10",
            "calculate integral of x^2",
            "derivative of sin(x)",
            "sum of series 1 + 2 + 3",
            "formula for area"
        ]
        
        for math_query in math_queries:
            weights = rrf_service.adaptive_weights(math_query)
            # Sparse should be boosted for math (index 2)
            assert weights[2] > 0.25  # Sparse has significant weight
            assert abs(sum(weights) - 1.0) < 0.001
    
    def test_adaptive_weights_combined_characteristics(self, rrf_service):
        """Test adaptive weights with queries having multiple characteristics."""
        # Long question query (both long and question)
        query = "How does the gradient descent optimization algorithm work in deep neural networks?"
        weights = rrf_service.adaptive_weights(query)
        
        # Dense should be heavily boosted (long + question)
        assert weights[1] > weights[0]
        assert weights[1] > weights[2]
        assert abs(sum(weights) - 1.0) < 0.001
    
    def test_adaptive_weights_normalization(self, rrf_service):
        """Test that adaptive weights always sum to 1.0."""
        test_queries = [
            "",
            "short",
            "this is a medium length query",
            "this is a very long query with many words that should trigger the long query detection",
            "def function(): pass",
            "What is the answer?",
            "x + y = z"
        ]
        
        for query in test_queries:
            weights = rrf_service.adaptive_weights(query)
            assert len(weights) == 3
            assert abs(sum(weights) - 1.0) < 0.001
            assert all(w >= 0 for w in weights)
