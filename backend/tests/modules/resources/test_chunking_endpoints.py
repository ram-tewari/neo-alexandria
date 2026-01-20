"""
Chunking Endpoints Tests (Phase 17.5 - Advanced RAG)

Tests the chunking API endpoints including:
- POST /api/resources/{resource_id}/chunks - Trigger chunking
- GET /api/resources/{resource_id}/chunks - List chunks with pagination
- GET /api/chunks/{chunk_id} - Retrieve specific chunk

All tests follow the anti-gaslighting pattern with clear assertions.
"""

import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models import DocumentChunk


def test_create_resource_chunks_success(
    client: TestClient, db_session: Session, create_test_resource, tmp_path
):
    """
    Test successful chunking of a resource.

    Verifies:
    - HTTP 201 response
    - Response contains expected fields
    - Chunking task is queued

    Requirements: 6.1-6.10
    """
    # Create a test resource with content
    resource = create_test_resource(
        title="Test Resource",
        source="https://example.com/test",
        ingestion_status="completed",
    )

    # Create a temporary content file
    content_file = tmp_path / "test_content.txt"
    content_file.write_text(
        "This is test content. It has multiple sentences. Each sentence is important."
    )

    # Update resource to point to content file
    resource.identifier = str(content_file)
    db_session.add(resource)
    db_session.commit()

    # Make API request
    response = client.post(
        f"/resources/{resource.id}/chunks",
        json={
            "strategy": "semantic",
            "chunk_size": 500,
            "overlap": 50,
            "parser_type": "text",
        },
    )

    # Verify HTTP response status
    assert response.status_code == 201, (
        f"IMPLEMENTATION FAILURE: Expected status 201, got {response.status_code}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
        f"Response: {response.json()}"
    )

    # Verify response body contains expected fields
    response_data = response.json()
    expected_fields = ["message", "resource_id", "strategy", "chunk_size", "overlap"]
    for field in expected_fields:
        assert field in response_data, (
            f"IMPLEMENTATION FAILURE: Expected field '{field}' in response\n"
            f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
            f"Response: {response_data}"
        )

    # Verify response values
    assert response_data["resource_id"] == str(resource.id), (
        f"IMPLEMENTATION FAILURE: Expected resource_id {resource.id}, got {response_data['resource_id']}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead."
    )

    assert response_data["strategy"] == "semantic", (
        f"IMPLEMENTATION FAILURE: Expected strategy 'semantic', got {response_data['strategy']}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead."
    )


def test_create_resource_chunks_resource_not_found(client: TestClient):
    """
    Test chunking fails for non-existent resource.

    Verifies:
    - HTTP 404 response
    - Error message indicates resource not found

    Requirements: 6.1-6.10
    """
    # Use a random UUID that doesn't exist
    fake_resource_id = uuid.uuid4()

    # Make API request
    response = client.post(
        f"/resources/{fake_resource_id}/chunks",
        json={"strategy": "semantic", "chunk_size": 500, "overlap": 50},
    )

    # Verify HTTP response status
    assert response.status_code == 404, (
        f"IMPLEMENTATION FAILURE: Expected status 404, got {response.status_code}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
        f"Response: {response.json()}"
    )

    # Verify error message
    response_data = response.json()
    assert "not found" in response_data["detail"].lower(), (
        f"IMPLEMENTATION FAILURE: Expected 'not found' in error message\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
        f"Response: {response_data}"
    )


def test_create_resource_chunks_no_content(client: TestClient, create_test_resource):
    """
    Test chunking fails for resource without content.

    Verifies:
    - HTTP 400 response
    - Error message indicates no content

    Requirements: 6.1-6.10
    """
    # Create a test resource without content (no identifier)
    resource = create_test_resource(
        title="Test Resource",
        source="https://example.com/test",
        ingestion_status="pending",
        identifier=None,
    )

    # Make API request
    response = client.post(
        f"/resources/{resource.id}/chunks",
        json={"strategy": "semantic", "chunk_size": 500, "overlap": 50},
    )

    # Verify HTTP response status
    assert response.status_code == 400, (
        f"IMPLEMENTATION FAILURE: Expected status 400, got {response.status_code}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
        f"Response: {response.json()}"
    )

    # Verify error message
    response_data = response.json()
    assert "no content" in response_data["detail"].lower(), (
        f"IMPLEMENTATION FAILURE: Expected 'no content' in error message\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
        f"Response: {response_data}"
    )


