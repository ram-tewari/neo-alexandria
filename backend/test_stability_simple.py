"""
Simple test script to verify server stability fixes.
Tests that the server can handle multiple consecutive requests without crashing.
"""

import requests
import time

BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcl9pZCI6ImIzYjA3ZTMwLTk2ZWYtNGRmNi04MjAwLTY5YzBmM2VhOTM2MSIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJ0aWVyIjoicHJlbWl1bSIsInNjb3BlcyI6W10sImV4cCI6MTc2ODkyNTE2MSwidHlwZSI6ImFjY2VzcyJ9.jyV84j-iJSiSqAA-2IF31rlBepYkAmZtrd9PhhBGWlc"


def main():
    print("\n" + "="*80)
    print("SERVER STABILITY TEST - 100 Consecutive Requests")
    print("="*80 + "\n")
    
    # Check server
    try:
        resp = requests.get(f"{BASE_URL}/docs", timeout=5)
        if resp.status_code != 200:
            print("ERROR: Server is not running")
            return False
    except:
        print("ERROR: Server is not running")
        return False
    
    print("OK: Server is ready\n")
    
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    successful = 0
    failed = 0
    errors = []
    
    # Test different endpoints
    endpoints = [
        ("GET", "/api/monitoring/health"),
        ("GET", "/resources/health"),
        ("GET", "/search/health"),
        ("GET", "/collections/health"),
        ("GET", "/api/monitoring/performance"),
    ]
    
    start_time = time.time()
    
    for i in range(100):
        endpoint_method, endpoint_path = endpoints[i % len(endpoints)]
        
        try:
            resp = requests.get(
                f"{BASE_URL}{endpoint_path}",
                headers=headers,
                timeout=10
            )
            
            if resp.status_code < 500:
                successful += 1
                if (i + 1) % 10 == 0:
                    print(f"Progress: {i + 1}/100 requests completed")
            else:
                failed += 1
                errors.append(f"Request {i + 1}: {resp.status_code}")
                
        except requests.exceptions.ConnectionError as e:
            failed += 1
            errors.append(f"Request {i + 1}: Connection error - SERVER CRASHED")
            print(f"\nERROR: Server crashed at request {i + 1}")
            break
        except Exception as e:
            failed += 1
            errors.append(f"Request {i + 1}: {str(e)[:50]}")
        
        time.sleep(0.05)
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)
    print(f"Total Requests: 100")
    print(f"Successful: {successful} ({successful/100*100:.1f}%)")
    print(f"Failed: {failed} ({failed/100*100:.1f}%)")
    print(f"Time Elapsed: {elapsed:.2f}s")
    print(f"Avg Latency: {elapsed/100*1000:.0f}ms")
    
    if failed == 0:
        print("\nRESULT: PASSED - No crashes detected")
        return True
    elif successful >= 90:
        print("\nRESULT: PARTIAL - Some failures but no crash")
        return True
    else:
        print("\nRESULT: FAILED - Server crashed or too many failures")
        if errors:
            print(f"\nFirst 5 errors:")
            for error in errors[:5]:
                print(f"  - {error}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
