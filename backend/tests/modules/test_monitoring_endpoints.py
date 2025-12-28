"""
Test suite for Monitoring module endpoints.

Endpoints tested:
- GET /api/monitoring/health - Overall system health
- GET /api/monitoring/performance - Performance metrics
- GET /api/monitoring/database - Database metrics
- GET /api/monitoring/events - Event bus metrics
- GET /api/monitoring/cache/stats - Cache statistics
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestMonitoringEndpoints:
    def test_get_health(self, client):
        """Test overall health check."""
        response = client.get("/api/monitoring/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_get_performance_metrics(self, client):
        """Test performance metrics endpoint."""
        response = client.get("/api/monitoring/performance")
        assert response.status_code == 200

    def test_get_database_metrics(self, client):
        """Test database metrics endpoint."""
        response = client.get("/api/monitoring/database")
        assert response.status_code == 200

    def test_get_event_bus_metrics(self, client):
        """Test event bus metrics endpoint."""
        response = client.get("/api/monitoring/events")
        assert response.status_code == 200

    def test_get_cache_stats(self, client):
        """Test cache statistics endpoint."""
        response = client.get("/api/monitoring/cache/stats")
        assert response.status_code == 200

    def test_get_db_pool_status(self, client):
        """Test database pool status endpoint."""
        response = client.get("/api/monitoring/db/pool")
        assert response.status_code == 200


class TestModuleHealth:
    def test_module_health_check(self, client):
        """Test module-specific health check."""
        response = client.get("/api/monitoring/health/module/resources")
        # Module may or may not be registered
        assert response.status_code in [200, 404]