def test_create_resource_chunks_invalid_strategy(
    client: TestClient, create_test_resource, tmp_path
):
    """
    Test chunking fails with invalid strategy.

    Verifies:
    - HTTP 400 response
    - Error message indicates invalid strategy

    Requirements: 6.1-6.10
    """
    # Create a test resource with content
    resource = create_test_resource(
        title="Test Resource",
        source="https://example.com/test",
        ingestion_status="completed",
    )

    # Create a temporary content file
    content_file = tmp_path / "test_content.txt"
    content_file.write_text("Test content")

    # Update resource to point to content file
    resource.identifier = str(content_file)
    db_session = next(
        iter([s for s in [resource] if hasattr(resource, "_sa_instance_state")])
    )._sa_instance_state.session
    db_session.add(resource)
    db_session.commit()

    # Make API request with invalid strategy
    response = client.post(
        f"/resources/{resource.id}/chunks",
        json={"strategy": "invalid_strategy", "chunk_size": 500, "overlap": 50},
    )

    # Verify HTTP response status
    assert response.status_code == 400, (
        f"IMPLEMENTATION FAILURE: Expected status 400, got {response.status_code}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
        f"Response: {response.json()}"
    )

    # Verify error message
    response_data = response.json()
    assert (
        "invalid" in response_data["detail"].lower()
        or "strategy" in response_data["detail"].lower()
    ), (
        f"IMPLEMENTATION FAILURE: Expected 'invalid' or 'strategy' in error message\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
        f"Response: {response_data}"
    )


def test_create_resource_chunks_overlap_too_large(
    client: TestClient, create_test_resource, tmp_path
):
    """
    Test chunking fails when overlap >= chunk_size.

    Verifies:
    - HTTP 400 response
    - Error message indicates overlap issue

    Requirements: 6.1-6.10
    """
    # Create a test resource with content
    resource = create_test_resource(
        title="Test Resource",
        source="https://example.com/test",
        ingestion_status="completed",
    )

    # Create a temporary content file
    content_file = tmp_path / "test_content.txt"
    content_file.write_text("Test content")

    # Update resource to point to content file
    resource.identifier = str(content_file)
    db_session = next(
        iter([s for s in [resource] if hasattr(resource, "_sa_instance_state")])
    )._sa_instance_state.session
    db_session.add(resource)
    db_session.commit()

    # Make API request with overlap >= chunk_size
    response = client.post(
        f"/resources/{resource.id}/chunks",
        json={
            "strategy": "semantic",
            "chunk_size": 100,
            "overlap": 100,  # Equal to chunk_size
        },
    )

    # Verify HTTP response status
    assert response.status_code == 400, (
        f"IMPLEMENTATION FAILURE: Expected status 400, got {response.status_code}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
        f"Response: {response.json()}"
    )

    # Verify error message
    response_data = response.json()
    assert "overlap" in response_data["detail"].lower(), (
        f"IMPLEMENTATION FAILURE: Expected 'overlap' in error message\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
        f"Response: {response_data}"
    )


