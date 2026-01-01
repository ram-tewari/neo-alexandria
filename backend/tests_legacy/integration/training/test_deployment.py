"""
Integration tests for deployment infrastructure.

This module tests:
- Blue-green deployment switches traffic correctly
- Canary deployment gradual rollout works
- Automatic rollback triggers on high error rate
- Deployment validation detects issues
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from backend.scripts.deployment.blue_green import BlueGreenDeployment
from backend.scripts.deployment.canary import CanaryDeployment
from backend.scripts.deployment.rollback_monitor import (
    monitor_and_rollback,
    get_production_metrics,
    rollback_to_previous_version
)
from backend.scripts.deployment.validate import validate_deployment
from backend.scripts.deployment.model_versioning import ModelVersioning


@pytest.fixture
def temp_model_dir():
    """Create temporary directory for test models."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_model_data():
    """Create mock model data for testing."""
    import torch
    from transformers import AutoTokenizer
    
    # Create a minimal mock model
    class MockModel:
        def __init__(self):
            self.config = MagicMock()
            self.config.num_labels = 10
        
        def to(self, device):
            return self
        
        def eval(self):
            return self
        
        def __call__(self, **inputs):
            # Return mock outputs
            batch_size = inputs['input_ids'].shape[0]
            logits = torch.randn(batch_size, 10)
            
            outputs = MagicMock()
            outputs.logits = logits
            return outputs
    
    # Use a real tokenizer for testing
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
    
    return {
        'model': MockModel(),
        'tokenizer': tokenizer,
        'label_map': {
            'label_to_id': {f'class_{i}': i for i in range(10)},
            'id_to_label': {i: f'class_{i}' for i in range(10)}
        }
    }


@pytest.fixture
def setup_test_versions(temp_model_dir, mock_model_data):
    """Set up test model versions."""
    versioning = ModelVersioning(base_dir=temp_model_dir)
    
    # Create mock model files
    model_dir = Path(temp_model_dir) / "test_model"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Save mock files
    (model_dir / "config.json").write_text(json.dumps({"model_type": "distilbert"}))
    (model_dir / "pytorch_model.bin").write_bytes(b"mock model data")
    
    # Create test versions
    metadata_v1 = {
        "model_name": "distilbert-base-uncased",
        "dataset": {"size": 1000},
        "metrics": {"accuracy": 0.90}
    }
    
    metadata_v2 = {
        "model_name": "distilbert-base-uncased",
        "dataset": {"size": 1500},
        "metrics": {"accuracy": 0.92}
    }
    
    # Create versions
    with patch.object(versioning, 'load_version', return_value=(mock_model_data, metadata_v1)):
        versioning.create_version(str(model_dir), "v1.0.0", metadata_v1)
        versioning.create_version(str(model_dir), "v1.1.0", metadata_v2)
    
    # Promote v1.0.0 to production
    versioning.promote_to_production("v1.0.0")
    
    return versioning


class TestBlueGreenDeployment:
    """Test blue-green deployment functionality."""
    
    def test_blue_green_deployment_initialization(self, temp_model_dir, setup_test_versions):
        """Test blue-green deployment initializes correctly."""
        deployment = BlueGreenDeployment(
            blue_version="v1.0.0",
            green_version="v1.1.0",
            base_dir=temp_model_dir
        )
        
        assert deployment.blue_version == "v1.0.0"
        assert deployment.green_version == "v1.1.0"
        assert deployment.active == "blue"
        assert len(deployment.deployment_log) > 0
    
    def test_deploy_green_success(self, temp_model_dir, setup_test_versions, mock_model_data):
        """Test deploying to green environment."""
        deployment = BlueGreenDeployment(
            blue_version="v1.0.0",
            green_version="v1.1.0",
            base_dir=temp_model_dir
        )
        
        # Mock load_version to return mock model
        with patch.object(deployment.versioning, 'load_version', return_value=(mock_model_data, {})):
            success = deployment.deploy_green()
        
        assert success is True
        assert deployment.green_model is not None
    
    def test_warmup_model(self, temp_model_dir, setup_test_versions, mock_model_data):
        """Test model warmup."""
        deployment = BlueGreenDeployment(
            blue_version="v1.0.0",
            green_version="v1.1.0",
            base_dir=temp_model_dir
        )
        
        deployment.green_model = mock_model_data
        
        success = deployment.warmup_model("green")
        
        assert success is True
    
    def test_health_check(self, temp_model_dir, setup_test_versions, mock_model_data):
        """Test health check on environment."""
        deployment = BlueGreenDeployment(
            blue_version="v1.0.0",
            green_version="v1.1.0",
            base_dir=temp_model_dir
        )
        
        deployment.green_model = mock_model_data
        
        health_ok = deployment.health_check("green")
        
        assert health_ok is True
    
    def test_switch_to_green(self, temp_model_dir, setup_test_versions, mock_model_data):
        """Test switching traffic to green environment."""
        deployment = BlueGreenDeployment(
            blue_version="v1.0.0",
            green_version="v1.1.0",
            base_dir=temp_model_dir
        )
        
        deployment.green_model = mock_model_data
        
        # Mock detect_issues to return False (no issues)
        with patch.object(deployment, 'detect_issues', return_value=False):
            success = deployment.switch_to_green()
        
        assert success is True
        assert deployment.active == "green"
    
    def test_rollback(self, temp_model_dir, setup_test_versions, mock_model_data):
        """Test rollback to blue environment."""
        deployment = BlueGreenDeployment(
            blue_version="v1.0.0",
            green_version="v1.1.0",
            base_dir=temp_model_dir
        )
        
        deployment.blue_model = mock_model_data
        deployment.active = "green"
        
        success = deployment.rollback()
        
        assert success is True
        assert deployment.active == "blue"
    
    def test_detect_issues(self, temp_model_dir, setup_test_versions, mock_model_data):
        """Test issue detection."""
        deployment = BlueGreenDeployment(
            blue_version="v1.0.0",
            green_version="v1.1.0",
            base_dir=temp_model_dir
        )
        
        deployment.green_model = mock_model_data
        deployment.active = "green"
        
        issues = deployment.detect_issues()
        
        # Should not detect issues with mock model
        assert issues is False


