# Authority API

## Overview

The Authority module manages subject authority files and classification trees, providing controlled vocabularies for resource organization.

**Module**: `app.modules.authority`  
**Router Prefix**: `/authority`  
**Version**: 1.0.0

## Endpoints

### Get Subject Suggestions

Get subject heading suggestions based on input text.

```http
GET /authority/subjects/suggest?q={query}&limit={limit}
```

**Query Parameters:**
- `q` (string, required) - Search query
- `limit` (integer, optional) - Maximum results (default: 10)

**Response:**
```json
{
  "suggestions": [
    {
      "heading": "Machine Learning",
      "code": "006.31",
      "confidence": 0.95,
      "broader_terms": ["Artificial Intelligence"],
      "narrower_terms": ["Deep Learning", "Neural Networks"]
    }
  ]
}
```

### Get Classification Tree

Get the complete classification tree or a subtree.

```http
GET /authority/classification/tree?root={code}&depth={depth}
```

**Query Parameters:**
- `root` (string, optional) - Root classification code (default: top level)
- `depth` (integer, optional) - Tree depth (default: unlimited)

**Response:**
```json
{
  "tree": {
    "code": "000",
    "label": "Computer Science",
    "children": [
      {
        "code": "006",
        "label": "Special Computer Methods",
        "children": [
          {
            "code": "006.3",
            "label": "Artificial Intelligence",
            "children": []
          }
        ]
      }
    ]
  }
}
```

### Health Check

Check module health status.

```http
GET /authority/health
```

**Response:**
```json
{
  "status": "healthy",
  "module": "authority",
  "version": "1.0.0"
}
```

## Module Structure

```python
from app.modules.authority import (
    authority_router,
    AuthorityService,
    SubjectHeading,
    ClassificationNode
)
```

## Related Documentation

- [Architecture: Modules](../architecture/modules.md)
- [Taxonomy API](taxonomy.md)
- [Resources API](resources.md)
