"""
Neo Alexandria 2.0 - Annotation Export Tests

Test suite for annotation export functionality (Task 5).
"""

import pytest
import uuid
from datetime import datetime, timezone

from backend.app.database.models import Resource, Annotation
from backend.app.services.annotation_service import AnnotationService


# db_session fixture is now in conftest.py


@pytest.fixture
def sample_resources(db_session):
    """Create sample resources for testing."""
    resources = []
    
    resource_data = [
        {
            "title": "Machine Learning Basics",
            "source": "https://example.com/ml-basics.pdf",
            "identifier": "storage/archive/ml-basics"
        },
        {
            "title": "Deep Learning Advanced",
            "source": "https://example.com/dl-advanced.pdf",
            "identifier": "storage/archive/dl-advanced"
        }
    ]
    
    for data in resource_data:
        resource = Resource(
            **data,
            read_status="unread",
            quality_score=0.8
        )
        db_session.add(resource)
        resources.append(resource)
    
    db_session.commit()
    for res in resources:
        db_session.refresh(res)
    
    return resources


@pytest.fixture
def sample_annotations(db_session, sample_resources):
    """Create sample annotations for testing export."""
    annotations = []
    
    # Annotations for first resource
    annotation_data = [
        {
            "resource_id": sample_resources[0].id,
            "start_offset": 10,
            "end_offset": 30,
            "highlighted_text": "machine learning is powerful",
            "note": "Key insight about ML capabilities",
            "tags": '["important", "intro"]',
            "color": "#FFFF00",
            "user_id": "user1"
        },
        {
            "resource_id": sample_resources[0].id,
            "start_offset": 50,
            "end_offset": 80,
            "highlighted_text": "supervised learning methods",
            "note": "Different types of supervised learning",
            "tags": '["methodology", "supervised"]',
            "color": "#00FF00",
            "user_id": "user1"
        },
        # Annotations for second resource
        {
            "resource_id": sample_resources[1].id,
            "start_offset": 100,
            "end_offset": 130,
            "highlighted_text": "neural networks architecture",
            "note": "Deep dive into NN structure",
            "tags": '["architecture", "important"]',
            "color": "#FF0000",
            "user_id": "user1"
        }
    ]
    
    for data in annotation_data:
        annotation = Annotation(
            id=uuid.uuid4(),
            **data,
            is_shared=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db_session.add(annotation)
        annotations.append(annotation)
    
    db_session.commit()
    for ann in annotations:
        db_session.refresh(ann)
    
    return annotations


class TestExportAnnotationsMarkdown:
    """Test export_annotations_markdown method."""
    
    def test_export_all_annotations(self, db_session, sample_annotations):
        """Test exporting all annotations to Markdown."""
        service = AnnotationService(db_session)
        
        markdown = service.export_annotations_markdown(user_id="user1")
        
        # Verify markdown structure
        assert "# Annotations Export" in markdown
        assert "## Machine Learning Basics" in markdown
        assert "## Deep Learning Advanced" in markdown
        
        # Verify annotation content
        assert "> machine learning is powerful" in markdown
        assert "**Note:** Key insight about ML capabilities" in markdown
        assert "`important`" in markdown
        assert "`intro`" in markdown
        
        # Verify all annotations are present
        assert "> supervised learning methods" in markdown
        assert "> neural networks architecture" in markdown
    
    def test_export_single_resource(self, db_session, sample_resources, sample_annotations):
        """Test exporting annotations for a single resource."""
        service = AnnotationService(db_session)
        
        markdown = service.export_annotations_markdown(
            user_id="user1",
            resource_id=str(sample_resources[0].id)
        )
        
        # Should only include first resource
        assert "## Machine Learning Basics" in markdown
        assert "## Deep Learning Advanced" not in markdown
        
        # Should include annotations from first resource
        assert "> machine learning is powerful" in markdown
        assert "> supervised learning methods" in markdown
        
        # Should not include annotations from second resource
        assert "> neural networks architecture" not in markdown
    
    def test_export_with_colors(self, db_session, sample_annotations):
        """Test that non-default colors are included in export."""
        service = AnnotationService(db_session)
        
        markdown = service.export_annotations_markdown(user_id="user1")
        
        # Non-default colors should be included
        assert "**Color:** #00FF00" in markdown
        assert "**Color:** #FF0000" in markdown
    
    def test_export_with_timestamps(self, db_session, sample_annotations):
        """Test that timestamps are included in export."""
        service = AnnotationService(db_session)
        
        markdown = service.export_annotations_markdown(user_id="user1")
        
        # Should include created timestamps
        assert "*Created:" in markdown
    
    def test_export_empty_annotations(self, db_session):
        """Test exporting when no annotations exist."""
        service = AnnotationService(db_session)
        
        markdown = service.export_annotations_markdown(user_id="nonexistent_user")
        
        assert "# Annotations Export" in markdown
        assert "No annotations found" in markdown
    
    def test_export_annotation_without_note(self, db_session, sample_resources):
        """Test exporting annotation without a note."""
        # Create annotation without note
        annotation = Annotation(
            id=uuid.uuid4(),
            resource_id=sample_resources[0].id,
            user_id="user1",
            start_offset=200,
            end_offset=220,
            highlighted_text="text without note",
            note=None,
            tags=None,
            color="#FFFF00",
            is_shared=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db_session.add(annotation)
        db_session.commit()
        
        service = AnnotationService(db_session)
        markdown = service.export_annotations_markdown(user_id="user1")
        
        # Should include highlighted text but not note section
        assert "> text without note" in markdown
        # Note section should not appear for this annotation
        lines = markdown.split("\n")
        note_line_idx = None
        for i, line in enumerate(lines):
            if "> text without note" in line:
                # Check next few lines don't have a note
                for j in range(i+1, min(i+5, len(lines))):
                    if "**Note:**" in lines[j]:
                        note_line_idx = j
                        break
                break
        
        # If we found the highlight, verify no note immediately follows
        assert note_line_idx is None or "text without note" not in markdown[max(0, markdown.find("> text without note")):markdown.find("> text without note") + 200]


class TestExportAnnotationsJSON:
    """Test export_annotations_json method."""
    
    def test_export_all_annotations_json(self, db_session, sample_annotations):
        """Test exporting all annotations to JSON."""
        service = AnnotationService(db_session)
        
        json_data = service.export_annotations_json(user_id="user1")
        
        # Should return list of 3 annotations
        assert len(json_data) == 3
        
        # Verify structure of first annotation
        first = json_data[0]
        assert "id" in first
        assert "resource_id" in first
        assert "user_id" in first
        assert "start_offset" in first
        assert "end_offset" in first
        assert "highlighted_text" in first
        assert "note" in first
        assert "tags" in first
        assert "color" in first
        assert "created_at" in first
        assert "updated_at" in first
        assert "resource" in first
        
        # Verify resource metadata is included
        assert first["resource"] is not None
        assert "title" in first["resource"]
    
    def test_export_single_resource_json(self, db_session, sample_resources, sample_annotations):
        """Test exporting annotations for a single resource to JSON."""
        service = AnnotationService(db_session)
        
        json_data = service.export_annotations_json(
            user_id="user1",
            resource_id=str(sample_resources[0].id)
        )
        
        # Should return 2 annotations from first resource
        assert len(json_data) == 2
        
        # All should be from the same resource
        for annotation in json_data:
            assert annotation["resource_id"] == str(sample_resources[0].id)
    
    def test_export_json_tags_parsed(self, db_session, sample_annotations):
        """Test that tags are parsed from JSON string to list."""
        service = AnnotationService(db_session)
        
        json_data = service.export_annotations_json(user_id="user1")
        
        # Find annotation with tags
        for annotation in json_data:
            if annotation["tags"]:
                assert isinstance(annotation["tags"], list)
                break
    
    def test_export_json_collection_ids_parsed(self, db_session, sample_resources):
        """Test that collection_ids are parsed from JSON string to list."""
        # Create annotation with collection_ids
        annotation = Annotation(
            id=uuid.uuid4(),
            resource_id=sample_resources[0].id,
            user_id="user1",
            start_offset=300,
            end_offset=320,
            highlighted_text="test with collections",
            note="Test note",
            tags='["test"]',
            color="#FFFF00",
            collection_ids='["col1", "col2"]',
            is_shared=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db_session.add(annotation)
        db_session.commit()
        
        service = AnnotationService(db_session)
        json_data = service.export_annotations_json(user_id="user1")
        
        # Find the annotation with collection_ids
        found = False
        for annotation in json_data:
            if annotation["collection_ids"]:
                assert isinstance(annotation["collection_ids"], list)
                assert len(annotation["collection_ids"]) == 2
                found = True
                break
        
        assert found, "Should have found annotation with collection_ids"
    
    def test_export_json_empty_result(self, db_session):
        """Test exporting when no annotations exist."""
        service = AnnotationService(db_session)
        
        json_data = service.export_annotations_json(user_id="nonexistent_user")
        
        assert json_data == []
    
    def test_export_json_datetime_serialization(self, db_session, sample_annotations):
        """Test that datetime fields are properly serialized."""
        service = AnnotationService(db_session)
        
        json_data = service.export_annotations_json(user_id="user1")
        
        # Verify datetime fields are ISO format strings
        for annotation in json_data:
            assert isinstance(annotation["created_at"], str)
            assert isinstance(annotation["updated_at"], str)
            # Should be parseable as ISO format
            datetime.fromisoformat(annotation["created_at"])
            datetime.fromisoformat(annotation["updated_at"])
