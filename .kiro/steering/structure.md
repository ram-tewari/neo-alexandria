# Neo Alexandria 2.0 - Repository Structure

## Repository Map

```
neo-alexandria-2.0/
├── AGENTS.md                          # Agent routing and context rules
├── .kiro/                             # Kiro IDE configuration
│   ├── steering/                      # Project steering docs
│   │   ├── product.md                 # Product vision and goals
│   │   ├── tech.md                    # Tech stack and constraints
│   │   └── structure.md               # This file
│   └── specs/                         # Feature specifications
│       ├── backend/                   # Backend feature specs (21)
│       ├── frontend/                  # Frontend feature specs (6)
│       └── README.md                  # Spec organization guide
├── backend/                           # Python/FastAPI backend
│   ├── app/                           # Application code
│   │   ├── modules/                   # Vertical slice modules (13 total)
│   │   │   ├── annotations/           # Text highlights and notes
│   │   │   ├── authority/             # Subject authority trees
│   │   │   ├── collections/           # Collection management
│   │   │   ├── curation/              # Content review
│   │   │   ├── graph/                 # Knowledge graph and citations
│   │   │   ├── monitoring/            # System health and metrics
│   │   │   ├── quality/               # Quality assessment
│   │   │   ├── recommendations/       # Hybrid recommendations
│   │   │   ├── resources/             # Resource CRUD
│   │   │   ├── scholarly/             # Academic metadata
│   │   │   ├── search/                # Hybrid search
│   │   │   └── taxonomy/              # ML classification
│   │   ├── shared/                    # Shared kernel
│   │   │   ├── database.py            # Database sessions
│   │   │   ├── event_bus.py           # Event system
│   │   │   ├── base_model.py          # Base models
│   │   │   ├── embeddings.py          # Vector embeddings
│   │   │   ├── ai_core.py             # AI operations
│   │   │   └── cache.py               # Redis cache
│   │   ├── database/                  # Database models and config
│   │   ├── domain/                    # Domain objects
│   │   ├── events/                    # Event system
│   │   └── main.py                    # FastAPI app entry point
│   ├── tests/                         # Test suite
│   │   ├── unit/                      # Unit tests
│   │   ├── integration/               # Integration tests
│   │   ├── performance/               # Performance tests
│   │   └── conftest.py                # Pytest configuration
│   ├── docs/                          # Technical documentation
│   │   ├── index.md                   # Documentation hub
│   │   ├── api/                       # API reference (modular)
│   │   │   ├── overview.md            # Base URL, auth, errors
│   │   │   ├── resources.md           # Resource endpoints
│   │   │   ├── search.md              # Search endpoints
│   │   │   ├── collections.md         # Collection endpoints
│   │   │   ├── annotations.md         # Annotation endpoints
│   │   │   ├── taxonomy.md            # Taxonomy endpoints
│   │   │   ├── graph.md               # Graph/citation endpoints
│   │   │   ├── recommendations.md     # Recommendation endpoints
│   │   │   ├── quality.md             # Quality endpoints
│   │   │   └── monitoring.md          # Health/monitoring endpoints
│   │   ├── architecture/              # Architecture documentation
│   │   │   ├── overview.md            # System architecture
│   │   │   ├── database.md            # Schema and models
│   │   │   ├── event-system.md        # Event bus
│   │   │   ├── modules.md             # Vertical slices
│   │   │   └── decisions.md           # ADRs
│   │   ├── guides/                    # Developer guides
│   │   │   ├── setup.md               # Installation
│   │   │   ├── workflows.md           # Development tasks
│   │   │   ├── testing.md             # Testing strategies
│   │   │   ├── deployment.md          # Docker/production
│   │   │   └── troubleshooting.md     # FAQ and issues
│   │   ├── POSTGRESQL_MIGRATION_GUIDE.md
│   │   └── ...                        # Other technical docs
│   ├── scripts/                       # Utility scripts
│   │   ├── training/                  # ML training scripts
│   │   ├── evaluation/                # Evaluation scripts
│   │   └── deployment/                # Deployment scripts
│   ├── alembic/                       # Database migrations
│   ├── requirements.txt               # Python dependencies
│   └── README.md                      # Backend overview
├── frontend/                          # React/TypeScript frontend
│   ├── src/                           # Source code
│   │   ├── components/                # React components
│   │   │   ├── features/              # Feature components
│   │   │   ├── ui/                    # UI components
│   │   │   ├── layout/                # Layout components
│   │   │   └── common/                # Common components
│   │   ├── lib/                       # Utilities and helpers
│   │   │   ├── api/                   # API client
│   │   │   ├── hooks/                 # Custom React hooks
│   │   │   └── utils/                 # Utility functions
│   │   ├── styles/                    # Global styles
│   │   ├── types/                     # TypeScript types
│   │   └── App.tsx                    # App entry point
│   ├── package.json                   # Node dependencies
│   └── README.md                      # Frontend overview
└── docker/                            # Docker configuration
    ├── docker-compose.yml             # Multi-container setup
    └── Dockerfile                     # Container image
```

