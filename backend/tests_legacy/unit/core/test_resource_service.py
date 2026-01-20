"""Tests for resource service integration."""

import pytest
import time
from unittest.mock import patch, Mock

from backend.app.services.resource_service import (
    create_pending_resource,
    process_ingestion,
    get_resource,
    update_resource,
    delete_resource,
)
from backend.app.database.models import Resource


class TestPendingResourceCreation:
    """Test pending resource creation service."""

    def test_create_pending_resource_success(self, test_db):
        """Test successful pending resource creation."""
        db = test_db()

        payload = {
            "url": "https://example.com/test",
            "title": "Test Article",
            "language": "en",
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
        assert resource.read_status == "unread"

    def test_create_pending_resource_missing_url(self, test_db):
        """Test pending resource creation with missing URL."""
        db = test_db()

        payload = {"title": "Test Article"}

        with pytest.raises(ValueError, match="url is required"):
            create_pending_resource(db, payload)

    def test_create_pending_resource_with_overrides(self, test_db):
        """Test pending resource creation with field overrides."""
        db = test_db()

        payload = {
            "url": "https://example.com/test",
            "title": "Override Title",
            "description": "Override Description",
            "creator": "Override Author",
            "language": "es",
            "type": "book",
        }

        resource = create_pending_resource(db, payload)

        assert resource.title == "Override Title"
        assert resource.description == "Override Description"
        assert resource.creator == "Override Author"
        assert resource.language == "es"
        assert resource.type == "book"
        assert resource.ingestion_status == "pending"

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
            "publisher": "O'REILLY MEDIA",
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
        with (
            patch("backend.app.utils.content_extractor.fetch_url") as mock_fetch,
            patch(
                "backend.app.utils.content_extractor.extract_from_fetched"
            ) as mock_extract,
            patch("backend.app.services.resource_service.AICore") as mock_ai_core_class,
        ):
            mock_fetch.return_value = {
                "url": "https://example.com/test",
                "status": 200,
                "html": "<html><head><title>Test</title></head><body><p>Test content</p></body></html>",
                "content_type": "text/html",
            }

            mock_extract.return_value = {
                "title": "Test",
                "text": "Test content about machine learning",
            }

            mock_ai_core = Mock()
            mock_ai_core.generate_summary.return_value = "Summary about ML"
            mock_ai_core.generate_tags.return_value = ["Machine Learning", "AI"]
            mock_ai_core.generate_embedding.return_value = [
                0.1,
                0.2,
                0.3,
            ]  # Mock embedding
            mock_ai_core_class.return_value = mock_ai_core

            # Process ingestion with test database URL
            db_for_url = test_db()
            engine_url = str(db_for_url.get_bind().url)
            db_for_url.close()
            process_ingestion(resource_id, archive_root=temp_dir, engine_url=engine_url)

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

        with patch("backend.app.utils.content_extractor.fetch_url") as mock_fetch:
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


class TestResourceCRUD:
    """Test resource CRUD operations."""

    def test_get_resource(self, test_db):
        """Test getting a resource by ID."""
        db = test_db()

        # Create a resource
        payload = {"url": "https://example.com/test", "title": "Test Resource"}
        resource = create_pending_resource(db, payload)
        resource_id = str(resource.id)
        db.close()

        # Get the resource
        db = test_db()
        retrieved = get_resource(db, resource_id)

        assert retrieved is not None
        assert retrieved.id == resource.id
        assert retrieved.title == "Test Resource"

    def test_get_resource_nonexistent(self, test_db):
        """Test getting a nonexistent resource."""
        db = test_db()
        result = get_resource(db, "00000000-0000-0000-0000-000000000000")
        assert result is None

    def test_update_resource(self, test_db):
        """Test updating a resource."""
        db = test_db()

        # Create a resource
        payload = {"url": "https://example.com/test", "title": "Original Title"}
        resource = create_pending_resource(db, payload)
        resource_id = str(resource.id)
        db.close()

        # Update the resource
        from backend.app.schemas.resource import ResourceUpdate

        db = test_db()
        updated = update_resource(
            db, resource_id, ResourceUpdate(title="Updated Title")
        )

        assert updated.title == "Updated Title"
        assert updated.id == resource.id

    def test_delete_resource(self, test_db):
        """Test deleting a resource."""
        db = test_db()

        # Create a resource
        payload = {"url": "https://example.com/test", "title": "Test Resource"}
        resource = create_pending_resource(db, payload)
        resource_id = str(resource.id)
        db.close()

        # Delete the resource
        db = test_db()
        delete_resource(db, resource_id)

        # Verify it's gone
        deleted = get_resource(db, resource_id)
        assert deleted is None


class TestAsyncIngestionIntegration:
    """Test async ingestion integration with API."""

    def test_async_ingestion_flow(self, client, test_db, temp_dir):
        """Test complete async ingestion flow via API."""
        with (
            patch("backend.app.utils.content_extractor.fetch_url") as mock_fetch,
            patch("backend.app.services.resource_service.ARCHIVE_ROOT", temp_dir),
            patch("backend.app.services.resource_service.AICore") as mock_ai_core_class,
        ):
            mock_fetch.return_value = {
                "url": "https://example.com/test",
                "status": 200,
                "html": "<html><head><title>Test</title></head><body><p>Test content</p></body></html>",
                "content_type": "text/html",
            }

            # Mock AI core to generate some tags
            mock_ai_core = Mock()
            mock_ai_core.generate_summary.return_value = "A test article about content"
            mock_ai_core.generate_tags.return_value = ["Test", "Content"]
            mock_ai_core.generate_embedding.return_value = [
                0.1,
                0.2,
                0.3,
            ]  # Mock embedding
            mock_ai_core_class.return_value = mock_ai_core

            # Submit ingestion request
            response = client.post(
                "/resources", json={"url": "https://example.com/test"}
            )
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

    def test_manual_classification_override_endpoint(self, client, test_db, temp_dir):
        """Test manual classification override endpoint."""
        with (
            patch("backend.app.utils.content_extractor.fetch_url") as mock_fetch,
            patch("backend.app.services.resource_service.ARCHIVE_ROOT", temp_dir),
        ):
            mock_fetch.return_value = {
                "url": "https://example.com/test",
                "status": 200,
                "html": "<html><body>Test</body></html>",
                "content_type": "text/html",
            }

            # Submit ingestion request
            response = client.post(
                "/resources", json={"url": "https://example.com/test"}
            )
            assert response.status_code == 202

            resource_id = response.json()["id"]

            # Wait for completion
            max_attempts = 50
            for _ in range(max_attempts):
                status_response = client.get(f"/resources/{resource_id}/status")
                status_data = status_response.json()
                if status_data["ingestion_status"] in ["completed", "failed"]:
                    break
                time.sleep(0.1)
            else:
                pytest.fail("Ingestion did not complete within timeout")

            # Override classification
            resp2 = client.put(
                f"/resources/{resource_id}/classify", json={"code": "900"}
            )
            assert resp2.status_code == 200
            assert resp2.json()["classification_code"] == "900"

    def test_update_resource_normalizes_fields(self, client, seeded_resources):
        """Test that resource updates apply authority normalization."""
        rid = seeded_resources[0]
        # Update subject list and creator/publisher
        resp = client.put(
            f"/resources/{rid}",
            json={
                "subject": ["ml", "database", "JS"],
                "creator": "doe, jane",
                "publisher": "packt",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "Machine Learning" in data["subject"]
        assert "Database" in data["subject"]
        assert "JavaScript" in data["subject"]
        assert data["creator"] == "Jane Doe"
        assert data["publisher"] == "Packt"
