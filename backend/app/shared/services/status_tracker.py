"""Status tracking service for resource processing pipeline.

This module provides real-time progress tracking for long-running background tasks
through various processing stages (INGESTION, QUALITY, TAXONOMY, GRAPH, EMBEDDING).

The StatusTracker uses Redis for storage with TTL to prevent memory bloat and
gracefully degrades when Redis is unavailable.

Related files:
- app/shared/schemas/status.py: Status enums and models
- app/cache/redis_cache.py: Redis cache service
- app/modules/*/handlers.py: Event handlers that update progress
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict

from ..schemas.status import ProcessingStage, StageStatus, ResourceProgress
from ...cache.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class StatusTracker:
    """Track resource processing progress in Redis.

    This service provides methods to set and retrieve progress for resources
    as they move through the processing pipeline. Progress is stored in Redis
    with a 24-hour TTL to prevent memory bloat.

    Attributes:
        cache: RedisCache instance for storage
        ttl: Time-to-live for progress records in seconds (default: 24 hours)
    """

    def __init__(self, cache: RedisCache):
        """Initialize StatusTracker.

        Args:
            cache: RedisCache instance for storage
        """
        self.cache = cache
        self.ttl = 86400  # 24 hours

    async def set_progress(
        self,
        resource_id: int,
        stage: ProcessingStage,
        status: StageStatus,
        error_message: Optional[str] = None,
    ) -> None:
        """Update progress for a specific stage.

        This method updates the status of a single processing stage for a resource.
        It retrieves the current progress, updates the specified stage, recalculates
        the overall status, and stores the updated progress back to Redis.

        Args:
            resource_id: Resource identifier
            stage: Processing stage being updated
            status: New status for the stage
            error_message: Optional error message if status is FAILED
        """
        try:
            # Get current progress or create new
            progress = await self.get_progress(resource_id)
            if not progress:
                progress = ResourceProgress(
                    resource_id=resource_id,
                    overall_status=StageStatus.PENDING,
                    stages={},
                    updated_at=datetime.now(timezone.utc).isoformat(),
                )

            # Update stage status
            progress.stages[stage] = status
            if error_message:
                progress.error_message = error_message

            # Calculate overall status
            progress.overall_status = self._calculate_overall_status(progress.stages)
            progress.updated_at = datetime.now(timezone.utc).isoformat()

            # Store in Redis
            key = f"progress:resource:{resource_id}"
            self.cache.set(key, progress.model_dump(), ttl=self.ttl)

            logger.debug(
                f"Updated progress for resource {resource_id}: "
                f"{stage.value}={status.value}, overall={progress.overall_status.value}"
            )

        except Exception as e:
            logger.error(f"Failed to set progress for resource {resource_id}: {e}")

    async def get_progress(self, resource_id: int) -> Optional[ResourceProgress]:
        """Get current progress for a resource.

        This method retrieves the current processing progress for a resource from Redis.
        If Redis is unavailable or the resource has no progress record, it returns None.

        Args:
            resource_id: Resource identifier

        Returns:
            ResourceProgress if found, None otherwise
        """
        try:
            key = f"progress:resource:{resource_id}"
            data = self.cache.get(key)
            if data:
                return ResourceProgress(**data)
            return None
        except Exception as e:
            logger.warning(f"Failed to get progress for resource {resource_id}: {e}")
            return None

    def _calculate_overall_status(
        self, stages: Dict[ProcessingStage, StageStatus]
    ) -> StageStatus:
        """Calculate overall status from stage statuses.

        This method implements the status calculation logic:
        - If any stage is FAILED, overall is FAILED
        - Else if any stage is PROCESSING, overall is PROCESSING
        - Else if all stages are COMPLETED, overall is COMPLETED
        - Otherwise, overall is PENDING

        Args:
            stages: Dictionary mapping each stage to its current status

        Returns:
            Calculated overall status
        """
        if not stages:
            return StageStatus.PENDING

        statuses = set(stages.values())

        # Priority order: FAILED > PROCESSING > COMPLETED > PENDING
        if StageStatus.FAILED in statuses:
            return StageStatus.FAILED
        if StageStatus.PROCESSING in statuses:
            return StageStatus.PROCESSING
        if all(s == StageStatus.COMPLETED for s in statuses):
            return StageStatus.COMPLETED

        return StageStatus.PENDING


# Global status tracker instance (initialized with cache)
_status_tracker: Optional[StatusTracker] = None


def get_status_tracker() -> StatusTracker:
    """Get global StatusTracker instance.

    This function provides access to the global StatusTracker instance,
    creating it if it doesn't exist yet.

    Returns:
        StatusTracker instance
    """
    global _status_tracker
    if _status_tracker is None:
        from ...cache.redis_cache import cache

        _status_tracker = StatusTracker(cache)
    return _status_tracker
