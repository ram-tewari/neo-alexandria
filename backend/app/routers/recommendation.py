"""
Neo Alexandria 2.0 - Phase 5.5 Recommendation System API Router

This module provides HTTP endpoints for the personalized recommendation engine.
It exposes RESTful APIs for generating content recommendations based on user preferences.

Related files:
- app/services/recommendation_service.py: Core recommendation logic
- app/schemas/recommendation.py: Request/response data models
- app/database/base.py: Database session management
- app/config/settings.py: Configuration parameters

Features:
- GET /recommendations: Generate personalized content recommendations
- Query parameter validation with sensible defaults
- Structured JSON responses with relevance scores and reasoning
- Error handling with appropriate HTTP status codes
- Integration with FastAPI dependency injection system

Endpoints:
- GET /recommendations?limit=N: Retrieve up to N recommendations (1-100, default: 10)

Response Format:
{
  "items": [
    {
      "url": "https://example.com/article",
      "title": "Article Title",
      "snippet": "Brief description...",
      "relevance_score": 0.85,
      "reasoning": ["Aligned with Machine Learning, Python"]
    }
  ]
}

Error Responses:
- 422: Invalid query parameters (limit out of range)
- 500: Internal server error (service failures)
"""

from __future__ import annotations


from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database.base import get_sync_db
from backend.app.schemas.recommendation import RecommendationResponse, RecommendedResource
from backend.app.services.recommendation_service import generate_recommendations


router = APIRouter(prefix="", tags=["recommendations"])


@router.get("/recommendations", response_model=RecommendationResponse, status_code=status.HTTP_200_OK)
def get_recommendations(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_sync_db)):
    try:
        recs = generate_recommendations(db, limit=limit)
        items = [RecommendedResource(**it) for it in recs]
        return RecommendationResponse(items=items)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate recommendations") from exc


