"""
Neo Alexandria 2.0 - Collection API Endpoints (Phase 7)

This module provides REST API endpoints for collection management and recommendations.

Related files:
- app/services/collection_service.py: Collection business logic
- app/schemas/collection.py: Request/response schemas
- app/database/models.py: Collection and Resource models
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from backend.app.database.base import get_sync_db
from backend.app.services.collection_service import CollectionService
from backend.app.schemas.collection import (
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    CollectionDetailResponse,
    CollectionListResponse,
    ResourceMembershipRequest,
    ResourceMembershipResponse,
    CollectionRecommendationsResponse,
    ResourceSummary,
    RecommendationItem,
)

router = APIRouter(prefix="/collections", tags=["collections"])


def _get_collection_service(db: Session = Depends(get_sync_db)) -> CollectionService:
    """Dependency to get collection service instance."""
    return CollectionService(db)


@router.post("", response_model=CollectionResponse, status_code=201)
async def create_collection(
    collection_data: CollectionCreate,
    user_id: str = Query(..., description="User ID (owner)"),
    service: CollectionService = Depends(_get_collection_service)
):
    """
    Create a new collection.
    
    Args:
        collection_data: Collection creation data
        user_id: User ID of the collection owner
        service: Collection service instance
        
    Returns:
        Created collection
    """
    try:
        collection = service.create_collection(
            owner_id=user_id,
            name=collection_data.name,
            description=collection_data.description,
            visibility=collection_data.visibility,
            parent_id=collection_data.parent_id
        )
        
        return CollectionResponse(
            id=str(collection.id),
            name=collection.name,
            description=collection.description,
            owner_id=collection.owner_id,
            visibility=collection.visibility,
            parent_id=str(collection.parent_id) if collection.parent_id else None,
            created_at=collection.created_at,
            updated_at=collection.updated_at,
            resource_count=len(collection.resources) if collection.resources else 0
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=CollectionListResponse)
async def list_collections(
    user_id: Optional[str] = Query(None, description="User ID for access control"),
    owner_filter: Optional[str] = Query(None, description="Filter by owner ID"),
    visibility_filter: Optional[str] = Query(None, description="Filter by visibility"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: CollectionService = Depends(_get_collection_service)
):
    """
    List collections with filtering and pagination.
    
    Args:
        user_id: Optional user ID for access control
        owner_filter: Optional filter by owner ID
        visibility_filter: Optional filter by visibility
        page: Page number (1-indexed)
        limit: Items per page
        service: Collection service instance
        
    Returns:
        Paginated list of collections
    """
    try:
        collections, total = service.list_collections(
            user_id=user_id,
            owner_filter=owner_filter,
            visibility_filter=visibility_filter,
            page=page,
            limit=limit
        )
        
        items = [
            CollectionResponse(
                id=str(c.id),
                name=c.name,
                description=c.description,
                owner_id=c.owner_id,
                visibility=c.visibility,
                parent_id=str(c.parent_id) if c.parent_id else None,
                created_at=c.created_at,
                updated_at=c.updated_at,
                resource_count=len(c.resources) if c.resources else 0
            )
            for c in collections
        ]
        
        return CollectionListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{collection_id}", response_model=CollectionDetailResponse)
async def get_collection(
    collection_id: str,
    user_id: Optional[str] = Query(None, description="User ID for access control"),
    service: CollectionService = Depends(_get_collection_service)
):
    """
    Retrieve a specific collection with resources.
    
    Args:
        collection_id: Collection UUID
        user_id: Optional user ID for access control
        service: Collection service instance
        
    Returns:
        Collection with embedded resources
    """
    try:
        collection = service.get_collection(collection_id, user_id)
        
        # Build resource summaries
        resources = [
            ResourceSummary(
                id=str(r.id),
                title=r.title,
                quality_score=r.quality_score,
                classification_code=r.classification_code
            )
            for r in collection.resources
        ] if collection.resources else []
        
        # Build subcollection summaries
        subcollections = [
            CollectionResponse(
                id=str(sc.id),
                name=sc.name,
                description=sc.description,
                owner_id=sc.owner_id,
                visibility=sc.visibility,
                parent_id=str(sc.parent_id) if sc.parent_id else None,
                created_at=sc.created_at,
                updated_at=sc.updated_at,
                resource_count=len(sc.resources) if sc.resources else 0
            )
            for sc in collection.subcollections
        ] if collection.subcollections else []
        
        return CollectionDetailResponse(
            id=str(collection.id),
            name=collection.name,
            description=collection.description,
            owner_id=collection.owner_id,
            visibility=collection.visibility,
            parent_id=str(collection.parent_id) if collection.parent_id else None,
            created_at=collection.created_at,
            updated_at=collection.updated_at,
            resource_count=len(resources),
            resources=resources,
            subcollections=subcollections
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        elif "access denied" in str(e).lower():
            raise HTTPException(status_code=403, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))


@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: str,
    updates: CollectionUpdate,
    user_id: str = Query(..., description="User ID"),
    service: CollectionService = Depends(_get_collection_service)
):
    """
    Update collection metadata.
    
    Args:
        collection_id: Collection UUID
        updates: Fields to update
        user_id: User ID requesting the update
        service: Collection service instance
        
    Returns:
        Updated collection
    """
    try:
        update_dict = updates.model_dump(exclude_unset=True)
        collection = service.update_collection(collection_id, user_id, update_dict)
        
        return CollectionResponse(
            id=str(collection.id),
            name=collection.name,
            description=collection.description,
            owner_id=collection.owner_id,
            visibility=collection.visibility,
            parent_id=str(collection.parent_id) if collection.parent_id else None,
            created_at=collection.created_at,
            updated_at=collection.updated_at,
            resource_count=len(collection.resources) if collection.resources else 0
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        elif "access denied" in str(e).lower():
            raise HTTPException(status_code=403, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{collection_id}", status_code=204)
async def delete_collection(
    collection_id: str,
    user_id: str = Query(..., description="User ID"),
    service: CollectionService = Depends(_get_collection_service)
):
    """
    Delete a collection.
    
    Args:
        collection_id: Collection UUID
        user_id: User ID requesting the deletion
        service: Collection service instance
        
    Returns:
        204 No Content
    """
    try:
        service.delete_collection(collection_id, user_id)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        elif "access denied" in str(e).lower():
            raise HTTPException(status_code=403, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))


@router.post("/{collection_id}/resources", response_model=ResourceMembershipResponse)
async def add_resources_to_collection(
    collection_id: str,
    request: ResourceMembershipRequest,
    user_id: str = Query(..., description="User ID"),
    background_tasks: BackgroundTasks = None,
    service: CollectionService = Depends(_get_collection_service)
):
    """
    Add resources to a collection (batch operation).
    
    Args:
        collection_id: Collection UUID
        request: Resource IDs to add
        user_id: User ID requesting the operation
        background_tasks: FastAPI background tasks
        service: Collection service instance
        
    Returns:
        Membership operation result
    """
    try:
        # Get initial resource count
        collection_before = service.get_collection(collection_id, user_id)
        initial_count = len(collection_before.resources) if collection_before.resources else 0
        
        # Add resources
        collection = service.add_resources(
            collection_id=collection_id,
            user_id=user_id,
            resource_ids=request.resource_ids
        )
        
        # Get final resource count
        final_count = len(collection.resources) if collection.resources else 0
        added_count = final_count - initial_count
        
        # Queue embedding recomputation in background
        if background_tasks and added_count > 0:
            background_tasks.add_task(service.recompute_embedding, collection_id)
        
        return ResourceMembershipResponse(
            collection_id=collection_id,
            added_count=added_count,
            total_resources=final_count
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        elif "access denied" in str(e).lower():
            raise HTTPException(status_code=403, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{collection_id}/resources", response_model=ResourceMembershipResponse)
async def remove_resources_from_collection(
    collection_id: str,
    request: ResourceMembershipRequest,
    user_id: str = Query(..., description="User ID"),
    background_tasks: BackgroundTasks = None,
    service: CollectionService = Depends(_get_collection_service)
):
    """
    Remove resources from a collection (batch operation).
    
    Args:
        collection_id: Collection UUID
        request: Resource IDs to remove
        user_id: User ID requesting the operation
        background_tasks: FastAPI background tasks
        service: Collection service instance
        
    Returns:
        Membership operation result
    """
    try:
        # Get initial resource count
        collection_before = service.get_collection(collection_id, user_id)
        initial_count = len(collection_before.resources) if collection_before.resources else 0
        
        # Remove resources
        collection = service.remove_resources(
            collection_id=collection_id,
            user_id=user_id,
            resource_ids=request.resource_ids
        )
        
        # Get final resource count
        final_count = len(collection.resources) if collection.resources else 0
        removed_count = initial_count - final_count
        
        # Queue embedding recomputation in background
        if background_tasks and removed_count > 0:
            background_tasks.add_task(service.recompute_embedding, collection_id)
        
        return ResourceMembershipResponse(
            collection_id=collection_id,
            removed_count=removed_count,
            total_resources=final_count
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        elif "access denied" in str(e).lower():
            raise HTTPException(status_code=403, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))


@router.get("/{collection_id}/recommendations", response_model=CollectionRecommendationsResponse)
async def get_collection_recommendations(
    collection_id: str,
    user_id: Optional[str] = Query(None, description="User ID for access control"),
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations per type"),
    service: CollectionService = Depends(_get_collection_service)
):
    """
    Get recommendations based on collection's aggregate embedding.
    
    Args:
        collection_id: Collection UUID
        user_id: Optional user ID for access control
        limit: Number of recommendations per type
        service: Collection service instance
        
    Returns:
        Resource and collection recommendations
    """
    try:
        recommendations = service.get_collection_recommendations(
            collection_id=collection_id,
            user_id=user_id or "anonymous",
            limit=limit
        )
        
        # Convert to response format
        resource_recs = [
            RecommendationItem(**item)
            for item in recommendations["resource_recommendations"]
        ]
        
        collection_recs = [
            RecommendationItem(**item)
            for item in recommendations["collection_recommendations"]
        ]
        
        return CollectionRecommendationsResponse(
            collection_id=collection_id,
            resource_recommendations=resource_recs,
            collection_recommendations=collection_recs
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        elif "access denied" in str(e).lower():
            raise HTTPException(status_code=403, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
