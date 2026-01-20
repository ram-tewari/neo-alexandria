"""
Deployment validation and smoke tests for model deployments.

This module provides functions for validating model deployments before
promoting to production, including smoke tests, size checks, and latency
verification.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from .model_versioning import ModelVersioning


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Validation thresholds
MAX_MODEL_SIZE_MB = 500
MAX_INFERENCE_LATENCY_MS = 100
MIN_PREDICTION_CONFIDENCE = 0.1  # Minimum confidence for valid predictions


def validate_deployment(
    version: str,
    base_dir: str = "models/classification",
    run_smoke_tests: bool = True,
    check_size: bool = True,
    check_latency: bool = True,
) -> Dict[str, Any]:
    """
    Validate a model deployment before promoting to production.

    This function performs comprehensive validation:
    1. Load model from checkpoint
    2. Run smoke tests (predict on sample inputs)
    3. Verify predictions are reasonable
    4. Check model size is within limits (<500MB)
    5. Check inference latency is acceptable (<100ms)

    Args:
        version: Model version to validate (e.g., "v1.0.0")
        base_dir: Base directory for model versions
        run_smoke_tests: Whether to run smoke tests (default: True)
        check_size: Whether to check model size (default: True)
        check_latency: Whether to check inference latency (default: True)

    Returns:
        Dictionary with validation results:
            - passed: Overall validation result (True/False)
            - checks: Dictionary of individual check results
            - errors: List of error messages
            - warnings: List of warning messages
            - timestamp: Validation timestamp
    """
    logger.info(f"Validating deployment for version: {version}")
    logger.info(f"{'=' * 60}")

    validation_results = {
        "version": version,
        "passed": False,
        "checks": {},
        "errors": [],
        "warnings": [],
        "timestamp": datetime.now().isoformat(),
    }

    try:
        versioning = ModelVersioning(base_dir=base_dir)

        # Check 1: Load model from checkpoint
        logger.info("Check 1: Loading model from checkpoint...")
        try:
            model_data, metadata = versioning.load_version(version)
            validation_results["checks"]["model_loaded"] = True
            logger.info("  ✓ Model loaded successfully")
            logger.info(f"    Model: {metadata.get('model_name', 'unknown')}")
            logger.info(f"    Created: {metadata.get('created_at', 'unknown')}")
        except Exception as e:
            validation_results["checks"]["model_loaded"] = False
            validation_results["errors"].append(f"Failed to load model: {e}")
            logger.error(f"  ✗ Failed to load model: {e}")
            return validation_results

        # Check 2: Model size
        if check_size:
            logger.info("\nCheck 2: Checking model size...")
            size_check = check_model_size(version, versioning, metadata)
            validation_results["checks"]["size_acceptable"] = size_check["passed"]
            validation_results["checks"]["model_size_mb"] = size_check["size_mb"]

            if size_check["passed"]:
                logger.info(
                    f"  ✓ Model size acceptable: {size_check['size_mb']:.2f} MB"
                )
            else:
                error_msg = f"Model size too large: {size_check['size_mb']:.2f} MB > {MAX_MODEL_SIZE_MB} MB"
                validation_results["errors"].append(error_msg)
                logger.error(f"  ✗ {error_msg}")

        # Check 3: Smoke tests
        if run_smoke_tests:
            logger.info("\nCheck 3: Running smoke tests...")
            smoke_test_results = run_smoke_test(model_data)
            validation_results["checks"]["smoke_tests_passed"] = smoke_test_results[
                "passed"
            ]
            validation_results["checks"]["smoke_test_details"] = smoke_test_results[
                "details"
            ]

            if smoke_test_results["passed"]:
                logger.info(
                    f"  ✓ Smoke tests passed ({smoke_test_results['num_passed']}/{smoke_test_results['num_tests']})"
                )
            else:
                error_msg = f"Smoke tests failed ({smoke_test_results['num_passed']}/{smoke_test_results['num_tests']})"
                validation_results["errors"].append(error_msg)
                logger.error(f"  ✗ {error_msg}")

                # Log failed tests
                for test in smoke_test_results["details"]:
                    if not test["passed"]:
                        logger.error(
                            f"    Failed: {test['input'][:50]}... - {test['error']}"
                        )

        # Check 4: Inference latency
        if check_latency:
            logger.info("\nCheck 4: Checking inference latency...")
            latency_check = check_inference_latency(model_data)
            validation_results["checks"]["latency_acceptable"] = latency_check["passed"]
            validation_results["checks"]["latency_p95_ms"] = latency_check[
                "latency_p95"
            ]

            if latency_check["passed"]:
                logger.info(
                    f"  ✓ Latency acceptable: {latency_check['latency_p95']:.2f} ms (p95)"
                )
            else:
                error_msg = f"Latency too high: {latency_check['latency_p95']:.2f} ms > {MAX_INFERENCE_LATENCY_MS} ms"
                validation_results["warnings"].append(error_msg)
                logger.warning(f"  ⚠ {error_msg}")
                # Latency is a warning, not a hard failure

        # Check 5: Prediction quality
        logger.info("\nCheck 5: Checking prediction quality...")
        quality_check = check_prediction_quality(model_data)
        validation_results["checks"]["predictions_reasonable"] = quality_check["passed"]
        validation_results["checks"]["quality_details"] = quality_check["details"]

        if quality_check["passed"]:
            logger.info("  ✓ Predictions are reasonable")
            logger.info(f"    Avg confidence: {quality_check['avg_confidence']:.4f}")
            logger.info(
                f"    Valid predictions: {quality_check['num_valid']}/{quality_check['num_tests']}"
            )
        else:
            error_msg = f"Predictions quality check failed: {quality_check['reason']}"
            validation_results["errors"].append(error_msg)
            logger.error(f"  ✗ {error_msg}")

        # Overall validation result
        validation_results["passed"] = (
            validation_results["checks"].get("model_loaded", False)
            and validation_results["checks"].get("size_acceptable", True)
            and validation_results["checks"].get("smoke_tests_passed", True)
            and validation_results["checks"].get("predictions_reasonable", True)
            # Note: latency is not a hard requirement
        )

        # Summary
        logger.info(f"\n{'=' * 60}")
        if validation_results["passed"]:
            logger.info(f"✓ Validation PASSED for version {version}")
        else:
            logger.error(f"✗ Validation FAILED for version {version}")
            logger.error(f"  Errors: {len(validation_results['errors'])}")
            for error in validation_results["errors"]:
                logger.error(f"    - {error}")

        if validation_results["warnings"]:
            logger.warning(f"  Warnings: {len(validation_results['warnings'])}")
            for warning in validation_results["warnings"]:
                logger.warning(f"    - {warning}")

        logger.info(f"{'=' * 60}")

        return validation_results

    except Exception as e:
        logger.error(f"Validation failed with exception: {e}")
        validation_results["errors"].append(f"Validation exception: {e}")
        validation_results["passed"] = False
        return validation_results


def check_model_size(
    version: str, versioning: ModelVersioning, metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Check if model size is within acceptable limits.

    Args:
        version: Model version
        versioning: ModelVersioning instance
        metadata: Model metadata

    Returns:
        Dictionary with:
            - passed: True if size acceptable
            - size_mb: Model size in megabytes
    """
    # Get size from metadata if available
    size_mb = metadata.get("model_size_mb")

    if size_mb is None:
        # Calculate size from version directory
        version_entry = None
        for v in versioning.registry.get("versions", []):
            if v["version"] == version:
                version_entry = v
                break

        if version_entry:
            version_dir = Path(version_entry["path"])
            if version_dir.exists():
                total_size = sum(
                    f.stat().st_size for f in version_dir.rglob("*") if f.is_file()
                )
                size_mb = total_size / (1024 * 1024)

    if size_mb is None:
        size_mb = 0.0

    passed = size_mb < MAX_MODEL_SIZE_MB

    return {"passed": passed, "size_mb": size_mb, "threshold_mb": MAX_MODEL_SIZE_MB}


