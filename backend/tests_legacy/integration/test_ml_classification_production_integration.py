"""
Integration tests for MLClassificationService with production ML training features.

This module tests the integration of:
- Versioned model loading
- A/B testing support
- Prediction monitoring
- Backward compatibility

Requirements: 15.1, 15.2, 15.8
"""

import pytest
import json
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from backend.app.services.ml_classification_service import MLClassificationService


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def mock_model_files(tmp_path):
    """Create mock model files for testing."""
    # Create a temporary model directory structure
    model_dir = tmp_path / "models" / "classification" / "arxiv_v1.0.0"
    model_dir.mkdir(parents=True, exist_ok=True)

    # Create mock config.json
    config = {"model_type": "distilbert", "num_labels": 10}
    with open(model_dir / "config.json", "w") as f:
        json.dump(config, f)

    # Create mock label_map.json
    label_map = {
        "id_to_label": {str(i): f"label_{i}" for i in range(10)},
        "label_to_id": {f"label_{i}": i for i in range(10)},
    }
    with open(model_dir / "label_map.json", "w") as f:
        json.dump(label_map, f)

    # Create production symlink
    production_dir = tmp_path / "models" / "classification" / "production"
    production_dir.mkdir(parents=True, exist_ok=True)

    with open(production_dir / "config.json", "w") as f:
        json.dump(config, f)

    with open(production_dir / "label_map.json", "w") as f:
        json.dump(label_map, f)

    return tmp_path


class TestVersionedModelLoading:
    """Test versioned model loading functionality."""

    def test_load_production_version(self, mock_db, mock_model_files):
        """Test that MLClassificationService loads production version by default."""
        # Initialize service without version parameter
        service = MLClassificationService(db=mock_db)

        # Should use production version (None means production)
        assert service.model_version is None

    def test_load_specific_version(self, mock_db, mock_model_files):
        """Test that MLClassificationService loads specific version when requested."""
        # Initialize service with specific version
        service = MLClassificationService(db=mock_db, version="v1.0.0")

        # Should use specified version
        assert service.model_version == "v1.0.0"

    def test_backward_compatibility_model_version_param(self, mock_db):
        """Test backward compatibility with legacy model_version parameter."""
        # Initialize service with legacy model_version parameter
        service = MLClassificationService(db=mock_db, model_version="v1.0")

        # Should still work
        assert service.model_version == "v1.0"


class TestABTestingIntegration:
    """Test A/B testing integration in prediction endpoint."""

    @patch("backend.scripts.deployment.ab_testing.ABTestingFramework")
    def test_ab_testing_routing(self, mock_ab_framework, mock_db):
        """Test that predictions are routed correctly in A/B tests."""
        # Setup mock A/B testing framework
        mock_ab_instance = Mock()
        mock_ab_instance.route_prediction.return_value = "treatment"
        mock_ab_framework.return_value = mock_ab_instance

        # Create service
        service = MLClassificationService(db=mock_db)

        # Mock model loading
        service.model = Mock()
        service.tokenizer = Mock()
        service.device = "cpu"
        service.id_to_label = {0: "label_0", 1: "label_1"}

        # Mock tokenizer and model outputs
        mock_tensor = Mock()
        mock_tensor.to.return_value = mock_tensor
        service.tokenizer.return_value = {
            "input_ids": mock_tensor,
            "attention_mask": mock_tensor,
        }

        mock_outputs = Mock()
        mock_logits = Mock()
        mock_logits.cpu.return_value.numpy.return_value = [[0.9, 0.1]]
        mock_outputs.logits = mock_logits
        service.model.return_value = mock_outputs

        # Make prediction with A/B testing
        with patch("torch.no_grad"):
            with patch("torch.sigmoid") as mock_sigmoid:
                mock_sigmoid_result = Mock()
                mock_sigmoid_result.cpu.return_value.numpy.return_value = [[0.9, 0.1]]
                mock_sigmoid.return_value = mock_sigmoid_result

                result = service.predict(
                    text="Test text", user_id="user123", experiment_id="exp_001"
                )

        # Verify A/B testing was called
        mock_ab_instance.route_prediction.assert_called_once_with("exp_001", "user123")

        # Verify result is ClassificationResult domain object
        from backend.app.domain.classification import ClassificationResult

        assert isinstance(result, ClassificationResult)
        assert result.model_version is not None
        assert result.predictions is not None

    @patch("backend.scripts.deployment.ab_testing.ABTestingFramework")
    def test_ab_testing_logging(self, mock_ab_framework, mock_db):
        """Test that predictions are logged for A/B testing analysis."""
        # Setup mock A/B testing framework
        mock_ab_instance = Mock()
        mock_ab_instance.route_prediction.return_value = "control"
        mock_ab_framework.return_value = mock_ab_instance

        # Create service
        service = MLClassificationService(db=mock_db)

        # Mock model loading
        service.model = Mock()
        service.tokenizer = Mock()
        service.device = "cpu"
        service.id_to_label = {0: "label_0"}
        service.model_version = "v1.0.0"

        # Mock tokenizer and model outputs
        mock_tensor = Mock()
        mock_tensor.to.return_value = mock_tensor
        service.tokenizer.return_value = {
            "input_ids": mock_tensor,
            "attention_mask": mock_tensor,
        }

        mock_outputs = Mock()
        mock_logits = Mock()
        mock_logits.cpu.return_value.numpy.return_value = [[0.9]]
        mock_outputs.logits = mock_logits
        service.model.return_value = mock_outputs

        # Make prediction with A/B testing
        with patch("torch.no_grad"):
            with patch("torch.sigmoid") as mock_sigmoid:
                mock_sigmoid_result = Mock()
                mock_sigmoid_result.cpu.return_value.numpy.return_value = [[0.9]]
                mock_sigmoid.return_value = mock_sigmoid_result

                service.predict(
                    text="Test text", user_id="user123", experiment_id="exp_001"
                )

        # Verify prediction was logged
        mock_ab_instance.log_prediction.assert_called_once()
        call_args = mock_ab_instance.log_prediction.call_args
        assert call_args[1]["experiment_id"] == "exp_001"
        assert call_args[1]["version"] == "v1.0.0"


