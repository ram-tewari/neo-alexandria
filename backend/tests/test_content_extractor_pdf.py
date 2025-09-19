"""Tests for PDF extraction functionality."""

import pytest
from unittest.mock import patch, Mock
import io

from backend.app.utils.content_extractor import (
    fetch_url, extract_from_fetched, extract_pdf, _looks_like_pdf_bytes
)


class TestPDFDetection:
    """Test PDF detection functionality."""
    
    def test_looks_like_pdf_bytes_valid(self):
        """Test PDF detection with valid PDF header."""
        pdf_bytes = b"%PDF-1.4\nSome PDF content here"
        assert _looks_like_pdf_bytes(pdf_bytes) is True
    
    def test_looks_like_pdf_bytes_invalid(self):
        """Test PDF detection with invalid content."""
        html_bytes = b"<html><body>Not a PDF</body></html>"
        assert _looks_like_pdf_bytes(html_bytes) is False
    
    def test_looks_like_pdf_bytes_empty(self):
        """Test PDF detection with empty content."""
        assert _looks_like_pdf_bytes(b"") is False
        assert _looks_like_pdf_bytes(None) is False
    
    def test_looks_like_pdf_bytes_short(self):
        """Test PDF detection with content too short."""
        assert _looks_like_pdf_bytes(b"PDF") is False


class TestPDFExtraction:
    """Test PDF text extraction functionality."""
    
    def test_extract_pdf_with_pymupdf(self):
        """Test PDF extraction using PyMuPDF."""
        # Mock PDF content
        mock_pdf_content = "This is extracted text from a PDF document. It contains multiple sentences."
        
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = mock_pdf_content
        mock_doc.__enter__ = Mock(return_value=mock_doc)
        mock_doc.__exit__ = Mock(return_value=None)
        mock_doc.__iter__ = Mock(return_value=iter([mock_page]))
        
        with patch('backend.app.utils.content_extractor.fitz') as mock_fitz:
            mock_fitz.open.return_value = mock_doc
            result = extract_pdf(b"%PDF-1.4\nfake pdf content")
            
            assert result["title"] is None
            assert result["text"] == mock_pdf_content
            mock_fitz.open.assert_called_once()
    
    def test_extract_pdf_with_pdfminer_fallback(self):
        """Test PDF extraction using pdfminer fallback."""
        mock_pdf_content = "This is text extracted using pdfminer."
        
        with patch('backend.app.utils.content_extractor.fitz', None), \
             patch('backend.app.utils.content_extractor.pdfminer_extract_text') as mock_pdfminer:
            mock_pdfminer.return_value = mock_pdf_content
            
            result = extract_pdf(b"%PDF-1.4\nfake pdf content")
            
            assert result["title"] is None
            assert result["text"] == mock_pdf_content
            mock_pdfminer.assert_called_once()
    
    def test_extract_pdf_no_libraries(self):
        """Test PDF extraction when no PDF libraries are available."""
        with patch('backend.app.utils.content_extractor.fitz', None), \
             patch('backend.app.utils.content_extractor.pdfminer_extract_text', None):
            result = extract_pdf(b"%PDF-1.4\nfake pdf content")
            
            assert result["title"] is None
            assert result["text"] == ""
    
    def test_extract_pdf_pymupdf_error_fallback(self):
        """Test PDF extraction falls back to pdfminer when PyMuPDF fails."""
        mock_pdf_content = "Text from pdfminer after PyMuPDF failed."
        
        with patch('backend.app.utils.content_extractor.fitz') as mock_fitz, \
             patch('backend.app.utils.content_extractor.pdfminer_extract_text') as mock_pdfminer:
            mock_fitz.open.side_effect = Exception("PyMuPDF error")
            mock_pdfminer.return_value = mock_pdf_content
            
            result = extract_pdf(b"%PDF-1.4\nfake pdf content")
            
            assert result["title"] is None
            assert result["text"] == mock_pdf_content
            mock_pdfminer.assert_called_once()
    
    def test_extract_pdf_both_libraries_fail(self):
        """Test PDF extraction when both libraries fail."""
        with patch('backend.app.utils.content_extractor.fitz') as mock_fitz, \
             patch('backend.app.utils.content_extractor.pdfminer_extract_text') as mock_pdfminer:
            mock_fitz.open.side_effect = Exception("PyMuPDF error")
            mock_pdfminer.side_effect = Exception("pdfminer error")
            
            result = extract_pdf(b"%PDF-1.4\nfake pdf content")
            
            assert result["title"] is None
            assert result["text"] == ""


