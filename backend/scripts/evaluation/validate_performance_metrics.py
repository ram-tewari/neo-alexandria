"""
Performance metrics validation script.

This script validates that the trained model meets all performance requirements:
- Test accuracy ≥90%
- F1 score ≥88%
- Model size <500MB
- Training time <4 hours on V100 GPU
- Inference latency <100ms (p95)

Requirements: 4.11, 4.12, 5.4, 5.5, 15.3, 15.4
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceValidator:
    """Validates model performance against requirements."""
    
    # Performance thresholds from requirements
    THRESHOLDS = {
        "test_accuracy": 0.90,      # ≥90%
        "test_f1": 0.88,            # ≥88%
        "model_size_mb": 500,       # <500MB
        "training_time_hours": 4,   # <4 hours
        "inference_latency_p95": 100  # <100ms
    }
    
    def __init__(self, results_file: str):
        """
        Initialize validator with pipeline results.
        
        Args:
            results_file: Path to pipeline results JSON
        """
        self.results_file = Path(results_file)
        
        if not self.results_file.exists():
            raise FileNotFoundError(f"Results file not found: {results_file}")
        
        with open(self.results_file, 'r') as f:
            self.results = json.load(f)
        
        self.validation_results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
        
        logger.info(f"Loaded results from: {results_file}")
    
    def validate_test_accuracy(self) -> Tuple[bool, str]:
        """
        Validate test accuracy meets threshold.
        
        Returns:
            Tuple of (passed, message)
        """
        actual = self.results.get("metrics", {}).get("test_accuracy", 0)
        threshold = self.THRESHOLDS["test_accuracy"]
        
        passed = actual >= threshold
        message = f"Test Accuracy: {actual:.4f} (threshold: ≥{threshold:.2f})"
        
        return passed, message
    
    def validate_test_f1(self) -> Tuple[bool, str]:
        """
        Validate F1 score meets threshold.
        
        Returns:
            Tuple of (passed, message)
        """
        actual = self.results.get("metrics", {}).get("test_f1", 0)
        threshold = self.THRESHOLDS["test_f1"]
        
        passed = actual >= threshold
        message = f"Test F1 Score: {actual:.4f} (threshold: ≥{threshold:.2f})"
        
        return passed, message
    
    def validate_model_size(self) -> Tuple[bool, str]:
        """
        Validate model size is within limit.
        
        Returns:
            Tuple of (passed, message)
        """
        actual = self.results.get("metrics", {}).get("model_size_mb", 0)
        threshold = self.THRESHOLDS["model_size_mb"]
        
        passed = actual < threshold
        message = f"Model Size: {actual:.2f} MB (threshold: <{threshold} MB)"
        
        return passed, message
    
    def validate_training_time(self) -> Tuple[bool, str]:
        """
        Validate training time is within limit.
        
        Returns:
            Tuple of (passed, message)
        """
        actual = self.results.get("total_time_hours", 0)
        threshold = self.THRESHOLDS["training_time_hours"]
        
        passed = actual < threshold
        message = f"Training Time: {actual:.2f} hours (threshold: <{threshold} hours)"
        
        return passed, message
    
    def validate_inference_latency(self) -> Tuple[bool, str]:
        """
        Validate inference latency is within limit.
        
        Returns:
            Tuple of (passed, message)
        """
        actual = self.results.get("metrics", {}).get("inference_latency_ms", 0)
        threshold = self.THRESHOLDS["inference_latency_p95"]
        
        passed = actual < threshold
        message = f"Inference Latency (p95): {actual:.2f} ms (threshold: <{threshold} ms)"
        
        return passed, message
    
    def run_all_validations(self) -> Dict[str, Any]:
        """
        Run all performance validations.
        
        Returns:
            Dictionary with validation results
        """
        logger.info("Running performance validations...")
        
        validations = [
            ("Test Accuracy", self.validate_test_accuracy),
            ("Test F1 Score", self.validate_test_f1),
            ("Model Size", self.validate_model_size),
            ("Training Time", self.validate_training_time),
            ("Inference Latency", self.validate_inference_latency)
        ]
        
        all_passed = True
        
        for name, validator in validations:
            passed, message = validator()
            
            if passed:
                self.validation_results["passed"].append(message)
                logger.info(f"✓ {message}")
            else:
                self.validation_results["failed"].append(message)
                logger.error(f"✗ {message}")
                all_passed = False
        
        self.validation_results["all_passed"] = all_passed
        
        return self.validation_results
    
    def save_validation_report(self, output_file: str):
        """
        Save validation report to file.
        
        Args:
            output_file: Path to output file
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        logger.info(f"Validation report saved to: {output_file}")
    
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 80)
        print("PERFORMANCE VALIDATION SUMMARY")
        print("=" * 80)
        
        print("\n✓ PASSED:")
        for item in self.validation_results["passed"]:
            print(f"  {item}")
        
        if self.validation_results["failed"]:
            print("\n✗ FAILED:")
            for item in self.validation_results["failed"]:
                print(f"  {item}")
        
        if self.validation_results["warnings"]:
            print("\n⚠ WARNINGS:")
            for item in self.validation_results["warnings"]:
                print(f"  {item}")
        
        print("\n" + "=" * 80)
        
        if self.validation_results["all_passed"]:
            print("✓ ALL VALIDATIONS PASSED")
        else:
            print("✗ SOME VALIDATIONS FAILED")
        
        print("=" * 80 + "\n")
    
    def get_actual_metrics(self) -> Dict[str, Any]:
        """
        Get actual metrics achieved.
        
        Returns:
            Dictionary of actual metrics
        """
        return {
            "test_accuracy": self.results.get("metrics", {}).get("test_accuracy", 0),
            "test_f1": self.results.get("metrics", {}).get("test_f1", 0),
            "model_size_mb": self.results.get("metrics", {}).get("model_size_mb", 0),
            "training_time_hours": self.results.get("total_time_hours", 0),
            "inference_latency_ms": self.results.get("metrics", {}).get("inference_latency_ms", 0),
            "train_accuracy": self.results.get("metrics", {}).get("train_accuracy", 0),
            "val_accuracy": self.results.get("metrics", {}).get("val_accuracy", 0),
            "load_time_s": self.results.get("metrics", {}).get("load_time_s", 0)
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate model performance metrics")
    parser.add_argument(
        "--results-file",
        type=str,
        default="data/e2e_validation/pipeline_results.json",
        help="Path to pipeline results JSON"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="data/e2e_validation/validation_report.json",
        help="Path to output validation report"
    )
    
    args = parser.parse_args()
    
    # Run validation
    validator = PerformanceValidator(args.results_file)
    results = validator.run_all_validations()
    
    # Print summary
    validator.print_summary()
    
    # Print actual metrics
    print("\nACTUAL METRICS ACHIEVED:")
    print("=" * 80)
    metrics = validator.get_actual_metrics()
    for key, value in metrics.items():
        if "accuracy" in key or "f1" in key:
            print(f"  {key}: {value:.4f}")
        elif "time" in key:
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value:.2f}")
    print("=" * 80 + "\n")
    
    # Save report
    validator.save_validation_report(args.output_file)
    
    # Exit with appropriate code
    if not results["all_passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
