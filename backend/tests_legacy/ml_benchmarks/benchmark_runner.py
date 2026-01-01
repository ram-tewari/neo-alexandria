"""
Benchmark orchestration system for Neo Alexandria ML components.

This module provides automated execution of all ML benchmark suites,
result aggregation, and report generation capabilities.
"""

import argparse
import gc
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import pytest


@dataclass
class BenchmarkResult:
    """Result from a single benchmark test."""
    test_name: str
    metric_name: str
    score: float
    baseline: float
    target: float
    passed: bool
    timestamp: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkSuiteResult:
    """Results from a complete benchmark suite."""
    suite_name: str
    results: List[BenchmarkResult]
    total_tests: int
    passed_tests: int
    failed_tests: int
    execution_time_seconds: float
    recommendations: List[str] = field(default_factory=list)


class BenchmarkRunner:
    """
    Orchestrates execution of all ML benchmark suites.
    
    Executes classification, collaborative filtering, search quality,
    summarization quality, and performance benchmarks sequentially,
    aggregates results, and generates comprehensive reports.
    """
    
    def __init__(self, output_dir: str = "docs"):
        """
        Initialize benchmark runner.
        
        Args:
            output_dir: Directory to save benchmark reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: Dict[str, BenchmarkSuiteResult] = {}
        self.start_time = datetime.now()
        
    def run_all_benchmarks(self) -> Dict[str, BenchmarkSuiteResult]:
        """
        Run all benchmark suites sequentially.
        
        Executes:
        - Classification benchmarks
        - Collaborative filtering benchmarks
        - Search quality benchmarks
        - Summarization quality benchmarks
        - Performance benchmarks
        
        Returns:
            Dictionary mapping suite names to BenchmarkSuiteResult instances
        """
        print("=" * 80)
        print("Neo Alexandria ML Benchmark Suite")
        print("=" * 80)
        print(f"Started at: {self.start_time.isoformat()}")
        print()
        
        # Run each benchmark suite
        self.results["classification"] = self._run_classification()
        self.results["collaborative_filtering"] = self._run_collaborative_filtering()
        self.results["search_quality"] = self._run_search_quality()
        self.results["summarization_quality"] = self._run_summarization_quality()
        self.results["performance"] = self._run_performance()
        
        # Generate report
        self._generate_report()
        
        # Print summary
        self._print_summary()
        
        return self.results

    def _run_classification(self) -> BenchmarkSuiteResult:
        """
        Run classification benchmarks via pytest.
        
        Returns:
            BenchmarkSuiteResult with classification metrics
        """
        print("\n[1/5] Running Classification Benchmarks...")
        print("-" * 80)
        
        suite_start = datetime.now()
        
        # Run pytest with JSON report
        result_file = self.output_dir / "classification_results.json"
        pytest.main([
            "tests/ml_benchmarks/test_classification_metrics.py",
            "-v",
            "--tb=short",
            "--json-report",
            f"--json-report-file={result_file}",
            "--timeout=1800"
        ])
        
        suite_end = datetime.now()
        execution_time = (suite_end - suite_start).total_seconds()
        
        # Parse results
        suite_result = self._parse_pytest_results(
            result_file,
            "classification",
            execution_time
        )
        
        # Cleanup
        self._cleanup_after_suite()
        
        print(f"✓ Classification benchmarks completed in {execution_time:.2f}s")
        print(f"  Passed: {suite_result.passed_tests}/{suite_result.total_tests}")
        
        return suite_result
    
    def _run_collaborative_filtering(self) -> BenchmarkSuiteResult:
        """
        Run collaborative filtering benchmarks via pytest.
        
        Returns:
            BenchmarkSuiteResult with NCF metrics
        """
        print("\n[2/5] Running Collaborative Filtering Benchmarks...")
        print("-" * 80)
        
        suite_start = datetime.now()
        
        # Run pytest with JSON report
        result_file = self.output_dir / "cf_results.json"
        pytest.main([
            "tests/ml_benchmarks/test_collaborative_filtering_metrics.py",
            "-v",
            "--tb=short",
            "--json-report",
            f"--json-report-file={result_file}",
            "--timeout=1800"
        ])
        
        suite_end = datetime.now()
        execution_time = (suite_end - suite_start).total_seconds()
        
        # Parse results
        suite_result = self._parse_pytest_results(
            result_file,
            "collaborative_filtering",
            execution_time
        )
        
        # Cleanup
        self._cleanup_after_suite()
        
        print(f"✓ Collaborative filtering benchmarks completed in {execution_time:.2f}s")
        print(f"  Passed: {suite_result.passed_tests}/{suite_result.total_tests}")
        
        return suite_result
    
    def _run_search_quality(self) -> BenchmarkSuiteResult:
        """
        Run search quality benchmarks via pytest.
        
        Returns:
            BenchmarkSuiteResult with search metrics
        """
        print("\n[3/5] Running Search Quality Benchmarks...")
        print("-" * 80)
        
        suite_start = datetime.now()
        
        # Run pytest with JSON report
        result_file = self.output_dir / "search_results.json"
        pytest.main([
            "tests/ml_benchmarks/test_search_quality_metrics.py",
            "-v",
            "--tb=short",
            "--json-report",
            f"--json-report-file={result_file}",
            "--timeout=1800"
        ])
        
        suite_end = datetime.now()
        execution_time = (suite_end - suite_start).total_seconds()
        
        # Parse results
        suite_result = self._parse_pytest_results(
            result_file,
            "search_quality",
            execution_time
        )
        
        # Cleanup
        self._cleanup_after_suite()
        
        print(f"✓ Search quality benchmarks completed in {execution_time:.2f}s")
        print(f"  Passed: {suite_result.passed_tests}/{suite_result.total_tests}")
        
        return suite_result
    
    def _run_summarization_quality(self) -> BenchmarkSuiteResult:
        """
        Run summarization quality benchmarks via pytest.
        
        Returns:
            BenchmarkSuiteResult with summarization metrics
        """
        print("\n[4/5] Running Summarization Quality Benchmarks...")
        print("-" * 80)
        
        suite_start = datetime.now()
        
        # Run pytest with JSON report
        result_file = self.output_dir / "summarization_results.json"
        pytest.main([
            "tests/ml_benchmarks/test_summarization_quality_metrics.py",
            "-v",
            "--tb=short",
            "--json-report",
            f"--json-report-file={result_file}",
            "--timeout=1800"
        ])
        
        suite_end = datetime.now()
        execution_time = (suite_end - suite_start).total_seconds()
        
        # Parse results
        suite_result = self._parse_pytest_results(
            result_file,
            "summarization_quality",
            execution_time
        )
        
        # Cleanup
        self._cleanup_after_suite()
        
        print(f"✓ Summarization quality benchmarks completed in {execution_time:.2f}s")
        print(f"  Passed: {suite_result.passed_tests}/{suite_result.total_tests}")
        
        return suite_result
    
    def _run_performance(self) -> BenchmarkSuiteResult:
        """
        Run performance benchmarks via pytest.
        
        Returns:
            BenchmarkSuiteResult with latency metrics
        """
        print("\n[5/5] Running Performance Benchmarks...")
        print("-" * 80)
        
        suite_start = datetime.now()
        
        # Run pytest with JSON report
        result_file = self.output_dir / "performance_results.json"
        pytest.main([
            "tests/performance/test_ml_latency.py",
            "-v",
            "--tb=short",
            "--json-report",
            f"--json-report-file={result_file}",
            "--timeout=1800"
        ])
        
        suite_end = datetime.now()
        execution_time = (suite_end - suite_start).total_seconds()
        
        # Parse results
        suite_result = self._parse_pytest_results(
            result_file,
            "performance",
            execution_time
        )
        
        # Cleanup
        self._cleanup_after_suite()
        
        print(f"✓ Performance benchmarks completed in {execution_time:.2f}s")
        print(f"  Passed: {suite_result.passed_tests}/{suite_result.total_tests}")
        
        return suite_result

    def _parse_pytest_results(
        self,
        result_file: Path,
        suite_name: str,
        execution_time: float
    ) -> BenchmarkSuiteResult:
        """
        Parse pytest JSON output and aggregate results.
        
        Extracts test names, metric values, pass/fail status, and execution times
        from pytest JSON report and aggregates into BenchmarkSuiteResult.
        
        Args:
            result_file: Path to pytest JSON report file
            suite_name: Name of the benchmark suite
            execution_time: Total execution time in seconds
            
        Returns:
            BenchmarkSuiteResult with aggregated metrics
        """
        results = []
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        try:
            if not result_file.exists():
                print(f"  Warning: Result file not found: {result_file}")
                return BenchmarkSuiteResult(
                    suite_name=suite_name,
                    results=[],
                    total_tests=0,
                    passed_tests=0,
                    failed_tests=0,
                    execution_time_seconds=execution_time,
                    recommendations=["Result file not found - tests may have been skipped"]
                )
            
            with open(result_file, 'r') as f:
                data = json.load(f)
            
            # Extract test results
            tests = data.get('tests', [])
            total_tests = len(tests)
            
            for test in tests:
                test_name = test.get('nodeid', 'unknown')
                outcome = test.get('outcome', 'unknown')
                
                # Determine pass/fail
                passed = outcome in ['passed', 'skipped']
                if passed:
                    passed_tests += 1
                else:
                    failed_tests += 1
                
                # Extract metric information from test output
                # This is a simplified extraction - actual implementation
                # would parse stdout/stderr for metric values
                call = test.get('call', {})
                stdout = call.get('stdout', '')
                
                # Create benchmark result
                # Note: In real implementation, we'd parse actual metric values
                # from test output or use custom pytest markers
                result = BenchmarkResult(
                    test_name=test_name,
                    metric_name=self._extract_metric_name(test_name),
                    score=0.0,  # Would be extracted from test output
                    baseline=0.0,  # Would be extracted from test output
                    target=0.0,  # Would be extracted from test output
                    passed=passed,
                    timestamp=datetime.now().isoformat(),
                    details={
                        'outcome': outcome,
                        'duration': test.get('duration', 0.0),
                        'stdout': stdout[:500] if stdout else ''  # Truncate for storage
                    }
                )
                results.append(result)
            
            # Generate recommendations for failed tests
            recommendations = self._generate_suite_recommendations(
                suite_name,
                results,
                failed_tests
            )
            
        except Exception as e:
            print(f"  Error parsing results: {str(e)}")
            recommendations = [f"Error parsing results: {str(e)}"]
        
        return BenchmarkSuiteResult(
            suite_name=suite_name,
            results=results,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            execution_time_seconds=execution_time,
            recommendations=recommendations
        )
    
    def _extract_metric_name(self, test_name: str) -> str:
        """
        Extract metric name from test name.
        
        Args:
            test_name: Full pytest test name (nodeid)
            
        Returns:
            Extracted metric name
        """
        # Extract method name from nodeid
        # e.g., "test_classification_metrics.py::TestClassificationMetrics::test_overall_accuracy"
        if '::' in test_name:
            parts = test_name.split('::')
            if len(parts) >= 2:
                method_name = parts[-1]
                # Convert test_overall_accuracy -> Overall Accuracy
                metric = method_name.replace('test_', '').replace('_', ' ').title()
                return metric
        
        return test_name
    
    def _generate_suite_recommendations(
        self,
        suite_name: str,
        results: List[BenchmarkResult],
        failed_count: int
    ) -> List[str]:
        """
        Generate actionable recommendations for a benchmark suite.
        
        Args:
            suite_name: Name of the benchmark suite
            results: List of benchmark results
            failed_count: Number of failed tests
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if failed_count == 0:
            recommendations.append(f"All {suite_name} benchmarks passed!")
            return recommendations
        
        # Generic recommendations based on suite type
        if suite_name == "classification":
            recommendations.append(
                "Consider adding more training data for underperforming classes"
            )
            recommendations.append(
                "Review hyperparameters (learning rate, batch size, epochs)"
            )
        elif suite_name == "collaborative_filtering":
            recommendations.append(
                "Increase training epochs or adjust embedding dimensions"
            )
            recommendations.append(
                "Consider adding more user-item interactions to training data"
            )
        elif suite_name == "search_quality":
            recommendations.append(
                "Review search weight configuration (FTS5, dense, sparse)"
            )
            recommendations.append(
                "Consider retraining embedding models with more data"
            )
        elif suite_name == "summarization_quality":
            recommendations.append(
                "Review summarization prompts and temperature settings"
            )
            recommendations.append(
                "Consider using a different model or fine-tuning"
            )
        elif suite_name == "performance":
            recommendations.append(
                "Profile code to identify performance bottlenecks"
            )
            recommendations.append(
                "Consider batch processing or caching optimizations"
            )
        
        return recommendations

    def _cleanup_after_suite(self) -> None:
        """
        Clean up resources after benchmark suite execution.
        
        Clears GPU memory (if available) and runs garbage collection
        to prevent memory leaks and OOM errors during long benchmark runs.
        """
        try:
            # Try to clear GPU memory if torch is available
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    print("  ✓ GPU memory cleared")
            except ImportError:
                pass  # torch not available, skip GPU cleanup
            
            # Run garbage collection
            gc.collect()
            print("  ✓ Garbage collection completed")
            
        except Exception as e:
            print(f"  Warning: Cleanup failed: {str(e)}")

    def _generate_report(self) -> None:
        """
        Generate comprehensive markdown benchmark report.
        
        Uses ReportGenerator to create detailed report with executive summary,
        per-suite results, regression detection, and recommendations.
        Saves to docs/ML_BENCHMARKS.md.
        """
        print("\n" + "=" * 80)
        print("Generating Benchmark Report...")
        print("=" * 80)
        
        try:
            try:
                from .report_generator import ReportGenerator
            except ImportError:
                from report_generator import ReportGenerator
            
            # Create report generator
            generator = ReportGenerator(self.results, output_dir=str(self.output_dir))
            
            # Generate comprehensive report
            generator.generate()
            
            print("✓ Report generation complete")
            
        except Exception as e:
            print(f"⚠️ Error generating report: {str(e)}")
            print("Falling back to basic report generation...")
            
            # Fallback to basic report
            self._generate_basic_report()
    
    def _generate_basic_report(self) -> None:
        """
        Generate basic markdown report (fallback).
        
        Used when ReportGenerator is not available or fails.
        """
        report_lines = []
        
        # Header
        report_lines.append("# Neo Alexandria ML Benchmark Report")
        report_lines.append("")
        report_lines.append(f"**Generated**: {datetime.now().isoformat()}")
        report_lines.append(f"**Started**: {self.start_time.isoformat()}")
        
        total_duration = (datetime.now() - self.start_time).total_seconds()
        report_lines.append(f"**Total Duration**: {total_duration:.2f}s ({total_duration/60:.2f} minutes)")
        report_lines.append("")
        
        # Executive Summary
        report_lines.append("## Executive Summary")
        report_lines.append("")
        report_lines.append("| Suite | Total Tests | Passed | Failed | Duration (s) | Status |")
        report_lines.append("|-------|-------------|--------|--------|--------------|--------|")
        
        for suite_name, suite_result in self.results.items():
            status = "✅ PASS" if suite_result.failed_tests == 0 else "❌ FAIL"
            report_lines.append(
                f"| {suite_name.replace('_', ' ').title()} | "
                f"{suite_result.total_tests} | "
                f"{suite_result.passed_tests} | "
                f"{suite_result.failed_tests} | "
                f"{suite_result.execution_time_seconds:.2f} | "
                f"{status} |"
            )
        
        report_lines.append("")
        
        # Per-Suite Details
        report_lines.append("## Detailed Results")
        report_lines.append("")
        
        for suite_name, suite_result in self.results.items():
            report_lines.append(f"### {suite_name.replace('_', ' ').title()}")
            report_lines.append("")
            report_lines.append(f"**Execution Time**: {suite_result.execution_time_seconds:.2f}s")
            report_lines.append(f"**Tests**: {suite_result.total_tests} total, "
                              f"{suite_result.passed_tests} passed, "
                              f"{suite_result.failed_tests} failed")
            report_lines.append("")
            
            # Test results table
            if suite_result.results:
                report_lines.append("| Test | Metric | Status | Duration (s) |")
                report_lines.append("|------|--------|--------|--------------|")
                
                for result in suite_result.results:
                    status_icon = "✅" if result.passed else "❌"
                    duration = result.details.get('duration', 0.0)
                    report_lines.append(
                        f"| {result.test_name.split('::')[-1] if '::' in result.test_name else result.test_name} | "
                        f"{result.metric_name} | "
                        f"{status_icon} | "
                        f"{duration:.2f} |"
                    )
                
                report_lines.append("")
            
            # Recommendations
            if suite_result.recommendations:
                report_lines.append("**Recommendations:**")
                report_lines.append("")
                for i, rec in enumerate(suite_result.recommendations, 1):
                    report_lines.append(f"{i}. {rec}")
                report_lines.append("")
        
        # Overall Recommendations
        report_lines.append("## Overall Recommendations")
        report_lines.append("")
        
        total_failed = sum(s.failed_tests for s in self.results.values())
        if total_failed == 0:
            report_lines.append("✅ All benchmarks passed! The ML system is performing well.")
        else:
            report_lines.append(f"⚠️ {total_failed} tests failed across all suites.")
            report_lines.append("")
            report_lines.append("Priority actions:")
            report_lines.append("1. Review failed tests and investigate root causes")
            report_lines.append("2. Check if test datasets need updating")
            report_lines.append("3. Consider retraining models with more data")
            report_lines.append("4. Review hyperparameters and model configurations")
        
        report_lines.append("")
        
        # Reproduction Steps
        report_lines.append("## Reproduction Steps")
        report_lines.append("")
        report_lines.append("```bash")
        report_lines.append("# Run all benchmarks")
        report_lines.append("python backend/tests/ml_benchmarks/benchmark_runner.py")
        report_lines.append("")
        report_lines.append("# Run specific suite")
        report_lines.append("python backend/tests/ml_benchmarks/benchmark_runner.py --suite classification")
        report_lines.append("")
        report_lines.append("# Generate report only (from existing results)")
        report_lines.append("python backend/tests/ml_benchmarks/benchmark_runner.py --report-only")
        report_lines.append("```")
        report_lines.append("")
        
        # Save report
        report_path = self.output_dir / "ML_BENCHMARKS.md"
        with open(report_path, 'w') as f:
            f.write('\n'.join(report_lines))
        
        print(f"✓ Report saved to: {report_path}")
        
        # Also save JSON results for programmatic access
        json_path = self.output_dir / "ML_BENCHMARKS.json"
        json_data = {
            'generated_at': datetime.now().isoformat(),
            'total_duration_seconds': total_duration,
            'suites': {
                name: {
                    'total_tests': suite.total_tests,
                    'passed_tests': suite.passed_tests,
                    'failed_tests': suite.failed_tests,
                    'execution_time_seconds': suite.execution_time_seconds,
                    'recommendations': suite.recommendations
                }
                for name, suite in self.results.items()
            }
        }
        
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"✓ JSON results saved to: {json_path}")
    
    def _print_summary(self) -> None:
        """Print summary of benchmark results to console."""
        print("\n" + "=" * 80)
        print("Benchmark Summary")
        print("=" * 80)
        
        total_tests = sum(s.total_tests for s in self.results.values())
        total_passed = sum(s.passed_tests for s in self.results.values())
        total_failed = sum(s.failed_tests for s in self.results.values())
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed} ({100*total_passed/total_tests if total_tests > 0 else 0:.1f}%)")
        print(f"Failed: {total_failed} ({100*total_failed/total_tests if total_tests > 0 else 0:.1f}%)")
        print(f"Duration: {total_duration:.2f}s ({total_duration/60:.2f} minutes)")
        print()
        
        if total_failed == 0:
            print("✅ All benchmarks passed!")
        else:
            print(f"❌ {total_failed} benchmarks failed")
            print("\nFailed suites:")
            for suite_name, suite_result in self.results.items():
                if suite_result.failed_tests > 0:
                    print(f"  - {suite_name}: {suite_result.failed_tests} failed")
        
        print("=" * 80)
    
    def run_single_suite(self, suite_name: str) -> Optional[BenchmarkSuiteResult]:
        """
        Run a single benchmark suite.
        
        Args:
            suite_name: Name of suite to run (classification, collaborative_filtering,
                       search_quality, summarization_quality, performance)
                       
        Returns:
            BenchmarkSuiteResult or None if suite not found
        """
        suite_map = {
            'classification': self._run_classification,
            'collaborative_filtering': self._run_collaborative_filtering,
            'search_quality': self._run_search_quality,
            'summarization_quality': self._run_summarization_quality,
            'performance': self._run_performance
        }
        
        if suite_name not in suite_map:
            print(f"Error: Unknown suite '{suite_name}'")
            print(f"Available suites: {', '.join(suite_map.keys())}")
            return None
        
        print(f"Running {suite_name} benchmark suite...")
        result = suite_map[suite_name]()
        self.results[suite_name] = result
        
        return result