class TestCanaryDeployment:
    """Test canary deployment functionality."""
    
    def test_canary_deployment_initialization(self, temp_model_dir, setup_test_versions):
        """Test canary deployment initializes correctly."""
        deployment = CanaryDeployment(
            production_version="v1.0.0",
            canary_version="v1.1.0",
            base_dir=temp_model_dir,
            stage_duration_seconds=10  # Short duration for testing
        )
        
        assert deployment.production_version == "v1.0.0"
        assert deployment.canary_version == "v1.1.0"
        assert deployment.canary_percentage == 0
        assert deployment.rollout_stages == [5, 10, 25, 50, 100]
    
    def test_gradual_rollout_success(self, temp_model_dir, setup_test_versions, mock_model_data):
        """Test gradual rollout completes successfully."""
        deployment = CanaryDeployment(
            production_version="v1.0.0",
            canary_version="v1.1.0",
            base_dir=temp_model_dir,
            stage_duration_seconds=1  # Very short for testing
        )
        
        # Mock load_version to return mock model
        with patch.object(deployment.versioning, 'load_version', return_value=(mock_model_data, {})):
            # Mock metrics_acceptable to always return True
            with patch.object(deployment, 'metrics_acceptable', return_value=True):
                success = deployment.gradual_rollout()
        
        assert success is True
        assert deployment.canary_percentage == 100
    
    def test_gradual_rollout_rollback_on_degradation(self, temp_model_dir, setup_test_versions, mock_model_data):
        """Test rollback when metrics degrade."""
        deployment = CanaryDeployment(
            production_version="v1.0.0",
            canary_version="v1.1.0",
            base_dir=temp_model_dir,
            stage_duration_seconds=1
        )
        
        # Mock load_version to return mock model
        with patch.object(deployment.versioning, 'load_version', return_value=(mock_model_data, {})):
            # Mock metrics_acceptable to return False (metrics degraded)
            with patch.object(deployment, 'metrics_acceptable', return_value=False):
                success = deployment.gradual_rollout()
        
        assert success is False
        assert deployment.canary_percentage == 0  # Rolled back
    
    def test_metrics_acceptable(self, temp_model_dir, setup_test_versions, mock_model_data):
        """Test metrics comparison."""
        deployment = CanaryDeployment(
            production_version="v1.0.0",
            canary_version="v1.1.0",
            base_dir=temp_model_dir
        )
        
        deployment.production_model = mock_model_data
        deployment.canary_model = mock_model_data
        
        # Mock _get_metrics to return consistent metrics
        def mock_get_metrics(version_type):
            return {
                'error_rate': 0.0,
                'latency_p95': 50.0,
                'num_samples': 10
            }
        
        with patch.object(deployment, '_get_metrics', side_effect=mock_get_metrics):
            acceptable = deployment.metrics_acceptable()
        
        # With same metrics, should be acceptable
        assert acceptable is True
    
    def test_rollback(self, temp_model_dir, setup_test_versions):
        """Test canary rollback."""
        deployment = CanaryDeployment(
            production_version="v1.0.0",
            canary_version="v1.1.0",
            base_dir=temp_model_dir
        )
        
        deployment.canary_percentage = 50
        
        success = deployment.rollback()
        
        assert success is True
        assert deployment.canary_percentage == 0


