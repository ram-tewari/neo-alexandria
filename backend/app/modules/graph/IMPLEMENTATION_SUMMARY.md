# Graph Module Implementation Summary

## Status: IN PROGRESS

This document tracks the migration of graph-related functionality from the layered architecture to the Graph module.

## Completed Tasks

### ✅ Task 8.1: Create Graph Module Structure
- Created `backend/app/modules/graph/` directory
- Created all placeholder files:
  - `__init__.py` - Module initialization
  - `router.py` - Main graph endpoints
  - `citations_router.py` - Citation endpoints
  - `discovery_router.py` - LBD endpoints
  - `service.py` - Core graph service
  - `advanced_service.py` - Advanced graph intelligence
  - `embeddings.py` - Graph embeddings
  - `citations.py` - Citation service
  - `discovery.py` - LBD service
  - `schema.py` - Pydantic schemas
  - `model.py` - Database models
  - `handlers.py` - Event handlers (skeleton)
  - `README.md` - Module documentation

## Pending Tasks

### 🔄 Task 8.2: Move Graph Routers
**Files to migrate:**
- `app/routers/graph.py` → `modules/graph/router.py`
- `app/routers/citations.py` → `modules/graph/citations_router.py`
- `app/routers/discovery.py` → `modules/graph/discovery_router.py`

**Actions required:**
1. Copy router content from source files
2. Update imports to use:
   - `from app.shared.database import get_db`
   - `from app.shared.embeddings import EmbeddingService`
   - Module-local services from `app.modules.graph.service`, etc.
3. Update router prefixes if needed
4. Verify all 12 endpoints are functional

**Endpoints to verify:**
- Graph: `/graph/related/{resource_id}`, `/graph/neighbors/{resource_id}`, etc.
- Citations: `/citations/{resource_id}`, `/citations/network/{resource_id}`, etc.
- Discovery: `/discovery/hypotheses`, `/discovery/abc-patterns`, etc.

### 🔄 Task 8.3: Move Graph Services
**Files to migrate:**
- `app/services/graph_service.py` → `modules/graph/service.py`
- `app/services/graph_service_phase10.py` → `modules/graph/advanced_service.py`
- `app/services/graph_embeddings_service.py` → `modules/graph/embeddings.py`
- `app/services/citation_service.py` → `modules/graph/citations.py`
- `app/services/lbd_service.py` → `modules/graph/discovery.py`

**Actions required:**
1. Copy service implementations
2. Update imports to use shared kernel:
   - `from app.shared.database import get_db, SessionLocal`
   - `from app.shared.embeddings import EmbeddingService`
   - `from app.shared.event_bus import event_bus`
3. Remove direct imports of other domain services
4. Use event-driven communication for cross-module interactions

### 🔄 Task 8.4: Move Graph Schemas
**Files to migrate:**
- `app/schemas/graph.py` → `modules/graph/schema.py` (merge)
- `app/schemas/discovery.py` → `modules/graph/schema.py` (merge)

**Actions required:**
1. Copy all Pydantic schemas
2. Update imports to use shared kernel
3. Organize schemas by category (graph, citations, discovery)
4. Ensure no circular dependencies

### 🔄 Task 8.5: Extract Graph Models
**Models to extract from `app/database/models.py`:**
- `GraphEdge` - Graph relationship edges
- `GraphEmbedding` - Graph node embeddings
- `DiscoveryHypothesis` - LBD hypotheses
- `Citation` - Citation records

**Actions required:**
1. Copy model definitions to `modules/graph/model.py`
2. Update to import from `app.shared.base_model`
3. Use string-based relationship references for cross-module relationships
4. Update `database/models.py` to import from module

### 🔄 Task 8.6: Create Graph Public Interface
**File:** `modules/graph/__init__.py`

**Actions required:**
1. Import all routers, services, and schemas
2. Export public interface:
   ```python
   from .router import router as graph_router
   from .citations_router import router as citations_router
   from .discovery_router import router as discovery_router
   from .service import GraphService
   from .advanced_service import AdvancedGraphService
   from .embeddings import GraphEmbeddingsService
   from .citations import CitationService
   from .discovery import LBDService
   from .schema import *
   ```
