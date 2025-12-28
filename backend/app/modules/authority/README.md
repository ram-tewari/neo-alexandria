# Authority Module

## Overview

The Authority module provides subject authority control and classification tree management for Neo Alexandria 2.0. It handles normalization of subjects, creators, and publishers with canonical forms, variants, and usage tracking.

## Purpose

This module centralizes authority control functionality, ensuring consistent naming and organization of subjects, creators, and publishers across the system. It also provides access to the hierarchical classification tree for UI navigation.

## Components

### Router (`router.py`)
- `GET /authority/subjects/suggest` - Get subject suggestions based on partial input
- `GET /authority/classification/tree` - Get hierarchical classification tree

### Service (`service.py`)
- `AuthorityControl` - Subject, creator, and publisher normalization
- `PersonalClassification` - Classification tree management and rule-based classification

### Schemas (`schema.py`)
- Currently no custom schemas (uses built-in types)

## Public Interface

```python
from app.modules.authority import (
    authority_router,
    AuthorityService,
    PersonalClassification
)
```

## Events

### Emitted Events
- None (read-only module)

### Subscribed Events
- None (read-only module)

## Dependencies

### Shared Kernel
- `app.shared.database` - Database session management

### External Dependencies
- SQLAlchemy ORM for database operations
- FastAPI for routing

## Usage Examples

### Subject Normalization
```python
from app.modules.authority import AuthorityService

service = AuthorityService(db)
canonical = service.normalize_subject("ml")  # Returns "Machine Learning"
```

### Subject Suggestions
```python
# GET /authority/subjects/suggest?q=mach
# Returns: ["Machine Learning", "Mathematics", ...]
```

### Classification Tree
```python
# GET /authority/classification/tree
# Returns hierarchical tree of classification codes
```

## Module Metadata

- **Version**: 1.0.0
- **Domain**: authority
- **Phase**: 14 (Complete Vertical Slice Refactor)

## Related Modules

- **Resources** - Uses authority control during resource ingestion
- **Taxonomy** - Shares classification functionality

## Testing

Tests for this module should be located in:
- `backend/tests/unit/authority/` - Unit tests
- `backend/tests/integration/authority/` - Integration tests

## Migration Notes

This module was extracted from:
- `app/routers/authority.py` → `app/modules/authority/router.py`
- `app/services/authority_service.py` → `app/modules/authority/service.py`
- Classification tree functionality from `app/services/classification_service.py`

## Requirements

Implements requirements:
- 10.1: Authority router migration
- 10.2: Authority service migration
- 10.3: Public interface exposure
- 10.4: Subject suggestion and classification tree endpoints
