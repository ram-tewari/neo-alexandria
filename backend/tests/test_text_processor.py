"""Tests for text processing utilities."""

from unittest.mock import patch

from backend.app.utils.text_processor import clean_text, readability_scores


class TestCleanText:
    """Test text cleaning functionality."""
    
    def test_clean_text_normal_whitespace(self):
        """Test cleaning normal whitespace."""
        text = "  This   is   a   test  "
        result = clean_text(text)
        assert result == "This is a test"
    
    def test_clean_text_control_characters(self):
        """Test cleaning control characters."""
        text = "This\x00is\x01a\x02test"
        result = clean_text(text)
        assert result == "This is a test"
    
    def test_clean_text_multiple_spaces(self):
        """Test cleaning multiple spaces."""
        text = "This    has    multiple    spaces"
        result = clean_text(text)
        assert result == "This has multiple spaces"
    
    def test_clean_text_newlines_and_tabs(self):
        """Test cleaning newlines and tabs."""
        text = "This\nhas\ttabs\nand\nnewlines"
        result = clean_text(text)
        assert result == "This has tabs and newlines"
    
    def test_clean_text_empty_string(self):
        """Test cleaning empty string."""
        result = clean_text("")
        assert result == ""
    
    def test_clean_text_none_input(self):
        """Test cleaning None input."""
        result = clean_text(None)
        assert result == ""


class TestReadabilityScores:
    """Test readability scoring functionality."""
    
    def test_readability_scores_with_textstat(self):
        """Test readability scores with textstat available."""
        text = "This is a simple test sentence. It has multiple sentences for testing."
        
        with patch('backend.app.utils.text_processor.textstat') as mock_textstat:
            mock_textstat.flesch_reading_ease.return_value = 75.5
            mock_textstat.flesch_kincaid_grade.return_value = 6.2
            
            result = readability_scores(text)
            
            assert result["reading_ease"] == 75.5
            assert result["fk_grade"] == 6.2
            mock_textstat.flesch_reading_ease.assert_called_once_with(text)
            mock_textstat.flesch_kincaid_grade.assert_called_once_with(text)
    
    def test_readability_scores_textstat_error_fallback(self):
        """Test readability scores fallback when textstat fails."""
        text = "This is a simple test sentence. It has multiple sentences for testing."
        
        with patch('backend.app.utils.text_processor.textstat') as mock_textstat:
            mock_textstat.flesch_reading_ease.side_effect = Exception("textstat error")
            
            result = readability_scores(text)
            
            # Should fall back to internal calculation
            assert "reading_ease" in result
            assert "fk_grade" in result
            assert isinstance(result["reading_ease"], float)
            assert isinstance(result["fk_grade"], float)
    
    def test_readability_scores_no_textstat(self):
        """Test readability scores without textstat."""
        text = "This is a simple test sentence. It has multiple sentences for testing."
        
        with patch('backend.app.utils.text_processor.textstat', None):
            result = readability_scores(text)
            
            assert "reading_ease" in result
            assert "fk_grade" in result
            assert isinstance(result["reading_ease"], float)
            assert isinstance(result["fk_grade"], float)
    
    def test_readability_scores_empty_text(self):
        """Test readability scores with empty text."""
        result = readability_scores("")
        
        assert result["reading_ease"] == 0.0
        assert result["fk_grade"] == 0.0
    
    def test_readability_scores_single_word(self):
        """Test readability scores with single word."""
        result = readability_scores("test")
        
        assert "reading_ease" in result
        assert "fk_grade" in result
        assert isinstance(result["reading_ease"], float)
        assert isinstance(result["fk_grade"], float)
    
    def test_readability_scores_complex_text(self):
        """Test readability scores with complex text."""
        text = """
        This is a more complex sentence with multiple clauses and sophisticated vocabulary.
        It contains various punctuation marks, including semicolons; colons: and dashes - for testing.
        The text also includes numbers like 123 and special characters like @#$% for comprehensive testing.
        """
        
        with patch('backend.app.utils.text_processor.textstat', None):
            result = readability_scores(text)
            
            assert "reading_ease" in result
            assert "fk_grade" in result
            assert isinstance(result["reading_ease"], float)
            assert isinstance(result["fk_grade"], float)
            # Should not be NaN
            assert not (result["reading_ease"] != result["reading_ease"])  # NaN check
            assert not (result["fk_grade"] != result["fk_grade"])  # NaN check
    
    def test_readability_scores_cleaned_text(self):
        """Test that readability scores work with cleaned text."""
        dirty_text = "  This   is   a   test  \n\n  sentence.  "
        clean_result = clean_text(dirty_text)
        
        with patch('backend.app.utils.text_processor.textstat', None):
            result = readability_scores(clean_result)
            
            assert "reading_ease" in result
            assert "fk_grade" in result
            assert isinstance(result["reading_ease"], float)
            assert isinstance(result["fk_grade"], float)
