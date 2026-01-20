"""
Search Metrics Service

Provides information retrieval metrics for evaluating search quality.
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class SearchMetricsService:
    """
    Service for computing information retrieval metrics.

    Supports:
    - nDCG (Normalized Discounted Cumulative Gain)
    - Recall@K
    - Precision@K
    - MRR (Mean Reciprocal Rank)
    """

    def compute_ndcg(
        self,
        ranked_results: List[str],
        relevance_judgments: Dict[str, int],
        k: int = 20,
    ) -> float:
        """
        Compute Normalized Discounted Cumulative Gain at K.

        Args:
            ranked_results: List of document IDs in ranked order
            relevance_judgments: Dict mapping document IDs to relevance scores (0-3)
            k: Cutoff position (default 20)

        Returns:
            nDCG@K score (0.0 to 1.0)
        """
        import math

        # Compute DCG@K
        dcg = 0.0
        for i, doc_id in enumerate(ranked_results[:k], start=1):
            relevance = relevance_judgments.get(doc_id, 0)
            dcg += (2**relevance - 1) / math.log2(i + 1)

        # Compute ideal DCG@K
        ideal_relevances = sorted(relevance_judgments.values(), reverse=True)[:k]
        idcg = 0.0
        for i, relevance in enumerate(ideal_relevances, start=1):
            idcg += (2**relevance - 1) / math.log2(i + 1)

        # Normalize
        if idcg == 0:
            return 0.0

        return dcg / idcg

    def compute_recall_at_k(
        self, ranked_results: List[str], relevant_docs: List[str], k: int = 20
    ) -> float:
        """
        Compute Recall@K.

        Args:
            ranked_results: List of document IDs in ranked order
            relevant_docs: List of relevant document IDs
            k: Cutoff position (default 20)

        Returns:
            Recall@K score (0.0 to 1.0)
        """
        if not relevant_docs:
            return 0.0

        retrieved_relevant = set(ranked_results[:k]) & set(relevant_docs)
        return len(retrieved_relevant) / len(relevant_docs)

    def compute_precision_at_k(
        self, ranked_results: List[str], relevant_docs: List[str], k: int = 20
    ) -> float:
        """
        Compute Precision@K.

        Args:
            ranked_results: List of document IDs in ranked order
            relevant_docs: List of relevant document IDs
            k: Cutoff position (default 20)

        Returns:
            Precision@K score (0.0 to 1.0)
        """
        if not ranked_results[:k]:
            return 0.0

        retrieved_relevant = set(ranked_results[:k]) & set(relevant_docs)
        return len(retrieved_relevant) / min(k, len(ranked_results))

    def compute_mean_reciprocal_rank(
        self, ranked_results: List[str], relevant_docs: List[str]
    ) -> float:
        """
        Compute Mean Reciprocal Rank.

        Args:
            ranked_results: List of document IDs in ranked order
            relevant_docs: List of relevant document IDs

        Returns:
            MRR score (0.0 to 1.0)
        """
        for i, doc_id in enumerate(ranked_results, start=1):
            if doc_id in relevant_docs:
                return 1.0 / i

        return 0.0
