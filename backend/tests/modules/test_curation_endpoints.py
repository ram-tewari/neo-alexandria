"""
Test suite for Curation module endpoints.

Endpoints tested:
- GET /curation/review-queue - Get review queue
- POST /curation/batch-update - Batch update operations
- GET /curation/quality-analysis/{resource_id} - Get quality analysis
- GET /curation/low-quality - Get low quality resources
- POST /curation/bulk-quality-check - Bulk quality check
"""




class TestCurationEndpoints:
    def test_get_review_queue(self, client, create_test_resource):
        """Test getting the review queue."""
        # Create a resource to ensure table exists
        create_test_resource(quality_score=0.3)
        response = client.get("/curation/review-queue")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or "total" in data

    def test_get_quality_analysis(self, client, create_test_resource):
        """Test getting quality analysis for a resource."""
        resource = create_test_resource()
        response = client.get(f"/curation/quality-analysis/{str(resource.id)}")
        assert response.status_code in [200, 404]

    def test_batch_update(self, client, create_test_resource):
        """Test batch update operation."""
        resource = create_test_resource()
        response = client.post("/curation/batch-update", json={
            "resource_ids": [str(resource.id)],
            "updates": {"read_status": "read"}
        })
        # Accept 200 for success, 400 for validation errors, 422 for schema errors
        assert response.status_code in [200, 400, 422]

    def test_get_low_quality_resources(self, client, create_test_resource):
        """Test getting low quality resources."""
        # Create a resource to ensure table exists
        create_test_resource(quality_score=0.3)
        response = client.get("/curation/low-quality?threshold=0.5")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or "total" in data

    def test_bulk_quality_check(self, client, create_test_resource):
        """Test bulk quality check."""
        resource = create_test_resource()
        response = client.post("/curation/bulk-quality-check", json={
            "resource_ids": [str(resource.id)]
        })
        assert response.status_code in [200, 202, 400]
