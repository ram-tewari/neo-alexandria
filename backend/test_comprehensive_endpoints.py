"""
Comprehensive endpoint testing for Neo Alexandria 2.0
Tests all 13 modules with proper authentication
"""

import requests
import time
from typing import Dict, Any, Optional, Tuple

# Test configuration
BASE_URL = "http://localhost:8000"
# Updated token with user_id field
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcl9pZCI6ImIzYjA3ZTMwLTk2ZWYtNGRmNi04MjAwLTY5YzBmM2VhOTM2MSIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJ0aWVyIjoicHJlbWl1bSIsInNjb3BlcyI6W10sImV4cCI6MTc2ODkyNTE2MSwidHlwZSI6ImFjY2VzcyJ9.jyV84j-iJSiSqAA-2IF31rlBepYkAmZtrd9PhhBGWlc"


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'


class EndpointTester:
    def __init__(self):
        self.results = []
        self.test_data = {}
        self.latencies = []
        
    def log(self, message: str, color: str = Colors.RESET):
        print(f"{color}{message}{Colors.RESET}")
    
    def test(self, name: str, method: str, endpoint: str, 
             data: Optional[Dict] = None, expected_status: int = 200,
             auth: bool = True) -> Tuple[bool, Optional[Dict]]:
        """
        Test an endpoint and return (success, response_data)
        """
        url = f"{BASE_URL}{endpoint}"
        headers = {}
        
        if auth:
            headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
        
        try:
            start = time.time()
            
            if method == "GET":
                resp = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                resp = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == "PUT":
                resp = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == "DELETE":
                resp = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            latency = (time.time() - start) * 1000
            self.latencies.append(latency)
            
            result = {
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "status": resp.status_code,
                "expected": expected_status,
                "latency_ms": round(latency, 2),
                "success": resp.status_code == expected_status
            }
            
            if resp.status_code == expected_status:
                self.log(f"  [OK] {name} ({int(latency)}ms)", Colors.GREEN)
                self.results.append(result)
                try:
                    return True, resp.json()
                except:
                    return True, None
            else:
                self.log(f"  [FAIL] {name} - Expected {expected_status}, got {resp.status_code}", Colors.RED)
                try:
                    error = resp.json()
                    self.log(f"    Error: {error.get('detail', error)}", Colors.RED)
                    result["error"] = error
                except:
                    result["error"] = resp.text[:200]
                self.results.append(result)
                return False, None
                
        except Exception as e:
            self.log(f"  [ERROR] {name} - Exception: {str(e)}", Colors.RED)
            self.results.append({
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "success": False,
                "error": str(e)
            })
            return False, None
    
    def run_all_tests(self):
        """Run comprehensive tests across all 13 modules"""
        self.log("\n" + "="*80, Colors.CYAN)
        self.log("NEO ALEXANDRIA 2.0 - COMPREHENSIVE ENDPOINT TEST SUITE", Colors.CYAN)
        self.log("="*80 + "\n", Colors.CYAN)
        
        # Add small delay between tests to avoid overwhelming the server
        import time as time_module
        def delay():
            time_module.sleep(0.5)
        
        # Module 1: Monitoring & Health (has /api prefix)
        self.log("[1/13] MONITORING MODULE", Colors.MAGENTA)
        self.test("Health Check", "GET", "/api/monitoring/health")
        delay()
        self.test("Performance Stats", "GET", "/api/monitoring/performance")
        delay()
        
        # Module 2: Auth
        self.log("\n[2/13] AUTH MODULE", Colors.MAGENTA)
        self.test("Get Current User", "GET", "/auth/me")
        delay()
        
        # Module 3: Resources
        self.log("\n[3/13] RESOURCES MODULE", Colors.MAGENTA)
        resource_data = {
            "title": "Comprehensive Test Resource",
            "url": "https://example.com/comprehensive-test",
            "content": "This is a comprehensive test resource.",
            "resource_type": "article",
            "tags": ["test", "comprehensive"]
        }
        success, data = self.test("Create Resource", "POST", "/resources/", 
                                  data=resource_data, expected_status=201)
        if success and data:
            self.test_data["resource_id"] = data.get("id")
            self.log(f"    -> Resource ID: {self.test_data['resource_id']}", Colors.CYAN)
        delay()
        
        self.test("List Resources", "GET", "/resources/")
        delay()
        self.test("List Resources with Pagination", "GET", "/resources/?skip=0&limit=10")
        delay()
        
        # Module 4: Search
        self.log("\n[4/13] SEARCH MODULE", Colors.MAGENTA)
        self.test("Keyword Search", "GET", "/search/?q=test&search_type=keyword")
        delay()
        self.test("Semantic Search", "GET", "/search/?q=comprehensive&search_type=semantic")
        delay()
        self.test("Hybrid Search", "GET", "/search/?q=test&search_type=hybrid")
        delay()
        
        # Module 5: Collections
        self.log("\n[5/13] COLLECTIONS MODULE", Colors.MAGENTA)
        collection_data = {
            "name": "Test Collection",
            "description": "A test collection"
        }
        success, data = self.test("Create Collection", "POST", "/collections/", 
                                  data=collection_data, expected_status=201)
        if success and data:
            self.test_data["collection_id"] = data.get("id")
        delay()
        
        self.test("List Collections", "GET", "/collections/")
        delay()
        
        # Module 6: Annotations
        self.log("\n[6/13] ANNOTATIONS MODULE", Colors.MAGENTA)
        if self.test_data.get("resource_id"):
            self.test("List Annotations", "GET", f"/resources/{self.test_data['resource_id']}/annotations")
            delay()
        
        # Module 7: Taxonomy
        self.log("\n[7/13] TAXONOMY MODULE", Colors.MAGENTA)
        self.test("List Categories", "GET", "/taxonomy/categories")
        delay()
        self.test("Get Taxonomy Tree", "GET", "/taxonomy/tree")
        delay()
        
        # Module 8: Quality
        self.log("\n[8/13] QUALITY MODULE", Colors.MAGENTA)
        self.test("List Quality Outliers", "GET", "/quality/outliers")
        delay()
        
        # Module 9: Recommendations
        self.log("\n[9/13] RECOMMENDATIONS MODULE", Colors.MAGENTA)
        self.test("Get Personalized Recommendations", "GET", "/recommendations/personalized")
        delay()
        
        # Module 10: Graph (has /api prefix)
        self.log("\n[10/13] GRAPH MODULE", Colors.MAGENTA)
        self.test("List Entities", "GET", "/api/graph/entities")
        delay()
        self.test("List Relationships", "GET", "/api/graph/relationships")
        delay()
        
        # Module 11: Scholarly
        self.log("\n[11/13] SCHOLARLY MODULE", Colors.MAGENTA)
        self.test("Extract Metadata", "POST", "/scholarly/extract", 
                 data={"text": "Sample academic text"})
        delay()
        
        # Module 12: Curation
        self.log("\n[12/13] CURATION MODULE", Colors.MAGENTA)
        self.test("Get Pending Items", "GET", "/curation/pending")
        delay()
        self.test("Get Curation Queue", "GET", "/curation/queue")
        delay()
        
        # Module 13: Authority
        self.log("\n[13/13] AUTHORITY MODULE", Colors.MAGENTA)
        self.test("List Authorities", "GET", "/authority/")
        delay()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "="*80, Colors.CYAN)
        self.log("TEST SUMMARY", Colors.CYAN)
        self.log("="*80, Colors.CYAN)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        self.log(f"\nTotal Tests: {total}", Colors.CYAN)
        self.log(f"Passed: {passed}", Colors.GREEN)
        self.log(f"Failed: {failed}", Colors.RED)
        self.log(f"Success Rate: {success_rate:.1f}%", 
                Colors.GREEN if success_rate >= 80 else Colors.YELLOW if success_rate >= 50 else Colors.RED)
        
        # Performance metrics
        if self.latencies:
            avg_latency = sum(self.latencies) / len(self.latencies)
            p95_latency = sorted(self.latencies)[int(len(self.latencies) * 0.95)]
            self.log(f"\nPerformance Metrics:", Colors.CYAN)
            self.log(f"  Average Latency: {avg_latency:.0f}ms", Colors.CYAN)
            self.log(f"  P95 Latency: {p95_latency:.0f}ms", Colors.CYAN)
            
            if p95_latency < 200:
                self.log(f"  [OK] Performance: EXCELLENT (P95 < 200ms)", Colors.GREEN)
            elif p95_latency < 500:
                self.log(f"  [OK] Performance: GOOD (P95 < 500ms)", Colors.YELLOW)
            else:
                self.log(f"  [FAIL] Performance: NEEDS IMPROVEMENT (P95 > 500ms)", Colors.RED)
        
        # Failed tests
        failed_tests = [r for r in self.results if not r["success"]]
        if failed_tests:
            self.log(f"\nFailed Tests ({len(failed_tests)}):", Colors.RED)
            for test in failed_tests:
                self.log(f"  • {test['name']}: {test['method']} {test['endpoint']}", Colors.RED)
                if "error" in test:
                    error_msg = str(test['error'])[:100]
                    self.log(f"    {error_msg}", Colors.YELLOW)
        
        # Module breakdown
        module_stats = {}
        for r in self.results:
            # Extract module from endpoint
            parts = r['endpoint'].strip('/').split('/')
            if parts[0] == 'api' and len(parts) > 1:
                module = parts[1]
            else:
                module = parts[0] if parts else 'unknown'
            
            if module not in module_stats:
                module_stats[module] = {"total": 0, "passed": 0}
            module_stats[module]["total"] += 1
            if r["success"]:
                module_stats[module]["passed"] += 1
        
        self.log(f"\nModule Breakdown:", Colors.CYAN)
        for module, stats in sorted(module_stats.items()):
            rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            color = Colors.GREEN if rate >= 80 else Colors.YELLOW if rate >= 50 else Colors.RED
            self.log(f"  {module:20s}: {stats['passed']:2d}/{stats['total']:2d} passed ({rate:.0f}%)", color)


def check_server():
    """Check if server is running"""
    try:
        resp = requests.get(f"{BASE_URL}/docs", timeout=5)
        if resp.status_code == 200:
            print(f"{Colors.GREEN}[OK] Server is ready!{Colors.RESET}")
            return True
    except:
        pass
    
    print(f"{Colors.RED}[ERROR] Server is not running at {BASE_URL}{Colors.RESET}")
    print(f"{Colors.YELLOW}Please start the server with: uvicorn app.main:app --reload{Colors.RESET}")
    return False


if __name__ == "__main__":
    if not check_server():
        exit(1)
    
    tester = EndpointTester()
    tester.run_all_tests()
