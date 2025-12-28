#!/usr/bin/env python
"""
Test script to verify all endpoints are working after modular refactoring.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set testing flag to skip database initialization
os.environ["TESTING"] = "true"

def test_module_imports():
    """Test that all modules can be imported."""
    print("=" * 80)
    print("TESTING MODULE IMPORTS")
    print("=" * 80)
    
    modules_to_test = [
        ("Collections", "app.modules.collections", "collections_router"),
        ("Resources", "app.modules.resources", "resources_router"),
        ("Search", "app.modules.search", "search_router"),
    ]
    
    results = []
    for name, module_path, router_name in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[router_name])
            router = getattr(module, router_name)
            route_count = len(router.routes)
            print(f"✓ {name:15} - {route_count} routes")
            results.append((name, True, route_count, None))
        except Exception as e:
            print(f"✗ {name:15} - FAILED: {e}")
            results.append((name, False, 0, str(e)))
    
    return results


def test_app_creation():
    """Test that the FastAPI app can be created."""
    print("\n" + "=" * 80)
    print("TESTING APPLICATION CREATION")
    print("=" * 80)
    
    try:
        from app import create_app
        app = create_app()
        print("✓ Application created successfully")
        print(f"  Title: {app.title}")
        print(f"  Version: {app.version}")
        return app, None
    except Exception as e:
        print(f"✗ Application creation FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None, str(e)


def list_all_endpoints(app):
    """List all registered endpoints."""
    print("\n" + "=" * 80)
    print("ALL REGISTERED ENDPOINTS")
    print("=" * 80)
    
    endpoints_by_module = {}
    
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            methods = ", ".join(sorted(route.methods))
            path = route.path
            name = route.name if hasattr(route, "name") else "unknown"
            
            # Categorize by path prefix
            if path.startswith("/api/collections"):
                module = "Collections Module"
            elif path.startswith("/api/resources"):
                module = "Resources Module"
            elif path.startswith("/api/search"):
                module = "Search Module"
            elif path.startswith("/api/curation"):
                module = "Curation (Legacy)"
            elif path.startswith("/api/authority"):
                module = "Authority (Legacy)"
            elif path.startswith("/api/classification"):
                module = "Classification (Legacy)"
            elif path.startswith("/api/graph"):
                module = "Graph (Legacy)"
            elif path.startswith("/api/recommendations"):
                module = "Recommendations (Legacy)"
            elif path.startswith("/api/citations"):
                module = "Citations (Legacy)"
            elif path.startswith("/api/annotations"):
                module = "Annotations (Legacy)"
            elif path.startswith("/api/taxonomy"):
                module = "Taxonomy (Legacy)"
            elif path.startswith("/api/quality"):
                module = "Quality (Legacy)"
            elif path.startswith("/api/discovery"):
                module = "Discovery (Legacy)"
            elif path.startswith("/monitoring"):
                module = "Monitoring"
            else:
                module = "Other"
            
            if module not in endpoints_by_module:
                endpoints_by_module[module] = []
            
            endpoints_by_module[module].append({
                "methods": methods,
                "path": path,
                "name": name
            })
    
    # Print organized by module
    total_endpoints = 0
    for module in sorted(endpoints_by_module.keys()):
        endpoints = endpoints_by_module[module]
        print(f"\n{module} ({len(endpoints)} endpoints):")
        print("-" * 80)
        for endpoint in sorted(endpoints, key=lambda x: x["path"]):
            print(f"  {endpoint['methods']:20} {endpoint['path']}")
        total_endpoints += len(endpoints)
    
    print("\n" + "=" * 80)
    print(f"TOTAL ENDPOINTS: {total_endpoints}")
    print("=" * 80)
    
    return endpoints_by_module


def verify_critical_endpoints(app):
    """Verify that critical endpoints exist."""
    print("\n" + "=" * 80)
    print("VERIFYING CRITICAL ENDPOINTS")
    print("=" * 80)
    
    critical_endpoints = [
        # Resources Module
        ("POST", "/api/resources", "Create resource (URL ingestion)"),
        ("GET", "/api/resources", "List resources"),
        ("GET", "/api/resources/{resource_id}", "Get resource"),
        ("PUT", "/api/resources/{resource_id}", "Update resource"),
        ("DELETE", "/api/resources/{resource_id}", "Delete resource"),
        ("GET", "/api/resources/{resource_id}/status", "Get ingestion status"),
        
        # Collections Module
        ("POST", "/api/collections", "Create collection"),
        ("GET", "/api/collections", "List collections"),
        ("GET", "/api/collections/{collection_id}", "Get collection"),
        ("PUT", "/api/collections/{collection_id}", "Update collection"),
        ("DELETE", "/api/collections/{collection_id}", "Delete collection"),
        ("PUT", "/api/collections/{collection_id}/resources", "Update collection resources"),
        
        # Search Module
        ("POST", "/api/search/hybrid", "Hybrid search"),
        ("POST", "/api/search/fts", "FTS search"),
        ("POST", "/api/search/vector", "Vector search"),
    ]
    
    all_paths = set()
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            for method in route.methods:
                # Normalize path by removing path parameters
                normalized_path = route.path
                all_paths.add((method, normalized_path))
    
    missing = []
    found = []
    
    for method, path, description in critical_endpoints:
        # Check if endpoint exists (accounting for path parameters)
        exists = False
        for registered_method, registered_path in all_paths:
            if registered_method == method:
                # Simple check - does the base path match?
                if "{" in path:
                    # Has path parameter - check base path
                    base_path = path.split("{")[0].rstrip("/")
                    if registered_path.startswith(base_path):
                        exists = True
                        break
                else:
                    # Exact match
                    if registered_path == path:
                        exists = True
                        break
        
        if exists:
            print(f"✓ {method:6} {path:50} - {description}")
            found.append((method, path, description))
        else:
            print(f"✗ {method:6} {path:50} - {description} [MISSING]")
            missing.append((method, path, description))
    
    print("\n" + "-" * 80)
    print(f"Found: {len(found)}/{len(critical_endpoints)} critical endpoints")
    
    if missing:
        print(f"\n⚠️  WARNING: {len(missing)} critical endpoints are missing!")
        return False
    else:
        print("\n✓ All critical endpoints are registered!")
        return True


def main():
    """Main test function."""
    print("\n" + "=" * 80)
    print("NEO ALEXANDRIA 2.0 - ENDPOINT VERIFICATION")
    print("=" * 80)
    
    # Test 1: Module imports
    import_results = test_module_imports()
    
    # Test 2: App creation
    app, error = test_app_creation()
    
    if app is None:
        print("\n❌ FAILED: Cannot create application")
        return 1
    
    # Test 3: List all endpoints
    list_all_endpoints(app)
    
    # Test 4: Verify critical endpoints
    all_critical_present = verify_critical_endpoints(app)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    module_success = all(result[1] for result in import_results)
    app_success = app is not None
    
    print(f"Module Imports:      {'✓ PASS' if module_success else '✗ FAIL'}")
    print(f"App Creation:        {'✓ PASS' if app_success else '✗ FAIL'}")
    print(f"Critical Endpoints:  {'✓ PASS' if all_critical_present else '✗ FAIL'}")
    
    if module_success and app_success and all_critical_present:
        print("\n✓ ALL TESTS PASSED - All endpoints are working!")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED - See details above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
