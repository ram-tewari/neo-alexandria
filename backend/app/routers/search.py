"""
Neo Alexandria 2.0 - Search API Router

This module provides the advanced search API endpoint for Neo Alexandria 2.0.
It implements full-text search with SQLite FTS5 support, faceting, and structured filtering.

Related files:
- app/services/search_service.py: AdvancedSearchService with FTS5 and faceting logic
- app/schemas/search.py: SearchQuery and SearchResults schemas
- app/schemas/resource.py: ResourceRead schema for search results
- app/database/base.py: Database session management
- alembic/versions/20250910_add_fts_and_triggers.py: FTS5 table and trigger setup

Features:
- Full-text search with SQLite FTS5 (with fallback to LIKE search)
- Faceted search results with counts
- Structured filtering by classification, type, language, etc.
- Pagination and sorting support
- Search result snippets (when FTS5 is available)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.base import get_sync_db
from backend.app.schemas.search import SearchQuery, SearchResults
from backend.app.schemas.resource import ResourceRead
from backend.app.services.search_service import AdvancedSearchService


router = APIRouter(prefix="", tags=["search"])


@router.post("/search", response_model=SearchResults, status_code=status.HTTP_200_OK)
def search_endpoint(payload: SearchQuery, db: Session = Depends(get_sync_db)):
    try:
        result = AdvancedSearchService.search(db, payload)
        # Service may return 3-tuple (fallback) or 4-tuple (fts with snippets)
        if len(result) == 4:
            items, total, facets, snippets = result
        else:
            items, total, facets = result
            snippets = {}
        # Map ORM to schema via from_attributes
        items_read = [ResourceRead.model_validate(it) for it in items]
        return SearchResults(total=total, items=items_read, facets=facets, snippets=snippets)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Search failed") from exc


