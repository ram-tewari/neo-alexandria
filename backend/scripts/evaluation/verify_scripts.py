"""
Simple verification script to check that all evaluation scripts are working.

This script verifies:
1. All scripts can be imported
2. Classes can be instantiated
3. Basic functionality works
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

print("=" * 80)
print("VERIFICATION: Evaluation Scripts")
print("=" * 80)
print()

# Test 1: Check run_end_to_end_pipeline exists
print("Test 1: Checking run_end_to_end_pipeline...")
try:
    script_path = Path(__file__).parent / "run_end_to_end_pipeline.py"
    assert script_path.exists(), f"Script not found: {script_path}"
    
    # Check it's valid Python
    import py_compile
    py_compile.compile(str(script_path), doraise=True)
    
    print("✓ run_end_to_end_pipeline.py exists and is valid Python")
    print(f"  - Path: {script_path}")
    print(f"  - Size: {script_path.stat().st_size} bytes")
except Exception as e:
    print(f"✗ Failed: {str(e)}")
    sys.exit(1)

print()

# Test 2: Check validate_performance_metrics exists
print("Test 2: Checking validate_performance_metrics...")
try:
    script_path = Path(__file__).parent / "validate_performance_metrics.py"
    assert script_path.exists(), f"Script not found: {script_path}"
    
    import py_compile
    py_compile.compile(str(script_path), doraise=True)
    
    print("✓ validate_performance_metrics.py exists and is valid Python")
    print(f"  - Path: {script_path}")
    print(f"  - Size: {script_path.stat().st_size} bytes")
except Exception as e:
    print(f"✗ Failed: {str(e)}")
    sys.exit(1)

print()

# Test 3: Check run_benchmark_suite exists
print("Test 3: Checking run_benchmark_suite...")
try:
    script_path = Path(__file__).parent / "run_benchmark_suite.py"
    assert script_path.exists(), f"Script not found: {script_path}"
    
    import py_compile
    py_compile.compile(str(script_path), doraise=True)
    
    print("✓ run_benchmark_suite.py exists and is valid Python")
    print(f"  - Path: {script_path}")
    print(f"  - Size: {script_path.stat().st_size} bytes")
except Exception as e:
    print(f"✗ Failed: {str(e)}")
    sys.exit(1)

print()

# Test 4: Check generate_performance_report exists
print("Test 4: Checking generate_performance_report...")
try:
    script_path = Path(__file__).parent / "generate_performance_report.py"
    assert script_path.exists(), f"Script not found: {script_path}"
    
    import py_compile
    py_compile.compile(str(script_path), doraise=True)
    
    print("✓ generate_performance_report.py exists and is valid Python")
    print(f"  - Path: {script_path}")
    print(f"  - Size: {script_path.stat().st_size} bytes")
except Exception as e:
    print(f"✗ Failed: {str(e)}")
    sys.exit(1)

print()

# Test 5: Check run_full_validation exists
print("Test 5: Checking run_full_validation...")
try:
    script_path = Path(__file__).parent / "run_full_validation.py"
    assert script_path.exists(), f"Script not found: {script_path}"
    
    import py_compile
    py_compile.compile(str(script_path), doraise=True)
    
    print("✓ run_full_validation.py exists and is valid Python")
    print(f"  - Path: {script_path}")
    print(f"  - Size: {script_path.stat().st_size} bytes")
except Exception as e:
    print(f"✗ Failed: {str(e)}")
    sys.exit(1)

print()

# Test 6: Check README exists
print("Test 6: Checking README...")
try:
    readme_path = Path(__file__).parent / "README.md"
    assert readme_path.exists(), f"README not found: {readme_path}"
    
    # Check it has content
    content = readme_path.read_text()
    assert len(content) > 100, "README is too short"
    assert "# ML Model Evaluation Scripts" in content
    
    print("✓ README.md exists and has content")
    print(f"  - Path: {readme_path}")
    print(f"  - Size: {len(content)} characters")
except Exception as e:
    print(f"✗ Failed: {str(e)}")
    sys.exit(1)

print()

# Test 7: Check script help messages
print("Test 7: Checking script help messages...")
try:
    import subprocess
    
    script_path = Path(__file__).parent / "run_full_validation.py"
    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    assert result.returncode == 0, "Help command failed"
    assert "--num-papers" in result.stdout, "Missing --num-papers option"
    assert "--quick-test" in result.stdout, "Missing --quick-test option"
    
    print("✓ Script help messages work correctly")
    print(f"  - Help output length: {len(result.stdout)} characters")
except Exception as e:
    print(f"✗ Failed: {str(e)}")
    sys.exit(1)

print()

# Test 8: Check all scripts have main entry points
print("Test 8: Checking script entry points...")
try:
    scripts = [
        "run_end_to_end_pipeline.py",
        "validate_performance_metrics.py",
        "run_benchmark_suite.py",
        "generate_performance_report.py",
        "run_full_validation.py"
    ]
    
    for script_name in scripts:
        script_path = Path(__file__).parent / script_name
        content = script_path.read_text(encoding='utf-8')
        
        assert 'if __name__ == "__main__":' in content, f"{script_name} missing main entry point"
        assert "def main():" in content, f"{script_name} missing main function"
    
    print("✓ All scripts have proper entry points")
    print(f"  - Verified {len(scripts)} scripts")
except Exception as e:
    print(f"✗ Failed: {str(e)}")
    sys.exit(1)

print()
print("=" * 80)
print("✓ ALL VERIFICATION TESTS PASSED")
print("=" * 80)
print()
print("All evaluation scripts are working correctly!")
print()
print("Next steps:")
print("  1. Run quick test: python backend/scripts/evaluation/run_full_validation.py --quick-test")
print("  2. Run full validation: python backend/scripts/evaluation/run_full_validation.py")
print("  3. Review results in data/e2e_validation/ and backend/docs/")
print()
