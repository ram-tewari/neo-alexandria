# Design Document

## Overview

Phase 14 completes the vertical slice architecture transformation by migrating all remaining domains from the traditional layered architecture to self-contained modules. This design follows the patterns established in Phase 13.5 (Collections, Resources, Search modules) and extends them to cover the entire codebase.

## Architecture

### Target Module Structure

```
app/
├── modules/
│   ├── collections/      # ✅ Phase 13.5 (Complete)
│   ├── resources/        # ✅ Phase 13.5 (Complete)
│   ├── search/           # ✅ Phase 13.5 (Complete)
│   ├── annotations/      # 🆕 Phase 14
│   ├── quality/          # 🆕 Phase 14
│   ├── taxonomy/         # 🆕 Phase 14
│   ├── recommendations/  # 🆕 Phase 14
│   ├── graph/            # 🆕 Phase 14
│   ├── curation/         # 🆕 Phase 14
│   ├── scholarly/        # 🆕 Phase 14
│   ├── monitoring/       # 🆕 Phase 14
│   └── authority/        # 🆕 Phase 14
├── shared/
│   ├── database.py       # ✅ Phase 13.5
│   ├── event_bus.py      # ✅ Phase 13.5
│   ├── base_model.py     # ✅ Phase 13.5
│   ├── embeddings.py     # 🆕 Phase 14
│   ├── ai_core.py        # 🆕 Phase 14
│   └── cache.py          # 🆕 Phase 14
├── events/               # Event system (keep as-is)
├── tasks/                # Celery tasks (keep as-is)
├── domain/               # Domain objects (keep as-is)
└── main.py               # Application entry point
```

### Module Standard Structure

Each module follows this standard structure:

```
modules/{module_name}/
├── __init__.py           # Public interface exports
├── router.py             # FastAPI router with endpoints
├── service.py            # Business logic
├── schema.py             # Pydantic schemas
├── model.py              # SQLAlchemy models
├── handlers.py           # Event handlers
├── README.md             # Module documentation
└── tests/                # Module-specific tests
    ├── __init__.py
    ├── test_service.py
    ├── test_router.py
    └── test_handlers.py
```

## Components and Interfaces

### Annotations Module

**Purpose**: Manage text highlights, notes, and tags on resources

**Public Interface** (`modules/annotations/__init__.py`):
```python
from .router import annotations_router
from .service import AnnotationService
from .schema import (
    AnnotationCreate,
    AnnotationUpdate,
    AnnotationResponse,
    AnnotationSearchRequest
)

__version__ = "1.0.0"
__domain__ = "annotations"
```

**Events Emitted**:
- `annotation.created` - When a new annotation is created
- `annotation.updated` - When an annotation is modified
- `annotation.deleted` - When an annotation is removed

**Events Subscribed**:
- `resource.deleted` - Cascade delete annotations for deleted resource

**Endpoints** (11 total):
- POST `/resources/{resource_id}/annotations` - Create annotation
- GET `/resources/{resource_id}/annotations` - List resource annotations
- GET `/annotations` - List all user annotations
- GET `/annotations/{annotation_id}` - Get annotation
- PUT `/annotations/{annotation_id}` - Update annotation
- DELETE `/annotations/{annotation_id}` - Delete annotation
- GET `/annotations/search/fulltext` - Full-text search
- GET `/annotations/search/semantic` - Semantic search
- GET `/annotations/search/tags` - Tag-based search
- GET `/annotations/export/markdown` - Export to Markdown
- GET `/annotations/export/json` - Export to JSON

### Quality Module

**Purpose**: Multi-dimensional quality assessment and outlier detection

**Public Interface** (`modules/quality/__init__.py`):
```python
from .router import quality_router
from .service import QualityService
from .evaluator import SummarizationEvaluator
from .schema import (
    QualityDimensions,
    QualityResponse,
    OutlierReport,
    DegradationReport
)

__version__ = "1.0.0"
__domain__ = "quality"
```

**Events Emitted**:
- `quality.computed` - When quality scores are calculated
- `quality.outlier_detected` - When anomalous quality is found
- `quality.degradation_detected` - When quality degrades over time

**Events Subscribed**:
- `resource.created` - Trigger initial quality computation
- `resource.updated` - Recompute quality on changes

**Endpoints** (9 total):
- GET `/quality/resources/{resource_id}/quality-details` - Get quality breakdown
- POST `/quality/recalculate` - Trigger quality recomputation
- GET `/quality/outliers` - List quality outliers
- GET `/quality/degradation` - Get degradation report
- POST `/quality/summaries/{resource_id}/evaluate` - Evaluate summary
- GET `/quality/distribution` - Quality distribution histogram
- GET `/quality/trends` - Quality trends over time
- GET `/quality/dimensions` - Average dimension scores
- GET `/quality/review-queue` - Resources needing review

