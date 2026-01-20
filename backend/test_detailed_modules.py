"""
Detailed Module Testing for Neo Alexandria 2.0
Tests all 13 modules with comprehensive endpoint coverage
"""

import requests
import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcl9pZCI6ImIzYjA3ZTMwLTk2ZWYtNGRmNi04MjAwLTY5YzBmM2VhOTM2MSIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJ0aWVyIjoicHJlbWl1bSIsInNjb3BlcyI6W10sImV4cCI6MTc2ODkyNTE2MSwidHlwZSI6ImFjY2VzcyJ9.jyV84j-iJSiSqAA-2IF31rlBepYkAmZtrd9PhhBGWlc"


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'


class DetailedModuleTester:
    def __init__(self):
        self.results = []
        self.test_data = {}
        self.latencies = []
        self.module_stats = {}
        
    def log(self, message: str, color: str = Colors.RESET):
        print(f"{color}{message}{Colors.RESET}")
    
    def request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                auth: bool = True, timeout: int = 30) -> requests.Response:
        """Make HTTP request"""
        url = f"{BASE_URL}{endpoint}"
        headers = {}
        if auth:
            headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
        
        start = time.time()
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            resp = requests.post(url, json=data, headers=headers, timeout=timeout)
        elif method == "PUT":
            resp = requests.put(url, json=data, headers=headers, timeout=timeout)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        latency = (time.time() - start) * 1000
        self.latencies.append(latency)
        return resp
    
    def test(self, module: str, name: str, method: str, endpoint: str, 
             data: Optional[Dict] = None, expected_status: int = 200,
             auth: bool = True) -> tuple[bool, Optional[Dict]]:
        """Test an endpoint"""
        try:
            resp = self.request(method, endpoint, data, auth)
            success = resp.status_code == expected_status
            
            result = {
                "module": module,
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "status": resp.status_code,
                "expected": expected_status,
                "latency_ms": round(self.latencies[-1], 2),
                "success": success
            }
            
            if success:
                self.log(f"  [OK] {name} ({int(self.latencies[-1])}ms)", Colors.GREEN)
                self.results.append(result)
                try:
                    return True, resp.json()
                except:
                    return True, None
            else:
                self.log(f"  [FAIL] {name} - Expected {expected_status}, got {resp.status_code}", Colors.RED)
                try:
                    error = resp.json()
                    self.log(f"    Error: {error.get('detail', error)}", Colors.YELLOW)
                    result["error"] = error
                except:
                    result["error"] = resp.text[:200]
                self.results.append(result)
                return False, None
                
        except Exception as e:
            self.log(f"  [ERROR] {name} - Exception: {str(e)[:100]}", Colors.RED)
            self.results.append({
                "module": module,
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "success": False,
                "error": str(e)
            })
            return False, None
    
    def test_monitoring_module(self):
        """Test Monitoring Module (12+ endpoints)"""
        self.log("\n" + "="*80, Colors.CYAN)
        self.log("MODULE 1: MONITORING & OBSERVABILITY", Colors.CYAN)
        self.log("="*80, Colors.CYAN)
        
        module = "monitoring"
        
        # Health checks
        self.test(module, "Health Check", "GET", "/api/monitoring/health")
        self.test(module, "Module Health", "GET", "/api/monitoring/health/module/resources")
        self.test(module, "ML Model Health", "GET", "/api/monitoring/health/ml")
        
        # Performance metrics
        self.test(module, "Performance Metrics", "GET", "/api/monitoring/performance")
        self.test(module, "Database Metrics", "GET", "/api/monitoring/database")
        self.test(module, "DB Pool Status", "GET", "/api/monitoring/db/pool")
        
        # Event system
        self.test(module, "Event Bus Metrics", "GET", "/api/monitoring/events")
        self.test(module, "Event History", "GET", "/api/monitoring/events/history?limit=10")
        
        # Cache and workers
        self.test(module, "Cache Stats", "GET", "/api/monitoring/cache/stats")
        self.test(module, "Worker Status", "GET", "/api/monitoring/workers/status")
        
        # Quality metrics
        self.test(module, "Recommendation Quality", "GET", "/api/monitoring/recommendation-quality?time_window_days=7")
        self.test(module, "User Engagement", "GET", "/api/monitoring/user-engagement?time_window_days=7")
        self.test(module, "Model Health", "GET", "/api/monitoring/model-health")
    
    def test_auth_module(self):
        """Test Auth Module"""
        self.log("\n" + "="*80, Colors.CYAN)
        self.log("MODULE 2: AUTHENTICATION & AUTHORIZATION", Colors.CYAN)
        self.log("="*80, Colors.CYAN)
        
        module = "auth"
        
        self.test(module, "Get Current User", "GET", "/auth/me")
        self.test(module, "Health Check", "GET", "/auth/health")
    
    def test_resources_module(self):
        """Test Resources Module (10+ endpoints)"""
        self.log("\n" + "="*80, Colors.CYAN)
        self.log("MODULE 3: RESOURCES (CRUD & INGESTION)", Colors.CYAN)
        self.log("="*80, Colors.CYAN)
        
        module = "resources"
        
        # Health check
        self.test(module, "Health Check", "GET", "/resources/health")
        
        # Create resource
        resource_data = {
            "title": "Detailed Test Resource",
            "url": "https://example.com/detailed-test",
            "content": "This is a comprehensive test resource with detailed content for testing all features including search, classification, and recommendations.",
            "resource_type": "article",
            "tags": ["test", "comprehensive", "detailed", "machine-learning"]
        }
        success, data = self.test(module, "Create Resource", "POST", "/resources/", 
                                  data=resource_data, expected_status=201)
        if success and data:
            self.test_data["resource_id"] = data.get("id")
            self.log(f"    → Resource ID: {self.test_data['resource_id']}", Colors.CYAN)
        
        # List and retrieve
        self.test(module, "List Resources", "GET", "/resources/")
        self.test(module, "List with Pagination", "GET", "/resources/?skip=0&limit=5")
        
        if self.test_data.get("resource_id"):
            rid = self.test_data["resource_id"]
            self.test(module, "Get Resource by ID", "GET", f"/resources/{rid}")
            self.test(module, "Get Resource Status", "GET", f"/resources/{rid}/status")
            self.test(module, "Get Resource Chunks", "GET", f"/resources/{rid}/chunks")
            
            # Update resource
            update_data = {"tags": ["test", "updated"]}
            self.test(module, "Update Resource", "PUT", f"/resources/{rid}", data=update_data)
    
    def test_search_module(self):
        """Test Search Module (6+ endpoints)"""
        self.log("\n" + "="*80, Colors.CYAN)
        self.log("MODULE 4: SEARCH (HYBRID, SEMANTIC, KEYWORD)", Colors.CYAN)
        self.log("="*80, Colors.CYAN)
        
        module = "search"
        
        # Health check
        self.test(module, "Health Check", "GET", "/search/health")
        
        # Different search types
        self.test(module, "Basic Search", "POST", "/search/", 
                 data={"query": "machine learning", "search_type": "keyword"})
        self.test(module, "Keyword Search", "POST", "/search/", 
                 data={"query": "test resource", "search_type": "keyword", "limit": 5})
        self.test(module, "Semantic Search", "POST", "/search/", 
                 data={"query": "artificial intelligence", "search_type": "semantic", "limit": 5})
        self.test(module, "Hybrid Search", "POST", "/search/", 
                 data={"query": "machine learning", "search_type": "hybrid", "limit": 5})
        
        # Advanced search
        self.test(module, "Three-Way Hybrid", "POST", "/search/three-way-hybrid", 
                 data={"query": "test", "limit": 5})
        self.test(module, "Advanced Search", "POST", "/search/advanced", 
                 data={"query": "test", "filters": {}})
        
        # Evaluation
        self.test(module, "Compare Methods", "POST", "/search/compare-methods", 
                 data={"query": "test", "limit": 5})
        self.test(module, "Evaluate Search", "POST", "/search/evaluate", 
                 data={"query": "test", "relevant_ids": []})
    
    def test_collections_module(self):
        """Test Collections Module (8+ endpoints)"""
        self.log("\n" + "="*80, Colors.CYAN)
        self.log("MODULE 5: COLLECTIONS & ORGANIZATION", Colors.CYAN)
        self.log("="*80, Colors.CYAN)
        
        module = "collections"
        
        # Health check
        self.test(module, "Health Check", "GET", "/collections/health")
        
        # Create collection
        collection_data = {
            "name": "Test Collection",
            "description": "A comprehensive test collection"
        }
        success, data = self.test(module, "Create Collection", "POST", "/collections/", 
                                  data=collection_data, expected_status=201)
        if success and data:
            self.test_data["collection_id"] = data.get("id")
            self.log(f"    → Collection ID: {self.test_data['collection_id']}", Colors.CYAN)
        
        # List collections
        self.test(module, "List Collections", "GET", "/collections/")
        
        if self.test_data.get("collection_id"):
            cid = self.test_data["collection_id"]
            self.test(module, "Get Collection", "GET", f"/collections/{cid}")
            self.test(module, "Get Collection Resources", "GET", f"/collections/{cid}/resources")
            self.test(module, "Get Collection Recommendations", "GET", f"/collections/{cid}/recommendations")
            self.test(module, "Get Similar Collections", "GET", f"/collections/{cid}/similar-collections")
            
            # Add resource to collection
            if self.test_data.get("resource_id"):
                rid = self.test_data["resource_id"]
                self.test(module, "Add Resource to Collection", "POST", 
                         f"/collections/{cid}/resources", data={"resource_id": rid})
    
    def test_annotations_module(self):
        """Test Annotations Module (6+ endpoints)"""
        self.log("\n" + "="*80, Colors.CYAN)
        self.log("MODULE 6: ANNOTATIONS & HIGHLIGHTS", Colors.CYAN)
        self.log("="*80, Colors.CYAN)
        
        module = "annotations"
        
        if self.test_data.get("resource_id"):
            rid = self.test_data["resource_id"]
            
            # Create annotation
            annotation_data = {
                "resource_id": rid,
                "highlighted_text": "machine learning",
                "note": "Important concept",
                "tags": ["ml", "important"]
            }
            success, data = self.test(module, "Create Annotation", "POST", 
                                     f"/resources/{rid}/annotations", 
                                     data=annotation_data, expected_status=201)
            if success and data:
                self.test_data["annotation_id"] = data.get("id")
            
            # List annotations
            self.test(module, "List Annotations", "GET", f"/resources/{rid}/annotations")
            
            # Search annotations
            self.test(module, "Fulltext Search", "GET", "/annotations/search/fulltext?q=machine")
            self.test(module, "Semantic Search", "POST", "/annotations/search/semantic", 
                     data={"query": "machine learning"})
            self.test(module, "Search by Tags", "GET", "/annotations/search/tags?tags=ml")
    
    def test_taxonomy_module(self):
        """Test Taxonomy Module (4+ endpoints)"""
        self.log("\n" + "="*80, Colors.CYAN)
        self.log("MODULE 7: TAXONOMY & CLASSIFICATION", Colors.CYAN)
        self.log("="*80, Colors.CYAN)
        
        module = "taxonomy"
        
        # List and tree
        self.test(module, "List All Categories", "POST", "/taxonomy/categories", data={})
        self.test(module, "Get Taxonomy Tree", "POST", "/taxonomy/tree", data={})
        
        # Classification
        if self.test_data.get("resource_id"):
            rid = self.test_data["resource_id"]
            self.test(module, "Classify Resource", "POST", f"/resources/{rid}/classify", data={})
    
    def test_quality_module(self):
        """Test Quality Module (4+ endpoints)"""
        self.log("\n" + "="*80, Colors.CYAN)
        self.log("MODULE 8: QUALITY ASSESSMENT", Colors.CYAN)
        self.log("="*80, Colors.CYAN)
        
        module = "quality"
        
        self.test(module, "List Quality Outliers", "POST", "/quality/outliers", data={})
        
        if self.test_data.get("resource_id"):
            rid = self.test_data["resource_id"]
            self.test(module, "Get Resource Quality", "GET", f"/quality/resource/{rid}")
    
    def test_recommendations_module(self):
        """Test Recommendations Module (5+ endpoints)"""
        self.log("\n" + "="*80, Colors.CYAN)
        self.log("MODULE 9: RECOMMENDATIONS (NCF, CONTENT, GRAPH)", Colors.CYAN)
        self.log("="*80, Colors.CYAN)
        
        module = "recommendations"
        
        self.test(module, "Get Personalized Recommendations", "GET", "/recommendations/personalized?limit=5")
        
        if self.test_data.get("resource_id"):
            rid = self.test_data["resource_id"]
            self.test(module, "Get Similar Resources", "GET", f"/recommendations/similar/{rid}?limit=5")
    
    def test_graph_module(self):
        """Test Graph Module (6+ endpoints)"""
        self.log("\n" + "="*80, Colors.CYAN)
        self.log("MODULE 10: KNOWLEDGE GRAPH & CITATIONS", Colors.CYAN)
        self.log("="*80, Colors.CYAN)
        
        module = "graph"
        
        # List entities and relationships
        self.test(module, "List Entities", "GET", "/api/graph/entities?limit=10")
        self.test(module, "List Relationships", "GET", "/api/graph/relationships?limit=10")
        self.test(module, "Get Graph Stats", "GET", "/api/graph/stats")
        
        # Search
        self.test(module, "Search Entities", "GET", "/api/graph/entities/search?query=test")
        
        if self.test_data.get("resource_id"):
            rid = self.test_data["resource_id"]
            self.test(module, "Extract Graph from Resource", "POST", f"/api/graph/extract/{rid}", data={})
    
    def test_scholarly_module(self):
        """Test Scholarly Module (3+ endpoints)"""
        self.log("\n" + "="*80, Colors.CYAN)
        self.log("MODULE 11: SCHOLARLY METADATA EXTRACTION", Colors.CYAN)
        self.log("="*80, Colors.CYAN)
        
        module = "scholarly"
        
        # Extract metadata
        self.test(module, "Extract Metadata", "POST", "/scholarly/extract", 
                 data={"text": "This is a sample academic text with equations and citations."})
        
        if self.test_data.get("resource_id"):
            rid = self.test_data["resource_id"]
            self.test(module, "Get Resource Metadata", "GET", f"/scholarly/resource/{rid}")
    
    def test_curation_module(self):
        """Test Curation Module (4+ endpoints)"""
        self.log("\n" + "="*80, Colors.CYAN)
        self.log("MODULE 12: CURATION & REVIEW", Colors.CYAN)
        self.log("="*80, Colors.CYAN)
        
        module = "curation"
        
        self.test(module, "Get Pending Items", "GET", "/curation/pending")
        self.test(module, "Get Curation Queue", "GET", "/curation/queue?limit=10")
        
        if self.test_data.get("resource_id"):
            rid = self.test_data["resource_id"]
            review_data = {
                "resource_id": rid,
                "status": "approved",
                "notes": "Test review"
            }
            self.test(module, "Submit Review", "POST", "/curation/review", data=review_data)
    
    def test_authority_module(self):
        """Test Authority Module (4+ endpoints)"""
        self.log("\n" + "="*80, Colors.CYAN)
        self.log("MODULE 13: AUTHORITY CONTROL", Colors.CYAN)
        self.log("="*80, Colors.CYAN)
        
        module = "authority"
        
        self.test(module, "List Authorities", "GET", "/authority/?limit=10")
        self.test(module, "Search Subjects", "GET", "/authority/subjects/search?query=test")
        self.test(module, "Search Creators", "GET", "/authority/creators/search?query=test")
        self.test(module, "Search Publishers", "GET", "/authority/publishers/search?query=test")
    
    def run_all_tests(self):
        """Run all module tests"""
        self.log("\n" + "="*80, Colors.MAGENTA)
        self.log("NEO ALEXANDRIA 2.0 - DETAILED MODULE TESTING", Colors.MAGENTA)
        self.log("="*80 + "\n", Colors.MAGENTA)
        
        start_time = time.time()
        
        # Test all modules
        self.test_monitoring_module()
        time.sleep(0.5)
        self.test_auth_module()
        time.sleep(0.5)
        self.test_resources_module()
        time.sleep(0.5)
        self.test_search_module()
        time.sleep(0.5)
        self.test_collections_module()
        time.sleep(0.5)
        self.test_annotations_module()
        time.sleep(0.5)
        self.test_taxonomy_module()
        time.sleep(0.5)
        self.test_quality_module()
        time.sleep(0.5)
        self.test_recommendations_module()
        time.sleep(0.5)
        self.test_graph_module()
        time.sleep(0.5)
        self.test_scholarly_module()
        time.sleep(0.5)
        self.test_curation_module()
        time.sleep(0.5)
        self.test_authority_module()
        
        total_time = time.time() - start_time
        
        # Print summary
        self.print_summary(total_time)
    
    def print_summary(self, total_time: float):
        """Print comprehensive test summary"""
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
        self.log(f"Total Time: {total_time:.1f}s", Colors.CYAN)
        
        # Performance metrics
        if self.latencies:
            avg_latency = sum(self.latencies) / len(self.latencies)
            p50_latency = sorted(self.latencies)[int(len(self.latencies) * 0.50)]
            p95_latency = sorted(self.latencies)[int(len(self.latencies) * 0.95)]
            p99_latency = sorted(self.latencies)[int(len(self.latencies) * 0.99)]
            
            self.log(f"\nPerformance Metrics:", Colors.CYAN)
            self.log(f"  Average Latency: {avg_latency:.0f}ms", Colors.CYAN)
            self.log(f"  P50 Latency: {p50_latency:.0f}ms", Colors.CYAN)
            self.log(f"  P95 Latency: {p95_latency:.0f}ms", Colors.CYAN)
            self.log(f"  P99 Latency: {p99_latency:.0f}ms", Colors.CYAN)
            
            if p95_latency < 200:
                self.log(f"  [OK] Performance: EXCELLENT (P95 < 200ms)", Colors.GREEN)
            elif p95_latency < 500:
                self.log(f"  [OK] Performance: GOOD (P95 < 500ms)", Colors.YELLOW)
            else:
                self.log(f"  [FAIL] Performance: NEEDS IMPROVEMENT (P95 > 500ms)", Colors.RED)
        
        # Module breakdown
        module_stats = {}
        for r in self.results:
            module = r.get("module", "unknown")
            if module not in module_stats:
                module_stats[module] = {"total": 0, "passed": 0, "latencies": []}
            module_stats[module]["total"] += 1
            if r["success"]:
                module_stats[module]["passed"] += 1
            if "latency_ms" in r:
                module_stats[module]["latencies"].append(r["latency_ms"])
        
        self.log(f"\nModule Breakdown:", Colors.CYAN)
        for module, stats in sorted(module_stats.items()):
            rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            avg_lat = sum(stats["latencies"]) / len(stats["latencies"]) if stats["latencies"] else 0
            color = Colors.GREEN if rate >= 80 else Colors.YELLOW if rate >= 50 else Colors.RED
            self.log(f"  {module:20s}: {stats['passed']:2d}/{stats['total']:2d} passed ({rate:5.1f}%) - Avg: {avg_lat:5.0f}ms", color)
        
        # Failed tests
        failed_tests = [r for r in self.results if not r["success"]]
        if failed_tests:
            self.log(f"\nFailed Tests ({len(failed_tests)}):", Colors.RED)
            for test in failed_tests[:20]:  # Show first 20
                self.log(f"  • {test.get('module', 'unknown')}: {test['name']}", Colors.RED)
                if "error" in test:
                    error_msg = str(test['error'])[:100]
                    self.log(f"    {error_msg}", Colors.YELLOW)
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_detailed_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "total": total,
                "passed": passed,
                "failed": failed,
                "success_rate": success_rate,
                "total_time": total_time,
                "module_stats": module_stats,
                "results": self.results
            }, f, indent=2)
        self.log(f"\nResults saved to: {filename}", Colors.CYAN)


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
    
    tester = DetailedModuleTester()
    tester.run_all_tests()
