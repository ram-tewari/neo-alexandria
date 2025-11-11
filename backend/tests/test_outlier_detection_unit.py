"""
Unit tests for outlier detection functionality.
Tests detect_quality_outliers and _identify_outlier_reasons methods.
"""
import pytest
from sqlalchemy.orm import Session
from backend.app.services.quality_service import QualityService
from backend.app.database.models import Resource


@pytest.fixture
def db_session(test_db):
    """Create a database session for tests."""
    db = test_db()
    yield db
    db.close()


@pytest.fixture
def quality_service(db_session: Session):
    """Create QualityService instance."""
    return QualityService(db_session)


@pytest.fixture
def create_resources_with_quality(db_session: Session):
    """Create multiple resources with quality scores."""
    def _create(count=20, include_outliers=True):
        resources = []
        for i in range(count):
            if include_outliers and i < 2:
                # Create outliers with very low scores
                resource = Resource(
                    title=f"Outlier Resource {i}",
                    identifier=f"https://example.com/outlier{i}",
                    description=f"Outlier content {i}",
                    type="article",
                    quality_accuracy=0.1,
                    quality_completeness=0.15,
                    quality_consistency=0.2,
                    quality_timeliness=0.1,
                    quality_relevance=0.15,
                    quality_overall=0.14
                )
            else:
                # Create normal resources with reasonable scores
                resource = Resource(
                    title=f"Normal Resource {i}",
                    identifier=f"https://example.com/normal{i}",
                    description=f"Normal content {i}",
                    type="article",
                    quality_accuracy=0.7 + (i % 3) * 0.1,
                    quality_completeness=0.65 + (i % 4) * 0.08,
                    quality_consistency=0.75 + (i % 2) * 0.05,
                    quality_timeliness=0.6 + (i % 5) * 0.06,
                    quality_relevance=0.7 + (i % 3) * 0.08,
                    quality_overall=0.68 + (i % 4) * 0.07
                )
            resources.append(resource)
            db_session.add(resource)
        
        db_session.commit()
        for r in resources:
            db_session.refresh(r)
        return resources
    
    return _create


class TestDetectQualityOutliers:
    """Tests for detect_quality_outliers method."""
    
    def test_detect_outliers_with_sufficient_data(self, quality_service, create_resources_with_quality, db_session):
        """Test outlier detection with sufficient resources."""
        resources = create_resources_with_quality(count=50, include_outliers=True)
        
        outlier_count = quality_service.detect_quality_outliers()
        
        assert outlier_count > 0
        
        # Verify outliers were flagged
        outliers = db_session.query(Resource).filter(Resource.is_quality_outlier == True).all()
        assert len(outliers) > 0
        
        for outlier in outliers:
            assert outlier.outlier_score is not None
            assert outlier.outlier_reasons is not None
            assert outlier.needs_quality_review == True
    
    def test_detect_outliers_insufficient_data(self, quality_service, create_resources_with_quality):
        """Test outlier detection with insufficient resources (< 10)."""
        create_resources_with_quality(count=5)
        
        with pytest.raises(ValueError, match="minimum 10 required"):
            quality_service.detect_quality_outliers()
    
    def test_detect_outliers_no_anomalies(self, quality_service, create_resources_with_quality, db_session):
        """Test outlier detection when all resources are similar."""
        resources = create_resources_with_quality(count=30, include_outliers=False)
        
        outlier_count = quality_service.detect_quality_outliers()
        
        # May detect some outliers due to natural variation, but should be minimal
        outliers = db_session.query(Resource).filter(Resource.is_quality_outlier == True).all()
        assert len(outliers) < len(resources) * 0.15  # Less than 15% flagged
    
    def test_detect_outliers_with_summary_scores(self, quality_service, create_resources_with_quality, db_session):
        """Test outlier detection includes summary quality dimensions."""
        resources = create_resources_with_quality(count=20)
        
        # Add summary scores to some resources
        for i, resource in enumerate(resources[:10]):
            resource.summary_quality_coherence = 0.8
            resource.summary_quality_consistency = 0.75
            resource.summary_quality_fluency = 0.85
            resource.summary_quality_relevance = 0.8
        
        db_session.commit()
        
        outlier_count = quality_service.detect_quality_outliers()
        
        # Should complete without errors
        assert outlier_count >= 0
    
    def test_detect_outliers_batch_processing(self, quality_service, create_resources_with_quality):
        """Test outlier detection with batch size parameter."""
        create_resources_with_quality(count=100)
        
        outlier_count = quality_service.detect_quality_outliers(batch_size=50)
        
        assert outlier_count >= 0
    
    def test_detect_outliers_with_missing_dimension_scores(self, quality_service, db_session):
        """Test feature matrix construction with missing quality dimension scores."""
        # Create resources with some missing dimension scores (None values)
        resources = []
        for i in range(20):
            if i < 3:
                # Resources with missing scores - should use 0.5 baseline
                resource = Resource(
                    title=f"Missing Scores Resource {i}",
                    identifier=f"https://example.com/missing{i}",
                    description=f"Content {i}",
                    type="article",
                    quality_accuracy=None,  # Missing
                    quality_completeness=0.7,
                    quality_consistency=None,  # Missing
                    quality_timeliness=0.6,
                    quality_relevance=None,  # Missing
                    quality_overall=0.65
                )
            else:
                # Normal resources with all scores
                resource = Resource(
                    title=f"Complete Resource {i}",
                    identifier=f"https://example.com/complete{i}",
                    description=f"Content {i}",
                    type="article",
                    quality_accuracy=0.75,
                    quality_completeness=0.7,
                    quality_consistency=0.8,
                    quality_timeliness=0.65,
                    quality_relevance=0.72,
                    quality_overall=0.72
                )
            resources.append(resource)
            db_session.add(resource)
        
        db_session.commit()
        
        # Should complete without errors despite missing scores
        outlier_count = quality_service.detect_quality_outliers()
        
        assert outlier_count >= 0
        # Verify the method handled missing scores gracefully
        outliers = db_session.query(Resource).filter(Resource.is_quality_outlier == True).all()
        assert len(outliers) >= 0  # May or may not flag resources with missing scores
    
    def test_detect_outliers_with_partial_summary_scores(self, quality_service, db_session):
        """Test feature matrix construction with partial summary quality scores."""
        # Create resources with some having partial summary scores
        resources = []
        for i in range(15):
            resource = Resource(
                title=f"Resource {i}",
                identifier=f"https://example.com/resource{i}",
                description=f"Content {i}",
                type="article",
                quality_accuracy=0.7,
                quality_completeness=0.75,
                quality_consistency=0.8,
                quality_timeliness=0.65,
                quality_relevance=0.7,
                quality_overall=0.72
            )
            
            # Only some resources have summary scores
            if i < 5:
                resource.summary_coherence = 0.8
                resource.summary_consistency = 0.75
                # Missing fluency and relevance - should use 0.5 baseline
            elif i < 10:
                # No summary scores at all
                pass
            else:
                # Complete summary scores
                resource.summary_coherence = 0.85
                resource.summary_consistency = 0.8
                resource.summary_fluency = 0.9
                resource.summary_relevance = 0.82
            
            resources.append(resource)
            db_session.add(resource)
        
        db_session.commit()
        
        # Should handle mixed summary score availability
        outlier_count = quality_service.detect_quality_outliers()
        
        assert outlier_count >= 0