### Taxonomy Module

**Purpose**: ML-based classification and taxonomy management

**Public Interface** (`modules/taxonomy/__init__.py`):
```python
from .router import taxonomy_router
from .service import TaxonomyService
from .ml_service import MLClassificationService
from .schema import (
    TaxonomyNode,
    ClassificationResult,
    TrainingRequest
)

__version__ = "1.0.0"
__domain__ = "taxonomy"
```

**Events Emitted**:
- `resource.classified` - When a resource is classified
- `taxonomy.node_created` - When a taxonomy node is added
- `taxonomy.model_trained` - When ML model is retrained

**Events Subscribed**:
- `resource.created` - Auto-classify new resources

**Endpoints** (11 total):
- POST `/taxonomy/nodes` - Create taxonomy node
- PUT `/taxonomy/nodes/{node_id}` - Update node
- DELETE `/taxonomy/nodes/{node_id}` - Delete node
- POST `/taxonomy/nodes/{node_id}/move` - Move node
- GET `/taxonomy/tree` - Get full taxonomy tree
- GET `/taxonomy/nodes/{node_id}/ancestors` - Get ancestors
- GET `/taxonomy/nodes/{node_id}/descendants` - Get descendants
- POST `/taxonomy/classify/{resource_id}` - Classify resource
- GET `/taxonomy/active-learning/uncertain` - Get uncertain samples
- POST `/taxonomy/active-learning/feedback` - Submit feedback
- POST `/taxonomy/train` - Train ML model

### Recommendations Module

**Purpose**: Hybrid recommendation engine with NCF, content, and graph strategies

**Public Interface** (`modules/recommendations/__init__.py`):
```python
from .router import recommendations_router
from .service import RecommendationService
from .strategies import (
    ContentStrategy,
    CollaborativeStrategy,
    GraphStrategy,
    HybridStrategy
)
from .user_profile import UserProfileService
from .schema import (
    RecommendationRequest,
    RecommendationResponse,
    UserProfile,
    InteractionRecord
)

__version__ = "1.0.0"
__domain__ = "recommendations"
```

**Events Emitted**:
- `recommendation.generated` - When recommendations are produced
- `user.profile_updated` - When user preferences change
- `interaction.recorded` - When user interacts with resource

**Events Subscribed**:
- `annotation.created` - Update user profile on annotation
- `collection.resource_added` - Update profile on collection add

**Endpoints** (6 total):
- GET `/recommendations` - Get personalized recommendations
- POST `/recommendations/interactions` - Record interaction
- GET `/recommendations/profile` - Get user profile
- PUT `/recommendations/profile` - Update preferences
- POST `/recommendations/feedback` - Submit feedback
- GET `/recommendations/metrics` - Get recommendation metrics

### Graph Module

**Purpose**: Knowledge graph, citations, and literature-based discovery

**Public Interface** (`modules/graph/__init__.py`):
```python
from .router import graph_router
from .citations_router import citations_router
from .discovery_router import discovery_router
from .service import GraphService
from .citations import CitationService
from .discovery import LBDService
from .embeddings import GraphEmbeddingsService
from .schema import (
    GraphNode,
    GraphEdge,
    CitationRecord,
    DiscoveryHypothesis
)

__version__ = "1.0.0"
__domain__ = "graph"
```

**Events Emitted**:
- `citation.extracted` - When citations are parsed
- `graph.updated` - When graph structure changes
- `hypothesis.discovered` - When LBD finds connection

**Events Subscribed**:
- `resource.created` - Extract citations from new resources
- `resource.deleted` - Remove from graph

**Endpoints** (12 total):
- GET `/graph/resource/{resource_id}/neighbors` - Get neighbors
- GET `/graph/overview` - Graph statistics
- GET `/citations/resources/{resource_id}/citations` - Get citations
- GET `/citations/graph/citations` - Citation graph
- POST `/citations/resources/{resource_id}/citations/extract` - Extract citations
- POST `/citations/resolve` - Resolve citation
- POST `/citations/importance/compute` - Compute PageRank
- GET `/discovery/open` - Open discovery
- POST `/discovery/closed` - Closed discovery
- GET `/discovery/graph/resources/{resource_id}/neighbors` - Multi-hop neighbors
- GET `/discovery/hypotheses` - List hypotheses
- POST `/discovery/hypotheses/{hypothesis_id}/validate` - Validate hypothesis

### Curation Module

**Purpose**: Content review queue and batch operations

