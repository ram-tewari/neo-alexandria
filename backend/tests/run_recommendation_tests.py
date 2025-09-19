#!/usr/bin/env python3
"""
Neo Alexandria 2.0 - Phase 5.5 Recommendation System Test Runner

This script provides a specialized test runner for the recommendation system
with multiple execution modes, coverage reporting, and performance testing.

Related files:
- test_phase55_recommendations.py: Main test suite being executed
- test_recommendation_config.py: Test utilities and configuration
- conftest.py: Test fixtures and database setup
- pytest.ini: Pytest configuration with recommendation markers

Features:
- Multiple test execution modes (unit, integration, api, performance, etc.)
- Coverage reporting with HTML and terminal output
- Parallel test execution support
- Performance benchmarking capabilities
- Custom test filtering and organization
- CI/CD friendly command-line interface

Execution Modes:
- unit: Run only unit tests (fastest)
- integration: Run integration tests
- api: Run API endpoint tests
- performance: Run performance tests (includes slow tests)
- edge_cases: Run edge case and error handling tests
- all: Run all recommendation tests
- quick: Run tests excluding slow ones
- coverage: Run with comprehensive coverage reporting

Usage Examples:
- python run_recommendation_tests.py unit
- python run_recommendation_tests.py coverage --html-coverage
- python run_recommendation_tests.py performance --verbose
- python run_recommendation_tests.py all --parallel 4

Options:
- --verbose: Enable verbose output
- --coverage: Generate coverage report
- --html-coverage: Generate HTML coverage report
- --parallel N: Run tests in parallel with N processes
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return the exit code."""
    if description:
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"Command: {' '.join(cmd)}")
        print(f"{'='*60}")
    
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run Phase 5.5 Recommendation System tests")
    parser.add_argument(
        "test_type",
        choices=["unit", "integration", "api", "performance", "edge_cases", "all", "quick", "coverage"],
        help="Type of recommendation tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--html-coverage",
        action="store_true",
        help="Generate HTML coverage report"
    )
    parser.add_argument(
        "--parallel", "-n",
        type=int,
        default=1,
        help="Number of parallel test processes"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add parallel execution
    if args.parallel > 1:
        cmd.extend(["-n", str(args.parallel)])
    
    # Add coverage
    if args.coverage or args.html_coverage:
        cmd.extend(["--cov=backend.app.services.recommendation_service"])
        cmd.extend(["--cov=backend.app.routers.recommendation"])
        cmd.extend(["--cov=backend.app.schemas.recommendation"])
        cmd.append("--cov-report=term")
        
        if args.html_coverage:
            cmd.append("--cov-report=html:htmlcov_recommendations")
    
    # Test type specific configurations
    if args.test_type == "unit":
        cmd.extend([
            "-m", "recommendation_unit",
            "--tb=short"
        ])
        description = "Unit tests for recommendation system components"
        
    elif args.test_type == "integration":
        cmd.extend([
            "-m", "recommendation_integration",
            "--tb=short"
        ])
        description = "Integration tests for recommendation system"
        
    elif args.test_type == "api":
        cmd.extend([
            "-m", "recommendation_api",
            "--tb=short"
        ])
        description = "API endpoint tests for recommendations"
        
    elif args.test_type == "performance":
        cmd.extend([
            "-m", "recommendation_performance",
            "--tb=short"
        ])
        description = "Performance tests for recommendation system"
        
    elif args.test_type == "edge_cases":
        cmd.extend([
            "-m", "recommendation_edge_cases",
            "--tb=short"
        ])
        description = "Edge case and error handling tests"
        
    elif args.test_type == "quick":
        cmd.extend([
            "-m", "recommendation and not slow",
            "--tb=short"
        ])
        description = "Quick recommendation tests (excluding slow tests)"
        
    elif args.test_type == "coverage":
        cmd.extend([
            "-m", "recommendation",
            "--cov=backend.app.services.recommendation_service",
            "--cov=backend.app.routers.recommendation",
            "--cov=backend.app.schemas.recommendation",
            "--cov-report=html:htmlcov_recommendations",
            "--cov-report=term-missing",
            "--tb=short"
        ])
        description = "Full recommendation test suite with coverage"
        
    elif args.test_type == "all":
        cmd.extend([
            "-m", "recommendation",
            "--tb=short"
        ])
        description = "All recommendation system tests"
    
    # Add the specific test file
    cmd.append("tests/test_phase55_recommendations.py")
    
    # Run the tests
    exit_code = run_command(cmd, description)
    
    if exit_code == 0:
        print(f"\n✅ {args.test_type} recommendation tests passed!")
        
        if args.html_coverage:
            print(f"\n📊 HTML coverage report generated in: htmlcov_recommendations/")
            print(f"   Open htmlcov_recommendations/index.html in your browser to view detailed coverage")
    else:
        print(f"\n❌ {args.test_type} recommendation tests failed!")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
