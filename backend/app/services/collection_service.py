"""
Neo Alexandria 2.0 - Collection Service (Phase 7)

This module handles collection management operations for Neo Alexandria 2.0.
It provides CRUD operations, resource membership management, aggregate embedding computation,
hierarchical validation, and recommendation generation.

Related files:
- app/database/models.py: Collection, CollectionResource, and Resource models
- app/routers/collections.py: Collection API endpoints
- app/schemas/collection.py: Pydantic schemas for API validation
- app/services/resource_service.py: Resource service integration

Features:
- Collection CRUD with ownership and access control
- Resource membership management (batch operations)
- Aggregate embedding computation from member resources
- Hierarchical collection organization with cycle prevention
- Collection-based recommendations via semantic similarity
"""

from __future__ import annotations

import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, delete

from backend.app.database.models import Collection, CollectionResource, Resource
from backend.app.database.base import Base


class CollectionService:
    """
    Handles collection management operations.
    
    This service provides methods for creating, reading, updating, and deleting collections,
    managing resource membership, computing aggregate embeddings, validating hierarchies,
    and generating recommendations based on semantic similarity.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the collection service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        
        # Ensure tables exist (safety check)
        try:
            Base.metadata.create_all(bind=db.get_bind())
        except Exception:
            pass

    def create_collection(
        self,
        owner_id: str,
        name: str,
        description: Optional[str] = None,
        visibility: str = "private",
        parent_id: Optional[str] = None
    ) -> Collection:
        """
        Create a new collection with validation.
        
        Algorithm:
        1. Validate name length (1-255 characters)
        2. Validate visibility value (private/shared/public)
        3. If parent_id provided:
           - Verify parent exists
           - Verify owner matches
           - Call validate_hierarchy to prevent circular references
        4. Create Collection instance with uuid4() id
        5. Commit to database and return Collection object
        
        Args:
            owner_id: User ID of the collection owner
            name: Collection name (1-255 characters)
            description: Optional collection description
            visibility: Access control level (private/shared/public)
            parent_id: Optional parent collection UUID for hierarchical organization
            
        Returns:
            Created Collection object
            
        Raises:
            ValueError: If validation fails (name length, visibility, parent not found, circular reference)
        """
        # Validate name length
        if not name or len(name) < 1:
            raise ValueError("Collection name must be at least 1 character")
        if len(name) > 255:
            raise ValueError("Collection name must not exceed 255 characters")
        
        # Validate visibility
        valid_visibility = ["private", "shared", "public"]
        if visibility not in valid_visibility:
            raise ValueError(f"Visibility must be one of: {', '.join(valid_visibility)}")
        
        # Validate parent if provided
        parent_uuid = None
        if parent_id:
            try:
                parent_uuid = uuid.UUID(parent_id)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid parent_id format: {parent_id}")
            
            # Verify parent exists
            result = self.db.execute(
                select(Collection).filter(Collection.id == parent_uuid)
            )
            parent = result.scalar_one_or_none()
            
            if not parent:
                raise ValueError(f"Parent collection not found: {parent_id}")
            
            # Verify owner matches
            if parent.owner_id != owner_id:
                raise ValueError("Cannot create subcollection: parent collection belongs to different owner")
        
        # Create collection
        collection = Collection(
            id=uuid.uuid4(),
            name=name,
            description=description,
            owner_id=owner_id,
            visibility=visibility,
            parent_id=parent_uuid
        )
        
        # Validate hierarchy (prevent circular references)
        if parent_uuid:
            # We need to add the collection temporarily to validate hierarchy
            self.db.add(collection)
            self.db.flush()  # Flush to get the ID without committing
            
            try:
                self.validate_hierarchy(str(collection.id), str(parent_uuid))
            except ValueError:
                self.db.rollback()
                raise
        
        self.db.add(collection)
        self.db.commit()
        self.db.refresh(collection)
        
        return collection

    def get_collection(
        self,
        collection_id: str,
        user_id: Optional[str] = None
    ) -> Collection:
        """
        Retrieve a collection with access control.
        
        Algorithm:
        1. Query Collection by id with eager-loaded resources
        2. Raise ValueError if not found
        3. Check access control:
           - If visibility='private', verify user_id == owner_id
           - If visibility='public', allow access
           - If visibility='shared', allow owner or check permissions (future)
        4. Return Collection object
        
        Args:
            collection_id: UUID of the collection to retrieve
            user_id: Optional user ID for access control checks
            
        Returns:
            Collection object with eager-loaded resources
            
        Raises:
            ValueError: If collection not found or access denied
        """
        # Convert string collection_id to UUID
        try:
            collection_uuid = uuid.UUID(collection_id)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid collection ID: {collection_id}")
        
        # Query collection with eager-loaded resources
        result = self.db.execute(
            select(Collection)
            .options(joinedload(Collection.resources))
            .filter(Collection.id == collection_uuid)
        )
        collection = result.unique().scalar_one_or_none()
        
        if not collection:
            raise ValueError(f"Collection not found: {collection_id}")
        
        # Access control
        if collection.visibility == "private":
            if not user_id or user_id != collection.owner_id:
                raise ValueError("Access denied: collection is private")
        elif collection.visibility == "shared":
            # For now, shared collections are accessible to owner only
            # Future: implement explicit permission checks
            if not user_id or user_id != collection.owner_id:
                raise ValueError("Access denied: collection is shared")
        # Public collections are accessible to all
        
        return collection

    def update_collection(
        self,
        collection_id: str,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Collection:
        """
        Update collection metadata.
        
        Algorithm:
        1. Retrieve collection using get_collection (enforces access)
        2. Verify user_id == owner_id (only owner can update)
        3. Validate updated fields:
           - name length (1-255 characters)
           - visibility value (private/shared/public)
        4. If parent_id changed, call validate_hierarchy
        5. Apply updates to collection object
        6. Update updated_at timestamp
        7. Commit and return updated Collection
        
        Args:
            collection_id: UUID of the collection to update
            user_id: User ID requesting the update
            updates: Dictionary of fields to update
            
        Returns:
            Updated Collection object
            
        Raises:
            ValueError: If validation fails or user is not owner
        """
        # Retrieve collection (enforces access control)
        collection = self.get_collection(collection_id, user_id)
        
        # Verify ownership
        if collection.owner_id != user_id:
            raise ValueError("Access denied: only collection owner can update")
        
        # Validate and apply updates
        if "name" in updates:
            name = updates["name"]
            if not name or len(name) < 1:
                raise ValueError("Collection name must be at least 1 character")
            if len(name) > 255:
                raise ValueError("Collection name must not exceed 255 characters")
            collection.name = name
        
        if "description" in updates:
            collection.description = updates["description"]
        
        if "visibility" in updates:
            visibility = updates["visibility"]
            valid_visibility = ["private", "shared", "public"]
            if visibility not in valid_visibility:
                raise ValueError(f"Visibility must be one of: {', '.join(valid_visibility)}")
            collection.visibility = visibility
        
        if "parent_id" in updates:
            new_parent_id = updates["parent_id"]
            
            # Handle None (remove parent)
            if new_parent_id is None:
                collection.parent_id = None
            else:
                # Validate parent exists and owner matches
                try:
                    parent_uuid = uuid.UUID(new_parent_id)
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid parent_id format: {new_parent_id}")
                
                result = self.db.execute(
                    select(Collection).filter(Collection.id == parent_uuid)
                )
                parent = result.scalar_one_or_none()
                
                if not parent:
                    raise ValueError(f"Parent collection not found: {new_parent_id}")
                
                if parent.owner_id != user_id:
                    raise ValueError("Cannot set parent: parent collection belongs to different owner")
                
                # Validate hierarchy (prevent circular references)
                self.validate_hierarchy(collection_id, new_parent_id)
                
                collection.parent_id = parent_uuid
        
        # Update timestamp
        collection.updated_at = datetime.now(timezone.utc)
        
        self.db.add(collection)
        self.db.commit()
        self.db.refresh(collection)
        
        return collection

    def delete_collection(
        self,
        collection_id: str,
        user_id: str
    ) -> None:
        """
        Delete a collection and cascade to subcollections.
        
        Algorithm:
        1. Retrieve collection and verify ownership
        2. Delete collection (CASCADE will handle subcollections and associations)
        3. Commit transaction
        
        Args:
            collection_id: UUID of the collection to delete
            user_id: User ID requesting the deletion
            
        Raises:
            ValueError: If collection not found or user is not owner
        """
        # Retrieve collection (enforces access control)
        collection = self.get_collection(collection_id, user_id)
        
        # Verify ownership
        if collection.owner_id != user_id:
            raise ValueError("Access denied: only collection owner can delete")
        
        # Delete collection (cascade will handle subcollections and associations)
        self.db.delete(collection)
        self.db.commit()

    def list_collections(
        self,
        user_id: Optional[str] = None,
        owner_filter: Optional[str] = None,
        visibility_filter: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Collection], int]:
        """
        List collections with filtering and pagination.
        
        Algorithm:
        1. Build base query for Collection
        2. Apply owner filter if provided
        3. Apply visibility filter if provided
        4. Apply access control: include collections where user is owner OR visibility is public
        5. Count total results before pagination
        6. Apply sorting (created_at DESC) and pagination (offset/limit)
        7. Return tuple of (collections list, total count)
        
        Args:
            user_id: Optional user ID for access control
            owner_filter: Optional filter by owner_id
            visibility_filter: Optional filter by visibility (private/shared/public)
            page: Page number (1-indexed)
            limit: Items per page (max 100)
            
        Returns:
            Tuple of (list of Collection objects, total count)
        """
        # Build base query
        query = select(Collection)
        
        # Apply owner filter
        if owner_filter:
            query = query.filter(Collection.owner_id == owner_filter)
        
        # Apply visibility filter
        if visibility_filter:
            valid_visibility = ["private", "shared", "public"]
            if visibility_filter not in valid_visibility:
                raise ValueError(f"Visibility filter must be one of: {', '.join(valid_visibility)}")
            query = query.filter(Collection.visibility == visibility_filter)
        
        # Apply access control
        if user_id:
            # Include collections where user is owner OR visibility is public
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    Collection.owner_id == user_id,
                    Collection.visibility == "public"
                )
            )
        else:
            # No user_id provided, only show public collections
            query = query.filter(Collection.visibility == "public")
        
        # Count total results before pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_result = self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting (created_at DESC)
        query = query.order_by(Collection.created_at.desc())
        
        # Apply pagination
        limit = min(limit, 100)  # Cap at 100
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = self.db.execute(query)
        collections = result.scalars().all()
        
        return list(collections), total

    def validate_hierarchy(
        self,
        collection_id: str,
        new_parent_id: str
    ) -> bool:
        """
        Validate hierarchy to prevent circular references.
        
        Algorithm:
        1. If new_parent_id is None, return True (top-level collection)
        2. Start traversal at new_parent_id
        3. Follow parent_id chain up the hierarchy
        4. If collection_id encountered, raise ValueError (circular reference)
        5. If None reached, return True (valid hierarchy)
        6. Limit traversal depth to 10 levels to prevent infinite loops
        
        Args:
            collection_id: UUID of the collection being updated
            new_parent_id: UUID of the proposed parent
            
        Returns:
            True if hierarchy is valid
            
        Raises:
            ValueError: If circular reference detected
        """
        if not new_parent_id:
            return True
        
        # Convert to UUIDs
        try:
            collection_uuid = uuid.UUID(collection_id)
            parent_uuid = uuid.UUID(new_parent_id)
        except (ValueError, TypeError):
            raise ValueError("Invalid UUID format")
        
        # Traverse up the parent chain
        current_id = parent_uuid
        depth = 0
        max_depth = 10
        
        while current_id and depth < max_depth:
            # Check if we've encountered the collection being updated
            if current_id == collection_uuid:
                raise ValueError("Circular reference detected: collection cannot be its own ancestor")
            
            # Get the parent of the current collection
            result = self.db.execute(
                select(Collection.parent_id).filter(Collection.id == current_id)
            )
            parent_id = result.scalar_one_or_none()
            
            if parent_id is None:
                # Reached the top of the hierarchy
                return True
            
            current_id = parent_id
            depth += 1
        
        if depth >= max_depth:
            raise ValueError("Hierarchy depth limit exceeded (max 10 levels)")
        
        return True

    def add_resources(
        self,
        collection_id: str,
        user_id: str,
        resource_ids: List[str]
    ) -> Collection:
        """
        Add resources to a collection (batch operation).
        
        Algorithm:
        1. Validate resource_ids list (max 100)
        2. Retrieve collection and verify ownership
        3. Validate all resource_ids exist in Resource table
        4. Batch insert CollectionResource associations
        5. Handle duplicate associations gracefully (ignore)
        6. Trigger recompute_embedding after successful insert
        7. Commit and return updated Collection
        
        Args:
            collection_id: UUID of the collection
            user_id: User ID requesting the operation
            resource_ids: List of resource UUIDs to add (max 100)
            
        Returns:
            Updated Collection object with new resources
            
        Raises:
            ValueError: If validation fails, user is not owner, or resources not found
        """
        # Validate resource_ids list
        if not resource_ids:
            raise ValueError("resource_ids list cannot be empty")
        if len(resource_ids) > 100:
            raise ValueError("Cannot add more than 100 resources at once")
        
        # Retrieve collection and verify ownership
        collection = self.get_collection(collection_id, user_id)
        
        if collection.owner_id != user_id:
            raise ValueError("Access denied: only collection owner can add resources")
        
        # Convert collection_id to UUID
        collection_uuid = uuid.UUID(collection_id)
        
        # Convert resource_ids to UUIDs and validate they exist
        resource_uuids = []
        for resource_id in resource_ids:
            try:
                resource_uuid = uuid.UUID(resource_id)
                resource_uuids.append(resource_uuid)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid resource ID format: {resource_id}")
        
        # Validate all resources exist
        result = self.db.execute(
            select(Resource.id).filter(Resource.id.in_(resource_uuids))
        )
        existing_resource_ids = set(result.scalars().all())
        
        missing_resources = set(resource_uuids) - existing_resource_ids
        if missing_resources:
            missing_str = ", ".join(str(r) for r in missing_resources)
            raise ValueError(f"Resources not found: {missing_str}")
        
        # Get existing associations to avoid duplicates
        result = self.db.execute(
            select(CollectionResource.resource_id).filter(
                CollectionResource.collection_id == collection_uuid,
                CollectionResource.resource_id.in_(resource_uuids)
            )
        )
        existing_associations = set(result.scalars().all())
        
        # Filter out resources that are already in the collection
        new_resource_uuids = [r for r in resource_uuids if r not in existing_associations]
        
        # Batch insert new associations
        if new_resource_uuids:
            # Prepare bulk insert data
            associations = [
                {
                    "collection_id": collection_uuid,
                    "resource_id": resource_uuid,
                    "added_at": datetime.now(timezone.utc)
                }
                for resource_uuid in new_resource_uuids
            ]
            
            # Use bulk_insert_mappings for efficient batch insert
            self.db.bulk_insert_mappings(CollectionResource, associations)
            self.db.commit()
            
            # Trigger embedding recomputation
            self.recompute_embedding(collection_id)
        
        # Refresh collection to get updated resources
        self.db.refresh(collection)
        
        return collection

    def remove_resources(
        self,
        collection_id: str,
        user_id: str,
        resource_ids: List[str]
    ) -> Collection:
        """
        Remove resources from a collection (batch operation).
        
        Algorithm:
        1. Validate resource_ids list (max 100)
        2. Retrieve collection and verify ownership
        3. Batch delete CollectionResource associations
        4. Trigger recompute_embedding after successful delete
        5. Commit and return updated Collection
        
        Args:
            collection_id: UUID of the collection
            user_id: User ID requesting the operation
            resource_ids: List of resource UUIDs to remove (max 100)
            
        Returns:
            Updated Collection object with resources removed
            
        Raises:
            ValueError: If validation fails or user is not owner
        """
        # Validate resource_ids list
        if not resource_ids:
            raise ValueError("resource_ids list cannot be empty")
        if len(resource_ids) > 100:
            raise ValueError("Cannot remove more than 100 resources at once")
        
        # Retrieve collection and verify ownership
        collection = self.get_collection(collection_id, user_id)
        
        if collection.owner_id != user_id:
            raise ValueError("Access denied: only collection owner can remove resources")
        
        # Convert collection_id to UUID
        collection_uuid = uuid.UUID(collection_id)
        
        # Convert resource_ids to UUIDs
        resource_uuids = []
        for resource_id in resource_ids:
            try:
                resource_uuid = uuid.UUID(resource_id)
                resource_uuids.append(resource_uuid)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid resource ID format: {resource_id}")
        
        # Batch delete CollectionResource associations
        delete_stmt = delete(CollectionResource).where(
            CollectionResource.collection_id == collection_uuid,
            CollectionResource.resource_id.in_(resource_uuids)
        )
        
        result = self.db.execute(delete_stmt)
        deleted_count = result.rowcount
        
        self.db.commit()
        
        # Trigger embedding recomputation if any resources were removed
        if deleted_count > 0:
            self.recompute_embedding(collection_id)
        
        # Refresh collection to get updated resources
        self.db.refresh(collection)
        
        return collection

    def compute_aggregate_embedding(self, embedding_vectors: List[List[float]]) -> Optional[List[float]]:
        """
        Compute aggregate embedding from a list of embedding vectors.
        
        Algorithm:
        1. Handle edge case: empty list returns None
        2. Stack vectors into numpy matrix (n x d)
        3. Compute column-wise mean
        4. Normalize result to unit length (L2 norm)
        5. Return as list of floats
        
        Edge cases handled:
        - Empty list: returns None
        - Single vector: normalized and returned
        - Zero vector: returns zero vector (no normalization)
        
        Args:
            embedding_vectors: List of embedding vectors (List[List[float]])
            
        Returns:
            Mean vector normalized to unit length, or None if input is empty
        """
        import numpy as np
        
        # Handle empty list
        if not embedding_vectors:
            return None
        
        # Stack vectors into matrix
        try:
            matrix = np.array(embedding_vectors, dtype=np.float64)
        except (ValueError, TypeError):
            return None
        
        # Compute column-wise mean
        mean_vector = np.mean(matrix, axis=0)
        
        # Normalize to unit length (L2 norm)
        norm = np.linalg.norm(mean_vector)
        
        if norm > 1e-10:  # Avoid division by zero
            mean_vector = mean_vector / norm
        # If norm is zero, return the zero vector as-is
        
        return mean_vector.tolist()

    def recompute_embedding(self, collection_id: str) -> Optional[List[float]]:
        """
        Recompute aggregate embedding from member resource embeddings.
        
        Algorithm:
        1. Query all resources in collection that have non-null embeddings
        2. If no embeddings found, set collection.embedding to None and return
        3. Extract embedding vectors into list of lists
        4. Call compute_aggregate_embedding helper function
        5. Store result in collection.embedding field
        6. Commit and return embedding vector
        
        Args:
            collection_id: UUID of the collection
            
        Returns:
            Computed embedding vector, or None if no resources with embeddings
            
        Raises:
            ValueError: If collection not found
        """
        # Convert string collection_id to UUID
        try:
            collection_uuid = uuid.UUID(collection_id)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid collection ID: {collection_id}")
        
        # Retrieve collection
        result = self.db.execute(
            select(Collection).filter(Collection.id == collection_uuid)
        )
        collection = result.scalar_one_or_none()
        
        if not collection:
            raise ValueError(f"Collection not found: {collection_id}")
        
        # Query all resources in collection that have non-null embeddings
        result = self.db.execute(
            select(Resource)
            .join(CollectionResource, CollectionResource.resource_id == Resource.id)
            .filter(
                CollectionResource.collection_id == collection_uuid,
                Resource.embedding.isnot(None)
            )
        )
        resources_with_embeddings = result.scalars().all()
        
        # Extract embedding vectors into list of lists
        embedding_vectors = []
        for resource in resources_with_embeddings:
            if resource.embedding and len(resource.embedding) > 0:
                embedding_vectors.append(resource.embedding)
        
        # If no embeddings found, set collection.embedding to None and return
        if not embedding_vectors:
            collection.embedding = None
            collection.updated_at = datetime.now(timezone.utc)
            self.db.add(collection)
            self.db.commit()
            return None
        
        # Call compute_aggregate_embedding helper function
        aggregate_embedding = self.compute_aggregate_embedding(embedding_vectors)
        
        # Store result in collection.embedding field
        collection.embedding = aggregate_embedding
        collection.updated_at = datetime.now(timezone.utc)
        
        # Commit and return embedding vector
        self.db.add(collection)
        self.db.commit()
        
        return aggregate_embedding

    def get_collection_recommendations(
        self,
        collection_id: str,
        user_id: str,
        limit: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get recommendations based on collection's aggregate embedding.
        
        Algorithm:
        1. Retrieve collection and verify access
        2. If collection.embedding is None, return empty recommendations
        3. Query all resources with embeddings (exclude resources already in collection)
        4. Compute cosine similarity between collection.embedding and each resource.embedding
        5. Sort by similarity DESC, take top N
        6. Query all other collections with embeddings (exclude self)
        7. Compute cosine similarity between collection.embedding and each collection.embedding
        8. Sort by similarity DESC, take top N
        9. Return dict with resource_recommendations and collection_recommendations
        
        Args:
            collection_id: UUID of the collection
            user_id: User ID requesting recommendations
            limit: Maximum number of recommendations per type (1-50)
            
        Returns:
            Dictionary with keys: resource_recommendations, collection_recommendations
            Each value is a list of dicts with: id, title, type, relevance_score
            
        Raises:
            ValueError: If collection not found or access denied
        """
        # Validate limit
        limit = max(1, min(limit, 50))
        
        # Retrieve collection (enforces access control)
        collection = self.get_collection(collection_id, user_id)
        
        # Check if collection has embedding
        if not collection.embedding or len(collection.embedding) == 0:
            return {
                "resource_recommendations": [],
                "collection_recommendations": []
            }
        
        import numpy as np
        from numpy.linalg import norm
        
        collection_embedding = np.array(collection.embedding)
        
        # Get member resource IDs to exclude
        result = self.db.execute(
            select(CollectionResource.resource_id).filter(
                CollectionResource.collection_id == uuid.UUID(collection_id)
            )
        )
        member_resource_ids = set(result.scalars().all())
        
        # Query resources with embeddings (exclude members)
        result = self.db.execute(
            select(Resource).filter(
                Resource.embedding.isnot(None),
                ~Resource.id.in_(member_resource_ids) if member_resource_ids else True
            )
        )
        candidate_resources = result.scalars().all()
        
        # Compute similarities for resources
        resource_similarities = []
        for resource in candidate_resources:
            if resource.embedding and len(resource.embedding) > 0:
                resource_embedding = np.array(resource.embedding)
                
                # Compute cosine similarity
                similarity = np.dot(collection_embedding, resource_embedding) / (
                    norm(collection_embedding) * norm(resource_embedding) + 1e-10
                )
                
                resource_similarities.append({
                    "id": str(resource.id),
                    "title": resource.title,
                    "type": "resource",
                    "relevance_score": float(similarity),
                    "description": resource.description,
                    "quality_score": resource.quality_score
                })
        
        # Sort by similarity and take top N
        resource_similarities.sort(key=lambda x: x["relevance_score"], reverse=True)
        top_resources = resource_similarities[:limit]
        
        # Query other collections with embeddings (exclude self)
        collection_uuid = uuid.UUID(collection_id)
        result = self.db.execute(
            select(Collection).filter(
                Collection.embedding.isnot(None),
                Collection.id != collection_uuid,
                Collection.visibility == "public"  # Only recommend public collections
            )
        )
        candidate_collections = result.scalars().all()
        
        # Compute similarities for collections
        collection_similarities = []
        for other_collection in candidate_collections:
            if other_collection.embedding and len(other_collection.embedding) > 0:
                other_embedding = np.array(other_collection.embedding)
                
                # Compute cosine similarity
                similarity = np.dot(collection_embedding, other_embedding) / (
                    norm(collection_embedding) * norm(other_embedding) + 1e-10
                )
                
                collection_similarities.append({
                    "id": str(other_collection.id),
                    "title": other_collection.name,
                    "type": "collection",
                    "relevance_score": float(similarity),
                    "description": other_collection.description,
                    "quality_score": None
                })
        
        # Sort by similarity and take top N
        collection_similarities.sort(key=lambda x: x["relevance_score"], reverse=True)
        top_collections = collection_similarities[:limit]
        
        return {
            "resource_recommendations": top_resources,
            "collection_recommendations": top_collections
        }

    def cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Compute cosine similarity between two embedding vectors.
        
        Algorithm:
        1. Use numpy to compute dot product
        2. Divide by product of L2 norms
        3. Return similarity score (float between -1 and 1)
        
        Edge cases handled:
        - Zero vectors: returns 0.0
        - Different dimensions: raises ValueError
        - None or empty vectors: raises ValueError
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (float between -1 and 1)
            
        Raises:
            ValueError: If vectors are None, empty, or have different dimensions
        """
        import numpy as np
        
        # Validate inputs
        if not embedding1 or not embedding2:
            raise ValueError("Embedding vectors cannot be None or empty")
        
        if len(embedding1) != len(embedding2):
            raise ValueError(
                f"Embedding dimensions must match: {len(embedding1)} != {len(embedding2)}"
            )
        
        # Convert to numpy arrays
        vec1 = np.array(embedding1, dtype=np.float64)
        vec2 = np.array(embedding2, dtype=np.float64)
        
        # Compute L2 norms
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        # Handle zero vectors
        if norm1 < 1e-10 or norm2 < 1e-10:
            return 0.0
        
        # Compute cosine similarity
        dot_product = np.dot(vec1, vec2)
        similarity = dot_product / (norm1 * norm2)
        
        return float(similarity)

    def find_similar_resources(
        self,
        target_embedding: List[float],
        exclude_resource_ids: List[str],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find resources similar to the target embedding.
        
        Algorithm:
        1. Query all Resources with non-null embeddings
        2. Exclude resources in exclude_resource_ids list
        3. Compute cosine similarity for each resource embedding vs target
        4. Sort by similarity descending
        5. Return top N resources with similarity scores
        
        Args:
            target_embedding: Target embedding vector to compare against
            exclude_resource_ids: List of resource IDs to exclude from results
            limit: Maximum number of results to return (1-50)
            
        Returns:
            List of dictionaries with resource information and similarity scores:
            [{"id": str, "title": str, "similarity": float, ...}]
        """
        # Validate limit
        limit = max(1, min(limit, 50))
        
        # Convert exclude_resource_ids to UUIDs
        exclude_uuids = []
        for resource_id in exclude_resource_ids:
            try:
                exclude_uuids.append(uuid.UUID(resource_id))
            except (ValueError, TypeError):
                # Skip invalid UUIDs
                pass
        
        # Query all resources with non-null embeddings
        query = select(Resource).filter(Resource.embedding.isnot(None))
        
        # Exclude resources in exclude list
        if exclude_uuids:
            query = query.filter(~Resource.id.in_(exclude_uuids))
        
        result = self.db.execute(query)
        candidate_resources = result.scalars().all()
        
        # Compute similarities
        resource_similarities = []
        for resource in candidate_resources:
            if resource.embedding and len(resource.embedding) > 0:
                try:
                    similarity = self.cosine_similarity(target_embedding, resource.embedding)
                    
                    resource_similarities.append({
                        "id": str(resource.id),
                        "title": resource.title,
                        "creator": resource.creator,
                        "quality_score": resource.quality_score,
                        "similarity": similarity,
                        "description": resource.description
                    })
                except ValueError:
                    # Skip resources with incompatible embeddings
                    continue
        
        # Sort by similarity descending
        resource_similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Return top N
        return resource_similarities[:limit]

    def find_similar_collections(
        self,
        target_embedding: List[float],
        user_id: Optional[str],
        exclude_collection_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find collections similar to the target embedding.
        
        Algorithm:
        1. Query all Collections with non-null embeddings
        2. Apply access control filter (owner or public visibility)
        3. Exclude collection with exclude_collection_id
        4. Compute cosine similarity for each collection embedding vs target
        5. Sort by similarity descending
        6. Return top N collections with similarity scores
        
        Args:
            target_embedding: Target embedding vector to compare against
            user_id: User ID for access control (can be None)
            exclude_collection_id: Collection ID to exclude from results
            limit: Maximum number of results to return (1-50)
            
        Returns:
            List of dictionaries with collection information and similarity scores:
            [{"id": str, "name": str, "similarity": float, ...}]
        """
        # Validate limit
        limit = max(1, min(limit, 50))
        
        # Convert exclude_collection_id to UUID
        try:
            exclude_uuid = uuid.UUID(exclude_collection_id)
        except (ValueError, TypeError):
            exclude_uuid = None
        
        # Query all collections with non-null embeddings
        query = select(Collection).filter(Collection.embedding.isnot(None))
        
        # Exclude the source collection
        if exclude_uuid:
            query = query.filter(Collection.id != exclude_uuid)
        
        # Apply access control filter
        if user_id:
            # Include collections where user is owner OR visibility is public
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    Collection.owner_id == user_id,
                    Collection.visibility == "public"
                )
            )
        else:
            # No user_id provided, only show public collections
            query = query.filter(Collection.visibility == "public")
        
        result = self.db.execute(query)
        candidate_collections = result.scalars().all()
        
        # Compute similarities
        collection_similarities = []
        for collection in candidate_collections:
            if collection.embedding and len(collection.embedding) > 0:
                try:
                    similarity = self.cosine_similarity(target_embedding, collection.embedding)
                    
                    collection_similarities.append({
                        "id": str(collection.id),
                        "name": collection.name,
                        "description": collection.description,
                        "owner_id": collection.owner_id,
                        "visibility": collection.visibility,
                        "similarity": similarity
                    })
                except ValueError:
                    # Skip collections with incompatible embeddings
                    continue
        
        # Sort by similarity descending
        collection_similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Return top N
        return collection_similarities[:limit]

    def get_recommendations(
        self,
        collection_id: str,
        user_id: Optional[str],
        limit: int = 10,
        include_resources: bool = True,
        include_collections: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get recommendations for resources and collections similar to this collection.
        
        Algorithm:
        1. Retrieve collection and verify access
        2. Get collection.embedding, raise error if None
        3. Initialize results dictionary with "resources" and "collections" keys
        4. If include_resources, call find_similar_resources
        5. If include_collections, call find_similar_collections
        6. Return results dictionary
        
        Args:
            collection_id: UUID of the collection
            user_id: User ID for access control (can be None)
            limit: Maximum number of recommendations per type (1-50)
            include_resources: Whether to include resource recommendations
            include_collections: Whether to include collection recommendations
            
        Returns:
            Dictionary with keys "resources" and "collections", each containing
            a list of recommendation dictionaries with similarity scores
            
        Raises:
            ValueError: If collection not found, access denied, or no embedding available
        """
        # Validate limit
        limit = max(1, min(limit, 50))
        
        # Retrieve collection and verify access
        collection = self.get_collection(collection_id, user_id)
        
        # Check if collection has embedding
        if not collection.embedding or len(collection.embedding) == 0:
            raise ValueError(
                f"Collection {collection_id} does not have an aggregate embedding. "
                "Add resources with embeddings to generate recommendations."
            )
        
        # Initialize results dictionary
        results = {
            "resources": [],
            "collections": []
        }
        
        # Get member resource IDs to exclude from resource recommendations
        result = self.db.execute(
            select(CollectionResource.resource_id).filter(
                CollectionResource.collection_id == uuid.UUID(collection_id)
            )
        )
        member_resource_ids = [str(rid) for rid in result.scalars().all()]
        
        # If include_resources, call find_similar_resources
        if include_resources:
            results["resources"] = self.find_similar_resources(
                target_embedding=collection.embedding,
                exclude_resource_ids=member_resource_ids,
                limit=limit
            )
        
        # If include_collections, call find_similar_collections
        if include_collections:
            results["collections"] = self.find_similar_collections(
                target_embedding=collection.embedding,
                user_id=user_id,
                exclude_collection_id=collection_id,
                limit=limit
            )
        
        return results

    def get_collection_with_annotations(
        self,
        collection_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get collection details with annotation count.
        
        Algorithm:
        1. Retrieve collection using get_collection (enforces access control)
        2. Count annotations associated with this collection
        3. Return collection data as dict with annotation_count field
        
        Args:
            collection_id: UUID of the collection
            user_id: User ID for access control
            
        Returns:
            Dictionary with collection data and annotation_count field
            
        Raises:
            ValueError: If collection not found or access denied
        """
        # Retrieve collection (enforces access control)
        collection = self.get_collection(collection_id, user_id)
        
        # Count annotations associated with this collection
        try:
            from backend.app.database.models import Annotation
            import json
            
            # Query annotations where collection_ids JSON array contains this collection_id
            # Use portable string matching since JSON operations vary by database
            
            # Count annotations that have this collection_id in their collection_ids JSON array
            annotation_count = self.db.query(Annotation).filter(
                Annotation.user_id == user_id
            ).all()
            
            # Filter in Python to handle JSON array matching portably
            count = 0
            for ann in annotation_count:
                if ann.collection_ids:
                    try:
                        coll_ids = json.loads(ann.collection_ids) if isinstance(ann.collection_ids, str) else ann.collection_ids
                        if isinstance(coll_ids, list) and collection_id in coll_ids:
                            count += 1
                    except (json.JSONDecodeError, TypeError):
                        continue
            
            annotation_count = count
            
        except Exception as e:
            # If annotation counting fails, default to 0
            print(f"Warning: Could not count annotations for collection {collection_id}: {e}")
            annotation_count = 0
        
        # Convert collection to dict
        collection_dict = {
            "id": str(collection.id),
            "name": collection.name,
            "description": collection.description,
            "owner_id": collection.owner_id,
            "visibility": collection.visibility,
            "parent_id": str(collection.parent_id) if collection.parent_id else None,
            "created_at": collection.created_at.isoformat() if collection.created_at else None,
            "updated_at": collection.updated_at.isoformat() if collection.updated_at else None,
            "annotation_count": annotation_count
        }
        
        return collection_dict
