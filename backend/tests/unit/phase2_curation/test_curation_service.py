"""Tests for curation service quality analysis functionality."""

import uuid
from unittest.mock import patch
import pytest

from backend.app.database.models import Resource
from backend.app.services.curation_service import CurationInterface
from backend.app.schemas.query import ReviewQueueParams, BatchUpdateResult


class TestCurationInterfaceQualityAnalysis:
    """Test quality analysis and improvement suggestions in curation service."""

    def test_quality_analysis_comprehensive(self, test_db):
        """Test comprehensive quality analysis for a resource."""
        db = test_db()
        try:
            # Create a test resource
            resource = Resource(
                title="Test Article",
                description="A comprehensive test article about machine learning",
                subject=["machine learning", "artificial intelligence"],
                creator="Dr. Jane Smith",
                language="en",
                type="research paper",
                identifier="/archive/2024/01/01/test-article",
                source="https://www.stanford.edu/research/ml-paper",
                quality_score=0.5
            )
            db.add(resource)
            db.commit()
            db.refresh(resource)
            
            # Mock the text file reading
            mock_text = """
            This is a comprehensive research paper examining machine learning algorithms.
            We present novel approaches to neural network optimization and demonstrate
            significant improvements in performance across multiple benchmark datasets.
            Our methodology combines theoretical analysis with empirical validation.
            """
            
            with patch("pathlib.Path.exists", return_value=True), \
                 patch("pathlib.Path.read_text", return_value=mock_text):
                
                analysis = CurationInterface.quality_analysis(db, resource.id)
                
                # Check all required fields are present
                assert "resource_id" in analysis
                assert "metadata_completeness" in analysis
                assert "readability" in analysis
                assert "source_credibility" in analysis
                assert "content_depth" in analysis
                assert "overall_quality" in analysis
                assert "quality_level" in analysis
                
                # Check data types and ranges
                assert analysis["resource_id"] == str(resource.id)
                assert 0 <= analysis["metadata_completeness"] <= 1
                assert 0 <= analysis["source_credibility"] <= 1
                assert 0 <= analysis["content_depth"] <= 1
                assert 0 <= analysis["overall_quality"] <= 1
                assert analysis["quality_level"] in ["HIGH", "MEDIUM", "LOW"]
                
                # Check readability metrics
                readability = analysis["readability"]
                assert "reading_ease" in readability
                assert "fk_grade" in readability
                assert "word_count" in readability
                assert "sentence_count" in readability
                
        finally:
            db.close()

    def test_quality_analysis_resource_not_found(self, test_db):
        """Test quality analysis with non-existent resource."""
        db = test_db()
        try:
            fake_id = uuid.uuid4()
            
            with pytest.raises(ValueError, match="Resource not found"):
                CurationInterface.quality_analysis(db, fake_id)
        finally:
            db.close()

    def test_quality_analysis_no_text_file(self, test_db):
        """Test quality analysis when text file doesn't exist."""
        db = test_db()
        try:
            resource = Resource(
                title="Test Article",
                description="Test description",
                subject=["test"],
                creator="Test Author",
                language="en",
                type="article",
                identifier="/archive/2024/01/01/test-article",
                source="https://example.com/article",
                quality_score=0.5
            )
            db.add(resource)
            db.commit()
            db.refresh(resource)
            
            # Mock file not existing
            with patch("pathlib.Path.exists", return_value=False):
                analysis = CurationInterface.quality_analysis(db, resource.id)
                
                # Should still work but with empty content
                assert analysis["content_depth"] == 0.0
                assert analysis["overall_quality"] >= 0.0
                
        finally:
            db.close()

    def test_improvement_suggestions_high_quality(self, test_db):
        """Test improvement suggestions for high-quality resource."""
        db = test_db()
        try:
            resource = Resource(
                title="Comprehensive ML Research",
                description="A detailed analysis of machine learning algorithms and their applications",
                subject=["machine learning", "artificial intelligence", "algorithms", "neural networks"],
                creator="Dr. Jane Smith",
                language="en",
                type="research paper",
                identifier="/archive/2024/01/01/ml-research",
                source="https://www.stanford.edu/research/ml-paper",
                quality_score=0.9
            )
            db.add(resource)
            db.commit()
            db.refresh(resource)
            
            mock_text = """
            This comprehensive research paper examines the latest developments in machine learning algorithms.
            We present novel approaches to neural network optimization and demonstrate significant improvements
            in performance across multiple benchmark datasets. Our methodology combines theoretical analysis
            with empirical validation, providing insights into the fundamental principles underlying modern AI systems.
            The research demonstrates clear findings with well-structured arguments and comprehensive analysis.
            """
            
            with patch("pathlib.Path.exists", return_value=True), \
                 patch("pathlib.Path.read_text", return_value=mock_text):
                
                suggestions = CurationInterface.improvement_suggestions(db, resource.id)
                
                # High quality resource should have few or no suggestions
                assert isinstance(suggestions, list)
                # Should not have basic metadata suggestions
                assert not any("Complete missing metadata" in s for s in suggestions)
                assert not any("Add a clear, descriptive summary" in s for s in suggestions)
                
        finally:
            db.close()

    def test_improvement_suggestions_low_quality(self, test_db):
        """Test improvement suggestions for low-quality resource."""
        db = test_db()
        try:
            resource = Resource(
                title="Test",
                description=None,
                subject=[],
                creator=None,
                language=None,
                type=None,
                identifier=None,
                source="http://192.168.1.1/page",
                quality_score=0.2
            )
            db.add(resource)
            db.commit()
            db.refresh(resource)
            
            mock_text = "Short."
            
            with patch("pathlib.Path.exists", return_value=True), \
                 patch("pathlib.Path.read_text", return_value=mock_text):
                
                suggestions = CurationInterface.improvement_suggestions(db, resource.id)
                
                # Low quality resource should have many suggestions
                assert isinstance(suggestions, list)
                assert len(suggestions) > 0
                
                # Should have metadata suggestions
                assert any("Complete missing metadata" in s for s in suggestions)
                assert any("Add a clear, descriptive summary" in s for s in suggestions)
                
                # Should have readability suggestions
                assert any("Improve readability" in s for s in suggestions)
                
                # Should have content depth suggestions
                assert any("Increase content depth" in s for s in suggestions)
                
                # Should have source credibility suggestions
                assert any("Use a more credible source" in s for s in suggestions)
                
                # Should have overall quality suggestions
                assert any("low quality" in s.lower() for s in suggestions)
                
        finally:
            db.close()

    def test_improvement_suggestions_medium_quality(self, test_db):
        """Test improvement suggestions for medium-quality resource."""
        db = test_db()
        try:
            resource = Resource(
                title="Medium Quality Article",
                description="Some description",
                subject=["test"],
                creator="Author",
                language="en",
                type="article",
                identifier="/archive/2024/01/01/medium-article",
                source="https://example.com/article",
                quality_score=0.6
            )
            db.add(resource)
            db.commit()
            db.refresh(resource)
            
            mock_text = """
            This is a medium quality article with some content but not comprehensive.
            It has multiple sentences but could be improved with more detail and better structure.
            The readability is okay but could be enhanced with clearer explanations.
            """
            
            with patch("pathlib.Path.exists", return_value=True), \
                 patch("pathlib.Path.read_text", return_value=mock_text):
                
                suggestions = CurationInterface.improvement_suggestions(db, resource.id)
                
                # Medium quality should have some targeted suggestions
                assert isinstance(suggestions, list)
                assert len(suggestions) > 0
                
                # Should have some suggestions but not the most basic ones
                assert not any("Complete missing metadata" in s for s in suggestions)
                
        finally:
            db.close()

    def test_bulk_quality_check_success(self, test_db):
        """Test bulk quality check with successful updates."""
        db = test_db()
        try:
            # Create test resources
            resources = []
            for i in range(3):
                resource = Resource(
                    title=f"Test Article {i}",
                    description=f"Description {i}",
                    subject=["test"],
                    creator="Author",
                    language="en",
                    type="article",
                    identifier=f"/archive/2024/01/01/article-{i}",
                    source="https://example.com/article",
                    quality_score=0.3  # Low initial score
                )
                db.add(resource)
                resources.append(resource)
            
            db.commit()
            for resource in resources:
                db.refresh(resource)
            
            resource_ids = [r.id for r in resources]
            
            # Mock text content
            mock_text = """
            This is a comprehensive article with good content and structure.
            It provides detailed information and analysis on the topic.
            The writing is clear and well-organized with proper explanations.
            """
            
            with patch("pathlib.Path.exists", return_value=True), \
                 patch("pathlib.Path.read_text", return_value=mock_text):
                
                result = CurationInterface.bulk_quality_check(db, resource_ids)
                
                assert isinstance(result, BatchUpdateResult)
                assert result.updated_count == 3
                assert len(result.failed_ids) == 0
                
                # Check that quality scores were updated
                db.commit()  # Ensure changes are committed
                for resource_id in resource_ids:
                    updated_resource = db.query(Resource).filter(Resource.id == resource_id).first()
                    assert updated_resource.quality_score > 0.3  # Should be higher than initial
                    
        finally:
            db.close()

    def test_bulk_quality_check_with_failures(self, test_db):
        """Test bulk quality check with some non-existent resources."""
        db = test_db()
        try:
            # Create one real resource
            resource = Resource(
                title="Test Article",
                description="Test description",
                subject=["test"],
                creator="Author",
                language="en",
                type="article",
                identifier="/archive/2024/01/01/test-article",
                source="https://example.com/article",
                quality_score=0.3
            )
            db.add(resource)
            db.commit()
            db.refresh(resource)
            
            # Mix real and fake IDs
            fake_id = uuid.uuid4()
            resource_ids = [resource.id, fake_id]
            
            mock_text = "Some test content for quality analysis."
            
            with patch("pathlib.Path.exists", return_value=True), \
                 patch("pathlib.Path.read_text", return_value=mock_text):
                
                result = CurationInterface.bulk_quality_check(db, resource_ids)
                
                assert isinstance(result, BatchUpdateResult)
                assert result.updated_count == 1
                assert len(result.failed_ids) == 1
                assert result.failed_ids[0] == fake_id
                
        finally:
            db.close()

    def test_bulk_quality_check_empty_list(self, test_db):
        """Test bulk quality check with empty resource list."""
        db = test_db()
        try:
            result = CurationInterface.bulk_quality_check(db, [])
            
            assert isinstance(result, BatchUpdateResult)
            assert result.updated_count == 0
            assert len(result.failed_ids) == 0
            
        finally:
            db.close()

    def test_review_queue_quality_filtering(self, test_db):
        """Test that review queue properly filters by quality threshold."""
        from backend.app.config.settings import Settings
        
        db = test_db()
        try:
            # Create resources with different quality scores
            resources = []
            quality_scores = [0.3, 0.6, 0.8, 0.9]
            
            for i, score in enumerate(quality_scores):
                resource = Resource(
                    title=f"Article {i}",
                    description=f"Description {i}",
                    subject=["test"],
                    creator="Author",
                    language="en",
                    type="article",
                    identifier=f"/archive/2024/01/01/article-{i}",
                    source="https://example.com/article",
                    quality_score=score
                )
                db.add(resource)
                resources.append(resource)
            
            db.commit()
            
            # Test with threshold 0.7 - should only return resources with score < 0.7
            settings = Settings()
            params = ReviewQueueParams(threshold=0.7, limit=10, offset=0)
            
            items, total = CurationInterface.review_queue(db, params, settings)
            
            assert total == 2  # Only 0.3 and 0.6 should be below 0.7
            assert len(items) == 2
            for item in items:
                assert item.quality_score < 0.7
                
        finally:
            db.close()

    def test_review_queue_sorting(self, test_db):
        """Test that review queue sorts by quality score ascending."""
        from backend.app.config.settings import Settings
        
        db = test_db()
        try:
            # Create resources with different quality scores
            quality_scores = [0.8, 0.2, 0.6, 0.4]
            
            for i, score in enumerate(quality_scores):
                resource = Resource(
                    title=f"Article {i}",
                    description=f"Description {i}",
                    subject=["test"],
                    creator="Author",
                    language="en",
                    type="article",
                    identifier=f"/archive/2024/01/01/article-{i}",
                    source="https://example.com/article",
                    quality_score=score
                )
                db.add(resource)
            
            db.commit()
            
            settings = Settings()
            params = ReviewQueueParams(threshold=0.7, limit=10, offset=0)
            
            items, total = CurationInterface.review_queue(db, params, settings)
            
            # Should be sorted by quality score ascending (lowest first)
            assert len(items) == 3  # 0.2, 0.4, 0.6 are below 0.7
            assert items[0].quality_score == 0.2
            assert items[1].quality_score == 0.4
            assert items[2].quality_score == 0.6
            
        finally:
            db.close()