class TestContentTypeDetection:
    """Test content type detection and extraction routing."""
    
    def test_extract_from_fetched_html(self):
        """Test extraction from HTML content."""
        fetched_data = {
            "content_type": "text/html",
            "html": "<html><head><title>Test</title></head><body><p>Test content</p></body></html>",
            "url": "https://example.com/test.html"
        }
        
        result = extract_from_fetched(fetched_data)
        
        assert result["title"] == "Test"
        assert "Test content" in result["text"]
    
    def test_extract_from_fetched_pdf_by_content_type(self):
        """Test extraction from PDF content detected by content type."""
        pdf_bytes = b"%PDF-1.4\nfake pdf content"
        fetched_data = {
            "content_type": "application/pdf",
            "content_bytes": pdf_bytes,
            "url": "https://example.com/test.pdf"
        }
        
        with patch('backend.app.utils.content_extractor.extract_pdf') as mock_extract_pdf:
            mock_extract_pdf.return_value = {"title": None, "text": "PDF text content"}
            
            result = extract_from_fetched(fetched_data)
            
            assert result["title"] is None
            assert result["text"] == "PDF text content"
            mock_extract_pdf.assert_called_once_with(pdf_bytes)
    
    def test_extract_from_fetched_pdf_by_url_extension(self):
        """Test extraction from PDF content detected by URL extension."""
        pdf_bytes = b"%PDF-1.4\nfake pdf content"
        fetched_data = {
            "content_type": "application/octet-stream",
            "content_bytes": pdf_bytes,
            "url": "https://example.com/document.PDF"
        }
        
        with patch('backend.app.utils.content_extractor.extract_pdf') as mock_extract_pdf:
            mock_extract_pdf.return_value = {"title": None, "text": "PDF text content"}
            
            result = extract_from_fetched(fetched_data)
            
            assert result["title"] is None
            assert result["text"] == "PDF text content"
            mock_extract_pdf.assert_called_once_with(pdf_bytes)
    
    def test_extract_from_fetched_pdf_by_signature(self):
        """Test extraction from PDF content detected by file signature."""
        pdf_bytes = b"%PDF-1.4\nfake pdf content"
        fetched_data = {
            "content_type": "application/octet-stream",
            "content_bytes": pdf_bytes,
            "url": "https://example.com/document"
        }
        
        with patch('backend.app.utils.content_extractor.extract_pdf') as mock_extract_pdf:
            mock_extract_pdf.return_value = {"title": None, "text": "PDF text content"}
            
            result = extract_from_fetched(fetched_data)
            
            assert result["title"] is None
            assert result["text"] == "PDF text content"
            mock_extract_pdf.assert_called_once_with(pdf_bytes)
    
    def test_extract_from_fetched_fallback_text_decode(self):
        """Test extraction fallback to text decoding."""
        text_bytes = b"This is plain text content"
        fetched_data = {
            "content_type": "text/plain",
            "content_bytes": text_bytes,
            "url": "https://example.com/test.txt"
        }
        
        result = extract_from_fetched(fetched_data)
        
        assert "This is plain text content" in result["text"]
    
    def test_extract_from_fetched_no_content(self):
        """Test extraction with no usable content."""
        fetched_data = {
            "content_type": "application/octet-stream",
            "content_bytes": b"",
            "url": "https://example.com/empty"
        }
        
        result = extract_from_fetched(fetched_data)
        
        assert result["title"] is None
        assert result["text"] == ""


class TestFetchURLEnhancements:
    """Test enhanced fetch_url functionality."""
    
    def test_fetch_url_returns_content_bytes(self):
        """Test fetch_url returns content bytes for PDF processing."""
        mock_response = Mock()
        mock_response.url = "https://example.com/test.pdf"
        mock_response.status_code = 200
        mock_response.text = "HTML content"
        mock_response.content = b"PDF binary content"
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.raise_for_status.return_value = None
        
        with patch('httpx.Client') as mock_client:
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response
            
            result = fetch_url("https://example.com/test.pdf")
            
            assert result["url"] == "https://example.com/test.pdf"
            assert result["status"] == 200
            assert result["content_bytes"] == b"PDF binary content"
            assert result["content_type"] == "application/pdf"
            assert result["headers"]["Content-Type"] == "application/pdf"
    
    def test_fetch_url_html_content_type(self):
        """Test fetch_url handles HTML content type correctly."""
        mock_response = Mock()
        mock_response.url = "https://example.com/test.html"
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.content = b"<html><body>Test</body></html>"
        mock_response.headers = {"Content-Type": "text/html; charset=utf-8"}
        mock_response.raise_for_status.return_value = None
        
        with patch('httpx.Client') as mock_client:
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response
            
            result = fetch_url("https://example.com/test.html")
            
            assert result["content_type"] == "text/html; charset=utf-8"
            assert result["html"] == "<html><body>Test</body></html>"
            assert result["content_bytes"] == b"<html><body>Test</body></html>"
    
    def test_fetch_url_network_error(self):
        """Test fetch_url handles network errors."""
        with patch('httpx.Client') as mock_client:
            mock_client.return_value.__enter__.return_value.get.side_effect = Exception("Network error")
            
            with pytest.raises(ValueError, match="Failed to fetch URL: Network error"):
                fetch_url("https://example.com/test")
    
    def test_fetch_url_http_error(self):
        """Test fetch_url handles HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")
        
        with patch('httpx.Client') as mock_client:
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response
            
            with pytest.raises(ValueError, match="Failed to fetch URL: HTTP 404"):
                fetch_url("https://example.com/notfound")
