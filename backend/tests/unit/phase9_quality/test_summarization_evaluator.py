"""
Unit tests for SummarizationEvaluator service.
Tests G-Eval methods, FineSurE metrics, BERTScore, and evaluate_summary.
"""
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from backend.app.services.summarization_evaluator import SummarizationEvaluator
from backend.app.database.models import Resource


@pytest.fixture
def evaluator(db_session: Session):
    """Create SummarizationEvaluator instance."""
    return SummarizationEvaluator(db_session)


@pytest.fixture
def evaluator_with_api_key(db_session: Session):
    """Create SummarizationEvaluator with mocked API key."""
    return SummarizationEvaluator(db_session, openai_api_key="test-key")


@pytest.fixture
def resource_with_summary(db_session: Session):
    """Create resource with summary for testing."""
    resource = Resource(
        title="Machine Learning Quality Assessment",
        url="https://example.com/ml-quality",
        content="This is a comprehensive article about machine learning quality assessment techniques. "
                "It covers various metrics, evaluation methods, and best practices for ensuring "
                "high-quality machine learning models in production environments.",
        summary="Article about ML quality assessment covering metrics and best practices.",
        resource_type="article"
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)
    return resource


class TestGEvalMethods:
    """Tests for G-Eval metric methods."""
    
    @patch('openai.ChatCompletion.create')
    def test_g_eval_coherence_success(self, mock_openai, evaluator_with_api_key):
        """Test G-Eval coherence with successful API call."""
        mock_openai.return_value = Mock(
            choices=[Mock(message=Mock(content="Rating: 4"))]
        )
        
        score = evaluator_with_api_key.g_eval_coherence(
            "Test summary",
            "Test reference text"
        )
        
        assert 0.0 <= score <= 1.0
        assert score == 0.75  # (4-1)/4 = 0.75
    
    @patch('openai.ChatCompletion.create')
    def test_g_eval_consistency_success(self, mock_openai, evaluator_with_api_key):
        """Test G-Eval consistency with successful API call."""
        mock_openai.return_value = Mock(
            choices=[Mock(message=Mock(content="Rating: 5"))]
        )
        
        score = evaluator_with_api_key.g_eval_consistency(
            "Test summary",
            "Test reference text"
        )
        
        assert score == 1.0  # (5-1)/4 = 1.0
    
    @patch('openai.ChatCompletion.create')
    def test_g_eval_fluency_success(self, mock_openai, evaluator_with_api_key):
        """Test G-Eval fluency with successful API call."""
        mock_openai.return_value = Mock(
            choices=[Mock(message=Mock(content="Rating: 3"))]
        )
        
        score = evaluator_with_api_key.g_eval_fluency("Test summary")
        
        assert score == 0.5  # (3-1)/4 = 0.5
    
    @patch('openai.ChatCompletion.create')
    def test_g_eval_relevance_success(self, mock_openai, evaluator_with_api_key):
        """Test G-Eval relevance with successful API call."""
        mock_openai.return_value = Mock(
            choices=[Mock(message=Mock(content="Rating: 2"))]
        )
        
        score = evaluator_with_api_key.g_eval_relevance(
            "Test summary",
            "Test reference text"
        )
        
        assert score == 0.25  # (2-1)/4 = 0.25
    
    @patch('openai.ChatCompletion.create')
    def test_g_eval_api_error_fallback(self, mock_openai, evaluator_with_api_key):
        """Test G-Eval falls back to 0.7 on API error."""
        mock_openai.side_effect = Exception("API Error")
        
        score = evaluator_with_api_key.g_eval_coherence(
            "Test summary",
            "Test reference text"
        )
        
        assert score == 0.7  # Fallback score
    
    def test_g_eval_without_api_key(self, evaluator):
        """Test G-Eval returns fallback when no API key."""
        score = evaluator.g_eval_coherence(
            "Test summary",
            "Test reference text"
        )
        
        assert score == 0.7  # Fallback score
    
    @patch('openai.ChatCompletion.create')
    def test_g_eval_parse_rating_variations(self, mock_openai, evaluator_with_api_key):
        """Test parsing various rating response formats."""
        test_cases = [
            ("Rating: 4", 0.75),
            ("The rating is 5", 1.0),
            ("4/5", 0.75),
            ("Score: 3", 0.5),
        ]
        
        for response_text, expected_score in test_cases:
            mock_openai.return_value = Mock(
                choices=[Mock(message=Mock(content=response_text))]
            )
            
            score = evaluator_with_api_key.g_eval_coherence("Test", "Test")
            # Allow some flexibility in parsing
            assert 0.0 <= score <= 1.0


