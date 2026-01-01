"""
Search Module Tests - Hybrid Search and RRF Fusion

Tests for Reciprocal Rank Fusion (RRF) algorithm using Golden Data.
All test expectations are defined in tests/golden_data/search_ranking.json.

NO inline expected values - all assertions use Golden Data.
"""

from typing import Dict, List, Tuple
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tests.protocol import assert_ranking_against_golden, load_golden_data


# ============================================================================
# RRF Implementation (Minimal for Testing)
# ============================================================================

class ReciprocalRankFusionService:
    """
    Reciprocal Rank Fusion (RRF) service for combining multiple ranked lists.
    
    RRF formula: score(d) = sum over all rankers r of: 1 / (k + rank_r(d))
    where k is a constant (typically 60) and rank_r(d) is the rank of document d in ranker r.
    """
    
    def __init__(self, k: int = 60):
        """
        Initialize RRF service.
        
        Args:
            k: Constant for RRF formula (default: 60)
        """
        self.k = k
    
    def fuse(
        self,
        ranked_lists: List[List[str]],
        weights: List[float] = None
    ) -> Tuple[List[str], Dict[str, float]]:
        """
        Fuse multiple ranked lists using Reciprocal Rank Fusion.
        
        Args:
            ranked_lists: List of ranked document ID lists
            weights: Optional weights for each ranker (default: equal weights)
            
        Returns:
            Tuple of (ranked_ids, scores) where:
            - ranked_ids: Fused ranking of document IDs
            - scores: RRF scores for each document
        """
        if not ranked_lists:
            return [], {}
        
        # Filter out empty lists
        non_empty_lists = [lst for lst in ranked_lists if lst]
        if not non_empty_lists:
            return [], {}
        
        # Default to equal weights
        if weights is None:
            weights = [1.0] * len(ranked_lists)
        
        # Calculate RRF scores and track best rank + earliest ranker for tie-breaking
        scores: Dict[str, float] = {}
        best_rank: Dict[str, int] = {}
        earliest_ranker: Dict[str, int] = {}
        
        for ranker_idx, ranked_list in enumerate(ranked_lists):
            if not ranked_list:  # Skip empty lists
                continue
            weight = weights[ranker_idx]
            for position, doc_id in enumerate(ranked_list):  # 0-indexed positions
                rank = position  # Use 0-indexed rank (position 0 = rank 0)
                
                # Track best (minimum) rank and earliest ranker for tie-breaking
                if doc_id not in best_rank or rank < best_rank[doc_id]:
                    best_rank[doc_id] = rank
                    earliest_ranker[doc_id] = ranker_idx
                elif rank == best_rank[doc_id] and ranker_idx < earliest_ranker[doc_id]:
                    earliest_ranker[doc_id] = ranker_idx
                
                # RRF formula: 1 / (k + rank)
                # rank is 0-indexed (first position = 0)
                rrf_score = weight / (self.k + rank)
                scores[doc_id] = scores.get(doc_id, 0.0) + rrf_score
        
        # Sort by score (descending), then by best rank (ascending), then by earliest ranker (ascending), then by doc_id
        ranked_ids = sorted(scores.keys(), key=lambda x: (-scores[x], best_rank[x], earliest_ranker[x], x))
        
        return ranked_ids, scores


# ============================================================================
# Test Cases
# ============================================================================

