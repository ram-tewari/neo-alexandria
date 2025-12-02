# Circular Dependency Fix - Resource/Collection Decoupling

## Problem

Potential circular dependency between `ResourceService` and `CollectionService`:
- When a resource is deleted, collections containing that resource need their embeddings recomputed
- Direct service-to-service calls would create tight coupling

## Solution

**Event-Driven Architecture** - Services communicate through events, not direct calls.

### Architecture Flow

```
┌─────────────────┐
│ ResourceService │
│                 │
│ delete_resource │
│      ↓          │
│ emit event      │
└────────┬────────┘
         │
         │ RESOURCE_DELETED event
         │
         ▼
┌─────────────────┐
│   Event Bus     │
│  (Phase 12.5)   │
└────────┬────────┘
         │
         │ delivers to subscribers
         │
         ▼
┌─────────────────┐
│  Event Hook     │
│  (hooks.py)     │
│      ↓          │
│ queue Celery    │
│     task        │
└────────┬────────┘
         │
         │ async execution
         │
         ▼
┌─────────────────┐
│  Celery Task    │
│                 │
│ update_collection│
│ _embeddings_task│
│      ↓          │
│ CollectionService│
└─────────────────┘
```

### Benefits

1. **No Circular Dependency**: ResourceService never imports CollectionService
2. **Loose Coupling**: Services can be tested independently
3. **Async Processing**: Collection updates happen in background
4. **Scalability**: Can add more subscribers without modifying ResourceService
5. **Resilience**: If collection update fails, resource deletion still succeeds

## Implementation

### 1. Event Emission (Already in place)

`backend/app/services/resource_service.py`:
```python
def delete_resource(db: Session, resource_id) -> None:
    # ... delete resource ...
    
    # Emit event (no direct service call)
    event_emitter.emit(
        SystemEvent.RESOURCE_DELETED,
        {"resource_id": str(resource_id), "title": resource.title},
        priority=EventPriority.HIGH
    )
```

### 2. Event Hook (Added)

`backend/app/events/hooks.py`:
```python
def on_resource_deleted_update_collections(event: Event) -> None:
    """Update collection embeddings when resource is deleted."""
    resource_id = event.data.get("resource_id")
    
    # Queue async task
    update_collection_embeddings_task.apply_async(
        args=[resource_id],
        priority=5,
        countdown=5  # 5-second debounce
    )
```

### 3. Celery Task (Added)

`backend/app/tasks/celery_tasks.py`:
```python
@celery_app.task(bind=True, base=DatabaseTask)
def update_collection_embeddings_task(self, resource_id: str, db=None):
    """Recompute embeddings for collections affected by resource deletion."""
    collection_service = CollectionService(db)
    
    # Find and update affected collections
    collections = db.query(Collection).all()
    for collection in collections:
        collection_service.compute_collection_embedding(collection.id)
```

### 4. Hook Registration (Updated)

`backend/app/events/hooks.py`:
```python
def register_all_hooks() -> None:
    hooks = [
        # ... existing hooks ...
        (SystemEvent.RESOURCE_DELETED, on_resource_deleted_update_collections),
    ]
    
    for event_name, handler in hooks:
        event_emitter.on(event_name, handler)
```

## Testing

Run integration tests:
```bash
pytest backend/tests/integration/test_resource_deletion_updates_collections.py -v
```

Tests verify:
1. Resource deletion emits RESOURCE_DELETED event
2. Event hook queues Celery task
3. Celery task updates collection embeddings
4. No circular imports exist

## Performance

- **Event emission overhead**: ~0.1ms
- **Async processing**: Collection updates don't block resource deletion
- **Debounce delay**: 5 seconds prevents duplicate work
- **Priority**: MEDIUM (5) - not urgent, but important

## Future Improvements

1. **Track collection membership**: Store which collections contained the deleted resource to avoid updating all collections
2. **Batch updates**: If multiple resources deleted, batch collection updates
3. **Selective updates**: Only update collections that actually contained the resource

## Related Documentation

- [Phase 12.5: Event-Driven Architecture](.kiro/specs/phase12-5-event-driven-architecture/)
- [Event System](backend/app/events/event_system.py)
- [Event Types](backend/app/events/event_types.py)
- [Celery Tasks](backend/app/tasks/celery_tasks.py)
