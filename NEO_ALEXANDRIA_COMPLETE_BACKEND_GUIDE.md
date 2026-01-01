# Neo Alexandria 2.0 - Complete Backend Guide

> **Comprehensive Documentation for External AI Systems**
> 
> This unified document contains all essential information about the Neo Alexandria 2.0 backend codebase, architecture, goals, and implementation details. Use this as a complete reference to understand the system.
>
> **Last Updated**: Phase 14 - Complete Vertical Slice Refactor
> **Version**: 2.0
> **Status**: Production-Ready Architecture

---

## Table of Contents

1. [Product Overview](#product-overview)
2. [Architecture](#architecture)
3. [Technical Stack](#technical-stack)
4. [Module System](#module-system)
5. [Event-Driven Communication](#event-driven-communication)
6. [Database Architecture](#database-architecture)
7. [API Reference](#api-reference)
8. [Development Workflow](#development-workflow)
9. [Testing Strategy](#testing-strategy)
10. [Deployment](#deployment)

---

# 1. Product Overview

## Purpose

Neo Alexandria 2.0 is an advanced knowledge management system that combines traditional information retrieval with modern AI-powered features to deliver intelligent content processing, advanced search, and personalized recommendations.

## Target Users

1. **Researchers** - Academic and industry researchers managing papers, articles, and datasets
2. **Knowledge Workers** - Professionals curating domain-specific knowledge bases
3. **Students** - Learners organizing study materials and research
4. **Teams** - Collaborative knowledge management for organizations

## Core Value Propositions

### Intelligent Content Processing
- Automatic summarization, tagging, and classification
- Quality assessment and metadata extraction
- Multi-format support (HTML, PDF, plain text)

### Advanced Discovery
- Hybrid search combining keyword and semantic approaches
- Knowledge graph for relationship exploration
- Citation network analysis
- Personalized recommendations

### Active Reading & Annotation
- Precise text highlighting with notes
- Semantic search across annotations
- Export to external tools (Markdown, JSON)

### Organization & Curation
- Flexible collection management
- Hierarchical taxonomy
- Quality-based filtering
- Batch operations

## Non-Goals (What We Are NOT Building)

❌ **Social Network** - No user profiles, followers, or social features
❌ **Content Creation Platform** - No authoring tools or publishing workflows
❌ **File Storage Service** - No general-purpose file hosting
❌ **Real-time Collaboration** - No simultaneous editing or live cursors
❌ **Mobile Apps** - Web-first, responsive design only
❌ **Enterprise SSO** - Simple authentication only
❌ **Multi-tenancy** - Single-user or small team focus
❌ **Blockchain/Web3** - Traditional database architecture
❌ **Video/Audio Processing** - Text and document focus only

## Product Principles

1. **API-First** - All features accessible via RESTful API
2. **Privacy-Focused** - User data stays local or self-hosted
3. **Open Source** - Transparent, extensible, community-driven
4. **Performance** - Fast response times (<200ms for most operations)
5. **Simplicity** - Clean interfaces, minimal configuration
6. **Extensibility** - Plugin architecture for custom features

## Success Metrics

- **Search Quality**: nDCG > 0.7 for hybrid search
- **Response Time**: P95 < 200ms for API endpoints
- **Classification Accuracy**: > 85% for ML taxonomy
- **User Satisfaction**: Qualitative feedback from early adopters
- **System Reliability**: 99.9% uptime for self-hosted deployments

---

# 2. Architecture

## Architecture Type

**Type**: Modular Monolith with Event-Driven Communication
**Pattern**: Vertical slices with shared kernel
**Deployment**: Self-hosted, containerized

## Architectural Principles

1. **Vertical Slice Architecture**: Each module is self-contained with its own models, schemas, services, and routes
2. **Event-Driven Communication**: Modules communicate via event bus (no direct imports)
3. **Shared Kernel**: Cross-cutting concerns (database, cache, embeddings, AI) in shared layer
4. **Zero Circular Dependencies**: Enforced by module isolation rules
5. **API-First Design**: All functionality exposed via REST API

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    NEO ALEXANDRIA 2.0 - COMPLETE MODULAR ARCHITECTURE                   │
│                              (13 Vertical Slice Modules)                                │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │                         FastAPI Application (main.py)                            │   │
│  │                    Registers all module routers & event handlers                 │   │
│  └────────────────────────────────┬─────────────────────────────────────────────────┘   │
│                                   │                                                     │
│                                   │ Module Registration                                 │
│                                   │                                                     │
│       ┌───────────────────────────┼───────────────────────────────────┐                 │
│       │                           │                                   │                 │
│       ▼                           ▼                                   ▼                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Resources │  │Collections│  │  Search  │  │Annotations│  │ Scholarly│  │ Authority│   │
│  │  Module  │  │  Module  │  │  Module  │  │  Module  │  │  Module  │  │  Module  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │             │             │           │
│       │             │             │             │             │             │           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Curation │  │  Quality │  │ Taxonomy │  │  Graph   │  │Recommend-│  │Monitoring│   │
│  │  Module  │  │  Module  │  │  Module  │  │  Module  │  │ ations   │  │  Module  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │             │             │           │
│       │             │             │             │             │             │           │
│       │    ┌────────┴─────────────┴─────────────┴─────────────┴─────────────┘           │
│       │    │                                                                            │
│       │    ▼                                                                            │
│       │  ┌─────────────────────────────────────────────────────────────────┐            │
│       │  │                      Shared Kernel                              │            │
│       │  │  ┌──────────┐  ┌──────────────┐  ┌──────────────┐               │            │
│       └─►│  │ Database │  │  Event Bus   │  │  Base Model  │               │◄──────────┘│
│          │  │ (Session)│  │  (Pub/Sub)   │  │   (GUID)     │               │            │
│          │  └──────────┘  └──────────────┘  └──────────────┘               │            │
│          │  ┌──────────────────────────────────────────────────────────┐   │            │
│          │  │  Cross-Cutting Services:                                 │   │            │
│          │  │  • EmbeddingService (dense & sparse embeddings)          │   │            │
│          │  │  • AICore (summarization, entity extraction)             │   │            │
│          │  │  • CacheService (Redis caching with TTL)                 │   │            │
│          │  └──────────────────────────────────────────────────────────┘   │            │
│          └─────────────────────────────────────────────────────────────────┘            │
│                                                                                         │
│  Event-Driven Communication (All Modules):                                              │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │  Resources ──[resource.created]──► Scholarly, Quality, Taxonomy, Graph           │   │
│  │  Resources ──[resource.updated]──► Collections, Quality, Search                  │   │
│  │  Resources ──[resource.deleted]──► Collections, Annotations, Graph               │   │
│  │  Quality ────[quality.outlier_detected]──► Curation                              │   │
│  │  Annotations ─[annotation.created]──► Recommendations                            │   │
│  │  Collections ─[collection.resource_added]──► Recommendations                     │   │
│  │  Taxonomy ───[resource.classified]──► Monitoring                                 │   │
│  │  Graph ──────[citation.extracted]──► Monitoring                                  │   │
│  │  All Modules ──[*.events]──► Monitoring (metrics aggregation)                    │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## 9-Layer Architecture

The system is organized into 9 distinct layers:

1. **Presentation Layer** - FastAPI routers, request/response handling
2. **Domain Layer** - Rich domain objects with business logic (DDD)
3. **Service Layer** - Business operations and orchestration
4. **Event-Driven Layer** - Pub/sub event bus for module communication
5. **Task Processing Layer** - Celery distributed task queue
6. **Caching Layer** - Redis multi-layer caching
7. **Data Access Layer** - SQLAlchemy ORM
8. **Database Layer** - SQLite (dev) / PostgreSQL (prod)
9. **Machine Learning Layer** - PyTorch + Transformers

---

# 3. Technical Stack

## Backend Stack

### Core Framework
- **Python 3.8+** - Primary language
- **FastAPI** - Web framework for REST API
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation and serialization

### Database
- **SQLite** - Development and small deployments
- **PostgreSQL 15+** - Production deployments
- **Alembic** - Database migrations
- **SQLAlchemy 2.0** - ORM with async support

### AI/ML
- **Transformers (Hugging Face)** - NLP models
- **PyTorch** - Deep learning framework
- **Sentence-Transformers** - Embedding generation
- **FAISS** - Vector similarity search
- **spaCy** - NLP processing

### Task Processing
- **Celery** - Async task queue
- **Redis** - Cache and message broker

### Testing
- **pytest** - Test framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Coverage reporting
- **hypothesis** - Property-based testing
- **Golden Data Pattern** - Immutable test expectations in JSON files
- **Protocol-Based Testing** - Anti-gaslighting test framework

## Development Tools

### Code Quality
- **Ruff** - Python linter and formatter
- **ESLint** - JavaScript/TypeScript linter
- **Prettier** - Code formatter
- **pre-commit** - Git hooks for quality checks

### Version Control
- **Git** - Source control
- **GitHub** - Repository hosting
- **GitHub Actions** - CI/CD pipelines

### Containerization
- **Docker** - Container runtime
- **Docker Compose** - Multi-container orchestration

## Performance Requirements

- API response time: P95 < 200ms
- Search latency: < 500ms for hybrid search
- Embedding generation: < 2s per document
- Database queries: < 100ms for most operations
- Event emission + delivery: < 1ms (p95)
- Module startup: < 10 seconds total

## Scalability Targets

- 100K+ resources in database
- 10K+ concurrent embeddings
- 1K+ collections per user
- 100+ requests/second

## Resource Limits

- Memory: 4GB minimum, 8GB recommended
- Storage: 10GB minimum for models and data
- CPU: 2+ cores recommended
- GPU: Optional, improves ML performance 10x

---

# 4. Module System

## 13 Domain Modules

The system is organized into 13 self-contained vertical slice modules:

1. **Resources** - Resource CRUD operations and metadata
2. **Collections** - Collection management and resource organization
3. **Search** - Hybrid search (keyword, semantic, full-text)
4. **Annotations** - Text highlights, notes, and tags on resources
5. **Scholarly** - Academic metadata extraction (equations, tables, citations)
6. **Authority** - Subject authority and classification trees
7. **Curation** - Content review and batch operations
8. **Quality** - Multi-dimensional quality assessment
9. **Taxonomy** - ML-based classification and taxonomy management
10. **Graph** - Knowledge graph, citations, and discovery
11. **Recommendations** - Hybrid recommendation engine (NCF, content, graph)
12. **Monitoring** - System health, metrics, and observability

## Vertical Slice Pattern

Each module follows a consistent structure:

```
app/modules/{module_name}/
├── __init__.py          # Public interface & exports
├── router.py            # FastAPI endpoints
├── service.py           # Business logic
├── schema.py            # Pydantic models
├── model.py             # SQLAlchemy models
├── handlers.py          # Event handlers
├── README.md            # Module documentation
└── tests/               # Module-specific tests
```

### Module Benefits

- **High Cohesion**: Related code stays together
- **Low Coupling**: Modules communicate via events only
- **Independent Testing**: Each module can be tested in isolation
- **Clear Boundaries**: Explicit public interfaces via `__init__.py`
- **Event-Driven**: Asynchronous, decoupled communication
- **Scalability**: Modules can be extracted to microservices if needed
- **Maintainability**: Changes to one module don't affect others

## Module Isolation Rules

### Allowed Imports
✅ Modules can import from:
- `app.shared.*` - Shared kernel only
- `app.events.*` - Event system
- `app.domain.*` - Domain objects
- Standard library and third-party packages

### Forbidden Imports
❌ Modules CANNOT import from:
- Other modules (`app.modules.*`)
- Legacy layers (`app.routers.*`, `app.services.*`, `app.schemas.*`)

### Communication Pattern
- **Direct calls**: Use shared kernel services
- **Cross-module**: Use event bus only
- **Example**: Quality module needs resource data → subscribe to `resource.created` event

### Validation
```bash
# Check all modules for violations
python scripts/check_module_isolation.py

# Generates dependency graph
# Fails if circular dependencies or direct module imports found
```

## Module Summary Table

| Module | Purpose | Key Events Emitted | Key Events Consumed |
|--------|---------|-------------------|---------------------|
| **Resources** | Resource CRUD operations | resource.created, resource.updated, resource.deleted | - |
| **Collections** | Collection management | collection.created, collection.updated, collection.resource_added | resource.created, resource.updated, resource.deleted |
| **Search** | Hybrid search (keyword + semantic + sparse) | search.executed | resource.created, resource.updated |
| **Annotations** | Text highlights and notes | annotation.created, annotation.updated, annotation.deleted | resource.deleted |
| **Scholarly** | Academic metadata extraction | metadata.extracted, equations.parsed, tables.extracted | resource.created |
| **Authority** | Subject authority and classification trees | - | - |
| **Curation** | Content review and batch operations | curation.reviewed, curation.approved, curation.rejected | quality.outlier_detected |
| **Quality** | Multi-dimensional quality assessment | quality.computed, quality.outlier_detected, quality.degradation_detected | resource.created, resource.updated |
| **Taxonomy** | ML classification and taxonomy management | resource.classified, taxonomy.node_created, taxonomy.model_trained | resource.created |
| **Graph** | Knowledge graph, citations, discovery | citation.extracted, graph.updated, hypothesis.discovered | resource.created, resource.deleted |
| **Recommendations** | Hybrid recommendation engine | recommendation.generated, user.profile_updated, interaction.recorded | annotation.created, collection.resource_added |
| **Monitoring** | System health and metrics aggregation | - | All events (for metrics) |

---

# 5. Event-Driven Communication

## Event Bus Architecture

The event system enables loose coupling between modules through publish-subscribe messaging.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EVENT BUS (Pub/Sub)                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Publishers                    Event Bus                  Subscribers   │
│  ──────────                    ─────────                  ───────────   │
│                                                                         │
│  ┌──────────┐                ┌───────────┐              ┌──────────┐    │
│  │Resources │──publish──────►│           │──notify─────►│Collections│   │
│  │ Module   │                │           │              │  Module   │   │
│  └──────────┘                │           │              └──────────┘    │
│                              │  Event    │                              │
│  ┌──────────┐                │   Bus     │              ┌──────────┐    │
│  │Collections│──publish─────►│           │──notify─────►│ Search   │    │
│  │  Module  │                │           │              │  Module  │    │
│  └──────────┘                │           │              └──────────┘    │
│                              │           │                              │
│  ┌──────────┐                │           │              ┌──────────┐    │
│  │ Search   │──publish──────►│           │──notify─────►│Analytics │    │
│  │  Module  │                └───────────┘              │ (future) │    │
│  └──────────┘                                           └──────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Event Types

### Resource Events

| Event | Payload | Triggered When |
|-------|---------|----------------|
| `resource.created` | `{resource_id, title, ...}` | New resource ingested |
| `resource.updated` | `{resource_id, changes}` | Resource metadata updated |
| `resource.deleted` | `{resource_id}` | Resource deleted |
| `resource.content_changed` | `{resource_id}` | Content modified |
| `resource.metadata_changed` | `{resource_id}` | Metadata modified |
| `resource.classified` | `{resource_id, taxonomy_ids}` | Classification assigned |
| `resource.quality_computed` | `{resource_id, score}` | Quality score calculated |

### Collection Events

| Event | Payload | Triggered When |
|-------|---------|----------------|
| `collection.created` | `{collection_id, name}` | New collection created |
| `collection.updated` | `{collection_id, changes}` | Collection metadata updated |
| `collection.deleted` | `{collection_id}` | Collection deleted |
| `collection.resource_added` | `{collection_id, resource_ids}` | Resources added |
| `collection.resource_removed` | `{collection_id, resource_ids}` | Resources removed |

### Search Events

| Event | Payload | Triggered When |
|-------|---------|----------------|
| `search.executed` | `{query, results_count, latency}` | Search performed |
| `search.facets_computed` | `{query, facets}` | Facets calculated |

### Processing Events

| Event | Payload | Triggered When |
|-------|---------|----------------|
| `ingestion.started` | `{url, resource_id}` | Ingestion begins |
| `ingestion.completed` | `{resource_id, status}` | Ingestion finishes |
| `citations.extracted` | `{resource_id, citation_ids}` | Citations parsed |
| `authors.extracted` | `{resource_id, author_names}` | Authors identified |

## Event Flow Example

```
1. User creates resource → resources module emits resource.created
2. Quality module subscribes → computes quality scores
3. Taxonomy module subscribes → auto-classifies resource
4. Scholarly module subscribes → extracts metadata
5. Graph module subscribes → extracts citations
6. All happen asynchronously, no blocking
```

## Celery Task Queue

### Task Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CELERY TASK HIERARCHY                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                        ┌──────────────────┐                                 │
│                        │  DatabaseTask    │                                 │
│                        │  (Base Class)    │                                 │
│                        │  • __call__()    │                                 │
│                        │  • Session mgmt  │                                 │
│                        └────────┬─────────┘                                 │
│                                 │                                           │
│         ┌───────────────────────┼───────────────────────┐                   │
│         │                       │                       │                   │
│  ┌──────▼──────────┐   ┌────────▼─────────┐   ┌─────────▼────────┐          │
│  │ regenerate_     │   │ recompute_       │   │ update_search_   │          │
│  │ embedding_task  │   │ quality_task     │   │ index_task       │          │
│  ├─────────────────┤   ├──────────────────┤   ├──────────────────┤          │
│  │ • max_retries=3 │   │ • max_retries=2  │   │ • priority=9     │          │
│  │ • retry_delay=60│   │ • priority=5     │   │ • max_retries=3  │          │
│  │ • priority=7    │   │ • countdown=10   │   │ • countdown=1    │          │
│  │ • countdown=5   │   └──────────────────┘   └──────────────────┘          │
│  └─────────────────┘                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Task Routing

- **urgent queue** (priority 9) - Search index, cache invalidation
- **high_priority queue** (priority 7) - Embeddings
- **ml_tasks queue** (priority 5) - Classification, quality
- **batch queue** (priority 3) - Batch processing
- **default queue** (priority 5) - General tasks

## Redis Caching

### Cache Key Strategy

```
embedding:{resource_id}           TTL: 3600s (1 hour)
quality:{resource_id}             TTL: 1800s (30 minutes)
search_query:{hash}               TTL: 300s (5 minutes)
resource:{resource_id}            TTL: 600s (10 minutes)
graph:{resource_id}:neighbors     TTL: 1800s (30 minutes)
user:{user_id}:profile            TTL: 600s (10 minutes)
classification:{resource_id}      TTL: 3600s (1 hour)
```

### Cache Invalidation Patterns

```
resource:{resource_id}:*          → All resource-related caches
search_query:*                    → All search result caches
graph:*                           → All graph caches
user:{user_id}:*                  → All user-related caches
```

## Performance Characteristics

- **Event emission + delivery**: < 1ms (p95)
- **Cache hit rate**: 60-70% for repeated operations
- **Task throughput**: 400 tasks/minute with 4 workers
- **Scalability**: Linear scaling with worker count
- **Task reliability**: <1% failure rate with automatic retries

---

# 6. Database Architecture

## Database Strategy

### SQLite (Development)
```bash
DATABASE_URL=sqlite:///./backend.db
```
- Zero configuration
- File-based, portable
- Limited concurrency
- No advanced features

### PostgreSQL (Production)
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
```
- High concurrency
- JSONB support
- Full-text search
- Advanced indexing
- Connection pooling

## Core Database Models

### Resource Model
```python
class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(String, primary_key=True)  # GUID
    title = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text)
    url = Column(String, unique=True)
    creator = Column(String)
    publisher = Column(String)
    source = Column(String)
    language = Column(String, default="en")
    type = Column(String)
    subject = Column(JSON)  # List of subjects
    classification_code = Column(String)
    quality_score = Column(Float)
    read_status = Column(String, default="unread")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    embeddings = relationship("Embedding", back_populates="resource")
    annotations = relationship("Annotation", back_populates="resource")
    collections = relationship("Collection", secondary="collection_resources")
```

### Collection Model
```python
class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    visibility = Column(String, default="private")  # private, shared, public
    parent_id = Column(String, ForeignKey("collections.id"))
    owner_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    resources = relationship("Resource", secondary="collection_resources")
    parent = relationship("Collection", remote_side=[id])
    children = relationship("Collection", back_populates="parent")
```

### Annotation Model
```python
class Annotation(Base):
    __tablename__ = "annotations"
    
    id = Column(String, primary_key=True)
    resource_id = Column(String, ForeignKey("resources.id"))
    user_id = Column(String, ForeignKey("users.id"))
    start_offset = Column(Integer, nullable=False)
    end_offset = Column(Integer, nullable=False)
    highlighted_text = Column(Text, nullable=False)
    note = Column(Text)
    tags = Column(JSON)  # List of tags
    color = Column(String, default="#FFD700")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    resource = relationship("Resource", back_populates="annotations")
```

### TaxonomyNode Model
```python
class TaxonomyNode(Base):
    __tablename__ = "taxonomy_nodes"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    parent_id = Column(String, ForeignKey("taxonomy_nodes.id"))
    path = Column(String)  # Materialized path for efficient queries
    keywords = Column(JSON)  # List of keywords
    allow_resources = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    parent = relationship("TaxonomyNode", remote_side=[id])
    children = relationship("TaxonomyNode", back_populates="parent")
```

## Database Migrations

Using Alembic for schema versioning:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

# 7. API Reference

## Base URL
```
http://127.0.0.1:8000
```

## Authentication
Currently, no authentication is required for development. Future releases will include API key authentication.

## Core Endpoints

### Resources API

```
POST   /resources                    # Create resource
GET    /resources                    # List resources
GET    /resources/{id}               # Get resource
PUT    /resources/{id}               # Update resource
DELETE /resources/{id}               # Delete resource
GET    /resources/{id}/status        # Get ingestion status
```

### Search API

```
POST   /search                       # Hybrid search
GET    /search/three-way-hybrid      # Three-way fusion search
GET    /search/compare-methods       # Compare search methods
POST   /search/evaluate              # Evaluate search quality
```

### Collections API

```
POST   /collections                  # Create collection
GET    /collections                  # List collections
GET    /collections/{id}             # Get collection
PUT    /collections/{id}             # Update collection
DELETE /collections/{id}             # Delete collection
POST   /collections/{id}/resources   # Add resources
DELETE /collections/{id}/resources   # Remove resources
GET    /collections/{id}/recommendations  # Get recommendations
```

### Annotations API

```
POST   /resources/{id}/annotations   # Create annotation
GET    /resources/{id}/annotations   # List resource annotations
GET    /annotations                  # List user annotations
GET    /annotations/{id}             # Get annotation
PUT    /annotations/{id}             # Update annotation
DELETE /annotations/{id}             # Delete annotation
GET    /annotations/search/fulltext  # Full-text search
GET    /annotations/search/semantic  # Semantic search
GET    /annotations/export/markdown  # Export to Markdown
GET    /annotations/export/json      # Export to JSON
```

### Taxonomy API

```
POST   /taxonomy/nodes               # Create taxonomy node
PUT    /taxonomy/nodes/{id}          # Update node
DELETE /taxonomy/nodes/{id}          # Delete node
POST   /taxonomy/nodes/{id}/move     # Move node
GET    /taxonomy/tree                # Get taxonomy tree
POST   /taxonomy/classify/{id}       # Classify resource
GET    /taxonomy/active-learning/uncertain  # Get uncertain predictions
POST   /taxonomy/active-learning/feedback   # Submit feedback
POST   /taxonomy/train               # Train ML model
```

### Graph API

```
GET    /graph/resource/{id}/neighbors  # Get related resources
GET    /graph/overview                 # Get global overview
GET    /citations/resources/{id}/citations  # Get citations
GET    /citations/graph/citations      # Get citation network
POST   /citations/resources/{id}/citations/extract  # Extract citations
POST   /citations/resolve              # Resolve internal citations
POST   /citations/importance/compute   # Compute PageRank
```

### Recommendations API

```
GET    /recommendations               # Get personalized recommendations
POST   /recommendations/track         # Track user interaction
GET    /recommendations/profile       # Get user profile
```

### Quality API

```
GET    /quality/resources/{id}        # Get quality score
POST   /quality/compute               # Compute quality
GET    /quality/outliers              # Get quality outliers
```

### Monitoring API

```
GET    /monitoring/health             # Health check
GET    /monitoring/metrics            # System metrics
GET    /monitoring/database           # Database stats
GET    /monitoring/cache              # Cache stats
```

## Response Format

```json
{
  "data": {},
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 25
  }
}
```

## Error Format

```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

# 8. Development Workflow

## Common Commands

### Backend Development
```bash
# Start dev server
cd backend
uvicorn app.main:app --reload

# Run migrations
alembic upgrade head

# Run tests
pytest tests/ -v

# Run module-specific tests
pytest tests/modules/test_resources_endpoints.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run property-based tests
pytest tests/properties/ -v

# Run E2E workflow tests
pytest tests/test_e2e_workflows.py -v

# Run performance tests
pytest tests/performance.py -v

# Lint and format
ruff check .
ruff format .

# Check module isolation
python scripts/check_module_isolation.py

# Verify all modules load
python test_app_startup.py
```

### Module Development
```bash
# Create new module structure
mkdir -p app/modules/mymodule
touch app/modules/mymodule/{__init__.py,router.py,service.py,schema.py,model.py,handlers.py,README.md}

# Register module in main.py
# Add to register_all_modules() function

# Test module endpoints
pytest tests/modules/test_mymodule_endpoints.py -v

# Verify module isolation
python scripts/check_module_isolation.py
```

### Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose up -d --build
```

### Database
```bash
# Create migration
cd backend
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Backup SQLite
cp backend.db backend.db.backup

# Backup PostgreSQL
pg_dump -U user -d database > backup.sql
```

## Environment Variables

### Required
```bash
DATABASE_URL=sqlite:///./backend.db
```

### Optional (with defaults)
```bash
# AI Models
EMBEDDING_MODEL_NAME=nomic-ai/nomic-embed-text-v1
SUMMARIZER_MODEL=facebook/bart-large-cnn

# Search
DEFAULT_HYBRID_SEARCH_WEIGHT=0.5
EMBEDDING_CACHE_SIZE=1000

# Graph
GRAPH_WEIGHT_VECTOR=0.6
GRAPH_WEIGHT_TAGS=0.3
GRAPH_WEIGHT_CLASSIFICATION=0.1

# Testing
TEST_DATABASE_URL=sqlite:///:memory:
```

---

# 9. Testing Strategy

## Testing Patterns

### Protocol-Based Testing (Golden Data Pattern)
Tests load expectations from immutable JSON files. Never modify tests to match implementation - fix implementation instead.

```bash
# Run tests with Golden Data validation
pytest tests/modules/quality/test_scoring.py -v

# Run all module tests
pytest tests/modules/ -v

# Run tests for specific module
pytest tests/modules/search/ -v

# Run property-based tests (hypothesis)
pytest tests/properties/ -v

# Check test infrastructure
pytest tests/test_infrastructure_checkpoint.py -v
```

### Test Structure

```
tests/
├── unit/                      # Unit tests
├── integration/               # Integration tests
├── performance/               # Performance tests
├── modules/                   # Module-specific tests
│   ├── resources/
│   ├── collections/
│   ├── search/
│   ├── annotations/
│   ├── taxonomy/
│   ├── graph/
│   ├── recommendations/
│   ├── quality/
│   └── monitoring/
├── golden_data/               # Immutable test expectations
│   ├── search_endpoints.json
│   ├── fulltext_search.json
│   ├── semantic_search.json
│   ├── hybrid_recommendations.json
│   └── taxonomy_prediction.json
├── properties/                # Property-based tests
└── conftest.py                # Pytest configuration
```

### Test Fixtures

```python
# conftest.py
@pytest.fixture
def db():
    """Provide test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture
def test_client(db):
    """Provide FastAPI test client."""
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as client:
        yield client
```

## Test Coverage Goals

- **Unit Tests**: >80% coverage
- **Integration Tests**: All critical workflows
- **E2E Tests**: Complete user journeys
- **Performance Tests**: All critical endpoints

---

# 10. Deployment

## Production Requirements

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended for AI features
- **Storage**: SSD recommended for database performance (minimum 20GB free space)
- **Network**: Stable internet connection for content ingestion
- **Database**: PostgreSQL 15+ for production (SQLite for development)

## Docker Compose Orchestration

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    
  celery_worker:
    build: .
    command: celery -A app.tasks worker --loglevel=info --concurrency=4
    depends_on:
      - redis
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '2'
          memory: 2G
    
  celery_beat:
    build: .
    command: celery -A app.tasks beat --loglevel=info
    depends_on:
      - redis
    
  flower:
    build: .
    command: celery -A app.tasks flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis
    
  app:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    depends_on:
      - redis
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/neo_alexandria
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
```

## Monitoring

- **Flower Dashboard**: http://localhost:5555 - Celery task monitoring
- **Health Check**: http://localhost:8000/monitoring/health
- **Metrics**: http://localhost:8000/monitoring/metrics
- **Cache Stats**: http://localhost:8000/monitoring/cache

---

# Appendix: Key Design Patterns

## Domain-Driven Design (DDD)
- **Value Objects**: ClassificationPrediction, QualityScore, RecommendationScore, SearchQuery
- **Entities**: Resource, TaxonomyNode, User
- **Domain Services**: Classification, Quality, Recommendation, Search domains

## Strategy Pattern
- **Context**: RecommendationService
- **Strategies**: CollaborativeFilteringStrategy, ContentBasedStrategy, GraphBasedStrategy, HybridStrategy

## Factory Pattern
- **RecommendationStrategyFactory**: Creates strategy instances based on type
- **SessionLocal**: Creates database session instances

## Repository Pattern
- **Database Models**: Act as repositories for domain entities
- **Service Layer**: Abstracts database operations from business logic

## Observer Pattern
- **Event Bus**: Pub/sub for inter-module communication
- **Event Handlers**: React to system events

## Command Query Separation (CQS)
- **Query Methods**: get_*, compute_*, analyze_* (no side effects)
- **Command Methods**: create_*, update_*, delete_* (modify state)

---

# Conclusion

Neo Alexandria 2.0 is a production-ready, modular knowledge management system built with modern architectural patterns. The vertical slice architecture with event-driven communication provides excellent scalability, maintainability, and testability.

Key achievements:
- ✅ 13 self-contained modules with zero circular dependencies
- ✅ Event-driven communication with <1ms latency
- ✅ Comprehensive test suite with Golden Data pattern
- ✅ Production-ready PostgreSQL support
- ✅ 97 API routes across all modules
- ✅ Complete documentation and developer guides

The system is ready for production deployment and can scale horizontally by adding more Celery workers or extracting modules into microservices as needed.

---

**For more information, see:**
- Repository: `backend/` directory
- Documentation: `backend/docs/` directory
- Steering Docs: `.kiro/steering/` directory
- API Docs: http://127.0.0.1:8000/docs (when running)
