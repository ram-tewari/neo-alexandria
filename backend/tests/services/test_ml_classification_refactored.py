"""
Test for refactored ml_classification_service.py - Replace Primitive with Object

This test verifies that the predict() method now returns ClassificationResult
domain objects instead of primitive dictionaries.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import torch

from backend.app.services.ml_classification_service import MLClassificationService
from backend.app.domain.classification import ClassificationResult, ClassificationPrediction


class TestMLClassificationServiceRefactored:
    """Test suite for refactored ML classification service."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_db):
        """Create ML classification service instance."""
        service = MLClassificationService(mock_db, model_name="distilbert-base-uncased")
        
        # Mock the model and tokenizer
        service.model = Mock()
        service.tokenizer = Mock()
        service.device = torch.device("cpu")
        
        # Set up label mappings
        service.id_to_label = {
            0: "node_id_1",
            1: "node_id_2",
            2: "node_id_3"
        }
        service.label_to_id = {
            "node_id_1": 0,
            "node_id_2": 1,
            "node_id_3": 2
        }
        
        # Mock the monitor
        service.monitor = Mock()
        
        return service
    
    def test_predict_returns_classification_result(self, service):
        """Test that predict() returns ClassificationResult domain object."""
        # Mock tokenizer
        service.tokenizer.return_value = {
            'input_ids': torch.tensor([[1, 2, 3]]),
            'attention_mask': torch.tensor([[1, 1, 1]])
        }
        
        # Mock model output
        mock_outputs = Mock()
        mock_outputs.logits = torch.tensor([[2.0, 1.5, 0.5]])
        service.model.return_value = mock_outputs
        
        # Make prediction
        with patch('torch.no_grad'):
            with patch('torch.sigmoid') as mock_sigmoid:
                mock_sigmoid_result = Mock()
                mock_sigmoid_result.cpu.return_value.numpy.return_value = np.array([[0.95, 0.87, 0.62]])
                mock_sigmoid.return_value = mock_sigmoid_result
                
                result = service.predict(text="Test text", top_k=3)
        
        # Verify result is ClassificationResult
        assert isinstance(result, ClassificationResult)
        assert result.model_version == "production"
        assert result.inference_time_ms > 0
        assert len(result.predictions) == 3
    
    def test_predict_returns_classification_predictions(self, service):
        """Test that predictions are ClassificationPrediction objects."""
        # Mock tokenizer
        service.tokenizer.return_value = {
            'input_ids': torch.tensor([[1, 2, 3]]),
            'attention_mask': torch.tensor([[1, 1, 1]])
        }
        
        # Mock model output
        mock_outputs = Mock()
        mock_outputs.logits = torch.tensor([[2.0, 1.5, 0.5]])
        service.model.return_value = mock_outputs
        
        # Make prediction
        with patch('torch.no_grad'):
            with patch('torch.sigmoid') as mock_sigmoid:
                mock_sigmoid_result = Mock()
                mock_sigmoid_result.cpu.return_value.numpy.return_value = np.array([[0.95, 0.87, 0.62]])
                mock_sigmoid.return_value = mock_sigmoid_result
                
                result = service.predict(text="Test text", top_k=3)
        
        # Verify predictions are ClassificationPrediction objects
        for pred in result.predictions:
            assert isinstance(pred, ClassificationPrediction)
            assert pred.taxonomy_id in ["node_id_1", "node_id_2", "node_id_3"]
            assert 0.0 <= pred.confidence <= 1.0
            assert pred.rank >= 1
    
    def test_predict_predictions_sorted_by_confidence(self, service):
        """Test that predictions are sorted by confidence (descending)."""
        # Mock tokenizer
        service.tokenizer.return_value = {
            'input_ids': torch.tensor([[1, 2, 3]]),
            'attention_mask': torch.tensor([[1, 1, 1]])
        }
        
        # Mock model output
        mock_outputs = Mock()
        mock_outputs.logits = torch.tensor([[2.0, 1.5, 0.5]])
        service.model.return_value = mock_outputs
        
        # Make prediction
        with patch('torch.no_grad'):
            with patch('torch.sigmoid') as mock_sigmoid:
                mock_sigmoid_result = Mock()
                mock_sigmoid_result.cpu.return_value.numpy.return_value = np.array([[0.95, 0.87, 0.62]])
                mock_sigmoid.return_value = mock_sigmoid_result
                
                result = service.predict(text="Test text", top_k=3)
        
        # Verify predictions are sorted by confidence
        confidences = [pred.confidence for pred in result.predictions]
        assert confidences == sorted(confidences, reverse=True)
        
        # Verify ranks are sequential
        ranks = [pred.rank for pred in result.predictions]
        assert ranks == [1, 2, 3]
    
    def test_predict_backward_compatibility_with_to_dict(self, service):
        """Test that ClassificationResult.to_dict() provides backward compatibility."""
        # Mock tokenizer
        service.tokenizer.return_value = {
            'input_ids': torch.tensor([[1, 2, 3]]),
            'attention_mask': torch.tensor([[1, 1, 1]])
        }
        
        # Mock model output
        mock_outputs = Mock()
        mock_outputs.logits = torch.tensor([[2.0, 1.5, 0.5]])
        service.model.return_value = mock_outputs
        
        # Make prediction
        with patch('torch.no_grad'):
            with patch('torch.sigmoid') as mock_sigmoid:
                mock_sigmoid_result = Mock()
                mock_sigmoid_result.cpu.return_value.numpy.return_value = np.array([[0.95, 0.87, 0.62]])
                mock_sigmoid.return_value = mock_sigmoid_result
                
                result = service.predict(text="Test text", top_k=3)
        
        # Convert to dict for backward compatibility
        result_dict = result.to_dict()
        
        # Verify dict structure
        assert 'predictions' in result_dict
        assert 'model_version' in result_dict
        assert 'inference_time_ms' in result_dict
        assert 'metadata' in result_dict
        
        # Verify predictions in dict format
        assert len(result_dict['predictions']) == 3
        for pred in result_dict['predictions']:
            assert 'taxonomy_id' in pred
            assert 'confidence' in pred
            assert 'rank' in pred
    
    def test_predict_domain_object_methods(self, service):
        """Test that domain object methods work correctly."""
        # Mock tokenizer
        service.tokenizer.return_value = {
            'input_ids': torch.tensor([[1, 2, 3]]),
            'attention_mask': torch.tensor([[1, 1, 1]])
        }
        
        # Mock model output
        mock_outputs = Mock()
        mock_outputs.logits = torch.tensor([[2.0, 1.5, 0.5]])
        service.model.return_value = mock_outputs
        
        # Make prediction
        with patch('torch.no_grad'):
            with patch('torch.sigmoid') as mock_sigmoid:
                mock_sigmoid_result = Mock()
                mock_sigmoid_result.cpu.return_value.numpy.return_value = np.array([[0.95, 0.45, 0.62]])
                mock_sigmoid.return_value = mock_sigmoid_result
                
                result = service.predict(text="Test text", top_k=3)
        
        # Test domain object methods
        high_conf = result.get_high_confidence(threshold=0.8)
        assert len(high_conf) == 1
        assert high_conf[0].confidence >= 0.8
        
        low_conf = result.get_low_confidence(threshold=0.5)
        assert len(low_conf) == 1
        assert low_conf[0].confidence < 0.5
        
        top_2 = result.get_top_k(2)
        assert len(top_2) == 2
        
        best = result.get_best_prediction()
        assert best.confidence == max(pred.confidence for pred in result.predictions)
