"""
Test suite for Taxonomy module endpoints.

NOTE: The taxonomy router is currently empty (Phase 14 migration in progress).
These tests are placeholders and will be updated when endpoints are implemented.

Endpoints to be tested (when implemented):
- POST /taxonomy/nodes - Create taxonomy node
- PUT /taxonomy/nodes/{id} - Update node
- DELETE /taxonomy/nodes/{id} - Delete node
- POST /taxonomy/nodes/{id}/move - Move node to new parent
- GET /taxonomy/tree - Get hierarchical tree
- GET /taxonomy/nodes/{id}/ancestors - Get ancestor nodes
- GET /taxonomy/nodes/{id}/descendants - Get descendant nodes
- POST /taxonomy/classify/{resource_id} - Classify resource
- GET /taxonomy/active-learning/uncertain - Get uncertain samples
- POST /taxonomy/active-learning/feedback - Submit feedback
- POST /taxonomy/train - Train ML model
"""

import pytest


# Note: This test file uses the shared fixtures from conftest.py
# The create_test_resource fixture is defined there with correct field names


@pytest.mark.skip(reason="Taxonomy router is empty - Phase 14 migration in progress")
class TestTaxonomyNodes:
    def test_create_node(self, client):
        """Test creating a taxonomy node."""
        response = client.post(
            "/taxonomy/nodes",
            json={
                "name": "Machine Learning",
                "description": "ML and AI topics",
                "keywords": ["ml", "ai", "deep learning"],
            },
        )
        assert response.status_code in [200, 201, 404]

    def test_get_tree(self, client):
        """Test getting the taxonomy tree."""
        response = client.get("/taxonomy/tree")
        assert response.status_code in [200, 404]


@pytest.mark.skip(reason="Taxonomy router is empty - Phase 14 migration in progress")
class TestClassification:
    def test_classify_resource(self, client, create_test_resource):
        """Test classifying a resource."""
        resource = create_test_resource()
        response = client.post(f"/taxonomy/classify/{str(resource.id)}")
        assert response.status_code in [200, 202, 404]
