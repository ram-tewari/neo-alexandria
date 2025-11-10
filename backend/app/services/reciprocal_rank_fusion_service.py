"""
Neo Alexandria 2.0 - Reciprocal Rank Fusion Service (Phase 8)

This module provides Reciprocal Rank Fusion (RRF) for merging results from multiple
retrieval methods (FTS5, dense vectors, sparse vectors). RRF is a score-agnostic
fusion algorithm that works with heterogeneous scoring functions.

Related files:
- app/services/search_service.py: Search orchestration
- app/services/sparse_embedding_service.py: Sparse vector search
- app/services/hybrid_search_methods.py: Dense vector search

Features:
- RRF algorithm for merging ranked result lists
- Weighted fusion with custom weights per retrieval method
- Query-adaptive weighting based on query characteristics
- Graceful handling of empty result lists
- Normalization of weights to sum to 1.0

References:
- Cormack, G. V., Clarke, C. L., & Buettcher, S. (2009). Reciprocal rank fusion
  outperforms condorcet and individual rank learning methods. SIGIR '09.
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from typing import List, Tuple, Dict, Optional

logger = logging.getLogger(__name__)


class ReciprocalRankFusionService:
    """Service for merging search results using Reciprocal Rank Fusion.
    
    RRF computes a fusion score for each document based on its ranks across
    multiple result lists using the formula:
        RRF_score(d) = Σ [weight_i / (k + rank_i(d))]
    
    where:
    - rank_i(d) = rank of document d in result list i (0-indexed)
    - weight_i = importance weight for result list i
    - k = constant (typically 60) that reduces impact of high ranks
    """
    
    def __init__(self, k: int = 60):
        """Initialize the RRF service.
        
        Args:
            k: RRF constant parameter (default: 60). Higher values reduce the
               impact of rank differences, making the fusion more democratic.
        """
        self.k = k
    
    def fuse_results(
        self,
        result_lists: List[List[Tuple[str, float]]],
        weights: Optional[List[float]] = None
    ) -> List[Tuple[str, float]]:
        """Merge multiple ranked lists using Reciprocal Rank Fusion.
        
        Args:
            result_lists: List of result lists, where each result list contains
                         tuples of (resource_id, score). The score is ignored
                         in RRF; only the rank (position) matters.
            weights: Optional list of weights for each result list. If None,
                    equal weights (1.0) are used. Weights are normalized to sum to 1.0.
        
        Returns:
            List of (resource_id, rrf_score) tuples sorted by RRF score descending.
            Returns empty list if all input lists are empty.
        
        Example:
            >>> rrf = ReciprocalRankFusionService(k=60)
            >>> fts5_results = [("doc1", 10.5), ("doc2", 8.3), ("doc3", 5.1)]
            >>> dense_results = [("doc2", 0.95), ("doc1", 0.87), ("doc4", 0.72)]
            >>> sparse_results = [("doc3", 0.88), ("doc1", 0.76), ("doc2", 0.65)]
            >>> merged = rrf.fuse_results([fts5_results, dense_results, sparse_results])
            >>> # doc1 appears in all three lists with good ranks -> high RRF score
        """
        # Handle empty input
        if not result_lists or all(not lst for lst in result_lists):
            logger.debug("All result lists are empty, returning empty results")
            return []
        
        # Set default weights if not provided
        if weights is None:
            weights = [1.0] * len(result_lists)
        
        # Validate weights length
        if len(weights) != len(result_lists):
            logger.warning(
                f"Weights length ({len(weights)}) doesn't match result lists length "
                f"({len(result_lists)}). Using equal weights."
            )
            weights = [1.0] * len(result_lists)
        
        # Normalize weights to sum to 1.0
        weight_sum = sum(weights)
        if weight_sum > 0:
            weights = [w / weight_sum for w in weights]
        else:
            logger.warning("All weights are zero, using equal weights")
            weights = [1.0 / len(result_lists)] * len(result_lists)
        
        # Compute RRF scores
        rrf_scores: Dict[str, float] = defaultdict(float)
        
        for result_list, weight in zip(result_lists, weights):
            for rank, (resource_id, _score) in enumerate(result_list):
                # RRF formula: weight / (k + rank)
                # rank is 0-indexed (first result has rank 0)
                rrf_score = weight / (self.k + rank)
                rrf_scores[resource_id] += rrf_score
        
        # Sort by RRF score descending
        sorted_results = sorted(
            rrf_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        logger.debug(
            f"RRF fusion: merged {len(result_lists)} lists with "
            f"{sum(len(lst) for lst in result_lists)} total results into "
            f"{len(sorted_results)} unique documents"
        )
        
        return sorted_results
    
    def adaptive_weights(
        self,
        query: str,
        result_lists: Optional[List[List[Tuple[str, float]]]] = None
    ) -> List[float]:
        """Compute query-adaptive weights for RRF fusion.
        
        Analyzes query characteristics and adjusts retrieval method weights:
        - Short queries (1-3 words): Boost FTS5 (keyword matching)
        - Long queries (>10 words): Boost dense vectors (semantic understanding)
        - Technical queries (code, math): Boost sparse vectors (learned keywords)
        - Question queries (who/what/when/where/why/how): Boost dense vectors
        
        Args:
            query: Search query text
            result_lists: Optional list of result lists (for future use, e.g.,
                         analyzing result overlap). Currently unused.
        
        Returns:
            List of three weights [fts5_weight, dense_weight, sparse_weight]
            normalized to sum to 1.0.
        
        Example:
            >>> rrf = ReciprocalRankFusionService()
            >>> rrf.adaptive_weights("machine learning")  # Short query
            [0.45, 0.30, 0.25]  # FTS5 boosted
            >>> rrf.adaptive_weights("How does gradient descent work in neural networks?")
            [0.20, 0.50, 0.30]  # Dense boosted (long + question)
            >>> rrf.adaptive_weights("def fibonacci(n): return n if n <= 1")
            [0.25, 0.25, 0.50]  # Sparse boosted (code)
        """
        query = (query or "").strip()
        if not query:
            # Default equal weights (normalized)
            return [1.0 / 3, 1.0 / 3, 1.0 / 3]
        
        # Start with baseline weights
        fts5_weight = 1.0
        dense_weight = 1.0
        sparse_weight = 1.0
        
        # Count words (simple whitespace split)
        words = query.split()
        word_count = len(words)
        
        # 1. Short queries (1-3 words): Boost FTS5
        if word_count <= 3:
            fts5_weight *= 1.5
            dense_weight *= 0.8
            logger.debug(f"Short query detected ({word_count} words), boosting FTS5")
        
        # 2. Long queries (>10 words): Boost dense vectors
        elif word_count > 10:
            dense_weight *= 1.5
            fts5_weight *= 0.8
            logger.debug(f"Long query detected ({word_count} words), boosting dense vectors")
        
        # 3. Question queries: Boost dense vectors
        question_words = ['who', 'what', 'when', 'where', 'why', 'how']
        if any(query.lower().startswith(qw) for qw in question_words):
            dense_weight *= 1.3
            logger.debug("Question query detected, boosting dense vectors")
        
        # 4. Technical queries: Boost sparse vectors
        # Detect code patterns: function calls, operators, brackets, etc.
        code_patterns = [
            r'\b(def|class|function|var|let|const|import|from|return)\b',  # Keywords
            r'[(){}\[\]]',  # Brackets
            r'[=<>!]+',  # Operators
            r'\b\w+\.\w+\b',  # Method calls (e.g., obj.method)
            r'\b\w+\(\)',  # Function calls
        ]
        
        # Detect math patterns: equations, symbols
        math_patterns = [
            r'[+\-*/^=]',  # Math operators
            r'\b(sum|integral|derivative|equation|formula)\b',  # Math terms
            r'[∫∑∏√∂∇]',  # Math symbols
        ]
        
        is_technical = any(re.search(pattern, query, re.IGNORECASE) for pattern in code_patterns)
        is_math = any(re.search(pattern, query, re.IGNORECASE) for pattern in math_patterns)
        
        if is_technical or is_math:
            sparse_weight *= 1.5
            dense_weight *= 0.9
            logger.debug(
                f"Technical query detected (code={is_technical}, math={is_math}), "
                "boosting sparse vectors"
            )
        
        # Normalize weights to sum to 1.0
        weights = [fts5_weight, dense_weight, sparse_weight]
        weight_sum = sum(weights)
        if weight_sum > 0:
            weights = [w / weight_sum for w in weights]
        else:
            # Fallback to equal weights
            weights = [1.0 / 3, 1.0 / 3, 1.0 / 3]
        
        logger.debug(
            f"Adaptive weights for query '{query[:50]}...': "
            f"FTS5={weights[0]:.3f}, Dense={weights[1]:.3f}, Sparse={weights[2]:.3f}"
        )
        
        return weights
