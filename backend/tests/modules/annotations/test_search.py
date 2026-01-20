"""
Annotations Module - Search Tests

Tests full-text search and tag-based search functionality.

Requirements: 1.2, 1.4
"""

import json
from app.modules.annotations.service import AnnotationService


def test_fulltext_search_basic(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test basic full-text search across notes and highlighted text.

    Verifies:
    1. Search finds matches in notes
    2. Search finds matches in highlighted_text
    3. Results are filtered by user_id
    4. Pagination works correctly

    Requirements: 1.2
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Search Test Resource")

    # Create annotations with searchable content
    ann1 = create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="machine learning algorithms",
        start_offset=0,
        end_offset=27,
        note="This discusses neural networks and deep learning",
    )

    ann2 = create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="data preprocessing steps",
        start_offset=50,
        end_offset=74,
        note="Important for machine learning pipelines",
    )

    ann3 = create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="statistical analysis methods",
        start_offset=100,
        end_offset=128,
        note="Traditional statistics, not ML",
    )

    # Test 1: Search for "machine learning" - should match ann1 and ann2
    results = service.search_annotations_fulltext(
        user_id="test_user", query="machine learning", limit=10
    )

    assert len(results) == 2
    result_ids = [ann.id for ann in results]
    assert ann1.id in result_ids
    assert ann2.id in result_ids

    # Test 2: Search for "neural" - should match ann1 only
    results = service.search_annotations_fulltext(
        user_id="test_user", query="neural", limit=10
    )

    assert len(results) == 1
    assert results[0].id == ann1.id

    # Test 3: Search for "preprocessing" - should match ann2 only
    results = service.search_annotations_fulltext(
        user_id="test_user", query="preprocessing", limit=10
    )

    assert len(results) == 1
    assert results[0].id == ann2.id

    # Test 4: Search for "statistics" - should match ann3 only
    results = service.search_annotations_fulltext(
        user_id="test_user", query="statistics", limit=10
    )

    assert len(results) == 1
    assert results[0].id == ann3.id


def test_fulltext_search_case_insensitive(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test that full-text search is case-insensitive.

    Requirements: 1.2
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Case Test")

    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Python Programming",
        start_offset=0,
        end_offset=18,
        note="Learn PYTHON basics",
    )

    # Test different case variations
    for query in ["python", "PYTHON", "Python", "pYtHoN"]:
        results = service.search_annotations_fulltext(
            user_id="test_user", query=query, limit=10
        )
        assert len(results) == 1, f"Query '{query}' should find the annotation"


