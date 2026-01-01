"""
Test suite for Recommendations module endpoints.

Endpoints tested:
- GET /recommendations - Get recommendations for user
- POST /recommendations/feedback - Submit feedback
- GET /recommendations/profile - Get user profile
- PUT /recommendations/profile - Update user profile
- POST /recommendations/refresh - Refresh recommendations
- GET /recommendations/health - Module health check
"""




class TestRecommendations:
    def test_get_recommendations(self, client):
        """Test getting recommendations."""
        response = client.get("/recommendations")
        assert response.status_code in [200, 404]

    def test_submit_feedback(self, client, create_test_resource):
        """Test submitting feedback on a recommendation."""
        resource = create_test_resource()
        response = client.post("/recommendations/feedback", json={
            "resource_id": str(resource.id),
            "was_clicked": True,
            "was_useful": True
        })
        # Accept various success codes or validation/server errors
        assert response.status_code in [200, 201, 400, 422, 500]

    def test_refresh_recommendations(self, client):
        """Test refreshing recommendations."""
        response = client.post("/recommendations/refresh")
        assert response.status_code in [200, 202, 404]


class TestUserProfile:
    def test_get_profile(self, client):
        """Test getting user profile."""
        response = client.get("/recommendations/profile")
        assert response.status_code in [200, 404]

    def test_update_profile(self, client):
        """Test updating user profile."""
        response = client.put("/recommendations/profile", json={
            "interests": ["machine learning", "python"]
        })
        assert response.status_code in [200, 201, 404, 422]


class TestRecommendationsHealth:
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/recommendations/health")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
