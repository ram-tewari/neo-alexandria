# Resources Module

## Overview

The Resources module is responsible for managing the core resource entities in Neo Alexandria. It handles URL ingestion, content processing, metadata extraction, and resource lifecycle management.

## Purpose

This module provides:
- **URL Ingestion**: Asynchronous processing of web resources with content extraction
- **CRUD Operations**: Create, read, update, and delete resources
- **Metadata Management**: Dublin Core metadata with scholarly extensions
- **Quality Assessment**: Automated quality scoring and classification
- **Search Integration**: Dense and sparse embeddings for hybrid search

## Public Interface

### Router
- `resources_router`: FastAPI router with resource endpoints

### Service
- `ResourceService`: Business logic for resource operations

### Schemas
- `ResourceCreate`: Schema for creating resources
- `ResourceUpdate`: Schema for updating resources
- `ResourceRead`: Schema for reading resources
- `ResourceStatus`: Schema for ingestion status

### Models
- `Resource`: SQLAlchemy model for resource entities

## Events

### Emitted Events
- `resource.created`: When a new resource is created
- `resource.updated`: When a resource is updated
- `resource.deleted`: When a resource is deleted
- `resource.content_changed`: When resource content is modified
- `resource.metadata_changed`: When resource metadata is modified
- `ingestion.started`: When ingestion begins
- `ingestion.completed`: When ingestion completes successfully
- `ingestion.failed`: When ingestion fails

### Subscribed Events
- `collection.updated`: Placeholder for future collection-related updates

## Dependencies

### Shared Kernel
- `shared.database`: Database session management
- `shared.event_bus`: Event-driven communication
- `shared.base_model`: Base model classes

### External Services
- AI Core: For embeddings and summarization
- Classification Service: For automatic classification
- Quality Service: For quality assessment
- Authority Control: For metadata normalization

## Architecture

The Resources module follows the vertical slice architecture pattern:
- **Router**: HTTP endpoints and request/response handling
- **Service**: Business logic and orchestration
- **Model**: Data persistence layer
- **Schema**: Data validation and serialization
- **Handlers**: Event-driven integration with other modules

## Usage Example

```python
from app.modules.resources import resources_router, ResourceService
from app.shared.database import get_db

# Register router in main application
app.include_router(resources_router, prefix="/api")

# Use service in business logic
service = ResourceService(db)
resource = service.create_resource({"url": "https://example.com"})
```

## Testing

Tests are located in `tests/` directory:
- `test_service.py`: Service layer tests
- `test_router.py`: API endpoint tests
- `test_handlers.py`: Event handler tests

## Related Modules

- **Collections**: Resources can be organized into collections
- **Search**: Resources are indexed for search
- **Quality**: Resources have quality scores computed
- **Classification**: Resources are automatically classified
