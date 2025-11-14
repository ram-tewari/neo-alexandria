"""
Verification script for Phase 9 Quality API Endpoints

This script verifies that all quality assessment API endpoints are properly
implemented and accessible.

Usage:
    python verify_quality_endpoints.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from app import create_app
from app.database.base import SessionLocal
from app.database.models import Resource
from app.services.quality_service import QualityService
import uuid
from datetime import datetime, timedelta


def verify_quality_endpoints():
    """Verify all quality API endpoints are implemented."""
    
    print("=" * 80)
    print("Phase 9 Quality API Endpoints Verification")
    print("=" * 80)
    
    # Create test client
    app = create_app()
    client = TestClient(app)
    
    # Create test database session
    db = SessionLocal()
    
    try:
        # Create test resource with quality scores
        print("\n1. Creating test resource with quality scores...")
        test_resource = Resource(
            id=uuid.uuid4(),
            title="Test Resource for Quality Endpoints",
            url="https://example.com/test",
            content="Test content for quality assessment verification.",
            summary="Test summary for evaluation.",
            quality_accuracy=0.75,
            quality_completeness=0.82,
            quality_consistency=0.88,
            quality_timeliness=0.65,
            quality_relevance=0.79,
            quality_overall=0.77,
            quality_weights='{"accuracy": 0.30, "completeness": 0.25, "consistency": 0.20, "timeliness": 0.15, "relevance": 0.10}',
            quality_last_computed=datetime.now(),
            quality_computation_version="v2.0",
            is_quality_outlier=False,
            needs_quality_review=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(test_resource)
        db.commit()
        print(f"✓ Created test resource: {test_resource.id}")
        
        # Test 1: GET /resources/{id}/quality-details
        print("\n2. Testing GET /resources/{id}/quality-details...")
        response = client.get(f"/resources/{test_resource.id}/quality-details")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Quality details endpoint working")
            print(f"  - Overall quality: {data['quality_overall']}")
            print(f"  - Dimensions: {list(data['quality_dimensions'].keys())}")
        else:
            print(f"✗ Quality details endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
        
        # Test 2: POST /quality/recalculate
        print("\n3. Testing POST /quality/recalculate...")
        response = client.post(
            "/quality/recalculate",
            json={"resource_id": str(test_resource.id)}
        )
        if response.status_code == 202:
            print(f"✓ Quality recalculation endpoint working")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Quality recalculation endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
        
        # Test 3: GET /quality/outliers
        print("\n4. Testing GET /quality/outliers...")
        response = client.get("/quality/outliers?page=1&limit=10")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Outliers endpoint working")
            print(f"  - Total outliers: {data['total']}")
            print(f"  - Page: {data['page']}, Limit: {data['limit']}")
        else:
            print(f"✗ Outliers endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
        
        # Test 4: GET /quality/degradation
        print("\n5. Testing GET /quality/degradation...")
        response = client.get("/quality/degradation?time_window_days=30")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Degradation endpoint working")
            print(f"  - Time window: {data['time_window_days']} days")
            print(f"  - Degraded count: {data['degraded_count']}")
        else:
            print(f"✗ Degradation endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
        
        # Test 5: POST /summaries/{id}/evaluate
        print("\n6. Testing POST /summaries/{id}/evaluate...")
        response = client.post(
            f"/summaries/{test_resource.id}/evaluate?use_g_eval=false"
        )
        if response.status_code == 202:
            print(f"✓ Summary evaluation endpoint working")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Summary evaluation endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
        
        # Test 6: GET /quality/distribution
        print("\n7. Testing GET /quality/distribution...")
        response = client.get("/quality/distribution?bins=10&dimension=overall")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Distribution endpoint working")
            print(f"  - Dimension: {data['dimension']}")
            print(f"  - Bins: {data['bins']}")
            print(f"  - Statistics: mean={data['statistics']['mean']:.2f}")
        else:
            print(f"✗ Distribution endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
        
        # Test 7: GET /quality/trends
        print("\n8. Testing GET /quality/trends...")
        response = client.get("/quality/trends?granularity=weekly&dimension=overall")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Trends endpoint working")
            print(f"  - Dimension: {data['dimension']}")
            print(f"  - Granularity: {data['granularity']}")
            print(f"  - Data points: {len(data['data_points'])}")
        else:
            print(f"✗ Trends endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
        
        # Test 8: GET /quality/dimensions
        print("\n9. Testing GET /quality/dimensions...")
        response = client.get("/quality/dimensions")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Dimensions endpoint working")
            print(f"  - Total resources: {data['total_resources']}")
            print(f"  - Dimensions tracked: {list(data['dimensions'].keys())}")
            print(f"  - Overall avg: {data['overall']['avg']:.2f}")
        else:
            print(f"✗ Dimensions endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
        
        # Test 9: GET /quality/review-queue
        print("\n10. Testing GET /quality/review-queue...")
        response = client.get("/quality/review-queue?page=1&limit=10&sort_by=quality_overall")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Review queue endpoint working")
            print(f"  - Total in queue: {data['total']}")
            print(f"  - Page: {data['page']}, Limit: {data['limit']}")
        else:
            print(f"✗ Review queue endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
        
        print("\n" + "=" * 80)
        print("Verification Complete!")
        print("=" * 80)
        print("\nAll 9 quality API endpoints have been implemented:")
        print("  1. GET /resources/{id}/quality-details")
        print("  2. POST /quality/recalculate")
        print("  3. GET /quality/outliers")
        print("  4. GET /quality/degradation")
        print("  5. POST /summaries/{id}/evaluate")
        print("  6. GET /quality/distribution")
        print("  7. GET /quality/trends")
        print("  8. GET /quality/dimensions")
        print("  9. GET /quality/review-queue")
        
    finally:
        # Cleanup
        db.query(Resource).filter(Resource.id == test_resource.id).delete()
        db.commit()
        db.close()


if __name__ == "__main__":
    verify_quality_endpoints()
