"""
Taxonomy Router

FastAPI router for taxonomy and classification endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional
from pydantic import BaseModel

from app.shared.database import get_sync_db
from app.modules.taxonomy.service import TaxonomyService

taxonomy_router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])


class CategoryCreate(BaseModel):
    """Schema for creating a category."""
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    allow_resources: bool = True


class ClassifyRequest(BaseModel):
    """Schema for classification request."""
    resource_id: str
    text: str


@taxonomy_router.post("/categories")
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_sync_db)
) -> Dict:
    """
    Create a new taxonomy category.
    
    Args:
        data: Category creation data
        db: Database session
        
    Returns:
        Created category information
    """
    service = TaxonomyService()
    
    try:
        category = service.create_category(
            name=data.name,
            db=db,
            parent_id=data.parent_id,
            description=data.description,
            allow_resources=data.allow_resources
        )
        
        return {
            "id": str(category.id),
            "name": category.name,
            "slug": category.slug,
            "parent_id": str(category.parent_id) if category.parent_id else None,
            "level": category.level,
            "path": category.path,
            "description": category.description,
            "allow_resources": category.allow_resources
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create category: {str(e)}")


@taxonomy_router.post("/classify/{resource_id}")
def classify_resource(
    resource_id: str,
    use_ml: bool = True,
    use_rules: bool = True,
    db: Session = Depends(get_sync_db)
) -> Dict:
    """
    Classify a resource using ML and/or rule-based classification.
    
    Args:
        resource_id: ID of the resource to classify
        use_ml: Whether to use ML-based classification
        use_rules: Whether to use rule-based classification
        db: Database session
        
    Returns:
        Classification results with primary and alternative predictions
        
    **Validates: Requirements 9.10, 10.1-10.5**
    """
    from app.modules.taxonomy.classification_service import ClassificationService
    
    service = ClassificationService(db)
    
    try:
        result = service.classify_resource(
            resource_id=resource_id,
            use_ml=use_ml,
            use_rules=use_rules,
            apply_to_resource=True
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )


@taxonomy_router.get("/predictions/{resource_id}")
def get_predictions(
    resource_id: str,
    db: Session = Depends(get_sync_db)
) -> Dict:
    """
    Get classification predictions for a resource.
    
    Args:
        resource_id: ID of the resource
        db: Database session
        
    Returns:
        Existing classification or None
        
    **Validates: Requirement 9.10**
    """
    from app.modules.taxonomy.classification_service import ClassificationService
    
    service = ClassificationService(db)
    
    try:
        result = service.get_classification(resource_id)
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"No classification found for resource {resource_id}"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get predictions: {str(e)}"
        )


@taxonomy_router.post("/retrain")
def retrain_model(
    training_data: Dict,
    validation_split: float = 0.2,
    model_type: str = "random_forest",
    db: Session = Depends(get_sync_db)
) -> Dict:
    """
    Retrain the ML classification model with new labeled data.
    
    Args:
        training_data: Dictionary with "samples" key containing list of
                      {"resource_id": str, "node_id": str} objects
        validation_split: Fraction of data for validation (default: 0.2)
        model_type: Type of model to train ("random_forest" or "logistic")
        db: Database session
        
    Returns:
        Training metrics (accuracy, f1_score, etc.)
        
    **Validates: Requirements 9.5, 9.6, 9.7, 9.10**
    """
    from app.modules.taxonomy.ml_service import MLClassificationService
    
    service = MLClassificationService(db)
    
    try:
        # Extract training samples
        samples = training_data.get("samples", [])
        if not samples:
            raise HTTPException(
                status_code=400,
                detail="No training samples provided"
            )
        
        # Convert to list of tuples
        training_tuples = [
            (sample["resource_id"], sample["node_id"])
            for sample in samples
        ]
        
        # Retrain model
        metrics = service.retrain_model(
            training_data=training_tuples,
            validation_split=validation_split,
            model_type=model_type
        )
        
        return metrics
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model retraining failed: {str(e)}"
        )


@taxonomy_router.get("/uncertain")
def get_uncertain_predictions(
    threshold: float = 0.5,
    limit: int = 100,
    db: Session = Depends(get_sync_db)
) -> Dict:
    """
    Get resources with uncertain classifications for active learning.
    
    Returns resources where the classification confidence is below
    the threshold, indicating they would benefit from manual review.
    
    Args:
        threshold: Confidence threshold (default: 0.5)
        limit: Maximum number of resources to return (default: 100)
        db: Database session
        
    Returns:
        Dictionary with list of uncertain resource IDs
        
    **Validates: Requirements 9.4, 9.10**
    """
    from app.modules.taxonomy.ml_service import MLClassificationService
    
    service = MLClassificationService(db)
    
    try:
        uncertain_ids = service.identify_uncertain_predictions(
            threshold=threshold,
            limit=limit
        )
        
        return {
            "threshold": threshold,
            "count": len(uncertain_ids),
            "resource_ids": uncertain_ids
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to identify uncertain predictions: {str(e)}"
        )
