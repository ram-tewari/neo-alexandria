"""
Test Phase 9 quality assessment integration with resource ingestion pipeline.

This test verifies that:
1. Quality assessment is called after embedding generation and ML classification
2. Multi-dimensional quality scores are computed and stored
3. Errors in quality assessment don't block ingestion
"""

from unittest.mock import patch, MagicMock
from uuid import uuid4
import pytest

from backend.app.services.resource_service import process_ingestion
from backend.app.database.models import Resource


def test_quality_integration_in_ingestion(test_db):
    """Test that quality assessment is integrated into ingestion pipeline."""
    
    # Create a test resource using the test database session
    session = test_db()
    try:
        resource = Resource(
            id=uuid4(),
            title="Test Resource",
            description="Test description",
            source="https://example.edu/test",
            ingestion_status="pending",
            quality_score=0.0
        )
        session.add(resource)
        session.commit()
        resource_id = str(resource.id)
        
        # Mock external dependencies
        with patch('backend.app.services.resource_service.ce.fetch_url') as mock_fetch, \
             patch('backend.app.services.resource_service.ce.extract_from_fetched') as mock_extract, \
             patch('backend.app.services.resource_service.ce.archive_local') as mock_archive, \
             patch('backend.app.services.resource_service.AICore') as mock_ai_class:
            
            # Setup mocks
            mock_fetch.return_value = {
                'url': 'https://example.edu/test',
                'status': 200,
                'html': '<html><body>Test content</body></html>',
                'content_type': 'text/html'
            }
            
            mock_extract.return_value = {
                'title': 'Test Resource',
                'text': 'This is test content with sufficient length for quality assessment.'
            }
            
            mock_archive.return_value = {
                'archive_path': '/archive/test.html'
            }
            
            mock_ai = MagicMock()
            mock_ai.generate_summary.return_value = "Test summary"
            mock_ai.generate_tags.return_value = ["test", "quality"]
            mock_ai.generate_embedding.return_value = [0.1] * 1536
            mock_ai_class.return_value = mock_ai
            
            # Run ingestion
            process_ingestion(resource_id)
            
            # Verify resource was updated
            session.refresh(resource)
            
            # Check that ingestion completed successfully
            assert resource.ingestion_status == "completed"
            
            # Check that Phase 9 quality scores were computed
            assert resource.quality_overall is not None
            assert resource.quality_accuracy is not None
            assert resource.quality_completeness is not None
            assert resource.quality_consistency is not None
            assert resource.quality_timeliness is not None
            assert resource.quality_relevance is not None
            
            # Check that quality metadata was set
            assert resource.quality_last_computed is not None
            assert resource.quality_computation_version == "v2.0"
            assert resource.quality_weights is not None
            
            # Check backward compatibility - legacy quality_score should match quality_overall
            assert resource.quality_score == resource.quality_overall
            
            print("✓ Quality integration test passed")
            print(f"  Overall quality: {resource.quality_overall:.2f}")
            print(f"  Accuracy: {resource.quality_accuracy:.2f}")
            print(f"  Completeness: {resource.quality_completeness:.2f}")
            print(f"  Consistency: {resource.quality_consistency:.2f}")
            print(f"  Timeliness: {resource.quality_timeliness:.2f}")
            print(f"  Relevance: {resource.quality_relevance:.2f}")
            
    finally:
        # Cleanup
        try:
            if resource and resource.id:
                # Refresh to ensure it's attached to session
                session.refresh(resource)
                session.delete(resource)
                session.commit()
        except Exception:
            # If resource was never persisted or already deleted, just rollback
            session.rollback()
        finally:
            session.close()


def test_quality_integration_error_handling(test_db):
    """Test that quality assessment errors don't block ingestion."""
    
    session = test_db()
    try:
        resource = Resource(
            id=uuid4(),
            title="Test Resource",
            description="Test description",
            source="https://example.com/test",
            ingestion_status="pending",
            quality_score=0.0
        )
        session.add(resource)
        session.commit()
        resource_id = str(resource.id)
        
        # Mock external dependencies
        with patch('backend.app.services.resource_service.ce.fetch_url') as mock_fetch, \
             patch('backend.app.services.resource_service.ce.extract_from_fetched') as mock_extract, \
             patch('backend.app.services.resource_service.ce.archive_local') as mock_archive, \
             patch('backend.app.services.resource_service.AICore') as mock_ai_class, \
             patch('backend.app.services.resource_service.QualityService') as mock_quality_service:
            
            # Setup mocks
            mock_fetch.return_value = {
                'url': 'https://example.com/test',
                'status': 200,
                'html': '<html><body>Test content</body></html>',
                'content_type': 'text/html'
            }
            
            mock_extract.return_value = {
                'title': 'Test Resource',
                'text': 'Test content'
            }
            
            mock_archive.return_value = {
                'archive_path': '/archive/test.html'
            }
            
            mock_ai = MagicMock()
            mock_ai.generate_summary.return_value = "Test summary"
            mock_ai.generate_tags.return_value = ["test"]
            mock_ai.generate_embedding.return_value = [0.1] * 1536
            mock_ai_class.return_value = mock_ai
            
            # Make quality service raise an error
            mock_quality_instance = MagicMock()
            mock_quality_instance.compute_quality.side_effect = Exception("Quality service error")
            mock_quality_service.return_value = mock_quality_instance
            
            # Run ingestion - should complete despite quality error
            process_ingestion(resource_id)
            
            # Verify resource ingestion still completed
            session.refresh(resource)
            assert resource.ingestion_status == "completed"
            
            # Legacy quality score should still be set
            assert resource.quality_score > 0.0
            
            print("✓ Quality error handling test passed")
            print("  Ingestion completed despite quality service error")
            
    finally:
        # Cleanup
        try:
            if resource and resource.id:
                # Refresh to ensure it's attached to session
                session.refresh(resource)
                session.delete(resource)
                session.commit()
        except Exception:
            # If resource was never persisted or already deleted, just rollback
            session.rollback()
        finally:
            session.close()


if __name__ == "__main__":
    print("Testing Phase 9 quality integration with ingestion pipeline...")
    print()
    
    try:
        test_quality_integration_in_ingestion()
        print()
        test_quality_integration_error_handling()
        print()
        print("✓ All quality integration tests passed!")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
