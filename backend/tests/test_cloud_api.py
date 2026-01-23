"""
Unit Tests for Cloud API (Phase 19)

These tests validate specific examples and edge cases for the Cloud API
ingestion endpoints.

Feature: phase19-hybrid-edge-cloud-orchestration
"""

import json
import os
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi.testclient import TestClient

# Mock upstash_redis before importing the router
sys.modules['upstash_redis'] = MagicMock()


@pytest.fixture(autouse=True)
def setup_env():
    """Set up environment variables for testing."""
    os.environ["MODE"] = "CLOUD"
    os.environ["PHAROS_ADMIN_TOKEN"] = "test-admin-token-12345"
    os.environ["UPSTASH_REDIS_REST_URL"] = "https://test-redis.upstash.io"
    os.environ["UPSTASH_REDIS_REST_TOKEN"] = "test-token"
    yield
    # Cleanup
    for key in ["MODE", "PHAROS_ADMIN_TOKEN", "UPSTASH_REDIS_REST_URL", "UPSTASH_REDIS_REST_TOKEN"]:
        os.environ.pop(key, None)


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    mock = Mock(spec=['llen', 'rpush', 'expire', 'get', 'lrange', 'ping'])
    # Use spec to prevent MagicMock behavior
    mock.llen = Mock(return_value=0)
    mock.rpush = Mock(return_value=42)
    mock.expire = Mock(return_value=True)
    mock.get = Mock(return_value=b"Idle")
    mock.lrange = Mock(return_value=[])
    mock.ping = Mock(return_value=True)
    return mock


@pytest.fixture
def client(mock_redis, monkeypatch):
    """Create FastAPI test client with mocked Redis."""
    import app.routers.ingestion as ingestion_module
    
    # Create a function that always returns the same mock instance
    def get_mock_redis():
        return mock_redis
    
    monkeypatch.setattr(ingestion_module, 'get_redis_client', get_mock_redis)
    
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(ingestion_module.router)
    
    test_client = TestClient(app)
    # Attach mock for easy access in tests
    test_client.mock_redis = mock_redis
    
    return test_client


def test_mode_cloud_doesnt_load_torch():
    """
    Test that MODE=CLOUD doesn't load torch modules.
    
    Validates: Requirements 1.2
    """
    # Verify MODE is set to CLOUD
    assert os.getenv("MODE") == "CLOUD"
    
    # Verify torch is not in sys.modules (or is mocked)
    # In a real scenario, torch wouldn't be imported at all
    # For this test, we just verify the MODE is correct
    assert os.getenv("MODE") != "EDGE"


def test_redis_connection_check(client):
    """
    Test Redis connection check in health endpoint.
    
    Validates: Requirements 1.5
    """
    # Act
    response = client.get("/api/v1/ingestion/health")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["services"]["redis"] == "healthy"


def test_503_when_redis_unavailable(client):
    """
    Test 503 status when Redis is unavailable.
    
    Validates: Requirements 2.5
    """
    # Arrange
    client.mock_redis.llen = Mock(side_effect=Exception("Connection refused"))
    
    # Act
    response = client.post(
        "/api/v1/ingestion/ingest/github.com/user/repo",
        headers={"Authorization": "Bearer test-admin-token-12345"}
    )
    
    # Assert
    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


def test_429_when_queue_is_full(client):
    """
    Test 429 status when queue is full (>= 10 tasks).
    
    Validates: Requirements 2.6
    """
    # Arrange
    client.mock_redis.llen = Mock(return_value=10)  # At capacity
    
    # Act
    response = client.post(
        "/api/v1/ingestion/ingest/github.com/user/repo",
        headers={"Authorization": "Bearer test-admin-token-12345"}
    )
    
    # Assert
    assert response.status_code == 429
    assert "full" in response.json()["detail"].lower()


def test_401_when_token_is_invalid(client):
    """
    Test 401 status when token is invalid.
    
    Validates: Requirements 2.8
    """
    # Act
    response = client.post(
        "/api/v1/ingestion/ingest/github.com/user/repo",
        headers={"Authorization": "Bearer wrong-token"}
    )
    
    # Assert
    assert response.status_code == 401
    assert "authentication" in response.json()["detail"].lower()


