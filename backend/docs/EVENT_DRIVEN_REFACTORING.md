# Event-Driven Refactoring - Resources and Collections

## Date: 2025-11-23

## Overview
Documentation of the event-driven refactoring that replaced direct service calls between Resources and Collections modules.

## Implementation Details

### ResourceService Changes

#### 1. Event Emission on Resource Deletion
**Location**: `backend/app/services/resource_service.py:1091`

```python
def delete_resource(db: Session, resource_id) -> None:
    """Delete a resource and its associated data."""
    # ... deletion logic ...
    
    # Emit resource.deleted event
    event_bus.emit(
        SystemEvent.RESOURCE_DELETED.value,
        {
            "resource_id": str(resource.id),
            "title": resource.title
        },
        priority=EventPriority.HIGH
    )
```

**Key Points**:
- Event is emitted AFTER successful deletion and commit
- Payload includes resource_id and title for logging/tracking
- High priority ensures timely processing
- No direct call to CollectionService

#### 2. Removed Dependencies
- ✅ No import of `CollectionService`
- ✅ No import of `collection_service` module
- ✅ No direct method calls to collection-related functions

#### 3. Required Imports
```python
from backend.app.shared.event_bus import event_bus, EventPriority
from backend.app.events.event_types import SystemEvent
```

### Collections Module Handler

#### 1. Event Handler Implementation
**Location**: `backend/app/modules/collections/handlers.py:24`

```python
def handle_resource_deleted(payload: Dict[str, Any]) -> None:
    """
    Handle resource deletion event.
    
    When a resource is deleted:
    1. Find all collections containing that resource
    2. Recompute their embeddings
    """
    resource_id = payload.get("resource_id")
    
    # Get database session
    db_gen = get_sync_db()
    db = next(db_gen)
    
    try:
        service = CollectionService(db)
        collections = service.find_collections_with_resource(resource_id)
        
        for collection in collections:
            service.compute_collection_embedding(collection.id)
    finally:
        # Close session
        try:
            next(db_gen)
        except StopIteration:
            pass
```

**Key Points**:
- Handler manages its own database session
- Finds affected collections using service method
- Recomputes embeddings for each affected collection
- Proper error handling and logging
- Session cleanup in finally block

#### 2. Event Registration
**Location**: `backend/app/modules/collections/handlers.py:103`

```python
def register_handlers() -> None:
    """Register all event handlers for the Collections module."""
    event_bus.subscribe("resource.deleted", handle_resource_deleted)
```

**Key Points**:
- Called during application startup
- Subscribes to the `resource.deleted` event
- Decoupled from ResourceService

### CollectionService Changes

#### New Method for Event Handler
**Location**: `backend/app/modules/collections/service.py`

```python
def find_collections_with_resource(self, resource_id) -> List[Collection]:
    """
    Find all collections that contain a specific resource.
    
    Args:
        resource_id: UUID of the resource
        
    Returns:
        List of collections containing the resource
    """
    # Implementation to query collections by resource membership
```

**Purpose**: Provides a clean interface for the event handler to find affected collections.

## Event Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│ 1. Client calls DELETE /resources/{id}                       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│ 2. ResourceService.delete_resource()                         │
│    - Validates resource exists                               │
│    - Deletes annotations                                     │
│    - Deletes resource from database                          │
│    - Commits transaction                                     │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│ 3. event_bus.emit("resource.deleted", payload)              │
│    - Event: SystemEvent.RESOURCE_DELETED                     │
│    - Payload: {resource_id, title}                           │
│    - Priority: HIGH                                          │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│ 4. Event Bus notifies all subscribers                        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│ 5. handle_resource_deleted(payload)                          │
│    - Extracts resource_id from payload                       │
│    - Gets database session                                   │
│    - Creates CollectionService instance                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│ 6. service.find_collections_with_resource(resource_id)       │
│    - Queries collections containing the resource             │
│    - Returns list of affected collections                    │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         v
┌──────────────────────────────────────────────────────────────┐
│ 7. For each collection:                                      │
│    service.compute_collection_embedding(collection.id)       │
│    - Recomputes embedding based on remaining resources       │
│    - Updates collection in database                          │
└──────────────────────────────────────────────────────────────┘
```

## Benefits of Event-Driven Approach

### 1. Decoupling
- ResourceService doesn't know about CollectionService
- CollectionService doesn't know about ResourceService
- Modules can evolve independently

### 2. Scalability
- Easy to add new event handlers without modifying ResourceService
- Other modules can subscribe to `resource.deleted` event
- Example: Search module could invalidate cache on resource deletion

### 3. Testability
- ResourceService can be tested without CollectionService
- Event handlers can be tested in isolation
- Mock event bus for unit tests

### 4. Maintainability
- Clear separation of concerns
- Event contracts are explicit (event name + payload structure)
- Easy to trace event flow through logs

### 5. Resilience
- If Collections module fails, ResourceService still succeeds
- Event handlers have isolated error handling
- Failed handlers don't affect other subscribers

## Testing Strategy

### Unit Tests
1. **ResourceService**: Verify event is emitted on deletion
2. **Collections Handler**: Verify handler processes event correctly
3. **Event Bus**: Verify subscription and notification work

### Integration Tests
1. Delete a resource that belongs to collections
2. Verify collections are updated
3. Verify embeddings are recomputed
4. Verify no direct service calls occur

## Migration Notes

### Before (Circular Dependency)
```python
# ResourceService
from backend.app.services.collection_service import CollectionService

def delete_resource(db, resource_id):
    # ... delete resource ...
    
    # Direct call - creates circular dependency
    collection_service = CollectionService(db)
    collection_service.recompute_embedding_for_resource(resource_id)
```

### After (Event-Driven)
```python
# ResourceService
from backend.app.shared.event_bus import event_bus

def delete_resource(db, resource_id):
    # ... delete resource ...
    
    # Emit event - no dependency on CollectionService
    event_bus.emit("resource.deleted", {"resource_id": str(resource_id)})
```

## Conclusion

The refactoring successfully eliminated the circular dependency between Resources and Collections by:
1. Removing all direct imports and method calls
2. Implementing event-driven communication
3. Creating proper event handlers with error isolation
4. Maintaining all functionality while improving architecture

The system is now more modular, testable, and maintainable.
