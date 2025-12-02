# Migration Guide: Layered to Modular Architecture

> **Phase 13.5: Vertical Slice Architecture Migration**
>
> This guide documents the transition from a traditional layered architecture to a modular vertical slice architecture in Neo Alexandria 2.0.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Comparison](#architecture-comparison)
3. [Migration Strategy](#migration-strategy)
4. [Module Structure](#module-structure)
5. [Event-Driven Communication](#event-driven-communication)
6. [Adding New Modules](#adding-new-modules)
7. [Updating Existing Code](#updating-existing-code)
8. [Testing Modules](#testing-modules)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### What Changed?

Neo Alexandria 2.0 has transitioned from a **layered architecture** (horizontal slicing) to a **modular architecture** (vertical slicing). This change improves:

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

## Event-Driven Communication

### Event Naming Convention

Events follow the pattern: `{domain}.{action}`

Examples:
- `resource.created`
- `resource.updated`
- `resource.deleted`
- `collection.updated`
- `search.completed`

### Emitting Events

```python
from app.shared.event_bus import event_bus

# Emit an event after an operation
def delete_resource(db: Session, resource_id: str):
    # Perform operation
    db.delete(resource)
    db.commit()
    
    # Emit event
    event_bus.emit("resource.deleted", {
        "resource_id": str(resource_id),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
```

### Subscribing to Events

```python
from app.shared.event_bus import event_bus

def handle_resource_deleted(payload: Dict[str, Any]):
    """Handle resource deletion."""
    resource_id = payload.get("resource_id")
    # Process the event
    logger.info(f"Resource {resource_id} was deleted")

# Register handler
event_bus.subscribe("resource.deleted", handle_resource_deleted)
```

### Event Handler Best Practices

1. **Error Isolation**: Always wrap handler logic in try-except
2. **Database Sessions**: Create and close sessions within handlers
3. **Idempotency**: Handlers should be idempotent (safe to run multiple times)
4. **Logging**: Log all event processing for debugging
5. **Performance**: Keep handlers fast (<100ms)

```python
def handle_event(payload: Dict[str, Any]):
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

### Remaining Migrations

The following modules still need to be extracted:

- Authority Control
- Classification
- Curation
- Discovery
- Graph
- Quality
- Recommendations
- Taxonomy
- Annotations
- Citations

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
