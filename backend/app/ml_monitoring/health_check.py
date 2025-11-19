"""
Health check module for ML model monitoring.

This module provides functions to check the health and readiness of ML models
for production use.
"""

import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_model_health(
    model: Optional[Any] = None,
    checkpoint_path: Optional[str] = None,
    test_input: Optional[str] = None,
    latency_threshold_ms: float = 200.0
) -> Dict[str, Any]:
    """
    Check the health of an ML model.
    
    This function performs multiple checks:
    1. Model is loaded (not None)
    2. Checkpoint file exists and is valid
    3. Inference works with test input
    4. Latency is acceptable
    
    Args:
        model: The loaded model instance (optional)
        checkpoint_path: Path to model checkpoint directory (optional)
        test_input: Test input text for inference check (optional)
        latency_threshold_ms: Maximum acceptable latency in milliseconds (default: 200)
    
    Returns:
        Dictionary containing:
            - model_loaded: Boolean indicating if model is loaded
            - checkpoint_valid: Boolean indicating if checkpoint is valid
            - inference_working: Boolean indicating if inference works
            - latency_acceptable: Boolean indicating if latency is acceptable
            - latency_ms: Actual inference latency in milliseconds
            - overall_healthy: Boolean indicating overall health status
            - details: Additional details about checks
    """
    results = {
        "model_loaded": False,
        "checkpoint_valid": False,
        "inference_working": False,
        "latency_acceptable": False,
        "latency_ms": None,
        "overall_healthy": False,
        "details": {}
    }
    
    # Check 1: Model is loaded
    if model is not None:
        results["model_loaded"] = True
        results["details"]["model_loaded"] = "Model instance is not None"
        logger.info("✓ Model is loaded")
    else:
        results["details"]["model_loaded"] = "Model instance is None"
        logger.warning("✗ Model is not loaded")
    
    # Check 2: Checkpoint file exists and is valid
    if checkpoint_path:
        checkpoint_dir = Path(checkpoint_path)
        
        if checkpoint_dir.exists():
            # Check for required files
            required_files = ["pytorch_model.bin", "config.json"]
            missing_files = []
            
            for filename in required_files:
                file_path = checkpoint_dir / filename
                if not file_path.exists():
                    missing_files.append(filename)
            
            if not missing_files:
                results["checkpoint_valid"] = True
                results["details"]["checkpoint_valid"] = f"All required files present in {checkpoint_path}"
                logger.info(f"✓ Checkpoint is valid: {checkpoint_path}")
            else:
                results["details"]["checkpoint_valid"] = f"Missing files: {missing_files}"
                logger.warning(f"✗ Checkpoint missing files: {missing_files}")
        else:
            results["details"]["checkpoint_valid"] = f"Checkpoint directory not found: {checkpoint_path}"
            logger.warning(f"✗ Checkpoint directory not found: {checkpoint_path}")
    else:
        results["details"]["checkpoint_valid"] = "No checkpoint path provided"
        logger.info("⊘ Checkpoint validation skipped (no path provided)")
    
    # Check 3: Inference works with test input
    if model is not None and test_input is not None:
        try:
            # Use default test input if none provided
            if test_input is None:
                test_input = "This is a test input for health check."
            
            # Measure inference latency
            start_time = time.time()
            
            # Try to run inference
            # Note: This is a generic check - actual implementation depends on model type
            if hasattr(model, 'predict'):
                _ = model.predict(test_input)
            elif hasattr(model, '__call__'):
                _ = model(test_input)
            else:
                raise AttributeError("Model does not have predict() or __call__() method")
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            results["inference_working"] = True
            results["latency_ms"] = latency_ms
            results["details"]["inference_working"] = f"Inference successful (latency: {latency_ms:.2f}ms)"
            logger.info(f"✓ Inference is working (latency: {latency_ms:.2f}ms)")
            
            # Check 4: Latency is acceptable
            if latency_ms < latency_threshold_ms:
                results["latency_acceptable"] = True
                results["details"]["latency_acceptable"] = f"Latency {latency_ms:.2f}ms < threshold {latency_threshold_ms}ms"
                logger.info(f"✓ Latency is acceptable: {latency_ms:.2f}ms < {latency_threshold_ms}ms")
            else:
                results["details"]["latency_acceptable"] = f"Latency {latency_ms:.2f}ms >= threshold {latency_threshold_ms}ms"
                logger.warning(f"✗ Latency is too high: {latency_ms:.2f}ms >= {latency_threshold_ms}ms")
                
        except Exception as e:
            results["details"]["inference_working"] = f"Inference failed: {str(e)}"
            logger.error(f"✗ Inference failed: {e}")
    else:
        if model is None:
            results["details"]["inference_working"] = "Cannot test inference: model is None"
            logger.info("⊘ Inference check skipped (model is None)")
        else:
            results["details"]["inference_working"] = "Cannot test inference: no test input provided"
            logger.info("⊘ Inference check skipped (no test input provided)")
    
    # Determine overall health
    # Model is healthy if:
    # 1. Model is loaded
    # 2. Checkpoint is valid (if path provided)
    # 3. Inference works (if test input provided)
    # 4. Latency is acceptable (if inference was tested)
    
    checks_to_pass = []
    
    # Always require model to be loaded
    checks_to_pass.append(results["model_loaded"])
    
    # Require checkpoint valid if path was provided
    if checkpoint_path:
        checks_to_pass.append(results["checkpoint_valid"])
    
    # Require inference working if test input was provided
    if test_input is not None and model is not None:
        checks_to_pass.append(results["inference_working"])
        checks_to_pass.append(results["latency_acceptable"])
    
    results["overall_healthy"] = all(checks_to_pass)
    
    if results["overall_healthy"]:
        logger.info("✓ Overall health: HEALTHY")
    else:
        logger.warning("✗ Overall health: UNHEALTHY")
    
    return results


