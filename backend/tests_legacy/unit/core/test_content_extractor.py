"""Tests for content extraction utilities."""

import pytest
from unittest.mock import patch, Mock
from pathlib import Path

from backend.app.utils.content_extractor import fetch_url, extract_text, archive_local


class TestFetchUrl:
    """Test URL fetching functionality."""

    def test_fetch_url_success(self):
        """Test successful URL fetching."""
        with patch("httpx.Client") as mock_client:
            mock_response = Mock()
            mock_response.url = "https://example.com"
            mock_response.status_code = 200
            mock_response.text = "<html><body>Test</body></html>"
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__enter__.return_value.get.return_value = (
                mock_response
            )

            result = fetch_url("https://example.com")

            assert result["url"] == "https://example.com"
            assert result["status"] == 200
            assert result["html"] == "<html><body>Test</body></html>"

    def test_fetch_url_http_error(self):
        """Test URL fetching with HTTP error."""
        with patch("httpx.Client") as mock_client:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("HTTP 404")

            mock_client.return_value.__enter__.return_value.get.return_value = (
                mock_response
            )

            with pytest.raises(Exception, match="HTTP 404"):
                fetch_url("https://example.com/notfound")

    def test_fetch_url_network_error(self):
        """Test URL fetching with network error."""
        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__.return_value.get.side_effect = Exception(
                "Network error"
            )

            with pytest.raises(Exception, match="Network error"):
                fetch_url("https://example.com")


class TestExtractText:
    """Test text extraction functionality."""

    def test_extract_text_with_readability(self):
        """Test text extraction with readability-lxml available."""
        html = """
        <html>
        <head><title>Test Article</title></head>
        <body>
            <article>
                <h1>Main Title</h1>
                <p>This is the main content.</p>
                <script>alert('xss');</script>
                <style>body { color: red; }</style>
            </article>
        </body>
        </html>
        """

        with patch("backend.app.utils.content_extractor.Document") as mock_doc:
            mock_doc_instance = Mock()
            mock_doc_instance.short_title.return_value = "Test Article"
            mock_doc_instance.summary.return_value = (
                "<h1>Main Title</h1><p>This is the main content.</p>"
            )
            mock_doc.return_value = mock_doc_instance

            result = extract_text(html)

            assert result["title"] == "Test Article"
            assert "Main Title" in result["text"]
            assert "This is the main content" in result["text"]
            assert "alert('xss')" not in result["text"]
            assert "color: red" not in result["text"]

    def test_extract_text_fallback_to_bs4(self):
        """Test text extraction fallback to BeautifulSoup only."""
        html = """
        <html>
        <head><title>Test Article</title></head>
        <body>
            <h1>Main Title</h1>
            <p>This is the main content.</p>
            <script>alert('xss');</script>
        </body>
        </html>
        """

        with patch("backend.app.utils.content_extractor.Document", None):
            result = extract_text(html)

            assert result["title"] == "Test Article"
            assert "Main Title" in result["text"]
            assert "This is the main content" in result["text"]
            assert "alert('xss')" not in result["text"]

    def test_extract_text_no_title(self):
        """Test text extraction with no title."""
        html = "<html><body><p>Content without title</p></body></html>"

        result = extract_text(html)

        assert result["title"] is None
        assert "Content without title" in result["text"]

    def test_extract_text_empty_html(self):
        """Test text extraction with empty HTML."""
        result = extract_text("")

        assert result["title"] is None
        assert result["text"] == ""


class TestArchiveLocal:
    """Test local archiving functionality."""

    def test_archive_local_creates_files(self, temp_dir):
        """Test that archive_local creates the expected files."""
        html = "<html><body>Test</body></html>"
        text = "Test content"
        meta = {"test": "data"}

        result = archive_local("https://example.com/test", html, text, meta, temp_dir)

        # Check return structure
        assert "archive_path" in result
        assert "files" in result
        assert "raw" in result["files"]
        assert "text" in result["files"]
        assert "meta" in result["files"]

        # Check files exist
        raw_path = Path(result["files"]["raw"])
        text_path = Path(result["files"]["text"])
        meta_path = Path(result["files"]["meta"])

        assert raw_path.exists()
        assert text_path.exists()
        assert meta_path.exists()

        # Check file contents
        assert raw_path.read_text(encoding="utf-8") == html
        assert text_path.read_text(encoding="utf-8") == text

        import json

        meta_content = json.loads(meta_path.read_text(encoding="utf-8"))
        assert meta_content["test"] == "data"
        assert meta_content["url"] == "https://example.com/test"
        assert "archived_at" in meta_content

    def test_archive_local_deterministic_path(self, temp_dir):
        """Test that archive paths are deterministic based on URL and date."""
        html = "<html><body>Test</body></html>"
        text = "Test content"
        meta = {}

        from datetime import datetime, timezone

        fixed_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)

        with patch("backend.app.utils.content_extractor.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_time

            result1 = archive_local(
                "https://example.com/test", html, text, meta, temp_dir
            )
            result2 = archive_local(
                "https://example.com/test", html, text, meta, temp_dir
            )

            # Same URL should produce same path
            assert result1["archive_path"] == result2["archive_path"]

    def test_archive_local_different_urls(self, temp_dir):
        """Test that different URLs produce different paths."""
        html = "<html><body>Test</body></html>"
        text = "Test content"
        meta = {}

        result1 = archive_local("https://example.com/test1", html, text, meta, temp_dir)
        result2 = archive_local("https://example.com/test2", html, text, meta, temp_dir)

        # Different URLs should produce different paths
        assert result1["archive_path"] != result2["archive_path"]