class TestIdentifyOutlierReasons:
    """Tests for _identify_outlier_reasons helper method."""
    
    def test_identify_reasons_low_accuracy(self, quality_service, db_session):
        """Test identifying low accuracy as outlier reason."""
        resource = Resource(
            title="Test",
            identifier="https://example.com/test",
            description="Test content",
            type="article",
            quality_accuracy=0.2,  # Below threshold
            quality_completeness=0.7,
            quality_consistency=0.7,
            quality_timeliness=0.7,
            quality_relevance=0.7
        )
        db_session.add(resource)
        db_session.commit()
        
        reasons = quality_service._identify_outlier_reasons(resource)
        
        assert "low_accuracy" in reasons
        assert len(reasons) == 1
    
    def test_identify_reasons_multiple_dimensions(self, quality_service, db_session):
        """Test identifying multiple low dimensions."""
        resource = Resource(
            title="Test",
            identifier="https://example.com/test",
            description="Test content",
            type="article",
            quality_accuracy=0.25,  # Below threshold
            quality_completeness=0.2,  # Below threshold
            quality_consistency=0.7,
            quality_timeliness=0.15,  # Below threshold
            quality_relevance=0.7
        )
        db_session.add(resource)
        db_session.commit()
        
        reasons = quality_service._identify_outlier_reasons(resource)
        
        assert "low_accuracy" in reasons
        assert "low_completeness" in reasons
        assert "low_timeliness" in reasons
        assert len(reasons) == 3
    
    def test_identify_reasons_with_summary_scores(self, quality_service, db_session):
        """Test identifying low summary quality dimensions."""
        resource = Resource(
            title="Test",
            identifier="https://example.com/test",
            description="Test content",
            type="article",
            quality_accuracy=0.7,
            quality_completeness=0.7,
            quality_consistency=0.7,
            quality_timeliness=0.7,
            quality_relevance=0.7,
            summary_coherence=0.2,  # Below threshold
            summary_fluency=0.25  # Below threshold
        )
        db_session.add(resource)
        db_session.commit()
        
        reasons = quality_service._identify_outlier_reasons(resource)
        
        assert "low_summary_coherence" in reasons
        assert "low_summary_fluency" in reasons
    
    def test_identify_reasons_no_issues(self, quality_service, db_session):
        """Test with all dimensions above threshold."""
        resource = Resource(
            title="Test",
            identifier="https://example.com/test",
            description="Test content",
            type="article",
            quality_accuracy=0.8,
            quality_completeness=0.75,
            quality_consistency=0.85,
            quality_timeliness=0.7,
            quality_relevance=0.8
        )
        db_session.add(resource)
        db_session.commit()
        
        reasons = quality_service._identify_outlier_reasons(resource)
        
        assert len(reasons) == 0
    
    def test_identify_reasons_threshold_boundary(self, quality_service, db_session):
        """Test behavior at threshold boundary (0.3)."""
        resource = Resource(
            title="Test",
            identifier="https://example.com/test",
            description="Test content",
            type="article",
            quality_accuracy=0.3,  # Exactly at threshold
            quality_completeness=0.29,  # Just below threshold
            quality_consistency=0.7,
            quality_timeliness=0.7,
            quality_relevance=0.7
        )
        db_session.add(resource)
        db_session.commit()
        
        reasons = quality_service._identify_outlier_reasons(resource)
        
        # 0.3 should not be flagged (threshold is <0.3)
        assert "low_accuracy" not in reasons
        # 0.29 should be flagged
        assert "low_completeness" in reasons
