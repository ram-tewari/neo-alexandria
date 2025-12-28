# Neo Alexandria 2.0 - Complete Documentation

**Generated:** December 28, 2025 at 08:19:49

---

# Table of Contents

1. [Agent Context Management](#agent-context-management)
2. [Product Overview](#product-overview)
3. [Technical Stack](#technical-stack)
4. [Repository Structure](#repository-structure)
5. [Backend Documentation Index](#backend-documentation-index)
6. [API Overview](#api-overview)
7. [Resources API](#resources-api)
8. [Search API](#search-api)
9. [Collections API](#collections-api)
10. [Annotations API](#annotations-api)
11. [Taxonomy API](#taxonomy-api)
12. [Graph API](#graph-api)
13. [Recommendations API](#recommendations-api)
14. [Quality API](#quality-api)
15. [Scholarly API](#scholarly-api)
16. [Authority API](#authority-api)
17. [Curation API](#curation-api)
18. [Monitoring API](#monitoring-api)
19. [Architecture Overview](#architecture-overview)
20. [Database Architecture](#database-architecture)
21. [Event System](#event-system)
22. [Event Catalog](#event-catalog)
23. [Module Architecture](#module-architecture)
24. [Architecture Decisions](#architecture-decisions)
25. [Setup Guide](#setup-guide)
26. [Development Workflows](#development-workflows)
27. [Testing Guide](#testing-guide)
28. [Deployment Guide](#deployment-guide)
29. [Troubleshooting](#troubleshooting)
30. [Backend Overview](#backend-overview)

---



# 1. Agent Context Management

*Source: `AGENTS.md`*

---

# Agent Context Management

## Purpose

This document provides routing rules for AI agents working with Neo Alexandria 2.0. It ensures efficient context usage and points to the right documentation.

## Token Hygiene Rules

1. **Never load entire files** unless explicitly needed for the current task
2. **Use targeted reads** with line ranges when possible
3. **Reference documentation** by path rather than loading it
4. **Close completed specs** - archive or mark as done when features are implemented
5. **Rotate context** - only keep active work in focus

## Documentation Structure

```
AGENTS.md (this file)          # Routing and hygiene rules
.kiro/steering/
  ├── product.md               # Product vision and goals
  ├── tech.md                  # Tech stack and constraints
  └── structure.md             # Repo map and truth sources
.kiro/specs/
  ├── [feature-name]/          # Active feature specs
  │   ├── requirements.md
  │   ├── design.md
  │   └── tasks.md
  └── README.md                # Spec organization
backend/docs/
  ├── index.md                 # Documentation index
  ├── api/                     # API reference (split by domain)
  ├── architecture/            # System architecture
  └── guides/                  # Developer guides
frontend/                      # Frontend-specific docs
```

## Finding the Right Documentation

### For Product Questions
→ Read `.kiro/steering/product.md`

### For Tech Stack Questions
→ Read `.kiro/steering/tech.md`

### For Repo Navigation
→ Read `.kiro/steering/structure.md`

### For Feature Work
→ Read `.kiro/specs/[feature-name]/requirements.md` and `design.md`

### For API Documentation
→ Read `backend/docs/index.md` then navigate to specific domain
→ Example: `backend/docs/api/search.md` for search endpoints

### For Architecture Details
→ Read `backend/docs/architecture/overview.md`
→ Example: `backend/docs/architecture/database.md` for schema

### For Development Guides
→ Read `backend/docs/guides/setup.md` for getting started
→ Example: `backend/docs/guides/testing.md` for test strategies

## Working with Specs

### Active Specs Only
Only load specs that are:
- Currently being worked on
- Explicitly requested by the user
- Needed for context on current task

### Completed Specs
Specs in `.kiro/specs/` that are fully implemented should be:
- Marked as complete in their README
- Referenced by path only (not loaded)
- Archived if no longer relevant

### Creating New Specs
Follow the spec workflow:
1. Create `.kiro/specs/[feature-name]/` directory
2. Write `requirements.md` first
3. Then `design.md`
4. Finally `tasks.md`
5. Execute tasks incrementally

## Context Budget Guidelines

- **Small tasks** (<5 files): Load files directly
- **Medium tasks** (5-15 files): Load selectively, reference others
- **Large tasks** (>15 files): Use structure.md as map, load only what's needed
- **Exploratory work**: Start with structure.md, drill down as needed

## Quick Reference

| Need | Read |
|------|------|
| What is this project? | `.kiro/steering/product.md` |
| What tech do we use? | `.kiro/steering/tech.md` |
| Where is X located? | `.kiro/steering/structure.md` |
| How do I implement Y? | `.kiro/specs/[feature]/design.md` |
| What's the API? | `backend/docs/index.md` → `api/` |
| What's the architecture? | `backend/docs/architecture/overview.md` |
| How do I set up dev env? | `backend/docs/guides/setup.md` |
| How do I test? | `backend/docs/guides/testing.md` |

## Anti-Patterns to Avoid

❌ Loading all specs at once
❌ Reading entire backend/README.md for simple questions
❌ Loading documentation "just in case"
❌ Keeping completed spec context open
❌ Reading files without a specific purpose

✅ Load only what's needed for current task
✅ Use structure.md as a map
✅ Reference docs by path
✅ Close completed work
✅ Ask user if unsure what's needed


<div style='page-break-after: always;'></div>

---



# 2. Product Overview

*Source: `.kiro/steering/product.md`*

---

# Neo Alexandria 2.0 - Product Overview

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

## Non-Goals

### What We Are NOT Building

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

## Roadmap Themes

### Current Focus (Phase 13-14)
- PostgreSQL migration for production scalability
- Test suite stabilization
- Vertical slice architecture refactoring
- Frontend-backend integration

### Near-term (Next 3-6 months)
- Enhanced ML classification with active learning
- Advanced graph intelligence features
- Improved recommendation algorithms
- Performance optimization

### Long-term Vision
- Multi-language support
- Advanced visualization tools
- Plugin ecosystem
- Community-contributed models


<div style='page-break-after: always;'></div>

---



# 3. Technical Stack

*Source: `.kiro/steering/tech.md`*

---

# Neo Alexandria 2.0 - Technical Stack

## Architecture

**Type**: Modular Monolith with Event-Driven Communication
**Pattern**: Vertical slices with shared kernel
**Deployment**: Self-hosted, containerized

### Architectural Principles

1. **Vertical Slice Architecture**: Each module is self-contained with its own models, schemas, services, and routes
2. **Event-Driven Communication**: Modules communicate via event bus (no direct imports)
3. **Shared Kernel**: Cross-cutting concerns (database, cache, embeddings, AI) in shared layer
4. **Zero Circular Dependencies**: Enforced by module isolation rules
5. **API-First Design**: All functionality exposed via REST API

### Module Structure

**13 Domain Modules**:
- Annotations, Authority, Collections, Curation, Graph
- Monitoring, Quality, Recommendations, Resources, Scholarly
- Search, Taxonomy

**Each Module Contains**:
- `router.py` - FastAPI endpoints
- `service.py` - Business logic
- `schema.py` - Pydantic models
- `model.py` - SQLAlchemy models
- `handlers.py` - Event handlers
- `README.md` - Documentation

**Shared Kernel**:
- Database session management
- Event bus (in-memory, async)
- Vector embeddings
- AI operations (summarization, extraction)
- Redis caching

### Event-Driven Communication

**Event Bus**: In-memory, async, <1ms latency (p95)

**Event Categories**:
- Resource lifecycle: `resource.created`, `resource.updated`, `resource.deleted`
- Collections: `collection.created`, `collection.resource_added`
- Annotations: `annotation.created`, `annotation.updated`, `annotation.deleted`
- Quality: `quality.computed`, `quality.outlier_detected`
- Classification: `resource.classified`, `taxonomy.model_trained`
- Graph: `citation.extracted`, `graph.updated`, `hypothesis.discovered`
- Recommendations: `recommendation.generated`, `user.profile_updated`
- Curation: `curation.reviewed`, `curation.approved`
- Metadata: `metadata.extracted`, `equations.parsed`, `tables.extracted`

**Event Flow Example**:
```
1. User creates resource → resources module emits resource.created
2. Quality module subscribes → computes quality scores
3. Taxonomy module subscribes → auto-classifies resource
4. Scholarly module subscribes → extracts metadata
5. Graph module subscribes → extracts citations
6. All happen asynchronously, no blocking
```

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
- **hypothesis** - Property-based testing (planned)

## Frontend Stack

### Core Framework
- **React 18** - UI library
- **TypeScript 5** - Type safety
- **Vite 5** - Build tool and dev server

### Routing & State
- **React Router 6** - Client-side routing
- **Zustand** - Lightweight state management
- **React Query** - Server state management

### Styling
- **CSS Modules** - Component styling
- **Tailwind CSS** - Utility-first CSS
- **Framer Motion** - Animations

### Testing
- **Vitest** - Unit testing
- **React Testing Library** - Component testing

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

## Key Constraints

### Performance Requirements
- API response time: P95 < 200ms
- Search latency: < 500ms for hybrid search
- Embedding generation: < 2s per document
- Database queries: < 100ms for most operations
- Event emission + delivery: < 1ms (p95)
- Module startup: < 10 seconds total

### Scalability Targets
- 100K+ resources in database
- 10K+ concurrent embeddings
- 1K+ collections per user
- 100+ requests/second

### Resource Limits
- Memory: 4GB minimum, 8GB recommended
- Storage: 10GB minimum for models and data
- CPU: 2+ cores recommended
- GPU: Optional, improves ML performance 10x

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

### Migration Path
- Maintain SQLite compatibility
- Test against both databases
- Use Alembic for schema changes
- Provide migration scripts

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

### Frontend Development
```bash
# Start dev server
cd frontend
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Lint
npm run lint
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

## API Standards

### REST Conventions
- Use standard HTTP methods (GET, POST, PUT, DELETE)
- Return appropriate status codes (200, 201, 400, 404, 500)
- Use JSON for request/response bodies
- Include pagination for list endpoints
- Provide filtering and sorting options

### Response Format
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

### Error Format
```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Security Considerations

- Input validation with Pydantic
- SQL injection prevention via ORM
- XSS protection in frontend
- CORS configuration for API
- Rate limiting (planned)
- API key authentication (planned)

## Monitoring & Observability

- Structured logging with JSON format
- Health check endpoints per module
- Database connection pool monitoring
- ML model performance tracking
- Event bus metrics (throughput, latency)
- Module dependency graph validation
- Error tracking and alerting (planned)

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

### CI/CD Integration
- Module isolation checker runs on every commit
- Build fails if violations detected
- Dependency graph generated and archived


<div style='page-break-after: always;'></div>

---



# 4. Repository Structure

*Source: `.kiro/steering/structure.md`*

---

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


<div style='page-break-after: always;'></div>

---



# 5. Backend Documentation Index

*Source: `backend/docs/index.md`*

---

# Backend Documentation Index

## Quick Navigation

| Need | Read |
|------|------|
| API endpoints | [API Reference](api/) |
| System architecture | [Architecture](architecture/) |
| Development setup | [Developer Guides](guides/) |
| Database info | [Architecture: Database](architecture/database.md) |
| Testing | [Guides: Testing](guides/testing.md) |

## Documentation Structure

```
backend/docs/
├── index.md                    # This file
├── api/                        # API Reference (split by domain/module)
│   ├── overview.md             # Auth, errors, base URLs, module architecture
│   ├── resources.md            # Resource management endpoints
│   ├── search.md               # Search endpoints (hybrid, vector, FTS)
│   ├── collections.md          # Collection management
│   ├── annotations.md          # Annotation system
│   ├── taxonomy.md             # Taxonomy & classification
│   ├── graph.md                # Knowledge graph & citations
│   ├── recommendations.md      # Recommendation engine
│   ├── quality.md              # Quality assessment
│   ├── scholarly.md            # Academic metadata extraction
│   ├── authority.md            # Subject authority
│   ├── curation.md             # Content review
│   └── monitoring.md           # Monitoring & health checks
├── architecture/               # System Architecture
│   ├── overview.md             # High-level system design
│   ├── database.md             # Database schema & models
│   ├── event-system.md         # Event-driven architecture
│   ├── events.md               # Event catalog
│   ├── modules.md              # Vertical slice modules
│   └── decisions.md            # Architectural Decision Records (ADRs)
└── guides/                     # Developer Guides
    ├── setup.md                # Installation & environment
    ├── workflows.md            # Common development tasks
    ├── testing.md              # Testing strategies
    ├── deployment.md           # Docker & production
    └── troubleshooting.md      # Common issues & solutions
```

## API Reference

Complete REST API documentation organized by module:

- [API Overview](api/overview.md) - Authentication, errors, pagination, module architecture
- [Resources API](api/resources.md) - Content management and ingestion
- [Search API](api/search.md) - Hybrid search, three-way fusion
- [Collections API](api/collections.md) - Collection management
- [Annotations API](api/annotations.md) - Text highlighting and notes
- [Taxonomy API](api/taxonomy.md) - Classification and ML
- [Graph API](api/graph.md) - Knowledge graph and citations
- [Recommendations API](api/recommendations.md) - Personalized content
- [Quality API](api/quality.md) - Quality assessment
- [Scholarly API](api/scholarly.md) - Academic metadata extraction
- [Authority API](api/authority.md) - Subject authority and classification
- [Curation API](api/curation.md) - Content review and batch operations
- [Monitoring API](api/monitoring.md) - Health checks and metrics

## Architecture

System design and technical decisions:

- [Architecture Overview](architecture/overview.md) - High-level system design and module structure
- [Database](architecture/database.md) - Schema, models, migrations
- [Event System](architecture/event-system.md) - Event-driven communication patterns
- [Event Catalog](architecture/events.md) - Complete event reference
- [Modules](architecture/modules.md) - Vertical slice architecture
- [Design Decisions](architecture/decisions.md) - ADRs

## Developer Guides

Getting started and development workflows:

- [Setup Guide](guides/setup.md) - Installation and configuration
- [Development Workflows](guides/workflows.md) - Common tasks
- [Testing Guide](guides/testing.md) - Running and writing tests
- [Deployment Guide](guides/deployment.md) - Docker and production
- [Troubleshooting](guides/troubleshooting.md) - Common issues

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Related Documentation

- [Steering Docs](../../.kiro/steering/) - High-level project context
- [Spec Organization](../../.kiro/specs/) - Feature specifications
- [Frontend Docs](../../frontend/README.md) - Frontend documentation


<div style='page-break-after: always;'></div>

---



# 6. API Overview

*Source: `backend/docs/api/overview.md`*

---

# API Overview

## Base URL

```
Development: http://127.0.0.1:8000
Production: https://your-domain.com/api
```

## Authentication

Currently, no authentication is required for development and testing.

**Future Authentication (Planned):**
- API Key in `Authorization` header: `Authorization: Bearer <api_key>`
- Rate limiting: 1000 requests/hour per API key
- Ingestion limits: 100 requests/hour per API key

## Content Types

All API endpoints accept and return JSON data:
```
Content-Type: application/json
```

## Response Format

### Success Response

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

### Error Response

```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 202 | Accepted - Request accepted for processing |
| 204 | No Content - Successful deletion |
| 400 | Bad Request - Invalid request parameters |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

## Pagination

List endpoints support pagination with `limit` and `offset`:

```
GET /resources?limit=25&offset=0
```

Response includes total count:

```json
{
  "items": [...],
  "total": 100
}
```

Some endpoints use page-based pagination:

```
GET /collections?page=1&limit=50
```

## Filtering

Most list endpoints support filtering:

```
GET /resources?language=en&min_quality=0.7&classification_code=004
```

See individual endpoint documentation for available filters.

## Sorting

List endpoints support sorting:

```
GET /resources?sort_by=created_at&sort_dir=desc
```

Common sort fields: `created_at`, `updated_at`, `quality_score`, `title`, `relevance`

## Rate Limiting

**Current**: No rate limits enforced

**Planned**:
- General API: 1000 requests per hour per API key
- Ingestion: 100 requests per hour per API key
- Search: 500 requests per hour per API key
- Burst Allowance: 50 requests per minute for short-term spikes

## API Endpoints by Domain

Neo Alexandria 2.0 uses a modular architecture where each domain is implemented as a self-contained module. All modules follow consistent patterns for routing, services, and event handling.

| Module | Description | Documentation |
|--------|-------------|---------------|
| Resources | Content management and ingestion | [resources.md](resources.md) |
| Search | Hybrid search with vector and FTS | [search.md](search.md) |
| Collections | Collection management and sharing | [collections.md](collections.md) |
| Annotations | Active reading with highlights and notes | [annotations.md](annotations.md) |
| Taxonomy | ML classification and taxonomy trees | [taxonomy.md](taxonomy.md) |
| Graph | Knowledge graph, citations, and discovery | [graph.md](graph.md) |
| Recommendations | Hybrid recommendation engine | [recommendations.md](recommendations.md) |
| Quality | Multi-dimensional quality assessment | [quality.md](quality.md) |
| Scholarly | Academic metadata extraction | [scholarly.md](scholarly.md) |
| Authority | Subject authority and classification | [authority.md](authority.md) |
| Curation | Content review and batch operations | [curation.md](curation.md) |
| Monitoring | System health and metrics | [monitoring.md](monitoring.md) |

### Module Architecture

Each module is self-contained with:
- **Router**: FastAPI endpoints at `/module-name/*`
- **Service**: Business logic and data access
- **Schema**: Pydantic models for validation
- **Model**: SQLAlchemy database models
- **Handlers**: Event subscribers and emitters
- **README**: Module-specific documentation

Modules communicate through an event bus, eliminating direct dependencies.

## Complete Endpoint Reference

### Content Management
- `POST /resources` - Ingest new resource from URL
- `GET /resources` - List resources with filtering
- `GET /resources/{id}` - Get specific resource
- `PUT /resources/{id}` - Update resource metadata
- `DELETE /resources/{id}` - Delete resource
- `GET /resources/{id}/status` - Check ingestion status
- `PUT /resources/{id}/classify` - Override classification

### Search and Discovery
- `POST /search` - Advanced hybrid search
- `GET /search/three-way-hybrid` - Three-way hybrid search
- `GET /search/compare-methods` - Compare search methods
- `POST /search/evaluate` - Evaluate search quality

### Collections
- `POST /collections` - Create collection
- `GET /collections/{id}` - Get collection
- `PUT /collections/{id}` - Update collection
- `DELETE /collections/{id}` - Delete collection
- `GET /collections` - List collections
- `POST /collections/{id}/resources` - Add resources
- `DELETE /collections/{id}/resources` - Remove resources
- `GET /collections/{id}/recommendations` - Get recommendations

### Annotations
- `POST /resources/{id}/annotations` - Create annotation
- `GET /resources/{id}/annotations` - List annotations
- `GET /annotations` - List all user annotations
- `PUT /annotations/{id}` - Update annotation
- `DELETE /annotations/{id}` - Delete annotation
- `GET /annotations/search/fulltext` - Full-text search
- `GET /annotations/search/semantic` - Semantic search
- `GET /annotations/export/markdown` - Export to Markdown
- `GET /annotations/export/json` - Export to JSON

### Taxonomy
- `POST /taxonomy/nodes` - Create taxonomy node
- `PUT /taxonomy/nodes/{id}` - Update node
- `DELETE /taxonomy/nodes/{id}` - Delete node
- `POST /taxonomy/nodes/{id}/move` - Move node
- `GET /taxonomy/tree` - Get taxonomy tree
- `POST /taxonomy/classify/{id}` - Classify resource
- `POST /taxonomy/train` - Train ML model

### Quality
- `GET /resources/{id}/quality-details` - Quality breakdown
- `POST /quality/recalculate` - Recalculate quality
- `GET /quality/outliers` - Get quality outliers
- `GET /quality/degradation` - Monitor degradation
- `GET /quality/distribution` - Quality distribution
- `GET /quality/trends` - Quality trends

### Monitoring
- `GET /health` - Health check
- `GET /monitoring/status` - System status
- `GET /monitoring/metrics` - System metrics

## SDKs and Libraries

### Python

```python
import requests

# Import from modules (new structure)
from app.modules.resources.schema import ResourceCreate
from app.modules.search.schema import SearchRequest

# Ingest a resource
response = requests.post(
    "http://127.0.0.1:8000/resources",
    json={"url": "https://example.com/article"}
)

# Search resources
response = requests.post(
    "http://127.0.0.1:8000/search",
    json={
        "text": "machine learning",
        "hybrid_weight": 0.7,
        "limit": 10
    }
)

# Create a collection
response = requests.post(
    "http://127.0.0.1:8000/collections",
    json={
        "name": "ML Papers",
        "description": "Machine learning research papers"
    }
)
```

### JavaScript

```javascript
// Ingest a resource
const response = await fetch('http://127.0.0.1:8000/resources', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://example.com/article' })
});

// Search resources
const searchResponse = await fetch('http://127.0.0.1:8000/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'machine learning',
    hybrid_weight: 0.7,
    limit: 10
  })
});

// Create a collection
const collectionResponse = await fetch('http://127.0.0.1:8000/collections', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'ML Papers',
    description: 'Machine learning research papers'
  })
});
```

### Module Imports (Backend Development)

When developing backend features, import from modules:

```python
# Import from modules
from app.modules.resources import ResourceService, ResourceCreate
from app.modules.search import SearchService, SearchRequest
from app.modules.collections import CollectionService, CollectionCreate
from app.modules.annotations import AnnotationService, AnnotationCreate
from app.modules.taxonomy import TaxonomyService, ClassificationResult
from app.modules.graph import GraphService, CitationService
from app.modules.recommendations import RecommendationService
from app.modules.quality import QualityService, QualityDimensions

# Import from shared kernel
from app.shared.embeddings import EmbeddingService
from app.shared.ai_core import AICore
from app.shared.cache import CacheService
from app.shared.database import get_db
from app.shared.event_bus import event_bus
```

## Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Related Documentation

- [Architecture Overview](../architecture/overview.md)
- [Developer Setup](../guides/setup.md)
- [Testing Guide](../guides/testing.md)


<div style='page-break-after: always;'></div>

---



# 7. Resources API

*Source: `backend/docs/api/resources.md`*

---

﻿# Resources API

Resource management endpoints for content ingestion, retrieval, and curation.

## Overview

The Resources API provides CRUD operations for managing knowledge resources. Resources are the core content units in Neo Alexandria, representing articles, papers, documents, and other knowledge artifacts.

## Endpoints

### POST /resources

Creates a new resource by ingesting content from a URL with AI-powered asynchronous processing.

**Request Body:**
```json
{
  "url": "string (required)",
  "title": "string (optional)",
  "description": "string (optional)",
  "language": "string (optional)",
  "type": "string (optional)",
  "source": "string (optional)"
}
```

**Response (202 Accepted):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending"
}
```

**Background Processing:**
1. Fetch content from the provided URL
2. Extract text from HTML/PDF content
3. Generate AI-powered summary using transformers
4. Generate intelligent tags using zero-shot classification
5. Normalize metadata using authority control
6. Classify content using the classification system
7. Calculate quality score
8. Archive content locally
9. Update resource status to "completed" or "failed"

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/resources \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

---

### GET /resources/{resource_id}/status

Monitor the ingestion status of a resource.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "ingestion_status": "completed",
  "ingestion_error": null,
  "ingestion_started_at": "2024-01-01T10:00:00Z",
  "ingestion_completed_at": "2024-01-01T10:02:30Z"
}
```

**Status Values:**
- `pending` - Request received, processing not started
- `processing` - Content is being processed
- `completed` - Processing finished successfully
- `failed` - Processing failed with error

---

### GET /resources

List resources with filtering, sorting, and pagination.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `q` | string | Keyword search on title/description | - |
| `classification_code` | string | Filter by classification code | - |
| `type` | string | Filter by resource type | - |
| `language` | string | Filter by language | - |
| `read_status` | string | Filter by read status | - |
| `min_quality` | float | Minimum quality score (0.0-1.0) | - |
| `created_from` | datetime | Filter by creation date (ISO 8601) | - |
| `created_to` | datetime | Filter by creation date (ISO 8601) | - |
| `updated_from` | datetime | Filter by update date (ISO 8601) | - |
| `updated_to` | datetime | Filter by update date (ISO 8601) | - |
| `subject_any` | string[] | Filter by any of these subjects | - |
| `subject_all` | string[] | Filter by all of these subjects | - |
| `limit` | integer | Number of results (1-100) | 25 |
| `offset` | integer | Number of results to skip | 0 |
| `sort_by` | string | Sort field | updated_at |
| `sort_dir` | string | Sort direction (asc/desc) | desc |

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Machine Learning Fundamentals",
      "description": "Comprehensive guide to ML concepts",
      "creator": "John Doe",
      "publisher": "Tech Publications",
      "source": "https://example.com/ml-guide",
      "language": "en",
      "type": "article",
      "subject": ["Machine Learning", "Artificial Intelligence"],
      "classification_code": "004",
      "quality_score": 0.85,
      "read_status": "unread",
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:02:30Z"
    }
  ],
  "total": 1
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/resources?limit=5&classification_code=004&min_quality=0.8"
```

---

### GET /resources/{resource_id}

Retrieve a specific resource by ID.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Machine Learning Fundamentals",
  "description": "Comprehensive guide to ML concepts",
  "creator": "John Doe",
  "publisher": "Tech Publications",
  "source": "https://example.com/ml-guide",
  "language": "en",
  "type": "article",
  "subject": ["Machine Learning", "Artificial Intelligence"],
  "classification_code": "004",
  "quality_score": 0.85,
  "read_status": "unread",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:02:30Z"
}
```

---

### PUT /resources/{resource_id}

Update a resource with partial data. Only provided fields are modified.

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "read_status": "in_progress",
  "subject": ["Updated", "Tags"]
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Updated Title",
  "description": "Updated description",
  "read_status": "in_progress",
  "subject": ["Updated", "Tags"],
  "updated_at": "2024-01-01T11:00:00Z"
}
```

---

### DELETE /resources/{resource_id}

Delete a resource by ID.

**Response:** `204 No Content`

---

### PUT /resources/{resource_id}/classify

Override the classification code for a specific resource.

**Request Body:**
```json
{
  "code": "004"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Resource Title",
  "classification_code": "004",
  "updated_at": "2024-01-01T11:00:00Z"
}
```

## Data Models

### Resource Model

The core resource model follows Dublin Core metadata standards with custom extensions:

```json
{
  "id": "uuid",
  "title": "string (required)",
  "description": "string",
  "creator": "string",
  "publisher": "string",
  "contributor": "string",
  "source": "string",
  "language": "string",
  "type": "string",
  "format": "string",
  "identifier": "string",
  "subject": ["string"],
  "relation": ["string"],
  "coverage": "string",
  "rights": "string",
  "classification_code": "string",
  "read_status": "unread|in_progress|completed|archived",
  "quality_score": "float (0.0-1.0)",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

## Module Structure

The Resources module is implemented as a self-contained vertical slice:

**Module**: `app.modules.resources`  
**Router Prefix**: `/resources`  
**Version**: 1.0.0

```python
from app.modules.resources import (
    resources_router,
    ResourceService,
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse
)
```

### Events

**Emitted Events:**
- `resource.created` - When a new resource is ingested
- `resource.updated` - When resource metadata is updated
- `resource.deleted` - When a resource is removed

**Subscribed Events:**
- None (Resources is a foundational module)

## Related Documentation

- [Search API](search.md) - Search and discovery
- [Collections API](collections.md) - Organize resources into collections
- [Quality API](quality.md) - Quality assessment details
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors, pagination


<div style='page-break-after: always;'></div>

---



# 8. Search API

*Source: `backend/docs/api/search.md`*

---

﻿# Search API

Advanced search endpoints with hybrid keyword/semantic capabilities, three-way fusion, and faceted results.

## Overview

The Search API provides multiple search strategies:
- **Hybrid Search** - Combines keyword (FTS5) and semantic (vector) search
- **Three-Way Hybrid** - Adds sparse vectors with RRF fusion and ColBERT reranking
- **Method Comparison** - Side-by-side comparison of search methods
- **Quality Evaluation** - IR metrics for search quality assessment

## Endpoints

### POST /search

Advanced search with hybrid keyword/semantic capabilities and faceted results.

**Request Body:**
```json
{
  "text": "machine learning algorithms",
  "hybrid_weight": 0.5,
  "filters": {
    "classification_code": ["004"],
    "language": ["en"],
    "min_quality": 0.7,
    "subject_any": ["Machine Learning"],
    "subject_all": ["Artificial Intelligence", "Machine Learning"]
  },
  "limit": 25,
  "offset": 0,
  "sort_by": "relevance",
  "sort_dir": "desc"
}
```

**Request Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `text` | string | Search query text | - |
| `hybrid_weight` | float | Weight for hybrid search (0.0-1.0) | 0.5 |
| `filters` | object | Filter criteria | - |
| `limit` | integer | Number of results (1-100) | 25 |
| `offset` | integer | Number of results to skip | 0 |
| `sort_by` | string | Sort field | relevance |
| `sort_dir` | string | Sort direction (asc/desc) | desc |

**Hybrid Search Weight:**
- `0.0` - Pure keyword search (FTS5)
- `0.5` - Balanced hybrid search (default)
- `1.0` - Pure semantic search (vector similarity)

**Response:**
```json
{
  "total": 42,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Machine Learning Fundamentals",
      "description": "Comprehensive guide to ML concepts",
      "subject": ["Machine Learning", "Artificial Intelligence"],
      "quality_score": 0.85,
      "relevance_score": 0.92,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:02:30Z"
    }
  ],
  "facets": {
    "classification_code": [{"key": "004", "count": 30}],
    "type": [{"key": "article", "count": 35}],
    "language": [{"key": "en", "count": 33}],
    "read_status": [{"key": "unread", "count": 20}],
    "subject": [{"key": "Machine Learning", "count": 18}]
  }
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "text": "artificial intelligence",
    "hybrid_weight": 0.7,
    "filters": {"min_quality": 0.8},
    "limit": 10
  }'
```

---

### GET /search/three-way-hybrid

Execute three-way hybrid search combining FTS5, dense vectors, and sparse vectors with RRF fusion and optional ColBERT reranking.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `query` | string | Search query text (required) | - |
| `limit` | integer | Number of results (1-100) | 20 |
| `offset` | integer | Number of results to skip | 0 |
| `enable_reranking` | boolean | Apply ColBERT reranking | true |
| `adaptive_weighting` | boolean | Use query-adaptive RRF weights | true |

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Machine Learning Fundamentals",
      "description": "Comprehensive guide to ML concepts",
      "subject": ["Machine Learning", "Artificial Intelligence"],
      "quality_score": 0.85,
      "relevance_score": 0.92,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 42,
  "latency_ms": 145.3,
  "method_contributions": {
    "fts5": 45,
    "dense": 38,
    "sparse": 42
  },
  "weights_used": [0.35, 0.35, 0.30],
  "facets": {
    "classification_code": [{"key": "004", "count": 30}],
    "type": [{"key": "article", "count": 35}],
    "language": [{"key": "en", "count": 33}]
  }
}
```

**Example:**
```bash
# Three-way search with reranking and adaptive weighting
curl "http://127.0.0.1:8000/search/three-way-hybrid?query=machine+learning&limit=20&enable_reranking=true"

# Fast three-way search without reranking
curl "http://127.0.0.1:8000/search/three-way-hybrid?query=neural+networks&limit=10&enable_reranking=false"
```

**Performance:**
- Target latency: <200ms at 95th percentile
- With reranking: <1 second for 100 candidates
- Parallel retrieval for optimal speed

---

### GET /search/compare-methods

Compare different search methods side-by-side for debugging and optimization.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `query` | string | Search query text (required) | - |
| `limit` | integer | Number of results per method (1-50) | 20 |

**Response (200 OK):**
```json
{
  "query": "machine learning",
  "methods": {
    "fts5_only": {
      "results": [...],
      "latency_ms": 25.3,
      "count": 20
    },
    "dense_only": {
      "results": [...],
      "latency_ms": 42.1,
      "count": 20
    },
    "sparse_only": {
      "results": [...],
      "latency_ms": 38.7,
      "count": 20
    },
    "two_way_hybrid": {
      "results": [...],
      "latency_ms": 67.4,
      "count": 20
    },
    "three_way_hybrid": {
      "results": [...],
      "latency_ms": 106.1,
      "count": 20
    },
    "three_way_reranked": {
      "results": [...],
      "latency_ms": 856.8,
      "count": 20
    }
  }
}
```

**Use Cases:**
- Debug search quality issues
- Compare method effectiveness for different query types
- Analyze latency trade-offs
- Validate search improvements

---

### POST /search/evaluate

Evaluate search quality using information retrieval metrics (nDCG, Recall, Precision, MRR).

**Request Body:**
```json
{
  "query": "machine learning",
  "relevance_judgments": {
    "resource_id_1": 3,
    "resource_id_2": 2,
    "resource_id_3": 1,
    "resource_id_4": 0
  }
}
```

**Relevance Scale:**
- `3` - Highly relevant
- `2` - Relevant
- `1` - Marginally relevant
- `0` - Not relevant

**Response (200 OK):**
```json
{
  "query": "machine learning",
  "metrics": {
    "ndcg@20": 0.847,
    "recall@20": 0.923,
    "precision@20": 0.650,
    "mrr": 0.833
  },
  "baseline_comparison": {
    "two_way_ndcg": 0.651,
    "improvement": 0.301
  }
}
```

**Metrics Explained:**
- **nDCG@20**: Normalized Discounted Cumulative Gain at position 20 (0-1, higher is better)
- **Recall@20**: Fraction of relevant documents retrieved in top 20 (0-1, higher is better)
- **Precision@20**: Fraction of top 20 results that are relevant (0-1, higher is better)
- **MRR**: Mean Reciprocal Rank of first relevant result (0-1, higher is better)

---

### POST /admin/sparse-embeddings/generate

Batch generate sparse embeddings for existing resources without them.

**Request Body:**
```json
{
  "resource_ids": ["uuid1", "uuid2"],
  "batch_size": 32
}
```

**Parameters:**
- `resource_ids` (optional): Specific resources to process. If omitted, processes all resources without sparse embeddings.
- `batch_size` (optional): Batch size for processing (default: 32 for GPU, 8 for CPU)

**Response (202 Accepted):**
```json
{
  "status": "queued",
  "job_id": "job_uuid",
  "estimated_duration_minutes": 45,
  "resources_to_process": 10000
}
```

**Background Processing:**
- Processes resources in batches for efficiency
- Commits every 100 resources
- Logs progress updates
- Resumes from last committed batch if interrupted
- Target: <1 second per resource

## Data Models

### Search Request Model

```json
{
  "text": "string",
  "hybrid_weight": "float (0.0-1.0)",
  "filters": {
    "classification_code": ["string"],
    "language": ["string"],
    "type": ["string"],
    "read_status": ["string"],
    "min_quality": "float",
    "max_quality": "float",
    "created_from": "datetime",
    "created_to": "datetime",
    "updated_from": "datetime",
    "updated_to": "datetime",
    "subject_any": ["string"],
    "subject_all": ["string"]
  },
  "limit": "integer (1-100)",
  "offset": "integer (>=0)",
  "sort_by": "relevance|updated_at|created_at|quality_score|title",
  "sort_dir": "asc|desc"
}
```

### Search Response Model

```json
{
  "total": "integer",
  "items": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string",
      "subject": ["string"],
      "quality_score": "float",
      "relevance_score": "float",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "facets": {
    "classification_code": [{"key": "string", "count": "integer"}],
    "type": [{"key": "string", "count": "integer"}],
    "language": [{"key": "string", "count": "integer"}],
    "read_status": [{"key": "string", "count": "integer"}],
    "subject": [{"key": "string", "count": "integer"}]
  }
}
```

## Module Structure

The Search module is implemented as a self-contained vertical slice:

**Module**: `app.modules.search`  
**Router Prefix**: `/search`  
**Version**: 1.0.0

```python
from app.modules.search import (
    search_router,
    SearchService,
    SearchRequest,
    SearchResponse,
    SearchStrategy
)
```

### Events

**Emitted Events:**
- `search.executed` - When a search is performed
- `search.results_returned` - When search results are returned

**Subscribed Events:**
- `resource.created` - Updates search indices
- `resource.updated` - Updates search indices
- `resource.deleted` - Removes from search indices

## Related Documentation

- [Resources API](resources.md) - Content management
- [Recommendations API](recommendations.md) - Personalized discovery
- [Graph API](graph.md) - Knowledge graph exploration
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors, pagination


<div style='page-break-after: always;'></div>

---



# 9. Collections API

*Source: `backend/docs/api/collections.md`*

---

﻿# Collections API

Collection management endpoints for organizing resources into hierarchical groups.

## Overview

Collections allow users to organize resources into named groups with:
- Hierarchical parent-child relationships
- Visibility controls (private, shared, public)
- Aggregate embeddings for similarity-based recommendations
- Batch resource membership operations

## Endpoints

### POST /collections

Create a new collection with metadata and optional hierarchical parent.

**Request Body:**
```json
{
  "name": "string (required, 1-255 characters)",
  "description": "string (optional, max 2000 characters)",
  "visibility": "private|shared|public (optional, default: private)",
  "parent_id": "string (optional, UUID of parent collection)"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Machine Learning Papers",
  "description": "Curated collection of ML research",
  "owner_id": "user123",
  "visibility": "public",
  "parent_id": null,
  "resource_count": 0,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z",
  "resources": []
}
```

**Error Responses:**
- `400 Bad Request` - Invalid name length, visibility value, or circular hierarchy
- `404 Not Found` - Parent collection not found

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Machine Learning Papers",
    "description": "Curated collection of ML research",
    "visibility": "public"
  }'
```

---

### GET /collections/{id}

Retrieve a specific collection with member resource summaries.

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Machine Learning Papers",
  "description": "Curated collection of ML research",
  "owner_id": "user123",
  "visibility": "public",
  "parent_id": null,
  "resource_count": 2,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:05:00Z",
  "resources": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Deep Learning Fundamentals",
      "creator": "John Doe",
      "quality_score": 0.92
    }
  ]
}
```

**Access Rules:**
- `private`: Only owner can access
- `shared`: Owner + explicit permissions (future)
- `public`: All authenticated users

---

### PUT /collections/{id}

Update collection metadata (name, description, visibility, parent).

**Request Body:**
```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "visibility": "private|shared|public (optional)",
  "parent_id": "string (optional, UUID or null)"
}
```

**Response (200 OK):** Returns updated collection object.

---

### DELETE /collections/{id}

Delete a collection. Cascade deletes all descendant collections.

**Response:** `204 No Content`

---

### GET /collections

List collections with filtering and pagination.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `owner_id` | string | Filter by owner | - |
| `visibility` | string | Filter by visibility | - |
| `parent_id` | string | Filter by parent (null for root) | - |
| `page` | integer | Page number | 1 |
| `limit` | integer | Results per page (1-100) | 50 |

**Response:**
```json
{
  "items": [...],
  "total": 1,
  "page": 1,
  "limit": 50
}
```

---

### POST /collections/{id}/resources

Add resources to a collection (batch operation, up to 100 resources).

**Request Body:**
```json
{
  "resource_ids": ["uuid", "uuid"]
}
```

**Response (200 OK):** Returns updated collection with new resource count.

**Behavior:**
- Validates all resource IDs exist before adding
- Handles duplicate associations gracefully (idempotent)
- Triggers aggregate embedding recomputation

---

### DELETE /collections/{id}/resources

Remove resources from a collection (batch operation).

**Request Body:**
```json
{
  "resource_ids": ["uuid", "uuid"]
}
```

**Response (200 OK):** Returns updated collection.

---

### GET /collections/{id}/recommendations

Get recommendations for similar resources and collections based on aggregate embedding.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Max results per category (1-50) | 10 |
| `include_resources` | boolean | Include resource recommendations | true |
| `include_collections` | boolean | Include collection recommendations | true |

**Response:**
```json
{
  "resources": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "title": "Advanced Neural Networks",
      "similarity": 0.92
    }
  ],
  "collections": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "name": "AI Research Papers",
      "similarity": 0.85
    }
  ]
}
```

---

### GET /collections/{id}/embedding

Retrieve the aggregate embedding vector for a collection.

**Response:**
```json
{
  "embedding": [0.123, -0.456, 0.789, ...],
  "dimension": 768
}
```

## Features

### Hierarchical Organization

Collections support parent-child relationships:

```bash
# Create parent
curl -X POST http://127.0.0.1:8000/collections \
  -d '{"name": "Computer Science", "visibility": "public"}'

# Create child
curl -X POST http://127.0.0.1:8000/collections \
  -d '{"name": "Machine Learning", "parent_id": "{parent_id}"}'
```

### Aggregate Embeddings

Collections automatically compute aggregate embeddings from member resources:
- Mean vector across all member resource embeddings
- Normalized to unit length (L2 norm)
- Recomputed when resources are added/removed

### Access Control

| Level | Owner | Other Users |
|-------|-------|-------------|
| `private` | Full access | None |
| `shared` | Full access | Read only (future) |
| `public` | Full access | Read only |

## Data Models

### Collection Model

```json
{
  "id": "uuid",
  "name": "string (1-255 characters)",
  "description": "string (max 2000 characters) or null",
  "owner_id": "string",
  "visibility": "private|shared|public",
  "parent_id": "uuid or null",
  "resource_count": "integer",
  "created_at": "datetime",
  "updated_at": "datetime",
  "resources": [...]
}
```

## Module Structure

The Collections module is implemented as a self-contained vertical slice:

**Module**: `app.modules.collections`  
**Router Prefix**: `/collections`  
**Version**: 1.0.0

```python
from app.modules.collections import (
    collections_router,
    CollectionService,
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse
)
```

### Events

**Emitted Events:**
- `collection.created` - When a new collection is created
- `collection.updated` - When collection metadata is updated
- `collection.deleted` - When a collection is removed
- `collection.resource_added` - When a resource is added to a collection
- `collection.resource_removed` - When a resource is removed from a collection

**Subscribed Events:**
- `resource.deleted` - Removes resource from all collections

## Related Documentation

- [Resources API](resources.md) - Content management
- [Recommendations API](recommendations.md) - Personalized discovery
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors, pagination


<div style='page-break-after: always;'></div>

---



# 10. Annotations API

*Source: `backend/docs/api/annotations.md`*

---

﻿# Annotations API

Active reading system for highlighting text and adding notes to resources.

## Overview

The Annotations API enables:
- Precise text highlighting with character offsets
- Notes with semantic embeddings for search
- Tag-based organization
- Full-text and semantic search across annotations
- Export to Markdown and JSON formats

## Endpoints

### POST /resources/{resource_id}/annotations

Create a new annotation on a resource.

**Request Body:**
```json
{
  "start_offset": "integer (required, >= 0)",
  "end_offset": "integer (required, > start_offset)",
  "highlighted_text": "string (required)",
  "note": "string (optional, max 10,000 characters)",
  "tags": ["string"] (optional, max 20 tags),
  "color": "string (optional, hex color, default: #FFFF00)",
  "collection_ids": ["uuid"] (optional)
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "resource_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "user123",
  "start_offset": 150,
  "end_offset": 200,
  "highlighted_text": "This is the key finding of the paper",
  "note": "Important result - contradicts previous assumptions",
  "tags": ["key-finding", "methodology"],
  "color": "#FFD700",
  "context_before": "...previous text leading up to...",
  "context_after": "...text following the highlight...",
  "is_shared": false,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

**Performance:** <50ms creation time (excluding async embedding generation)

---

### GET /resources/{resource_id}/annotations

List all annotations for a specific resource in document order.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `include_shared` | boolean | Include shared annotations | false |
| `tags` | string[] | Filter by tags (comma-separated) | - |

**Response:** Array of annotations ordered by `start_offset` ascending.

---

### GET /annotations

List all annotations for the authenticated user across all resources.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Results per page (1-100) | 50 |
| `offset` | integer | Number to skip | 0 |
| `sort_by` | string | Sort order (recent/oldest) | recent |

---

### GET /annotations/{annotation_id}

Retrieve a specific annotation by ID.

---

### PUT /annotations/{annotation_id}

Update an annotation's note, tags, color, or sharing status.

**Request Body:**
```json
{
  "note": "string (optional)",
  "tags": ["string"] (optional),
  "color": "string (optional)",
  "is_shared": "boolean (optional)"
}
```

**Note:** Cannot update `start_offset`, `end_offset`, or `highlighted_text`.

---

### DELETE /annotations/{annotation_id}

Delete an annotation.

**Response:** `204 No Content`

---

## Search Endpoints

### GET /annotations/search/fulltext

Search annotations using full-text search across notes and highlighted text.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `query` | string | Search query (required) | - |
| `limit` | integer | Max results (1-100) | 25 |

**Performance:** <100ms for 10,000 annotations

---

### GET /annotations/search/semantic

Search annotations using semantic similarity for conceptual discovery.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `query` | string | Search query (required) | - |
| `limit` | integer | Max results (1-50) | 10 |

**Response includes `similarity` score (0.0-1.0).**

**Performance:** <500ms for 1,000 annotations

---

### GET /annotations/search/tags

Search annotations by tags with flexible matching.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `tags` | string[] | Tags to search (comma-separated) | - |
| `match_all` | boolean | Require all tags (true) or any (false) | false |
| `limit` | integer | Max results (1-100) | 50 |

---

## Export Endpoints

### GET /annotations/export/markdown

Export annotations to Markdown format.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `resource_id` | string | Filter by resource (optional) | - |

**Response:** `Content-Type: text/markdown`

```markdown
# Annotations Export

## Deep Learning Fundamentals

### Annotation 1
**Highlighted Text:**
> This is the key finding of the paper

**Note:** Important result

**Tags:** key-finding, methodology

**Created:** 2024-01-01 10:00:00
```

---

### GET /annotations/export/json

Export annotations to JSON format with complete metadata.

**Response:**
```json
{
  "annotations": [...],
  "total": 1,
  "exported_at": "2024-01-01T12:00:00Z"
}
```

## Features

### Text Offset Tracking

Annotations use character offsets for precise positioning:
- Zero-indexed character positions
- `start_offset`: First character (inclusive)
- `end_offset`: Last character (exclusive)
- Example: `"Hello World"[0:5]` = `"Hello"`

### Context Extraction

Automatically captures 50 characters before and after the highlight for preview.

### Semantic Embeddings

Annotations with notes get automatic semantic embeddings:
- Generated asynchronously after creation
- Uses nomic-ai/nomic-embed-text-v1 (384 dimensions)
- Enables semantic search across annotations

### Privacy Model

- `is_shared=false`: Only owner can view (default)
- `is_shared=true`: Visible to all users with resource access

## Data Models

### Annotation Model

```json
{
  "id": "uuid",
  "resource_id": "uuid",
  "user_id": "string",
  "start_offset": "integer (>= 0)",
  "end_offset": "integer (> start_offset)",
  "highlighted_text": "string",
  "note": "string or null (max 10,000 characters)",
  "tags": ["string"] (max 20 tags),
  "color": "string (hex color)",
  "embedding": [float] or null (384-dimensional),
  "context_before": "string or null",
  "context_after": "string or null",
  "is_shared": "boolean",
  "collection_ids": ["uuid"] or null,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Module Structure

The Annotations module is implemented as a self-contained vertical slice:

**Module**: `app.modules.annotations`  
**Router Prefix**: `/annotations`  
**Version**: 1.0.0

```python
from app.modules.annotations import (
    annotations_router,
    AnnotationService,
    AnnotationCreate,
    AnnotationUpdate,
    AnnotationResponse
)
```

### Events

**Emitted Events:**
- `annotation.created` - When a new annotation is created
- `annotation.updated` - When an annotation is modified
- `annotation.deleted` - When an annotation is removed

**Subscribed Events:**
- `resource.deleted` - Cascade deletes annotations for deleted resources

## Related Documentation

- [Resources API](resources.md) - Content management
- [Search API](search.md) - Search capabilities
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors


<div style='page-break-after: always;'></div>

---



# 11. Taxonomy API

*Source: `backend/docs/api/taxonomy.md`*

---

﻿# Taxonomy API

Hierarchical taxonomy management and ML-powered classification endpoints.

## Overview

The Taxonomy API provides:
- CRUD operations for hierarchical taxonomy trees
- Materialized paths for efficient queries
- ML-powered resource classification
- Active learning for continuous model improvement
- Authority control for subjects and classification

## Taxonomy Management Endpoints

### POST /taxonomy/nodes

Create a new taxonomy node in the hierarchical tree.

**Request Body:**
```json
{
  "name": "Machine Learning",
  "parent_id": "550e8400-e29b-41d4-a716-446655440000",
  "description": "ML and deep learning topics",
  "keywords": ["neural networks", "deep learning"],
  "allow_resources": true
}
```

**Response (200 OK):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "Machine Learning",
  "slug": "machine-learning",
  "parent_id": "550e8400-e29b-41d4-a716-446655440000",
  "level": 1,
  "path": "/computer-science/machine-learning",
  "description": "ML and deep learning topics",
  "keywords": ["neural networks", "deep learning"],
  "resource_count": 0,
  "descendant_resource_count": 0,
  "is_leaf": true,
  "allow_resources": true,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

---

### PUT /taxonomy/nodes/{node_id}

Update taxonomy node metadata.

**Request Body:**
```json
{
  "name": "Deep Learning",
  "description": "Neural networks with multiple layers",
  "keywords": ["CNN", "RNN", "transformers"],
  "allow_resources": true
}
```

**Note:** To change parent, use the move endpoint instead.

---

### DELETE /taxonomy/nodes/{node_id}

Delete a taxonomy node.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `cascade` | boolean | Delete descendants vs reparent children | false |

**Behavior:**
- `cascade=false`: Child nodes reparented to deleted node's parent
- `cascade=true`: All descendant nodes deleted recursively
- Fails if node has assigned resources

---

### POST /taxonomy/nodes/{node_id}/move

Move a taxonomy node to a different parent.

**Request Body:**
```json
{
  "new_parent_id": "770e8400-e29b-41d4-a716-446655440002"
}
```

**Validation:**
- Prevents circular references
- Prevents self-parenting
- Updates level and path for node and all descendants

---

### GET /taxonomy/tree

Retrieve the hierarchical taxonomy tree as nested JSON.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `root_id` | string | Starting node UUID | null (all roots) |
| `max_depth` | integer | Maximum tree depth | null (unlimited) |

**Response:** Nested tree structure with `children` arrays.

---

### GET /taxonomy/nodes/{node_id}/ancestors

Get all ancestor nodes for breadcrumb navigation.

**Performance:** O(depth) using materialized path, typically <10ms

---

### GET /taxonomy/nodes/{node_id}/descendants

Get all descendant nodes at any depth.

**Performance:** O(1) query using path pattern matching, typically <10ms

---

## Authority Control Endpoints

### GET /authority/subjects/suggest

Get subject suggestions for autocomplete.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query (required) |

**Response:**
```json
["Machine Learning", "Artificial Intelligence", "Data Science"]
```

---

### GET /authority/classification/tree

Retrieve the hierarchical classification tree (Dewey-style).

**Response:**
```json
{
  "tree": [
    {
      "code": "000",
      "name": "General",
      "description": "General knowledge and reference",
      "children": [
        {
          "code": "004",
          "name": "Computer Science",
          "description": "Computer science and programming",
          "children": []
        }
      ]
    }
  ]
}
```

---

### GET /classification/tree

Alternative endpoint for classification tree (same response).

---

## ML Classification Endpoints

### POST /taxonomy/classify/{resource_id}

Classify a resource using the fine-tuned ML model.

**Response (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Classification task enqueued",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Background Processing:**
1. Load ML model (lazy loading)
2. Extract resource content
3. Predict taxonomy categories with confidence scores
4. Filter predictions (confidence >= 0.3)
5. Store classifications
6. Flag low-confidence predictions (< 0.7) for review

---

### GET /taxonomy/active-learning/uncertain

Get resources with uncertain classifications for human review.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of samples (1-1000) | 100 |

**Response:**
```json
[
  {
    "resource_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Introduction to Neural Networks",
    "uncertainty_score": 0.87,
    "predicted_categories": [
      {
        "taxonomy_node_id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "Machine Learning",
        "confidence": 0.65
      }
    ]
  }
]
```

**Uncertainty Metrics:**
- **Entropy**: Prediction uncertainty across all classes
- **Margin**: Difference between top-2 predictions
- **Confidence**: Maximum probability

---

### POST /taxonomy/active-learning/feedback

Submit human classification feedback.

**Request Body:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "correct_taxonomy_ids": ["node_id_1", "node_id_2"]
}
```

**Response:**
```json
{
  "updated": true,
  "message": "Feedback recorded successfully",
  "manual_labels_count": 87,
  "retraining_threshold": 100,
  "retraining_recommended": false
}
```

---

### POST /taxonomy/train

Initiate ML model fine-tuning.

**Request Body:**
```json
{
  "labeled_data": [
    {
      "text": "Introduction to neural networks",
      "taxonomy_ids": ["node_id_1", "node_id_2"]
    }
  ],
  "unlabeled_texts": ["Article about CNNs..."],
  "epochs": 3,
  "batch_size": 16,
  "learning_rate": 2e-5
}
```

**Response (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Training task enqueued",
  "training_id": "990e8400-e29b-41d4-a716-446655440004",
  "labeled_examples": 150,
  "unlabeled_examples": 5000,
  "estimated_duration_minutes": 15
}
```

**Semi-Supervised Learning:**
- High-confidence predictions (>= 0.9) become pseudo-labels
- Enables effective training with <500 labeled examples

## Data Models

### Taxonomy Node Model

```json
{
  "id": "uuid",
  "name": "string",
  "slug": "string",
  "parent_id": "uuid or null",
  "level": "integer",
  "path": "string (materialized path)",
  "description": "string or null",
  "keywords": ["string"],
  "resource_count": "integer",
  "descendant_resource_count": "integer",
  "is_leaf": "boolean",
  "allow_resources": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Module Structure

The Taxonomy module is implemented as a self-contained vertical slice:

**Module**: `app.modules.taxonomy`  
**Router Prefix**: `/taxonomy`  
**Version**: 1.0.0

```python
from app.modules.taxonomy import (
    taxonomy_router,
    TaxonomyService,
    MLClassificationService,
    ClassificationService,
    TaxonomyNode,
    ClassificationResult
)
```

### Events

**Emitted Events:**
- `resource.classified` - When a resource is classified
- `taxonomy.node_created` - When a taxonomy node is added
- `taxonomy.model_trained` - When the ML model is retrained

**Subscribed Events:**
- `resource.created` - Triggers automatic classification

## Related Documentation

- [Resources API](resources.md) - Content management
- [Quality API](quality.md) - Quality assessment
- [Authority API](authority.md) - Subject authority
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors


<div style='page-break-after: always;'></div>

---



# 12. Graph API

*Source: `backend/docs/api/graph.md`*

---

﻿# Graph API

Knowledge graph and citation network endpoints for relationship exploration.

## Overview

The Graph API provides:
- Knowledge graph for resource relationships
- Citation network analysis
- Mind-map visualization data
- PageRank importance scoring

## Knowledge Graph Endpoints

### GET /graph/resource/{resource_id}/neighbors

Find related resources for mind-map visualization.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of neighbors (1-50) | 7 |

**Response:**
```json
{
  "nodes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Machine Learning Fundamentals",
      "type": "article",
      "classification_code": "004"
    }
  ],
  "edges": [
    {
      "source": "550e8400-e29b-41d4-a716-446655440000",
      "target": "550e8400-e29b-41d4-a716-446655440001",
      "weight": 0.76,
      "details": {
        "connection_type": "classification",
        "vector_similarity": 0.8,
        "shared_subjects": ["python", "programming"]
      }
    }
  ]
}
```

---

### GET /graph/overview

Get global relationship overview of strongest connections across the library.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of edges (1-200) | 50 |
| `vector_threshold` | float | Minimum vector similarity | 0.85 |

**Response:** Same structure as neighbors endpoint with `connection_type: "hybrid"`.

---

## Citation Network Endpoints

### GET /citations/resources/{resource_id}/citations

Retrieve all citations for a specific resource.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `direction` | string | `outbound`, `inbound`, or `both` | both |

**Response:**
```json
{
  "resource_id": "uuid",
  "outbound": [
    {
      "id": "uuid",
      "source_resource_id": "uuid",
      "target_url": "string",
      "target_resource_id": "uuid or null",
      "citation_type": "reference|dataset|code|general",
      "context_snippet": "string or null",
      "position": "integer or null",
      "importance_score": "float or null",
      "created_at": "datetime",
      "target_resource": {
        "id": "uuid",
        "title": "string",
        "source": "string"
      }
    }
  ],
  "inbound": [...],
  "counts": {
    "outbound": 5,
    "inbound": 3,
    "total": 8
  }
}
```

**Example:**
```bash
# Get all citations
curl "http://127.0.0.1:8000/citations/resources/{resource_id}/citations"

# Get only outbound citations
curl "http://127.0.0.1:8000/citations/resources/{resource_id}/citations?direction=outbound"
```

---

### GET /citations/graph/citations

Get citation network for visualization.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `resource_ids` | string[] | Filter to specific resources | - |
| `min_importance` | float | Minimum importance score (0.0-1.0) | 0.0 |
| `depth` | integer | Graph traversal depth (1-2) | 1 |

**Response:**
```json
{
  "nodes": [
    {
      "id": "uuid",
      "title": "string",
      "type": "source|cited|citing"
    }
  ],
  "edges": [
    {
      "source": "uuid",
      "target": "uuid",
      "type": "reference|dataset|code|general"
    }
  ]
}
```

**Performance Notes:**
- Results limited to 100 nodes maximum
- Depth capped at 2 to prevent exponential explosion

---

### POST /citations/resources/{resource_id}/citations/extract

Manually trigger citation extraction for a resource.

**Response (202 Accepted):**
```json
{
  "status": "queued",
  "resource_id": "uuid",
  "message": "Citation extraction queued for processing"
}
```

**Background Processing:**
1. Retrieve resource content from archive
2. Determine content type (HTML, PDF, Markdown)
3. Extract citations using appropriate parser
4. Classify citation types
5. Extract context snippets
6. Store citations and trigger resolution

---

### POST /citations/resolve

Trigger internal citation resolution to match URLs to existing resources.

**Response (202 Accepted):**
```json
{
  "status": "queued"
}
```

**Processing:**
- Queries citations with `target_resource_id = NULL`
- Normalizes URLs and matches to existing resources
- Processes in batches of 100

---

### POST /citations/importance/compute

Recompute PageRank importance scores for all citations.

**Response (202 Accepted):**
```json
{
  "status": "queued"
}
```

**Algorithm:**
- Damping factor: 0.85
- Max iterations: 100
- Convergence threshold: 1e-6
- Normalizes scores to [0, 1] range

**Performance:**
- Small graphs (<100 nodes): <1s
- Medium graphs (100-1000 nodes): <5s
- Large graphs (1000+ nodes): <30s

---

## Citation Type Classification

The system automatically classifies citations:

| Type | Indicators |
|------|------------|
| `dataset` | File extensions: `.csv`, `.json`, `.xml`, `.xlsx` |
| `code` | Domains: `github.com`, `gitlab.com`, `bitbucket.org` |
| `reference` | Domains: `doi.org`, `arxiv.org`, `scholar.google` |
| `general` | All other URLs |

## Data Models

### Graph Response Model

```json
{
  "nodes": [
    {
      "id": "uuid",
      "title": "string",
      "type": "string",
      "classification_code": "string"
    }
  ],
  "edges": [
    {
      "source": "uuid",
      "target": "uuid",
      "weight": "float (0.0-1.0)",
      "details": {
        "connection_type": "vector|subject|classification|hybrid",
        "vector_similarity": "float",
        "shared_subjects": ["string"],
        "classification_match": "boolean"
      }
    }
  ]
}
```

### Citation Model

```json
{
  "id": "uuid",
  "source_resource_id": "uuid",
  "target_resource_id": "uuid or null",
  "target_url": "string",
  "citation_type": "reference|dataset|code|general",
  "context_snippet": "string or null",
  "position": "integer or null",
  "importance_score": "float or null (0.0-1.0)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Integration Examples

### Periodic Citation Resolution

```bash
# Cron job (daily at 2 AM)
0 2 * * * curl -X POST http://127.0.0.1:8000/citations/resolve
```

### Periodic Importance Updates

```bash
# Cron job (weekly on Sunday at 3 AM)
0 3 * * 0 curl -X POST http://127.0.0.1:8000/citations/importance/compute
```

### Citation Network Visualization

```javascript
const response = await fetch(
  `/citations/graph/citations?resource_ids=${resourceId}&depth=2`
);
const graph = await response.json();
renderGraph(graph.nodes, graph.edges);
```

## Module Structure

The Graph module is implemented as a self-contained vertical slice:

**Module**: `app.modules.graph`  
**Router Prefix**: `/graph`, `/citations`, `/discovery`  
**Version**: 1.0.0

```python
from app.modules.graph import (
    graph_router,
    citations_router,
    discovery_router,
    GraphService,
    CitationService,
    LBDService,
    GraphEdge,
    Citation,
    DiscoveryHypothesis
)
```

### Events

**Emitted Events:**
- `citation.extracted` - When citations are extracted from a resource
- `graph.updated` - When the knowledge graph is updated
- `hypothesis.discovered` - When a new discovery hypothesis is generated

**Subscribed Events:**
- `resource.created` - Extracts citations and updates graph
- `resource.deleted` - Removes resource from graph

## Related Documentation

- [Resources API](resources.md) - Content management
- [Search API](search.md) - Discovery features
- [Recommendations API](recommendations.md) - Related content
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors


<div style='page-break-after: always;'></div>

---



# 13. Recommendations API

*Source: `backend/docs/api/recommendations.md`*

---

﻿# Recommendations API

Personalized content recommendation endpoints using hybrid strategies.

## Overview

The Recommendations API provides:
- Multi-strategy recommendations (collaborative, content, graph)
- User profile learning from interactions
- Diversity optimization with MMR
- Novelty promotion for discovery
- Cold start handling for new users

## Endpoints

### GET /recommendations

Get personalized content recommendations based on library content.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of recommendations (1-100) | 10 |

**Response:**
```json
{
  "items": [
    {
      "url": "https://example.com/new-ml-article",
      "title": "Latest Advances in Machine Learning",
      "snippet": "Recent developments in ML algorithms",
      "relevance_score": 0.85,
      "reasoning": ["Aligned with Machine Learning, Python"]
    }
  ]
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/recommendations?limit=5"
```

---

### GET /api/recommendations

Get personalized recommendations using hybrid strategy (Phase 11).

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of recommendations (1-100) | 20 |
| `strategy` | string | Recommendation strategy | hybrid |
| `diversity` | float | Diversity preference (0.0-1.0) | user profile |
| `min_quality` | float | Minimum quality threshold (0.0-1.0) | 0.0 |

**Strategy Options:**
- `collaborative` - Neural Collaborative Filtering (requires ≥5 interactions)
- `content` - Content-based similarity only
- `graph` - Graph-based relationships only
- `hybrid` - Combines all strategies (default)

**Response:**
```json
{
  "recommendations": [
    {
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Advanced Machine Learning Techniques",
      "description": "Comprehensive guide to modern ML algorithms",
      "score": 0.87,
      "strategy": "hybrid",
      "scores": {
        "collaborative": 0.92,
        "content": 0.85,
        "graph": 0.78,
        "quality": 0.88,
        "recency": 0.65
      },
      "rank": 1,
      "novelty_score": 0.42,
      "source": "https://example.com/ml-guide",
      "classification_code": "004",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "metadata": {
    "total": 20,
    "strategy": "hybrid",
    "diversity_applied": true,
    "gini_coefficient": 0.24,
    "user_interactions": 47,
    "cold_start": false
  }
}
```

**Hybrid Scoring Formula:**
```
hybrid_score = 
  0.35 * collaborative_score +
  0.30 * content_score +
  0.20 * graph_score +
  0.10 * quality_score +
  0.05 * recency_score
```

**Performance:**
- Target latency: <200ms for 20 recommendations
- Cache hit rate: >80% for user embeddings

**Cold Start Behavior:**
- Users with <5 interactions: Uses content + graph strategies only
- Collaborative filtering enabled after 5+ interactions

---

### POST /api/interactions

Track user-resource interactions for personalized learning.

**Request Body:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "interaction_type": "view",
  "dwell_time": 45,
  "scroll_depth": 0.8,
  "session_id": "session_abc123"
}
```

**Interaction Types:**

| Type | Strength | Description |
|------|----------|-------------|
| `view` | 0.1-0.5 | Based on dwell time and scroll depth |
| `annotation` | 0.7 | User annotated the resource |
| `collection_add` | 0.8 | User added to collection |
| `export` | 0.9 | User exported the resource |
| `rating` | varies | Based on rating value |

**Response (201 Created):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "user123",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "interaction_type": "view",
  "interaction_strength": 0.42,
  "is_positive": true,
  "confidence": 0.85,
  "dwell_time": 45,
  "scroll_depth": 0.8,
  "return_visits": 1,
  "interaction_timestamp": "2024-01-15T14:30:00Z"
}
```

## Features

### Multi-Strategy Recommendations

The hybrid engine combines multiple strategies:

1. **Collaborative Filtering (NCF)**
   - Learns from user interaction patterns
   - Requires ≥5 interactions to activate
   - Uses neural network for user-item embeddings

2. **Content-Based Similarity**
   - Uses resource embeddings for semantic similarity
   - Works immediately for new users
   - Based on resource metadata and content

3. **Graph-Based Discovery**
   - Leverages knowledge graph relationships
   - Finds resources through citation networks
   - Discovers related topics through classification

### Diversity Optimization

Uses Maximal Marginal Relevance (MMR) to:
- Prevent filter bubbles
- Balance relevance with diversity
- Surface varied content types

### Novelty Promotion

Surfaces lesser-known but relevant resources:
- Tracks resource popularity
- Boosts underexposed quality content
- Balances popular vs. niche recommendations

## Data Models

### Recommendation Response Model

```json
{
  "items": [
    {
      "url": "string",
      "title": "string",
      "snippet": "string",
      "relevance_score": "float (0.0-1.0)",
      "reasoning": ["string"]
    }
  ]
}
```

### Interaction Model

```json
{
  "id": "uuid",
  "user_id": "string",
  "resource_id": "uuid",
  "interaction_type": "view|annotation|collection_add|export|rating",
  "interaction_strength": "float (0.0-1.0)",
  "is_positive": "boolean",
  "confidence": "float (0.0-1.0)",
  "dwell_time": "integer (seconds)",
  "scroll_depth": "float (0.0-1.0)",
  "return_visits": "integer",
  "interaction_timestamp": "datetime"
}
```

## Module Structure

The Recommendations module is implemented as a self-contained vertical slice:

**Module**: `app.modules.recommendations`  
**Router Prefix**: `/recommendations`  
**Version**: 1.0.0

```python
from app.modules.recommendations import (
    recommendations_router,
    RecommendationService,
    HybridRecommendationService,
    CollaborativeFilteringService,
    NCFService,
    UserProfileService,
    RecommendationRequest,
    RecommendationResponse
)
```

### Events

**Emitted Events:**
- `recommendation.generated` - When recommendations are generated
- `user.profile_updated` - When user profile is updated
- `interaction.recorded` - When user interaction is recorded

**Subscribed Events:**
- `annotation.created` - Updates user profile
- `collection.resource_added` - Updates user profile

## Related Documentation

- [Resources API](resources.md) - Content management
- [Search API](search.md) - Discovery features
- [Graph API](graph.md) - Knowledge graph
- [Collections API](collections.md) - Collection recommendations
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors


<div style='page-break-after: always;'></div>

---



# 14. Quality API

*Source: `backend/docs/api/quality.md`*

---

﻿# Quality API

Multi-dimensional quality assessment endpoints for resource evaluation.

## Overview

The Quality API provides:
- Multi-dimensional quality scoring (accuracy, completeness, consistency, timeliness, relevance)
- Quality outlier detection using Isolation Forest
- Quality degradation monitoring over time
- Summary quality evaluation (G-Eval, FineSurE, BERTScore)
- Quality distribution analytics and trends

## Endpoints

### GET /resources/{id}/quality-details

Retrieve full quality dimension breakdown for a resource.

**Response (200 OK):**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "quality_dimensions": {
    "accuracy": 0.75,
    "completeness": 0.82,
    "consistency": 0.88,
    "timeliness": 0.65,
    "relevance": 0.79
  },
  "quality_overall": 0.77,
  "quality_weights": {
    "accuracy": 0.30,
    "completeness": 0.25,
    "consistency": 0.20,
    "timeliness": 0.15,
    "relevance": 0.10
  },
  "quality_last_computed": "2025-11-10T12:00:00Z",
  "quality_computation_version": "v2.0",
  "is_quality_outlier": false,
  "outlier_score": null,
  "outlier_reasons": null,
  "needs_quality_review": false
}
```

**Quality Dimensions:**
- **Accuracy (0.0-1.0)**: Citation validity, source credibility, scholarly metadata
- **Completeness (0.0-1.0)**: Metadata coverage, content depth, multi-modal content
- **Consistency (0.0-1.0)**: Title-content alignment, internal coherence
- **Timeliness (0.0-1.0)**: Publication recency, content freshness
- **Relevance (0.0-1.0)**: Classification confidence, citation count

---

### POST /quality/recalculate

Trigger quality recomputation with optional custom weights.

**Request Body:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "weights": {
    "accuracy": 0.35,
    "completeness": 0.25,
    "consistency": 0.20,
    "timeliness": 0.10,
    "relevance": 0.10
  }
}
```

**Note:** Provide either `resource_id` or `resource_ids` (array), not both. Weights must sum to 1.0.

**Response (202 Accepted):**
```json
{
  "status": "queued",
  "message": "Quality computation queued for background processing"
}
```

---

### GET /quality/outliers

Retrieve paginated list of detected quality outliers.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `page` | integer | Page number | 1 |
| `limit` | integer | Results per page (1-100) | 50 |
| `min_outlier_score` | float | Minimum anomaly score (-1.0 to 1.0) | null |
| `reason` | string | Filter by outlier reason | null |

**Outlier Reasons:**
- `low_accuracy`, `low_completeness`, `low_consistency`, `low_timeliness`, `low_relevance`
- `low_summary_coherence`, `low_summary_consistency`, `low_summary_fluency`, `low_summary_relevance`

**Response:**
```json
{
  "total": 42,
  "page": 1,
  "limit": 50,
  "outliers": [
    {
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Resource Title",
      "quality_overall": 0.35,
      "outlier_score": -0.82,
      "outlier_reasons": ["low_accuracy", "low_completeness"],
      "needs_quality_review": true,
      "quality_last_computed": "2025-11-10T12:00:00Z"
    }
  ]
}
```

**Outlier Score Interpretation:**
- Lower scores indicate higher anomaly likelihood
- Scores < -0.5 are typically significant outliers
- Uses Isolation Forest with contamination=0.1

---

### GET /quality/degradation

Monitor quality degradation over time.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `time_window_days` | integer | Lookback period in days | 30 |

**Response:**
```json
{
  "time_window_days": 30,
  "degraded_count": 15,
  "degraded_resources": [
    {
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Resource Title",
      "old_quality": 0.85,
      "new_quality": 0.62,
      "degradation_pct": 27.1,
      "quality_last_computed": "2025-10-15T12:00:00Z"
    }
  ]
}
```

**Detection:** Flags resources with >20% quality drop.

---

### POST /summaries/{id}/evaluate

Trigger summary quality evaluation using G-Eval, FineSurE, and BERTScore.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `use_g_eval` | boolean | Use GPT-4 for G-Eval metrics | false |

**Response (202 Accepted):**
```json
{
  "status": "queued",
  "message": "Summary evaluation queued for background processing"
}
```

**Evaluation Metrics:**
- **G-Eval (optional)**: Coherence, consistency, fluency, relevance (1-5 scale)
- **FineSurE**: Completeness and conciseness (0.0-1.0)
- **BERTScore**: Semantic similarity F1 score (0.0-1.0)

**Performance:**
- Without G-Eval: <2 seconds per resource
- With G-Eval: <10 seconds per resource

---

### GET /quality/distribution

Retrieve quality score distribution histogram.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `bins` | integer | Number of histogram bins (1-50) | 10 |
| `dimension` | string | Dimension or "overall" | overall |

**Response:**
```json
{
  "dimension": "overall",
  "bins": 10,
  "distribution": [
    {"range": "0.0-0.1", "count": 5},
    {"range": "0.1-0.2", "count": 12},
    ...
  ],
  "statistics": {
    "mean": 0.65,
    "median": 0.68,
    "std_dev": 0.18,
    "min": 0.12,
    "max": 0.98,
    "total_resources": 494
  }
}
```

---

### GET /quality/trends

Retrieve quality trends over time.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `granularity` | string | daily, weekly, monthly | weekly |
| `start_date` | date | Start of range (ISO 8601) | 90 days ago |
| `end_date` | date | End of range (ISO 8601) | today |
| `dimension` | string | Dimension or "overall" | overall |

**Response:**
```json
{
  "dimension": "overall",
  "granularity": "weekly",
  "data_points": [
    {
      "period": "2025-W31",
      "avg_quality": 0.72,
      "resource_count": 145,
      "date": "2025-08-03"
    }
  ]
}
```

---

### GET /quality/dimensions

Retrieve average scores per dimension across all resources.

**Response:**
```json
{
  "dimensions": {
    "accuracy": {"avg": 0.75, "min": 0.12, "max": 0.98, "std_dev": 0.15},
    "completeness": {"avg": 0.68, "min": 0.25, "max": 0.95, "std_dev": 0.18},
    ...
  },
  "overall": {"avg": 0.71, "min": 0.28, "max": 0.96, "std_dev": 0.16},
  "total_resources": 1247
}
```

---

### GET /quality/review-queue

Retrieve resources flagged for quality review.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `page` | integer | Page number | 1 |
| `limit` | integer | Results per page (1-100) | 50 |
| `sort_by` | string | outlier_score, quality_overall, updated_at | outlier_score |

---

## Curation Endpoints

### GET /curation/review-queue

Access low-quality items for review and curation.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `threshold` | float | Quality threshold | null |
| `include_unread_only` | boolean | Include only unread | false |
| `limit` | integer | Number of items (1-100) | 25 |
| `offset` | integer | Results to skip | 0 |

---

### GET /curation/low-quality

Get resources with quality scores below threshold.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `threshold` | float | Quality threshold (0.0-1.0) | 0.5 |
| `limit` | integer | Number of items (1-100) | 25 |

---

### GET /curation/quality-analysis/{resource_id}

Get detailed quality analysis for a specific resource.

**Response:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "metadata_completeness": 0.8,
  "readability": {
    "flesch_kincaid": 12.5,
    "gunning_fog": 14.2,
    "automated_readability": 11.8
  },
  "source_credibility": 0.7,
  "content_depth": 0.6,
  "overall_quality": 0.7,
  "quality_level": "good",
  "suggestions": [
    "Improve metadata completeness",
    "Add more detailed description"
  ]
}
```

---

### POST /curation/batch-update

Apply partial updates to multiple resources.

**Request Body:**
```json
{
  "resource_ids": ["uuid1", "uuid2"],
  "updates": {
    "read_status": "in_progress",
    "subject": ["Updated", "Tags"]
  }
}
```

---

### POST /curation/bulk-quality-check

Perform quality analysis on multiple resources.

**Request Body:**
```json
{
  "resource_ids": ["uuid1", "uuid2"]
}
```

## Quality Dimension Algorithms

**Accuracy:**
```
accuracy = 0.5 (baseline)
  + 0.20 * (valid_citations / total_citations)
  + 0.15 * (1 if credible_domain else 0)
  + 0.15 * (1 if has_academic_identifier else 0)
  + 0.10 * (1 if has_authors else 0)
```

**Completeness:**
```
completeness = 
  0.30 * (filled_required_fields / 3)
  + 0.30 * (filled_important_fields / 4)
  + 0.20 * (filled_scholarly_fields / 4)
  + 0.20 * (multimodal_content_score / 3)
```

**Timeliness:**
```
age_years = current_year - publication_year
recency_score = max(0.0, 1.0 - (age_years / 20))
timeliness = recency_score + (0.1 if ingested_within_30_days else 0)
```

## Module Structure

The Quality module is implemented as a self-contained vertical slice:

**Module**: `app.modules.quality`  
**Router Prefix**: `/quality`  
**Version**: 1.0.0

```python
from app.modules.quality import (
    quality_router,
    QualityService,
    SummarizationEvaluator,
    QualityDimensions,
    QualityResponse,
    OutlierReport
)
```

### Events

**Emitted Events:**
- `quality.computed` - When quality scores are calculated
- `quality.outlier_detected` - When anomalous quality is found
- `quality.degradation_detected` - When quality degrades over time

**Subscribed Events:**
- `resource.created` - Triggers initial quality computation
- `resource.updated` - Recomputes quality on changes

## Related Documentation

- [Resources API](resources.md) - Content management
- [Taxonomy API](taxonomy.md) - Classification
- [Curation API](curation.md) - Content review
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors


<div style='page-break-after: always;'></div>

---



# 15. Scholarly API

*Source: `backend/docs/api/scholarly.md`*

---

# Scholarly API

## Overview

The Scholarly module provides academic metadata extraction from resources, including equations, tables, citations, and scholarly metadata.

**Module**: `app.modules.scholarly`  
**Router Prefix**: `/scholarly`  
**Version**: 1.0.0

## Endpoints

### Extract Metadata

Extract scholarly metadata from a resource.

```http
POST /scholarly/extract/{resource_id}
```

**Path Parameters:**
- `resource_id` (integer, required) - Resource ID

**Response:**
```json
{
  "resource_id": 1,
  "equations": [
    {
      "id": 1,
      "latex": "E = mc^2",
      "context": "Einstein's mass-energy equivalence"
    }
  ],
  "tables": [
    {
      "id": 1,
      "caption": "Experimental Results",
      "data": {...}
    }
  ],
  "metadata": {
    "authors": ["John Doe"],
    "publication_date": "2024-01-01",
    "journal": "Nature",
    "doi": "10.1234/example"
  }
}
```

### Get Resource Metadata

Get scholarly metadata for a resource.

```http
GET /scholarly/resources/{resource_id}/metadata
```

**Path Parameters:**
- `resource_id` (integer, required) - Resource ID

**Response:**
```json
{
  "resource_id": 1,
  "authors": ["John Doe", "Jane Smith"],
  "publication_date": "2024-01-01",
  "journal": "Nature",
  "volume": "123",
  "issue": "4",
  "pages": "567-890",
  "doi": "10.1234/example",
  "abstract": "This paper presents..."
}
```

### Get Equations

Get all equations extracted from a resource.

```http
GET /scholarly/resources/{resource_id}/equations
```

**Path Parameters:**
- `resource_id` (integer, required) - Resource ID

**Response:**
```json
{
  "equations": [
    {
      "id": 1,
      "latex": "E = mc^2",
      "context": "Einstein's mass-energy equivalence",
      "position": 42
    }
  ]
}
```

### Get Tables

Get all tables extracted from a resource.

```http
GET /scholarly/resources/{resource_id}/tables
```

**Path Parameters:**
- `resource_id` (integer, required) - Resource ID

**Response:**
```json
{
  "tables": [
    {
      "id": 1,
      "caption": "Experimental Results",
      "headers": ["Condition", "Result", "P-value"],
      "rows": [
        ["Control", "0.5", "0.001"],
        ["Treatment", "0.8", "0.001"]
      ]
    }
  ]
}
```

### Health Check

Check module health status.

```http
GET /scholarly/health
```

**Response:**
```json
{
  "status": "healthy",
  "module": "scholarly",
  "version": "1.0.0"
}
```

## Events

### Emitted Events

- `metadata.extracted` - When scholarly metadata is extracted
- `equations.parsed` - When equations are parsed from content
- `tables.extracted` - When tables are extracted from content

### Subscribed Events

- `resource.created` - Triggers automatic metadata extraction

## Module Structure

```python
from app.modules.scholarly import (
    scholarly_router,
    MetadataExtractor,
    ScholarlyMetadata,
    Equation,
    Table
)
```

## Related Documentation

- [Architecture: Modules](../architecture/modules.md)
- [Architecture: Events](../architecture/events.md)
- [Resources API](resources.md)


<div style='page-break-after: always;'></div>

---



# 16. Authority API

*Source: `backend/docs/api/authority.md`*

---

# Authority API

## Overview

The Authority module manages subject authority files and classification trees, providing controlled vocabularies for resource organization.

**Module**: `app.modules.authority`  
**Router Prefix**: `/authority`  
**Version**: 1.0.0

## Endpoints

### Get Subject Suggestions

Get subject heading suggestions based on input text.

```http
GET /authority/subjects/suggest?q={query}&limit={limit}
```

**Query Parameters:**
- `q` (string, required) - Search query
- `limit` (integer, optional) - Maximum results (default: 10)

**Response:**
```json
{
  "suggestions": [
    {
      "heading": "Machine Learning",
      "code": "006.31",
      "confidence": 0.95,
      "broader_terms": ["Artificial Intelligence"],
      "narrower_terms": ["Deep Learning", "Neural Networks"]
    }
  ]
}
```

### Get Classification Tree

Get the complete classification tree or a subtree.

```http
GET /authority/classification/tree?root={code}&depth={depth}
```

**Query Parameters:**
- `root` (string, optional) - Root classification code (default: top level)
- `depth` (integer, optional) - Tree depth (default: unlimited)

**Response:**
```json
{
  "tree": {
    "code": "000",
    "label": "Computer Science",
    "children": [
      {
        "code": "006",
        "label": "Special Computer Methods",
        "children": [
          {
            "code": "006.3",
            "label": "Artificial Intelligence",
            "children": []
          }
        ]
      }
    ]
  }
}
```

### Health Check

Check module health status.

```http
GET /authority/health
```

**Response:**
```json
{
  "status": "healthy",
  "module": "authority",
  "version": "1.0.0"
}
```

## Module Structure

```python
from app.modules.authority import (
    authority_router,
    AuthorityService,
    SubjectHeading,
    ClassificationNode
)
```

## Related Documentation

- [Architecture: Modules](../architecture/modules.md)
- [Taxonomy API](taxonomy.md)
- [Resources API](resources.md)


<div style='page-break-after: always;'></div>

---



# 17. Curation API

*Source: `backend/docs/api/curation.md`*

---

# Curation API

## Overview

The Curation module provides content review workflows and batch operations for managing resource quality and organization.

**Module**: `app.modules.curation`  
**Router Prefix**: `/curation`  
**Version**: 1.0.0

## Endpoints

### Get Review Queue

Get resources pending review.

```http
GET /curation/review-queue?status={status}&limit={limit}&offset={offset}
```

**Query Parameters:**
- `status` (string, optional) - Filter by status: `pending`, `approved`, `rejected`
- `limit` (integer, optional) - Results per page (default: 25)
- `offset` (integer, optional) - Pagination offset (default: 0)

**Response:**
```json
{
  "items": [
    {
      "resource_id": 1,
      "title": "Example Resource",
      "status": "pending",
      "quality_score": 0.45,
      "flagged_reason": "Low quality score",
      "added_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 42
}
```

### Review Resource

Submit a review decision for a resource.

```http
POST /curation/review/{resource_id}
```

**Path Parameters:**
- `resource_id` (integer, required) - Resource ID

**Request Body:**
```json
{
  "decision": "approved",
  "notes": "High quality content, well-structured",
  "tags": ["verified", "high-quality"]
}
```

**Response:**
```json
{
  "resource_id": 1,
  "decision": "approved",
  "reviewed_by": "curator@example.com",
  "reviewed_at": "2024-01-01T00:00:00Z"
}
```

### Batch Update

Perform batch operations on multiple resources.

```http
POST /curation/batch
```

**Request Body:**
```json
{
  "resource_ids": [1, 2, 3],
  "operation": "add_tags",
  "parameters": {
    "tags": ["reviewed", "approved"]
  }
}
```

**Supported Operations:**
- `add_tags` - Add tags to resources
- `remove_tags` - Remove tags from resources
- `update_classification` - Update classification
- `approve` - Approve resources
- `reject` - Reject resources

**Response:**
```json
{
  "success": 3,
  "failed": 0,
  "results": [
    {
      "resource_id": 1,
      "status": "success"
    }
  ]
}
```

### Get Curation Stats

Get curation statistics.

```http
GET /curation/stats
```

**Response:**
```json
{
  "pending": 42,
  "approved": 1234,
  "rejected": 56,
  "total_reviewed": 1290,
  "avg_review_time_hours": 2.5
}
```

### Health Check

Check module health status.

```http
GET /curation/health
```

**Response:**
```json
{
  "status": "healthy",
  "module": "curation",
  "version": "1.0.0"
}
```

## Events

### Emitted Events

- `curation.reviewed` - When a resource is reviewed
- `curation.approved` - When a resource is approved
- `curation.rejected` - When a resource is rejected

### Subscribed Events

- `quality.outlier_detected` - Adds resources to review queue

## Module Structure

```python
from app.modules.curation import (
    curation_router,
    CurationService,
    ReviewDecision,
    BatchOperation
)
```

## Related Documentation

- [Architecture: Modules](../architecture/modules.md)
- [Architecture: Events](../architecture/events.md)
- [Quality API](quality.md)
- [Resources API](resources.md)


<div style='page-break-after: always;'></div>

---



# 18. Monitoring API

*Source: `backend/docs/api/monitoring.md`*

---

﻿# Monitoring API

System monitoring, health checks, and metrics endpoints.

## Overview

The Monitoring API provides:
- Health check endpoints for load balancers
- System metrics and statistics
- Database connection monitoring
- Service status information

## Endpoints

### GET /health

Basic health check endpoint for load balancers and orchestration systems.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "timestamp": "2024-01-01T10:00:00Z",
  "error": "Database connection failed"
}
```

**Use Cases:**
- Kubernetes liveness probes
- Load balancer health checks
- Uptime monitoring

**Example:**
```bash
curl http://127.0.0.1:8000/health
```

---

### GET /monitoring/status

Detailed system status with component health information.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "0.9.0",
  "uptime_seconds": 86400,
  "components": {
    "database": {
      "status": "healthy",
      "type": "postgresql",
      "connection_pool": {
        "size": 10,
        "available": 8,
        "in_use": 2
      }
    },
    "cache": {
      "status": "healthy",
      "type": "redis",
      "connected": true
    },
    "ml_models": {
      "status": "healthy",
      "embedding_model": "loaded",
      "classification_model": "loaded"
    }
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**Example:**
```bash
curl http://127.0.0.1:8000/monitoring/status
```

---

### GET /monitoring/metrics

System metrics and statistics.

**Response (200 OK):**
```json
{
  "resources": {
    "total": 10000,
    "by_status": {
      "completed": 9500,
      "pending": 300,
      "failed": 200
    },
    "by_type": {
      "article": 6000,
      "paper": 3000,
      "book": 1000
    }
  },
  "collections": {
    "total": 500,
    "by_visibility": {
      "private": 300,
      "public": 150,
      "shared": 50
    }
  },
  "annotations": {
    "total": 25000,
    "by_user_count": 150
  },
  "search": {
    "queries_last_hour": 1500,
    "avg_latency_ms": 145
  },
  "quality": {
    "avg_score": 0.72,
    "outliers_count": 42,
    "review_queue_size": 87
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**Example:**
```bash
curl http://127.0.0.1:8000/monitoring/metrics
```

---

### GET /monitoring/database

Database-specific monitoring information.

**Response (200 OK):**
```json
{
  "type": "postgresql",
  "version": "15.2",
  "connection": {
    "status": "connected",
    "pool_size": 10,
    "active_connections": 3,
    "idle_connections": 7
  },
  "tables": {
    "resources": {
      "row_count": 10000,
      "size_mb": 256
    },
    "annotations": {
      "row_count": 25000,
      "size_mb": 64
    },
    "collections": {
      "row_count": 500,
      "size_mb": 8
    }
  },
  "indexes": {
    "total": 45,
    "size_mb": 128
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

---

## Integration Examples

### Kubernetes Liveness Probe

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### Kubernetes Readiness Probe

```yaml
readinessProbe:
  httpGet:
    path: /monitoring/status
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

### Prometheus Metrics (Planned)

Future releases will expose Prometheus-compatible metrics at `/metrics`:

```
# HELP neo_alexandria_resources_total Total number of resources
# TYPE neo_alexandria_resources_total gauge
neo_alexandria_resources_total 10000

# HELP neo_alexandria_search_latency_seconds Search latency histogram
# TYPE neo_alexandria_search_latency_seconds histogram
neo_alexandria_search_latency_seconds_bucket{le="0.1"} 500
neo_alexandria_search_latency_seconds_bucket{le="0.2"} 1200
```

### Alerting Rules (Example)

```yaml
groups:
  - name: neo-alexandria
    rules:
      - alert: HighSearchLatency
        expr: neo_alexandria_search_latency_seconds > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High search latency detected"
          
      - alert: DatabaseConnectionPoolExhausted
        expr: neo_alexandria_db_pool_available == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool exhausted"
```

## Health Check Best Practices

1. **Use `/health` for simple checks** - Fast, lightweight, suitable for frequent polling
2. **Use `/monitoring/status` for detailed checks** - More comprehensive, use for debugging
3. **Set appropriate timeouts** - Health checks should respond within 5 seconds
4. **Monitor trends** - Track metrics over time to identify degradation

## Module Structure

The Monitoring module is implemented as a self-contained vertical slice:

**Module**: `app.modules.monitoring`  
**Router Prefix**: `/monitoring`, `/health`  
**Version**: 1.0.0

```python
from app.modules.monitoring import (
    monitoring_router,
    MonitoringService,
    HealthStatus,
    SystemMetrics
)
```

### Events

**Emitted Events:**
- None (Monitoring is a read-only aggregation module)

**Subscribed Events:**
- All events (for metrics aggregation)

## Related Documentation

- [API Overview](overview.md) - Authentication, errors
- [Architecture Overview](../architecture/overview.md) - System design
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [Deployment Guide](../guides/deployment.md) - Production setup


<div style='page-break-after: always;'></div>

---



# 19. Architecture Overview

*Source: `backend/docs/architecture/overview.md`*

---

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

### High-Level Modular Structure (Phase 14 - Complete)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    NEO ALEXANDRIA 2.0 - COMPLETE MODULAR ARCHITECTURE                   │
│                              (13 Vertical Slice Modules)                                │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │                         FastAPI Application (main.py)                            │   │
│  │                    Registers all module routers & event handlers                 │   │
│  └────────────────────────────────────┬─────────────────────────────────────────────┘   │
│                                       │                                                 │
│                                       │ Module Registration                             │
│                                       │                                                 │
│       ┌───────────────────────────────┼───────────────────────────────────┐             │
│       │                               │                                   │             │
│       ▼                               ▼                                   ▼             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Resources │  │Collections│ │  Search  │  │Annotations│ │ Scholarly│  │ Authority│     │
│  │  Module  │  │  Module  │  │  Module  │  │  Module  │  │  Module  │  │  Module  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │             │             │             │             │           │
│       │             │             │             │             │             │           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Curation │  │  Quality │  │ Taxonomy │  │  Graph   │  │Recommend-│  │Monitoring│     │
│  │  Module  │  │  Module  │  │  Module  │  │  Module  │  │ ations   │  │  Module  │     │
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

### Module Summary (13 Modules)

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


<div style='page-break-after: always;'></div>

---



# 20. Database Architecture

*Source: `backend/docs/architecture/database.md`*

---

# Database Architecture

Database schema, models, and migration strategies for Neo Alexandria 2.0.

## Database Support

Neo Alexandria supports both SQLite and PostgreSQL with automatic detection.

### SQLite (Development)

```bash
DATABASE_URL=sqlite:///./backend.db
```

**Use Cases:**
- Local development and prototyping
- Single-user deployments
- Testing and CI/CD pipelines
- Small datasets (<10,000 resources)

**Advantages:**
- Zero configuration
- File-based (portable)
- No separate server needed

**Limitations:**
- Single writer (limited concurrency)
- No advanced indexing (GIN, JSONB)

### PostgreSQL (Production)

```bash
DATABASE_URL=postgresql://user:password@host:5432/database
```

**Use Cases:**
- Production deployments
- Multi-user environments
- High concurrency (100+ users)
- Large datasets (>10,000 resources)

**Advantages:**
- Excellent concurrent write performance
- Advanced indexing (GIN for JSONB)
- Native JSONB support
- Connection pooling

---

## Database Model Hierarchy

```
                    ┌─────────────────────┐
                    │   SQLAlchemy Base   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┬────────────────┐
              │                │                │                │
    ┌─────────▼────────┐  ┌───▼──────────┐  ┌─▼──────────┐  ┌──▼─────────┐
    │    Resource      │  │ TaxonomyNode │  │ Collection │  │ Annotation │
    ├──────────────────┤  ├──────────────┤  ├────────────┤  ├────────────┤
    │ • id: UUID       │  │ • id: UUID   │  │ • id: UUID │  │ • id: UUID │
    │ • title: str     │  │ • code: str  │  │ • name     │  │ • content  │
    │ • description    │  │ • name: str  │  │ • owner_id │  │ • user_id  │
    │ • creator        │  │ • parent_id  │  │ • public   │  │ • type     │
    │ • subject: JSON  │  │ • level: int │  └────────────┘  └────────────┘
    │ • type           │  └──────────────┘
    │ • language       │         │
    │ • identifier     │         │ self-referential
    │ • doi            │         ▼
    │ • embedding      │  ┌──────────────┐
    │ • created_at     │  │   children   │
    │ • updated_at     │  │  (List[Node])│
    └──────────────────┘  └──────────────┘
            │
            │ one-to-many
            ▼
    ┌──────────────────┐
    │ ResourceTaxonomy │
    ├──────────────────┤
    │ • resource_id    │
    │ • taxonomy_id    │
    │ • confidence     │
    │ • method         │
    └──────────────────┘
```

---

## Core Schema

### Resource Model

```
┌──────────────────────────────────────────────────────────────────┐
│                         Resource                                 │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                    │
│ title: String (required)                                         │
│ description: Text                                                │
│ creator: String                                                  │
│ publisher: String                                                │
│ source: String (URL)                                             │
│ language: String                                                 │
│ type: String                                                     │
│ subject: JSON (array of strings)                                 │
│ classification_code: String                                      │
│ quality_score: Float (0.0-1.0)                                   │
│ read_status: Enum (unread, in_progress, completed, archived)     │
│ embedding: JSON (vector array)                                   │
│ created_at: DateTime                                             │
│ updated_at: DateTime                                             │
└──────────────────────────────────────────────────────────────────┘
```

### Collection Model

```
┌──────────────────────────────────────────────────────────────────┐
│                         Collection                               │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                    │
│ name: String (1-255 chars)                                       │
│ description: Text (max 2000 chars)                               │
│ owner_id: String (indexed)                                       │
│ visibility: Enum (private, shared, public)                       │
│ parent_id: UUID (FK → Collection, nullable)                      │
│ embedding: JSON (aggregate vector)                               │
│ created_at: DateTime                                             │
│ updated_at: DateTime                                             │
└──────────────────────────────────────────────────────────────────┘
```

### Annotation Model

```
┌──────────────────────────────────────────────────────────────────┐
│                         Annotation                               │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                    │
│ resource_id: UUID (FK → Resource)                                │
│ user_id: String                                                  │
│ start_offset: Integer                                            │
│ end_offset: Integer                                              │
│ highlighted_text: Text                                           │
│ note: Text (max 10,000 chars)                                    │
│ tags: JSON (array, max 20)                                       │
│ color: String (hex)                                              │
│ embedding: JSON (384-dim vector)                                 │
│ is_shared: Boolean                                               │
│ created_at: DateTime                                             │
│ updated_at: DateTime                                             │
└──────────────────────────────────────────────────────────────────┘
```

### Taxonomy Node Model

```
┌──────────────────────────────────────────────────────────────────┐
│                       TaxonomyNode                               │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                    │
│ name: String                                                     │
│ slug: String (unique)                                            │
│ parent_id: UUID (FK → TaxonomyNode, nullable)                    │
│ level: Integer                                                   │
│ path: String (materialized path)                                 │
│ description: Text                                                │
│ keywords: JSON (array)                                           │
│ resource_count: Integer                                          │
│ descendant_resource_count: Integer                               │
│ is_leaf: Boolean                                                 │
│ allow_resources: Boolean                                         │
│ created_at: DateTime                                             │
│ updated_at: DateTime                                             │
└──────────────────────────────────────────────────────────────────┘
```

### Citation Model

```
┌──────────────────────────────────────────────────────────────────┐
│                         Citation                                 │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                    │
│ source_resource_id: UUID (FK → Resource)                         │
│ target_resource_id: UUID (FK → Resource)                         │
│ citation_type: String (cites, cited_by, related)                 │
│ context: Text (surrounding text)                                 │
│ confidence: Float (0.0-1.0)                                      │
│ created_at: DateTime                                             │
└──────────────────────────────────────────────────────────────────┘
```

### User Interaction Model

```
┌──────────────────────────────────────────────────────────────────┐
│                      UserInteraction                             │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                    │
│ user_id: String (indexed)                                        │
│ resource_id: UUID (FK → Resource)                                │
│ interaction_type: String (view, bookmark, rate, download)        │
│ rating: Integer (1-5, nullable)                                  │
│ duration_seconds: Integer (nullable)                             │
│ metadata: JSON                                                   │
│ created_at: DateTime                                             │
└──────────────────────────────────────────────────────────────────┘
```

---

## Association Tables

### Collection-Resource Association

```sql
CREATE TABLE collection_resources (
    collection_id UUID REFERENCES collections(id) ON DELETE CASCADE,
    resource_id UUID REFERENCES resources(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (collection_id, resource_id)
);

CREATE INDEX idx_collection_resources_collection ON collection_resources(collection_id);
CREATE INDEX idx_collection_resources_resource ON collection_resources(resource_id);
```

### Resource-Taxonomy Association

```sql
CREATE TABLE resource_taxonomy (
    resource_id UUID REFERENCES resources(id) ON DELETE CASCADE,
    taxonomy_id UUID REFERENCES taxonomy_nodes(id) ON DELETE CASCADE,
    confidence FLOAT,
    is_predicted BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (resource_id, taxonomy_id)
);
```

---

## Connection Pool Configuration

### PostgreSQL

```python
postgresql_params = {
    'pool_size': 20,              # Base connections
    'max_overflow': 40,           # Burst connections
    'pool_recycle': 3600,         # Recycle after 1 hour
    'pool_pre_ping': True,        # Validate before use
}
```

### SQLite

```python
sqlite_params = {
    'pool_size': 5,
    'max_overflow': 10,
    'connect_args': {
        'check_same_thread': False,
        'timeout': 30
    }
}
```

---

## Database Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       DATABASE LAYER                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    Shared Kernel (app/shared/)                   │   │
│  │                                                                  │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │   │
│  │  │   database.py   │  │  base_model.py  │  │   event_bus.py  │   │   │
│  │  │                 │  │                 │  │                 │   │   │
│  │  │ • get_db()      │  │ • BaseModel     │  │ • publish()     │   │   │
│  │  │ • SessionLocal  │  │   - id (GUID)   │  │ • subscribe()   │   │   │
│  │  │ • engine        │  │   - created_at  │  │ • Event class   │   │   │
│  │  │ • Base          │  │   - updated_at  │  │                 │   │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    │ used by                            │
│                                    ▼                                    │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    Module Models                                 │   │
│  │                                                                  │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │   │
│  │  │ resources/      │  │ collections/    │  │ search/         │   │   │
│  │  │   model.py      │  │   model.py      │  │   (uses shared) │   │   │
│  │  │                 │  │                 │  │                 │   │   │
│  │  │ • Resource      │  │ • Collection    │  │ • FTS5 tables   │   │   │
│  │  │ • Annotation    │  │ • CollectionRes │  │ • Vector index  │   │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Migration Commands

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Check current version
alembic current
```

## Database Migration (SQLite ↔ PostgreSQL)

### SQLite → PostgreSQL

```bash
python backend/scripts/migrate_sqlite_to_postgresql.py \
  --source sqlite:///./backend.db \
  --target postgresql://user:pass@host:5432/db \
  --validate
```

### PostgreSQL → SQLite

```bash
python backend/scripts/migrate_postgresql_to_sqlite.py \
  --source postgresql://user:pass@host:5432/db \
  --target sqlite:///./backend.db \
  --validate
```

---

## Backup Strategies

### PostgreSQL

```bash
# Full backup
pg_dump -h localhost -U postgres -d neo_alexandria > backup.sql

# Compressed backup
pg_dump -h localhost -U postgres -d neo_alexandria | gzip > backup.sql.gz
```

### SQLite

```bash
# Simple copy
cp backend.db backend.db.backup

# SQLite backup command
sqlite3 backend.db ".backup 'backup.db'"
```

---

## Related Documentation

- [Architecture Overview](overview.md) - System design
- [PostgreSQL Migration Guide](../POSTGRESQL_MIGRATION_GUIDE.md) - Detailed migration
- [PostgreSQL Backup Guide](../POSTGRESQL_BACKUP_GUIDE.md) - Backup procedures


<div style='page-break-after: always;'></div>

---



# 21. Event System

*Source: `backend/docs/architecture/event-system.md`*

---

# Event System Architecture

Event-driven communication, Celery task queue, and Redis caching for Neo Alexandria 2.0.

> **Last Updated**: Phase 14 - Complete Vertical Slice Refactor

## Table of Contents

1. [Overview](#overview)
2. [Event System Core](#event-system-core)
3. [Celery Distributed Task Queue](#celery-distributed-task-queue)
4. [Redis Caching Architecture](#redis-caching-architecture)
5. [Event Hooks](#event-hooks)
6. [Service Integration](#service-integration)
7. [Docker Compose Orchestration](#docker-compose-orchestration)
8. [Performance Characteristics](#performance-characteristics)

---

## Overview

The event system enables loose coupling between modules through publish-subscribe messaging. Modules emit events when significant actions occur, and other modules can subscribe to react to these events.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EVENT-DRIVEN ARCHITECTURE (Phase 12.5)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Event System Core                           │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │                     EventEmitter (Singleton)                 │   │    │
│  │  │  • on(event_type, handler) - Register listener               │   │    │
│  │  │  • off(event_type, handler) - Unregister listener            │   │    │
│  │  │  • emit(event_type, data, priority) - Dispatch event         │   │    │
│  │  │  • get_event_history(limit) - Retrieve event log             │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │                    SystemEvent Enum                          │   │    │
│  │  │  Resource: created, updated, deleted, content_changed        │   │    │
│  │  │  Processing: ingestion, embedding, quality, classification   │   │    │
│  │  │  User: interaction_tracked, profile_updated                  │   │    │
│  │  │  System: cache_invalidated, search_index_updated             │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Event System Core

### Event Bus Architecture

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

### Event Types

#### Resource Events

| Event | Payload | Triggered When |
|-------|---------|----------------|
| `resource.created` | `{resource_id, title, ...}` | New resource ingested |
| `resource.updated` | `{resource_id, changes}` | Resource metadata updated |
| `resource.deleted` | `{resource_id}` | Resource deleted |
| `resource.content_changed` | `{resource_id}` | Content modified |
| `resource.metadata_changed` | `{resource_id}` | Metadata modified |
| `resource.classified` | `{resource_id, taxonomy_ids}` | Classification assigned |
| `resource.quality_computed` | `{resource_id, score}` | Quality score calculated |

#### Collection Events

| Event | Payload | Triggered When |
|-------|---------|----------------|
| `collection.created` | `{collection_id, name}` | New collection created |
| `collection.updated` | `{collection_id, changes}` | Collection metadata updated |
| `collection.deleted` | `{collection_id}` | Collection deleted |
| `collection.resource_added` | `{collection_id, resource_ids}` | Resources added |
| `collection.resource_removed` | `{collection_id, resource_ids}` | Resources removed |

#### Search Events

| Event | Payload | Triggered When |
|-------|---------|----------------|
| `search.executed` | `{query, results_count, latency}` | Search performed |
| `search.facets_computed` | `{query, facets}` | Facets calculated |

#### Processing Events

| Event | Payload | Triggered When |
|-------|---------|----------------|
| `ingestion.started` | `{url, resource_id}` | Ingestion begins |
| `ingestion.completed` | `{resource_id, status}` | Ingestion finishes |
| `citations.extracted` | `{resource_id, citation_ids}` | Citations parsed |
| `authors.extracted` | `{resource_id, author_names}` | Authors identified |

### Event Bus Implementation

```python
# app/shared/event_bus.py
from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    type: str
    payload: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe a handler to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        handlers = self._subscribers.get(event.type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Event handler error: {e}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Remove a handler from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)

# Global event bus instance
event_bus = EventBus()
```

---

## Celery Distributed Task Queue

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
│  ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐         │
│  │ update_graph_    │   │ classify_        │   │ invalidate_      │         │
│  │ edges_task       │   │ resource_task    │   │ cache_task       │         │
│  ├──────────────────┤   ├──────────────────┤   ├──────────────────┤         │
│  │ • priority=5     │   │ • max_retries=2  │   │ • priority=9     │         │
│  │ • countdown=30   │   │ • priority=5     │   │ • countdown=0    │         │
│  │ • batch_delay    │   │ • countdown=20   │   │ • pattern support│         │
│  └──────────────────┘   └──────────────────┘   └──────────────────┘         │
│                                                                             │
│  ┌──────────────────┐   ┌──────────────────────────────────────────┐        │
│  │ refresh_         │   │ batch_process_resources_task             │        │
│  │ recommendation_  │   ├──────────────────────────────────────────┤        │
│  │ profile_task     │   │ • Progress tracking with update_state()  │        │
│  ├──────────────────┤   │ • Operations: regenerate_embeddings,     │        │
│  │ • priority=3     │   │   recompute_quality                      │        │
│  │ • countdown=300  │   │ • Returns: processed_count, status       │        │
│  └──────────────────┘   └──────────────────────────────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Task Routing

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Task Routing                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  • urgent queue (priority 9) - Search index, cache invalidation         │
│  • high_priority queue (priority 7) - Embeddings                        │
│  • ml_tasks queue (priority 5) - Classification, quality                │
│  • batch queue (priority 3) - Batch processing                          │
│  • default queue (priority 5) - General tasks                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Redis Caching Architecture

### Multi-Layer Caching

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MULTI-LAYER REDIS CACHING                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         RedisCache Class                            │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │  Methods:                                                    │   │    │
│  │  │  • get(key) → value | None                                   │   │    │
│  │  │  • set(key, value, ttl) → None                               │   │    │
│  │  │  • delete(key) → None                                        │   │    │
│  │  │  • delete_pattern(pattern) → int (count)                     │   │    │
│  │  │  • get_default_ttl(key) → int (seconds)                      │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │                    CacheStats Tracking                       │   │    │
│  │  │  • hits: int                                                 │   │    │
│  │  │  • misses: int                                               │   │    │
│  │  │  • invalidations: int                                        │   │    │
│  │  │  • hit_rate() → float (0.0-1.0)                              │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        Cache Key Strategy                           │    │
│  │                                                                     │    │
│  │  embedding:{resource_id}           TTL: 3600s (1 hour)              │    │
│  │  quality:{resource_id}             TTL: 1800s (30 minutes)          │    │
│  │  search_query:{hash}               TTL: 300s (5 minutes)            │    │
│  │  resource:{resource_id}            TTL: 600s (10 minutes)           │    │
│  │  graph:{resource_id}:neighbors     TTL: 1800s (30 minutes)          │    │
│  │  user:{user_id}:profile            TTL: 600s (10 minutes)           │    │
│  │  classification:{resource_id}      TTL: 3600s (1 hour)              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Cache Invalidation Patterns                      │    │
│  │                                                                     │    │
│  │  resource:{resource_id}:*          → All resource-related caches    │    │
│  │  search_query:*                    → All search result caches       │    │
│  │  graph:*                           → All graph caches               │    │
│  │  user:{user_id}:*                  → All user-related caches        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Event Hooks

### Auto-Consistency Hooks

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Event Hooks (Auto-Consistency)                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  resource.content_changed ──► regenerate_embedding_task (5s delay)      │
│  resource.metadata_changed ─► recompute_quality_task (10s delay)        │
│  resource.updated ──────────► update_search_index_task (1s delay)       │
│  citations.extracted ────────► update_graph_edges_task (30s delay)      │
│  resource.updated ──────────► invalidate_cache_task (immediate)         │
│  user.interaction_tracked ───► refresh_profile_task (every 10)          │
│  resource.created ───────────► classify_resource_task (20s delay)       │
│  authors.extracted ──────────► normalize_names_task (60s delay)         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Service Integration

### ResourceService Event Integration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       ResourceService                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  create(data) → Resource                                                │
│    1. Create resource in database                                       │
│    2. Emit: resource.created                                            │
│    3. Hooks trigger: classify_resource_task                             │
│                                                                         │
│  update(id, data) → Resource                                            │
│    1. Update resource in database                                       │
│    2. Detect changes (content vs metadata)                              │
│    3. Emit: resource.updated                                            │
│    4. Emit: resource.content_changed (if content changed)               │
│    5. Emit: resource.metadata_changed (if metadata changed)             │
│    6. Hooks trigger:                                                    │
│       - regenerate_embedding_task (if content)                          │
│       - recompute_quality_task (if metadata)                            │
│       - update_search_index_task (always)                               │
│       - invalidate_cache_task (always)                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### IngestionService Event Integration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      IngestionService                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  process(url) → Resource                                                │
│    1. Emit: ingestion.started                                           │
│    2. Fetch and extract content                                         │
│    3. Generate embeddings                                               │
│    4. Extract citations → Emit: citations.extracted                     │
│    5. Extract authors → Emit: authors.extracted                         │
│    6. Compute quality                                                   │
│    7. Create resource → Emit: resource.created                          │
│    8. Emit: ingestion.completed                                         │
│    9. Hooks trigger all downstream tasks                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### UserInteractionTracking

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   UserInteractionTracking                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  track_interaction(user_id, resource_id, type) → None                   │
│    1. Record interaction in database                                    │
│    2. Get total interaction count for user                              │
│    3. Emit: user.interaction_tracked                                    │
│    4. Hook checks: if count % 10 == 0                                   │
│       → refresh_recommendation_profile_task                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Docker Compose Orchestration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DOCKER COMPOSE ORCHESTRATION                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                            Redis                                    │    │
│  │  • Image: redis:7-alpine                                            │    │
│  │  • Memory: 2GB with allkeys-lru eviction                            │    │
│  │  • Persistence: appendonly yes                                      │    │
│  │  • Port: 6379                                                       │    │
│  │  • Health check: redis-cli ping                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                   │                                         │
│                    ┌──────────────┼──────────────┐                          │
│                    │              │              │                          │
│  ┌─────────────────▼──┐  ┌────────▼────────┐  ┌──▼──────────────────┐       │
│  │  Celery Workers    │  │  Celery Beat    │  │     Flower          │       │
│  │  (4 replicas)      │  │  (Scheduler)    │  │   (Monitoring)      │       │
│  ├────────────────────┤  ├─────────────────┤  ├─────────────────────┤       │
│  │ • Concurrency: 4   │  │ • Schedules:    │  │ • Port: 5555        │       │
│  │ • CPU: 2 cores     │  │   - Daily 2 AM  │  │ • Web dashboard     │       │
│  │ • Memory: 2GB      │  │   - Weekly Sun  │  │ • Task monitoring   │       │
│  │ • Queues: all      │  │   - Monthly 1st │  │ • Worker stats      │       │
│  │ • Auto-restart     │  │   - Daily 4 AM  │  │ • Real-time graphs  │       │
│  └────────────────────┘  └─────────────────┘  └─────────────────────┘       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         FastAPI Application                         │    │
│  │  • Depends on: Redis                                                │    │
│  │  • Environment: CELERY_BROKER_URL, CELERY_RESULT_BACKEND            │    │
│  │  • Startup: register_all_hooks(), initialize Redis cache            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Performance Characteristics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 12.5 PERFORMANCE METRICS                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Scalability:                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • 100+ concurrent ingestions without degradation                   │    │
│  │  • Linear throughput scaling with worker count                      │    │
│  │  • Horizontal scaling across multiple machines                      │    │
│  │  • 4 workers → 400 tasks/minute                                     │    │
│  │  • 8 workers → 800 tasks/minute (linear)                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Cache Performance:                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • 60-70% cache hit rate for repeated operations                    │    │
│  │  • 50-70% computation reduction through caching                     │    │
│  │  • Sub-millisecond cache lookups                                    │    │
│  │  • Pattern-based invalidation in <10ms                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Task Reliability:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • <1% task failure rate with automatic retries                     │    │
│  │  • Exponential backoff for transient errors                         │    │
│  │  • Dead letter queue for permanent failures                         │    │
│  │  • Task acknowledgment after completion                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Search Index Updates:                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • Complete within 5 seconds of resource updates                    │    │
│  │  • URGENT priority ensures immediate searchability                  │    │
│  │  • Automatic retry on failure                                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Database Connection Pooling:                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • 20 base connections + 40 overflow = 60 total                     │    │
│  │  • Connection recycling after 1 hour                                │    │
│  │  • Pre-ping health checks                                           │    │
│  │  • Handles 100+ concurrent requests                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Best Practices

### Event Design

- Keep payloads minimal (IDs, not full objects)
- Include timestamp for ordering
- Use past tense for event names (`created`, not `create`)
- Make events idempotent when possible

### Handler Design

- Handlers should be fast (<100ms)
- Use background tasks for slow operations
- Handle errors gracefully (don't crash on failure)
- Log all event processing

### Testing Events

```python
def test_resource_deletion_updates_collections(db, event_bus):
    # Create resource and collection
    resource = create_resource(db, {...})
    collection = create_collection(db, {...})
    add_resource_to_collection(db, collection.id, resource.id)
    
    # Delete resource (triggers event)
    delete_resource(db, resource.id)
    
    # Verify collection updated
    updated = get_collection(db, collection.id)
    assert resource.id not in [r.id for r in updated.resources]
```

---

## Related Documentation

- [Architecture Overview](overview.md) - System design
- [Modules](modules.md) - Vertical slice architecture
- [Database](database.md) - Schema and models
- [Event-Driven Refactoring](../EVENT_DRIVEN_REFACTORING.md) - Migration details


<div style='page-break-after: always;'></div>

---



# 22. Event Catalog

*Source: `backend/docs/architecture/events.md`*

---

# Event Catalog

Complete reference for all events in Neo Alexandria 2.0's event-driven architecture.

> **Phase 14 Complete**: This catalog documents all 25+ events used for inter-module communication in the fully modular vertical slice architecture.

---

## Table of Contents

1. [Overview](#overview)
2. [Event Naming Conventions](#event-naming-conventions)
3. [Event Categories](#event-categories)
4. [Complete Event Reference](#complete-event-reference)
5. [Event Flow Diagrams](#event-flow-diagrams)
6. [Best Practices](#best-practices)
7. [Monitoring Events](#monitoring-events)

---

## Overview

### What Are Events?

Events are the primary mechanism for communication between modules in Neo Alexandria 2.0. Instead of modules directly calling each other (which creates tight coupling), modules emit events when something significant happens, and other modules subscribe to events they care about.

### Benefits of Event-Driven Architecture

1. **Loose Coupling**: Modules don't need to know about each other
2. **Scalability**: Easy to add new subscribers without modifying emitters
3. **Testability**: Modules can be tested in isolation
4. **Flexibility**: Event handlers can be added/removed dynamically
5. **Auditability**: All inter-module communication is logged

### Event Bus

The event bus is implemented in `app/shared/event_bus.py` and provides:
- **Synchronous delivery**: Events are delivered immediately in the same process
- **Error isolation**: Handler failures don't affect other handlers
- **Metrics tracking**: Events emitted, delivered, and errors are tracked
- **Type safety**: Events have defined types and payloads

---

## Event Naming Conventions

### Pattern

All events follow the pattern: `{domain}.{action}`

- **domain**: The module or entity that owns the event (lowercase, singular)
- **action**: The action that occurred (past tense, snake_case)

### Examples

```
resource.created          # Resource module created a resource
resource.updated          # Resource module updated a resource
resource.deleted          # Resource module deleted a resource
collection.updated        # Collection module updated a collection
quality.computed          # Quality module computed quality scores
quality.outlier_detected  # Quality module detected an outlier
annotation.created        # Annotation module created an annotation
```

### Guidelines

1. **Use past tense**: Events describe what happened, not what will happen
2. **Be specific**: `resource.created` not `resource.changed`
3. **Use snake_case**: `outlier_detected` not `outlierDetected`
4. **Keep it short**: Prefer concise names that are still clear
5. **Avoid abbreviations**: `metadata.extracted` not `meta.ext`

---

## Event Categories

### Resource Lifecycle Events

Events related to resource creation, modification, and deletion.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `resource.created` | Resources | New resource added to system |
| `resource.updated` | Resources | Resource metadata or content changed |
| `resource.deleted` | Resources | Resource removed from system |

### Collection Events

Events related to collection management.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `collection.updated` | Collections | Collection metadata changed |
| `collection.deleted` | Collections | Collection removed |
| `collection.resource_added` | Collections | Resource added to collection |
| `collection.resource_removed` | Collections | Resource removed from collection |

### Annotation Events

Events related to user annotations.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `annotation.created` | Annotations | User created annotation |
| `annotation.updated` | Annotations | User modified annotation |
| `annotation.deleted` | Annotations | User deleted annotation |

### Quality Events

Events related to quality assessment.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `quality.computed` | Quality | Quality scores calculated |
| `quality.outlier_detected` | Quality | Anomalous quality detected |
| `quality.degradation_detected` | Quality | Quality decreased over time |

### Taxonomy Events

Events related to classification and taxonomy.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `resource.classified` | Taxonomy | Resource auto-classified |
| `taxonomy.node_created` | Taxonomy | New taxonomy node added |
| `taxonomy.model_trained` | Taxonomy | ML model retrained |

### Graph Events

Events related to knowledge graph and citations.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `citation.extracted` | Graph | Citations parsed from resource |
| `graph.updated` | Graph | Graph structure changed |
| `hypothesis.discovered` | Graph | LBD found new connection |

### Recommendation Events

Events related to recommendations and user profiles.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `recommendation.generated` | Recommendations | Recommendations produced |
| `user.profile_updated` | Recommendations | User preferences changed |
| `interaction.recorded` | Recommendations | User interaction logged |

### Scholarly Events

Events related to academic metadata.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `metadata.extracted` | Scholarly | Academic metadata parsed |
| `equations.parsed` | Scholarly | Mathematical equations found |
| `tables.extracted` | Scholarly | Tables extracted from content |

### Curation Events

Events related to content review.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `curation.reviewed` | Curation | Content reviewed by curator |
| `curation.approved` | Curation | Content approved |
| `curation.rejected` | Curation | Content rejected |

### Search Events

Events related to search operations.

| Event | Emitter | Purpose |
|-------|---------|---------|
| `search.completed` | Search | Search query executed |

---

## Complete Event Reference

### resource.created

**Emitter**: Resources Module  
**Subscribers**: Annotations, Quality, Taxonomy, Graph, Scholarly  
**Purpose**: Trigger processing for newly created resources

**Payload**:
```python
{
    "resource_id": str,        # UUID of created resource
    "title": str,              # Resource title
    "content": str,            # Resource content (may be truncated)
    "content_type": str,       # MIME type (e.g., "text/html")
    "url": str | None,         # Source URL if applicable
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("resource.created", {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Introduction to Machine Learning",
    "content": "Machine learning is...",
    "content_type": "text/html",
    "url": "https://example.com/ml-intro",
    "timestamp": "2024-01-15T10:30:00Z"
})
```

**Subscribers React By**:
- **Quality**: Computing initial quality scores
- **Taxonomy**: Auto-classifying the resource
- **Graph**: Extracting citations
- **Scholarly**: Extracting academic metadata
- **Annotations**: (No immediate action, but enables annotation creation)

---

### resource.updated

**Emitter**: Resources Module  
**Subscribers**: Quality, Search  
**Purpose**: Update dependent data when resource changes

**Payload**:
```python
{
    "resource_id": str,        # UUID of updated resource
    "changed_fields": list,    # List of field names that changed
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("resource.updated", {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "changed_fields": ["title", "content", "tags"],
    "timestamp": "2024-01-15T11:00:00Z"
})
```

**Subscribers React By**:
- **Quality**: Recomputing quality scores
- **Search**: Reindexing the resource

---

### resource.deleted

**Emitter**: Resources Module  
**Subscribers**: Collections, Annotations, Graph  
**Purpose**: Cascade cleanup when resource is removed

**Payload**:
```python
{
    "resource_id": str,        # UUID of deleted resource
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("resource.deleted", {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "timestamp": "2024-01-15T12:00:00Z"
})
```

**Subscribers React By**:
- **Collections**: Removing resource from all collections
- **Annotations**: Deleting all annotations on the resource
- **Graph**: Removing resource from knowledge graph

---

### collection.updated

**Emitter**: Collections Module  
**Subscribers**: Search  
**Purpose**: Reindex collection when metadata changes

**Payload**:
```python
{
    "collection_id": str,      # UUID of updated collection
    "resource_count": int,     # Number of resources in collection
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("collection.updated", {
    "collection_id": "456e7890-e89b-12d3-a456-426614174000",
    "resource_count": 42,
    "timestamp": "2024-01-15T13:00:00Z"
})
```

**Subscribers React By**:
- **Search**: Reindexing the collection

---

### collection.resource_added

**Emitter**: Collections Module  
**Subscribers**: Recommendations  
**Purpose**: Update user preferences based on collection additions

**Payload**:
```python
{
    "collection_id": str,      # UUID of collection
    "resource_id": str,        # UUID of added resource
    "user_id": str,            # UUID of user who added it
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("collection.resource_added", {
    "collection_id": "456e7890-e89b-12d3-a456-426614174000",
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "789e0123-e89b-12d3-a456-426614174000",
    "timestamp": "2024-01-15T14:00:00Z"
})
```

**Subscribers React By**:
- **Recommendations**: Updating user profile with new preferences

---

### annotation.created

**Emitter**: Annotations Module  
**Subscribers**: Recommendations  
**Purpose**: Update user profile based on annotation activity

**Payload**:
```python
{
    "annotation_id": str,      # UUID of created annotation
    "resource_id": str,        # UUID of annotated resource
    "user_id": str,            # UUID of user who created it
    "text": str,               # Annotation text
    "tags": list,              # List of tags
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("annotation.created", {
    "annotation_id": "abc12345-e89b-12d3-a456-426614174000",
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "789e0123-e89b-12d3-a456-426614174000",
    "text": "Important concept for my research",
    "tags": ["machine-learning", "research"],
    "timestamp": "2024-01-15T15:00:00Z"
})
```

**Subscribers React By**:
- **Recommendations**: Updating user profile with annotation topics

---

### quality.computed

**Emitter**: Quality Module  
**Subscribers**: Monitoring  
**Purpose**: Track quality metrics across the system

**Payload**:
```python
{
    "resource_id": str,        # UUID of assessed resource
    "overall_score": float,    # Overall quality score (0-1)
    "dimensions": dict,        # Scores by dimension
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("quality.computed", {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "overall_score": 0.85,
    "dimensions": {
        "completeness": 0.9,
        "accuracy": 0.8,
        "readability": 0.85
    },
    "timestamp": "2024-01-15T16:00:00Z"
})
```

**Subscribers React By**:
- **Monitoring**: Aggregating quality statistics

---

### quality.outlier_detected

**Emitter**: Quality Module  
**Subscribers**: Curation  
**Purpose**: Flag resources with anomalous quality for review

**Payload**:
```python
{
    "resource_id": str,        # UUID of outlier resource
    "outlier_score": float,    # How anomalous (higher = more anomalous)
    "reasons": list,           # List of reasons for outlier status
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("quality.outlier_detected", {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "outlier_score": 0.95,
    "reasons": [
        "Completeness score 3 std devs below mean",
        "Readability score in bottom 5%"
    ],
    "timestamp": "2024-01-15T17:00:00Z"
})
```

**Subscribers React By**:
- **Curation**: Adding resource to review queue with high priority

---

### resource.classified

**Emitter**: Taxonomy Module  
**Subscribers**: Search  
**Purpose**: Update search index with classification results

**Payload**:
```python
{
    "resource_id": str,        # UUID of classified resource
    "classifications": list,   # List of classification results
    "model_version": str,      # ML model version used
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("resource.classified", {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "classifications": [
        {"category": "cs.AI", "confidence": 0.92},
        {"category": "cs.LG", "confidence": 0.85}
    ],
    "model_version": "v2.0",
    "timestamp": "2024-01-15T18:00:00Z"
})
```

**Subscribers React By**:
- **Search**: Updating search index with classification tags

---

### citation.extracted

**Emitter**: Graph Module  
**Subscribers**: Monitoring  
**Purpose**: Track citation network growth

**Payload**:
```python
{
    "resource_id": str,        # UUID of resource with citations
    "citation_count": int,     # Number of citations found
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("citation.extracted", {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "citation_count": 15,
    "timestamp": "2024-01-15T19:00:00Z"
})
```

**Subscribers React By**:
- **Monitoring**: Tracking citation network statistics

---

### recommendation.generated

**Emitter**: Recommendations Module  
**Subscribers**: Monitoring  
**Purpose**: Track recommendation quality and usage

**Payload**:
```python
{
    "user_id": str,            # UUID of user receiving recommendations
    "count": int,              # Number of recommendations generated
    "strategy": str,           # Strategy used (e.g., "hybrid")
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("recommendation.generated", {
    "user_id": "789e0123-e89b-12d3-a456-426614174000",
    "count": 10,
    "strategy": "hybrid",
    "timestamp": "2024-01-15T20:00:00Z"
})
```

**Subscribers React By**:
- **Monitoring**: Aggregating recommendation metrics

---

### metadata.extracted

**Emitter**: Scholarly Module  
**Subscribers**: Monitoring  
**Purpose**: Track metadata extraction completeness

**Payload**:
```python
{
    "resource_id": str,        # UUID of resource
    "metadata_fields": list,   # List of extracted field names
    "timestamp": str           # ISO 8601 timestamp
}
```

**Example**:
```python
event_bus.emit("metadata.extracted", {
    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
    "metadata_fields": ["authors", "abstract", "doi", "publication_date"],
    "timestamp": "2024-01-15T21:00:00Z"
})
```

**Subscribers React By**:
- **Monitoring**: Tracking metadata completeness statistics

---

## Event Flow Diagrams

### Resource Creation Flow

```
User creates resource via API
        ↓
┌───────────────────┐
│ Resources Module  │
│ ├─ Save to DB     │
│ ├─ Emit event     │
│ └─ Return response│
└───────────────────┘
        │
        │ resource.created
        ↓
┌───────────────────────────────────────────────────────┐
│              Event Bus Distribution                    │
└───────────────────────────────────────────────────────┘
        │
        ├──────────┬──────────┬──────────┬──────────┐
        ↓          ↓          ↓          ↓          ↓
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │Quality │ │Taxonomy│ │ Graph  │ │Scholarly│ │Annot.  │
   │        │ │        │ │        │ │        │ │        │
   │Compute │ │Auto-   │ │Extract │ │Extract │ │(Ready) │
   │quality │ │classify│ │citations│ │metadata│ │        │
   └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
        │          │          │          │
        ↓          ↓          ↓          ↓
   quality.   resource.  citation.  metadata.
   computed   classified extracted  extracted
```

### Quality Outlier Detection Flow

```
Quality Module computes scores
        ↓
Detects outlier (score > threshold)
        ↓
┌───────────────────┐
│  Quality Module   │
│ Emit event        │
└───────────────────┘
        │
        │ quality.outlier_detected
        ↓
┌───────────────────┐
│ Curation Module   │
│ ├─ Add to queue   │
│ ├─ Set priority   │
│ └─ Notify curator │
└───────────────────┘
        │
        │ curation.reviewed (when reviewed)
        ↓
┌───────────────────┐
│ Monitoring Module │
│ Track metrics     │
└───────────────────┘
```

### User Interaction Flow

```
User adds annotation
        ↓
┌───────────────────┐
│Annotations Module │
│ ├─ Save annotation│
│ ├─ Emit event     │
│ └─ Return response│
└───────────────────┘
        │
        │ annotation.created
        ↓
┌───────────────────────┐
│ Recommendations Module│
│ ├─ Update profile     │
│ ├─ Adjust preferences │
│ ├─ Emit event         │
│ └─ Refresh recs       │
└───────────────────────┘
        │
        │ user.profile_updated
        ↓
┌───────────────────┐
│ Monitoring Module │
│ Track engagement  │
└───────────────────┘
```

### Resource Deletion Cascade

```
User deletes resource
        ↓
┌───────────────────┐
│ Resources Module  │
│ ├─ Delete from DB │
│ ├─ Emit event     │
│ └─ Return 204     │
└───────────────────┘
        │
        │ resource.deleted
        ↓
┌───────────────────────────────────────┐
│       Event Bus Distribution          │
└───────────────────────────────────────┘
        │
        ├──────────┬──────────┬──────────┐
        ↓          ↓          ↓          ↓
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │Collect.│ │Annot.  │ │ Graph  │ │Monitor.│
   │        │ │        │ │        │ │        │
   │Remove  │ │Delete  │ │Remove  │ │Track   │
   │from    │ │all     │ │from    │ │deletion│
   │colls   │ │annots  │ │graph   │ │        │
   └────────┘ └────────┘ └────────┘ └────────┘
```

---

## Best Practices

### For Event Emitters

1. **Emit after commit**: Always emit events AFTER database commits succeed
   ```python
   # Good
   db.commit()
   event_bus.emit("resource.created", payload)
   
   # Bad - event emitted before commit
   event_bus.emit("resource.created", payload)
   db.commit()  # Could fail!
   ```

2. **Include sufficient context**: Provide enough information for subscribers
   ```python
   # Good - includes all relevant data
   event_bus.emit("resource.created", {
       "resource_id": str(resource.id),
       "title": resource.title,
       "content_type": resource.content_type,
       "timestamp": datetime.now(timezone.utc).isoformat()
   })
   
   # Bad - insufficient context
   event_bus.emit("resource.created", {
       "resource_id": str(resource.id)
   })
   ```

3. **Use ISO 8601 timestamps**: Always include timestamps in ISO 8601 format
   ```python
   from datetime import datetime, timezone
   
   "timestamp": datetime.now(timezone.utc).isoformat()
   ```

4. **Don't emit on failures**: Only emit events for successful operations
   ```python
   try:
       resource = create_resource(data)
       db.commit()
       event_bus.emit("resource.created", payload)
   except Exception as e:
       db.rollback()
       # Don't emit event on failure
       raise
   ```

### For Event Subscribers

1. **Create fresh database sessions**: Always create new sessions in handlers
   ```python
   def handle_resource_created(payload: dict):
       from app.shared.database import SessionLocal
       
       db = SessionLocal()  # Fresh session
       try:
           # Process event
           pass
       finally:
           db.close()  # Always close
   ```

2. **Catch all exceptions**: Don't let handler failures affect other handlers
   ```python
   def handle_event(payload: dict):
       try:
           # Process event
           pass
       except Exception as e:
           logger.error(f"Handler error: {e}", exc_info=True)
           # Don't re-raise - let other handlers continue
       finally:
           db.close()
   ```

3. **Keep handlers fast**: Aim for <100ms execution time
   ```python
   # Good - quick processing
   def handle_event(payload: dict):
       resource_id = payload["resource_id"]
       update_cache(resource_id)  # Fast operation
   
   # Bad - slow processing
   def handle_event(payload: dict):
       resource_id = payload["resource_id"]
       recompute_all_embeddings()  # Slow! Use Celery instead
   ```

4. **Make handlers idempotent**: Safe to run multiple times
   ```python
   def handle_resource_created(payload: dict):
       resource_id = payload["resource_id"]
       
       # Check if already processed
       if already_processed(resource_id):
           return
       
       # Process event
       process_resource(resource_id)
       mark_as_processed(resource_id)
   ```

5. **Log all processing**: Include event type and payload in logs
   ```python
   def handle_event(payload: dict):
       logger.info(f"Processing event: {payload}")
       try:
           # Process
           logger.info(f"Successfully processed: {payload}")
       except Exception as e:
           logger.error(f"Failed to process: {payload}", exc_info=True)
   ```

### Event Payload Guidelines

1. **Use UUIDs as strings**: Always convert UUIDs to strings
   ```python
   "resource_id": str(resource.id)  # Good
   "resource_id": resource.id       # Bad - not JSON serializable
   ```

2. **Keep payloads small**: Don't include large content
   ```python
   # Good - reference only
   "resource_id": "123e4567-e89b-12d3-a456-426614174000"
   
   # Bad - includes full content
   "content": "..." # 10MB of text
   ```

3. **Use consistent field names**: Follow naming conventions
   ```python
   # Good - snake_case
   "resource_id", "user_id", "created_at"
   
   # Bad - mixed case
   "resourceId", "userId", "createdAt"
   ```

4. **Include metadata**: Add context for debugging
   ```python
   {
       "resource_id": "...",
       "timestamp": "2024-01-15T10:00:00Z",
       "source": "api",  # Where did this come from?
       "user_id": "..."  # Who triggered it?
   }
   ```

---

## Monitoring Events

### Event Bus Metrics

Check event bus health and metrics:

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

### Event History

View recent events:

```bash
curl http://localhost:8000/monitoring/events/history?limit=10
```

Response:
```json
{
  "events": [
    {
      "type": "resource.created",
      "timestamp": "2024-01-15T10:00:00Z",
      "payload": {"resource_id": "..."},
      "handlers_called": 5,
      "latency_ms": 1.2
    }
  ]
}
```

### Debugging Event Issues

1. **Check if event is being emitted**:
   ```python
   # Add logging in emitter
   logger.info(f"Emitting event: {event_type}")
   event_bus.emit(event_type, payload)
   ```

2. **Check if handlers are registered**:
   ```bash
   curl http://localhost:8000/monitoring/events
   # Look at handler_count per event type
   ```

3. **Check handler errors**:
   ```bash
   curl http://localhost:8000/monitoring/events/history
   # Look for events with errors
   ```

4. **Enable debug logging**:
   ```python
   # In app/shared/event_bus.py
   logger.setLevel(logging.DEBUG)
   ```

---

## Related Documentation

- [Architecture Overview](overview.md) - System architecture
- [Event System](event-system.md) - Event bus implementation details
- [Module Documentation](modules.md) - Module-specific event usage
- [Migration Guide](../MIGRATION_GUIDE.md) - Event-driven migration patterns
- [Development Workflows](../guides/workflows.md) - Working with events

---

*Last Updated: Phase 14 Complete - December 2024*


<div style='page-break-after: always;'></div>

---



# 23. Module Architecture

*Source: `backend/docs/architecture/modules.md`*

---

# Vertical Slice Modules & Service Architecture

Module architecture, service layer, and class hierarchies for Neo Alexandria 2.0.

> **Last Updated**: Phase 14 - Complete Vertical Slice Refactor

## Modular Architecture Overview (Phase 14 - Complete)

Phase 14 completes the vertical slice architecture transformation with 13 self-contained modules.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    NEO ALEXANDRIA 2.0 - COMPLETE MODULAR ARCHITECTURE                   │
│                              (13 Vertical Slice Modules)                                │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │                         FastAPI Application (main.py)                            │   │
│  │                    Registers all module routers & event handlers                 │   │
│  └────────────────────────────────────┬─────────────────────────────────────────────┘   │
│                                       │                                                 │
│                                       │ Module Registration                             │
│                                       │                                                 │
│       ┌───────────────────────────────┼───────────────────────────────────┐             │
│       │                               │                                   │             │
│       ▼                               ▼                                   ▼             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Resources │  │Collections│ │  Search  │  │Annotations│ │ Scholarly│  │ Authority│   │
│  │  Module  │  │  Module  │  │  Module  │  │  Module  │  │  Module  │  │  Module  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │             │             │          │
│       │             │             │             │             │             │          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Curation │  │  Quality │  │ Taxonomy │  │  Graph   │  │Recommend-│  │Monitoring│   │
│  │  Module  │  │  Module  │  │  Module  │  │  Module  │  │ ations   │  │  Module  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │             │             │          │
│       │             │             │             │             │             │          │
│       │    ┌────────┴─────────────┴─────────────┴─────────────┴────────────┘          │
│       │    │                                                                           │
│       │    ▼                                                                           │
│       │  ┌─────────────────────────────────────────────────────────────────┐           │
│       │  │                      Shared Kernel                              │           │
│       │  │  ┌──────────┐  ┌──────────────┐  ┌──────────────┐              │           │
│       └─►│  │ Database │  │  Event Bus   │  │  Base Model  │              │◄──────────┘
│          │  │ (Session)│  │  (Pub/Sub)   │  │   (GUID)     │              │           │
│          │  └──────────┘  └──────────────┘  └──────────────┘              │           │
│          │  ┌──────────────────────────────────────────────────────────┐   │           │
│          │  │  Cross-Cutting Services:                                 │   │           │
│          │  │  • EmbeddingService (dense & sparse embeddings)          │   │           │
│          │  │  • AICore (summarization, entity extraction)             │   │           │
│          │  │  • CacheService (Redis caching with TTL)                 │   │           │
│          │  └──────────────────────────────────────────────────────────┘   │           │
│          └─────────────────────────────────────────────────────────────────┘           │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### All 13 Modules

| # | Module | Domain | Events Emitted | Events Consumed |
|---|--------|--------|----------------|-----------------|
| 1 | **Resources** | Content management | resource.created, resource.updated, resource.deleted | - |
| 2 | **Collections** | Organization | collection.created, collection.updated, collection.resource_added | resource.deleted |
| 3 | **Search** | Discovery | search.executed | resource.created, resource.updated |
| 4 | **Annotations** | Highlights & notes | annotation.created, annotation.updated, annotation.deleted | resource.deleted |
| 5 | **Scholarly** | Academic metadata | metadata.extracted, equations.parsed, tables.extracted | resource.created |
| 6 | **Authority** | Subject authority | - | - |
| 7 | **Curation** | Content review | curation.reviewed, curation.approved, curation.rejected | quality.outlier_detected |
| 8 | **Quality** | Quality assessment | quality.computed, quality.outlier_detected | resource.created, resource.updated |
| 9 | **Taxonomy** | ML classification | resource.classified, taxonomy.node_created | resource.created |
| 10 | **Graph** | Knowledge graph | citation.extracted, graph.updated, hypothesis.discovered | resource.created, resource.deleted |
| 11 | **Recommendations** | Personalization | recommendation.generated, user.profile_updated | annotation.created, collection.resource_added |
| 12 | **Monitoring** | System health | - | All events (metrics) |

---

## Vertical Slice Module Pattern

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

## Current Modules

### Resources Module

**Domain:** Content management and ingestion

**Responsibilities:**
- Resource CRUD operations
- URL ingestion and content extraction
- AI-powered summarization and tagging
- Quality score computation
- Classification assignment

**Events Published:**
- `resource.created`
- `resource.updated`
- `resource.deleted`
- `resource.classified`

**Location:** `app/modules/resources/`

### Collections Module

**Domain:** Resource organization and curation

**Responsibilities:**
- Collection CRUD operations
- Hierarchical organization (parent-child)
- Resource membership management
- Aggregate embedding computation
- Collection-based recommendations

**Events Published:**
- `collection.created`
- `collection.updated`
- `collection.deleted`
- `collection.resource_added`
- `collection.resource_removed`

**Events Subscribed:**
- `resource.deleted` → Remove from collections

**Location:** `app/modules/collections/`

### Search Module

**Domain:** Discovery and retrieval

**Responsibilities:**
- Hybrid search (keyword + semantic)
- Three-way search with RRF fusion
- Faceted search results
- Search quality evaluation

**Events Published:**
- `search.executed`

**Events Subscribed:**
- `resource.created` → Update search index
- `resource.updated` → Update search index
- `resource.deleted` → Remove from index

**Location:** `app/modules/search/`

---

## Module Communication

Modules communicate through the event bus, not direct imports:

```
┌──────────────────────────────────────────────────────────────────────┐
│                    MODULE COMMUNICATION                              │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ❌ WRONG: Direct Import                                             │
│  ─────────────────────────                                           │
│  from app.modules.resources.service import get_resource              │
│                                                                      │
│  ✅ CORRECT: Event-Based Communication                               │
│  ─────────────────────────────────────                               │
│  event_bus.publish(Event(type="resource.deleted", payload={...}))    │
│                                                                      │
│  ✅ CORRECT: Shared Kernel                                           │
│  ─────────────────────────                                           │
│  from app.shared.database import get_db                              │
│  from app.shared.event_bus import event_bus                          │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Shared Kernel

Common infrastructure shared by all modules:

```
app/shared/
├── __init__.py
├── database.py      # Database session, engine
├── event_bus.py     # Event publishing/subscribing
└── base_model.py    # Base SQLAlchemy model with GUID
```

### Database Access

```python
from app.shared.database import get_db, SessionLocal

# In router
@router.get("/resources")
def list_resources(db: Session = Depends(get_db)):
    return service.list_resources(db)
```

### Event Bus

```python
from app.shared.event_bus import event_bus, Event

# Publishing
event_bus.publish(Event(
    type="resource.created",
    payload={"resource_id": str(resource.id)}
))

# Subscribing
event_bus.subscribe("resource.deleted", handle_resource_deleted)
```

### Base Model

```python
from app.shared.base_model import BaseModel

class Resource(BaseModel):
    __tablename__ = "resources"
    # Inherits: id (UUID), created_at, updated_at
    title = Column(String, nullable=False)
```

---

## Service Layer Architecture

The service layer implements business logic and orchestrates domain objects, database operations, and external services.

### ML Classification Service

```
┌────────────────────────────────────────────────────────────────────┐
│                    MLClassificationService                         │
├────────────────────────────────────────────────────────────────────┤
│ Attributes:                                                        │
│  • db: Session                                                     │
│  • model_name: str = "distilbert-base-uncased"                     │
│  • model: Optional[AutoModelForSequenceClassification]             │
│  • tokenizer: Optional[AutoTokenizer]                              │
│  • id_to_label: Dict[int, str]                                     │
│  • label_to_id: Dict[str, int]                                     │
│  • monitor: PredictionMonitor                                      │
│  • checkpoint_dir: Path                                            │
│  • device: torch.device                                            │
├────────────────────────────────────────────────────────────────────┤
│ Constants:                                                         │
│  • DEFAULT_MODEL_NAME = "distilbert-base-uncased"                  │
│  • MAX_TOKEN_LENGTH = 512                                          │
│  • DEFAULT_EPOCHS = 3                                              │
│  • DEFAULT_BATCH_SIZE = 16                                         │
│  • DEFAULT_LEARNING_RATE = 2e-5                                    │
│  • BINARY_PREDICTION_THRESHOLD = 0.5                               │
│  • HIGH_CONFIDENCE_THRESHOLD = 0.8                                 │
│  • DEFAULT_TOP_K = 5                                               │
├────────────────────────────────────────────────────────────────────┤
│ Public Methods:                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Training & Fine-tuning                                       │  │ 
│  │  • fine_tune(labeled_data, ...) → Dict[str, float]           │  │
│  │  • semi_supervised_learning(...) → Dict[str, float]          │  │
│  └──────────────────────────────────────────────────────────────┘  │ 
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Inference                                                    │  │
│  │  • predict(text, top_k) → ClassificationResult               │  │
│  │  • predict_batch(texts, top_k) → List[ClassificationResult]  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Active Learning                                              │  │
│  │  • active_learning_uncertainty_sampling(...)                 │  │
│  │  • get_model_metrics(window_minutes) → Dict                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────────────┤
│ Private Methods (20+ helper methods):                              │
│  • _load_model(), _import_ml_libraries()                           │
│  • _tokenize_texts(), _create_datasets()                           │
│  • _compute_metrics(), _calculate_classification_metrics()         │
│  • _build_label_mapping(), _convert_to_multihot_encoding()         │
│  • _split_train_validation(), _initialize_model_for_training()     │
│  • _configure_trainer(), _train_model()                            │
│  • _perform_semi_supervised_learning()                             │
│  • _save_model_and_artifacts(), _extract_metrics()                 │
└────────────────────────────────────────────────────────────────────┘
```

### Quality Service

```
┌────────────────────────────────────────────────────────────────┐
│                 ContentQualityAnalyzer                         │
├────────────────────────────────────────────────────────────────┤
│ Attributes:                                                    │
│  • REQUIRED_KEYS: List[str] = ["title", "description",         │
│    "subject", "creator", "language", "type", "identifier"]     │
├────────────────────────────────────────────────────────────────┤
│ Constants:                                                     │
│  • METADATA_WEIGHT = 0.6                                       │
│  • READABILITY_WEIGHT = 0.4                                    │
│  • READING_EASE_MIN = 0.0                                      │
│  • READING_EASE_MAX = 100.0                                    │
│  • CREDIBILITY_HIGH = 0.9                                      │
│  • CREDIBILITY_MEDIUM = 0.7                                    │
│  • CREDIBILITY_DEFAULT = 0.6                                   │
│  • DEPTH_THRESHOLD_MINIMAL = 100                               │
│  • DEPTH_THRESHOLD_SHORT = 500                                 │
│  • DEPTH_THRESHOLD_MEDIUM = 2000                               │
├────────────────────────────────────────────────────────────────┤
│ Methods:                                                       │
│  • metadata_completeness(resource) → float                     │
│  • text_readability(text) → Dict[str, float]                   │
│  • overall_quality(resource, text) → float                     │
│  • quality_level(score) → str                                  │
│  • source_credibility(source) → float                          │
│  • content_depth(text) → float                                 │
└────────────────────────────────────────────────────────────────┘
                            │
                            │ used by
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                      QualityService                            │
├────────────────────────────────────────────────────────────────┤
│ Attributes:                                                    │
│  • db: Session                                                 │
│  • quality_version: str = "v2.0"                               │
├────────────────────────────────────────────────────────────────┤
│ Constants:                                                     │
│  • HIGH_QUALITY_THRESHOLD = 0.8                                │
│  • MEDIUM_QUALITY_THRESHOLD = 0.5                              │
│  • DEFAULT_QUALITY_WEIGHTS = {...}                             │
│  • COMPLETENESS_FIELD_WEIGHT = 0.2                             │
│  • DEGRADATION_THRESHOLD = 0.2                                 │
│  • OUTLIER_MIN_RESOURCES = 10                                  │
│  • OUTLIER_CONTAMINATION = 0.1                                 │
│  • OUTLIER_THRESHOLD_LOW = 0.3                                 │
├────────────────────────────────────────────────────────────────┤
│ Public Methods:                                                │
│  • compute_quality(resource_id, weights) → QualityScore        │
│  • monitor_quality_degradation(days) → List[Dict]              │
│  • detect_quality_outliers(batch_size) → int                   │
├────────────────────────────────────────────────────────────────┤
│ Private Methods:                                               │
│  • _compute_accuracy_dimension(resource) → float               │
│  • _compute_completeness_dimension(resource) → float           │
│  • _compute_consistency_dimension(resource) → float            │
│  • _compute_timeliness_dimension(resource) → float             │
│  • _compute_relevance_dimension(resource) → float              │
│  • _update_resource_quality_fields(resource, ...) → None       │
│  • _identify_outlier_reasons(resource) → List[str]             │
└────────────────────────────────────────────────────────────────┘
```

### Recommendation Service (Strategy Pattern)

```
                    ┌──────────────────────────────┐
                    │  RecommendationStrategy      │
                    │  (Abstract Base Class)       │
                    ├──────────────────────────────┤
                    │ + generate(user_id, limit)   │
                    │   → List[Recommendation]     │
                    └──────────────┬───────────────┘
                                   │
                                   │ implements
              ┌────────────────────┼────────────────────┬────────────────┐
              │                    │                    │                │
    ┌─────────▼──────────┐  ┌──────▼────────┐    ┌──────▼────────┐   ┌───▼──────┐
    │ Collaborative      │  │  Content      │    │   Graph       │   │  Hybrid  │
    │ FilteringStrategy  │  │  BasedStrategy│    │BasedStrategy  │   │ Strategy │
    ├────────────────────┤  ├───────────────┤    ├───────────────┤   ├──────────┤
    │• db: Session       │  │• db: Session  │    │• db: Session  │   │• strats  │
    ├────────────────────┤  ├───────────────┤    ├───────────────┤   │• weights │
    │+ generate()        │  │+ generate()   │    │+ generate()   │   ├──────────┤
    │- _build_matrix()   │  │- _build_prof()│    │- _traverse()  │   │+ generate│
    │- _find_similar()   │  │- _compute_sim │    │- _score_path()│   │- _merge()│
    └────────────────────┘  └───────────────┘    └───────────────┘   └──────────┘
```

```
RecommendationService
├── Public Functions:
│   ├── get_graph_based_recommendations(db, resource_id, limit=10)
│   ├── generate_recommendations_with_graph_fusion(db, resource_id, ...)
│   ├── generate_recommendations(db, resource_id, limit, strategy, user_id)
│   ├── generate_user_profile_vector(db, user_id) → List[float]
│   ├── recommend_based_on_annotations(db, user_id, limit) → List[Dict]
│   └── get_top_subjects(db, limit=10) → List[str]
├── Private Functions:
│   ├── _cosine_similarity(vec1, vec2) → float
│   ├── _convert_subjects_to_vector(subjects) → List[float]
│   └── _to_numpy_vector(data) → List[float]

RecommendationStrategyFactory
├── Methods:
│   └── create(strategy_type: str, db: Session) → RecommendationStrategy
```

### Search Service

```
┌────────────────────────────────────────────────────────────────┐
│                   AdvancedSearchService                        │
├────────────────────────────────────────────────────────────────┤
│ Public Methods:                                                │
│  • hybrid_search(db, query, weight) → (resources, total, ...)  │
│  • fts_search(db, query, filters, ...) → (resources, ...)      │
│  • vector_search(db, query_text, ...) → (resources, ...)       │
│  • parse_search_query(query: str) → str                        │
│  • generate_snippets(text, query, max_len) → str               │
│                                                                │
│ Private Methods:                                               │
│  • _analyze_query(query) → Dict[str, Any]                      │
│  • _search_sparse(db, query_text, limit) → List[Tuple]         │
│  • _fetch_resources_ordered(db, ids, filters) → List[Res]      │
│  • _compute_facets(db, query) → Facets                         │
└────────────────────────────────────────────────────────────────┘
                            │
                            │ uses
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                     HybridSearchQuery                          │
├────────────────────────────────────────────────────────────────┤
│ Attributes:                                                    │
│  • db: Session                                                 │
│  • query: DomainSearchQuery                                    │
│  • enable_reranking: bool                                      │
│  • adaptive_weighting: bool                                    │
│  • _diagnostics: Dict[str, Any]                                │
├────────────────────────────────────────────────────────────────┤
│ Public Methods:                                                │
│  • execute() → Tuple[List[Resource], int, Facets, ...]         │
│  • get_diagnostic_info() → Dict[str, Any]                      │
├────────────────────────────────────────────────────────────────┤
│ Private Methods:                                               │
│  • _convert_to_schema_filters() → SearchFilters | None         │
│  • _ensure_tables_exist() → None                               │
│  • _check_services_available() → bool                          │
│  • _fallback_to_two_way_hybrid(start_time) → Tuple[...]        │
│  • _analyze_query() → Dict[str, Any]                           │
│  • _execute_retrieval_phase() → RetrievalCandidates            │
│  • _execute_fusion_phase(candidates) → FusedCandidates         │
│  • _execute_reranking_phase(fused) → List[Tuple[str, float]]   │
│  • _search_fts5() → List[Tuple[str, float]]                    │
│  • _search_dense() → List[Tuple[str, float]]                   │
│  • _search_sparse() → List[Tuple[str, float]]                  │
│  • _compute_weights() → List[float]                            │
│  • _compute_method_contributions(...) → Dict[str, int]         │
│  • _fetch_paginated_resources(fused) → List[Resource]          │
│  • _compute_facets(fused) → Facets                             │
│  • _generate_snippets(resources) → Dict[str, str]              │
└────────────────────────────────────────────────────────────────┘
```

### Search Pipeline Data Structures

```
┌────────────────────────────────────────────────────────────────┐
│                   RetrievalCandidates                          │
├────────────────────────────────────────────────────────────────┤
│ Attributes:                                                    │
│  • fts5_results: List[Tuple[str, float]]                       │
│  • dense_results: List[Tuple[str, float]]                      │
│  • sparse_results: List[Tuple[str, float]]                     │
│  • retrieval_time_ms: float                                    │
│  • method_times_ms: Dict[str, float]                           │
├────────────────────────────────────────────────────────────────┤
│ Methods:                                                       │
│  • get_all_candidate_ids() → set[str]                          │
│  • get_method_counts() → Dict[str, int]                        │
└────────────────────────────────────────────────────────────────┘
                            │
                            │ feeds into
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                     FusedCandidates                            │
├────────────────────────────────────────────────────────────────┤
│ Attributes:                                                    │
│  • fused_results: List[Tuple[str, float]]                      │
│  • weights_used: List[float]                                   │
│  • fusion_time_ms: float                                       │
│  • method_contributions: Dict[str, int]                        │
├────────────────────────────────────────────────────────────────┤
│ Methods:                                                       │
│  • get_top_k(k: int) → List[Tuple[str, float]]                 │
│  • get_candidate_ids() → List[str]                             │
└────────────────────────────────────────────────────────────────┘
```

---

## Domain Layer Architecture (Phase 11)

```
┌─────────────────────────────────────────────────────────────────────────┐
│            DOMAIN-DRIVEN DESIGN (DDD) REFACTORING                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                   ┌──────────────────────────┐                          │
│                   │  BaseDomainObject (ABC)  │                          │
│                   ├──────────────────────────┤                          │
│                   │ + to_dict()              │                          │
│                   │ + from_dict()            │                          │
│                   │ + to_json()              │                          │
│                   │ + from_json()            │                          │
│                   │ + validate() [abstract]  │                          │
│                   │ + __eq__()               │                          │
│                   │ + __repr__()             │                          │
│                   └────────┬─────────────────┘                          │
│                            │                                            │
│              ┌─────────────┴──────────────┐                             │
│              │                            │                             │
│    ┌─────────▼──────────┐      ┌──────────▼──────────┐                  │
│    │   ValueObject      │      │   DomainEntity      │                  │
│    │   (dataclass)      │      │                     │                  │
│    ├────────────────────┤      ├─────────────────────┤                  │
│    │ Immutable          │      │ • entity_id: str    │                  │
│    │ Defined by values  │      │ Identity-based      │                  │
│    │ No identity        │      │ Mutable             │                  │
│    └─────────┬──────────┘      └─────────────────────┘                  │
│              │                                                          │
│              │ subclasses                                               │
│              │                                                          │
│    ┌─────────┼─────────┬─────────────┬─────────────┬─────────────┐      │
│    │         │         │             │             │             │      │
│    ▼         ▼         ▼             ▼             ▼             ▼      │
│ ┌──────┐ ┌──────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│ │Class-│ │Class-│ │ Quality  │ │Recommend-│ │ Search   │ │ Search   │   │
│ │ifica-│ │ifica-│ │  Score   │ │  ation   │ │  Query   │ │ Result   │   │
│ │tion  │ │tion  │ │          │ │  Score   │ │          │ │          │   │
│ │Predic│ │Result│ │          │ │          │ │          │ │          │   │
│ │tion  │ │      │ │          │ │          │ │          │ │          │   │
│ └──────┘ └──────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Domain Objects


#### Classification Domain

```
┌──────────────────────────────────────────────────────────────┐
│         ClassificationPrediction (ValueObject)               │
├──────────────────────────────────────────────────────────────┤
│ Attributes:                                                  │
│  • taxonomy_id: str                                          │
│  • confidence: float (0.0-1.0)                               │
│  • rank: int (1-based)                                       │
├──────────────────────────────────────────────────────────────┤
│ Methods:                                                     │
│  • validate()                                                │
│  • is_high_confidence(threshold=0.8) → bool                  │
│  • is_low_confidence(threshold=0.5) → bool                   │
│  • is_medium_confidence(low, high) → bool                    │ 
└──────────────────────────────────────────────────────────────┘
                             │
                             │ contains multiple
                             ▼
┌──────────────────────────────────────────────────────────────┐
│         ClassificationResult (ValueObject)                   │
├──────────────────────────────────────────────────────────────┤
│ Attributes:                                                  │
│  • predictions: List[ClassificationPrediction]               │
│  • model_version: str                                        │
│  • inference_time_ms: float                                  │
│  • resource_id: Optional[str]                                │
├──────────────────────────────────────────────────────────────┤
│ Methods:                                                     │
│  • validate()                                                │
│  • get_high_confidence(threshold) → List[Prediction]         │
│  • get_top_k(k) → List[Prediction]                           │
│  • get_best_prediction() → Prediction                        │
│  • count_by_confidence_level() → Dict[str, int]              │
│  • to_dict() → Dict[str, Any]                                │
│  • from_dict(data) → ClassificationResult                    │
└──────────────────────────────────────────────────────────────┘
```

#### Quality Domain

```
┌──────────────────────────────────────────────────────────────┐
│              QualityScore (ValueObject)                      │
├──────────────────────────────────────────────────────────────┤
│ Attributes (5 Dimensions):                                   │
│  • accuracy: float (0.0-1.0)        Weight: 0.30             │
│  • completeness: float (0.0-1.0)    Weight: 0.25             │
│  • consistency: float (0.0-1.0)     Weight: 0.20             │
│  • timeliness: float (0.0-1.0)      Weight: 0.15             │
│  • relevance: float (0.0-1.0)       Weight: 0.15             │
├──────────────────────────────────────────────────────────────┤
│ Methods:                                                     │
│  • validate()                                                │
│  • overall_score() → float                                   │
│  • is_high_quality(threshold=0.7) → bool                     │
│  • is_low_quality(threshold=0.5) → bool                      │
│  • get_quality_level() → str ("high"/"medium"/"low")         │
│  • get_weakest_dimension() → str                             │
│  • get_strongest_dimension() → str                           │
│  • get_dimension_scores() → Dict[str, float]                 │
│  • has_dimension_below_threshold(t) → bool                   │
│  • count_dimensions_below_threshold(t) → int                 │
│  • to_dict() → Dict[str, Any]                                │
│  • from_dict(data) → QualityScore                            │
└──────────────────────────────────────────────────────────────┘
```

#### Recommendation Domain

```
┌──────────────────────────────────────────────────────────────┐
│         RecommendationScore (ValueObject)                    │
├──────────────────────────────────────────────────────────────┤
│ Attributes:                                                  │
│  • score: float (0.0-1.0)                                    │
│  • confidence: float (0.0-1.0)                               │
│  • rank: int (1-based)                                       │
├──────────────────────────────────────────────────────────────┤
│ Methods:                                                     │
│  • validate()                                                │
│  • is_high_confidence(threshold=0.8) → bool                  │
│  • is_high_score(threshold=0.7) → bool                       │
│  • is_top_ranked(top_k=5) → bool                             │
│  • combined_quality() → float                                │
└──────────────────────────────────────────────────────────────┘
                             │
                             │ embedded in
                             ▼
┌──────────────────────────────────────────────────────────────┐
│              Recommendation (ValueObject)                    │
├──────────────────────────────────────────────────────────────┤
│ Attributes:                                                  │
│  • resource_id: str                                          │
│  • user_id: str                                              │
│  • recommendation_score: RecommendationScore                 │
│  • strategy: str = "unknown"                                 │
│  • reason: Optional[str]                                     │
│  • metadata: Optional[Dict[str, Any]]                        │
├──────────────────────────────────────────────────────────────┤
│ Methods:                                                     │
│  • validate()                                                │
│  • get_score() → float                                       │
│  • get_confidence() → float                                  │
│  • get_rank() → int                                          │
│  • is_high_quality(score_t, conf_t) → bool                   │
│  • is_top_recommendation(top_k=5) → bool                     │
│  • get_metadata_value(key, default) → Any                    │
│  • __lt__, __le__, __gt__, __ge__ (for sorting)              │
│  • to_dict() → Dict[str, Any]                                │
│  • from_dict(data) → Recommendation                          │
└──────────────────────────────────────────────────────────────┘
```

#### Search Domain

```
┌──────────────────────────────────────────────────────────────┐
│              SearchQuery (ValueObject)                       │
├──────────────────────────────────────────────────────────────┤
│ Attributes:                                                  │
│  • query_text: str                                           │
│  • limit: int = 20                                           │
│  • enable_reranking: bool = True                             │
│  • adaptive_weights: bool = True                             │
│  • search_method: str = "hybrid"                             │
├──────────────────────────────────────────────────────────────┤
│ Methods:                                                     │
│  • validate()                                                │
│  • is_short_query(threshold=3) → bool                        │
│  • is_long_query(threshold=10) → bool                        │
│  • is_medium_query(short, long) → bool                       │
│  • get_word_count() → int                                    │
│  • is_single_word() → bool                                   │
│  • get_query_length() → int                                  │
└──────────────────────────────────────────────────────────────┘
                             │
                             │ produces
                             ▼
┌──────────────────────────────────────────────────────────────┐
│              SearchResults (ValueObject)                     │
├──────────────────────────────────────────────────────────────┤
│ Attributes:                                                  │
│  • results: List[SearchResult]                               │
│  • query: SearchQuery                                        │
│  • total_results: int                                        │
│  • search_time_ms: float                                     │
│  • reranked: bool = False                                    │
├──────────────────────────────────────────────────────────────┤
│ Methods:                                                     │
│  • validate()                                                │
│  • get_top_k(k) → List[SearchResult]                         │
│  • get_by_score_threshold(t) → List[SearchResult]            │
│  • is_empty() → bool                                         │
│  • has_results() → bool                                      │
└──────────────────────────────────────────────────────────────┘
```

---

## Refactoring Framework Architecture (Phase 12)

The refactoring framework implements Fowler's refactoring patterns with automated code smell detection and validation.

### Refactoring Models

```
SmellType (Enum)
├── Values:
│   ├── DUPLICATED_CODE
│   ├── LONG_FUNCTION
│   ├── LARGE_CLASS
│   ├── GLOBAL_DATA
│   ├── FEATURE_ENVY
│   ├── DATA_CLUMPS
│   ├── PRIMITIVE_OBSESSION
│   ├── REPEATED_SWITCHES
│   ├── DATA_CLASS
│   └── LONG_PARAMETER_LIST

Severity (Enum)
├── Values:
│   ├── HIGH (blocks production)
│   ├── MEDIUM (technical debt)
│   └── LOW (minor improvement)

RefactoringTechnique (Enum)
├── Values:
│   ├── EXTRACT_FUNCTION
│   ├── EXTRACT_CLASS
│   ├── REPLACE_PRIMITIVE_WITH_OBJECT
│   ├── COMBINE_FUNCTIONS_INTO_CLASS
│   ├── SEPARATE_QUERY_FROM_MODIFIER
│   ├── ENCAPSULATE_COLLECTION
│   ├── SPLIT_PHASE
│   ├── REPLACE_CONDITIONAL_WITH_POLYMORPHISM
│   ├── MOVE_FUNCTION
│   └── INLINE_FUNCTION
```

### Refactoring Data Classes

```
Location (dataclass)
├── Attributes:
│   ├── file_path: Path
│   ├── start_line: int
│   ├── end_line: int
│   ├── function_name: Optional[str]
│   └── class_name: Optional[str]

CodeSmell (dataclass)
├── Attributes:
│   ├── smell_type: SmellType
│   ├── severity: Severity
│   ├── location: Location
│   ├── description: str
│   ├── suggested_technique: RefactoringTechnique
│   └── metrics: Dict[str, Any]

SmellReport (dataclass)
├── Attributes:
│   ├── file_path: Path
│   ├── smells: List[CodeSmell]
│   ├── total_lines: int
│   ├── complexity_score: float
│   └── timestamp: str
├── Methods:
│   ├── high_priority_smells() → List[CodeSmell]
│   ├── smells_by_type(smell_type) → List[CodeSmell]
│   └── summary() → str

RefactoringResult (dataclass)
├── Attributes:
│   ├── success: bool
│   ├── original_code: str
│   ├── refactored_code: str
│   ├── technique_applied: RefactoringTechnique
│   ├── changes_made: List[str]
│   └── test_results: Optional[TestResults]

TestResults (dataclass)
├── Attributes:
│   ├── total_tests: int
│   ├── passed: int
│   ├── failed: int
│   ├── errors: List[str]
│   ├── coverage_percentage: float
│   └── execution_time_seconds: float
├── Methods:
│   ├── all_passed() → bool
│   ├── coverage_acceptable(threshold=0.85) → bool
│   └── summary() → str
```

### Refactoring Detector

```
┌────────────────────────────────────────────────────────────────┐
│                    CodeSmellDetector                           │
├────────────────────────────────────────────────────────────────┤
│ Attributes:                                                    │
│  • function_checker: FunctionLengthChecker                     │
│  • class_checker: ClassSizeChecker                             │
│  • type_hint_checker: TypeHintCoverageChecker                  │
│  • duplication_detector: CodeDuplicationDetector               │
├────────────────────────────────────────────────────────────────┤
│ Public Methods:                                                │
│  • analyze_file(file_path: Path) → SmellReport                 │
│  • analyze_directory(dir_path: Path) → List[SmellReport]       │
│  • prioritize_smells(reports) → PrioritizedSmells              │
│  • generate_summary_report(reports) → str                      │
├────────────────────────────────────────────────────────────────┤
│ Private Methods:                                               │
│  • _detect_feature_envy(file_path) → List[CodeSmell]           │
│  • _detect_long_parameter_lists(file_path) → List[CodeSmell]   │
│  • _count_lines(file_path) → int                               │
│  • _calculate_complexity(file_path) → float                    │
└────────────────────────────────────────────────────────────────┘
```

### Refactoring Validators

```
FunctionLengthChecker
├── Constants: MAX_FUNCTION_LINES = 50
├── Methods:
│   ├── check_file(file_path: Path) → List[CodeSmell]
│   ├── _extract_functions(tree, source) → List[FunctionInfo]
│   └── _create_smell(file_path, func) → CodeSmell

ClassSizeChecker
├── Constants: MAX_CLASS_LINES = 200, MAX_METHODS = 10
├── Methods:
│   ├── check_file(file_path: Path) → List[CodeSmell]
│   ├── _extract_classes(tree, source) → List[ClassInfo]
│   └── _create_smell(file_path, cls) → CodeSmell

TypeHintCoverageChecker
├── Constants: MIN_TYPE_HINT_COVERAGE = 1.0
├── Methods:
│   ├── check_file(file_path: Path) → Tuple[float, List[CodeSmell]]
│   └── _has_complete_type_hints(node) → bool

CodeDuplicationDetector
├── Constants: DUPLICATION_SIMILARITY_THRESHOLD = 0.8
├── Methods:
│   ├── check_files(file_paths: List[Path]) → List[CodeSmell]
│   ├── _extract_function_bodies(tree, source) → List[Tuple]
│   └── _calculate_similarity(body1, body2) → float
```

---

## Router Layer Architecture

The router layer provides FastAPI endpoints for all services, implementing REST API patterns.

### Main Routers

```
Classification Router (/api/classification)
├── Endpoints:
│   ├── POST /classify
│   │   ├── Input: ClassifyRequest (text, top_k)
│   │   └── Output: ClassificationResult
│   ├── POST /fine-tune
│   │   ├── Input: FineTuneRequest (labeled_data, epochs, batch_size)
│   │   └── Output: TrainingMetrics
│   └── GET /metrics
│       └── Output: ModelMetrics

Quality Router (/api/quality)
├── Endpoints:
│   ├── POST /compute/{resource_id}
│   │   ├── Input: Optional[QualityWeights]
│   │   └── Output: QualityScore
│   ├── GET /monitor/degradation
│   │   ├── Query: time_window_days
│   │   └── Output: List[DegradationReport]
│   └── POST /detect/outliers
│       ├── Query: batch_size
│       └── Output: OutlierDetectionResult

Recommendation Router (/api/recommendations)
├── Endpoints:
│   ├── GET /user/{user_id}
│   │   ├── Query: limit, strategy
│   │   └── Output: List[Recommendation]
│   ├── GET /resource/{resource_id}
│   │   ├── Query: limit
│   │   └── Output: List[Recommendation]
│   └── GET /graph/{resource_id}
│       ├── Query: limit, graph_weight
│       └── Output: List[Recommendation]

Search Router (/api/search)
├── Endpoints:
│   ├── POST /hybrid
│   │   ├── Input: HybridSearchRequest
│   │   └── Output: SearchResults with facets
│   ├── GET /fts
│   │   ├── Query: q, filters, limit, offset
│   │   └── Output: SearchResults
│   └── GET /vector
│       ├── Query: q, limit, offset
│       └── Output: SearchResults
```

---

## Creating a New Module

1. Create module directory:
```bash
mkdir -p app/modules/new_module
```

2. Create module files:
```python
# __init__.py
from .router import router
from .service import create_item, get_item
from .schema import ItemCreate, ItemResponse
from .model import Item

__version__ = "1.0.0"
__domain__ = "new_module"
```

3. Register router in main.py:
```python
from app.modules.new_module import router as new_module_router
app.include_router(new_module_router, prefix="/new-module", tags=["new-module"])
```

4. Register event handlers:
```python
# In handlers.py
from app.shared.event_bus import event_bus

def register_handlers():
    event_bus.subscribe("some.event", handle_some_event)

# Call in __init__.py or main.py
register_handlers()
```

---

## Module Isolation Rules

1. **No cross-module imports** - Use events or shared kernel
2. **String-based relationships** - Avoid circular imports in models
3. **Independent testing** - Each module has its own tests
4. **Clear public interface** - Export only what's needed in `__init__.py`
5. **Self-contained migrations** - Module-specific schema changes

---

## Legacy Services Migration Status

Services being migrated to modules:

| Service | Target Module | Status |
|---------|---------------|--------|
| `resource_service.py` | Resources | ✅ Complete |
| `collection_service.py` | Collections | ✅ Complete |
| `search_service.py` | Search | ✅ Complete |
| `taxonomy_service.py` | Taxonomy | 🔄 Planned |
| `annotation_service.py` | Annotations | 🔄 Planned |
| `quality_service.py` | Quality | 🔄 Planned |
| `graph_service.py` | Graph | 🔄 Planned |
| `recommendation_service.py` | Recommendations | 🔄 Planned |

---

## Schema Layer Architecture

The schema layer defines Pydantic models for API request/response validation.

```
SearchQuery (Pydantic)
├── Attributes:
│   ├── text: str
│   ├── limit: int = 20
│   ├── offset: int = 0
│   ├── hybrid_weight: float = 0.5
│   ├── filters: Optional[SearchFilters]
│   └── sort_by: Optional[str]

SearchFilters (Pydantic)
├── Attributes:
│   ├── classification_code: Optional[List[str]]
│   ├── type: Optional[List[str]]
│   ├── language: Optional[List[str]]
│   ├── year_min: Optional[int]
│   └── year_max: Optional[int]

ResourceCreate (Pydantic)
├── Attributes:
│   ├── title: str
│   ├── description: Optional[str]
│   ├── creator: Optional[str]
│   ├── subject: Optional[List[str]]
│   ├── type: str
│   ├── language: str
│   └── identifier: str

ResourceUpdate (Pydantic)
├── Attributes:
│   ├── title: Optional[str]
│   ├── description: Optional[str]
│   ├── creator: Optional[str]
│   ├── subject: Optional[List[str]]
│   └── classification_code: Optional[str]

ClassifyRequest (Pydantic)
├── Attributes:
│   ├── text: str
│   └── top_k: int = 5

AnnotationCreate (Pydantic)
├── Attributes:
│   ├── resource_id: UUID
│   ├── content: str
│   ├── annotation_type: str
│   ├── start_position: Optional[int]
│   ├── end_position: Optional[int]
│   └── tags: Optional[List[str]]

RecommendationRequest (Pydantic)
├── Attributes:
│   ├── user_id: str
│   ├── limit: int = 10
│   └── strategy: str = "hybrid"
```

---

## Configuration Layer Architecture

The configuration layer manages application settings and environment variables.

```
Settings (Pydantic BaseSettings)
├── Attributes:
│   ├── DATABASE_URL: str
│   ├── SECRET_KEY: str
│   ├── API_VERSION: str = "v2.0"
│   ├── DEBUG: bool = False
│   ├── LOG_LEVEL: str = "INFO"
│   ├── CORS_ORIGINS: List[str]
│   ├── MAX_UPLOAD_SIZE: int
│   ├── EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
│   ├── CLASSIFICATION_MODEL: str = "distilbert-base-uncased"
│   ├── ENABLE_GPU: bool = True
│   ├── CACHE_TTL: int = 3600
│   └── RATE_LIMIT: int = 100
├── Methods:
│   ├── get_database_url() → str
│   ├── is_production() → bool
│   └── validate_settings() → None

get_settings()
├── Returns: Settings (singleton)
└── Usage: settings = get_settings()
```

---

## Utility Layer Architecture

The utility layer provides helper functions and shared utilities across the application.

### Text Processing Utilities

```
text_processor module
├── Functions:
│   ├── readability_scores(text: str) -> Dict[str, float]
│   │   ├── Returns: flesch_reading_ease, flesch_kincaid_grade, etc.
│   │   └── Uses: textstat library
│   ├── extract_keywords(text: str, top_k: int) -> List[str]
│   │   ├── Returns: List of top keywords
│   │   └── Uses: TF-IDF or RAKE
│   ├── clean_text(text: str) -> str
│   │   ├── Removes: HTML tags, special characters
│   │   └── Returns: Cleaned text
│   ├── tokenize(text: str) -> List[str]
│   │   └── Returns: List of tokens
│   └── normalize_text(text: str) -> str
│       ├── Lowercases, removes punctuation
│       └── Returns: Normalized text

content_extractor module
├── Functions:
│   ├── extract_from_pdf(file_path: Path) -> str
│   │   └── Uses: PyPDF2 or pdfplumber
│   ├── extract_from_html(html: str) -> str
│   │   └── Uses: BeautifulSoup
│   ├── extract_metadata(file_path: Path) -> Dict[str, Any]
│   │   └── Returns: Title, author, date, etc.
│   └── extract_citations(text: str) -> List[str]
│       └── Returns: List of citation strings
```

### Performance Monitoring Utilities

```
performance_monitoring module
├── Classes:
│   └── PerformanceMonitor
│       ├── Attributes:
│       │   ├── metrics: Dict[str, List[float]]
│       │   └── start_times: Dict[str, float]
│       ├── Methods:
│       │   ├── start_timer(name: str) -> None
│       │   ├── stop_timer(name: str) -> float
│       │   ├── record_metric(name: str, value: float) -> None
│       │   ├── get_average(name: str) -> float
│       │   ├── get_percentile(name: str, percentile: float) -> float
│       │   └── get_summary() -> Dict[str, Any]
│
├── Decorators:
│   ├── @time_function
│   │   └── Measures function execution time
│   └── @log_performance
│       └── Logs performance metrics

recommendation_metrics module
├── Functions:
│   ├── precision_at_k(predictions, ground_truth, k) -> float
│   ├── recall_at_k(predictions, ground_truth, k) -> float
│   ├── ndcg_at_k(predictions, ground_truth, k) -> float
│   ├── mean_average_precision(predictions, ground_truth) -> float
│   └── hit_rate_at_k(predictions, ground_truth, k) -> float
```

---

## ML Monitoring Architecture

The ML monitoring layer provides observability for machine learning models and predictions.

```
PredictionMonitor
├── Attributes:
│   ├── predictions: List[Dict[str, Any]]
│   ├── metrics: Dict[str, float]
│   └── alert_thresholds: Dict[str, float]
├── Methods:
│   ├── __init__()
│   ├── log_prediction(model_name, input_data, prediction, confidence, latency_ms) -> None
│   ├── get_metrics(window_minutes: int) -> Dict[str, Any]
│   ├── get_prediction_distribution() -> Dict[str, int]
│   ├── get_average_confidence() -> float
│   ├── get_average_latency() -> float
│   ├── check_drift(baseline_distribution) -> bool
│   └── export_metrics() -> Dict[str, Any]

AlertManager
├── Attributes:
│   ├── alerts: List[Alert]
│   └── notification_channels: List[NotificationChannel]
├── Methods:
│   ├── __init__()
│   ├── create_alert(alert_type, severity, message, metadata) -> Alert
│   ├── check_thresholds(metrics: Dict[str, float]) -> List[Alert]
│   ├── send_notification(alert: Alert) -> None
│   └── get_active_alerts() -> List[Alert]

HealthCheck
├── Methods:
│   ├── check_model_health(model_name: str) -> Dict[str, Any]
│   ├── check_database_health() -> Dict[str, Any]
│   ├── check_service_health(service_name: str) -> Dict[str, Any]
│   └── get_system_health() -> Dict[str, Any]

JSONLogging
├── Functions:
│   ├── setup_json_logging(log_level: str) -> None
│   ├── log_structured(level, message, **kwargs) -> None
│   └── get_logger(name: str) -> logging.Logger
```

---

## Complete System Flow Diagrams

### Classification Flow

```
User Request
    ↓
FastAPI Router (POST /api/classification/classify)
    ↓
MLClassificationService.predict(text, top_k)
    ↓
    ├─→ _load_model() [if not loaded]
    │   ├─→ _import_ml_libraries()
    │   ├─→ _load_tokenizer()
    │   ├─→ _determine_checkpoint_path()
    │   ├─→ _load_model_from_checkpoint()
    │   └─→ _move_model_to_device()
    │
    ├─→ Tokenize input text
    ├─→ Model inference (forward pass)
    ├─→ Apply sigmoid activation
    ├─→ Sort by confidence
    ├─→ Take top_k predictions
    │
    └─→ Create ClassificationResult domain object
        ├─→ ClassificationPrediction objects
        └─→ Validate all predictions
    ↓
PredictionMonitor.log_prediction()
    ↓
Return ClassificationResult
    ↓
Convert to JSON response
    ↓
User receives predictions
```

### Quality Assessment Flow

```
User Request
    ↓
FastAPI Router (POST /api/quality/compute/{resource_id})
    ↓
QualityService.compute_quality(resource_id, weights)
    ↓
    ├─→ Validate weights
    ├─→ Query Resource from database
    │
    ├─→ _compute_accuracy_dimension(resource)
    ├─→ _compute_completeness_dimension(resource)
    ├─→ _compute_consistency_dimension(resource)
    ├─→ _compute_timeliness_dimension(resource)
    └─→ _compute_relevance_dimension(resource)
    ↓
Create QualityScore domain object
    ├─→ Validate all dimensions (0.0-1.0)
    └─→ Calculate overall_score()
    ↓
_update_resource_quality_fields(resource, ...)
    ↓
Database commit
    ↓
Return QualityScore
    ↓
Convert to JSON response
    ↓
User receives quality assessment
```

### Recommendation Flow (Strategy Pattern)

```
User Request
    ↓
FastAPI Router (GET /api/recommendations/user/{user_id})
    ↓
generate_recommendations(db, resource_id, limit, strategy, user_id)
    ↓
RecommendationStrategyFactory.create(strategy_type, db)
    ↓
    ├─→ strategy="collaborative" → CollaborativeFilteringStrategy
    ├─→ strategy="content" → ContentBasedStrategy
    ├─→ strategy="graph" → GraphBasedStrategy
    └─→ strategy="hybrid" → HybridStrategy
    ↓
Strategy.generate(user_id, limit)
    ↓
    [CollaborativeFilteringStrategy]
    ├─→ _build_user_item_matrix()
    ├─→ Compute user similarities
    ├─→ Generate predictions
    └─→ Create Recommendation objects
    
    [ContentBasedStrategy]
    ├─→ Query UserInteraction
    ├─→ _build_user_profile(interactions)
    ├─→ Query Resources with embeddings
    ├─→ _compute_similarity(profile, embedding)
    └─→ Create Recommendation objects
    
    [GraphBasedStrategy]
    ├─→ _traverse_citation_network(resource_id, depth)
    ├─→ Score by citation distance
    └─→ Create Recommendation objects
    
    [HybridStrategy]
    ├─→ Execute all sub-strategies
    ├─→ _merge_recommendations(results, weights)
    └─→ Create Recommendation objects
    ↓
Return List[Recommendation]
    ↓
Convert to List[Dict] for API compatibility
    ↓
User receives recommendations
```

### Search Flow (Three-Way Hybrid)

```
User Request
    ↓
FastAPI Router (POST /api/search/three-way)
    ↓
HybridSearchQuery(db, query, enable_reranking, adaptive_weights)
    ↓
execute()
    ↓
    ├─→ _ensure_tables_exist()
    ├─→ _check_services_available()
    ├─→ _analyze_query() → query characteristics
    │
    ├─→ PHASE 1: _execute_retrieval_phase()
    │   ├─→ _search_fts5() → FTS5 keyword results
    │   ├─→ _search_dense() → Dense vector results
    │   └─→ _search_sparse() → Sparse vector results
    │   └─→ Return RetrievalCandidates
    │
    ├─→ PHASE 2: _execute_fusion_phase(candidates)
    │   ├─→ _compute_weights() → adaptive RRF weights
    │   ├─→ ReciprocalRankFusionService.fuse_results()
    │   ├─→ _compute_method_contributions()
    │   └─→ Return FusedCandidates
    │
    ├─→ PHASE 3: _execute_reranking_phase(fused)
    │   ├─→ RerankingService.rerank() [if enabled]
    │   └─→ Return final ranked results
    │
    ├─→ _fetch_paginated_resources(results)
    ├─→ _compute_facets(results)
    └─→ _generate_snippets(resources)
    ↓
Return (resources, total, facets, snippets, metadata)
    ↓
Convert to JSON response
    ↓
User receives search results
```

### Refactoring Detection Flow

```
Developer runs CLI
    ↓
refactoring.cli.detect_smells(directory_path)
    ↓
CodeSmellDetector()
    ├─→ Initialize validators:
    │   ├─→ FunctionLengthChecker()
    │   ├─→ ClassSizeChecker()
    │   ├─→ TypeHintCoverageChecker()
    │   └─→ CodeDuplicationDetector()
    ↓
analyze_directory(dir_path)
    ↓
    For each Python file:
    ├─→ analyze_file(file_path)
    │   ├─→ FunctionLengthChecker.check_file()
    │   │   ├─→ Parse AST
    │   │   ├─→ _extract_functions()
    │   │   ├─→ _analyze_function()
    │   │   └─→ _create_smell() if violation
    │   │
    │   ├─→ ClassSizeChecker.check_file()
    │   │   ├─→ Parse AST
    │   │   ├─→ _extract_classes()
    │   │   ├─→ _analyze_class()
    │   │   └─→ _create_smell() if violation
    │   │
    │   ├─→ TypeHintCoverageChecker.check_file()
    │   │   ├─→ Parse AST
    │   │   ├─→ _has_complete_type_hints()
    │   │   └─→ _create_smell() if missing
    │   │
    │   ├─→ _detect_feature_envy()
    │   ├─→ _detect_long_parameter_lists()
    │   ├─→ _count_lines()
    │   └─→ _calculate_complexity()
    │   ↓
    │   Return SmellReport
    │
    └─→ CodeDuplicationDetector.check_files(all_files)
        ├─→ _extract_function_bodies()
        ├─→ Compare all pairs
        ├─→ _calculate_similarity()
        └─→ _create_smell() if duplicate
    ↓
prioritize_smells(reports)
    ├─→ Sort by severity (HIGH, MEDIUM, LOW)
    └─→ Return PrioritizedSmells
    ↓
generate_summary_report(reports)
    ↓
Display results to developer
```

---

## Related Documentation

- [Architecture Overview](overview.md) - System design
- [Event System](event-system.md) - Event-driven communication
- [Database](database.md) - Schema and models
- [Design Decisions](decisions.md) - ADRs


<div style='page-break-after: always;'></div>

---



# 24. Architecture Decisions

*Source: `backend/docs/architecture/decisions.md`*

---

# Architecture Decision Records

Key architectural decisions for Neo Alexandria 2.0.

## ADR-001: Vertical Slice Architecture

**Status:** Accepted (Phase 13.5)

**Context:**
The original layered architecture (routers → services → models) led to:
- Tight coupling between components
- Circular import issues
- Difficult testing
- Hard to understand feature boundaries

**Decision:**
Adopt vertical slice architecture where each feature is a self-contained module with all layers.

**Consequences:**
- ✅ High cohesion within modules
- ✅ Low coupling between modules
- ✅ Easier to understand and test
- ✅ Modules can be extracted to microservices
- ⚠️ Some code duplication between modules
- ⚠️ Requires discipline to maintain boundaries

---

## ADR-002: Event-Driven Communication

**Status:** Accepted (Phase 12.5)

**Context:**
Direct service-to-service calls created:
- Circular dependencies
- Tight coupling
- Difficult to add new features

**Decision:**
Use publish-subscribe event bus for inter-module communication.

**Consequences:**
- ✅ Loose coupling between modules
- ✅ Easy to add new subscribers
- ✅ Supports async processing
- ⚠️ Eventual consistency (not immediate)
- ⚠️ Harder to trace execution flow
- ⚠️ Need to handle event failures

---

## ADR-003: Dual Database Support

**Status:** Accepted (Phase 13)

**Context:**
SQLite is convenient for development but has limitations:
- Single writer (no concurrent writes)
- No advanced indexing
- Not suitable for production

**Decision:**
Support both SQLite (development) and PostgreSQL (production) with automatic detection.

**Consequences:**
- ✅ Easy local development
- ✅ Production-grade database option
- ✅ Automatic configuration
- ⚠️ Must maintain compatibility
- ⚠️ Some features PostgreSQL-only
- ⚠️ Migration scripts needed

---

## ADR-004: Domain Objects for Business Logic

**Status:** Accepted (Phase 11)

**Context:**
Business logic was scattered across services with primitive types, making it hard to:
- Validate business rules
- Reuse logic
- Test in isolation

**Decision:**
Create domain objects (value objects, entities) to encapsulate business logic.

**Consequences:**
- ✅ Centralized validation
- ✅ Reusable business logic
- ✅ Self-documenting code
- ✅ Easier testing
- ⚠️ More classes to maintain
- ⚠️ Mapping between layers

---

## ADR-005: Hybrid Search Strategy

**Status:** Accepted (Phase 4, enhanced Phase 8)

**Context:**
Pure keyword search misses semantic meaning. Pure vector search misses exact matches.

**Decision:**
Implement hybrid search combining:
- FTS5 keyword search (BM25)
- Dense vector search (semantic)
- Sparse vector search (SPLADE) - Phase 8
- Reciprocal Rank Fusion for combining results

**Consequences:**
- ✅ Best of both approaches
- ✅ Configurable weighting
- ✅ Better search quality
- ⚠️ Higher latency
- ⚠️ More complex implementation
- ⚠️ Requires embedding generation

---

## ADR-006: Aggregate Embeddings for Collections

**Status:** Accepted (Phase 7)

**Context:**
Collections needed semantic representation for:
- Finding similar collections
- Recommending resources to add
- Collection-based search

**Decision:**
Compute aggregate embedding as normalized mean of member resource embeddings.

**Consequences:**
- ✅ Enables collection similarity
- ✅ Supports recommendations
- ✅ Simple algorithm
- ⚠️ Must recompute on membership changes
- ⚠️ Large collections may dilute signal

---

## ADR-007: Multi-Dimensional Quality Assessment

**Status:** Accepted (Phase 9)

**Context:**
Single quality score didn't capture different aspects of resource quality.

**Decision:**
Implement 5-dimensional quality assessment:
- Accuracy (30%)
- Completeness (25%)
- Consistency (20%)
- Timeliness (15%)
- Relevance (10%)

**Consequences:**
- ✅ Granular quality insights
- ✅ Actionable improvement suggestions
- ✅ Configurable weights
- ⚠️ More complex computation
- ⚠️ Requires more storage

---

## ADR-008: Strategy Pattern for Recommendations

**Status:** Accepted (Phase 10-11)

**Context:**
Different recommendation approaches work better for different scenarios.

**Decision:**
Use strategy pattern with multiple recommendation strategies:
- Collaborative filtering
- Content-based
- Graph-based
- Hybrid (combines all)

**Consequences:**
- ✅ Flexible recommendation system
- ✅ Easy to add new strategies
- ✅ Can tune per user/context
- ⚠️ More complex architecture
- ⚠️ Need to balance strategies

---

## ADR-009: Materialized Paths for Taxonomy

**Status:** Accepted (Phase 8.5)

**Context:**
Hierarchical taxonomy queries (ancestors, descendants) were slow with recursive queries.

**Decision:**
Use materialized path pattern storing full path in each node (e.g., `/science/computer-science/ml`).

**Consequences:**
- ✅ O(1) ancestor queries
- ✅ O(1) descendant queries via LIKE
- ✅ Simple breadcrumb generation
- ⚠️ Must update paths on move
- ⚠️ Path length limits

---

## ADR-010: Async Ingestion Pipeline

**Status:** Accepted (Phase 3.5)

**Context:**
Content ingestion involves slow operations:
- HTTP fetching
- PDF extraction
- AI summarization
- Embedding generation

**Decision:**
Make ingestion asynchronous with status tracking.

**Consequences:**
- ✅ Fast API response
- ✅ Can process in background
- ✅ Supports batch ingestion
- ⚠️ Need status polling
- ⚠️ Error handling complexity

---

## Decision Template

```markdown
## ADR-XXX: [Title]

**Status:** [Proposed | Accepted | Deprecated | Superseded]

**Context:**
[What is the issue that we're seeing that is motivating this decision?]

**Decision:**
[What is the change that we're proposing and/or doing?]

**Consequences:**
[What becomes easier or more difficult to do because of this change?]
- ✅ Positive consequence
- ⚠️ Trade-off or risk
```

## Related Documentation

- [Architecture Overview](overview.md) - System design
- [Modules](modules.md) - Vertical slice details
- [Event System](event-system.md) - Event-driven communication


<div style='page-break-after: always;'></div>

---



# 25. Setup Guide

*Source: `backend/docs/guides/setup.md`*

---

# Development Setup Guide

Installation and environment configuration for Neo Alexandria 2.0.

> **Phase 14 Complete**: Neo Alexandria now uses a fully modular vertical slice architecture with 13 self-contained modules, enhanced shared kernel, and event-driven communication.

## Prerequisites

- Python 3.8 or higher
- Git
- SQLite (included with Python) or PostgreSQL 15+ (recommended for production)
- 4GB RAM minimum (8GB recommended for AI features)
- 2GB free disk space

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Database Configuration
DATABASE_URL=sqlite:///backend.db
TEST_DATABASE_URL=sqlite:///:memory:

# AI Model Configuration
EMBEDDING_MODEL_NAME=nomic-ai/nomic-embed-text-v1
SUMMARIZER_MODEL=facebook/bart-large-cnn
TAGGER_MODEL=facebook/bart-large-mnli

# Search Configuration
DEFAULT_HYBRID_SEARCH_WEIGHT=0.5
EMBEDDING_CACHE_SIZE=1000

# Graph Configuration
GRAPH_WEIGHT_VECTOR=0.6
GRAPH_WEIGHT_TAGS=0.3
GRAPH_WEIGHT_CLASSIFICATION=0.1

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
```

### 5. Run Database Migrations

```bash
alembic upgrade head
```

### 6. Start Development Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## Verify Installation

### Check API Documentation

Open in browser:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Test Health Endpoint

```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "2024-01-01T10:00:00Z"}
```

### Verify Module Registration

Check that all 13 modules are loaded:

```bash
curl http://127.0.0.1:8000/monitoring/health
```

Expected response should show all modules as healthy:
```json
{
  "status": "healthy",
  "modules": {
    "collections": "healthy",
    "resources": "healthy",
    "search": "healthy",
    "annotations": "healthy",
    "scholarly": "healthy",
    "authority": "healthy",
    "curation": "healthy",
    "quality": "healthy",
    "taxonomy": "healthy",
    "graph": "healthy",
    "recommendations": "healthy",
    "monitoring": "healthy"
  },
  "event_bus": {
    "status": "healthy",
    "handlers_registered": 12
  }
}
```

### Run Tests

```bash
pytest tests/ -v
```

## Understanding the Module Structure

### Phase 14 Architecture

Neo Alexandria uses a **vertical slice architecture** where each feature is a self-contained module:

```
app/
├── shared/              # Shared kernel (no business logic)
│   ├── database.py      # Database session management
│   ├── event_bus.py     # Event-driven communication
│   ├── base_model.py    # Base SQLAlchemy model
│   ├── embeddings.py    # Embedding generation service
│   ├── ai_core.py       # AI/ML operations
│   └── cache.py         # Caching service
└── modules/             # 13 self-contained modules
    ├── collections/     # Collection management
    ├── resources/       # Resource CRUD
    ├── search/          # Hybrid search
    ├── annotations/     # Text highlights & notes
    ├── scholarly/       # Academic metadata
    ├── authority/       # Subject authority
    ├── curation/        # Content review
    ├── quality/         # Quality assessment
    ├── taxonomy/        # ML classification
    ├── graph/           # Knowledge graph & citations
    ├── recommendations/ # Hybrid recommendations
    └── monitoring/      # System health & metrics
```

### Module Standard Structure

Each module follows this pattern:

```
modules/{module_name}/
├── __init__.py      # Public interface
├── router.py        # API endpoints
├── service.py       # Business logic
├── schema.py        # Pydantic models
├── model.py         # SQLAlchemy models (optional)
├── handlers.py      # Event handlers
└── README.md        # Documentation
```

### Key Principles

1. **Module Independence**: Modules don't import from each other
2. **Event-Driven**: Modules communicate via events, not direct calls
3. **Shared Kernel**: Common infrastructure (database, events, cache) in `shared/`
4. **Standard Structure**: All modules follow the same layout
5. **Self-Contained**: Each module has its own router, service, schema, and tests

## Database Configuration

### SQLite (Default)

No additional setup required. Database file created automatically.

```bash
DATABASE_URL=sqlite:///backend.db
```

### PostgreSQL (Production)

1. Install PostgreSQL 15+
2. Create database:
```bash
createdb neo_alexandria
```
3. Update `.env`:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/neo_alexandria
```
4. Run migrations:
```bash
alembic upgrade head
```

## AI Model Setup

Models are downloaded automatically on first use. To pre-download:

```python
from transformers import AutoModel, AutoTokenizer

# Embedding model
AutoModel.from_pretrained("nomic-ai/nomic-embed-text-v1")
AutoTokenizer.from_pretrained("nomic-ai/nomic-embed-text-v1")

# Summarization model
AutoModel.from_pretrained("facebook/bart-large-cnn")
AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
```

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Pylance
- Black Formatter
- isort

Settings (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

### PyCharm

1. Set interpreter to `.venv/bin/python`
2. Enable Black formatter
3. Configure pytest as test runner

## Common Issues

### Import Errors

Ensure virtual environment is activated:
```bash
source .venv/bin/activate
which python  # Should show .venv path
```

### Module Not Loading

Check application startup logs for module registration:
```bash
uvicorn app.main:app --reload --log-level debug
```

Look for lines like:
```
INFO: ✓ Registered router for module: collections
INFO: ✓ Registered event handlers for module: collections
```

If a module fails to load, check:
1. Module `__init__.py` exists and exports correctly
2. No circular imports within the module
3. All dependencies are installed

### Database Locked (SQLite)

SQLite doesn't support concurrent writes. For development:
- Use single process
- Or switch to PostgreSQL

### Model Download Fails

Check internet connection and disk space. Models require ~2GB.

### Memory Errors

AI models require significant RAM. Options:
- Increase system RAM to 8GB+
- Use smaller models
- Disable AI features for testing

### Event Handlers Not Firing

Check that event handlers are registered during startup:
```bash
curl http://127.0.0.1:8000/monitoring/events
```

Should show events being emitted and delivered. If not:
1. Verify `register_handlers()` is called in module `__init__.py`
2. Check application logs for handler registration errors
3. Ensure event types match exactly (case-sensitive)

## Next Steps

- [Development Workflows](workflows.md) - Common tasks and module development patterns
- [Testing Guide](testing.md) - Running tests
- [Migration Guide](../MIGRATION_GUIDE.md) - Understanding the modular architecture
- [API Documentation](../api/) - API reference

## Related Documentation

- [Architecture Overview](../architecture/overview.md) - System architecture and module structure
- [Module Documentation](../architecture/modules.md) - Complete module reference
- [Event System](../architecture/event-system.md) - Event-driven communication patterns
- [Database Configuration](../architecture/database.md)
- [Troubleshooting](troubleshooting.md)



<div style='page-break-after: always;'></div>

---



# 26. Development Workflows

*Source: `backend/docs/guides/workflows.md`*

---

# Development Workflows

Common development tasks and patterns for Neo Alexandria 2.0.

> **Phase 14 Complete**: This guide reflects the fully modular vertical slice architecture with 13 self-contained modules, enhanced shared kernel, and event-driven communication patterns.

## Quick Reference

### Module Structure
All modules follow a standard structure:
```
modules/{module_name}/
├── __init__.py      # Public interface
├── router.py        # API endpoints
├── service.py       # Business logic
├── schema.py        # Pydantic models
├── model.py         # SQLAlchemy models (optional)
├── handlers.py      # Event handlers
└── README.md        # Documentation
```

### Current Modules (13 Total)
1. **collections** - Collection management
2. **resources** - Resource CRUD operations
3. **search** - Hybrid search (keyword + semantic)
4. **annotations** - Text highlights and notes
5. **scholarly** - Academic metadata extraction
6. **authority** - Subject authority control
7. **curation** - Content review and batch operations
8. **quality** - Multi-dimensional quality assessment
9. **taxonomy** - ML-based classification
10. **graph** - Knowledge graph and citations
11. **recommendations** - Hybrid recommendation engine
12. **monitoring** - System health and metrics

### Shared Kernel Services
- **database.py** - Database session management
- **event_bus.py** - Event-driven communication
- **base_model.py** - Base SQLAlchemy model
- **embeddings.py** - Embedding generation (dense & sparse)
- **ai_core.py** - AI/ML operations (summarization, entity extraction)
- **cache.py** - Caching service with TTL support

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

## Module Development Patterns

### Using Shared Kernel Services

#### Embedding Generation

```python
# In your module service
from app.shared.embeddings import EmbeddingService

class MyModuleService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
    
    def process_text(self, text: str):
        # Generate dense embedding
        embedding = self.embedding_service.generate_embedding(text)
        
        # Generate sparse embedding (SPLADE)
        sparse_embedding = self.embedding_service.generate_sparse_embedding(text)
        
        # Batch generation
        embeddings = self.embedding_service.batch_generate([text1, text2, text3])
```

#### AI/ML Operations

```python
# In your module service
from app.shared.ai_core import AICore

class MyModuleService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_core = AICore()
    
    def process_content(self, text: str):
        # Generate summary
        summary = self.ai_core.summarize(text)
        
        # Extract entities
        entities = self.ai_core.extract_entities(text)
        
        # Zero-shot classification
        labels = ["science", "technology", "business"]
        scores = self.ai_core.classify_text(text, labels)
```

#### Caching

```python
# In your module service
from app.shared.cache import CacheService

class MyModuleService:
    def __init__(self, db: Session):
        self.db = db
        self.cache = CacheService()
    
    def get_expensive_data(self, key: str):
        # Try cache first
        cached = self.cache.get(f"mymodule:{key}")
        if cached:
            return cached
        
        # Compute if not cached
        data = self._compute_expensive_operation(key)
        
        # Cache with TTL (seconds)
        self.cache.set(f"mymodule:{key}", data, ttl=3600)
        return data
    
    def invalidate_cache(self, pattern: str):
        # Invalidate by pattern
        self.cache.invalidate(f"mymodule:{pattern}*")
```

### Event-Driven Communication

#### Emitting Events

```python
# In your module service
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

#### Subscribing to Events

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
    except Exception as e:
        logger.error(f"Error handling resource.created: {e}", exc_info=True)
    finally:
        db.close()

def register_handlers():
    """Register all event handlers for this module."""
    event_bus.subscribe("resource.created", handle_resource_created)
    event_bus.subscribe("resource.updated", handle_resource_updated)
```

#### Event Handler Best Practices

1. **Always create fresh database sessions** in handlers
2. **Always close sessions** in finally block
3. **Catch exceptions** - don't let one handler break others
4. **Log errors** with full traceback
5. **Keep handlers fast** (<100ms) - offload heavy work to Celery
6. **Make handlers idempotent** - safe to run multiple times

```python
def handle_event(payload: dict):
    """Example handler with best practices."""
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
touch app/modules/new_feature/README.md
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
from app.shared.event_bus import event_bus

class NewFeatureService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_feature(self, data: NewFeatureCreate) -> NewFeature:
        feature = NewFeature(**data.dict())
        self.db.add(feature)
        self.db.commit()
        self.db.refresh(feature)
        
        # Publish event
        event_bus.emit("new_feature.created", {
            "id": str(feature.id),
            "name": feature.name
        })
        
        return feature
```

### 5. Create Router

```python
# app/modules/new_feature/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.shared.database import get_db
from .service import NewFeatureService
from .schema import NewFeatureCreate, NewFeatureResponse

router = APIRouter(prefix="/new-features", tags=["new-features"])

@router.post("/", response_model=NewFeatureResponse)
def create(data: NewFeatureCreate, db: Session = Depends(get_db)):
    service = NewFeatureService(db)
    return service.create_feature(data)
```

### 6. Create Event Handlers

```python
# app/modules/new_feature/handlers.py
from app.shared.event_bus import event_bus
from app.shared.database import SessionLocal
from .service import NewFeatureService

def handle_external_event(payload: dict):
    """Handle events from other modules."""
    db = SessionLocal()
    try:
        service = NewFeatureService(db)
        service.process_event(payload)
    except Exception as e:
        logger.error(f"Error handling event: {e}", exc_info=True)
    finally:
        db.close()

def register_handlers():
    """Register all event handlers for this module."""
    event_bus.subscribe("external.event", handle_external_event)
```

### 7. Create Public Interface

```python
# app/modules/new_feature/__init__.py
"""New Feature Module - Public Interface"""

__version__ = "1.0.0"
__domain__ = "new_feature"

from .router import router as new_feature_router
from .service import NewFeatureService
from .schema import NewFeatureCreate, NewFeatureResponse
from .handlers import register_handlers

__all__ = [
    "new_feature_router",
    "NewFeatureService",
    "NewFeatureCreate",
    "NewFeatureResponse",
    "register_handlers",
]
```

### 8. Register Module

Add to `app/__init__.py`:

```python
modules = [
    # Existing modules
    ("collections", "backend.app.modules.collections", "collections_router"),
    ("resources", "backend.app.modules.resources", "resources_router"),
    ("search", "backend.app.modules.search", "search_router"),
    
    # New module
    ("new_feature", "backend.app.modules.new_feature", "new_feature_router"),
]
```

### 9. Create Migration

```bash
alembic revision --autogenerate -m "Add new_features table"
alembic upgrade head
```

### 10. Write Tests

```python
# app/modules/new_feature/tests/test_service.py
import pytest
from app.modules.new_feature.service import NewFeatureService
from app.modules.new_feature.schema import NewFeatureCreate

def test_create_feature(db_session):
    service = NewFeatureService(db_session)
    data = NewFeatureCreate(name="Test", description="Test description")
    
    feature = service.create_feature(data)
    
    assert feature.name == "Test"
    assert feature.description == "Test description"
    assert feature.id is not None
```

## Adding API Endpoints

### GET Endpoint

```python
@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: UUID, db: Session = Depends(get_db)):
    service = ItemService(db)
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

### POST Endpoint

```python
@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    service = ItemService(db)
    return service.create_item(data)
```

### PUT Endpoint

```python
@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: UUID,
    data: ItemUpdate,
    db: Session = Depends(get_db)
):
    service = ItemService(db)
    item = service.update_item(item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

### DELETE Endpoint

```python
@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: UUID, db: Session = Depends(get_db)):
    service = ItemService(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
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

### Event Bus Debugging

Check event metrics:
```bash
curl http://localhost:8000/monitoring/events
```

View event history:
```bash
curl http://localhost:8000/monitoring/events/history
```

### Interactive Debugging

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use VS Code debugger with launch.json
```

### Module Isolation Validation

Check for circular dependencies:
```bash
python backend/scripts/check_module_isolation.py
```

This will detect:
- Direct imports between modules
- Circular dependencies
- Violations of module boundaries

## Common Patterns

### Async Background Tasks

For long-running operations, use Celery:

```python
# In your service
from app.tasks.celery_tasks import process_heavy_task

def trigger_processing(self, item_id: str):
    # Queue task for background processing
    process_heavy_task.delay(item_id)
    return {"status": "queued"}
```

### Pagination

```python
from fastapi import Query

@router.get("/items")
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    service = ItemService(db)
    items = service.list_items(skip=skip, limit=limit)
    total = service.count_items()
    
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }
```

### Error Handling

```python
from fastapi import HTTPException

def get_item(self, item_id: str):
    item = self.db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"Item {item_id} not found"
        )
    return item
```

## Related Documentation

- [Setup Guide](setup.md) - Installation
- [Testing Guide](testing.md) - Running tests
- [Architecture](../architecture/) - System design
- [Migration Guide](../MIGRATION_GUIDE.md) - Understanding the modular architecture
- [Event System](../architecture/event-system.md) - Event-driven patterns



<div style='page-break-after: always;'></div>

---



# 27. Testing Guide

*Source: `backend/docs/guides/testing.md`*

---

# Testing Guide

Testing strategies and practices for Neo Alexandria 2.0.

## Running Tests

### All Tests

```bash
cd backend
pytest tests/ -v
```

### With Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

Coverage report generated in `htmlcov/index.html`

### Specific Test File

```bash
pytest tests/test_resources.py -v
```

### Specific Test Function

```bash
pytest tests/test_resources.py::test_create_resource -v
```

### By Marker

```bash
# Run only unit tests
pytest tests/ -m unit -v

# Run only integration tests
pytest tests/ -m integration -v

# Run PostgreSQL-specific tests
pytest tests/ -m postgresql -v
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_services.py
│   ├── test_schemas.py
│   └── test_domain.py
├── integration/             # Integration tests
│   ├── test_api.py
│   ├── test_database.py
│   └── test_events.py
└── performance/             # Performance tests
    └── test_benchmarks.py
```

## Test Fixtures

### Database Session

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base

@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(db_engine):
    """Create test database session."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
```

### Test Client

```python
@pytest.fixture
def client(db_session):
    """Create test API client."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.shared.database import get_db
    
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Sample Data

```python
@pytest.fixture
def sample_resource(db_session):
    """Create sample resource for testing."""
    from app.modules.resources.model import Resource
    
    resource = Resource(
        title="Test Resource",
        description="Test description",
        source="https://example.com/test"
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)
    return resource
```

## Writing Tests

### Unit Tests

Test individual functions in isolation:

```python
# tests/unit/test_quality_service.py
import pytest
from app.services.quality_service import compute_accuracy_score

def test_compute_accuracy_score_with_citations():
    """Test accuracy score with valid citations."""
    resource = MockResource(
        citations=["https://doi.org/10.1234/test"],
        source="https://arxiv.org/paper"
    )
    
    score = compute_accuracy_score(resource)
    
    assert 0.0 <= score <= 1.0
    assert score > 0.5  # Should be above baseline

def test_compute_accuracy_score_no_citations():
    """Test accuracy score without citations."""
    resource = MockResource(citations=[], source="https://example.com")
    
    score = compute_accuracy_score(resource)
    
    assert score == 0.5  # Baseline score
```

### Integration Tests

Test API endpoints end-to-end:

```python
# tests/integration/test_resources_api.py
def test_create_resource(client):
    """Test resource creation via API."""
    response = client.post(
        "/resources",
        json={"url": "https://example.com/article"}
    )
    
    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"

def test_get_resource(client, sample_resource):
    """Test resource retrieval via API."""
    response = client.get(f"/resources/{sample_resource.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == sample_resource.title

def test_get_resource_not_found(client):
    """Test 404 for non-existent resource."""
    response = client.get("/resources/00000000-0000-0000-0000-000000000000")
    
    assert response.status_code == 404
```

### Event Tests

Test event publishing and handling:

```python
# tests/integration/test_events.py
from app.shared.event_bus import event_bus, Event

def test_resource_deleted_updates_collections(db_session, sample_resource, sample_collection):
    """Test that deleting a resource updates collections."""
    # Add resource to collection
    add_resource_to_collection(db_session, sample_collection.id, sample_resource.id)
    
    # Delete resource (triggers event)
    delete_resource(db_session, sample_resource.id)
    
    # Verify collection updated
    collection = get_collection(db_session, sample_collection.id)
    assert sample_resource.id not in [r.id for r in collection.resources]
```

### Database Tests

Test with different databases:

```python
# tests/test_postgresql.py
import pytest

@pytest.mark.postgresql
def test_jsonb_containment_query(db_session):
    """Test PostgreSQL JSONB containment query."""
    # Create resource with subjects
    resource = Resource(
        title="ML Paper",
        subject=["Machine Learning", "AI"]
    )
    db_session.add(resource)
    db_session.commit()
    
    # Query using JSONB containment
    results = db_session.query(Resource).filter(
        Resource.subject.contains(["Machine Learning"])
    ).all()
    
    assert len(results) == 1
    assert results[0].id == resource.id
```

## Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    postgresql: PostgreSQL-specific tests
    slow: Slow tests
addopts = -v --tb=short
```

### Environment Variables

```bash
# Use in-memory SQLite for tests
TEST_DATABASE_URL=sqlite:///:memory:

# Or test against PostgreSQL
TEST_DATABASE_URL=postgresql://user:pass@localhost:5432/test_db
```

## Mocking

### Mock External Services

```python
from unittest.mock import Mock, patch

def test_ingestion_with_mock_http(db_session):
    """Test ingestion with mocked HTTP client."""
    with patch('httpx.get') as mock_get:
        mock_get.return_value = Mock(
            status_code=200,
            text="<html><body>Test content</body></html>"
        )
        
        result = ingest_url(db_session, "https://example.com/test")
        
        assert result.title is not None
        mock_get.assert_called_once()
```

### Mock AI Models

```python
def test_classification_with_mock_model(db_session):
    """Test classification with mocked ML model."""
    with patch('app.services.ml_classification_service.model') as mock_model:
        mock_model.predict.return_value = [
            {"label": "Computer Science", "score": 0.95}
        ]
        
        result = classify_resource(db_session, resource_id)
        
        assert result.classification_code == "004"
```

## Performance Testing

```python
# tests/performance/test_benchmarks.py
import pytest
import time

@pytest.mark.slow
def test_search_performance(client, many_resources):
    """Test search completes within time limit."""
    start = time.time()
    
    response = client.post(
        "/search",
        json={"text": "machine learning", "limit": 100}
    )
    
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 0.5  # Should complete in <500ms
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Related Documentation

- [Setup Guide](setup.md) - Installation
- [Workflows](workflows.md) - Development tasks
- [Troubleshooting](troubleshooting.md) - Common issues


<div style='page-break-after: always;'></div>

---



# 28. Deployment Guide

*Source: `backend/docs/guides/deployment.md`*

---

# Deployment Guide

Docker and production deployment for Neo Alexandria 2.0.

## Docker Deployment

### Quick Start

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/neo_alexandria
    depends_on:
      - db
    volumes:
      - ./storage:/app/storage

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=neo_alexandria
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run with Gunicorn
CMD ["gunicorn", "app.main:app", "-c", "gunicorn.conf.py"]
```

### Build and Run

```bash
# Build image
docker build -t neo-alexandria .

# Run container
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -v $(pwd)/storage:/app/storage \
  neo-alexandria
```

## Production Configuration

### Gunicorn Settings

```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4  # (2 * CPU cores) + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

### Environment Variables

```bash
# Production .env
DATABASE_URL=postgresql://user:password@host:5432/neo_alexandria
DEBUG=false
LOG_LEVEL=WARNING

# AI Models
EMBEDDING_MODEL_NAME=nomic-ai/nomic-embed-text-v1
SUMMARIZER_MODEL=facebook/bart-large-cnn

# Search
DEFAULT_HYBRID_SEARCH_WEIGHT=0.5
EMBEDDING_CACHE_SIZE=5000

# Security (future)
# API_KEY_REQUIRED=true
# CORS_ORIGINS=https://your-domain.com
```

### PostgreSQL Production Setup

```bash
# Create database
createdb neo_alexandria

# Create user with limited privileges
psql -c "CREATE USER neo_app WITH PASSWORD 'secure_password';"
psql -c "GRANT CONNECT ON DATABASE neo_alexandria TO neo_app;"
psql -c "GRANT USAGE ON SCHEMA public TO neo_app;"
psql -c "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO neo_app;"

# Run migrations
DATABASE_URL=postgresql://neo_app:secure_password@localhost:5432/neo_alexandria \
  alembic upgrade head
```

## Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/neo-alexandria
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files (if any)
    location /static {
        alias /app/static;
        expires 30d;
    }
}
```

## Systemd Service

```ini
# /etc/systemd/system/neo-alexandria.service
[Unit]
Description=Neo Alexandria API
After=network.target postgresql.service

[Service]
User=neo-app
Group=neo-app
WorkingDirectory=/opt/neo-alexandria
Environment="PATH=/opt/neo-alexandria/.venv/bin"
Environment="DATABASE_URL=postgresql://user:pass@localhost:5432/neo_alexandria"
ExecStart=/opt/neo-alexandria/.venv/bin/gunicorn app.main:app -c gunicorn.conf.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable neo-alexandria
sudo systemctl start neo-alexandria
sudo systemctl status neo-alexandria
```

## Health Checks

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /monitoring/status
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Docker Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

## Backup Strategy

### Automated PostgreSQL Backup

```bash
#!/bin/bash
# /opt/neo-alexandria/scripts/backup.sh

BACKUP_DIR=/var/backups/neo-alexandria
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup
pg_dump -h localhost -U postgres neo_alexandria | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Remove old backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
```

```bash
# Cron job (daily at 2 AM)
0 2 * * * /opt/neo-alexandria/scripts/backup.sh
```

### Storage Backup

```bash
# Backup storage directory
rsync -avz /opt/neo-alexandria/storage/ /backup/storage/
```

## Monitoring

### Prometheus Metrics (Planned)

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'neo-alexandria'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
```

### Log Aggregation

```bash
# Send logs to centralized logging
docker-compose logs -f | logger -t neo-alexandria
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
services:
  api:
    deploy:
      replicas: 3
    
  nginx:
    image: nginx
    ports:
      - "80:80"
    depends_on:
      - api
```

### Database Connection Pooling

For high-traffic deployments, use PgBouncer:

```ini
# pgbouncer.ini
[databases]
neo_alexandria = host=localhost dbname=neo_alexandria

[pgbouncer]
listen_port = 6432
listen_addr = 127.0.0.1
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
```

## Related Documentation

- [Setup Guide](setup.md) - Development setup
- [Database Architecture](../architecture/database.md) - Database configuration
- [Troubleshooting](troubleshooting.md) - Common issues


<div style='page-break-after: always;'></div>

---



# 29. Troubleshooting

*Source: `backend/docs/guides/troubleshooting.md`*

---

# Troubleshooting Guide

Common issues and solutions for Neo Alexandria 2.0.

## Installation Issues

### Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Verify Python path
which python  # Should show .venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### Dependency Conflicts

**Symptom:** `ERROR: Cannot install package due to conflicting dependencies`

**Solution:**
```bash
# Create fresh virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Model Download Fails

**Symptom:** `OSError: Can't load tokenizer for 'nomic-ai/nomic-embed-text-v1'`

**Solution:**
```bash
# Check internet connection
ping huggingface.co

# Check disk space (models need ~2GB)
df -h

# Try manual download
python -c "from transformers import AutoModel; AutoModel.from_pretrained('nomic-ai/nomic-embed-text-v1')"
```

## Database Issues

### Database Locked (SQLite)

**Symptom:** `sqlite3.OperationalError: database is locked`

**Cause:** SQLite doesn't support concurrent writes.

**Solutions:**
1. Use single process for development
2. Switch to PostgreSQL for multi-user scenarios
3. Increase timeout:
```python
connect_args={"timeout": 30}
```

### Migration Fails

**Symptom:** `alembic.util.exc.CommandError: Can't locate revision`

**Solution:**
```bash
# Check current state
alembic current

# Stamp to known state
alembic stamp head

# Re-run migrations
alembic upgrade head
```

### Connection Pool Exhausted

**Symptom:** `QueuePool limit of size X overflow Y reached`

**Solution:**
```python
# Increase pool size in database configuration
postgresql_params = {
    'pool_size': 30,      # Increase from 20
    'max_overflow': 60,   # Increase from 40
}
```

### PostgreSQL Connection Refused

**Symptom:** `psycopg2.OperationalError: could not connect to server`

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection string
psql -h localhost -U postgres -d neo_alexandria

# Verify pg_hba.conf allows connections
sudo cat /etc/postgresql/15/main/pg_hba.conf
```

## API Issues

### 422 Validation Error

**Symptom:** `{"detail":[{"loc":["body","field"],"msg":"field required"}]}`

**Solution:**
- Check request body matches schema
- Verify Content-Type header is `application/json`
- Check for typos in field names

### 500 Internal Server Error

**Symptom:** Generic server error with no details

**Solution:**
```bash
# Enable debug mode
DEBUG=true uvicorn app.main:app --reload

# Check application logs
tail -f /var/log/neo-alexandria/error.log
```

### Slow API Responses

**Symptom:** Requests take >1 second

**Solutions:**
1. Check database query performance:
```sql
EXPLAIN ANALYZE SELECT * FROM resources WHERE ...;
```

2. Add missing indexes:
```sql
CREATE INDEX idx_resources_subject ON resources USING GIN (subject);
```

3. Enable query logging:
```python
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

## Search Issues

### No Search Results

**Symptom:** Search returns empty results for known content

**Solutions:**
1. Check FTS5 index exists:
```sql
SELECT * FROM resources_fts;
```

2. Rebuild search index:
```bash
python -c "from app.services.search_service import rebuild_fts_index; rebuild_fts_index()"
```

3. Verify embeddings exist:
```sql
SELECT COUNT(*) FROM resources WHERE embedding IS NOT NULL;
```

### Search Quality Issues

**Symptom:** Irrelevant results ranked highly

**Solutions:**
1. Adjust hybrid weight:
```json
{"text": "query", "hybrid_weight": 0.7}  // More semantic
{"text": "query", "hybrid_weight": 0.3}  // More keyword
```

2. Check embedding model is loaded:
```python
from app.services.ai_core import AICore
ai = AICore()
print(ai.embedding_model)  # Should not be None
```

## AI/ML Issues

### Out of Memory

**Symptom:** `RuntimeError: CUDA out of memory` or system OOM

**Solutions:**
1. Reduce batch size:
```python
batch_size = 8  # Reduce from 32
```

2. Use CPU instead of GPU:
```python
device = "cpu"  # Instead of "cuda"
```

3. Increase system RAM to 8GB+

### Model Loading Slow

**Symptom:** First request takes 30+ seconds

**Cause:** Models loaded lazily on first use.

**Solutions:**
1. Pre-load models at startup:
```python
# In main.py
@app.on_event("startup")
async def load_models():
    ai_core = AICore()
    ai_core.load_embedding_model()
```

2. Use smaller models for development

### Classification Accuracy Low

**Symptom:** ML classification gives wrong categories

**Solutions:**
1. Retrain with more labeled data
2. Adjust confidence threshold:
```python
min_confidence = 0.5  # Increase from 0.3
```

3. Use active learning to improve model

## Event System Issues

### Events Not Firing

**Symptom:** Event handlers not called

**Solutions:**
1. Verify handler is registered:
```python
print(event_bus._subscribers)  # Check handlers
```

2. Check for exceptions in handlers:
```python
def handle_event(event):
    try:
        # handler code
    except Exception as e:
        logger.error(f"Handler error: {e}")
```

### Circular Import Errors

**Symptom:** `ImportError: cannot import name 'X' from partially initialized module`

**Solution:**
- Use string-based relationships in models
- Import inside functions, not at module level
- Use event bus instead of direct imports

## Performance Issues

### High CPU Usage

**Symptom:** CPU at 100% during normal operation

**Solutions:**
1. Profile the application:
```python
import cProfile
cProfile.run('function_to_profile()')
```

2. Check for infinite loops in event handlers
3. Optimize database queries

### High Memory Usage

**Symptom:** Memory grows over time

**Solutions:**
1. Check for memory leaks:
```python
import tracemalloc
tracemalloc.start()
# ... run code ...
snapshot = tracemalloc.take_snapshot()
```

2. Clear embedding cache periodically
3. Use streaming for large responses

## Docker Issues

### Container Won't Start

**Symptom:** Container exits immediately

**Solution:**
```bash
# Check logs
docker logs container_name

# Run interactively
docker run -it neo-alexandria /bin/bash
```

### Volume Permission Errors

**Symptom:** `PermissionError: [Errno 13] Permission denied`

**Solution:**
```bash
# Fix ownership
sudo chown -R 1000:1000 ./storage

# Or run as root (not recommended)
docker run --user root ...
```

## Getting Help

### Collect Debug Information

```bash
# System info
python --version
pip freeze > requirements_actual.txt

# Database info
alembic current
psql -c "SELECT version();"

# Application logs
tail -100 /var/log/neo-alexandria/app.log
```

### Report Issues

Include:
1. Error message and stack trace
2. Steps to reproduce
3. Environment details (OS, Python version)
4. Relevant configuration

## Related Documentation

- [Setup Guide](setup.md) - Installation
- [Testing Guide](testing.md) - Running tests
- [Deployment Guide](deployment.md) - Production setup


<div style='page-break-after: always;'></div>

---



# 30. Backend Overview

*Source: `backend/README.md`*

---

# Neo Alexandria 2.0 - Advanced Knowledge Management API

## Overview

Neo Alexandria 2.0 is a comprehensive knowledge management system that provides intelligent content processing, advanced search capabilities, and personalized recommendations through a RESTful API. The system combines traditional information retrieval with modern AI-powered features to deliver a complete solution for knowledge curation and discovery.

## Key Features

### Content Ingestion and Processing
- **Asynchronous URL Ingestion**: Submit web content for intelligent processing
- **AI-Powered Analysis**: Automatic summarization, tagging, and classification
- **Multi-Format Support**: HTML, PDF, and plain text content extraction
- **Quality Assessment**: Comprehensive content quality scoring and evaluation

### Advanced Search and Discovery
- **Hybrid Search**: Combines keyword and semantic search with configurable weighting
- **Vector Embeddings**: Semantic similarity search using state-of-the-art embedding models
- **Faceted Search**: Advanced filtering by classification, language, quality, and subjects
- **Full-Text Search**: SQLite FTS5 integration with graceful fallbacks

### Knowledge Graph and Relationships
- **Hybrid Graph Scoring**: Multi-signal relationship detection combining vector similarity, shared subjects, and classification matches
- **Mind-Map Visualization**: Resource-centric neighbor discovery for exploration
- **Global Overview**: System-wide relationship analysis and connection mapping

### Citation Network & Link Intelligence
- **Multi-Format Citation Extraction**: Automatically extract citations from HTML, PDF, and Markdown content
- **Internal Citation Resolution**: Link citations to existing resources in your library
- **PageRank Importance Scoring**: Compute citation importance using network analysis
- **Citation Graph Visualization**: Build and explore citation networks with configurable depth
- **Smart Citation Classification**: Automatically categorize citations as datasets, code, references, or general links

### Personalized Recommendations
- **Content-Based Filtering**: Learn user preferences from existing library content
- **Fresh Content Discovery**: Source and rank new content from external providers
- **Explainable Recommendations**: Provide reasoning for recommendation decisions

### Collection Management
- **Curated Collections**: Organize resources into named, thematic collections with descriptions
- **Hierarchical Organization**: Create nested collections for complex topic structures
- **Visibility Controls**: Set collections as private, shared, or public for flexible collaboration
- **Aggregate Embeddings**: Automatic semantic representation computed from member resources
- **Collection Recommendations**: Discover similar resources and collections based on semantic similarity
- **Batch Operations**: Add or remove up to 100 resources in a single request
- **Automatic Cleanup**: Collections update automatically when resources are deleted
- **Access Control**: Owner-based permissions with visibility-based read access

### Annotation & Active Reading System
- **Precise Text Highlighting**: Character-offset-based text selection with context preservation
- **Rich Note-Taking**: Add personal notes to highlights with automatic semantic embedding
- **Tag Organization**: Categorize annotations with custom tags and color-coding
- **Full-Text Search**: Search across all annotation notes and highlighted text (<100ms for 10K annotations)
- **Semantic Search**: Find conceptually related annotations using AI-powered similarity
- **Export Capabilities**: Export annotations to Markdown or JSON for external tools
- **Collection Integration**: Associate annotations with research collections
- **Privacy Controls**: Annotations are private by default with optional sharing

### Authority Control and Classification
- **Subject Normalization**: Intelligent tag standardization and canonical forms
- **Hierarchical Classification**: UDC-inspired classification system with automatic assignment
- **Usage Tracking**: Monitor and optimize metadata usage patterns

### ML-Powered Classification & Taxonomy
- **Transformer-Based Classification**: Fine-tuned BERT/DistilBERT models for accurate resource categorization
- **Hierarchical Taxonomy Management**: Create and manage multi-level category trees with parent-child relationships
- **Multi-Label Classification**: Resources can belong to multiple categories with confidence scores
- **Semi-Supervised Learning**: Train effective models with minimal labeled data (<500 examples)
- **Active Learning**: System identifies uncertain predictions for targeted human review
- **Confidence Scoring**: Every classification includes a confidence score (0.0-1.0) for transparency
- **Model Versioning**: Track and manage multiple model versions with rollback capability
- **GPU Acceleration**: Automatic GPU utilization with graceful CPU fallback
- **Continuous Improvement**: Models improve automatically through human feedback loops

## API-First Architecture

Neo Alexandria 2.0 is built with an API-first approach, enabling seamless integration with external systems and applications. The RESTful API provides comprehensive endpoints for all system functionality, making it suitable for both internal knowledge management and external service integration.

## Quick Start

### Prerequisites

- Python 3.8 or higher
- SQLite (default) or PostgreSQL database
- 4GB RAM minimum (8GB recommended for AI features)

### Installation

1. **Clone the repository and navigate to the project directory**

2. **Create a virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r backend/requirements.txt
```

4. **Run database migrations**
```bash
cd backend
alembic upgrade head
```

5. **Start the API server**
```bash
uvicorn backend.app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### First API Call

Test the API by ingesting your first resource:

```bash
curl -X POST http://127.0.0.1:8000/resources \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

## API Documentation

### Base URL
```
http://127.0.0.1:8000
```

### Authentication
Currently, no authentication is required for development and testing. Future releases will include API key authentication and rate limiting.

### Core Endpoints

#### Content Management
- `POST /resources` - Ingest new content from URLs
- `GET /resources` - List resources with filtering and pagination
- `GET /resources/{id}` - Retrieve specific resource details
- `PUT /resources/{id}` - Update resource metadata
- `DELETE /resources/{id}` - Remove resources
- `GET /resources/{id}/status` - Check ingestion status

#### Search and Discovery
- `POST /search` - Advanced search with hybrid keyword/semantic capabilities
- `GET /search/three-way-hybrid` - Three-way hybrid search with RRF and reranking
- `GET /search/compare-methods` - Compare different search methods side-by-side
- `POST /search/evaluate` - Evaluate search quality with IR metrics
- `POST /admin/sparse-embeddings/generate` - Batch generate sparse embeddings
- `GET /recommendations` - Get personalized content recommendations

#### Knowledge Graph
- `GET /graph/resource/{id}/neighbors` - Find related resources for mind-map visualization
- `GET /graph/overview` - Get global relationship overview

#### Citation Network
- `GET /citations/resources/{id}/citations` - Get citations for a resource (inbound/outbound)
- `GET /citations/graph/citations` - Get citation network for visualization
- `POST /citations/resources/{id}/citations/extract` - Trigger citation extraction
- `POST /citations/resolve` - Resolve internal citations
- `POST /citations/importance/compute` - Compute PageRank importance scores

#### Collection Management
- `POST /collections` - Create a new collection
- `GET /collections/{id}` - Retrieve collection details with member resources
- `PUT /collections/{id}` - Update collection metadata
- `DELETE /collections/{id}` - Delete collection and subcollections
- `GET /collections` - List collections with filtering and pagination
- `POST /collections/{id}/resources` - Add resources to collection
- `DELETE /collections/{id}/resources` - Remove resources from collection
- `GET /collections/{id}/recommendations` - Get similar resources and collections
- `GET /collections/{id}/embedding` - Retrieve collection aggregate embedding

#### Annotation Management
- `POST /resources/{resource_id}/annotations` - Create annotation on resource
- `GET /resources/{resource_id}/annotations` - List resource annotations
- `GET /annotations` - List user annotations with pagination
- `GET /annotations/{id}` - Retrieve specific annotation
- `PUT /annotations/{id}` - Update annotation note, tags, or color
- `DELETE /annotations/{id}` - Delete annotation
- `GET /annotations/search/fulltext` - Full-text search across annotations
- `GET /annotations/search/semantic` - Semantic search with similarity scores
- `GET /annotations/search/tags` - Tag-based annotation search
- `GET /annotations/export/markdown` - Export annotations to Markdown
- `GET /annotations/export/json` - Export annotations to JSON

#### Authority and Classification
- `GET /authority/subjects/suggest` - Get subject suggestions for autocomplete
- `GET /authority/classification/tree` - Retrieve hierarchical classification structure

#### Taxonomy Management (Phase 8.5)
- `POST /taxonomy/nodes` - Create new taxonomy node
- `PUT /taxonomy/nodes/{node_id}` - Update taxonomy node metadata
- `DELETE /taxonomy/nodes/{node_id}` - Delete taxonomy node (with cascade option)
- `POST /taxonomy/nodes/{node_id}/move` - Move node to different parent
- `GET /taxonomy/tree` - Retrieve hierarchical taxonomy tree
- `GET /taxonomy/nodes/{node_id}/ancestors` - Get ancestor nodes (breadcrumb trail)
- `GET /taxonomy/nodes/{node_id}/descendants` - Get all descendant nodes

#### ML Classification (Phase 8.5)
- `POST /taxonomy/classify/{resource_id}` - Classify resource using ML model
- `GET /taxonomy/active-learning/uncertain` - Get uncertain predictions for review
- `POST /taxonomy/active-learning/feedback` - Submit human classification feedback
- `POST /taxonomy/train` - Initiate model fine-tuning with training data

#### Curation and Quality Control
- `GET /curation/review-queue` - Access low-quality items for review
- `POST /curation/batch-update` - Apply batch updates to multiple resources

## Data Models

### Resource Model
The core data model follows Dublin Core metadata standards with custom extensions:

```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "creator": "string",
  "publisher": "string",
  "source": "string",
  "language": "string",
  "type": "string",
  "subject": ["string"],
  "classification_code": "string",
  "quality_score": 0.85,
  "read_status": "unread",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Search Request Model
```json
{
  "text": "search query",
  "hybrid_weight": 0.5,
  "filters": {
    "classification_code": ["004"],
    "language": ["en"],
    "min_quality": 0.7,
    "subject_any": ["Machine Learning"]
  },
  "limit": 25,
  "offset": 0,
  "sort_by": "relevance",
  "sort_dir": "desc"
}
```

### Recommendation Response Model
```json
{
  "items": [
    {
      "url": "https://example.com/article",
      "title": "Article Title",
      "snippet": "Brief description...",
      "relevance_score": 0.85,
      "reasoning": ["Aligned with Machine Learning, Python"]
    }
  ]
}
```

## Configuration

### Database Configuration

Neo Alexandria 2.0 supports both SQLite and PostgreSQL databases. Choose the appropriate database based on your deployment scenario:

#### SQLite (Development)
- **Use Case**: Local development, testing, small deployments
- **Advantages**: Zero configuration, file-based, portable
- **Limitations**: Limited concurrency, no advanced features
- **Configuration**:
  ```bash
  DATABASE_URL=sqlite:///./backend.db
  ```

#### PostgreSQL (Production)
- **Use Case**: Production deployments, high concurrency, large datasets
- **Advantages**: Advanced indexing, JSONB support, full-text search, high concurrency
- **Requirements**: PostgreSQL 15 or higher
- **Configuration**:
  ```bash
  DATABASE_URL=postgresql://user:password@host:5432/database
  ```

#### Database Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | `sqlite:///./backend.db` | Primary database connection string |
| `TEST_DATABASE_URL` | No | `sqlite:///:memory:` | Test database connection string (overrides default test database) |
| `ENV` | No | `dev` | Environment name (`dev`, `staging`, `prod`) |

#### Database URL Format

**SQLite:**
```bash
# File-based database
DATABASE_URL=sqlite:///./backend.db

# In-memory database (testing only)
DATABASE_URL=sqlite:///:memory:

# Absolute path
DATABASE_URL=sqlite:////absolute/path/to/database.db
```

**PostgreSQL:**
```bash
# Basic connection
DATABASE_URL=postgresql://username:password@hostname:5432/database_name

# With SSL (recommended for production)
DATABASE_URL=postgresql://username:password@hostname:5432/database_name?sslmode=require

# With connection pool parameters
DATABASE_URL=postgresql://username:password@hostname:5432/database_name?pool_size=20&max_overflow=40
```

#### Environment-Specific Configuration Files

Neo Alexandria provides example configuration files for different environments:

- **`.env.development`** - Local development with SQLite
- **`.env.staging`** - Staging environment with PostgreSQL
- **`.env.production`** - Production environment with PostgreSQL

Copy the appropriate file to `.env` and customize for your environment:

```bash
# For local development
cp .env.development .env

# For staging
cp .env.staging .env
# Edit .env and update database credentials

# For production
cp .env.production .env
# Edit .env and update database credentials
```

#### Testing with Different Databases

By default, tests use in-memory SQLite for speed. To test against PostgreSQL:

```bash
# Set TEST_DATABASE_URL in your .env file
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db

# Or set it inline when running tests
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db pytest backend/tests/
```

#### Database Migration

When switching from SQLite to PostgreSQL or vice versa:

1. **Run migrations** to ensure schema is up to date:
   ```bash
   cd backend
   alembic upgrade head
   ```

2. **Migrate data** (if switching databases):
   ```bash
   # SQLite to PostgreSQL (forward migration)
   python backend/scripts/migrate_sqlite_to_postgresql.py \
     --source sqlite:///./backend.db \
     --target postgresql://user:password@host:5432/database \
     --validate
   
   # PostgreSQL to SQLite (rollback/reverse migration)
   python backend/scripts/migrate_postgresql_to_sqlite.py \
     --source postgresql://user:password@host:5432/database \
     --target sqlite:///./backend.db \
     --validate
   ```

3. **Verify migration** by checking row counts and running tests

#### Rollback Procedures

If you need to rollback from PostgreSQL to SQLite:

1. **Stop the application**:
   ```bash
   # Docker Compose
   docker-compose down
   
   # Or kill the process
   pkill -f "uvicorn backend.app.main:app"
   ```

2. **Restore SQLite backup** (if available):
   ```bash
   cp backend.db.backup backend.db
   ```

3. **Or run reverse migration** (if no backup):
   ```bash
   python backend/scripts/migrate_postgresql_to_sqlite.py \
     --source postgresql://user:password@host:5432/database \
     --target sqlite:///./backend.db \
     --validate
   ```

4. **Update environment configuration**:
   ```bash
   # Update .env file
   DATABASE_URL=sqlite:///./backend.db
   ```

5. **Restart the application**:
   ```bash
   uvicorn backend.app.main:app --reload
   ```

**⚠️ Important Rollback Limitations:**
- JSONB columns are converted to JSON text (no binary optimization)
- PostgreSQL full-text search vectors are not migrated (FTS5 must be rebuilt)
- Some PostgreSQL-specific indexes cannot be recreated in SQLite
- Array types are converted to JSON arrays

For detailed rollback procedures and troubleshooting, see:
- **[PostgreSQL Migration Guide](backend/docs/POSTGRESQL_MIGRATION_GUIDE.md)** - Complete migration and rollback procedures
- **[SQLite Compatibility Maintenance](backend/docs/SQLITE_COMPATIBILITY_MAINTENANCE.md)** - Maintaining compatibility during transition

#### Connection Pool Configuration

PostgreSQL connection pooling is automatically configured with optimal defaults:

- **Pool Size**: 20 base connections
- **Max Overflow**: 40 additional connections for burst traffic
- **Pool Recycle**: 3600 seconds (1 hour)
- **Pool Pre-Ping**: Enabled (validates connections before use)

Monitor connection pool usage via the monitoring endpoint:
```bash
curl http://localhost:8000/monitoring/database
```

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=sqlite:///backend.db
TEST_DATABASE_URL=sqlite:///:memory:

# AI Model Configuration
EMBEDDING_MODEL_NAME=nomic-ai/nomic-embed-text-v1
SUMMARIZER_MODEL=facebook/bart-large-cnn
TAGGER_MODEL=facebook/bart-large-mnli

# Search Configuration
DEFAULT_HYBRID_SEARCH_WEIGHT=0.5
EMBEDDING_CACHE_SIZE=1000

# Recommendation Configuration
RECOMMENDATION_PROFILE_SIZE=50
RECOMMENDATION_KEYWORD_COUNT=5
RECOMMENDATION_CANDIDATES_PER_KEYWORD=10
SEARCH_PROVIDER=ddgs
SEARCH_TIMEOUT=10

# Graph Configuration
GRAPH_WEIGHT_VECTOR=0.6
GRAPH_WEIGHT_TAGS=0.3
GRAPH_WEIGHT_CLASSIFICATION=0.1
GRAPH_VECTOR_MIN_SIM_THRESHOLD=0.85
```

## Error Handling

The API uses standard HTTP status codes and returns structured error responses:

```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common Status Codes
- `200 OK` - Successful request
- `202 Accepted` - Request accepted for processing
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Rate Limits

Currently, no rate limits are enforced. Future releases will implement:
- 1000 requests per hour per API key
- 100 ingestion requests per hour per API key
- Burst allowance for short-term spikes

## Examples

### Basic Content Ingestion
```bash
# Submit URL for processing
curl -X POST http://127.0.0.1:8000/resources \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/machine-learning-guide"}'

# Check processing status
curl http://127.0.0.1:8000/resources/{resource_id}/status

# Retrieve processed resource
curl http://127.0.0.1:8000/resources/{resource_id}
```

### Advanced Search
```bash
# Hybrid search with semantic similarity
curl -X POST http://127.0.0.1:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "text": "artificial intelligence algorithms",
    "hybrid_weight": 0.7,
    "filters": {
      "min_quality": 0.8,
      "subject_any": ["Machine Learning", "AI"]
    },
    "limit": 10
  }'
```

### Knowledge Graph Exploration
```bash
# Find related resources for mind-map
curl "http://127.0.0.1:8000/graph/resource/{resource_id}/neighbors?limit=7"

# Get global relationship overview
curl "http://127.0.0.1:8000/graph/overview?limit=50&vector_threshold=0.85"
```

### Personalized Recommendations
```bash
# Get content recommendations
curl "http://127.0.0.1:8000/recommendations?limit=10"
```

### Collection Management
```bash
# Create a new collection
curl -X POST http://127.0.0.1:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Machine Learning Papers",
    "description": "Curated collection of ML research",
    "visibility": "public"
  }'

# Add resources to collection
curl -X POST http://127.0.0.1:8000/collections/{collection_id}/resources \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": [
      "550e8400-e29b-41d4-a716-446655440000",
      "660e8400-e29b-41d4-a716-446655440001"
    ]
  }'

# Get collection with member resources
curl "http://127.0.0.1:8000/collections/{collection_id}"

# Get recommendations based on collection
curl "http://127.0.0.1:8000/collections/{collection_id}/recommendations?limit=10"

# Create nested collection
curl -X POST http://127.0.0.1:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Deep Learning Subset",
    "parent_id": "{parent_collection_id}",
    "visibility": "public"
  }'
```

### Annotation and Active Reading
```bash
# Create annotation on a resource
curl -X POST http://127.0.0.1:8000/resources/{resource_id}/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "start_offset": 150,
    "end_offset": 200,
    "highlighted_text": "This is the key finding of the paper",
    "note": "Important result - contradicts previous assumptions",
    "tags": ["key-finding", "methodology"],
    "color": "#FFD700"
  }'

# Search annotations semantically
curl "http://127.0.0.1:8000/annotations/search/semantic?query=machine+learning+algorithms&limit=10"

# Export annotations to Markdown
curl "http://127.0.0.1:8000/annotations/export/markdown?resource_id={resource_id}"

# List all user annotations
curl "http://127.0.0.1:8000/annotations?limit=50&sort_by=recent"
```

### Three-Way Hybrid Search (Phase 8)
```bash
# Three-way hybrid search with reranking
curl -X GET "http://127.0.0.1:8000/search/three-way-hybrid?query=machine+learning&limit=20&enable_reranking=true&adaptive_weighting=true"

# Compare all search methods side-by-side
curl -X GET "http://127.0.0.1:8000/search/compare-methods?query=neural+networks&limit=10"

# Evaluate search quality with metrics
curl -X POST http://127.0.0.1:8000/search/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "deep learning",
    "relevance_judgments": {
      "resource_id_1": 3,
      "resource_id_2": 2,
      "resource_id_3": 1
    }
  }'

# Generate sparse embeddings for existing resources
curl -X POST http://127.0.0.1:8000/admin/sparse-embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 32}'

# Three-way search without reranking (faster)
curl -X GET "http://127.0.0.1:8000/search/three-way-hybrid?query=artificial+intelligence&limit=20&enable_reranking=false"

# Three-way search with custom weighting (disable adaptive)
curl -X GET "http://127.0.0.1:8000/search/three-way-hybrid?query=data+science&limit=20&adaptive_weighting=false"
```

### ML Classification & Taxonomy Management (Phase 8.5)
```bash
# Create a taxonomy node
curl -X POST http://127.0.0.1:8000/taxonomy/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Machine Learning",
    "description": "ML and deep learning topics",
    "keywords": ["neural networks", "deep learning"],
    "allow_resources": true
  }'

# Create a child node
curl -X POST http://127.0.0.1:8000/taxonomy/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Deep Learning",
    "parent_id": "{parent_node_id}",
    "description": "Neural networks with multiple layers"
  }'

# Get the full taxonomy tree
curl "http://127.0.0.1:8000/taxonomy/tree"

# Get a subtree starting from a specific node
curl "http://127.0.0.1:8000/taxonomy/tree?root_id={node_id}&max_depth=3"

# Get ancestors (breadcrumb trail)
curl "http://127.0.0.1:8000/taxonomy/nodes/{node_id}/ancestors"

# Get all descendants
curl "http://127.0.0.1:8000/taxonomy/nodes/{node_id}/descendants"

# Move a node to a different parent
curl -X POST http://127.0.0.1:8000/taxonomy/nodes/{node_id}/move \
  -H "Content-Type: application/json" \
  -d '{"new_parent_id": "{new_parent_id}"}'

# Classify a resource using ML
curl -X POST "http://127.0.0.1:8000/taxonomy/classify/{resource_id}"

# Get uncertain predictions for human review
curl "http://127.0.0.1:8000/taxonomy/active-learning/uncertain?limit=50"

# Submit human feedback on classification
curl -X POST http://127.0.0.1:8000/taxonomy/active-learning/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "resource_id": "{resource_id}",
    "correct_taxonomy_ids": ["{node_id_1}", "{node_id_2}"]
  }'

# Train/fine-tune the ML model
curl -X POST http://127.0.0.1:8000/taxonomy/train \
  -H "Content-Type: application/json" \
  -d '{
    "labeled_data": [
      {
        "text": "Introduction to neural networks and backpropagation",
        "taxonomy_ids": ["{ml_node_id}", "{dl_node_id}"]
      }
    ],
    "unlabeled_texts": [
      "Article about convolutional neural networks",
      "Tutorial on recurrent neural networks"
    ],
    "epochs": 3,
    "batch_size": 16
  }'
```

## Testing

Run the comprehensive test suite:

```bash
# All tests
pytest backend/tests/ -v

# With coverage reporting
pytest backend/tests/ --cov=backend --cov-report=html

# Specific test categories
pytest backend/tests/ -m "recommendation"  # Recommendation system tests
pytest backend/tests/ -m "integration"     # Integration tests
```

## Development Phases

### Phase 0: Foundation
- Database schema and models
- Migration system
- Configuration management

### Phase 1: Content Ingestion
- URL processing and content extraction
- Basic metadata extraction
- Local content archiving

### Phase 2: CRUD Operations
- Resource management endpoints
- Curation workflows
- Batch operations

### Phase 3: Search and Discovery
- Full-text search with FTS5
- Faceted search capabilities
- Advanced filtering

### Phase 3.5: AI Integration
- Asynchronous processing
- AI-powered summarization and tagging
- Quality assessment algorithms

### Phase 4: Vector Search
- Semantic embeddings
- Hybrid search fusion
- Vector similarity search

### Phase 5: Knowledge Graph
- Relationship detection
- Graph-based exploration
- Mind-map visualization

### Phase 5.5: Recommendations
- Personalized content recommendations
- External content sourcing
- Explainable recommendation reasoning

### Phase 6: Citation Network & Link Intelligence ✅
- Citation extraction from HTML, PDF, and Markdown
- Internal citation resolution (link resources together)
- PageRank-style importance scoring
- Citation graph visualization endpoints
- Integration with knowledge graph service

### Phase 6.5: Advanced Metadata Extraction & Scholarly Processing ✅
- Fine-tuned metadata extraction for academic papers (authors, DOI, affiliations, funding)
- Mathematical equation extraction with LaTeX format preservation
- Table extraction with structure preservation (camelot-py + tabula-py)
- Figure/image extraction with caption detection
- OCR processing for scanned PDFs with error correction
- Metadata validation and completeness scoring
- Scholarly metadata API endpoints for comprehensive access
- Integration with quality service for metadata quality scoring

### Phase 7: Collection Management ✅
- User-curated collections for organizing resources into thematic groups
- Hierarchical collection organization with parent/child relationships
- Flexible visibility controls (private, shared, public) for collaboration
- Aggregate embedding computation for collection-level semantic representation
- Intelligent recommendations based on collection similarity
- Resource membership management with batch operations
- Automatic collection updates when resources are deleted
- Integration with existing search and recommendation infrastructure

### Phase 7.5: Annotation & Active Reading System ✅
- Character-offset-based text highlighting with precise positioning
- Rich annotation notes with automatic semantic embedding generation
- Tag-based organization with color-coding for visual categorization
- Full-text search across notes and highlighted text (<100ms for 10K annotations)
- Semantic search using cosine similarity for conceptual discovery
- Markdown and JSON export for integration with external note-taking tools
- Collection integration for project-based annotation organization
- Privacy-first design with optional annotation sharing
- Performance: <50ms annotation creation, <500ms semantic search, <2s export for 1K annotations

### Phase 8: Three-Way Hybrid Search with Sparse Vectors & Reranking ✅
- Sparse vector embeddings using BGE-M3 model for learned keyword representations
- Three-way retrieval combining FTS5, dense vectors, and sparse vectors
- Reciprocal Rank Fusion (RRF) for score-agnostic result merging
- Query-adaptive weighting that automatically adjusts method importance
- ColBERT-style cross-encoder reranking for maximum precision
- Comprehensive search metrics (nDCG, Recall, Precision, MRR)
- Method comparison endpoints for debugging and optimization
- Batch sparse embedding generation with progress tracking
- Performance: <200ms three-way search, <1s reranking, 30%+ nDCG improvement

### Phase 8: Three-Way Hybrid Search with Sparse Vectors & Reranking ✅
- Sparse vector embeddings using BGE-M3 model for learned keyword representations
- Three-way retrieval combining FTS5, dense vectors, and sparse vectors
- Reciprocal Rank Fusion (RRF) for score-agnostic result merging
- Query-adaptive weighting that automatically adjusts method importance
- ColBERT-style cross-encoder reranking for maximum precision
- Comprehensive search metrics (nDCG, Recall, Precision, MRR)
- Method comparison endpoints for debugging and optimization
- Batch sparse embedding generation with progress tracking
- Performance: <200ms three-way search, <1s reranking, 30%+ nDCG improvement

### Phase 8.5: ML Classification & Hierarchical Taxonomy ✅
- Transformer-based classification using fine-tuned BERT/DistilBERT models
- Hierarchical taxonomy tree with unlimited depth and parent-child relationships
- Multi-label classification with confidence scores (0.0-1.0) for each category
- Semi-supervised learning to leverage unlabeled data with <500 labeled examples
- Active learning workflow to identify uncertain predictions for human review
- Materialized path pattern for efficient ancestor/descendant queries
- Model versioning and checkpoint management for rollback capability
- GPU acceleration support with automatic CPU fallback
- Automatic classification during resource ingestion pipeline
- Performance: <100ms inference, F1 score >0.85, 60%+ reduction in labeling effort

## Production Deployment

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended for AI features
- **Storage**: SSD recommended for database performance (minimum 20GB free space)
- **Network**: Stable internet connection for content ingestion
- **Database**: PostgreSQL 15+ for production (SQLite for development)

### Database Selection Guide

#### SQLite (Development & Small Deployments)
**Use Cases:**
- Local development and testing
- Single-user deployments
- Prototyping and demos
- Small datasets (<10,000 resources)

**Advantages:**
- Zero configuration required
- File-based (portable)
- No separate database server needed
- Perfect for development

**Limitations:**
- Limited concurrent writes (single writer)
- No advanced indexing (GIN, JSONB)
- File locking can cause issues under load
- Not suitable for production with multiple users

#### PostgreSQL (Production & High Concurrency)
**Use Cases:**
- Production deployments
- Multi-user environments
- High concurrency requirements (100+ simultaneous users)
- Large datasets (>10,000 resources)
- Advanced search and analytics

**Advantages:**
- Excellent concurrent write performance
- Advanced indexing (GIN indexes for JSONB, full-text search)
- Native JSONB support for efficient JSON queries
- Connection pooling with health checks
- Production-grade reliability and ACID compliance
- Point-in-time recovery and replication support

**Requirements:**
- PostgreSQL 15 or higher
- Dedicated database server or managed service (AWS RDS, Google Cloud SQL, Azure Database)
- Regular backups and monitoring

### PostgreSQL Setup for Production

#### Option 1: Docker Compose (Recommended for Development/Staging)
```bash
# Start PostgreSQL with Docker
cd backend/docker
docker-compose up -d postgres

# Verify PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs postgres
```

#### Option 2: Managed Database Service (Recommended for Production)
**AWS RDS:**
```bash
# Create PostgreSQL RDS instance
aws rds create-db-instance \
  --db-instance-identifier neo-alexandria-prod \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.4 \
  --master-username admin \
  --master-user-password <secure-password> \
  --allocated-storage 100 \
  --backup-retention-period 7 \
  --multi-az
```

**Google Cloud SQL:**
```bash
# Create PostgreSQL instance
gcloud sql instances create neo-alexandria-prod \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-7680 \
  --region=us-central1 \
  --backup \
  --backup-start-time=02:00
```

#### Option 3: Self-Hosted PostgreSQL
```bash
# Install PostgreSQL 15 (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql-15 postgresql-contrib-15

# Create database and user
sudo -u postgres psql
CREATE DATABASE neo_alexandria;
CREATE USER neo_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE neo_alexandria TO neo_user;
\q
```

### Migration from SQLite to PostgreSQL

**Prerequisites:**
- Backup your SQLite database
- PostgreSQL 15+ installed and running
- Python environment with all dependencies

**Migration Steps:**
```bash
# 1. Backup SQLite database
cp backend.db backend.db.backup

# 2. Set up PostgreSQL connection
export DATABASE_URL="postgresql://user:password@host:5432/database"

# 3. Run schema migrations
cd backend
alembic upgrade head

# 4. Migrate data from SQLite to PostgreSQL
python scripts/migrate_sqlite_to_postgresql.py \
  --source sqlite:///./backend.db \
  --target postgresql://user:password@host:5432/database \
  --validate

# 5. Verify migration
# Check row counts match between source and target

# 6. Update environment configuration
# Edit .env file
DATABASE_URL=postgresql://user:password@host:5432/database

# 7. Restart application
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

**Migration Validation:**
```bash
# Compare row counts
python -c "
from sqlalchemy import create_engine, inspect
sqlite_engine = create_engine('sqlite:///./backend.db')
pg_engine = create_engine('postgresql://user:password@host:5432/database')

for table in inspect(sqlite_engine).get_table_names():
    sqlite_count = sqlite_engine.execute(f'SELECT COUNT(*) FROM {table}').scalar()
    pg_count = pg_engine.execute(f'SELECT COUNT(*) FROM {table}').scalar()
    print(f'{table}: SQLite={sqlite_count}, PostgreSQL={pg_count}')
"
```

### Database Backup Strategy

#### PostgreSQL Backups
```bash
# Full database backup
pg_dump -h localhost -U postgres -d neo_alexandria > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -h localhost -U postgres -d neo_alexandria | gzip > backup_$(date +%Y%m%d).sql.gz

# Custom format (supports parallel restore)
pg_dump -h localhost -U postgres -d neo_alexandria -Fc > backup_$(date +%Y%m%d).dump
```

**Automated Backup Script:**
```bash
# Use the provided backup script
chmod +x backend/scripts/backup_postgresql.sh
./backend/scripts/backup_postgresql.sh

# Schedule with cron (daily at 2 AM)
crontab -e
0 2 * * * /path/to/backend/scripts/backup_postgresql.sh
```

**Backup Retention Policy:**
- Daily backups: Keep for 7 days
- Weekly backups: Keep for 4 weeks
- Monthly backups: Keep for 12 months

#### SQLite Backups
```bash
# Simple file copy
cp backend.db backend.db.backup_$(date +%Y%m%d)

# Using SQLite backup command
sqlite3 backend.db ".backup 'backend.db.backup_$(date +%Y%m%d)'"
```

### Monitoring and Performance

#### Connection Pool Monitoring
```bash
# Check connection pool status
curl http://localhost:8000/monitoring/database

# Response includes:
# - database_type: "postgresql" or "sqlite"
# - pool_size: 20 (PostgreSQL)
# - connections_in_use: current active connections
# - connections_available: idle connections
# - overflow_connections: connections beyond pool_size
```

#### Performance Tuning (PostgreSQL)
```sql
-- Check slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Check cache hit ratio (should be >90%)
SELECT 
  sum(heap_blks_read) as heap_read,
  sum(heap_blks_hit) as heap_hit,
  sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;
```

### Rollback Procedures

If you need to rollback from PostgreSQL to SQLite:

```bash
# 1. Stop the application
pkill -f "uvicorn backend.app.main:app"

# 2. Run reverse migration
python backend/scripts/migrate_postgresql_to_sqlite.py \
  --source postgresql://user:password@host:5432/database \
  --target sqlite:///./backend.db \
  --validate

# 3. Update environment
DATABASE_URL=sqlite:///./backend.db

# 4. Restart application
uvicorn backend.app.main:app --reload
```

**⚠️ Rollback Limitations:**
- JSONB columns converted to JSON text (no binary optimization)
- PostgreSQL full-text search vectors not migrated (FTS5 must be rebuilt)
- Some PostgreSQL-specific indexes cannot be recreated in SQLite
- Performance may degrade for large datasets

### Security Considerations
- **Database Security:**
  - Use strong passwords for database users
  - Enable SSL/TLS for database connections in production
  - Restrict database access to application servers only
  - Regular security updates for PostgreSQL
  
- **Application Security:**
  - API key authentication (future release)
  - Rate limiting and abuse prevention
  - Input validation and sanitization
  - Secure content storage and access controls

### Additional Resources
- **[PostgreSQL Migration Guide](backend/docs/POSTGRESQL_MIGRATION_GUIDE.md)** - Complete migration procedures
- **[PostgreSQL Backup Guide](backend/docs/POSTGRESQL_BACKUP_GUIDE.md)** - Backup and recovery procedures
- **[SQLite Compatibility Guide](backend/docs/SQLITE_COMPATIBILITY_MAINTENANCE.md)** - Maintaining compatibility
- **[Developer Guide](backend/docs/DEVELOPER_GUIDE.md)** - Database configuration details

## Support and Documentation

### Comprehensive Documentation
- **[API Reference](docs/API_DOCUMENTATION.md)** - Complete endpoint documentation
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Architecture and development setup
- **[Examples](docs/EXAMPLES.md)** - Practical usage examples and tutorials
- **[Changelog](docs/CHANGELOG.md)** - Version history and release notes

### Community and Support
- GitHub Issues for bug reports and feature requests
- Documentation updates and improvements
- Community contributions and feedback

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

We welcome contributions to Neo Alexandria 2.0. Please see our contributing guidelines in the documentation for details on:
- Code style and standards
- Testing requirements
- Documentation standards
- Pull request process

## Roadmap

### Upcoming Features
- API key authentication and rate limiting
- Advanced analytics and reporting
- Multi-user support and permissions
- Enhanced recommendation algorithms
- Real-time collaboration features
- Mobile API optimizations

### Long-term Vision
- Distributed knowledge graph federation
- Advanced AI model integration
- Enterprise-grade security and compliance
- Scalable cloud deployment options
- Integration with popular knowledge management tools

<div style='page-break-after: always;'></div>

---