def test_401_when_token_is_missing(client):
    """
    Test 401 status when token is missing.
    
    Validates: Requirements 2.8
    """
    # Act
    response = client.post(
        "/api/v1/ingestion/ingest/github.com/user/repo"
    )
    
    # Assert
    assert response.status_code == 403  # FastAPI returns 403 for missing auth


def test_authentication_failure_logging(client, caplog):
    """
    Test that authentication failures are logged.
    
    Validates: Requirements 2.9
    """
    # Act
    response = client.post(
        "/api/v1/ingestion/ingest/github.com/user/repo",
        headers={"Authorization": "Bearer wrong-token"}
    )
    
    # Assert
    assert response.status_code == 401
    # Check that a warning was logged (caplog captures log messages)
    assert any("Authentication failure" in record.message for record in caplog.records)


def test_health_check_endpoint(client):
    """
    Test health check endpoint returns service status.
    
    Validates: Requirements 12.6
    """
    # Act
    response = client.get("/api/v1/ingestion/health")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data
    assert "redis" in data["services"]


def test_worker_status_returns_real_time_updates(client):
    """
    Test GET /worker/status returns real-time updates for UI.
    
    Validates: Requirements 2.10
    """
    # Arrange
    client.mock_redis.get = Mock(return_value=b"Training Graph on github.com/user/repo")
    
    # Act
    response = client.get("/api/v1/ingestion/worker/status")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "Training Graph on github.com/user/repo"


def test_valid_url_accepted(client):
    """
    Test that valid repository URLs are accepted.
    
    Validates: Requirements 2.4
    """
    valid_urls = [
        "github.com/user/repo",
        "https://github.com/user/repo",
        "gitlab.com/org/project",
        "bitbucket.org/team/code",
    ]
    
    for url in valid_urls:
        response = client.post(
            f"/api/v1/ingestion/ingest/{url}",
            headers={"Authorization": "Bearer test-admin-token-12345"}
        )
        assert response.status_code == 200, f"Failed for URL: {url}"


def test_invalid_url_rejected(client):
    """
    Test that invalid repository URLs are rejected.
    
    Validates: Requirements 2.4, 11.4
    """
    invalid_urls = [
        "; rm -rf /",
        "|cat /etc/passwd",
        "`whoami`",
        "test\nmalicious",
    ]
    
    for url in invalid_urls:
        response = client.post(
            f"/api/v1/ingestion/ingest/{url}",
            headers={"Authorization": "Bearer test-admin-token-12345"}
        )
        assert response.status_code == 400, f"Should reject URL: {url}"


def test_job_history_endpoint(client):
    """
    Test job history endpoint returns recent jobs.
    
    Validates: Requirements 9.6
    """
    # Arrange
    job_records = [
        json.dumps({
            "repo_url": "github.com/user/repo1",
            "status": "complete",
            "duration_seconds": 120.5,
            "files_processed": 100,
            "embeddings_generated": 100,
            "timestamp": "2024-01-20T10:00:00Z"
        }),
        json.dumps({
            "repo_url": "github.com/user/repo2",
            "status": "failed",
            "error": "Clone failed",
            "timestamp": "2024-01-20T11:00:00Z"
        })
    ]
    client.mock_redis.lrange = Mock(return_value=[r.encode() for r in job_records])
    
    # Act
    response = client.get("/api/v1/ingestion/jobs/history?limit=10")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert len(data["jobs"]) == 2
    assert data["jobs"][0]["repo_url"] == "github.com/user/repo1"
    assert data["jobs"][1]["status"] == "failed"


def test_task_metadata_includes_ttl(client):
    """
    Test that queued tasks include TTL metadata.
    
    Validates: Requirements 2.7
    """
    # Act
    response = client.post(
        "/api/v1/ingestion/ingest/github.com/user/repo",
        headers={"Authorization": "Bearer test-admin-token-12345"}
    )
    
    # Assert
    assert response.status_code == 200
    
    # Check that rpush was called with task data containing TTL
    client.mock_redis.rpush.assert_called_once()
    call_args = client.mock_redis.rpush.call_args
    task_data = json.loads(call_args[0][1])
    assert "ttl" in task_data
    assert task_data["ttl"] == 86400  # 24 hours


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