**Public Interface** (`modules/curation/__init__.py`):
```python
from .router import curation_router
from .service import CurationService
from .schema import (
    ReviewQueueItem,
    BatchUpdateRequest,
    QualityAnalysis
)

__version__ = "1.0.0"
__domain__ = "curation"
```

**Events Emitted**:
- `curation.reviewed` - When item is reviewed
- `curation.approved` - When content is approved
- `curation.rejected` - When content is rejected

**Events Subscribed**:
- `quality.outlier_detected` - Add to review queue

**Endpoints** (5 total):
- GET `/curation/review-queue` - Get review queue
- POST `/curation/batch-update` - Batch update resources
- GET `/curation/quality-analysis/{resource_id}` - Analyze quality
- GET `/curation/low-quality` - List low-quality resources
- POST `/curation/bulk-quality-check` - Bulk quality check

### Scholarly Module

**Purpose**: Academic metadata extraction (equations, tables, authors)

**Public Interface** (`modules/scholarly/__init__.py`):
```python
from .router import scholarly_router
from .extractor import MetadataExtractor
from .schema import (
    ScholarlyMetadata,
    EquationData,
    TableData
)

__version__ = "1.0.0"
__domain__ = "scholarly"
```

**Events Emitted**:
- `metadata.extracted` - When metadata is parsed
- `equations.parsed` - When equations are found
- `tables.extracted` - When tables are extracted

**Events Subscribed**:
- `resource.created` - Extract metadata from new resources

**Endpoints** (5 total):
- GET `/scholarly/resources/{resource_id}/metadata` - Get metadata
- GET `/scholarly/resources/{resource_id}/equations` - Get equations
- GET `/scholarly/resources/{resource_id}/tables` - Get tables
- POST `/scholarly/resources/{resource_id}/metadata/extract` - Extract metadata
- GET `/scholarly/metadata/completeness-stats` - Completeness statistics

### Monitoring Module

**Purpose**: System health, metrics, and observability

**Public Interface** (`modules/monitoring/__init__.py`):
```python
from .router import monitoring_router
from .service import MonitoringService
from .schema import (
    HealthStatus,
    PerformanceMetrics,
    EventMetrics
)

__version__ = "1.0.0"
__domain__ = "monitoring"
```

**Events Subscribed**:
- All events (for metrics aggregation)

**Endpoints** (12 total):
- GET `/monitoring/health` - Overall health
- GET `/monitoring/health/ml` - ML model health
- GET `/monitoring/performance` - Performance metrics
- GET `/monitoring/recommendation-quality` - Recommendation metrics
- GET `/monitoring/user-engagement` - Engagement metrics
- GET `/monitoring/model-health` - Model health
- GET `/monitoring/database` - Database status
- GET `/monitoring/db/pool` - Connection pool stats
- GET `/monitoring/events` - Event bus metrics
- GET `/monitoring/events/history` - Event history
- GET `/monitoring/cache/stats` - Cache statistics
- GET `/monitoring/workers/status` - Worker status

### Authority Module

**Purpose**: Subject authority and classification trees

**Public Interface** (`modules/authority/__init__.py`):
```python
from .router import authority_router
from .service import AuthorityService
from .schema import (
    SubjectSuggestion,
    ClassificationTree
)

__version__ = "1.0.0"
__domain__ = "authority"
```

**Endpoints** (2 total):
- GET `/authority/subjects/suggest` - Suggest subjects
- GET `/authority/classification/tree` - Get classification tree

## Data Models

### Model Migration Strategy

Each module extracts its models from `database/models.py`:

| Module | Models to Extract |
|--------|-------------------|
| Annotations | `Annotation` |
| Quality | Quality fields on `Resource` (no separate model) |
| Taxonomy | `TaxonomyNode`, `ResourceClassification` |
| Recommendations | `UserProfile`, `UserInteraction`, `RecommendationFeedback` |
| Graph | `GraphEdge`, `GraphEmbedding`, `DiscoveryHypothesis`, `Citation` |
| Curation | Uses `Resource` model (no separate model) |
| Scholarly | `ScholarlyMetadata`, `Equation`, `Table` |
| Monitoring | No database models (metrics only) |
| Authority | Uses `TaxonomyNode` (shared with Taxonomy) |

### Shared Models (Remain in database/models.py)

```python
# Models that are truly shared across multiple modules
- Resource (core entity, used by all modules)
- User (authentication, used by all modules)
```

## Event System

### Event Catalog

