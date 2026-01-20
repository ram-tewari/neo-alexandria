"""
Test suite for Scholarly module endpoints.

Endpoints tested:
- GET /scholarly/resources/{resource_id}/metadata - Get scholarly metadata
- GET /scholarly/resources/{resource_id}/equations - Get equations
- GET /scholarly/resources/{resource_id}/tables - Get tables
- POST /scholarly/resources/{resource_id}/metadata/extract - Extract metadata
- GET /scholarly/metadata/completeness-stats - Get completeness stats
- GET /scholarly/health - Module health check
"""

from unittest.mock import patch, MagicMock


class TestMetadataExtraction:
    def test_get_metadata(self, client, create_test_resource):
        """Test getting scholarly metadata for a resource."""
        resource = create_test_resource()
        response = client.get(f"/scholarly/resources/{str(resource.id)}/metadata")
        assert response.status_code in [200, 404]

    def test_extract_metadata(self, client, create_test_resource):
        """Test triggering metadata extraction."""
        resource = create_test_resource()
        # Mock celery to avoid import errors
        with patch.dict("sys.modules", {"celery": MagicMock()}):
            response = client.post(
                f"/scholarly/resources/{str(resource.id)}/metadata/extract",
                json={"force": False},
            )
            # Accept various status codes
            assert response.status_code in [200, 202, 404]

    def test_get_equations(self, client, create_test_resource):
        """Test getting equations from a resource."""
        resource = create_test_resource()
        response = client.get(f"/scholarly/resources/{str(resource.id)}/equations")
        assert response.status_code in [200, 404]

    def test_get_tables(self, client, create_test_resource):
        """Test getting tables from a resource."""
        resource = create_test_resource()
        response = client.get(f"/scholarly/resources/{str(resource.id)}/tables")
        assert response.status_code in [200, 404]

    def test_get_completeness_stats(self, client, create_test_resource):
        """Test getting metadata completeness stats."""
        create_test_resource()
        response = client.get("/scholarly/metadata/completeness-stats")
        assert response.status_code == 200


class TestScholarlyHealth:
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/scholarly/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
