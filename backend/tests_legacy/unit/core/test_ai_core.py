"""Tests for AI core functionality."""

from unittest.mock import patch, Mock

from backend.app.shared.ai_core import Summarizer, ZeroShotTagger, AICore


class TestSummarizer:
    """Test summarization functionality."""
    
    def test_summarizer_initialization(self):
        """Test summarizer can be initialized with custom parameters."""
        summarizer = Summarizer(
            model_name="test-model",
            max_length=100,
            min_length=30
        )
        assert summarizer.model_name == "test-model"
        assert summarizer.max_length == 100
        assert summarizer.min_length == 30
    
    def test_summarizer_empty_text(self):
        """Test summarizer handles empty text."""
        summarizer = Summarizer()
        result = summarizer.summarize("")
        assert result == ""
    
    def test_summarizer_short_text(self):
        """Test summarizer with short text."""
        summarizer = Summarizer()
        text = "This is a short text."
        
        with patch('backend.app.services.ai_core.pipeline', None):
            result = summarizer.summarize(text)
            assert result == text  # Should return as-is for short text
    
    def test_summarizer_long_text_fallback(self):
        """Test summarizer fallback when transformers not available."""
        summarizer = Summarizer()
        long_text = "This is a very long text. " * 50  # Much longer than 280 chars
        
        with patch('backend.app.services.ai_core.pipeline', None):
            result = summarizer.summarize(long_text)
            assert len(result) == 280 + 1  # Should be truncated with ellipsis
            assert result.endswith("…")
    
    def test_summarizer_with_transformers(self):
        """Test summarizer with mock transformers pipeline."""
        summarizer = Summarizer()
        text = "This is a long article about machine learning and artificial intelligence. " * 10
        
        mock_pipeline = Mock()
        mock_pipeline.return_value = [{"summary_text": "This article discusses AI and ML concepts."}]
        
        with patch('backend.app.services.ai_core.pipeline') as mock_pipeline_func:
            mock_pipeline_func.return_value = mock_pipeline
            result = summarizer.summarize(text)
            assert result == "This article discusses AI and ML concepts."
            mock_pipeline.assert_called_once()
    
    def test_summarizer_pipeline_error_fallback(self):
        """Test summarizer falls back to truncation on pipeline error."""
        summarizer = Summarizer()
        text = "This is a long text that should be truncated. " * 20
        
        mock_pipeline = Mock()
        mock_pipeline.side_effect = Exception("Model error")
        
        with patch('backend.app.services.ai_core.pipeline') as mock_pipeline_func:
            mock_pipeline_func.return_value = mock_pipeline
            result = summarizer.summarize(text)
            assert len(result) == 280 + 1
            assert result.endswith("…")


