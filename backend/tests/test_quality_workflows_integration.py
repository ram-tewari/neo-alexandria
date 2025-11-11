"""
Integration tests for quality assessment workflows.
Tests end-to-end quality assessment, summarization evaluation,
outlier detection, and integration with Phase 6, 6.5, and 8.5.
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.quality_service import QualityService
from app.services.summarization_evaluator import SummarizationEvaluator
from app.models.resource import Resource
from app.models.citation import Citation
from app.models.taxonomy_node import TaxonomyNode
from app.models.resource_classification import ResourceClassification


@pytest.fixture
def quality_service(db_session: Session):
    """Create QualityService instance."""
    return QualityService(db_session)


@pytest.fixture
def summarization_evaluator(db_session: Session):
    """Create SummarizationEvaluator instance."""
    return SummarizationEvaluator(db_session)


class TestEndToEndQualityAssessment:
    """Test complete quality assessment workflow."""
    
    def test_resource_creation_to_quality_score(
        self, quality_service, db_session
    ):
        """Test end-to-end from resource creation to quality score storage."""
        # Create resource
        resource = Resource(
            title="Complete Research Article",
            url="https://arxiv.org/abs/2024.12345",
            content="Comprehensive research article about machine learning quality assessment.",
            summary="Research on ML quality assessment",
            resource_type="article",
            authors="Dr. Jane Smith, Dr. John Doe",
            publication_year=2024,
            doi="10.1234/ml.quality.2024",
            tags="machine-learning,quality,assessment"
        )
        db_session.add(resource)
        db_session.commit()
        db_session.refresh(resource)
        
        # Compute quality
        result = quality_service.compute_quality(resource.id)
        
        # Verify all dimensions computed
        assert result["accuracy"] is not None
        assert result["completeness"] is not None
        assert result["consistency"] is not None
        assert result["timeliness"] is not None
        assert result["relevance"] is not None
        assert result["overall"] is not None
        
        # Verify resource updated
        db_session.refresh(resource)
        assert resource.quality_overall == result["overall"]
        assert resource.quality_accuracy == result["accuracy"]
        assert resource.quality_last_computed is not None
        assert resource.quality_computation_version is not None
        
        # Verify backward compatibility
        assert resource.quality_score == resource.quality_overall
    
    def test_quality_with_phase6_citations(
        self, quality_service, db_session
    ):
        """Test quality assessment integrates with Phase 6 citations."""
        # Create resource
        resource = Resource(
            title="Cited Research",
            url="https://example.com/cited",
            content="Research with citations",
            resource_type="article"
        )
        db_session.add(resource)
        db_session.commit()
        
        # Add Phase 6 citations
        citations = [
            Citation(
                resource_id=resource.id,
                citation_text="Smith et al. (2023)",
                is_valid=True,
                confidence_score=0.95
            ),
            Citation(
                resource_id=resource.id,
                citation_text="Doe (2024)",
                is_valid=True,
                confidence_score=0.88
            )
        ]
        db_session.add_all(citations)
        db_session.commit()
        
        # Compute quality
        result = quality_service.compute_quality(resource.id)
        
        # Accuracy should benefit from valid citations
        assert result["accuracy"] > 0.5
    
    def test_quality_with_phase65_scholarly_metadata(
        self, quality_service, db_session
    ):
        """Test quality assessment integrates with Phase 6.5 scholarly metadata."""
        # Create resource with scholarly metadata
        resource = Resource(
            title="Scholarly Article",
            url="https://example.com/scholarly",
            content="Scholarly research article",
            resource_type="article",
            doi="10.1234/scholarly.2024",
            pmid="12345678",
            arxiv_id="2024.12345",
            journal="Nature Machine Learning",
            authors="Dr. Expert",
            affiliations="MIT, Stanford",
            funding_sources="NSF Grant ABC123"
        )
        db_session.add(resource)
        db_session.commit()
        
        # Compute quality
        result = quality_service.compute_quality(resource.id)
        
        # Accuracy and completeness should benefit from metadata
        assert result["accuracy"] > 0.6
        assert result["completeness"] > 0.7
    
    def test_quality_with_phase85_classification(
        self, quality_service, db_session
    ):
        """Test quality assessment integrates with Phase 8.5 ML classification."""
        # Create taxonomy node
        node = TaxonomyNode(
            name="Machine Learning",
            level=1,
            description="ML topics"
        )
        db_session.add(node)
        db_session.commit()
        
        # Create resource
        resource = Resource(
            title="ML Research",
            url="https://example.com/ml",
            content="Machine learning research",
            resource_type="article"
        )
        db_session.add(resource)
        db_session.commit()
        
        # Add Phase 8.5 classification
        classification = ResourceClassification(
            resource_id=resource.id,
            node_id=node.id,
            confidence_score=0.92
        )
        db_session.add(classification)
        db_session.commit()
        
        # Compute quality
        result = quality_service.compute_quality(resource.id)
        
        # Relevance should benefit from high-confidence classification
        assert result["relevance"] > 0.5


class TestSummarizationEvaluationWorkflow:
    """Test summarization evaluation workflow."""
    
    def test_summary_generation_to_evaluation(
        self, summarization_evaluator, db_session
    ):
        """Test workflow from summary generation to evaluation."""
        # Create resource with summary
        resource = Resource(
            title="Research Article",
            url="https://example.com/research",
            content="This is a comprehensive research article about machine learning quality "
                    "assessment techniques and methodologies for production systems.",
            summary="Article about ML quality assessment in production.",
            resource_type="article"
        )
        db_session.add(resource)
        db_session.commit()
        db_session.refresh(resource)
        
        # Evaluate summary (without G-Eval to avoid API costs)
        result = summarization_evaluator.evaluate_summary(
            resource.id,
            use_g_eval=False
        )
        
        # Verify all metrics computed
        assert "coherence" in result
        assert "consistency" in result
        assert "fluency" in result
        assert "relevance" in result
        assert "completeness" in result
        assert "conciseness" in result
        assert "bertscore" in result
        assert "overall" in result
        
        # Verify resource updated
        db_session.refresh(resource)
        assert resource.summary_quality_overall == result["overall"]
        assert resource.summary_quality_coherence == result["coherence"]


class TestOutlierDetectionWorkflow:
    """Test outlier detection workflow."""
    
    def test_batch_outlier_detection(self, quality_service, db_session):
        """Test outlier detection with batch of resources."""
        # Create mix of normal and outlier resources
        resources = []
        
        # Normal resources
        for i in range(15):
            resource = Resource(
                title=f"Normal Resource {i}",
                url=f"https://example.com/normal{i}",
                content=f"Normal content {i}",
                resource_type="article",
                quality_accuracy=0.7 + (i % 3) * 0.05,
                quality_completeness=0.68 + (i % 4) * 0.06,
                quality_consistency=0.72 + (i % 2) * 0.04,
                quality_timeliness=0.65 + (i % 5) * 0.05,
                quality_relevance=0.7 + (i % 3) * 0.06,
                quality_overall=0.69 + (i % 4) * 0.05
            )
            resources.append(resource)
        
        # Outlier resources
        for i in range(3):
            resource = Resource(
                title=f"Outlier Resource {i}",
                url=f"https://example.com/outlier{i}",
                content=f"Outlier content {i}",
                resource_type="article",
                quality_accuracy=0.15,
                quality_completeness=0.2,
                quality_consistency=0.18,
                quality_timeliness=0.12,
                quality_relevance=0.16,
                quality_overall=0.16
            )
            resources.append(resource)
        
        db_session.add_all(resources)
        db_session.commit()
        
        # Detect outliers
        outlier_count = quality_service.detect_quality_outliers()
        
        # Should detect some outliers
        assert outlier_count > 0
        
        # Verify outliers flagged
        outliers = db_session.query(Resource).filter(
            Resource.is_quality_outlier == True
        ).all()
        
        assert len(outliers) > 0
        
        for outlier in outliers:
            assert outlier.outlier_score is not None
            assert outlier.outlier_reasons is not None
            assert outlier.needs_quality_review == True


class TestQualityDegradationWorkflow:
    """Test quality degradation monitoring workflow."""
    
    def test_time_based_degradation_monitoring(
        self, quality_service, db_session
    ):
        """Test degradation monitoring with time-based scenarios."""
        from datetime import timedelta
        
        # Create resource with old quality score
        resource = Resource(
            title="Aging Resource",
            url="https://example.com/aging",
            content="Content that may degrade",
            resource_type="article",
            quality_overall=0.85,
            quality_accuracy=0.85,
            quality_completeness=0.85,
            quality_consistency=0.85,
            quality_timeliness=0.85,
            quality_relevance=0.85,
            quality_last_computed=datetime.now() - timedelta(days=35)
        )
        db_session.add(resource)
        db_session.commit()
        
        # Monitor degradation
        reports = quality_service.monitor_quality_degradation(time_window_days=30)
        
        # Should check the resource
        assert isinstance(reports, list)
        
        # Verify resource quality was recomputed
        db_session.refresh(resource)
        assert resource.quality_last_computed > (datetime.now() - timedelta(days=1))


class TestCrossPhaseIntegration:
    """Test integration across multiple phases."""
    
    def test_complete_resource_lifecycle(
        self, quality_service, summarization_evaluator, db_session
    ):
        """Test complete resource lifecycle with all quality features."""
        # 1. Create resource with full metadata
        resource = Resource(
            title="Complete Lifecycle Resource",
            url="https://arxiv.org/abs/2024.complete",
            content="Comprehensive research article with full metadata and citations.",
            summary="Complete research with metadata",
            resource_type="article",
            authors="Dr. Complete",
            publication_year=2024,
            doi="10.1234/complete.2024",
            journal="Complete Journal",
            tags="complete,lifecycle,test"
        )
        db_session.add(resource)
        db_session.commit()
        
        # 2. Add citations (Phase 6)
        citation = Citation(
            resource_id=resource.id,
            citation_text="Reference (2024)",
            is_valid=True,
            confidence_score=0.9
        )
        db_session.add(citation)
        db_session.commit()
        
        # 3. Add classification (Phase 8.5)
        node = TaxonomyNode(name="Research", level=1)
        db_session.add(node)
        db_session.commit()
        
        classification = ResourceClassification(
            resource_id=resource.id,
            node_id=node.id,
            confidence_score=0.88
        )
        db_session.add(classification)
        db_session.commit()
        
        # 4. Compute quality (Phase 9)
        quality_result = quality_service.compute_quality(resource.id)
        
        assert quality_result["overall"] > 0.6  # Should have good quality
        
        # 5. Evaluate summary (Phase 9)
        summary_result = summarization_evaluator.evaluate_summary(
            resource.id,
            use_g_eval=False
        )
        
        assert summary_result["overall"] > 0.5
        
        # 6. Verify all data persisted
        db_session.refresh(resource)
        assert resource.quality_overall is not None
        assert resource.summary_quality_overall is not None
        assert resource.quality_last_computed is not None