3. Add to `__all__` list

### 🔄 Task 8.7: Create Graph Event Handlers
**File:** `modules/graph/handlers.py`

**Actions required:**
1. Implement `handle_resource_created(payload)`:
   - Extract citations from resource
   - Add resource to knowledge graph
   - Emit `citation.extracted` event
   - Emit `graph.updated` event
2. Implement `handle_resource_deleted(payload)`:
   - Remove resource from graph
   - Update graph relationships
   - Emit `graph.updated` event
3. Implement `register_handlers()`:
   - Subscribe to `resource.created`
   - Subscribe to `resource.deleted`

### ⏸️ Task 8.8: Write Graph Module Tests (Optional)
**Test files to create:**
- `modules/graph/tests/test_service.py`
- `modules/graph/tests/test_citations.py`
- `modules/graph/tests/test_discovery.py`
- `modules/graph/tests/test_router.py`
- `modules/graph/tests/test_handlers.py`

**Test coverage:**
- Graph algorithms and operations
- Citation extraction and network building
- LBD hypothesis generation
- Event handler behavior
- API endpoint functionality

## Migration Notes

### Dependencies
The Graph module depends on:
- **Shared Kernel:**
  - `shared.database` - Database sessions
  - `shared.embeddings` - Embedding generation
  - `shared.event_bus` - Event communication
- **External Libraries:**
  - NetworkX - Graph algorithms
  - FAISS - Vector similarity
  - NumPy - Numerical operations

### Import Pattern Changes
**Before (layered):**
```python
from app.database.base import get_db
from app.services.embedding_service import EmbeddingService
from app.services.resource_service import ResourceService
```

**After (modular):**
```python
from app.shared.database import get_db
from app.shared.embeddings import EmbeddingService
from app.shared.event_bus import event_bus
# No direct import of ResourceService - use events instead
```

### Event-Driven Communication
Instead of directly calling other services:
```python
# OLD: Direct service call
resource = resource_service.get_resource(resource_id)

# NEW: Event-driven
event_bus.emit("graph.needs_resource", {"resource_id": resource_id})
# Or query through shared database
```

### Backward Compatibility
- All API endpoints maintain same paths
- Response schemas remain unchanged
- Existing clients continue to work
- Old router imports deprecated but functional during transition

## Testing Strategy

### Unit Tests
- Test graph algorithms in isolation
- Test citation extraction logic
- Test LBD hypothesis generation
- Mock database and external services

### Integration Tests
- Test API endpoints end-to-end
- Test event handler integration
- Test cross-module communication
- Test with real database

### Performance Tests
- Graph operations with large datasets
- Citation network building performance
- Embedding generation throughput
- Event bus latency

## Rollback Plan

If issues arise:
1. Keep old routers/services in place temporarily
2. Use feature flags to toggle between old/new
3. Gradual migration of endpoints
4. Monitor error rates and performance
5. Quick rollback capability via imports

## Next Steps

1. Complete Task 8.2: Move routers
2. Complete Task 8.3: Move services
3. Complete Task 8.4: Move schemas
4. Complete Task 8.5: Extract models
5. Complete Task 8.6: Update public interface
6. Complete Task 8.7: Implement event handlers
7. Update main.py to register graph module
8. Run integration tests
9. Update documentation

## Questions/Issues

- [ ] Verify all 12 endpoints are documented
- [ ] Confirm event payload structures
- [ ] Review graph algorithm performance
- [ ] Check citation extraction accuracy
- [ ] Validate LBD hypothesis quality

## References

- Requirements: `.kiro/specs/backend/phase14-complete-vertical-slice-refactor/requirements.md` (Requirement 5)
- Design: `.kiro/specs/backend/phase14-complete-vertical-slice-refactor/design.md`
- Module README: `backend/app/modules/graph/README.md`
- API Documentation: `backend/docs/api/graph.md`
