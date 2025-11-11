"""
API endpoint tests for quality assessment endpoints.
Tests all quality API endpoints with valid/invalid inputs, pagination, and error handling.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.resource import Resource


@pytest.fixture
def test_resource(db_session: Session):
    """Create test resource with quality scores."""
    resource = Resource(
        title="Test Resource",
        url="https://example.com/test",
        content="Test content for API testing",
        resource_type="article",
        quality_accuracy=0.75,
        quality_completeness=0.70,
        quality_consistency=0.80,
        quality_timeliness=0.65,
        quality_relevance=0.72,
        quality_overall=0.72,
        quality_last_computed=datetime.now(),
        quality_computation_version="1.0"
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)
    return resource


@pytest.fixture
def outlier_resource(db_session: Session):
    """Create outlier resource for testing."""
    resource = Resource(
        title="Outlier Resource",
        url="https://example.com/outlier",
        content="Outlier content",
        resource_type="article",
        quality_accuracy=0.15,
        quality_completeness=0.20,
        quality_consistency=0.18,
        quality_timeliness=0.12,
        quality_relevance=0.16,
        quality_overall=0.16,
        is_quality_outlier=True,
        outlier_score=-0.5,
        outlier_reasons=["low_accuracy", "low_completeness", "low_timeliness"],
        needs_quality_review=True
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)
    return resource


class TestQualityDetailsEndpoint:
    """Tests for GET /resources/{id}/quality-details endpoint."""
    
    def test_get_quality_details_success(self, client: TestClient, test_resource):
        """Test successful retrieval of quality details."""
        response = client.get(f"/resources/{test_resource.id}/quality-details")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["resource_id"] == test_resource.id
        assert "dimensions" in data
        assert data["dimensions"]["accuracy"] == 0.75
        assert data["dimensions"]["completeness"] == 0.70
        assert data["overall_quality"] == 0.72
        assert "metadata" in data
        assert "outlier_status" in data
    
    def test_get_quality_details_not_found(self, client: TestClient):
        """Test quality details for non-existent resource."""
        response = client.get("/resources/99999/quality-details")
        
        assert response.status_code == 404
    
    def test_get_quality_details_no_quality_computed(self, client: TestClient, db_session):
        """Test quality details for resource without quality scores."""
        resource = Resource(
            title="No Quality",
            url="https://example.com/no-quality",
            content="No quality computed",
            resource_type="article"
        )
        db_session.add(resource)
        db_session.commit()
        
        response = client.get(f"/resources/{resource.id}/quality-details")
        
        # Should still return 200 with null values
        assert response.status_code in [200, 404]


class TestQualityRecalculateEndpoint:
    """Tests for POST /quality/recalculate endpoint."""
    
    def test_recalculate_single_resource(self, client: TestClient, test_resource):
        """Test recalculating quality for single resource."""
        response = client.post(
            "/quality/recalculate",
            json={"resource_id": test_resource.id}
        )
        
        assert response.status_code == 202  # Accepted
    
    def test_recalculate_multiple_resources(self, client: TestClient, test_resource, db_session):
        """Test recalculating quality for multiple resources."""
        resource2 = Resource(
            title="Test 2",
            url="https://example.com/test2",
            content="Test content 2",
            resource_type="article"
        )
        db_session.add(resource2)
        db_session.commit()
        
        response = client.post(
            "/quality/recalculate",
            json={"resource_ids": [test_resource.id, resource2.id]}
        )
        
        assert response.status_code == 202
    
    def test_recalculate_with_custom_weights(self, client: TestClient, test_resource):
        """Test recalculation with custom weights."""
        response = client.post(
            "/quality/recalculate",
            json={
                "resource_id": test_resource.id,
                "custom_weights": {
                    "accuracy": 0.3,
                    "completeness": 0.2,
                    "consistency": 0.2,
                    "timeliness": 0.15,
                    "relevance": 0.15
                }
            }
        )
        
        assert response.status_code == 202
    
    def test_recalculate_invalid_weights_sum(self, client: TestClient, test_resource):
        """Test recalculation with invalid weight sum."""
        response = client.post(
            "/quality/recalculate",
            json={
                "resource_id": test_resource.id,
                "custom_weights": {
                    "accuracy": 0.5,
                    "completeness": 0.3,
                    "consistency": 0.3,
                    "timeliness": 0.1,
                    "relevance": 0.1
                }
            }
        )
        
        assert response.status_code == 400  # Bad request
    
    def test_recalculate_missing_dimension(self, client: TestClient, test_resource):
        """Test recalculation with missing dimension in weights."""
        response = client.post(
            "/quality/recalculate",
            json={
                "resource_id": test_resource.id,
                "custom_weights": {
                    "accuracy": 0.5,
                    "completeness": 0.5
                }
            }
        )
        
        assert response.status_code == 400


class TestOutliersEndpoint:
    """Tests for GET /quality/outliers endpoint."""
    
    def test_get_outliers_success(self, client: TestClient, outlier_resource):
        """Test successful retrieval of outliers."""
        response = client.get("/quality/outliers")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "outliers" in data
        assert "total" in data
        assert data["total"] >= 1
        
        outlier = data["outliers"][0]
        assert "resource_id" in outlier
        assert "title" in outlier
        assert "outlier_score" in outlier
        assert "reasons" in outlier
    
    def test_get_outliers_with_pagination(self, client: TestClient, outlier_resource):
        """Test outliers endpoint with pagination."""
        response = client.get("/quality/outliers?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["outliers"]) <= 10
    
    def test_get_outliers_filter_by_score(self, client: TestClient, outlier_resource):
        """Test filtering outliers by minimum score."""
        response = client.get("/quality/outliers?min_outlier_score=-0.6")
        
        assert response.status_code == 200
        data = response.json()
        
        for outlier in data["outliers"]:
            assert outlier["outlier_score"] >= -0.6
    
    def test_get_outliers_filter_by_reason(self, client: TestClient, outlier_resource):
        """Test filtering outliers by specific reason."""
        response = client.get("/quality/outliers?reason=low_accuracy")
        
        assert response.status_code == 200
        data = response.json()
        
        for outlier in data["outliers"]:
            assert "low_accuracy" in outlier["reasons"]
    
    def test_get_outliers_empty_result(self, client: TestClient, test_resource):
        """Test outliers endpoint when no outliers exist."""
        response = client.get("/quality/outliers")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 0
        assert isinstance(data["outliers"], list)


class TestDegradationEndpoint:
    """Tests for GET /quality/degradation endpoint."""
    
    def test_get_degradation_report(self, client: TestClient, db_session):
        """Test degradation report endpoint."""
        # Create resource with old quality
        resource = Resource(
            title="Old Quality",
            url="https://example.com/old",
            content="Old content",
            resource_type="article",
            quality_overall=0.9,
            quality_last_computed=datetime.now() - timedelta(days=35)
        )
        db_session.add(resource)
        db_session.commit()
        
        response = client.get("/quality/degradation?time_window_days=30")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "degraded_resources" in data
        assert "total_checked" in data
        assert isinstance(data["degraded_resources"], list)
    
    def test_get_degradation_custom_window(self, client: TestClient):
        """Test degradation report with custom time window."""
        response = client.get("/quality/degradation?time_window_days=60")
        
        assert response.status_code == 200
    
    def test_get_degradation_invalid_window(self, client: TestClient):
        """Test degradation report with invalid time window."""
        response = client.get("/quality/degradation?time_window_days=-10")
        
        assert response.status_code == 400


class TestSummaryEvaluationEndpoint:
    """Tests for POST /summaries/{id}/evaluate endpoint."""
    
    def test_evaluate_summary_success(self, client: TestClient, db_session):
        """Test successful summary evaluation."""
        resource = Resource(
            title="With Summary",
            url="https://example.com/summary",
            content="Content for summary evaluation",
            summary="Brief summary",
            resource_type="article"
        )
        db_session.add(resource)
        db_session.commit()
        
        response = client.post(f"/summaries/{resource.id}/evaluate")
        
        assert response.status_code == 202  # Accepted
    
    def test_evaluate_summary_with_g_eval(self, client: TestClient, db_session):
        """Test summary evaluation with G-Eval enabled."""
        resource = Resource(
            title="With Summary",
            url="https://example.com/summary",
            content="Content",
            summary="Summary",
            resource_type="article"
        )
        db_session.add(resource)
        db_session.commit()
        
        response = client.post(
            f"/summaries/{resource.id}/evaluate?use_g_eval=true"
        )
        
        assert response.status_code == 202
    
    def test_evaluate_summary_no_summary(self, client: TestClient, test_resource):
        """Test evaluation when resource has no summary."""
        response = client.post(f"/summaries/{test_resource.id}/evaluate")
        
        assert response.status_code in [400, 404]


class TestQualityDistributionEndpoint:
    """Tests for GET /quality/distribution endpoint."""
    
    def test_get_distribution_default(self, client: TestClient, test_resource):
        """Test quality distribution with defaults."""
        response = client.get("/quality/distribution")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "distribution" in data
        assert "statistics" in data
        assert "mean" in data["statistics"]
        assert "median" in data["statistics"]
        assert "std_dev" in data["statistics"]
    
    def test_get_distribution_specific_dimension(self, client: TestClient, test_resource):
        """Test distribution for specific dimension."""
        response = client.get("/quality/distribution?dimension=accuracy")
        
        assert response.status_code == 200
        data = response.json()
        assert "distribution" in data
    
    def test_get_distribution_custom_bins(self, client: TestClient, test_resource):
        """Test distribution with custom bin count."""
        response = client.get("/quality/distribution?bins=20")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["distribution"]) <= 20


class TestQualityTrendsEndpoint:
    """Tests for GET /quality/trends endpoint."""
    
    def test_get_trends_daily(self, client: TestClient, test_resource):
        """Test quality trends with daily granularity."""
        response = client.get("/quality/trends?granularity=daily")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "trends" in data
        assert isinstance(data["trends"], list)
    
    def test_get_trends_with_date_range(self, client: TestClient, test_resource):
        """Test trends with specific date range."""
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
        end_date = datetime.now().isoformat()
        
        response = client.get(
            f"/quality/trends?start_date={start_date}&end_date={end_date}"
        )
        
        assert response.status_code == 200


class TestDimensionAveragesEndpoint:
    """Tests for GET /quality/dimensions endpoint."""
    
    def test_get_dimension_averages(self, client: TestClient, test_resource):
        """Test dimension averages endpoint."""
        response = client.get("/quality/dimensions")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "dimensions" in data
        assert "total_resources" in data
        
        dimensions = data["dimensions"]
        assert "accuracy" in dimensions
        assert "completeness" in dimensions
        assert "consistency" in dimensions
        assert "timeliness" in dimensions
        assert "relevance" in dimensions
        
        for dim_data in dimensions.values():
            assert "average" in dim_data
            assert "min" in dim_data
            assert "max" in dim_data


class TestReviewQueueEndpoint:
    """Tests for GET /quality/review-queue endpoint."""
    
    def test_get_review_queue(self, client: TestClient, outlier_resource):
        """Test review queue endpoint."""
        response = client.get("/quality/review-queue")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "queue" in data
        assert "total" in data
        assert data["total"] >= 1
    
    def test_get_review_queue_with_pagination(self, client: TestClient, outlier_resource):
        """Test review queue with pagination."""
        response = client.get("/quality/review-queue?skip=0&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["queue"]) <= 5
    
    def test_get_review_queue_sort_by_score(self, client: TestClient, outlier_resource):
        """Test review queue sorted by outlier score."""
        response = client.get("/quality/review-queue?sort_by=outlier_score")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify sorting
        if len(data["queue"]) > 1:
            scores = [item["outlier_score"] for item in data["queue"] if item.get("outlier_score")]
            assert scores == sorted(scores)
    
    def test_get_review_queue_empty(self, client: TestClient, test_resource):
        """Test review queue when empty."""
        response = client.get("/quality/review-queue")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["queue"], list)
