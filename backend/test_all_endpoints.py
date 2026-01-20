"""
Comprehensive API endpoint testing script.
Tests all critical endpoints with actual HTTP calls.
"""
import requests
import json
import time
from typing import Dict, Any, List, Optional
import sys

BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"
# Pre-generated token from create_test_user.py
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNzY4NTQzOTA4LCJ0eXBlIjoiYWNjZXNzIn0.xr8bSgjiO7WBmEsAsD8Acc7Gq8gOBoK-z_tYRDS01kg"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class EndpointTester:
    def __init__(self):
        self.token: Optional[str] = TEST_TOKEN  # Use pre-generated token
        self.test_resource_id: Optional[int] = None
        self.test_collection_id: Optional[int] = None
        self.test_annotation_id: Optional[int] = None
        self.results: List[Dict[str, Any]] = []
        
    def log(self, message: str, color: str = Colors.BLUE):
        print(f"{color}{message}{Colors.END}")
        
    def test_endpoint(self, name: str, method: str, endpoint: str, 
                     data: Optional[Dict] = None, 
                     expected_status: int = 200,
                     auth: bool = False) -> Optional[Dict]:
        """Test a single endpoint and record results."""
        url = f"{BASE_URL}{endpoint}"
        headers = {}
        
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=data)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            success = response.status_code == expected_status
            
            result = {
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "status": response.status_code,
                "expected": expected_status,
                "success": success,
                "response_time": response.elapsed.total_seconds()
            }
            
            if success:
                self.log(f"✓ {name}: {method} {endpoint} - {response.status_code}", Colors.GREEN)
                try:
                    result["data"] = response.json()
                except:
                    result["data"] = response.text
            else:
                self.log(f"✗ {name}: {method} {endpoint} - Expected {expected_status}, got {response.status_code}", Colors.RED)
                try:
                    result["error"] = response.json()
                except:
                    result["error"] = response.text
                    
            self.results.append(result)
            return result.get("data") if success else None
            
        except Exception as e:
            self.log(f"✗ {name}: {method} {endpoint} - Exception: {str(e)}", Colors.RED)
            self.results.append({
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "success": False,
                "error": str(e)
            })
            return None
    
    def run_all_tests(self):
        """Run comprehensive endpoint tests."""
        self.log("\n" + "="*80, Colors.BLUE)
        self.log("NEO ALEXANDRIA 2.0 - COMPREHENSIVE API ENDPOINT TEST", Colors.BLUE)
        self.log("="*80 + "\n", Colors.BLUE)
        
        # 1. Health & Monitoring
        self.log("\n[1] HEALTH & MONITORING ENDPOINTS", Colors.YELLOW)
        self.test_endpoint("Root Endpoint", "GET", "/")
        self.test_endpoint("API Docs", "GET", "/docs", expected_status=200)
        self.test_endpoint("OpenAPI Schema", "GET", "/openapi.json", expected_status=200)
        
        # 2. Authentication
        self.log("\n[2] AUTHENTICATION ENDPOINTS", Colors.YELLOW)
        
        # Get current user (using pre-generated token)
        self.test_endpoint("Get Current User", "GET", "/api/auth/me", auth=True)
        self.log(f"  → Using pre-generated token", Colors.GREEN)
        
        # 3. Resources
        self.log("\n[3] RESOURCE ENDPOINTS", Colors.YELLOW)
        
        # Create resource
        resource_data = {
            "title": "Test Resource",
            "url": "https://example.com/test",
            "content": "This is a test resource for API testing.",
            "resource_type": "article"
        }
        create_response = self.test_endpoint("Create Resource", "POST", 
                                            "/api/resources/", 
                                            data=resource_data, 
                                            auth=True, 
                                            expected_status=201)
        if create_response:
            self.test_resource_id = create_response.get("id")
            self.log(f"  → Resource created with ID: {self.test_resource_id}", Colors.GREEN)
        
        # List resources
        self.test_endpoint("List Resources", "GET", "/api/resources/", auth=True)
        
        # Get specific resource
        if self.test_resource_id:
            self.test_endpoint("Get Resource", "GET", 
                             f"/api/resources/{self.test_resource_id}", 
                             auth=True)
            
            # Update resource
            update_data = {
                "title": "Updated Test Resource",
                "content": "Updated content"
            }
            self.test_endpoint("Update Resource", "PUT", 
                             f"/api/resources/{self.test_resource_id}", 
                             data=update_data, 
                             auth=True)
        
        # 4. Search
        self.log("\n[4] SEARCH ENDPOINTS", Colors.YELLOW)
        
        # Keyword search
        self.test_endpoint("Keyword Search", "GET", "/api/search/", 
                          data={"q": "test", "search_type": "keyword"}, 
                          auth=True)
        
        # Semantic search
        self.test_endpoint("Semantic Search", "GET", "/api/search/", 
                          data={"q": "test resource", "search_type": "semantic"}, 
                          auth=True)
        
        # Hybrid search
        self.test_endpoint("Hybrid Search", "GET", "/api/search/", 
                          data={"q": "test", "search_type": "hybrid"}, 
                          auth=True)
        
        # 5. Collections
        self.log("\n[5] COLLECTION ENDPOINTS", Colors.YELLOW)
        
        # Create collection
        collection_data = {
            "name": "Test Collection",
            "description": "A test collection"
        }
        collection_response = self.test_endpoint("Create Collection", "POST", 
                                                 "/api/collections/", 
                                                 data=collection_data, 
                                                 auth=True, 
                                                 expected_status=201)
        if collection_response:
            self.test_collection_id = collection_response.get("id")
            self.log(f"  → Collection created with ID: {self.test_collection_id}", Colors.GREEN)
        
        # List collections
        self.test_endpoint("List Collections", "GET", "/api/collections/", auth=True)
        
        # Add resource to collection
        if self.test_collection_id and self.test_resource_id:
            self.test_endpoint("Add Resource to Collection", "POST", 
                             f"/api/collections/{self.test_collection_id}/resources/{self.test_resource_id}", 
                             auth=True)
        
        # 6. Annotations
        self.log("\n[6] ANNOTATION ENDPOINTS", Colors.YELLOW)
        
        if self.test_resource_id:
            # Create annotation
            annotation_data = {
                "resource_id": self.test_resource_id,
                "content": "This is a test annotation",
                "start_offset": 0,
                "end_offset": 10,
                "tags": ["test", "annotation"]
            }
            annotation_response = self.test_endpoint("Create Annotation", "POST", 
                                                     "/api/annotations/", 
                                                     data=annotation_data, 
                                                     auth=True, 
                                                     expected_status=201)
            if annotation_response:
                self.test_annotation_id = annotation_response.get("id")
                self.log(f"  → Annotation created with ID: {self.test_annotation_id}", Colors.GREEN)
            
            # List annotations for resource
            self.test_endpoint("List Resource Annotations", "GET", 
                             f"/api/annotations/?resource_id={self.test_resource_id}", 
                             auth=True)
        
        # 7. Taxonomy
        self.log("\n[7] TAXONOMY ENDPOINTS", Colors.YELLOW)
        
        # List categories
        self.test_endpoint("List Categories", "GET", "/api/taxonomy/categories", auth=True)
        
        # Get taxonomy tree
        self.test_endpoint("Get Taxonomy Tree", "GET", "/api/taxonomy/tree", auth=True)
        
        # 8. Quality
        self.log("\n[8] QUALITY ENDPOINTS", Colors.YELLOW)
        
        if self.test_resource_id:
            # Get quality score
            self.test_endpoint("Get Quality Score", "GET", 
                             f"/api/quality/resources/{self.test_resource_id}", 
                             auth=True)
        
        # 9. Recommendations
        self.log("\n[9] RECOMMENDATION ENDPOINTS", Colors.YELLOW)
        
        if self.test_resource_id:
            # Get recommendations
            self.test_endpoint("Get Recommendations", "GET", 
                             f"/api/recommendations/resources/{self.test_resource_id}", 
                             auth=True)
        
        # Get personalized recommendations
        self.test_endpoint("Get Personalized Recommendations", "GET", 
                          "/api/recommendations/personalized", 
                          auth=True)
        
        # 10. Graph
        self.log("\n[10] GRAPH ENDPOINTS", Colors.YELLOW)
        
        if self.test_resource_id:
            # Get citations
            self.test_endpoint("Get Citations", "GET", 
                             f"/api/graph/resources/{self.test_resource_id}/citations", 
                             auth=True)
            
            # Get related resources
            self.test_endpoint("Get Related Resources", "GET", 
                             f"/api/graph/resources/{self.test_resource_id}/related", 
                             auth=True)
        
        # 11. Curation
        self.log("\n[11] CURATION ENDPOINTS", Colors.YELLOW)
        
        # Get pending items
        self.test_endpoint("Get Pending Curation Items", "GET", 
                          "/api/curation/pending", 
                          auth=True)
        
        # 12. Scholarly
        self.log("\n[12] SCHOLARLY ENDPOINTS", Colors.YELLOW)
        
        if self.test_resource_id:
            # Get metadata
            self.test_endpoint("Get Scholarly Metadata", "GET", 
                             f"/api/scholarly/resources/{self.test_resource_id}/metadata", 
                             auth=True)
        
        # 13. Authority
        self.log("\n[13] AUTHORITY ENDPOINTS", Colors.YELLOW)
        
        # List authorities
        self.test_endpoint("List Authorities", "GET", "/api/authority/", auth=True)
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary."""
        self.log("\n" + "="*80, Colors.BLUE)
        self.log("TEST SUMMARY", Colors.BLUE)
        self.log("="*80, Colors.BLUE)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("success"))
        failed = total - passed
        
        self.log(f"\nTotal Tests: {total}", Colors.BLUE)
        self.log(f"Passed: {passed}", Colors.GREEN)
        self.log(f"Failed: {failed}", Colors.RED if failed > 0 else Colors.GREEN)
        self.log(f"Success Rate: {(passed/total*100):.1f}%", 
                Colors.GREEN if passed == total else Colors.YELLOW)
        
        if failed > 0:
            self.log("\nFailed Tests:", Colors.RED)
            for result in self.results:
                if not result.get("success"):
                    self.log(f"  - {result['name']}: {result['method']} {result['endpoint']}", Colors.RED)
                    if "error" in result:
                        self.log(f"    Error: {result['error']}", Colors.RED)
        
        # Performance stats
        response_times = [r.get("response_time", 0) for r in self.results if r.get("success")]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            self.log(f"\nPerformance:", Colors.BLUE)
            self.log(f"  Average Response Time: {avg_time*1000:.2f}ms", Colors.BLUE)
            self.log(f"  Max Response Time: {max_time*1000:.2f}ms", Colors.BLUE)
        
        self.log("\n" + "="*80 + "\n", Colors.BLUE)
        
        return failed == 0

if __name__ == "__main__":
    tester = EndpointTester()
    
    # Wait for server to be ready
    print("Waiting for server to start...")
    for i in range(30):
        try:
            # Try root endpoint or docs which don't require auth
            response = requests.get(f"{BASE_URL}/docs", timeout=1)
            if response.status_code in [200, 307]:  # 307 is redirect
                print("Server is ready!")
                break
        except Exception as e:
            if i % 5 == 0:
                print(f"  Attempt {i+1}/30... ({str(e)[:50]})")
        time.sleep(1)
    else:
        print("Server failed to start within 30 seconds")
        print("Trying to continue anyway...")
        # Don't exit, try to run tests anyway
    
    # Run tests
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
