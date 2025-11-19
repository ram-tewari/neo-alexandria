"""Tests for new curation API endpoints."""

import uuid
from datetime import datetime, timedelta, timezone
import pytest

from backend.app.database.models import Resource


@pytest.fixture
def quality_test_resources(test_db):
    """Create test resources with different quality scores for endpoint testing."""
    TestingSessionLocal = test_db
    db = TestingSessionLocal()
    now = datetime.now(timezone.utc)
    items = []
    
    # Create resources with different quality levels
    quality_configs = [
        {"score": 0.3, "title": "Low Quality Article", "description": "Short desc"},
        {"score": 0.6, "title": "Medium Quality Article", "description": "Better description with more detail"},
        {"score": 0.9, "title": "High Quality Article", "description": "Comprehensive description with detailed analysis"},
        {"score": 0.4, "title": "Another Low Quality", "description": "Brief"},
        {"score": 0.7, "title": "Another Medium Quality", "description": "Good description"},
    ]
    
    for i, config in enumerate(quality_configs):
        quality = config["score"]
        r = Resource(
            title=config["title"],
            description=config["description"],
            language="en",
            type="article",
            classification_code="006",
            subject=["test", "quality"],
            read_status="unread",
            quality_score=quality,
            # Add quality dimensions for Phase 9 compatibility
            quality_overall=quality,
            quality_accuracy=min(1.0, quality + 0.03),
            quality_completeness=min(1.0, quality - 0.02),
            quality_consistency=min(1.0, quality + 0.01),
            quality_timeliness=min(1.0, quality - 0.01),
            quality_relevance=min(1.0, quality + 0.02),
            creator="Test Author",
            identifier=f"/archive/2024/01/01/article-{i}",
            source="https://example.com/article",
            date_created=now - timedelta(days=30 - i),
            date_modified=now - timedelta(days=15 - i),
        )
        db.add(r)
        items.append(r)
    
    db.commit()
    # Extract IDs before closing session
    item_ids = [str(item.id) for item in items]
    db.close()
    return item_ids


class TestQualityAnalysisEndpoint:
    """Test the quality analysis endpoint."""

    def test_quality_analysis_success(self, client, test_db, quality_test_resources):
        """Test successful quality analysis request."""
        resource_id = quality_test_resources[0]
        
        # Mock the text file reading
        mock_text = """
        This is a comprehensive article about machine learning and artificial intelligence.
        It covers various algorithms and their applications in real-world scenarios.
        The content is well-structured with clear explanations and examples.
        """
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr("pathlib.Path.exists", lambda self: True)
            m.setattr("pathlib.Path.read_text", lambda self, encoding: mock_text)
            
            resp = client.get(f"/curation/quality-analysis/{resource_id}")
            assert resp.status_code == 200
            
            data = resp.json()
            
            # Check response structure
            required_fields = [
                "resource_id", "metadata_completeness", "readability",
                "source_credibility", "content_depth", "overall_quality",
                "quality_level", "suggestions"
            ]
            for field in required_fields:
                assert field in data
            
            # Check data types and ranges
            assert data["resource_id"] == resource_id
            assert 0 <= data["metadata_completeness"] <= 1
            assert 0 <= data["source_credibility"] <= 1
            assert 0 <= data["content_depth"] <= 1
            assert 0 <= data["overall_quality"] <= 1
            assert data["quality_level"] in ["HIGH", "MEDIUM", "LOW"]
            assert isinstance(data["suggestions"], list)
            
            # Check readability structure
            readability = data["readability"]
            assert "reading_ease" in readability
            assert "fk_grade" in readability
            assert "word_count" in readability
            assert "sentence_count" in readability

    def test_quality_analysis_invalid_uuid(self, client):
        """Test quality analysis with invalid UUID."""
        resp = client.get("/curation/quality-analysis/invalid-uuid")
        assert resp.status_code == 400
        assert "Invalid resource id" in resp.json()["detail"]

    def test_quality_analysis_nonexistent_resource(self, client):
        """Test quality analysis with non-existent resource."""
        fake_id = str(uuid.uuid4())
        resp = client.get(f"/curation/quality-analysis/{fake_id}")
        assert resp.status_code == 404
        assert "Resource not found" in resp.json()["detail"]

    def test_quality_analysis_with_suggestions(self, client, test_db, quality_test_resources):
        """Test that quality analysis includes actionable suggestions."""
        # Use a low-quality resource to ensure we get suggestions
        resource_id = quality_test_resources[0]  # Low quality (0.3)
        
        mock_text = "Short content."
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr("pathlib.Path.exists", lambda self: True)
            m.setattr("pathlib.Path.read_text", lambda self, encoding: mock_text)
            
            resp = client.get(f"/curation/quality-analysis/{resource_id}")
            assert resp.status_code == 200
            
            data = resp.json()
            suggestions = data["suggestions"]
            
            # Should have suggestions for low-quality resource
            assert len(suggestions) > 0
            assert isinstance(suggestions, list)
            
            # Check that suggestions are actionable
            suggestion_text = " ".join(suggestions).lower()
            assert any(keyword in suggestion_text for keyword in [
                "metadata", "readability", "content", "source", "quality"
            ])


