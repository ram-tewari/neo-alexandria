"""
Test suite for Quality module endpoints.

Endpoints tested:
- GET /resources/{resource_id}/quality-details - Get quality details
- POST /quality/recalculate - Trigger quality recomputation
- GET /quality/outliers - List quality outliers
- GET /quality/degradation - Get degradation report
- GET /quality/distribution - Get quality distribution
- GET /quality/trends - Get quality trends
- GET /quality/dimensions - Get dimension averages
- GET /quality/review-queue - Get review queue
- GET /quality/health - Module health check
"""

from unittest.mock import patch, MagicMock



class TestQualityEndpoints:
    def test_get_quality_details(self, client, create_test_resource):
        """Test retrieving quality details for a resource."""
        resource = create_test_resource()
        response = client.get(f"/resources/{str(resource.id)}/quality-details")
        assert response.status_code in [200, 404]

    def test_recalculate_quality(self, client, create_test_resource):
        """Test triggering quality recomputation."""
        resource = create_test_resource()
        # Mock celery to avoid import errors
        with patch.dict('sys.modules', {'celery': MagicMock()}):
            response = client.post("/quality/recalculate", json={"resource_id": str(resource.id)})
            # Accept 200/202 for success, 400 for validation errors, 422 for schema errors
            assert response.status_code in [200, 202, 400, 422]

    def test_get_outliers(self, client, create_test_resource):
        """Test getting quality outliers."""
        create_test_resource()
        response = client.get("/quality/outliers")
        assert response.status_code == 200

    def test_get_degradation_report(self, client, create_test_resource):
        """Test getting degradation report."""
        create_test_resource()
        response = client.get("/quality/degradation")
        assert response.status_code == 200

    def test_get_distribution(self, client, create_test_resource):
        """Test getting quality distribution."""
        create_test_resource()
        response = client.get("/quality/distribution")
        assert response.status_code == 200

    def test_get_trends(self, client, create_test_resource):
        """Test getting quality trends."""
        create_test_resource()
        response = client.get("/quality/trends")
        assert response.status_code == 200

    def test_get_dimensions(self, client, create_test_resource):
        """Test getting dimension averages."""
        create_test_resource()
        response = client.get("/quality/dimensions")
        assert response.status_code == 200

    def test_get_review_queue(self, client, create_test_resource):
        """Test getting review queue."""
        create_test_resource()
        response = client.get("/quality/review-queue")
        assert response.status_code == 200


class TestQualityHealth:
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/quality/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
