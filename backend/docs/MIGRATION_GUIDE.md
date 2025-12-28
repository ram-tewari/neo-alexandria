# Migration Guide: Layered to Modular Architecture

> **Phase 14: Complete Vertical Slice Architecture**
>
> This guide documents the complete transition from a traditional layered architecture to a fully modular vertical slice architecture in Neo Alexandria 2.0.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Comparison](#architecture-comparison)
3. [Migration Strategy](#migration-strategy)
4. [Phase 14: Complete Module List](#phase-14-complete-module-list)
5. [Module Structure](#module-structure)
6. [Event-Driven Communication](#event-driven-communication)
7. [Shared Kernel Usage](#shared-kernel-usage)
8. [Adding New Modules](#adding-new-modules)
9. [Updating Existing Code](#updating-existing-code)
10. [Testing Modules](#testing-modules)
11. [Troubleshooting](#troubleshooting)

---

## Overview

### What Changed?

Neo Alexandria 2.0 has completed the transition from a **layered architecture** (horizontal slicing) to a **fully modular architecture** (vertical slicing) with 13 self-contained modules. This change improves:

- **Modularity**: Each module is self-contained with all its layers
- **Independence**: Modules can be developed and tested independently
- **Scalability**: Modules can be extracted into microservices if needed
- **Maintainability**: Changes are localized to specific modules
- **Coupling**: Event-driven communication eliminates circular dependencies

### What Stayed the Same?

- **API Endpoints**: All existing endpoints remain at the same paths
- **Response Schemas**: API responses are unchanged
- **Database Schema**: No database migrations required
- **Functionality**: All features work exactly as before

---

## Architecture Comparison

### Before: Layered Architecture

```
app/
├── routers/           # All API endpoints
│   ├── collections.py
│   ├── resources.py
│   └── search.py
├── services/          # All business logic
│   ├── collection_service.py
│   ├── resource_service.py
│   └── search_service.py
├── schemas/           # All Pydantic models
│   ├── collection.py
│   ├── resource.py
│   └── search.py
└── database/
    └── models.py      # All SQLAlchemy models
```

**Problems:**
- Circular dependencies between services
- Difficult to test in isolation
- Changes ripple across layers
- Hard to extract features into microservices

### After: Modular Architecture

```
app/
├── shared/            # Shared kernel (database, event_bus, base_model)
│   ├── database.py
│   ├── event_bus.py
│   └── base_model.py
└── modules/           # Self-contained modules
    ├── collections/
    │   ├── __init__.py
    │   ├── router.py
    │   ├── service.py
    │   ├── schema.py
    │   ├── model.py
    │   └── handlers.py
    ├── resources/
    │   └── ...
    └── search/
        └── ...
```

**Benefits:**
- No circular dependencies (event-driven communication)
- Easy to test modules in isolation
- Changes are localized to modules
- Clear path to microservices if needed

---

## Migration Strategy

The migration follows a phased approach to minimize risk:

### Phase 1: Shared Kernel Setup ✓

Extract common infrastructure to `app/shared/`:

```python
# app/shared/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
engine = None
SessionLocal = None

def init_database(database_url: str, env: str):
    """Initialize database engine and session factory."""
    global engine, SessionLocal
    engine = create_engine(database_url, ...)
    SessionLocal = sessionmaker(bind=engine)

def get_db():
    """Dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

```python
# app/shared/event_bus.py
class EventBus:
    """In-memory event bus for module communication."""
    
    def __init__(self):
        self._handlers = {}
        self._metrics = EventMetrics()
    
    def subscribe(self, event_type: str, handler: Callable):
        """Register an event handler."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def emit(self, event_type: str, payload: Dict[str, Any]):
        """Emit an event to all registered handlers."""
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(payload)
            except Exception as e:
                logger.error(f"Handler error: {e}")
                # Continue with other handlers

event_bus = EventBus()  # Global singleton
```

### Phase 2: Extract First Module (Collections) ✓

Create the module structure:

```bash
mkdir -p app/modules/collections
touch app/modules/collections/{__init__.py,router.py,service.py,schema.py,model.py,handlers.py}
```

Move code from layered structure to module:

1. **Router**: `app/routers/collections.py` → `app/modules/collections/router.py`
2. **Service**: `app/services/collection_service.py` → `app/modules/collections/service.py`
3. **Schema**: `app/schemas/collection.py` → `app/modules/collections/schema.py`
4. **Handlers**: Create new `app/modules/collections/handlers.py` for events

Update imports to use shared kernel:

```python
# Before
from app.database.base import get_sync_db, Base

# After
from app.shared.database import get_db, Base
```

Create public interface in `__init__.py`:

```python
# app/modules/collections/__init__.py
"""Collections Module - Public Interface"""

__version__ = "1.0.0"
__domain__ = "collections"

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "collections_router":
        from .router import router
        return router
    elif name == "CollectionService":
        from .service import CollectionService
        return CollectionService
    elif name == "register_handlers":
        from .handlers import register_handlers
        return register_handlers
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "collections_router",
    "CollectionService",
    "register_handlers",
]
```

### Phase 3: Replace Direct Calls with Events ✓

Identify circular dependencies:

```python
# Before: Direct service call (creates circular dependency)
from app.services.collection_service import CollectionService

def delete_resource(db: Session, resource_id: str):
    # Delete resource
    db.delete(resource)
    db.commit()
    
    # Update collections (direct call)
    collection_service = CollectionService(db)
    collections = collection_service.find_collections_with_resource(resource_id)
    for collection in collections:
        collection_service.recompute_embedding(collection.id)
```

Replace with event emission:

```python
# After: Event-driven (no circular dependency)
from app.shared.event_bus import event_bus

def delete_resource(db: Session, resource_id: str):
    # Delete resource
    db.delete(resource)
    db.commit()
    
    # Emit event (no direct dependency on CollectionService)
    event_bus.emit("resource.deleted", {
        "resource_id": str(resource_id)
    })
```

Create event handler in Collections module:

```python
# app/modules/collections/handlers.py
from app.shared.event_bus import event_bus
from .service import CollectionService

def handle_resource_deleted(payload: Dict[str, Any]):
    """Handle resource deletion by updating affected collections."""
    resource_id = payload.get("resource_id")
    
    # Get database session
    from app.shared.database import SessionLocal
    db = SessionLocal()
    
    try:
        service = CollectionService(db)
        collections = service.find_collections_with_resource(resource_id)
        
        for collection in collections:
            service.recompute_embedding(collection.id)
    finally:
        db.close()

def register_handlers():
    """Register all event handlers for Collections module."""
    event_bus.subscribe("resource.deleted", handle_resource_deleted)
```

### Phase 4: Register Modules in Application ✓

Update `app/__init__.py` to register modules dynamically:

```python
def register_all_modules(app: FastAPI) -> None:
    """Register all modular vertical slices with the application."""
    
    modules = [
        ("collections", "backend.app.modules.collections", "collections_router"),
        ("resources", "backend.app.modules.resources", "resources_router"),
        ("search", "backend.app.modules.search", "search_router"),
    ]
    
    for module_name, module_path, router_name in modules:
        try:
            # Dynamically import the module
            import importlib
            module = importlib.import_module(module_path)
            
            # Register the router
            if hasattr(module, router_name):
                router = getattr(module, router_name)
                app.include_router(router)
                logger.info(f"✓ Registered router for module: {module_name}")
            
            # Register event handlers
            if hasattr(module, "register_handlers"):
                register_handlers_func = getattr(module, "register_handlers")
                register_handlers_func()
                logger.info(f"✓ Registered event handlers for module: {module_name}")
        
        except Exception as e:
            logger.error(f"✗ Failed to register module {module_name}: {e}")
```

Call during application startup:

```python
def create_app() -> FastAPI:
    app = FastAPI(title="Neo Alexandria 2.0", version="0.4.0")
    
    # Initialize database
    init_database(settings.DATABASE_URL, settings.ENV)
    
    # Register modular vertical slices
    register_all_modules(app)
    
    # Register remaining layered routers (to be migrated)
    app.include_router(curation_router)
    app.include_router(authority_router)
    # ...
    
    return app
```

---

## Module Structure

### Standard Module Layout

Every module follows this structure:

```
app/modules/{module_name}/
├── __init__.py          # Public interface
├── router.py            # FastAPI endpoints
├── service.py           # Business logic
├── schema.py            # Pydantic models
├── model.py             # SQLAlchemy models (optional)
├── handlers.py          # Event handlers
├── README.md            # Module documentation
└── tests/               # Module-specific tests
    ├── test_service.py
    ├── test_router.py
    └── test_handlers.py
```

### File Responsibilities

#### `__init__.py` - Public Interface

Defines what the module exports to other parts of the application:

```python
"""Module Name - Public Interface"""

__version__ = "1.0.0"
__domain__ = "module_domain"

# Export public components
from .router import router as module_router
from .service import ModuleService
from .schema import (
    ModuleCreate,
    ModuleUpdate,
    ModuleRead,
)
from .handlers import register_handlers

__all__ = [
    "module_router",
    "ModuleService",
    "ModuleCreate",
    "ModuleUpdate",
    "ModuleRead",
    "register_handlers",
]
```

#### `router.py` - API Endpoints

Defines FastAPI routes for the module:

```python
"""Module Router - API Endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.shared.database import get_db
from .service import ModuleService
from .schema import ModuleCreate, ModuleRead

router = APIRouter(prefix="/module", tags=["module"])

@router.post("", response_model=ModuleRead)
async def create_item(
    payload: ModuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new item."""
    service = ModuleService(db)
    return service.create(payload)
```

#### `service.py` - Business Logic

Contains the core business logic:

```python
"""Module Service - Business Logic"""

from sqlalchemy.orm import Session
from .model import ModuleModel
from .schema import ModuleCreate

class ModuleService:
    """Service for module operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, data: ModuleCreate) -> ModuleModel:
        """Create a new item."""
        item = ModuleModel(**data.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
```

#### `schema.py` - Pydantic Models

Defines request/response schemas:

```python
"""Module Schemas - Pydantic Models"""

from pydantic import BaseModel
from datetime import datetime

class ModuleBase(BaseModel):
    name: str
    description: str | None = None

class ModuleCreate(ModuleBase):
    pass

class ModuleRead(ModuleBase):
    id: str
    created_at: datetime
    
    model_config = {"from_attributes": True}
```

#### `model.py` - Database Models

Defines SQLAlchemy models (optional during migration):

```python
"""Module Models - SQLAlchemy"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base, GUID

class ModuleModel(Base):
    __tablename__ = "module_items"
    
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
```

#### `handlers.py` - Event Handlers

Defines event handlers for cross-module communication:

```python
"""Module Event Handlers"""

from typing import Dict, Any
from app.shared.event_bus import event_bus
from .service import ModuleService

def handle_external_event(payload: Dict[str, Any]):
    """Handle events from other modules."""
    from app.shared.database import SessionLocal
    db = SessionLocal()
    
    try:
        service = ModuleService(db)
        # Process event
        service.do_something(payload)
    finally:
        db.close()

def register_handlers():
    """Register all event handlers for this module."""
    event_bus.subscribe("external.event", handle_external_event)
```

---

## Shared Kernel Usage

### Phase 14 Enhanced Shared Kernel

Phase 14 enhanced the shared kernel with three new services that provide common functionality across all modules:

#### Embedding Service

Centralized embedding generation for semantic search and similarity:

```python
# app/shared/embeddings.py
from app.shared.embeddings import EmbeddingService

class MyModuleService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
    
    def process_text(self, text: str):
        # Generate dense embedding (768-dim vector)
        dense_embedding = self.embedding_service.generate_embedding(text)
        
        # Generate sparse embedding (SPLADE)
        sparse_embedding = self.embedding_service.generate_sparse_embedding(text)
        
        # Batch generation for efficiency
        texts = ["text1", "text2", "text3"]
        embeddings = self.embedding_service.batch_generate(texts)
```

**Key Features**:
- Dense embeddings using nomic-embed-text-v1 (768 dimensions)
- Sparse embeddings using SPLADE for keyword-aware semantic search
- Batch processing for efficiency
- Automatic caching of embeddings

**Used By**: Search, Annotations, Collections, Graph, Recommendations

#### AI Core Service

Centralized AI/ML operations for text processing:

```python
# app/shared/ai_core.py
from app.shared.ai_core import AICore

class MyModuleService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_core = AICore()
    
    def process_content(self, text: str):
        # Generate summary (BART-large-cnn)
        summary = self.ai_core.summarize(text, max_length=150)
        
        # Extract named entities (spaCy)
        entities = self.ai_core.extract_entities(text)
        # Returns: [{"text": "Python", "label": "LANGUAGE"}, ...]
        
        # Zero-shot classification
        labels = ["science", "technology", "business"]
        scores = self.ai_core.classify_text(text, labels)
        # Returns: {"science": 0.8, "technology": 0.6, "business": 0.2}
```

**Key Features**:
- Text summarization using BART-large-cnn
- Named entity extraction using spaCy
- Zero-shot classification using BART-large-mnli
- Automatic model loading and caching

**Used By**: Quality, Scholarly, Taxonomy, Curation

#### Cache Service

Centralized caching with TTL support and pattern-based invalidation:

```python
# app/shared/cache.py
from app.shared.cache import CacheService

class MyModuleService:
    def __init__(self, db: Session):
        self.db = db
        self.cache = CacheService()
    
    def get_expensive_data(self, key: str):
        # Try cache first
        cache_key = f"mymodule:{key}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # Compute if not cached
        data = self._compute_expensive_operation(key)
        
        # Cache with TTL (3600 seconds = 1 hour)
        self.cache.set(cache_key, data, ttl=3600)
        return data
    
    def invalidate_related_cache(self, pattern: str):
        # Invalidate all keys matching pattern
        self.cache.invalidate(f"mymodule:{pattern}*")
```

**Key Features**:
- In-memory caching with Redis backend support
- TTL (time-to-live) support for automatic expiration
- Pattern-based invalidation (e.g., "user:*" invalidates all user keys)
- Automatic serialization/deserialization

**Used By**: Search, Embeddings, Quality, Recommendations

### Shared Kernel Best Practices

1. **Always use shared services** instead of creating module-specific versions
2. **Namespace cache keys** by module (e.g., "search:query:abc123")
3. **Set appropriate TTLs** based on data volatility
4. **Batch operations** when possible for efficiency
5. **Handle service failures gracefully** (embeddings, AI operations can fail)

Example with error handling:

```python
def process_with_ai(self, text: str):
    try:
        summary = self.ai_core.summarize(text)
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        summary = text[:200]  # Fallback to truncation
    
    try:
        embedding = self.embedding_service.generate_embedding(text)
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        embedding = None  # Fallback to None
    
    return summary, embedding
```

---

## Event-Driven Communication

### Event Naming Convention

Events follow the pattern: `{domain}.{action}`

Examples:
- `resource.created`
- `resource.updated`
- `resource.deleted`
- `collection.updated`
- `search.completed`
- `annotation.created`
- `quality.computed`
- `quality.outlier_detected`
- `resource.classified`
- `citation.extracted`
- `recommendation.generated`

### Phase 14 Event Catalog

Complete list of events in the system:

| Event | Emitter | Subscribers | Payload | Purpose |
|-------|---------|-------------|---------|---------|
| `resource.created` | Resources | Annotations, Quality, Taxonomy, Graph, Scholarly | `{resource_id, title, content}` | Trigger processing for new resources |
| `resource.updated` | Resources | Quality, Search | `{resource_id, changed_fields}` | Update dependent data |
| `resource.deleted` | Resources | Collections, Annotations, Graph | `{resource_id}` | Cascade cleanup |
| `annotation.created` | Annotations | Recommendations | `{annotation_id, resource_id, user_id}` | Update user profile |
| `collection.updated` | Collections | Search | `{collection_id, resource_count}` | Reindex collection |
| `collection.resource_added` | Collections | Recommendations | `{collection_id, resource_id, user_id}` | Update user preferences |
| `quality.computed` | Quality | Monitoring | `{resource_id, overall_score, dimensions}` | Track quality metrics |
| `quality.outlier_detected` | Quality | Curation | `{resource_id, outlier_score, reasons}` | Add to review queue |
| `quality.degradation_detected` | Quality | Curation | `{resource_id, old_score, new_score}` | Flag for review |
| `resource.classified` | Taxonomy | Search | `{resource_id, classifications}` | Update search index |
| `taxonomy.node_created` | Taxonomy | Monitoring | `{node_id, parent_id, name}` | Track taxonomy growth |
| `taxonomy.model_trained` | Taxonomy | Monitoring | `{model_version, accuracy, timestamp}` | Track ML model updates |
| `citation.extracted` | Graph | Monitoring | `{resource_id, citation_count}` | Track citation network |
| `graph.updated` | Graph | Search | `{resource_id, neighbor_count}` | Update graph-based features |
| `hypothesis.discovered` | Graph | Monitoring | `{hypothesis_id, confidence}` | Track LBD discoveries |
| `recommendation.generated` | Recommendations | Monitoring | `{user_id, count, strategy}` | Track recommendation quality |
| `user.profile_updated` | Recommendations | Monitoring | `{user_id, preferences}` | Track user engagement |
| `metadata.extracted` | Scholarly | Monitoring | `{resource_id, metadata_fields}` | Track metadata completeness |
| `curation.reviewed` | Curation | Monitoring | `{resource_id, reviewer, decision}` | Track curation activity |

### Emitting Events

```python
from app.shared.event_bus import event_bus

class MyModuleService:
    def create_item(self, db: Session, data: ItemCreate):
        # Create item
        item = MyItem(**data.dict())
        db.add(item)
        db.commit()
        db.refresh(item)
        
        # Emit event for other modules
        event_bus.emit("mymodule.item_created", {
            "item_id": str(item.id),
            "name": item.name,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return item
```

### Subscribing to Events

```python
# In your module handlers.py
from app.shared.event_bus import event_bus
from app.shared.database import SessionLocal
from .service import MyModuleService

def handle_resource_created(payload: dict):
    """Handle resource creation event."""
    resource_id = payload.get("resource_id")
    
    # Create fresh database session
    db = SessionLocal()
    try:
        service = MyModuleService(db)
        service.process_new_resource(resource_id)
        
        logger.info(f"Successfully processed resource.created: {resource_id}")
    except Exception as e:
        logger.error(f"Error handling resource.created: {e}", exc_info=True)
        # Don't re-raise - let other handlers continue
    finally:
        db.close()

def register_handlers():
    """Register all event handlers for this module."""
    event_bus.subscribe("resource.created", handle_resource_created)
    event_bus.subscribe("resource.updated", handle_resource_updated)
```

### Event Flow Examples

#### Example 1: Resource Creation Flow

```
User creates resource
        ↓
Resources Module
├─ Saves to database
├─ Emits: resource.created
└─ Returns response
        ↓
Event Bus distributes to subscribers:
        ↓
┌───────┴───────┬───────────┬──────────┬──────────┐
│               │           │          │          │
Quality      Taxonomy    Graph    Scholarly   Annotations
│               │           │          │          │
├─ Compute     ├─ Auto-    ├─ Extract ├─ Extract │
│  quality     │  classify │  citations│  metadata│
│  score       │  resource │          │          │
│              │           │          │          │
├─ Emit:       ├─ Emit:    ├─ Emit:   ├─ Emit:   │
│  quality.    │  resource. │  citation.│  metadata.│
│  computed    │  classified│  extracted│  extracted│
```

#### Example 2: Quality Outlier Detection Flow

```
Quality Module detects outlier
        ↓
Emits: quality.outlier_detected
        ↓
Curation Module receives event
├─ Adds resource to review queue
├─ Assigns priority based on outlier score
└─ Emits: curation.reviewed (when reviewed)
        ↓
Monitoring Module tracks metrics
```

#### Example 3: User Interaction Flow

```
User adds annotation
        ↓
Annotations Module
├─ Saves annotation
├─ Emits: annotation.created
└─ Returns response
        ↓
Recommendations Module receives event
├─ Updates user profile
├─ Adjusts preferences based on annotation
├─ Emits: user.profile_updated
└─ Triggers recommendation refresh
```

### Event Handler Best Practices

1. **Error Isolation**: Always wrap handler logic in try-except
2. **Database Sessions**: Create and close sessions within handlers
3. **Idempotency**: Handlers should be idempotent (safe to run multiple times)
4. **Logging**: Log all event processing for debugging
5. **Performance**: Keep handlers fast (<100ms)
6. **No Re-raising**: Don't re-raise exceptions - let other handlers continue

```python
def handle_event(payload: dict):
    """Example event handler with best practices."""
    from app.shared.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Process event
        service = MyService(db)
        service.process(payload)
        
        logger.info(f"Successfully processed event: {payload}")
    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True)
        # Don't re-raise - let other handlers continue
    finally:
        db.close()
```

### Monitoring Events

Check event bus metrics:

```bash
curl http://localhost:8000/monitoring/events
```

Response:
```json
{
  "events_emitted": 1523,
  "events_delivered": 4569,
  "handler_errors": 3,
  "event_types": {
    "resource.created": 234,
    "resource.updated": 1289,
    "quality.computed": 234,
    "resource.classified": 234
  },
  "latency_ms": {
    "p50": 0.8,
    "p95": 2.3,
    "p99": 5.1
  }
}
```

View event history:

```bash
curl http://localhost:8000/monitoring/events/history?limit=10
```

---

## Adding New Modules

### Step-by-Step Guide

#### 1. Create Module Structure

```bash
mkdir -p app/modules/my_module
cd app/modules/my_module
touch __init__.py router.py service.py schema.py model.py handlers.py README.md
mkdir tests
touch tests/{test_service.py,test_router.py,test_handlers.py}
```

#### 2. Define Schemas

```python
# schema.py
from pydantic import BaseModel

class MyModuleCreate(BaseModel):
    name: str
    description: str | None = None

class MyModuleRead(MyModuleCreate):
    id: str
    
    model_config = {"from_attributes": True}
```

#### 3. Define Models

```python
# model.py
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.base_model import Base, GUID

class MyModule(Base):
    __tablename__ = "my_modules"
    
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
```

#### 4. Implement Service

```python
# service.py
from sqlalchemy.orm import Session
from .model import MyModule
from .schema import MyModuleCreate

class MyModuleService:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, data: MyModuleCreate) -> MyModule:
        item = MyModule(**data.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
```

#### 5. Create Router

```python
# router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.shared.database import get_db
from .service import MyModuleService
from .schema import MyModuleCreate, MyModuleRead

router = APIRouter(prefix="/my-module", tags=["my-module"])

@router.post("", response_model=MyModuleRead)
async def create_item(
    payload: MyModuleCreate,
    db: Session = Depends(get_db)
):
    service = MyModuleService(db)
    return service.create(payload)
```

#### 6. Add Event Handlers

```python
# handlers.py
from app.shared.event_bus import event_bus

def handle_external_event(payload):
    # Handle event
    pass

def register_handlers():
    event_bus.subscribe("external.event", handle_external_event)
```

#### 7. Create Public Interface

```python
# __init__.py
"""My Module - Public Interface"""

__version__ = "1.0.0"
__domain__ = "my_module"

from .router import router as my_module_router
from .service import MyModuleService
from .schema import MyModuleCreate, MyModuleRead
from .handlers import register_handlers

__all__ = [
    "my_module_router",
    "MyModuleService",
    "MyModuleCreate",
    "MyModuleRead",
    "register_handlers",
]
```

#### 8. Register Module

Add to `app/__init__.py`:

```python
modules = [
    # Existing modules
    ("collections", "backend.app.modules.collections", "collections_router"),
    ("resources", "backend.app.modules.resources", "resources_router"),
    ("search", "backend.app.modules.search", "search_router"),
    
    # New module
    ("my_module", "backend.app.modules.my_module", "my_module_router"),
]
```

#### 9. Write Tests

```python
# tests/test_service.py
import pytest
from app.modules.my_module.service import MyModuleService
from app.modules.my_module.schema import MyModuleCreate

def test_create_item(db_session):
    service = MyModuleService(db_session)
    data = MyModuleCreate(name="Test", description="Test description")
    
    item = service.create(data)
    
    assert item.name == "Test"
    assert item.description == "Test description"
```

#### 10. Document Module

```markdown
# My Module

## Purpose

Brief description of what this module does.

## Public Interface

- `my_module_router`: FastAPI router
- `MyModuleService`: Business logic service
- `MyModuleCreate`, `MyModuleRead`: Pydantic schemas

## Events

### Emitted
- `my_module.created`: When a new item is created
- `my_module.updated`: When an item is updated

### Subscribed
- `external.event`: Handles external events

## Dependencies

- Shared Kernel (database, event_bus)
- No direct module dependencies
```

---

## Updating Existing Code

### Updating Imports

#### Old Layered Imports

```python
# Before
from app.routers.collections import router as collections_router
from app.services.collection_service import CollectionService
from app.schemas.collection import CollectionCreate, CollectionRead
from app.database.models import Collection
```

#### New Modular Imports

```python
# After
from app.modules.collections import (
    collections_router,
    CollectionService,
    CollectionCreate,
    CollectionRead,
)
# Note: Models still in database.models during migration
from app.database.models import Collection
```

### Replacing Direct Service Calls

#### Before: Direct Call (Circular Dependency)

```python
from app.services.collection_service import CollectionService

def update_resource(db: Session, resource_id: str, updates: dict):
    # Update resource
    resource.update(updates)
    db.commit()
    
    # Direct call to another service
    collection_service = CollectionService(db)
    collections = collection_service.find_collections_with_resource(resource_id)
    for collection in collections:
        collection_service.recompute_embedding(collection.id)
```

#### After: Event Emission (No Dependency)

```python
from app.shared.event_bus import event_bus

def update_resource(db: Session, resource_id: str, updates: dict):
    # Update resource
    resource.update(updates)
    db.commit()
    
    # Emit event instead of direct call
    event_bus.emit("resource.updated", {
        "resource_id": str(resource_id),
        "fields_updated": list(updates.keys())
    })
```

### Backward Compatibility

During migration, compatibility shims maintain old import paths:

```python
# app/schemas/collection.py (compatibility shim)
"""
DEPRECATED: Use backend.app.modules.collections instead.
"""
import warnings

warnings.warn(
    "backend.app.schemas.collection is deprecated. "
    "Use backend.app.modules.collections instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from new location
from backend.app.modules.collections import (
    CollectionCreate,
    CollectionUpdate,
    CollectionRead,
)

__all__ = ["CollectionCreate", "CollectionUpdate", "CollectionRead"]
```

---

## Testing Modules

### Unit Testing Services

```python
# tests/test_service.py
import pytest
from app.modules.my_module.service import MyModuleService
from app.modules.my_module.schema import MyModuleCreate

def test_create_item(db_session):
    """Test creating an item."""
    service = MyModuleService(db_session)
    data = MyModuleCreate(name="Test", description="Test description")
    
    item = service.create(data)
    
    assert item.name == "Test"
    assert item.description == "Test description"
    assert item.id is not None
```

### Testing Routers

```python
# tests/test_router.py
import pytest
from fastapi.testclient import TestClient

def test_create_endpoint(client: TestClient):
    """Test POST /my-module endpoint."""
    response = client.post("/my-module", json={
        "name": "Test",
        "description": "Test description"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test"
```

### Testing Event Handlers

```python
# tests/test_handlers.py
import pytest
from unittest.mock import Mock, patch
from app.modules.my_module.handlers import handle_external_event

def test_handle_external_event(db_session):
    """Test event handler processes events correctly."""
    payload = {"resource_id": "123"}
    
    with patch("app.modules.my_module.handlers.SessionLocal", return_value=db_session):
        handle_external_event(payload)
    
    # Assert expected side effects
    # ...
```

### Integration Testing

```python
# tests/integration/test_event_flow.py
import pytest
from app.shared.event_bus import event_bus
from app.modules.resources import delete_resource
from app.modules.collections import CollectionService

def test_resource_deletion_updates_collections(db_session):
    """Test that deleting a resource updates affected collections."""
    # Setup: Create resource and collection
    resource = create_test_resource(db_session)
    collection = create_test_collection(db_session)
    add_resource_to_collection(db_session, collection.id, resource.id)
    
    # Action: Delete resource (emits event)
    delete_resource(db_session, resource.id)
    
    # Assert: Collection was updated
    collection_service = CollectionService(db_session)
    updated_collection = collection_service.get_collection(collection.id)
    assert resource.id not in [r.id for r in updated_collection.resources]
```

---

## Troubleshooting

### Common Issues

#### 1. Circular Import Errors

**Symptom**: `ImportError: cannot import name 'X' from partially initialized module`

**Cause**: Direct imports between modules

**Solution**: Use event-driven communication instead of direct imports

```python
# Bad: Direct import
from app.modules.other_module import OtherService

# Good: Event emission
from app.shared.event_bus import event_bus
event_bus.emit("other_module.action", payload)
```

#### 2. Event Handlers Not Firing

**Symptom**: Events are emitted but handlers don't execute

**Cause**: Handlers not registered during startup

**Solution**: Ensure `register_handlers()` is called in `app/__init__.py`

```python
def register_all_modules(app: FastAPI):
    for module_name, module_path, router_name in modules:
        module = importlib.import_module(module_path)
        
        # Make sure this is called!
        if hasattr(module, "register_handlers"):
            register_handlers_func = getattr(module, "register_handlers")
            register_handlers_func()
```

#### 3. Database Session Errors in Handlers

**Symptom**: `sqlalchemy.exc.InvalidRequestError: Object is already attached to session`

**Cause**: Reusing database sessions across handler calls

**Solution**: Create fresh session in each handler

```python
def handle_event(payload):
    from app.shared.database import SessionLocal
    
    db = SessionLocal()  # Fresh session
    try:
        # Use db
        pass
    finally:
        db.close()  # Always close
```

#### 4. Module Not Found

**Symptom**: `ModuleNotFoundError: No module named 'app.modules.my_module'`

**Cause**: Module not properly registered or Python path issues

**Solution**: 
1. Verify module structure is correct
2. Check `__init__.py` exists in all directories
3. Verify module is added to registration list in `app/__init__.py`

#### 5. Deprecation Warnings

**Symptom**: `DeprecationWarning: backend.app.schemas.collection is deprecated`

**Cause**: Using old import paths

**Solution**: Update imports to use new module paths

```python
# Old
from app.schemas.collection import CollectionCreate

# New
from app.modules.collections import CollectionCreate
```

### Debugging Tips

#### 1. Enable Event Bus Logging

```python
# app/shared/event_bus.py
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def emit(self, event_type: str, payload: Dict[str, Any]):
    logger.debug(f"Emitting event: {event_type} with payload: {payload}")
    # ...
```

#### 2. Check Event Metrics

```python
# Get event bus metrics
from app.shared.event_bus import event_bus

metrics = event_bus.get_metrics()
print(f"Events emitted: {metrics.events_emitted}")
print(f"Events delivered: {metrics.events_delivered}")
print(f"Handler errors: {metrics.handler_errors}")
```

#### 3. Monitor Event Flow

Use the monitoring endpoint:

```bash
curl http://localhost:8000/monitoring/events
```

Response:
```json
{
  "events_emitted": 1523,
  "events_delivered": 4569,
  "handler_errors": 3,
  "event_types": {
    "resource.deleted": 234,
    "resource.updated": 1289
  },
  "latency_ms": {
    "p50": 0.8,
    "p95": 2.3,
    "p99": 5.1
  }
}
```

#### 4. Validate Module Isolation

Run the isolation checker:

```bash
python backend/scripts/check_module_isolation.py
```

This will detect:
- Direct imports between modules
- Circular dependencies
- Violations of module boundaries

---

## Next Steps

### Phase 14 Migration Complete ✅

All 13 modules have been successfully extracted and the modular architecture is complete:

**Completed Modules**:
- ✅ Collections (Phase 13.5)
- ✅ Resources (Phase 13.5)
- ✅ Search (Phase 13.5)
- ✅ Annotations (Phase 14)
- ✅ Scholarly (Phase 14)
- ✅ Authority (Phase 14)
- ✅ Curation (Phase 14)
- ✅ Quality (Phase 14)
- ✅ Taxonomy (Phase 14)
- ✅ Graph (Phase 14)
- ✅ Recommendations (Phase 14)
- ✅ Monitoring (Phase 14)

**Shared Kernel Enhanced**:
- ✅ database.py - Database session management
- ✅ event_bus.py - Event-driven communication
- ✅ base_model.py - Base SQLAlchemy model
- ✅ embeddings.py - Embedding generation (Phase 14)
- ✅ ai_core.py - AI/ML operations (Phase 14)
- ✅ cache.py - Caching service (Phase 14)

**Legacy Code Removed**:
- ✅ app/routers/ directory deleted
- ✅ app/services/ directory deleted
- ✅ app/schemas/ directory deleted
- ✅ Extracted models moved to modules

### Architecture Statistics

- **Total Modules**: 13
- **Total API Endpoints**: 96
- **Event Types**: 25+
- **Shared Services**: 6
- **Module Independence**: 100% (no direct module-to-module imports)
- **Event-Driven Communication**: All cross-module interactions via events

### Module Summary

| Module | Endpoints | Events Emitted | Events Subscribed | Status |
|--------|-----------|----------------|-------------------|--------|
| collections | 8 | 3 | 1 | ✅ Complete |
| resources | 10 | 3 | 0 | ✅ Complete |
| search | 5 | 1 | 3 | ✅ Complete |
| annotations | 11 | 3 | 1 | ✅ Complete |
| scholarly | 5 | 3 | 1 | ✅ Complete |
| authority | 2 | 0 | 0 | ✅ Complete |
| curation | 5 | 3 | 1 | ✅ Complete |
| quality | 9 | 3 | 2 | ✅ Complete |
| taxonomy | 11 | 3 | 1 | ✅ Complete |
| graph | 12 | 3 | 2 | ✅ Complete |
| recommendations | 6 | 3 | 2 | ✅ Complete |
| monitoring | 12 | 0 | All | ✅ Complete |

### Future Enhancements

1. **Microservices**: Extract modules into separate services
2. **API Gateway**: Add gateway for routing between services
3. **Message Queue**: Replace in-memory event bus with RabbitMQ/Kafka
4. **Service Mesh**: Add Istio/Linkerd for service-to-service communication
5. **Distributed Tracing**: Add OpenTelemetry for request tracing

---

## Resources

- [Architecture Diagram](./ARCHITECTURE_DIAGRAM.md) - Visual system architecture
- [Developer Guide](./DEVELOPER_GUIDE.md) - Development best practices
- [Module Isolation Validation](./MODULE_ISOLATION_VALIDATION.md) - Dependency checking
- [Event-Driven Refactoring](./EVENT_DRIVEN_REFACTORING.md) - Event patterns

---

*For questions or issues, please refer to the troubleshooting section or consult the development team.*
