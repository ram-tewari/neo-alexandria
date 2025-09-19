#!/usr/bin/env python3
"""
Test runner script for Neo Alexandria.

This script provides different test configurations to run tests with or without AI mocking.
"""

import sys
import subprocess
import argparse


def run_command(cmd):
    """Run a command and return the exit code."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run Neo Alexandria tests")
    parser.add_argument(
        "test_type",
        choices=["unit", "integration", "ai", "all", "fast", "slow"],
        help="Type of tests to run"
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
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add coverage
    if args.coverage:
        cmd.extend(["--cov=backend", "--cov-report=html", "--cov-report=term"])
    
    # Test type specific configurations
    if args.test_type == "unit":
        # Unit tests - fast, mocked AI
        cmd.extend([
            "-m", "not (ai or integration or slow)",
            "--tb=short"
        ])
        print("Running unit tests (fast, with AI mocking)...")
        
    elif args.test_type == "integration":
        # Integration tests - may include some AI
        cmd.extend([
            "-m", "integration",
            "--tb=short"
        ])
        print("Running integration tests...")
        
    elif args.test_type == "ai":
        # AI tests - real AI functionality
        cmd.extend([
            "-m", "ai",
            "--tb=short"
        ])
        print("Running AI tests (real AI functionality)...")
        
    elif args.test_type == "fast":
        # Fast tests - everything except slow and AI
        cmd.extend([
            "-m", "not (slow or requires_ai_deps)",
            "--tb=short"
        ])
        print("Running fast tests (no AI dependencies)...")
        
    elif args.test_type == "slow":
        # Slow tests - includes AI
        cmd.extend([
            "-m", "slow or requires_ai_deps",
            "--tb=short"
        ])
        print("Running slow tests (includes AI)...")
        
    elif args.test_type == "all":
        # All tests
        cmd.extend(["--tb=short"])
        print("Running all tests...")
    
    # Run the tests
    exit_code = run_command(cmd)
    
    if exit_code == 0:
        print(f"\n✅ {args.test_type} tests passed!")
    else:
        print(f"\n❌ {args.test_type} tests failed!")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
