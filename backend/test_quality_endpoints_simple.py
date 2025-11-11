"""
Simple test to verify quality API endpoints are properly defined.

This test checks that all endpoints are registered and have the correct
HTTP methods and paths.
"""

import sys
from pathlib import Path

# Ensure we can import from app
sys.path.insert(0, str(Path(__file__).parent))


def test_quality_router_structure():
    """Test that quality router has all expected endpoints."""
    
    # Import the router directly (avoiding app init issues)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "quality_router",
        Path(__file__).parent / "app" / "routers" / "quality.py"
    )
    quality_module = importlib.util.module_from_spec(spec)
    
    # Mock the dependencies before loading
    import unittest.mock as mock
    
    # Mock all the imports that might fail
    sys.modules['app.database.base'] = mock.MagicMock()
    sys.modules['app.database.models'] = mock.MagicMock()
    sys.modules['app.schemas.quality'] = mock.MagicMock()
    sys.modules['app.services.quality_service'] = mock.MagicMock()
    sys.modules['app.services.summarization_evaluator'] = mock.MagicMock()
    
    # Now load the module
    spec.loader.exec_module(quality_module)
    
    router = quality_module.router
    
    print("=" * 80)
    print("Quality API Endpoints Verification")
    print("=" * 80)
    
    # Check that router exists
    assert router is not None, "Router should exist"
    print(f"\n✓ Quality router created successfully")
    
    # Get all routes
    routes = router.routes
    print(f"✓ Router has {len(routes)} routes")
    
    # Expected endpoints
    expected_endpoints = [
        ("GET", "/resources/{resource_id}/quality-details"),
        ("POST", "/quality/recalculate"),
        ("GET", "/quality/outliers"),
        ("GET", "/quality/degradation"),
        ("POST", "/summaries/{resource_id}/evaluate"),
        ("GET", "/quality/distribution"),
        ("GET", "/quality/trends"),
        ("GET", "/quality/dimensions"),
        ("GET", "/quality/review-queue"),
    ]
    
    print("\nVerifying endpoints:")
    found_endpoints = []
    
    for route in routes:
        methods = list(route.methods) if hasattr(route, 'methods') else []
        path = route.path if hasattr(route, 'path') else ""
        
        for method in methods:
            endpoint = (method, path)
            found_endpoints.append(endpoint)
            print(f"  {method:6} {path}")
    
    print("\nChecking expected endpoints:")
    all_found = True
    for method, path in expected_endpoints:
        found = any(
            m == method and p == path
            for m, p in found_endpoints
        )
        status = "✓" if found else "✗"
        print(f"  {status} {method:6} {path}")
        if not found:
            all_found = False
    
    print("\n" + "=" * 80)
    if all_found:
        print("SUCCESS: All 9 quality API endpoints are properly defined!")
    else:
        print("WARNING: Some endpoints may be missing")
    print("=" * 80)
    
    return all_found


if __name__ == "__main__":
    try:
        success = test_quality_router_structure()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
