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
- Batch review operations (approve/reject/flag)
- Batch tagging
- Curator assignment
- Review tracking
"""

from __future__ import annotations

from pathlib import Path
import uuid
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timezone
import time

from sqlalchemy import asc
from sqlalchemy.orm import Session

from ...config.settings import Settings
from ...database.models import Resource, CurationReview
from ...shared.event_bus import EventBus
from ..quality.service import ContentQualityAnalyzer
from .schema import ReviewQueueParams, BatchUpdateResult, EnhancedReviewQueueParams


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
        self.event_bus = EventBus()
        # Don't call _ensure_tables() - tables should already exist
        # In production, tables are created by Alembic migrations
        # In tests, tables are created by test fixtures

    def _ensure_tables(self):
        """Ensure database tables exist."""
        from ...database.base import Base

        try:
            Base.metadata.create_all(bind=self.db.get_bind())
        except Exception:
            pass

    def batch_review(
        self,
        resource_ids: List[uuid.UUID],
        action: str,
        curator_id: str,
        comment: Optional[str] = None,
    ) -> BatchUpdateResult:
        """
        Perform batch review operations on multiple resources.

        Args:
            resource_ids: List of resource UUIDs to review
            action: Review action (approve, reject, flag)
            curator_id: ID of curator performing review
            comment: Optional comment for review

        Returns:
            BatchUpdateResult with updated count and failed IDs
        """
        start_time = time.time()
        failed: List[uuid.UUID] = []
        updated_count = 0

        # Validate action
        if action not in ["approve", "reject", "flag"]:
            raise ValueError(f"Invalid action: {action}")

        # Map action to curation status
        status_map = {"approve": "approved", "reject": "rejected", "flag": "flagged"}
        new_status = status_map[action]

        # Process each resource
        for rid in resource_ids:
            try:
                resource = self.db.query(Resource).filter(Resource.id == rid).first()
                if not resource:
                    failed.append(rid)
                    continue

                # Update resource status
                resource.curation_status = new_status
                resource.updated_at = datetime.now(timezone.utc)

                # Create review record
                review = CurationReview(
                    resource_id=rid,
                    curator_id=curator_id,
                    action=action,
                    comment=comment,
                    timestamp=datetime.now(timezone.utc),
                )
                self.db.add(review)
                self.db.add(resource)

                # Emit curation.reviewed event
                from .handlers import emit_curation_reviewed

                emit_curation_reviewed(
                    review_id=str(review.id)
                    if hasattr(review, "id")
                    else str(uuid.uuid4()),
                    resource_id=str(rid),
                    reviewer_id=curator_id,
                    status=new_status,
                    quality_rating=resource.quality_score,
                )

                # Emit curation.approved event if approved
                if action == "approve":
                    from .handlers import emit_curation_approved

                    emit_curation_approved(
                        review_id=str(review.id)
                        if hasattr(review, "id")
                        else str(uuid.uuid4()),
                        resource_id=str(rid),
                        reviewer_id=curator_id,
                        approval_notes=comment,
                    )

                updated_count += 1

            except Exception:
                failed.append(rid)
                continue

        # Commit transaction
        self.db.commit()

        # Emit event
        elapsed_time = time.time() - start_time
        self.event_bus.emit(
            "curation.batch_reviewed",
            {
                "resource_ids": [str(rid) for rid in resource_ids],
                "action": action,
                "curator_id": curator_id,
                "updated_count": updated_count,
                "failed_count": len(failed),
                "elapsed_time_seconds": elapsed_time,
            },
        )

        return BatchUpdateResult(updated_count=updated_count, failed_ids=failed)

    def batch_tag(
        self, resource_ids: List[uuid.UUID], tags: List[str]
    ) -> BatchUpdateResult:
        """
        Add tags to multiple resources in batch.

        Args:
            resource_ids: List of resource UUIDs
            tags: List of tags to add

        Returns:
            BatchUpdateResult with updated count and failed IDs
        """
        failed: List[uuid.UUID] = []
        updated_count = 0

        # Deduplicate and normalize tags
        normalized_tags = list(set(tag.strip().lower() for tag in tags if tag.strip()))

        for rid in resource_ids:
            try:
                resource = self.db.query(Resource).filter(Resource.id == rid).first()
                if not resource:
                    failed.append(rid)
                    continue

                # Get existing subjects (tags)
                existing_subjects = resource.subject or []

                # Merge with new tags, avoiding duplicates
                updated_subjects = list(set(existing_subjects + normalized_tags))

                # Update resource
                resource.subject = updated_subjects
                resource.updated_at = datetime.now(timezone.utc)
                self.db.add(resource)

                updated_count += 1

            except Exception:
                failed.append(rid)
                continue

        # Commit transaction
        self.db.commit()

        return BatchUpdateResult(updated_count=updated_count, failed_ids=failed)

    def assign_curator(
        self, resource_ids: List[uuid.UUID], curator_id: str
    ) -> BatchUpdateResult:
        """
        Assign resources to a curator for review.

        Args:
            resource_ids: List of resource UUIDs
            curator_id: ID of curator to assign

        Returns:
            BatchUpdateResult with updated count and failed IDs
        """
        failed: List[uuid.UUID] = []
        updated_count = 0

        for rid in resource_ids:
            try:
                resource = self.db.query(Resource).filter(Resource.id == rid).first()
                if not resource:
                    failed.append(rid)
                    continue

                # Assign curator and update status
                resource.assigned_curator = curator_id
                resource.curation_status = "assigned"
                resource.updated_at = datetime.now(timezone.utc)
                self.db.add(resource)

                updated_count += 1

            except Exception:
                failed.append(rid)
                continue

        # Commit transaction
        self.db.commit()

        return BatchUpdateResult(updated_count=updated_count, failed_ids=failed)

    def review_queue_enhanced(
        self, params: EnhancedReviewQueueParams
    ) -> Tuple[List[Resource], int]:
        """
        Get items in the review queue with enhanced filtering.

        Args:
            params: Enhanced review queue parameters

        Returns:
            Tuple of (items, total_count)
        """
        # Start with base query
        query = self.db.query(Resource)

        # Apply quality threshold filter
        if params.threshold is not None:
            query = query.filter(Resource.quality_score < float(params.threshold))

        # Apply quality range filters
        if params.min_quality is not None:
            query = query.filter(Resource.quality_score >= float(params.min_quality))
        if params.max_quality is not None:
            query = query.filter(Resource.quality_score <= float(params.max_quality))

        # Apply curation status filter
        if params.status:
            query = query.filter(Resource.curation_status == params.status)

        # Apply curator assignment filter
        if params.assigned_curator:
            query = query.filter(Resource.assigned_curator == params.assigned_curator)

        # Apply unread filter
        if params.include_unread_only:
            query = query.filter(Resource.read_status == "unread")

        # Get total count
        total = query.count()

        # Apply ordering (low quality first for priority)
        query = query.order_by(asc(Resource.quality_score), asc(Resource.updated_at))

        # Apply pagination
        items = query.offset(params.offset).limit(params.limit).all()

        return items, total

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

        query = self.db.query(Resource).filter(
            Resource.quality_score < float(threshold)
        )

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
            suggestions.append(
                "Add a clear, descriptive summary and at least 3 relevant subjects."
            )

        # Readability suggestions
        read = analysis.get("readability", {})
        reading_ease = float(read.get("reading_ease", 0.0))
        avg_wps = float(read.get("avg_words_per_sentence", 0.0))
        if reading_ease < 50:
            suggestions.append(
                "Improve readability: shorten sentences, use simpler words, add headings."
            )
        elif reading_ease < 70:
            suggestions.append(
                "Slightly improve readability: vary sentence length and clarify structure."
            )
        if avg_wps > 25:
            suggestions.append(
                "Break up long sentences to reduce average words per sentence below ~20."
            )

        # Depth suggestions
        depth = float(analysis.get("content_depth", 0.0))
        if depth < 0.4:
            suggestions.append(
                "Increase content depth: expand sections, add examples, and references."
            )
        elif depth < 0.7:
            suggestions.append(
                "Enrich content with more detail and domain-specific terminology."
            )

        # Source credibility
        cred = float(analysis.get("source_credibility", 0.0))
        if cred < 0.5:
            suggestions.append(
                "Use a more credible source URL (prefer https, .edu/.gov/.org domains)."
            )

        # Overall
        overall = float(analysis.get("overall_quality", 0.0))
        if overall < 0.5:
            suggestions.append(
                "This item is low quality; prioritize for curation and fact-checking."
            )
        elif overall < 0.8:
            suggestions.append(
                "This item is medium quality; targeted edits can raise it to high quality."
            )

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
        self, resource_ids: List[uuid.UUID], updates: Dict[str, Any]
    ) -> BatchUpdateResult:
        """
        Apply batch updates to multiple resources.

        Args:
            resource_ids: List of resource UUIDs
            updates: Dictionary with fields to update

        Returns:
            BatchUpdateResult with updated count and failed IDs

        Raises:
            ValueError: If no updates provided
        """
        if not updates:
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
                updates.pop(key, None)

            for key, value in updates.items():
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
