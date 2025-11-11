"""
Quick verification test for Phase 9 Quality Service implementation.
Tests the core QualityService class and dimension computation methods.
"""

import sys
import os

# Prevent app initialization by setting environment variable
os.environ['TESTING'] = '1'

import uuid
from datetime import datetime, timezone, timedelta

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Direct imports
import app.database.base as base_module
import app.database.models as models_module
import app.services.quality_service as quality_module

Base = base_module.Base
Resource = models_module.Resource
Citation = models_module.Citation
ResourceTaxonomy = models_module.ResourceTaxonomy
TaxonomyNode = models_module.TaxonomyNode
QualityService = quality_module.QualityService


def test_quality_service():
    """Test QualityService initialization and compute_quality method."""
    
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Create test resource with various metadata
        resource = Resource(
            id=uuid.uuid4(),
            title="Machine Learning in Healthcare",
            description="A comprehensive study on machine learning applications in healthcare diagnostics.",
            creator="Dr. Jane Smith",
            source="https://arxiv.org/paper/12345",
            doi="10.1234/test.2024",
            pmid="12345678",
            publication_year=2023,
            authors='[{"name": "Jane Smith", "affiliation": "MIT"}]',
            journal="Nature Medicine",
            equation_count=5,
            table_count=3,
            figure_count=8,
            created_at=datetime.now(timezone.utc)
        )
        db.add(resource)
        db.commit()
        
        # Initialize QualityService
        quality_service = QualityService(db, quality_version="v2.0")
        
        print("✓ QualityService initialized successfully")
        
        # Test compute_quality with default weights
        result = quality_service.compute_quality(str(resource.id))
        
        print("\n=== Quality Assessment Results ===")
        print(f"Accuracy:      {result['accuracy']:.3f}")
        print(f"Completeness:  {result['completeness']:.3f}")
        print(f"Consistency:   {result['consistency']:.3f}")
        print(f"Timeliness:    {result['timeliness']:.3f}")
        print(f"Relevance:     {result['relevance']:.3f}")
        print(f"Overall:       {result['overall']:.3f}")
        
        # Verify resource was updated
        db.refresh(resource)
        assert resource.quality_accuracy is not None
        assert resource.quality_completeness is not None
        assert resource.quality_consistency is not None
        assert resource.quality_timeliness is not None
        assert resource.quality_relevance is not None
        assert resource.quality_overall is not None
        assert resource.quality_score == resource.quality_overall  # Backward compatibility
        assert resource.quality_computation_version == "v2.0"
        assert resource.quality_last_computed is not None
        
        print("\n✓ Resource fields updated correctly")
        
        # Test custom weights
        custom_weights = {
            "accuracy": 0.4,
            "completeness": 0.3,
            "consistency": 0.15,
            "timeliness": 0.1,
            "relevance": 0.05
        }
        result2 = quality_service.compute_quality(str(resource.id), weights=custom_weights)
        
        print("\n=== Custom Weights Results ===")
        print(f"Overall with custom weights: {result2['overall']:.3f}")
        
        # Verify custom weights were stored
        db.refresh(resource)
        import json
        stored_weights = json.loads(resource.quality_weights)
        assert stored_weights == custom_weights
        
        print("✓ Custom weights applied and stored correctly")
        
        # Test invalid weights (should raise ValueError)
        try:
            invalid_weights = {
                "accuracy": 0.5,
                "completeness": 0.3,
                "consistency": 0.1
                # Missing dimensions
            }
            quality_service.compute_quality(str(resource.id), weights=invalid_weights)
            print("✗ Should have raised ValueError for invalid weights")
        except ValueError as e:
            print(f"\n✓ Correctly rejected invalid weights: {e}")
        
        # Test weights that don't sum to 1.0
        try:
            invalid_sum_weights = {
                "accuracy": 0.3,
                "completeness": 0.3,
                "consistency": 0.2,
                "timeliness": 0.1,
                "relevance": 0.05  # Sum = 0.95
            }
            quality_service.compute_quality(str(resource.id), weights=invalid_sum_weights)
            print("✗ Should have raised ValueError for weights not summing to 1.0")
        except ValueError as e:
            print(f"✓ Correctly rejected weights not summing to 1.0: {e}")
        
        print("\n" + "="*50)
        print("✓ All Phase 9 Quality Service tests passed!")
        print("="*50)
        
    finally:
        db.close()


