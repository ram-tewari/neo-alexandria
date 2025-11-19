"""
Master validation script that orchestrates all validation tasks.

This script runs the complete validation workflow:
1. End-to-end pipeline (14.1)
2. Performance metrics validation (14.2)
3. Benchmark suite (14.3)
4. Performance report generation (14.4)

Requirements: 4.11, 4.12, 5.4, 5.5, 14.1, 14.2, 14.3, 15.3, 15.4, 15.9, 15.10
"""

import sys
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FullValidationRunner:
    """Orchestrates the complete validation workflow."""
    
    def __init__(self, num_papers: int = 10000, baseline_version: str = None):
        """
        Initialize validation runner.
        
        Args:
            num_papers: Number of papers to collect for training
            baseline_version: Baseline model version for comparison
        """
        self.num_papers = num_papers
        self.baseline_version = baseline_version
        
        self.output_dir = Path("data/e2e_validation")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.benchmark_dir = Path("data/benchmarks")
        self.benchmark_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Initialized full validation runner")
        logger.info(f"  - Papers to collect: {num_papers}")
        logger.info(f"  - Baseline version: {baseline_version or 'None'}")
    
    def run_script(self, script_name: str, args: list = None) -> bool:
        """
        Run a Python script.
        
        Args:
            script_name: Name of the script to run
            args: Additional arguments for the script
            
        Returns:
            True if successful, False otherwise
        """
        script_path = Path(__file__).parent / script_name
        
        if not script_path.exists():
            logger.error(f"Script not found: {script_path}")
            return False
        
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        
        logger.info(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=14400  # 4 hours max
            )
            
            # Print output
            if result.stdout:
                print(result.stdout)
            
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            
            if result.returncode == 0:
                logger.info(f"✓ {script_name} completed successfully")
                return True
            else:
                logger.error(f"✗ {script_name} failed with exit code {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"✗ {script_name} timed out")
            return False
        except Exception as e:
            logger.error(f"✗ {script_name} failed: {str(e)}")
            return False
    
    def step1_run_pipeline(self) -> bool:
        """
        Step 1: Run end-to-end pipeline.
        
        Returns:
            True if successful
        """
        logger.info("=" * 80)
        logger.info("STEP 1: Running End-to-End Pipeline")
        logger.info("=" * 80)
        
        args = [
            "--num-papers", str(self.num_papers),
            "--output-dir", str(self.output_dir)
        ]
        
        return self.run_script("run_end_to_end_pipeline.py", args)
    
    def step2_validate_metrics(self) -> bool:
        """
        Step 2: Validate performance metrics.
        
        Returns:
            True if successful
        """
        logger.info("=" * 80)
        logger.info("STEP 2: Validating Performance Metrics")
        logger.info("=" * 80)
        
        args = [
            "--results-file", str(self.output_dir / "pipeline_results.json"),
            "--output-file", str(self.output_dir / "validation_report.json")
        ]
        
        return self.run_script("validate_performance_metrics.py", args)
    
    def step3_run_benchmarks(self) -> bool:
        """
        Step 3: Run benchmark suite.
        
        Returns:
            True if successful
        """
        logger.info("=" * 80)
        logger.info("STEP 3: Running Benchmark Suite")
        logger.info("=" * 80)
        
        # Get model version from pipeline results
        import json
        results_file = self.output_dir / "pipeline_results.json"
        
        if not results_file.exists():
            logger.error("Pipeline results not found")
            return False
        
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        model_version = results.get("metrics", {}).get("model_version")
        
        if not model_version:
            logger.error("Model version not found in pipeline results")
            return False
        
        args = [
            "--model-version", model_version,
            "--output-file", str(self.benchmark_dir / "benchmark_results.json")
        ]
        
        if self.baseline_version:
            args.extend(["--baseline-version", self.baseline_version])
        
        return self.run_script("run_benchmark_suite.py", args)
    
    def step4_generate_report(self) -> bool:
        """
        Step 4: Generate performance report.
        
        Returns:
            True if successful
        """
        logger.info("=" * 80)
        logger.info("STEP 4: Generating Performance Report")
        logger.info("=" * 80)
        
        args = [
            "--pipeline-results", str(self.output_dir / "pipeline_results.json"),
            "--validation-results", str(self.output_dir / "validation_report.json"),
            "--benchmark-results", str(self.benchmark_dir / "benchmark_results.json"),
            "--output-file", "backend/docs/PRODUCTION_ML_TRAINING_RESULTS.md"
        ]
        
        return self.run_script("generate_performance_report.py", args)
    
    def run_full_validation(self):
        """Run the complete validation workflow."""
        start_time = datetime.now()
        
        logger.info("\n" + "=" * 80)
        logger.info("STARTING FULL VALIDATION WORKFLOW")
        logger.info("=" * 80 + "\n")
        
        results = {
            "step1_pipeline": False,
            "step2_validation": False,
            "step3_benchmarks": False,
            "step4_report": False
        }
        
        # Step 1: Run pipeline
        results["step1_pipeline"] = self.step1_run_pipeline()
        
        if not results["step1_pipeline"]:
            logger.error("Pipeline failed, stopping validation")
            self.print_final_summary(results, start_time)
            return False
        
        # Step 2: Validate metrics
        results["step2_validation"] = self.step2_validate_metrics()
        
        # Step 3: Run benchmarks (continue even if validation failed)
        results["step3_benchmarks"] = self.step3_run_benchmarks()
        
        # Step 4: Generate report
        results["step4_report"] = self.step4_generate_report()
        
        # Print final summary
        self.print_final_summary(results, start_time)
        
        # Return overall success
        return all(results.values())
    
    def print_final_summary(self, results: dict, start_time: datetime):
        """Print final validation summary."""
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("VALIDATION WORKFLOW SUMMARY")
        print("=" * 80)
        
        print("\nStep Results:")
        for step, success in results.items():
            status = "✓ PASSED" if success else "✗ FAILED"
            print(f"  {step}: {status}")
        
        print(f"\nTotal Time: {elapsed / 3600:.2f} hours")
        
        if all(results.values()):
            print("\n✓ ALL VALIDATION STEPS COMPLETED SUCCESSFULLY")
        else:
            print("\n✗ SOME VALIDATION STEPS FAILED")
        
        print("=" * 80 + "\n")
        
        # Print next steps
        if all(results.values()):
            print("Next Steps:")
            print("  1. Review the performance report: backend/docs/PRODUCTION_ML_TRAINING_RESULTS.md")
            print("  2. Check validation results: data/e2e_validation/validation_report.json")
            print("  3. Review benchmark results: data/benchmarks/benchmark_results.json")
            print("  4. If all requirements are met, proceed with production deployment")
        else:
            print("Action Required:")
            print("  1. Review failed steps and error logs")
            print("  2. Address any issues identified")
            print("  3. Re-run validation workflow")
        
        print("")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run complete validation workflow for production ML training"
    )
    parser.add_argument(
        "--num-papers",
        type=int,
        default=10000,
        help="Number of papers to collect for training (default: 10000)"
    )
    parser.add_argument(
        "--baseline-version",
        type=str,
        help="Baseline model version for comparison"
    )
    parser.add_argument(
        "--quick-test",
        action="store_true",
        help="Run quick test with only 1000 papers"
    )
    
    args = parser.parse_args()
    
    # Adjust for quick test
    num_papers = 1000 if args.quick_test else args.num_papers
    
    if args.quick_test:
        logger.info("Running in QUICK TEST mode with 1000 papers")
    
    # Run validation
    runner = FullValidationRunner(
        num_papers=num_papers,
        baseline_version=args.baseline_version
    )
    
    success = runner.run_full_validation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
