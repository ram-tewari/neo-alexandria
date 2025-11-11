"""
Neo Alexandria 2.0 - Taxonomy Schemas (Phase 8.5)

This module defines Pydantic schemas for taxonomy and ML classification API requests and responses.

Related files:
- app/database/models.py: TaxonomyNode and ResourceTaxonomy models
- app/routers/taxonomy.py: Taxonomy API endpoints (to be implemented)
- app/services/taxonomy_service.py: Taxonomy business logic
- app/services/ml_classification_service.py: ML classification service
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TaxonomyNodeCreate(BaseModel):
    """Schema for creating a new taxonomy node."""
    name: str = Field(..., min_length=1, max_length=255, description="Category name")
    parent_id: Optional[str] = Field(None, description="Parent node UUID for hierarchical organization")
    description: Optional[str] = Field(None, description="Category description")
    keywords: Optional[List[str]] = Field(None, description="Related keywords for the category")
    allow_resources: bool = Field(default=True, description="Whether resources can be directly assigned to this node")


class TaxonomyNodeUpdate(BaseModel):
    """Schema for updating taxonomy node metadata."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    keywords: Optional[List[str]] = Field(None, description="Related keywords for the category")
    allow_resources: Optional[bool] = Field(None, description="Whether resources can be directly assigned to this node")


class TaxonomyNodeResponse(BaseModel):
    """Schema for taxonomy node API responses."""
    id: str = Field(..., description="Taxonomy node UUID")
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL-friendly identifier")
    parent_id: Optional[str] = Field(None, description="Parent node UUID")
    level: int = Field(..., description="Tree depth (0 for root nodes)")
    path: str = Field(..., description="Materialized path (e.g., '/computer-science/machine-learning')")
    description: Optional[str] = Field(None, description="Category description")
    keywords: Optional[List[str]] = Field(default=None, description="Related keywords")
    resource_count: int = Field(..., description="Direct resource count")
    descendant_resource_count: int = Field(..., description="Total resources including subcategories")
    is_leaf: bool = Field(..., description="Whether node has children")
    allow_resources: bool = Field(..., description="Whether resources can be assigned")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Custom validation to handle UUID and keywords conversion."""
        if hasattr(obj, '__dict__'):
            data = {}
            for key, value in obj.__dict__.items():
                if key.startswith('_'):
                    continue
                if key in ('id', 'parent_id') and value is not None:
                    data[key] = str(value)
                elif key == 'keywords' and value is not None:
                    # Ensure keywords is a list
                    if isinstance(value, str):
                        import json
                        try:
                            data[key] = json.loads(value)
                        except:
                            data[key] = []
                    else:
                        data[key] = value if isinstance(value, list) else []
                else:
                    data[key] = value
            return cls(**data)
        return super().model_validate(obj, **kwargs)


class TaxonomyNodeTree(BaseModel):
    """Schema for nested taxonomy tree structure."""
    id: str = Field(..., description="Taxonomy node UUID")
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL-friendly identifier")
    parent_id: Optional[str] = Field(default=None, description="Parent node UUID")
    level: int = Field(..., description="Tree depth (0 for root nodes)")
    path: str = Field(..., description="Materialized path")
    description: Optional[str] = Field(default=None, description="Category description")
    keywords: Optional[List[str]] = Field(default=None, description="Related keywords")
    resource_count: int = Field(..., description="Direct resource count")
    descendant_resource_count: int = Field(..., description="Total resources including subcategories")
    is_leaf: bool = Field(..., description="Whether node has children")
    allow_resources: bool = Field(..., description="Whether resources can be assigned")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    children: List["TaxonomyNodeTree"] = Field(default_factory=list, description="Child nodes")
    
    class Config:
        from_attributes = True


class TaxonomyNodeMove(BaseModel):
    """Schema for moving a taxonomy node to a new parent."""
    new_parent_id: Optional[str] = Field(None, description="New parent node UUID (null for root)")


class ClassificationFeedback(BaseModel):
    """Schema for submitting human classification feedback for active learning."""
    resource_id: str = Field(..., description="Resource UUID to classify")
    correct_taxonomy_ids: List[str] = Field(
        ..., 
        min_items=1, 
        description="Correct taxonomy node UUIDs for this resource"
    )


class LabeledExample(BaseModel):
    """Schema for a single labeled training example."""
    text: str = Field(..., description="Text content to classify")
    taxonomy_ids: List[str] = Field(..., min_items=1, description="Taxonomy node UUIDs for this text")


class ClassifierTrainingRequest(BaseModel):
    """Schema for initiating ML classifier fine-tuning."""
    labeled_data: List[LabeledExample] = Field(
        ..., 
        min_items=1, 
        description="Labeled training examples"
    )
    unlabeled_texts: Optional[List[str]] = Field(
        None, 
        description="Unlabeled texts for semi-supervised learning"
    )
    epochs: int = Field(default=3, ge=1, le=10, description="Number of training epochs")
    batch_size: int = Field(default=16, ge=1, le=64, description="Training batch size")
    learning_rate: float = Field(default=2e-5, gt=0, description="Learning rate for fine-tuning")


class ClassifierTrainingResponse(BaseModel):
    """Schema for training task response."""
    task_id: str = Field(..., description="Background task identifier")
    status: str = Field(..., description="Task status (e.g., 'queued', 'running')")
    message: str = Field(..., description="Status message")


class ClassificationResult(BaseModel):
    """Schema for a single classification result."""
    taxonomy_node_id: str = Field(..., description="Taxonomy node UUID")
    taxonomy_node_name: str = Field(..., description="Category name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence score")
    needs_review: bool = Field(..., description="Whether this classification needs human review")


class ResourceClassificationResponse(BaseModel):
    """Schema for resource classification response."""
    resource_id: str = Field(..., description="Resource UUID")
    classifications: List[ClassificationResult] = Field(
        default_factory=list, 
        description="Classification results"
    )
    predicted_by: str = Field(..., description="Model version or 'manual'")


class UncertainSample(BaseModel):
    """Schema for an uncertain sample identified by active learning."""
    resource_id: str = Field(..., description="Resource UUID")
    resource_title: str = Field(..., description="Resource title")
    uncertainty_score: float = Field(..., ge=0.0, le=1.0, description="Uncertainty score (higher = more uncertain)")
    current_classifications: List[ClassificationResult] = Field(
        default_factory=list, 
        description="Current predicted classifications"
    )


class UncertainSamplesResponse(BaseModel):
    """Schema for uncertain samples list response."""
    samples: List[UncertainSample] = Field(default_factory=list, description="Uncertain samples for review")
    total: int = Field(..., description="Total number of samples")


class ClassificationMetrics(BaseModel):
    """Schema for classification model evaluation metrics."""
    f1_score: float = Field(..., ge=0.0, le=1.0, description="F1 score (macro average)")
    precision: float = Field(..., ge=0.0, le=1.0, description="Precision (macro average)")
    recall: float = Field(..., ge=0.0, le=1.0, description="Recall (macro average)")
    model_version: str = Field(..., description="Model version identifier")


class TaxonomyStatsResponse(BaseModel):
    """Schema for taxonomy statistics."""
    total_nodes: int = Field(..., description="Total number of taxonomy nodes")
    total_resources_classified: int = Field(..., description="Total resources with classifications")
    avg_confidence: float = Field(..., ge=0.0, le=1.0, description="Average classification confidence")
    resources_needing_review: int = Field(..., description="Number of resources flagged for review")
    model_version: Optional[str] = Field(None, description="Current model version")
