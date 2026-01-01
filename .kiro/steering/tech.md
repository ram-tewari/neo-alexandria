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
- **hypothesis** - Property-based testing
- **Golden Data Pattern** - Immutable test expectations in JSON files
- **Protocol-Based Testing** - Anti-gaslighting test framework

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

### Testing Patterns

```bash
# Protocol-based testing (Golden Data pattern)
# Tests load expectations from immutable JSON files
# Never modify tests to match implementation - fix implementation instead

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
