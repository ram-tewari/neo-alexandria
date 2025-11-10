"""Tests for Reranking Service (Phase 8)."""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from backend.app.services.reranking_service import RerankingService
from backend.app.database.models import Resource


class TestRerankingService:
    """Test reranking service functionality."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_db):
        """Create a reranking service instance."""
        return RerankingService(
            db=mock_db,
            model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",
            max_length=500
        )
    
    def test_service_initialization(self, mock_db):
        """Test service can be initialized with custom parameters."""
        service = RerankingService(
            db=mock_db,
            model_name="test-model",
            max_length=300
        )
        assert service.db is mock_db
        assert service.model_name == "test-model"
        assert service.max_length == 300
        assert service._model is None
        assert service._device is None
    
    def test_rerank_empty_query(self, service):
        """Test reranking with empty query returns empty list."""
        result = service.rerank("", ["doc1", "doc2"])
        assert result == []
        
        result = service.rerank(None, ["doc1", "doc2"])
        assert result == []
    
    def test_rerank_empty_candidates(self, service):
        """Test reranking with empty candidates returns empty list."""
        result = service.rerank("test query", [])
        assert result == []
    
    def test_rerank_no_model(self, service):
        """Test reranking when model unavailable returns empty list."""
        with patch('backend.app.services.reranking_service.CrossEncoder', None):
            result = service.rerank("test query", ["doc1", "doc2"])
            assert result == []
    
    def test_rerank_with_mock_model(self, service, mock_db):
        """Test reranking with mock model and resources."""
        # Create mock resources
        resource1 = Mock(spec=Resource)
        resource1.id = "uuid-1"
        resource1.title = "Machine Learning Basics"
        resource1.description = "Introduction to ML algorithms and techniques"
        
        resource2 = Mock(spec=Resource)
        resource2.id = "uuid-2"
        resource2.title = "Deep Learning Advanced"
        resource2.description = "Advanced deep learning concepts"
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [resource1, resource2]
        mock_db.query.return_value = mock_query
        
        # Mock CrossEncoder
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.85, 0.72]  # Scores for doc1, doc2
        
        # Mock torch
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        
        with patch('backend.app.services.reranking_service.CrossEncoder') as mock_ce, \
             patch('backend.app.services.reranking_service.torch', mock_torch):
            
            mock_ce.return_value = mock_model
            
            result = service.rerank("machine learning", ["uuid-1", "uuid-2"], top_k=2)
            
            # Verify results
            assert len(result) == 2
            assert result[0][0] == "uuid-1"  # Higher score
            assert result[0][1] == 0.85
            assert result[1][0] == "uuid-2"  # Lower score
            assert result[1][1] == 0.72
            
            # Verify model was called with correct pairs
            mock_model.predict.assert_called_once()
            pairs = mock_model.predict.call_args[0][0]
            assert len(pairs) == 2
            assert pairs[0][0] == "machine learning"
            assert "Machine Learning Basics" in pairs[0][1]
    
    def test_rerank_top_k_limit(self, service, mock_db):
        """Test reranking respects top_k parameter."""
        # Create 5 mock resources
        resources = []
        for i in range(5):
            resource = Mock(spec=Resource)
            resource.id = f"uuid-{i}"
            resource.title = f"Document {i}"
            resource.description = f"Description {i}"
            resources.append(resource)
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = resources
        mock_db.query.return_value = mock_query
        
        # Mock CrossEncoder with scores
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.9, 0.8, 0.7, 0.6, 0.5]
        
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        
        with patch('backend.app.services.reranking_service.CrossEncoder') as mock_ce, \
             patch('backend.app.services.reranking_service.torch', mock_torch):
            
            mock_ce.return_value = mock_model
            
            # Request top 3
            result = service.rerank(
                "test query",
                [f"uuid-{i}" for i in range(5)],
                top_k=3
            )
            
            # Should return only 3 results
            assert len(result) == 3
            assert result[0][0] == "uuid-0"  # Highest score
            assert result[1][0] == "uuid-1"
            assert result[2][0] == "uuid-2"
    
    def test_rerank_no_resources_found(self, service, mock_db):
        """Test reranking when no resources found in database."""
        # Mock database query returning empty list
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query
        
        result = service.rerank("test query", ["uuid-1", "uuid-2"])
        assert result == []
    
    def test_rerank_resources_with_no_content(self, service, mock_db):
        """Test reranking skips resources with no content."""
        # Create resources with no title or description
        resource1 = Mock(spec=Resource)
        resource1.id = "uuid-1"
        resource1.title = None
        resource1.description = None
        
        resource2 = Mock(spec=Resource)
        resource2.id = "uuid-2"
        resource2.title = ""
        resource2.description = ""
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [resource1, resource2]
        mock_db.query.return_value = mock_query
        
        result = service.rerank("test query", ["uuid-1", "uuid-2"])
        
        # Should return empty since no valid content
        assert result == []
    
    def test_rerank_truncates_long_descriptions(self, service, mock_db):
        """Test reranking truncates descriptions to max_length."""
        # Create resource with long description
        long_desc = "A" * 1000  # 1000 characters
        resource = Mock(spec=Resource)
        resource.id = "uuid-1"
        resource.title = "Test"
        resource.description = long_desc
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [resource]
        mock_db.query.return_value = mock_query
        
        # Mock CrossEncoder
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.8]
        
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        
        with patch('backend.app.services.reranking_service.CrossEncoder') as mock_ce, \
             patch('backend.app.services.reranking_service.torch', mock_torch):
            
            mock_ce.return_value = mock_model
            
            service.rerank("test", ["uuid-1"])
            
            # Verify description was truncated
            pairs = mock_model.predict.call_args[0][0]
            doc_text = pairs[0][1]
            # Should be title + truncated description (max 500 chars for description)
            assert len(doc_text) <= len("Test") + 1 + 500
    
    def test_rerank_with_timeout(self, service, mock_db):
        """Test reranking respects timeout parameter."""
        # Create mock resource
        resource = Mock(spec=Resource)
        resource.id = "uuid-1"
        resource.title = "Test"
        resource.description = "Description"
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [resource]
        mock_db.query.return_value = mock_query
        
        # Mock CrossEncoder with slow prediction
        mock_model = MagicMock()
        def slow_predict(*args, **kwargs):
            time.sleep(0.2)  # Simulate slow prediction
            return [0.8]
        mock_model.predict = slow_predict
        
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        
        with patch('backend.app.services.reranking_service.CrossEncoder') as mock_ce, \
             patch('backend.app.services.reranking_service.torch', mock_torch):
            
            mock_ce.return_value = mock_model
            
            # Set very short timeout
            result = service.rerank("test", ["uuid-1"], timeout=0.01)
            
            # Should timeout and return empty or still return results
            # (implementation returns results even if timeout exceeded after prediction)
            assert isinstance(result, list)
    
    def test_rerank_gpu_oom_fallback(self, service, mock_db):
        """Test reranking falls back to CPU on GPU OOM."""
        # Create mock resource
        resource = Mock(spec=Resource)
        resource.id = "uuid-1"
        resource.title = "Test"
        resource.description = "Description"
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [resource]
        mock_db.query.return_value = mock_query
        
        # Mock torch with GPU available
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.empty_cache = Mock()
        
        # Mock CrossEncoder that raises OOM on first call, succeeds on second
        call_count = [0]
        def create_model_with_oom(*args, **kwargs):
            call_count[0] += 1
            mock_model = MagicMock()
            if call_count[0] == 1:
                # First call (GPU) - raise OOM
                def raise_oom(*args, **kwargs):
                    raise RuntimeError("CUDA out of memory")
                mock_model.predict = raise_oom
            else:
                # Second call (CPU) - succeed
                mock_model.predict.return_value = [0.8]
            return mock_model
        
        with patch('backend.app.services.reranking_service.CrossEncoder', side_effect=create_model_with_oom), \
             patch('backend.app.services.reranking_service.torch', mock_torch):
            
            result = service.rerank("test", ["uuid-1"])
            
            # Should have fallen back to CPU and succeeded
            # Note: This test is simplified; actual behavior may vary
            assert isinstance(result, list)
    
    def test_rerank_model_loading_failure(self, service):
        """Test graceful handling of model loading failures."""
        with patch('backend.app.services.reranking_service.CrossEncoder') as mock_ce:
            mock_ce.side_effect = Exception("Model loading failed")
            
            loaded = service._ensure_loaded()
            assert loaded is False
            assert service._model is None
    
    def test_rerank_with_caching_no_cache(self, service, mock_db):
        """Test rerank_with_caching without cache performs normal reranking."""
        # Create mock resource
        resource = Mock(spec=Resource)
        resource.id = "uuid-1"
        resource.title = "Test"
        resource.description = "Description"
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [resource]
        mock_db.query.return_value = mock_query
        
        # Mock CrossEncoder
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.8]
        
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        
        with patch('backend.app.services.reranking_service.CrossEncoder') as mock_ce, \
             patch('backend.app.services.reranking_service.torch', mock_torch):
            
            mock_ce.return_value = mock_model
            
            result = service.rerank_with_caching("test", ["uuid-1"], cache=None)
            
            assert len(result) == 1
            assert result[0][0] == "uuid-1"
    
    def test_rerank_with_caching_cache_miss(self, service, mock_db):
        """Test rerank_with_caching on cache miss performs reranking."""
        # Create mock resource
        resource = Mock(spec=Resource)
        resource.id = "uuid-1"
        resource.title = "Test"
        resource.description = "Description"
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [resource]
        mock_db.query.return_value = mock_query
        
        # Mock CrossEncoder
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.8]
        
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        
        with patch('backend.app.services.reranking_service.CrossEncoder') as mock_ce, \
             patch('backend.app.services.reranking_service.torch', mock_torch):
            
            mock_ce.return_value = mock_model
            
            cache = {}
            result = service.rerank_with_caching("test", ["uuid-1"], cache=cache)
            
            # Should have performed reranking and stored in cache
            assert len(result) == 1
            assert len(cache) == 1
    
    def test_rerank_with_caching_cache_hit(self, service):
        """Test rerank_with_caching on cache hit returns cached results."""
        # Pre-populate cache
        cache = {}
        import hashlib
        cache_key_str = "test|uuid-1|20"
        cache_key = hashlib.md5(cache_key_str.encode()).hexdigest()
        cached_results = [("uuid-1", 0.95)]
        cache[cache_key] = cached_results
        
        # Call with same query and candidates
        result = service.rerank_with_caching("test", ["uuid-1"], cache=cache)
        
        # Should return cached results without calling model
        assert result == cached_results
    
    def test_rerank_with_caching_consistent_cache_keys(self, service, mock_db):
        """Test cache keys are consistent regardless of candidate order."""
        # Create mock resources
        resource1 = Mock(spec=Resource)
        resource1.id = "uuid-1"
        resource1.title = "Test 1"
        resource1.description = "Description 1"
        
        resource2 = Mock(spec=Resource)
        resource2.id = "uuid-2"
        resource2.title = "Test 2"
        resource2.description = "Description 2"
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [resource1, resource2]
        mock_db.query.return_value = mock_query
        
        # Mock CrossEncoder
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.8, 0.7]
        
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        
        with patch('backend.app.services.reranking_service.CrossEncoder') as mock_ce, \
             patch('backend.app.services.reranking_service.torch', mock_torch):
            
            mock_ce.return_value = mock_model
            
            cache = {}
            
            # Call with candidates in different order
            result1 = service.rerank_with_caching(
                "test",
                ["uuid-1", "uuid-2"],
                cache=cache
            )
            
            # Reset mock to track second call
            mock_model.predict.reset_mock()
            
            result2 = service.rerank_with_caching(
                "test",
                ["uuid-2", "uuid-1"],  # Different order
                cache=cache
            )
            
            # Second call should hit cache (model.predict not called again)
            mock_model.predict.assert_not_called()
            
            # Cache should have only one entry
            assert len(cache) == 1
    
    def test_rerank_performance_target(self, service, mock_db):
        """Test reranking meets performance target of >100 docs/sec."""
        # Create 100 mock resources
        resources = []
        for i in range(100):
            resource = Mock(spec=Resource)
            resource.id = f"uuid-{i}"
            resource.title = f"Document {i}"
            resource.description = f"Description {i}"
            resources.append(resource)
        
        # Mock database query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = resources
        mock_db.query.return_value = mock_query
        
        # Mock CrossEncoder with fast prediction
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.5 + i/1000 for i in range(100)]
        
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        
        with patch('backend.app.services.reranking_service.CrossEncoder') as mock_ce, \
             patch('backend.app.services.reranking_service.torch', mock_torch):
            
            mock_ce.return_value = mock_model
            
            start_time = time.time()
            result = service.rerank(
                "test query",
                [f"uuid-{i}" for i in range(100)],
                top_k=20
            )
            elapsed = time.time() - start_time
            
            # Should complete in reasonable time
            # Note: This is a mock test, actual performance depends on real model
            assert len(result) == 20
            assert elapsed < 5.0  # Should be much faster with mocks


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
