# Architecture Overview

High-level system architecture for Neo Alexandria 2.0.

> **Last Updated**: Phase 13.5 - Vertical Slice Refactoring

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

### High-Level Modular Structure (Phase 13.5)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    NEO ALEXANDRIA 2.0 - MODULAR ARCHITECTURE            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      FastAPI Application                         │   │
│  │                         (main.py)                                │   │
│  └────────────────────────────┬─────────────────────────────────────┘   │
│                               │                                         │
│                               │ registers routers & handlers            │
│                               │                                         │
│       ┌───────────────────────┼───────────────────────┐                 │
│       │                       │                       │                 │
│       ▼                       ▼                       ▼                 │
│  ┌──────────┐          ┌──────────┐          ┌──────────┐              │
│  │Resources │          │Collections│         │  Search  │              │
│  │  Module  │          │  Module  │          │  Module  │              │
│  └────┬─────┘          └────┬─────┘          └────┬─────┘              │
│       │                     │                     │                     │
│       │                     │                     │                     │
│       │    ┌────────────────┴────────────────┐    │                     │
│       │    │                                 │    │                     │
│       │    ▼                                 ▼    │                     │
│       │  ┌─────────────────────────────────────┐  │                     │
│       │  │       Shared Kernel                 │  │                     │
│       │  │  ┌──────────┐  ┌──────────────┐     │  │                     │
│       └─►│  │ Database │  │  Event Bus   │     │◄─┘                     │
│          │  │ (Base,   │  │ (Pub/Sub)    │     │                        │
│          │  │Session)  │  │              │     │                        │
│          │  └──────────┘  └──────────────┘     │                        │
│          │  ┌──────────────────────────────┐   │                        │
│          │  │      Base Model (GUID)       │   │                        │
│          │  └──────────────────────────────┘   │                        │
│          └─────────────────────────────────────┘                        │
│                                                                         │
│  Event-Driven Communication:                                            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Resources ──[resource.created]──► Collections                   │   │
│  │  Resources ──[resource.updated]──► Collections                   │   │
│  │  Resources ──[resource.deleted]──► Collections                   │   │
│  │  Collections ─[collection.updated]─► Resources (placeholder)     │   │
│  │  Search ──────[search.executed]────► Analytics (future)          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

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
│  │   • router                                                          │
│  │   • service functions                                               │
│  │   • schemas                                                         │
│  │   • models                                                          │
│  │   • module metadata (__version__, __domain__)                       │
│  │                                                                      │
│  ├── router.py            # FastAPI endpoints                          │
│  │   • HTTP request/response handling                                  │
│  │   • Input validation                                                │
│  │   • Calls service layer                                             │
│  │                                                                      │
│  ├── service.py           # Business logic                             │
│  │   • Core domain operations                                          │
│  │   • Orchestration                                                   │
│  │   • Event emission                                                  │
│  │                                                                      │
│  ├── schema.py            # Pydantic models                            │
│  │   • Request/response validation                                     │
│  │   • Data serialization                                              │
│  │                                                                      │
│  ├── model.py             # SQLAlchemy models                          │
│  │   • Database entities                                               │
│  │   • String-based relationships (avoid circular imports)             │
│  │                                                                      │
│  ├── handlers.py          # Event handlers                             │
│  │   • Subscribe to events from other modules                          │
│  │   • React to system events                                          │
│  │                                                                      │
│  ├── README.md            # Module documentation                       │
│  │                                                                      │
│  └── tests/               # Module-specific tests                      │
│      └── __init__.py                                                   │
│                                                                         │
│  Benefits:                                                              │
│  • High cohesion - related code stays together                         │
│  • Low coupling - modules communicate via events                       │
│  • Independent deployment - modules can be extracted to microservices  │
│  • Clear boundaries - explicit public interfaces                       │
│  • Easy testing - isolated module tests                                │
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
║  │ • API key authentication                                        │        ║
║  │ • Role-based access control (RBAC)                              │        ║
║  │ • Input validation and sanitization                             │        ║
║  │ • SQL injection prevention (ORM)                                │        ║
║  │ • Rate limiting                                                 │        ║
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
