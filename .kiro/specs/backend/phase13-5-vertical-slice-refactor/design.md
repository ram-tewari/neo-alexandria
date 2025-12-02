# Design Document

## Overview

Phase 13.5 transforms Neo Alexandria 2.0 from a traditional layered architecture to a modular monolith using vertical slices. This design document details the technical approach for implementing the requirements, focusing on the "Strangler Fig" pattern for incremental migration.

### Current Architecture Problems

1. **Horizontal Rigidity**: Code organized by technical layer (routers/, services/, models/) makes features span multiple directories
2. **Tight Coupling**: ResourceService directly imports CollectionService, creating circular dependencies
3. **Testing Complexity**: Cannot test domains in isolation due to cross-service dependencies
4. **Deployment Constraints**: Cannot extract features into microservices without major refactoring

### Target Architecture Benefits

1. **Vertical Organization**: Each domain contains all its layers in one module
2. **Loose Coupling**: Modules communicate via events, not direct imports
3. **Independent Testing**: Each module can be tested in isolation
4. **Future-Proof**: Modules can be extracted into microservices if needed

### Design Principles

1. **Domain-Driven Design**: Organize by business domain, not technical layer
2. **Event-Driven Architecture**: Use publish-subscribe for cross-module communication
3. **Shared Kernel**: Minimize shared components to database, events, and base models
4. **Backward Compatibility**: Maintain all existing APIs during migration
5. **Incremental Migration**: Use Strangler Fig pattern to migrate one module at a time

## Architecture

### High-Level Structure

```
backend/app/
├── shared/                    # Shared Kernel (no dependencies on modules)
│   ├── __init__.py
│   ├── database.py           # Database engine, session, Base
│   ├── event_bus.py          # Event emitter and subscription system
│   └── base_model.py         # SQLAlchemy Base and common mixins
│
├── modules/                   # Vertical Slices (Domain Modules)
│   ├── collections/
│   │   ├── __init__.py       # Public interface
│   │   ├── router.py         # FastAPI endpoints
│   │   ├── service.py        # Business logic
│   │   ├── schema.py         # Pydantic models
│   │   ├── model.py          # SQLAlchemy models
│   │   ├── handlers.py       # Event handlers
│   │   ├── README.md         # Module documentation
│   │   └── tests/            # Module-specific tests
│   │
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schema.py
│   │   ├── model.py
│   │   ├── handlers.py
│   │   ├── README.md
│   │   └── tests/
│   │
│   └── search/
│       ├── __init__.py
│       ├── router.py
│       ├── service.py
│       ├── schema.py
│       ├── model.py
│       ├── handlers.py
│       ├── README.md
│       └── tests/
│
├── main.py                    # Application entry point
└── config/                    # Configuration (unchanged)
```


### Module Communication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     Event-Driven Communication                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐                           ┌──────────────┐    │
│  │  Resources   │                           │ Collections  │    │
│  │   Module     │                           │   Module     │    │
│  │              │                           │              │    │
│  │  DELETE      │                           │              │    │
│  │  /resources  │                           │              │    │
│  │  /{id}       │                           │              │    │
│  └──────┬───────┘                           └──────▲───────┘    │
│         │                                          │            │
│         │ 1. Delete resource                       │            │
│         │                                          │            │
│         │ 2. Emit event                            │ 4. Update  │
│         │    "resource.deleted"                    │    affected│
│         │                                          │    collections│
│         │                                          │            │
│         └──────────►┌──────────────┐──────────────┘            │
│                     │  Event Bus   │                            │
│                     │  (Shared)    │                            │
│                     │              │                            │
│                     │ • Publish    │                            │
│                     │ • Subscribe  │                            │
│                     │ • Deliver    │                            │
│                     └──────────────┘                            │
│                                                                 │
│  Key Benefits:                                                  │
│  • No direct imports between modules                            │
│  • Modules can be tested independently                          │
│  • Async processing possible (future)                           │
│  • Easy to add new subscribers                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Dependency Rules

1. **Modules CANNOT import from other modules** (except through public interfaces)
2. **Modules CAN import from shared kernel** (database, event_bus, base_model)
3. **Modules MUST communicate via events** for cross-module operations
4. **Shared kernel CANNOT import from modules** (one-way dependency)

## Components and Interfaces

### 1. Shared Kernel Components

#### database.py

