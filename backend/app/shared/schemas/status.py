"""Status tracking schemas for resource processing pipeline.

This module defines the enums and models for tracking resource processing
progress through various stages (INGESTION, QUALITY, TAXONOMY, GRAPH, EMBEDDING).
"""

from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field


class ProcessingStage(str, Enum):
    """Processing stages for resource ingestion pipeline.

    Each stage represents a distinct phase of resource processing:
    - INGESTION: Initial resource creation and metadata extraction
    - QUALITY: Quality assessment and scoring
    - TAXONOMY: ML-based classification and tagging
    - GRAPH: Citation extraction and knowledge graph integration
    - EMBEDDING: Vector embedding generation for semantic search
    """

    INGESTION = "ingestion"
    QUALITY = "quality"
    TAXONOMY = "taxonomy"
    GRAPH = "graph"
    EMBEDDING = "embedding"


class StageStatus(str, Enum):
    """Status of a processing stage.

    - PENDING: Stage has not started yet
    - PROCESSING: Stage is currently in progress
    - COMPLETED: Stage finished successfully
    - FAILED: Stage encountered an error and failed
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ResourceProgress(BaseModel):
    """Progress tracking for a resource through processing stages.

    This model represents the current state of a resource as it moves
    through the processing pipeline. It tracks individual stage statuses
    and calculates an overall status.

    Attributes:
        resource_id: Unique identifier for the resource
        overall_status: Calculated overall status based on all stages
        stages: Dictionary mapping each stage to its current status
        error_message: Optional error message if any stage failed
        updated_at: ISO 8601 timestamp of last update
    """

    resource_id: int
    overall_status: StageStatus
    stages: Dict[ProcessingStage, StageStatus] = Field(default_factory=dict)
    error_message: Optional[str] = None
    updated_at: str  # ISO 8601 timestamp

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "resource_id": 123,
                "overall_status": "processing",
                "stages": {
                    "ingestion": "completed",
                    "quality": "completed",
                    "taxonomy": "processing",
                    "graph": "pending",
                    "embedding": "pending",
                },
                "error_message": None,
                "updated_at": "2026-01-01T12:00:00Z",
            }
        }
