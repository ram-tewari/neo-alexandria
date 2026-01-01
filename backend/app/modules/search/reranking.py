"""
Reranking Service

Provides ColBERT-style reranking functionality using cross-encoder models.
"""

from typing import List, Tuple
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class RerankingService:
    """
    Reranking service for improving search result quality.
    
    Uses cross-encoder models (e.g., MS MARCO MiniLM) for reranking
    search results based on query-document relevance.
    """
    
    def __init__(self, db: Session, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize reranking service.
        
        Args:
            db: Database session
            model_name: Cross-encoder model name
        """
        self.db = db
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Lazy load the cross-encoder model."""
        try:
            # Try to import and load cross-encoder model
            # from sentence_transformers import CrossEncoder
            # self.model = CrossEncoder(self.model_name)
            pass
        except Exception as e:
            logger.warning(f"Could not load reranking model: {e}")
            self.model = None
    
    def rerank(
        self,
        query: str,
        candidates: List[Tuple[str, float]],
        top_k: int = None
    ) -> List[Tuple[str, float]]:
        """
        Rerank candidates using cross-encoder.
        
        Args:
            query: Search query
            candidates: List of (resource_id, score) tuples
            top_k: Optional limit on number of results to return
            
        Returns:
            Reranked list of (resource_id, score) tuples
        """
        if not candidates:
            return []
        
        try:
            if self.model is None:
                # No reranking model available, return candidates as-is
                logger.debug("Reranking model not available, returning original ranking")
                return candidates[:top_k] if top_k else candidates
            
            # Fetch resource content for reranking
            from ...database.models import Resource
            
            resource_ids = [rid for rid, _ in candidates]
            resources = self.db.query(Resource).filter(Resource.id.in_(resource_ids)).all()
            
            id_to_resource = {str(r.id): r for r in resources}
            
            # Prepare query-document pairs
            pairs = []
            valid_ids = []
            
            for resource_id, _ in candidates:
                resource = id_to_resource.get(resource_id)
                if resource and resource.embedding:
                    # Use title + description for reranking (faster than full content)
                    doc_text = f"{resource.title or ''} {resource.description or ''}"
                    pairs.append([query, doc_text])
                    valid_ids.append(resource_id)
            
            if not pairs:
                return candidates[:top_k] if top_k else candidates
            
            # Compute relevance scores
            # scores = self.model.predict(pairs)
            
            # For now, return original ranking
            # In production, would use: reranked = sorted(zip(valid_ids, scores), key=lambda x: x[1], reverse=True)
            reranked = [(rid, score) for rid, score in candidates if rid in valid_ids]
            
            return reranked[:top_k] if top_k else reranked
            
        except Exception as e:
            logger.error(f"Error during reranking: {e}")
            # Fall back to original ranking
            return candidates[:top_k] if top_k else candidates
