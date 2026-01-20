"""
Integration tests for validation scripts.

This module tests that the validation scripts can be imported and initialized correctly.

Requirements: 14.1, 14.2, 14.3
"""

import pytest
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestEndToEndPipeline:
    """Test end-to-end pipeline script."""

    def test_import_pipeline_script(self):
        """Test that pipeline script can be imported."""
        from scripts.evaluation.run_end_to_end_pipeline import EndToEndPipeline

        # Should be able to create instance
        pipeline = EndToEndPipeline(output_dir="data/test_e2e")

        assert pipeline is not None
        assert pipeline.output_dir == Path("data/test_e2e")

    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        from scripts.evaluation.run_end_to_end_pipeline import EndToEndPipeline

        pipeline = EndToEndPipeline(output_dir="data/test_e2e")

        # Check results structure
        assert "pipeline_start" in pipeline.results
        assert "steps" in pipeline.results
        assert "timings" in pipeline.results
        assert "metrics" in pipeline.results

    def test_run_step_success(self):
        """Test run_step method with successful step."""
        from scripts.evaluation.run_end_to_end_pipeline import EndToEndPipeline

        pipeline = EndToEndPipeline(output_dir="data/test_e2e")

        # Mock step function
        def mock_step():
            return "success"

        result = pipeline.run_step("test_step", mock_step)

        assert result == "success"
        assert pipeline.results["steps"]["test_step"] == "SUCCESS"
        assert "test_step" in pipeline.results["timings"]

    def test_run_step_failure(self):
        """Test run_step method with failing step."""
        from scripts.evaluation.run_end_to_end_pipeline import EndToEndPipeline

        pipeline = EndToEndPipeline(output_dir="data/test_e2e")

        # Mock step function that raises error
        def mock_step():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            pipeline.run_step("test_step", mock_step)

        assert "FAILED" in pipeline.results["steps"]["test_step"]


class TestPerformanceValidator:
    """Test performance validator script."""

    def test_import_validator_script(self):
        """Test that validator script can be imported."""
        from scripts.evaluation.validate_performance_metrics import PerformanceValidator

        # Create mock results file
        test_results = {
            "metrics": {
                "test_accuracy": 0.92,
                "test_f1": 0.90,
                "model_size_mb": 268,
                "inference_latency_ms": 85,
            },
            "total_time_hours": 3.5,
        }

        results_file = Path("data/test_validation_results.json")
        results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(results_file, "w") as f:
            json.dump(test_results, f)

        try:
            # Should be able to create instance
            validator = PerformanceValidator(str(results_file))

            assert validator is not None
            assert validator.results == test_results
        finally:
            # Cleanup
            if results_file.exists():
                results_file.unlink()

    def test_validate_test_accuracy_pass(self):
        """Test accuracy validation passes when threshold met."""
        from scripts.evaluation.validate_performance_metrics import PerformanceValidator

        test_results = {"metrics": {"test_accuracy": 0.92}}

        results_file = Path("data/test_validation_results.json")
        results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(results_file, "w") as f:
            json.dump(test_results, f)

        try:
            validator = PerformanceValidator(str(results_file))
            passed, message = validator.validate_test_accuracy()

            assert passed is True
            assert "0.92" in message
        finally:
            if results_file.exists():
                results_file.unlink()

    def test_validate_test_accuracy_fail(self):
        """Test accuracy validation fails when threshold not met."""
        from scripts.evaluation.validate_performance_metrics import PerformanceValidator

        test_results = {"metrics": {"test_accuracy": 0.85}}

        results_file = Path("data/test_validation_results.json")
        results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(results_file, "w") as f:
            json.dump(test_results, f)

        try:
            validator = PerformanceValidator(str(results_file))
            passed, message = validator.validate_test_accuracy()

            assert passed is False
            assert "0.85" in message
        finally:
            if results_file.exists():
                results_file.unlink()


class TestBenchmarkRunner:
    """Test benchmark runner script."""

    def test_import_benchmark_script(self):
        """Test that benchmark script can be imported."""
        from scripts.evaluation.run_benchmark_suite import BenchmarkRunner

        # Should be able to create instance
        runner = BenchmarkRunner(model_version="v1.0.0")

        assert runner is not None
        assert runner.model_version == "v1.0.0"

    def test_benchmark_initialization(self):
        """Test benchmark runner initialization."""
        from scripts.evaluation.run_benchmark_suite import BenchmarkRunner

        runner = BenchmarkRunner(model_version="v1.0.0", baseline_version="v0.9.0")

        # Check results structure
        assert "benchmark_date" in runner.results
        assert "model_version" in runner.results
        assert "baseline_version" in runner.results
        assert runner.results["model_version"] == "v1.0.0"
        assert runner.results["baseline_version"] == "v0.9.0"


