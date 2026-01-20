"""
Tests for Resource Migration Script

Tests cover:
- Sample resource migration
- Batch processing
- Error handling and resume
- Progress tracking

Requirements: 5.9, 5.10
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, timezone
import uuid as uuid_module

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import Resource, DocumentChunk
from app.shared.base_model import Base

# Import migration script components
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
from migrate_existing_resources import (
    MigrationProgress,
    get_resources_without_chunks,
    chunk_resource,
)


@pytest.fixture
def temp_progress_file():
    """Create temporary progress file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = Path(f.name)
    yield temp_path
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def test_db():
    """Create in-memory test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def sample_resources(test_db, tmp_path):
    """Create sample resources for testing."""
    resources = []

    # Create archive directory
    archive_root = tmp_path / "archive"
    archive_root.mkdir(parents=True, exist_ok=True)

    # Create 5 resources with archived content
    for i in range(5):
        resource_id = uuid_module.uuid4()

        # Create archive directory for this resource
        resource_archive = archive_root / str(resource_id)
        resource_archive.mkdir(parents=True, exist_ok=True)

        # Write content to archive
        content = f"This is test content for resource {i + 1}. " * 50  # ~500 words
        text_file = resource_archive / "text.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(content)

        # Create resource with archive path
        resource = Resource(
            id=resource_id,
            title=f"Test Resource {i + 1}",
            identifier=str(resource_archive),  # Archive path
            ingestion_status="completed",
            source=f"https://example.com/resource{i + 1}",
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(resource)
        resources.append(resource)

    test_db.commit()

    # Refresh to get IDs
    for resource in resources:
        test_db.refresh(resource)

    return resources


class TestMigrationProgress:
    """Test progress tracking functionality."""

    def test_default_data(self, temp_progress_file):
        """Test default progress data structure."""
        progress = MigrationProgress(temp_progress_file)

        assert progress.data["last_processed_id"] is None
        assert progress.data["processed_count"] == 0
        assert progress.data["success_count"] == 0
        assert progress.data["failure_count"] == 0
        assert progress.data["failed_resources"] == []
        assert progress.data["started_at"] is None

    def test_save_and_load(self, temp_progress_file):
        """Test saving and loading progress."""
        # Create and save progress
        progress1 = MigrationProgress(temp_progress_file)
        progress1.data["processed_count"] = 10
        progress1.data["success_count"] = 8
        progress1.data["failure_count"] = 2
        progress1.save()

        # Load progress in new instance
        progress2 = MigrationProgress(temp_progress_file)

        assert progress2.data["processed_count"] == 10
        assert progress2.data["success_count"] == 8
        assert progress2.data["failure_count"] == 2

    def test_update_success(self, temp_progress_file):
        """Test updating progress for successful processing."""
        progress = MigrationProgress(temp_progress_file)
        resource_id = str(uuid_module.uuid4())

        progress.update(resource_id, success=True)

        assert progress.data["last_processed_id"] == resource_id
        assert progress.data["processed_count"] == 1
        assert progress.data["success_count"] == 1
        assert progress.data["failure_count"] == 0
        assert len(progress.data["failed_resources"]) == 0

    def test_update_failure(self, temp_progress_file):
        """Test updating progress for failed processing."""
        progress = MigrationProgress(temp_progress_file)
        resource_id = str(uuid_module.uuid4())
        error_msg = "Test error"

        progress.update(resource_id, success=False, error=error_msg)

        assert progress.data["last_processed_id"] == resource_id
        assert progress.data["processed_count"] == 1
        assert progress.data["success_count"] == 0
        assert progress.data["failure_count"] == 1
        assert len(progress.data["failed_resources"]) == 1
        assert progress.data["failed_resources"][0]["resource_id"] == resource_id
        assert progress.data["failed_resources"][0]["error"] == error_msg

    def test_get_summary(self, temp_progress_file):
        """Test getting migration summary."""
        progress = MigrationProgress(temp_progress_file)
        progress.start()
        progress.update(str(uuid_module.uuid4()), success=True)
        progress.update(str(uuid_module.uuid4()), success=False, error="Test error")

        summary = progress.get_summary()

        assert summary["processed"] == 2
        assert summary["success"] == 1
        assert summary["failed"] == 1
        assert summary["started_at"] is not None


class TestGetResourcesWithoutChunks:
    """Test resource querying functionality."""

    def test_get_all_resources_without_chunks(self, test_db, sample_resources):
        """Test getting all resources without chunks."""
        resources = get_resources_without_chunks(test_db, batch_size=10)

        assert len(resources) == 5
        assert all(r.ingestion_status == "completed" for r in resources)

    def test_batch_size_limit(self, test_db, sample_resources):
        """Test batch size limiting."""
        resources = get_resources_without_chunks(test_db, batch_size=3)

        assert len(resources) == 3

    def test_exclude_resources_with_chunks(self, test_db, sample_resources):
        """Test that resources with chunks are excluded."""
        # Add chunks to first resource
        resource = sample_resources[0]
        chunk = DocumentChunk(
            resource_id=resource.id,
            content="Test chunk",
            chunk_index=0,
            chunk_metadata={},
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(chunk)
        test_db.commit()

        # Query resources without chunks
        resources = get_resources_without_chunks(test_db, batch_size=10)

        # Should get 4 resources (excluding the one with chunks)
        assert len(resources) == 4
        assert resource.id not in [r.id for r in resources]

    def test_resume_from_last_processed(self, test_db, sample_resources):
        """Test resuming from last processed resource."""
        # Get first batch
        first_batch = get_resources_without_chunks(test_db, batch_size=2)
        assert len(first_batch) == 2

        # Get next batch starting after last processed
        last_id = str(first_batch[-1].id)
        next_batch = get_resources_without_chunks(
            test_db, batch_size=2, last_processed_id=last_id
        )

        # Should get different resources
        assert len(next_batch) > 0
        assert all(r.id not in [rb.id for rb in first_batch] for r in next_batch)


class TestChunkResource:
    """Test individual resource chunking."""

    @patch("migrate_existing_resources.ChunkingService")
    def test_chunk_resource_success(
        self, mock_chunking_service, test_db, sample_resources
    ):
        """Test successful resource chunking."""
        resource = sample_resources[0]

        # Mock chunking service
        mock_service = Mock()
        mock_service.chunk_resource.return_value = [
            Mock(id=uuid_module.uuid4(), chunk_index=0),
            Mock(id=uuid_module.uuid4(), chunk_index=1),
        ]

        # Chunk resource
        success, error = chunk_resource(test_db, resource, mock_service)

        assert success is True
        assert error is None
        mock_service.chunk_resource.assert_called_once()

    @patch("migrate_existing_resources.ChunkingService")
    def test_chunk_resource_empty_content(
        self, mock_chunking_service, test_db, tmp_path
    ):
        """Test chunking resource with empty content."""
        # Create resource with no archived content
        resource_id = uuid_module.uuid4()
        resource_archive = tmp_path / "archive" / str(resource_id)
        resource_archive.mkdir(parents=True, exist_ok=True)

        # Create empty text file
        text_file = resource_archive / "text.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write("")

        resource = Resource(
            id=resource_id,
            title="Empty Resource",
            identifier=str(resource_archive),
            ingestion_status="completed",
            source="https://example.com/empty",
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(resource)
        test_db.commit()

        mock_service = Mock()

        # Chunk resource
        success, error = chunk_resource(test_db, resource, mock_service)

        # Should succeed but skip chunking
        assert success is True
        assert error is None
        mock_service.chunk_resource.assert_not_called()

    @patch("migrate_existing_resources.ChunkingService")
    def test_chunk_resource_error_handling(
        self, mock_chunking_service, test_db, sample_resources
    ):
        """Test error handling during chunking."""
        resource = sample_resources[0]

        # Mock chunking service to raise error
        mock_service = Mock()
        mock_service.chunk_resource.side_effect = Exception("Chunking failed")

        # Chunk resource
        success, error = chunk_resource(test_db, resource, mock_service)

        assert success is False
        assert error is not None
        assert "Chunking failed" in error


class TestMigrateResources:
    """Test full migration process."""

    @patch("migrate_existing_resources.get_settings")
    @patch("migrate_existing_resources.EmbeddingGenerator")
    @patch("migrate_existing_resources.ChunkingService")
    def test_migrate_with_sample_resources(
        self,
        mock_chunking_service,
        mock_embedding_gen,
        mock_get_settings,
        test_db,
        sample_resources,
        temp_progress_file,
    ):
        """Test migration with sample resources."""
        # Mock settings
        mock_settings = Mock()
        mock_settings.database_url = "sqlite:///:memory:"
        mock_get_settings.return_value = mock_settings

        # Mock embedding generator
        mock_embedding_gen.return_value = Mock()

        # Mock chunking service
        mock_service_instance = Mock()
        mock_service_instance.chunk_resource.return_value = [
            Mock(id=uuid_module.uuid4(), chunk_index=0)
        ]
        mock_chunking_service.return_value = mock_service_instance

        # Test the components work together
        progress = MigrationProgress(temp_progress_file)
        progress.start()

        # Simulate processing one resource
        resource = sample_resources[0]
        success, error = chunk_resource(test_db, resource, mock_service_instance)
        progress.update(str(resource.id), success, error)

        summary = progress.get_summary()
        assert summary["processed"] == 1
        assert summary["success"] == 1

    @patch("migrate_existing_resources.get_settings")
    @patch("migrate_existing_resources.EmbeddingGenerator")
    def test_batch_processing(
        self,
        mock_embedding_gen,
        mock_get_settings,
        test_db,
        sample_resources,
        temp_progress_file,
    ):
        """Test batch processing of resources."""
        # Get resources in batches
        batch1 = get_resources_without_chunks(test_db, batch_size=2)
        assert len(batch1) == 2

        batch2 = get_resources_without_chunks(
            test_db, batch_size=2, last_processed_id=str(batch1[-1].id)
        )
        assert len(batch2) > 0

        # Verify no overlap
        batch1_ids = {r.id for r in batch1}
        batch2_ids = {r.id for r in batch2}
        assert len(batch1_ids & batch2_ids) == 0

    def test_progress_tracking(self, temp_progress_file):
        """Test progress tracking throughout migration."""
        progress = MigrationProgress(temp_progress_file)
        progress.start()

        # Simulate processing multiple resources
        for i in range(5):
            resource_id = str(uuid_module.uuid4())
            success = i % 4 != 0  # Fail every 4th resource (indices 0 and 4)
            error = "Test error" if not success else None
            progress.update(resource_id, success, error)

        summary = progress.get_summary()
        assert summary["processed"] == 5
        assert summary["success"] == 3
        assert summary["failed"] == 2

        # Verify progress was saved
        progress2 = MigrationProgress(temp_progress_file)
        summary2 = progress2.get_summary()
        assert summary2["processed"] == 5

    def test_resume_capability(self, test_db, sample_resources, temp_progress_file):
        """Test resume from last processed resource."""
        progress = MigrationProgress(temp_progress_file)
        progress.start()

        # Process first 2 resources
        batch1 = get_resources_without_chunks(test_db, batch_size=2)
        for resource in batch1:
            progress.update(str(resource.id), success=True)

        # Get last processed ID
        last_id = progress.get_last_processed_id()
        assert last_id is not None

        # Resume from last processed
        batch2 = get_resources_without_chunks(
            test_db, batch_size=3, last_processed_id=last_id
        )

        # Should get remaining resources
        assert len(batch2) > 0
        assert all(str(r.id) != last_id for r in batch2)


class TestErrorHandling:
    """Test error handling and recovery."""

    @patch("migrate_existing_resources.ChunkingService")
    def test_continue_on_error(
        self, mock_chunking_service, test_db, sample_resources, temp_progress_file
    ):
        """Test that migration continues after errors."""
        progress = MigrationProgress(temp_progress_file)
        progress.start()

        # Mock service that fails on first resource
        mock_service = Mock()
        call_count = 0

        def chunk_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("First resource failed")
            return [Mock(id=uuid_module.uuid4(), chunk_index=0)]

        mock_service.chunk_resource.side_effect = chunk_side_effect

        # Process resources
        for resource in sample_resources[:3]:
            success, error = chunk_resource(test_db, resource, mock_service)
            progress.update(str(resource.id), success, error)

        summary = progress.get_summary()
        assert summary["processed"] == 3
        assert summary["success"] == 2
        assert summary["failed"] == 1

    def test_error_logging(self, temp_progress_file):
        """Test that errors are properly logged."""
        progress = MigrationProgress(temp_progress_file)

        resource_id = str(uuid_module.uuid4())
        error_msg = "Test error message"

        progress.update(resource_id, success=False, error=error_msg)

        failed = progress.data["failed_resources"]
        assert len(failed) == 1
        assert failed[0]["resource_id"] == resource_id
        assert failed[0]["error"] == error_msg
        assert "timestamp" in failed[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
