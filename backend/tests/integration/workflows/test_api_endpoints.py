"""Tests for API endpoints."""

from unittest.mock import patch
import time


class TestResourcesAPI:
    """Test resources API endpoints."""
    
    def _poll_until_completed(self, client, rid: str, timeout_s: float = 5.0):
        deadline = time.time() + timeout_s
        last = None
        while time.time() < deadline:
            resp = client.get(f"/resources/{rid}/status")
            if resp.status_code == 200:
                last = resp.json()
                if last.get("ingestion_status") in {"completed", "failed"}:
                    return last
            time.sleep(0.05)
        return last

    def test_create_resource_success(self, client, test_db, mock_fetch_url, mock_archive_local):
        """Test successful async resource creation via API."""
        payload = {
            "url": "https://example.com/test",
            "title": "Test Article",
            "language": "en"
        }
        
        with patch('backend.app.services.resource_service.ARCHIVE_ROOT', "/tmp"):
            response = client.post("/resources", json=payload)
        
        assert response.status_code == 202
        rid = response.json()["id"]
        status = self._poll_until_completed(client, rid)
        assert status and status["ingestion_status"] == "completed"

        data = client.get(f"/resources/{rid}").json()
        # Check response structure
        assert "id" in data
        assert data["title"] == "Test Article"
        assert data["language"] == "en"
        assert data["quality_score"] > 0
        assert data["classification_code"] is not None
        assert data["read_status"] == "unread"
        assert isinstance(data["subject"], list)
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_resource_minimal_payload(self, client, test_db, mock_fetch_url, mock_archive_local):
        """Test async resource creation with minimal payload (only URL)."""
        payload = {"url": "https://example.com/test"}
        
        with patch('backend.app.services.resource_service.ARCHIVE_ROOT', "/tmp"):
            response = client.post("/resources", json=payload)
        
        assert response.status_code == 202
        rid = response.json()["id"]
        status = self._poll_until_completed(client, rid)
        assert status and status["ingestion_status"] == "completed"
        
        data = client.get(f"/resources/{rid}").json()
        assert data["url"] == "https://example.com/test"
        assert data["title"] is not None  # Should have extracted or fallback title
        assert data["quality_score"] > 0
    
    def test_create_resource_with_all_fields(self, client, test_db, mock_fetch_url, mock_archive_local):
        """Test async resource creation with all optional fields."""
        payload = {
            "url": "https://example.com/test",
            "title": "Custom Title",
            "description": "Custom description",
            "language": "es",
            "type": "book",
            "source": "Custom source"
        }
        
        with patch('backend.app.services.resource_service.ARCHIVE_ROOT', "/tmp"):
            response = client.post("/resources", json=payload)
        
        assert response.status_code == 202
        rid = response.json()["id"]
        self._poll_until_completed(client, rid)
        data = client.get(f"/resources/{rid}").json()
        
        assert data["title"] == "Custom Title"
        assert data["description"] == "Custom description"
        assert data["language"] == "es"
        assert data["type"] == "book"
        assert data["source"] == "Custom source"
    
    def test_create_resource_missing_url(self, client, test_db):
        """Test resource creation without required URL."""
        payload = {"title": "Test Article"}
        
        response = client.post("/resources", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_create_resource_invalid_url(self, client, test_db):
        """Test resource creation with invalid URL format."""
        payload = {"url": "not-a-url"}
        
        response = client.post("/resources", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_create_resource_fetch_error(self, client, test_db):
        """Test resource creation when URL fetching fails."""
        payload = {"url": "https://example.com/test"}
        
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch:
            mock_fetch.side_effect = ValueError("Failed to fetch URL")
            response = client.post("/resources", json=payload)
        
        assert response.status_code == 202  # queued
        rid = response.json()["id"]
        # Poll should eventually fail
        status = self._poll_until_completed(client, rid)
        assert status and status["ingestion_status"] == "failed"
        assert "Failed to fetch URL" in (status.get("ingestion_error") or "")
    
    def test_create_resource_network_timeout(self, client, test_db):
        """Test resource creation with network timeout."""
        payload = {"url": "https://example.com/test"}
        
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch:
            mock_fetch.side_effect = ValueError("Failed to fetch URL: timeout")
            response = client.post("/resources", json=payload)
        
        assert response.status_code == 202
        rid = response.json()["id"]
        status = self._poll_until_completed(client, rid)
        assert status and status["ingestion_status"] == "failed"
        assert "timeout" in (status.get("ingestion_error") or "")
    
    def test_create_resource_http_error(self, client, test_db):
        """Test resource creation with HTTP error."""
        payload = {"url": "https://example.com/notfound"}
        
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch:
            mock_fetch.side_effect = ValueError("Failed to fetch URL: HTTP 404")
            response = client.post("/resources", json=payload)
        
        assert response.status_code == 202
        rid = response.json()["id"]
        status = self._poll_until_completed(client, rid)
        assert status and status["ingestion_status"] == "failed"
        assert "HTTP 404" in (status.get("ingestion_error") or "")
    
    def test_create_resource_archive_error(self, client, test_db, mock_fetch_url):
        """Test resource creation when archiving fails."""
        payload = {"url": "https://example.com/test"}
        
        with patch('backend.app.utils.content_extractor.archive_local') as mock_archive:
            mock_archive.side_effect = Exception("Archive failed")
            response = client.post("/resources", json=payload)
        
        assert response.status_code == 202
        rid = response.json()["id"]
        status = self._poll_until_completed(client, rid)
        assert status and status["ingestion_status"] == "failed"
        assert "Archive failed" in (status.get("ingestion_error") or "")
    
    def test_create_resource_database_error(self, client, test_db, mock_fetch_url, mock_archive_local):
        """Test resource creation when database operation fails."""
        payload = {"url": "https://example.com/test"}
        
        with patch('backend.app.database.models.Resource') as mock_resource:
            mock_resource.side_effect = Exception("Database error")
            response = client.post("/resources", json=payload)
        
        # The pending row creation will fail immediately with 500
        assert response.status_code in (400, 500)
    
    def test_create_resource_content_type_validation(self, client, test_db):
        """Test resource creation with invalid content type."""
        payload = "invalid json"
        
        response = client.post("/resources", data=payload)
        
        assert response.status_code == 422
    
    def test_create_resource_empty_payload(self, client, test_db):
        """Test resource creation with empty payload."""
        response = client.post("/resources", json={})
        
        assert response.status_code == 422
    
    def test_create_resource_null_payload(self, client, test_db):
        """Test resource creation with null payload."""
        response = client.post("/resources", json=None)
        
        assert response.status_code == 422
    
    def test_create_resource_extra_fields(self, client, test_db, mock_fetch_url, mock_archive_local):
        """Test resource creation with extra fields (should be ignored)."""
        payload = {
            "url": "https://example.com/test",
            "title": "Test Article",
            "extra_field": "should be ignored",
            "another_extra": 123
        }
        
        with patch('backend.app.services.resource_service.ARCHIVE_ROOT', "/tmp"):
            response = client.post("/resources", json=payload)
        
        assert response.status_code == 202
        rid = response.json()["id"]
        self._poll_until_completed(client, rid)
        data = client.get(f"/resources/{rid}").json()
        
        # Extra fields should not be in response
        assert "extra_field" not in data
        assert "another_extra" not in data
        assert data["title"] == "Test Article"
    
    def test_create_resource_response_model(self, client, test_db, mock_fetch_url, mock_archive_local):
        """Test that response matches ResourceRead schema after completion."""
        payload = {"url": "https://example.com/test"}
        
        response = client.post("/resources", json=payload)
        assert response.status_code == 202
        rid = response.json()["id"]
        self._poll_until_completed(client, rid)
        data = client.get(f"/resources/{rid}").json()
        
        # Check all required fields from ResourceRead schema
        required_fields = [
            "id", "title", "subject", "relation", "read_status", 
            "quality_score", "created_at", "updated_at"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Check field types
        assert isinstance(data["id"], str)  # UUID as string
        assert isinstance(data["title"], str)
        assert isinstance(data["subject"], list)
        assert isinstance(data["relation"], list)
        assert isinstance(data["quality_score"], (int, float))
        assert data["read_status"] in ["unread", "in_progress", "completed", "archived"]
    
    def test_create_resource_multiple_requests(self, client, test_db, mock_fetch_url, mock_archive_local):
        """Test multiple resource creation requests."""
        payloads = [
            {"url": "https://example.com/test1"},
            {"url": "https://example.com/test2"},
            {"url": "https://example.com/test3"}
        ]
        
        responses = []
        for payload in payloads:
            response = client.post("/resources", json=payload)
            responses.append(response)
        
        # All should be accepted
        for response in responses:
            assert response.status_code == 202
        
        # All should have different IDs and complete
        ids = [resp.json()["id"] for resp in responses]
        assert len(set(ids)) == 3  # All unique
        for rid in ids:
            self._poll_until_completed(client, rid)
    
    def test_create_resource_concurrent_requests(self, client, test_db, mock_fetch_url, mock_archive_local):
        """Test concurrent resource creation requests."""
        import threading
        
        results = []
        errors = []
        
        def create_resource_thread(url):
            try:
                payload = {"url": url}
                response = client.post("/resources", json=payload)
                results.append(response)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        urls = [f"https://example.com/test{i}" for i in range(5)]
        
        for url in urls:
            thread = threading.Thread(target=create_resource_thread, args=(url,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        
        # All should be accepted and eventually complete
        for response in results:
            assert response.status_code == 202
        for resp in results:
            rid = resp.json()["id"]
            self._poll_until_completed(client, rid)


class TestClassificationAPI:
    def test_get_classification_tree(self, client, test_db):
        resp = client.get("/classification/tree")
        assert resp.status_code == 200
        data = resp.json()
        # Should include top-level codes like 000 and 400
        assert "000" in data
        assert data["000"]["title"].lower().startswith("computer")
        assert "400" in data
        assert data["400"]["title"].lower().startswith("language")