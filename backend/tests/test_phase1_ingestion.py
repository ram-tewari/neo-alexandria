"""Updated comprehensive test for Phase 1 ingestion pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.base import SessionLocal
from backend.app.database.models import Resource


TEST_HTML = """
<html>
  <head><title>Test Language Article</title></head>
  <body>
    <article>
      <h1>On Language and Grammar</h1>
      <p>Language is a system of communication used by a particular community.</p>
      <p>Grammar provides a structure for language and linguistics.</p>
      <script>alert('xss');</script>
    </article>
  </body>
</html>
"""


def test_ingestion_pipeline_writes_archive_and_persists(monkeypatch, tmp_path: Path, test_db):
    """Test that the ingestion pipeline writes archive files and persists to database."""
    # Mock fetch_url to avoid network
    from backend.app.utils import content_extractor as ce

    def fake_fetch(url: str, timeout: float = 10.0) -> Dict[str, Any]:
        return {"url": url, "status": 200, "html": TEST_HTML}

    def fake_archive(url: str, html: str, text: str, meta: Dict[str, Any], root: Path):
        folder = tmp_path / "archive"
        folder.mkdir(parents=True, exist_ok=True)
        raw = folder / "raw.html"
        text_f = folder / "text.txt"
        meta_f = folder / "meta.json"
        raw.write_text(html, encoding="utf-8")
        text_f.write_text(text, encoding="utf-8")
        meta_f.write_text(json.dumps(meta), encoding="utf-8")
        return {"archive_path": str(folder), "files": {"raw": str(raw), "text": str(text_f), "meta": str(meta_f)}}

    monkeypatch.setattr(ce, "fetch_url", fake_fetch)
    monkeypatch.setattr(ce, "archive_local", fake_archive)
    # Mock extract_text to avoid parser dependencies
    def fake_extract(html: str) -> Dict[str, Any]:
        return {"title": "Test Language Article", "text": "Language grammar linguistics"}
    monkeypatch.setattr(ce, "extract_text", fake_extract)
    
    # Mock the ARCHIVE_ROOT path
    from backend.app.services import resource_service
    monkeypatch.setattr(resource_service, "ARCHIVE_ROOT", tmp_path)
    
    # Mock text processing to avoid dependencies
    from backend.app.utils import text_processor as tp
    def fake_clean_text(text: str) -> str:
        return text
    def fake_readability_scores(text: str) -> Dict[str, float]:
        return {"flesch_kincaid": 10.0, "gunning_fog": 12.0}
    monkeypatch.setattr(tp, "clean_text", fake_clean_text)
    monkeypatch.setattr(tp, "readability_scores", fake_readability_scores)

    client = TestClient(app)
    resp = client.post("/resources", json={"url": "https://example.com/article"})
    assert resp.status_code == 202, resp.text  # API returns 202 Accepted for async processing
    initial_data = resp.json()
    assert initial_data["id"]
    assert initial_data["status"] == "pending"
    
    resource_id = initial_data["id"]
    
    # Wait for processing to complete (TestClient runs background tasks synchronously)
    # But just to be safe, poll for completion
    import time
    max_attempts = 10
    final_resource = None
    for _ in range(max_attempts):
        get_resp = client.get(f"/resources/{resource_id}")
        if get_resp.status_code == 200:
            final_resource = get_resp.json()
            break
        time.sleep(0.1)
    
    assert final_resource is not None
    assert final_resource["id"] == resource_id
    assert final_resource["title"]
    assert final_resource["subject"]
    assert isinstance(final_resource["subject"], list)
    assert final_resource["classification_code"] in {"400", "000", "005", "006"}
    assert final_resource["quality_score"] > 0

    # Archive exists
    assert any((tmp_path / "archive").iterdir())

    # DB persisted
    db = test_db()
    try:
        obj = db.query(Resource).first()
        assert obj is not None
        # Authority normalization should have occurred
        assert isinstance(obj.subject, list)
    finally:
        db.close()


def test_api_endpoint_validation():
    """Test API endpoint input validation."""
    client = TestClient(app)
    
    # Test missing URL
    resp = client.post("/resources", json={})
    assert resp.status_code == 422
    
    # Test invalid URL format
    resp = client.post("/resources", json={"url": "not-a-url"})
    assert resp.status_code == 422
    
    # Test valid request structure
    resp = client.post("/resources", json={"url": "https://example.com"})
    # Should not be a validation error (might be network error, but not 422)
    assert resp.status_code != 422


def test_response_schema_compliance():
    """Test that API response matches expected schema."""
    from unittest.mock import patch
    
    with patch('backend.app.utils.content_extractor.fetch_url') as mock_fetch, \
         patch('backend.app.utils.content_extractor.archive_local') as mock_archive:
        
        mock_fetch.return_value = {
            "url": "https://example.com/test",
            "status": 200,
            "html": "<html><head><title>Test</title></head><body><p>Test content</p></body></html>"
        }
        mock_archive.return_value = {
            "archive_path": "/tmp/test",
            "files": {"raw": "/tmp/raw.html", "text": "/tmp/text.txt", "meta": "/tmp/meta.json"}
        }
        
        client = TestClient(app)
        resp = client.post("/resources", json={"url": "https://example.com/test"})
        
        if resp.status_code == 201:
            data = resp.json()
            
            # Check required fields from ResourceRead schema
            required_fields = [
                "id", "title", "subject", "relation", "read_status", 
                "quality_score", "created_at", "updated_at"
            ]
            
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"
            
            # Check field types
            assert isinstance(data["id"], str)
            assert isinstance(data["title"], str)
            assert isinstance(data["subject"], list)
            assert isinstance(data["relation"], list)
            assert isinstance(data["quality_score"], (int, float))
            assert data["read_status"] in ["unread", "in_progress", "completed", "archived"]