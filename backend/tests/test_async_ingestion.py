"""Tests for async ingestion functionality."""

import pytest
import time
from unittest.mock import patch, Mock
from pathlib import Path

from backend.app.services.resource_service import (
    create_pending_resource, process_ingestion, get_resource
)
from backend.app.database.models import Resource
from backend.app.services.ai_core import AICore


class TestPendingResourceCreation:
    """Test pending resource creation functionality."""
    
    def test_create_pending_resource_success(self, test_db):
        """Test successful pending resource creation."""
        db = test_db()
        payload = {
            "url": "https://example.com/test",
            "title": "Test Article",
            "language": "en"
        }
        
        resource = create_pending_resource(db, payload)
        
        assert isinstance(resource, Resource)
        assert resource.title == "Test Article"
        assert resource.language == "en"
        assert resource.source == "https://example.com/test"
        assert resource.ingestion_status == "pending"
        assert resource.ingestion_error is None
        assert resource.ingestion_started_at is None
        assert resource.ingestion_completed_at is None
        assert resource.quality_score == 0.0
        assert resource.classification_code is None
    
    def test_create_pending_resource_missing_url(self, test_db):
        """Test pending resource creation with missing URL."""
        db = test_db()
        payload = {"title": "Test Article"}
        
        with pytest.raises(ValueError, match="url is required"):
            create_pending_resource(db, payload)
    
    def test_create_pending_resource_idempotent(self, test_db):
        """Test pending resource creation is idempotent for same URL."""
        db = test_db()
        payload = {"url": "https://example.com/test"}
        
        # Create first resource
        resource1 = create_pending_resource(db, payload)
        
        # Create second resource with same URL
        resource2 = create_pending_resource(db, payload)
        
        # Should return the same resource
        assert resource1.id == resource2.id
        assert resource1.source == resource2.source
    
    def test_create_pending_resource_authority_normalization(self, test_db):
        """Test pending resource creation applies authority normalization."""
        db = test_db()
        payload = {
            "url": "https://example.com/test",
            "creator": "doe, john",
            "publisher": "O'REILLY MEDIA"
        }
        
        resource = create_pending_resource(db, payload)
        
        assert resource.creator == "John Doe"
        assert resource.publisher == "O'Reilly Media"


