"""
Taxonomy Schemas

Pydantic schemas for taxonomy and classification requests/responses.
Placeholder - will be populated by moving schemas from app/schemas/
"""

from pydantic import BaseModel


class TaxonomyNodeCreate(BaseModel):
    """Schema for creating a taxonomy node"""
    pass


class TaxonomyNodeUpdate(BaseModel):
    """Schema for updating a taxonomy node"""
    pass


class TaxonomyNodeResponse(BaseModel):
    """Schema for taxonomy node response"""
    pass


class TaxonomyTreeResponse(BaseModel):
    """Schema for taxonomy tree response"""
    pass


class ClassificationRequest(BaseModel):
    """Schema for classification request"""
    pass


class ClassificationResponse(BaseModel):
    """Schema for classification response"""
    pass


class TrainingRequest(BaseModel):
    """Schema for model training request"""
    pass


class TrainingResponse(BaseModel):
    """Schema for model training response"""
    pass


class ActiveLearningRequest(BaseModel):
    """Schema for active learning request"""
    pass


class ActiveLearningResponse(BaseModel):
    """Schema for active learning response"""
    pass