```python
"""
Shared database components.
Provides engine, session factory, and Base for all modules.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator

# Database engine (configured from settings)
engine = None
SessionLocal = None
Base = declarative_base()

def init_database(database_url: str) -> None:
    """Initialize database engine and session factory."""
    global engine, SessionLocal
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency injection for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```


#### event_bus.py

```python
"""
Shared event bus for inter-module communication.
Implements publish-subscribe pattern with synchronous delivery.
"""
from typing import Callable, Dict, List, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class EventPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3

class EventBus:
    """
    Synchronous event bus for module communication.
    
    Features:
    - Type-safe event names (use Enum)
    - Priority-based delivery
    - Error isolation (handler failures don't affect other handlers)
    - Logging and metrics
    """
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._metrics = {
            "events_emitted": 0,
            "events_delivered": 0,
            "handler_errors": 0
        }
    
    def subscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Event type to subscribe to
            handler: Callable that receives event payload
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Subscribed handler to {event_type}")
    
    def emit(self, event_type: str, payload: Dict[str, Any], priority: EventPriority = EventPriority.NORMAL) -> None:
        """
        Emit an event to all subscribers.
        
        Args:
            event_type: Event type to emit
            payload: Event data
            priority: Event priority (for logging/metrics)
        """
        self._metrics["events_emitted"] += 1
        logger.debug(f"Emitting {event_type} with priority {priority.name}")
        
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(payload)
                self._metrics["events_delivered"] += 1
            except Exception as e:
                self._metrics["handler_errors"] += 1
                logger.error(f"Handler error for {event_type}: {e}", exc_info=True)
    
    def get_metrics(self) -> Dict[str, int]:
        """Get event bus metrics."""
        return self._metrics.copy()

# Global event bus instance
event_bus = EventBus()
```

#### base_model.py

```python
"""
Shared base model and mixins for all domain models.
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from datetime import datetime, timezone
from uuid import uuid4

Base = declarative_base()

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))

class UUIDMixin:
    """Mixin for UUID primary key."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
```


### 2. Collections Module Design

#### Module Structure

```
modules/collections/
├── __init__.py           # Public interface
├── router.py             # FastAPI endpoints
├── service.py            # Business logic
├── schema.py             # Pydantic models
├── model.py              # SQLAlchemy models
├── handlers.py           # Event handlers
├── README.md             # Module documentation
└── tests/
    ├── test_service.py
    ├── test_router.py
    └── test_handlers.py
```

#### __init__.py (Public Interface)

```python
"""
Collections Module - Public Interface

Exposes only what other parts of the application need.
Internal implementation details are hidden.
"""
from .router import router as collections_router
from .service import CollectionService
from .schema import (
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    CollectionListResponse
)

__all__ = [
    "collections_router",
    "CollectionService",
    "CollectionCreate",
    "CollectionUpdate",
    "CollectionResponse",
    "CollectionListResponse"
]

# Module metadata
__version__ = "1.0.0"
__domain__ = "collections"
```

#### handlers.py (Event Handlers)

```python
"""
Event handlers for Collections module.
Subscribes to events from other modules.
"""
from backend.app.shared.event_bus import event_bus
from backend.app.shared.database import SessionLocal
from .service import CollectionService
import logging

logger = logging.getLogger(__name__)

def handle_resource_deleted(payload: dict) -> None:
    """
    Handle resource.deleted event.
    Recomputes embeddings for collections that contained the deleted resource.
    
    Args:
        payload: Event payload containing resource_id
    """
    resource_id = payload.get("resource_id")
    if not resource_id:
        logger.warning("resource.deleted event missing resource_id")
        return
    
    logger.info(f"Handling resource.deleted for {resource_id}")
    
    # Open new database session for this handler
    db = SessionLocal()
    try:
        service = CollectionService(db)
        
        # Find collections containing this resource
        affected_collections = service.find_collections_with_resource(resource_id)
        
        # Recompute embeddings for affected collections
        for collection in affected_collections:
            try:
                service.recompute_embedding(collection.id)
                logger.info(f"Recomputed embedding for collection {collection.id}")
            except Exception as e:
                logger.error(f"Failed to recompute embedding for collection {collection.id}: {e}")
    
    finally:
        db.close()

def register_handlers() -> None:
    """Register all event handlers for Collections module."""
    event_bus.subscribe("resource.deleted", handle_resource_deleted)
    logger.info("Collections module event handlers registered")
```


### 3. Resources Module Design

