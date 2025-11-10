"""
Unit tests for SearchMetricsService

Tests information retrieval metrics:
- nDCG (Normalized Discounted Cumulative Gain)
- Recall@K
- Precision@K
- Mean Reciprocal Rank (MRR)
"""

import pytest
from app.services.search_metrics_service import SearchMetricsService


class TestSearchMetricsService:
    """Test suite for SearchMetricsService."""
    
    @pytest.fixture
    def service(self):
        """Create SearchMetricsService instance."""
        return SearchMetricsService()
    
    # ========== nDCG Tests ==========
    
    def test_compute_ndcg_perfect_ranking(self, service):
        """Test nDCG with perfect ranking returns 1.0."""
        ranked_results = ["doc1", "doc2", "doc3", "doc4"]
        relevance_judgments = {
            "doc1": 3,  # Highly relevant
            "doc2": 2,  # Relevant
            "doc3": 1,  # Marginally relevant
            "doc4": 0   # Not relevant
        }
        
        ndcg = service.compute_ndcg(ranked_results, relevance_judgments, k=4)
        
        # Perfect ranking should give nDCG = 1.0
        assert ndcg == pytest.approx(1.0, abs=0.001)
    
    def test_compute_ndcg_worst_ranking(self, service):
        """Test nDCG with worst possible ranking."""
        ranked_results = ["doc4", "doc3", "doc2", "doc1"]
        relevance_judgments = {
            "doc1": 3,  # Highly relevant (ranked last)
            "doc2": 2,  # Relevant (ranked 3rd)
            "doc3": 1,  # Marginally relevant (ranked 2nd)
            "doc4": 0   # Not relevant (ranked first)
        }
        
        ndcg = service.compute_ndcg(ranked_results, relevance_judgments, k=4)
        
        # Worst ranking should give low nDCG
        assert 0.0 < ndcg < 0.5
    
    def test_compute_ndcg_partial_ranking(self, service):
        """Test nDCG with some relevant docs ranked well."""
        ranked_results = ["doc1", "doc4", "doc2", "doc3"]
        relevance_judgments = {
            "doc1": 3,  # Highly relevant (ranked 1st - good)
            "doc2": 2,  # Relevant (ranked 3rd - okay)
            "doc3": 1,  # Marginally relevant (ranked 4th - okay)
            "doc4": 0   # Not relevant (ranked 2nd - bad)
        }
        
        ndcg = service.compute_ndcg(ranked_results, relevance_judgments, k=4)
        
        # Should be between 0.5 and 1.0
        assert 0.5 < ndcg < 1.0
    
    def test_compute_ndcg_with_k_limit(self, service):
        """Test nDCG respects k parameter."""
        ranked_results = ["doc1", "doc2", "doc3", "doc4", "doc5"]
        relevance_judgments = {
            "doc1": 3,
            "doc2": 2,
            "doc3": 1,
            "doc4": 0,
            "doc5": 3  # Highly relevant but beyond k=3
        }
        
        ndcg_k3 = service.compute_ndcg(ranked_results, relevance_judgments, k=3)
        ndcg_k5 = service.compute_ndcg(ranked_results, relevance_judgments, k=5)
        
        # k=3 should ignore doc5, k=5 should include it
        # Since doc5 is highly relevant but ranked last, k=3 should have higher nDCG
        assert ndcg_k3 > ndcg_k5
    
    def test_compute_ndcg_empty_results(self, service):
        """Test nDCG with empty results returns 0."""
        ndcg = service.compute_ndcg([], {"doc1": 3}, k=20)
        assert ndcg == 0.0
    
    def test_compute_ndcg_empty_judgments(self, service):
        """Test nDCG with empty judgments returns 0."""
        ndcg = service.compute_ndcg(["doc1", "doc2"], {}, k=20)
        assert ndcg == 0.0
    
    def test_compute_ndcg_no_relevant_docs(self, service):
        """Test nDCG when all docs have zero relevance."""
        ranked_results = ["doc1", "doc2", "doc3"]
        relevance_judgments = {
            "doc1": 0,
            "doc2": 0,
            "doc3": 0
        }
        
        ndcg = service.compute_ndcg(ranked_results, relevance_judgments, k=3)
        assert ndcg == 0.0
    
    def test_compute_ndcg_missing_judgments(self, service):
        """Test nDCG treats missing docs as non-relevant."""
        ranked_results = ["doc1", "doc2", "doc3"]
        relevance_judgments = {
            "doc1": 3,
            # doc2 and doc3 missing - should be treated as 0
        }
        
        ndcg = service.compute_ndcg(ranked_results, relevance_judgments, k=3)
        
        # Should be less than perfect since only first doc is relevant
        assert 0.0 < ndcg < 1.0
    
    # ========== Recall@K Tests ==========
    
    def test_compute_recall_perfect(self, service):
        """Test Recall@K when all relevant docs are in top-k."""
        ranked_results = ["doc1", "doc2", "doc3", "doc4"]
        relevant_docs = ["doc1", "doc2"]
        
        recall = service.compute_recall_at_k(ranked_results, relevant_docs, k=4)
        
        # All relevant docs found
        assert recall == 1.0
    
    def test_compute_recall_partial(self, service):
        """Test Recall@K when some relevant docs are missing."""
        ranked_results = ["doc1", "doc2", "doc3", "doc4"]
        relevant_docs = ["doc1", "doc3", "doc5"]  # doc5 not in results
        
        recall = service.compute_recall_at_k(ranked_results, relevant_docs, k=4)
        
        # Found 2 out of 3 relevant docs
        assert recall == pytest.approx(2/3, abs=0.001)
    
    def test_compute_recall_with_k_limit(self, service):
        """Test Recall@K respects k parameter."""
        ranked_results = ["doc1", "doc2", "doc3", "doc4"]
        relevant_docs = ["doc1", "doc4"]
        
        recall_k2 = service.compute_recall_at_k(ranked_results, relevant_docs, k=2)
        recall_k4 = service.compute_recall_at_k(ranked_results, relevant_docs, k=4)
        
        # k=2 finds only doc1, k=4 finds both
        assert recall_k2 == 0.5
        assert recall_k4 == 1.0
    
    def test_compute_recall_zero(self, service):
        """Test Recall@K when no relevant docs found."""
        ranked_results = ["doc1", "doc2", "doc3"]
        relevant_docs = ["doc4", "doc5"]
        
        recall = service.compute_recall_at_k(ranked_results, relevant_docs, k=3)
        assert recall == 0.0
    
    def test_compute_recall_empty_relevant(self, service):
        """Test Recall@K with empty relevant docs returns 0."""
        recall = service.compute_recall_at_k(["doc1", "doc2"], [], k=2)
        assert recall == 0.0
    
    # ========== Precision@K Tests ==========
    
    def test_compute_precision_perfect(self, service):
        """Test Precision@K when all results are relevant."""
        ranked_results = ["doc1", "doc2", "doc3", "doc4"]
        relevant_docs = ["doc1", "doc2", "doc3", "doc4", "doc5"]
        
        precision = service.compute_precision_at_k(ranked_results, relevant_docs, k=4)
        
        # All 4 results are relevant
        assert precision == 1.0
    
    def test_compute_precision_partial(self, service):
        """Test Precision@K when some results are not relevant."""
        ranked_results = ["doc1", "doc2", "doc3", "doc4"]
        relevant_docs = ["doc1", "doc3"]
        
        precision = service.compute_precision_at_k(ranked_results, relevant_docs, k=4)
        
        # 2 out of 4 results are relevant
        assert precision == 0.5
    
    def test_compute_precision_with_k_limit(self, service):
        """Test Precision@K respects k parameter."""
        ranked_results = ["doc1", "doc2", "doc3", "doc4"]
        relevant_docs = ["doc1", "doc2"]
        
        precision_k2 = service.compute_precision_at_k(ranked_results, relevant_docs, k=2)
        precision_k4 = service.compute_precision_at_k(ranked_results, relevant_docs, k=4)
        
        # k=2: 2/2 relevant, k=4: 2/4 relevant
        assert precision_k2 == 1.0
        assert precision_k4 == 0.5
    
    def test_compute_precision_zero(self, service):
        """Test Precision@K when no results are relevant."""
        ranked_results = ["doc1", "doc2", "doc3"]
        relevant_docs = ["doc4", "doc5"]
        
        precision = service.compute_precision_at_k(ranked_results, relevant_docs, k=3)
        assert precision == 0.0
    
    def test_compute_precision_k_zero(self, service):
        """Test Precision@K with k=0 returns 0."""
        precision = service.compute_precision_at_k(["doc1"], ["doc1"], k=0)
        assert precision == 0.0
    
    # ========== MRR Tests ==========
    
    def test_compute_mrr_first_position(self, service):
        """Test MRR when first result is relevant."""
        ranked_results = ["doc1", "doc2", "doc3"]
        relevant_docs = ["doc1", "doc4"]
        
        mrr = service.compute_mean_reciprocal_rank(ranked_results, relevant_docs)
        
        # First position = rank 1, so MRR = 1/1 = 1.0
        assert mrr == 1.0
    
    def test_compute_mrr_second_position(self, service):
        """Test MRR when first relevant result is at position 2."""
        ranked_results = ["doc1", "doc2", "doc3"]
        relevant_docs = ["doc2", "doc4"]
        
        mrr = service.compute_mean_reciprocal_rank(ranked_results, relevant_docs)
        
        # Second position = rank 2, so MRR = 1/2 = 0.5
        assert mrr == 0.5
    
    def test_compute_mrr_third_position(self, service):
        """Test MRR when first relevant result is at position 3."""
        ranked_results = ["doc1", "doc2", "doc3", "doc4"]
        relevant_docs = ["doc3", "doc5"]
        
        mrr = service.compute_mean_reciprocal_rank(ranked_results, relevant_docs)
        
        # Third position = rank 3, so MRR = 1/3
        assert mrr == pytest.approx(1/3, abs=0.001)
    
    def test_compute_mrr_no_relevant_found(self, service):
        """Test MRR when no relevant docs are in results."""
        ranked_results = ["doc1", "doc2", "doc3"]
        relevant_docs = ["doc4", "doc5"]
        
        mrr = service.compute_mean_reciprocal_rank(ranked_results, relevant_docs)
        assert mrr == 0.0
    
    def test_compute_mrr_empty_relevant(self, service):
        """Test MRR with empty relevant docs returns 0."""
        mrr = service.compute_mean_reciprocal_rank(["doc1", "doc2"], [])
        assert mrr == 0.0
    
    def test_compute_mrr_multiple_relevant(self, service):
        """Test MRR only considers first relevant doc."""
        ranked_results = ["doc1", "doc2", "doc3", "doc4"]
        relevant_docs = ["doc2", "doc3", "doc4"]  # Multiple relevant
        
        mrr = service.compute_mean_reciprocal_rank(ranked_results, relevant_docs)
        
        # First relevant is doc2 at position 2, so MRR = 1/2
        assert mrr == 0.5
    
    # ========== Integration Tests ==========
    
    def test_all_metrics_together(self, service):
        """Test computing all metrics on the same dataset."""
        ranked_results = ["doc1", "doc2", "doc3", "doc4", "doc5"]
        relevant_docs = ["doc1", "doc3", "doc6"]
        relevance_judgments = {
            "doc1": 3,
            "doc2": 0,
            "doc3": 2,
            "doc4": 0,
            "doc5": 0,
            "doc6": 1
        }
        
        ndcg = service.compute_ndcg(ranked_results, relevance_judgments, k=5)
        recall = service.compute_recall_at_k(ranked_results, relevant_docs, k=5)
        precision = service.compute_precision_at_k(ranked_results, relevant_docs, k=5)
        mrr = service.compute_mean_reciprocal_rank(ranked_results, relevant_docs)
        
        # All metrics should be computable
        assert 0.0 <= ndcg <= 1.0
        assert 0.0 <= recall <= 1.0
        assert 0.0 <= precision <= 1.0
        assert 0.0 <= mrr <= 1.0
        
        # Recall should be 2/3 (found doc1 and doc3, missing doc6)
        assert recall == pytest.approx(2/3, abs=0.001)
        
        # Precision should be 2/5 (2 relevant out of 5 results)
        assert precision == pytest.approx(2/5, abs=0.001)
        
        # MRR should be 1.0 (first result is relevant)
        assert mrr == 1.0
