"""
Content-based recommendation tests.

Tests cosine similarity calculations for content-based recommendations.
"""

import numpy as np
from backend.tests.protocol import load_golden_data


# ============================================================================
# Golden Logic Tests
# ============================================================================


def test_content_based_recommendations():
    """
    Test content-based recommendations using cosine similarity.

    Verifies that given a query resource and candidate resources,
    the cosine similarity calculations produce the expected ranking.
    """
    # Load golden data
    golden_data = load_golden_data("recommendations_ranking")
    case = golden_data["content_similarity"]

    # Extract inputs
    query_resource = case["input"]["query_resource"]
    candidate_resources = case["input"]["candidate_resources"]
    expected_ranking = case["expected"]["ranked_resource_ids"]
    expected_scores = case["expected"]["similarity_scores"]
    tolerance = case["expected"]["tolerance"]

    # Calculate cosine similarity
    query_embedding = np.array(query_resource["embedding"])

    similarities = {}
    for candidate in candidate_resources:
        candidate_id = candidate["id"]
        candidate_embedding = np.array(candidate["embedding"])

        # Cosine similarity = dot product / (norm1 * norm2)
        dot_product = np.dot(query_embedding, candidate_embedding)
        norm_query = np.linalg.norm(query_embedding)
        norm_candidate = np.linalg.norm(candidate_embedding)

        similarity = dot_product / (norm_query * norm_candidate)
        similarities[candidate_id] = float(similarity)

    # Rank by similarity
    ranked_candidates = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    actual_ranking = [rid for rid, _ in ranked_candidates]

    # Verify ranking matches golden data
    assert actual_ranking == expected_ranking, (
        f"Ranking mismatch:\nExpected: {expected_ranking}\nActual: {actual_ranking}"
    )

    # Verify similarity scores are within tolerance
    for resource_id, actual_score in similarities.items():
        expected_score = expected_scores[str(resource_id)]
        assert abs(actual_score - expected_score) <= tolerance, (
            f"Similarity score mismatch for resource {resource_id}:\n"
            f"Expected: {expected_score}\n"
            f"Actual: {actual_score}\n"
            f"Difference: {abs(actual_score - expected_score)}"
        )