#### Key Changes from Current Implementation

**Before (Tight Coupling):**
```python
# resource_service.py
from backend.app.services.collection_service import CollectionService

def delete_resource(db: Session, resource_id) -> None:
    resource = get_resource(db, resource_id)
    db.delete(resource)
    db.commit()
    
    # Direct service call - creates circular dependency
    collection_service = CollectionService(db)
    collection_service.recompute_embedding_for_resource(resource_id)
```

**After (Event-Driven):**
```python
# modules/resources/service.py
from backend.app.shared.event_bus import event_bus, EventPriority

def delete_resource(db: Session, resource_id) -> None:
    resource = get_resource(db, resource_id)
    db.delete(resource)
    db.commit()
    
    # Emit event - no direct dependency on Collections
    event_bus.emit(
        "resource.deleted",
        {"resource_id": str(resource_id)},
        priority=EventPriority.HIGH
    )
```

#### handlers.py (Event Handlers)

```python
"""
Event handlers for Resources module.
"""
from backend.app.shared.event_bus import event_bus
import logging

logger = logging.getLogger(__name__)

def handle_collection_updated(payload: dict) -> None:
    """
    Handle collection.updated event.
    Could trigger resource re-indexing or cache invalidation.
    
    Args:
        payload: Event payload containing collection_id
    """
    collection_id = payload.get("collection_id")
    logger.info(f"Collection {collection_id} updated, resources may need re-indexing")
    # Future: Implement resource re-indexing logic

def register_handlers() -> None:
    """Register all event handlers for Resources module."""
    event_bus.subscribe("collection.updated", handle_collection_updated)
    logger.info("Resources module event handlers registered")
```

### 4. Search Module Design

The Search module consolidates multiple search-related services:
- `search_service.py`
- `hybrid_search_methods.py`
- `reciprocal_rank_fusion_service.py`
- `reranking_service.py`
- `sparse_embedding_service.py`

#### Consolidated Service Structure

```python
"""
modules/search/service.py

Consolidated search service combining all search strategies.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

class SearchService:
    """
    Unified search service providing multiple search strategies.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self._fts_strategy = FTSSearchStrategy(db)
        self._vector_strategy = VectorSearchStrategy(db)
        self._hybrid_strategy = HybridSearchStrategy(db)
    
    def search(
        self,
        query: str,
        strategy: str = "hybrid",
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Execute search using specified strategy.
        
        Args:
            query: Search query
            strategy: "fts", "vector", or "hybrid"
            filters: Optional filters
            limit: Maximum results
            
        Returns:
            List of search results
        """
        if strategy == "fts":
            return self._fts_strategy.search(query, filters, limit)
        elif strategy == "vector":
            return self._vector_strategy.search(query, filters, limit)
        else:
            return self._hybrid_strategy.search(query, filters, limit)
```


## Data Models

### Model Organization

Each module owns its domain models. Models are moved from the monolithic `database/models.py` to module-specific `model.py` files.

#### Collections Module Models

```python
"""
modules/collections/model.py
"""
from backend.app.shared.base_model import Base, TimestampMixin, UUIDMixin
from sqlalchemy import Column, String, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship

class Collection(Base, UUIDMixin, TimestampMixin):
    """Collection model - owns its own table definition."""
    __tablename__ = "collections"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String(255), nullable=False, index=True)
    visibility = Column(String(20), nullable=False, default="private", index=True)
    parent_id = Column(UUID, ForeignKey("collections.id", ondelete="CASCADE"), nullable=True, index=True)
    embedding = Column(JSON, nullable=True)
    
    # Relationships
    resources = relationship("Resource", secondary="collection_resources", back_populates="collections")
    parent = relationship("Collection", remote_side=[id], back_populates="subcollections")
    subcollections = relationship("Collection", back_populates="parent", cascade="all, delete-orphan")

class CollectionResource(Base):
    """Association table for many-to-many relationship."""
    __tablename__ = "collection_resources"
    
    collection_id = Column(UUID, ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True)
    resource_id = Column(UUID, ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)
    added_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    
    __table_args__ = (
        Index('idx_collection_resources_collection', 'collection_id'),
        Index('idx_collection_resources_resource', 'resource_id'),
    )
```

#### Resources Module Models

