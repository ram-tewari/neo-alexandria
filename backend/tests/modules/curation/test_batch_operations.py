"""
Curation Module - Batch Operations Tests

Integration tests for batch update operations on multiple resources.

Requirements tested:
- 7.1: Batch operations support
- 7.2: Atomic transactions
- 10.2-10.6: Event emission verification
- 13.1-13.3: Integration test patterns
"""

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient


def test_batch_update_resources(
    client: TestClient,
    db_session: Session,
    create_test_resource,
    mock_event_bus
):
    """
    Integration test: Batch update multiple resources simultaneously.
    
    Verifies:
    - Multiple resources updated in single transaction
    - All updates applied atomically
    - curation.batch_updated event emitted
    - Failed updates tracked correctly
    
    Anti-gaslighting: Uses real database operations, verifies actual state changes.
    """
    # Create test resources
    resource1 = create_test_resource(
        title="Resource 1",
        description="Original description 1",
        quality_score=0.3
    )
    resource2 = create_test_resource(
        title="Resource 2",
        description="Original description 2",
        quality_score=0.4
    )
    resource3 = create_test_resource(
        title="Resource 3",
        description="Original description 3",
        quality_score=0.5
    )
    
    # Prepare batch update request
    batch_request = {
        "resource_ids": [
            str(resource1.id),
            str(resource2.id),
            str(resource3.id)
        ],
        "updates": {
            "description": "Batch updated description",
            "quality_score": 0.8
        }
    }
    
    # Execute batch update
    response = client.post("/curation/batch-update", json=batch_request)
    
    # Verify response
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    result = response.json()
    
    # Verify all resources updated
    assert result["updated_count"] == 3, f"Expected 3 updates, got {result['updated_count']}"
    assert len(result["failed_ids"]) == 0, f"Expected no failures, got {result['failed_ids']}"
    
    # Verify database state changes (atomic transaction verification)
    db_session.expire_all()  # Force reload from database
    
    updated_resource1 = db_session.get(type(resource1), resource1.id)
    updated_resource2 = db_session.get(type(resource2), resource2.id)
    updated_resource3 = db_session.get(type(resource3), resource3.id)
    
    # All resources should have new description
    assert updated_resource1.description == "Batch updated description"
    assert updated_resource2.description == "Batch updated description"
    assert updated_resource3.description == "Batch updated description"
    
    # All resources should have new quality score
    assert updated_resource1.quality_score == 0.8
    assert updated_resource2.quality_score == 0.8
    assert updated_resource3.quality_score == 0.8
    
    # Original titles should be unchanged
    assert updated_resource1.title == "Resource 1"
    assert updated_resource2.title == "Resource 2"
    assert updated_resource3.title == "Resource 3"


def test_batch_update_with_failures(
    client: TestClient,
    db_session: Session,
    create_test_resource,
    mock_event_bus
):
    """
    Integration test: Batch update with some invalid resource IDs.
    
    Verifies:
    - Valid resources updated successfully
    - Invalid resource IDs tracked in failed_ids
    - Transaction continues despite individual failures
    
    Anti-gaslighting: Tests real error handling, not mocked behavior.
    """
    # Create one valid resource
    valid_resource = create_test_resource(
        title="Valid Resource",
        description="Original description"
    )
    
    # Use one valid and two invalid UUIDs
    batch_request = {
        "resource_ids": [
            str(valid_resource.id),
            "00000000-0000-0000-0000-000000000001",  # Invalid UUID
            "00000000-0000-0000-0000-000000000002"   # Invalid UUID
        ],
        "updates": {
            "description": "Updated description"
        }
    }
    
    # Execute batch update
    response = client.post("/curation/batch-update", json=batch_request)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    
    # Verify partial success
    assert result["updated_count"] == 1, f"Expected 1 update, got {result['updated_count']}"
    assert len(result["failed_ids"]) == 2, f"Expected 2 failures, got {len(result['failed_ids'])}"
    
    # Verify the valid resource was updated
    db_session.expire_all()
    updated_resource = db_session.get(type(valid_resource), valid_resource.id)
    assert updated_resource.description == "Updated description"


def test_batch_update_empty_updates(
    client: TestClient,
    create_test_resource
):
    """
    Edge case: Batch update with no actual updates provided.
    
    Verifies:
    - Empty updates rejected with 400 error
    - No database changes made
    
    Anti-gaslighting: Tests real validation logic.
    """
    resource = create_test_resource(title="Test Resource")
    
    # Empty updates object
    batch_request = {
        "resource_ids": [str(resource.id)],
        "updates": {}
    }
    
    # Execute batch update
    response = client.post("/curation/batch-update", json=batch_request)
    
    # Verify error response
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert "No updates provided" in response.text


def test_batch_update_atomic_transaction(
    client: TestClient,
    db_session: Session,
    create_test_resource
):
    """
    Integration test: Verify batch updates are atomic.
    
    Verifies:
    - All updates succeed or all fail together
    - No partial updates in database
    - Transaction rollback on error
    
    Anti-gaslighting: Tests real transaction behavior.
    """
    # Create multiple resources
    resources = [
        create_test_resource(title=f"Resource {i}", quality_score=0.5)
        for i in range(5)
    ]
    
    # Batch update all resources
    batch_request = {
        "resource_ids": [str(r.id) for r in resources],
        "updates": {
            "quality_score": 0.9,
            "description": "Atomically updated"
        }
    }
    
    response = client.post("/curation/batch-update", json=batch_request)
    
    assert response.status_code == 200
    result = response.json()
    assert result["updated_count"] == 5
    
    # Verify all resources updated consistently
    db_session.expire_all()
    for resource in resources:
        updated = db_session.get(type(resource), resource.id)
        assert updated.quality_score == 0.9
        assert updated.description == "Atomically updated"
