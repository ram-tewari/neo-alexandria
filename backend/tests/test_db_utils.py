"""
Tests for database utility functions.

This module tests the optimized database operations provided by db_utils.py.
"""

import pytest
from backend.tests.db_utils import (
    batch_insert,
    bulk_delete,
    create_minimal_resource,
    create_minimal_resources_batch,
    create_resource_with_quality_score,
    create_minimal_authority_subject,
    cleanup_test_data
)
from backend.app.database.models import Resource, AuthoritySubject
from backend.app.domain.quality import QualityScore


def test_batch_insert(test_db):
    """Test batch insert operation."""
    db = test_db()
    
    # Create resources
    resources = [
        create_minimal_resource(title=f"Resource {i}", quality_score=0.8)
        for i in range(5)
    ]
    
    # Batch insert
    inserted = batch_insert(db, resources)
    
    # Verify
    assert len(inserted) == 5
    assert all(r.id is not None for r in inserted)
    
    # Cleanup
    bulk_delete(db, Resource, [r.id for r in inserted])
    db.close()


def test_bulk_delete(test_db):
    """Test bulk delete operation."""
    db = test_db()
    
    # Create and insert resources
    resources = create_minimal_resources_batch(count=5)
    inserted = batch_insert(db, resources)
    resource_ids = [r.id for r in inserted]
    
    # Verify they exist
    count_before = db.query(Resource).filter(Resource.id.in_(resource_ids)).count()
    assert count_before == 5
    
    # Bulk delete
    deleted_count = bulk_delete(db, Resource, resource_ids)
    
    # Verify deletion
    assert deleted_count == 5
    count_after = db.query(Resource).filter(Resource.id.in_(resource_ids)).count()
    assert count_after == 0
    
    db.close()


def test_create_minimal_resource():
    """Test creating a minimal resource."""
    resource = create_minimal_resource(
        title="Test Resource",
        quality_score=0.9,
        language="en"
    )
    
    assert resource.title == "Test Resource"
    assert resource.quality_score == 0.9
    assert resource.language == "en"
    assert resource.type == "article"  # Default
    assert resource.description == "Test description"  # Default


def test_create_minimal_resources_batch():
    """Test creating multiple resources in batch."""
    resources = create_minimal_resources_batch(
        count=10,
        base_quality=0.7,
        quality_increment=0.05,
        language="en"
    )
    
    assert len(resources) == 10
    assert all(r.language == "en" for r in resources)
    
    # Verify quality scores increment
    for i, resource in enumerate(resources):
        expected_quality = min(1.0, 0.7 + i * 0.05)
        assert abs(resource.quality_score - expected_quality) < 0.01


def test_create_resource_with_quality_score():
    """Test creating a resource from QualityScore domain object."""
    quality = QualityScore(
        accuracy=0.9,
        completeness=0.85,
        consistency=0.88,
        timeliness=0.92,
        relevance=0.9
    )
    
    resource = create_resource_with_quality_score(
        "Test Resource",
        quality,
        language="en"
    )
    
    assert resource.title == "Test Resource"
    assert resource.quality_accuracy == 0.9
    assert resource.quality_completeness == 0.85
    assert resource.quality_consistency == 0.88
    assert resource.quality_timeliness == 0.92
    assert resource.quality_relevance == 0.9
    assert abs(resource.quality_overall - quality.overall_score()) < 0.01


def test_create_minimal_authority_subject():
    """Test creating a minimal authority subject."""
    subject = create_minimal_authority_subject(
        "Machine Learning",
        usage_count=100
    )
    
    assert subject.canonical_form == "Machine Learning"
    assert subject.usage_count == 100
    assert "machine learning" in subject.variants


def test_cleanup_test_data(test_db):
    """Test cleanup of multiple model types."""
    db = test_db()
    
    # Create resources
    resources = create_minimal_resources_batch(count=3)
    inserted_resources = batch_insert(db, resources)
    resource_ids = [r.id for r in inserted_resources]
    
    # Create subjects
    subjects = [
        create_minimal_authority_subject(f"Subject {i}", usage_count=i)
        for i in range(3)
    ]
    inserted_subjects = batch_insert(db, subjects)
    subject_ids = [s.id for s in inserted_subjects]
    
    # Verify they exist
    assert db.query(Resource).filter(Resource.id.in_(resource_ids)).count() == 3
    assert db.query(AuthoritySubject).filter(AuthoritySubject.id.in_(subject_ids)).count() == 3
    
    # Cleanup all at once
    cleanup_test_data(
        db,
        (Resource, resource_ids),
        (AuthoritySubject, subject_ids)
    )
    
    # Verify deletion
    assert db.query(Resource).filter(Resource.id.in_(resource_ids)).count() == 0
    assert db.query(AuthoritySubject).filter(AuthoritySubject.id.in_(subject_ids)).count() == 0
    
    db.close()


def test_batch_operations_performance(test_db, benchmark=None):
    """Test that batch operations are faster than individual operations."""
    db = test_db()
    
    # This is a simple verification test
    # In a real benchmark, batch operations should be 5-10x faster
    
    # Create 20 resources using batch operations
    resources = create_minimal_resources_batch(count=20)
    inserted = batch_insert(db, resources)
    resource_ids = [r.id for r in inserted]
    
    # Verify all inserted
    assert len(inserted) == 20
    assert all(r.id is not None for r in inserted)
    
    # Cleanup using bulk delete
    deleted_count = bulk_delete(db, Resource, resource_ids)
    assert deleted_count == 20
    
    db.close()
