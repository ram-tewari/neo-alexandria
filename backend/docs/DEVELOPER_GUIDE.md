# Neo Alexandria 2.0 Developer Guide

## Overview

This comprehensive developer guide provides detailed documentation for developers working with Neo Alexandria 2.0. It covers the system architecture, code structure, development setup, testing procedures, and deployment strategies for the complete knowledge management platform through Phase 5.5.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Development Setup](#development-setup)
- [Code Architecture](#code-architecture)
- [Testing Framework](#testing-framework)
- [Deployment Guide](#deployment-guide)
- [Contributing Guidelines](#contributing-guidelines)
- [Troubleshooting](#troubleshooting)

## Architecture Overview

### System Architecture

Neo Alexandria 2.0 implements a modern, API-first architecture with the following key components:

#### Core Components

1. **API Layer** - FastAPI-based RESTful API with automatic OpenAPI documentation
2. **Service Layer** - Business logic and processing services
3. **Data Layer** - SQLAlchemy ORM with database abstraction
4. **AI Processing** - Asynchronous AI-powered content analysis
5. **Search Engine** - Hybrid keyword and semantic search capabilities
6. **Knowledge Graph** - Relationship detection and graph-based exploration
7. **Recommendation Engine** - Personalized content recommendations

#### Data Flow Architecture

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

#### Technology Stack

**Core Framework:**
- FastAPI 0.104.1 - Modern, fast web framework with automatic API documentation
- SQLAlchemy 2.0.23 - Advanced ORM with async support
- Pydantic 2.5.2 - Data validation and serialization

**AI and Machine Learning:**
- Hugging Face Transformers 4.38.2 - State-of-the-art NLP models
- PyTorch 2.2.1 - Deep learning framework
- sentence-transformers - Semantic embedding generation
- numpy - Numerical computing and vector operations

**Content Processing:**
- httpx 0.27.2 - Modern HTTP client with async support
- BeautifulSoup4 4.12.3 - HTML parsing and extraction
- PyMuPDF 1.23.26 - Fast PDF text extraction
- pdfminer.six - PDF processing fallback
- readability-lxml 0.8.1 - Content extraction and cleaning

**Database and Storage:**
- SQLite - Development and testing database
- PostgreSQL - Production database (optional)
- Alembic 1.13.1 - Database migration management

**Search and Discovery:**
- SQLite FTS5 - Full-text search capabilities
- Custom vector similarity - Semantic search implementation
- Hybrid search fusion - Combined keyword and semantic search

## Project Structure

```
neo_alexandria/
├── app/                          # Main application package
│   ├── __init__.py              # FastAPI application factory
│   ├── main.py                  # Application entry point
│   ├── config/                  # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py          # Pydantic settings with environment variables
│   ├── database/                # Database layer
│   │   ├── __init__.py
│   │   ├── base.py              # SQLAlchemy engine and session management
│   │   └── models.py            # Database models and relationships
│   ├── routers/                 # API endpoint definitions
│   │   ├── __init__.py
│   │   ├── resources.py         # Resource CRUD and ingestion endpoints
│   │   ├── search.py            # Search and discovery endpoints
│   │   ├── curation.py          # Curation and quality control endpoints
│   │   ├── authority.py         # Authority control endpoints
│   │   ├── classification.py    # Classification system endpoints
│   │   ├── graph.py             # Knowledge graph endpoints
│   │   └── recommendation.py    # Recommendation system endpoints
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── ai_core.py           # AI processing and embedding generation
│   │   ├── resource_service.py  # Resource management and ingestion
│   │   ├── search_service.py    # Search and discovery logic
│   │   ├── hybrid_search_methods.py # Vector search and score fusion
│   │   ├── authority_service.py # Authority control and normalization
│   │   ├── classification_service.py # Classification system logic
│   │   ├── quality_service.py   # Quality assessment algorithms
│   │   ├── curation_service.py  # Curation workflows
│   │   ├── graph_service.py     # Knowledge graph processing
│   │   ├── recommendation_service.py # Recommendation engine
│   │   └── dependencies.py      # Dependency injection
│   ├── schemas/                 # Data validation schemas
│   │   ├── __init__.py
│   │   ├── resource.py          # Resource validation schemas
│   │   ├── search.py            # Search request/response schemas
│   │   ├── query.py             # Query parameter schemas
│   │   ├── graph.py             # Graph data schemas
│   │   └── recommendation.py    # Recommendation schemas
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   ├── content_extractor.py # Content extraction and processing
│   │   └── text_processor.py    # Text processing and analysis
│   └── monitoring.py            # Application monitoring and metrics
├── alembic/                     # Database migrations
│   ├── versions/                # Migration files
│   │   ├── f3e272b2b6cd_initial_schema_with_enhanced_resource_.py
│   │   ├── 20250910_add_fts_and_triggers.py
│   │   ├── 20250911_add_authority_tables.py
│   │   ├── 20250911_add_ingestion_status_fields.py
│   │   ├── 20250912_add_classification_codes.py
│   │   └── 20250912_add_vector_embeddings.py
│   ├── env.py                   # Alembic environment configuration
│   └── script.py.mako           # Migration template
├── tests/                       # Comprehensive test suite
│   ├── conftest.py              # Test configuration and fixtures
│   ├── test_*.py                # Test modules for each component
│   ├── test_recommendation_config.py # Recommendation test utilities
│   └── run_recommendation_tests.py # Specialized test runner
├── docs/                        # Documentation
│   ├── README.md                # Documentation index
│   ├── API_DOCUMENTATION.md     # Complete API reference
│   ├── DEVELOPER_GUIDE.md       # This file
│   ├── EXAMPLES.md              # Usage examples and tutorials
│   └── CHANGELOG.md             # Version history
├── monitoring/                  # Monitoring configuration
│   ├── prometheus.yml           # Prometheus metrics configuration
│   └── grafana/                 # Grafana dashboard configuration
├── storage/                     # Local content storage
│   └── archive/                 # Archived content files
├── alembic.ini                  # Alembic configuration
├── requirements.txt             # Python dependencies
├── pytest.ini                  # Pytest configuration
├── gunicorn.conf.py             # Production WSGI configuration
├── Dockerfile                   # Container configuration
├── docker-compose.yml           # Multi-service deployment
└── README.md                    # Project overview
```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- SQLite (included with Python)
- 4GB RAM minimum (8GB recommended for AI features)
- 2GB free disk space

### Installation Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd backend
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Create .env file (optional)
cp .env.example .env
# Edit .env with your configuration
```

5. **Run database migrations**
```bash
alembic upgrade head
```

6. **Start development server**
```bash
uvicorn backend.app.main:app --reload
```

### Environment Configuration

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=sqlite:///backend.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/backend

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

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
```

### Development Tools

**Code Quality:**
```bash
# Format code
black backend/
isort backend/

# Lint code
flake8 backend/
mypy backend/

# Type checking
mypy backend/app/
```

**Database Management:**
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check current migration
alembic current
```

## Code Architecture

### Application Factory Pattern

The application uses FastAPI's application factory pattern for clean separation of concerns:

```python
# app/__init__.py
def create_app() -> FastAPI:
    app = FastAPI(
        title="Neo Alexandria 2.0",
        description="Advanced Knowledge Management System",
        version="0.7.0"
    )
    
    # Include routers
    app.include_router(resources_router)
    app.include_router(search_router)
    # ... other routers
    
    return app
```

### Dependency Injection

Services use dependency injection for testability and modularity:

```python
# app/services/dependencies.py
def get_ai_core() -> AICore:
    return AICore()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Service Layer Architecture

Each service follows a consistent pattern:

```python
class ResourceService:
    def __init__(self, db: Session, ai_core: AICore):
        self.db = db
        self.ai_core = ai_core
    
    async def create_resource(self, resource_data: ResourceCreate) -> Resource:
        # Business logic implementation
        pass
    
    async def get_resource(self, resource_id: UUID) -> Resource:
        # Data retrieval logic
        pass
```

### Database Models

Models use SQLAlchemy 2.0 syntax with proper relationships:

```python
class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    # ... other fields
    
    # Relationships
    subjects = relationship("AuthoritySubject", secondary=resource_subjects)
```

### Schema Validation

Pydantic schemas provide request/response validation:

```python
class ResourceCreate(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/article",
                "title": "Example Article"
            }
        }
```

## Testing Framework

### Test Structure

The testing framework provides comprehensive coverage:

```
tests/
├── conftest.py                  # Global test configuration
├── test_*.py                    # Component-specific tests
├── test_recommendation_config.py # Test utilities
└── run_recommendation_tests.py  # Specialized test runner
```

### Test Categories

**Unit Tests:**
- Individual function testing
- Mock external dependencies
- Fast execution (< 1 second per test)

**Integration Tests:**
- End-to-end workflow testing
- Database integration
- API endpoint testing

**Performance Tests:**
- Load testing
- Memory usage validation
- Response time benchmarks

### Running Tests

```bash
# All tests
pytest backend/tests/ -v

# Specific test categories
pytest backend/tests/ -m "unit"
pytest backend/tests/ -m "integration"
pytest backend/tests/ -m "recommendation"

# With coverage
pytest backend/tests/ --cov=backend --cov-report=html

# Performance tests
pytest backend/tests/ -m "performance"

# Recommendation system tests
python backend/tests/run_recommendation_tests.py all
```

### Test Fixtures

Common test fixtures are available in `conftest.py`:

```python
@pytest.fixture
def test_db():
    """Create isolated test database"""
    pass

@pytest.fixture
def mock_ai_core():
    """Mock AI processing for tests"""
    pass

@pytest.fixture
def sample_resources():
    """Sample data for testing"""
    pass
```

## Deployment Guide

### Development Deployment

**Local Development:**
```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Docker Development:**
```bash
docker-compose up --build
```

### Production Deployment

**System Requirements:**
- CPU: 4+ cores
- RAM: 8GB minimum, 16GB recommended
- Storage: SSD recommended
- Network: Stable internet connection

**Environment Setup:**
```bash
# Production environment variables
export DATABASE_URL=postgresql://user:password@localhost/backend
export DEBUG=false
export LOG_LEVEL=WARNING
```

**Database Setup:**
```bash
# PostgreSQL setup
createdb backend
alembic upgrade head
```

**Application Deployment:**
```bash
# Using Gunicorn
gunicorn backend.app.main:app -c gunicorn.conf.py

# Using Docker
docker build -t neo-alexandria .
docker run -p 8000:8000 neo-alexandria
```

### Monitoring and Logging

**Application Monitoring:**
- Prometheus metrics collection
- Grafana dashboards
- Health check endpoints
- Performance monitoring

**Logging Configuration:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler()
    ]
)
```

### Security Considerations

**Production Security:**
- API key authentication (future release)
- Rate limiting and abuse prevention
- Input validation and sanitization
- Secure content storage
- HTTPS enforcement
- Database connection encryption

## Contributing Guidelines

### Code Standards

**Python Style:**
- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import organization
- Type hints for all functions
- Comprehensive docstrings

**Commit Messages:**
```
feat: add new recommendation endpoint
fix: resolve search performance issue
docs: update API documentation
test: add integration tests for graph service
```

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**
```bash
git checkout -b feature/new-feature
```

3. **Make changes with tests**
4. **Run test suite**
```bash
pytest backend/tests/ -v
```

5. **Submit pull request**

### Pull Request Requirements

- All tests must pass
- Code coverage maintained
- Documentation updated
- No linting errors
- Clear commit messages
- Description of changes

## Troubleshooting

### Common Issues

**Database Connection Issues:**
```bash
# Check database file permissions
ls -la backend.db

# Verify migration status
alembic current

# Reset database (development only)
rm backend.db
alembic upgrade head
```

**AI Model Loading Issues:**
```bash
# Check available memory
free -h

# Verify model downloads
python -c "from transformers import pipeline; print('Models available')"

# Clear model cache
rm -rf ~/.cache/huggingface/
```

**Search Performance Issues:**
```bash
# Check FTS5 availability
sqlite3 backend.db "SELECT fts5();"

# Rebuild search index
sqlite3 backend.db "DELETE FROM resources_fts; INSERT INTO resources_fts(resources_fts) VALUES('rebuild');"
```

### Performance Optimization

**Database Optimization:**
- Use PostgreSQL for production
- Add appropriate indexes
- Regular VACUUM operations
- Connection pooling

**AI Processing Optimization:**
- Model caching
- Batch processing
- GPU acceleration (if available)
- Async processing

**Search Optimization:**
- Vector index optimization
- Query result caching
- Search result pagination
- Hybrid search tuning

### Debug Mode

Enable debug mode for development:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
uvicorn backend.app.main:app --reload
```

### Health Checks

Monitor application health:

```bash
# Basic health check
curl http://127.0.0.1:8000/health

# Database connectivity
curl http://127.0.0.1:8000/health/db

# AI service status
curl http://127.0.0.1:8000/health/ai
```

## Additional Resources

### Documentation
- [API Reference](API_DOCUMENTATION.md) - Complete endpoint documentation
- [Examples](EXAMPLES.md) - Usage examples and tutorials
- [Changelog](CHANGELOG.md) - Version history and changes

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)

### Community
- GitHub Issues for bug reports
- Feature request discussions
- Community contributions
- Documentation improvements