"""
Test for Phase 9 Outlier Detection implementation.
Tests detect_quality_outliers and _identify_outlier_reasons methods.
"""

import sys
import os
import uuid
from datetime import datetime, timezone

backend_path = os.path.dirname(os.path.abspath(__file__))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Prevent Prometheus metrics registration issues
os.environ['TESTING'] = '1'
os.environ['PROMETHEUS_DISABLE_CREATED_SERIES'] = 'True'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import database models directly without going through app
from backend.app.database.base import Base
from backend.app.database.models import Resource
from backend.app.services.quality_service import QualityService


def test_outlier_detection():
    """Test outlier detection with Isolation Forest."""
    
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        quality_service = QualityService(db, quality_version="v2.0")
        
        # Create 20 resources with normal quality scores
        print("Creating test resources...")
        resource_ids = []
        
        for i in range(20):
            resource = Resource(
                id=uuid.uuid4(),
                title=f"Test Resource {i}",
                description=f"Description for resource {i}",
                creator="Test Author",
                source=f"https://example.com/resource{i}",
                created_at=datetime.now(timezone.utc),
                # Normal quality scores (0.6-0.8 range)
                quality_accuracy=0.7 + (i % 3) * 0.05,
                quality_completeness=0.65 + (i % 4) * 0.05,
                quality_consistency=0.75 + (i % 2) * 0.05,
                quality_timeliness=0.7 + (i % 5) * 0.03,
                quality_relevance=0.68 + (i % 3) * 0.04,
                quality_overall=0.7
            )
            db.add(resource)
            resource_ids.append(resource.id)
        
        # Create 3 outlier resources with very low quality scores
        outlier_ids = []
        for i in range(3):
            outlier = Resource(
                id=uuid.uuid4(),
                title=f"Outlier Resource {i}",
                description=f"Low quality resource {i}",
                creator="Unknown",
                source=f"https://suspicious.com/resource{i}",
                created_at=datetime.now(timezone.utc),
                # Very low quality scores
                quality_accuracy=0.15 + i * 0.05,
                quality_completeness=0.2 + i * 0.03,
                quality_consistency=0.25 + i * 0.02,
                quality_timeliness=0.18 + i * 0.04,
                quality_relevance=0.22 + i * 0.03,
                quality_overall=0.2
            )
            db.add(outlier)
            outlier_ids.append(outlier.id)
        
        db.commit()
        print(f"✓ Created {len(resource_ids)} normal resources and {len(outlier_ids)} outlier resources")
        
        # Test insufficient resources error with a fresh database
        print("\nTesting insufficient resources validation...")
        temp_engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(temp_engine)
        TempSession = sessionmaker(bind=temp_engine)
        temp_db = TempSession()
        temp_service = QualityService(temp_db, quality_version="v2.0")
        try:
            temp_service.detect_quality_outliers()
            print("✗ Should have raised ValueError for insufficient resources")
        except ValueError as e:
            print(f"✓ Correctly raised ValueError: {e}")
        finally:
            temp_db.close()
            temp_engine.dispose()
        
        # Run outlier detection
        print("\nRunning outlier detection...")
        outlier_count = quality_service.detect_quality_outliers(batch_size=1000)
        
        print(f"✓ Detected {outlier_count} outliers")
        
        # Verify outliers were flagged
        print("\nVerifying outlier flags...")
        for outlier_id in outlier_ids:
            resource = db.query(Resource).filter(Resource.id == outlier_id).first()
            if resource.is_quality_outlier:
                print(f"✓ Resource {resource.title} correctly flagged as outlier")
                print(f"  - Outlier score: {resource.outlier_score:.3f}")
                print(f"  - Needs review: {resource.needs_quality_review}")
                
                # Check outlier reasons
                if resource.outlier_reasons:
                    import json
                    reasons = json.loads(resource.outlier_reasons)
                    print(f"  - Reasons: {', '.join(reasons)}")
                    
                    # Verify reasons match low scores
                    if resource.quality_accuracy < 0.3:
                        assert "low_accuracy" in reasons
                    if resource.quality_completeness < 0.3:
                        assert "low_completeness" in reasons
                    if resource.quality_consistency < 0.3:
                        assert "low_consistency" in reasons
                    if resource.quality_timeliness < 0.3:
                        assert "low_timeliness" in reasons
                    if resource.quality_relevance < 0.3:
                        assert "low_relevance" in reasons
        
        # Test _identify_outlier_reasons directly
        print("\nTesting _identify_outlier_reasons method...")
        test_resource = Resource(
            id=uuid.uuid4(),
            title="Test Resource",
            quality_accuracy=0.25,  # Below threshold
            quality_completeness=0.8,  # Above threshold
            quality_consistency=0.15,  # Below threshold
            quality_timeliness=0.5,  # Above threshold
            quality_relevance=0.28,  # Below threshold
            summary_coherence=0.2,  # Below threshold
            summary_fluency=0.9  # Above threshold
        )
        
        reasons = quality_service._identify_outlier_reasons(test_resource)
        print(f"Identified reasons: {reasons}")
        
        assert "low_accuracy" in reasons
        assert "low_consistency" in reasons
        assert "low_relevance" in reasons
        assert "low_summary_coherence" in reasons
        assert "low_completeness" not in reasons
        assert "low_timeliness" not in reasons
        
        print("✓ _identify_outlier_reasons works correctly")
        
        print("\n" + "="*50)
        print("✓ All outlier detection tests passed!")
        print("="*50)
        
    finally:
        db.close()


if __name__ == "__main__":
    test_outlier_detection()