class TestAutomaticRollback:
    """Test automatic rollback monitoring."""
    
    def test_get_production_metrics(self, temp_model_dir, setup_test_versions, mock_model_data):
        """Test getting production metrics."""
        versioning = setup_test_versions
        
        # Mock load_version to return mock model
        with patch.object(versioning, 'load_version', return_value=(mock_model_data, {})):
            metrics = get_production_metrics(versioning)
        
        assert 'error_rate' in metrics
        assert 'latency_p95' in metrics
        assert 'production_version' in metrics
    
    def test_rollback_to_previous_version(self, temp_model_dir, setup_test_versions):
        """Test rolling back to previous version."""
        versioning = setup_test_versions
        
        # Promote v1.1.0 to production
        versioning.promote_to_production("v1.1.0")
        
        # Rollback to previous version
        success = rollback_to_previous_version(versioning, reason="Test rollback")
        
        assert success is True
        
        # Check that v1.0.0 is now production
        current_production = versioning.registry.get('production_version')
        assert current_production == "v1.0.0"
    
    def test_monitor_and_rollback_with_high_error_rate(self, temp_model_dir, setup_test_versions, mock_model_data):
        """Test automatic rollback triggers on high error rate."""
        
        # Mock get_production_metrics to return high error rate
        def mock_get_metrics(v):
            return {
                'error_rate': 0.15,  # 15% > 10% threshold
                'latency_p95': 50.0,
                'production_version': 'v1.0.0'
            }
        
        with patch('backend.scripts.deployment.rollback_monitor.get_production_metrics', side_effect=mock_get_metrics):
            with patch('backend.scripts.deployment.rollback_monitor.rollback_to_previous_version', return_value=True) as mock_rollback:
                with patch('backend.scripts.deployment.rollback_monitor.send_alert_notification'):
                    # Run monitor for short duration
                    monitor_and_rollback(
                        check_interval_seconds=1,
                        max_duration_seconds=2,
                        base_dir=temp_model_dir
                    )
                
                # Verify rollback was called
                assert mock_rollback.called


class TestDeploymentValidation:
    """Test deployment validation."""
    
    def test_validate_deployment_success(self, temp_model_dir, setup_test_versions, mock_model_data):
        """Test successful deployment validation."""
        versioning = setup_test_versions
        
        # Mock load_version to return mock model
        with patch.object(versioning, 'load_version', return_value=(mock_model_data, {"model_name": "test"})):
            with patch('backend.scripts.deployment.validate.ModelVersioning', return_value=versioning):
                results = validate_deployment(
                    version="v1.0.0",
                    base_dir=temp_model_dir,
                    run_smoke_tests=True,
                    check_size=True,
                    check_latency=True
                )
        
        assert results['passed'] is True
        assert results['checks']['model_loaded'] is True
        assert 'smoke_tests_passed' in results['checks']
    
    def test_validate_deployment_model_load_failure(self, temp_model_dir, setup_test_versions):
        """Test validation fails when model cannot be loaded."""
        versioning = setup_test_versions
        
        # Mock load_version to raise exception
        with patch.object(versioning, 'load_version', side_effect=Exception("Model not found")):
            with patch('backend.scripts.deployment.validate.ModelVersioning', return_value=versioning):
                results = validate_deployment(
                    version="v99.99.99",
                    base_dir=temp_model_dir
                )
        
        assert results['passed'] is False
        assert results['checks']['model_loaded'] is False
        assert len(results['errors']) > 0
    
    def test_validate_deployment_size_check(self, temp_model_dir, setup_test_versions, mock_model_data):
        """Test model size validation."""
        versioning = setup_test_versions
        
        # Mock metadata with large size
        metadata = {
            "model_name": "test",
            "model_size_mb": 600  # > 500MB threshold
        }
        
        with patch.object(versioning, 'load_version', return_value=(mock_model_data, metadata)):
            with patch('backend.scripts.deployment.validate.ModelVersioning', return_value=versioning):
                results = validate_deployment(
                    version="v1.0.0",
                    base_dir=temp_model_dir,
                    run_smoke_tests=False,
                    check_size=True,
                    check_latency=False
                )
        
        assert results['checks']['size_acceptable'] is False
        assert any('size too large' in error.lower() for error in results['errors'])
    
    def test_validate_deployment_smoke_tests(self, temp_model_dir, setup_test_versions, mock_model_data):
        """Test smoke tests run correctly."""
        versioning = setup_test_versions
        
        with patch.object(versioning, 'load_version', return_value=(mock_model_data, {})):
            with patch('backend.scripts.deployment.validate.ModelVersioning', return_value=versioning):
                results = validate_deployment(
                    version="v1.0.0",
                    base_dir=temp_model_dir,
                    run_smoke_tests=True,
                    check_size=False,
                    check_latency=False
                )
        
        assert 'smoke_tests_passed' in results['checks']
        assert 'smoke_test_details' in results['checks']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
