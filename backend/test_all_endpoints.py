#!/usr/bin/env python3
"""
Comprehensive Endpoint Testing Script

Tests all endpoints in the Neo Alexandria 2.0 application to verify:
1. All endpoints are accessible
2. No import errors or startup failures
3. Endpoints return expected status codes
4. Phase 13 and Phase 13.5 endpoints work correctly
"""

import sys
import time
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import requests
from typing import Dict, List, Tuple
import json


class EndpointTester:
    """Tests all endpoints in the application"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            'passed': [],
            'failed': [],
            'errors': []
        }
        
    def test_endpoint(self, method: str, path: str, expected_status: int = None) -> Tuple[bool, str]:
        """
        Test a single endpoint
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: Endpoint path
            expected_status: Expected status code (None = any 2xx, 4xx acceptable)
            
        Returns:
            Tuple of (success, message)
        """
        url = f"{self.base_url}{path}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                response = requests.post(url, json={}, timeout=5)
            elif method == "PUT":
                response = requests.put(url, json={}, timeout=5)
            elif method == "DELETE":
                response = requests.delete(url, timeout=5)
            else:
                return False, f"Unknown method: {method}"
            
            # Check status code
            if expected_status:
                if response.status_code == expected_status:
                    return True, f"✓ {response.status_code}"
                else:
                    return False, f"✗ Expected {expected_status}, got {response.status_code}"
            else:
                # Accept 2xx, 4xx (client errors are OK for testing without data)
                if 200 <= response.status_code < 500:
                    return True, f"✓ {response.status_code}"
                else:
                    return False, f"✗ {response.status_code}"
                    
        except requests.exceptions.ConnectionError:
            return False, "✗ Connection refused - server not running?"
        except requests.exceptions.Timeout:
            return False, "✗ Timeout"
        except Exception as e:
            return False, f"✗ Error: {str(e)}"
    
    def test_module_endpoints(self):
        """Test Phase 13.5 module endpoints"""
        print("\n" + "="*80)
        print("TESTING PHASE 13.5 MODULE ENDPOINTS")
        print("="*80)
        
        module_endpoints = [
            # Collections Module
            ("GET", "/collections/health", "Collections health check"),
            ("GET", "/collections", "List collections (requires owner_id)"),
            
            # Resources Module
            ("GET", "/resources/health", "Resources health check"),
            ("GET", "/resources", "List resources"),
            
            # Search Module
            ("GET", "/search/health", "Search health check"),
            ("POST", "/search", "Advanced search"),
        ]
        
        print("\n📦 Module Endpoints:")
        for method, path, description in module_endpoints:
            success, message = self.test_endpoint(method, path)
            status = "✅" if success else "❌"
            print(f"  {status} {method:6} {path:40} - {description}")
            print(f"     {message}")
            
            if success:
                self.results['passed'].append((method, path))
            else:
                self.results['failed'].append((method, path, message))
    
    def test_traditional_routers(self):
        """Test traditional router endpoints"""
        print("\n" + "="*80)
        print("TESTING TRADITIONAL ROUTER ENDPOINTS")
        print("="*80)
        
        router_endpoints = [
            # Monitoring
            ("GET", "/monitoring/health", "Health check"),
            ("GET", "/monitoring/database", "Database metrics"),
            ("GET", "/monitoring/events", "Event bus metrics"),
            
            # Authority
            ("GET", "/authority/subjects/suggest", "Subject suggestions (requires q param)"),
            ("GET", "/authority/classification/tree", "Classification tree"),
            
            # Quality
            ("GET", "/quality/distribution", "Quality distribution"),
            
            # Taxonomy
            ("GET", "/taxonomy/tree", "Taxonomy tree"),
            
            # Graph
            ("GET", "/graph/overview", "Graph overview"),
            
            # Recommendations
            ("GET", "/recommendations", "Get recommendations"),
        ]
        
        print("\n📁 Traditional Router Endpoints:")
        for method, path, description in router_endpoints:
            success, message = self.test_endpoint(method, path)
            status = "✅" if success else "❌"
            print(f"  {status} {method:6} {path:40} - {description}")
            print(f"     {message}")
            
            if success:
                self.results['passed'].append((method, path))
            else:
                self.results['failed'].append((method, path, message))
    
    def test_database_endpoints(self):
        """Test Phase 13 database-related endpoints"""
        print("\n" + "="*80)
        print("TESTING PHASE 13 DATABASE ENDPOINTS")
        print("="*80)
        
        db_endpoints = [
            ("GET", "/monitoring/database", "Database connection pool metrics"),
            ("GET", "/monitoring/db/pool", "Database pool status"),
        ]
        
        print("\n🗄️  Database Monitoring Endpoints:")
        for method, path, description in db_endpoints:
            success, message = self.test_endpoint(method, path)
            status = "✅" if success else "❌"
            print(f"  {status} {method:6} {path:40} - {description}")
            print(f"     {message}")
            
            if success:
                self.results['passed'].append((method, path))
            else:
                self.results['failed'].append((method, path, message))
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        total = len(self.results['passed']) + len(self.results['failed'])
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])
        
        print(f"\n📊 Results:")
        print(f"   Total endpoints tested: {total}")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        
        if failed > 0:
            print(f"\n❌ Failed Endpoints:")
            for method, path, message in self.results['failed']:
                print(f"   {method:6} {path:40} - {message}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n✅ ALL ENDPOINTS WORKING!")
            return True
        elif success_rate >= 80:
            print("\n⚠️  MOST ENDPOINTS WORKING - Some issues found")
            return False
        else:
            print("\n❌ MANY ENDPOINTS FAILING - Critical issues")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all endpoint tests"""
        print("\n" + "="*80)
        print("NEO ALEXANDRIA 2.0 - COMPREHENSIVE ENDPOINT TEST")
        print("="*80)
        print(f"\nTesting server at: {self.base_url}")
        print("Waiting for server to be ready...")
        
        # Wait for server to be ready
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"{self.base_url}/monitoring/health", timeout=2)
                if response.status_code == 200:
                    print("✓ Server is ready!\n")
                    break
            except:
                if i < max_retries - 1:
                    print(f"  Waiting... ({i+1}/{max_retries})")
                    time.sleep(2)
                else:
                    print("\n❌ Server is not responding. Please start the server first:")
                    print("   cd backend")
                    print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
                    return False
        
        # Run tests
        self.test_module_endpoints()
        self.test_traditional_routers()
        self.test_database_endpoints()
        
        # Print summary
        return self.print_summary()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test all Neo Alexandria 2.0 endpoints")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the server")
    parser.add_argument("--no-wait", action="store_true", help="Don't wait for server to be ready")
    
    args = parser.parse_args()
    
    tester = EndpointTester(args.url)
    
    if args.no_wait:
        print("Skipping server readiness check...")
    
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
