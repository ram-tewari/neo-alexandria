"""
Test suite for Authority module endpoints.

Endpoints tested:
- GET /authority/subjects/suggest - Get subject suggestions
- GET /authority/classification/tree - Get classification tree
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestAuthorityEndpoints:
    def test_get_subject_suggestions(self, client):
        """Test getting subject suggestions based on partial input."""
        response = client.get("/authority/subjects/suggest?q=machine")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_classification_tree(self, client):
        """Test getting the hierarchical classification tree."""
        response = client.get("/authority/classification/tree")
        assert response.status_code == 200
        data = response.json()
        # The response should be a dictionary or list structure
        assert data is not None
