"""
Verification script for SearchMetricsService

Demonstrates all four metrics with realistic examples.
"""

import sys
sys.path.insert(0, 'app/services')
from search_metrics_service import SearchMetricsService


def main():
    """Demonstrate SearchMetricsService functionality."""
    service = SearchMetricsService()
    
    print("=" * 70)
    print("SearchMetricsService Verification")
    print("=" * 70)
    print()
    
    # Example 1: Comparing two search methods
    print("Example 1: Comparing Two Search Methods")
    print("-" * 70)
    
    # Baseline method results
    baseline_results = ["doc3", "doc1", "doc5", "doc2", "doc4"]
    
    # Enhanced method results
    enhanced_results = ["doc1", "doc2", "doc3", "doc4", "doc5"]
    
    # Ground truth
    relevant_docs = ["doc1", "doc2", "doc3"]
    relevance_judgments = {
        "doc1": 3,  # Highly relevant
        "doc2": 2,  # Relevant
        "doc3": 2,  # Relevant
        "doc4": 0,  # Not relevant
        "doc5": 0   # Not relevant
    }
    
    # Compute metrics for baseline
    baseline_ndcg = service.compute_ndcg(baseline_results, relevance_judgments, k=5)
    baseline_recall = service.compute_recall_at_k(baseline_results, relevant_docs, k=5)
    baseline_precision = service.compute_precision_at_k(baseline_results, relevant_docs, k=5)
    baseline_mrr = service.compute_mean_reciprocal_rank(baseline_results, relevant_docs)
    
    # Compute metrics for enhanced
    enhanced_ndcg = service.compute_ndcg(enhanced_results, relevance_judgments, k=5)
    enhanced_recall = service.compute_recall_at_k(enhanced_results, relevant_docs, k=5)
    enhanced_precision = service.compute_precision_at_k(enhanced_results, relevant_docs, k=5)
    enhanced_mrr = service.compute_mean_reciprocal_rank(enhanced_results, relevant_docs)
    
    print("Baseline Method:")
    print(f"  nDCG@5:      {baseline_ndcg:.3f}")
    print(f"  Recall@5:    {baseline_recall:.3f}")
    print(f"  Precision@5: {baseline_precision:.3f}")
    print(f"  MRR:         {baseline_mrr:.3f}")
    print()
    
    print("Enhanced Method:")
    print(f"  nDCG@5:      {enhanced_ndcg:.3f}")
    print(f"  Recall@5:    {enhanced_recall:.3f}")
    print(f"  Precision@5: {enhanced_precision:.3f}")
    print(f"  MRR:         {enhanced_mrr:.3f}")
    print()
    
    # Calculate improvements
    ndcg_improvement = ((enhanced_ndcg - baseline_ndcg) / baseline_ndcg) * 100
    print("Improvements:")
    print(f"  nDCG improvement: {ndcg_improvement:+.1f}%")
    print(f"  Recall improvement: {(enhanced_recall - baseline_recall):+.3f}")
    print(f"  Precision improvement: {(enhanced_precision - baseline_precision):+.3f}")
    print(f"  MRR improvement: {(enhanced_mrr - baseline_mrr):+.3f}")
    print()
    
    # Example 2: Evaluating search quality at different K values
    print("Example 2: Metrics at Different K Values")
    print("-" * 70)
    
    results = ["doc1", "doc2", "doc5", "doc3", "doc6", "doc4", "doc7", "doc8"]
    relevant = ["doc1", "doc3", "doc4", "doc9"]
    
    print(f"Results: {results}")
    print(f"Relevant docs: {relevant}")
    print()
    
    for k in [3, 5, 10]:
        recall = service.compute_recall_at_k(results, relevant, k=k)
        precision = service.compute_precision_at_k(results, relevant, k=k)
        print(f"K={k:2d}:  Recall={recall:.3f}  Precision={precision:.3f}")
    print()
    
    # Example 3: Perfect vs Poor Ranking
    print("Example 3: Perfect vs Poor Ranking")
    print("-" * 70)
    
    judgments = {
        "doc1": 3,
        "doc2": 2,
        "doc3": 1,
        "doc4": 0,
        "doc5": 0
    }
    
    perfect_ranking = ["doc1", "doc2", "doc3", "doc4", "doc5"]
    poor_ranking = ["doc5", "doc4", "doc3", "doc2", "doc1"]
    
    perfect_ndcg = service.compute_ndcg(perfect_ranking, judgments, k=5)
    poor_ndcg = service.compute_ndcg(poor_ranking, judgments, k=5)
    
    print(f"Perfect ranking: {perfect_ranking}")
    print(f"  nDCG@5: {perfect_ndcg:.3f}")
    print()
    print(f"Poor ranking: {poor_ranking}")
    print(f"  nDCG@5: {poor_ndcg:.3f}")
    print()
    print(f"Quality difference: {(perfect_ndcg - poor_ndcg):.3f}")
    print()
    
    # Example 4: MRR for different first relevant positions
    print("Example 4: MRR for Different First Relevant Positions")
    print("-" * 70)
    
    for position in range(1, 6):
        # Create results where first relevant doc is at 'position'
        results = [f"irrelevant_{i}" for i in range(position - 1)]
        results.append("relevant_doc")
        results.extend([f"irrelevant_{i}" for i in range(position, 10)])
        
        mrr = service.compute_mean_reciprocal_rank(results, ["relevant_doc"])
        print(f"First relevant at position {position}: MRR = {mrr:.3f} (1/{position})")
    print()
    
    print("=" * 70)
    print("✓ SearchMetricsService verification complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
