"""
Monitoring Module Health Check Integration Tests

Tests the health check endpoints for all modules in the system.
Verifies that each module's health endpoint returns 200 OK and
follows the expected response format.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_module_health_endpoints(client: TestClient, db_session: Session):
    """
    Test that all module health endpoints return 200 OK.
    
    This integration test verifies that each of the 12 modules in the system
    has a functioning health check endpoint that returns a successful response.
    
    Modules tested:
    - annotations
    - authority
    - collections
    - curation
    - graph
    - quality
    - recommendations
    - resources
    - scholarly
    - search
    - taxonomy
    - monitoring (self-check)
    
    Verifies:
    - HTTP 200 response for each module
    - Response contains 'status' field
    - Status is 'healthy' or 'ok'
    """
    # List of all modules in the system
    modules = [
        "annotations",
        "authority",
        "collections",
        "curation",
        "graph",
        "quality",
        "recommendations",
        "resources",
        "scholarly",
        "search",
        "taxonomy",
        "monitoring",
    ]
    
    failed_modules = []
    
    for module_name in modules:
        # Make health check request
        response = client.get(f"/api/monitoring/health/module/{module_name}")
        
        # Verify HTTP 200 response
        if response.status_code != 200:
            failed_modules.append({
                "module": module_name,
                "status_code": response.status_code,
                "reason": f"Expected 200, got {response.status_code}"
            })
            continue
        
        # Verify response format
        response_data = response.json()
        
        # Check that response contains 'status' field
        if "status" not in response_data:
            failed_modules.append({
                "module": module_name,
                "status_code": response.status_code,
                "reason": "Response missing 'status' field"
            })
            continue
        
        # Verify status is healthy
        status = response_data["status"]
        if status not in ["healthy", "ok", "available"]:
            failed_modules.append({
                "module": module_name,
                "status_code": response.status_code,
                "reason": f"Unexpected status: {status}"
            })
    
    # Assert all modules passed
    assert len(failed_modules) == 0, (
        f"IMPLEMENTATION FAILURE: {len(failed_modules)} module(s) failed health check\n"
        f"DO NOT UPDATE THE TEST - Fix the module health endpoints instead.\n"
        f"\n"
        f"Failed modules:\n"
        + "\n".join([
            f"  - {m['module']}: {m['reason']} (status code: {m['status_code']})"
            for m in failed_modules
        ])
    )


def test_overall_health_check(client: TestClient, db_session: Session):
    """
    Test the overall system health check endpoint.
    
    Verifies:
    - HTTP 200 response
    - Response contains 'status' field
    - Response contains system-level health information
    """
    # Make overall health check request
    response = client.get("/api/monitoring/health")
    
    # Verify HTTP 200 response
    assert response.status_code == 200, (
        f"IMPLEMENTATION FAILURE: Expected status 200, got {response.status_code}\n"
        f"DO NOT UPDATE THE TEST - Fix the health check endpoint instead."
    )
    
    # Verify response format
    response_data = response.json()
    
    # Check that response contains 'status' field
    assert "status" in response_data, (
        f"IMPLEMENTATION FAILURE: Response missing 'status' field\n"
        f"DO NOT UPDATE THE TEST - Fix the health check endpoint instead.\n"
        f"Response: {response_data}"
    )
    
    # Verify status is healthy
    status = response_data["status"]
    assert status in ["healthy", "ok"], (
        f"IMPLEMENTATION FAILURE: Unexpected status: {status}\n"
        f"DO NOT UPDATE THE TEST - Fix the health check endpoint instead."
    )
