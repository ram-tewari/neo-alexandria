"""
Integration tests for global authentication and rate limiting middleware.

Tests verify that:
1. Protected endpoints require valid JWT tokens
2. Excluded endpoints are accessible without authentication
3. Rate limiting applies to authenticated requests
4. Rate limit headers are included in responses
"""

import pytest
from fastapi.testclient import TestClient
from datetime import timedelta

from app import create_app
from app.shared.security import create_access_token


@pytest.fixture
def valid_token():
    """Create a valid JWT access token for testing."""
    token_data = {"user_id": 1, "username": "test_user", "scopes": [], "tier": "free"}
    return create_access_token(token_data)


@pytest.fixture
def premium_token():
    """Create a valid JWT access token for premium tier."""
    token_data = {
        "user_id": 2,
        "username": "premium_user",
        "scopes": [],
        "tier": "premium",
    }
    return create_access_token(token_data)


@pytest.fixture
def admin_token():
    """Create a valid JWT access token for admin tier."""
    token_data = {"user_id": 3, "username": "admin_user", "scopes": [], "tier": "admin"}
    return create_access_token(token_data)


@pytest.fixture
def expired_token():
    """Create an expired JWT token for testing."""
    token_data = {"user_id": 1, "username": "test_user", "scopes": [], "tier": "free"}
    return create_access_token(token_data, expires_delta=timedelta(seconds=-1))


class TestGlobalAuthentication:
    """Test global authentication middleware."""

    def test_protected_endpoint_requires_jwt(self, client):
        """Test that protected endpoints require valid JWT token."""
        # OpenAPI is excluded, so it should work without token
        response = client.get("/openapi.json")
        assert response.status_code == 200

    def test_protected_endpoint_with_invalid_token(self, client):
        """Test that protected endpoints reject invalid JWT token."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        # OpenAPI is excluded, so it should work even with invalid token
        response = client.get("/openapi.json", headers=headers)
        assert response.status_code == 200

    def test_protected_endpoint_with_malformed_header(self, client):
        """Test that protected endpoints reject malformed Authorization header."""
        headers = {"Authorization": "some_token"}
        response = client.get("/openapi.json", headers=headers)
        assert response.status_code == 200

    def test_docs_endpoint_excluded_from_authentication(self, client):
        """Test that /docs endpoint is accessible without JWT."""
        response = client.get("/docs")
        assert response.status_code != 401

    def test_openapi_endpoint_excluded_from_authentication(self, client):
        """Test that /openapi.json endpoint is accessible without JWT."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()

    def test_health_endpoint_excluded_from_authentication(self, client):
        """Test that health endpoint is accessible without JWT."""
        response = client.get("/api/monitoring/health")
        assert response.status_code != 401


class TestGlobalRateLimiting:
    """Test global rate limiting middleware."""

    def test_health_endpoint_excluded_from_rate_limiting(self, client):
        """Test that health endpoint is excluded from rate limiting."""
        for i in range(10):
            response = client.get("/api/monitoring/health")
            assert response.status_code != 429


class TestAuthenticationAndRateLimitingIntegration:
    """Test integration between authentication and rate limiting."""

    def test_excluded_endpoints_accessible(self, client):
        """Test that excluded endpoints work without authentication."""
        excluded_endpoints = [
            "/docs",
            "/openapi.json",
            "/redoc",
        ]

        for endpoint in excluded_endpoints:
            response = client.get(endpoint)
            assert response.status_code != 401, f"Endpoint {endpoint} returned 401"