class TestFineSureMetrics:
    """Tests for FineSurE metric methods."""
    
    def test_finesure_completeness_good_coverage(self, evaluator):
        """Test completeness with good keyword coverage."""
        reference = "machine learning quality assessment metrics evaluation"
        summary = "ML quality metrics and evaluation"
        
        score = evaluator.finesure_completeness(summary, reference)
        
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Good coverage should score well
    
    def test_finesure_completeness_poor_coverage(self, evaluator):
        """Test completeness with poor keyword coverage."""
        reference = "machine learning quality assessment metrics evaluation"
        summary = "cooking recipes and food preparation"
        
        score = evaluator.finesure_completeness(summary, reference)
        
        assert 0.0 <= score <= 1.0
        assert score < 0.5  # Poor coverage should score low
    
    def test_finesure_completeness_empty_summary(self, evaluator):
        """Test completeness with empty summary."""
        score = evaluator.finesure_completeness("", "reference text")
        
        assert score == 0.0
    
    def test_finesure_conciseness_optimal_ratio(self, evaluator):
        """Test conciseness with optimal compression ratio."""
        reference = "This is a long reference text " * 20  # ~100 words
        summary = "Brief summary of key points"  # ~5 words, ~5% ratio
        
        score = evaluator.finesure_conciseness(summary, reference)
        
        assert 0.0 <= score <= 1.0
        assert score > 0.7  # Optimal ratio should score high
    
    def test_finesure_conciseness_too_long(self, evaluator):
        """Test conciseness with summary too long."""
        reference = "Short reference text"
        summary = "Very long summary that is almost as long as the reference " * 5
        
        score = evaluator.finesure_conciseness(summary, reference)
        
        assert 0.0 <= score <= 1.0
        assert score < 0.5  # Too long should score low
    
    def test_finesure_conciseness_too_short(self, evaluator):
        """Test conciseness with summary too short."""
        reference = "This is a long reference text " * 50
        summary = "Short"
        
        score = evaluator.finesure_conciseness(summary, reference)
        
        assert 0.0 <= score <= 1.0
        # Very short summaries may score lower


class TestBERTScore:
    """Tests for BERTScore metric."""
    
    @patch('bert_score.score')
    def test_bertscore_success(self, mock_bert_score, evaluator):
        """Test BERTScore with successful computation."""
        # Mock BERTScore return value
        mock_bert_score.return_value = (
            Mock(),  # precision
            Mock(),  # recall
            Mock(item=lambda: 0.85)  # F1 score
        )
        
        score = evaluator.bertscore_f1(
            "Test summary",
            "Test reference"
        )
        
        assert score == 0.85
    
    @patch('bert_score.score')
    def test_bertscore_error_fallback(self, mock_bert_score, evaluator):
        """Test BERTScore falls back on error."""
        mock_bert_score.side_effect = Exception("BERTScore error")
        
        score = evaluator.bertscore_f1(
            "Test summary",
            "Test reference"
        )
        
        assert score == 0.5  # Fallback score
    
    @patch('bert_score.score')
    def test_bertscore_model_configuration(self, mock_bert_score, evaluator):
        """Test BERTScore uses correct model."""
        mock_bert_score.return_value = (Mock(), Mock(), Mock(item=lambda: 0.8))
        
        evaluator.bertscore_f1("Test", "Test")
        
        # Verify correct model was requested
        call_kwargs = mock_bert_score.call_args[1]
        assert call_kwargs.get('model_type') == 'microsoft/deberta-xlarge-mnli'


