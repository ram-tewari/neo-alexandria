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
GET /authority/subjects/suggest?q={query}
```

**Query Parameters:**
- `q` (string, required) - Search query (minimum 1 character)

**Response:**
```json
[
  "Machine Learning",
  "Artificial Intelligence",
  "Deep Learning",
  "Neural Networks"
]
```

### Get Classification Tree

Get the complete classification tree or a subtree.

```http
GET /authority/classification/tree
```

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