class TestPredictionMonitoring:
    """Test prediction monitoring integration."""

    def test_monitor_initialization(self, mock_db):
        """Test that PredictionMonitor is initialized with service."""
        service = MLClassificationService(db=mock_db)

        # Verify monitor is initialized
        assert hasattr(service, "monitor")
        assert service.monitor is not None

    def test_prediction_logging_to_monitor(self, mock_db):
        """Test that predictions are logged to monitor."""
        service = MLClassificationService(db=mock_db)

        # Mock model loading
        service.model = Mock()
        service.tokenizer = Mock()
        service.device = "cpu"
        service.id_to_label = {0: "label_0"}

        # Mock tokenizer and model outputs
        mock_tensor = Mock()
        mock_tensor.to.return_value = mock_tensor
        service.tokenizer.return_value = {
            "input_ids": mock_tensor,
            "attention_mask": mock_tensor,
        }

        mock_outputs = Mock()
        mock_logits = Mock()
        mock_logits.cpu.return_value.numpy.return_value = [[0.9]]
        mock_outputs.logits = mock_logits
        service.model.return_value = mock_outputs

        # Mock monitor
        service.monitor = Mock()

        # Make prediction
        with patch("torch.no_grad"):
            with patch("torch.sigmoid") as mock_sigmoid:
                mock_sigmoid_result = Mock()
                mock_sigmoid_result.cpu.return_value.numpy.return_value = [[0.9]]
                mock_sigmoid.return_value = mock_sigmoid_result

                service.predict(text="Test text")

        # Verify monitor was called
        service.monitor.log_prediction.assert_called_once()
        call_args = service.monitor.log_prediction.call_args
        assert call_args[1]["input_text"] == "Test text"
        assert "latency_ms" in call_args[1]

    def test_get_metrics_method(self, mock_db):
        """Test that get_metrics method exposes monitor metrics."""
        service = MLClassificationService(db=mock_db)

        # Mock monitor
        service.monitor = Mock()
        service.monitor.get_metrics.return_value = {
            "total_predictions": 100,
            "error_rate": 0.01,
            "latency_p95": 95.5,
        }

        # Get metrics
        metrics = service.get_metrics(window_minutes=30)

        # Verify monitor was called
        service.monitor.get_metrics.assert_called_once_with(window_minutes=30)

        # Verify metrics returned
        assert metrics["total_predictions"] == 100
        assert metrics["error_rate"] == 0.01
        assert metrics["latency_p95"] == 95.5


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""

    def test_predict_without_ab_testing(self, mock_db):
        """Test that predict works without A/B testing parameters."""
        service = MLClassificationService(db=mock_db)

        # Mock model loading
        service.model = Mock()
        service.tokenizer = Mock()
        service.device = "cpu"
        service.id_to_label = {0: "label_0"}

        # Mock tokenizer and model outputs
        mock_tensor = Mock()
        mock_tensor.to.return_value = mock_tensor
        service.tokenizer.return_value = {
            "input_ids": mock_tensor,
            "attention_mask": mock_tensor,
        }

        mock_outputs = Mock()
        mock_logits = Mock()
        mock_logits.cpu.return_value.numpy.return_value = [[0.9]]
        mock_outputs.logits = mock_logits
        service.model.return_value = mock_outputs

        # Make prediction without A/B testing parameters
        with patch("torch.no_grad"):
            with patch("torch.sigmoid") as mock_sigmoid:
                mock_sigmoid_result = Mock()
                mock_sigmoid_result.cpu.return_value.numpy.return_value = [[0.9]]
                mock_sigmoid.return_value = mock_sigmoid_result

                result = service.predict(text="Test text")

        # Verify result is ClassificationResult domain object
        from backend.app.domain.classification import ClassificationResult

        assert isinstance(result, ClassificationResult)
        assert result.predictions is not None
        assert len(result.predictions) > 0

    def test_initialization_without_version(self, mock_db):
        """Test that service initializes without version parameter."""
        # Should not raise any errors
        service = MLClassificationService(db=mock_db)

        # Should default to None (production)
        assert service.model_version is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
