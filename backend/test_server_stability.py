"""
Test script to verify server stability fixes.
Tests that the server can handle multiple consecutive requests without crashing.
"""

import requests
import time
from typing import List, Tuple

BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcl9pZCI6ImIzYjA3ZTMwLTk2ZWYtNGRmNi04MjAwLTY5YzBmM2VhOTM2MSIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJ0aWVyIjoicHJlbWl1bSIsInNjb3BlcyI6W10sImV4cCI6MTc2ODkyNTE2MSwidHlwZSI6ImFjY2VzcyJ9.jyV84j-iJSiSqAA-2IF31rlBepYkAmZtrd9PhhBGWlc"


def test_server_stability(num_requests: int = 100) -> Tuple[int, int, List[str]]:
    """
    Test server stability by making consecutive requests.
    
    Args:
        num_requests: Number of requests to make
        
    Returns:
        Tuple of (successful_requests, failed_requests, error_messages)
    """
    print(f"\n{'='*80}")
    print(f"SERVER STABILITY TEST - {num_requests} Consecutive Requests")
    print(f"{'='*80}\n")
    
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    successful = 0
    failed = 0
    errors = []
    
    # Test different endpoints to stress different parts of the system
    endpoints = [
        ("GET", "/api/monitoring/health"),
        ("GET", "/resources/health"),
        ("GET", "/search/health"),
        ("GET", "/collections/health"),
        ("GET", "/api/monitoring/performance"),
    ]
    
    start_time = time.time()
    
    for i in range(num_requests):
        endpoint_method, endpoint_path = endpoints[i % len(endpoints)]
        
        try:
            if endpoint_method == "GET":
                resp = requests.get(
                    f"{BASE_URL}{endpoint_path}",
                    headers=headers,
                    timeout=10
                )
            else:
                resp = requests.post(
                    f"{BASE_URL}{endpoint_path}",
                    headers=headers,
                    json={},
                    timeout=10
                )
            
            if resp.status_code < 500:  # Accept any non-500 error
                successful += 1
                if (i + 1) % 10 == 0:
                    print(f"✓ Completed {i + 1}/{num_requests} requests")
            else:
                failed += 1
                error_msg = f"Request {i + 1} failed with {resp.status_code}: {endpoint_path}"
                errors.append(error_msg)
                print(f"✗ {error_msg}")
                
        except requests.exceptions.ConnectionError as e:
            failed += 1
            error_msg = f"Request {i + 1} - Connection error (server crashed?): {str(e)[:100]}"
            errors.append(error_msg)
            print(f"✗ {error_msg}")
            print("\n❌ SERVER CRASHED - Test failed")
            break
        except Exception as e:
            failed += 1
            error_msg = f"Request {i + 1} - Error: {str(e)[:100]}"
            errors.append(error_msg)
            print(f"✗ {error_msg}")
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.05)
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*80}")
    print("TEST RESULTS")
    print(f"{'='*80}")
    print(f"Total Requests: {num_requests}")
    print(f"Successful: {successful} ({successful/num_requests*100:.1f}%)")
    print(f"Failed: {failed} ({failed/num_requests*100:.1f}%)")
    print(f"Time Elapsed: {elapsed:.2f}s")
    print(f"Avg Latency: {elapsed/num_requests*1000:.0f}ms")
    
    if failed == 0:
        print("\n✅ SERVER STABILITY TEST PASSED - No crashes detected")
    elif successful >= num_requests * 0.9:
        print("\n⚠️  SERVER STABILITY TEST PARTIAL - Some failures but no crash")
    else:
        print("\n❌ SERVER STABILITY TEST FAILED - Server crashed or too many failures")
    
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
    
    return successful, failed, errors


def check_server():
    """Check if server is running"""
    try:
        resp = requests.get(f"{BASE_URL}/docs", timeout=5)
        if resp.status_code == 200:
            print("✓ Server is ready")
            return True
    except:
        pass
    
    print("✗ Server is not running")
    print("Please start the server with: uvicorn app.main:app --reload")
    return False


if __name__ == "__main__":
    if not check_server():
        exit(1)
    
    # Run stability test
    successful, failed, errors = test_server_stability(100)
    
    # Exit with appropriate code
    if failed == 0:
        exit(0)  # Success
    elif successful >= 90:
        exit(1)  # Partial success
    else:
        exit(2)  # Failure
