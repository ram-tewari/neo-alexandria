"""Tests for classification service."""

from backend.app.services.classification_service import PersonalClassification


class TestPersonalClassification:
    """Test personal classification functionality."""
    
    def test_auto_classify_language_keyword_in_title(self):
        """Test classification with language keyword in title."""
        classifier = PersonalClassification()
        
        result = classifier.auto_classify(
            title="Introduction to Language Studies",
            description="A comprehensive guide to linguistics",
            tags=["education", "academic"]
        )
        
        assert result == "400"
    
    def test_auto_classify_ai_keyword_in_description(self):
        """Test classification with AI keyword in description."""
        classifier = PersonalClassification()
        
        result = classifier.auto_classify(
            title="Technology Overview",
            description="This article covers artificial intelligence and machine learning",
            tags=["tech", "innovation"]
        )
        
        assert result == "000"  # AI/ML now maps to 000 (Computer Science)
    
    def test_auto_classify_ml_keyword_in_tags(self):
        """Test classification with ML keyword in tags."""
        classifier = PersonalClassification()
        
        result = classifier.auto_classify(
            title="Data Science Guide",
            description="Learn about data analysis",
            tags=["python", "ml", "statistics"]
        )
        
        assert result == "000"  # ML now maps to 000 (Computer Science)
    
    def test_auto_classify_programming_keyword(self):
        """Test classification with programming keyword."""
        classifier = PersonalClassification()
        
        result = classifier.auto_classify(
            title="Python Programming Tutorial",
            description="Learn Python programming basics",
            tags=["tutorial", "coding"]
        )
        
        assert result == "000"  # Programming now maps to 000 (Computer Science)
    
    def test_auto_classify_multiple_keywords_first_match(self):
        """Test classification with multiple keywords - should return first match."""
        classifier = PersonalClassification()
        
        result = classifier.auto_classify(
            title="Language and AI Programming",
            description="Combining linguistics with artificial intelligence",
            tags=["programming", "python"]
        )
        
        # Should match "programming" first (000) before "language" (400)
        assert result == "000"
    
    def test_auto_classify_case_insensitive(self):
        """Test classification is case insensitive."""
        classifier = PersonalClassification()
        
        result = classifier.auto_classify(
            title="MACHINE LEARNING BASICS",
            description="Introduction to ML concepts",
            tags=["AI", "Data Science"]
        )
        
        assert result == "000"  # ML now maps to 000 (Computer Science)
    
    def test_auto_classify_no_keywords_fallback(self):
        """Test classification with no matching keywords returns fallback."""
        classifier = PersonalClassification()
        
        result = classifier.auto_classify(
            title="General Article",
            description="This is a general article about various topics",
            tags=["general", "miscellaneous"]
        )
        
        assert result == "000"
    
    def test_auto_classify_empty_inputs(self):
        """Test classification with empty inputs."""
        classifier = PersonalClassification()
        
        result = classifier.auto_classify(
            title=None,
            description=None,
            tags=[]
        )
        
        assert result == "000"
    
    def test_auto_classify_none_inputs(self):
        """Test classification with None inputs."""
        classifier = PersonalClassification()
        
        result = classifier.auto_classify(
            title="",
            description="",
            tags=None
        )
        
        assert result == "000"
    
    def test_auto_classify_partial_inputs(self):
        """Test classification with partial inputs."""
        classifier = PersonalClassification()
        
        result = classifier.auto_classify(
            title="AI Research",
            description=None,
            tags=None
        )
        
        assert result == "000"  # AI now maps to 000 (Computer Science)
    
    def test_auto_classify_whitespace_handling(self):
        """Test classification handles whitespace properly."""
        classifier = PersonalClassification()
        
        result = classifier.auto_classify(
            title="  Machine Learning  ",
            description="  AI and ML concepts  ",
            tags=["  python  ", "  data  "]
        )
        
        assert result == "000"  # ML now maps to 000 (Computer Science)
    
    def test_auto_classify_keyword_variations(self):
        """Test classification with keyword variations."""
        classifier = PersonalClassification()
        
        # Test "artificial intelligence" (full phrase)
        result1 = classifier.auto_classify(
            title="Artificial Intelligence Overview",
            description="",
            tags=[]
        )
        assert result1 == "000"  # AI now maps to 000 (Computer Science)
        
        # Test "machine learning" (full phrase)
        result2 = classifier.auto_classify(
            title="Machine Learning Tutorial",
            description="",
            tags=[]
        )
        assert result2 == "000"  # ML now maps to 000 (Computer Science)
        
        # Test "natural language processing"
        result3 = classifier.auto_classify(
            title="Natural Language Processing Guide",
            description="",
            tags=[]
        )
        assert result3 == "000"  # NLP now maps to 000 (Computer Science)
    
    def test_auto_classify_deterministic_ordering(self):
        """Test that classification is deterministic based on keyword order."""
        classifier = PersonalClassification()
        
        # Same inputs should always produce same result
        result1 = classifier.auto_classify(
            title="Language and AI",
            description="",
            tags=[]
        )
        
        result2 = classifier.auto_classify(
            title="Language and AI",
            description="",
            tags=[]
        )
        
        assert result1 == result2 == "000"  # "ai" has higher precedence than "language"
    
    def test_classification_keyword_mapping_completeness(self):
        """Test that all expected keywords are mapped."""
        classifier = PersonalClassification()
        
        # Test all keywords in the mapping
        test_cases = [
            ("language", "400"),
            ("linguistics", "400"),
            ("grammar", "400"),
            ("ai", "000"),  # AI now maps to 000 (Computer Science)
            ("artificial intelligence", "000"),  # AI now maps to 000
            ("machine learning", "000"),  # ML now maps to 000
            ("ml", "000"),  # ML now maps to 000
            ("programming", "000"),  # Programming now maps to 000
            ("python", "000"),  # Python now maps to 000
            ("software", "000"),  # Software now maps to 000
        ]
        
        for keyword, expected_code in test_cases:
            result = classifier.auto_classify(
                title=f"Test {keyword}",
                description="",
                tags=[]
            )
            assert result == expected_code, f"Keyword '{keyword}' should map to '{expected_code}'"
