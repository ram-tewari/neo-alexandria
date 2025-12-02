"""
Integration tests for service event emissions.

Tests verify that services correctly emit events when performing operations.
These tests focus on the service-to-event flow, ensuring that all required
events are emitted with correct data.

Test Strategy:
- Use real database sessions with test fixtures
- Monitor event emissions using event_emitter.get_event_history()
- Verify event data contains required fields
- Test ResourceService, IngestionService, UserProfileService, CitationService, MetadataExtractor
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from uuid import uuid4

from backend.app.events import event_emitter, EventPriority
from backend.app.events.event_types import SystemEvent
from app.services.resource_service import (
    create_pending_resource,
    update_resource,
    delete_resource
)
from app.services.user_profile_service import UserProfileService
from app.services.citation_service import CitationService
from app.services.metadata_extractor import MetadataExtractor
from app.schemas.resource import ResourceUpdate
from app.database.models import Resource, User, UserProfile


@pytest.fixture(autouse=True)
def clear_event_history():
    """Clear event history before and after each test."""
    event_emitter.clear_history()
    yield
    event_emitter.clear_history()


# db_session fixture is now in integration/conftest.py


class TestResourceServiceEvents:
    """Test event emissions from ResourceService."""
    
    def test_create_pending_resource_emits_resource_created(self, db_session):
        """Test that creating a resource emits resource.created event."""
        # Arrange
        payload = {
            "url": "https://example.com/test-paper.pdf",
            "title": "Test Paper"
        }
        
        # Act
        resource = create_pending_resource(db_session, payload)
        
        # Assert
        events = event_emitter.get_event_history(limit=10)
        created_events = [e for e in events if e["name"] == SystemEvent.RESOURCE_CREATED]
        
        assert len(created_events) == 1
        event_data = created_events[0]["data"]
        assert event_data["resource_id"] == str(resource.id)
        assert event_data["title"] == "Test Paper"
        assert event_data["source"] == payload["url"]
    
    def test_update_resource_emits_resource_updated(self, db_session):
        """Test that updating a resource emits resource.updated event."""
        # Arrange
        resource = create_pending_resource(db_session, {
            "url": "https://example.com/test.pdf",
            "title": "Original Title"
        })
        event_emitter.clear_history()  # Clear creation event
        
        update_payload = ResourceUpdate(title="Updated Title")
        
        # Act
        updated_resource = update_resource(db_session, resource.id, update_payload)
        
        # Assert
        events = event_emitter.get_event_history(limit=10)
        updated_events = [e for e in events if e["name"] == SystemEvent.RESOURCE_UPDATED]
        
        assert len(updated_events) == 1
        event_data = updated_events[0]["data"]
        assert event_data["resource_id"] == str(resource.id)
        assert "title" in event_data["changed_fields"]
    
    def test_update_resource_content_emits_content_changed(self, db_session):
        """Test that updating content emits resource.content_changed event."""
        # Arrange
        resource = create_pending_resource(db_session, {
            "url": "https://example.com/test.pdf"
        })
        event_emitter.clear_history()
        
        # Update with content field
        update_payload = ResourceUpdate(identifier="/path/to/content")
        
        # Act
        update_resource(db_session, resource.id, update_payload)
        
        # Assert
        events = event_emitter.get_event_history(limit=10)
        content_events = [e for e in events if e["name"] == SystemEvent.RESOURCE_CONTENT_CHANGED]
        
        assert len(content_events) == 1
        event_data = content_events[0]["data"]
        assert event_data["resource_id"] == str(resource.id)
    
    def test_update_resource_metadata_emits_metadata_changed(self, db_session):
        """Test that updating metadata emits resource.metadata_changed event."""
        # Arrange
        resource = create_pending_resource(db_session, {
            "url": "https://example.com/test.pdf"
        })
        event_emitter.clear_history()
        
        # Update with metadata field only (not content)
        update_payload = ResourceUpdate(
            title="New Title",
            description="New Description"
        )
        
        # Act
        update_resource(db_session, resource.id, update_payload)
        
        # Assert
        events = event_emitter.get_event_history(limit=10)
        metadata_events = [e for e in events if e["name"] == SystemEvent.RESOURCE_METADATA_CHANGED]
        
        assert len(metadata_events) == 1
        event_data = metadata_events[0]["data"]
        assert event_data["resource_id"] == str(resource.id)
        assert "title" in event_data["changed_fields"]
        assert "description" in event_data["changed_fields"]
    
    def test_delete_resource_emits_resource_deleted(self, db_session):
        """Test that deleting a resource emits resource.deleted event."""
        # Arrange
        resource = create_pending_resource(db_session, {
            "url": "https://example.com/test.pdf",
            "title": "To Be Deleted"
        })
        resource_id = resource.id
        resource_title = resource.title
        event_emitter.clear_history()
        
        # Act
        delete_resource(db_session, resource_id)
        
        # Assert
        events = event_emitter.get_event_history(limit=10)
        deleted_events = [e for e in events if e["name"] == SystemEvent.RESOURCE_DELETED]
        
        assert len(deleted_events) == 1
        event_data = deleted_events[0]["data"]
        assert event_data["resource_id"] == str(resource_id)
        assert event_data["title"] == resource_title


class TestIngestionServiceEvents:
    """Test event emissions from ingestion process."""
    
    @patch('app.services.resource_service.ce.fetch_url')
    @patch('app.services.resource_service.ce.extract_from_fetched')
    @patch('app.services.resource_service.AICore')
    def test_ingestion_emits_started_and_completed_events(
        self,
        mock_ai_core,
        mock_extract,
        mock_fetch,
        db_session
    ):
        """Test that ingestion emits started and completed events."""
        # Arrange
        from app.services.resource_service import process_ingestion
        
        resource = create_pending_resource(db_session, {
            "url": "https://example.com/test.pdf"
        })
        event_emitter.clear_history()
        
        # Mock fetch and extract
        mock_fetch.return_value = {
            "url": "https://example.com/test.pdf",
            "status": 200,
            "html": "<html>Test content</html>",
            "content_type": "text/html"
        }
        mock_extract.return_value = {
            "title": "Test Paper",
            "text": "Test content text"
        }
        
        # Mock AI core
        mock_ai_instance = MagicMock()
        mock_ai_instance.generate_summary.return_value = "Test summary"
        mock_ai_instance.generate_tags.return_value = ["test", "paper"]
        mock_ai_instance.generate_embedding.return_value = [0.1] * 768
        mock_ai_core.return_value = mock_ai_instance
        
        # Act
        process_ingestion(str(resource.id), ai=mock_ai_instance)
        
        # Assert
        events = event_emitter.get_event_history(limit=50)
        started_events = [e for e in events if e["name"] == SystemEvent.INGESTION_STARTED]
        completed_events = [e for e in events if e["name"] == SystemEvent.INGESTION_COMPLETED]
        
        assert len(started_events) == 1
        assert len(completed_events) == 1
        
        # Verify started event
        started_data = started_events[0]["data"]
        assert started_data["resource_id"] == str(resource.id)
        assert "started_at" in started_data
        
        # Verify completed event
        completed_data = completed_events[0]["data"]
        assert completed_data["resource_id"] == str(resource.id)
        assert completed_data["success"] is True
        assert "duration_seconds" in completed_data
        assert completed_data["duration_seconds"] >= 0
    
    @patch('app.services.resource_service.ce.fetch_url')
    def test_ingestion_failure_emits_failed_event(self, mock_fetch, db_session):
        """Test that ingestion failure emits ingestion.failed event."""
        # Arrange
        from app.services.resource_service import process_ingestion
        
        resource = create_pending_resource(db_session, {
            "url": "https://example.com/test.pdf"
        })
        event_emitter.clear_history()
        
        # Mock fetch to raise exception
        mock_fetch.side_effect = Exception("Network error")
        
        # Act
        process_ingestion(str(resource.id))
        
        # Assert
        events = event_emitter.get_event_history(limit=50)
        failed_events = [e for e in events if e["name"] == SystemEvent.INGESTION_FAILED]
        
        assert len(failed_events) == 1
        failed_data = failed_events[0]["data"]
        assert failed_data["resource_id"] == str(resource.id)
        assert failed_data["success"] is False
        assert "error" in failed_data
        assert "Network error" in failed_data["error"]
        assert "duration_seconds" in failed_data


class TestUserInteractionEvents:
    """Test event emissions from user interaction tracking."""
    
    def test_track_interaction_emits_user_interaction_tracked(self, db_session):
        """Test that tracking interaction emits user.interaction_tracked event."""
        # Arrange
        # Create user
        user = User(
            username="testuser",
            email="test@example.com"
        )
        db_session.add(user)
        
        # Create resource
        resource = create_pending_resource(db_session, {
            "url": "https://example.com/test.pdf"
        })
        db_session.commit()
        
        event_emitter.clear_history()
        
        # Create service
        service = UserProfileService(db_session)
        
        # Act
        service.track_interaction(
            user_id=user.id,
            resource_id=resource.id,
            interaction_type="view",
            dwell_time=120
        )
        
        # Assert
        events = event_emitter.get_event_history(limit=10)
        interaction_events = [e for e in events if e["name"] == SystemEvent.USER_INTERACTION_TRACKED]
        
        assert len(interaction_events) == 1
        event_data = interaction_events[0]["data"]
        assert event_data["user_id"] == str(user.id)
        assert event_data["resource_id"] == str(resource.id)
        assert event_data["interaction_type"] == "view"
        assert "total_interactions" in event_data
        assert event_data["total_interactions"] >= 1
    
    def test_multiple_interactions_emit_multiple_events(self, db_session):
        """Test that multiple interactions emit multiple events."""
        # Arrange
        user = User(
            username="testuser",
            email="test@example.com"
        )
        db_session.add(user)
        
        resource1 = create_pending_resource(db_session, {
            "url": "https://example.com/test1.pdf"
        })
        resource2 = create_pending_resource(db_session, {
            "url": "https://example.com/test2.pdf"
        })
        db_session.commit()
        
        event_emitter.clear_history()
        
        service = UserProfileService(db_session)
        
        # Act
        service.track_interaction(user.id, resource1.id, "view")
        service.track_interaction(user.id, resource2.id, "annotation")
        
        # Assert
        events = event_emitter.get_event_history(limit=10)
        interaction_events = [e for e in events if e["name"] == SystemEvent.USER_INTERACTION_TRACKED]
        
        assert len(interaction_events) == 2


class TestCitationExtractionEvents:
    """Test event emissions from citation extraction."""
    
    def test_extract_citations_emits_citations_extracted(self, db_session, tmp_path):
        """Test that extracting citations emits citations.extracted event."""
        # Arrange
        # Create resource with archived content
        resource = create_pending_resource(db_session, {
            "url": "https://example.com/test.pdf"
        })
        
        # Create mock archive directory
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        resource.identifier = str(archive_dir)
        
        # Create mock HTML file with citations
        html_file = archive_dir / "content.html"
        html_file.write_text("""
        <html>
            <body>
                <a href="https://example.com/ref1.pdf">Reference 1</a>
                <a href="https://example.com/ref2.pdf">Reference 2</a>
            </body>
        </html>
        """)
        
        db_session.commit()
        event_emitter.clear_history()
        
        # Create service
        service = CitationService(db_session)
        
        # Act
        citations = service.extract_citations(str(resource.id))
        
        # Assert
        events = event_emitter.get_event_history(limit=10)
        citation_events = [e for e in events if e["name"] == SystemEvent.CITATIONS_EXTRACTED]
        
        assert len(citation_events) == 1
        event_data = citation_events[0]["data"]
        assert event_data["resource_id"] == str(resource.id)
        assert "citations" in event_data
        assert event_data["citation_count"] == len(citations)
        assert len(event_data["citations"]) > 0


class TestAuthorExtractionEvents:
    """Test event emissions from author extraction."""
    
    def test_extract_authors_emits_authors_extracted(self, db_session):
        """Test that extracting authors emits authors.extracted event."""
        # Arrange
        resource = create_pending_resource(db_session, {
            "url": "https://example.com/test.pdf",
            "description": "A paper by John Doe and Jane Smith"
        })
        db_session.commit()
        
        event_emitter.clear_history()
        
        # Create service
        service = MetadataExtractor(db_session)
        
        # Mock the _extract_authors method to return test data
        test_authors = [
            {"name": "John Doe"},
            {"name": "Jane Smith"}
        ]
        
        # Act
        service.emit_authors_extracted_event(str(resource.id), test_authors)
        
        # Assert
        events = event_emitter.get_event_history(limit=10)
        author_events = [e for e in events if e["name"] == SystemEvent.AUTHORS_EXTRACTED]
        
        assert len(author_events) == 1
        event_data = author_events[0]["data"]
        assert event_data["resource_id"] == str(resource.id)
        assert "authors" in event_data
        assert event_data["author_count"] == 2
        assert event_data["authors"] == test_authors


class TestEventDataCompleteness:
    """Test that events contain all required data fields."""
    
    def test_resource_created_event_has_required_fields(self, db_session):
        """Test that resource.created event has all required fields."""
        # Act
        resource = create_pending_resource(db_session, {
            "url": "https://example.com/test.pdf",
            "title": "Test"
        })
        
        # Assert
        events = event_emitter.get_event_history(limit=10)
        created_event = next(e for e in events if e["name"] == SystemEvent.RESOURCE_CREATED)
        
        required_fields = ["resource_id", "title", "source"]
        for field in required_fields:
            assert field in created_event["data"], f"Missing required field: {field}"
    
    def test_user_interaction_event_has_required_fields(self, db_session):
        """Test that user.interaction_tracked event has all required fields."""
        # Arrange
        user = User(username="test", email="test@example.com")
        db_session.add(user)
        resource = create_pending_resource(db_session, {"url": "https://example.com/test.pdf"})
        db_session.commit()
        
        event_emitter.clear_history()
        service = UserProfileService(db_session)
        
        # Act
        service.track_interaction(user.id, resource.id, "view")
        
        # Assert
        events = event_emitter.get_event_history(limit=10)
        interaction_event = next(e for e in events if e["name"] == SystemEvent.USER_INTERACTION_TRACKED)
        
        required_fields = ["user_id", "resource_id", "interaction_type", "total_interactions"]
        for field in required_fields:
            assert field in interaction_event["data"], f"Missing required field: {field}"


class TestEventPriorities:
    """Test that events are emitted with correct priorities."""
    
    def test_resource_updated_has_high_priority(self, db_session):
        """Test that resource.updated event has HIGH priority."""
        # Arrange
        resource = create_pending_resource(db_session, {"url": "https://example.com/test.pdf"})
        event_emitter.clear_history()
        
        # Act
        update_resource(db_session, resource.id, ResourceUpdate(title="Updated"))
        
        # Assert
        events = event_emitter.get_event_history(limit=10)
        updated_event = next(e for e in events if e["name"] == SystemEvent.RESOURCE_UPDATED)
        
        assert updated_event["priority"] == "HIGH"
    
    def test_user_interaction_has_low_priority(self, db_session):
        """Test that user.interaction_tracked event has LOW priority."""
        # Arrange
        user = User(username="test", email="test@example.com")
        db_session.add(user)
        resource = create_pending_resource(db_session, {"url": "https://example.com/test.pdf"})
        db_session.commit()
        
        event_emitter.clear_history()
        service = UserProfileService(db_session)
        
        # Act
        service.track_interaction(user.id, resource.id, "view")
        
        # Assert
        events = event_emitter.get_event_history(limit=10)
        interaction_event = next(e for e in events if e["name"] == SystemEvent.USER_INTERACTION_TRACKED)
        
        assert interaction_event["priority"] == "LOW"
