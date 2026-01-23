# Architecture Overview

High-level system architecture for Neo Alexandria 2.0.

> **Last Updated**: Phase 14 - Complete Vertical Slice Refactor

## Table of Contents

1. [Modular Architecture Overview](#modular-architecture-overview)
2. [Core Components](#core-components)
3. [Technology Stack](#technology-stack)
4. [Vertical Slice Module Pattern](#vertical-slice-module-pattern)
5. [Complete System Architecture](#complete-system-architecture)
6. [Data Flow](#data-flow)
7. [Design Patterns](#design-patterns)
8. [Key Architectural Principles](#key-architectural-principles)

---

## Modular Architecture Overview

### High-Level Modular Structure (Phase 17 - Complete)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    NEO ALEXANDRIA 2.0 - COMPLETE MODULAR ARCHITECTURE                   │
│                              (14 Vertical Slice Modules)                                │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │                         FastAPI Application (main.py)                            │   │
│  │                    Registers all module routers & event handlers                 │   │
│  │                    Global Authentication & Rate Limiting Middleware              │   │
│  └────────────────────────────────────┬─────────────────────────────────────────────┘   │
│                                       │                                                 │
│                                       │ Module Registration                             │
│                                       │                                                 │
│       ┌───────────────────────────────┼───────────────────────────────────┐             │
│       │                               │                                   │             │
│       ▼                               ▼                                   ▼             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   Auth   │  │Resources │  │Collections│ │  Search  │  │Annotations│ │ Scholarly│     │
│  │  Module  │  │  Module  │  │  Module  │  │  Module  │  │  Module  │  │  Module  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │             │             │             │             │           │
│       │             │             │             │             │             │           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Authority│  │ Curation │  │  Quality │  │ Taxonomy │  │  Graph   │  │Recommend-│     │
│  │  Module  │  │  Module  │  │  Module  │  │  Module  │  │  Module  │  │ ations   │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │             │             │             │             │           │
│       │             │             │             │             │             │           │
│       │    ┌────────┴─────────────┴─────────────┴─────────────┴─────────────┘           │
│       │    │                                                                            │
│       │    ▼                                                                            │
│       │  ┌─────────────────────────────────────────────────────────────────┐            │
│       │  │                      Shared Kernel                              │            │
│       │  │  ┌──────────┐  ┌──────────────┐  ┌──────────────┐               │            │
│       └─►│  │ Database │  │  Event Bus   │  │  Base Model  │               │◄──────────┘|
│          │  │ (Session)│  │  (Pub/Sub)   │  │   (GUID)     │               │            │
│          │  └──────────┘  └──────────────┘  └──────────────┘               │            │
│          │  ┌──────────────────────────────────────────────────────────┐   │            │
│          │  │  Cross-Cutting Services:                                 │   │            │
│          │  │  • EmbeddingService (dense & sparse embeddings)          │   │            │
│          │  │  • AICore (summarization, entity extraction)             │   │            │
│          │  │  • CacheService (Redis caching with TTL)                 │   │            │
│          │  │  • Security (JWT, password hashing, OAuth2)              │   │            │
│          │  │  • RateLimiter (tiered rate limiting with Redis)         │   │            │
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

### Module Summary (13 Modules: 11 Base + 2 Conditional)

**Base Modules (Always Loaded)**:

| Module | Purpose | Key Events Emitted | Key Events Consumed |
|--------|---------|-------------------|---------------------|
| **Auth** | JWT authentication and OAuth2 | - | - |
| **Resources** | Resource CRUD operations | resource.created, resource.updated, resource.deleted, resource.chunked, resource.chunking_failed | - |
| **Collections** | Collection management | collection.created, collection.updated, collection.resource_added | resource.created, resource.updated, resource.deleted |
| **Search** | Hybrid search (keyword + semantic + sparse) | search.executed | resource.created, resource.updated |
| **Annotations** | Text highlights and notes | annotation.created, annotation.updated, annotation.deleted | resource.deleted |
| **Scholarly** | Academic metadata extraction | metadata.extracted, equations.parsed, tables.extracted | resource.created |
| **Authority** | Subject authority and classification trees | - | - |
| **Curation** | Content review and batch operations | curation.reviewed, curation.approved, curation.rejected | quality.outlier_detected |
| **Quality** | Multi-dimensional quality assessment | quality.computed, quality.outlier_detected, quality.degradation_detected | resource.created, resource.updated |
| **Taxonomy** | ML-based classification | resource.classified, taxonomy.model_trained | resource.created |
| **Graph** | Knowledge graph and citations | citation.extracted, graph.updated, hypothesis.discovered, graph.entity_extracted, graph.relationship_extracted | resource.created |

**Conditional Modules (Deployment-Specific)**:

| Module | Purpose | Load Condition | Key Events |
|--------|---------|----------------|------------|
| **Recommendations** | Hybrid recommendation engine (NCF, content, graph) | EDGE mode only (requires PyTorch) | recommendation.generated, user.profile_updated |
| **Monitoring** | System health and metrics | Redis available | - |
| **Taxonomy** | ML classification and taxonomy management | resource.classified, taxonomy.node_created, taxonomy.model_trained | resource.created |
| **Graph** | Knowledge graph, citations, discovery | citation.extracted, graph.updated, hypothesis.discovered | resource.created, resource.deleted |
| **Recommendations** | Hybrid recommendation engine | recommendation.generated, user.profile_updated, interaction.recorded | annotation.created, collection.resource_added |
| **Monitoring** | System health and metrics aggregation | - | All events (for metrics) |

### Phase 17: Production Hardening

Phase 17 adds production-ready authentication, rate limiting, and infrastructure improvements.

**New Features:**

1. **Auth Module** - JWT authentication with OAuth2 support
   - JWT access and refresh tokens
   - OAuth2 integration (Google, GitHub)
   - Token revocation with Redis
   - User management and authentication service
   - Public endpoints: `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/google`, `/auth/github`

2. **Global Authentication Middleware** - Protect all endpoints
   - JWT Bearer token validation
   - Automatic token extraction from Authorization header
   - Excluded endpoints: `/auth/*`, `/docs`, `/openapi.json`, `/monitoring/health`
   - TEST_MODE for development bypass

3. **Rate Limiting** - Tiered rate limiting with Redis
   - Free tier: 100 requests/hour
   - Premium tier: 1,000 requests/hour
   - Admin tier: 10,000 requests/hour
   - Sliding window algorithm
   - Rate limit headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
   - Graceful degradation when Redis unavailable

4. **Shared Kernel Enhancements** - Security and rate limiting services
   - `Security` - Password hashing, JWT creation/validation, token revocation
   - `RateLimiter` - Tiered rate limiting with sliding window
   - `OAuth2` - OAuth2 provider integration (Google, GitHub)

**Architecture Benefits:**

- **Production Ready**: JWT authentication and rate limiting for production deployments
- **Secure**: Password hashing with bcrypt, JWT token signing, OAuth2 integration
- **Scalable**: Redis-backed rate limiting and token revocation
- **Flexible**: Tiered rate limits, OAuth2 providers, TEST_MODE for development
- **Resilient**: Graceful degradation when Redis unavailable

### Phase 19: Hybrid Edge-Cloud Orchestration

Phase 19 introduces a hybrid architecture that splits the backend into Cloud API (Render) and Edge Worker (local GPU) for cost-optimized ML processing.

**New Components:**

1. **Cloud API (Control Plane)** - Lightweight FastAPI service on Render Free Tier
   - POST `/api/v1/ingestion/ingest/{repo_url}` - Queue repository for processing
   - GET `/api/v1/ingestion/worker/status` - Real-time worker status
   - GET `/api/v1/ingestion/jobs/history` - Job history and metrics
   - Bearer token authentication (PHAROS_ADMIN_TOKEN)
   - Queue cap (10 pending tasks) and TTL (24 hours)
   - Memory: <512MB (no ML libraries loaded)

2. **Edge Worker (Compute Plane)** - GPU-accelerated Python worker on local hardware
   - Repository cloning and parsing (GitPython, Tree-sitter)
   - Dependency graph construction (PyTorch tensors)
   - Graph neural network training (PyTorch Geometric Node2Vec)
   - Structural embedding generation (64 dimensions)
   - Batch upload to Qdrant Cloud
   - GPU utilization: 70-90% during training

3. **Serverless Infrastructure** - $0/month cloud costs
   - Upstash Redis - Task queue, worker status, job history
   - Neon PostgreSQL - Metadata storage (3GB free tier)
   - Qdrant Cloud - Vector embeddings (1GB free tier)

4. **Configuration Management** - Base + extension strategy
   - `requirements-base.txt` - Shared dependencies
   - `requirements-cloud.txt` - Extends base with cloud-specific deps
   - `requirements-edge.txt` - Extends base with ML dependencies
   - MODE-aware configuration (CLOUD vs EDGE)

**Architecture Benefits:**

- **Cost Optimized**: $0/month cloud costs, ~$10-20/month edge costs (electricity)
- **Performance**: Local GPU for 10x faster ML training
- **Scalable**: Multiple edge workers can share the same queue
- **Secure**: Bearer token authentication, queue caps, task TTL
- **Resilient**: Retry logic, graceful degradation, error recovery
- **Transparent**: Real-time status updates for UI integration

**See Also**: [Phase 19 Hybrid Architecture](phase19-hybrid.md)

### Phase 14: Complete Vertical Slice Refactor

Phase 14 completes the modular architecture transformation by migrating all remaining domains from the traditional layered structure to self-contained vertical slice modules.

**Migration Summary:**
- **Phase 13.5**: Extracted 3 modules (Resources, Collections, Search) - 20% of codebase
- **Phase 14**: Extracted 10 additional modules - 80% of codebase
- **Result**: 13 total modules with complete event-driven communication

**New Modules Added in Phase 14:**

1. **Annotations Module** - Text highlights and notes with semantic search
   - Migrated from: `routers/annotations.py`, `services/annotation_service.py`
   - Event handlers: Cascade delete on `resource.deleted`
   - Public interface: `AnnotationService`, annotation schemas

2. **Scholarly Module** - Academic metadata extraction (equations, tables, citations)
   - Migrated from: `routers/scholarly.py`, `services/metadata_extractor.py`
   - Event handlers: Extract metadata on `resource.created`
   - Public interface: `MetadataExtractor`, scholarly schemas

3. **Authority Module** - Subject authority and classification trees
   - Migrated from: `routers/authority.py`, `services/authority_service.py`
   - No event handlers (read-only service)
   - Public interface: `AuthorityService`, authority schemas

4. **Curation Module** - Content review and batch operations
   - Migrated from: `routers/curation.py`, `services/curation_service.py`
   - Event handlers: Add to review queue on `quality.outlier_detected`
   - Public interface: `CurationService`, curation schemas

5. **Quality Module** - Multi-dimensional quality assessment
   - Migrated from: `routers/quality.py`, `services/quality_service.py`, `services/summarization_evaluator.py`
   - Event handlers: Compute quality on `resource.created` and `resource.updated`
   - Public interface: `QualityService`, `SummarizationEvaluator`, quality schemas

6. **Taxonomy Module** - ML classification and taxonomy management
   - Migrated from: `routers/taxonomy.py`, `routers/classification.py`, `services/taxonomy_service.py`, `services/ml_classification_service.py`, `services/classification_service.py`
   - Event handlers: Auto-classify on `resource.created`
   - Public interface: `TaxonomyService`, `MLClassificationService`, taxonomy schemas

7. **Graph Module** - Knowledge graph, citations, and discovery
   - Migrated from: `routers/graph.py`, `routers/citations.py`, `routers/discovery.py`, 5 graph services
   - Event handlers: Extract citations on `resource.created`, remove from graph on `resource.deleted`
   - Public interface: `GraphService`, `CitationService`, `LBDService`, graph schemas

8. **Recommendations Module** - Hybrid recommendation engine (collaborative + content-based + graph-based)
   - Migrated from: `routers/recommendation.py`, `routers/recommendations.py`, 6 recommendation services
   - Event handlers: Update user profile on `annotation.created` and `collection.resource_added`
   - Public interface: `RecommendationService`, strategy classes, `UserProfileService`, recommendation schemas

9. **Monitoring Module** - System health and metrics aggregation
   - Migrated from: `routers/monitoring.py`, monitoring services
   - Event handlers: Aggregate metrics from all event types
   - Public interface: `MonitoringService`, monitoring schemas

10. **Shared Kernel Enhancements** - Cross-cutting services moved to shared kernel
    - `EmbeddingService` - Dense and sparse embedding generation
    - `AICore` - Summarization, entity extraction, classification
    - `CacheService` - Redis caching with TTL and pattern-based invalidation

**Architecture Benefits:**

- **High Cohesion**: Related code stays together within each module
- **Low Coupling**: Modules communicate only via events, no direct imports
- **Independent Testing**: Each module can be tested in isolation
- **Clear Boundaries**: Explicit public interfaces via `__init__.py`
- **Event-Driven**: Asynchronous, decoupled communication
- **Scalability**: Modules can be extracted to microservices if needed
- **Maintainability**: Changes to one module don't affect others

**Legacy Cleanup:**

Phase 14 also removed all legacy layered structure directories:
- ❌ Deleted `app/routers/` (all routers moved to modules)
- ❌ Deleted `app/services/` (all services moved to modules or shared kernel)
- ❌ Deleted `app/schemas/` (all schemas moved to modules)
- ✅ Cleaned `app/database/models.py` (only shared models remain: Resource, User, ResourceStatus)

---

## Core Components

1. **API Layer** - FastAPI-based RESTful API with automatic OpenAPI documentation
2. **Module Layer** - Vertical slice modules (Resources, Collections, Search)
3. **Service Layer** - Business logic and processing services
4. **Domain Layer** - Rich domain objects with business rules (Phase 11 DDD)
5. **Data Layer** - SQLAlchemy ORM with database abstraction
6. **Event Layer** - Event-driven communication between modules
7. **Task Layer** - Celery distributed task queue
8. **Cache Layer** - Redis multi-layer caching
9. **AI Processing** - Asynchronous AI-powered content analysis
10. **Search Engine** - Three-way hybrid search with RRF fusion
11. **Knowledge Graph** - Relationship detection and graph-based exploration
12. **Recommendation Engine** - Strategy-based personalized recommendations

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Web Framework | FastAPI 0.104.1 |
| ORM | SQLAlchemy 2.0.23 |
| Validation | Pydantic 2.5.2 |
| AI/ML | Hugging Face Transformers, PyTorch |
| Embeddings | sentence-transformers |
| Database | SQLite (dev), PostgreSQL (prod) |
| Search | FTS5, Vector Similarity, SPLADE |
| Task Queue | Celery + Redis |
| Caching | Redis |
| Migrations | Alembic 1.13.1 |

---

## Vertical Slice Module Pattern

Each module follows a consistent structure:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    VERTICAL SLICE MODULE PATTERN                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Each module (Resources, Collections, Search) follows this structure:   │
│                                                                         │
│  app/modules/{module_name}/                                             │
│  │                                                                      │
│  ├── __init__.py          # Public interface & exports                  │
│  │   • router                                                           │
│  │   • service functions                                                │
│  │   • schemas                                                          │
│  │   • models                                                           │
│  │   • module metadata (__version__, __domain__)                        │
│  │                                                                      │
│  ├── router.py            # FastAPI endpoints                           │
│  │   • HTTP request/response handling                                   │
│  │   • Input validation                                                 │
│  │   • Calls service layer                                              │
│  │                                                                      │
│  ├── service.py           # Business logic                              │
│  │   • Core domain operations                                           │
│  │   • Orchestration                                                    │
│  │   • Event emission                                                   │
│  │                                                                      │
│  ├── schema.py            # Pydantic models                             │
│  │   • Request/response validation                                      │
│  │   • Data serialization                                               │
│  │                                                                      │
│  ├── model.py             # SQLAlchemy models                           │
│  │   • Database entities                                                │
│  │   • String-based relationships (avoid circular imports)              │
│  │                                                                      │
│  ├── handlers.py          # Event handlers                              │
│  │   • Subscribe to events from other modules                           │
│  │   • React to system events                                           │
│  │                                                                      │
│  ├── README.md            # Module documentation                        │
│  │                                                                      │
│  └── tests/               # Module-specific tests                       │
│      └── __init__.py                                                    │
│                                                                         │
│  Benefits:                                                              │
│  • High cohesion - related code stays together                          │
│  • Low coupling - modules communicate via events                        │
│  • Independent deployment - modules can be extracted to microservices   │
│  • Clear boundaries - explicit public interfaces                        │
│  • Easy testing - isolated module tests                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Complete System Architecture - Layered View

```
╔═════════════════════════════════════════════════════════════════════════════╗
║                          LAYER 1: PRESENTATION                              ║
║                  (FastAPI Routers)                                          ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  /api/resources      /api/search         /api/collections                   ║
║  /api/taxonomy       /api/annotations    /api/recommendations               ║
║  /api/quality        /api/classification /api/monitoring                    ║
║  /api/scholarly      /api/graph          /api/citations                     ║
║                                                                             ║
║  • Request validation (Pydantic)                                            ║
║  • Authentication & authorization                                           ║
║  • Response serialization                                                   ║
║  • OpenAPI documentation                                                    ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ HTTP Requests
                                    ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                          LAYER 2: DOMAIN LAYER                              ║
║                      (Phase 11: Domain-Driven Design)                       ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Rich Domain Objects with Business Logic:                                   ║
║                                                                             ║
║  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              ║
║  │ClassificationRe-│  │  SearchQuery    │  │  QualityScore   │              ║
║  │sult (ValueObj)  │  │  (ValueObject)  │  │  (ValueObject)  │              ║
║  │ • validate()    │  │  • execute()    │  │  • compute()    │              ║
║  │ • to_dict()     │  │  • to_dict()    │  │  • to_dict()    │              ║
║  └─────────────────┘  └─────────────────┘  └─────────────────┘              ║
║                                                                             ║
║  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              ║
║  │ Recommendation  │  │Classification   │  │  SearchResult   │              ║
║  │ (ValueObject)   │  │Prediction       │  │  (ValueObject)  │              ║
║  │ • get_score()   │  │  • validate()   │  │  • to_dict()    │              ║
║  │ • to_dict()     │  │  • to_dict()    │  │                 │              ║
║  └─────────────────┘  └─────────────────┘  └─────────────────┘              ║
║                                                                             ║
║  • Encapsulates business rules                                              ║
║  • Independent of persistence                                               ║
║  • Ubiquitous language                                                      ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ Business Logic
                                    ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                          LAYER 3: SERVICE LAYER                             ║
║                         (Core Business Services)                            ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Core Services:                                                             ║
║  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐           ║
║  │ ResourceService  │  │  SearchService   │  │ QualityService   │           ║
║  │ • create()       │  │  • hybrid()      │  │  • compute()     │           ║
║  │ • update()       │  │  • three_way()   │  │  • dimensions()  │           ║
║  │ • delete()       │  │  • rerank()      │  │  • outliers()    │           ║
║  └──────────────────┘  └──────────────────┘  └──────────────────┘           ║
║                                                                             ║
║  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐           ║
║  │RecommendService  │  │MLClassifyService │  │ EmbeddingService │           ║
║  │ • get_similar()  │  │  • predict()     │  │  • generate()    │           ║
║  │ • graph_based()  │  │  • fine_tune()   │  │  • batch()       │           ║
║  │ • collaborative()│  │  • active_learn()│  │  • similarity()  │           ║
║  └──────────────────┘  └──────────────────┘  └──────────────────┘           ║
║                                                                             ║
║  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐           ║
║  │ CitationService  │  │ TaxonomyService  │  │AnnotationService │           ║
║  │ • extract()      │  │  • classify()    │  │  • create()      │           ║
║  │ • parse()        │  │  • get_tree()    │  │  • update()      │           ║
║  │ • graph_update() │  │  • suggest()     │  │  • by_resource() │           ║
║  └──────────────────┘  └──────────────────┘  └──────────────────┘           ║
║                                                                             ║
║  • Orchestrates business operations                                         ║
║  • Emits domain events                                                      ║
║  • Transaction management                                                   ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ Event Emission
                                    ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                       LAYER 4: EVENT-DRIVEN LAYER                           ║
║                      (Phase 12.5: Event System)                             ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  See: [Event System Architecture](event-system.md)                          ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ Task Queue
                                    ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                      LAYER 5: TASK PROCESSING LAYER                         ║
║                          (Celery + Redis)                                   ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  See: [Event System Architecture](event-system.md)                          ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ Cache Access
                                    ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                         LAYER 6: CACHING LAYER                              ║
║                            (Redis Cache)                                    ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  See: [Event System Architecture](event-system.md)                          ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ Data Access
                                    ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                       LAYER 7: DATA ACCESS LAYER                            ║
║                         (SQLAlchemy ORM)                                    ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  See: [Database Architecture](database.md)                                  ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
```

---

## Data Flow

### URL Ingestion Pipeline

```
URL Input → API Validation → Asynchronous Processing Pipeline
    ↓
Content Fetching → Multi-Format Extraction → AI Analysis
    ↓
Vector Embedding → Authority Control → Classification
    ↓
Quality Scoring → Archiving → Database Persistence
    ↓
Search Indexing → Graph Relationship Detection → Recommendation Learning
```

### Resource Update Event Cascade

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              RESOURCE UPDATE EVENT CASCADE (Phase 12.5)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. API Request: PUT /resources/{id}                                        │
│     │                                                                       │
│     ▼                                                                       │
│  2. ResourceService.update(id, data)                                        │
│     │                                                                       │
│     ├─► Update database                                                     │
│     │                                                                       │
│     ├─► Detect changes: content_changed = True, metadata_changed = False    │
│     │                                                                       │
│     ├─► Emit: resource.updated                                              │
│     │   └─► Hook: on_resource_updated_sync_search_index                     │
│     │       └─► Queue: update_search_index_task (priority=9, countdown=1s)  │
│     │                                                                       │
│     ├─► Emit: resource.updated                                              │
│     │   └─► Hook: on_resource_updated_invalidate_caches                     │
│     │       └─► Queue: invalidate_cache_task (priority=9, countdown=0s)     │
│     │           └─► Invalidate: resource:{id}:*, search_query:*             │
│     │                                                                       │
│     └─► Emit: resource.content_changed                                      │
│         └─► Hook: on_content_changed_regenerate_embedding                   │
│             └─► Queue: regenerate_embedding_task (priority=7, countdown=5s) │
│                 └─► Generate embedding → Store in cache                     │
│                                                                             │
│  3. Celery Workers Process Tasks (in parallel)                              │
│     │                                                                       │
│     ├─► Worker 1: update_search_index_task (1s delay)                       │
│     │   └─► Update FTS5 index → Resource searchable                         │
│     │                                                                       │
│     ├─► Worker 2: invalidate_cache_task (immediate)                         │
│     │   └─► Delete cache keys → Fresh data on next request                  │
│     │                                                                       │
│     └─► Worker 3: regenerate_embedding_task (5s delay)                      │
│         └─► Generate embedding → Cache → Enable semantic search             │
│                                                                             │
│  4. All tasks complete within 10 seconds                                    │
│     └─► Resource fully updated and consistent across all systems            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Design Patterns Used

### Domain-Driven Design (DDD)
- **Value Objects**: ClassificationPrediction, QualityScore, RecommendationScore, SearchQuery
- **Entities**: Resource, TaxonomyNode, User (via entity_id)
- **Domain Services**: Classification, Quality, Recommendation, Search domains
- **Validation**: Encapsulated in domain objects with validate() methods

### Strategy Pattern
- **Context**: RecommendationService
- **Strategy Interface**: RecommendationStrategy (ABC)
- **Concrete Strategies**: CollaborativeFilteringStrategy, ContentBasedStrategy, GraphBasedStrategy, HybridStrategy
- **Factory**: RecommendationStrategyFactory

### Factory Pattern
- **RecommendationStrategyFactory**: Creates strategy instances based on type
- **SessionLocal**: Creates database session instances

### Repository Pattern
- **Database Models**: Act as repositories for domain entities
- **Service Layer**: Abstracts database operations from business logic

### Dependency Injection
- **FastAPI Dependencies**: get_db() provides database sessions
- **Service Constructors**: Accept db: Session parameter

### Observer Pattern
- **PredictionMonitor**: Observes and logs ML predictions
- **AlertManager**: Observes metrics and triggers alerts
- **Event Bus**: Pub/sub for inter-module communication

### Command Query Separation (CQS)
- **Query Methods**: get_*, compute_*, analyze_* (no side effects)
- **Command Methods**: create_*, update_*, delete_* (modify state)

### Builder Pattern
- **SearchQuery**: Builds complex search queries with optional parameters
- **ClassificationResult**: Builds results with predictions and metadata

---

## Key Architectural Principles

### 1. Separation of Concerns
- **Domain Layer**: Pure business logic, no infrastructure dependencies
- **Service Layer**: Orchestrates domain objects and infrastructure
- **Router Layer**: HTTP concerns only, delegates to services
- **Database Layer**: Data persistence only

### 2. Dependency Inversion
- High-level modules (services) don't depend on low-level modules (database)
- Both depend on abstractions (domain objects, interfaces)
- Database sessions injected via dependency injection

### 3. Single Responsibility
- Each class has one reason to change
- Domain objects: Represent business concepts
- Services: Implement business operations
- Validators: Check specific code quality aspects
- Routers: Handle HTTP requests/responses

### 4. Open/Closed Principle
- Open for extension: New strategies can be added without modifying existing code
- Closed for modification: Core abstractions remain stable
- Example: Adding new RecommendationStrategy doesn't change RecommendationService

### 5. Liskov Substitution
- All RecommendationStrategy implementations are interchangeable
- All ValueObject subclasses can be used polymorphically
- Domain objects can be substituted without breaking contracts

### 6. Interface Segregation
- Small, focused interfaces (RecommendationStrategy has one method)
- Clients depend only on methods they use
- No fat interfaces with unused methods

### 7. Don't Repeat Yourself (DRY)
- Common validation logic in base classes (BaseDomainObject)
- Shared utilities in utility layer
- Reusable validators in refactoring framework

### 8. Composition Over Inheritance
- HybridStrategy composes multiple strategies
- Services compose domain objects
- Minimal inheritance hierarchies

---

## Complete 9-Layer System Architecture

```
╔═════════════════════════════════════════════════════════════════════════════╗
║                          LAYER 1: PRESENTATION                              ║
║                  (FastAPI Routers + Middleware)                             ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Authentication Middleware (Phase 17):                                      ║
║  ┌─────────────────────────────────────────────────────────────────┐        ║
║  │ • JWT Bearer token validation                                   │        ║
║  │ • Token extraction from Authorization header                    │        ║
║  │ • Token revocation check (Redis)                                │        ║
║  │ • User context injection                                        │        ║
║  │ • Excluded: /auth/*, /docs, /openapi.json, /monitoring/health   │        ║
║  └─────────────────────────────────────────────────────────────────┘        ║
║                                                                             ║
║  Rate Limiting Middleware (Phase 17):                                       ║
║  ┌─────────────────────────────────────────────────────────────────┐        ║
║  │ • Tiered rate limiting (free, premium, admin)                   │        ║
║  │ • Sliding window algorithm with Redis                           │        ║
║  │ • Rate limit headers: X-RateLimit-*                             │        ║
║  │ • HTTP 429 when limit exceeded                                  │        ║
║  │ • Excluded: /monitoring/health                                  │        ║
║  └─────────────────────────────────────────────────────────────────┘        ║
║                                                                             ║
║  API Endpoints:                                                             ║
║  /api/auth           /api/resources      /api/search                        ║
║  /api/collections    /api/taxonomy       /api/annotations                   ║
║  /api/recommendations /api/quality       /api/classification                ║
║  /api/monitoring     /api/scholarly      /api/graph                         ║
║  /api/citations                                                             ║
║                                                                             ║
║  • Request validation (Pydantic)                                            ║
║  • Authentication & authorization                                           ║
║  • Response serialization                                                   ║
║  • OpenAPI documentation                                                    ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ HTTP Requests
                                    ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                          LAYER 2: DOMAIN LAYER                              ║
║                      (Phase 11: Domain-Driven Design)                       ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Rich Domain Objects with Business Logic:                                   ║
║                                                                             ║
║  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              ║
║  │ClassificationRe-│  │  SearchQuery    │  │  QualityScore   │              ║
║  │sult (ValueObj)  │  │  (ValueObject)  │  │  (ValueObject)  │              ║
║  │ • validate()    │  │  • execute()    │  │  • compute()    │              ║
║  │ • to_dict()     │  │  • to_dict()    │  │  • to_dict()    │              ║
║  └─────────────────┘  └─────────────────┘  └─────────────────┘              ║
║                                                                             ║
║  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              ║
║  │ Recommendation  │  │Classification   │  │  SearchResult   │              ║
║  │ (ValueObject)   │  │Prediction       │  │  (ValueObject)  │              ║
║  │ • get_score()   │  │  • validate()   │  │  • to_dict()    │              ║
║  │ • to_dict()     │  │  • to_dict()    │  │                 │              ║
║  └─────────────────┘  └─────────────────┘  └─────────────────┘              ║
║                                                                             ║
║  • Encapsulates business rules                                              ║
║  • Independent of persistence                                               ║
║  • Ubiquitous language                                                      ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ Business Logic
                                    ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                          LAYER 3: SERVICE LAYER                             ║
║                         (Core Business Services)                            ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  See: [Modules Architecture](modules.md)                                    ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ Event Emission
                                    ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                       LAYER 4: EVENT-DRIVEN LAYER                           ║
║                      (Phase 12.5: Event System)                             ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  See: [Event System Architecture](event-system.md)                          ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ Task Queue
                                    ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                      LAYER 5: TASK PROCESSING LAYER                         ║
║                          (Celery + Redis)                                   ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  See: [Event System Architecture](event-system.md)                          ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ Cache Access
                                    ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                         LAYER 6: CACHING LAYER                              ║
║                            (Redis Cache)                                    ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  See: [Event System Architecture](event-system.md)                          ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ Data Access
                                    ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                       LAYER 7: DATA ACCESS LAYER                            ║
║                         (SQLAlchemy ORM)                                    ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  See: [Database Architecture](database.md)                                  ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ SQL Queries
                                    ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                         LAYER 8: DATABASE LAYER                             ║
║                       (SQLite / PostgreSQL)                                 ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  See: [Database Architecture](database.md)                                  ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ ML Processing
                                    ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                      LAYER 9: MACHINE LEARNING LAYER                        ║
║                    (PyTorch + Transformers)                                 ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Classification Models (Phase 5-7):                                         ║
║  • DistilBERT / BERT Transformer                                            ║
║  • Multi-label classification                                               ║
║  • Fine-tuned on academic taxonomy                                          ║
║  • Active learning with uncertainty sampling                                ║
║                                                                             ║
║  Embedding Models (Phase 4, 8):                                             ║
║  • Dense Embeddings (BERT/Sentence-BERT) - 768-dimensional vectors          ║
║  • Sparse Embeddings (SPLADE/TF-IDF) - Term importance weighting            ║
║                                                                             ║
║  Reranking Models (Phase 8):                                                ║
║  • ColBERT Cross-Encoder                                                    ║
║  • Query-document interaction modeling                                      ║
║                                                                             ║
║  Quality Assessment Models (Phase 9):                                       ║
║  • Isolation Forest (Outlier Detection)                                     ║
║  • 9-dimensional feature space                                              ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
```

---

## Cross-Cutting Concerns

```
╔═════════════════════════════════════════════════════════════════════════════╗
║                         CROSS-CUTTING CONCERNS                              ║
║                    (Applied Across All Layers)                              ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  Monitoring & Observability:                                                ║
║  ┌─────────────────────────────────────────────────────────────────┐        ║
║  │ • PredictionMonitor - ML model performance tracking             │        ║
║  │ • Flower Dashboard - Celery task monitoring                     │        ║
║  │ • Event history logging                                         │        ║
║  │ • Cache statistics tracking                                     │        ║
║  │ • API endpoints: /api/monitoring/health, /metrics, /cache-stats │        ║
║  └─────────────────────────────────────────────────────────────────┘        ║
║                                                                             ║
║  Error Handling & Resilience:                                               ║
║  ┌─────────────────────────────────────────────────────────────────┐        ║
║  │ • Automatic task retries with exponential backoff               │        ║
║  │ • Circuit breakers for external services                        │        ║
║  │ • Graceful degradation (fallback to cached data)                │        ║
║  │ • Dead letter queues for failed tasks                           │        ║
║  │ • Comprehensive error logging                                   │        ║
║  │ • Health checks for all services                                │        ║
║  └─────────────────────────────────────────────────────────────────┘        ║
║                                                                             ║
║  Security & Authentication:                                                 ║
║  ┌─────────────────────────────────────────────────────────────────┐        ║
║  │ • JWT authentication with OAuth2 (Phase 17)                     │        ║
║  │ • Password hashing with bcrypt                                  │        ║
║  │ • Token revocation with Redis                                   │        ║
║  │ • OAuth2 providers (Google, GitHub)                             │        ║
║  │ • Tiered rate limiting (free, premium, admin)                   │        ║
║  │ • Role-based access control (RBAC)                              │        ║
║  │ • Input validation and sanitization                             │        ║
║  │ • SQL injection prevention (ORM)                                │        ║
║  │ • CORS configuration                                            │        ║
║  └─────────────────────────────────────────────────────────────────┘        ║
║                                                                             ║
║  Configuration Management:                                                  ║
║  ┌─────────────────────────────────────────────────────────────────┐        ║
║  │ • Environment-based configuration (.env files)                  │        ║
║  │ • Centralized settings (settings.py)                            │        ║
║  │ • Feature flags                                                 │        ║
║  │ • Dynamic configuration updates                                 │        ║
║  │ • Secrets management                                            │        ║
║  └─────────────────────────────────────────────────────────────────┘        ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
```

---

## Testing Architecture

### Unit Tests
```
test_domain_*.py
├── Test domain object validation
├── Test domain object methods
├── Test value object immutability
└── No database or external dependencies

test_*_service.py
├── Test service methods with mocked database
├── Test business logic
├── Test error handling
└── Use pytest fixtures for setup

test_refactoring_*.py
├── Test code smell detection
├── Test validators
├── Test AST parsing
└── Use sample code files
```

### Integration Tests
```
test_*_integration.py
├── Test service + database interactions
├── Test API endpoints
├── Use test database
└── Test complete workflows
```

### Test Fixtures
```
conftest.py
├── @pytest.fixture: db_session
├── @pytest.fixture: test_client
├── @pytest.fixture: sample_resources
└── @pytest.fixture: mock_ml_model
```

---

## Performance Considerations

### Lazy Loading
- ML models loaded on first use (MLClassificationService._load_model)
- Reduces startup time and memory usage

### Caching
- Model checkpoints cached on disk
- Embeddings cached in database and Redis
- Query results cached with TTL

### Batch Processing
- predict_batch() for multiple classifications
- Batch quality outlier detection
- Vectorized operations in numpy

### Database Optimization
- Indexes on frequently queried fields (id, resource_id, user_id)
- JSON fields for flexible metadata
- Pagination for large result sets
- Connection pooling (20 base + 40 overflow)

### Async Operations
- FastAPI async endpoints
- Background tasks for long-running operations
- Celery for distributed task processing

---

## Security Considerations

### Input Validation
- Pydantic schemas validate all API inputs
- Domain objects validate business rules
- SQL injection prevented by SQLAlchemy ORM

### Authentication & Authorization
- JWT tokens for API authentication (planned)
- Role-based access control (planned)
- Resource ownership validation

### Data Privacy
- User data anonymization options
- GDPR compliance considerations
- Audit logging for sensitive operations

---

## Deployment Architecture

```
Production Environment
├── Load Balancer
│   └── Distributes traffic across instances
├── Application Servers (multiple instances)
│   ├── FastAPI application
│   ├── Gunicorn workers
│   └── ML models loaded in memory
├── Database Server
│   ├── PostgreSQL (production)
│   └── SQLite (development)
├── Cache Layer
│   └── Redis
├── Task Queue
│   ├── Celery Workers (4 replicas)
│   ├── Celery Beat (scheduler)
│   └── Flower (monitoring)
└── Monitoring
    ├── Prometheus metrics
    ├── Grafana dashboards
    └── Alert notifications
```

---

## Future Enhancements

### Planned Features
1. **Async Operations**: Convert services to async for better concurrency
2. **GraphQL API**: Alternative to REST for flexible queries
3. **Real-time Updates**: WebSocket support for live notifications
4. **Advanced ML**: Add more sophisticated models (BERT, GPT)
5. **Distributed Training**: Multi-GPU and distributed model training
6. **A/B Testing**: Framework for testing recommendation strategies
7. **Explainability**: Add SHAP/LIME for model interpretability

### Technical Debt
1. Complete async conversion of database operations
2. Add comprehensive API documentation (OpenAPI/Swagger)
3. Implement rate limiting and throttling
4. Add request/response compression
5. Implement circuit breakers for external services
6. Add distributed tracing (OpenTelemetry)

---

## Related Documentation

- [Database Architecture](database.md) - Schema, models, migrations
- [Event System](event-system.md) - Event-driven communication, Celery, Redis
- [Modules](modules.md) - Vertical slice details, service architecture
- [Design Decisions](decisions.md) - ADRs
