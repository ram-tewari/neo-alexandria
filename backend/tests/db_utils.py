"""
Database utility functions for optimized test data creation.

This module provides helper functions for efficient database operations
in tests, including batch inserts, bulk deletes, and minimal data creation.
"""

from typing import List, Dict, Any, Type, TypeVar
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.app.database.models import Resource, AuthoritySubject, TaxonomyNode
from backend.app.domain.quality import QualityScore


T = TypeVar('T')


def batch_insert(db: Session, objects: List[Any]) -> List[Any]:
    """
    Batch insert multiple objects into the database.
    
    This is much faster than individual inserts as it uses a single
    database transaction and minimizes round trips.
    
    Args:
        db: Database session
        objects: List of SQLAlchemy model instances to insert
        
    Returns:
        List of inserted objects with IDs populated
        
    Example:
        resources = [Resource(title=f"Resource {i}") for i in range(10)]
        inserted = batch_insert(db, resources)
    """
    if not objects:
        return []
    
    db.add_all(objects)
    db.commit()
    
    # Refresh all objects to get IDs
    for obj in objects:
        db.refresh(obj)
    
    return objects


def bulk_delete(db: Session, model: Type[T], ids: List[Any]) -> int:
    """
    Bulk delete objects by ID.
    
    This is much faster than individual deletes as it uses a single
    DELETE query with an IN clause.
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        ids: List of IDs to delete
        
    Returns:
        Number of rows deleted
        
    Example:
        deleted_count = bulk_delete(db, Resource, resource_ids)
    """
    if not ids:
        return 0
    
    try:
        count = db.query(model).filter(model.id.in_(ids)).delete(synchronize_session=False)
        db.commit()
        return count
    except Exception:
        db.rollback()
        raise


def create_minimal_resource(
    title: str = "Test Resource",
    quality_score: float = 0.8,
    **kwargs
) -> Resource:
    """
    Create a Resource with minimal required fields.
    
    This creates a resource with only the essential fields populated,
    which is faster than creating resources with all fields.
    
    Args:
        title: Resource title
        quality_score: Overall quality score (0.0-1.0)
        **kwargs: Additional fields to set on the resource
        
    Returns:
        Resource instance (not yet persisted to database)
        
    Example:
        resource = create_minimal_resource(
            title="My Resource",
            quality_score=0.9,
            language="en"
        )
        db.add(resource)
        db.commit()
    """
    # Set defaults for required fields
    defaults = {
        "description": "Test description",
        "type": "article",
        "language": "en",
        "quality_score": quality_score,
        "quality_overall": quality_score,
        "quality_accuracy": min(1.0, quality_score + 0.02),
        "quality_completeness": min(1.0, quality_score - 0.01),
        "quality_consistency": min(1.0, quality_score + 0.01),
        "quality_timeliness": min(1.0, quality_score - 0.02),
        "quality_relevance": min(1.0, quality_score + 0.03),
    }
    
    # Override defaults with provided kwargs
    defaults.update(kwargs)
    
    return Resource(title=title, **defaults)


def create_minimal_resources_batch(
    count: int = 10,
    base_quality: float = 0.7,
    quality_increment: float = 0.05,
    **common_kwargs
) -> List[Resource]:
    """
    Create multiple resources with minimal fields in batch.
    
    This is optimized for creating test data quickly by using
    minimal fields and preparing all objects in memory before
    database insertion.
    
    Args:
        count: Number of resources to create
        base_quality: Starting quality score
        quality_increment: Amount to increment quality for each resource
        **common_kwargs: Common fields to set on all resources
        
    Returns:
        List of Resource instances (not yet persisted to database)
        
    Example:
        resources = create_minimal_resources_batch(
            count=5,
            base_quality=0.8,
            language="en"
        )
        batch_insert(db, resources)
    """
    resources = []
    for i in range(count):
        quality = min(1.0, base_quality + i * quality_increment)
        resource = create_minimal_resource(
            title=f"Test Resource {i}",
            quality_score=quality,
            **common_kwargs
        )
        resources.append(resource)
    
    return resources


def create_resource_with_quality_score(
    title: str,
    quality_score: QualityScore,
    **kwargs
) -> Resource:
    """
    Create a Resource from a QualityScore domain object.
    
    This helper converts a QualityScore domain object into the
    individual quality dimension fields required by the Resource model.
    
    Args:
        title: Resource title
        quality_score: QualityScore domain object
        **kwargs: Additional fields to set on the resource
        
    Returns:
        Resource instance (not yet persisted to database)
        
    Example:
        quality = QualityScore(0.9, 0.85, 0.88, 0.92, 0.9)
        resource = create_resource_with_quality_score(
            "My Resource",
            quality,
            language="en"
        )
        db.add(resource)
        db.commit()
    """
    defaults = {
        "description": "Test description",
        "type": "article",
        "language": "en",
        "quality_score": quality_score.overall_score(),
        "quality_overall": quality_score.overall_score(),
        "quality_accuracy": quality_score.accuracy,
        "quality_completeness": quality_score.completeness,
        "quality_consistency": quality_score.consistency,
        "quality_timeliness": quality_score.timeliness,
        "quality_relevance": quality_score.relevance,
        "quality_last_computed": datetime.now(timezone.utc),
        "quality_computation_version": "v2.0",
    }
    
    defaults.update(kwargs)
    
    return Resource(title=title, **defaults)


def create_minimal_authority_subject(
    canonical_form: str,
    usage_count: int = 1,
    **kwargs
) -> AuthoritySubject:
    """
    Create an AuthoritySubject with minimal required fields.
    
    Args:
        canonical_form: Canonical form of the subject
        usage_count: Usage count
        **kwargs: Additional fields to set
        
    Returns:
        AuthoritySubject instance (not yet persisted to database)
        
    Example:
        subject = create_minimal_authority_subject(
            "Machine Learning",
            usage_count=100
        )
        db.add(subject)
        db.commit()
    """
    defaults = {
        "variants": [canonical_form.lower()],
        "usage_count": usage_count,
    }
    
    defaults.update(kwargs)
    
    return AuthoritySubject(canonical_form=canonical_form, **defaults)


def create_minimal_taxonomy_node(
    code: str,
    label: str,
    **kwargs
) -> TaxonomyNode:
    """
    Create a TaxonomyNode with minimal required fields.
    
    Args:
        code: Taxonomy code (e.g., "004")
        label: Node label
        **kwargs: Additional fields to set
        
    Returns:
        TaxonomyNode instance (not yet persisted to database)
        
    Example:
        node = create_minimal_taxonomy_node(
            "004",
            "Computer Science"
        )
        db.add(node)
        db.commit()
    """
    defaults = {
        "level": len(code.split(".")),
        "parent_code": None,
    }
    
    defaults.update(kwargs)
    
    return TaxonomyNode(code=code, label=label, **defaults)


def cleanup_test_data(db: Session, *model_id_pairs):
    """
    Clean up test data with bulk deletes.
    
    This helper performs bulk deletes for multiple model types
    in a single transaction, which is much faster than individual
    deletes.
    
    Args:
        db: Database session
        *model_id_pairs: Tuples of (Model, [ids]) to delete
        
    Example:
        cleanup_test_data(
            db,
            (Resource, resource_ids),
            (AuthoritySubject, subject_ids),
            (TaxonomyNode, node_ids)
        )
    """
    try:
        for model, ids in model_id_pairs:
            if ids:
                db.query(model).filter(model.id.in_(ids)).delete(synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()
        raise
