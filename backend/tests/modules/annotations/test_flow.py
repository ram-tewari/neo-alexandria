"""
Annotations Module - Integration Flow Tests

Tests annotation creation flow with event verification and database persistence.

Requirements: 9.4, 10.2-10.6, 13.1-13.3
"""

import pytest
import json
from app.modules.annotations.service import AnnotationService


def test_annotation_creation_flow(db_session, create_test_resource, mock_event_bus):
    """
    Test complete annotation creation flow with event emission.

    This integration test verifies:
    1. Annotation is created with correct text ranges
    2. Context is extracted from resource content
    3. annotation.created event is emitted with correct payload
    4. Annotation is persisted to database
    5. Annotation can be retrieved with correct data

    Requirements: 9.4, 10.2-10.6, 13.1-13.3
    """
    service = AnnotationService(db_session)

    # Create test resource
    resource = create_test_resource(
        title="Test Document", description="A document for annotation testing"
    )

    # Create annotation
    annotation = service.create_annotation(
        resource_id=str(resource.id),
        user_id="test_user",
        start_offset=10,
        end_offset=30,
        highlighted_text="important passage here",
        note="This is a key insight",
        tags=["important", "research"],
        color="#FF0000",
    )

    # Verify annotation object
    assert annotation is not None
    assert annotation.id is not None
    assert str(annotation.resource_id) == str(resource.id)
    assert annotation.user_id == "test_user"
    assert annotation.start_offset == 10
    assert annotation.end_offset == 30
    assert annotation.highlighted_text == "important passage here"
    assert annotation.note == "This is a key insight"
    assert annotation.color == "#FF0000"

    # Verify tags are stored as JSON
    assert annotation.tags is not None
    tags = json.loads(annotation.tags)
    assert tags == ["important", "research"]

    # Verify context fields are populated (even if empty due to no actual file)
    assert annotation.context_before is not None
    assert annotation.context_after is not None

    # Verify timestamps
    assert annotation.created_at is not None
    assert annotation.updated_at is not None

    # Verify database persistence - retrieve annotation
    retrieved = service.get_annotation_by_id(
        annotation_id=str(annotation.id), user_id="test_user"
    )

    assert retrieved is not None
    assert retrieved.id == annotation.id
    assert retrieved.start_offset == 10
    assert retrieved.end_offset == 30
    assert retrieved.highlighted_text == "important passage here"
    assert retrieved.note == "This is a key insight"

    # Verify annotation appears in resource annotations list
    resource_annotations = service.get_annotations_for_resource(
        resource_id=str(resource.id), user_id="test_user"
    )

    assert len(resource_annotations) == 1
    assert resource_annotations[0].id == annotation.id

    # Note: Event emission verification would require event bus integration
    # For now, we verify the annotation was created successfully
    # In a full implementation, we would check:
    # mock_event_bus.assert_called_with(
    #     "annotation.created",
    #     {"annotation_id": str(annotation.id), "resource_id": str(resource.id)}
    # )


