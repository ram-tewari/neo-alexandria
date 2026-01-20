"""
Taxonomy Event Handlers

Emits taxonomy and classification-related events.

Events Emitted:
- resource.classified: When a resource is classified
- taxonomy.model_trained: When a classification model is trained
"""

import logging
from typing import List

from app.shared.event_bus import event_bus, EventPriority

logger = logging.getLogger(__name__)


def emit_resource_classified(
    resource_id: str,
    classification_code: str,
    confidence: float,
    method: str,
    taxonomy_version: str = None,
):
    """
    Emit resource.classified event.

    This should be called after classifying a resource.

    Args:
        resource_id: UUID of the resource
        classification_code: Assigned classification code
        confidence: Classification confidence score (0.0-1.0)
        method: Classification method (rule_based, ml, hybrid)
        taxonomy_version: Optional taxonomy version used
    """
    try:
        payload = {
            "resource_id": resource_id,
            "classification_code": classification_code,
            "confidence": confidence,
            "method": method,
        }

        if taxonomy_version:
            payload["taxonomy_version"] = taxonomy_version

        event_bus.emit("resource.classified", payload, priority=EventPriority.NORMAL)
        logger.debug(f"Emitted resource.classified event for resource {resource_id}")
    except Exception as e:
        logger.error(
            f"Error emitting resource.classified event: {str(e)}", exc_info=True
        )


def emit_taxonomy_model_trained(
    model_type: str,
    training_samples: int,
    accuracy: float,
    model_version: str,
    features_used: List[str] = None,
):
    """
    Emit taxonomy.model_trained event.

    This should be called after training a classification model.

    Args:
        model_type: Type of model (random_forest, svm, neural_network, etc.)
        training_samples: Number of training samples used
        accuracy: Model accuracy on validation set
        model_version: Version identifier for the trained model
        features_used: Optional list of features used in training
    """
    try:
        payload = {
            "model_type": model_type,
            "training_samples": training_samples,
            "accuracy": accuracy,
            "model_version": model_version,
        }

        if features_used:
            payload["features_used"] = features_used

        event_bus.emit("taxonomy.model_trained", payload, priority=EventPriority.HIGH)
        logger.info(f"Emitted taxonomy.model_trained event for {model_type} model")
    except Exception as e:
        logger.error(
            f"Error emitting taxonomy.model_trained event: {str(e)}", exc_info=True
        )


def register_handlers():
    """
    Register all event handlers for the taxonomy module.

    This function should be called during application startup.
    Currently, taxonomy module only emits events and doesn't subscribe to any.
    """
    logger.info("Taxonomy module event handlers registered")
