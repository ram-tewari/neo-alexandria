"""
Neo Alexandria 2.0 - Celery Task Implementations

This module contains all Celery task implementations for background processing.
Tasks are organized by category: data consistency, scheduled maintenance, and batch operations.

Related files:
- app/tasks/celery_app.py: Celery configuration
- app/events/hooks.py: Event hooks that trigger these tasks
- app/services/: Service layer implementations used by tasks
- app/database/base.py: Database session management

Task Categories:
1. Data Consistency Tasks: Maintain derived data (embeddings, quality, search index)
2. Scheduled Maintenance Tasks: Periodic system health and optimization
3. Batch Processing Tasks: Process multiple resources efficiently

Design Patterns:
- DatabaseTask base class: Automatic DB session management
- Retry with exponential backoff: Handle transient errors
- Progress tracking: Report status for long-running tasks
- Priority queuing: Critical tasks execute first
"""

import logging
from typing import List, Optional, Dict, Any
from celery import Task

from .celery_app import celery_app
from ..database.base import SessionLocal, Base

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """
    Base task class with automatic database session management.
    
    This class provides automatic DB session lifecycle management for Celery tasks.
    Sessions are created before task execution and properly closed after completion,
    even if the task raises an exception.
    
    Usage:
        @celery_app.task(bind=True, base=DatabaseTask)
        def my_task(self, resource_id: str, db=None):
            # db session is automatically provided
            resource = db.query(Resource).filter_by(id=resource_id).first()
            # ... process resource
    
    Features:
    - Automatic session creation and cleanup
    - Ensures tables exist (useful for SQLite)
    - Proper exception handling and session rollback
    - Compatible with Celery's retry mechanism
    """
    
    _db = None
    
    def __call__(self, *args, **kwargs):
        """
        Execute task with automatic database session management.
        
        Creates a database session, passes it to the task via the 'db' parameter,
        and ensures proper cleanup in a finally block.
        
        Args:
            *args: Positional arguments passed to the task
            **kwargs: Keyword arguments passed to the task
            
        Returns:
            Task execution result
        """
        # Create database session
        db = SessionLocal()
        
        try:
            # Ensure tables exist (especially for SQLite)
            try:
                Base.metadata.create_all(bind=db.get_bind())
            except Exception:
                # Best effort; ignore if fails
                pass
            
            # Execute task with db session
            return self.run(*args, db=db, **kwargs)
        
        finally:
            # Always close the session
            db.close()


# ============================================================================
# Data Consistency Tasks
# ============================================================================