def test_list_resource_chunks_success(
    client: TestClient, db_session: Session, create_test_resource
):
    """
    Test successful listing of resource chunks with pagination.

    Verifies:
    - HTTP 200 response
    - Response contains items and pagination metadata
    - Chunks are ordered by chunk_index

    Requirements: 6.1-6.10
    """
    # Create a test resource
    resource = create_test_resource(
        title="Test Resource",
        source="https://example.com/test",
        ingestion_status="completed",
    )

    # Create test chunks
    chunks = []
    for i in range(5):
        chunk = DocumentChunk(
            resource_id=resource.id,
            content=f"Chunk {i} content",
            chunk_index=i,
            chunk_metadata={"page": 1},
            embedding_id=None,
        )
        db_session.add(chunk)
        chunks.append(chunk)

    db_session.commit()

    # Make API request
    response = client.get(f"/resources/{resource.id}/chunks?limit=3&offset=0")

    # Verify HTTP response status
    assert response.status_code == 200, (
        f"IMPLEMENTATION FAILURE: Expected status 200, got {response.status_code}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
        f"Response: {response.json()}"
    )

    # Verify response structure
    response_data = response.json()
    expected_fields = ["items", "total", "limit", "offset"]
    for field in expected_fields:
        assert field in response_data, (
            f"IMPLEMENTATION FAILURE: Expected field '{field}' in response\n"
            f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
            f"Response: {response_data}"
        )

    # Verify pagination metadata
    assert response_data["total"] == 5, (
        f"IMPLEMENTATION FAILURE: Expected total 5, got {response_data['total']}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead."
    )

    assert response_data["limit"] == 3, (
        f"IMPLEMENTATION FAILURE: Expected limit 3, got {response_data['limit']}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead."
    )

    assert response_data["offset"] == 0, (
        f"IMPLEMENTATION FAILURE: Expected offset 0, got {response_data['offset']}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead."
    )

    # Verify items
    assert len(response_data["items"]) == 3, (
        f"IMPLEMENTATION FAILURE: Expected 3 items, got {len(response_data['items'])}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead."
    )

    # Verify chunks are ordered by chunk_index
    for i, item in enumerate(response_data["items"]):
        assert item["chunk_index"] == i, (
            f"IMPLEMENTATION FAILURE: Expected chunk_index {i}, got {item['chunk_index']}\n"
            f"DO NOT UPDATE THE TEST - Fix the implementation instead."
        )


def test_list_resource_chunks_pagination(
    client: TestClient, db_session: Session, create_test_resource
):
    """
    Test pagination works correctly for chunk listing.

    Verifies:
    - Offset and limit parameters work correctly
    - Second page returns correct chunks

    Requirements: 6.1-6.10
    """
    # Create a test resource
    resource = create_test_resource(
        title="Test Resource",
        source="https://example.com/test",
        ingestion_status="completed",
    )

    # Create test chunks
    for i in range(10):
        chunk = DocumentChunk(
            resource_id=resource.id,
            content=f"Chunk {i} content",
            chunk_index=i,
            chunk_metadata={"page": 1},
            embedding_id=None,
        )
        db_session.add(chunk)

    db_session.commit()

    # Make API request for second page
    response = client.get(f"/resources/{resource.id}/chunks?limit=3&offset=3")

    # Verify HTTP response status
    assert response.status_code == 200, (
        f"IMPLEMENTATION FAILURE: Expected status 200, got {response.status_code}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead."
    )

    # Verify response
    response_data = response.json()
    assert len(response_data["items"]) == 3, (
        f"IMPLEMENTATION FAILURE: Expected 3 items, got {len(response_data['items'])}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead."
    )

    # Verify we got chunks 3, 4, 5
    for i, item in enumerate(response_data["items"]):
        expected_index = i + 3
        assert item["chunk_index"] == expected_index, (
            f"IMPLEMENTATION FAILURE: Expected chunk_index {expected_index}, got {item['chunk_index']}\n"
            f"DO NOT UPDATE THE TEST - Fix the implementation instead."
        )


def test_list_resource_chunks_resource_not_found(client: TestClient):
    """
    Test listing chunks fails for non-existent resource.

    Verifies:
    - HTTP 404 response
    - Error message indicates resource not found

    Requirements: 6.1-6.10
    """
    # Use a random UUID that doesn't exist
    fake_resource_id = uuid.uuid4()

    # Make API request
    response = client.get(f"/resources/{fake_resource_id}/chunks")

    # Verify HTTP response status
    assert response.status_code == 404, (
        f"IMPLEMENTATION FAILURE: Expected status 404, got {response.status_code}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
        f"Response: {response.json()}"
    )

    # Verify error message
    response_data = response.json()
    assert "not found" in response_data["detail"].lower(), (
        f"IMPLEMENTATION FAILURE: Expected 'not found' in error message\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
        f"Response: {response_data}"
    )


