"""
Test resource ingestion integration with ML classification (Phase 8.5 Task 15).

This test verifies that ML classification is triggered during resource ingestion
after embedding generation and before quality scoring.

Requirements: 12.1, 12.2, 12.3
"""

import pytest
import uuid
from unittest.mock import Mock, patch

from backend.app.services.resource_service import process_ingestion
from backend.app.database.models import Resource, TaxonomyNode
from backend.app.database.base import SessionLocal


@pytest.fixture
def db_session():
    """Create a test database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_resource(db_session):
    """Create a sample resource for testing."""
    resource = Resource(
        id=uuid.uuid4(),
        title="Test Resource",
        description="A test resource for classification",
        source="https://example.com/test",
        ingestion_status="pending",
        quality_score=0.0,
        subject=[]
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)
    return resource


@pytest.fixture
def sample_taxonomy_nodes(db_session):
    """Create sample taxonomy nodes for testing."""
    nodes = []
    
    # Create root node
    root = TaxonomyNode(
        id=uuid.uuid4(),
        name="Computer Science",
        slug="computer-science",
        level=0,
        path="/computer-science",
        is_leaf=False,
        allow_resources=True
    )
    db_session.add(root)
    nodes.append(root)
    
    # Create child node
    child = TaxonomyNode(
        id=uuid.uuid4(),
        name="Machine Learning",
        slug="machine-learning",
        parent_id=root.id,
        level=1,
        path="/computer-science/machine-learning",
        is_leaf=True,
        allow_resources=True
    )
    db_session.add(child)
    nodes.append(child)
    
    db_session.commit()
    for node in nodes:
        db_session.refresh(node)
    
    return nodes


def test_classification_triggered_during_ingestion(db_session, sample_resource, sample_taxonomy_nodes):
    """
    Test that ML classification is triggered during resource ingestion.
    
    Verifies:
    - Classification is called after embedding generation
    - Classification is called before quality scoring
    - Classification failures don't block ingestion
    
    Requirement: 12.1, 12.2
    """
    resource_id = str(sample_resource.id)
    
    # Mock external dependencies
    with patch('backend.app.services.resource_service.ce') as mock_ce, \
         patch('backend.app.services.resource_service.AICore') as mock_ai_core, \
         patch('backend.app.services.resource_service.get_classification_service') as mock_get_classifier, \
         patch('backend.app.services.resource_service.get_quality_analyzer') as mock_get_analyzer, \
         patch('backend.app.services.resource_service.get_authority_control') as mock_get_authority, \
         patch('backend.app.services.resource_service.ClassificationService') as mock_classification_service:
        
        # Setup mocks
        mock_ce.fetch_url.return_value = {
            'url': 'https://example.com/test',
            'status': 200,
            'html': '<html><body>Test content about machine learning</body></html>',
            'content_type': 'text/html'
        }
        
        mock_ce.extract_from_fetched.return_value = {
            'title': 'Introduction to Machine Learning',
            'text': 'This is a comprehensive guide to machine learning algorithms and techniques.'
        }
        
        mock_ce.archive_local.return_value = {
            'archive_path': '/archive/test.html'
        }
        
        # Mock AI Core
        mock_ai_instance = Mock()
        mock_ai_instance.generate_summary.return_value = "A guide to ML"
        mock_ai_instance.generate_tags.return_value = ["machine learning", "AI"]
        mock_ai_instance.generate_embedding.return_value = [0.1] * 768
        mock_ai_core.return_value = mock_ai_instance
        
        # Mock authority control
        mock_authority = Mock()
        mock_authority.normalize_subjects.return_value = ["machine learning", "AI"]
        mock_authority.normalize_creator.return_value = None
        mock_authority.normalize_publisher.return_value = None
        mock_get_authority.return_value = mock_authority
        
        # Mock rule-based classifier
        mock_classifier = Mock()
        mock_classifier.auto_classify.return_value = "000"
        mock_get_classifier.return_value = mock_classifier
        
        # Mock quality analyzer
        mock_analyzer = Mock()
        mock_analyzer.overall_quality_score.return_value = 0.85
        mock_get_analyzer.return_value = mock_analyzer
        
        # Mock ML classification service
        mock_ml_service_instance = Mock()
        mock_ml_service_instance.classify_resource.return_value = {
            'resource_id': resource_id,
            'method': 'ml',
            'classifications': [
                {
                    'taxonomy_node_id': str(sample_taxonomy_nodes[1].id),
                    'confidence': 0.92,
                    'needs_review': False
                }
            ],
            'filtered_count': 0
        }
        mock_classification_service.return_value = mock_ml_service_instance
        
        # Run ingestion
        process_ingestion(
            resource_id=resource_id,
            archive_root="storage/archive",
            ai=mock_ai_instance
        )
        
        # Verify classification service was called
        assert mock_classification_service.called, "ClassificationService should be instantiated"
        
        # Verify classify_resource was called with correct parameters
        mock_ml_service_instance.classify_resource.assert_called_once()
        call_args = mock_ml_service_instance.classify_resource.call_args
        assert call_args[1]['use_ml'], "Should use ML classification"
        
        # Verify resource was updated successfully
        db_session.refresh(sample_resource)
        assert sample_resource.ingestion_status == "completed"
        assert sample_resource.quality_score > 0


def test_classification_failure_does_not_block_ingestion(db_session, sample_resource):
    """
    Test that classification failures are handled gracefully.
    
    Verifies:
    - Ingestion completes even if classification fails
    - Error is logged but doesn't propagate
    - Resource status is still "completed"
    
    Requirement: 12.3
    """
    resource_id = str(sample_resource.id)
    
    # Mock external dependencies
    with patch('backend.app.services.resource_service.ce') as mock_ce, \
         patch('backend.app.services.resource_service.AICore') as mock_ai_core, \
         patch('backend.app.services.resource_service.get_classification_service') as mock_get_classifier, \
         patch('backend.app.services.resource_service.get_quality_analyzer') as mock_get_analyzer, \
         patch('backend.app.services.resource_service.get_authority_control') as mock_get_authority, \
         patch('backend.app.services.resource_service.ClassificationService') as mock_classification_service:
        
        # Setup mocks
        mock_ce.fetch_url.return_value = {
            'url': 'https://example.com/test',
            'status': 200,
            'html': '<html><body>Test content</body></html>',
            'content_type': 'text/html'
        }
        
        mock_ce.extract_from_fetched.return_value = {
            'title': 'Test Article',
            'text': 'Test content for classification failure test.'
        }
        
        mock_ce.archive_local.return_value = {
            'archive_path': '/archive/test.html'
        }
        
        # Mock AI Core
        mock_ai_instance = Mock()
        mock_ai_instance.generate_summary.return_value = "Test summary"
        mock_ai_instance.generate_tags.return_value = ["test"]
        mock_ai_instance.generate_embedding.return_value = [0.1] * 768
        mock_ai_core.return_value = mock_ai_instance
        
        # Mock authority control
        mock_authority = Mock()
        mock_authority.normalize_subjects.return_value = ["test"]
        mock_authority.normalize_creator.return_value = None
        mock_authority.normalize_publisher.return_value = None
        mock_get_authority.return_value = mock_authority
        
        # Mock rule-based classifier
        mock_classifier = Mock()
        mock_classifier.auto_classify.return_value = "000"
        mock_get_classifier.return_value = mock_classifier
        
        # Mock quality analyzer
        mock_analyzer = Mock()
        mock_analyzer.overall_quality_score.return_value = 0.75
        mock_get_analyzer.return_value = mock_analyzer
        
        # Mock ML classification service to raise an exception
        mock_ml_service_instance = Mock()
        mock_ml_service_instance.classify_resource.side_effect = Exception("Classification model not available")
        mock_classification_service.return_value = mock_ml_service_instance
        
        # Run ingestion - should complete despite classification failure
        process_ingestion(
            resource_id=resource_id,
            archive_root="storage/archive",
            ai=mock_ai_instance
        )
        
        # Verify resource ingestion completed successfully
        db_session.refresh(sample_resource)
        assert sample_resource.ingestion_status == "completed", "Ingestion should complete despite classification failure"
        assert sample_resource.quality_score > 0, "Quality score should be set"
        assert sample_resource.ingestion_error is None, "No ingestion error should be recorded"


def test_classification_executes_after_embeddings(db_session, sample_resource, sample_taxonomy_nodes):
    """
    Test that classification executes after embedding generation.
    
    Verifies:
    - Dense embedding is generated first
    - Sparse embedding is generated second
    - ML classification is executed third
    - Quality scoring happens after classification
    
    Requirement: 12.2
    """
    resource_id = str(sample_resource.id)
    
    # Track call order
    call_order = []
    
    def track_embedding(*args, **kwargs):
        call_order.append('dense_embedding')
        return [0.1] * 768
    
    def track_sparse_embedding(*args, **kwargs):
        call_order.append('sparse_embedding')
        return {'indices': [1, 2, 3], 'values': [0.5, 0.3, 0.2]}
    
    def track_classification(*args, **kwargs):
        call_order.append('classification')
        return {
            'resource_id': resource_id,
            'method': 'ml',
            'classifications': [],
            'filtered_count': 0
        }
    
    def track_quality(*args, **kwargs):
        call_order.append('quality_scoring')
        return 0.8
    
    # Mock external dependencies
    with patch('backend.app.services.resource_service.ce') as mock_ce, \
         patch('backend.app.services.resource_service.AICore') as mock_ai_core, \
         patch('backend.app.services.resource_service.get_classification_service') as mock_get_classifier, \
         patch('backend.app.services.resource_service.get_quality_analyzer') as mock_get_analyzer, \
         patch('backend.app.services.resource_service.get_authority_control') as mock_get_authority, \
         patch('backend.app.services.resource_service.SparseEmbeddingService') as mock_sparse_service, \
         patch('backend.app.services.resource_service.ClassificationService') as mock_classification_service:
        
        # Setup mocks
        mock_ce.fetch_url.return_value = {
            'url': 'https://example.com/test',
            'status': 200,
            'html': '<html><body>Test content</body></html>',
            'content_type': 'text/html'
        }
        
        mock_ce.extract_from_fetched.return_value = {
            'title': 'Test Article',
            'text': 'Test content for order verification.'
        }
        
        mock_ce.archive_local.return_value = {
            'archive_path': '/archive/test.html'
        }
        
        # Mock AI Core with tracking
        mock_ai_instance = Mock()
        mock_ai_instance.generate_summary.return_value = "Test summary"
        mock_ai_instance.generate_tags.return_value = ["test"]
        mock_ai_instance.generate_embedding.side_effect = track_embedding
        mock_ai_core.return_value = mock_ai_instance
        
        # Mock authority control
        mock_authority = Mock()
        mock_authority.normalize_subjects.return_value = ["test"]
        mock_authority.normalize_creator.return_value = None
        mock_authority.normalize_publisher.return_value = None
        mock_get_authority.return_value = mock_authority
        
        # Mock rule-based classifier
        mock_classifier = Mock()
        mock_classifier.auto_classify.return_value = "000"
        mock_get_classifier.return_value = mock_classifier
        
        # Mock sparse embedding service with tracking
        mock_sparse_instance = Mock()
        mock_sparse_instance.generate_sparse_embedding.side_effect = track_sparse_embedding
        mock_sparse_service.return_value = mock_sparse_instance
        
        # Mock ML classification service with tracking
        mock_ml_service_instance = Mock()
        mock_ml_service_instance.classify_resource.side_effect = track_classification
        mock_classification_service.return_value = mock_ml_service_instance
        
        # Mock quality analyzer with tracking
        mock_analyzer = Mock()
        mock_analyzer.overall_quality_score.side_effect = track_quality
        mock_get_analyzer.return_value = mock_analyzer
        
        # Run ingestion
        process_ingestion(
            resource_id=resource_id,
            archive_root="storage/archive",
            ai=mock_ai_instance
        )
        
        # Verify execution order
        assert 'dense_embedding' in call_order, "Dense embedding should be generated"
        assert 'sparse_embedding' in call_order, "Sparse embedding should be generated"
        assert 'classification' in call_order, "Classification should be executed"
        assert 'quality_scoring' in call_order, "Quality scoring should be executed"
        
        # Verify order: embeddings -> classification -> quality
        dense_idx = call_order.index('dense_embedding')
        sparse_idx = call_order.index('sparse_embedding')
        classification_idx = call_order.index('classification')
        quality_idx = call_order.index('quality_scoring')
        
        assert dense_idx < sparse_idx, "Dense embedding should come before sparse embedding"
        assert sparse_idx < classification_idx, "Sparse embedding should come before classification"
        assert classification_idx < quality_idx, "Classification should come before quality scoring"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