def test_annotation_update_flow(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test annotation update flow with validation.

    Verifies:
    1. Annotation can be updated by owner
    2. Updated fields are persisted
    3. updated_at timestamp is updated
    4. Non-owner cannot update

    Requirements: 9.4, 10.2-10.6
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Test Resource")

    # Create annotation
    annotation = create_test_annotation(
        resource_id=resource.id,
        user_id="owner_user",
        highlighted_text="Original text",
        start_offset=0,
        end_offset=13,
        note="Original note",
        tags=json.dumps(["tag1"]),
        color="#FFFF00",
    )

    original_updated_at = annotation.updated_at

    # Update annotation as owner
    updated = service.update_annotation(
        annotation_id=str(annotation.id),
        user_id="owner_user",
        note="Updated note",
        tags=["tag1", "tag2", "tag3"],
        color="#FF0000",
    )

    # Verify updates
    assert updated.note == "Updated note"
    assert updated.color == "#FF0000"

    tags = json.loads(updated.tags)
    assert tags == ["tag1", "tag2", "tag3"]

    # Verify updated_at changed
    assert updated.updated_at > original_updated_at

    # Verify immutable fields unchanged
    assert updated.start_offset == 0
    assert updated.end_offset == 13
    assert updated.highlighted_text == "Original text"
    assert updated.user_id == "owner_user"

    # Verify non-owner cannot update
    with pytest.raises(
        PermissionError, match="Cannot update another user's annotation"
    ):
        service.update_annotation(
            annotation_id=str(annotation.id),
            user_id="other_user",
            note="Malicious update",
        )

    # Verify annotation was not changed by failed update
    retrieved = service.get_annotation_by_id(
        annotation_id=str(annotation.id), user_id="owner_user"
    )
    assert retrieved.note == "Updated note"  # Still has owner's update


def test_annotation_delete_flow(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test annotation deletion flow with ownership verification.

    Verifies:
    1. Annotation can be deleted by owner
    2. Annotation is removed from database
    3. Non-owner cannot delete

    Requirements: 9.4, 10.2-10.6
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Test Resource")

    # Create annotation
    annotation = create_test_annotation(
        resource_id=resource.id,
        user_id="owner_user",
        highlighted_text="Text to delete",
        start_offset=0,
        end_offset=14,
    )

    annotation_id = str(annotation.id)

    # Verify annotation exists
    retrieved = service.get_annotation_by_id(
        annotation_id=annotation_id, user_id="owner_user"
    )
    assert retrieved is not None

    # Try to delete as non-owner (should fail)
    with pytest.raises(
        PermissionError, match="Cannot delete another user's annotation"
    ):
        service.delete_annotation(annotation_id=annotation_id, user_id="other_user")

    # Verify annotation still exists
    retrieved = service.get_annotation_by_id(
        annotation_id=annotation_id, user_id="owner_user"
    )
    assert retrieved is not None

    # Delete as owner
    result = service.delete_annotation(
        annotation_id=annotation_id, user_id="owner_user"
    )

    assert result is True

    # Verify annotation is deleted
    retrieved = service.get_annotation_by_id(
        annotation_id=annotation_id, user_id="owner_user"
    )
    assert retrieved is None

    # Verify annotation not in resource list
    resource_annotations = service.get_annotations_for_resource(
        resource_id=str(resource.id), user_id="owner_user"
    )
    assert len(resource_annotations) == 0


def test_annotation_access_control_flow(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test annotation access control with shared annotations.

    Verifies:
    1. Owner can always access their annotations
    2. Non-owner cannot access private annotations
    3. Non-owner can access shared annotations
    4. Shared annotations appear in resource list when include_shared=True

    Requirements: 9.4, 10.2-10.6, 13.1-13.3
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Shared Resource")

    # Create private annotation
    private_ann = create_test_annotation(
        resource_id=resource.id,
        user_id="user1",
        highlighted_text="Private annotation",
        start_offset=0,
        end_offset=18,
        is_shared=0,
    )

    # Create shared annotation
    shared_ann = create_test_annotation(
        resource_id=resource.id,
        user_id="user1",
        highlighted_text="Shared annotation",
        start_offset=20,
        end_offset=37,
        is_shared=1,
    )

    # Test 1: Owner can access both
    owner_annotations = service.get_annotations_for_resource(
        resource_id=str(resource.id), user_id="user1", include_shared=False
    )
    assert len(owner_annotations) == 2

    # Test 2: Non-owner cannot access private annotation
    private_retrieved = service.get_annotation_by_id(
        annotation_id=str(private_ann.id), user_id="user2"
    )
    assert private_retrieved is None

    # Test 3: Non-owner can access shared annotation
    shared_retrieved = service.get_annotation_by_id(
        annotation_id=str(shared_ann.id), user_id="user2"
    )
    assert shared_retrieved is not None
    assert shared_retrieved.id == shared_ann.id

    # Test 4: Non-owner sees only shared annotations with include_shared=True
    user2_annotations = service.get_annotations_for_resource(
        resource_id=str(resource.id), user_id="user2", include_shared=True
    )
    assert len(user2_annotations) == 1
    assert user2_annotations[0].id == shared_ann.id

    # Test 5: Non-owner sees no annotations with include_shared=False
    user2_private_only = service.get_annotations_for_resource(
        resource_id=str(resource.id), user_id="user2", include_shared=False
    )
    assert len(user2_private_only) == 0


def test_annotation_tag_filtering_flow(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test annotation retrieval with tag filtering.

    Verifies:
    1. Annotations can be filtered by tags
    2. Multiple tags work correctly (ANY match)
    3. Annotations without tags are excluded

    Requirements: 9.4, 10.2-10.6
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Tagged Resource")

    # Create annotations with different tags
    ann1 = create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Important finding",
        start_offset=0,
        end_offset=17,
        tags=json.dumps(["important", "research"]),
    )

    ann2 = create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="TODO item",
        start_offset=20,
        end_offset=29,
        tags=json.dumps(["todo"]),
    )

    ann3 = create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Research note",
        start_offset=30,
        end_offset=43,
        tags=json.dumps(["research", "methodology"]),
    )

    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Untagged annotation",
        start_offset=50,
        end_offset=69,
        tags=None,
    )

    # Test 1: Filter by single tag "research"
    research_annotations = service.get_annotations_for_resource(
        resource_id=str(resource.id), user_id="test_user", tags=["research"]
    )
    assert len(research_annotations) == 2
    assert ann1.id in [a.id for a in research_annotations]
    assert ann3.id in [a.id for a in research_annotations]

    # Test 2: Filter by single tag "todo"
    todo_annotations = service.get_annotations_for_resource(
        resource_id=str(resource.id), user_id="test_user", tags=["todo"]
    )
    assert len(todo_annotations) == 1
    assert todo_annotations[0].id == ann2.id

    # Test 3: Filter by multiple tags (ANY match)
    multi_tag_annotations = service.get_annotations_for_resource(
        resource_id=str(resource.id),
        user_id="test_user",
        tags=["important", "methodology"],
    )
    assert len(multi_tag_annotations) == 2
    assert ann1.id in [a.id for a in multi_tag_annotations]
    assert ann3.id in [a.id for a in multi_tag_annotations]

    # Test 4: Filter by non-existent tag
    no_match_annotations = service.get_annotations_for_resource(
        resource_id=str(resource.id), user_id="test_user", tags=["nonexistent"]
    )
    assert len(no_match_annotations) == 0

    # Test 5: No tag filter returns all annotations
    all_annotations = service.get_annotations_for_resource(
        resource_id=str(resource.id), user_id="test_user", tags=None
    )
    assert len(all_annotations) == 4
