"""
Neo Alexandria 2.0 - Resources API Router

This module provides the REST API endpoints for resource management in Neo Alexandria 2.0.
It handles URL ingestion, CRUD operations, and resource querying with filtering and pagination.

Related files:
- app/services/resource_service.py: Business logic for resource operations
- app/schemas/resource.py: Pydantic schemas for request/response validation
- app/schemas/query.py: Query parameter schemas for filtering and pagination
- app/database/models.py: Resource database model
- app/database/base.py: Database session management

Endpoints:
- POST /resources: URL ingestion with content processing
- GET /resources: List resources with filtering, sorting, and pagination
- GET /resources/{id}: Retrieve a specific resource
- PUT /resources/{id}: Update resource metadata
- DELETE /resources/{id}: Delete a resource
"""

from __future__ import annotations

from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from sqlalchemy.orm import Session

from ..database.base import get_sync_db
from ..config.settings import get_settings
from ..schemas.resource import ResourceRead, ResourceUpdate, ResourceStatus
from ..schemas.query import PageParams, SortParams, ResourceFilters
from ..services.resource_service import (
    create_pending_resource,
    get_resource,
    list_resources,
    update_resource,
    delete_resource,
    process_ingestion,
)


router = APIRouter(prefix="", tags=["resources"])


class ResourceIngestRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    url: HttpUrl = Field(..., description="URL to ingest")
    title: Optional[str] = None
    description: Optional[str] = None
    creator: Optional[str] = None
    language: Optional[str] = None
    type: Optional[str] = None
    source: Optional[str] = None


class ResourceAccepted(BaseModel):
    id: str
    status: str = "pending"


@router.post("/resources", response_model=ResourceAccepted, status_code=status.HTTP_202_ACCEPTED)
async def create_resource_endpoint(
    payload: ResourceIngestRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_sync_db),
):
    try:
        # Convert payload to dict with string values for SQLite compatibility
        payload_dict = payload.model_dump(exclude_none=True)
        # Convert HttpUrl to string
        if "url" in payload_dict:
            payload_dict["url"] = str(payload_dict["url"])
        resource = create_pending_resource(db, payload_dict)
        # Derive engine URL from current DB bind so background uses the same database
        engine_url = None
        try:
            bind = db.get_bind()
            if bind is not None and hasattr(bind, "url"):
                engine_url = str(bind.url)
        except Exception:
            engine_url = get_settings().DATABASE_URL
        # Kick off background ingestion
        background.add_task(process_ingestion, str(resource.id), archive_root=None, ai=None, engine_url=engine_url)
        return ResourceAccepted(id=str(resource.id), status="pending")
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:  # pragma: no cover - unexpected error path
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to queue ingestion") from exc


@router.get("/resources/{resource_id}", response_model=ResourceRead)
async def get_resource_endpoint(resource_id: uuid.UUID, db: Session = Depends(get_sync_db)):
    resource = get_resource(db, str(resource_id))
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    # computed mapping for url
    resource.url = resource.source  # type: ignore[attr-defined]
    return resource


class ResourceListResponse(BaseModel):
    items: list[ResourceRead]
    total: int


@router.get("/resources", response_model=ResourceListResponse)
async def list_resources_endpoint(
    q: Optional[str] = None,
    classification_code: Optional[str] = None,
    type: Optional[str] = None,
    language: Optional[str] = None,
    read_status: Optional[str] = None,
    min_quality: Optional[float] = None,
    created_from: Optional[str] = None,
    created_to: Optional[str] = None,
    updated_from: Optional[str] = None,
    updated_to: Optional[str] = None,
    subject_any: Optional[str] = None,
    subject_all: Optional[str] = None,
    limit: int = 25,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
    db: Session = Depends(get_sync_db),
):
    # Parse comma-separated subject lists
    subject_any_list = subject_any.split(',') if subject_any else None
    subject_all_list = subject_all.split(',') if subject_all else None
    
    # Build pydantic structures from query params
    filters = ResourceFilters(
        q=q,
        classification_code=classification_code,
        type=type,
        language=language,
        read_status=read_status,  # Pydantic will validate
        min_quality=min_quality,
        created_from=created_from,
        created_to=created_to,
        updated_from=updated_from,
        updated_to=updated_to,
        subject_any=subject_any_list,
        subject_all=subject_all_list,
    )
    page = PageParams(limit=limit, offset=offset)
    sort = SortParams(sort_by=sort_by, sort_dir=sort_dir)

    items, total = list_resources(db, filters, page, sort)
    # Map url for response
    for it in items:
        it.url = it.source  # type: ignore[attr-defined]
    return ResourceListResponse(items=items, total=total)


@router.get("/resources/{resource_id}/status", response_model=ResourceStatus)
async def get_resource_status(resource_id: uuid.UUID, db: Session = Depends(get_sync_db)):
    resource = get_resource(db, str(resource_id))
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return resource  # ResourceStatus uses from_attributes


@router.put("/resources/{resource_id}", response_model=ResourceRead)
async def update_resource_endpoint(resource_id: uuid.UUID, payload: ResourceUpdate, db: Session = Depends(get_sync_db)):
    try:
        updated = update_resource(db, str(resource_id), payload)
        return updated
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")


@router.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource_endpoint(resource_id: uuid.UUID, db: Session = Depends(get_sync_db)):
    try:
        delete_resource(db, str(resource_id))
        return None
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")


class ClassificationOverrideRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=16, description="Classification code override")


@router.put("/resources/{resource_id}/classify", response_model=ResourceRead)
async def classify_resource_override(resource_id: uuid.UUID, payload: ClassificationOverrideRequest, db: Session = Depends(get_sync_db)):
    try:
        updated = update_resource(db, str(resource_id), ResourceUpdate(classification_code=payload.code))
        return updated
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")