"""
Annotations Module - Export Tests

Tests Markdown and JSON export functionality.

Requirements: 1.5, 1.7
"""

import pytest
import json
from datetime import datetime
from app.modules.annotations.service import AnnotationService


def test_markdown_export_single_resource(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test Markdown export for a single resource.

    Verifies:
    1. Markdown format is correct
    2. Resource title is included
    3. Annotations are formatted properly
    4. Tags and notes are included
    5. Timestamps are formatted

    Requirements: 1.5
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(
        title="Machine Learning Fundamentals", identifier="ml-fundamentals"
    )

    # Create annotations
    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Neural networks are powerful",
        start_offset=0,
        end_offset=28,
        note="Key concept for deep learning",
        tags=json.dumps(["important", "neural-networks"]),
        color="#FF0000",
    )

    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Backpropagation algorithm",
        start_offset=50,
        end_offset=75,
        note="Core training mechanism",
        tags=json.dumps(["algorithm", "training"]),
        color="#00FF00",
    )

    # Export to Markdown
    markdown = service.export_annotations_markdown(
        user_id="test_user", resource_id=str(resource.id)
    )

    # Verify structure
    assert "# Annotations Export" in markdown
    assert "Machine Learning Fundamentals" in markdown
    assert "Neural networks are powerful" in markdown
    assert "Key concept for deep learning" in markdown
    assert "important" in markdown
    assert "neural-networks" in markdown
    assert "Backpropagation algorithm" in markdown
    assert "Core training mechanism" in markdown
    assert "algorithm" in markdown
    assert "training" in markdown

    # Verify formatting (actual format uses ## for resource title, not "## Resource:")
    assert "##" in markdown  # Resource title uses ##
    assert "**Note:**" in markdown
    assert "**Tags:**" in markdown
    assert "*Created:" in markdown


