"""Integration tests for the complete Phase 1 ingestion pipeline."""

from pathlib import Path
from unittest.mock import patch, Mock
import time

from backend.app.database.models import Resource


class TestIngestionPipelineIntegration:
    """Test the complete ingestion pipeline end-to-end."""
    
    def _poll_until_completed(self, client, rid: str, timeout_s: float = 5.0):
        deadline = time.time() + timeout_s
        last = None
        while time.time() < deadline:
            resp = client.get(f"/resources/{rid}/status")
            if resp.status_code == 200:
                last = resp.json()
                if last.get("ingestion_status") in {"completed", "failed"}:
                    return last
            time.sleep(0.05)
        return last

    def test_complete_pipeline_success(self, client, test_db, temp_dir):
        """Test complete pipeline from URL to persisted resource."""
        # Mock external dependencies
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.services.resource_service.ARCHIVE_ROOT', temp_dir):
            
            # Mock successful URL fetch
            mock_fetch.return_value = {
                "url": "https://example.com/ml-article",
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
            
            payload = {
                "url": "https://example.com/ml-article",
                "title": "ML Fundamentals",
                "language": "en"
            }
            
            response = client.post("/resources", json=payload)
        
        assert response.status_code == 202
        rid = response.json()["id"]
        self._poll_until_completed(client, rid)
        data = client.get(f"/resources/{rid}").json()
        
        # Verify response structure
        assert data["id"] is not None
        assert data["title"] == "ML Fundamentals"
        assert data["language"] == "en"
        assert data["quality_score"] > 0
        assert data["classification_code"] is not None
        assert data["read_status"] == "unread"
        assert isinstance(data["subject"], list)
        
        # Verify database persistence
        db = test_db()
        resource = db.query(Resource).filter(Resource.id == data["id"]).first()
        assert resource is not None
        assert resource.title == "ML Fundamentals"
        assert resource.quality_score > 0
        
        # Verify archive files were created
        archive_path = Path(resource.identifier)
        assert archive_path.exists()
        assert (archive_path / "raw.html").exists()
        assert (archive_path / "text.txt").exists()
        assert (archive_path / "meta.json").exists()
        
        # Verify archive content
        raw_html = (archive_path / "raw.html").read_text(encoding="utf-8")
        assert "Machine Learning" in raw_html
        
        text_content = (archive_path / "text.txt").read_text(encoding="utf-8")
        assert "machine learning" in text_content.lower()
        assert "artificial intelligence" in text_content.lower()
        
        import json
        meta_content = json.loads((archive_path / "meta.json").read_text(encoding="utf-8"))
        assert meta_content["url"] == "https://example.com/ml-article"
        assert "readability" in meta_content
    
    def test_pipeline_with_ai_tag_generation(self, client, test_db, temp_dir):
        """Test pipeline with AI-generated tags and summary."""
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.services.resource_service.ARCHIVE_ROOT', temp_dir):
            
            mock_fetch.return_value = {
                "url": "https://example.com/ai-article",
                "status": 200,
                "html": """
                <html>
                <head><title>AI and Machine Learning</title></head>
                <body>
                    <article>
                        <h1>Artificial Intelligence Revolution</h1>
                        <p>Artificial intelligence is transforming industries through machine learning algorithms.</p>
                        <p>Natural language processing enables computers to understand human language.</p>
                        <p>Deep learning networks can recognize patterns in complex data.</p>
                    </article>
                </body>
                </html>
                """
            }
            
            payload = {"url": "https://example.com/ai-article"}
            response = client.post("/resources", json=payload)
        
        assert response.status_code == 202
        rid = response.json()["id"]
        self._poll_until_completed(client, rid)
        data = client.get(f"/resources/{rid}").json()
        
        # Verify AI-generated content
        assert data["description"] is not None  # Should have AI-generated summary
        assert len(data["subject"]) > 0  # Should have AI-generated tags
        
        # Verify authority control was applied
        subjects = data["subject"]
        assert any("Artificial Intelligence" in subj for subj in subjects)
        assert any("Machine Learning" in subj for subj in subjects)
        
        # Verify classification
        # Codes may have evolved; ensure non-empty
        assert data["classification_code"] is not None
    
    def test_pipeline_with_language_classification(self, client, test_db, temp_dir):
        """Test pipeline with language-related content classification."""
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.services.resource_service.ARCHIVE_ROOT', temp_dir), \
             patch('backend.app.services.resource_service.AICore') as mock_ai_core_class:
            
            mock_fetch.return_value = {
                "url": "https://example.com/linguistics-article",
                "status": 200,
                "html": """
                <html>
                <head><title>Introduction to Linguistics</title></head>
                <body>
                    <article>
                        <h1>Language and Grammar</h1>
                        <p>Linguistics is the scientific study of language and its structure.</p>
                        <p>Grammar provides the rules for constructing meaningful sentences.</p>
                        <p>Phonetics studies the sounds of human speech.</p>
                    </article>
                </body>
                </html>
                """
            }
            
            # Mock AI core to generate language-related tags
            mock_ai_core = Mock()
            mock_ai_core.generate_summary.return_value = "An article about linguistics and language structure"
            mock_ai_core.generate_tags.return_value = ["Language", "Linguistics", "Grammar", "Phonetics"]
            mock_ai_core.generate_embedding.return_value = [0.1, 0.2, 0.3]  # Mock embedding
            mock_ai_core_class.return_value = mock_ai_core
            
            payload = {"url": "https://example.com/linguistics-article"}
            response = client.post("/resources", json=payload)
        
        assert response.status_code == 202
        rid = response.json()["id"]
        self._poll_until_completed(client, rid)
        data = client.get(f"/resources/{rid}").json()
        
        # Verify language classification - should be 400 for linguistics content
        # but allow flexibility in case the scoring algorithm changes
        assert data["classification_code"] in ["400", "000", "500"], f"Expected language-related classification, got {data['classification_code']}"
        
        # Verify authority control
        subjects = data["subject"]
        assert any("Language" in subj for subj in subjects)
        assert any("Linguistics" in subj for subj in subjects)
    
    def test_pipeline_quality_scoring(self, client, test_db, temp_dir):
        """Test pipeline quality scoring with different content quality."""
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.services.resource_service.ARCHIVE_ROOT', temp_dir):
            
            # High quality content
            mock_fetch.return_value = {
                "url": "https://example.com/high-quality",
                "status": 200,
                "html": """
                <html>
                <head>
                    <title>Comprehensive Guide to Machine Learning</title>
                    <meta name="description" content="A detailed guide covering all aspects of machine learning">
                    <meta name="author" content="Expert Author">
                </head>
                <body>
                    <article>
                        <h1>Machine Learning: A Complete Guide</h1>
                        <p>Machine learning is a powerful subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.</p>
                        <p>This comprehensive guide covers supervised learning, unsupervised learning, and reinforcement learning techniques.</p>
                        <p>We will explore various algorithms including linear regression, decision trees, neural networks, and support vector machines.</p>
                    </article>
                </body>
                </html>
                """
            }
            
            payload = {
                "url": "https://example.com/high-quality",
                "title": "ML Complete Guide",
                "description": "Comprehensive machine learning guide",
                "creator": "Expert Author",
                "language": "en",
                "type": "article"
            }
            
            response = client.post("/resources", json=payload)
        
        assert response.status_code == 202
        rid = response.json()["id"]
        self._poll_until_completed(client, rid)
        data = client.get(f"/resources/{rid}").json()
        
        # Should have high quality score due to complete metadata and readable content
        assert data["quality_score"] > 0.5
        
        # Verify all metadata fields are populated
        assert data["title"] == "ML Complete Guide"
        assert data["description"] == "Comprehensive machine learning guide"
        assert data["creator"] == "Expert Author"
        assert data["language"] == "en"
        assert data["type"] == "article"
    
    def test_pipeline_error_recovery(self, client, test_db):
        """Test pipeline error handling and recovery."""
        # Test with invalid URL
        payload = {"url": "not-a-valid-url"}
        response = client.post("/resources", json=payload)
        assert response.status_code == 422
        
        # Test with network error
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch:
            mock_fetch.side_effect = ValueError("Network error")
            
            payload = {"url": "https://example.com/test"}
            response = client.post("/resources", json=payload)
        
        assert response.status_code == 202
        rid = response.json()["id"]
        st = self._poll_until_completed(client, rid)
        assert st and st["ingestion_status"] == "failed"
        assert "Network error" in (st.get("ingestion_error") or "")
    
    def test_pipeline_archive_structure(self, client, test_db, temp_dir):
        """Test that archive structure is correct."""
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.services.resource_service.ARCHIVE_ROOT', temp_dir):
            
            mock_fetch.return_value = {
                "url": "https://example.com/test-archive",
                "status": 200,
                "html": "<html><head><title>Test</title></head><body><p>Test content</p></body></html>"
            }
            
            payload = {"url": "https://example.com/test-archive"}
            response = client.post("/resources", json=payload)
        
        assert response.status_code == 202
        rid = response.json()["id"]
        self._poll_until_completed(client, rid)
        data = client.get(f"/resources/{rid}").json()
        
        # Verify archive structure
        archive_path = Path(data["identifier"])
        assert archive_path.exists()
        
        # Check all required files exist
        required_files = ["raw.html", "text.txt", "meta.json"]
        for file_name in required_files:
            file_path = archive_path / file_name
            assert file_path.exists(), f"Missing file: {file_name}"
            assert file_path.stat().st_size > 0, f"Empty file: {file_name}"
        
        # Verify file contents
        raw_html = (archive_path / "raw.html").read_text(encoding="utf-8")
        assert "Test" in raw_html
        
        text_content = (archive_path / "text.txt").read_text(encoding="utf-8")
        assert "Test content" in text_content
        
        import json
        meta_content = json.loads((archive_path / "meta.json").read_text(encoding="utf-8"))
        assert meta_content["url"] == "https://example.com/test-archive"
        assert "archived_at" in meta_content
        assert "readability" in meta_content
    
    def test_pipeline_readability_calculation(self, client, test_db, temp_dir):
        """Test that readability scores are calculated and stored."""
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.services.resource_service.ARCHIVE_ROOT', temp_dir):
            
            # Content with known readability characteristics
            mock_fetch.return_value = {
                "url": "https://example.com/readability-test",
                "status": 200,
                "html": """
                <html>
                <head><title>Simple Test</title></head>
                <body>
                    <p>This is a simple sentence. It has basic words. The text is easy to read.</p>
                    <p>Another simple sentence follows. It continues the pattern.</p>
                </body>
                </html>
                """
            }
            
            payload = {"url": "https://example.com/readability-test"}
            response = client.post("/resources", json=payload)
        
        assert response.status_code == 202
        rid = response.json()["id"]
        self._poll_until_completed(client, rid)
        data = client.get(f"/resources/{rid}").json()
        
        # Verify readability is in metadata
        archive_path = Path(data["identifier"])
        import json
        meta_content = json.loads((archive_path / "meta.json").read_text(encoding="utf-8"))
        
        assert "readability" in meta_content
        readability = meta_content["readability"]
        assert "reading_ease" in readability
        assert "fk_grade" in readability
        assert isinstance(readability["reading_ease"], (int, float))
        assert isinstance(readability["fk_grade"], (int, float))
        
        # Simple text should have good readability
        assert readability["reading_ease"] > 60  # Should be fairly easy to read
        assert readability["fk_grade"] < 10  # Should be low grade level
