"""Integration tests for AI service functionality.

These tests use the real AI service to ensure it's working properly.
They should be run separately from unit tests and may require AI dependencies.
"""

import pytest
from backend.app.services.ai_core import AICore


class TestAIIntegration:
    """Test real AI service functionality."""
    
    @pytest.mark.ai
    @pytest.mark.requires_ai_deps
    def test_ai_summary_generation(self):
        """Test that AI can generate summaries from text."""
        ai = AICore()
        
        test_text = """
        Machine learning is a subset of artificial intelligence that focuses on algorithms.
        These algorithms can learn from data and make predictions or decisions.
        Python programming is essential for implementing machine learning solutions.
        """
        
        summary = ai.generate_summary(test_text)
        
        # Should return a non-empty summary
        assert summary
        assert len(summary) > 0
        assert len(summary) < len(test_text)  # Should be shorter than original
        
        # Should contain relevant keywords
        summary_lower = summary.lower()
        assert any(keyword in summary_lower for keyword in ["machine learning", "ai", "algorithms", "python"])
    
    @pytest.mark.ai
    @pytest.mark.requires_ai_deps
    def test_ai_tag_generation(self):
        """Test that AI can generate relevant tags from text."""
        ai = AICore()
        
        test_text = """
        Machine learning is a subset of artificial intelligence that focuses on algorithms.
        These algorithms can learn from data and make predictions or decisions.
        Python programming is essential for implementing machine learning solutions.
        """
        
        tags = ai.generate_tags(test_text)
        
        # Should return a list of tags
        assert isinstance(tags, list)
        assert len(tags) > 0
        
        # Should contain relevant tags
        tag_text = " ".join(tags).lower()
        assert any(keyword in tag_text for keyword in ["machine learning", "artificial intelligence", "python"])
    
    @pytest.mark.ai
    def test_ai_fallback_behavior(self):
        """Test AI fallback behavior when models aren't available."""
        ai = AICore()
        
        # Test with empty text
        summary = ai.generate_summary("")
        assert summary == ""
        
        tags = ai.generate_tags("")
        assert tags == []
        
        # Test with very short text
        short_text = "AI"
        summary = ai.generate_summary(short_text)
        assert summary  # Should return something
        
        tags = ai.generate_tags(short_text)
        assert isinstance(tags, list)  # Should return a list (may be empty)
    
    @pytest.mark.ai
    @pytest.mark.requires_ai_deps
    def test_ai_with_different_content_types(self):
        """Test AI with different types of content."""
        ai = AICore()
        
        # Technical content
        tech_text = "Python is a programming language used for data science and machine learning."
        tech_tags = ai.generate_tags(tech_text)
        assert isinstance(tech_tags, list)
        
        # Language content
        lang_text = "Linguistics is the scientific study of language and its structure."
        lang_tags = ai.generate_tags(lang_text)
        assert isinstance(lang_tags, list)
        
        # Science content
        science_text = "Physics is the study of matter, energy, and their interactions."
        science_tags = ai.generate_tags(science_text)
        assert isinstance(science_tags, list)


class TestAIWithRealIngestion:
    """Test AI integration with real ingestion pipeline."""
    
    @pytest.mark.ai
    @pytest.mark.integration
    @pytest.mark.requires_ai_deps
    def test_end_to_end_ai_processing(self, client, test_db, temp_dir):
        """Test complete ingestion with real AI processing."""
        from unittest.mock import patch
        
        # Don't mock AI - use real AI service
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.services.resource_service.ARCHIVE_ROOT', temp_dir):
            
            mock_fetch.return_value = {
                "url": "https://example.com/ai-test",
                "status": 200,
                "html": """
                <html>
                <head><title>Machine Learning Fundamentals</title></head>
                <body>
                    <article>
                        <h1>Understanding Machine Learning</h1>
                        <p>Machine learning is a subset of artificial intelligence that focuses on algorithms.</p>
                        <p>These algorithms can learn from data and make predictions or decisions.</p>
                        <p>Python programming is essential for implementing machine learning solutions.</p>
                    </article>
                </body>
                </html>
                """
            }
            
            # Submit ingestion request
            response = client.post("/resources", json={"url": "https://example.com/ai-test"})
            assert response.status_code == 202
            
            data = response.json()
            resource_id = data["id"]
            
            # Poll status until completion
            import time
            max_attempts = 50
            for _ in range(max_attempts):
                status_response = client.get(f"/resources/{resource_id}/status")
                assert status_response.status_code == 200
                
                status_data = status_response.json()
                if status_data["ingestion_status"] in ["completed", "failed"]:
                    break
                time.sleep(0.1)
            else:
                pytest.fail("Ingestion did not complete within timeout")
            
            # Verify completion
            assert status_data["ingestion_status"] == "completed"
            
            # Fetch full resource
            resource_response = client.get(f"/resources/{resource_id}")
            assert resource_response.status_code == 200
            
            resource_data = resource_response.json()
            
            # Verify AI processing worked
            assert resource_data["description"]  # Should have AI-generated summary
            assert len(resource_data["subject"]) > 0  # Should have AI-generated tags
            
            # Verify the AI actually processed the content
            description = resource_data["description"].lower()
            subjects = " ".join(resource_data["subject"]).lower()
            
            # Should contain relevant AI-generated content
            assert any(keyword in description or keyword in subjects 
                      for keyword in ["machine learning", "artificial intelligence", "python", "algorithms"])