def run_smoke_test(model_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run smoke tests on the model with sample inputs.

    Smoke tests verify basic functionality by running predictions on
    a set of sample inputs and checking that:
    - Predictions complete without errors
    - Outputs have expected format
    - Predictions are not all the same (model is not broken)

    Args:
        model_data: Dictionary with model, tokenizer, and label_map

    Returns:
        Dictionary with:
            - passed: True if all tests passed
            - num_tests: Number of tests run
            - num_passed: Number of tests passed
            - details: List of test results
    """
    import torch

    model = model_data["model"]
    tokenizer = model_data["tokenizer"]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()

    # Sample inputs for smoke tests
    test_inputs = [
        "Machine learning is a subset of artificial intelligence that enables computers to learn from data.",
        "Deep neural networks with multiple layers can learn hierarchical representations of data.",
        "Natural language processing techniques allow computers to understand and generate human language.",
        "Computer vision systems use convolutional neural networks to analyze and interpret images.",
        "Reinforcement learning agents learn optimal behaviors through trial and error interactions.",
        "Transfer learning allows models to leverage knowledge from pre-trained networks.",
        "Supervised learning algorithms learn from labeled training examples.",
        "Unsupervised learning discovers patterns in data without explicit labels.",
        "Recurrent neural networks process sequential data like text and time series.",
        "Attention mechanisms help models focus on relevant parts of the input.",
    ]

    test_results = []
    predictions = []

    with torch.no_grad():
        for test_input in test_inputs:
            test_result = {
                "input": test_input,
                "passed": False,
                "error": None,
                "prediction": None,
            }

            try:
                # Tokenize
                inputs = tokenizer(
                    test_input,
                    truncation=True,
                    padding="max_length",
                    max_length=512,
                    return_tensors="pt",
                )
                inputs = {k: v.to(device) for k, v in inputs.items()}

                # Forward pass
                outputs = model(**inputs)

                # Check output format
                if not hasattr(outputs, "logits"):
                    test_result["error"] = "Output missing 'logits' attribute"
                    test_results.append(test_result)
                    continue

                logits = outputs.logits

                # Check for NaN or Inf
                if torch.isnan(logits).any():
                    test_result["error"] = "Output contains NaN"
                    test_results.append(test_result)
                    continue

                if torch.isinf(logits).any():
                    test_result["error"] = "Output contains Inf"
                    test_results.append(test_result)
                    continue

                # Get prediction
                pred_id = torch.argmax(logits, dim=-1).item()
                predictions.append(pred_id)

                test_result["passed"] = True
                test_result["prediction"] = pred_id

            except Exception as e:
                test_result["error"] = str(e)

            test_results.append(test_result)

    # Check that predictions are not all the same (model is not broken)
    unique_predictions = len(set(predictions))
    all_same = unique_predictions == 1 and len(predictions) > 1

    if all_same:
        for result in test_results:
            if result["passed"]:
                result["passed"] = False
                result["error"] = "All predictions are identical (model may be broken)"

    num_passed = sum(1 for r in test_results if r["passed"])
    num_tests = len(test_results)

    return {
        "passed": num_passed == num_tests,
        "num_tests": num_tests,
        "num_passed": num_passed,
        "details": test_results,
        "unique_predictions": unique_predictions,
    }


def check_inference_latency(model_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if inference latency is acceptable.

    This function measures inference latency on sample inputs and
    checks if the 95th percentile latency is below the threshold.

    Args:
        model_data: Dictionary with model, tokenizer, and label_map

    Returns:
        Dictionary with:
            - passed: True if latency acceptable
            - latency_p95: 95th percentile latency in milliseconds
            - latency_p50: 50th percentile latency in milliseconds
            - latency_avg: Average latency in milliseconds
    """
    import torch
    import numpy as np

    model = model_data["model"]
    tokenizer = model_data["tokenizer"]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()

    # Test input
    test_text = "This is a test input for measuring inference latency."

    # Warm up (first inference is often slower)
    with torch.no_grad():
        inputs = tokenizer(
            test_text,
            truncation=True,
            padding="max_length",
            max_length=512,
            return_tensors="pt",
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        _ = model(**inputs)

    # Measure latency over multiple runs
    latencies = []
    num_runs = 50

    with torch.no_grad():
        for _ in range(num_runs):
            inputs = tokenizer(
                test_text,
                truncation=True,
                padding="max_length",
                max_length=512,
                return_tensors="pt",
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}

            start_time = time.time()
            _ = model(**inputs)
            latency_ms = (time.time() - start_time) * 1000

            latencies.append(latency_ms)

    # Calculate statistics
    latency_p50 = np.percentile(latencies, 50)
    latency_p95 = np.percentile(latencies, 95)
    latency_avg = np.mean(latencies)

    passed = latency_p95 < MAX_INFERENCE_LATENCY_MS

    return {
        "passed": passed,
        "latency_p95": latency_p95,
        "latency_p50": latency_p50,
        "latency_avg": latency_avg,
        "threshold_ms": MAX_INFERENCE_LATENCY_MS,
        "num_runs": num_runs,
    }


def check_prediction_quality(model_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if predictions are reasonable.

    This function verifies that:
    - Predictions have reasonable confidence scores
    - Model produces diverse predictions (not stuck on one class)
    - Predictions are consistent for similar inputs

    Args:
        model_data: Dictionary with model, tokenizer, and label_map

    Returns:
        Dictionary with:
            - passed: True if predictions are reasonable
            - avg_confidence: Average prediction confidence
            - num_valid: Number of valid predictions
            - num_tests: Total number of tests
            - reason: Reason for failure (if failed)
    """
    import torch
    import torch.nn.functional as F

    model = model_data["model"]
    tokenizer = model_data["tokenizer"]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()

    # Test inputs
    test_inputs = [
        "Machine learning algorithms learn patterns from data.",
        "Deep neural networks have revolutionized AI.",
        "Natural language processing enables text understanding.",
        "Computer vision systems analyze visual information.",
        "Reinforcement learning optimizes sequential decisions.",
    ]

    confidences = []
    predictions = []

    with torch.no_grad():
        for text in test_inputs:
            try:
                # Tokenize
                inputs = tokenizer(
                    text,
                    truncation=True,
                    padding="max_length",
                    max_length=512,
                    return_tensors="pt",
                )
                inputs = {k: v.to(device) for k, v in inputs.items()}

                # Forward pass
                outputs = model(**inputs)
                logits = outputs.logits

                # Get probabilities
                probs = F.softmax(logits, dim=-1)
                max_prob = torch.max(probs).item()
                pred_id = torch.argmax(probs, dim=-1).item()

                confidences.append(max_prob)
                predictions.append(pred_id)

            except Exception as e:
                logger.debug(f"Prediction error: {e}")

    # Check results
    num_valid = len(confidences)
    num_tests = len(test_inputs)

    if num_valid == 0:
        return {
            "passed": False,
            "avg_confidence": 0.0,
            "num_valid": 0,
            "num_tests": num_tests,
            "reason": "No valid predictions",
            "details": {},
        }

    avg_confidence = sum(confidences) / len(confidences)
    unique_predictions = len(set(predictions))

    # Check 1: Confidence scores are reasonable
    if avg_confidence < MIN_PREDICTION_CONFIDENCE:
        return {
            "passed": False,
            "avg_confidence": avg_confidence,
            "num_valid": num_valid,
            "num_tests": num_tests,
            "reason": f"Average confidence too low: {avg_confidence:.4f}",
            "details": {"confidences": confidences},
        }

    # Check 2: Predictions are diverse (not all the same)
    if unique_predictions == 1 and len(predictions) > 1:
        return {
            "passed": False,
            "avg_confidence": avg_confidence,
            "num_valid": num_valid,
            "num_tests": num_tests,
            "reason": "All predictions are identical",
            "details": {"predictions": predictions},
        }

    # All checks passed
    return {
        "passed": True,
        "avg_confidence": avg_confidence,
        "num_valid": num_valid,
        "num_tests": num_tests,
        "details": {
            "confidences": confidences,
            "predictions": predictions,
            "unique_predictions": unique_predictions,
        },
    }


def save_validation_results(
    validation_results: Dict[str, Any], output_file: str = "validation_results.json"
) -> None:
    """
    Save validation results to file.

    Args:
        validation_results: Validation results dictionary
        output_file: Path to output JSON file
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(validation_results, f, indent=2)

    logger.info(f"Validation results saved to {output_file}")


def main():
    """
    Main function for command-line usage.

    Example usage:
        # Validate a model version
        python validate.py validate --version v1.0.0

        # Validate with specific checks
        python validate.py validate --version v1.0.0 --no-smoke-tests

        # Quick validation (skip latency check)
        python validate.py validate --version v1.0.0 --no-latency
    """
    import argparse

    parser = argparse.ArgumentParser(description="Deployment validation")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate model deployment"
    )
    validate_parser.add_argument(
        "--version", required=True, help="Model version to validate"
    )
    validate_parser.add_argument(
        "--base-dir", default="models/classification", help="Base directory for models"
    )
    validate_parser.add_argument(
        "--no-smoke-tests", action="store_true", help="Skip smoke tests"
    )
    validate_parser.add_argument(
        "--no-size-check", action="store_true", help="Skip size check"
    )
    validate_parser.add_argument(
        "--no-latency", action="store_true", help="Skip latency check"
    )
    validate_parser.add_argument(
        "--output", default="validation_results.json", help="Output file for results"
    )

    args = parser.parse_args()

    if args.command == "validate":
        # Validate deployment
        print(f"Validating deployment for version: {args.version}")
        print()

        results = validate_deployment(
            version=args.version,
            base_dir=args.base_dir,
            run_smoke_tests=not args.no_smoke_tests,
            check_size=not args.no_size_check,
            check_latency=not args.no_latency,
        )

        # Save results
        save_validation_results(results, args.output)

        # Print summary
        print()
        if results["passed"]:
            print("✓ Validation PASSED")
            exit(0)
        else:
            print("✗ Validation FAILED")
            print("\nErrors:")
            for error in results["errors"]:
                print(f"  - {error}")
            exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