| Event | Emitter | Subscribers | Payload |
|-------|---------|-------------|---------|
| `resource.created` | Resources | Annotations, Quality, Taxonomy, Graph, Scholarly | `{resource_id, title, content}` |
| `resource.updated` | Resources | Quality, Search | `{resource_id, changed_fields}` |
| `resource.deleted` | Resources | Collections, Annotations, Graph | `{resource_id}` |
| `annotation.created` | Annotations | Recommendations | `{annotation_id, resource_id, user_id}` |
| `quality.computed` | Quality | - | `{resource_id, overall_score, dimensions}` |
| `quality.outlier_detected` | Quality | Curation | `{resource_id, outlier_score, reasons}` |
| `resource.classified` | Taxonomy | Search | `{resource_id, classifications}` |
| `citation.extracted` | Graph | - | `{resource_id, citation_count}` |
| `recommendation.generated` | Recommendations | Monitoring | `{user_id, count, strategy}` |

### Event Flow Diagram

```
┌─────────────┐     resource.created     ┌─────────────┐
│  Resources  │─────────────────────────▶│   Quality   │
│   Module    │                          │   Module    │
└─────────────┘                          └─────────────┘
       │                                        │
       │ resource.created                       │ quality.outlier_detected
       ▼                                        ▼
┌─────────────┐                          ┌─────────────┐
│  Taxonomy   │                          │  Curation   │
│   Module    │                          │   Module    │
└─────────────┘                          └─────────────┘
       │
       │ resource.created
       ▼
┌─────────────┐     resource.created     ┌─────────────┐
│    Graph    │◀─────────────────────────│  Scholarly  │
│   Module    │                          │   Module    │
└─────────────┘                          └─────────────┘
```

## Shared Kernel Enhancement

### Embeddings Service (`shared/embeddings.py`)

```python
class EmbeddingService:
    """Centralized embedding generation for all modules."""
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate dense embedding for text."""
        
    def generate_sparse_embedding(self, text: str) -> Dict[int, float]:
        """Generate sparse (SPLADE) embedding."""
        
    def batch_generate(self, texts: List[str]) -> List[List[float]]:
        """Batch embedding generation."""
```

### AI Core Service (`shared/ai_core.py`)

```python
class AICore:
    """Centralized AI/ML operations."""
    
    def summarize(self, text: str) -> str:
        """Generate text summary."""
        
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract named entities."""
        
    def classify_text(self, text: str, labels: List[str]) -> Dict[str, float]:
        """Zero-shot classification."""
```

### Cache Service (`shared/cache.py`)

```python
class CacheService:
    """Centralized caching for all modules."""
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set cached value with TTL."""
        
    def invalidate(self, pattern: str) -> None:
        """Invalidate keys matching pattern."""
```

## Error Handling

### Module-Level Error Handling

Each module defines its own exceptions:

```python
# modules/annotations/exceptions.py
class AnnotationNotFoundError(Exception):
    """Raised when annotation doesn't exist."""

class AnnotationPermissionError(Exception):
    """Raised when user lacks permission."""

class InvalidOffsetError(Exception):
    """Raised when text offsets are invalid."""
```

### Event Handler Error Isolation

```python
# Event handlers are isolated - failures don't affect other handlers
async def handle_resource_deleted(payload: dict):
    try:
        await cascade_delete_annotations(payload["resource_id"])
    except Exception as e:
        logger.error(f"Failed to delete annotations: {e}")
        # Error is logged but doesn't propagate
```

## Testing Strategy

### Module Testing Approach

1. **Unit Tests**: Test service methods in isolation
2. **Integration Tests**: Test router endpoints with database
3. **Event Tests**: Test event emission and handling
4. **Module Isolation Tests**: Verify no cross-module imports

### Test Structure

```
modules/{module}/tests/
├── test_service.py      # Service unit tests
├── test_router.py       # Endpoint integration tests
├── test_handlers.py     # Event handler tests
└── conftest.py          # Module-specific fixtures
```

## Migration Strategy

### Phase 14 Migration Order

1. **Shared Kernel Enhancement** - Add embeddings, AI core, cache
2. **Annotations Module** - Simple, few dependencies
3. **Scholarly Module** - Simple, few dependencies
4. **Authority Module** - Simple, few dependencies
5. **Curation Module** - Depends on Quality events
6. **Quality Module** - Core functionality, many subscribers
7. **Taxonomy Module** - ML complexity, depends on embeddings
8. **Graph Module** - Complex, multiple routers
9. **Recommendations Module** - Most complex, many services
10. **Monitoring Module** - Last, aggregates all metrics
11. **Legacy Cleanup** - Remove old directories

### Rollback Strategy

Each module migration is atomic:
1. Create new module structure
2. Copy code to new location
3. Update imports in main.py
4. Run full test suite
5. If tests pass, delete old files
6. If tests fail, revert to old structure