class TestReportGenerator:
    """Test report generator script."""

    def test_import_report_script(self):
        """Test that report script can be imported."""
        from scripts.evaluation.generate_performance_report import (
            PerformanceReportGenerator,
        )

        # Create mock result files
        pipeline_results = {"metrics": {}, "steps": {}, "timings": {}}
        validation_results = {"passed": [], "failed": []}
        benchmark_results = {"performance": {}}

        pipeline_file = Path("data/test_pipeline.json")
        validation_file = Path("data/test_validation.json")
        benchmark_file = Path("data/test_benchmark.json")

        pipeline_file.parent.mkdir(parents=True, exist_ok=True)

        with open(pipeline_file, "w") as f:
            json.dump(pipeline_results, f)
        with open(validation_file, "w") as f:
            json.dump(validation_results, f)
        with open(benchmark_file, "w") as f:
            json.dump(benchmark_results, f)

        try:
            # Should be able to create instance
            generator = PerformanceReportGenerator(
                pipeline_results_file=str(pipeline_file),
                validation_results_file=str(validation_file),
                benchmark_results_file=str(benchmark_file),
            )

            assert generator is not None
            assert generator.pipeline_results == pipeline_results
        finally:
            # Cleanup
            for f in [pipeline_file, validation_file, benchmark_file]:
                if f.exists():
                    f.unlink()

    def test_generate_markdown_report(self):
        """Test markdown report generation."""
        from scripts.evaluation.generate_performance_report import (
            PerformanceReportGenerator,
        )

        # Create mock result files with complete data
        pipeline_results = {
            "metrics": {
                "test_accuracy": 0.92,
                "test_f1": 0.90,
                "model_size_mb": 268,
                "collected_papers": 10000,
                "categories": 10,
            },
            "steps": {"step1": "SUCCESS"},
            "timings": {"step1": 100},
            "total_time_hours": 3.5,
        }
        validation_results = {
            "passed": ["Test passed"],
            "failed": [],
            "all_passed": True,
        }
        benchmark_results = {
            "performance": {
                "latency": {"p95": 85},
                "throughput": {"predictions_per_second": 50},
            }
        }

        pipeline_file = Path("data/test_pipeline.json")
        validation_file = Path("data/test_validation.json")
        benchmark_file = Path("data/test_benchmark.json")

        pipeline_file.parent.mkdir(parents=True, exist_ok=True)

        with open(pipeline_file, "w") as f:
            json.dump(pipeline_results, f)
        with open(validation_file, "w") as f:
            json.dump(validation_results, f)
        with open(benchmark_file, "w") as f:
            json.dump(benchmark_results, f)

        try:
            generator = PerformanceReportGenerator(
                pipeline_results_file=str(pipeline_file),
                validation_results_file=str(validation_file),
                benchmark_results_file=str(benchmark_file),
            )

            report = generator.generate_markdown_report()

            # Check report contains expected sections
            assert "# Production ML Training Results" in report
            assert "## Executive Summary" in report
            assert "## Dataset Statistics" in report
            assert "## Training Results" in report
            assert "## Inference Performance" in report
            assert "0.92" in report  # Test accuracy
        finally:
            # Cleanup
            for f in [pipeline_file, validation_file, benchmark_file]:
                if f.exists():
                    f.unlink()


class TestFullValidation:
    """Test full validation runner script."""

    def test_import_full_validation_script(self):
        """Test that full validation script can be imported."""
        from scripts.evaluation.run_full_validation import FullValidationRunner

        # Should be able to create instance
        runner = FullValidationRunner(num_papers=1000)

        assert runner is not None
        assert runner.num_papers == 1000

    def test_full_validation_initialization(self):
        """Test full validation runner initialization."""
        from scripts.evaluation.run_full_validation import FullValidationRunner

        runner = FullValidationRunner(num_papers=1000, baseline_version="v1.0.0")

        assert runner.num_papers == 1000
        assert runner.baseline_version == "v1.0.0"
        assert runner.output_dir == Path("data/e2e_validation")
        assert runner.benchmark_dir == Path("data/benchmarks")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