def test_fulltext_search_user_isolation(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test that full-text search only returns annotations for the requesting user.

    Requirements: 1.2
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Shared Resource")

    # Create annotations for different users
    create_test_annotation(
        resource_id=resource.id,
        user_id="user1",
        highlighted_text="User 1 content",
        start_offset=0,
        end_offset=14,
        note="User 1 note with keyword",
    )

    create_test_annotation(
        resource_id=resource.id,
        user_id="user2",
        highlighted_text="User 2 content",
        start_offset=20,
        end_offset=34,
        note="User 2 note with keyword",
    )

    # Search as user1
    results_user1 = service.search_annotations_fulltext(
        user_id="user1", query="keyword", limit=10
    )

    assert len(results_user1) == 1
    assert results_user1[0].user_id == "user1"

    # Search as user2
    results_user2 = service.search_annotations_fulltext(
        user_id="user2", query="keyword", limit=10
    )

    assert len(results_user2) == 1
    assert results_user2[0].user_id == "user2"


def test_fulltext_search_pagination(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test limit parameter in full-text search.

    Requirements: 1.2
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Pagination Test")

    # Create 10 annotations with the same keyword
    for i in range(10):
        create_test_annotation(
            resource_id=resource.id,
            user_id="test_user",
            highlighted_text=f"Content {i}",
            start_offset=i * 100,
            end_offset=i * 100 + 20,
            note=f"Note {i} with keyword",
        )

    # Test limit=5 returns exactly 5 results
    results_limited = service.search_annotations_fulltext(
        user_id="test_user", query="keyword", limit=5
    )

    assert len(results_limited) == 5

    # Test limit=10 returns all 10 results
    results_all = service.search_annotations_fulltext(
        user_id="test_user", query="keyword", limit=10
    )

    assert len(results_all) == 10

    # Test limit=20 returns only 10 results (all available)
    results_over = service.search_annotations_fulltext(
        user_id="test_user", query="keyword", limit=20
    )

    assert len(results_over) == 10


def test_fulltext_search_empty_query(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test full-text search with empty query returns no results.

    Requirements: 1.2
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Empty Query Test")

    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Some content",
        start_offset=0,
        end_offset=12,
        note="Some note",
    )

    results = service.search_annotations_fulltext(
        user_id="test_user", query="", limit=10
    )

    assert len(results) == 0


def test_fulltext_search_no_matches(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test full-text search with no matches returns empty list.

    Requirements: 1.2
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="No Match Test")

    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Python programming",
        start_offset=0,
        end_offset=18,
        note="Learn Python",
    )

    results = service.search_annotations_fulltext(
        user_id="test_user", query="javascript", limit=10
    )

    assert len(results) == 0


def test_tag_search_any_mode(db_session, create_test_resource, create_test_annotation):
    """
    Test tag-based search with ANY (OR) matching mode.

    Verifies that annotations matching ANY of the provided tags are returned.

    Requirements: 1.4
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Tag Search Test")

    # Create annotations with different tag combinations
    ann1 = create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Content 1",
        start_offset=0,
        end_offset=9,
        tags=json.dumps(["python", "programming"]),
    )

    ann2 = create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Content 2",
        start_offset=20,
        end_offset=29,
        tags=json.dumps(["python", "data-science"]),
    )

    ann3 = create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Content 3",
        start_offset=40,
        end_offset=49,
        tags=json.dumps(["javascript", "web-dev"]),
    )

    ann4 = create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Content 4",
        start_offset=60,
        end_offset=69,
        tags=json.dumps(["data-science", "machine-learning"]),
    )

    # Test 1: Search for ["python"] - should match ann1 and ann2
    results = service.search_annotations_by_tags(
        user_id="test_user", tags=["python"], match_all=False
    )

    assert len(results) == 2
    result_ids = {ann.id for ann in results}
    assert ann1.id in result_ids
    assert ann2.id in result_ids

    # Test 2: Search for ["data-science"] - should match ann2 and ann4
    results = service.search_annotations_by_tags(
        user_id="test_user", tags=["data-science"], match_all=False
    )

    assert len(results) == 2
    result_ids = {ann.id for ann in results}
    assert ann2.id in result_ids
    assert ann4.id in result_ids

    # Test 3: Search for ["python", "javascript"] - should match ann1, ann2, ann3
    results = service.search_annotations_by_tags(
        user_id="test_user", tags=["python", "javascript"], match_all=False
    )

    assert len(results) == 3
    result_ids = {ann.id for ann in results}
    assert ann1.id in result_ids
    assert ann2.id in result_ids
    assert ann3.id in result_ids


def test_tag_search_all_mode(db_session, create_test_resource, create_test_annotation):
    """
    Test tag-based search with ALL (AND) matching mode.

    Verifies that only annotations matching ALL provided tags are returned.

    Requirements: 1.4
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Tag Search ALL Test")

    # Create annotations with different tag combinations
    ann1 = create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Content 1",
        start_offset=0,
        end_offset=9,
        tags=json.dumps(["python", "programming", "tutorial"]),
    )

    ann2 = create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Content 2",
        start_offset=20,
        end_offset=29,
        tags=json.dumps(["python", "programming"]),
    )

    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Content 3",
        start_offset=40,
        end_offset=49,
        tags=json.dumps(["python", "data-science"]),
    )

    ann4 = create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Content 4",
        start_offset=60,
        end_offset=69,
        tags=json.dumps(["programming", "tutorial"]),
    )

    # Test 1: Search for ["python", "programming"] with ALL - should match ann1 and ann2
    results = service.search_annotations_by_tags(
        user_id="test_user", tags=["python", "programming"], match_all=True
    )

    assert len(results) == 2
    result_ids = {ann.id for ann in results}
    assert ann1.id in result_ids
    assert ann2.id in result_ids

    # Test 2: Search for ["python", "tutorial"] with ALL - should match ann1 only
    results = service.search_annotations_by_tags(
        user_id="test_user", tags=["python", "tutorial"], match_all=True
    )

    assert len(results) == 1
    assert results[0].id == ann1.id

    # Test 3: Search for ["programming", "tutorial"] with ALL - should match ann1 and ann4
    results = service.search_annotations_by_tags(
        user_id="test_user", tags=["programming", "tutorial"], match_all=True
    )

    assert len(results) == 2
    result_ids = {ann.id for ann in results}
    assert ann1.id in result_ids
    assert ann4.id in result_ids

    # Test 4: Search for ["python", "data-science", "tutorial"] with ALL - should match none
    results = service.search_annotations_by_tags(
        user_id="test_user", tags=["python", "data-science", "tutorial"], match_all=True
    )

    assert len(results) == 0


def test_tag_search_user_isolation(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test that tag search only returns annotations for the requesting user.

    Requirements: 1.4
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Tag Isolation Test")

    # Create annotations for different users with same tags
    create_test_annotation(
        resource_id=resource.id,
        user_id="user1",
        highlighted_text="User 1 content",
        start_offset=0,
        end_offset=14,
        tags=json.dumps(["shared-tag"]),
    )

    create_test_annotation(
        resource_id=resource.id,
        user_id="user2",
        highlighted_text="User 2 content",
        start_offset=20,
        end_offset=34,
        tags=json.dumps(["shared-tag"]),
    )

    # Search as user1
    results_user1 = service.search_annotations_by_tags(
        user_id="user1", tags=["shared-tag"], match_all=False
    )

    assert len(results_user1) == 1
    assert results_user1[0].user_id == "user1"

    # Search as user2
    results_user2 = service.search_annotations_by_tags(
        user_id="user2", tags=["shared-tag"], match_all=False
    )

    assert len(results_user2) == 1
    assert results_user2[0].user_id == "user2"


def test_tag_search_empty_tags(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test tag search with empty tag list returns no results.

    Requirements: 1.4
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="Empty Tags Test")

    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Content",
        start_offset=0,
        end_offset=7,
        tags=json.dumps(["tag1", "tag2"]),
    )

    results = service.search_annotations_by_tags(
        user_id="test_user", tags=[], match_all=False
    )

    assert len(results) == 0


def test_tag_search_no_matches(
    db_session, create_test_resource, create_test_annotation
):
    """
    Test tag search with non-existent tags returns empty list.

    Requirements: 1.4
    """
    service = AnnotationService(db_session)

    resource = create_test_resource(title="No Match Test")

    create_test_annotation(
        resource_id=resource.id,
        user_id="test_user",
        highlighted_text="Content",
        start_offset=0,
        end_offset=7,
        tags=json.dumps(["python", "programming"]),
    )

    results = service.search_annotations_by_tags(
        user_id="test_user", tags=["javascript", "web-dev"], match_all=False
    )

    assert len(results) == 0
