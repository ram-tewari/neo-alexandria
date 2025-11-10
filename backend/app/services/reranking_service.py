"""
Neo Alexandria 2.0 - Reranking Service (Phase 8)

This module provides ColBERT-style cross-encoder reranking for search results.
Reranking refines the ranking of candidate documents by computing query-document
relevance scores using a neural cross-encoder model.

Related files:
- app/services/search_service.py: Search orchestration
- app/services/reciprocal_rank_fusion_service.py: Result fusion
- app/database/models.py: Resource model

Features:
- ColBERT cross-encoder reranking for top candidates
- Batch processing for efficiency
- GPU acceleration with CPU fallback
- Result caching for repeated queries
- Timeout handling for long operations
- Comprehensive error handling and logging

References:
- Nogueira, R., & Cho, K. (2019). Passage Re-ranking with BERT. arXiv:1901.04085
- Khattab, O., & Zaharia, M. (2020). ColBERT: Efficient and Effective Passage Search
  via Contextualized Late Interaction over BERT. SIGIR '20.
"""

from __future__ import annotations

import hashlib
import logging
import threading
import time
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from backend.app.database.models import Resource

# Lazy import sentence_transformers and torch to avoid heavy imports at module load
try:
    from sentence_transformers import CrossEncoder
    import torch
except ImportError:  # pragma: no cover
    CrossEncoder = None
    torch = None

# Setup logging
logger = logging.getLogger(__name__)