class TestZeroShotTagger:
    """Test zero-shot tagging functionality."""
    
    def test_tagger_initialization(self):
        """Test tagger can be initialized with custom parameters."""
        custom_labels = ["AI", "ML", "Programming"]
        tagger = ZeroShotTagger(
            model_name="test-model",
            candidate_labels=custom_labels,
            multi_label=True,
            threshold=0.5
        )
        assert tagger.model_name == "test-model"
        assert tagger.candidate_labels == custom_labels
        assert tagger.multi_label is True
        assert tagger.threshold == 0.5
    
    def test_tagger_empty_text(self):
        """Test tagger handles empty text."""
        tagger = ZeroShotTagger()
        result = tagger.generate_tags("")
        assert result == []
    
    def test_tagger_fallback_heuristics(self):
        """Test tagger fallback heuristics when transformers not available."""
        tagger = ZeroShotTagger()
        text = "This article discusses artificial intelligence and machine learning concepts."
        
        with patch('backend.app.services.ai_core.pipeline', None):
            result = tagger.generate_tags(text)
            assert "Artificial Intelligence" in result
            assert "Machine Learning" in result
    
    def test_tagger_with_transformers(self):
        """Test tagger with mock transformers pipeline."""
        tagger = ZeroShotTagger()
        text = "This article discusses machine learning algorithms."
        
        mock_pipeline = Mock()
        mock_pipeline.return_value = {
            "labels": ["Machine Learning", "Programming"],
            "scores": [0.8, 0.6]
        }
        
        with patch('backend.app.services.ai_core.pipeline') as mock_pipeline_func:
            mock_pipeline_func.return_value = mock_pipeline
            result = tagger.generate_tags(text)
            assert "Machine Learning" in result
            assert "Programming" in result
            mock_pipeline.assert_called_once()
    
    def test_tagger_threshold_filtering(self):
        """Test tagger filters results by threshold."""
        tagger = ZeroShotTagger(threshold=0.7)
        text = "This article discusses machine learning algorithms."
        
        mock_pipeline = Mock()
        mock_pipeline.return_value = {
            "labels": ["Machine Learning", "Programming"],
            "scores": [0.8, 0.6]  # Only first should pass threshold
        }
        
        with patch('backend.app.services.ai_core.pipeline') as mock_pipeline_func:
            mock_pipeline_func.return_value = mock_pipeline
            result = tagger.generate_tags(text)
            assert "Machine Learning" in result
            assert "Programming" not in result
    
    def test_tagger_pipeline_error_fallback(self):
        """Test tagger falls back to heuristics on pipeline error."""
        tagger = ZeroShotTagger()
        text = "This article discusses artificial intelligence and Python programming."
        
        mock_pipeline = Mock()
        mock_pipeline.side_effect = Exception("Model error")
        
        with patch('backend.app.services.ai_core.pipeline') as mock_pipeline_func:
            mock_pipeline_func.return_value = mock_pipeline
            result = tagger.generate_tags(text)
            assert "Artificial Intelligence" in result
            assert "Python" in result


class TestAICore:
    """Test AI core facade."""
    
    def test_ai_core_initialization(self):
        """Test AI core can be initialized with custom components."""
        summarizer = Summarizer()
        tagger = ZeroShotTagger()
        ai_core = AICore(summarizer=summarizer, tagger=tagger)
        
        assert ai_core.summarizer is summarizer
        assert ai_core.tagger is tagger
    
    def test_ai_core_default_initialization(self):
        """Test AI core initializes with default components."""
        ai_core = AICore()
        assert isinstance(ai_core.summarizer, Summarizer)
        assert isinstance(ai_core.tagger, ZeroShotTagger)
    
    def test_ai_core_generate_summary(self):
        """Test AI core summary generation."""
        ai_core = AICore()
        text = "This is a test article about machine learning."
        
        with patch.object(ai_core.summarizer, 'summarize') as mock_summarize:
            mock_summarize.return_value = "Test summary"
            result = ai_core.generate_summary(text)
            assert result == "Test summary"
            mock_summarize.assert_called_once_with(text)
    
    def test_ai_core_generate_tags(self):
        """Test AI core tag generation."""
        ai_core = AICore()
        text = "This is a test article about machine learning."
        
        with patch.object(ai_core.tagger, 'generate_tags') as mock_generate_tags:
            mock_generate_tags.return_value = ["Machine Learning", "AI"]
            result = ai_core.generate_tags(text)
            assert result == ["Machine Learning", "AI"]
            mock_generate_tags.assert_called_once_with(text)
    
    def test_ai_core_integration(self):
        """Test AI core integration with real text processing."""
        ai_core = AICore()
        text = "This article discusses artificial intelligence, machine learning, and natural language processing. It covers various algorithms and techniques used in modern AI systems."
        
        # Test with fallback behavior (no transformers)
        with patch('backend.app.services.ai_core.pipeline', None):
            summary = ai_core.generate_summary(text)
            tags = ai_core.generate_tags(text)
            
            assert isinstance(summary, str)
            assert len(summary) > 0
            assert isinstance(tags, list)
            assert "Artificial Intelligence" in tags
            assert "Machine Learning" in tags
