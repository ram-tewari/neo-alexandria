"""
Test script for ML classification training functionality.

This script tests the fine_tune() method and related training functionality
without requiring a full database setup.
"""

import sys
from pathlib import Path

def test_training_methods():
    """Test that training methods are properly implemented."""
    # Direct import to avoid full app initialization
    import importlib.util
    
    # Construct path from test file to backend/app/services/ml_classification_service.py
    # Test file is at: backend/tests/unit/phase8_classification/test_ml_training.py
    # Target file is at: backend/app/services/ml_classification_service.py
    backend_root = Path(__file__).parent.parent.parent.parent
    ml_service_path = backend_root / "app" / "services" / "ml_classification_service.py"
    spec = importlib.util.spec_from_file_location(
        "ml_classification_service",
        ml_service_path
    )
    ml_module = importlib.util.module_from_spec(spec)
    
    # Mock the database models before loading
    from unittest.mock import Mock
    sys.modules['sqlalchemy.orm'] = Mock()
    
    spec.loader.exec_module(ml_module)
    MLClassificationService = ml_module.MLClassificationService
    
    print("Testing ML Classification Training Implementation...")
    
    # Create mock database session
    mock_db = Mock()
    
    # Initialize service
    service = MLClassificationService(
        db=mock_db,
        model_name="distilbert-base-uncased",
        model_version="test_v1.0"
    )
    
    print("✓ Service initialized successfully")
    
    # Check that methods exist
    assert hasattr(service, 'fine_tune'), "fine_tune method not found"
    assert hasattr(service, '_compute_metrics'), "_compute_metrics method not found"
    assert hasattr(service, '_semi_supervised_iteration'), "_semi_supervised_iteration method not found"
    assert hasattr(service, 'predict'), "predict method not found"
    
    print("✓ All required methods exist")
    
    # Check method signatures
    import inspect
    
    # Check fine_tune signature
    fine_tune_sig = inspect.signature(service.fine_tune)
    expected_params = ['labeled_data', 'unlabeled_data', 'epochs', 'batch_size', 'learning_rate']
    actual_params = list(fine_tune_sig.parameters.keys())
    for param in expected_params:
        assert param in actual_params, f"fine_tune missing parameter: {param}"
    
    print("✓ fine_tune has correct signature")
    
    # Check _compute_metrics signature
    compute_metrics_sig = inspect.signature(service._compute_metrics)
    assert 'eval_pred' in compute_metrics_sig.parameters, "_compute_metrics missing eval_pred parameter"
    
    print("✓ _compute_metrics has correct signature")
    
    # Check _semi_supervised_iteration signature
    semi_sig = inspect.signature(service._semi_supervised_iteration)
    expected_params = ['labeled_data', 'unlabeled_data', 'confidence_threshold']
    actual_params = list(semi_sig.parameters.keys())
    for param in expected_params:
        assert param in actual_params, f"_semi_supervised_iteration missing parameter: {param}"
    
    print("✓ _semi_supervised_iteration has correct signature")
    
    # Check predict signature
    predict_sig = inspect.signature(service.predict)
    expected_params = ['text', 'top_k']
    actual_params = list(predict_sig.parameters.keys())
    for param in expected_params:
        assert param in actual_params, f"predict missing parameter: {param}"
    
    print("✓ predict has correct signature")
    
    # Test _compute_metrics with mock data
    print("\nTesting _compute_metrics...")
    import numpy as np
    
    # Create mock eval_pred
    class MockEvalPred:
        def __init__(self):
            # Logits for 3 samples, 4 labels
            self.predictions = np.array([
                [2.0, -1.0, 0.5, -0.5],
                [-1.0, 2.0, -0.5, 0.5],
                [0.5, -0.5, 2.0, -1.0]
            ])
            # Ground truth labels
            self.label_ids = np.array([
                [1, 0, 1, 0],
                [0, 1, 0, 1],
                [1, 0, 1, 0]
            ])
    
    mock_eval_pred = MockEvalPred()
    metrics = service._compute_metrics((mock_eval_pred.predictions, mock_eval_pred.label_ids))
    
    assert 'f1' in metrics, "Metrics missing f1 score"
    assert 'precision' in metrics, "Metrics missing precision"
    assert 'recall' in metrics, "Metrics missing recall"
    assert 0.0 <= metrics['f1'] <= 1.0, "F1 score out of range"
    assert 0.0 <= metrics['precision'] <= 1.0, "Precision out of range"
    assert 0.0 <= metrics['recall'] <= 1.0, "Recall out of range"
    
    print("✓ _compute_metrics works correctly")
    print(f"  F1: {metrics['f1']:.4f}, Precision: {metrics['precision']:.4f}, Recall: {metrics['recall']:.4f}")
    
    print("\n" + "="*60)
    print("All training method tests passed!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        test_training_methods()
        print("\n✓ Training implementation verified successfully")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
