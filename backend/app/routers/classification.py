"""
Neo Alexandria 2.0 - Classification API Router

This module provides API endpoints for the Personal Classification System in Neo Alexandria 2.0.
It offers access to the hierarchical classification tree for frontend applications.

Related files:
- app/services/classification_service.py: PersonalClassification class for classification logic
- app/database/models.py: ClassificationCode database model
- app/database/base.py: Database session management
- alembic/versions/20250912_add_classification_codes.py: Classification table and seed data

Endpoints:
- GET /classification/tree: Get hierarchical classification tree with UDC-inspired codes
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.base import get_sync_db
from backend.app.services.classification_service import PersonalClassification


router = APIRouter(prefix="/classification", tags=["classification"])


@router.get("/tree")
def get_classification_tree(db: Session = Depends(get_sync_db)):
    classifier = PersonalClassification()
    return classifier.get_classification_tree(db)


