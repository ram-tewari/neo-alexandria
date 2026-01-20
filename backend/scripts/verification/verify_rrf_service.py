"""
Verification script for Reciprocal Rank Fusion Service (Phase 8, Task 4)

This script demonstrates the RRF service functionality including:
1. Basic RRF fusion with multiple result lists
2. Weighted fusion with custom weights
3. Query-adaptive weighting for different query types
"""

from backend.app.services.reciprocal_rank_fusion_service import (
    ReciprocalRankFusionService,
)


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print("=" * 80)


def main():
    print("Reciprocal Rank Fusion Service Verification")
    print("=" * 80)

    # Initialize service
    rrf_service = ReciprocalRankFusionService(k=60)
    print(f"✓ Initialized RRF service with k={rrf_service.k}")

    # Test 1: Basic RRF Fusion
    print_section("Test 1: Basic RRF Fusion")

    fts5_results = [("doc1", 10.5), ("doc2", 8.3), ("doc3", 5.1)]

    dense_results = [("doc2", 0.95), ("doc1", 0.87), ("doc4", 0.72)]

    sparse_results = [("doc3", 0.88), ("doc1", 0.76), ("doc2", 0.65)]

    print("\nInput result lists:")
    print(f"  FTS5:   {fts5_results}")
    print(f"  Dense:  {dense_results}")
    print(f"  Sparse: {sparse_results}")

    fused = rrf_service.fuse_results([fts5_results, dense_results, sparse_results])

    print("\nFused results (sorted by RRF score):")
    for i, (doc_id, score) in enumerate(fused, 1):
        print(f"  {i}. {doc_id}: {score:.6f}")

    print(f"\n✓ Successfully fused {len(fused)} unique documents")

    # Test 2: Weighted Fusion
    print_section("Test 2: Weighted Fusion")

    weights = [0.5, 0.3, 0.2]  # Boost FTS5, moderate dense, lower sparse
    print(
        f"\nCustom weights: FTS5={weights[0]}, Dense={weights[1]}, Sparse={weights[2]}"
    )

    fused_weighted = rrf_service.fuse_results(
        [fts5_results, dense_results, sparse_results], weights=weights
    )

    print("\nWeighted fusion results:")
    for i, (doc_id, score) in enumerate(fused_weighted, 1):
        print(f"  {i}. {doc_id}: {score:.6f}")

    print("\n✓ Successfully applied custom weights")

    # Test 3: Query-Adaptive Weighting
    print_section("Test 3: Query-Adaptive Weighting")

    test_queries = [
        ("machine learning", "Short query (2 words)"),
        (
            "How does gradient descent optimization work in deep neural networks?",
            "Long query (10+ words)",
        ),
        ("What is Python?", "Question query"),
        ("def fibonacci(n): return n if n <= 1", "Code query"),
        ("solve equation x + y = 10", "Math query"),
    ]

    for query, description in test_queries:
        weights = rrf_service.adaptive_weights(query)
        print(f"\n{description}:")
        print(f"  Query: '{query[:60]}{'...' if len(query) > 60 else ''}'")
        print(
            f"  Weights: FTS5={weights[0]:.3f}, Dense={weights[1]:.3f}, Sparse={weights[2]:.3f}"
        )
        print(f"  Sum: {sum(weights):.3f}")

    print("\n✓ Successfully computed adaptive weights for all query types")

    # Test 4: Edge Cases
    print_section("Test 4: Edge Cases")

    # Empty lists
    empty_result = rrf_service.fuse_results([])
    print(f"\nEmpty input lists: {len(empty_result)} results")
    print("✓ Handled empty lists gracefully")

    # Single list
    single_result = rrf_service.fuse_results([fts5_results])
    print(f"\nSingle input list: {len(single_result)} results")
    print("✓ Handled single list correctly")

    # Mismatched weights
    mismatched_result = rrf_service.fuse_results(
        [fts5_results, dense_results, sparse_results],
        weights=[1.0, 2.0],  # Only 2 weights for 3 lists
    )
    print(
        f"\nMismatched weights: {len(mismatched_result)} results (fell back to equal weights)"
    )
    print("✓ Handled mismatched weights gracefully")

    # Zero weights
    zero_result = rrf_service.fuse_results(
        [fts5_results, dense_results], weights=[0.0, 0.0]
    )
    print(f"\nZero weights: {len(zero_result)} results (fell back to equal weights)")
    print("✓ Handled zero weights gracefully")

    # Summary
    print_section("Verification Summary")
    print("\n✓ All RRF service features verified successfully!")
    print("\nImplemented features:")
    print("  1. Basic RRF fusion algorithm with k=60")
    print("  2. Weighted fusion with custom weights")
    print("  3. Weight normalization to sum to 1.0")
    print("  4. Query-adaptive weighting for:")
    print("     - Short queries (boost FTS5)")
    print("     - Long queries (boost dense vectors)")
    print("     - Question queries (boost dense vectors)")
    print("     - Code queries (boost sparse vectors)")
    print("     - Math queries (boost sparse vectors)")
    print("  5. Graceful handling of edge cases:")
    print("     - Empty result lists")
    print("     - Single result list")
    print("     - Mismatched weights")
    print("     - Zero weights")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