class TestLowQualityEndpoint:
    """Test the low quality filtering endpoint."""

    def test_low_quality_default_threshold(self, client, quality_test_resources):
        """Test low quality endpoint with default threshold."""
        resp = client.get("/curation/low-quality")
        assert resp.status_code == 200
        
        data = resp.json()
        assert "items" in data
        assert "total" in data
        
        # Default threshold is 0.5, so should return items with score < 0.5
        items = data["items"]
        for item in items:
            assert item["quality_score"] < 0.5

    def test_low_quality_custom_threshold(self, client, quality_test_resources):
        """Test low quality endpoint with custom threshold."""
        resp = client.get("/curation/low-quality?threshold=0.7")
        assert resp.status_code == 200
        
        data = resp.json()
        items = data["items"]
        
        # Should return items with score < 0.7
        for item in items:
            assert item["quality_score"] < 0.7

    def test_low_quality_pagination(self, client, quality_test_resources):
        """Test low quality endpoint pagination."""
        resp1 = client.get("/curation/low-quality?limit=2&offset=0")
        resp2 = client.get("/curation/low-quality?limit=2&offset=2")
        
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        
        data1 = resp1.json()
        data2 = resp2.json()
        
        # Should have different items (unless there are fewer than 4 low-quality items)
        if len(data1["items"]) == 2 and len(data2["items"]) > 0:
            assert data1["items"] != data2["items"]

    def test_low_quality_high_threshold(self, client, quality_test_resources):
        """Test low quality endpoint with high threshold (should return more items)."""
        resp = client.get("/curation/low-quality?threshold=0.9")
        assert resp.status_code == 200
        
        data = resp.json()
        items = data["items"]
        
        # Should return items with score < 0.9 (most items)
        for item in items:
            assert item["quality_score"] < 0.9

    def test_low_quality_low_threshold(self, client, quality_test_resources):
        """Test low quality endpoint with low threshold (should return fewer items)."""
        resp = client.get("/curation/low-quality?threshold=0.2")
        assert resp.status_code == 200
        
        data = resp.json()
        items = data["items"]
        
        # Should return items with score < 0.2 (very few items)
        for item in items:
            assert item["quality_score"] < 0.2


