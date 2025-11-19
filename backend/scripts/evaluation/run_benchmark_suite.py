"""
Benchmark suite runner for ML models.

This script runs comprehensive benchmarks on trained models:
- Existing ML benchmark tests
- Performance comparison with baseline
- Latency and throughput benchmarks
- Memory usage benchmarks

Requirements: 14.1, 14.2, 14.3
"""

import sys
import time
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import numpy as np

# Add backend and workspace root to path
backend_path = Path(__file__).parent.parent.parent
workspace_root = backend_path.parent
sys.path.insert(0, str(workspace_root))
sys.path.insert(0, str(backend_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BenchmarkRunner:
    """Runs comprehensive benchmarks on ML models."""
    
    def __init__(self, model_version: str, baseline_version: str = None):
        """
        Initialize benchmark runner.
        
        Args:
            model_version: Version of model to benchmark
            baseline_version: Version of baseline model for comparison
        """
        self.model_version = model_version
        self.baseline_version = baseline_version
        
        self.results = {
            "benchmark_date": datetime.now().isoformat(),
            "model_version": model_version,
            "baseline_version": baseline_version,
            "tests": {},
            "performance": {},
            "comparison": {}
        }
        
        logger.info(f"Initialized benchmark runner for model: {model_version}")
    
    def run_pytest_benchmarks(self) -> Dict[str, Any]:
        """
        Run existing pytest benchmark tests.
        
        Returns:
            Test results
        """
        logger.info("Running pytest benchmark tests...")
        
        try:
            # Run pytest with benchmark plugin
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "backend/tests/",
                    "-v",
                    "--tb=short",
                    "-k",
                    "classification"
                ],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            test_results = {
                "exit_code": result.returncode,
                "passed": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            # Parse test results
            if "passed" in result.stdout:
                # Extract number of passed tests
                import re
                match = re.search(r'(\d+) passed', result.stdout)
                if match:
                    test_results["num_passed"] = int(match.group(1))
            
            self.results["tests"]["pytest"] = test_results
            
            if test_results["passed"]:
                logger.info("✓ Pytest benchmarks passed")
            else:
                logger.warning("✗ Some pytest benchmarks failed")
            
            return test_results
            
        except subprocess.TimeoutExpired:
            logger.error("Pytest benchmarks timed out")
            return {"passed": False, "error": "Timeout"}
        except Exception as e:
            logger.error(f"Error running pytest benchmarks: {str(e)}")
            return {"passed": False, "error": str(e)}
    
    def benchmark_inference_latency(self, num_samples: int = 1000) -> Dict[str, float]:
        """
        Benchmark inference latency.
        
        Args:
            num_samples: Number of samples to benchmark
            
        Returns:
            Latency statistics
        """
        logger.info(f"Benchmarking inference latency with {num_samples} samples...")
        
        try:
            from app.services.ml_classification_service import MLClassificationService
            from app.database.base import get_sync_db
            
            # Initialize service
            db = get_sync_db()
            service = MLClassificationService(db=db, version=self.model_version)
            
            # Generate test samples
            test_texts = [
                f"This is a test paper about machine learning and artificial intelligence. "
                f"Sample {i} for benchmarking purposes."
                for i in range(num_samples)
            ]
            
            # Warm up
            for _ in range(10):
                service.predict(test_texts[0])
            
            # Benchmark
            latencies = []
            for text in test_texts:
                start = time.time()
                service.predict(text)
                latency = (time.time() - start) * 1000  # Convert to ms
                latencies.append(latency)
            
            # Calculate statistics
            latencies_array = np.array(latencies)
            stats = {
                "mean": float(np.mean(latencies_array)),
                "median": float(np.median(latencies_array)),
                "p50": float(np.percentile(latencies_array, 50)),
                "p95": float(np.percentile(latencies_array, 95)),
                "p99": float(np.percentile(latencies_array, 99)),
                "min": float(np.min(latencies_array)),
                "max": float(np.max(latencies_array)),
                "std": float(np.std(latencies_array))
            }
            
            self.results["performance"]["latency"] = stats
            
            logger.info(f"Latency benchmarks: p50={stats['p50']:.2f}ms, p95={stats['p95']:.2f}ms, p99={stats['p99']:.2f}ms")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error benchmarking latency: {str(e)}")
            return {}
    
    def benchmark_throughput(self, duration_seconds: int = 60) -> Dict[str, float]:
        """
        Benchmark throughput (predictions per second).
        
        Args:
            duration_seconds: Duration to run benchmark
            
        Returns:
            Throughput statistics
        """
        logger.info(f"Benchmarking throughput for {duration_seconds} seconds...")
        
        try:
            from app.services.ml_classification_service import MLClassificationService
            from app.database.base import get_sync_db
            
            # Initialize service
            db = get_sync_db()
            service = MLClassificationService(db=db, version=self.model_version)
            
            test_text = "This is a test paper about machine learning and artificial intelligence."
            
            # Warm up
            for _ in range(10):
                service.predict(test_text)
            
            # Benchmark
            start_time = time.time()
            count = 0
            
            while time.time() - start_time < duration_seconds:
                service.predict(test_text)
                count += 1
            
            elapsed = time.time() - start_time
            throughput = count / elapsed
            
            stats = {
                "predictions_per_second": throughput,
                "total_predictions": count,
                "duration_seconds": elapsed
            }
            
            self.results["performance"]["throughput"] = stats
            
            logger.info(f"Throughput: {throughput:.2f} predictions/second")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error benchmarking throughput: {str(e)}")
            return {}
    
    def benchmark_memory_usage(self) -> Dict[str, float]:
        """
        Benchmark memory usage.
        
        Returns:
            Memory statistics
        """
        logger.info("Benchmarking memory usage...")
        
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            
            # Get initial memory
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Load model
            from app.services.ml_classification_service import MLClassificationService
            from app.database.base import get_sync_db
            
            db = get_sync_db()
            service = MLClassificationService(db=db, version=self.model_version)
            
            # Get memory after loading
            loaded_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Run some predictions
            test_text = "This is a test paper about machine learning."
            for _ in range(100):
                service.predict(test_text)
            
            # Get memory after predictions
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            stats = {
                "initial_mb": initial_memory,
                "after_load_mb": loaded_memory,
                "after_predictions_mb": final_memory,
                "model_load_overhead_mb": loaded_memory - initial_memory,
                "prediction_overhead_mb": final_memory - loaded_memory
            }
            
            self.results["performance"]["memory"] = stats
            
            logger.info(f"Memory usage: model_load={stats['model_load_overhead_mb']:.2f}MB")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error benchmarking memory: {str(e)}")
            return {}
    
    def compare_with_baseline(self) -> Dict[str, Any]:
        """
        Compare performance with baseline model.
        
        Returns:
            Comparison results
        """
        if not self.baseline_version:
            logger.info("No baseline version specified, skipping comparison")
            return {}
        
        logger.info(f"Comparing with baseline: {self.baseline_version}")
        
        try:
            # Load baseline results if available
            baseline_file = Path(f"data/benchmarks/baseline_{self.baseline_version}.json")
            
            if not baseline_file.exists():
                logger.warning(f"Baseline results not found: {baseline_file}")
                return {}
            
            with open(baseline_file, 'r') as f:
                baseline_results = json.load(f)
            
            # Compare latency
            current_latency = self.results["performance"].get("latency", {})
            baseline_latency = baseline_results.get("performance", {}).get("latency", {})
            
            comparison = {
                "latency": {
                    "current_p95": current_latency.get("p95", 0),
                    "baseline_p95": baseline_latency.get("p95", 0),
                    "improvement_percent": (
                        (baseline_latency.get("p95", 0) - current_latency.get("p95", 0)) /
                        baseline_latency.get("p95", 1) * 100
                        if baseline_latency.get("p95", 0) > 0 else 0
                    )
                },
                "throughput": {
                    "current": self.results["performance"].get("throughput", {}).get("predictions_per_second", 0),
                    "baseline": baseline_results.get("performance", {}).get("throughput", {}).get("predictions_per_second", 0)
                }
            }
            
            self.results["comparison"] = comparison
            
            logger.info(f"Latency improvement: {comparison['latency']['improvement_percent']:.2f}%")
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing with baseline: {str(e)}")
            return {}
    
    def run_all_benchmarks(self):
        """Run all benchmarks."""
        logger.info("=" * 80)
        logger.info("Starting Benchmark Suite")
        logger.info("=" * 80)
        
        # Run pytest benchmarks
        self.run_pytest_benchmarks()
        
        # Run performance benchmarks
        self.benchmark_inference_latency(num_samples=1000)
        self.benchmark_throughput(duration_seconds=30)
        self.benchmark_memory_usage()
        
        # Compare with baseline
        if self.baseline_version:
            self.compare_with_baseline()
        
        logger.info("=" * 80)
        logger.info("Benchmark Suite Completed")
        logger.info("=" * 80)
    
    def save_results(self, output_file: str):
        """
        Save benchmark results to file.
        
        Args:
            output_file: Path to output file
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Benchmark results saved to: {output_file}")
    
    def print_summary(self):
        """Print benchmark summary."""
        print("\n" + "=" * 80)
        print("BENCHMARK SUMMARY")
        print("=" * 80)
        
        # Test results
        print("\nTest Results:")
        pytest_results = self.results.get("tests", {}).get("pytest", {})
        if pytest_results.get("passed"):
            print(f"  [PASS] Pytest: PASSED ({pytest_results.get('num_passed', 0)} tests)")
        else:
            print("  [FAIL] Pytest: FAILED")
        
        # Performance results
        print("\nPerformance Metrics:")
        
        latency = self.results.get("performance", {}).get("latency", {})
        if latency:
            print("  Latency:")
            print(f"    - p50: {latency.get('p50', 0):.2f} ms")
            print(f"    - p95: {latency.get('p95', 0):.2f} ms")
            print(f"    - p99: {latency.get('p99', 0):.2f} ms")
        
        throughput = self.results.get("performance", {}).get("throughput", {})
        if throughput:
            print(f"  Throughput: {throughput.get('predictions_per_second', 0):.2f} pred/s")
        
        memory = self.results.get("performance", {}).get("memory", {})
        if memory:
            print("  Memory:")
            print(f"    - Model load: {memory.get('model_load_overhead_mb', 0):.2f} MB")
            print(f"    - After predictions: {memory.get('after_predictions_mb', 0):.2f} MB")
        
        # Comparison
        comparison = self.results.get("comparison", {})
        if comparison:
            print("\nComparison with Baseline:")
            latency_comp = comparison.get("latency", {})
            if latency_comp:
                improvement = latency_comp.get("improvement_percent", 0)
                if improvement > 0:
                    print(f"  [IMPROVED] Latency improved by {improvement:.2f}%")
                else:
                    print(f"  [DEGRADED] Latency degraded by {abs(improvement):.2f}%")
        
        print("\n" + "=" * 80)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run ML model benchmark suite")
    parser.add_argument(
        "--model-version",
        type=str,
        required=True,
        help="Version of model to benchmark"
    )
    parser.add_argument(
        "--baseline-version",
        type=str,
        help="Version of baseline model for comparison"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="data/benchmarks/benchmark_results.json",
        help="Path to output benchmark results"
    )
    
    args = parser.parse_args()
    
    # Run benchmarks
    runner = BenchmarkRunner(
        model_version=args.model_version,
        baseline_version=args.baseline_version
    )
    runner.run_all_benchmarks()
    
    # Print summary
    runner.print_summary()
    
    # Save results
    runner.save_results(args.output_file)


if __name__ == "__main__":
    main()
