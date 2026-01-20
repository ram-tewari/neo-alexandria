"""
Quality Event Handlers

Emits quality-related events for monitoring and analytics.

Events Emitted:
- quality.computed: When quality scores are computed for a resource
- quality.outlier_detected: When a quality outlier is detected
"""

import logging
from typing import Dict

from app.shared.event_bus import event_bus, EventPriority

logger = logging.getLogger(__name__)


def emit_quality_computed(
    resource_id: str,
    quality_score: float,
    dimensions: Dict[str, float],
    computation_version: str,
):
    """
    Emit quality.computed event.

    This should be called by the quality service after computing quality scores.

    Args:
        resource_id: UUID of the resource
        quality_score: Overall quality score (0.0-1.0)
        dimensions: Dictionary of dimension scores (accuracy, completeness, etc.)
        computation_version: Version of the quality computation algorithm
    """
    try:
        event_bus.emit(
            "quality.computed",
            {
                "resource_id": resource_id,
                "quality_score": quality_score,
                "dimensions": dimensions,
                "computation_version": computation_version,
            },
            priority=EventPriority.LOW,
        )
        logger.debug(f"Emitted quality.computed event for resource {resource_id}")
    except Exception as e:
        logger.error(f"Error emitting quality.computed event: {str(e)}", exc_info=True)


def emit_quality_outlier_detected(
    resource_id: str,
    quality_score: float,
    outlier_score: float,
    dimensions: Dict[str, float],
    reason: str,
):
    """
    Emit quality.outlier_detected event.

    This should be called by the quality service when an outlier is detected.

    Args:
        resource_id: UUID of the resource
        quality_score: Overall quality score
        outlier_score: Outlier detection score (-1 for outlier, 1 for inlier)
        dimensions: Dictionary of dimension scores
        reason: Reason for outlier detection (e.g., "low_completeness", "anomalous_pattern")
    """
    try:
        event_bus.emit(
            "quality.outlier_detected",
            {
                "resource_id": resource_id,
                "quality_score": quality_score,
                "outlier_score": outlier_score,
                "dimensions": dimensions,
                "reason": reason,
            },
            priority=EventPriority.NORMAL,
        )
        logger.info(
            f"Emitted quality.outlier_detected event for resource {resource_id}"
        )
    except Exception as e:
        logger.error(
            f"Error emitting quality.outlier_detected event: {str(e)}", exc_info=True
        )


def register_handlers():
    """
    Register all event handlers for the quality module.

    This function should be called during application startup.
    Currently, quality module only emits events and doesn't subscribe to any.
    """
    logger.info("Quality module event handlers registered")
