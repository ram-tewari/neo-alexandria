# Collections Module

## Overview

The Collections module provides functionality for managing user-curated collections of resources in Neo Alexandria. It supports hierarchical organization, visibility controls, and semantic similarity-based recommendations.

## Purpose

This module enables users to:
- **Organize Resources**: Group related resources into collections
- **Hierarchical Structure**: Create nested collections (folders/subfolders)
- **Visibility Control**: Manage private, shared, and public collections
- **Semantic Discovery**: Find similar resources based on collection content
- **Batch Operations**: Add/remove multiple resources efficiently
- **Collaboration**: Share collections with other users

## Module Structure

```
collections/
├── __init__.py          # Public interface and module metadata
├── router.py            # FastAPI endpoints (7 endpoints)
├── service.py           # Business logic for collection management
├── schema.py            # Pydantic schemas for validation
├── model.py             # SQLAlchemy models (Collection, CollectionResource)
├── handlers.py          # Event handlers for cross-module communication
├── README.md            # This file
└── tests/
    ├── test_service.py
    ├── test_router.py
    └── test_handlers.py
```

## Public Interface

### Router
```python
from app.modules.collections import collections_router

# Endpoints:
# POST /collections - Create collection
# GET /collections - List user collections
# GET /collections/{id} - Get collection with resources
# PUT /collections/{id} - Update collection
# DELETE /collections/{id} - Delete collection
# PUT /collections/{id}/resources - Batch add/remove resources
# GET /collections/{id}/recommendations - Get similar resources
```

### Service
```python
from app.modules.collections import CollectionService

service = CollectionService(db)
# Methods:
# - create_collection(data: CollectionCreate) -> Collection
# - get_collection(collection_id: UUID, owner_id: str) -> Collection
# - list_collections(owner_id: str, filters) -> List[Collection]
# - update_collection(collection_id: UUID, data: CollectionUpdate) -> Collection
# - delete_collection(collection_id: UUID, owner_id: str) -> None
# - add_resources_to_collection(collection_id: UUID, resource_ids: List[UUID]) -> int
# - remove_resources_from_collection(collection_id: UUID, resource_ids: List[UUID]) -> int
# - get_collection_resources(collection_id: UUID) -> List[Resource]
# - compute_collection_embedding(collection_id: UUID) -> np.ndarray
# - find_similar_resources(collection_id: UUID, limit: int) -> List[Resource]
# - find_collections_with_resource(resource_id: UUID, owner_id: str) -> List[Collection]
```

### Schemas
```python
from app.modules.collections import (
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    CollectionListResponse,
    CollectionResourcesResponse,
    BatchResourceOperation,
    SimilarResourcesResponse
)
```

### Models
```python
from app.modules.collections import Collection, CollectionResource

# Collection model fields:
# - id: UUID
# - name: str
# - description: Optional[str]
# - owner_id: str
# - visibility: Enum (private, shared, public)
# - parent_id: Optional[UUID]
# - embedding: Optional[vector]
# - created_at, updated_at: datetime

# CollectionResource model fields:
# - collection_id: UUID (FK)
# - resource_id: UUID (FK)
# - added_at: datetime
```

## Events

### Emitted Events

#### collection.created
Emitted when a new collection is created.
```python
{
    "collection_id": str,
    "name": str,
    "owner_id": str,
    "visibility": str,
    "timestamp": datetime
}
```

#### collection.updated
Emitted when a collection is modified.
```python
{
    "collection_id": str,
    "updated_fields": List[str],
    "owner_id": str,
    "timestamp": datetime
}
```

#### collection.deleted
Emitted when a collection is deleted.
```python
{
    "collection_id": str,
    "owner_id": str,
    "resource_count": int,
    "timestamp": datetime
}
```

#### collection.resource_added
Emitted when resources are added to a collection.
```python
{
    "collection_id": str,
    "resource_ids": List[str],
    "owner_id": str,
    "timestamp": datetime
}
```

#### collection.resource_removed
Emitted when resources are removed from a collection.
```python
{
    "collection_id": str,
    "resource_ids": List[str],
    "owner_id": str,
    "timestamp": datetime
}
```

