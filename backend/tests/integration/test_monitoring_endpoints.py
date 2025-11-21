"""
Integration tests for Phase 12.5 monitoring endpoints.

Tests for:
- Event history endpoint
- Cache statistics endpoint
- Worker status endpoint
- Database pool status endpoint
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.events.event_system import event_emitter, EventPriority
from backend.app.cache.redis_cache import cache


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestEventHistoryEndpoint:
    """Tests for GET /api/monitoring/events/history endpoint."""
    
    def test_get_event_history_empty(self, client):
        """Test getting event history when no events exist."""
        # Clear event history
        event_emitter.clear_history()
        
        response = client.get("/api/monitoring/events/history")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["count"] == 0
        assert data["events"] == []
    
    def test_get_event_history_with_events(self, client):
        """Test getting event history with events."""
        # Clear and add test events
        event_emitter.clear_history()
        
        event_emitter.emit("test.event1", {"data": "value1"}, EventPriority.HIGH)
        event_emitter.emit("test.event2", {"data": "value2"}, EventPriority.NORMAL)
        event_emitter.emit("test.event3", {"data": "value3"}, EventPriority.LOW)
        
        response = client.get("/api/monitoring/events/history")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["count"] == 3
        assert len(data["events"]) == 3
        
        # Check event structure
        event = data["events"][0]
        assert "name" in event
        assert "data" in event
        assert "timestamp" in event
        assert "priority" in event
        assert "correlation_id" in event
    
    def test_get_event_history_with_limit(self, client):
        """Test getting event history with custom limit."""
        # Clear and add many events
        event_emitter.clear_history()
        
        for i in range(50):
            event_emitter.emit(f"test.event{i}", {"index": i})
        
        response = client.get("/api/monitoring/events/history?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["count"] == 10
        assert len(data["events"]) == 10
    
    def test_get_event_history_limit_validation(self, client):
        """Test limit parameter validation."""
        # Test with limit too high
        response = client.get("/api/monitoring/events/history?limit=2000")
        assert response.status_code == 422  # Validation error
        
        # Test with limit too low
        response = client.get("/api/monitoring/events/history?limit=0")
        assert response.status_code == 422  # Validation error


class TestCacheStatsEndpoint:
    """Tests for GET /api/monitoring/cache/stats endpoint."""
    
    def test_get_cache_stats_initial(self, client):
        """Test getting cache stats with no activity."""
        # Reset cache stats
        cache.stats.reset()
        
        response = client.get("/api/monitoring/cache/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "cache_stats" in data
        
        stats = data["cache_stats"]
        assert stats["hit_rate"] == 0.0
        assert stats["hit_rate_percent"] == 0.0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["invalidations"] == 0
        assert stats["total_requests"] == 0
    
    def test_get_cache_stats_with_activity(self, client):
        """Test getting cache stats after cache activity."""
        # Reset and simulate cache activity
        cache.stats.reset()
        
        # Simulate hits and misses
        cache.stats.record_hit()
        cache.stats.record_hit()
        cache.stats.record_hit()
        cache.stats.record_miss()
        cache.stats.record_invalidation(2)
        
        response = client.get("/api/monitoring/cache/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        
        stats = data["cache_stats"]
        assert stats["hits"] == 3
        assert stats["misses"] == 1
        assert stats["invalidations"] == 2
        assert stats["total_requests"] == 4
        assert stats["hit_rate"] == 0.75
        assert stats["hit_rate_percent"] == 75.0


class TestWorkerStatusEndpoint:
    """Tests for GET /api/monitoring/workers/status endpoint."""
    
    def test_get_worker_status_no_workers(self, client):
        """Test getting worker status when no workers are running."""
        response = client.get("/api/monitoring/workers/status")
        
        # Should return error or empty worker list when Redis/Celery not available
        assert response.status_code == 200
        data = response.json()
        
        # Either error status or ok with no workers
        if data["status"] == "error":
            assert "error" in data
        else:
            assert data["status"] == "ok"
            assert "workers" in data


class TestDatabasePoolStatusEndpoint:
    """Tests for GET /api/monitoring/db/pool endpoint."""
    
    def test_get_db_pool_status(self, client):
        """Test getting database pool status."""
        response = client.get("/api/monitoring/db/pool")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "pool" in data
        
        pool = data["pool"]
        assert "size" in pool
        assert "checked_in" in pool
        assert "checked_out" in pool
        assert "overflow" in pool
        assert "total_capacity" in pool  # Updated field name
        assert "max_connections" in pool
        assert "utilization_percent" in pool
        
        # Validate pool metrics are reasonable
        assert pool["size"] >= 0
        assert pool["checked_in"] >= 0
        assert pool["checked_out"] >= 0
        # overflow can be negative (represents available overflow capacity)
        assert pool["total_capacity"] >= 0
        assert pool["max_connections"] == 60
        assert 0 <= pool["utilization_percent"] <= 100


class TestDatabaseMetricsEndpoint:
    """Tests for GET /api/monitoring/database endpoint (Phase 13)."""
    
    def test_get_database_metrics(self, client):
        """Test getting comprehensive database metrics."""
        response = client.get("/api/monitoring/database")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["ok", "unhealthy"]
        assert "timestamp" in data
        
        # Check database info
        assert "database" in data
        db_info = data["database"]
        assert "type" in db_info
        assert db_info["type"] in ["sqlite", "postgresql"]
        assert "healthy" in db_info
        assert "health_message" in db_info
        
        # Check connection pool info
        assert "connection_pool" in data
        pool = data["connection_pool"]
        assert "database_type" in pool
        assert "size" in pool
        assert "max_overflow" in pool
        assert "checked_in" in pool
        assert "checked_out" in pool
        assert "overflow" in pool
        assert "total_capacity" in pool
        assert "pool_usage_percent" in pool
        assert "connections_available" in pool
        
        # Validate pool metrics
        assert pool["size"] >= 0
        assert pool["max_overflow"] >= 0
        assert pool["checked_in"] >= 0
        assert pool["checked_out"] >= 0
        assert pool["total_capacity"] > 0
        assert 0 <= pool["pool_usage_percent"] <= 100
        assert pool["connections_available"] >= 0
        
        # Check warnings array exists
        assert "warnings" in data
        assert isinstance(data["warnings"], list)
    
    def test_database_metrics_postgresql_specific(self, client):
        """Test PostgreSQL-specific metrics when using PostgreSQL."""
        response = client.get("/api/monitoring/database")
        
        assert response.status_code == 200
        data = response.json()
        
        pool = data["connection_pool"]
        
        # If using PostgreSQL, check for PostgreSQL-specific fields
        if pool["database_type"] == "postgresql":
            assert "pool_recycle" in pool
            assert pool["pool_recycle"] == 3600
            assert "pool_pre_ping" in pool
            assert pool["pool_pre_ping"] is True
            assert "statement_timeout_ms" in pool
            assert pool["statement_timeout_ms"] == 30000
    
    def test_database_metrics_warnings(self, client):
        """Test that warnings are generated appropriately."""
        response = client.get("/api/monitoring/database")
        
        assert response.status_code == 200
        data = response.json()
        
        warnings = data["warnings"]
        
        # Check warning structure if any exist
        for warning in warnings:
            assert "level" in warning
            assert warning["level"] in ["info", "warning", "error"]
            assert "message" in warning
            assert "recommendation" in warning


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
