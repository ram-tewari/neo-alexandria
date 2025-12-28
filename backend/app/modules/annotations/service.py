"""
Neo Alexandria 2.0 - Annotation Service (Phase 14)

This module handles annotation management operations for Neo Alexandria 2.0.
It provides CRUD operations, search functionality (full-text and semantic),
export capabilities, and integration with the embedding system.

Related files:
- app/modules/annotations/model.py: Annotation model
- app/modules/annotations/router.py: Annotation API endpoints
- app/modules/annotations/schema.py: Pydantic schemas for API validation
- app/shared/embeddings.py: Embedding generation

Features:
- Annotation CRUD with ownership and access control
- Text offset-based highlighting with context extraction
- Full-text and semantic search across annotations
- Tag-based organization and filtering
- Markdown and JSON export
- Automatic embedding generation for semantic search
"""

from __future__ import annotations

import uuid
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, or_, and_

from .model import Annotation
from ...database.models import Resource
from ...shared.embeddings import EmbeddingGenerator

# Constants
DEFAULT_CONTEXT_LENGTH = 50
DEFAULT_SEARCH_LIMIT = 50
DEFAULT_SEMANTIC_LIMIT = 10
DEFAULT_USER_ANNOTATIONS_LIMIT = 100
DEFAULT_COLOR = "#FFFF00"
MAX_EXPORT_ANNOTATIONS = 1000