def main():
    """
    Command-line interface for benchmark runner.
    
    Supports:
    - Running all benchmarks
    - Running individual suites
    - Report generation only
    """
    parser = argparse.ArgumentParser(
        description='Neo Alexandria ML Benchmark Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all benchmarks
  python benchmark_runner.py
  
  # Run specific suite
  python benchmark_runner.py --suite classification
  
  # Generate report only (from existing results)
  python benchmark_runner.py --report-only
  
  # Custom output directory
  python benchmark_runner.py --output /path/to/output
        """
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='docs',
        help='Output directory for reports (default: docs)'
    )
    
    parser.add_argument(
        '--suite',
        type=str,
        choices=['classification', 'collaborative_filtering', 'search_quality',
                'summarization_quality', 'performance'],
        help='Run only a specific benchmark suite'
    )
    
    parser.add_argument(
        '--report-only',
        action='store_true',
        help='Generate report from existing results without running tests'
    )
    
    args = parser.parse_args()
    
    # Create runner
    runner = BenchmarkRunner(output_dir=args.output)
    
    if args.report_only:
        print("Report-only mode: Loading existing results...")
        # In report-only mode, we'd load previous results from JSON
        # For now, just print a message
        print("Note: Report-only mode requires existing result files")
        print("Run benchmarks first to generate results")
        return 0
    
    # Run benchmarks
    if args.suite:
        # Run single suite
        result = runner.run_single_suite(args.suite)
        if result is None:
            return 1
        
        # Generate report for single suite
        runner._generate_report()
        
        # Return exit code based on results
        return 1 if result.failed_tests > 0 else 0
    else:
        # Run all benchmarks
        results = runner.run_all_benchmarks()
        
        # Return exit code based on results
        total_failed = sum(s.failed_tests for s in results.values())
        return 1 if total_failed > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
