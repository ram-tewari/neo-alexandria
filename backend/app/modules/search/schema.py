"""
Search Module Schemas

Pydantic schemas for search functionality including:
- SearchQuery: Search query parameters
- SearchResults: Search results with facets and snippets
- ThreeWayHybridResults: Results from three-way hybrid search
- SearchFilters: Structured filtering options
- Facets: Faceted search results
- Evaluation schemas: For search quality evaluation
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, Field, field_validator

from ...schemas.resource import ResourceRead


class FacetBucket(BaseModel):
    key: str
    count: int


class Facets(BaseModel):
    classification_code: List[FacetBucket] = Field(default_factory=list)
    type: List[FacetBucket] = Field(default_factory=list)
    language: List[FacetBucket] = Field(default_factory=list)
    read_status: List[FacetBucket] = Field(default_factory=list)
    subject: List[FacetBucket] = Field(default_factory=list)


class SearchFilters(BaseModel):
    classification_code: Optional[List[str]] = None
    type: Optional[List[str]] = None
    language: Optional[List[str]] = None
    read_status: Optional[List[Literal["unread", "in_progress", "completed", "archived"]]] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    updated_from: Optional[datetime] = None
    updated_to: Optional[datetime] = None
    subject_any: Optional[List[str]] = None
    subject_all: Optional[List[str]] = None
    min_quality: Optional[float] = None


class SearchQuery(BaseModel):
    text: Optional[str] = None
    filters: Optional[SearchFilters] = None
    limit: int = 25
    offset: int = 0
    sort_by: Literal["relevance", "updated_at", "created_at", "quality_score", "title"] = "relevance"
    sort_dir: Literal["asc", "desc"] = "desc"
    hybrid_weight: Optional[float] = None  # 0.0=keyword only, 1.0=semantic only, None=use default

    @field_validator("limit")
    @classmethod
    def _validate_limit(cls, v: int) -> int:
        if not (1 <= v <= 100):
            raise ValueError("limit must be between 1 and 100")
        return v

    @field_validator("offset")
    @classmethod
    def _validate_offset(cls, v: int) -> int:
        if v < 0:
            raise ValueError("offset must be >= 0")
        return v

    @field_validator("hybrid_weight")
    @classmethod
    def _validate_hybrid_weight(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError("hybrid_weight must be between 0.0 and 1.0")
        return v


class SearchResults(BaseModel):
    total: int
    items: List[ResourceRead]
    facets: Facets
    snippets: dict[str, str] = Field(default_factory=dict)


class MethodContributions(BaseModel):
    """Contribution counts from each retrieval method"""
    fts5: int = 0
    dense: int = 0
    sparse: int = 0


class ThreeWayHybridResults(BaseModel):
    """Results from three-way hybrid search with metadata"""
    total: int
    items: List[ResourceRead]
    facets: Facets
    snippets: dict[str, str] = Field(default_factory=dict)
    latency_ms: float
    method_contributions: MethodContributions
    weights_used: List[float]


class ComparisonMethodResults(BaseModel):
    """Results from a single search method for comparison"""
    results: List[ResourceRead]
    latency_ms: float
    total: int = 0


class ComparisonResults(BaseModel):
    """Side-by-side comparison of different search methods"""
    query: str
    methods: dict[str, ComparisonMethodResults]


class RelevanceJudgments(BaseModel):
    """Relevance judgments for evaluation (0-3 scale)"""
    judgments: dict[str, int] = Field(
        description="Map of resource_id to relevance score (0=not relevant, 1=marginally, 2=relevant, 3=highly relevant)"
    )


class EvaluationMetrics(BaseModel):
    """Information retrieval metrics"""
    ndcg_at_20: float
    recall_at_20: float
    precision_at_20: float
    mrr: float


class EvaluationRequest(BaseModel):
    """Request for search quality evaluation"""
    query: str
    relevance_judgments: dict[str, int] = Field(
        description="Map of resource_id to relevance score (0-3)"
    )


class EvaluationResults(BaseModel):
    """Evaluation results with metrics and baseline comparison"""
    query: str
    metrics: EvaluationMetrics
    baseline_comparison: Optional[dict[str, float]] = None


class BatchSparseEmbeddingRequest(BaseModel):
    """Request for batch sparse embedding generation"""
    resource_ids: Optional[List[str]] = Field(
        None,
        description="Optional list of specific resource IDs to process. If None, processes all resources without sparse embeddings."
    )
    batch_size: Optional[int] = Field(
        32,
        description="Batch size for processing (32 for GPU, 8 for CPU)"
    )


class BatchSparseEmbeddingResponse(BaseModel):
    """Response for batch sparse embedding generation"""
    status: str
    job_id: str
    estimated_duration_minutes: int
    resources_to_process: int