def test_markdown_export_multiple_resources(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test Markdown export across multiple resources.

    Verifies that annotations are grouped by resource.

    Requirements: 1.5
    """
    service = AnnotationService(db_session)

    # Create two resources
    resource1 = create_test_resource(title="Resource 1")
    resource2 = create_test_resource(title="Resource 2")

    # Create annotations for each resource
    create_test_annotation(
        resource_id=resource1.id,
        user_id="test_user",
        highlighted_text="Content from resource 1",
        start_offset=0,
        end_offset=23,
        note="Note 1",
    )

    create_test_annotation(
        resource_id=resource2.id,
        user_id="test_user",
        highlighted_text="Content from resource 2",
        start_offset=0,
        end_offset=23,
        note="Note 2",
    )

    # Export all annotations
    markdown = service.export_annotations_markdown(user_id="test_user")

    # Verify both resources are included
    assert "Resource 1" in markdown
    assert "Resource 2" in markdown
    assert "Content from resource 1" in markdown
    assert "Content from resource 2" in markdown
    assert "Note 1" in markdown
    assert "Note 2" in markdown

    # Verify resource grouping (Resource 1 should appear before its content)
    resource1_pos = markdown.index("Resource 1")
    content1_pos = markdown.index("Content from resource 1")
    assert resource1_pos < content1_pos

    resource2_pos = markdown.index("Resource 2")
    content2_pos = markdown.index("Content from resource 2")
    assert resource2_pos < content2_pos


def test_markdown_export_no_annotations(db_session, create_test_resource):
    """
    Test Markdown export when user has no annotations.

    Requirements: 1.5
    """
    service = AnnotationService(db_session)

    markdown = service.export_annotations_markdown(user_id="test_user")

    # Should return header with no content
    assert "# Annotations Export" in markdown
    assert len(markdown.split("\n")) < 10  # Minimal content


def test_markdown_export_without_tags(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test Markdown export for annotations without tags.

    Requirements: 1.5
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Test Resource")

    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Content without tags",
        start_offset=0,
        end_offset=20,
        note="Note without tags",
        tags=None,
    )

    markdown = service.export_annotations_markdown(
        user_id="test_user", resource_id=str(resource.id)
    )

    # Should not have tags section or should show empty
    assert "Content without tags" in markdown
    assert "Note without tags" in markdown


def test_markdown_export_without_note(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test Markdown export for annotations without notes.

    Requirements: 1.5
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Test Resource")

    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Content without note",
        start_offset=0,
        end_offset=20,
        note=None,
        tags=json.dumps(["tag1"]),
    )

    markdown = service.export_annotations_markdown(
        user_id="test_user", resource_id=str(resource.id)
    )

    # Should include highlight but not note section
    assert "Content without note" in markdown
    assert "tag1" in markdown


def test_json_export_single_resource(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test JSON export for a single resource.

    Verifies:
    1. JSON structure is correct
    2. All fields are included
    3. Metadata is complete
    4. Resource information is included

    Requirements: 1.7
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Test Resource", type="article")

    # Create annotation
    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Test highlight",
        start_offset=10,
        end_offset=24,
        note="Test note",
        tags=json.dumps(["tag1", "tag2"]),
        color="#FF0000",
        is_shared=1,
    )

    # Export to JSON
    json_data = service.export_annotations_json(
        user_id="test_user", resource_id=str(resource.id)
    )

    # Verify structure
    assert isinstance(json_data, list)
    assert len(json_data) == 1

    exported = json_data[0]

    # Verify all fields are present
    assert "id" in exported
    assert "resource_id" in exported
    assert "user_id" in exported
    assert "start_offset" in exported
    assert "end_offset" in exported
    assert "highlighted_text" in exported
    assert "note" in exported
    assert "tags" in exported
    assert "color" in exported
    assert "context_before" in exported
    assert "context_after" in exported
    assert "is_shared" in exported
    assert "collection_ids" in exported
    assert "created_at" in exported
    assert "updated_at" in exported
    assert "resource" in exported

    # Verify values
    assert exported["user_id"] == "test_user"
    assert exported["start_offset"] == 10
    assert exported["end_offset"] == 24
    assert exported["highlighted_text"] == "Test highlight"
    assert exported["note"] == "Test note"
    assert exported["tags"] == ["tag1", "tag2"]
    assert exported["color"] == "#FF0000"
    assert exported["is_shared"] == 1  # Stored as integer in database

    # Verify resource metadata
    assert exported["resource"] is not None
    assert exported["resource"]["title"] == "Test Resource"
    assert exported["resource"]["type"] == "article"

    # Verify timestamps are ISO format
    assert "T" in exported["created_at"]
    assert "T" in exported["updated_at"]


def test_json_export_multiple_resources(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test JSON export across multiple resources.

    Requirements: 1.7
    """
    service = AnnotationService(db_session)

    # Create two resources
    resource1 = create_test_resource(title="Resource 1")
    resource2 = create_test_resource(title="Resource 2")

    # Create annotations
    create_test_annotation(
        resource_id=resource1.id,
        user_id="test_user",
        highlighted_text="Highlight 1",
        start_offset=0,
        end_offset=11,
        note="Note 1",
    )

    create_test_annotation(
        resource_id=resource2.id,
        user_id="test_user",
        highlighted_text="Highlight 2",
        start_offset=0,
        end_offset=11,
        note="Note 2",
    )

    # Export all annotations
    json_data = service.export_annotations_json(user_id="test_user")

    # Verify both annotations are included
    assert len(json_data) == 2

    # Verify resource information
    resource_titles = {item["resource"]["title"] for item in json_data}
    assert "Resource 1" in resource_titles
    assert "Resource 2" in resource_titles


def test_json_export_no_annotations(db_session):
    """
    Test JSON export when user has no annotations.

    Requirements: 1.7
    """
    service = AnnotationService(db_session)

    json_data = service.export_annotations_json(user_id="test_user")

    # Should return empty list
    assert isinstance(json_data, list)
    assert len(json_data) == 0


def test_json_export_user_isolation(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test that JSON export only includes annotations for the requesting user.

    Requirements: 1.7
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Shared Resource")

    # Create annotations for different users
    create_test_annotation(
        resource_id=resource.id,
        user_id="user1",
        highlighted_text="User 1 highlight",
        start_offset=0,
        end_offset=16,
    )

    create_test_annotation(
        resource_id=resource.id,
        user_id="user2",
        highlighted_text="User 2 highlight",
        start_offset=20,
        end_offset=36,
    )

    # Export as user1
    json_data_user1 = service.export_annotations_json(user_id="user1")

    assert len(json_data_user1) == 1
    assert json_data_user1[0]["user_id"] == "user1"

    # Export as user2
    json_data_user2 = service.export_annotations_json(user_id="user2")

    assert len(json_data_user2) == 1
    assert json_data_user2[0]["user_id"] == "user2"


def test_json_export_ordering(db_session, create_test_resource, create_test_annotation):
    """
    Test that JSON export returns annotations in descending created_at order.

    Requirements: 1.7
    """
    import time

    service = AnnotationService(db_session)

    resource = create_test_resource(title="Test Resource")

    # Create annotations in sequence with delays to ensure different timestamps
    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="First",
        start_offset=0,
        end_offset=5,
    )
    time.sleep(0.1)  # Larger delay to ensure different timestamp

    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Second",
        start_offset=10,
        end_offset=16,
    )
    time.sleep(0.1)  # Larger delay to ensure different timestamp

    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Third",
        start_offset=20,
        end_offset=25,
    )

    # Export
    json_data = service.export_annotations_json(user_id="test_user")

    # Verify we have 3 annotations
    assert len(json_data) == 3

    # Verify they are ordered by created_at descending (most recent first)
    # Parse timestamps to verify ordering
    timestamps = [datetime.fromisoformat(item["created_at"]) for item in json_data]

    # Verify timestamps are in descending order
    for i in range(len(timestamps) - 1):
        assert timestamps[i] >= timestamps[i + 1], (
            "Timestamps should be in descending order"
        )


def test_json_export_invalid_resource_id(db_session):
    """
    Test JSON export with invalid resource_id format.

    Requirements: 1.7
    """
    service = AnnotationService(db_session)

    with pytest.raises(ValueError, match="Invalid resource_id format"):
        service.export_annotations_json(user_id="test_user", resource_id="not-a-uuid")


def test_export_performance(db_session, create_test_resource, create_test_annotation):
    """
    Test that export completes within performance requirements.

    Target: <2s for 1,000 annotations

    Requirements: 1.5
    """
    import time

    service = AnnotationService(db_session)

    resource = create_test_resource(title="Performance Test")

    # Create 100 annotations (scaled down for test speed)
    for i in range(100):
        create_test_annotation(
            resource_id=resource.id,
            user_id="test_user",
            highlighted_text=f"Highlight {i}",
            start_offset=i * 100,
            end_offset=i * 100 + 20,
            note=f"Note {i}",
            tags=json.dumps([f"tag{i}"]),
        )

    # Test Markdown export performance
    start_time = time.time()
    markdown = service.export_annotations_markdown(user_id="test_user")
    markdown_time = time.time() - start_time

    # Should complete quickly (scaled: 100 annotations in <0.2s)
    assert markdown_time < 0.2, f"Markdown export took {markdown_time}s"
    assert len(markdown) > 0

    # Test JSON export performance
    start_time = time.time()
    json_data = service.export_annotations_json(user_id="test_user")
    json_time = time.time() - start_time

    # Should complete quickly (scaled: 100 annotations in <0.2s)
    assert json_time < 0.2, f"JSON export took {json_time}s"
    assert len(json_data) == 100