class RerankingService:
    """Service for reranking search results using cross-encoder models.
    
    Cross-encoders model query-document interaction directly by encoding
    both together, providing more accurate relevance scores than bi-encoders
    (which encode query and document separately).
    """
    
    def __init__(
        self,
        db: Session,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        max_length: int = 500
    ):
        """Initialize the reranking service.
        
        Args:
            db: Database session for resource operations
            model_name: Hugging Face cross-encoder model identifier
                       (default: cross-encoder/ms-marco-MiniLM-L-6-v2)
            max_length: Maximum characters to use from document content (default: 500)
        """
        self.db = db
        self.model_name = model_name
        self.max_length = max_length
        self._model = None
        self._model_lock = threading.Lock()
        self._device = None
    
    def _ensure_loaded(self) -> bool:
        """Lazy load the cross-encoder model in a thread-safe manner.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        if self._model is not None:
            return True
        
        with self._model_lock:
            # Double-check locking pattern
            if self._model is not None:
                return True
            
            # Check if dependencies are available
            if CrossEncoder is None or torch is None:
                logger.error("sentence_transformers or torch not available for reranking")
                return False
            
            try:
                logger.info(f"Loading reranking model: {self.model_name}")
                
                # Determine device (GPU if available, else CPU)
                if torch.cuda.is_available():
                    self._device = "cuda"
                    logger.info("Using GPU for reranking")
                else:
                    self._device = "cpu"
                    logger.info("Using CPU for reranking")
                
                # Load cross-encoder model
                self._model = CrossEncoder(self.model_name, device=self._device)
                
                logger.info(f"Successfully loaded {self.model_name} on {self._device}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to load reranking model: {e}", exc_info=True)
                self._model = None
                self._device = None
                return False
    
    def rerank(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 20,
        timeout: Optional[float] = None
    ) -> List[Tuple[str, float]]:
        """Rerank candidates using cross-encoder model.
        
        Algorithm:
        1. Fetch resource content for candidate IDs
        2. Build (query, document) pairs using title + first N chars of content
        3. Batch predict relevance scores using cross-encoder
        4. Sort by relevance score descending
        5. Return top-K results
        
        Args:
            query: Search query text
            candidates: List of resource IDs to rerank
            top_k: Number of top results to return (default: 20)
            timeout: Optional timeout in seconds for reranking operation
        
        Returns:
            List of (resource_id, relevance_score) tuples sorted by score descending.
            Returns empty list if model unavailable or all candidates fail.
        
        Example:
            >>> reranker = RerankingService(db)
            >>> candidates = ["uuid1", "uuid2", "uuid3", ...]
            >>> reranked = reranker.rerank("machine learning", candidates, top_k=10)
            >>> # Returns top 10 most relevant documents with scores
        """
        query = (query or "").strip()
        if not query or not candidates:
            logger.debug("Empty query or candidates, returning empty results")
            return []
        
        # Ensure model is loaded
        if not self._ensure_loaded():
            logger.warning("Reranking model not available, returning empty results")
            return []
        
        start_time = time.time()
        
        try:
            # Fetch resources for candidates
            resources = self.db.query(Resource).filter(
                Resource.id.in_(candidates)
            ).all()
            
            if not resources:
                logger.warning(f"No resources found for {len(candidates)} candidates")
                return []
            
            # Build resource ID to resource mapping
            resource_map = {str(resource.id): resource for resource in resources}
            
            # Build (query, document) pairs
            pairs = []
            valid_candidate_ids = []
            
            for candidate_id in candidates:
                resource = resource_map.get(candidate_id)
                if not resource:
                    logger.debug(f"Resource {candidate_id} not found, skipping")
                    continue
                
                # Build document text: title + first N chars of description
                doc_parts = []
                if resource.title:
                    doc_parts.append(resource.title)
                if resource.description:
                    # Truncate description to max_length
                    desc = resource.description[:self.max_length]
                    doc_parts.append(desc)
                
                doc_text = " ".join(doc_parts)
                
                if not doc_text.strip():
                    logger.debug(f"Resource {candidate_id} has no content, skipping")
                    continue
                
                pairs.append([query, doc_text])
                valid_candidate_ids.append(candidate_id)
            
            if not pairs:
                logger.warning("No valid query-document pairs to rerank")
                return []
            
            # Check timeout before prediction
            if timeout and (time.time() - start_time) > timeout:
                logger.warning(f"Reranking timeout ({timeout}s) exceeded before prediction")
                return []
            
            # Batch predict relevance scores
            logger.debug(f"Reranking {len(pairs)} candidates")
            scores = self._model.predict(pairs, show_progress_bar=False)
            
            # Check timeout after prediction
            if timeout and (time.time() - start_time) > timeout:
                logger.warning(f"Reranking timeout ({timeout}s) exceeded after prediction")
                # Still return results since we have them
            
            # Combine candidate IDs with scores
            scored_candidates = list(zip(valid_candidate_ids, scores))
            
            # Sort by relevance score descending
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            
            # Return top-K
            results = scored_candidates[:top_k]
            
            elapsed = time.time() - start_time
            logger.debug(
                f"Reranked {len(pairs)} candidates in {elapsed*1000:.1f}ms, "
                f"returning top {len(results)}"
            )
            
            return results
        
        except RuntimeError as e:
            # Handle GPU out of memory errors
            if "out of memory" in str(e).lower() and self._device == "cuda":
                logger.warning("GPU OOM during reranking, falling back to CPU")
                if torch:
                    torch.cuda.empty_cache()
                
                # Retry on CPU
                try:
                    self._device = "cpu"
                    self._model = CrossEncoder(self.model_name, device=self._device)
                    return self.rerank(query, candidates, top_k, timeout)
                except Exception as retry_e:
                    logger.error(f"Failed to rerank on CPU: {retry_e}")
                    return []
            else:
                logger.error(f"Failed to rerank: {e}", exc_info=True)
                return []
        
        except Exception as e:
            logger.error(f"Failed to rerank: {e}", exc_info=True)
            return []
    
    def rerank_with_caching(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 20,
        cache: Optional[Dict[str, List[Tuple[str, float]]]] = None,
        timeout: Optional[float] = None
    ) -> List[Tuple[str, float]]:
        """Rerank with optional result caching.
        
        Computes a cache key from query and candidates, checks cache for existing
        results, and returns cached results if available. Otherwise, performs
        reranking and stores results in cache.
        
        Args:
            query: Search query text
            candidates: List of resource IDs to rerank
            top_k: Number of top results to return (default: 20)
            cache: Optional cache dictionary to use. If None, no caching is performed.
            timeout: Optional timeout in seconds for reranking operation
        
        Returns:
            List of (resource_id, relevance_score) tuples sorted by score descending.
        
        Example:
            >>> reranker = RerankingService(db)
            >>> cache = {}  # Simple dict cache
            >>> # First call - performs reranking
            >>> results1 = reranker.rerank_with_caching("ML", ["id1", "id2"], cache=cache)
            >>> # Second call with same query/candidates - returns cached results
            >>> results2 = reranker.rerank_with_caching("ML", ["id1", "id2"], cache=cache)
        """
        query = (query or "").strip()
        if not query or not candidates:
            return []
        
        # If no cache provided, just perform reranking
        if cache is None:
            return self.rerank(query, candidates, top_k, timeout)
        
        # Compute cache key from query and sorted candidates
        # Sort candidates to ensure consistent cache keys regardless of order
        sorted_candidates = sorted(candidates)
        cache_key_str = f"{query}|{','.join(sorted_candidates)}|{top_k}"
        cache_key = hashlib.md5(cache_key_str.encode()).hexdigest()
        
        # Check cache
        if cache_key in cache:
            logger.debug(f"Cache hit for query '{query[:50]}...'")
            return cache[cache_key]
        
        # Cache miss - perform reranking
        logger.debug(f"Cache miss for query '{query[:50]}...', performing reranking")
        results = self.rerank(query, candidates, top_k, timeout)
        
        # Store in cache
        cache[cache_key] = results
        
        return results
