"""
Test dict-like access to domain objects for backward compatibility.
"""
import pytest
from backend.app.domain.quality import QualityScore
from backend.app.domain.classification import ClassificationResult, ClassificationPrediction
from backend.app.domain.search import SearchResult, SearchResults, SearchQuery
from backend.app.domain.recommendation import Recommendation, RecommendationScore


class TestQualityScoreDictAccess:
    """Test dict-like access to QualityScore."""
    
    def test_getitem_dimension(self):
        """Test __getitem__ for dimension access."""
        score = QualityScore(
            accuracy=0.8,
            completeness=0.7,
            consistency=0.75,
            timeliness=0.9,
            relevance=0.85
        )
        
        assert score['accuracy'] == 0.8
        assert score['completeness'] == 0.7
        assert score['overall_score'] == score.overall_score()
    
    def test_getitem_invalid_key(self):
        """Test __getitem__ raises KeyError for invalid key."""
        score = QualityScore(
            accuracy=0.8,
            completeness=0.7,
            consistency=0.75,
            timeliness=0.9,
            relevance=0.85
        )
        
        with pytest.raises(KeyError):
            _ = score['invalid_key']
    
    def test_get_method(self):
        """Test get method with default value."""
        score = QualityScore(
            accuracy=0.8,
            completeness=0.7,
            consistency=0.75,
            timeliness=0.9,
            relevance=0.85
        )
        
        assert score.get('accuracy') == 0.8
        assert score.get('invalid_key', 0.0) == 0.0
        assert score.get('overall_score') == score.overall_score()


class TestRecommendationDictAccess:
    """Test dict-like access to Recommendation."""
    
    def test_getitem_score_attributes(self):
        """Test __getitem__ for score-related attributes."""
        rec_score = RecommendationScore(score=0.9, confidence=0.85, rank=1)
        rec = Recommendation(
            resource_id="res123",
            user_id="user456",
            recommendation_score=rec_score,
            strategy="hybrid"
        )
        
        assert rec['score'] == 0.9
        assert rec['confidence'] == 0.85
        assert rec['rank'] == 1
        assert rec['resource_id'] == "res123"
        assert rec['strategy'] == "hybrid"
    
    def test_getitem_invalid_key(self):
        """Test __getitem__ raises KeyError for invalid key."""
        rec_score = RecommendationScore(score=0.9, confidence=0.85, rank=1)
        rec = Recommendation(
            resource_id="res123",
            user_id="user456",
            recommendation_score=rec_score
        )
        
        with pytest.raises(KeyError):
            _ = rec['invalid_key']
    
    def test_get_method(self):
        """Test get method with default value."""
        rec_score = RecommendationScore(score=0.9, confidence=0.85, rank=1)
        rec = Recommendation(
            resource_id="res123",
            user_id="user456",
            recommendation_score=rec_score
        )
        
        assert rec.get('score') == 0.9
        assert rec.get('invalid_key', 'default') == 'default'


class TestClassificationResultDictAccess:
    """Test dict-like access to ClassificationResult."""
    
    def test_getitem_attributes(self):
        """Test __getitem__ for attribute access."""
        pred = ClassificationPrediction(taxonomy_id="cat1", confidence=0.9, rank=1)
        result = ClassificationResult(
            predictions=[pred],
            model_version="v1",
            inference_time_ms=50.0
        )
        
        assert result['model_version'] == "v1"
        assert result['inference_time_ms'] == 50.0
        assert result['predictions'] == [pred]
    
    def test_getitem_invalid_key(self):
        """Test __getitem__ raises KeyError for invalid key."""
        pred = ClassificationPrediction(taxonomy_id="cat1", confidence=0.9, rank=1)
        result = ClassificationResult(
            predictions=[pred],
            model_version="v1",
            inference_time_ms=50.0
        )
        
        with pytest.raises(KeyError):
            _ = result['invalid_key']
    
    def test_get_method(self):
        """Test get method with default value."""
        pred = ClassificationPrediction(taxonomy_id="cat1", confidence=0.9, rank=1)
        result = ClassificationResult(
            predictions=[pred],
            model_version="v1",
            inference_time_ms=50.0
        )
        
        assert result.get('model_version') == "v1"
        assert result.get('invalid_key', 'default') == 'default'


class TestSearchResultDictAccess:
    """Test dict-like access to SearchResult."""
    
    def test_getitem_attributes(self):
        """Test __getitem__ for attribute access."""
        result = SearchResult(
            resource_id="res123",
            score=0.95,
            rank=1,
            title="Test Resource"
        )
        
        assert result['resource_id'] == "res123"
        assert result['score'] == 0.95
        assert result['rank'] == 1
        assert result['title'] == "Test Resource"
    
    def test_getitem_invalid_key(self):
        """Test __getitem__ raises KeyError for invalid key."""
        result = SearchResult(
            resource_id="res123",
            score=0.95,
            rank=1
        )
        
        with pytest.raises(KeyError):
            _ = result['invalid_key']
    
    def test_get_method(self):
        """Test get method with default value."""
        result = SearchResult(
            resource_id="res123",
            score=0.95,
            rank=1
        )
        
        assert result.get('score') == 0.95
        assert result.get('invalid_key', 'default') == 'default'


class TestSearchResultsDictAccess:
    """Test dict-like access to SearchResults."""
    
    def test_getitem_attributes(self):
        """Test __getitem__ for attribute access."""
        query = SearchQuery(query_text="test")
        result = SearchResult(resource_id="res123", score=0.95, rank=1)
        results = SearchResults(
            results=[result],
            query=query,
            total_results=1,
            search_time_ms=100.0
        )
        
        assert results['total_results'] == 1
        assert results['search_time_ms'] == 100.0
        assert results['results'] == [result]
    
    def test_getitem_invalid_key(self):
        """Test __getitem__ raises KeyError for invalid key."""
        query = SearchQuery(query_text="test")
        results = SearchResults(
            results=[],
            query=query,
            total_results=0,
            search_time_ms=100.0
        )
        
        with pytest.raises(KeyError):
            _ = results['invalid_key']
    
    def test_get_method(self):
        """Test get method with default value."""
        query = SearchQuery(query_text="test")
        results = SearchResults(
            results=[],
            query=query,
            total_results=0,
            search_time_ms=100.0
        )
        
        assert results.get('total_results') == 0
        assert results.get('invalid_key', 'default') == 'default'
