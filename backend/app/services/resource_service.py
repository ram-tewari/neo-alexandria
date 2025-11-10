from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, or_, asc, desc, String, cast, select

from backend.app.database import models as db_models
from backend.app.database.base import Base, SessionLocal
from backend.app.utils import content_extractor as ce
from backend.app.utils.text_processor import clean_text, readability_scores
from backend.app.services.dependencies import (
    get_ai_core,
    get_classification_service,
    get_quality_analyzer,
    get_authority_control,
)
from backend.app.schemas.query import PageParams, SortParams, ResourceFilters
from backend.app.schemas.resource import ResourceUpdate
from backend.app.services.ai_core import AICore
from backend.app.monitoring import (
    track_ingestion_success,
    track_ingestion_failure,
    increment_active_ingestions,
    decrement_active_ingestions,
)


ARCHIVE_ROOT = Path("storage/archive")


def create_pending_resource(db: Session, payload: Dict[str, Any]) -> db_models.Resource:
    """Create a pending resource row and return it. Idempotent on URL/source."""
    try:
        Base.metadata.create_all(bind=db.get_bind())
    except Exception:
        pass

    url = payload.get("url")
    if not url:
        raise ValueError("url is required")

    # Idempotency: reuse existing resource for same source URL if pending or completed
    result = db.execute(
        select(db_models.Resource)
        .filter(db_models.Resource.source == url)
        .order_by(db_models.Resource.created_at.desc())
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    now = datetime.now(timezone.utc)
    authority = get_authority_control(db)

    resource = db_models.Resource(
        title=payload.get("title") or "Untitled",
        description=payload.get("description"),
        creator=authority.normalize_creator(payload.get("creator")) if payload.get("creator") else None,
        publisher=authority.normalize_publisher(payload.get("publisher")) if payload.get("publisher") else None,
        contributor=payload.get("contributor"),
        date_created=payload.get("date_created"),
        date_modified=payload.get("date_modified") or now,
        type=payload.get("type"),
        format=payload.get("format"),
        identifier=None,
        source=payload.get("source") or url,
        language=payload.get("language"),
        coverage=payload.get("coverage"),
        rights=payload.get("rights"),
        subject=payload.get("subject") or [],
        relation=payload.get("relation") or [],
        classification_code=None,
        read_status=payload.get("read_status") or "unread",
        quality_score=0.0,
        ingestion_status="pending",
        ingestion_error=None,
        ingestion_started_at=None,
        ingestion_completed_at=None,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


def process_ingestion(
    resource_id: str,
    archive_root: Path | str | None = None,
    ai: Optional[AICore] = None,
    engine_url: Optional[str] = None,
) -> None:
    """Background ingestion job. Opens its own DB session.

    Steps: fetch, extract, AI summarize/tag, authority normalize, classify, quality, archive, persist.
    """
    session: Optional[Session] = None
    local_session_factory = None
    increment_active_ingestions()
    try:
        if engine_url:
            engine = create_engine(engine_url, echo=False)
            local_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            session = local_session_factory()
        else:
            session = SessionLocal()
        try:
            Base.metadata.create_all(bind=session.get_bind())
        except Exception:
            pass

        # Convert string resource_id back to UUID for proper comparison
        try:
            import uuid as uuid_module
            resource_uuid = uuid_module.UUID(resource_id)
        except (ValueError, TypeError):
            # If resource_id is not a valid UUID string, return early
            return
        resource = session.query(db_models.Resource).filter(db_models.Resource.id == resource_uuid).first()
        if not resource:
            return

        # Mark started
        resource.ingestion_status = "processing"
        resource.ingestion_error = None
        resource.ingestion_started_at = datetime.now(timezone.utc)
        session.add(resource)
        session.commit()

        target_url = resource.source or ""
        fetched = ce.fetch_url(target_url)
        extracted = ce.extract_from_fetched(fetched)
        text_clean = clean_text(extracted.get("text", ""))

        # AI - let exceptions propagate to trigger failure path
        # Resolve AICore dynamically from this module to honor test patching
        if ai is not None:
            ai_core = ai
        else:
            try:
                import sys as _sys
                _mod = _sys.modules.get(__name__)
                AICoreClass = getattr(_mod, "AICore") if _mod is not None else AICore
            except Exception:  # pragma: no cover
                AICoreClass = AICore
            ai_core = AICoreClass()
        summary = ai_core.generate_summary(text_clean)
        tags_raw = ai_core.generate_tags(text_clean)

        # Authority control
        authority = get_authority_control(session)
        normalized_tags = authority.normalize_subjects(tags_raw)

        # Classification
        classifier = get_classification_service()
        # Use extracted title if current title is default "Untitled"
        extracted_title = extracted.get("title") or ""
        if resource.title == "Untitled" and extracted_title:
            title_final = extracted_title
        else:
            title_final = resource.title or extracted_title or "Untitled"
        # Prefer user-provided description over AI summary
        description_final = resource.description or summary or None
        classification_code = classifier.auto_classify(title_final, description_final, normalized_tags)

        # Archive
        meta = {
            "source_url": fetched.get("url"),
            "status": fetched.get("status"),
            "extracted_title": extracted.get("title"),
            "readability": readability_scores(text_clean),
            "content_type": fetched.get("content_type"),
        }
        root_path = archive_root or ARCHIVE_ROOT
        root_path = root_path if isinstance(root_path, Path) else Path(str(root_path))
        html_for_archive = fetched.get("html") or ""
        archive_info = ce.archive_local(
            fetched.get("url", target_url), html_for_archive, text_clean, meta, root_path
        )

        # Quality
        analyzer = get_quality_analyzer()
        candidate_metadata = {
            "title": title_final,
            "description": description_final,
            "subject": normalized_tags,
            "creator": resource.creator,
            "language": resource.language,
            "type": resource.type,
            "identifier": archive_info.get("archive_path"),
            "source": resource.source or fetched.get("url"),
        }
        quality = analyzer.overall_quality_score(candidate_metadata, text_clean)

        # Generate embedding for Phase 4 hybrid search
        try:
            from backend.app.services.ai_core import create_composite_text
            # Create a temporary resource object for embedding generation
            temp_resource = type('obj', (object,), {
                'title': title_final,
                'description': description_final,
                'subject': normalized_tags
            })()
            composite_text = create_composite_text(temp_resource)
            if composite_text.strip():
                embedding = ai_core.generate_embedding(composite_text)
                if embedding:
                    resource.embedding = embedding
        except Exception:
            # Embedding generation is optional, don't fail the whole ingestion
            pass

        # Persist updates
        resource.title = title_final
        resource.description = description_final
        resource.subject = normalized_tags
        resource.classification_code = classification_code
        resource.identifier = archive_info.get("archive_path")
        resource.source = resource.source or fetched.get("url")
        resource.quality_score = float(quality)
        resource.date_modified = resource.date_modified or datetime.now(timezone.utc)
        resource.ingestion_status = "completed"
        resource.ingestion_completed_at = datetime.now(timezone.utc)
        resource.format = fetched.get("content_type")  # Store content type for citation extraction
        session.add(resource)
        session.commit()
        
        # Track successful ingestion
        track_ingestion_success()
        
        # Phase 6: Extract citations if content type supports it
        try:
            content_type = fetched.get("content_type", "").lower()
            if any(ct in content_type for ct in ["html", "pdf", "markdown"]):
                from backend.app.services.citation_service import CitationService
                citation_service = CitationService(session)
                citation_service.extract_citations(str(resource.id))
                # Resolve internal citations
                citation_service.resolve_internal_citations()
        except Exception as citation_exc:
            # Citation extraction is optional, don't fail the whole ingestion
            print(f"Warning: Citation extraction failed for {resource_id}: {citation_exc}")

    except Exception as exc:  # pragma: no cover - error path
        if session is not None:
            try:
                # Convert string resource_id back to UUID for proper comparison
                try:
                    resource_uuid = uuid_module.UUID(resource_id)
                    resource = session.query(db_models.Resource).filter(db_models.Resource.id == resource_uuid).first()
                except (ValueError, TypeError):
                    resource = None
                if resource is not None:
                    resource.ingestion_status = "failed"
                    resource.ingestion_error = str(exc)
                    resource.ingestion_completed_at = datetime.now(timezone.utc)
                    session.add(resource)
                    session.commit()
                    
                    # Track failed ingestion
                    track_ingestion_failure(type(exc).__name__)
            except Exception:
                pass
    finally:
        decrement_active_ingestions()
        if session is not None:
            session.close()


def get_resource(db: Session, resource_id) -> Optional[db_models.Resource]:
    try:
        Base.metadata.create_all(bind=db.get_bind())
    except Exception:
        pass
    
    # Convert string resource_id to UUID if needed
    if isinstance(resource_id, str):
        try:
            import uuid as uuid_module
            resource_uuid = uuid_module.UUID(resource_id)
        except (ValueError, TypeError):
            return None
    else:
        resource_uuid = resource_id
    
    result = db.execute(
        select(db_models.Resource).filter(db_models.Resource.id == resource_uuid)
    )
    return result.scalar_one_or_none()


def _apply_resource_filters(query, filters: ResourceFilters):
    if not filters:
        return query

    if filters.q:
        q_val = f"%{filters.q.lower()}%"
        query = query.filter(
            or_(
                func.lower(db_models.Resource.title).like(q_val),
                func.lower(db_models.Resource.description).like(q_val),
            )
        )

    if filters.classification_code:
        query = query.filter(db_models.Resource.classification_code == filters.classification_code)

    if filters.type:
        query = query.filter(db_models.Resource.type == filters.type)

    if filters.language:
        query = query.filter(db_models.Resource.language == filters.language)

    if filters.read_status:
        query = query.filter(db_models.Resource.read_status == filters.read_status)

    if filters.min_quality is not None:
        query = query.filter(db_models.Resource.quality_score >= float(filters.min_quality))

    if filters.created_from:
        query = query.filter(db_models.Resource.created_at >= filters.created_from)
    if filters.created_to:
        query = query.filter(db_models.Resource.created_at <= filters.created_to)
    if filters.updated_from:
        query = query.filter(db_models.Resource.updated_at >= filters.updated_from)
    if filters.updated_to:
        query = query.filter(db_models.Resource.updated_at <= filters.updated_to)

    # Fallback subject matching on serialized JSON text (portable across SQLite/Postgres)
    if filters.subject_any:
        ser = func.lower(cast(db_models.Resource.subject, String))
        ors = [ser.like(f"%{term.lower()}%") for term in filters.subject_any]
        if ors:
            query = query.filter(or_(*ors))

    if filters.subject_all:
        ser_all = func.lower(cast(db_models.Resource.subject, String))
        for term in filters.subject_all:
            query = query.filter(ser_all.like(f"%{term.lower()}%"))

    return query


def list_resources(
    db: Session,
    filters: ResourceFilters,
    page: PageParams,
    sort: SortParams,
) -> Tuple[List[db_models.Resource], int]:
    try:
        Base.metadata.create_all(bind=db.get_bind())
    except Exception:
        pass
    query = select(db_models.Resource)
    query = _apply_resource_filters(query, filters)

    # Total before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_result = db.execute(count_query)
    total = total_result.scalar()

    # Sorting guard
    sort_map = {
        "created_at": db_models.Resource.created_at,
        "updated_at": db_models.Resource.updated_at,
        "quality_score": db_models.Resource.quality_score,
        "title": db_models.Resource.title,
    }
    sort_col = sort_map.get(sort.sort_by)
    if sort_col is None:
        # This should be prevented by Pydantic Literal, but double-guard anyway
        sort_col = db_models.Resource.created_at

    order = asc(sort_col) if sort.sort_dir == "asc" else desc(sort_col)
    query = query.order_by(order)

    query = query.offset(page.offset).limit(page.limit)
    result = db.execute(query)
    items = result.scalars().all()
    return items, total


def update_resource(db: Session, resource_id, payload: ResourceUpdate) -> db_models.Resource:
    try:
        Base.metadata.create_all(bind=db.get_bind())
    except Exception:
        pass
    resource = get_resource(db, resource_id)
    if not resource:
        raise ValueError("Resource not found")

    updates = payload.model_dump(exclude_unset=True)

    # Protect immutable/system-managed fields
    for key in [
        "id",
        "created_at",
        "updated_at",
    ]:
        updates.pop(key, None)

    # Track if fields that affect embedding have changed
    embedding_fields_changed = False
    embedding_affecting_fields = {"title", "description", "subject"}
    
    # Assign allowed fields with authority normalization on certain fields
    authority = get_authority_control(db)
    for key, value in updates.items():
        if key == "subject" and isinstance(value, list):
            setattr(resource, key, authority.normalize_subjects(value))
            embedding_fields_changed = True
        elif key == "creator":
            setattr(resource, key, authority.normalize_creator(value))
        elif key == "publisher":
            setattr(resource, key, authority.normalize_publisher(value))
        else:
            setattr(resource, key, value)
            if key in embedding_affecting_fields:
                embedding_fields_changed = True

    # Regenerate embedding if relevant fields changed
    if embedding_fields_changed:
        try:
            from backend.app.services.ai_core import create_composite_text, generate_embedding
            composite_text = create_composite_text(resource)
            if composite_text.strip():
                embedding = generate_embedding(composite_text)
                if embedding:
                    resource.embedding = embedding
        except Exception:
            # Embedding generation is optional, don't fail the update
            pass

    # Ensure updated_at moves forward
    resource.updated_at = datetime.now(timezone.utc)

    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


def delete_resource(db: Session, resource_id) -> None:
    try:
        Base.metadata.create_all(bind=db.get_bind())
    except Exception:
        pass
    resource = get_resource(db, resource_id)
    if not resource:
        raise ValueError("Resource not found")
    db.delete(resource)
    db.commit()