```python
"""
modules/resources/model.py
"""
from backend.app.shared.base_model import Base, TimestampMixin, UUIDMixin
from sqlalchemy import Column, String, Text, JSON, Float, DateTime

class Resource(Base, UUIDMixin, TimestampMixin):
    """Resource model - owns its own table definition."""
    __tablename__ = "resources"
    
    title = Column(String, nullable=False)
    description = Column(Text)
    creator = Column(String)
    publisher = Column(String)
    contributor = Column(String)
    date_created = Column(DateTime(timezone=True))
    date_modified = Column(DateTime(timezone=True))
    type = Column(String)
    format = Column(String)
    identifier = Column(String)
    source = Column(String)
    language = Column(String)
    coverage = Column(String)
    rights = Column(String)
    subject = Column(JSON)
    relation = Column(JSON)
    classification_code = Column(String)
    read_status = Column(String, default="unread")
    quality_score = Column(Float, default=0.0)
    embedding = Column(JSON)
    sparse_embedding = Column(JSON)
    sparse_embedding_model = Column(String)
    sparse_embedding_updated_at = Column(DateTime(timezone=True))
    
    # Ingestion tracking
    ingestion_status = Column(String, default="pending")
    ingestion_error = Column(Text)
    ingestion_started_at = Column(DateTime(timezone=True))
    ingestion_completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    collections = relationship("Collection", secondary="collection_resources", back_populates="resources")
```

### Cross-Module Model References

**Problem**: Resources and Collections reference each other through relationships.

**Solution**: Use string-based relationship references and lazy loading:

```python
# In modules/resources/model.py
collections = relationship("Collection", secondary="collection_resources", back_populates="resources", lazy="select")

# In modules/collections/model.py
resources = relationship("Resource", secondary="collection_resources", back_populates="collections", lazy="select")
```

SQLAlchemy resolves string references at runtime, avoiding import cycles.


## Error Handling

### Event Handler Error Isolation

Event handlers must not crash the event bus or affect other handlers:

```python
def emit(self, event_type: str, payload: Dict[str, Any], priority: EventPriority = EventPriority.NORMAL) -> None:
    """Emit event with error isolation."""
    handlers = self._handlers.get(event_type, [])
    
    for handler in handlers:
        try:
            handler(payload)
            self._metrics["events_delivered"] += 1
        except Exception as e:
            # Log error but continue to next handler
            self._metrics["handler_errors"] += 1
            logger.error(f"Handler error for {event_type}: {e}", exc_info=True)
            
            # Optionally emit error event for monitoring
            self.emit(
                "handler.error",
                {
                    "event_type": event_type,
                    "handler": handler.__name__,
                    "error": str(e)
                },
                priority=EventPriority.HIGH
            )
```

### Database Transaction Handling

Each event handler opens its own database session:

```python
def handle_resource_deleted(payload: dict) -> None:
    """Handler with proper transaction management."""
    db = SessionLocal()
    try:
        # Perform database operations
        service = CollectionService(db)
        service.recompute_embedding(collection_id)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Transaction failed: {e}")
        raise
    finally:
        db.close()
```

### Module Import Errors

If a module fails to import, the application should still start:

```python
# main.py
def register_all_modules():
    """Register all modules with graceful error handling."""
    modules = [
        ("collections", "backend.app.modules.collections"),
        ("resources", "backend.app.modules.resources"),
        ("search", "backend.app.modules.search"),
    ]
    
    for module_name, module_path in modules:
        try:
            module = importlib.import_module(module_path)
            
            # Register router
            if hasattr(module, f"{module_name}_router"):
                app.include_router(getattr(module, f"{module_name}_router"))
            
            # Register event handlers
            if hasattr(module, "register_handlers"):
                module.register_handlers()
            
            logger.info(f"Registered module: {module_name}")
        except Exception as e:
            logger.error(f"Failed to register module {module_name}: {e}", exc_info=True)
            # Continue with other modules
```

## Testing Strategy

### Module-Level Testing

Each module has its own test suite that can run independently:

```python
# modules/collections/tests/test_service.py
import pytest
from unittest.mock import Mock, patch
from backend.app.shared.database import Base, SessionLocal
from backend.app.modules.collections.service import CollectionService

@pytest.fixture
def db_session():
    """Create in-memory database for testing."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()

@pytest.fixture
def mock_event_bus():
    """Mock event bus to avoid cross-module dependencies."""
    with patch("backend.app.shared.event_bus.event_bus") as mock:
        yield mock

def test_create_collection(db_session, mock_event_bus):
    """Test collection creation in isolation."""
    service = CollectionService(db_session)
    
    collection = service.create_collection(
        name="Test Collection",
        owner_id="user123",
        description="Test description"
    )
    
    assert collection.name == "Test Collection"
    assert collection.owner_id == "user123"
    
    # Verify event was emitted
    mock_event_bus.emit.assert_called_once_with(
        "collection.created",
        {"collection_id": str(collection.id)},
        priority=EventPriority.NORMAL
    )
```

