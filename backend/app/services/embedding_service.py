"""
Neo Alexandria 2.0 - Embedding Service with Caching

This module provides a caching layer for embedding generation operations.
It wraps the ai_core embedding functionality with Redis caching to reduce
expensive computation for Phase 12.5 event-driven architecture.

Features:
- Cached embedding retrieval with 1-hour TTL
- Automatic cache population after generation
- Cache invalidation on resource updates
- Statistics tracking for cache performance

Related files:
- app/services/ai_core.py: Core embedding generation
- app/cache/redis_cache.py: Redis caching layer
- app/events/hooks.py: Cache invalidation hooks
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from ..services.ai_core import AICore, create_composite_text
from ..cache.redis_cache import cache
from ..database import models as db_models

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and caching embeddings.
    
    This service wraps the AICore embedding generation with Redis caching
    to reduce expensive computation. Embeddings are cached with a 1-hour TTL.
    
    Attributes:
        db: Database session
        ai_core: AICore instance for embedding generation
    """
    
    def __init__(self, db: Session, ai_core: Optional[AICore] = None):
        """Initialize embedding service.
        
        Args:
            db: Database session
            ai_core: Optional AICore instance. If not provided, creates new instance.
        """
        self.db = db
        self.ai_core = ai_core or AICore()
    
    def get_embedding(self, resource_id: str) -> Optional[List[float]]:
        """Get embedding for a resource with caching.
        
        First checks cache, then generates if not found and stores in cache.
        
        Args:
            resource_id: Resource ID
            
        Returns:
            Embedding vector as list of floats, or None if generation fails
        """
        cache_key = f"embedding:{resource_id}"
        
        # Try cache first
        cached_embedding = cache.get(cache_key)
        if cached_embedding is not None:
            logger.debug(f"Cache hit for embedding: {resource_id}")
            return cached_embedding
        
        # Cache miss - generate embedding
        logger.debug(f"Cache miss for embedding: {resource_id}")
        embedding = self._generate_embedding(resource_id)
        
        # Store in cache if generation succeeded
        if embedding:
            cache.set(cache_key, embedding, ttl=3600)  # 1 hour TTL
        
        return embedding
    
    def _generate_embedding(self, resource_id: str) -> Optional[List[float]]:
        """Generate embedding for a resource.
        
        Args:
            resource_id: Resource ID
            
        Returns:
            Embedding vector as list of floats, or None if generation fails
        """
        try:
            # Fetch resource from database
            resource = self.db.query(db_models.Resource).filter(
                db_models.Resource.id == resource_id
            ).first()
            
            if not resource:
                logger.warning(f"Resource not found: {resource_id}")
                return None
            
            # Create composite text from resource
            composite_text = create_composite_text(resource)
            
            if not composite_text.strip():
                logger.warning(f"Empty composite text for resource: {resource_id}")
                return None
            
            # Generate embedding
            embedding = self.ai_core.generate_embedding(composite_text)
            
            if not embedding:
                logger.warning(f"Embedding generation failed for resource: {resource_id}")
                return None
            
            logger.info(f"Generated embedding for resource: {resource_id}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding for resource {resource_id}: {e}")
            return None
    
    def generate_and_store_embedding(self, resource_id: str) -> bool:
        """Generate embedding and store in both database and cache.
        
        This method is used by background tasks to regenerate embeddings
        after resource updates.
        
        Args:
            resource_id: Resource ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate embedding
            embedding = self._generate_embedding(resource_id)
            
            if not embedding:
                return False
            
            # Store in database
            resource = self.db.query(db_models.Resource).filter(
                db_models.Resource.id == resource_id
            ).first()
            
            if not resource:
                logger.warning(f"Resource not found: {resource_id}")
                return False
            
            resource.embedding = embedding
            self.db.commit()
            
            # Store in cache
            cache_key = f"embedding:{resource_id}"
            cache.set(cache_key, embedding, ttl=3600)  # 1 hour TTL
            
            logger.info(f"Stored embedding for resource: {resource_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing embedding for resource {resource_id}: {e}")
            self.db.rollback()
            return False
    
    def invalidate_cache(self, resource_id: str):
        """Invalidate cached embedding for a resource.
        
        Args:
            resource_id: Resource ID
        """
        cache_key = f"embedding:{resource_id}"
        cache.delete(cache_key)
        logger.info(f"Invalidated embedding cache for resource: {resource_id}")
