"""
Neo Alexandria 2.0 - Authority Control API Router

This module provides API endpoints for the Authority Control System in Neo Alexandria 2.0.
It offers subject suggestions and classification tree access for frontend applications.

Related files:
- app/services/authority_service.py: AuthorityControl class for subject normalization
- app/services/classification_service.py: PersonalClassification for classification tree
- app/database/models.py: Authority and classification database models
- app/database/base.py: Database session management

Endpoints:
- GET /authority/subjects/suggest: Get subject suggestions based on partial input
- GET /authority/classification/tree: Get hierarchical classification tree
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database.base import get_sync_db
from ..services.authority_service import AuthorityControl
from ..services.classification_service import PersonalClassification


router = APIRouter(prefix="/authority", tags=["authority"]) 


@router.get("/subjects/suggest", response_model=list[str])
def suggest_subjects(q: str = Query(..., min_length=1), db: Session = Depends(get_sync_db)):
    svc = AuthorityControl(db)
    return svc.get_subject_suggestions(q)


@router.get("/classification/tree")
def get_classification_tree(db: Session = Depends(get_sync_db)):
    classifier = PersonalClassification()
    return classifier.get_classification_tree(db)