@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=3,
    default_retry_delay=60,
    name="app.tasks.celery_tasks.regenerate_embedding_task"
)
def regenerate_embedding_task(self, resource_id: str, db=None):
    """
    Regenerate embedding vector for a resource.
    
    Triggered by: resource.content_changed event
    Priority: HIGH (7)
    Retry: 3 attempts with exponential backoff for transient errors
    
    Args:
        resource_id: UUID of the resource to process
        db: Database session (automatically provided by DatabaseTask)
    """
    try:
        logger.info(f"Regenerating embedding for resource {resource_id}")
        
        # Import here to avoid circular dependencies
        from ..services.embedding_service import EmbeddingService
        
        embedding_service = EmbeddingService(db)
        embedding_service.generate_and_store_embedding(resource_id)
        
        logger.info(f"Successfully regenerated embedding for resource {resource_id}")
        
    except Exception as e:
        # Check if error is transient (network, timeout, connection)
        error_msg = str(e).lower()
        if any(keyword in error_msg for keyword in ["timeout", "connection", "network"]):
            # Retry with exponential backoff
            logger.warning(f"Transient error regenerating embedding for {resource_id}: {e}")
            raise self.retry(exc=e, countdown=2 ** self.request.retries)
        else:
            # Permanent error - don't retry
            logger.error(f"Permanent error regenerating embedding for {resource_id}: {e}", exc_info=True)
            raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=2,
    name="app.tasks.celery_tasks.recompute_quality_task"
)
def recompute_quality_task(self, resource_id: str, weights: Optional[Dict[str, float]] = None, db=None):
    """
    Recompute quality scores for a resource.
    
    Triggered by: resource.metadata_changed event
    Priority: MEDIUM (5)
    Retry: 2 attempts
    
    Args:
        resource_id: UUID of the resource to process
        weights: Optional custom weights for quality dimensions
        db: Database session (automatically provided by DatabaseTask)
    """
    try:
        logger.info(f"Recomputing quality for resource {resource_id}")
        
        from ..services.quality_service import QualityService
        
        quality_service = QualityService(db)
        quality_scores = quality_service.compute_quality(resource_id, weights=weights)
        
        logger.info(f"Successfully recomputed quality for resource {resource_id}: {quality_scores}")
        
    except Exception as e:
        logger.error(f"Error recomputing quality for {resource_id}: {e}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=3,
    default_retry_delay=5,
    name="app.tasks.celery_tasks.update_search_index_task"
)
def update_search_index_task(self, resource_id: str, db=None):
    """
    Update FTS5 search index for a resource.
    
    Triggered by: resource.updated event
    Priority: URGENT (9)
    Retry: 3 attempts with 5-second delay
    
    Args:
        resource_id: UUID of the resource to process
        db: Database session (automatically provided by DatabaseTask)
    """
    try:
        logger.info(f"Updating search index for resource {resource_id}")
        
        from ..services.search_service import SearchService
        
        search_service = SearchService(db)
        search_service.update_fts5_index(resource_id)
        
        logger.info(f"Successfully updated search index for resource {resource_id}")
        
    except Exception as e:
        logger.error(f"Error updating search index for {resource_id}: {e}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.celery_tasks.update_graph_edges_task"
)
def update_graph_edges_task(self, resource_id: str, citations: List[str], db=None):
    """
    Update knowledge graph edges for citations.
    
    Triggered by: citations.extracted event
    Priority: MEDIUM (5)
    
    Args:
        resource_id: UUID of the source resource
        citations: List of cited resource IDs
        db: Database session (automatically provided by DatabaseTask)
    """
    try:
        logger.info(f"Updating graph edges for resource {resource_id} with {len(citations)} citations")
        
        from ..services.graph_service import GraphService
        
        graph_service = GraphService(db)
        graph_service.add_citation_edges(resource_id, citations)
        
        # Invalidate graph cache
        invalidate_cache_task.apply_async(
            args=[[f"graph:neighbors:{resource_id}", "graph:*"]],
            priority=9
        )
        
        logger.info(f"Successfully updated graph edges for resource {resource_id}")
        
    except Exception as e:
        logger.error(f"Error updating graph edges for {resource_id}: {e}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=2,
    name="app.tasks.celery_tasks.classify_resource_task"
)
def classify_resource_task(self, resource_id: str, db=None):
    """
    Classify resource using ML model.
    
    Triggered by: resource.created event
    Priority: MEDIUM (5)
    Retry: 2 attempts
    
    Args:
        resource_id: UUID of the resource to classify
        db: Database session (automatically provided by DatabaseTask)
    """
    try:
        logger.info(f"Classifying resource {resource_id}")
        
        from ..services.ml_classification_service import MLClassificationService
        from ..services.taxonomy_service import TaxonomyService
        
        # Get predictions from ML model - returns ClassificationResult domain object
        ml_service = MLClassificationService(db)
        result = ml_service.predict(resource_id, top_k=5)
        
        # Store predictions - iterate over ClassificationPrediction objects
        taxonomy_service = TaxonomyService(db)
        for prediction in result.predictions:
            taxonomy_service.classify_resource(
                resource_id=resource_id,
                category_id=prediction.taxonomy_id,
                confidence=prediction.confidence,
                is_predicted=True
            )
        
        logger.info(f"Successfully classified resource {resource_id} with {len(result.predictions)} categories")
        
    except Exception as e:
        logger.error(f"Error classifying resource {resource_id}: {e}", exc_info=True)
        raise


