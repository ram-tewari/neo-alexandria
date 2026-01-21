#!/usr/bin/env python3
"""
Test all endpoints on the deployed cloud API.
Tests public endpoints and authenticated endpoints.
"""

import requests
import json
import sys
from typing import Dict, List, Tuple
from datetime import datetime

# Cloud API URL
BASE_URL = "https://pharos.onrender.com"

# Test results
results = {
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "tests": []
}


def test_endpoint(
    method: str,
    path: str,
    expected_status: int,
    description: str,
    headers: Dict = None,
    json_data: Dict = None,
    auth_required: bool = False
) -> Tuple[bool, str]:
    """Test a single endpoint."""
    url = f"{BASE_URL}{path}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=json_data, timeout=30)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=json_data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            return False, f"Unsupported method: {method}"
        
        # Check status code
        if response.status_code == expected_status:
            return True, f"✓ {response.status_code}"
        elif auth_required and response.status_code == 401:
            return True, f"✓ 401 (auth required, as expected)"
        else:
            return False, f"✗ Expected {expected_status}, got {response.status_code}"
            
    except requests.exceptions.Timeout:
        return False, "✗ Timeout"
    except requests.exceptions.ConnectionError:
        return False, "✗ Connection error"
    except Exception as e:
        return False, f"✗ Error: {str(e)}"


def run_tests():
    """Run all endpoint tests."""
    print("=" * 80)
    print(f"Testing Cloud API: {BASE_URL}")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 80)
    print()
    
    # Test categories
    tests = [
        # Public endpoints
        ("Public Endpoints", [
            ("GET", "/docs", 200, "API Documentation", False),
            ("GET", "/openapi.json", 200, "OpenAPI Schema", False),
            ("GET", "/redoc", 200, "ReDoc Documentation", False),
            ("GET", "/api/monitoring/health", 200, "Health Check", False),
        ]),
        
        # Auth endpoints (should work without token for registration/login)
        ("Auth Endpoints", [
            ("GET", "/api/auth/health", 200, "Auth Health Check", False),
            ("POST", "/api/auth/register", 422, "Register (no data)", False),
            ("POST", "/api/auth/login", 422, "Login (no data)", False),
        ]),
        
        # Protected endpoints (should return 401 without auth)
        ("Resources Endpoints (Protected)", [
            ("GET", "/api/resources/health", 401, "Resources Health", True),
            ("GET", "/api/resources/", 401, "List Resources", True),
            ("POST", "/api/resources/", 401, "Create Resource", True),
        ]),
        
        ("Collections Endpoints (Protected)", [
            ("GET", "/api/collections/health", 401, "Collections Health", True),
            ("GET", "/api/collections/", 401, "List Collections", True),
        ]),
        
        ("Search Endpoints (Protected)", [
            ("GET", "/api/search/health", 401, "Search Health", True),
            ("GET", "/api/search/?q=test", 401, "Search Query", True),
        ]),
        
        ("Annotations Endpoints (Protected)", [
            ("GET", "/api/annotations/health", 401, "Annotations Health", True),
            ("GET", "/api/annotations/", 401, "List Annotations", True),
        ]),
        
        ("Quality Endpoints (Protected)", [
            ("GET", "/api/quality/health", 401, "Quality Health", True),
        ]),
        
        ("Taxonomy Endpoints (Protected)", [
            ("GET", "/api/taxonomy/health", 401, "Taxonomy Health", True),
            ("GET", "/api/taxonomy/categories", 401, "List Categories", True),
        ]),
        
        ("Graph Endpoints (Protected)", [
            ("GET", "/api/graph/health", 401, "Graph Health", True),
        ]),
        
        ("Scholarly Endpoints (Protected)", [
            ("GET", "/api/scholarly/health", 401, "Scholarly Health", True),
        ]),
        
        ("Authority Endpoints (Protected)", [
            ("GET", "/api/authority/health", 401, "Authority Health", True),
        ]),
        
        ("Curation Endpoints (Protected)", [
            ("GET", "/api/curation/health", 401, "Curation Health", True),
        ]),
        
        # Phase 19 Ingestion endpoints (require admin token)
        ("Ingestion Endpoints (Admin Only)", [
            ("GET", "/api/v1/ingestion/health", 200, "Ingestion Health", False),
            ("GET", "/api/v1/ingestion/worker/status", 200, "Worker Status", False),
            ("GET", "/api/v1/ingestion/jobs/history", 200, "Job History", False),
            ("POST", "/api/v1/ingestion/ingest/github.com/test/repo", 401, "Ingest Repo (no auth)", True),
        ]),
    ]
    
    # Run tests
    for category, category_tests in tests:
        print(f"\n{category}")
        print("-" * 80)
        
        for method, path, expected_status, description, auth_required in category_tests:
            success, message = test_endpoint(
                method, path, expected_status, description, auth_required=auth_required
            )
            
            # Record result
            test_result = {
                "category": category,
                "method": method,
                "path": path,
                "description": description,
                "success": success,
                "message": message
            }
            results["tests"].append(test_result)
            
            if success:
                results["passed"] += 1
                status = "✓"
            else:
                results["failed"] += 1
                status = "✗"
            
            print(f"  {status} {method:6} {path:50} {message}")
    
    # Summary
    print()
    print("=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"Total Tests: {results['passed'] + results['failed']}")
    print(f"Passed:      {results['passed']} ✓")
    print(f"Failed:      {results['failed']} ✗")
    print(f"Success Rate: {results['passed'] / (results['passed'] + results['failed']) * 100:.1f}%")
    print()
    
    # Module status
    print("Module Status:")
    print("-" * 80)
    
    modules_tested = {}
    for test in results["tests"]:
        category = test["category"]
        if category not in modules_tested:
            modules_tested[category] = {"passed": 0, "failed": 0}
        
        if test["success"]:
            modules_tested[category]["passed"] += 1
        else:
            modules_tested[category]["failed"] += 1
    
    for module, stats in modules_tested.items():
        total = stats["passed"] + stats["failed"]
        status = "✓" if stats["failed"] == 0 else "✗"
        print(f"  {status} {module:40} {stats['passed']}/{total} passed")
    
    print()
    print("=" * 80)
    print(f"Completed: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Return exit code
    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
