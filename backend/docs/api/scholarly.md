# Scholarly API

Academic metadata extraction endpoints for scholarly resources.

## Overview

The Scholarly API provides functionality for extracting and accessing academic metadata from scholarly resources including:
- Author information and affiliations
- Publication identifiers (DOI, PMID, arXiv ID, ISBN)
- Journal and conference details
- Equations and tables extraction
- Metadata completeness scoring
- OCR processing for scanned documents

## Endpoints

### GET /scholarly/resources/{resource_id}/metadata

Get complete scholarly metadata for a resource.

Returns all extracted scholarly fields including authors, DOI, publication details, and structural content counts.

**Response:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "authors": [
    {
      "name": "John Doe",
      "affiliation": "MIT",
      "email": "john@mit.edu"
    }
  ],
  "affiliations": ["MIT", "Stanford University"],
  "doi": "10.1234/example.2024",
  "pmid": "12345678",
  "arxiv_id": "2024.12345",
  "isbn": "978-3-16-148410-0",
  "journal": "Nature Machine Learning",
  "conference": null,
  "volume": "15",
  "issue": "3",
  "pages": "123-145",
  "publication_year": 2024,
  "funding_sources": ["NSF Grant 12345", "NIH Grant 67890"],
  "acknowledgments": "We thank...",
  "equation_count": 15,
  "table_count": 3,
  "figure_count": 8,
  "reference_count": 42,
  "metadata_completeness_score": 0.92,
  "extraction_confidence": 0.88,
  "requires_manual_review": false,
  "is_ocr_processed": false,
  "ocr_confidence": null,
  "ocr_corrections_applied": null
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/scholarly/resources/550e8400-e29b-41d4-a716-446655440000/metadata"
```

---

### GET /scholarly/resources/{resource_id}/equations

Get all equations from a resource.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `format` | string | Output format: "latex" or "mathml" | latex |

**Response:**
```json
[
  {
    "latex": "E = mc^2",
    "position": 1250,
    "context": "Einstein's famous equation",
    "is_numbered": true,
    "equation_number": "1"
  },
  {
    "latex": "\\frac{\\partial u}{\\partial t} = \\nabla^2 u",
    "position": 2500,
    "context": "Heat equation",
    "is_numbered": true,
    "equation_number": "2"
  }
]
```

**Example:**
```bash
curl "http://127.0.0.1:8000/scholarly/resources/550e8400-e29b-41d4-a716-446655440000/equations?format=latex"
```

---

### GET /scholarly/resources/{resource_id}/tables

Get all tables from a resource.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `include_data` | boolean | Include table data (false for metadata only) | true |

**Response:**
```json
[
  {
    "caption": "Experimental Results",
    "position": 3500,
    "headers": ["Method", "Accuracy", "F1-Score"],
    "rows": [
      ["Baseline", "0.75", "0.72"],
      ["Our Method", "0.89", "0.87"]
    ],
    "table_number": "1"
  }
]
```

**Example:**
```bash
curl "http://127.0.0.1:8000/scholarly/resources/550e8400-e29b-41d4-a716-446655440000/tables?include_data=true"
```

---

### POST /scholarly/resources/{resource_id}/metadata/extract

Manually trigger scholarly metadata extraction.

**Request Body:**
```json
{
  "force": false
}
```

**Response (202 Accepted):**
```json
{
  "status": "queued",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Metadata extraction queued for processing"
}
```

**Status Values:**
- `already_processed` - Metadata already extracted (use force=true to re-extract)
- `queued` - Extraction task queued for background processing
- `completed` - Extraction completed synchronously

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/scholarly/resources/550e8400-e29b-41d4-a716-446655440000/metadata/extract" \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

---

### GET /scholarly/metadata/{resource_id}

Get scholarly metadata for a resource (convenience alias).

Alias for `/scholarly/resources/{resource_id}/metadata`.

**Response:** Same as `/scholarly/resources/{resource_id}/metadata`

---

### GET /scholarly/equations/{resource_id}

Get equations for a resource (convenience alias).

Alias for `/scholarly/resources/{resource_id}/equations`.

**Response:** Same as `/scholarly/resources/{resource_id}/equations`

---

### GET /scholarly/tables/{resource_id}

Get tables for a resource (convenience alias).

Alias for `/scholarly/resources/{resource_id}/tables`.

**Response:** Same as `/scholarly/resources/{resource_id}/tables`

---

### GET /scholarly/metadata/completeness-stats

Get aggregate statistics on metadata completeness.

**Response:**
```json
{
  "total_resources": 1250,
  "with_doi": 850,
  "with_authors": 1100,
  "with_publication_year": 1050,
  "avg_completeness_score": 0.78,
  "requires_review_count": 125,
  "by_content_type": {
    "application/pdf": 800,
    "text/html": 350,
    "text/plain": 100
  }
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/scholarly/metadata/completeness-stats"
```

---

### GET /scholarly/health

Health check endpoint for Scholarly module.

**Response:**
```json
{
  "status": "healthy",
  "module": "scholarly",
  "database": true,
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## Data Models

### Author Model

```json
{
  "name": "string (required)",
  "affiliation": "string (optional)",
  "email": "string (optional)",
  "orcid": "string (optional)"
}
```

### Equation Model

```json
{
  "latex": "string (required)",
  "position": "integer",
  "context": "string",
  "is_numbered": "boolean",
  "equation_number": "string (optional)"
}
```

### Table Model

```json
{
  "caption": "string",
  "position": "integer",
  "headers": ["string"],
  "rows": [["string"]],
  "table_number": "string (optional)"
}
```

### Scholarly Metadata Model

```json
{
  "resource_id": "uuid",
  "authors": ["Author"],
  "affiliations": ["string"],
  "doi": "string",
  "pmid": "string",
  "arxiv_id": "string",
  "isbn": "string",
  "journal": "string",
  "conference": "string",
  "volume": "string",
  "issue": "string",
  "pages": "string",
  "publication_year": "integer",
  "funding_sources": ["string"],
  "acknowledgments": "string",
  "equation_count": "integer",
  "table_count": "integer",
  "figure_count": "integer",
  "reference_count": "integer",
  "metadata_completeness_score": "float (0.0-1.0)",
  "extraction_confidence": "float (0.0-1.0)",
  "requires_manual_review": "boolean",
  "is_ocr_processed": "boolean",
  "ocr_confidence": "float (0.0-1.0)",
  "ocr_corrections_applied": "integer"
}
```

## Module Structure

The Scholarly module is implemented as a self-contained vertical slice:

**Module**: `app.modules.scholarly`  
**Router Prefix**: `/scholarly`  
**Version**: 1.0.0

```python
from app.modules.scholarly import (
    router,
    MetadataExtractor,
    ScholarlyMetadataResponse,
    Equation,
    TableData
)
```

### Events

**Emitted Events:**
- `metadata.extracted` - When scholarly metadata is extracted
- `equations.parsed` - When equations are parsed from content
- `tables.extracted` - When tables are extracted from content

**Subscribed Events:**
- `resource.created` - Triggers metadata extraction for new resources

## Related Documentation

- [Resources API](resources.md) - Resource management
- [Quality API](quality.md) - Quality assessment
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors, pagination