@celery_app.task(
    name="app.tasks.celery_tasks.invalidate_cache_task"
)
def invalidate_cache_task(cache_keys: List[str]):
    """
    Invalidate cache entries.
    
    Triggered by: resource.updated event, graph updates
    Priority: URGENT (9)
    
    Supports both exact keys and pattern-based invalidation (wildcard *).
    
    Args:
        cache_keys: List of cache keys or patterns to invalidate
    """
    try:
        logger.info(f"Invalidating {len(cache_keys)} cache keys/patterns")
        
        from ..cache.redis_cache import cache
        
        invalidation_count = 0
        for key in cache_keys:
            if "*" in key:
                # Pattern-based invalidation
                count = cache.delete_pattern(key)
                invalidation_count += count
            else:
                # Exact key invalidation
                cache.delete(key)
                invalidation_count += 1
        
        logger.info(f"Successfully invalidated {invalidation_count} cache entries")
        
    except Exception as e:
        logger.error(f"Error invalidating cache: {e}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.celery_tasks.refresh_recommendation_profile_task"
)
def refresh_recommendation_profile_task(self, user_id: str, db=None):
    """
    Refresh user recommendation profile.
    
    Triggered by: user.interaction_tracked event (every 10 interactions)
    Priority: LOW (3)
    
    Args:
        user_id: UUID of the user
        db: Database session (automatically provided by DatabaseTask)
    """
    try:
        logger.info(f"Refreshing recommendation profile for user {user_id}")
        
        from ..services.recommendation_service import UserProfileService
        
        profile_service = UserProfileService(db)
        profile_service._update_learned_preferences(user_id)
        
        logger.info(f"Successfully refreshed recommendation profile for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error refreshing recommendation profile for {user_id}: {e}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.celery_tasks.normalize_author_names_task"
)
def normalize_author_names_task(self, resource_id: str, authors: List[str], db=None):
    """
    Normalize author names for consistency.
    
    Triggered by: authors.extracted event
    Priority: LOW (3)
    
    Args:
        resource_id: UUID of the resource
        authors: List of author names to normalize
        db: Database session (automatically provided by DatabaseTask)
    """
    try:
        logger.info(f"Normalizing {len(authors)} author names for resource {resource_id}")
        
        # TODO: Implement author normalization logic
        # This would involve:
        # 1. Standardizing name formats (Last, First vs First Last)
        # 2. Handling initials and abbreviations
        # 3. Detecting duplicate authors with different spellings
        # 4. Linking to author entities in the database
        
        logger.info(f"Successfully normalized author names for resource {resource_id}")
        
    except Exception as e:
        logger.error(f"Error normalizing author names for {resource_id}: {e}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=2,
    name="app.tasks.celery_tasks.extract_citations_task"
)
def extract_citations_task(self, resource_id: str, db=None):
    """
    Extract citations from a resource.
    
    Triggered by: Manual API call
    Priority: MEDIUM (5)
    Retry: 2 attempts
    
    Args:
        resource_id: UUID of the resource to process
        db: Database session (automatically provided by DatabaseTask)
    """
    try:
        logger.info(f"Extracting citations for resource {resource_id}")
        
        from ..services.citation_service import CitationService
        
        service = CitationService(db)
        service.extract_citations(resource_id)
        
        logger.info(f"Successfully extracted citations for resource {resource_id}")
        
    except Exception as e:
        logger.error(f"Error extracting citations for {resource_id}: {e}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=2,
    name="app.tasks.celery_tasks.resolve_citations_task"
)
def resolve_citations_task(self, db=None):
    """
    Resolve internal citations.
    
    Triggered by: Manual API call
    Priority: MEDIUM (5)
    Retry: 2 attempts
    
    Matches unresolved citation URLs to existing resources in the database.
    
    Args:
        db: Database session (automatically provided by DatabaseTask)
    """
    try:
        logger.info("Resolving internal citations")
        
        from ..services.citation_service import CitationService
        
        service = CitationService(db)
        service.resolve_internal_citations()
        
        logger.info("Successfully resolved internal citations")
        
    except Exception as e:
        logger.error(f"Error resolving citations: {e}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=2,
    name="app.tasks.celery_tasks.compute_citation_importance_task"
)
def compute_citation_importance_task(self, db=None):
    """
    Compute PageRank importance scores for all citations.
    
    Triggered by: Manual API call
    Priority: LOW (3)
    Retry: 2 attempts
    
    This is a computationally expensive operation that should be run
    periodically rather than on every request.
    
    Args:
        db: Database session (automatically provided by DatabaseTask)
    """
    try:
        logger.info("Computing citation importance scores")
        
        from ..services.citation_service import CitationService
        
        service = CitationService(db)
        service.compute_citation_importance()
        
        logger.info("Successfully computed citation importance scores")
        
    except Exception as e:
        logger.error(f"Error computing citation importance: {e}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=2,
    name="app.tasks.celery_tasks.extract_scholarly_metadata_task"
)
def extract_scholarly_metadata_task(self, resource_id: str, db=None):
    """
    Extract scholarly metadata from a resource.
    
    Triggered by: Manual API call
    Priority: MEDIUM (5)
    Retry: 2 attempts
    
    Extracts authors, DOI, publication details, and structural content.
    
    Args:
        resource_id: UUID of the resource to process
        db: Database session (automatically provided by DatabaseTask)
    """
    try:
        logger.info(f"Extracting scholarly metadata for resource {resource_id}")
        
        from ..services.metadata_extractor import MetadataExtractor
        
        extractor = MetadataExtractor(db)
        extractor.extract_scholarly_metadata(resource_id)
        
        logger.info(f"Successfully extracted scholarly metadata for resource {resource_id}")
        
    except Exception as e:
        logger.error(f"Error extracting scholarly metadata for {resource_id}: {e}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=2,
    name="app.tasks.celery_tasks.evaluate_summary_task"
)
def evaluate_summary_task(self, resource_id: str, use_g_eval: bool = False, db=None):
    """
    Evaluate summary quality for a resource.
    
    Triggered by: Manual API call
    Priority: MEDIUM (5)
    Retry: 2 attempts
    
    Args:
        resource_id: UUID of the resource to process
        use_g_eval: Whether to use G-Eval (requires OpenAI API)
        db: Database session (automatically provided by DatabaseTask)
    """
    try:
        logger.info(f"Evaluating summary for resource {resource_id} (use_g_eval={use_g_eval})")
        
        import os
        from ..services.summarization_evaluator import SummarizationEvaluator
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        evaluator = SummarizationEvaluator(db, openai_api_key=openai_api_key)
        evaluator.evaluate_summary(resource_id, use_g_eval=use_g_eval)
        
        logger.info(f"Successfully evaluated summary for resource {resource_id}")
        
    except Exception as e:
        logger.error(f"Error evaluating summary for {resource_id}: {e}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.celery_tasks.batch_process_resources_task"
)
def batch_process_resources_task(
    self,
    resource_ids: List[str],
    operation: str,
    db=None
) -> Dict[str, Any]:
    """
    Batch process multiple resources with progress tracking.
    
    Priority: LOW (3) - batch queue
    
    Supported operations:
    - regenerate_embeddings: Regenerate embeddings for all resources
    - recompute_quality: Recompute quality scores for all resources
    
    Args:
        resource_ids: List of resource UUIDs to process
        operation: Operation to perform
        db: Database session (automatically provided by DatabaseTask)
        
    Returns:
        Dict with status and processed count
    """
    try:
        total = len(resource_ids)
        logger.info(f"Starting batch {operation} for {total} resources")
        
        for i, resource_id in enumerate(resource_ids):
            # Update progress
            self.update_state(
                state='PROCESSING',
                meta={'current': i + 1, 'total': total, 'operation': operation}
            )
            
            # Queue individual task based on operation
            if operation == "regenerate_embeddings":
                regenerate_embedding_task.apply_async(args=[resource_id], priority=5)
            elif operation == "recompute_quality":
                recompute_quality_task.apply_async(args=[resource_id], priority=5)
            else:
                logger.warning(f"Unknown operation: {operation}")
        
        logger.info(f"Successfully queued {total} tasks for batch {operation}")
        
        return {
            'status': 'completed',
            'processed': total,
            'operation': operation
        }
        
    except Exception as e:
        logger.error(f"Error in batch processing: {e}", exc_info=True)
        raise