class TestBackgroundIngestion:
    """Test background ingestion processing."""
    
    def test_process_ingestion_success(self, test_db, temp_dir):
        """Test successful background ingestion processing."""
        db = test_db()
        
        # Create pending resource
        payload = {"url": "https://example.com/test"}
        resource = create_pending_resource(db, payload)
        resource_id = str(resource.id)
        db.close()
        
        # Mock external dependencies
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.utils.content_extractor.extract_from_fetched') as mock_extract, \
             patch('backend.app.services.resource_service.AICore') as mock_ai_core_class:
            
            mock_fetch.return_value = {
                "url": "https://example.com/test",
                "status": 200,
                "html": "<html><head><title>Test</title></head><body><p>Test content</p></body></html>",
                "content_type": "text/html"
            }
            
            mock_extract.return_value = {
                "title": "Test",
                "text": "Test content about machine learning"
            }
            
            mock_ai_core = Mock()
            mock_ai_core.generate_summary.return_value = "Summary about ML"
            mock_ai_core.generate_tags.return_value = ["Machine Learning", "AI"]
            mock_ai_core.generate_embedding.return_value = [0.1, 0.2, 0.3]  # Mock embedding
            mock_ai_core_class.return_value = mock_ai_core
            
            # Process ingestion with test database URL
            db_for_url = test_db()
            engine_url = str(db_for_url.get_bind().url)
            db_for_url.close()
            process_ingestion(resource_id, archive_root=temp_dir, ai=mock_ai_core, engine_url=engine_url)
        
        # Verify resource was updated
        db = test_db()
        updated_resource = get_resource(db, resource_id)
        
        assert updated_resource.ingestion_status == "completed"
        assert updated_resource.ingestion_error is None
        assert updated_resource.ingestion_started_at is not None
        assert updated_resource.ingestion_completed_at is not None
        assert updated_resource.title == "Test"
        assert updated_resource.description == "Summary about ML"
        assert "Machine Learning" in updated_resource.subject
        assert updated_resource.quality_score > 0
        assert updated_resource.classification_code is not None
        assert updated_resource.identifier is not None
    
    def test_process_ingestion_fetch_error(self, test_db):
        """Test background ingestion handles fetch errors."""
        db = test_db()
        
        payload = {"url": "https://example.com/test"}
        resource = create_pending_resource(db, payload)
        resource_id = str(resource.id)
        db.close()
        
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch:
            mock_fetch.side_effect = ValueError("Network error")
            
            # Get test database URL
            db_for_url = test_db()
            engine_url = str(db_for_url.get_bind().url)
            db_for_url.close()
            process_ingestion(resource_id, engine_url=engine_url)
        
        # Verify resource was marked as failed
        db = test_db()
        failed_resource = get_resource(db, resource_id)
        
        assert failed_resource.ingestion_status == "failed"
        assert "Network error" in (failed_resource.ingestion_error or "")
        assert failed_resource.ingestion_started_at is not None
        assert failed_resource.ingestion_completed_at is not None
    
    def test_process_ingestion_ai_error(self, test_db, temp_dir):
        """Test background ingestion handles AI processing errors."""
        db = test_db()
        
        payload = {"url": "https://example.com/test"}
        resource = create_pending_resource(db, payload)
        resource_id = str(resource.id)
        db.close()
        
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.utils.content_extractor.extract_from_fetched') as mock_extract, \
             patch('backend.app.services.resource_service.AICore') as mock_ai_core_class:
            
            mock_fetch.return_value = {
                "url": "https://example.com/test",
                "status": 200,
                "html": "<html><body>Test</body></html>",
                "content_type": "text/html"
            }
            
            mock_extract.return_value = {
                "title": "Test",
                "text": "Test content"
            }
            
            mock_ai_core = Mock()
            mock_ai_core.generate_summary.side_effect = Exception("AI processing error")
            mock_ai_core_class.return_value = mock_ai_core
            
            # Get test database URL
            db_for_url = test_db()
            engine_url = str(db_for_url.get_bind().url)
            db_for_url.close()
            process_ingestion(resource_id, archive_root=temp_dir, engine_url=engine_url)
        
        # Verify resource was marked as failed
        db = test_db()
        failed_resource = get_resource(db, resource_id)
        
        assert failed_resource.ingestion_status == "failed"
        assert "AI processing error" in (failed_resource.ingestion_error or "")
    
    def test_process_ingestion_nonexistent_resource(self, test_db):
        """Test background ingestion handles nonexistent resource."""
        # Get test database URL
        db_for_url = test_db()
        engine_url = str(db_for_url.get_bind().url)
        db_for_url.close()
        # Process ingestion for non-existent resource
        process_ingestion("00000000-0000-0000-0000-000000000000", engine_url=engine_url)
        
        # Should not raise exception
        assert True
    
    def test_process_ingestion_custom_ai_core(self, test_db, temp_dir):
        """Test background ingestion with custom AI core."""
        db = test_db()
        
        payload = {"url": "https://example.com/test"}
        resource = create_pending_resource(db, payload)
        resource_id = str(resource.id)
        db.close()
        
        # Create custom AI core
        custom_ai = Mock()
        custom_ai.generate_summary.return_value = "Custom summary"
        custom_ai.generate_tags.return_value = ["Custom Tag"]
        custom_ai.generate_embedding.return_value = [0.1, 0.2, 0.3]  # Mock embedding
        
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.utils.content_extractor.extract_from_fetched') as mock_extract:
            
            mock_fetch.return_value = {
                "url": "https://example.com/test",
                "status": 200,
                "html": "<html><body>Test</body></html>",
                "content_type": "text/html"
            }
            
            mock_extract.return_value = {
                "title": "Test",
                "text": "Test content"
            }
            
            # Get test database URL
            db_for_url = test_db()
            engine_url = str(db_for_url.get_bind().url)
            db_for_url.close()
            process_ingestion(resource_id, archive_root=temp_dir, ai=custom_ai, engine_url=engine_url)
        
        # Verify custom AI core was used
        custom_ai.generate_summary.assert_called_once()
        custom_ai.generate_tags.assert_called_once()
        
        # Verify resource was updated
        db = test_db()
        updated_resource = get_resource(db, resource_id)
        
        assert updated_resource.ingestion_status == "completed"
        assert updated_resource.description == "Custom summary"
        assert "Custom Tag" in updated_resource.subject


