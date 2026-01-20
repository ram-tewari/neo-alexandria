"""
Live endpoint testing - tests actual running server with proper authentication flow.
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log(msg, color=Colors.BLUE):
    print(f"{color}{msg}{Colors.END}")

def test_endpoint(name, method, url, headers=None, json_data=None, params=None, expected_status=200):
    """Test a single endpoint."""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=json_data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=json_data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        
        success = response.status_code == expected_status
        if success:
            log(f"✓ {name} - {response.status_code}", Colors.GREEN)
            try:
                return True, response.json()
            except:
                return True, response.text
        else:
            log(f"✗ {name} - Expected {expected_status}, got {response.status_code}", Colors.RED)
            try:
                log(f"  Error: {response.json()}", Colors.RED)
            except:
                log(f"  Error: {response.text[:100]}", Colors.RED)
            return False, None
    except Exception as e:
        log(f"✗ {name} - Exception: {str(e)}", Colors.RED)
        return False, None

def main():
    log("\n" + "="*80, Colors.BLUE)
    log("NEO ALEXANDRIA 2.0 - LIVE ENDPOINT TESTING", Colors.BLUE)
    log("="*80 + "\n", Colors.BLUE)
    
    passed = 0
    failed = 0
    token = None
    resource_id = None
    collection_id = None
    
    # Wait for server
    log("Waiting for server...", Colors.YELLOW)
    for i in range(30):
        try:
            response = requests.get(f"{BASE_URL}/docs", timeout=1)
            if response.status_code == 200:
                log("Server ready!\n", Colors.GREEN)
                break
        except:
            pass
        time.sleep(1)
    else:
        log("Server not ready after 30 seconds", Colors.RED)
        return False
    
    # Test 1: Public endpoints
    log("[1] PUBLIC ENDPOINTS", Colors.YELLOW)
    success, _ = test_endpoint("API Docs", "GET", f"{BASE_URL}/docs")
    passed += success
    failed += not success
    
    success, _ = test_endpoint("OpenAPI Schema", "GET", f"{BASE_URL}/openapi.json")
    passed += success
    failed += not success
    
    # Test 2: Authentication - Register (should work now with fixed middleware)
    log("\n[2] AUTHENTICATION", Colors.YELLOW)
    
    # Try to login with existing test user
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    success, data = test_endpoint(
        "Login Existing User",
        "POST",
        f"{BASE_URL}/auth/login",
        json_data=login_data
    )
        if success and data:
            token = data.get("access_token")
            log(f"  → Token acquired: {token[:30]}...", Colors.GREEN)
            passed += 1
        else:
            failed += 1
    
    if not token:
        log("\n✗ Cannot proceed without authentication token", Colors.RED)
        log(f"\nResults: {passed} passed, {failed} failed", Colors.YELLOW)
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 3: Get current user
    success, user_data = test_endpoint("Get Current User", "GET", f"{BASE_URL}/auth/me", headers=headers)
    passed += success
    failed += not success
    
    # Test 4: Resources
    log("\n[3] RESOURCES", Colors.YELLOW)
    
    # Create resource
    resource_data = {
        "title": "Test Resource for API Testing",
        "url": "https://example.com/test-resource",
        "content": "This is test content for comprehensive API testing.",
        "resource_type": "article"
    }
    success, data = test_endpoint(
        "Create Resource",
        "POST",
        f"{BASE_URL}/resources",
        headers=headers,
        json_data=resource_data,
        expected_status=201
    )
    passed += success
    failed += not success
    if success and data:
        resource_id = data.get("id")
        log(f"  → Resource ID: {resource_id}", Colors.GREEN)
    
    # List resources
    success, _ = test_endpoint("List Resources", "GET", f"{BASE_URL}/resources", headers=headers)
    passed += success
    failed += not success
    
    # Get specific resource
    if resource_id:
        success, _ = test_endpoint("Get Resource", "GET", f"{BASE_URL}/resources/{resource_id}", headers=headers)
        passed += success
        failed += not success
    
    # Test 5: Search
    log("\n[4] SEARCH", Colors.YELLOW)
    
    search_data = {"query": "test", "search_type": "keyword"}
    success, _ = test_endpoint(
        "Keyword Search",
        "POST",
        f"{BASE_URL}/search",
        headers=headers,
        json_data=search_data
    )
    passed += success
    failed += not success
    
    search_data = {"query": "test resource", "search_type": "semantic"}
    success, _ = test_endpoint(
        "Semantic Search",
        "POST",
        f"{BASE_URL}/search",
        headers=headers,
        json_data=search_data
    )
    passed += success
    failed += not success
    
    search_data = {"query": "test", "search_type": "hybrid"}
    success, _ = test_endpoint(
        "Hybrid Search",
        "POST",
        f"{BASE_URL}/search",
        headers=headers,
        json_data=search_data
    )
    passed += success
    failed += not success
    
    # Test 6: Collections
    log("\n[5] COLLECTIONS", Colors.YELLOW)
    
    collection_data = {
        "name": "Test Collection",
        "description": "Collection for API testing"
    }
    success, data = test_endpoint(
        "Create Collection",
        "POST",
        f"{BASE_URL}/collections",
        headers=headers,
        json_data=collection_data,
        expected_status=201
    )
    passed += success
    failed += not success
    if success and data:
        collection_id = data.get("id")
        log(f"  → Collection ID: {collection_id}", Colors.GREEN)
    
    success, _ = test_endpoint("List Collections", "GET", f"{BASE_URL}/collections", headers=headers)
    passed += success
    failed += not success
    
    # Test 7: Annotations
    log("\n[6] ANNOTATIONS", Colors.YELLOW)
    
    if resource_id:
        annotation_data = {
            "resource_id": resource_id,
            "content": "Test annotation",
            "start_offset": 0,
            "end_offset": 10,
            "tags": ["test"]
        }
        success, _ = test_endpoint(
            "Create Annotation",
            "POST",
            f"{BASE_URL}/resources/{resource_id}/annotations",
            headers=headers,
            json_data=annotation_data,
            expected_status=201
        )
        passed += success
        failed += not success
    
    # Test 8: Taxonomy
    log("\n[7] TAXONOMY", Colors.YELLOW)
    
    success, _ = test_endpoint("List Categories", "POST", f"{BASE_URL}/taxonomy/categories", headers=headers, json_data={})
    passed += success
    failed += not success
    
    # Test 9: Quality
    log("\n[8] QUALITY", Colors.YELLOW)
    
    if resource_id:
        success, _ = test_endpoint(
            "Get Quality Score",
            "GET",
            f"{BASE_URL}/resources/{resource_id}/quality-details",
            headers=headers
        )
        passed += success
        failed += not success
    
    # Test 10: Recommendations
    log("\n[9] RECOMMENDATIONS", Colors.YELLOW)
    
    success, _ = test_endpoint(
        "Get Personalized Recommendations",
        "GET",
        f"{BASE_URL}/recommendations",
        headers=headers
    )
    passed += success
    failed += not success
    
    if resource_id:
        success, _ = test_endpoint(
            "Get Resource Recommendations",
            "GET",
            f"{BASE_URL}/recommendations?resource_id={resource_id}",
            headers=headers
        )
        passed += success
        failed += not success
    
    # Test 11: Graph
    log("\n[10] GRAPH", Colors.YELLOW)
    
    if resource_id:
        success, _ = test_endpoint(
            "Get Citations",
            "GET",
            f"{BASE_URL}/citations/resources/{resource_id}/citations",
            headers=headers
        )
        passed += success
        failed += not success
        
        success, _ = test_endpoint(
            "Get Related Resources",
            "GET",
            f"{BASE_URL}/discovery/graph/resources/{resource_id}/neighbors",
            headers=headers
        )
        passed += success
        failed += not success
    
    # Test 12: Authority
    log("\n[11] AUTHORITY", Colors.YELLOW)
    
    success, _ = test_endpoint("Get Authority Tree", "GET", f"{BASE_URL}/authority/classification/tree", headers=headers)
    passed += success
    failed += not success
    
    # Test 13: Monitoring
    log("\n[12] MONITORING", Colors.YELLOW)
    
    success, _ = test_endpoint("Health Check", "GET", f"{BASE_URL}/api/monitoring/health", headers=headers)
    passed += success
    failed += not success
    
    success, _ = test_endpoint("System Metrics", "GET", f"{BASE_URL}/api/monitoring/performance", headers=headers)
    passed += success
    failed += not success
    
    # Summary
    log("\n" + "="*80, Colors.BLUE)
    log("TEST SUMMARY", Colors.BLUE)
    log("="*80, Colors.BLUE)
    log(f"\nTotal: {passed + failed} tests", Colors.BLUE)
    log(f"Passed: {passed}", Colors.GREEN)
    log(f"Failed: {failed}", Colors.RED if failed > 0 else Colors.GREEN)
    log(f"Success Rate: {(passed/(passed+failed)*100):.1f}%\n", Colors.GREEN if failed == 0 else Colors.YELLOW)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