def check_classification_model_health(
    service: Any,
    test_input: str = "This is a test paper about machine learning and neural networks.",
    latency_threshold_ms: float = 200.0
) -> Dict[str, Any]:
    """
    Check health of a classification model service.
    
    This is a specialized health check for MLClassificationService.
    
    Args:
        service: MLClassificationService instance
        test_input: Test input text for classification
        latency_threshold_ms: Maximum acceptable latency in milliseconds
    
    Returns:
        Dictionary with health check results
    """
    results = {
        "model_loaded": False,
        "checkpoint_valid": False,
        "inference_working": False,
        "latency_acceptable": False,
        "latency_ms": None,
        "overall_healthy": False,
        "details": {}
    }
    
    # Check if service has model loaded
    if hasattr(service, 'model') and service.model is not None:
        results["model_loaded"] = True
        results["details"]["model_loaded"] = "Classification model is loaded"
        logger.info("✓ Classification model is loaded")
    else:
        results["details"]["model_loaded"] = "Classification model is not loaded"
        logger.warning("✗ Classification model is not loaded")
        return results
    
    # Check checkpoint validity
    if hasattr(service, 'checkpoint_dir'):
        checkpoint_path = Path(service.checkpoint_dir)
        if checkpoint_path.exists():
            required_files = ["pytorch_model.bin", "config.json", "label_map.json"]
            missing_files = [f for f in required_files if not (checkpoint_path / f).exists()]
            
            if not missing_files:
                results["checkpoint_valid"] = True
                results["details"]["checkpoint_valid"] = "All required checkpoint files present"
                logger.info("✓ Checkpoint is valid")
            else:
                results["details"]["checkpoint_valid"] = f"Missing files: {missing_files}"
                logger.warning(f"✗ Missing checkpoint files: {missing_files}")
        else:
            results["details"]["checkpoint_valid"] = "Checkpoint directory not found"
            logger.warning("✗ Checkpoint directory not found")
    
    # Test inference
    try:
        start_time = time.time()
        prediction = service.classify_text(test_input)
        end_time = time.time()
        
        latency_ms = (end_time - start_time) * 1000
        results["latency_ms"] = latency_ms
        
        # Check if prediction has expected structure
        if isinstance(prediction, dict) and "label" in prediction:
            results["inference_working"] = True
            results["details"]["inference_working"] = f"Classification successful: {prediction.get('label')}"
            logger.info(f"✓ Inference working (predicted: {prediction.get('label')})")
        else:
            results["details"]["inference_working"] = "Prediction has unexpected format"
            logger.warning("✗ Prediction has unexpected format")
        
        # Check latency
        if latency_ms < latency_threshold_ms:
            results["latency_acceptable"] = True
            results["details"]["latency_acceptable"] = f"Latency {latency_ms:.2f}ms < {latency_threshold_ms}ms"
            logger.info(f"✓ Latency acceptable: {latency_ms:.2f}ms")
        else:
            results["details"]["latency_acceptable"] = f"Latency {latency_ms:.2f}ms >= {latency_threshold_ms}ms"
            logger.warning(f"✗ Latency too high: {latency_ms:.2f}ms")
            
    except Exception as e:
        results["details"]["inference_working"] = f"Inference failed: {str(e)}"
        logger.error(f"✗ Inference failed: {e}")
    
    # Overall health
    results["overall_healthy"] = all([
        results["model_loaded"],
        results["checkpoint_valid"],
        results["inference_working"],
        results["latency_acceptable"]
    ])
    
    return results
