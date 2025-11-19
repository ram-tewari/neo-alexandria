from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, or_, asc, desc, String, cast, select

from backend.app.database import models as db_models
from backend.app.database.base import Base, SessionLocal
from backend.app.utils import content_extractor as ce
from backend.app.utils.text_processor import clean_text, readability_scores
from backend.app.services.dependencies import (
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
from backend.app.events.event_system import event_emitter, EventPriority
from backend.app.events.event_types import SystemEvent


ARCHIVE_ROOT = Path("storage/archive")
logger = logging.getLogger(__name__)


def _find_existing_resource_by_url(db: Session, url: str) -> Optional[db_models.Resource]:
    """
    Query for existing resource by source URL.
    
    Args:
        db: Database session
        url: Source URL to search for
        
    Returns:
        Existing resource if found, None otherwise
    """
    result = db.execute(
        select(db_models.Resource)
        .filter(db_models.Resource.source == url)
        .order_by(db_models.Resource.created_at.desc())
    )
    return result.scalar_one_or_none()


def create_pending_resource(db: Session, payload: Dict[str, Any]) -> db_models.Resource:
    """
    Create a pending resource row and return it. Idempotent on URL/source.
    
    Args:
        db: Database session
        payload: Resource data including required 'url' field
        
    Returns:
        Created or existing resource
        
    Raises:
        ValueError: If url is not provided
    """
    try:
        Base.metadata.create_all(bind=db.get_bind())
    except Exception:
        pass

    url = payload.get("url")
    if not url:
        raise ValueError("url is required")

    # Query: Check for existing resource (no side effects)
    existing = _find_existing_resource_by_url(db, url)
    if existing:
        logger.info(f"Reusing existing resource for URL: {url}")
        return existing

    # Modifier: Create new resource
    logger.info(f"Creating new pending resource for URL: {url}")
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
    logger.info(f"Created pending resource with source: {url}")
    
    # Emit resource.created event
    try:
        event_emitter.emit(
            SystemEvent.RESOURCE_CREATED,
            {
                "resource_id": str(resource.id),
                "title": resource.title,
                "source": resource.source
            },
            priority=EventPriority.NORMAL
        )
        logger.debug(f"Emitted resource.created event for {resource.id}")
    except Exception as e:
        logger.error(f"Failed to emit resource.created event: {e}", exc_info=True)
    
    return resource


def _mark_ingestion_started(session: Session, resource: db_models.Resource) -> None:
    """
    Mark resource ingestion as started (modifier).
    
    Args:
        session: Database session
        resource: Resource to update
    """
    resource.ingestion_status = "processing"
    resource.ingestion_error = None
    resource.ingestion_started_at = datetime.now(timezone.utc)
    session.add(resource)
    session.commit()
    logger.info(f"Resource {resource.id} marked as processing")


def _mark_ingestion_failed(session: Session, resource: db_models.Resource, error: str) -> None:
    """
    Mark resource ingestion as failed (modifier).
    
    Args:
        session: Database session
        resource: Resource to update
        error: Error message
    """
    resource.ingestion_status = "failed"
    resource.ingestion_error = error
    resource.ingestion_completed_at = datetime.now(timezone.utc)
    session.add(resource)
    session.commit()
    logger.error(f"Resource {resource.id} marked as failed: {error}")


def _mark_ingestion_completed(session: Session, resource: db_models.Resource) -> None:
    """
    Mark resource ingestion as completed (modifier).
    
    Args:
        session: Database session
        resource: Resource to update
    """
    resource.ingestion_status = "completed"
    resource.ingestion_completed_at = datetime.now(timezone.utc)
    session.add(resource)
    session.commit()
    logger.info(f"Resource {resource.id} marked as completed")


def _fetch_and_extract_content(target_url: str) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
    """
    Fetch and extract content from URL (query with external side effects).
    
    Args:
        target_url: URL to fetch
        
    Returns:
        Tuple of (fetched_data, extracted_data, cleaned_text)
    """
    logger.info(f"Fetching content from {target_url}")
    fetched = ce.fetch_url(target_url)
    logger.info("Content fetched successfully, extracting text")
    extracted = ce.extract_from_fetched(fetched)
    text_clean = clean_text(extracted.get("text", ""))
    logger.info(f"Text extracted and cleaned, length: {len(text_clean)} characters")
    return fetched, extracted, text_clean


def _generate_ai_content(ai_core: AICore, text_clean: str) -> Tuple[str, List[str]]:
    """
    Generate AI summary and tags (query with external side effects).
    
    Args:
        ai_core: AI core service
        text_clean: Cleaned text
        
    Returns:
        Tuple of (summary, tags)
    """
    summary = ai_core.generate_summary(text_clean)
    tags_raw = ai_core.generate_tags(text_clean)
    return summary, tags_raw


def _generate_embeddings(
    ai_core: AICore,
    resource: db_models.Resource,
    session: Session,
    title: str,
    description: str,
    tags: List[str]
) -> None:
    """
    Generate dense and sparse embeddings for resource (modifier).
    
    Args:
        ai_core: AI core service
        resource: Resource to update
        session: Database session
        title: Resource title
        description: Resource description
        tags: Resource tags
    """
    # Generate dense embedding
    try:
        from backend.app.services.ai_core import create_composite_text
        temp_resource = type('obj', (object,), {
            'title': title,
            'description': description,
            'subject': tags
        })()
        composite_text = create_composite_text(temp_resource)
        if composite_text.strip():
            embedding = ai_core.generate_embedding(composite_text)
            if embedding:
                resource.embedding = embedding
                logger.info(f"Generated dense embedding for resource {resource.id}")
    except Exception as e:
        logger.warning(f"Dense embedding generation failed: {e}")
    
    # Generate sparse embedding
    try:
        from backend.app.services.sparse_embedding_service import SparseEmbeddingService
        sparse_service = SparseEmbeddingService(session, model_name="BAAI/bge-m3")
        
        text_parts = []
        if title:
            text_parts.append(title)
        if description:
            text_parts.append(description)
        if tags:
            subjects_text = " ".join(tags)
            if subjects_text.strip():
                text_parts.append(f"Keywords: {subjects_text}")
        
        composite_text = " ".join(text_parts)
        
        if not composite_text.strip():
            resource.sparse_embedding = None
            resource.sparse_embedding_model = None
            resource.sparse_embedding_updated_at = datetime.now(timezone.utc)
        else:
            sparse_vec = sparse_service.generate_sparse_embedding(composite_text)
            if sparse_vec:
                resource.sparse_embedding = json.dumps(sparse_vec)
                resource.sparse_embedding_model = "BAAI/bge-m3"
                resource.sparse_embedding_updated_at = datetime.now(timezone.utc)
                logger.info(f"Generated sparse embedding for resource {resource.id}")
            else:
                resource.sparse_embedding = None
                resource.sparse_embedding_model = None
                resource.sparse_embedding_updated_at = None
    except Exception as e:
        logger.warning(f"Sparse embedding generation failed: {e}")
        resource.sparse_embedding = None
        resource.sparse_embedding_model = None
        resource.sparse_embedding_updated_at = None


def _perform_ml_classification(session: Session, resource_id) -> None:
    """
    Perform ML classification on resource (modifier).
    
    Args:
        session: Database session
        resource_id: Resource ID
    """
    try:
        from backend.app.services.classification_service import ClassificationService
        
        classification_service = ClassificationService(
            db=session,
            use_ml=True,
            confidence_threshold=0.3
        )
        
        classification_result = classification_service.classify_resource(
            resource_id=resource_id,
            use_ml=True
        )
        
        logger.info(f"ML classification completed for resource {resource_id}: "
                   f"{len(classification_result.get('classifications', []))} classifications")
    except Exception as e:
        logger.warning(f"ML classification failed for resource {resource_id}: {e}")


def _compute_quality_scores(session: Session, resource_id) -> None:
    """
    Compute quality scores for resource (modifier).
    
    Args:
        session: Database session
        resource_id: Resource ID
    """
    try:
        from backend.app.services.quality_service import QualityService
        
        quality_service = QualityService(db=session)
        quality_result = quality_service.compute_quality(resource_id)
        
        # quality_result is a QualityScore domain object
        logger.info(f"Quality assessment completed for resource {resource_id}: "
                   f"overall={quality_result.overall_score():.2f}")
    except Exception as e:
        logger.warning(f"Quality assessment failed for resource {resource_id}: {e}")


def _evaluate_summarization(session: Session, resource_id, summary: str) -> None:
    """
    Evaluate summarization quality (modifier).
    
    Args:
        session: Database session
        resource_id: Resource ID
        summary: Generated summary
    """
    if not summary or not summary.strip():
        return
    
    try:
        from backend.app.services.summarization_evaluator import SummarizationEvaluator
        
        summarization_evaluator = SummarizationEvaluator(db=session)
        summary_result = summarization_evaluator.evaluate_summary(
            resource_id=resource_id,
            use_g_eval=False
        )
        
        logger.info(f"Summarization evaluation completed for resource {resource_id}: "
                   f"overall={summary_result.get('overall', 0.0):.2f}")
    except Exception as e:
        logger.warning(f"Summarization evaluation failed for resource {resource_id}: {e}")


def _extract_citations(session: Session, resource_id: str, content_type: str) -> None:
    """
    Extract citations from resource content (modifier).
    
    Args:
        session: Database session
        resource_id: Resource ID
        content_type: Content type
    """
    try:
        content_type_lower = content_type.lower()
        if any(ct in content_type_lower for ct in ["html", "pdf", "markdown"]):
            from backend.app.services.citation_service import CitationService
            citation_service = CitationService(session)
            citation_service.extract_citations(resource_id)
            citation_service.resolve_internal_citations()
            logger.info(f"Citations extracted for resource {resource_id}")
    except Exception as e:
        logger.warning(f"Citation extraction failed for resource {resource_id}: {e}")


def process_ingestion(
    resource_id: str,
    archive_root: Path | str | None = None,
    ai: Optional[AICore] = None,
    engine_url: Optional[str] = None,
) -> None:
    """
    Background ingestion job (modifier, returns None). Opens its own DB session.

    Steps: fetch, extract, AI summarize/tag, authority normalize, classify, quality, archive, persist.
    
    Args:
        resource_id: Resource ID to ingest
        archive_root: Optional archive root directory
        ai: Optional AI core instance
        engine_url: Optional database engine URL
    """
    session: Optional[Session] = None
    increment_active_ingestions()
    start_time = datetime.now(timezone.utc)
    
    logger.info(f"Starting ingestion for resource {resource_id}")
    
    # Emit ingestion.started event
    event_emitter.emit(
        SystemEvent.INGESTION_STARTED,
        {
            "resource_id": resource_id,
            "started_at": start_time.isoformat()
        },
        priority=EventPriority.NORMAL
    )
    
    try:
        # Setup database session
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

        # Query: Get resource
        try:
            import uuid as uuid_module
            resource_uuid = uuid_module.UUID(resource_id)
        except (ValueError, TypeError):
            logger.error(f"Invalid UUID format for resource_id: {resource_id}")
            return
        
        resource = session.query(db_models.Resource).filter(db_models.Resource.id == resource_uuid).first()
        if not resource:
            logger.warning(f"Resource not found: {resource_id}")
            return

        # Modifier: Mark ingestion started
        _mark_ingestion_started(session, resource)
        
        target_url = resource.source or ""
        
        # Query: Fetch and extract content
        fetched, extracted, text_clean = _fetch_and_extract_content(target_url)

        # Resolve AI core
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
        
        # Query: Generate AI content
        summary, tags_raw = _generate_ai_content(ai_core, text_clean)

        # Query: Normalize tags
        authority = get_authority_control(session)
        normalized_tags = authority.normalize_subjects(tags_raw)

        # Query: Classify resource
        classifier = get_classification_service()
        extracted_title = extracted.get("title") or ""
        if resource.title == "Untitled" and extracted_title:
            title_final = extracted_title
        else:
            title_final = resource.title or extracted_title or "Untitled"
        description_final = resource.description or summary or None
        classification_code = classifier.auto_classify(title_final, description_final, normalized_tags)

        # Modifier: Archive content
        meta = {
            "source_url": fetched.get("url"),
            "status": fetched.get("status"),
            "extracted_title": extracted.get("title"),
            "readability": readability_scores(text_clean),
            "content_type": fetched.get("content_type"),
        }
        root_path = archive_root or ARCHIVE_ROOT
        root_path = root_path if isinstance(root_path, Path) else Path(str(root_path))
        
        try:
            root_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Archive root ready: {root_path}")
        except Exception as mkdir_exc:
            logger.error(f"Failed to create archive root {root_path}: {str(mkdir_exc)}")
        
        html_for_archive = fetched.get("html") or ""
        archive_info = ce.archive_local(
            fetched.get("url", target_url), html_for_archive, text_clean, meta, root_path
        )
        logger.info(f"Content archived to {archive_info.get('archive_path')}")

        # Modifier: Generate embeddings
        _generate_embeddings(ai_core, resource, session, title_final, description_final, normalized_tags)
        
        # Modifier: Perform ML classification
        _perform_ml_classification(session, resource.id)

        # Query: Compute legacy quality score
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
        quality = analyzer.overall_quality(candidate_metadata, text_clean)

        # Modifier: Persist resource updates
        resource.title = title_final
        resource.description = description_final
        resource.subject = normalized_tags
        resource.classification_code = classification_code
        resource.identifier = archive_info.get("archive_path")
        resource.source = resource.source or fetched.get("url")
        resource.quality_score = float(quality)
        resource.date_modified = resource.date_modified or datetime.now(timezone.utc)
        resource.format = fetched.get("content_type")
        session.add(resource)
        session.commit()
        
        # Modifier: Mark ingestion completed
        _mark_ingestion_completed(session, resource)
        
        # Modifier: Compute quality scores
        _compute_quality_scores(session, resource.id)
        
        # Modifier: Evaluate summarization
        _evaluate_summarization(session, resource.id, summary)
        
        # Modifier: Extract citations
        _extract_citations(session, str(resource.id), fetched.get("content_type", ""))
        
        # Track successful ingestion
        track_ingestion_success()
        
        # Calculate duration
        end_time = datetime.now(timezone.utc)
        duration_seconds = (end_time - start_time).total_seconds()
        
        logger.info(f"Ingestion completed successfully for resource {resource_id}")
        
        # Emit ingestion.completed event
        event_emitter.emit(
            SystemEvent.INGESTION_COMPLETED,
            {
                "resource_id": resource_id,
                "duration_seconds": duration_seconds,
                "success": True,
                "completed_at": end_time.isoformat()
            },
            priority=EventPriority.NORMAL
        )

    except Exception as exc:  # pragma: no cover - error path
        logger.error(f"Ingestion failed for resource {resource_id}: {type(exc).__name__}: {str(exc)}", exc_info=True)
        
        # Calculate duration
        end_time = datetime.now(timezone.utc)
        duration_seconds = (end_time - start_time).total_seconds()
        
        # Emit ingestion.failed event
        event_emitter.emit(
            SystemEvent.INGESTION_FAILED,
            {
                "resource_id": resource_id,
                "error": str(exc),
                "error_type": type(exc).__name__,
                "duration_seconds": duration_seconds,
                "success": False,
                "failed_at": end_time.isoformat()
            },
            priority=EventPriority.HIGH
        )
        
        if session is not None:
            try:
                import uuid as uuid_module
                try:
                    resource_uuid = uuid_module.UUID(resource_id)
                    resource = session.query(db_models.Resource).filter(db_models.Resource.id == resource_uuid).first()
                except (ValueError, TypeError):
                    resource = None
                
                if resource is not None:
                    _mark_ingestion_failed(session, resource, str(exc))
                    track_ingestion_failure(type(exc).__name__)
            except Exception as commit_exc:
                logger.error(f"Failed to update resource status for {resource_id}: {str(commit_exc)}")
    finally:
        decrement_active_ingestions()
        if session is not None:
            session.close()


def get_resource(db: Session, resource_id) -> Optional[db_models.Resource]:
    """
    Query for a resource by ID (pure query, no side effects).
    
    Args:
        db: Database session
        resource_id: Resource ID (UUID or string)
        
    Returns:
        Resource if found, None otherwise
    """
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
    """
    Apply filters to resource query (pure query helper).
    
    Args:
        query: SQLAlchemy query
        filters: Resource filters
        
    Returns:
        Filtered query
    """
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
    """
    Query for list of resources with filtering, pagination, and sorting (pure query).
    
    Args:
        db: Database session
        filters: Resource filters
        page: Pagination parameters
        sort: Sort parameters
        
    Returns:
        Tuple of (resources, total_count)
    """
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


def _apply_resource_updates(
    resource: db_models.Resource,
    updates: Dict[str, Any],
    authority
) -> Tuple[bool, bool, bool]:
    """
    Apply updates to resource fields (modifier helper).
    
    Args:
        resource: Resource to update
        updates: Dictionary of field updates
        authority: Authority control service
        
    Returns:
        Tuple of (embedding_fields_changed, quality_fields_changed, content_changed)
    """
    embedding_fields_changed = False
    embedding_affecting_fields = {"title", "description", "subject"}
    
    quality_fields_changed = False
    quality_affecting_fields = {
        "title", "description", "subject", "content", 
        "creator", "publisher", "date_created", "publication_year",
        "doi", "pmid", "arxiv_id", "journal", "affiliations", "funding_sources"
    }
    
    content_changed = False
    content_fields = {"content", "identifier"}  # identifier is the archive path with content
    
    # Track if quality_score was explicitly set (manual override)
    quality_score_manually_set = "quality_score" in updates
    
    for key, value in updates.items():
        if key == "subject" and isinstance(value, list):
            setattr(resource, key, authority.normalize_subjects(value))
            embedding_fields_changed = True
            # Only trigger recomputation if quality_score wasn't manually set
            if not quality_score_manually_set:
                quality_fields_changed = True
        elif key == "creator":
            setattr(resource, key, authority.normalize_creator(value))
            # Only trigger recomputation if quality_score wasn't manually set
            if not quality_score_manually_set:
                quality_fields_changed = True
        elif key == "publisher":
            setattr(resource, key, authority.normalize_publisher(value))
            # Only trigger recomputation if quality_score wasn't manually set
            if not quality_score_manually_set:
                quality_fields_changed = True
        elif key == "quality_score":
            # Handle QualityScore domain object or float
            if hasattr(value, 'overall_score'):
                # It's a QualityScore domain object
                setattr(resource, key, value.overall_score())
            elif hasattr(value, 'to_dict'):
                # It has a to_dict method, extract overall_score
                setattr(resource, key, value.to_dict().get('overall_score', 0.0))
            else:
                # It's already a float or numeric value
                setattr(resource, key, float(value))
            # Don't trigger recomputation when quality_score is manually set
        else:
            setattr(resource, key, value)
            if key in embedding_affecting_fields:
                embedding_fields_changed = True
            if key in quality_affecting_fields and not quality_score_manually_set:
                quality_fields_changed = True
            if key in content_fields:
                content_changed = True
    
    return embedding_fields_changed, quality_fields_changed, content_changed


def _regenerate_embeddings(db: Session, resource: db_models.Resource) -> None:
    """
    Regenerate dense and sparse embeddings for resource (modifier).
    
    Args:
        db: Database session
        resource: Resource to regenerate embeddings for
    """
    # Regenerate dense embedding
    try:
        from backend.app.services.ai_core import create_composite_text, generate_embedding
        composite_text = create_composite_text(resource)
        if composite_text.strip():
            embedding = generate_embedding(composite_text)
            if embedding:
                resource.embedding = embedding
                logger.info(f"Regenerated dense embedding for resource {resource.id}")
    except Exception as e:
        logger.warning(f"Dense embedding regeneration failed for {resource.id}: {e}")
    
    # Regenerate sparse embedding
    try:
        from backend.app.services.sparse_embedding_service import SparseEmbeddingService
        sparse_service = SparseEmbeddingService(db, model_name="BAAI/bge-m3")
        
        text_parts = []
        if resource.title:
            text_parts.append(resource.title)
        if resource.description:
            text_parts.append(resource.description)
        if resource.subject:
            subjects_text = " ".join(resource.subject)
            if subjects_text.strip():
                text_parts.append(f"Keywords: {subjects_text}")
        
        composite_text = " ".join(text_parts)
        
        if not composite_text.strip():
            resource.sparse_embedding = None
            resource.sparse_embedding_model = None
            resource.sparse_embedding_updated_at = datetime.now(timezone.utc)
        else:
            sparse_vec = sparse_service.generate_sparse_embedding(composite_text)
            if sparse_vec:
                resource.sparse_embedding = json.dumps(sparse_vec)
                resource.sparse_embedding_model = "BAAI/bge-m3"
                resource.sparse_embedding_updated_at = datetime.now(timezone.utc)
                logger.info(f"Regenerated sparse embedding for resource {resource.id}")
            else:
                resource.sparse_embedding = None
                resource.sparse_embedding_model = None
                resource.sparse_embedding_updated_at = None
    except Exception as e:
        logger.warning(f"Sparse embedding regeneration failed for {resource.id}: {e}")
        resource.sparse_embedding = None
        resource.sparse_embedding_model = None
        resource.sparse_embedding_updated_at = None


def _recompute_quality(db: Session, resource_id) -> None:
    """
    Recompute quality score for resource (modifier).
    
    Args:
        db: Database session
        resource_id: Resource ID
    """
    try:
        from backend.app.services.quality_service import QualityService
        
        quality_service = QualityService(db=db)
        quality_result = quality_service.compute_quality(resource_id)
        
        # quality_result is a QualityScore domain object
        logger.info(f"Recomputed quality for resource {resource_id}: "
                   f"overall={quality_result.overall_score():.2f}")
    except Exception as e:
        logger.warning(f"Quality recomputation failed for resource {resource_id}: {e}")


def update_resource(db: Session, resource_id, payload: ResourceUpdate) -> db_models.Resource:
    """
    Update a resource with new data.
    
    Args:
        db: Database session
        resource_id: Resource ID
        payload: Update data
        
    Returns:
        Updated resource
        
    Raises:
        ValueError: If resource not found
    """
    try:
        Base.metadata.create_all(bind=db.get_bind())
    except Exception:
        pass
    
    # Query: Get resource
    resource = get_resource(db, resource_id)
    if not resource:
        raise ValueError("Resource not found")

    updates = payload.model_dump(exclude_unset=True)

    # Protect immutable/system-managed fields
    for key in ["id", "created_at", "updated_at"]:
        updates.pop(key, None)

    logger.info(f"Updating resource {resource_id} with {len(updates)} field(s)")
    
    # Track which fields changed
    changed_fields = list(updates.keys())
    
    # Modifier: Apply updates
    authority = get_authority_control(db)
    embedding_changed, quality_changed, content_changed = _apply_resource_updates(resource, updates, authority)

    # Modifier: Regenerate embeddings if needed
    if embedding_changed:
        _regenerate_embeddings(db, resource)

    # Modifier: Update timestamp
    resource.updated_at = datetime.now(timezone.utc)

    # Modifier: Persist changes
    db.add(resource)
    db.commit()
    db.refresh(resource)
    
    logger.info(f"Successfully updated resource {resource_id}")
    
    # Emit resource.updated event
    event_emitter.emit(
        SystemEvent.RESOURCE_UPDATED,
        {
            "resource_id": str(resource.id),
            "changed_fields": changed_fields
        },
        priority=EventPriority.HIGH
    )
    
    # Emit specific change events
    if content_changed:
        event_emitter.emit(
            SystemEvent.RESOURCE_CONTENT_CHANGED,
            {
                "resource_id": str(resource.id),
                "changed_fields": changed_fields
            },
            priority=EventPriority.HIGH
        )
    
    # Metadata changed if quality fields changed but not content
    metadata_fields = {"title", "description", "subject", "creator", "publisher", 
                      "date_created", "publication_year", "doi", "pmid", "arxiv_id", 
                      "journal", "affiliations", "funding_sources", "language", "type"}
    metadata_changed = any(field in metadata_fields for field in changed_fields)
    
    if metadata_changed and not content_changed:
        event_emitter.emit(
            SystemEvent.RESOURCE_METADATA_CHANGED,
            {
                "resource_id": str(resource.id),
                "changed_fields": changed_fields
            },
            priority=EventPriority.NORMAL
        )
    
    # Modifier: Recompute quality if needed (after commit)
    if quality_changed:
        _recompute_quality(db, resource_id)
    
    return resource


def _delete_resource_annotations(db: Session, resource_id) -> None:
    """
    Delete annotations associated with a resource (modifier).
    
    Args:
        db: Database session
        resource_id: Resource ID
    """
    try:
        from backend.app.database.models import Annotation
        
        # Convert resource_id to UUID if needed
        if isinstance(resource_id, str):
            try:
                import uuid as uuid_module
                resource_uuid = uuid_module.UUID(resource_id)
            except (ValueError, TypeError):
                resource_uuid = resource_id
        else:
            resource_uuid = resource_id
        
        # Delete annotations associated with this resource
        annotation_count = db.query(Annotation).filter(Annotation.resource_id == resource_uuid).delete()
        if annotation_count > 0:
            logger.info(f"Deleted {annotation_count} annotations for resource {resource_id}")
    except Exception as e:
        # Log but don't fail if annotation deletion fails
        # The CASCADE constraint will handle it at the database level
        logger.warning(f"Could not explicitly delete annotations for resource {resource_id}: {e}")


def delete_resource(db: Session, resource_id) -> None:
    """
    Delete a resource and its associated data (modifier, returns None).
    
    Args:
        db: Database session
        resource_id: Resource ID
        
    Raises:
        ValueError: If resource not found
    """
    try:
        Base.metadata.create_all(bind=db.get_bind())
    except Exception:
        pass
    
    # Query: Get resource
    resource = get_resource(db, resource_id)
    if not resource:
        raise ValueError("Resource not found")
    
    logger.info(f"Deleting resource {resource_id}")
    
    # Store resource info for event
    resource_info = {
        "resource_id": str(resource.id),
        "title": resource.title
    }
    
    # Modifier: Delete associated annotations
    _delete_resource_annotations(db, resource_id)
    
    # Modifier: Delete resource
    db.delete(resource)
    db.commit()
    
    logger.info(f"Successfully deleted resource {resource_id}")
    
    # Emit resource.deleted event
    event_emitter.emit(
        SystemEvent.RESOURCE_DELETED,
        resource_info,
        priority=EventPriority.HIGH
    )
