"""
Search Metrics Service

Provides information retrieval metrics for evaluating search quality:
- nDCG (Normalized Discounted Cumulative Gain)
- Recall@K
- Precision@K
- Mean Reciprocal Rank (MRR)

These metrics are used to measure and compare search quality across different
retrieval methods and configurations.
"""

import math
from typing import Dict, List


class SearchMetricsService:
    """Service for computing information retrieval metrics."""
    
    def compute_ndcg(
        self,
        ranked_results: List[str],
        relevance_judgments: Dict[str, int],
        k: int = 20
    ) -> float:
        """
        Compute Normalized Discounted Cumulative Gain at K.
        
        nDCG measures ranking quality by considering both the relevance of documents
        and their positions in the ranking. Higher scores indicate better ranking.
        
        Args:
            ranked_results: List of document IDs in ranked order
            relevance_judgments: Dict mapping document IDs to relevance scores (0-3)
                                0 = not relevant
                                1 = marginally relevant
                                2 = relevant
                                3 = highly relevant
            k: Number of top results to consider (default: 20)
            
        Returns:
            nDCG@k score in range [0, 1], where 1 is perfect ranking
            
        Formula:
            DCG@k = Σ [(2^rel_i - 1) / log2(i + 2)]
            nDCG@k = DCG@k / IDCG@k
            
        Example:
            >>> service = SearchMetricsService()
            >>> ranked = ["doc1", "doc2", "doc3"]
            >>> judgments = {"doc1": 3, "doc2": 2, "doc3": 0}
            >>> service.compute_ndcg(ranked, judgments, k=3)
            0.95  # High score because relevant docs are ranked first
        """
        if not ranked_results or not relevance_judgments:
            return 0.0
        
        # Compute DCG (Discounted Cumulative Gain)
        dcg = 0.0
        for i, doc_id in enumerate(ranked_results[:k]):
            relevance = relevance_judgments.get(doc_id, 0)
            # Formula: (2^rel - 1) / log2(i + 2)
            # i + 2 because: i is 0-indexed, and we want log2(2) for first position
            dcg += (2 ** relevance - 1) / math.log2(i + 2)
        
        # Compute IDCG (Ideal DCG) - DCG of perfect ranking
        # Sort relevance scores in descending order
        ideal_relevances = sorted(relevance_judgments.values(), reverse=True)[:k]
        idcg = 0.0
        for i, relevance in enumerate(ideal_relevances):
            idcg += (2 ** relevance - 1) / math.log2(i + 2)
        
        # Avoid division by zero
        if idcg == 0.0:
            return 0.0
        
        # Normalize DCG by IDCG
        ndcg = dcg / idcg
        return ndcg
    
    def compute_recall_at_k(
        self,
        ranked_results: List[str],
        relevant_docs: List[str],
        k: int = 20
    ) -> float:
        """
        Compute Recall at K.
        
        Recall@K measures what fraction of all relevant documents appear in the
        top K results. It indicates retrieval completeness.
        
        Args:
            ranked_results: List of document IDs in ranked order
            relevant_docs: List of all relevant document IDs
            k: Number of top results to consider (default: 20)
            
        Returns:
            Recall@k score in range [0, 1]
            
        Formula:
            Recall@k = (# relevant docs in top-k) / (total # relevant docs)
            
        Example:
            >>> service = SearchMetricsService()
            >>> ranked = ["doc1", "doc2", "doc3", "doc4"]
            >>> relevant = ["doc1", "doc3", "doc5"]
            >>> service.compute_recall_at_k(ranked, relevant, k=4)
            0.667  # Found 2 out of 3 relevant docs
        """
        if not relevant_docs:
            return 0.0
        
        # Get top-k results
        top_k = set(ranked_results[:k])
        relevant_set = set(relevant_docs)
        
        # Count how many relevant docs are in top-k
        relevant_in_top_k = len(top_k & relevant_set)
        
        # Recall = relevant found / total relevant
        recall = relevant_in_top_k / len(relevant_set)
        return recall
    
    def compute_precision_at_k(
        self,
        ranked_results: List[str],
        relevant_docs: List[str],
        k: int = 20
    ) -> float:
        """
        Compute Precision at K.
        
        Precision@K measures what fraction of the top K results are relevant.
        It indicates retrieval accuracy.
        
        Args:
            ranked_results: List of document IDs in ranked order
            relevant_docs: List of all relevant document IDs
            k: Number of top results to consider (default: 20)
            
        Returns:
            Precision@k score in range [0, 1]
            
        Formula:
            Precision@k = (# relevant docs in top-k) / k
            
        Example:
            >>> service = SearchMetricsService()
            >>> ranked = ["doc1", "doc2", "doc3", "doc4"]
            >>> relevant = ["doc1", "doc3"]
            >>> service.compute_precision_at_k(ranked, relevant, k=4)
            0.5  # 2 out of 4 results are relevant
        """
        if k == 0:
            return 0.0
        
        # Get top-k results
        top_k = set(ranked_results[:k])
        relevant_set = set(relevant_docs)
        
        # Count how many results in top-k are relevant
        relevant_in_top_k = len(top_k & relevant_set)
        
        # Precision = relevant found / k
        precision = relevant_in_top_k / k
        return precision
    
    def compute_mean_reciprocal_rank(
        self,
        ranked_results: List[str],
        relevant_docs: List[str]
    ) -> float:
        """
        Compute Mean Reciprocal Rank.
        
        MRR measures how quickly a relevant result appears in the ranking.
        It's the reciprocal of the rank of the first relevant document.
        
        Args:
            ranked_results: List of document IDs in ranked order
            relevant_docs: List of all relevant document IDs
            
        Returns:
            MRR score in range [0, 1]
            
        Formula:
            MRR = 1 / (rank of first relevant document)
            
        Example:
            >>> service = SearchMetricsService()
            >>> ranked = ["doc1", "doc2", "doc3", "doc4"]
            >>> relevant = ["doc3", "doc5"]
            >>> service.compute_mean_reciprocal_rank(ranked, relevant)
            0.333  # First relevant doc is at position 3, so 1/3
        """
        if not relevant_docs:
            return 0.0
        
        relevant_set = set(relevant_docs)
        
        # Find rank of first relevant document (1-indexed)
        for i, doc_id in enumerate(ranked_results):
            if doc_id in relevant_set:
                # Rank is 1-indexed, so add 1 to 0-indexed position
                rank = i + 1
                return 1.0 / rank
        
        # No relevant document found
        return 0.0