### Subscribed Events

#### resource.deleted
Triggered when a resource is deleted from the system.

**Handler**: `handle_resource_deleted(payload)`

**Action**: 
- Removes resource from all collections
- Recomputes embeddings for affected collections
- Emits collection.updated events

## Dependencies

### Shared Kernel
- `shared.database`: Database session management
- `shared.event_bus`: Event-driven communication
- `shared.base_model`: Base SQLAlchemy model
- `shared.embeddings`: Embedding generation for collections

### External Libraries
- `sqlalchemy`: ORM
- `numpy`: Vector operations for embeddings

## Usage Examples

### Create a Collection
```python
from app.modules.collections import CollectionService, CollectionCreate

service = CollectionService(db)
collection = await service.create_collection(
    CollectionCreate(
        name="Machine Learning Papers",
        description="Curated ML research papers",
        owner_id="user123",
        visibility="private"
    )
)
```

### Add Resources to Collection
```python
added_count = await service.add_resources_to_collection(
    collection_id=collection.id,
    resource_ids=[resource1_id, resource2_id, resource3_id],
    owner_id="user123"
)
print(f"Added {added_count} resources")
```

### Get Collection with Resources
```python
collection = await service.get_collection(
    collection_id=collection.id,
    owner_id="user123"
)
resources = await service.get_collection_resources(collection.id)
```

### Find Similar Resources
```python
similar = await service.find_similar_resources(
    collection_id=collection.id,
    owner_id="user123",
    limit=20,
    min_similarity=0.7
)
```

### Create Nested Collections
```python
parent = await service.create_collection(
    CollectionCreate(name="Computer Science", owner_id="user123")
)
child = await service.create_collection(
    CollectionCreate(
        name="Machine Learning",
        parent_id=parent.id,
        owner_id="user123"
    )
)
```

## Integration Patterns

### Event-Driven Integration
```python
from app.shared.event_bus import event_bus

# Subscribe to collection events
@event_bus.subscribe("collection.resource_added")
async def handle_resource_added(payload):
    collection_id = payload["collection_id"]
    # Update recommendations, analytics, etc.
```

### Cascade Deletion
```python
# When a resource is deleted, collections are automatically updated
@event_bus.subscribe("resource.deleted")
async def handle_resource_deleted(payload):
    resource_id = payload["resource_id"]
    # Remove from all collections
    # Recompute collection embeddings
```

## Testing

### Unit Tests
```bash
pytest backend/tests/modules/test_collections_endpoints.py -v
```

### Integration Tests
```bash
pytest backend/tests/integration/ -k collections -v
```

### Test Coverage
- Collection CRUD operations
- Resource membership management
- Hierarchical organization
- Visibility controls
- Embedding computation
- Event handling
- Error handling

## Performance Considerations

- **Embedding Caching**: Collection embeddings cached after computation
- **Batch Operations**: Optimized for adding/removing multiple resources
- **Lazy Loading**: Resources loaded on demand, not with collection
- **Indexing**: Database indexes on owner_id, parent_id, visibility
- **Pagination**: List endpoints support cursor-based pagination

## Troubleshooting

### Issue: Collection Embedding Not Computed
**Solution**: Ensure resources have embeddings. Trigger recomputation via API.

### Issue: Cannot Delete Collection with Subcollections
**Solution**: Delete child collections first, or implement cascade deletion.

### Issue: Visibility Controls Not Working
**Solution**: Verify owner_id matches authenticated user. Check visibility enum values.

### Issue: Similar Resources Returns Empty
**Solution**: Ensure collection has embedding. Check min_similarity threshold.

## Related Modules

- **Resources**: Collections contain resources
- **Recommendations**: Collection-based recommendations
- **Search**: Search within collections
- **Annotations**: Annotations can be associated with collections

## Version History

- **1.0.0** (Phase 14): Initial extraction from layered architecture
  - Moved from `routers/collections.py` and `services/collection_service.py`
  - Implemented event-driven communication
  - Added module isolation

## Module Metadata

- **Version**: 1.0.0
- **Domain**: collections
- **Phase**: 14 (Complete Vertical Slice Refactor)