## Truth Sources

### Product & Vision
**Source**: `.kiro/steering/product.md`
- Product purpose and goals
- Target users
- Non-goals and boundaries
- Success metrics

### Technical Stack
**Source**: `.kiro/steering/tech.md`
- Technology choices
- Development tools
- Common commands
- Environment variables

### API Reference
**Source**: `backend/docs/api/` (modular structure)
- `overview.md` - Base URL, authentication, error handling
- `resources.md` - Resource CRUD endpoints
- `search.md` - Search and hybrid search endpoints
- `collections.md` - Collection management endpoints
- `annotations.md` - Annotation endpoints
- `taxonomy.md` - Taxonomy and classification endpoints
- `graph.md` - Knowledge graph and citation endpoints
- `recommendations.md` - Recommendation endpoints
- `quality.md` - Quality assessment endpoints
- `monitoring.md` - Health and monitoring endpoints

### Architecture
**Source**: `backend/docs/architecture/` (modular structure)
- `overview.md` - High-level system architecture
- `database.md` - Schema, models, migrations
- `event-system.md` - Event bus and handlers
- `modules.md` - Vertical slice module structure
- `decisions.md` - Architecture decision records

### Developer Guides
**Source**: `backend/docs/guides/` (modular structure)
- `setup.md` - Installation and environment setup
- `workflows.md` - Common development tasks
- `testing.md` - Testing strategies and patterns
- `deployment.md` - Docker and production deployment
- `troubleshooting.md` - Common issues and FAQ

### Database Schema
**Source**: `backend/alembic/versions/`
- Migration history
- Schema changes
- Current schema state

### Feature Specifications
**Source**: `.kiro/specs/[feature-name]/`
- Requirements (user stories, acceptance criteria)
- Design (technical architecture)
- Tasks (implementation checklist)

## Key Directories Explained

### Backend Modules (`backend/app/modules/`)

**Purpose**: Vertical slice architecture for feature isolation

Each module contains:
- `model.py` - Database models
- `schema.py` - Pydantic schemas
- `service.py` - Business logic
- `router.py` - API endpoints
- `handlers.py` - Event handlers
- `README.md` - Module documentation

**Complete Module List (13 modules)**:
- `annotations/` - Text highlights, notes, and tags on resources
- `authority/` - Subject authority and classification trees
- `collections/` - Collection management and resource organization
- `curation/` - Content review and batch operations
- `graph/` - Knowledge graph, citations, and discovery
- `monitoring/` - System health, metrics, and observability
- `quality/` - Multi-dimensional quality assessment
- `recommendations/` - Hybrid recommendation engine (NCF, content, graph)
- `resources/` - Resource CRUD operations and metadata
- `scholarly/` - Academic metadata extraction (equations, tables, citations)
- `search/` - Hybrid search (keyword, semantic, full-text)
- `taxonomy/` - ML-based classification and taxonomy management

**Module Communication**: All modules communicate via event bus (no direct imports)

### Backend Shared Kernel (`backend/app/shared/`)

**Purpose**: Cross-cutting concerns shared by all modules

**Key Components**:
- `database.py` - Database session management
- `event_bus.py` - Event-driven communication
- `base_model.py` - Base SQLAlchemy model
- `embeddings.py` - Vector embedding generation
- `ai_core.py` - AI operations (summarization, entity extraction)
- `cache.py` - Redis caching service

**Rules**: Shared kernel has no dependencies on domain modules

### Backend Domain (`backend/app/domain/`)

**Purpose**: Domain objects and business rules

**Key Files**:
- `base.py` - Base domain classes
- `search.py` - Search domain objects
- `classification.py` - Classification domain
- `quality.py` - Quality domain
- `recommendation.py` - Recommendation domain

### Backend Events (`backend/app/events/`)

**Purpose**: Event-driven architecture for module communication

**Key Files**:
- `event_system.py` - Event bus implementation (in-memory, async)
- `event_types.py` - Event type definitions and schemas
- `hooks.py` - Event hook registration

**Event Categories**:
- Resource events: `resource.created`, `resource.updated`, `resource.deleted`
- Collection events: `collection.created`, `collection.resource_added`
- Annotation events: `annotation.created`, `annotation.updated`, `annotation.deleted`
- Quality events: `quality.computed`, `quality.outlier_detected`
- Classification events: `resource.classified`, `taxonomy.model_trained`
- Graph events: `citation.extracted`, `graph.updated`, `hypothesis.discovered`
- Recommendation events: `recommendation.generated`, `user.profile_updated`
- Curation events: `curation.reviewed`, `curation.approved`
- Metadata events: `metadata.extracted`, `equations.parsed`, `tables.extracted`

