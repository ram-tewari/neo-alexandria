"""
Authority Module Router

This module provides API endpoints for the Authority Control System.
It offers subject suggestions and classification tree access for frontend applications.

Endpoints:
- GET /authority/subjects/suggest: Get subject suggestions based on partial input
- GET /authority/classification/tree: Get hierarchical classification tree
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...shared.database import get_sync_db
from .service import AuthorityControl, PersonalClassification


router = APIRouter(prefix="/authority", tags=["authority"]) 


@router.get("/subjects/suggest", response_model=list[str])
def suggest_subjects(q: str = Query(..., min_length=1), db: Session = Depends(get_sync_db)):
    """
    Get subject suggestions based on partial input.
    
    Args:
        q: Partial subject string (minimum 1 character)
        db: Database session
        
    Returns:
        List of suggested subject strings
    """
    svc = AuthorityControl(db)
    return svc.get_subject_suggestions(q)


@router.get("/classification/tree")
def get_classification_tree(db: Session = Depends(get_sync_db)):
    """
    Get hierarchical classification tree.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with classification tree structure
    """
    classifier = PersonalClassification()
    return classifier.get_classification_tree(db)
