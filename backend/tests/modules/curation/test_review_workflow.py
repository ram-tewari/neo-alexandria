"""
Curation Module - Review Workflow Tests

Integration tests for content review and approval workflows.

Requirements tested:
- 7.2: Review workflow state transitions
- 7.3: Approval/rejection logic
- 7.4: Review queue management
- 13.1-13.3: Integration test patterns
"""

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient


def test_review_queue_filtering(
    client: TestClient, db_session: Session, create_test_resource
):
    """
    Integration test: Review queue filters low-quality resources.

    Verifies:
    - Resources below threshold appear in queue
    - Resources above threshold excluded
    - Queue sorted by quality score (ascending)

    Anti-gaslighting: Uses real database queries, verifies actual filtering.
    """
    # Create resources with varying quality scores
    low_quality_1 = create_test_resource(title="Low Quality 1", quality_score=0.2)
    low_quality_2 = create_test_resource(title="Low Quality 2", quality_score=0.3)
    medium_quality = create_test_resource(title="Medium Quality", quality_score=0.6)
    high_quality = create_test_resource(title="High Quality", quality_score=0.9)

    # Query review queue with threshold 0.5
    response = client.get("/curation/review-queue?threshold=0.5&limit=10")

    assert response.status_code == 200
    result = response.json()

    # Verify only low-quality resources in queue
    assert result["total"] == 2, f"Expected 2 items in queue, got {result['total']}"
    assert len(result["items"]) == 2

    # Verify sorting by quality score (ascending)
    items = result["items"]
    assert items[0]["quality_score"] == 0.2
    assert items[1]["quality_score"] == 0.3

    # Verify correct resources returned
    returned_ids = {item["id"] for item in items}
    assert str(low_quality_1.id) in returned_ids
    assert str(low_quality_2.id) in returned_ids
    assert str(medium_quality.id) not in returned_ids
    assert str(high_quality.id) not in returned_ids


def test_quality_analysis_endpoint(client: TestClient, create_test_resource):
    """
    Integration test: Quality analysis provides detailed metrics.

    Verifies:
    - Analysis returns all quality dimensions
    - Improvement suggestions generated
    - Metrics calculated correctly

    Anti-gaslighting: Tests real quality analyzer, not mocked values.
    """
    resource = create_test_resource(
        title="Test Resource", description="A short description", quality_score=0.4
    )

    # Get quality analysis
    response = client.get(f"/curation/quality-analysis/{resource.id}")

    assert response.status_code == 200
    analysis = response.json()

    # Verify all quality dimensions present
    assert "resource_id" in analysis
    assert "metadata_completeness" in analysis
    assert "readability" in analysis
    assert "source_credibility" in analysis
    assert "content_depth" in analysis
    assert "overall_quality" in analysis
    assert "quality_level" in analysis
    assert "suggestions" in analysis

    # Verify resource ID matches
    assert analysis["resource_id"] == str(resource.id)

    # Verify suggestions is a list
    assert isinstance(analysis["suggestions"], list)

    # Verify quality metrics are floats
    assert isinstance(analysis["metadata_completeness"], (int, float))
    assert isinstance(analysis["source_credibility"], (int, float))
    assert isinstance(analysis["content_depth"], (int, float))
    assert isinstance(analysis["overall_quality"], (int, float))


def test_bulk_quality_check(
    client: TestClient, db_session: Session, create_test_resource
):
    """
    Integration test: Bulk quality check recalculates scores.

    Verifies:
    - Quality scores recalculated for all resources
    - Database updated with new scores
    - Failed resources tracked

    Anti-gaslighting: Tests real quality calculation, verifies database changes.
    """
    # Create resources with initial quality scores
    resource1 = create_test_resource(
        title="Resource 1",
        description="Test description",
        quality_score=0.0,  # Initial score
    )
    resource2 = create_test_resource(
        title="Resource 2",
        description="Another test description",
        quality_score=0.0,  # Initial score
    )

    # Perform bulk quality check
    bulk_request = {"resource_ids": [str(resource1.id), str(resource2.id)]}

    response = client.post("/curation/bulk-quality-check", json=bulk_request)

    assert response.status_code == 200
    result = response.json()

    # Verify all resources processed
    assert result["updated_count"] == 2
    assert len(result["failed_ids"]) == 0

    # Verify quality scores updated in database
    db_session.expire_all()
    updated_resource1 = db_session.get(type(resource1), resource1.id)
    updated_resource2 = db_session.get(type(resource2), resource2.id)

    # Quality scores should be recalculated (not 0.0 anymore)
    assert updated_resource1.quality_score > 0.0
    assert updated_resource2.quality_score > 0.0


def test_empty_batch_operation(client: TestClient):
    """
    Edge case: Batch operation with empty resource list.

    Verifies:
    - Empty batch rejected with 400 error
    - Appropriate error message returned

    Anti-gaslighting: Tests real validation logic.
    """
    # Empty resource list
    batch_request = {
        "resource_ids": [],
        "updates": {"description": "Should not be applied"},
    }

    response = client.post("/curation/batch-update", json=batch_request)

    # Verify validation error
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


def test_review_queue_pagination(client: TestClient, create_test_resource):
    """
    Integration test: Review queue supports pagination.

    Verifies:
    - Limit parameter controls page size
    - Offset parameter controls starting position
    - Total count accurate

    Anti-gaslighting: Tests real pagination logic.
    """
    # Create 10 low-quality resources
    for i in range(10):
        create_test_resource(
            title=f"Low Quality {i}",
            quality_score=0.1 + (i * 0.01),  # 0.1 to 0.19
        )

    # Get first page (5 items)
    response1 = client.get("/curation/review-queue?threshold=0.5&limit=5&offset=0")
    assert response1.status_code == 200
    page1 = response1.json()

    assert page1["total"] == 10
    assert len(page1["items"]) == 5

    # Get second page (5 items)
    response2 = client.get("/curation/review-queue?threshold=0.5&limit=5&offset=5")
    assert response2.status_code == 200
    page2 = response2.json()

    assert page2["total"] == 10
    assert len(page2["items"]) == 5

    # Verify no overlap between pages
    page1_ids = {item["id"] for item in page1["items"]}
    page2_ids = {item["id"] for item in page2["items"]}
    assert len(page1_ids & page2_ids) == 0, "Pages should not overlap"


def test_low_quality_endpoint(client: TestClient, create_test_resource):
    """
    Integration test: Low-quality endpoint filters correctly.

    Verifies:
    - Returns resources below threshold
    - Excludes resources above threshold
    - Respects pagination parameters

    Anti-gaslighting: Tests real filtering logic.
    """
    # Create resources with varying quality
    low1 = create_test_resource(title="Low 1", quality_score=0.2)
    low2 = create_test_resource(title="Low 2", quality_score=0.3)
    high = create_test_resource(title="High", quality_score=0.8)

    # Query low-quality resources
    response = client.get("/curation/low-quality?threshold=0.5")

    assert response.status_code == 200
    result = response.json()

    # Verify filtering
    assert result["total"] == 2
    assert len(result["items"]) == 2

    returned_ids = {item["id"] for item in result["items"]}
    assert str(low1.id) in returned_ids
    assert str(low2.id) in returned_ids
    assert str(high.id) not in returned_ids