**Performance**: Event emission + delivery < 1ms (p95)

### Frontend Components (`frontend/src/components/`)

**Purpose**: React component library

**Structure**:
- `features/` - Feature-specific components (library, upload, resource-detail)
- `ui/` - Reusable UI components (Button, Card, Input)
- `layout/` - Layout components (Navbar, Sidebar, MainLayout)
- `common/` - Common components (CommandPalette, ErrorBoundary)

### Frontend API Client (`frontend/src/lib/api/`)

**Purpose**: Backend API integration

**Key Files**:
- `resources.ts` - Resource API calls
- `search.ts` - Search API calls
- `collections.ts` - Collection API calls
- `graph.ts` - Graph API calls
- `types.ts` - TypeScript type definitions

## Documentation Hierarchy

### Level 1: Quick Reference
- `AGENTS.md` - Agent routing rules
- `.kiro/steering/product.md` - Product overview
- `.kiro/steering/tech.md` - Tech stack
- `.kiro/steering/structure.md` - This file

### Level 2: Feature Specs
- `.kiro/specs/[feature]/requirements.md` - What to build
- `.kiro/specs/[feature]/design.md` - How to build it
- `.kiro/specs/[feature]/tasks.md` - Implementation steps

### Level 3: Technical Details
- `backend/docs/index.md` - Documentation hub and navigation
- `backend/docs/api/*.md` - API reference (10 domain files)
- `backend/docs/architecture/*.md` - Architecture documentation (5 files)
- `backend/docs/guides/*.md` - Developer guides (5 files)
- `backend/docs/POSTGRESQL_MIGRATION_GUIDE.md` - Database migration
- `backend/docs/EVENT_DRIVEN_REFACTORING.md` - Event architecture

### Level 4: Implementation
- `backend/app/modules/[module]/README.md` - Module documentation
- `backend/app/services/[service].py` - Service implementation
- `frontend/src/components/features/[feature]/README.md` - Component docs

## Finding What You Need

### "Where is the API for X?"
1. Check `backend/docs/index.md` for navigation
2. Check `backend/docs/api/[domain].md` for specific endpoint docs
3. Find router in `backend/app/modules/[module]/router.py`
4. Find service in `backend/app/modules/[module]/service.py`

### "How does feature X work?"
1. Check `.kiro/specs/[feature]/design.md` for architecture
2. Check `backend/docs/architecture/overview.md` for system context
3. Check implementation in `backend/app/modules/[module]/`

### "What are the requirements for X?"
1. Check `.kiro/specs/[feature]/requirements.md` for user stories
2. Check `backend/docs/api/[domain].md` for API contracts

### "How do I implement X?"
1. Check `.kiro/specs/[feature]/tasks.md` for implementation steps
2. Check `backend/docs/guides/workflows.md` for development workflows
3. Check existing implementations in `backend/app/modules/` for patterns

### "What tests exist for X?"
1. Check `backend/tests/modules/` for module-specific tests
2. Check `backend/tests/integration/` for integration tests
3. Check `backend/tests/conftest.py` for test fixtures

### "How do modules communicate?"
1. Check `backend/docs/architecture/event-system.md` for event bus details
2. Check `backend/docs/architecture/events.md` for event catalog
3. Check `backend/app/modules/[module]/handlers.py` for event handlers

## Migration Status

### Completed Migrations
- ✅ Event-driven architecture (Phase 12.5)
- ✅ Vertical slice refactoring (Phase 13.5 + Phase 14) - Complete
- ✅ PostgreSQL support (Phase 13)
- ✅ Test suite stabilization (Phase 14)
- ✅ Documentation modular migration (20 files migrated)
- ✅ Legacy code cleanup (Phase 14)

### Architecture Achievements
- ✅ 13 self-contained modules with event-driven communication
- ✅ Shared kernel for cross-cutting concerns
- ✅ Zero circular dependencies between modules
- ✅ 97 API routes across all modules
- ✅ Event bus with <1ms latency (p95)

### Planned
- 📋 API versioning
- 📋 Authentication and authorization
- 📋 Rate limiting
- 📋 Frontend-backend integration completion

## Related Documentation

- [Product Overview](.kiro/steering/product.md)
- [Tech Stack](.kiro/steering/tech.md)
- [Spec Organization](.kiro/specs/README.md)
- [Documentation Index](../../backend/docs/index.md)
- [API Reference](../../backend/docs/api/overview.md)
- [Architecture Overview](../../backend/docs/architecture/overview.md)
- [Developer Setup Guide](../../backend/docs/guides/setup.md)
