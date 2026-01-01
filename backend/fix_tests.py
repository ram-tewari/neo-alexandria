#!/usr/bin/env python3
"""
Quick test fix script to verify our changes work.
Runs a subset of tests to validate fixes.
"""

import subprocess
import sys

def run_test(test_path, description):
    """Run a single test and report results."""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return False
    return True

def main():
    """Run test suite to verify fixes."""
    tests = [
        ("tests/modules/monitoring/test_service.py::TestPerformanceMetrics::test_get_performance_metrics_success", 
         "Monitoring async test (pytest-asyncio fix)"),
        ("tests/test_annotation_workflow_e2e.py::TestAnnotationWorkflowE2E::test_complete_annotation_workflow",
         "Annotation E2E workflow (router fix)"),
    ]
    
    passed = 0
    failed = 0
    
    for test_path, description in tests:
        if run_test(test_path, description):
            passed += 1
            print(f"✓ PASSED: {description}")
        else:
            failed += 1
            print(f"✗ FAILED: {description}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
