# Development Workflows

Common development tasks and patterns for Neo Alexandria 2.0.

## Code Quality

### Formatting

```bash
# Format with Black
black backend/

# Sort imports
isort backend/

# Both at once
black backend/ && isort backend/
```

### Linting

```bash
# Lint with Ruff
ruff check backend/

# Auto-fix issues
ruff check backend/ --fix

# Type checking
mypy backend/app/
```

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pre-commit install
```

Run manually:
```bash
pre-commit run --all-files
```

## Database Management

### Create Migration

```bash
cd backend
alembic revision --autogenerate -m "Add new field to resources"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
# Rollback one step
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123
```

### Check Current Version

```bash
alembic current
```

### View Migration History

```bash
alembic history
```

## Adding New Features

### 1. Create Module (Vertical Slice)

```bash
mkdir -p app/modules/new_feature
touch app/modules/new_feature/__init__.py
touch app/modules/new_feature/router.py
touch app/modules/new_feature/service.py
touch app/modules/new_feature/schema.py
touch app/modules/new_feature/model.py
touch app/modules/new_feature/handlers.py
```

### 2. Define Model

```python
# app/modules/new_feature/model.py
from app.shared.base_model import BaseModel
from sqlalchemy import Column, String, Text

class NewFeature(BaseModel):
    __tablename__ = "new_features"
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
```

### 3. Create Schema

```python
# app/modules/new_feature/schema.py
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class NewFeatureCreate(BaseModel):
    name: str
    description: Optional[str] = None

class NewFeatureResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True
```

### 4. Implement Service

```python
# app/modules/new_feature/service.py
from sqlalchemy.orm import Session
from .model import NewFeature
from .schema import NewFeatureCreate
from app.shared.event_bus import event_bus, Event

def create_feature(db: Session, data: NewFeatureCreate) -> NewFeature:
    feature = NewFeature(**data.dict())
    db.add(feature)
    db.commit()
    db.refresh(feature)
    
    # Publish event
    event_bus.publish(Event(
        type="new_feature.created",
        payload={"id": str(feature.id), "name": feature.name}
    ))
    
    return feature
```

### 5. Create Router

```python
# app/modules/new_feature/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.shared.database import get_db
from . import service
from .schema import NewFeatureCreate, NewFeatureResponse

router = APIRouter()

@router.post("/", response_model=NewFeatureResponse)
def create(data: NewFeatureCreate, db: Session = Depends(get_db)):
    return service.create_feature(db, data)
```

### 6. Register Router

```python
# app/main.py
from app.modules.new_feature import router as new_feature_router

app.include_router(
    new_feature_router,
    prefix="/new-features",
    tags=["new-features"]
)
```

### 7. Create Migration

```bash
alembic revision --autogenerate -m "Add new_features table"
alembic upgrade head
```

## Adding API Endpoints

### GET Endpoint

```python
@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: UUID, db: Session = Depends(get_db)):
    item = service.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

### POST Endpoint

```python
@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    return service.create_item(db, data)
```

### PUT Endpoint

```python
@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: UUID,
    data: ItemUpdate,
    db: Session = Depends(get_db)
):
    item = service.update_item(db, item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

### DELETE Endpoint

```python
@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: UUID, db: Session = Depends(get_db)):
    success = service.delete_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
```

## Event Handling

### Subscribe to Events

```python
# app/modules/new_feature/handlers.py
from app.shared.event_bus import event_bus, Event

def handle_resource_created(event: Event):
    resource_id = event.payload["resource_id"]
    # React to resource creation
    pass

def register_handlers():
    event_bus.subscribe("resource.created", handle_resource_created)
```

### Publish Events

```python
from app.shared.event_bus import event_bus, Event

event_bus.publish(Event(
    type="new_feature.created",
    payload={"id": str(feature.id)}
))
```

## Debugging

### Enable Debug Logging

```bash
LOG_LEVEL=DEBUG uvicorn app.main:app --reload
```

### Database Query Logging

```python
# In settings or main.py
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### Interactive Debugging

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use VS Code debugger with launch.json
```

## Related Documentation

- [Setup Guide](setup.md) - Installation
- [Testing Guide](testing.md) - Running tests
- [Architecture](../architecture/) - System design