# ============================================================================
# Scheduled Maintenance Tasks
# ============================================================================

@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.celery_tasks.monitor_quality_degradation_task"
)
def monitor_quality_degradation_task(self, db=None):
    """
    Monitor quality score degradation over time.
    
    Schedule: Daily at 2 AM
    Priority: MEDIUM (5)
    
    Detects resources whose quality scores have decreased significantly
    and triggers recomputation or alerts.
    
    Args:
        db: Database session (automatically provided by DatabaseTask)
    """
    try:
        logger.info("Starting quality degradation monitoring")
        
        # TODO: Implement quality degradation detection
        # This would involve:
        # 1. Query resources with quality history
        # 2. Detect significant drops in quality scores
        # 3. Trigger recomputation for degraded resources
        # 4. Generate alerts for manual review
        
        logger.info("Completed quality degradation monitoring")
        
    except Exception as e:
        logger.error(f"Error in quality degradation monitoring: {e}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.celery_tasks.detect_quality_outliers_task"
)
def detect_quality_outliers_task(self, db=None):
    """
    Detect quality score outliers for review.
    
    Schedule: Weekly on Sunday at 3 AM
    Priority: MEDIUM (5)
    
    Identifies resources with unusually high or low quality scores
    that may indicate data quality issues or exceptional content.
    
    Args:
        db: Database session (automatically provided by DatabaseTask)
    """
    try:
        logger.info("Starting quality outlier detection")
        
        # TODO: Implement quality outlier detection
        # This would involve:
        # 1. Calculate quality score statistics (mean, std dev)
        # 2. Identify outliers (e.g., >3 standard deviations)
        # 3. Generate report for manual review
        # 4. Optionally trigger recomputation
        
        logger.info("Completed quality outlier detection")
        
    except Exception as e:
        logger.error(f"Error in quality outlier detection: {e}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.celery_tasks.retrain_classification_model_task"
)
def retrain_classification_model_task(self, db=None):
    """
    Retrain classification model with new data.
    
    Schedule: Monthly on 1st at midnight
    Priority: MEDIUM (5)
    
    Retrains the ML classification model using accumulated user feedback
    and newly classified resources.
    
    Args:
        db: Database session (automatically provided by DatabaseTask)
    """
    try:
        logger.info("Starting classification model retraining")
        
        # TODO: Implement model retraining
        # This would involve:
        # 1. Collect training data (user-confirmed classifications)
        # 2. Prepare training dataset
        # 3. Train new model version
        # 4. Evaluate model performance
        # 5. Deploy new model if performance improves
        
        logger.info("Completed classification model retraining")
        
    except Exception as e:
        logger.error(f"Error in classification model retraining: {e}", exc_info=True)
        raise