class AnnotationService:
    """
    Handles annotation management operations.
    
    This service provides methods for creating, reading, updating, and deleting annotations,
    searching annotations (full-text and semantic), extracting context, generating embeddings,
    and exporting annotations in multiple formats.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the annotation service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.embedding_generator = EmbeddingGenerator()

    def create_annotation(
        self,
        resource_id: str,
        user_id: str,
        start_offset: int,
        end_offset: int,
        highlighted_text: str,
        note: Optional[str] = None,
        tags: Optional[List[str]] = None,
        color: str = DEFAULT_COLOR,
        collection_ids: Optional[List[str]] = None
    ) -> Annotation:
        """
        Create a new annotation with validation and context extraction.
        
        Algorithm:
        1. Validate resource exists and user has access
        2. Validate offsets (start < end, non-negative)
        3. Extract context (50 chars before/after)
        4. Create Annotation record with uuid4() ID
        5. Commit to database
        6. Enqueue embedding generation if note provided
        
        Args:
            resource_id: UUID of the resource being annotated
            user_id: User ID of the annotation owner
            start_offset: Starting character position (0-indexed)
            end_offset: Ending character position (exclusive)
            highlighted_text: The actual text being highlighted
            note: Optional user note/commentary
            tags: Optional list of tags for organization
            color: Hex color code for visual styling (default: yellow)
            collection_ids: Optional list of collection UUIDs
            
        Returns:
            Created Annotation object
            
        Raises:
            ValueError: If validation fails (resource not found, invalid offsets)
        """
        # Validate inputs
        self._validate_offsets(start_offset, end_offset)
        resource_uuid = self._validate_resource_id(resource_id)
        resource = self._fetch_resource(resource_uuid)
        
        # Extract context from resource content
        content = self._get_resource_content(resource)
        context_before = self._extract_context(content, start_offset, before=True)
        context_after = self._extract_context(content, end_offset, before=False)
        
        # Create annotation
        annotation = self._build_annotation(
            resource_uuid=resource_uuid,
            user_id=user_id,
            start_offset=start_offset,
            end_offset=end_offset,
            highlighted_text=highlighted_text,
            note=note,
            tags=tags,
            color=color,
            collection_ids=collection_ids,
            context_before=context_before,
            context_after=context_after
        )
        
        self._save_annotation(annotation)
        
        # Generate embedding if note provided (async in background)
        if note:
            self._generate_annotation_embedding(annotation)
        
        return annotation
    
    def _validate_offsets(self, start_offset: int, end_offset: int) -> None:
        """Validate annotation offsets."""
        if start_offset < 0 or end_offset < 0:
            raise ValueError("Offsets must be non-negative")
        
        if start_offset >= end_offset:
            raise ValueError("start_offset must be less than end_offset")
    
    def _validate_resource_id(self, resource_id: str) -> uuid.UUID:
        """Validate and convert resource ID to UUID."""
        try:
            return uuid.UUID(resource_id)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid resource_id format: {resource_id}")
    
    def _fetch_resource(self, resource_uuid: uuid.UUID) -> Resource:
        """Fetch resource from database."""
        result = self.db.execute(
            select(Resource).filter(Resource.id == resource_uuid)
        )
        resource = result.scalar_one_or_none()
        
        if not resource:
            raise ValueError(f"Resource not found: {resource_uuid}")
        
        return resource
    
    def _build_annotation(
        self,
        resource_uuid: uuid.UUID,
        user_id: str,
        start_offset: int,
        end_offset: int,
        highlighted_text: str,
        note: Optional[str],
        tags: Optional[List[str]],
        color: str,
        collection_ids: Optional[List[str]],
        context_before: str,
        context_after: str
    ) -> Annotation:
        """Build annotation object."""
        return Annotation(
            id=uuid.uuid4(),
            resource_id=resource_uuid,
            user_id=user_id,
            start_offset=start_offset,
            end_offset=end_offset,
            highlighted_text=highlighted_text,
            note=note,
            tags=json.dumps(tags) if tags else None,
            color=color,
            context_before=context_before,
            context_after=context_after,
            is_shared=0,
            collection_ids=json.dumps(collection_ids) if collection_ids else None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    
    def _save_annotation(self, annotation: Annotation) -> None:
        """Save annotation to database."""
        self.db.add(annotation)
        self.db.commit()
        self.db.refresh(annotation)

    def update_annotation(
        self,
        annotation_id: str,
        user_id: str,
        note: Optional[str] = None,
        tags: Optional[List[str]] = None,
        color: Optional[str] = None,
        is_shared: Optional[bool] = None
    ) -> Annotation:
        """
        Update an existing annotation with ownership verification.
        
        Algorithm:
        1. Fetch annotation and verify ownership
        2. Update note, tags, color, is_shared fields
        3. Regenerate embedding if note changed
        4. Update updated_at timestamp
        
        Args:
            annotation_id: UUID of the annotation to update
            user_id: User ID for ownership verification
            note: Optional new note content
            tags: Optional new tags list
            color: Optional new color hex code
            is_shared: Optional new sharing status
            
        Returns:
            Updated Annotation object
            
        Raises:
            ValueError: If annotation not found
            PermissionError: If user doesn't own the annotation
        """
        # Fetch annotation
        try:
            annotation_uuid = uuid.UUID(annotation_id)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid annotation_id format: {annotation_id}")
        
        result = self.db.execute(
            select(Annotation).filter(Annotation.id == annotation_uuid)
        )
        annotation = result.scalar_one_or_none()
        
        if not annotation:
            raise ValueError(f"Annotation not found: {annotation_id}")
        
        # Verify ownership
        if annotation.user_id != user_id:
            raise PermissionError("Cannot update another user's annotation")
        
        # Track if note changed for embedding regeneration
        note_changed = False
        if note is not None and note != annotation.note:
            annotation.note = note
            note_changed = True
        
        # Update fields
        if tags is not None:
            annotation.tags = json.dumps(tags)
        
        if color is not None:
            annotation.color = color
        
        if is_shared is not None:
            annotation.is_shared = 1 if is_shared else 0
        
        # Update timestamp
        annotation.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(annotation)
        
        # Regenerate embedding if note changed
        if note_changed and note:
            self._generate_annotation_embedding(annotation)
        
        return annotation

    def delete_annotation(
        self,
        annotation_id: str,
        user_id: str
    ) -> bool:
        """
        Delete an annotation with ownership verification.
        
        Algorithm:
        1. Fetch annotation and verify ownership
        2. Delete from database
        
        Args:
            annotation_id: UUID of the annotation to delete
            user_id: User ID for ownership verification
            
        Returns:
            True if deletion successful
            
        Raises:
            ValueError: If annotation not found
            PermissionError: If user doesn't own the annotation
        """
        # Fetch annotation
        try:
            annotation_uuid = uuid.UUID(annotation_id)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid annotation_id format: {annotation_id}")
        
        result = self.db.execute(
            select(Annotation).filter(Annotation.id == annotation_uuid)
        )
        annotation = result.scalar_one_or_none()
        
        if not annotation:
            raise ValueError(f"Annotation not found: {annotation_id}")
        
        # Verify ownership
        if annotation.user_id != user_id:
            raise PermissionError("Cannot delete another user's annotation")
        
        # Delete annotation
        self.db.delete(annotation)
        self.db.commit()
        
        return True

    def get_annotation_by_id(
        self,
        annotation_id: str,
        user_id: str
    ) -> Optional[Annotation]:
        """
        Retrieve annotation with access control (owner or shared).
        
        Args:
            annotation_id: UUID of the annotation to retrieve
            user_id: User ID for access control
            
        Returns:
            Annotation object if found and accessible, None otherwise
        """
        # Fetch annotation
        try:
            annotation_uuid = uuid.UUID(annotation_id)
        except (ValueError, TypeError):
            return None
        
        result = self.db.execute(
            select(Annotation).filter(Annotation.id == annotation_uuid)
        )
        annotation = result.scalar_one_or_none()
        
        if not annotation:
            return None
        
        # Access control: owner or shared
        if annotation.user_id != user_id and not annotation.is_shared:
            return None
        
        return annotation

    def get_annotations_for_resource(
        self,
        resource_id: str,
        user_id: str,
        include_shared: bool = False,
        tags: Optional[List[str]] = None
    ) -> List[Annotation]:
        """
        Query annotations by resource_id with filtering options.
        
        Returns annotations ordered by start_offset (document order).
        Filters by user_id (owner) or optionally includes shared annotations.
        Can filter by tags if specified.
        
        Args:
            resource_id: UUID of the resource
            user_id: User ID for ownership filtering
            include_shared: If True, include shared annotations from other users
            tags: Optional list of tags to filter by (matches ANY tag)
            
        Returns:
            List of Annotation objects ordered by start_offset
            
        Requirements: 2.5, 3.1, 3.2, 3.3, 6.1, 6.5
        """
        # Validate resource_id format
        try:
            resource_uuid = uuid.UUID(resource_id)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid resource_id format: {resource_id}")
        
        # Build base query
        query = select(Annotation).filter(Annotation.resource_id == resource_uuid)
        
        # Apply access control filter
        if include_shared:
            # Include annotations owned by user OR shared by others
            query = query.filter(
                or_(
                    Annotation.user_id == user_id,
                    Annotation.is_shared
                )
            )
        else:
            # Only annotations owned by user
            query = query.filter(Annotation.user_id == user_id)
        
        # Apply tag filter if specified
        if tags:
            # Filter annotations that have ANY of the specified tags
            # Tags are stored as JSON array, so we need to check if any tag matches
            tag_conditions = []
            for tag in tags:
                # Use JSON contains check - this works with SQLite JSON functions
                tag_conditions.append(Annotation.tags.contains(f'"{tag}"'))
            
            if tag_conditions:
                query = query.filter(or_(*tag_conditions))
        
        # Order by start_offset (document order)
        query = query.order_by(Annotation.start_offset.asc())
        
        # Execute query
        result = self.db.execute(query)
        annotations = result.scalars().all()
        
        return list(annotations)

    def get_annotations_for_user(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "recent"
    ) -> List[Annotation]:
        """
        Query annotations by user_id across all resources.
        
        Supports pagination and sorting by creation date.
        Eagerly loads resource relationship to prevent N+1 queries.
        
        Args:
            user_id: User ID to retrieve annotations for
            limit: Maximum number of annotations to return (default: 100)
            offset: Number of annotations to skip for pagination (default: 0)
            sort_by: Sort order - "recent" (newest first) or "oldest" (oldest first)
            
        Returns:
            List of Annotation objects with resource relationship loaded
            
        Requirements: 6.2, 6.3, 6.4, 6.5
        """
        # Build base query with eager loading
        query = select(Annotation).options(
            joinedload(Annotation.resource)
        ).filter(Annotation.user_id == user_id)
        
        # Apply sorting
        if sort_by == "oldest":
            query = query.order_by(Annotation.created_at.asc())
        else:  # "recent" is default
            query = query.order_by(Annotation.created_at.desc())
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        # Execute query
        result = self.db.execute(query)
        annotations = result.scalars().all()
        
        return list(annotations)

    def _get_resource_content(self, resource: Resource) -> str:
        """
        Get the full text content of a resource.
        
        Reads from the archived text file if available.
        
        Args:
            resource: Resource object
            
        Returns:
            Full text content of the resource
        """
        if not resource.identifier:
            return ""
        
        try:
            # The identifier contains the archive path
            archive_path = Path(resource.identifier)
            text_path = archive_path / "text.txt"
            
            if text_path.exists():
                return text_path.read_text(encoding="utf-8")
        except Exception:
            # If we can't read the file, return empty string
            pass
        
        return ""
    
    def _extract_context(
        self,
        content: str,
        offset: int,
        before: bool = True,
        context_length: int = 50
    ) -> str:
        """
        Extract context characters before or after an offset.
        
        Handles document boundaries gracefully.
        
        Args:
            content: Full document content
            offset: Character position
            before: If True, extract before offset; if False, extract after
            context_length: Number of characters to extract (default: 50)
            
        Returns:
            Context string (up to context_length characters)
        """
        if not content:
            return ""
        
        if before:
            # Extract context before offset
            start = max(0, offset - context_length)
            return content[start:offset]
        else:
            # Extract context after offset
            end = min(len(content), offset + context_length)
            return content[offset:end]
    
    def search_annotations_fulltext(
        self,
        user_id: str,
        query: str,
        limit: int = 50
    ) -> List[Annotation]:
        """
        Full-text search across annotation notes and highlighted text.
        
        Searches both the note content and highlighted_text fields using
        LIKE queries. Results are filtered to only include annotations
        owned by the requesting user.
        
        Args:
            user_id: User ID to filter annotations by
            query: Search query string
            limit: Maximum number of results to return (default: 50)
            
        Returns:
            List of matching Annotation objects
            
        Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 12.2
        Target: <100ms for 10,000 annotations
        """
        if not query:
            return []
        
        # Build LIKE pattern
        search_pattern = f"%{query}%"
        
        # Build query - search in both note and highlighted_text
        query_stmt = select(Annotation).filter(
            and_(
                Annotation.user_id == user_id,
                or_(
                    Annotation.note.ilike(search_pattern),
                    Annotation.highlighted_text.ilike(search_pattern)
                )
            )
        ).limit(limit)
        
        # Execute query
        result = self.db.execute(query_stmt)
        annotations = result.scalars().all()
        
        return list(annotations)

    def search_annotations_semantic(
        self,
        user_id: str,
        query: str,
        limit: int = 10
    ) -> List[Tuple[Annotation, float]]:
        """
        Semantic search across annotation notes using embeddings.
        
        Algorithm:
        1. Generate embedding for query text
        2. Retrieve all user annotations that have embeddings
        3. Compute cosine similarity between query and each annotation
        4. Sort by similarity descending
        5. Return top N matches with similarity scores
        
        Args:
            user_id: User ID to filter annotations by
            query: Search query string
            limit: Maximum number of results to return (default: 10)
            
        Returns:
            List of tuples (Annotation, similarity_score) sorted by score descending
            
        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
        """
        if not query:
            return []
        
        # Generate embedding for query
        try:
            query_embedding = self.embedding_generator.generate_embedding(query)
            if not query_embedding:
                return []
        except Exception:
            return []
        
        # Retrieve user annotations with embeddings
        query_stmt = select(Annotation).filter(
            and_(
                Annotation.user_id == user_id,
                Annotation.embedding.isnot(None)
            )
        )
        
        result = self.db.execute(query_stmt)
        annotations = result.scalars().all()
        
        if not annotations:
            return []
        
        # Compute cosine similarity for each annotation
        results = []
        for annotation in annotations:
            if annotation.embedding:
                similarity = self._cosine_similarity(query_embedding, annotation.embedding)
                results.append((annotation, similarity))
        
        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N matches
        return results[:limit]

    def search_annotations_by_tags(
        self,
        user_id: str,
        tags: List[str],
        match_all: bool = False
    ) -> List[Annotation]:
        """
        Search annotations by tag membership.
        
        Supports matching ANY tag (default) or ALL tags.
        Uses JSON contains operations to query the tags field.
        
        Args:
            user_id: User ID to filter annotations by
            tags: List of tags to search for
            match_all: If True, annotation must have ALL tags; if False, ANY tag matches
            
        Returns:
            List of matching Annotation objects
            
        Requirements: 3.1, 3.2, 3.3
        """
        if not tags:
            return []
        
        # Build base query
        query_stmt = select(Annotation).filter(Annotation.user_id == user_id)
        
        if match_all:
            # Annotation must contain ALL specified tags
            for tag in tags:
                query_stmt = query_stmt.filter(Annotation.tags.contains(f'"{tag}"'))
        else:
            # Annotation must contain ANY of the specified tags
            tag_conditions = []
            for tag in tags:
                tag_conditions.append(Annotation.tags.contains(f'"{tag}"'))
            
            if tag_conditions:
                query_stmt = query_stmt.filter(or_(*tag_conditions))
        
        # Execute query
        result = self.db.execute(query_stmt)
        annotations = result.scalars().all()
        
        return list(annotations)

    def _generate_annotation_embedding(self, annotation: Annotation) -> None:
        """
        Generate and store embedding for annotation note.
        
        This method generates a semantic embedding from the annotation's note
        and updates the annotation record. In production, this should be
        run as a background task.
        
        Args:
            annotation: Annotation object to generate embedding for
        """
        if not annotation.note:
            return
        
        try:
            # Generate embedding
            embedding = self.embedding_generator.generate_embedding(annotation.note)
            
            if embedding:
                # Update annotation with embedding
                annotation.embedding = embedding
                self.db.commit()
        except Exception:
            # Silently fail - embedding generation is not critical
            # In production, this should be logged
            pass

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Compute cosine similarity between two vectors.
        
        Uses numpy for efficient computation.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
            
        Requirements: 5.2, 5.3
        """
        try:
            import numpy as np
            
            # Convert to numpy arrays
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Compute cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            similarity = dot_product / (norm_a * norm_b)
            
            # Ensure result is in [0, 1] range (handle floating point errors)
            return max(0.0, min(1.0, float(similarity)))
        except Exception:
            return 0.0

    def export_annotations_markdown(
        self,
        user_id: str,
        resource_id: Optional[str] = None
    ) -> str:
        """
        Export annotations to Markdown format.
        
        Algorithm:
        1. Retrieve annotations (filtered by resource if specified)
        2. Group by resource_id
        3. For each resource:
           - Add resource title header
           - For each annotation:
             - Format as blockquote (highlighted text)
             - Add note, tags, timestamp
             - Add separator
        4. Concatenate all sections
        
        Args:
            user_id: User ID to export annotations for
            resource_id: Optional resource UUID to filter by (exports all if None)
            
        Returns:
            Markdown-formatted string with all annotations
            
        Requirements: 7.1, 7.2, 7.3, 7.5, 12.3
        Target: <2s for 1,000 annotations
        """
        # Build query with eager loading of resource relationship
        query_stmt = select(Annotation).options(
            joinedload(Annotation.resource)
        ).filter(Annotation.user_id == user_id)
        
        # Filter by resource if specified
        if resource_id:
            try:
                resource_uuid = uuid.UUID(resource_id)
                query_stmt = query_stmt.filter(Annotation.resource_id == resource_uuid)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid resource_id format: {resource_id}")
        
        # Order by resource and then by offset within resource
        query_stmt = query_stmt.order_by(
            Annotation.resource_id.asc(),
            Annotation.start_offset.asc()
        )
        
        # Execute query
        result = self.db.execute(query_stmt)
        annotations = result.scalars().all()
        
        if not annotations:
            return "# Annotations Export\n\nNo annotations found.\n"
        
        # Group annotations by resource
        from itertools import groupby
        
        markdown_parts = ["# Annotations Export\n\n"]
        
        # Group by resource_id
        for resource_id_key, resource_annotations in groupby(
            annotations, 
            key=lambda a: a.resource_id
        ):
            resource_annotations_list = list(resource_annotations)
            
            # Get resource title from first annotation's relationship
            resource_title = "Unknown Resource"
            if resource_annotations_list and resource_annotations_list[0].resource:
                resource_title = resource_annotations_list[0].resource.title or "Untitled Resource"
            
            # Add resource header
            markdown_parts.append(f"## {resource_title}\n\n")
            
            # Format each annotation
            for annotation in resource_annotations_list:
                # Highlighted text as blockquote
                markdown_parts.append(f"> {annotation.highlighted_text}\n\n")
                
                # Note (if present)
                if annotation.note:
                    markdown_parts.append(f"**Note:** {annotation.note}\n\n")
                
                # Tags (if present)
                if annotation.tags:
                    try:
                        tags_list = json.loads(annotation.tags)
                        if tags_list:
                            tags_str = ", ".join(f"`{tag}`" for tag in tags_list)
                            markdown_parts.append(f"**Tags:** {tags_str}\n\n")
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                # Color (if not default)
                if annotation.color and annotation.color != "#FFFF00":
                    markdown_parts.append(f"**Color:** {annotation.color}\n\n")
                
                # Timestamp
                created_str = annotation.created_at.strftime("%Y-%m-%d %H:%M:%S")
                markdown_parts.append(f"*Created: {created_str}*\n\n")
                
                # Separator
                markdown_parts.append("---\n\n")
            
            # Add spacing between resources
            markdown_parts.append("\n")
        
        # Concatenate all parts efficiently
        return "".join(markdown_parts)

    def export_annotations_json(
        self,
        user_id: str,
        resource_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Export annotations to JSON format with complete metadata.
        
        Algorithm:
        1. Retrieve annotations with resource metadata
        2. Convert to JSON-serializable dicts
        
        Args:
            user_id: User ID to export annotations for
            resource_id: Optional resource UUID to filter by (exports all if None)
            
        Returns:
            List of annotation dictionaries with complete metadata
            
        Requirements: 7.3, 7.4
        """
        # Build query with eager loading of resource relationship
        query_stmt = select(Annotation).options(
            joinedload(Annotation.resource)
        ).filter(Annotation.user_id == user_id)
        
        # Filter by resource if specified
        if resource_id:
            try:
                resource_uuid = uuid.UUID(resource_id)
                query_stmt = query_stmt.filter(Annotation.resource_id == resource_uuid)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid resource_id format: {resource_id}")
        
        # Order by created_at descending (most recent first)
        query_stmt = query_stmt.order_by(Annotation.created_at.desc())
        
        # Execute query
        result = self.db.execute(query_stmt)
        annotations = result.scalars().all()
        
        # Convert to JSON-serializable dicts
        json_annotations = []
        for annotation in annotations:
            annotation_dict = {
                "id": str(annotation.id),
                "resource_id": str(annotation.resource_id),
                "user_id": annotation.user_id,
                "start_offset": annotation.start_offset,
                "end_offset": annotation.end_offset,
                "highlighted_text": annotation.highlighted_text,
                "note": annotation.note,
                "tags": json.loads(annotation.tags) if annotation.tags else [],
                "color": annotation.color,
                "context_before": annotation.context_before,
                "context_after": annotation.context_after,
                "is_shared": annotation.is_shared,
                "collection_ids": json.loads(annotation.collection_ids) if annotation.collection_ids else [],
                "created_at": annotation.created_at.isoformat(),
                "updated_at": annotation.updated_at.isoformat(),
                "resource": {
                    "id": str(annotation.resource.id) if annotation.resource else None,
                    "title": annotation.resource.title if annotation.resource else None,
                    "type": annotation.resource.type if annotation.resource else None,
                } if annotation.resource else None
            }
            json_annotations.append(annotation_dict)
        
        return json_annotations

