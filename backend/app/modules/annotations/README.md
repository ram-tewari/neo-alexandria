# Annotations Module

## Purpose

The Annotations module provides functionality for creating, managing, and searching text highlights and notes on resource content. It enables users to annotate documents with precise text selection, add notes, organize with tags, and perform both full-text and semantic search across their annotations.

## Features

- **Precise Text Selection**: Character offset-based highlighting with context preservation
- **Rich Note-Taking**: Add notes with semantic embeddings for intelligent search
- **Tag Organization**: Organize annotations with tags and color coding
- **Multiple Search Methods**:
  - Full-text search across notes and highlighted text
  - Semantic search using embeddings
  - Tag-based filtering
- **Export Capabilities**: Export annotations to Markdown or JSON formats
- **Privacy Controls**: Private or shared annotations
- **Collection Integration**: Associate annotations with collections

## Module Structure

```
annotations/
├── __init__.py          # Public interface exports
├── router.py            # FastAPI endpoints (11 endpoints)
├── service.py           # Business logic
├── schema.py            # Pydantic schemas
├── model.py             # SQLAlchemy model
├── handlers.py          # Event handlers
└── README.md            # This file
```

## Public Interface

```python
from app.modules.annotations import (
    annotations_router,
    AnnotationService,
    AnnotationCreate,
    AnnotationUpdate,
    AnnotationResponse,
    AnnotationListResponse,
    AnnotationSearchResult,
    AnnotationSearchResponse
)
```

## API Endpoints

### Annotation CRUD
- `POST /resources/{resource_id}/annotations` - Create annotation
- `GET /resources/{resource_id}/annotations` - List resource annotations
- `GET /annotations` - List all user annotations
- `GET /annotations/{annotation_id}` - Get annotation
- `PUT /annotations/{annotation_id}` - Update annotation
- `DELETE /annotations/{annotation_id}` - Delete annotation

### Search
- `GET /annotations/search/fulltext` - Full-text search
- `GET /annotations/search/semantic` - Semantic search
- `GET /annotations/search/tags` - Tag-based search

### Export
- `GET /annotations/export/markdown` - Export to Markdown
- `GET /annotations/export/json` - Export to JSON

## Events

### Emitted Events
- `annotation.created` - When a new annotation is created
  - Payload: `{annotation_id, resource_id, user_id}`
- `annotation.updated` - When an annotation is modified
  - Payload: `{annotation_id, resource_id, user_id, changed_fields}`
- `annotation.deleted` - When an annotation is removed
  - Payload: `{annotation_id, resource_id, user_id}`

### Subscribed Events
- `resource.deleted` - Cascade delete annotations for deleted resource
  - Handler: `handle_resource_deleted(payload)`

## Dependencies

### Shared Kernel
- `shared.database` - Database session management
- `shared.embeddings` - Embedding generation for semantic search
- `shared.event_bus` - Event emission and subscription

### External
- SQLAlchemy - Database ORM
- FastAPI - Web framework
- Pydantic - Data validation

## Usage Examples

### Creating an Annotation

```python
from app.modules.annotations import AnnotationService, AnnotationCreate

service = AnnotationService(db)
annotation = service.create_annotation(
    resource_id="123e4567-e89b-12d3-a456-426614174000",
    user_id="user-123",
    start_offset=100,
    end_offset=150,
    highlighted_text="This is the selected text",
    note="My thoughts on this passage",
    tags=["important", "review"],
    color="#FFFF00"
)
```

### Searching Annotations

```python
# Full-text search
annotations = service.search_annotations_fulltext(
    user_id="user-123",
    query="machine learning",
    limit=50
)

# Semantic search
results = service.search_annotations_semantic(
    user_id="user-123",
    query="neural networks",
    limit=10
)

# Tag search
annotations = service.search_annotations_by_tags(
    user_id="user-123",
    tags=["important", "review"],
    match_all=False  # Match ANY tag
)
```

### Exporting Annotations

```python
# Export to Markdown
markdown = service.export_annotations_markdown(
    user_id="user-123",
    resource_id="123e4567-e89b-12d3-a456-426614174000"
)

# Export to JSON
json_data = service.export_annotations_json(
    user_id="user-123"
)
```

## Database Model

The `Annotation` model includes:
- **Primary Key**: UUID
- **Foreign Keys**: resource_id (CASCADE delete), user_id
- **Text Selection**: start_offset, end_offset, highlighted_text
- **User Content**: note, tags (JSON array)
- **Visual**: color (hex code)
- **Search**: embedding (vector for semantic search)
- **Context**: context_before, context_after (50 chars each)
- **Sharing**: is_shared (boolean)
- **Organization**: collection_ids (JSON array)
- **Audit**: created_at, updated_at

## Performance Considerations

- **Indexes**: Composite indexes on (user_id, resource_id) and (created_at)
- **Eager Loading**: Uses `joinedload` for resource relationship to prevent N+1 queries
- **Embedding Generation**: Async background task (not blocking)
- **Search Limits**: Default limits to prevent excessive memory usage
- **Export Limits**: Maximum 1,000 annotations per export

## Testing

Tests are located in `tests/modules/annotations/`:
- `test_service.py` - Service unit tests
- `test_router.py` - Endpoint integration tests
- `test_handlers.py` - Event handler tests

## Requirements Mapping

This module implements requirements from Phase 14 specification:
- **Requirement 1.1**: Router migration
- **Requirement 1.2**: Service migration
- **Requirement 1.3**: Schema migration
- **Requirement 1.4**: Model extraction
- **Requirement 1.5**: Public interface
- **Requirement 1.6**: Event subscription (resource.deleted)
- **Requirement 1.7**: Event emission (annotation.created/updated/deleted)

## Version

- **Version**: 1.0.0
- **Domain**: annotations
- **Phase**: 14 (Complete Vertical Slice Refactor)