class TestAsyncIngestionIntegration:
    """Test async ingestion integration with API."""
    
    def test_async_ingestion_flow(self, client, test_db, temp_dir):
        """Test complete async ingestion flow via API."""
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.services.resource_service.ARCHIVE_ROOT', temp_dir), \
             patch('backend.app.services.resource_service.AICore') as mock_ai_core_class:
            
            mock_fetch.return_value = {
                "url": "https://example.com/test",
                "status": 200,
                "html": "<html><head><title>Test</title></head><body><p>Test content</p></body></html>",
                "content_type": "text/html"
            }
            
            # Mock AI core to generate some tags
            mock_ai_core = Mock()
            mock_ai_core.generate_summary.return_value = "A test article about content"
            mock_ai_core.generate_tags.return_value = ["Test", "Content"]
            mock_ai_core.generate_embedding.return_value = [0.1, 0.2, 0.3]  # Mock embedding
            mock_ai_core_class.return_value = mock_ai_core
            
            # Submit ingestion request
            response = client.post("/resources", json={"url": "https://example.com/test"})
            assert response.status_code == 202
            
            data = response.json()
            resource_id = data["id"]
            assert data["status"] == "pending"
            
            # Poll status until completion
            max_attempts = 50
            for _ in range(max_attempts):
                status_response = client.get(f"/resources/{resource_id}/status")
                assert status_response.status_code == 200
                
                status_data = status_response.json()
                if status_data["ingestion_status"] in ["completed", "failed"]:
                    break
                time.sleep(0.1)
            else:
                pytest.fail("Ingestion did not complete within timeout")
            
            # Verify completion
            assert status_data["ingestion_status"] == "completed"
            assert status_data["ingestion_error"] is None
            assert status_data["ingestion_started_at"] is not None
            assert status_data["ingestion_completed_at"] is not None
            
            # Fetch full resource
            resource_response = client.get(f"/resources/{resource_id}")
            assert resource_response.status_code == 200
            
            resource_data = resource_response.json()
            assert resource_data["title"] == "Test"
            assert resource_data["quality_score"] > 0
            assert resource_data["classification_code"] is not None
            assert len(resource_data["subject"]) > 0
    
    def test_async_ingestion_failure_flow(self, client, test_db):
        """Test async ingestion failure flow via API."""
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch:
            mock_fetch.side_effect = ValueError("Network error")
            
            # Submit ingestion request
            response = client.post("/resources", json={"url": "https://example.com/test"})
            assert response.status_code == 202
            
            data = response.json()
            resource_id = data["id"]
            
            # Poll status until failure
            max_attempts = 50
            for _ in range(max_attempts):
                status_response = client.get(f"/resources/{resource_id}/status")
                assert status_response.status_code == 200
                
                status_data = status_response.json()
                if status_data["ingestion_status"] == "failed":
                    break
                time.sleep(0.1)
            else:
                pytest.fail("Ingestion did not fail within timeout")
            
            # Verify failure
            assert status_data["ingestion_status"] == "failed"
            assert "Network error" in (status_data["ingestion_error"] or "")
    
    def test_status_endpoint_nonexistent_resource(self, client):
        """Test status endpoint for nonexistent resource."""
        response = client.get("/resources/00000000-0000-0000-0000-000000000000/status")
        assert response.status_code == 404
    
    def test_multiple_concurrent_ingestions(self, client, test_db, temp_dir):
        """Test multiple concurrent ingestion requests."""
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.services.resource_service.ARCHIVE_ROOT', temp_dir):
            
            mock_fetch.return_value = {
                "url": "https://example.com/test",
                "status": 200,
                "html": "<html><body>Test</body></html>",
                "content_type": "text/html"
            }
            
            # Submit multiple requests
            responses = []
            for i in range(3):
                response = client.post("/resources", json={"url": f"https://example.com/test{i}"})
                assert response.status_code == 202
                responses.append(response.json())
            
            # Verify all have different IDs
            resource_ids = [resp["id"] for resp in responses]
            assert len(set(resource_ids)) == 3
            
            # Wait for all to complete
            for resource_id in resource_ids:
                max_attempts = 50
                for _ in range(max_attempts):
                    status_response = client.get(f"/resources/{resource_id}/status")
                    status_data = status_response.json()
                    if status_data["ingestion_status"] in ["completed", "failed"]:
                        break
                    time.sleep(0.1)
                else:
                    pytest.fail(f"Ingestion {resource_id} did not complete within timeout")
                
                assert status_data["ingestion_status"] == "completed"
