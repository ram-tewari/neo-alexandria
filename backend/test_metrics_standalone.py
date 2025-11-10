"""
Standalone test for SearchMetricsService
"""

import sys
import math

# Import directly without going through app
sys.path.insert(0, 'app/services')
from search_metrics_service import SearchMetricsService


def test_ndcg():
    """Test nDCG computation."""
    service = SearchMetricsService()
    
    # Test 1: Perfect ranking
    ranked = ["doc1", "doc2", "doc3"]
    judgments = {"doc1": 3, "doc2": 2, "doc3": 1}
    ndcg = service.compute_ndcg(ranked, judgments, k=3)
    assert abs(ndcg - 1.0) < 0.001, f"Perfect ranking should give nDCG=1.0, got {ndcg}"
    print("✓ nDCG perfect ranking test passed")
    
    # Test 2: Worst ranking
    ranked = ["doc3", "doc2", "doc1"]
    judgments = {"doc1": 3, "doc2": 2, "doc3": 1}
    ndcg = service.compute_ndcg(ranked, judgments, k=3)
    assert 0.0 < ndcg < 0.9, f"Worst ranking should give low nDCG, got {ndcg}"
    print("✓ nDCG worst ranking test passed")
    
    # Test 3: Empty results
    ndcg = service.compute_ndcg([], {"doc1": 3}, k=3)
    assert ndcg == 0.0, f"Empty results should give nDCG=0.0, got {ndcg}"
    print("✓ nDCG empty results test passed")


def test_recall():
    """Test Recall@K computation."""
    service = SearchMetricsService()
    
    # Test 1: Perfect recall
    ranked = ["doc1", "doc2", "doc3"]
    relevant = ["doc1", "doc2"]
    recall = service.compute_recall_at_k(ranked, relevant, k=3)
    assert recall == 1.0, f"Should find all relevant docs, got recall={recall}"
    print("✓ Recall perfect test passed")
    
    # Test 2: Partial recall
    ranked = ["doc1", "doc2", "doc3"]
    relevant = ["doc1", "doc4"]
    recall = service.compute_recall_at_k(ranked, relevant, k=3)
    assert abs(recall - 0.5) < 0.001, f"Should find 1/2 relevant docs, got recall={recall}"
    print("✓ Recall partial test passed")
    
    # Test 3: Zero recall
    ranked = ["doc1", "doc2"]
    relevant = ["doc3", "doc4"]
    recall = service.compute_recall_at_k(ranked, relevant, k=2)
    assert recall == 0.0, f"Should find no relevant docs, got recall={recall}"
    print("✓ Recall zero test passed")


def test_precision():
    """Test Precision@K computation."""
    service = SearchMetricsService()
    
    # Test 1: Perfect precision
    ranked = ["doc1", "doc2", "doc3"]
    relevant = ["doc1", "doc2", "doc3", "doc4"]
    precision = service.compute_precision_at_k(ranked, relevant, k=3)
    assert precision == 1.0, f"All results relevant, got precision={precision}"
    print("✓ Precision perfect test passed")
    
    # Test 2: Partial precision
    ranked = ["doc1", "doc2", "doc3", "doc4"]
    relevant = ["doc1", "doc3"]
    precision = service.compute_precision_at_k(ranked, relevant, k=4)
    assert abs(precision - 0.5) < 0.001, f"2/4 results relevant, got precision={precision}"
    print("✓ Precision partial test passed")
    
    # Test 3: Zero precision
    ranked = ["doc1", "doc2"]
    relevant = ["doc3", "doc4"]
    precision = service.compute_precision_at_k(ranked, relevant, k=2)
    assert precision == 0.0, f"No results relevant, got precision={precision}"
    print("✓ Precision zero test passed")


def test_mrr():
    """Test Mean Reciprocal Rank computation."""
    service = SearchMetricsService()
    
    # Test 1: First position
    ranked = ["doc1", "doc2", "doc3"]
    relevant = ["doc1"]
    mrr = service.compute_mean_reciprocal_rank(ranked, relevant)
    assert mrr == 1.0, f"First position should give MRR=1.0, got {mrr}"
    print("✓ MRR first position test passed")
    
    # Test 2: Second position
    ranked = ["doc1", "doc2", "doc3"]
    relevant = ["doc2"]
    mrr = service.compute_mean_reciprocal_rank(ranked, relevant)
    assert abs(mrr - 0.5) < 0.001, f"Second position should give MRR=0.5, got {mrr}"
    print("✓ MRR second position test passed")
    
    # Test 3: Third position
    ranked = ["doc1", "doc2", "doc3"]
    relevant = ["doc3"]
    mrr = service.compute_mean_reciprocal_rank(ranked, relevant)
    assert abs(mrr - 1/3) < 0.001, f"Third position should give MRR=0.333, got {mrr}"
    print("✓ MRR third position test passed")
    
    # Test 4: Not found
    ranked = ["doc1", "doc2"]
    relevant = ["doc3"]
    mrr = service.compute_mean_reciprocal_rank(ranked, relevant)
    assert mrr == 0.0, f"Not found should give MRR=0.0, got {mrr}"
    print("✓ MRR not found test passed")


def main():
    """Run all tests."""
    print("Testing SearchMetricsService...")
    print()
    
    test_ndcg()
    print()
    
    test_recall()
    print()
    
    test_precision()
    print()
    
    test_mrr()
    print()
    
    print("=" * 60)
    print("✓ All SearchMetricsService tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
