"""Tests for PDF ingestion functionality."""

import pytest
import time
from unittest.mock import patch, Mock
from pathlib import Path

from backend.app.utils.content_extractor import extract_from_fetched


class TestPDFIngestionFlow:
    """Test complete PDF ingestion flow."""
    
    def test_pdf_ingestion_via_api(self, client, test_db, temp_dir):
        """Test PDF ingestion through the API."""
        # Mock PDF content
        pdf_content = b"%PDF-1.4\nfake pdf content"
        extracted_text = "This is a PDF document about machine learning and artificial intelligence. It contains detailed information about neural networks and deep learning algorithms."
        
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.services.resource_service.ARCHIVE_ROOT', temp_dir):
            
            mock_fetch.return_value = {
                "url": "https://example.com/document.pdf",
                "status": 200,
                "content_bytes": pdf_content,
                "content_type": "application/pdf",
                "headers": {"Content-Type": "application/pdf"}
            }
            
            # Submit PDF ingestion request
            response = client.post("/resources", json={"url": "https://example.com/document.pdf"})
            assert response.status_code == 202
            
            data = response.json()
            resource_id = data["id"]
            
            # Poll status until completion
            max_attempts = 50
            for _ in range(max_attempts):
                status_response = client.get(f"/resources/{resource_id}/status")
                assert status_response.status_code == 200
                
                status_data = status_response.json()
                if status_data["ingestion_status"] in ["completed", "failed"]:
                    break
                time.sleep(0.1)
            else:
                pytest.fail("PDF ingestion did not complete within timeout")
            
            # Verify completion
            assert status_data["ingestion_status"] == "completed"
            
            # Fetch full resource
            resource_response = client.get(f"/resources/{resource_id}")
            assert resource_response.status_code == 200
            
            resource_data = resource_response.json()
            assert resource_data["source"] == "https://example.com/document.pdf"
            assert resource_data["quality_score"] > 0
            assert resource_data["classification_code"] is not None
    
    def test_pdf_ingestion_by_url_extension(self, client, test_db, temp_dir):
        """Test PDF ingestion detected by URL extension."""
        pdf_content = b"%PDF-1.4\nfake pdf content"
        
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.services.resource_service.ARCHIVE_ROOT', temp_dir):
            
            mock_fetch.return_value = {
                "url": "https://example.com/document.PDF",
                "status": 200,
                "content_bytes": pdf_content,
                "content_type": "application/octet-stream",
                "headers": {"Content-Type": "application/octet-stream"}
            }
            
            response = client.post("/resources", json={"url": "https://example.com/document.PDF"})
            assert response.status_code == 202
            
            data = response.json()
            resource_id = data["id"]
            
            # Wait for completion
            max_attempts = 50
            for _ in range(max_attempts):
                status_response = client.get(f"/resources/{resource_id}/status")
                status_data = status_response.json()
                if status_data["ingestion_status"] in ["completed", "failed"]:
                    break
                time.sleep(0.1)
            else:
                pytest.fail("PDF ingestion did not complete within timeout")
            
            assert status_data["ingestion_status"] == "completed"
    
    def test_pdf_ingestion_by_file_signature(self, client, test_db, temp_dir):
        """Test PDF ingestion detected by file signature."""
        pdf_content = b"%PDF-1.4\nfake pdf content"
        
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.services.resource_service.ARCHIVE_ROOT', temp_dir):
            
            mock_fetch.return_value = {
                "url": "https://example.com/document",
                "status": 200,
                "content_bytes": pdf_content,
                "content_type": "application/octet-stream",
                "headers": {"Content-Type": "application/octet-stream"}
            }
            
            response = client.post("/resources", json={"url": "https://example.com/document"})
            assert response.status_code == 202
            
            data = response.json()
            resource_id = data["id"]
            
            # Wait for completion
            max_attempts = 50
            for _ in range(max_attempts):
                status_response = client.get(f"/resources/{resource_id}/status")
                status_data = status_response.json()
                if status_data["ingestion_status"] in ["completed", "failed"]:
                    break
                time.sleep(0.1)
            else:
                pytest.fail("PDF ingestion did not complete within timeout")
            
            assert status_data["ingestion_status"] == "completed"
    
    def test_pdf_extraction_failure_handling(self, client, test_db):
        """Test PDF extraction failure handling."""
        # Mock PDF content that will fail extraction
        pdf_content = b"%PDF-1.4\ncorrupted pdf content"
        
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.utils.content_extractor.extract_pdf') as mock_extract_pdf:
            
            mock_fetch.return_value = {
                "url": "https://example.com/corrupted.pdf",
                "status": 200,
                "content_bytes": pdf_content,
                "content_type": "application/pdf"
            }
            
            # Mock PDF extraction to fail
            mock_extract_pdf.side_effect = Exception("PDF extraction failed")
            
            response = client.post("/resources", json={"url": "https://example.com/corrupted.pdf"})
            assert response.status_code == 202
            
            data = response.json()
            resource_id = data["id"]
            
            # Wait for failure
            max_attempts = 50
            for _ in range(max_attempts):
                status_response = client.get(f"/resources/{resource_id}/status")
                status_data = status_response.json()
                if status_data["ingestion_status"] == "failed":
                    break
                time.sleep(0.1)
            else:
                pytest.fail("PDF ingestion did not fail within timeout")
            
            assert status_data["ingestion_status"] == "failed"
            assert "PDF extraction failed" in (status_data["ingestion_error"] or "")