class TestBulkQualityCheckEndpoint:
    """Test the bulk quality check endpoint."""

    def test_bulk_quality_check_success(self, client, test_db, quality_test_resources):
        """Test successful bulk quality check."""
        # Use first two resources
        resource_ids = quality_test_resources[:2]
        
        mock_text = """
        This is a comprehensive article with good content and structure.
        It provides detailed information and analysis on the topic.
        The writing is clear and well-organized with proper explanations.
        """
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr("pathlib.Path.exists", lambda self: True)
            m.setattr("pathlib.Path.read_text", lambda self, encoding: mock_text)
            
            payload = {"resource_ids": resource_ids}
            resp = client.post("/curation/bulk-quality-check", json=payload)
            
            assert resp.status_code == 200
            data = resp.json()
            
            assert "updated_count" in data
            assert "failed_ids" in data
            assert data["updated_count"] == 2
            assert len(data["failed_ids"]) == 0

    def test_bulk_quality_check_with_failures(self, client, test_db, quality_test_resources):
        """Test bulk quality check with some invalid resource IDs."""
        # Mix valid and invalid IDs
        valid_id = quality_test_resources[0]
        invalid_id = str(uuid.uuid4())
        resource_ids = [valid_id, invalid_id]
        
        mock_text = "Some test content for quality analysis."
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr("pathlib.Path.exists", lambda self: True)
            m.setattr("pathlib.Path.read_text", lambda self, encoding: mock_text)
            
            payload = {"resource_ids": resource_ids}
            resp = client.post("/curation/bulk-quality-check", json=payload)
            
            assert resp.status_code == 200
            data = resp.json()
            
            assert data["updated_count"] == 1
            assert len(data["failed_ids"]) == 1
            assert data["failed_ids"][0] == invalid_id

    def test_bulk_quality_check_empty_list(self, client):
        """Test bulk quality check with empty resource list."""
        payload = {"resource_ids": []}
        resp = client.post("/curation/bulk-quality-check", json=payload)
        
        assert resp.status_code == 400
        assert "No resource ids provided" in resp.json()["detail"]

    def test_bulk_quality_check_invalid_uuid(self, client):
        """Test bulk quality check with invalid UUID in list."""
        payload = {"resource_ids": ["invalid-uuid"]}
        resp = client.post("/curation/bulk-quality-check", json=payload)
        
        assert resp.status_code == 400
        assert "Invalid resource id in list" in resp.json()["detail"]

    def test_bulk_quality_check_missing_field(self, client):
        """Test bulk quality check with missing resource_ids field."""
        payload = {}
        resp = client.post("/curation/bulk-quality-check", json=payload)
        
        assert resp.status_code == 422  # Validation error

    def test_bulk_quality_check_updates_scores(self, client, test_db, quality_test_resources):
        """Test that bulk quality check actually updates quality scores."""
        resource_id = quality_test_resources[0]
        
        # Get initial quality score
        initial_resp = client.get(f"/resources/{resource_id}")
        initial_score = initial_resp.json()["quality_score"]
        
        # Mock high-quality content
        mock_text = """
        This is an exceptionally comprehensive and well-written article that demonstrates
        excellent research methodology and clear communication. The content is thorough,
        well-structured, and provides valuable insights into the subject matter.
        The analysis is detailed and the conclusions are well-supported by evidence.
        """
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr("pathlib.Path.exists", lambda self: True)
            m.setattr("pathlib.Path.read_text", lambda self, encoding: mock_text)
            
            payload = {"resource_ids": [resource_id]}
            resp = client.post("/curation/bulk-quality-check", json=payload)
            
            assert resp.status_code == 200
            
            # Check that quality score was updated
            updated_resp = client.get(f"/resources/{resource_id}")
            updated_score = updated_resp.json()["quality_score"]
            
            # Score should have changed (likely increased due to better content)
            assert updated_score != initial_score


class TestEndpointIntegration:
    """Test integration between different quality endpoints."""

    def test_quality_analysis_and_bulk_check_consistency(self, client, test_db, quality_test_resources):
        """Test that quality analysis and bulk check produce consistent results."""
        resource_id = quality_test_resources[0]
        
        mock_text = """
        This is a comprehensive article with detailed analysis and clear structure.
        The content provides valuable insights and is well-organized.
        """
        
        with pytest.MonkeyPatch().context() as m:
            m.setattr("pathlib.Path.exists", lambda self: True)
            m.setattr("pathlib.Path.read_text", lambda self, encoding: mock_text)
            
            # Get quality analysis
            analysis_resp = client.get(f"/curation/quality-analysis/{resource_id}")
            assert analysis_resp.status_code == 200
            analysis_data = analysis_resp.json()
            analysis_score = analysis_data["overall_quality"]
            
            # Perform bulk quality check
            payload = {"resource_ids": [resource_id]}
            bulk_resp = client.post("/curation/bulk-quality-check", json=payload)
            assert bulk_resp.status_code == 200
            
            # Get updated resource
            resource_resp = client.get(f"/resources/{resource_id}")
            assert resource_resp.status_code == 200
            updated_score = resource_resp.json()["quality_score"]
            
            # Scores should be consistent (allowing for small floating point differences)
            assert abs(analysis_score - updated_score) < 0.01

    def test_low_quality_filtering_consistency(self, client, quality_test_resources):
        """Test that low quality endpoint is consistent with review queue."""
        # Test with same threshold
        threshold = 0.6
        
        low_quality_resp = client.get(f"/curation/low-quality?threshold={threshold}")
        review_queue_resp = client.get(f"/curation/review-queue?threshold={threshold}")
        
        assert low_quality_resp.status_code == 200
        assert review_queue_resp.status_code == 200
        
        low_quality_data = low_quality_resp.json()
        review_queue_data = review_queue_resp.json()
        
        # Both should return items below the threshold
        for item in low_quality_data["items"]:
            assert item["quality_score"] < threshold
        
        for item in review_queue_data["items"]:
            assert item["quality_score"] < threshold