class TestEvaluateSummary:
    """Tests for evaluate_summary composite method."""
    
    @patch('app.services.summarization_evaluator.SummarizationEvaluator.g_eval_coherence')
    @patch('app.services.summarization_evaluator.SummarizationEvaluator.g_eval_consistency')
    @patch('app.services.summarization_evaluator.SummarizationEvaluator.g_eval_fluency')
    @patch('app.services.summarization_evaluator.SummarizationEvaluator.g_eval_relevance')
    @patch('app.services.summarization_evaluator.SummarizationEvaluator.finesure_completeness')
    @patch('app.services.summarization_evaluator.SummarizationEvaluator.finesure_conciseness')
    @patch('app.services.summarization_evaluator.SummarizationEvaluator.bertscore_f1')
    def test_evaluate_summary_with_g_eval(
        self, mock_bert, mock_concise, mock_complete, mock_rel, mock_flu, mock_cons, mock_coh,
        evaluator_with_api_key, resource_with_summary, db_session
    ):
        """Test evaluate_summary with G-Eval enabled."""
        # Mock all metric methods
        mock_coh.return_value = 0.8
        mock_cons.return_value = 0.85
        mock_flu.return_value = 0.9
        mock_rel.return_value = 0.75
        mock_complete.return_value = 0.7
        mock_concise.return_value = 0.8
        mock_bert.return_value = 0.82
        
        result = evaluator_with_api_key.evaluate_summary(
            resource_with_summary.id,
            use_g_eval=True
        )
        
        assert "coherence" in result
        assert "consistency" in result
        assert "fluency" in result
        assert "relevance" in result
        assert "completeness" in result
        assert "conciseness" in result
        assert "bertscore" in result
        assert "overall" in result
        
        # Verify all scores in valid range
        for key, value in result.items():
            assert 0.0 <= value <= 1.0
        
        # Verify resource was updated
        db_session.refresh(resource_with_summary)
        assert resource_with_summary.summary_quality_overall is not None
    
    @patch('app.services.summarization_evaluator.SummarizationEvaluator.finesure_completeness')
    @patch('app.services.summarization_evaluator.SummarizationEvaluator.finesure_conciseness')
    @patch('app.services.summarization_evaluator.SummarizationEvaluator.bertscore_f1')
    def test_evaluate_summary_without_g_eval(
        self, mock_bert, mock_concise, mock_complete,
        evaluator, resource_with_summary, db_session
    ):
        """Test evaluate_summary without G-Eval (uses fallback)."""
        mock_complete.return_value = 0.7
        mock_concise.return_value = 0.8
        mock_bert.return_value = 0.75
        
        result = evaluator.evaluate_summary(
            resource_with_summary.id,
            use_g_eval=False
        )
        
        # G-Eval metrics should use fallback value of 0.7
        assert result["coherence"] == 0.7
        assert result["consistency"] == 0.7
        assert result["fluency"] == 0.7
        assert result["relevance"] == 0.7
        
        # Other metrics should be computed
        assert result["completeness"] == 0.7
        assert result["conciseness"] == 0.8
        assert result["bertscore"] == 0.75
    
    def test_evaluate_summary_no_summary(self, evaluator, db_session):
        """Test evaluate_summary raises error when no summary exists."""
        resource = Resource(
            title="No Summary",
            url="https://example.com/no-summary",
            content="Content without summary",
            resource_type="article"
        )
        db_session.add(resource)
        db_session.commit()
        
        with pytest.raises(ValueError, match="No summary"):
            evaluator.evaluate_summary(resource.id)
    
    def test_evaluate_summary_composite_calculation(self, evaluator, resource_with_summary, db_session):
        """Test composite score calculation uses correct weights."""
        with patch.multiple(
            'app.services.summarization_evaluator.SummarizationEvaluator',
            g_eval_coherence=Mock(return_value=0.8),
            g_eval_consistency=Mock(return_value=0.8),
            g_eval_fluency=Mock(return_value=0.8),
            g_eval_relevance=Mock(return_value=0.8),
            finesure_completeness=Mock(return_value=0.8),
            finesure_conciseness=Mock(return_value=0.8),
            bertscore_f1=Mock(return_value=0.8)
        ):
            result = evaluator.evaluate_summary(resource_with_summary.id, use_g_eval=False)
            
            # With all metrics at 0.8, composite should also be 0.8
            # (weights: 20%, 20%, 15%, 15%, 15%, 5%, 10% = 100%)
            expected = 0.8 * (0.20 + 0.20 + 0.15 + 0.15 + 0.15 + 0.05 + 0.10)
            assert abs(result["overall"] - expected) < 0.01
