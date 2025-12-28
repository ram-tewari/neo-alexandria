# Scholarly API

## Overview

The Scholarly module provides academic metadata extraction from resources, including equations, tables, citations, and scholarly metadata.

**Module**: `app.modules.scholarly`  
**Router Prefix**: `/scholarly`  
**Version**: 1.0.0

## Endpoints

### Extract Metadata

Extract scholarly metadata from a resource.

```http
POST /scholarly/extract/{resource_id}
```

**Path Parameters:**
- `resource_id` (integer, required) - Resource ID

**Response:**
```json
{
  "resource_id": 1,
  "equations": [
    {
      "id": 1,
      "latex": "E = mc^2",
      "context": "Einstein's mass-energy equivalence"
    }
  ],
  "tables": [
    {
      "id": 1,
      "caption": "Experimental Results",
      "data": {...}
    }
  ],
  "metadata": {
    "authors": ["John Doe"],
    "publication_date": "2024-01-01",
    "journal": "Nature",
    "doi": "10.1234/example"
  }
}
```

### Get Resource Metadata

Get scholarly metadata for a resource.

```http
GET /scholarly/resources/{resource_id}/metadata
```

**Path Parameters:**
- `resource_id` (integer, required) - Resource ID

**Response:**
```json
{
  "resource_id": 1,
  "authors": ["John Doe", "Jane Smith"],
  "publication_date": "2024-01-01",
  "journal": "Nature",
  "volume": "123",
  "issue": "4",
  "pages": "567-890",
  "doi": "10.1234/example",
  "abstract": "This paper presents..."
}
```

### Get Equations

Get all equations extracted from a resource.

```http
GET /scholarly/resources/{resource_id}/equations
```

**Path Parameters:**
- `resource_id` (integer, required) - Resource ID

**Response:**
```json
{
  "equations": [
    {
      "id": 1,
      "latex": "E = mc^2",
      "context": "Einstein's mass-energy equivalence",
      "position": 42
    }
  ]
}
```

### Get Tables

Get all tables extracted from a resource.

```http
GET /scholarly/resources/{resource_id}/tables
```

**Path Parameters:**
- `resource_id` (integer, required) - Resource ID

**Response:**
```json
{
  "tables": [
    {
      "id": 1,
      "caption": "Experimental Results",
      "headers": ["Condition", "Result", "P-value"],
      "rows": [
        ["Control", "0.5", "0.001"],
        ["Treatment", "0.8", "0.001"]
      ]
    }
  ]
}
```

### Health Check

Check module health status.

```http
GET /scholarly/health
```

**Response:**
```json
{
  "status": "healthy",
  "module": "scholarly",
  "version": "1.0.0"
}
```

## Events

### Emitted Events

- `metadata.extracted` - When scholarly metadata is extracted
- `equations.parsed` - When equations are parsed from content
- `tables.extracted` - When tables are extracted from content

### Subscribed Events

- `resource.created` - Triggers automatic metadata extraction

## Module Structure

```python
from app.modules.scholarly import (
    scholarly_router,
    MetadataExtractor,
    ScholarlyMetadata,
    Equation,
    Table
)
```

## Related Documentation

- [Architecture: Modules](../architecture/modules.md)
- [Architecture: Events](../architecture/events.md)
- [Resources API](resources.md)
