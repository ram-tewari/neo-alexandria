"""
Neo Alexandria 2.0 - Content Extraction and Processing

This module provides comprehensive content extraction capabilities for Neo Alexandria 2.0.
It handles web content extraction, PDF processing, and content archiving with support
for various formats and intelligent content cleaning.

Related files:
- app/services/resource_service.py: Uses content extraction during URL ingestion
- app/utils/text_processor.py: Processes extracted text for quality analysis
- app/config/settings.py: Configuration for content extraction settings

Features:
- Web content extraction with readability processing
- PDF text extraction using multiple backends (PyMuPDF, pdfminer)
- Content archiving with metadata preservation
- Intelligent content cleaning and normalization
- Error handling and fallback mechanisms
- Support for various content types and formats
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from datetime import datetime, timezone

import io
import json
import logging
import httpx
from bs4 import BeautifulSoup
from slugify import slugify

try:
    from readability import Document  # type: ignore
except Exception:  # pragma: no cover - optional dependency fallback
    Document = None  # type: ignore

try:  # PDF extraction primary
    import fitz  # type: ignore  # PyMuPDF
except Exception:  # pragma: no cover - optional
    fitz = None  # type: ignore

try:  # PDF extraction fallback
    from pdfminer.high_level import extract_text as pdfminer_extract_text  # type: ignore
except Exception:  # pragma: no cover - optional
    pdfminer_extract_text = None  # type: ignore

logger = logging.getLogger(__name__)

DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def fetch_url(url: str, timeout: float = 10.0) -> Dict[str, Any]:
    """Fetch a URL using httpx with sane defaults.

    Returns a dict with final URL, status code, headers, raw content bytes, and HTML text when applicable.
    Raises ValueError on network or HTTP errors.
    """
    try:
        with httpx.Client(
            headers={"User-Agent": DESKTOP_UA},
            follow_redirects=True,
            timeout=timeout,
        ) as client:
            resp = client.get(url)
            # Raise for status, but let tests capture original message
            try:
                resp.raise_for_status()
            except Exception as exc:
                raise ValueError(f"Failed to fetch URL: {exc}") from exc
            # Normalize headers to a plain dict for robustness in tests
            raw_headers = getattr(resp, "headers", None)
            if isinstance(raw_headers, dict):
                headers_norm: Dict[str, Any] = raw_headers
            else:
                try:
                    headers_norm = dict(raw_headers.items()) if hasattr(raw_headers, "items") else {}
                except Exception:
                    headers_norm = {}
            content_type = (headers_norm.get("Content-Type") or "").lower()
            data: Dict[str, Any] = {
                "url": str(resp.url),
                "status": resp.status_code,
                "headers": headers_norm,
                "content_bytes": resp.content,
                "content_type": content_type,
            }
            # Back-compat: expose html field for HTML responses and always include for tests
            if "text/html" in content_type or content_type.startswith("text/"):
                data["html"] = resp.text
            else:
                # Always include html field even for non-HTML to avoid KeyError in tests
                data["html"] = resp.text if hasattr(resp, "text") else ""
            return data
    except (httpx.HTTPError, httpx.RequestError, Exception) as exc:  # pragma: no cover - error path
        logger.warning("Fetch failed for %s: %s", url, exc)
        # Preserve message for tests expecting specific substrings
        raise ValueError(f"Failed to fetch URL: {exc}")


def _strip_scripts_and_styles(soup: BeautifulSoup) -> None:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()


def extract_text(html: str) -> Dict[str, Any]:
    """Extract title and main text content from HTML.

    Prefer readability-lxml if available; fallback to BeautifulSoup-only.
    Always strip scripts/styles and return plain text.
    """
    title: str | None = None
    text: str = ""

    if Document is not None:
        try:
            doc = Document(html)
            title = doc.short_title() or None
            summary_html = doc.summary(html_partial=True)
            soup = BeautifulSoup(summary_html, "html.parser")
            _strip_scripts_and_styles(soup)
            text = soup.get_text("\n", strip=True)
        except Exception:
            # Fallback to plain BeautifulSoup
            pass

    if not text:
        soup = BeautifulSoup(html, "html.parser")
        _strip_scripts_and_styles(soup)
        # Best-effort title
        if title is None:
            t = soup.find("title")
            if t and t.text:
                title = t.text.strip() or None
        text = soup.get_text("\n", strip=True)

    return {"title": title, "text": text}


def _looks_like_pdf_bytes(b: Optional[bytes]) -> bool:
    if not b or len(b) < 4:
        return False
    try:
        head = b[:4]
        return head == b"%PDF"
    except Exception:
        return False


def extract_pdf(content_bytes: bytes) -> Dict[str, Any]:
    """Extract text from a PDF byte stream using PyMuPDF, fallback to pdfminer.

    Returns a dict with keys: title (None) and text.
    """
    text_content = ""
    # Primary: PyMuPDF
    if fitz is not None:  # pragma: no cover - depends on optional lib
        try:
            with fitz.open(stream=content_bytes, filetype="pdf") as doc:
                parts = []
                for page in doc:
                    parts.append(page.get_text("text"))
                text_content = "\n".join(parts).strip()
        except Exception as exc:
            logger.info("PyMuPDF failed to parse PDF: %s", exc)
    # Fallback: pdfminer
    if not text_content and pdfminer_extract_text is not None:  # pragma: no cover
        try:
            buf = io.BytesIO(content_bytes)
            text_content = (pdfminer_extract_text(buf) or "").strip()
        except Exception as exc:
            logger.info("pdfminer failed to parse PDF: %s", exc)
    return {"title": None, "text": text_content or ""}


def extract_from_fetched(fetched: Dict[str, Any]) -> Dict[str, Any]:
    """Extract title/text from fetched response supporting HTML and PDF.

    - For HTML: use extract_text on the HTML string
    - For PDF: use extract_pdf on the bytes
    - For others: fallback to text decode if possible
    """
    content_type = (fetched.get("content_type") or "").lower()
    url = fetched.get("url") or ""
    content_bytes: Optional[bytes] = fetched.get("content_bytes")

    # Detect by header, URL extension, or signature
    is_pdf = (
        "application/pdf" in content_type
        or url.lower().endswith(".pdf")
        or _looks_like_pdf_bytes(content_bytes)
    )

    if is_pdf and content_bytes:
        return extract_pdf(content_bytes)

    # HTML path retains compatibility
    html = fetched.get("html")
    if isinstance(html, str):
        return extract_text(html)

    # Fallback: try to decode bytes as UTF-8 text
    if content_bytes:
        try:
            decoded = content_bytes.decode("utf-8", errors="ignore")
            return extract_text(decoded)
        except Exception:
            pass

    return {"title": None, "text": ""}


def _build_archive_folder(url: str, root: Path) -> Path:
    now = datetime.now(timezone.utc)
    y = now.strftime("%Y")
    m = now.strftime("%m")
    d = now.strftime("%d")

    parsed = urlparse(url)
    host = parsed.hostname or "unknown-host"
    path = parsed.path or "/"
    slug_source = f"{host}{path}"
    slug = slugify(slug_source, lowercase=True, separator="-")
    folder = root / y / m / d / slug
    return folder


def archive_local(url: str, html: str, text: str, meta: Dict[str, Any], root: Path) -> Dict[str, Any]:
    """Archive raw HTML, extracted text, and metadata to a deterministic folder.

    Writes UTF-8 files: raw.html, text.txt, meta.json
    Returns paths for the archive and files.
    """
    folder = _build_archive_folder(url, root)
    folder.mkdir(parents=True, exist_ok=True)

    raw_path = folder / "raw.html"
    text_path = folder / "text.txt"
    meta_path = folder / "meta.json"

    # Ensure meta contains minimal required fields
    meta_to_write = dict(meta)
    meta_to_write.setdefault("url", url)
    meta_to_write.setdefault("archived_at", datetime.now(timezone.utc).isoformat())

    # Binary-safe, explicit UTF-8
    raw_path.write_text(html, encoding="utf-8")
    text_path.write_text(text, encoding="utf-8")
    meta_path.write_text(json.dumps(meta_to_write, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "archive_path": str(folder),
        "files": {
            "raw": str(raw_path),
            "text": str(text_path),
            "meta": str(meta_path),
        },
    }