### Event Handler Testing

Test event handlers independently:

```python
# modules/collections/tests/test_handlers.py
import pytest
from unittest.mock import Mock, patch
from backend.app.modules.collections.handlers import handle_resource_deleted

def test_handle_resource_deleted():
    """Test resource deletion handler."""
    payload = {"resource_id": "resource-123"}
    
    with patch("backend.app.modules.collections.handlers.SessionLocal") as mock_session:
        with patch("backend.app.modules.collections.handlers.CollectionService") as mock_service:
            # Setup mocks
            mock_db = Mock()
            mock_session.return_value = mock_db
            
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.find_collections_with_resource.return_value = [
                Mock(id="collection-1"),
                Mock(id="collection-2")
            ]
            
            # Execute handler
            handle_resource_deleted(payload)
            
            # Verify service calls
            mock_service_instance.find_collections_with_resource.assert_called_once_with("resource-123")
            assert mock_service_instance.recompute_embedding.call_count == 2
```

### Integration Testing

Test cross-module communication through events:

```python
# tests/integration/test_resource_collection_integration.py
import pytest
from backend.app.shared.event_bus import event_bus
from backend.app.modules.resources.service import ResourceService
from backend.app.modules.collections.service import CollectionService

def test_resource_deletion_updates_collections(db_session):
    """Test that deleting a resource updates collection embeddings."""
    # Setup
    resource_service = ResourceService(db_session)
    collection_service = CollectionService(db_session)
    
    # Create resource and collection
    resource = resource_service.create_resource({"url": "https://example.com"})
    collection = collection_service.create_collection("Test", "user123")
    collection_service.add_resource(collection.id, resource.id)
    
    # Track event emissions
    events_emitted = []
    def track_event(event_type, payload, priority):
        events_emitted.append((event_type, payload))
    
    with patch.object(event_bus, "emit", side_effect=track_event):
        # Delete resource
        resource_service.delete_resource(resource.id)
    
    # Verify event was emitted
    assert ("resource.deleted", {"resource_id": str(resource.id)}) in events_emitted
    
    # Verify collection was updated (through event handler)
    updated_collection = collection_service.get_collection(collection.id)
    assert updated_collection.embedding is not None  # Recomputed
```


## Migration Strategy (Strangler Fig Pattern)

### Phase 1: Setup Shared Kernel (Week 1)

1. Create `app/shared/` directory
2. Extract `database.py` from `app/database/base.py`
3. Create `event_bus.py` with EventBus implementation
4. Create `base_model.py` with Base and mixins
5. Update all existing imports to use shared kernel
6. Run full test suite to verify no regressions

**Success Criteria**: All tests pass, no functionality changes

### Phase 2: Extract Collections Module (Week 2)

