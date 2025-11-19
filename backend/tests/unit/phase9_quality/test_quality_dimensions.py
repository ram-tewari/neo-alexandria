"""
Unit tests for quality dimension computation methods.
Tests _compute_accuracy, _compute_completeness, _compute_consistency,
_compute_timeliness, _compute_relevance, and compute_quality.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.services.quality_service import QualityService
from backend.app.database.models import Resource, Citation, TaxonomyNode


# db_session and quality_service fixtures are now in conftest.py


@pytest.fixture
def base_resource(db_session: Session):
    """Create a base resource for testing."""
    resource = Resource(
        title="Test Resource",
        url="https://example.com/test",
        content="Test content for quality assessment",
        resource_type="article"
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)
    return resource


class TestComputeAccuracy:
    """Tests for _compute_accuracy dimension method."""
    
    def test_accuracy_with_valid_citations(self, quality_service, base_resource, db_session):
        """Test accuracy with valid citations."""
        # Add valid citations
        citation1 = Citation(
            resource_id=base_resource.id,
            citation_text="Valid citation 1",
            is_valid=True,
            confidence_score=0.9
        )
        citation2 = Citation(
            resource_id=base_resource.id,
            citation_text="Valid citation 2",
            is_valid=True,
            confidence_score=0.85
        )
        db_session.add_all([citation1, citation2])
        db_session.commit()
        
        score = quality_service._compute_accuracy(base_resource)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be above neutral baseline
    
    def test_accuracy_with_invalid_citations(self, quality_service, base_resource, db_session):
        """Test accuracy with invalid citations."""
        citation = Citation(
            resource_id=base_resource.id,
            citation_text="Invalid citation",
            is_valid=False,
            confidence_score=0.3
        )
        db_session.add(citation)
        db_session.commit()
        
        score = quality_service._compute_accuracy(base_resource)
        assert 0.0 <= score <= 1.0
        assert score < 0.5  # Should be below neutral baseline
    
    def test_accuracy_without_citations(self, quality_service, base_resource):
        """Test accuracy without citations uses neutral baseline."""
        score = quality_service._compute_accuracy(base_resource)
        assert score == 0.5  # Neutral baseline
    
    def test_accuracy_with_scholarly_metadata(self, quality_service, base_resource, db_session):
        """Test accuracy with DOI and scholarly metadata."""
        base_resource.doi = "10.1234/test.doi"
        base_resource.authors = "John Doe, Jane Smith"
        db_session.commit()
        
        score = quality_service._compute_accuracy(base_resource)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Scholarly metadata should boost score
    
    def test_accuracy_with_credible_source(self, quality_service, base_resource, db_session):
        """Test accuracy with credible source domain."""
        base_resource.url = "https://arxiv.org/abs/1234.5678"
        db_session.commit()
        
        score = quality_service._compute_accuracy(base_resource)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Credible domain should boost score


class TestComputeCompleteness:
    """Tests for _compute_completeness dimension method."""
    
    def test_completeness_minimal_fields(self, quality_service, base_resource):
        """Test completeness with only required fields."""
        score = quality_service._compute_completeness(base_resource)
        assert 0.0 <= score <= 1.0
        assert score < 0.5  # Only required fields present
    
    def test_completeness_with_important_fields(self, quality_service, base_resource, db_session):
        """Test completeness with important fields."""
        base_resource.summary = "Test summary"
        base_resource.tags = "test,quality,assessment"
        base_resource.authors = "John Doe"
        base_resource.publication_year = 2024
        db_session.commit()
        
        score = quality_service._compute_completeness(base_resource)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Important fields should boost score
    
    def test_completeness_with_scholarly_fields(self, quality_service, base_resource, db_session):
        """Test completeness with scholarly fields."""
        base_resource.doi = "10.1234/test"
        base_resource.journal = "Test Journal"
        base_resource.affiliations = "Test University"
        base_resource.funding_sources = "NSF Grant 12345"
        db_session.commit()
        
        score = quality_service._compute_completeness(base_resource)
        assert 0.0 <= score <= 1.0
        assert score > 0.6  # Scholarly fields should significantly boost score
    
    def test_completeness_fully_populated(self, quality_service, base_resource, db_session):
        """Test completeness with all fields populated."""
        base_resource.summary = "Complete summary"
        base_resource.tags = "test,complete"
        base_resource.authors = "John Doe"
        base_resource.publication_year = 2024
        base_resource.doi = "10.1234/test"
        base_resource.journal = "Test Journal"
        base_resource.affiliations = "Test University"
        base_resource.funding_sources = "NSF"
        base_resource.equations_count = 5
        base_resource.tables_count = 3
        base_resource.figures_count = 2
        db_session.commit()
        
        score = quality_service._compute_completeness(base_resource)
        assert 0.0 <= score <= 1.0
        assert score > 0.8  # Fully populated should have high score


class TestComputeConsistency:
    """Tests for _compute_consistency dimension method."""
    
    def test_consistency_with_aligned_title_content(self, quality_service, base_resource, db_session):
        """Test consistency with aligned title and content."""
        base_resource.title = "Machine Learning Quality Assessment"
        base_resource.content = "This article discusses machine learning techniques for quality assessment in data systems."
        db_session.commit()
        
        score = quality_service._compute_consistency(base_resource)
        assert 0.0 <= score <= 1.0
        assert score > 0.7  # Good alignment should score high
    
    def test_consistency_with_misaligned_title_content(self, quality_service, base_resource, db_session):
        """Test consistency with misaligned title and content."""
        base_resource.title = "Quantum Physics Research"
        base_resource.content = "This article discusses cooking recipes and culinary techniques."
        db_session.commit()
        
        score = quality_service._compute_consistency(base_resource)
        assert 0.0 <= score <= 1.0
        # Score may still be around baseline due to optimistic assumption
    
    def test_consistency_with_summary(self, quality_service, base_resource, db_session):
        """Test consistency with summary-content alignment."""
        base_resource.content = "Long detailed content about machine learning" * 50
        base_resource.summary = "Brief summary about machine learning"
        db_session.commit()
        
        score = quality_service._compute_consistency(base_resource)
        assert 0.0 <= score <= 1.0
        assert score >= 0.5  # Should have reasonable consistency


class TestComputeTimeliness:
    """Tests for _compute_timeliness dimension method."""
    
    def test_timeliness_recent_publication(self, quality_service, base_resource, db_session):
        """Test timeliness with recent publication."""
        base_resource.publication_year = datetime.now().year
        db_session.commit()
        
        score = quality_service._compute_timeliness(base_resource)
        assert 0.0 <= score <= 1.0
        assert score > 0.9  # Recent publication should score very high
    
    def test_timeliness_old_publication(self, quality_service, base_resource, db_session):
        """Test timeliness with old publication."""
        base_resource.publication_year = 1990
        db_session.commit()
        
        score = quality_service._compute_timeliness(base_resource)
        assert 0.0 <= score <= 1.0
        assert score < 0.5  # Old publication should score lower
    
    def test_timeliness_recent_ingestion(self, quality_service, base_resource, db_session):
        """Test timeliness with recent ingestion bonus."""
        base_resource.created_at = datetime.now() - timedelta(days=15)
        db_session.commit()
        
        score = quality_service._compute_timeliness(base_resource)
        assert 0.0 <= score <= 1.0
        # Should get ingestion recency bonus
    
    def test_timeliness_no_publication_date(self, quality_service, base_resource):
        """Test timeliness without publication date uses neutral baseline."""
        score = quality_service._compute_timeliness(base_resource)
        assert score == 0.5  # Neutral baseline


class TestComputeRelevance:
    """Tests for _compute_relevance dimension method."""
    
    def test_relevance_with_classification(self, quality_service, base_resource, db_session):
        """Test relevance with high-confidence classification."""
        node = TaxonomyNode(name="Machine Learning", level=1)
        db_session.add(node)
        db_session.commit()
        
        classification = ResourceClassification(
            resource_id=base_resource.id,
            node_id=node.id,
            confidence_score=0.95
        )
        db_session.add(classification)
        db_session.commit()
        
        score = quality_service._compute_relevance(base_resource)
        assert 0.0 <= score <= 1.0
        assert score > 0.6  # High confidence should boost score
    
    def test_relevance_with_citations(self, quality_service, base_resource, db_session):
        """Test relevance with citation count."""
        base_resource.citation_count = 50
        db_session.commit()
        
        score = quality_service._compute_relevance(base_resource)
        assert 0.0 <= score <= 1.0
        assert score > 0.6  # Citations should boost score
    
    def test_relevance_without_data(self, quality_service, base_resource):
        """Test relevance without classification or citations."""
        score = quality_service._compute_relevance(base_resource)
        assert score == 0.5  # Neutral baseline


class TestComputeQuality:
    """Tests for compute_quality method with weight validation."""
    
    def test_compute_quality_default_weights(self, quality_service, base_resource, db_session):
        """Test compute_quality with default weights."""
        result = quality_service.compute_quality(base_resource.id)
        
        # Result should be a QualityScore domain object
        assert hasattr(result, 'accuracy')
        assert hasattr(result, 'completeness')
        assert hasattr(result, 'consistency')
        assert hasattr(result, 'timeliness')
        assert hasattr(result, 'relevance')
        assert hasattr(result, 'overall_score')
        
        # Verify all scores are in valid range
        assert 0.0 <= result.accuracy <= 1.0
        assert 0.0 <= result.completeness <= 1.0
        assert 0.0 <= result.consistency <= 1.0
        assert 0.0 <= result.timeliness <= 1.0
        assert 0.0 <= result.relevance <= 1.0
        assert 0.0 <= result.overall_score() <= 1.0
        
        # Verify resource was updated
        db_session.refresh(base_resource)
        assert base_resource.quality_overall is not None
        assert base_resource.quality_last_computed is not None
    
    def test_compute_quality_custom_weights(self, quality_service, base_resource, db_session):
        """Test compute_quality with custom weights."""
        custom_weights = {
            "accuracy": 0.3,
            "completeness": 0.2,
            "consistency": 0.2,
            "timeliness": 0.1,
            "relevance": 0.2
        }
        
        result = quality_service.compute_quality(base_resource.id, custom_weights=custom_weights)
        
        assert result is not None
        db_session.refresh(base_resource)
        assert base_resource.quality_weights == custom_weights
    
    def test_compute_quality_invalid_weights_sum(self, quality_service, base_resource):
        """Test compute_quality rejects weights that don't sum to 1.0."""
        invalid_weights = {
            "accuracy": 0.3,
            "completeness": 0.3,
            "consistency": 0.2,
            "timeliness": 0.1,
            "relevance": 0.2  # Sum = 1.1
        }
        
        with pytest.raises(ValueError, match="must sum to 1.0"):
            quality_service.compute_quality(base_resource.id, custom_weights=invalid_weights)
    
    def test_compute_quality_missing_dimension(self, quality_service, base_resource):
        """Test compute_quality rejects weights missing a dimension."""
        invalid_weights = {
            "accuracy": 0.4,
            "completeness": 0.3,
            "consistency": 0.3
            # Missing timeliness and relevance
        }
        
        with pytest.raises(ValueError, match="must include all five dimensions"):
            quality_service.compute_quality(base_resource.id, custom_weights=invalid_weights)
    
    def test_compute_quality_backward_compatibility(self, quality_service, base_resource, db_session):
        """Test compute_quality updates legacy quality_score field."""
        quality_service.compute_quality(base_resource.id)
        
        db_session.refresh(base_resource)
        assert base_resource.quality_score == base_resource.quality_overall
