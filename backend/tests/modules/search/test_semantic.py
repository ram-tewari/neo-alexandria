"""
Search Module Tests - Semantic Search

Tests for embedding-based semantic search using Golden Data.
All test expectations are defined in tests/golden_data/semantic_search.json.

NO inline expected values - all assertions use Golden Data.

**Validates: Requirements 8.2, 8.3**
"""

import sys
from pathlib import Path
from typing import List, Tuple
import numpy as np

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tests.protocol import assert_ranking_against_golden, load_golden_data


# ============================================================================
# Semantic Search Implementation (Minimal for Testing)
# ============================================================================

class SemanticSearchService:
    """
    Semantic search service using embedding-based similarity.
    
    Uses cosine similarity to rank documents by semantic relevance.
    """
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not vec1 or not vec2:
            return 0.0
        
        # Convert to numpy arrays
        a = np.array(vec1)
        b = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def search(
        self,
        query_embedding: List[float],
        resources: List[dict]
    ) -> Tuple[List[str], dict]:
        """
        Search resources by semantic similarity.
        
        Args:
            query_embedding: Query embedding vector
            resources: List of resource dicts with 'id' and 'embedding'
            
        Returns:
            Tuple of (ranked_ids, similarity_scores)
        """
        if not query_embedding or not resources:
            return [], {}
        
        # Calculate similarity scores
        scores = {}
        for resource in resources:
            resource_id = resource['id']
            resource_embedding = resource.get('embedding', [])
            
            if resource_embedding:
                similarity = self.cosine_similarity(query_embedding, resource_embedding)
                scores[resource_id] = similarity
        
        # Sort by similarity (descending)
        ranked_ids = sorted(scores.keys(), key=lambda x: -scores[x])
        
        return ranked_ids, scores


# ============================================================================
# Test Cases
# ============================================================================

def test_embedding_similarity_basic():
    """
    Test basic semantic similarity search with embedding vectors.
    
    Uses Golden Data case: embedding_similarity_basic
    
    Verifies:
    - Cosine similarity calculation
    - Correct ranking by similarity score
    - Resources ranked from most to least similar
    
    **Validates: Requirements 8.2, 8.3**
    """
    # Load Golden Data
    golden_data = load_golden_data("semantic_search")
    test_case = golden_data["embedding_similarity_basic"]
    
    # Get inputs from Golden Data
    query_embedding = test_case["query_embedding"]
    resources = test_case["resources"]
    
    # Execute semantic search
    service = SemanticSearchService()
    ranked_ids, scores = service.search(query_embedding, resources)
    
    # Assert ranking against Golden Data
    assert_ranking_against_golden(
        "semantic_search",
        "embedding_similarity_basic",
        ranked_ids,
        check_order=True
    )
    
    # Verify similarity scores (with tolerance for floating point)
    expected_scores = test_case["similarity_scores"]
    for resource_id, expected_score in expected_scores.items():
        actual_score = scores.get(resource_id, 0.0)
        tolerance = 0.01  # Allow 1% difference for floating point
        assert abs(actual_score - expected_score) < tolerance, (
            f"Similarity score mismatch for {resource_id}: "
            f"expected {expected_score}, got {actual_score}"
        )


def test_embedding_empty_query():
    """
    Test semantic search with empty query embedding.
    
    Uses Golden Data case: embedding_empty_query
    
    Verifies:
    - Empty query returns no results
    - No errors with empty input
    
    **Validates: Requirements 8.2, 8.3**
    """
    # Load Golden Data
    golden_data = load_golden_data("semantic_search")
    test_case = golden_data["embedding_empty_query"]
    
    # Get inputs from Golden Data
    query_embedding = test_case["query_embedding"]
    resources = test_case["resources"]
    
    # Execute semantic search
    service = SemanticSearchService()
    ranked_ids, scores = service.search(query_embedding, resources)
    
    # Assert ranking against Golden Data
    assert_ranking_against_golden(
        "semantic_search",
        "embedding_empty_query",
        ranked_ids,
        check_order=True
    )
    
    # Verify scores are empty
    assert scores == {}, f"Expected empty scores, got {scores}"


def test_embedding_no_results():
    """
    Test semantic search with no matching resources.
    
    Uses Golden Data case: embedding_no_results
    
    Verifies:
    - Query with no resources returns empty results
    - No errors with empty resource list
    
    **Validates: Requirements 8.2, 8.3**
    """
    # Load Golden Data
    golden_data = load_golden_data("semantic_search")
    test_case = golden_data["embedding_no_results"]
    
    # Get inputs from Golden Data
    query_embedding = test_case["query_embedding"]
    resources = test_case["resources"]
    
    # Execute semantic search
    service = SemanticSearchService()
    ranked_ids, scores = service.search(query_embedding, resources)
    
    # Assert ranking against Golden Data
    assert_ranking_against_golden(
        "semantic_search",
        "embedding_no_results",
        ranked_ids,
        check_order=True
    )
    
    # Verify scores are empty
    assert scores == {}, f"Expected empty scores, got {scores}"


def test_embedding_ranking_order():
    """
    Test correct ranking order by similarity score.
    
    Uses Golden Data case: embedding_ranking_order
    
    Verifies:
    - Resources ranked from highest to lowest similarity
    - Correct ordering with multiple similar resources
    - Dissimilar resources ranked lower
    
    **Validates: Requirements 8.2, 8.3**
    """
    # Load Golden Data
    golden_data = load_golden_data("semantic_search")
    test_case = golden_data["embedding_ranking_order"]
    
    # Get inputs from Golden Data
    query_embedding = test_case["query_embedding"]
    resources = test_case["resources"]
    
    # Execute semantic search
    service = SemanticSearchService()
    ranked_ids, scores = service.search(query_embedding, resources)
    
    # Assert ranking against Golden Data
    assert_ranking_against_golden(
        "semantic_search",
        "embedding_ranking_order",
        ranked_ids,
        check_order=True
    )
    
    # Verify similarity scores (with tolerance)
    expected_scores = test_case["similarity_scores"]
    for resource_id, expected_score in expected_scores.items():
        actual_score = scores.get(resource_id, 0.0)
        tolerance = 0.01
        assert abs(actual_score - expected_score) < tolerance, (
            f"Similarity score mismatch for {resource_id}: "
            f"expected {expected_score}, got {actual_score}"
        )
    
    # Verify scores are in descending order
    score_values = [scores[rid] for rid in ranked_ids]
    assert score_values == sorted(score_values, reverse=True), (
        "Scores are not in descending order"
    )
