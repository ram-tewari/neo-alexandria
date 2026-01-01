"""
Annotations Module - Text Range Edge Cases

Tests precise text range storage, overlapping annotations, and validation.

Requirements: 9.1, 9.2, 9.3
"""

import pytest
from app.modules.annotations.service import AnnotationService


def test_precise_text_range_storage(db_session, create_test_resource):
    """
    Test precise text range storage with boundary conditions.
    
    Edge cases:
    - Zero-length selection (start == end - 1)
    - Start of document (offset 0)
    - End of document
    - Multi-line selections
    
    Requirements: 9.1, 9.2
    """
    service = AnnotationService(db_session)
    
    # Create resource with known content
    resource = create_test_resource(
        title="Test Document",
        identifier="test_doc"
    )
    
    # Test case 1: Single character at start of document
    annotation1 = service.create_annotation(
        resource_id=str(resource.id),
        user_id="test_user",
        start_offset=0,
        end_offset=1,
        highlighted_text="T"
    )
    
    assert annotation1.start_offset == 0
    assert annotation1.end_offset == 1
    assert annotation1.highlighted_text == "T"
    
    # Test case 2: Multi-character selection
    annotation2 = service.create_annotation(
        resource_id=str(resource.id),
        user_id="test_user",
        start_offset=10,
        end_offset=25,
        highlighted_text="sample text here"
    )
    
    assert annotation2.start_offset == 10
    assert annotation2.end_offset == 25
    assert annotation2.highlighted_text == "sample text here"
    
    # Test case 3: Large offset values (end of long document)
    annotation3 = service.create_annotation(
        resource_id=str(resource.id),
        user_id="test_user",
        start_offset=10000,
        end_offset=10050,
        highlighted_text="text at end of document"
    )
    
    assert annotation3.start_offset == 10000
    assert annotation3.end_offset == 10050
    
    # Verify all annotations are stored correctly
    annotations = service.get_annotations_for_resource(
        resource_id=str(resource.id),
        user_id="test_user"
    )
    
    assert len(annotations) == 3
    # Verify they're ordered by start_offset
    assert annotations[0].start_offset == 0
    assert annotations[1].start_offset == 10
    assert annotations[2].start_offset == 10000


def test_overlapping_annotations(db_session, create_test_resource):
    """
    Test that overlapping annotations are allowed and stored correctly.
    
    The system should allow multiple annotations on the same text range,
    as users may want to highlight the same passage with different notes.
    
    Edge cases:
    - Partial overlap
    - Complete overlap (same range)
    - Nested annotations (one inside another)
    
    Requirements: 9.2, 9.3
    """
    service = AnnotationService(db_session)
    
    resource = create_test_resource(title="Overlap Test")
    
    # Create first annotation
    service.create_annotation(
        resource_id=str(resource.id),
        user_id="test_user",
        start_offset=0,
        end_offset=20,
        highlighted_text="The quick brown fox",
        note="First annotation"
    )
    
    # Create overlapping annotation (partial overlap)
    service.create_annotation(
        resource_id=str(resource.id),
        user_id="test_user",
        start_offset=10,
        end_offset=30,
        highlighted_text="brown fox jumps over",
        note="Overlapping annotation"
    )
    
    # Create nested annotation (completely inside first)
    service.create_annotation(
        resource_id=str(resource.id),
        user_id="test_user",
        start_offset=4,
        end_offset=9,
        highlighted_text="quick",
        note="Nested annotation"
    )
    
    # Create exact duplicate range (same offsets, different note)
    service.create_annotation(
        resource_id=str(resource.id),
        user_id="test_user",
        start_offset=0,
        end_offset=20,
        highlighted_text="The quick brown fox",
        note="Duplicate range with different note"
    )
    
    # Verify all annotations are stored
    annotations = service.get_annotations_for_resource(
        resource_id=str(resource.id),
        user_id="test_user"
    )
    
    assert len(annotations) == 4
    
    # Verify they're ordered by start_offset
    assert annotations[0].start_offset == 0
    assert annotations[1].start_offset == 0
    assert annotations[2].start_offset == 4
    assert annotations[3].start_offset == 10
    
    # Verify each has unique ID
    ids = [ann.id for ann in annotations]
    assert len(set(ids)) == 4
    
    # Verify notes are preserved
    notes = [ann.note for ann in annotations]
    assert "First annotation" in notes
    assert "Overlapping annotation" in notes
    assert "Nested annotation" in notes
    assert "Duplicate range with different note" in notes


def test_invalid_text_range(db_session, create_test_resource):
    """
    Test validation of invalid text ranges.
    
    Should reject:
    - start_offset >= end_offset
    - Negative offsets
    - Invalid resource_id format
    
    Requirements: 9.1, 9.3
    """
    service = AnnotationService(db_session)
    
    resource = create_test_resource(title="Validation Test")
    
    # Test case 1: start_offset >= end_offset
    with pytest.raises(ValueError, match="start_offset must be less than end_offset"):
        service.create_annotation(
            resource_id=str(resource.id),
            user_id="test_user",
            start_offset=10,
            end_offset=10,  # Equal to start
            highlighted_text="invalid"
        )
    
    with pytest.raises(ValueError, match="start_offset must be less than end_offset"):
        service.create_annotation(
            resource_id=str(resource.id),
            user_id="test_user",
            start_offset=20,
            end_offset=10,  # Less than start
            highlighted_text="invalid"
        )
    
    # Test case 2: Negative offsets
    with pytest.raises(ValueError, match="Offsets must be non-negative"):
        service.create_annotation(
            resource_id=str(resource.id),
            user_id="test_user",
            start_offset=-5,
            end_offset=10,
            highlighted_text="invalid"
        )
    
    with pytest.raises(ValueError, match="Offsets must be non-negative"):
        service.create_annotation(
            resource_id=str(resource.id),
            user_id="test_user",
            start_offset=0,
            end_offset=-1,
            highlighted_text="invalid"
        )
    
    # Test case 3: Invalid resource_id format
    with pytest.raises(ValueError, match="Invalid resource_id format"):
        service.create_annotation(
            resource_id="not-a-uuid",
            user_id="test_user",
            start_offset=0,
            end_offset=10,
            highlighted_text="invalid"
        )
    
    # Test case 4: Non-existent resource
    with pytest.raises(ValueError, match="Resource not found"):
        service.create_annotation(
            resource_id="00000000-0000-0000-0000-000000000000",
            user_id="test_user",
            start_offset=0,
            end_offset=10,
            highlighted_text="invalid"
        )
    
    # Verify no annotations were created
    annotations = service.get_annotations_for_resource(
        resource_id=str(resource.id),
        user_id="test_user"
    )
    
    assert len(annotations) == 0
