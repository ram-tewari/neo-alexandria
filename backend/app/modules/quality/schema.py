"""
Quality Module - Schemas

This module defines Pydantic schemas for quality assessment data validation and serialization.
Extracted from app/schemas/quality.py as part of Phase 14 vertical slice refactoring.

Schemas:
- QualityDetailsResponse: Full quality dimension breakdown
- QualityRecalculateRequest: Request for quality recomputation
- OutlierResponse: Quality outlier information
- DegradationReport: Quality degradation report
- SummaryEvaluationResponse: Summary quality evaluation results
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class QualityDetailsResponse(BaseModel):
    """Schema for quality details response with all dimension scores."""
    
    resource_id: str
    quality_dimensions: Dict[str, float] = Field(
        description="Individual quality dimension scores (accuracy, completeness, consistency, timeliness, relevance)"
    )
    quality_overall: float = Field(description="Weighted overall quality score")
    quality_weights: Dict[str, float] = Field(description="Applied dimension weights")
    quality_last_computed: Optional[datetime] = Field(None, description="Last computation timestamp")
    quality_computation_version: Optional[str] = Field(None, description="Algorithm version")
    is_quality_outlier: bool = Field(False, description="Whether resource is flagged as quality outlier")
    needs_quality_review: bool = Field(False, description="Whether resource needs human review")
    outlier_score: Optional[float] = Field(None, description="Anomaly score (lower = more anomalous)")
    outlier_reasons: Optional[List[str]] = Field(None, description="Specific outlier reasons")


class QualityRecalculateRequest(BaseModel):
    """Schema for quality recalculation request."""
    
    resource_id: Optional[str] = Field(None, description="Single resource ID to recalculate")
    resource_ids: Optional[List[str]] = Field(None, description="Batch of resource IDs to recalculate")
    weights: Optional[Dict[str, float]] = Field(
        None,
        description="Custom dimension weights (must sum to 1.0 and include all five dimensions)"
    )
    
    @field_validator('weights')
    @classmethod
    def validate_weights(cls, v: Optional[Dict[str, float]]) -> Optional[Dict[str, float]]:
        """Validate that weights sum to 1.0 and include all dimensions."""
        if v is not None:
            required_dims = {"accuracy", "completeness", "consistency", "timeliness", "relevance"}
            if set(v.keys()) != required_dims:
                raise ValueError(f"Must specify all five dimensions: {required_dims}")
            
            weight_sum = sum(v.values())
            if abs(weight_sum - 1.0) > 0.01:
                raise ValueError(f"Weights must sum to 1.0, got {weight_sum}")
        
        return v
    
    @field_validator('resource_ids')
    @classmethod
    def validate_resource_ids(cls, v: Optional[List[str]], info) -> Optional[List[str]]:
        """Validate that either resource_id or resource_ids is provided."""
        # Access other field values through info.data
        resource_id = info.data.get('resource_id')
        if resource_id is None and (v is None or len(v) == 0):
            raise ValueError("Must provide either resource_id or resource_ids")
        return v


class OutlierResponse(BaseModel):
    """Schema for quality outlier response."""
    
    resource_id: str
    title: str
    quality_overall: float
    outlier_score: float
    outlier_reasons: List[str]
    needs_quality_review: bool


class OutlierListResponse(BaseModel):
    """Schema for paginated outlier list response."""
    
    total: int
    page: int
    limit: int
    outliers: List[OutlierResponse]


class DegradationResourceReport(BaseModel):
    """Schema for individual resource degradation report."""
    
    resource_id: str
    title: str
    old_quality: float
    new_quality: float
    degradation_pct: float


class DegradationReport(BaseModel):
    """Schema for quality degradation report."""
    
    time_window_days: int
    degraded_count: int
    degraded_resources: List[DegradationResourceReport]


class SummaryEvaluationResponse(BaseModel):
    """Schema for summary quality evaluation response."""
    
    resource_id: str
    summary_quality: Dict[str, float] = Field(description="All summary quality metrics")
    summary_quality_overall: float = Field(description="Composite summary quality score")


class QualityDistributionBin(BaseModel):
    """Schema for quality distribution histogram bin."""
    
    range: str = Field(description="Score range (e.g., '0.0-0.1')")
    count: int = Field(description="Number of resources in this bin")


class QualityStatistics(BaseModel):
    """Schema for quality statistics."""
    
    mean: float
    median: float
    std_dev: float


class QualityDistributionResponse(BaseModel):
    """Schema for quality distribution response."""
    
    dimension: str = Field(description="Quality dimension or 'overall'")
    bins: int = Field(description="Number of histogram bins")
    distribution: List[QualityDistributionBin]
    statistics: QualityStatistics


class QualityTrendDataPoint(BaseModel):
    """Schema for quality trend data point."""
    
    period: str = Field(description="Time period (e.g., '2025-W01', '2025-11', '2025-11-10')")
    avg_quality: float = Field(description="Average quality score for period")
    resource_count: int = Field(description="Number of resources in period")


class QualityTrendsResponse(BaseModel):
    """Schema for quality trends response."""
    
    dimension: str = Field(description="Quality dimension or 'overall'")
    granularity: str = Field(description="Time granularity (daily, weekly, monthly)")
    data_points: List[QualityTrendDataPoint]


class DimensionStatistics(BaseModel):
    """Schema for dimension statistics."""
    
    avg: float
    min: float
    max: float


class QualityDimensionsResponse(BaseModel):
    """Schema for quality dimensions response."""
    
    dimensions: Dict[str, DimensionStatistics] = Field(
        description="Statistics for each quality dimension"
    )
    overall: DimensionStatistics = Field(description="Overall quality statistics")
    total_resources: int = Field(description="Total number of resources with quality scores")


class ReviewQueueItem(BaseModel):
    """Schema for review queue item."""
    
    resource_id: str
    title: str
    quality_overall: Optional[float]
    is_quality_outlier: bool
    outlier_score: Optional[float]
    outlier_reasons: Optional[List[str]]
    quality_last_computed: Optional[datetime]


class ReviewQueueResponse(BaseModel):
    """Schema for review queue response."""
    
    total: int
    page: int
    limit: int
    review_queue: List[ReviewQueueItem]