def test_list_resource_chunks_invalid_pagination(
    client: TestClient, create_test_resource
):
    """
    Test listing chunks fails with invalid pagination parameters.

    Verifies:
    - HTTP 400 response for invalid limit
    - HTTP 400 response for invalid offset

    Requirements: 6.1-6.10
    """
    # Create a test resource
    resource = create_test_resource(
        title="Test Resource",
        source="https://example.com/test",
        ingestion_status="completed",
    )

    # Test invalid limit (too large)
    response = client.get(f"/resources/{resource.id}/chunks?limit=200")
    assert response.status_code == 400, (
        f"IMPLEMENTATION FAILURE: Expected status 400 for limit > 100, got {response.status_code}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead."
    )

    # Test invalid limit (zero)
    response = client.get(f"/resources/{resource.id}/chunks?limit=0")
    assert response.status_code == 400, (
        f"IMPLEMENTATION FAILURE: Expected status 400 for limit = 0, got {response.status_code}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead."
    )

    # Test invalid offset (negative)
    response = client.get(f"/resources/{resource.id}/chunks?offset=-1")
    assert response.status_code == 400, (
        f"IMPLEMENTATION FAILURE: Expected status 400 for negative offset, got {response.status_code}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead."
    )


def test_get_chunk_success(
    client: TestClient, db_session: Session, create_test_resource
):
    """
    Test successful retrieval of a specific chunk.

    Verifies:
    - HTTP 200 response
    - Response contains all chunk fields
    - Chunk data matches database

    Requirements: 6.1-6.10
    """
    # Create a test resource
    resource = create_test_resource(
        title="Test Resource",
        source="https://example.com/test",
        ingestion_status="completed",
    )

    # Create a test chunk
    chunk = DocumentChunk(
        resource_id=resource.id,
        content="Test chunk content",
        chunk_index=0,
        chunk_metadata={"page": 1, "coordinates": [10, 20]},
        embedding_id=None,
    )
    db_session.add(chunk)
    db_session.commit()
    db_session.refresh(chunk)

    # Make API request
    response = client.get(f"/chunks/{chunk.id}")

    # Verify HTTP response status
    assert response.status_code == 200, (
        f"IMPLEMENTATION FAILURE: Expected status 200, got {response.status_code}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
        f"Response: {response.json()}"
    )

    # Verify response structure
    response_data = response.json()
    expected_fields = [
        "id",
        "resource_id",
        "content",
        "chunk_index",
        "chunk_metadata",
        "embedding_id",
        "created_at",
    ]
    for field in expected_fields:
        assert field in response_data, (
            f"IMPLEMENTATION FAILURE: Expected field '{field}' in response\n"
            f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
            f"Response: {response_data}"
        )

    # Verify chunk data
    assert response_data["id"] == str(chunk.id), (
        f"IMPLEMENTATION FAILURE: Expected id {chunk.id}, got {response_data['id']}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead."
    )

    assert response_data["resource_id"] == str(resource.id), (
        f"IMPLEMENTATION FAILURE: Expected resource_id {resource.id}, got {response_data['resource_id']}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead."
    )

    assert response_data["content"] == "Test chunk content", (
        f"IMPLEMENTATION FAILURE: Expected content 'Test chunk content', got {response_data['content']}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead."
    )

    assert response_data["chunk_index"] == 0, (
        f"IMPLEMENTATION FAILURE: Expected chunk_index 0, got {response_data['chunk_index']}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead."
    )

    assert response_data["chunk_metadata"] == {"page": 1, "coordinates": [10, 20]}, (
        f"IMPLEMENTATION FAILURE: Expected metadata to match, got {response_data['chunk_metadata']}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead."
    )


def test_get_chunk_not_found(client: TestClient):
    """
    Test retrieval fails for non-existent chunk.

    Verifies:
    - HTTP 404 response
    - Error message indicates chunk not found

    Requirements: 6.1-6.10
    """
    # Use a random UUID that doesn't exist
    fake_chunk_id = uuid.uuid4()

    # Make API request
    response = client.get(f"/chunks/{fake_chunk_id}")

    # Verify HTTP response status
    assert response.status_code == 404, (
        f"IMPLEMENTATION FAILURE: Expected status 404, got {response.status_code}\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
        f"Response: {response.json()}"
    )

    # Verify error message
    response_data = response.json()
    assert "not found" in response_data["detail"].lower(), (
        f"IMPLEMENTATION FAILURE: Expected 'not found' in error message\n"
        f"DO NOT UPDATE THE TEST - Fix the implementation instead.\n"
        f"Response: {response_data}"
    )
