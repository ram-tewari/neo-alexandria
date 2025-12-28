"""
Neo Alexandria 2.0 - Curation and Quality Control Service

This module provides curation and quality control functionality for Neo Alexandria 2.0.
It handles content review workflows, batch operations, and quality-based filtering
to help maintain high-quality content in the knowledge base.

Related files:
- app/modules/curation/router.py: API endpoints for curation operations
- app/modules/curation/schema.py: Schemas for batch operations and filtering
- app/services/quality_service.py: Quality scoring and assessment
- app/shared/database.py: Database session management

Features:
- Review queue management for low-quality content
- Batch update operations for multiple resources
- Quality-based filtering and sorting
- Content archiving and organization
- Workflow management for content curation
"""

from __future__ import annotations

from pathlib import Path
import uuid
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timezone

from sqlalchemy import asc
from sqlalchemy.orm import Session

from ...config.settings import Settings
from ...database.models import Resource
from ...schemas.resource import ResourceUpdate
from ...services.quality_service import ContentQualityAnalyzer
from .schema import ReviewQueueParams, BatchUpdateResult


class CurationService:
    """Service for content curation and quality control operations."""
    
    def __init__(self, db: Session, settings: Optional[Settings] = None):
        """
        Initialize CurationService.
        
        Args:
            db: Database session
            settings: Application settings (optional)
        """
        self.db = db
        self.settings = settings
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure database tables exist."""
        from ...database.base import Base
        try:
            Base.metadata.create_all(bind=self.db.get_bind())
        except Exception:
            pass
    
    def review_queue(self, params: ReviewQueueParams) -> Tuple[List[Resource], int]:
        """
        Get items in the review queue based on quality threshold.
        
        Args:
            params: Review queue parameters
            
        Returns:
            Tuple of (items, total_count)
        """
        threshold = params.threshold
        if threshold is None and self.settings:
            threshold = self.settings.MIN_QUALITY_THRESHOLD
        if threshold is None:
            threshold = 0.5  # Default fallback

        query = self.db.query(Resource).filter(Resource.quality_score < float(threshold))
        
        if params.include_unread_only:
            query = query.filter(Resource.read_status == "unread")

        total = query.count()
        items = (
            query.order_by(asc(Resource.quality_score), asc(Resource.updated_at))
            .offset(params.offset)
            .limit(params.limit)
            .all()
        )
        return items, total

    def _read_resource_text(self, resource: Resource) -> str:
        """
        Best-effort load of the archived text for a resource.
        
        Args:
            resource: Resource to read text from
            
        Returns:
            Resource text content or empty string
        """
        try:
            if resource and resource.identifier:
                text_path = Path(str(resource.identifier)) / "text.txt"
                if text_path.exists():
                    return text_path.read_text(encoding="utf-8")
        except Exception:
            pass
        return ""

    def quality_analysis(self, resource_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get detailed quality analysis for a resource.
        
        Args:
            resource_id: Resource UUID
            
        Returns:
            Dictionary with quality metrics
            
        Raises:
            ValueError: If resource not found
        """
        resource = self.db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            raise ValueError("Resource not found")

        analyzer = ContentQualityAnalyzer()
        content = self._read_resource_text(resource)

        meta_score = analyzer.metadata_completeness(resource)
        readability = analyzer.text_readability(content)
        credibility = analyzer.source_credibility(
            getattr(resource, "source", None) or getattr(resource, "identifier", None)
        )
        depth = analyzer.content_depth(content)
        overall = analyzer.overall_quality(resource, content)
        level = analyzer.quality_level(overall)

        return {
            "resource_id": str(resource.id),
            "metadata_completeness": float(meta_score),
            "readability": readability,
            "source_credibility": float(credibility),
            "content_depth": float(depth),
            "overall_quality": float(overall),
            "quality_level": level,
        }

    def improvement_suggestions(self, resource_id: uuid.UUID) -> List[str]:
        """
        Generate improvement suggestions for a resource.
        
        Args:
            resource_id: Resource UUID
            
        Returns:
            List of improvement suggestions
        """
        analysis = self.quality_analysis(resource_id)
        suggestions: List[str] = []

        # Metadata suggestions based on completeness and missing fields
        meta_score = analysis.get("metadata_completeness", 0.0)
        if meta_score < 1.0:
            suggestions.append(
                "Complete missing metadata: title, description, subjects, creator, language, type, identifier."
            )
        if meta_score < 0.5:
            suggestions.append("Add a clear, descriptive summary and at least 3 relevant subjects.")

        # Readability suggestions
        read = analysis.get("readability", {})
        reading_ease = float(read.get("reading_ease", 0.0))
        avg_wps = float(read.get("avg_words_per_sentence", 0.0))
        if reading_ease < 50:
            suggestions.append("Improve readability: shorten sentences, use simpler words, add headings.")
        elif reading_ease < 70:
            suggestions.append("Slightly improve readability: vary sentence length and clarify structure.")
        if avg_wps > 25:
            suggestions.append("Break up long sentences to reduce average words per sentence below ~20.")

        # Depth suggestions
        depth = float(analysis.get("content_depth", 0.0))
        if depth < 0.4:
            suggestions.append("Increase content depth: expand sections, add examples, and references.")
        elif depth < 0.7:
            suggestions.append("Enrich content with more detail and domain-specific terminology.")

        # Source credibility
        cred = float(analysis.get("source_credibility", 0.0))
        if cred < 0.5:
            suggestions.append("Use a more credible source URL (prefer https, .edu/.gov/.org domains).")

        # Overall
        overall = float(analysis.get("overall_quality", 0.0))
        if overall < 0.5:
            suggestions.append("This item is low quality; prioritize for curation and fact-checking.")
        elif overall < 0.8:
            suggestions.append("This item is medium quality; targeted edits can raise it to high quality.")

        return suggestions

    def bulk_quality_check(self, resource_ids: List[uuid.UUID]) -> BatchUpdateResult:
        """
        Perform bulk quality check on multiple resources.
        
        Args:
            resource_ids: List of resource UUIDs
            
        Returns:
            BatchUpdateResult with updated count and failed IDs
        """
        analyzer = ContentQualityAnalyzer()
        failed: List[uuid.UUID] = []
        updated_count = 0

        for rid in resource_ids:
            resource = self.db.query(Resource).filter(Resource.id == rid).first()
            if not resource:
                failed.append(rid)
                continue
            
            content = self._read_resource_text(resource)
            new_score = analyzer.overall_quality(resource, content)
            resource.quality_score = float(new_score)
            resource.updated_at = datetime.now(timezone.utc)
            self.db.add(resource)
            updated_count += 1

        self.db.commit()
        return BatchUpdateResult(updated_count=updated_count, failed_ids=failed)

    def batch_update(
        self, 
        resource_ids: List[uuid.UUID], 
        updates: ResourceUpdate
    ) -> BatchUpdateResult:
        """
        Apply batch updates to multiple resources.
        
        Args:
            resource_ids: List of resource UUIDs
            updates: ResourceUpdate with fields to update
            
        Returns:
            BatchUpdateResult with updated count and failed IDs
            
        Raises:
            ValueError: If no updates provided
        """
        payload = updates.model_dump(exclude_unset=True)
        if not payload:
            raise ValueError("No updates provided")

        failed: List[uuid.UUID] = []
        updated_count = 0

        # Single transaction
        for rid in resource_ids:
            resource = self.db.query(Resource).filter(Resource.id == rid).first()
            if not resource:
                failed.append(rid)
                continue

            # Protect immutable fields
            for key in ["id", "created_at", "updated_at"]:
                payload.pop(key, None)

            for key, value in payload.items():
                setattr(resource, key, value)

            resource.updated_at = datetime.now(timezone.utc)
            self.db.add(resource)
            updated_count += 1

        self.db.commit()
        return BatchUpdateResult(updated_count=updated_count, failed_ids=failed)

    def find_duplicates(self) -> List[tuple[uuid.UUID, uuid.UUID]]:
        """
        Find duplicate resources (placeholder for future implementation).
        
        Returns:
            List of duplicate resource ID pairs
        """
        # Placeholder for future duplication detection (Phase 3+)
        return []
