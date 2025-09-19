"""
Neo Alexandria 2.0 - Phase 5.5 Recommendation System Schemas

This module defines Pydantic models for the personalized recommendation engine.
It provides structured data models for recommendation requests and responses.

Related files:
- app/services/recommendation_service.py: Core recommendation logic
- app/routers/recommendation.py: API endpoints that use these schemas
- app/config/settings.py: Configuration for recommendation parameters

Features:
- Structured recommendation response models with validation
- Relevance score validation (0.0 to 1.0 range)
- Reasoning field for explainable recommendations
- Type-safe data transfer between service and API layers

Models:
- RecommendedResource: Individual recommendation item with metadata
- RecommendationResponse: Container for multiple recommendations
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class RecommendedResource(BaseModel):
    url: str
    title: str
    snippet: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    reasoning: List[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    items: List[RecommendedResource] = Field(default_factory=list)


