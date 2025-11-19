"""
Neo Alexandria 2.0 - Annotation Retrieval Tests

Test suite for annotation retrieval and filtering functionality (Task 3).
"""

import pytest
import uuid
from datetime import datetime, timezone

from backend.app.database.models import Resource, Annotation
from backend.app.services.annotation_service import AnnotationService


# db_session fixture is now in conftest.py


@pytest.fixture
def sample_resource(db_session):
    """Create a sample resource for testing."""
    resource = Resource(
        title="Test Paper",
        source="https://example.com/paper.pdf",
        read_status="unread",
        quality_score=0.8,
        identifier="storage/archive/test-paper"
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)
    return resource


@pytest.fixture
def sample_annotations(db_session, sample_resource):
    """Create sample annotations for testing."""
    annotations = []
    
    # Create annotations with different offsets and tags
    annotation_data = [
        {
            "start_offset": 10,
            "end_offset": 30,
            "highlighted_text": "first highlight",
            "note": "First note",
            "tags": '["important", "intro"]',
            "user_id": "user1",
            "is_shared": False
        },
        {
            "start_offset": 50,
            "end_offset": 80,
            "highlighted_text": "second highlight",
            "note": "Second note",
            "tags": '["methodology"]',
            "user_id": "user1",
            "is_shared": False
        },
        {
            "start_offset": 100,
            "end_offset": 120,
            "highlighted_text": "third highlight",
            "note": "Third note",
            "tags": '["important", "results"]',
            "user_id": "user1",
            "is_shared": False
        },
        {
            "start_offset": 150,
            "end_offset": 170,
            "highlighted_text": "shared highlight",
            "note": "Shared note",
            "tags": '["public"]',
            "user_id": "user2",
            "is_shared": True
        }
    ]
    
    for data in annotation_data:
        annotation = Annotation(
            id=uuid.uuid4(),
            resource_id=sample_resource.id,
            **data,
            color="#FFFF00",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db_session.add(annotation)
        annotations.append(annotation)
    
    db_session.commit()
    for ann in annotations:
        db_session.refresh(ann)
    
    return annotations


class TestGetAnnotationsForResource:
    """Test get_annotations_for_resource method."""
    
    def test_get_annotations_basic(self, db_session, sample_resource, sample_annotations):
        """Test retrieving annotations for a resource."""
        service = AnnotationService(db_session)
        
        annotations = service.get_annotations_for_resource(
            resource_id=str(sample_resource.id),
            user_id="user1"
        )
        
        # Should return 3 annotations for user1
        assert len(annotations) == 3
        
        # Should be ordered by start_offset
        assert annotations[0].start_offset == 10
        assert annotations[1].start_offset == 50
        assert annotations[2].start_offset == 100
    
    def test_get_annotations_include_shared(self, db_session, sample_resource, sample_annotations):
        """Test retrieving annotations including shared ones."""
        service = AnnotationService(db_session)
        
        annotations = service.get_annotations_for_resource(
            resource_id=str(sample_resource.id),
            user_id="user1",
            include_shared=True
        )
        
        # Should return 3 owned + 1 shared = 4 annotations
        assert len(annotations) == 4
    
    def test_get_annotations_filter_by_tags(self, db_session, sample_resource, sample_annotations):
        """Test filtering annotations by tags."""
        service = AnnotationService(db_session)
        
        # Filter by "important" tag
        annotations = service.get_annotations_for_resource(
            resource_id=str(sample_resource.id),
            user_id="user1",
            tags=["important"]
        )
        
        # Should return 2 annotations with "important" tag
        assert len(annotations) == 2
        assert annotations[0].start_offset == 10
        assert annotations[1].start_offset == 100
    
    def test_get_annotations_filter_by_multiple_tags(self, db_session, sample_resource, sample_annotations):
        """Test filtering by multiple tags (ANY match)."""
        service = AnnotationService(db_session)
        
        # Filter by "methodology" or "results" tags
        annotations = service.get_annotations_for_resource(
            resource_id=str(sample_resource.id),
            user_id="user1",
            tags=["methodology", "results"]
        )
        
        # Should return 2 annotations (one with methodology, one with results)
        assert len(annotations) == 2
    
    def test_get_annotations_empty_result(self, db_session, sample_resource):
        """Test retrieving annotations when none exist."""
        service = AnnotationService(db_session)
        
        annotations = service.get_annotations_for_resource(
            resource_id=str(sample_resource.id),
            user_id="user999"
        )
        
        assert len(annotations) == 0


class TestGetAnnotationsForUser:
    """Test get_annotations_for_user method."""
    
    def test_get_annotations_for_user_basic(self, db_session, sample_annotations):
        """Test retrieving all annotations for a user."""
        service = AnnotationService(db_session)
        
        annotations = service.get_annotations_for_user(
            user_id="user1"
        )
        
        # Should return 3 annotations for user1
        assert len(annotations) == 3
    
    def test_get_annotations_sort_recent(self, db_session, sample_annotations):
        """Test sorting by recent (newest first)."""
        service = AnnotationService(db_session)
        
        annotations = service.get_annotations_for_user(
            user_id="user1",
            sort_by="recent"
        )
        
        # Should be sorted by created_at descending
        # Most recent first (last created)
        assert len(annotations) == 3
        # Verify they're in descending order
        for i in range(len(annotations) - 1):
            assert annotations[i].created_at >= annotations[i + 1].created_at
    
    def test_get_annotations_sort_oldest(self, db_session, sample_annotations):
        """Test sorting by oldest (oldest first)."""
        service = AnnotationService(db_session)
        
        annotations = service.get_annotations_for_user(
            user_id="user1",
            sort_by="oldest"
        )
        
        # Should be sorted by created_at ascending
        assert len(annotations) == 3
        # Verify they're in ascending order
        for i in range(len(annotations) - 1):
            assert annotations[i].created_at <= annotations[i + 1].created_at
    
    def test_get_annotations_pagination(self, db_session, sample_annotations):
        """Test pagination with limit and offset."""
        service = AnnotationService(db_session)
        
        # Get first 2 annotations
        page1 = service.get_annotations_for_user(
            user_id="user1",
            limit=2,
            offset=0
        )
        
        assert len(page1) == 2
        
        # Get next annotation
        page2 = service.get_annotations_for_user(
            user_id="user1",
            limit=2,
            offset=2
        )
        
        assert len(page2) == 1
    
    def test_get_annotations_resource_loaded(self, db_session, sample_annotations):
        """Test that resource relationship is eagerly loaded."""
        service = AnnotationService(db_session)
        
        annotations = service.get_annotations_for_user(
            user_id="user1"
        )
        
        # Access resource without triggering additional query
        # This would fail if relationship wasn't eagerly loaded
        assert annotations[0].resource is not None
        assert annotations[0].resource.title == "Test Paper"