class TestPDFContentExtraction:
    """Test PDF content extraction functionality."""
    
    def test_extract_from_fetched_pdf_with_pymupdf(self):
        """Test PDF extraction using PyMuPDF."""
        pdf_content = b"%PDF-1.4\nfake pdf content"
        extracted_text = "This is text extracted from a PDF using PyMuPDF."
        
        fetched_data = {
            "content_type": "application/pdf",
            "content_bytes": pdf_content,
            "url": "https://example.com/test.pdf"
        }
        
        with patch('backend.app.utils.content_extractor.extract_pdf') as mock_extract_pdf:
            mock_extract_pdf.return_value = {"title": None, "text": extracted_text}
            
            result = extract_from_fetched(fetched_data)
            
            assert result["title"] is None
            assert result["text"] == extracted_text
            mock_extract_pdf.assert_called_once_with(pdf_content)
    
    def test_extract_from_fetched_pdf_with_pdfminer_fallback(self):
        """Test PDF extraction using pdfminer fallback."""
        pdf_content = b"%PDF-1.4\nfake pdf content"
        extracted_text = "This is text extracted using pdfminer as fallback."
        
        fetched_data = {
            "content_type": "application/pdf",
            "content_bytes": pdf_content,
            "url": "https://example.com/test.pdf"
        }
        
        with patch('backend.app.utils.content_extractor.extract_pdf') as mock_extract_pdf:
            mock_extract_pdf.return_value = {"title": None, "text": extracted_text}
            
            result = extract_from_fetched(fetched_data)
            
            assert result["title"] is None
            assert result["text"] == extracted_text
    
    def test_extract_from_fetched_pdf_no_libraries(self):
        """Test PDF extraction when no PDF libraries are available."""
        pdf_content = b"%PDF-1.4\nfake pdf content"
        
        fetched_data = {
            "content_type": "application/pdf",
            "content_bytes": pdf_content,
            "url": "https://example.com/test.pdf"
        }
        
        with patch('backend.app.utils.content_extractor.extract_pdf') as mock_extract_pdf:
            mock_extract_pdf.return_value = {"title": None, "text": ""}
            
            result = extract_from_fetched(fetched_data)
            
            assert result["title"] is None
            assert result["text"] == ""
    
    def test_pdf_vs_html_content_type_detection(self):
        """Test proper content type detection for PDF vs HTML."""
        # Test PDF content
        pdf_content = b"%PDF-1.4\nfake pdf content"
        pdf_fetched = {
            "content_type": "application/pdf",
            "content_bytes": pdf_content,
            "url": "https://example.com/test.pdf"
        }
        
        with patch('backend.app.utils.content_extractor.extract_pdf') as mock_extract_pdf:
            mock_extract_pdf.return_value = {"title": None, "text": "PDF text"}
            result = extract_from_fetched(pdf_fetched)
            assert result["text"] == "PDF text"
            mock_extract_pdf.assert_called_once()
        
        # Test HTML content
        html_fetched = {
            "content_type": "text/html",
            "html": "<html><head><title>Test</title></head><body><p>HTML content</p></body></html>",
            "url": "https://example.com/test.html"
        }
        
        result = extract_from_fetched(html_fetched)
        assert result["title"] == "Test"
        assert "HTML content" in result["text"]


