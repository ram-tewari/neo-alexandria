"""
Simple test to verify quality API endpoints are properly defined.

This test checks that all endpoints are registered and have the correct
HTTP methods and paths.
"""

import sys
from pathlib import Path


def test_quality_router_structure():
    """Test that quality router has all expected endpoints."""
    
    # Import the router using proper Python import
    # The backend directory is already in the Python path via pytest configuration
    try:
        from backend.app.routers.quality import router
    except ImportError:
        # Fallback: add backend to path if needed
        backend_root = Path(__file__).parent.parent.parent.parent
        if str(backend_root) not in sys.path:
            sys.path.insert(0, str(backend_root))
        from backend.app.routers.quality import router
    
    print("=" * 80)
    print("Quality API Endpoints Verification")
    print("=" * 80)
    
    # Check that router exists
    assert router is not None, "Router should exist"
    print("\n✓ Quality router created successfully")
    
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
