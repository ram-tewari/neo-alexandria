"""
Neo Alexandria 2.0 - Curation and Quality Control Service

This module provides curation and quality control functionality for Neo Alexandria 2.0.
It handles content review workflows, batch operations, and quality-based filtering
to help maintain high-quality content in the knowledge base.

Related files:
- app/routers/curation.py: API endpoints for curation operations
- app/schemas/query.py: Schemas for batch operations and filtering
- app/services/quality_service.py: Quality scoring and assessment
- app/services/resource_service.py: Resource management operations

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
from typing import List, Tuple, Dict, Any
from datetime import datetime, timezone

from sqlalchemy import asc
from sqlalchemy.orm import Session

from backend.app.config.settings import Settings
from backend.app.database.models import Resource
from backend.app.schemas.query import ReviewQueueParams, BatchUpdateResult
from backend.app.schemas.resource import ResourceUpdate
from backend.app.services.quality_service import ContentQualityAnalyzer


class CurationInterface:
    @staticmethod
    def review_queue(db: Session, params: ReviewQueueParams, settings: Settings) -> Tuple[List[Resource], int]:
        # Ensure tables exist
        from backend.app.database.base import Base
        try:
            Base.metadata.create_all(bind=db.get_bind())
        except Exception:
            pass
        
        threshold = params.threshold if params.threshold is not None else settings.MIN_QUALITY_THRESHOLD

        query = db.query(Resource).filter(Resource.quality_score < float(threshold))
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

    @staticmethod
    def _read_resource_text(resource: Resource) -> str:
        """Best-effort load of the archived text for a resource."""
        try:
            if resource and resource.identifier:
                text_path = Path(str(resource.identifier)) / "text.txt"
                if text_path.exists():
                    return text_path.read_text(encoding="utf-8")
        except Exception:
            pass
        return ""

    @staticmethod
    def quality_analysis(db: Session, resource_id: uuid.UUID) -> Dict[str, Any]:
        # Ensure tables exist
        from backend.app.database.base import Base
        try:
            Base.metadata.create_all(bind=db.get_bind())
        except Exception:
            pass

        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            raise ValueError("Resource not found")

        analyzer = ContentQualityAnalyzer()
        content = CurationInterface._read_resource_text(resource)

        meta_score = analyzer.metadata_completeness(resource)
        readability = analyzer.text_readability(content)
        credibility = analyzer.source_credibility(getattr(resource, "source", None) or getattr(resource, "identifier", None))
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

    @staticmethod
    def improvement_suggestions(db: Session, resource_id: uuid.UUID) -> List[str]:
        analysis = CurationInterface.quality_analysis(db, resource_id)
        suggestions: List[str] = []

        # Metadata suggestions based on completeness and missing fields
        # We only have the score here, so provide generic guidance.
        meta_score = analysis.get("metadata_completeness", 0.0)
        if meta_score < 1.0:
            suggestions.append("Complete missing metadata: title, description, subjects, creator, language, type, identifier.")
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

    @staticmethod
    def bulk_quality_check(db: Session, resource_ids: List[uuid.UUID]) -> BatchUpdateResult:
        # Ensure tables exist
        from backend.app.database.base import Base
        try:
            Base.metadata.create_all(bind=db.get_bind())
        except Exception:
            pass

        analyzer = ContentQualityAnalyzer()
        failed: List[uuid.UUID] = []
        updated_count = 0

        for rid in resource_ids:
            resource = db.query(Resource).filter(Resource.id == rid).first()
            if not resource:
                failed.append(rid)
                continue
            content = CurationInterface._read_resource_text(resource)
            new_score = analyzer.overall_quality(resource, content)
            resource.quality_score = float(new_score)
            resource.updated_at = datetime.now(timezone.utc)
            db.add(resource)
            updated_count += 1

        db.commit()
        return BatchUpdateResult(updated_count=updated_count, failed_ids=failed)

    @staticmethod
    def batch_update(db: Session, resource_ids: List[uuid.UUID], updates: ResourceUpdate) -> BatchUpdateResult:
        # Ensure tables exist
        from backend.app.database.base import Base
        try:
            Base.metadata.create_all(bind=db.get_bind())
        except Exception:
            pass
        
        payload = updates.model_dump(exclude_unset=True)
        if not payload:
            raise ValueError("No updates provided")

        failed: List[uuid.UUID] = []
        updated_count = 0

        # Single transaction
        for rid in resource_ids:
            resource = db.query(Resource).filter(Resource.id == rid).first()
            if not resource:
                failed.append(rid)
                continue

            # Protect immutable fields
            for key in ["id", "created_at", "updated_at"]:
                payload.pop(key, None)

            for key, value in payload.items():
                setattr(resource, key, value)

            resource.updated_at = datetime.now(timezone.utc)
            db.add(resource)
            updated_count += 1

        db.commit()
        return BatchUpdateResult(updated_count=updated_count, failed_ids=failed)

    @staticmethod
    def find_duplicates(db: Session) -> List[tuple[uuid.UUID, uuid.UUID]]:
        # Placeholder for future duplication detection (Phase 3+)
        return []


