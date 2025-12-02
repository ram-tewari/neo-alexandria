# Collections Module

## Overview

The Collections module provides functionality for managing user-curated collections of resources in Neo Alexandria. It supports hierarchical organization, visibility controls, and semantic similarity-based recommendations.

## Features

- **Collection CRUD**: Create, read, update, and delete collections
- **Resource Membership**: Add and remove resources from collections
- **Hierarchical Organization**: Support for parent/subcollections
- **Visibility Controls**: Private, shared, and public collections
- **Semantic Embeddings**: Collection-level embeddings computed from member resources
- **Recommendations**: Find similar resources based on collection embedding

## Architecture

### Components

- **router.py**: FastAPI endpoints for collection operations
- **service.py**: Business logic for collection management
- **schema.py**: Pydantic models for request/response validation
- **model.py**: SQLAlchemy models for Collection and CollectionResource
- **handlers.py**: Event handlers for cross-module communication

### Dependencies

- **Shared Kernel**: Uses `shared.database`, `shared.event_bus`, and `shared.base_model`
- **No Direct Module Dependencies**: Communicates with other modules via events

## Public API

### Router Endpoints

- `POST /collections`: Create a new collection
- `GET /collections`: List user's collections
- `GET /collections/{id}`: Retrieve a specific collection with resources
- `PUT /collections/{id}`: Update collection metadata
- `DELETE /collections/{id}`: Delete a collection
- `PUT /collections/{id}/resources`: Batch add/remove resources
- `GET /collections/{id}/recommendations`: Get collection-based recommendations

### Service Methods

- `create_collection()`: Create a new collection
- `get_collection()`: Retrieve a collection by ID
- `list_collections()`: List collections for a user
- `update_collection()`: Update collection metadata
- `delete_collection()`: Delete a collection
- `add_resources_to_collection()`: Add resources to a collection
- `remove_resources_from_collection()`: Remove resources from a collection
- `get_collection_resources()`: Get resources in a collection
- `compute_collection_embedding()`: Compute collection embedding
- `find_similar_resources()`: Find similar resources based on collection
- `find_collections_with_resource()`: Find collections containing a resource

## Events

### Subscribed Events

- `resource.deleted`: Triggered when a resource is deleted
  - Handler: `handle_resource_deleted()`
  - Action: Recomputes embeddings for affected collections

### Emitted Events

None currently. Future events may include:
- `collection.created`
- `collection.updated`
- `collection.deleted`
- `collection.resource_added`
- `collection.resource_removed`

## Data Models

### Collection

- `id`: UUID primary key
- `name`: Collection name
- `description`: Optional description
- `owner_id`: Owner user ID
- `visibility`: private | shared | public
- `parent_id`: Optional parent collection ID
- `embedding`: Aggregate embedding vector
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### CollectionResource

- `collection_id`: Collection UUID (FK)
- `resource_id`: Resource UUID (FK)
- `added_at`: Timestamp when resource was added

## Usage Examples

### Creating a Collection

```python
from backend.app.modules.collections import CollectionService

service = CollectionService(db)
collection = service.create_collection(
    name="Machine Learning Papers",
    description="Curated ML research papers",
    owner_id="user123",
    visibility="private"
)
```

### Adding Resources

```python
added_count = service.add_resources_to_collection(
    collection_id=collection.id,
    resource_ids=[resource1_id, resource2_id],
    owner_id="user123"
)
```

### Getting Recommendations

```python
similar_resources = service.find_similar_resources(
    collection_id=collection.id,
    owner_id="user123",
    limit=20,
    min_similarity=0.7
)
```

## Testing

Run module tests:

```bash
pytest backend/app/modules/collections/tests/
```

## Version History

- **1.0.0**: Initial extraction from layered architecture
  - Moved from `routers/collections.py`, `services/collection_service.py`, `schemas/collection.py`
  - Added event-driven communication
  - Implemented module isolation
