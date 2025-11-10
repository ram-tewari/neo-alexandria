# Phase 6.5 Quick Start Guide

Get started with scholarly metadata extraction in 5 minutes.

## Prerequisites

- Neo Alexandria 2.0 backend running
- Database migrated to Phase 6.5 schema
- At least one resource ingested

## Step 1: Verify Installation

Check that the migration was applied:

```bash
cd backend
python -m alembic current
```

You should see: `c15f564b1ccd (head)`

## Step 2: Check Available Endpoints

The following new endpoints are available:

```
GET  /scholarly/resources/{id}/metadata
GET  /scholarly/resources/{id}/equations
GET  /scholarly/resources/{id}/tables
POST /scholarly/resources/{id}/metadata/extract
GET  /scholarly/metadata/completeness-stats
```

## Step 3: Extract Metadata for a Resource

### Option A: Automatic (During Ingestion)

Scholarly metadata is automatically extracted for resources that appear to be academic papers (PDFs from arxiv.org, doi.org, etc.).

### Option B: Manual Trigger

Trigger extraction for an existing resource:

```bash
curl -X POST http://localhost:8000/scholarly/resources/YOUR_RESOURCE_ID/metadata/extract \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

## Step 4: View Extracted Metadata

Get the scholarly metadata:

```bash
curl http://localhost:8000/scholarly/resources/YOUR_RESOURCE_ID/metadata
```

Example response:

```json
{
  "resource_id": "...",
  "doi": "10.1234/example.2024.001",
  "authors": [{"name": "John Doe", "affiliation": "MIT"}],
  "publication_year": 2024,
  "journal": "Example Journal",
  "equation_count": 5,
  "table_count": 2,
  "metadata_completeness_score": 0.85,
  "extraction_confidence": 0.92
}
```

## Step 5: Access Structured Content

### Get Equations

```bash
curl http://localhost:8000/scholarly/resources/YOUR_RESOURCE_ID/equations
```

### Get Tables

```bash
curl http://localhost:8000/scholarly/resources/YOUR_RESOURCE_ID/tables
```

## Step 6: Monitor System Statistics

Check extraction coverage across all resources:

```bash
curl http://localhost:8000/scholarly/metadata/completeness-stats
```

## Common Use Cases

### Find Papers by DOI

```python
from backend.app.database import models as db_models
from backend.app.database.base import SessionLocal

db = SessionLocal()

paper = db.query(db_models.Resource).filter(
    db_models.Resource.doi == "10.1234/example.2024.001"
).first()

print(f"Found: {paper.title}")
```

### Find Papers from Specific Year

```python
papers_2024 = db.query(db_models.Resource).filter(
    db_models.Resource.publication_year == 2024
).all()

print(f"Found {len(papers_2024)} papers from 2024")
```

### Find Papers Needing Review

```python
needs_review = db.query(db_models.Resource).filter(
    db_models.Resource.requires_manual_review == True
).all()

print(f"{len(needs_review)} papers need manual review")
```

## Troubleshooting

### No Metadata Extracted

**Problem**: Metadata fields are all null after extraction.

**Solutions**:
- Check if content contains scholarly indicators (DOI, arXiv ID, etc.)
- Verify resource format is supported (PDF, HTML)
- Check extraction confidence score
- Try manual extraction with `force=true`

### Low Completeness Score

**Problem**: `metadata_completeness_score` is below 0.5.

**Solutions**:
- Source document may lack metadata
- Consider manual metadata entry
- Check if content is actually scholarly/academic

### Extraction Failed

**Problem**: Extraction returns error or empty result.

**Solutions**:
- Check server logs for detailed error messages
- Verify resource exists and has content
- Ensure database migration was applied
- Check that required dependencies are installed

## Next Steps

- Read [EXAMPLES_PHASE6_5.md](EXAMPLES_PHASE6_5.md) for detailed usage examples
- Review [PHASE6_5_IMPLEMENTATION_SUMMARY.md](../PHASE6_5_IMPLEMENTATION_SUMMARY.md) for technical details
- Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference

## Optional: Install Advanced Dependencies

For enhanced table extraction from PDFs:

```bash
# Install camelot-py with OpenCV support
pip install "camelot-py[cv]"

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install python3-tk ghostscript

# Install system dependencies (macOS)
brew install tcl-tk ghostscript
```

For OCR support (future feature):

```bash
# Install Tesseract (Ubuntu/Debian)
sudo apt-get install tesseract-ocr

# Install Tesseract (macOS)
brew install tesseract

# Install Tesseract (Windows)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

## Support

For issues or questions:
- Check the [CHANGELOG](CHANGELOG.md) for known issues
- Review test cases in `tests/test_phase6_5_scholarly.py`
- Consult the implementation summary for architecture details