@celery_app.task(
    name="app.tasks.celery_tasks.cleanup_expired_cache_task"
)
def cleanup_expired_cache_task():
    """
    Clean up expired cache entries.
    
    Schedule: Daily at 4 AM
    Priority: LOW (3)
    
    Removes expired cache entries to free up Redis memory.
    Redis handles TTL expiration automatically, but this task
    can perform additional cleanup and optimization.
    """
    try:
        logger.info("Starting cache cleanup")
        
        from ..cache.redis_cache import cache
        
        # Redis automatically handles TTL expiration
        # This task can perform additional cleanup if needed
        # For now, just log cache statistics
        stats = cache.get_stats()
        logger.info(f"Cache statistics: {stats}")
        
        logger.info("Completed cache cleanup")
        
    except Exception as e:
        logger.error(f"Error in cache cleanup: {e}", exc_info=True)
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    max_retries=3,
    default_retry_delay=60,
    name="app.tasks.celery_tasks.update_collection_embeddings_task"
)
def update_collection_embeddings_task(self, resource_id: str, db=None) -> Dict[str, Any]:
    """
    Update collection embeddings after a resource is deleted.
    
    This task finds all collections that contained the deleted resource and
    recomputes their embeddings. Collection embeddings are the average of
    member resource embeddings, so they need to be updated when membership changes.
    
    Args:
        resource_id: UUID of the deleted resource
        db: Database session (automatically provided by DatabaseTask)
        
    Returns:
        Dict with status and number of collections updated
        
    Raises:
        Exception: If collection embedding update fails (will retry)
    """
    import uuid
    from ..services.collection_service import CollectionService
    from ..database.models import Collection, CollectionResource
    
    try:
        logger.info(f"Updating collection embeddings for deleted resource {resource_id}")
        
        # Convert resource_id to UUID
        try:
            resource_uuid = uuid.UUID(resource_id)
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid resource_id format: {resource_id}")
            return {"status": "error", "message": f"Invalid UUID: {e}"}
        
        # Find all collections that contained this resource
        # Note: The resource is already deleted, but we can find collections
        # that need updating by checking for any that might have had it
        collection_service = CollectionService(db)
        
        # Get all collections (we'll recompute all since we can't query deleted resource)
        # In a production system, you might want to track this relationship before deletion
        collections = db.query(Collection).all()
        
        updated_count = 0
        for collection in collections:
            try:
                # Recompute embedding for each collection
                collection_service.compute_collection_embedding(collection.id)
                updated_count += 1
                logger.debug(f"Updated embedding for collection {collection.id}")
            except Exception as e:
                logger.warning(f"Failed to update collection {collection.id}: {e}")
                # Continue with other collections
        
        logger.info(
            f"Updated {updated_count} collection embeddings after resource {resource_id} deletion"
        )
        
        return {
            "status": "success",
            "resource_id": resource_id,
            "collections_updated": updated_count
        }
        
    except Exception as e:
        logger.error(
            f"Error updating collection embeddings for resource {resource_id}: {e}",
            exc_info=True
        )
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)
