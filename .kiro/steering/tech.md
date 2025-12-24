# Neo Alexandria 2.0 - Technical Stack

## Architecture

**Type**: Modular Monolith (transitioning from layered architecture)
**Pattern**: Event-driven with vertical slices
**Deployment**: Self-hosted, containerized

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

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Lint and format
ruff check .
ruff format .
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
- Health check endpoints
- Database connection pool monitoring
- ML model performance tracking
- Error tracking and alerting (planned)