def test_quality_degradation_monitoring():
    """Test monitor_quality_degradation method."""
    
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Initialize QualityService
        quality_service = QualityService(db, quality_version="v2.0")
        
        print("\n" + "="*50)
        print("Testing Quality Degradation Monitoring")
        print("="*50)
        
        # Create test resources with old quality scores
        now = datetime.now(timezone.utc)
        old_date = now - timedelta(days=45)  # 45 days ago (outside 30-day window)
        
        # Resource 1: Will degrade (broken link scenario)
        resource1 = Resource(
            id=uuid.uuid4(),
            title="Resource with Degraded Quality",
            description="This resource will show quality degradation.",
            creator="Author One",
            source="https://example.com/paper1",
            publication_year=2023,
            created_at=old_date
        )
        db.add(resource1)
        db.commit()
        
        # Compute initial quality
        quality_service.compute_quality(str(resource1.id))
        db.refresh(resource1)
        initial_quality1 = resource1.quality_overall
        
        # Simulate old computation date
        resource1.quality_last_computed = old_date
        
        # Simulate degradation by removing metadata
        resource1.creator = None
        resource1.publication_year = None
        db.commit()
        
        print(f"\nResource 1 initial quality: {initial_quality1:.3f}")
        
        # Resource 2: Will NOT degrade significantly
        resource2 = Resource(
            id=uuid.uuid4(),
            title="Stable Quality Resource",
            description="This resource maintains quality.",
            creator="Author Two",
            source="https://arxiv.org/paper2",
            doi="10.1234/stable.2024",
            publication_year=2024,
            created_at=old_date
        )
        db.add(resource2)
        db.commit()
        
        # Compute initial quality
        quality_service.compute_quality(str(resource2.id))
        db.refresh(resource2)
        initial_quality2 = resource2.quality_overall
        
        # Simulate old computation date
        resource2.quality_last_computed = old_date
        db.commit()
        
        print(f"Resource 2 initial quality: {initial_quality2:.3f}")
        
        # Resource 3: Recent computation (should be skipped)
        resource3 = Resource(
            id=uuid.uuid4(),
            title="Recently Computed Resource",
            description="This resource was computed recently.",
            creator="Author Three",
            source="https://example.com/paper3",
            publication_year=2024,
            created_at=now
        )
        db.add(resource3)
        db.commit()
        
        # Compute quality with recent date
        quality_service.compute_quality(str(resource3.id))
        db.refresh(resource3)
        
        print(f"Resource 3 quality: {resource3.quality_overall:.3f} (recent, should be skipped)")
        
        # Run quality degradation monitoring
        print("\n--- Running Quality Degradation Monitoring (30-day window) ---")
        degraded_resources = quality_service.monitor_quality_degradation(time_window_days=30)
        
        print(f"\nFound {len(degraded_resources)} degraded resource(s)")
        
        # Verify results
        if len(degraded_resources) > 0:
            for report in degraded_resources:
                print(f"\nDegraded Resource:")
                print(f"  ID: {report['resource_id']}")
                print(f"  Title: {report['title']}")
                print(f"  Old Quality: {report['old_quality']:.3f}")
                print(f"  New Quality: {report['new_quality']:.3f}")
                print(f"  Degradation: {report['degradation_pct']:.1f}%")
                
                # Verify degradation threshold (20% drop)
                quality_drop = report['old_quality'] - report['new_quality']
                assert quality_drop > 0.2, f"Expected >20% drop, got {quality_drop:.3f}"
                
                # Verify degradation percentage calculation
                expected_pct = (quality_drop / report['old_quality']) * 100.0
                assert abs(report['degradation_pct'] - expected_pct) < 0.1
        
        # Verify resource1 was flagged for review
        db.refresh(resource1)
        if resource1.quality_overall < initial_quality1 - 0.2:
            assert resource1.needs_quality_review == True
            print(f"\n✓ Resource 1 correctly flagged for review")
        
        # Verify resource2 was NOT flagged (no significant degradation)
        db.refresh(resource2)
        quality_change = abs(resource2.quality_overall - initial_quality2)
        if quality_change <= 0.2:
            print(f"✓ Resource 2 correctly NOT flagged (change: {quality_change:.3f})")
        
        # Verify resource3 was skipped (recent computation)
        db.refresh(resource3)
        # Resource3 should not be in degraded list
        resource3_in_report = any(r['resource_id'] == str(resource3.id) for r in degraded_resources)
        assert not resource3_in_report, "Resource 3 should not be in degradation report"
        print(f"✓ Resource 3 correctly skipped (recent computation)")
        
        print("\n" + "="*50)
        print("✓ Quality Degradation Monitoring tests passed!")
        print("="*50)
        
    finally:
        db.close()


if __name__ == "__main__":
    test_quality_service()
    test_quality_degradation_monitoring()