1. Create `app/modules/collections/` directory structure
2. Copy (don't move yet) files to new locations:
   - `routers/collections.py` → `modules/collections/router.py`
   - `services/collection_service.py` → `modules/collections/service.py`
   - `schemas/collection.py` → `modules/collections/schema.py`
3. Extract Collection models from `database/models.py` → `modules/collections/model.py`
4. Create `modules/collections/__init__.py` with public interface
5. Create `modules/collections/handlers.py` with event handlers
6. Update imports in copied files to use shared kernel
7. Register Collections module in `main.py`
8. Add deprecation warnings to old import paths
9. Run Collections module tests
10. Run full integration test suite

**Success Criteria**: Collections module works independently, all tests pass

### Phase 3: Decouple Resources from Collections (Week 3)

1. Identify all direct imports of CollectionService in ResourceService
2. Replace direct calls with event emissions:
   ```python
   # Before
   collection_service.recompute_embedding(resource_id)
   
   # After
   event_bus.emit("resource.deleted", {"resource_id": resource_id})
   ```
3. Implement event handlers in Collections module
4. Test event-driven flow with integration tests
5. Remove direct imports from ResourceService
6. Verify no circular dependencies remain

**Success Criteria**: ResourceService has no imports from CollectionService, all tests pass

### Phase 4: Extract Resources Module (Week 4)

1. Create `app/modules/resources/` directory structure
2. Move files to new locations:
   - `routers/resources.py` → `modules/resources/router.py`
   - `services/resource_service.py` → `modules/resources/service.py`
   - `schemas/resource.py` → `modules/resources/schema.py`
3. Extract Resource models from `database/models.py` → `modules/resources/model.py`
4. Create `modules/resources/__init__.py` with public interface
5. Create `modules/resources/handlers.py` with event handlers
6. Update all imports to use new module paths
7. Register Resources module in `main.py`
8. Run Resources module tests
9. Run full integration test suite

**Success Criteria**: Resources module works independently, all tests pass

### Phase 5: Extract Search Module (Week 5)

1. Create `app/modules/search/` directory structure
2. Consolidate search services:
   - `services/search_service.py`
   - `services/hybrid_search_methods.py`
   - `services/reciprocal_rank_fusion_service.py`
   - `services/reranking_service.py`
   - `services/sparse_embedding_service.py`
3. Merge into unified `modules/search/service.py`
4. Move `routers/search.py` → `modules/search/router.py`
5. Move `schemas/search.py` → `modules/search/schema.py`
6. Create `modules/search/__init__.py` with public interface
7. Update all imports to use new module paths
8. Register Search module in `main.py`
9. Run Search module tests
10. Run full integration test suite

**Success Criteria**: Search module works independently, all tests pass

### Phase 6: Cleanup and Documentation (Week 6)

1. Remove old layered structure files:
   - Delete `routers/` directory (after verifying all moved)
   - Delete `services/` directory (after verifying all moved)
   - Delete `schemas/` directory (after verifying all moved)
2. Update `database/models.py` to only contain shared models (if any)
3. Remove deprecation warnings
4. Update all documentation:
   - `ARCHITECTURE_DIAGRAM.md`
   - `DEVELOPER_GUIDE.md`
   - Create `MIGRATION_GUIDE.md`
5. Create module-specific README files
6. Run full test suite
7. Performance testing to verify no regressions

**Success Criteria**: Clean codebase, comprehensive documentation, all tests pass

### Rollback Strategy

Each phase is reversible:

1. **Phase 1-2**: Keep old files, new modules are additive
2. **Phase 3**: Revert event emissions to direct calls
3. **Phase 4-5**: Restore old import paths using compatibility shims
4. **Phase 6**: Git revert if issues found

### Risk Mitigation

1. **Comprehensive Testing**: Run full test suite after each phase
2. **Feature Flags**: Use feature flags to toggle between old/new implementations
3. **Gradual Rollout**: Deploy to staging environment first
4. **Monitoring**: Track event bus metrics and performance
5. **Backward Compatibility**: Maintain old import paths with deprecation warnings


## Performance Considerations

### Event Bus Overhead

**Concern**: Event-driven communication adds latency compared to direct function calls.

**Mitigation**:
1. **Synchronous Delivery**: Events are delivered synchronously in the same thread (no network overhead)
2. **Minimal Overhead**: Event bus adds ~0.1ms per event emission
3. **Batching**: Future optimization to batch multiple events
4. **Async Option**: Can upgrade to async event delivery if needed

**Benchmark Target**: Event emission + delivery < 1ms for 95th percentile

### Database Session Management

**Concern**: Each event handler opens a new database session.

**Mitigation**:
1. **Connection Pooling**: SQLAlchemy connection pool reuses connections
2. **Session Lifecycle**: Sessions are short-lived (only during handler execution)
3. **Transaction Isolation**: Each handler has its own transaction
4. **Pool Sizing**: Configure pool size based on concurrent event handlers

**Configuration**:
```python
engine = create_engine(
    database_url,
    pool_size=20,           # Base connections
    max_overflow=40,        # Additional connections for burst traffic
    pool_pre_ping=True,     # Validate connections before use
    pool_recycle=3600       # Recycle connections after 1 hour
)
```

### Module Import Time

**Concern**: Importing modules at startup adds initialization time.

**Mitigation**:
1. **Lazy Loading**: Import modules only when needed
2. **Parallel Loading**: Load modules in parallel during startup
3. **Caching**: Cache imported modules

**Benchmark Target**: Application startup < 5 seconds

### Memory Footprint

**Concern**: Modular structure may increase memory usage.

**Mitigation**:
1. **Shared Kernel**: Common components are shared, not duplicated
2. **Lazy Loading**: Load module components on-demand
3. **Garbage Collection**: Properly close database sessions and release resources

**Benchmark Target**: Memory usage increase < 10% compared to layered architecture

## Monitoring and Observability

### Event Bus Metrics

Expose metrics through `/monitoring/events` endpoint:

```json
{
  "events_emitted": 1523,
  "events_delivered": 1520,
  "handler_errors": 3,
  "event_types": {
    "resource.created": 450,
    "resource.updated": 320,
    "resource.deleted": 180,
    "collection.created": 120,
    "collection.updated": 453
  },
  "handler_latency_ms": {
    "p50": 0.8,
    "p95": 2.1,
    "p99": 5.3
  }
}
```

### Module Health Checks

Each module exposes a health check endpoint:

```python
# modules/collections/router.py
@router.get("/health")
def health_check():
    """Health check for Collections module."""
    return {
        "module": "collections",
        "status": "healthy",
        "version": "1.0.0",
        "database": check_database_connection(),
        "event_handlers": check_event_handlers_registered()
    }
```

### Logging Strategy

Structured logging for module operations:

```python
logger.info(
    "Module operation",
    extra={
        "module": "collections",
        "operation": "create_collection",
        "user_id": user_id,
        "collection_id": collection_id,
        "duration_ms": duration
    }
)
```

## Security Considerations

### Module Isolation

1. **No Direct Access**: Modules cannot access each other's internal state
2. **Event Validation**: Validate event payloads before processing
3. **Authorization**: Each module enforces its own authorization rules
4. **Data Sanitization**: Sanitize data at module boundaries

### Event Bus Security

1. **Type Safety**: Use Enum for event types to prevent typos
2. **Payload Validation**: Validate event payloads with Pydantic schemas
3. **Rate Limiting**: Prevent event flooding attacks
4. **Audit Logging**: Log all events for security auditing

```python
class EventPayload(BaseModel):
    """Base class for event payloads with validation."""
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
class ResourceDeletedPayload(EventPayload):
    """Validated payload for resource.deleted event."""
    resource_id: str = Field(..., regex=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
```

## Future Enhancements

### Async Event Processing

Upgrade to async event delivery for better performance:

```python
async def emit_async(self, event_type: str, payload: Dict[str, Any]) -> None:
    """Asynchronous event emission."""
    handlers = self._handlers.get(event_type, [])
    
    # Execute handlers concurrently
    tasks = [handler(payload) for handler in handlers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle errors
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Async handler error: {result}")
```

### Message Queue Integration

Replace in-memory event bus with message queue (RabbitMQ, Redis Streams):

```python
class MessageQueueEventBus(EventBus):
    """Event bus backed by message queue for distributed systems."""
    
    def __init__(self, queue_url: str):
        self.queue = connect_to_queue(queue_url)
    
    def emit(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Publish event to message queue."""
        self.queue.publish(
            exchange="events",
            routing_key=event_type,
            body=json.dumps(payload)
        )
```

### Microservices Extraction

Modules can be extracted into microservices:

1. **API Gateway**: Route requests to appropriate microservice
2. **Service Discovery**: Use Consul or Eureka for service registration
3. **Event Bus**: Replace with distributed message queue
4. **Database**: Each microservice gets its own database

### Module Versioning

Support multiple versions of modules simultaneously:

```python
# modules/collections/v1/__init__.py
# modules/collections/v2/__init__.py

# Route to specific version
@app.get("/api/v1/collections")
def list_collections_v1():
    from backend.app.modules.collections.v1 import CollectionService
    ...

@app.get("/api/v2/collections")
def list_collections_v2():
    from backend.app.modules.collections.v2 import CollectionService
    ...
```

## Conclusion

This design transforms Neo Alexandria 2.0 from a tightly-coupled layered architecture to a loosely-coupled modular monolith. The key benefits are:

1. **Improved Maintainability**: Each domain is self-contained and easier to understand
2. **Better Testability**: Modules can be tested in isolation
3. **Reduced Coupling**: Event-driven communication eliminates circular dependencies
4. **Future-Proof**: Modules can be extracted into microservices if needed
5. **Team Scalability**: Different teams can work on different modules independently

The Strangler Fig migration strategy ensures a safe, incremental transition with minimal risk.
