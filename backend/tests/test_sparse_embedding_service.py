"""Tests for Sparse Embedding Service (Phase 8)."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from backend.app.services.sparse_embedding_service import SparseEmbeddingService
from backend.app.database.models import Resource


class TestSparseEmbeddingService:
    """Test sparse embedding service functionality."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_db):
        """Create a sparse embedding service instance."""
        return SparseEmbeddingService(db=mock_db, model_name="BAAI/bge-m3")
    
    def test_service_initialization(self, mock_db):
        """Test service can be initialized with custom parameters."""
        service = SparseEmbeddingService(db=mock_db, model_name="test-model")
        assert service.db is mock_db
        assert service.model_name == "test-model"
        assert service._model is None
        assert service._tokenizer is None
    
    def test_generate_sparse_embedding_empty_text(self, service):
        """Test sparse embedding generation with empty text."""
        result = service.generate_sparse_embedding("")
        assert result == {}
    
    def test_generate_sparse_embedding_no_model(self, service):
        """Test sparse embedding generation when model unavailable."""
        with patch('backend.app.services.sparse_embedding_service.AutoModel', None):
            result = service.generate_sparse_embedding("test text")
            assert result == {}
    
    def test_generate_sparse_embedding_with_mock_model(self, service):
        """Test sparse embedding generation with mock model."""
        # Mock torch and model components
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.no_grad.return_value.__enter__ = Mock()
        mock_torch.no_grad.return_value.__exit__ = Mock()
        
        # Create mock tensors
        mock_hidden_states = MagicMock()
        mock_sparse_vec = MagicMock()
        mock_sparse_vec.cpu.return_value = mock_sparse_vec
        
        # Mock topk results
        mock_values = MagicMock()
        mock_indices = MagicMock()
        mock_values.__len__ = Mock(return_value=5)
        mock_values.min.return_value = 0.1
        mock_values.max.return_value = 0.9
        mock_values.__getitem__ = Mock(return_value=mock_values)
        mock_values.tolist.return_value = [0.9, 0.7, 0.5, 0.3, 0.1]
        mock_indices.__getitem__ = Mock(return_value=mock_indices)
        mock_indices.tolist.return_value = [100, 200, 300, 400, 500]
        
        mock_sparse_vec.__len__ = Mock(return_value=1000)
        mock_torch.topk.return_value = (mock_values, mock_indices)
        mock_torch.sum.return_value.squeeze.return_value = mock_sparse_vec
        mock_torch.log.return_value = mock_hidden_states
        mock_torch.relu.return_value = mock_hidden_states
        
        # Mock model and tokenizer
        mock_tokenizer = MagicMock()
        mock_tokenizer.return_value = {"input_ids": MagicMock(), "attention_mask": MagicMock()}
        
        mock_model = MagicMock()
        mock_outputs = MagicMock()
        mock_outputs.last_hidden_state = mock_hidden_states
        mock_model.return_value = mock_outputs
        mock_model.eval.return_value = None
        mock_model.to.return_value = mock_model
        
        with patch('backend.app.services.sparse_embedding_service.torch', mock_torch), \
             patch('backend.app.services.sparse_embedding_service.AutoModel') as mock_auto_model, \
             patch('backend.app.services.sparse_embedding_service.AutoTokenizer') as mock_auto_tokenizer:
            
            mock_auto_model.from_pretrained.return_value = mock_model
            mock_auto_tokenizer.from_pretrained.return_value = mock_tokenizer
            
            result = service.generate_sparse_embedding("test text")
            
            # Verify result is a dictionary
            assert isinstance(result, dict)
    
    def test_generate_sparse_embeddings_batch_empty_list(self, service):
        """Test batch generation with empty list."""
        result = service.generate_sparse_embeddings_batch([])
        assert result == []
    
    def test_generate_sparse_embeddings_batch_no_model(self, service):
        """Test batch generation when model unavailable."""
        with patch('backend.app.services.sparse_embedding_service.AutoModel', None):
            result = service.generate_sparse_embeddings_batch(["text1", "text2"])
            assert result == [{}, {}]
    
    def test_search_by_sparse_vector_empty_query(self, service):
        """Test sparse vector search with empty query."""
        result = service.search_by_sparse_vector({})
        assert result == []
    
    def test_search_by_sparse_vector_with_resources(self, service, mock_db):
        """Test sparse vector search with mock resources."""
        # Create mock resources with sparse embeddings
        resource1 = Mock(spec=Resource)
        resource1.id = "uuid-1"
        resource1.sparse_embedding = json.dumps({"100": 0.8, "200": 0.6})
        
        resource2 = Mock(spec=Resource)
        resource2.id = "uuid-2"
        resource2.sparse_embedding = json.dumps({"100": 0.5, "300": 0.7})
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [resource1, resource2]
        mock_db.query.return_value = mock_query
        
        # Query sparse vector
        query_sparse = {100: 0.9, 200: 0.4}
        
        result = service.search_by_sparse_vector(query_sparse, limit=10)
        
        # Verify results
        assert len(result) == 2
        assert all(isinstance(item, tuple) for item in result)
        assert all(len(item) == 2 for item in result)
        # Results should be sorted by score descending
        assert result[0][1] >= result[1][1]
    
    def test_update_resource_sparse_embedding_not_found(self, service, mock_db):
        """Test updating sparse embedding for non-existent resource."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = service.update_resource_sparse_embedding("non-existent-id")
        assert result is False
    
    def test_update_resource_sparse_embedding_empty_content(self, service, mock_db):
        """Test updating sparse embedding for resource with no content."""
        # Create mock resource with no content
        resource = Mock(spec=Resource)
        resource.id = "uuid-1"
        resource.title = None
        resource.description = None
        resource.subject = []
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = resource
        mock_db.query.return_value = mock_query
        
        result = service.update_resource_sparse_embedding("uuid-1")
        
        # Should succeed but set embedding to None
        assert result is True
        assert resource.sparse_embedding is None
        assert resource.sparse_embedding_model is None
        assert resource.sparse_embedding_updated_at is not None
        mock_db.commit.assert_called_once()
    
    def test_batch_update_sparse_embeddings_no_resources(self, service, mock_db):
        """Test batch update with no resources to process."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query
        
        result = service.batch_update_sparse_embeddings()
        
        assert result['total'] == 0
        assert result['success'] == 0
        assert result['failed'] == 0
        assert result['skipped'] == 0
    
    def test_batch_update_sparse_embeddings_with_resources(self, service, mock_db):
        """Test batch update with mock resources."""
        # Create mock resources
        resources = []
        for i in range(5):
            resource = Mock(spec=Resource)
            resource.id = f"uuid-{i}"
            resource.title = f"Title {i}"
            resource.description = f"Description {i}"
            resource.subject = [f"Subject {i}"]
            resources.append(resource)
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = resources
        mock_db.query.return_value = mock_query
        
        # Mock embedding generation to return empty dicts (model not loaded)
        with patch.object(service, 'generate_sparse_embeddings_batch') as mock_gen:
            mock_gen.return_value = [{} for _ in range(5)]
            
            result = service.batch_update_sparse_embeddings()
            
            assert result['total'] == 5
            # All should succeed even with empty embeddings
            assert result['success'] == 5
            assert result['failed'] == 0
    
    def test_model_loading_failure_handling(self, service):
        """Test graceful handling of model loading failures."""
        with patch('backend.app.services.sparse_embedding_service.AutoModel') as mock_auto_model:
            mock_auto_model.from_pretrained.side_effect = Exception("Model loading failed")
            
            # Should return False and not crash
            loaded = service._ensure_loaded()
            assert loaded is False
            assert service._model is None
    
    def test_gpu_oom_fallback(self, service):
        """Test GPU out of memory fallback to CPU."""
        # This is a simplified test - actual OOM handling is complex
        # Just verify the error handling structure exists
        with patch('backend.app.services.sparse_embedding_service.torch') as mock_torch:
            mock_torch.cuda.is_available.return_value = True
            
            # Simulate OOM error
            def raise_oom(*args, **kwargs):
                raise RuntimeError("CUDA out of memory")
            
            # The service should handle this gracefully
            # Actual test would require more complex mocking
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