def test_rrf_fusion_basic():
    """
    Test basic RRF fusion with three result lists.
    
    Uses Golden Data case: rrf_fusion_scenario_1
    
    Input lists:
    - Dense: [A, B, C]
    - Sparse: [C, A, D]
    - Keyword: [B, A, E]
    
    Expected ranking from Golden Data: [A, B, C, D, E]
    
    **Validates: Requirements 9.2, 9.3, 9.4, 9.5**
    """
    # Load Golden Data to get inputs
    golden_data = load_golden_data("search_ranking")
    test_case = golden_data["rrf_fusion_scenario_1"]
    
    # Get inputs from Golden Data
    inputs = test_case["inputs"]
    dense_results = inputs["dense_results"]
    sparse_results = inputs["sparse_results"]
    keyword_results = inputs["keyword_results"]
    
    # Execute RRF fusion
    rrf_service = ReciprocalRankFusionService(k=60)
    ranked_ids, scores = rrf_service.fuse([
        dense_results,
        sparse_results,
        keyword_results
    ])
    
    # Assert against Golden Data
    # This will compare both the ranking order and the scores
    assert_ranking_against_golden(
        "search_ranking",
        "rrf_fusion_scenario_1",
        ranked_ids,
        check_order=True
    )
    
    # Also verify scores match (within tolerance)
    expected_scores = test_case["scores"]
    for doc_id, expected_score in expected_scores.items():
        actual_score = scores.get(doc_id, 0.0)
        tolerance = 0.0001
        assert abs(actual_score - expected_score) < tolerance, (
            f"Score mismatch for {doc_id}: "
            f"expected {expected_score}, got {actual_score}"
        )


def test_rrf_fusion_empty_lists():
    """
    Test RRF fusion with empty input lists.
    
    Uses Golden Data case: rrf_fusion_empty_lists
    
    Input lists: All empty
    Expected ranking: Empty list
    
    **Validates: Requirements 9.2, 9.3, 9.4, 9.5**
    """
    # Load Golden Data to get inputs
    golden_data = load_golden_data("search_ranking")
    test_case = golden_data["rrf_fusion_empty_lists"]
    
    # Get inputs from Golden Data
    inputs = test_case["inputs"]
    dense_results = inputs["dense_results"]
    sparse_results = inputs["sparse_results"]
    keyword_results = inputs["keyword_results"]
    
    # Execute RRF fusion
    rrf_service = ReciprocalRankFusionService(k=60)
    ranked_ids, scores = rrf_service.fuse([
        dense_results,
        sparse_results,
        keyword_results
    ])
    
    # Assert against Golden Data
    assert_ranking_against_golden(
        "search_ranking",
        "rrf_fusion_empty_lists",
        ranked_ids,
        check_order=True
    )
    
    # Verify scores are also empty
    assert scores == {}, f"Expected empty scores, got {scores}"


def test_rrf_fusion_single_list():
    """
    Test RRF fusion with only one non-empty list.
    
    Uses Golden Data case: rrf_fusion_single_list
    
    Input lists:
    - Dense: [X, Y, Z]
    - Sparse: []
    - Keyword: []
    
    Expected ranking from Golden Data: [X, Y, Z]
    
    **Validates: Requirements 9.2, 9.3, 9.4, 9.5**
    """
    # Load Golden Data to get inputs
    golden_data = load_golden_data("search_ranking")
    test_case = golden_data["rrf_fusion_single_list"]
    
    # Get inputs from Golden Data
    inputs = test_case["inputs"]
    dense_results = inputs["dense_results"]
    sparse_results = inputs["sparse_results"]
    keyword_results = inputs["keyword_results"]
    
    # Execute RRF fusion
    rrf_service = ReciprocalRankFusionService(k=60)
    ranked_ids, scores = rrf_service.fuse([
        dense_results,
        sparse_results,
        keyword_results
    ])
    
    # Assert against Golden Data
    assert_ranking_against_golden(
        "search_ranking",
        "rrf_fusion_single_list",
        ranked_ids,
        check_order=True
    )
    
    # Also verify scores match (within tolerance)
    expected_scores = test_case["scores"]
    for doc_id, expected_score in expected_scores.items():
        actual_score = scores.get(doc_id, 0.0)
        tolerance = 0.0001
        assert abs(actual_score - expected_score) < tolerance, (
            f"Score mismatch for {doc_id}: "
            f"expected {expected_score}, got {actual_score}"
        )