class TestPDFIngestionWithAI:
    """Test PDF ingestion with AI processing."""
    
    def test_pdf_ingestion_with_ai_summarization(self, client, test_db, temp_dir):
        """Test PDF ingestion with AI summarization and tagging."""
        pdf_content = b"%PDF-1.4\nfake pdf content"
        
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.utils.content_extractor.extract_pdf') as mock_extract_pdf, \
             patch('backend.app.services.resource_service.ARCHIVE_ROOT', temp_dir), \
             patch('backend.app.services.resource_service.AICore') as mock_ai_core_class:
            
            mock_fetch.return_value = {
                "url": "https://example.com/ai-paper.pdf",
                "status": 200,
                "content_bytes": pdf_content,
                "content_type": "application/pdf"
            }
            
            # Mock PDF extraction to return meaningful text
            mock_extract_pdf.return_value = {
                "title": "AI Paper",
                "text": "This paper discusses advanced machine learning techniques and deep learning algorithms."
            }
            
            # Mock AI core
            mock_ai_core = Mock()
            mock_ai_core.generate_summary.return_value = "This paper discusses advanced machine learning techniques."
            mock_ai_core.generate_tags.return_value = ["Machine Learning", "Deep Learning", "Neural Networks"]
            mock_ai_core.generate_embedding.return_value = [0.1, 0.2, 0.3]  # Mock embedding
            mock_ai_core_class.return_value = mock_ai_core
            
            response = client.post("/resources", json={"url": "https://example.com/ai-paper.pdf"})
            assert response.status_code == 202
            
            data = response.json()
            resource_id = data["id"]
            
            # Wait for completion
            max_attempts = 50
            for _ in range(max_attempts):
                status_response = client.get(f"/resources/{resource_id}/status")
                status_data = status_response.json()
                if status_data["ingestion_status"] in ["completed", "failed"]:
                    break
                time.sleep(0.1)
            else:
                pytest.fail("PDF ingestion did not complete within timeout")
            
            assert status_data["ingestion_status"] == "completed"
            
            # Verify AI processing was called
            mock_ai_core.generate_summary.assert_called_once()
            mock_ai_core.generate_tags.assert_called_once()
            
            # Fetch full resource
            resource_response = client.get(f"/resources/{resource_id}")
            resource_data = resource_response.json()
            
            assert resource_data["description"] == "This paper discusses advanced machine learning techniques."
            assert "Machine Learning" in resource_data["subject"]
            assert "Deep Learning" in resource_data["subject"]
            assert "Neural Networks" in resource_data["subject"]
    
    def test_pdf_ingestion_ai_failure_fallback(self, client, test_db, temp_dir):
        """Test PDF ingestion with AI failure fallback."""
        pdf_content = b"%PDF-1.4\nfake pdf content"
        
        with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
             patch('backend.app.utils.content_extractor.extract_pdf') as mock_extract_pdf, \
             patch('backend.app.services.resource_service.ARCHIVE_ROOT', temp_dir), \
             patch('backend.app.services.resource_service.AICore') as mock_ai_core_class:
            
            mock_fetch.return_value = {
                "url": "https://example.com/test.pdf",
                "status": 200,
                "content_bytes": pdf_content,
                "content_type": "application/pdf"
            }
            
            # Mock PDF extraction to return meaningful text
            mock_extract_pdf.return_value = {
                "title": "Test PDF",
                "text": "This is a test PDF document with some content for processing."
            }
            
            # Mock AI core to fail
            mock_ai_core = Mock()
            mock_ai_core.generate_summary.side_effect = Exception("AI processing failed")
            mock_ai_core_class.return_value = mock_ai_core
            
            response = client.post("/resources", json={"url": "https://example.com/test.pdf"})
            assert response.status_code == 202
            
            data = response.json()
            resource_id = data["id"]
            
            # Wait for failure
            max_attempts = 50
            for _ in range(max_attempts):
                status_response = client.get(f"/resources/{resource_id}/status")
                status_data = status_response.json()
                if status_data["ingestion_status"] == "failed":
                    break
                time.sleep(0.1)
            else:
                pytest.fail("PDF ingestion did not fail within timeout")
            
            assert status_data["ingestion_status"] == "failed"
            assert "AI processing failed" in (status_data["ingestion_error"] or "")
