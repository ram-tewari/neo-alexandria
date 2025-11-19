# Neo Alexandria 2.0 Developer Guide

## Overview

This comprehensive developer guide provides detailed documentation for developers working with Neo Alexandria 2.0. It covers the system architecture, code structure, development setup, testing procedures, and deployment strategies for the complete knowledge management platform through Phase 5.5.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Development Setup](#development-setup)
- [Code Architecture](#code-architecture)
- [Testing Framework](#testing-framework)
- [ML Benchmarking](#ml-benchmarking)
- [ML Model Training](#ml-model-training)
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
8. **Collection Management** - User-curated collections with semantic embeddings
9. **Annotation System** - Text highlighting and note-taking with semantic search

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
│   │   ├── recommendation.py    # Recommendation system endpoints
│   │   ├── collections.py       # Collection management endpoints
│   │   └── annotations.py       # Annotation management endpoints
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
│   │   ├── collection_service.py # Collection management logic
│   │   ├── annotation_service.py # Annotation management logic
│   │   └── dependencies.py      # Dependency injection
│   ├── schemas/                 # Data validation schemas
│   │   ├── __init__.py
│   │   ├── resource.py          # Resource validation schemas
│   │   ├── search.py            # Search request/response schemas
│   │   ├── query.py             # Query parameter schemas
│   │   ├── graph.py             # Graph data schemas
│   │   ├── recommendation.py    # Recommendation schemas
│   │   ├── collection.py        # Collection validation schemas
│   │   └── annotation.py        # Annotation validation schemas
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

### Collection Service Architecture

The collection service implements a comprehensive system for organizing resources:

#### Many-to-Many Association Pattern

Collections use a many-to-many relationship with resources through an association table:

```python
# Association table
class CollectionResource(Base):
    __tablename__ = "collection_resources"
    
    collection_id = Column(UUID, ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True)
    resource_id = Column(UUID, ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)
    added_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    
    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_collection_resources_collection', 'collection_id'),
        Index('idx_collection_resources_resource', 'resource_id'),
    )

# Collection model
class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String(255), nullable=False, index=True)
    visibility = Column(String(20), nullable=False, default="private", index=True)
    parent_id = Column(UUID, ForeignKey("collections.id", ondelete="CASCADE"), nullable=True, index=True)
    embedding = Column(JSON, nullable=True)
    
    # Relationships
    resources = relationship("Resource", secondary="collection_resources", back_populates="collections")
    parent = relationship("Collection", remote_side=[id], back_populates="subcollections")
    subcollections = relationship("Collection", back_populates="parent", cascade="all, delete-orphan")
```

**Key Design Decisions:**
- **CASCADE DELETE**: Parent deletion automatically removes subcollections
- **Composite Primary Key**: Prevents duplicate resource associations
- **Indexed Foreign Keys**: Optimizes queries for collection membership
- **JSON Embedding Storage**: Cross-database compatibility for vector data

#### Aggregate Embedding Computation

Collections compute semantic representations from member resources:

```python
def compute_aggregate_embedding(resource_embeddings: List[List[float]]) -> List[float]:
    """
    Compute mean embedding from resource embeddings.
    
    Algorithm:
    1. Stack embeddings into matrix (n x d)
    2. Compute column-wise mean
    3. Normalize to unit length (L2 norm)
    4. Return as list
    """
    if not resource_embeddings:
        return None
    
    import numpy as np
    
    # Stack into matrix
    matrix = np.array(resource_embeddings)
    
    # Compute mean
    mean_vector = np.mean(matrix, axis=0)
    
    # Normalize to unit length
    norm = np.linalg.norm(mean_vector)
    if norm > 0:
        mean_vector = mean_vector / norm
    
    return mean_vector.tolist()
```

**Performance Characteristics:**
- Time Complexity: O(n × d) where n = resources, d = embedding dimension
- Space Complexity: O(n × d) for matrix storage
- Target Performance: <1 second for 1000 resources
- Uses NumPy for efficient vector operations

**Automatic Updates:**
- Embedding recomputed when resources added
- Embedding recomputed when resources removed
- Embedding set to null if no member resources have embeddings
- Triggered automatically by membership operations

#### Hierarchy Validation

Collections prevent circular references in parent-child relationships:

```python
def validate_hierarchy(collection_id: str, new_parent_id: str) -> bool:
    """
    Prevent circular references in hierarchy.
    
    Algorithm:
    1. Start at new_parent_id
    2. Traverse up parent chain
    3. If collection_id encountered → cycle detected
    4. If None reached → valid hierarchy
    5. Limit traversal depth to 10 levels
    """
    if new_parent_id is None:
        return True  # Top-level collection
    
    visited = set()
    current_id = new_parent_id
    depth = 0
    max_depth = 10
    
    while current_id is not None and depth < max_depth:
        if current_id == collection_id:
            raise ValueError("Circular reference detected in collection hierarchy")
        
        if current_id in visited:
            raise ValueError("Cycle detected in collection hierarchy")
        
        visited.add(current_id)
        
        # Get parent of current collection
        collection = db.query(Collection).filter(Collection.id == current_id).first()
        if collection is None:
            raise ValueError(f"Parent collection {current_id} not found")
        
        current_id = collection.parent_id
        depth += 1
    
    if depth >= max_depth:
        raise ValueError("Collection hierarchy exceeds maximum depth")
    
    return True
```

**Validation Rules:**
- Maximum hierarchy depth: 10 levels
- No circular references allowed
- Parent must exist and be owned by same user
- Validated on collection creation and update

#### Batch Operations

Resource membership supports efficient batch operations:

```python
def add_resources(collection_id: str, user_id: str, resource_ids: List[str]) -> Collection:
    """
    Add resources to collection (batch operation).
    
    Performance optimizations:
    - Validates all resources exist in single query
    - Uses bulk_insert_mappings for batch insert
    - Handles duplicates gracefully (idempotent)
    - Triggers single embedding recomputation
    """
    # Verify ownership
    collection = get_collection(collection_id, user_id)
    if collection.owner_id != user_id:
        raise PermissionError("Only owner can modify collection")
    
    # Validate all resources exist
    resources = db.query(Resource).filter(Resource.id.in_(resource_ids)).all()
    if len(resources) != len(resource_ids):
        raise ValueError("Some resource IDs not found")
    
    # Batch insert associations
    associations = [
        {"collection_id": collection_id, "resource_id": rid}
        for rid in resource_ids
    ]
    db.bulk_insert_mappings(CollectionResource, associations)
    
    # Recompute embedding once
    recompute_embedding(collection_id)
    
    db.commit()
    return collection
```

**Batch Limits:**
- Maximum 100 resources per operation
- Single database transaction
- Bulk operations for performance
- Idempotent (duplicate handling)

#### Access Control Implementation

Collections implement owner-based permissions with visibility levels:

```python
def get_collection(collection_id: str, user_id: str) -> Collection:
    """
    Retrieve collection with access control.
    
    Access Rules:
    - private: Only owner can access
    - shared: Owner + explicit permissions (future)
    - public: All authenticated users
    """
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    
    if collection is None:
        raise ValueError("Collection not found")
    
    # Check access
    if collection.visibility == "private":
        if user_id != collection.owner_id:
            raise PermissionError("Access denied to private collection")
    elif collection.visibility == "public":
        pass  # All authenticated users can access
    elif collection.visibility == "shared":
        # Future: Check explicit permissions
        if user_id != collection.owner_id:
            raise PermissionError("Access denied to shared collection")
    
    return collection
```

**Authorization Patterns:**
- Read operations: Check visibility level
- Write operations: Verify owner_id match
- List operations: Filter by access rules
- Cascade operations: Inherit parent permissions

#### Resource Deletion Integration

Collections automatically update when resources are deleted:

```python
# In resource_service.py
def delete_resource(db: Session, resource_id: str) -> None:
    """
    Delete resource and update affected collections.
    
    Integration steps:
    1. Query affected collections
    2. Delete resource-collection associations
    3. Recompute embeddings for affected collections
    4. Delete resource
    """
    # Find affected collections
    affected_collections = (
        db.query(Collection.id)
        .join(CollectionResource)
        .filter(CollectionResource.resource_id == resource_id)
        .all()
    )
    
    # Delete associations (CASCADE handles this, but explicit is better)
    db.execute(
        delete(CollectionResource).where(CollectionResource.resource_id == resource_id)
    )
    
    # Recompute embeddings for affected collections
    for collection_id in affected_collections:
        collection_service.recompute_embedding(collection_id)
    
    # Delete resource
    db.delete(resource)
    db.commit()
```

**Cleanup Guarantees:**
- No orphaned associations remain
- Embeddings updated automatically
- Resource counts accurate
- Performance: <2 seconds for 100 collections

#### Extending Collection Features

The collection service is designed for extensibility:

**Adding New Visibility Levels:**
```python
# 1. Update visibility enum in model
visibility = Column(String(20), nullable=False, default="private")

# 2. Update access control logic
def check_access(collection, user_id):
    if collection.visibility == "team":
        return user_id in get_team_members(collection.team_id)
    # ... existing logic

# 3. Update schema validation
class CollectionCreate(BaseModel):
    visibility: Literal["private", "shared", "public", "team"] = "private"
```

**Adding Collection Metadata:**
```python
# 1. Add column to model
tags = Column(JSON, nullable=True)

# 2. Update schema
class CollectionCreate(BaseModel):
    tags: List[str] = []

# 3. Add filtering support
def list_collections(tags: List[str] = None):
    query = db.query(Collection)
    if tags:
        query = query.filter(Collection.tags.contains(tags))
    return query.all()
```

**Adding Collection Analytics:**
```python
# 1. Create analytics service
class CollectionAnalytics:
    def get_view_count(self, collection_id: str) -> int:
        pass
    
    def get_popular_resources(self, collection_id: str) -> List[Resource]:
        pass

# 2. Add analytics endpoint
@router.get("/collections/{id}/analytics")
def get_analytics(id: str):
    return analytics_service.get_collection_analytics(id)
```

### Working with Annotations

The annotation system enables users to highlight text passages, add notes, and organize their reading with tags. This section covers the architecture, text offset tracking, and annotation workflows.

#### Annotation Model Architecture

Annotations use character offsets for precise text positioning:

```python
class Annotation(Base):
    __tablename__ = "annotations"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    resource_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("resources.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Text selection (precise positioning)
    start_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    end_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    highlighted_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # User content
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    
    # Visual styling
    color: Mapped[str] = mapped_column(String(7), nullable=False, default="#FFFF00")
    
    # Semantic search
    embedding: Mapped[List[float] | None] = mapped_column(JSON, nullable=True)
    
    # Context preservation
    context_before: Mapped[str | None] = mapped_column(String(50), nullable=True)
    context_after: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Sharing and organization
    is_shared: Mapped[bool] = mapped_column(Integer, nullable=False, default=0)
    collection_ids: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.current_timestamp())
    
    # Relationships
    resource: Mapped["Resource"] = relationship("Resource", back_populates="annotations")
```

**Key Design Decisions:**
- **Character offsets**: More reliable than DOM-based selection, works with any text format
- **JSON for arrays**: Flexible storage for tags and collection IDs without additional tables
- **Context fields**: 50 chars before/after for preview without re-parsing full content
- **Embedding field**: Enables semantic search without external vector database

#### Text Offset Tracking

Annotations use zero-indexed character offsets for precise text positioning:

**Offset Calculation:**
```python
# Example: "Hello World"
text = "Hello World"
start_offset = 0
end_offset = 5
highlighted_text = text[start_offset:end_offset]  # "Hello"
```

**Validation Rules:**
```python
def validate_offsets(start_offset: int, end_offset: int, content_length: int):
    """Validate annotation offsets."""
    if start_offset < 0 or end_offset < 0:
        raise ValidationError("Offsets must be non-negative")
    
    if start_offset >= end_offset:
        raise ValidationError("start_offset must be less than end_offset")
    
    if end_offset > content_length:
        raise ValidationError(f"end_offset exceeds content length")
```

**Advantages:**
- Works with any text format (HTML, PDF, plain text)
- More reliable than DOM-based selection
- Survives content reformatting
- Simple to implement and understand

**Edge Cases:**
```python
# Handle document boundaries
def extract_context(content: str, start: int, end: int, context_size: int = 50):
    """Extract context around highlight."""
    # Context before (handle start of document)
    context_start = max(0, start - context_size)
    context_before = content[context_start:start]
    
    # Context after (handle end of document)
    context_end = min(len(content), end + context_size)
    context_after = content[end:context_end]
    
    return context_before, context_after
```

#### Annotation Service Architecture

The annotation service implements CRUD operations and search functionality:

```python
class AnnotationService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService(db)
    
    def create_annotation(
        self,
        resource_id: str,
        user_id: str,
        start_offset: int,
        end_offset: int,
        highlighted_text: str,
        note: Optional[str] = None,
        tags: Optional[List[str]] = None,
        color: str = "#FFFF00"
    ) -> Annotation:
        """
        Create annotation with validation and context extraction.
        
        Steps:
        1. Validate resource exists and user has access
        2. Validate offsets (start < end, non-negative)
        3. Extract context (50 chars before/after)
        4. Create Annotation record
        5. Enqueue embedding generation if note provided
        6. Return created annotation
        
        Performance: <50ms (excluding embedding)
        """
        # Validate resource
        resource = self.db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            raise ValueError("Resource not found")
        
        # Validate offsets
        validate_offsets(start_offset, end_offset, len(resource.content))
        
        # Extract context
        context_before, context_after = extract_context(
            resource.content, start_offset, end_offset
        )
        
        # Create annotation
        annotation = Annotation(
            id=uuid.uuid4(),
            resource_id=resource_id,
            user_id=user_id,
            start_offset=start_offset,
            end_offset=end_offset,
            highlighted_text=highlighted_text,
            note=note,
            tags=json.dumps(tags) if tags else None,
            color=color,
            context_before=context_before,
            context_after=context_after
        )
        
        self.db.add(annotation)
        self.db.commit()
        
        # Enqueue embedding generation (async)
        if note:
            background_tasks.add_task(
                self._generate_annotation_embedding,
                annotation.id,
                note
            )
        
        return annotation
```

#### Semantic Search Implementation

Annotations support semantic search using cosine similarity:

```python
def search_annotations_semantic(
    self,
    user_id: str,
    query: str,
    limit: int = 10
) -> List[Tuple[Annotation, float]]:
    """
    Search annotations using semantic similarity.
    
    Algorithm:
    1. Generate embedding for query text
    2. Retrieve user annotations with embeddings
    3. Compute cosine similarity for each
    4. Sort by similarity descending
    5. Return top N with scores
    
    Performance: <500ms for 1,000 annotations
    """
    # Generate query embedding
    query_embedding = self.embedding_service.generate_embedding(query)
    
    # Get user annotations with embeddings
    annotations = (
        self.db.query(Annotation)
        .filter(
            Annotation.user_id == user_id,
            Annotation.embedding.isnot(None)
        )
        .all()
    )
    
    # Compute similarities
    results = []
    for annotation in annotations:
        similarity = self._cosine_similarity(
            query_embedding,
            json.loads(annotation.embedding)
        )
        results.append((annotation, similarity))
    
    # Sort by similarity and return top N
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:limit]

def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    import numpy as np
    
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))
```

#### Export Functionality

Annotations can be exported to Markdown or JSON:

```python
def export_annotations_markdown(
    self,
    user_id: str,
    resource_id: Optional[str] = None
) -> str:
    """
    Export annotations to Markdown format.
    
    Algorithm:
    1. Retrieve annotations (filtered by resource if specified)
    2. Group by resource
    3. Format each annotation as Markdown block
    4. Concatenate all sections
    
    Performance: <2s for 1,000 annotations
    """
    # Query annotations
    query = self.db.query(Annotation).filter(Annotation.user_id == user_id)
    if resource_id:
        query = query.filter(Annotation.resource_id == resource_id)
    
    annotations = query.options(joinedload(Annotation.resource)).all()
    
    # Group by resource
    by_resource = {}
    for ann in annotations:
        if ann.resource_id not in by_resource:
            by_resource[ann.resource_id] = []
        by_resource[ann.resource_id].append(ann)
    
    # Format as Markdown
    markdown_parts = ["# Annotations Export\n\n"]
    
    for resource_id, anns in by_resource.items():
        resource_title = anns[0].resource.title
        markdown_parts.append(f"## {resource_title}\n\n")
        
        for i, ann in enumerate(anns, 1):
            markdown_parts.append(f"### Annotation {i}\n")
            markdown_parts.append(f"**Highlighted Text:**\n> {ann.highlighted_text}\n\n")
            
            if ann.note:
                markdown_parts.append(f"**Note:** {ann.note}\n\n")
            
            if ann.tags:
                tags = json.loads(ann.tags)
                markdown_parts.append(f"**Tags:** {', '.join(tags)}\n\n")
            
            markdown_parts.append(f"**Created:** {ann.created_at}\n\n")
            markdown_parts.append("---\n\n")
    
    return "".join(markdown_parts)
```

#### Annotation Workflows

**Creating an Annotation:**
```python
# 1. User selects text in frontend
selection = {
    "start_offset": 150,
    "end_offset": 200,
    "highlighted_text": "This is the key finding"
}

# 2. Frontend sends POST request
response = requests.post(
    f"/resources/{resource_id}/annotations",
    json={
        "start_offset": selection["start_offset"],
        "end_offset": selection["end_offset"],
        "highlighted_text": selection["highlighted_text"],
        "note": "Important result",
        "tags": ["key-finding"],
        "color": "#FFD700"
    }
)

# 3. Backend validates and creates annotation
# 4. Embedding generated asynchronously
# 5. Annotation returned immediately
```

**Searching Annotations:**
```python
# Full-text search
results = annotation_service.search_annotations_fulltext(
    user_id="user123",
    query="machine learning",
    limit=10
)

# Semantic search
results = annotation_service.search_annotations_semantic(
    user_id="user123",
    query="neural network architectures",
    limit=10
)

# Tag-based search
results = annotation_service.search_annotations_by_tags(
    user_id="user123",
    tags=["key-finding", "methodology"],
    match_all=False  # ANY tag
)
```

**Exporting Annotations:**
```python
# Export to Markdown
markdown = annotation_service.export_annotations_markdown(
    user_id="user123",
    resource_id=None  # All resources
)

with open("annotations.md", "w") as f:
    f.write(markdown)

# Export to JSON
json_data = annotation_service.export_annotations_json(
    user_id="user123",
    resource_id=resource_id  # Specific resource
)

with open("annotations.json", "w") as f:
    json.dump(json_data, f, indent=2)
```

#### Performance Optimization

**Database Indexes:**
```sql
-- Fast resource annotation retrieval
CREATE INDEX idx_annotations_resource ON annotations(resource_id);

-- Fast user annotation retrieval
CREATE INDEX idx_annotations_user ON annotations(user_id);

-- Composite index for user-resource filtering
CREATE INDEX idx_annotations_user_resource ON annotations(user_id, resource_id);

-- Sorting by recency
CREATE INDEX idx_annotations_created ON annotations(created_at);
```

### Taxonomy Service Architecture (Phase 8.5)

The taxonomy service manages hierarchical category trees with parent-child relationships using the materialized path pattern for efficient queries.

#### Database Models

**TaxonomyNode Model:**
```python
class TaxonomyNode(Base):
    __tablename__ = "taxonomy_nodes"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    parent_id = Column(UUID, ForeignKey("taxonomy_nodes.id", ondelete="CASCADE"), nullable=True, index=True)
    level = Column(Integer, nullable=False, default=0)
    path = Column(String(1000), nullable=False, index=True)
    description = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)
    resource_count = Column(Integer, nullable=False, default=0)
    descendant_resource_count = Column(Integer, nullable=False, default=0)
    is_leaf = Column(Boolean, nullable=False, default=True)
    allow_resources = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), onupdate=func.current_timestamp())
    
    # Relationships
    parent = relationship("TaxonomyNode", remote_side=[id], back_populates="children")
    children = relationship("TaxonomyNode", back_populates="parent", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('level >= 0', name='check_level_non_negative'),
    )
```

**ResourceTaxonomy Association Model:**
```python
class ResourceTaxonomy(Base):
    __tablename__ = "resource_taxonomy"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    resource_id = Column(UUID, ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    taxonomy_node_id = Column(UUID, ForeignKey("taxonomy_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    is_predicted = Column(Boolean, nullable=False, default=True)
    predicted_by = Column(String(50), nullable=True)
    needs_review = Column(Boolean, nullable=False, default=False, index=True)
    review_priority = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), onupdate=func.current_timestamp())
    
    # Relationships
    resource = relationship("Resource", back_populates="taxonomy_classifications")
    taxonomy_node = relationship("TaxonomyNode")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('confidence >= 0.0 AND confidence <= 1.0', name='check_confidence_range'),
    )
```

#### Materialized Path Pattern

The taxonomy uses materialized paths for efficient hierarchical queries:

```python
# Example hierarchy:
# Computer Science (level=0, path="/computer-science")
#   ├── Machine Learning (level=1, path="/computer-science/machine-learning")
#   │   ├── Deep Learning (level=2, path="/computer-science/machine-learning/deep-learning")
#   │   └── NLP (level=2, path="/computer-science/machine-learning/nlp")
#   └── Databases (level=1, path="/computer-science/databases")

def _compute_path(self, parent: Optional[TaxonomyNode], slug: str) -> str:
    """
    Compute materialized path for a node.
    
    Algorithm:
    1. If no parent → path = "/{slug}"
    2. If parent exists → path = "{parent.path}/{slug}"
    
    Example:
    - Root: "/computer-science"
    - Child: "/computer-science/machine-learning"
    - Grandchild: "/computer-science/machine-learning/deep-learning"
    """
    if parent is None:
        return f"/{slug}"
    return f"{parent.path}/{slug}"
```

**Advantages:**
- **O(1) ancestor queries**: Parse path string
- **O(1) descendant queries**: `path LIKE 'parent_path/%'`
- **No recursive CTEs needed**
- **Efficient with proper indexing**

**Trade-offs:**
- Path updates on reparenting (acceptable for infrequent operations)
- Path length limits (mitigated by slug length limits)

#### Core Operations

**Creating Nodes:**
```python
def create_node(
    self,
    name: str,
    parent_id: Optional[str] = None,
    description: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    allow_resources: bool = True
) -> TaxonomyNode:
    """
    Create taxonomy node with automatic path computation.
    
    Steps:
    1. Validate parent exists (if specified)
    2. Generate slug from name
    3. Compute level = parent.level + 1 (or 0 for root)
    4. Compute path = parent.path + "/" + slug
    5. Create node
    6. Update parent.is_leaf = False
    
    Performance: <10ms
    """
    # Validate parent
    parent = None
    if parent_id:
        parent = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == parent_id).first()
        if not parent:
            raise ValueError(f"Parent node {parent_id} not found")
    
    # Generate slug
    slug = self._slugify(name)
    
    # Compute level and path
    level = parent.level + 1 if parent else 0
    path = self._compute_path(parent, slug)
    
    # Create node
    node = TaxonomyNode(
        id=uuid.uuid4(),
        name=name,
        slug=slug,
        parent_id=parent_id,
        level=level,
        path=path,
        description=description,
        keywords=json.dumps(keywords) if keywords else None,
        allow_resources=allow_resources
    )
    
    self.db.add(node)
    
    # Update parent
    if parent:
        parent.is_leaf = False
    
    self.db.commit()
    return node
```

**Moving Nodes (Reparenting):**
```python
def move_node(self, node_id: str, new_parent_id: Optional[str]) -> TaxonomyNode:
    """
    Move node to different parent with circular reference prevention.
    
    Steps:
    1. Validate node exists
    2. Prevent circular references (check if new_parent is descendant)
    3. Update parent_id
    4. Recalculate level
    5. Recalculate path
    6. Update all descendants' levels and paths
    
    Performance: O(descendants) - typically <50ms
    """
    node = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == node_id).first()
    if not node:
        raise ValueError(f"Node {node_id} not found")
    
    # Prevent circular references
    if new_parent_id and self._is_descendant(new_parent_id, node_id):
        raise ValueError("Cannot move node to its own descendant")
    
    # Get new parent
    new_parent = None
    if new_parent_id:
        new_parent = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == new_parent_id).first()
        if not new_parent:
            raise ValueError(f"New parent {new_parent_id} not found")
    
    # Update node
    node.parent_id = new_parent_id
    node.level = new_parent.level + 1 if new_parent else 0
    node.path = self._compute_path(new_parent, node.slug)
    
    # Update descendants
    self._update_descendants(node)
    
    self.db.commit()
    return node

def _is_descendant(self, potential_descendant_id: str, ancestor_id: str) -> bool:
    """Check if potential_descendant is a descendant of ancestor."""
    descendant = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == potential_descendant_id).first()
    if not descendant:
        return False
    
    ancestor = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == ancestor_id).first()
    if not ancestor:
        return False
    
    # Check if descendant's path starts with ancestor's path
    return descendant.path.startswith(ancestor.path + "/")
```

**Hierarchical Queries:**
```python
def get_ancestors(self, node_id: str) -> List[TaxonomyNode]:
    """
    Get all ancestors using materialized path.
    
    Algorithm:
    1. Get node
    2. Parse path: "/a/b/c" → ["a", "b", "c"]
    3. Query nodes by slugs
    4. Return in hierarchical order
    
    Performance: O(depth) - typically <10ms
    """
    node = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == node_id).first()
    if not node:
        return []
    
    # Parse path
    slugs = [s for s in node.path.split("/") if s]
    
    # Query ancestors
    ancestors = []
    for i in range(len(slugs)):
        path = "/" + "/".join(slugs[:i+1])
        ancestor = self.db.query(TaxonomyNode).filter(TaxonomyNode.path == path).first()
        if ancestor:
            ancestors.append(ancestor)
    
    return ancestors

def get_descendants(self, node_id: str) -> List[TaxonomyNode]:
    """
    Get all descendants using path pattern matching.
    
    Algorithm:
    1. Get node
    2. Query nodes with path LIKE 'node.path/%'
    3. Return all matches
    
    Performance: O(1) query - typically <10ms
    """
    node = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == node_id).first()
    if not node:
        return []
    
    # Query descendants
    descendants = (
        self.db.query(TaxonomyNode)
        .filter(TaxonomyNode.path.like(f"{node.path}/%"))
        .all()
    )
    
    return descendants
```

**Tree Retrieval:**
```python
def get_tree(
    self,
    root_id: Optional[str] = None,
    max_depth: Optional[int] = None
) -> List[Dict]:
    """
    Retrieve taxonomy tree as nested structure.
    
    Algorithm:
    1. Query root nodes (or specific root)
    2. Recursively build tree structure
    3. Limit depth if specified
    
    Performance: O(nodes) - typically <50ms for depth 5
    """
    # Get root nodes
    if root_id:
        roots = [self.db.query(TaxonomyNode).filter(TaxonomyNode.id == root_id).first()]
    else:
        roots = self.db.query(TaxonomyNode).filter(TaxonomyNode.parent_id.is_(None)).all()
    
    # Build tree
    def build_subtree(node: TaxonomyNode, current_depth: int = 0) -> Dict:
        result = {
            "id": str(node.id),
            "name": node.name,
            "slug": node.slug,
            "level": node.level,
            "path": node.path,
            "resource_count": node.resource_count,
            "descendant_resource_count": node.descendant_resource_count,
            "children": []
        }
        
        # Check depth limit
        if max_depth is not None and current_depth >= max_depth:
            return result
        
        # Add children
        for child in node.children:
            result["children"].append(build_subtree(child, current_depth + 1))
        
        return result
    
    return [build_subtree(root) for root in roots if root]
```

#### Resource Classification

```python
def classify_resource(
    self,
    resource_id: str,
    taxonomy_node_ids: List[str],
    confidence_scores: Dict[str, float],
    is_predicted: bool = True,
    predicted_by: Optional[str] = None
) -> None:
    """
    Assign taxonomy classifications to resource.
    
    Steps:
    1. Remove existing predicted classifications
    2. Add new classifications with metadata
    3. Flag low confidence (<0.7) for review
    4. Compute review priority for flagged items
    5. Update resource counts for affected nodes
    
    Performance: <20ms
    """
    # Remove existing predicted classifications
    if is_predicted:
        self.db.query(ResourceTaxonomy).filter(
            ResourceTaxonomy.resource_id == resource_id,
            ResourceTaxonomy.is_predicted == True
        ).delete()
    
    # Add new classifications
    for node_id in taxonomy_node_ids:
        confidence = confidence_scores.get(node_id, 1.0)
        needs_review = confidence < 0.7
        review_priority = (1.0 - confidence) if needs_review else None
        
        classification = ResourceTaxonomy(
            id=uuid.uuid4(),
            resource_id=resource_id,
            taxonomy_node_id=node_id,
            confidence=confidence,
            is_predicted=is_predicted,
            predicted_by=predicted_by,
            needs_review=needs_review,
            review_priority=review_priority
        )
        
        self.db.add(classification)
    
    # Update resource counts
    self._update_resource_counts(taxonomy_node_ids)
    
    self.db.commit()
```

### ML Classification Service Architecture (Phase 8.5)

The ML classification service provides transformer-based classification with semi-supervised learning and active learning capabilities.

#### Service Initialization

```python
class MLClassificationService:
    def __init__(
        self,
        db: Session,
        model_name: str = "distilbert-base-uncased",
        model_version: str = "v1.0"
    ):
        """
        Initialize ML classification service with lazy model loading.
        
        Components:
        - model: Transformer model (loaded on first prediction)
        - tokenizer: Text tokenizer (loaded with model)
        - label_map: Taxonomy ID to model index mapping
        - device: CUDA or CPU
        """
        self.db = db
        self.model_name = model_name
        self.model_version = model_version
        self.model = None
        self.tokenizer = None
        self.label_map = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
```

#### Model Training

```python
def fine_tune(
    self,
    labeled_data: List[Tuple[str, List[str]]],
    unlabeled_data: Optional[List[str]] = None,
    epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 2e-5
) -> Dict[str, float]:
    """
    Fine-tune BERT model with optional semi-supervised learning.
    
    Algorithm:
    1. Build label mapping from unique taxonomy IDs
    2. Convert multi-label to multi-hot encoding
    3. Split train/validation (80/20)
    4. Tokenize texts (max_length=512)
    5. Create PyTorch datasets
    6. Configure Hugging Face Trainer
    7. Train model with evaluation
    8. If unlabeled data provided, perform semi-supervised iteration
    9. Save model, tokenizer, and label map
    
    Performance: ~10 minutes for 500 examples on GPU
    """
    from transformers import (
        AutoTokenizer,
        AutoModelForSequenceClassification,
        Trainer,
        TrainingArguments
    )
    from sklearn.model_selection import train_test_split
    
    # Build label mapping
    all_labels = set()
    for _, labels in labeled_data:
        all_labels.update(labels)
    
    self.label_map = {label: idx for idx, label in enumerate(sorted(all_labels))}
    num_labels = len(self.label_map)
    
    # Convert to multi-hot encoding
    texts = [text for text, _ in labeled_data]
    labels = []
    for _, label_list in labeled_data:
        multi_hot = [0.0] * num_labels
        for label in label_list:
            multi_hot[self.label_map[label]] = 1.0
        labels.append(multi_hot)
    
    # Split train/validation
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )
    
    # Load tokenizer and model
    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
    self.model = AutoModelForSequenceClassification.from_pretrained(
        self.model_name,
        num_labels=num_labels,
        problem_type="multi_label_classification"
    )
    
    # Tokenize
    train_encodings = self.tokenizer(
        train_texts,
        truncation=True,
        padding=True,
        max_length=512
    )
    val_encodings = self.tokenizer(
        val_texts,
        truncation=True,
        padding=True,
        max_length=512
    )
    
    # Create datasets
    train_dataset = MultiLabelDataset(train_encodings, train_labels)
    val_dataset = MultiLabelDataset(val_encodings, val_labels)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=f"./models/classification/{self.model_version}",
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_dir="./logs"
    )
    
    # Trainer
    trainer = Trainer(
        model=self.model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=self._compute_metrics
    )
    
    # Train
    trainer.train()
    
    # Evaluate
    metrics = trainer.evaluate()
    
    # Semi-supervised learning
    if unlabeled_data:
        self._semi_supervised_iteration(
            labeled_data,
            unlabeled_data,
            confidence_threshold=0.9
        )
    
    # Save model
    self.model.save_pretrained(f"./models/classification/{self.model_version}")
    self.tokenizer.save_pretrained(f"./models/classification/{self.model_version}")
    
    # Save label map
    with open(f"./models/classification/{self.model_version}/label_map.json", "w") as f:
        json.dump(self.label_map, f)
    
    return metrics
```

#### Semi-Supervised Learning

```python
def _semi_supervised_iteration(
    self,
    labeled_data: List[Tuple[str, List[str]]],
    unlabeled_data: List[str],
    confidence_threshold: float = 0.9
) -> None:
    """
    Perform one iteration of semi-supervised learning using pseudo-labeling.
    
    Algorithm:
    1. Predict labels for unlabeled data
    2. Filter predictions with confidence >= threshold
    3. Add high-confidence predictions as pseudo-labeled examples
    4. Combine with original labeled data
    5. Re-train model for 1 epoch
    
    Expected: 10-30% of unlabeled data becomes pseudo-labeled
    """
    # Predict on unlabeled data
    predictions = self.predict_batch(unlabeled_data, top_k=3)
    
    # Filter high-confidence predictions
    pseudo_labeled = []
    for text, preds in zip(unlabeled_data, predictions):
        high_conf_labels = [
            label for label, conf in preds.items()
            if conf >= confidence_threshold
        ]
        if high_conf_labels:
            pseudo_labeled.append((text, high_conf_labels))
    
    print(f"Generated {len(pseudo_labeled)} pseudo-labeled examples from {len(unlabeled_data)} unlabeled")
    
    # Combine with labeled data
    combined_data = labeled_data + pseudo_labeled
    
    # Re-train for 1 epoch
    # (Implementation similar to fine_tune but with epochs=1)
```

#### Inference

```python
def predict(self, text: str, top_k: int = 5) -> Dict[str, float]:
    """
    Predict taxonomy categories for single text.
    
    Algorithm:
    1. Load model if not loaded (lazy loading)
    2. Tokenize text
    3. Forward pass through model
    4. Apply sigmoid activation
    5. Get top-K predictions
    6. Convert indices to taxonomy node IDs
    
    Performance: <100ms per prediction
    """
    # Lazy load model
    if self.model is None:
        self._load_model()
    
    # Tokenize
    inputs = self.tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=512,
        return_tensors="pt"
    ).to(self.device)
    
    # Predict
    with torch.no_grad():
        outputs = self.model(**inputs)
        logits = outputs.logits
        probs = torch.sigmoid(logits)[0]
    
    # Get top-K
    top_k_values, top_k_indices = torch.topk(probs, min(top_k, len(probs)))
    
    # Convert to taxonomy IDs
    reverse_label_map = {idx: label for label, idx in self.label_map.items()}
    predictions = {}
    for idx, prob in zip(top_k_indices.cpu().numpy(), top_k_values.cpu().numpy()):
        taxonomy_id = reverse_label_map[int(idx)]
        predictions[taxonomy_id] = float(prob)
    
    return predictions

def predict_batch(self, texts: List[str], top_k: int = 5) -> List[Dict[str, float]]:
    """
    Batch prediction for efficiency.
    
    Algorithm:
    1. Process in batches (32 for GPU, 8 for CPU)
    2. Tokenize batch
    3. Forward pass with batch
    4. Apply sigmoid and get top-K for each
    
    Performance: ~400ms for 32 texts on GPU
    """
    # Determine batch size
    batch_size = 32 if self.device == "cuda" else 8
    
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        
        # Tokenize batch
        inputs = self.tokenizer(
            batch,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt"
        ).to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.sigmoid(logits)
        
        # Process each text in batch
        for text_probs in probs:
            top_k_values, top_k_indices = torch.topk(text_probs, min(top_k, len(text_probs)))
            
            reverse_label_map = {idx: label for label, idx in self.label_map.items()}
            predictions = {}
            for idx, prob in zip(top_k_indices.cpu().numpy(), top_k_values.cpu().numpy()):
                taxonomy_id = reverse_label_map[int(idx)]
                predictions[taxonomy_id] = float(prob)
            
            results.append(predictions)
    
    return results
```

#### Active Learning

```python
def identify_uncertain_samples(
    self,
    resource_ids: Optional[List[str]] = None,
    limit: int = 100
) -> List[Tuple[str, float]]:
    """
    Identify resources with uncertain classifications for human review.
    
    Algorithm:
    1. Query resources (prioritize predicted classifications)
    2. Predict classifications for resources
    3. Compute uncertainty metrics:
       - Entropy: -Σ(p * log(p))
       - Margin: difference between top-2 predictions
       - Max confidence: highest probability
    4. Combined uncertainty: entropy * (1 - margin) * (1 - max_conf)
    5. Sort by uncertainty descending
    6. Return top-N most uncertain
    
    Performance: <5s for 1000 resources
    """
    # Query resources
    query = self.db.query(Resource)
    if resource_ids:
        query = query.filter(Resource.id.in_(resource_ids))
    
    resources = query.limit(limit * 2).all()  # Get more than needed
    
    # Compute uncertainty for each
    uncertainties = []
    for resource in resources:
        text = f"{resource.title} {resource.description or ''}"
        predictions = self.predict(text, top_k=10)
        
        if not predictions:
            continue
        
        # Compute metrics
        probs = list(predictions.values())
        
        # Entropy
        entropy = -sum(p * np.log(p + 1e-10) for p in probs)
        
        # Margin
        sorted_probs = sorted(probs, reverse=True)
        margin = sorted_probs[0] - sorted_probs[1] if len(sorted_probs) > 1 else 0
        
        # Max confidence
        max_conf = max(probs)
        
        # Combined uncertainty
        uncertainty = entropy * (1 - margin) * (1 - max_conf)
        
        uncertainties.append((str(resource.id), uncertainty))
    
    # Sort and return top N
    uncertainties.sort(key=lambda x: x[1], reverse=True)
    return uncertainties[:limit]
```

#### Integration Points

**Resource Ingestion Pipeline:**
```python
# In resource_service.py
async def ingest_resource(self, url: str) -> Resource:
    # ... content extraction ...
    # ... embedding generation ...
    
    # ML Classification (Phase 8.5)
    if self.use_ml:
        background_tasks.add_task(
            self._classify_resource_ml,
            resource.id
        )
    
    # ... quality scoring ...
    return resource

async def _classify_resource_ml(self, resource_id: str):
    """Background task for ML classification."""
    ml_service = MLClassificationService(self.db)
    taxonomy_service = TaxonomyService(self.db)
    
    # Get resource
    resource = self.db.query(Resource).filter(Resource.id == resource_id).first()
    
    # Predict
    text = f"{resource.title} {resource.description or ''}"
    predictions = ml_service.predict(text, top_k=5)
    
    # Filter by confidence threshold
    filtered = {
        node_id: conf for node_id, conf in predictions.items()
        if conf >= 0.3
    }
    
    # Store classifications
    taxonomy_service.classify_resource(
        resource_id=resource_id,
        taxonomy_node_ids=list(filtered.keys()),
        confidence_scores=filtered,
        is_predicted=True,
        predicted_by=ml_service.model_version
    )
```

#### Troubleshooting

**Common Issues:**

1. **CUDA Out of Memory**
   - Reduce batch size: `batch_size=8` or `batch_size=4`
   - Use DistilBERT instead of BERT
   - Clear GPU cache: `torch.cuda.empty_cache()`

2. **Slow Training**
   - Enable GPU acceleration
   - Increase batch size on GPU: `batch_size=32`
   - Reduce epochs: `epochs=2`

3. **Low Accuracy**
   - Increase training data (aim for 500+ examples)
   - Balance dataset across categories
   - Use semi-supervised learning
   - Collect feedback through active learning

4. **Model Not Found**
   - Train model first using `/taxonomy/train`
   - Verify model saved to `models/classification/{version}/`
   - Check model version in service initialization

### Phase 8: Three-Way Hybrid Search Architecture

Phase 8 implements a state-of-the-art three-way hybrid search system that combines FTS5, dense vectors, and sparse vectors with Reciprocal Rank Fusion (RRF) and ColBERT-style reranking.

#### Sparse Vector Embeddings

**Model Architecture:**
```python
class SparseEmbeddingService:
    """
    Generate and manage sparse vector embeddings using BGE-M3 model.
    
    Sparse vectors are learned keyword representations with 50-200 non-zero
    dimensions that capture term importance beyond traditional TF-IDF.
    """
    
    def __init__(self, db: Session, model_name: str = "BAAI/bge-m3"):
        self.db = db
        self.model_name = model_name
        self._model = None  # Lazy loading
    
    def generate_sparse_embedding(self, text: str) -> Dict[int, float]:
        """
        Generate sparse vector for single text.
        
        Algorithm:
        1. Tokenize input text (max 512 tokens)
        2. Forward pass through BGE-M3 model
        3. Extract sparse representation layer
        4. Apply ReLU + log transformation (SPLADE-style)
        5. Select top-200 non-zero dimensions
        6. Normalize weights to [0, 1]
        7. Return as dict {token_id: weight}
        
        Performance: <1 second per resource
        """
        if self._model is None:
            self._load_model()
        
        # Tokenize and encode
        inputs = self._tokenizer(
            text,
            max_length=512,
            truncation=True,
            return_tensors="pt"
        )
        
        # Generate sparse representation
        with torch.no_grad():
            outputs = self._model(**inputs)
            sparse_vec = outputs.sparse_embedding
        
        # Apply transformations
        sparse_vec = torch.relu(sparse_vec)
        sparse_vec = torch.log(1 + sparse_vec)
        
        # Select top-K
        top_k = 200
        values, indices = torch.topk(sparse_vec, k=top_k)
        
        # Normalize to [0, 1]
        if values.max() > 0:
            values = values / values.max()
        
        # Convert to dict
        sparse_dict = {
            int(idx): float(val)
            for idx, val in zip(indices.tolist(), values.tolist())
            if val > 0
        }
        
        return sparse_dict
```

**Storage Format:**
```python
# Resource model extension
class Resource(Base):
    # ... existing fields ...
    
    # Sparse embedding fields (Phase 8)
    sparse_embedding: Mapped[str | None] = mapped_column(Text, nullable=True)
    sparse_embedding_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sparse_embedding_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

# Example sparse embedding JSON
{
  "2453": 0.87,
  "8921": 0.65,
  "1234": 0.43,
  ...
}
```

**Sparse Vector Search:**
```python
def search_by_sparse_vector(
    self,
    query_sparse: Dict[int, float],
    limit: int = 100,
    min_score: float = 0.0
) -> List[Tuple[str, float]]:
    """
    Search resources using sparse similarity.
    
    Algorithm:
    1. Generate query sparse vector
    2. For each resource with sparse embedding:
       a. Parse JSON to dict
       b. Compute sparse dot product (only overlapping dimensions)
       c. Accumulate score
    3. Sort by score descending
    4. Return top-K results
    
    Performance: Linear scan acceptable for <100K resources
    """
    resources = (
        self.db.query(Resource)
        .filter(Resource.sparse_embedding.isnot(None))
        .all()
    )
    
    results = []
    for resource in resources:
        resource_sparse = json.loads(resource.sparse_embedding)
        
        # Sparse dot product
        score = sum(
            query_sparse.get(token_id, 0) * weight
            for token_id, weight in resource_sparse.items()
        )
        
        if score >= min_score:
            results.append((resource.id, score))
    
    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:limit]
```

#### Reciprocal Rank Fusion (RRF)

**RRF Algorithm Implementation:**
```python
class ReciprocalRankFusionService:
    """
    Merge results from multiple retrieval methods using RRF.
    
    RRF is score-agnostic and works with heterogeneous scoring functions
    (e.g., BM25 scores vs cosine similarity).
    """
    
    def __init__(self, k: int = 60):
        self.k = k  # Constant that reduces impact of high ranks
    
    def fuse_results(
        self,
        result_lists: List[List[Tuple[str, float]]],
        weights: List[float] = None
    ) -> List[Tuple[str, float]]:
        """
        Merge multiple ranked lists using RRF.
        
        Formula: RRF_score(d) = Σ [weight_i / (k + rank_i(d))]
        
        where:
        - rank_i(d) = rank of document d in result list i (0-indexed)
        - weight_i = importance weight for result list i
        - k = constant (typically 60)
        
        Performance: <5ms for typical result sets
        """
        if weights is None:
            weights = [1.0] * len(result_lists)
        
        # Normalize weights to sum to 1.0
        weight_sum = sum(weights)
        weights = [w / weight_sum for w in weights]
        
        # Compute RRF scores
        rrf_scores = {}
        
        for i, result_list in enumerate(result_lists):
            for rank, (doc_id, _) in enumerate(result_list):
                if doc_id not in rrf_scores:
                    rrf_scores[doc_id] = 0.0
                
                rrf_scores[doc_id] += weights[i] / (self.k + rank)
        
        # Sort by RRF score descending
        sorted_results = sorted(
            rrf_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_results
```

**Query-Adaptive Weighting:**
```python
def adaptive_weights(
    self,
    query: str,
    result_lists: List[List[Tuple[str, float]]]
) -> List[float]:
    """
    Compute query-adaptive weights based on query characteristics.
    
    Heuristics:
    - Short queries (1-3 words): Boost FTS5 by 50%
    - Long queries (>10 words): Boost dense vectors by 50%
    - Technical queries (code, math): Boost sparse vectors by 50%
    - Question queries (who/what/when/where/why/how): Boost dense by 30%
    
    Returns: [fts5_weight, dense_weight, sparse_weight]
    """
    # Start with equal weights
    weights = [1.0, 1.0, 1.0]  # FTS5, dense, sparse
    
    # Analyze query
    words = query.split()
    word_count = len(words)
    
    # Short query heuristic
    if word_count <= 3:
        weights[0] *= 1.5  # Boost FTS5
    
    # Long query heuristic
    if word_count > 10:
        weights[1] *= 1.5  # Boost dense
    
    # Technical query heuristic
    technical_indicators = ['def ', 'class ', '()', '{}', '[]', '=', '+', '-', '*', '/']
    if any(indicator in query for indicator in technical_indicators):
        weights[2] *= 1.5  # Boost sparse
    
    # Question query heuristic
    question_words = ['who', 'what', 'when', 'where', 'why', 'how']
    if any(query.lower().startswith(qw) for qw in question_words):
        weights[1] *= 1.3  # Boost dense
    
    # Normalize to sum to 1.0
    weight_sum = sum(weights)
    weights = [w / weight_sum for w in weights]
    
    return weights
```

#### ColBERT Reranking

**Reranking Service:**
```python
class RerankingService:
    """
    Apply ColBERT-style cross-encoder reranking for maximum precision.
    
    Cross-encoders model query-document interaction directly for
    better relevance scoring than retrieval methods.
    """
    
    def __init__(
        self,
        db: Session,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        self.db = db
        self.model_name = model_name
        self._model = None  # Lazy loading
    
    def rerank(
        self,
        query: str,
        candidates: List[str],  # Resource IDs
        top_k: int = 20
    ) -> List[Tuple[str, float]]:
        """
        Rerank candidates using cross-encoder.
        
        Algorithm:
        1. Fetch resource content for candidate IDs
        2. Build (query, document) pairs
           - Use title + first 500 chars of content
        3. Batch predict relevance scores using cross-encoder
        4. Sort by relevance score descending
        5. Return top-K results
        
        Performance: >100 documents/second
        """
        if self._model is None:
            self._load_model()
        
        # Fetch resources
        resources = (
            self.db.query(Resource)
            .filter(Resource.id.in_(candidates))
            .all()
        )
        
        # Build query-document pairs
        pairs = []
        resource_map = {}
        for resource in resources:
            doc_text = f"{resource.title}. {resource.content[:500]}"
            pairs.append([query, doc_text])
            resource_map[len(pairs) - 1] = resource.id
        
        # Batch predict relevance scores
        scores = self._model.predict(pairs)
        
        # Sort by relevance score
        results = [
            (resource_map[i], float(score))
            for i, score in enumerate(scores)
        ]
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
```

#### Three-Way Hybrid Search Integration

**Complete Search Pipeline:**
```python
class AdvancedSearchService:
    """
    Orchestrate three-way hybrid search with RRF and reranking.
    """
    
    @staticmethod
    def search_three_way_hybrid(
        db: Session,
        query: SearchQuery,
        enable_reranking: bool = True,
        adaptive_weighting: bool = True
    ) -> Tuple[List[Resource], int, Facets, Dict[str, str]]:
        """
        Three-way hybrid search with RRF and reranking.
        
        Algorithm:
        1. Query Analysis
           - Parse query text
           - Detect query characteristics (length, type, technical)
        
        2. Parallel Retrieval (target: <150ms total)
           - FTS5 search → top 100 results
           - Dense vector search → top 100 results
           - Sparse vector search → top 100 results
        
        3. Adaptive Weighting (if enabled)
           - Compute weights based on query characteristics
           - Default: [1.0, 1.0, 1.0] (equal weights)
        
        4. RRF Fusion
           - Merge three result lists using RRF
           - Apply adaptive weights
           - Sort by RRF score
        
        5. Reranking (if enabled)
           - Extract top 100 candidates
           - Apply ColBERT cross-encoder
           - Sort by relevance score
           - Return top-K
        
        6. Fetch Resources
           - Retrieve Resource objects preserving order
           - Apply structured filters
           - Compute facets
        
        7. Return Results
           - Resources, total count, facets, snippets
        
        Performance: <200ms at 95th percentile
        """
        start_time = time.time()
        
        # 1. Query analysis
        query_text = query.text
        
        # 2. Parallel retrieval
        fts5_results = AdvancedSearchService._search_fts5(db, query_text, limit=100)
        dense_results = AdvancedSearchService._search_dense(db, query_text, limit=100)
        sparse_results = AdvancedSearchService._search_sparse(db, query_text, limit=100)
        
        # 3. Adaptive weighting
        if adaptive_weighting:
            rrf_service = ReciprocalRankFusionService()
            weights = rrf_service.adaptive_weights(
                query_text,
                [fts5_results, dense_results, sparse_results]
            )
        else:
            weights = [1.0, 1.0, 1.0]
        
        # 4. RRF fusion
        rrf_service = ReciprocalRankFusionService(k=60)
        fused_results = rrf_service.fuse_results(
            [fts5_results, dense_results, sparse_results],
            weights=weights
        )
        
        # 5. Reranking (optional)
        if enable_reranking:
            reranking_service = RerankingService(db)
            candidate_ids = [doc_id for doc_id, _ in fused_results[:100]]
            reranked_results = reranking_service.rerank(
                query_text,
                candidate_ids,
                top_k=query.limit
            )
            final_results = reranked_results
        else:
            final_results = fused_results[:query.limit]
        
        # 6. Fetch resources
        resource_ids = [doc_id for doc_id, _ in final_results]
        resources = AdvancedSearchService._fetch_resources_ordered(db, resource_ids)
        
        # 7. Compute metadata
        latency_ms = (time.time() - start_time) * 1000
        method_contributions = {
            "fts5": len([r for r in fts5_results if r[0] in resource_ids]),
            "dense": len([r for r in dense_results if r[0] in resource_ids]),
            "sparse": len([r for r in sparse_results if r[0] in resource_ids])
        }
        
        # Log performance
        logger.info(
            f"Three-way search completed in {latency_ms:.1f}ms "
            f"(FTS5={method_contributions['fts5']}, "
            f"Dense={method_contributions['dense']}, "
            f"Sparse={method_contributions['sparse']}, "
            f"Weights={weights})"
        )
        
        if latency_ms > 500:
            logger.warning(f"Slow query detected: {query_text} ({latency_ms:.1f}ms)")
        
        return resources, len(resources), {}, {}
```

#### Search Metrics Service

**Information Retrieval Metrics:**
```python
class SearchMetricsService:
    """
    Compute information retrieval metrics for evaluation.
    """
    
    def compute_ndcg(
        self,
        ranked_results: List[str],
        relevance_judgments: Dict[str, int],
        k: int = 20
    ) -> float:
        """
        Compute nDCG@k (Normalized Discounted Cumulative Gain).
        
        Formula:
        DCG@k = Σ [(2^rel_i - 1) / log2(i + 2)]
        nDCG@k = DCG@k / IDCG@k
        
        where:
        - rel_i = relevance score of document at position i (0-3 scale)
        - IDCG@k = ideal DCG (perfect ranking)
        
        Range: [0, 1], higher is better
        Target: >0.7 for excellent search quality
        """
        import math
        
        # Compute DCG
        dcg = 0.0
        for i, doc_id in enumerate(ranked_results[:k]):
            rel = relevance_judgments.get(doc_id, 0)
            dcg += (2 ** rel - 1) / math.log2(i + 2)
        
        # Compute IDCG (ideal ranking)
        ideal_rels = sorted(relevance_judgments.values(), reverse=True)[:k]
        idcg = sum(
            (2 ** rel - 1) / math.log2(i + 2)
            for i, rel in enumerate(ideal_rels)
        )
        
        # Normalize
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    def compute_recall_at_k(
        self,
        ranked_results: List[str],
        relevant_docs: List[str],
        k: int = 20
    ) -> float:
        """
        Compute Recall@k.
        
        Formula: Recall@k = (# relevant docs in top-k) / (total # relevant docs)
        
        Range: [0, 1], higher is better
        """
        top_k = set(ranked_results[:k])
        relevant_set = set(relevant_docs)
        
        retrieved_relevant = len(top_k & relevant_set)
        total_relevant = len(relevant_set)
        
        if total_relevant == 0:
            return 0.0
        
        return retrieved_relevant / total_relevant
    
    def compute_precision_at_k(
        self,
        ranked_results: List[str],
        relevant_docs: List[str],
        k: int = 20
    ) -> float:
        """
        Compute Precision@k.
        
        Formula: Precision@k = (# relevant docs in top-k) / k
        
        Range: [0, 1], higher is better
        """
        top_k = set(ranked_results[:k])
        relevant_set = set(relevant_docs)
        
        retrieved_relevant = len(top_k & relevant_set)
        
        return retrieved_relevant / k
    
    def compute_mean_reciprocal_rank(
        self,
        ranked_results: List[str],
        relevant_docs: List[str]
    ) -> float:
        """
        Compute MRR (Mean Reciprocal Rank).
        
        Formula: MRR = 1 / (rank of first relevant document)
        
        Range: [0, 1], higher is better
        """
        relevant_set = set(relevant_docs)
        
        for i, doc_id in enumerate(ranked_results):
            if doc_id in relevant_set:
                return 1.0 / (i + 1)
        
        return 0.0
```

#### Performance Optimization Strategies

**Parallel Retrieval:**
```python
import asyncio

async def parallel_retrieval(query: str):
    """Execute three retrieval methods in parallel."""
    tasks = [
        asyncio.to_thread(search_fts5, query, limit=100),
        asyncio.to_thread(search_dense, query, limit=100),
        asyncio.to_thread(search_sparse, query, limit=100)
    ]
    results = await asyncio.gather(*tasks)
    return results

# Expected speedup: 2-3x (from ~150ms sequential to ~50-75ms parallel)
```

**GPU Acceleration:**
```python
# Sparse embedding generation
if torch.cuda.is_available():
    model = model.cuda()
    inputs = {k: v.cuda() for k, v in inputs.items()}

# Expected speedup: 5-10x for batch processing

# Reranking
model = CrossEncoder(model_name, device='cuda' if torch.cuda.is_available() else 'cpu')

# Expected speedup: 5-10x for reranking 100 documents
```

**Caching Strategy:**
```python
from functools import lru_cache
from cachetools import TTLCache

# Query result caching
@lru_cache(maxsize=1000)
def cached_search(query_hash: str, filters_hash: str):
    # Cache search results for 5 minutes
    pass

# Reranking result caching
reranking_cache = TTLCache(maxsize=500, ttl=3600)

cache_key = f"{query}|{sorted(candidates)}"
if cache_key in reranking_cache:
    return reranking_cache[cache_key]
```

**Query Optimization:**
```python
# Use eager loading to prevent N+1 queries
annotations = (
    db.query(Annotation)
    .options(joinedload(Annotation.resource))
    .filter(Annotation.user_id == user_id)
    .all()
)

# Batch operations for export
annotations = (
    db.query(Annotation)
    .filter(Annotation.user_id == user_id)
    .order_by(Annotation.created_at.desc())
    .limit(1000)
    .all()
)
```

**Embedding Generation Strategy:**
```python
# Synchronous path (fast)
annotation = create_annotation(...)  # <50ms
return annotation

# Asynchronous path (background)
background_tasks.add_task(
    generate_annotation_embedding,
    annotation.id,
    note
)
```

#### Integration with Other Services

**Resource Deletion:**
```python
# In resource_service.py
def delete_resource(db: Session, resource_id: str) -> None:
    """Delete resource and cascade to annotations."""
    # Annotations automatically deleted via CASCADE constraint
    db.delete(resource)
    db.commit()
```

**Search Integration:**
```python
# In search_service.py
def search_with_annotations(
    self,
    query: str,
    user_id: str,
    include_annotations: bool = True
) -> Dict:
    """Include annotation matches in search results."""
    # Standard resource search
    resources = self.search(query)
    
    if include_annotations:
        # Search user's annotations
        annotation_service = AnnotationService(self.db)
        annotations = annotation_service.search_annotations_fulltext(
            user_id, query
        )
        
        # Build resource-annotation mapping
        resource_annotation_map = {}
        for ann in annotations:
            if ann.resource_id not in resource_annotation_map:
                resource_annotation_map[ann.resource_id] = []
            resource_annotation_map[ann.resource_id].append(ann.id)
        
        return {
            "resources": resources,
            "annotations": annotations,
            "resource_annotation_matches": resource_annotation_map
        }
    
    return {"resources": resources, "annotations": []}
```

**Recommendation Integration:**
```python
# In recommendation_service.py
def recommend_based_on_annotations(
    self,
    user_id: str,
    limit: int = 10
) -> List[Resource]:
    """Generate recommendations from annotation patterns."""
    annotation_service = AnnotationService(self.db)
    
    # Get recent annotations
    annotations = annotation_service.get_annotations_for_user(
        user_id=user_id,
        limit=100,
        sort_by="recent"
    )
    
    # Extract patterns
    all_notes = " ".join([ann.note for ann in annotations if ann.note])
    all_tags = []
    for ann in annotations:
        if ann.tags:
            all_tags.extend(json.loads(ann.tags))
    
    # Generate recommendations
    # ... (see recommendation_service.py for full implementation)
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

## ML Benchmarking

### Overview

Neo Alexandria includes a comprehensive ML benchmarking system that evaluates all machine learning algorithms deployed in the platform. The system provides automated testing, performance measurement, and detailed reporting to ensure ML components meet quality standards and detect performance regressions.

**Key Features:**
- Standardized test datasets for reproducible evaluation
- Industry-standard metrics (accuracy, F1, NDCG, BERTScore, latency)
- Automated regression detection
- Actionable recommendations for improvements
- CI/CD integration for pre-deployment validation

**Benchmark Suites:**
1. **Classification**: Taxonomy classification accuracy and confidence calibration
2. **Collaborative Filtering**: Recommendation quality using NDCG@10 and Hit Rate@10
3. **Search Quality**: Three-way hybrid search evaluation with NDCG@20
4. **Summarization**: Summary quality using BERTScore and ROUGE scores
5. **Performance**: Inference latency measurements (p50, p95, p99)

### Running Benchmarks Locally

#### Quick Start

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run all benchmarks
python tests/ml_benchmarks/benchmark_runner.py

# Expected runtime: 25-30 minutes
# Output: docs/ML_BENCHMARKS.md
```

#### Run Specific Suite

```bash
# Classification benchmarks only
python tests/ml_benchmarks/benchmark_runner.py --suite classification

# Collaborative filtering benchmarks only
python tests/ml_benchmarks/benchmark_runner.py --suite collaborative_filtering

# Search quality benchmarks only
python tests/ml_benchmarks/benchmark_runner.py --suite search

# Summarization benchmarks only
python tests/ml_benchmarks/benchmark_runner.py --suite summarization

# Performance benchmarks only
python tests/ml_benchmarks/benchmark_runner.py --suite performance
```

#### Run with pytest

```bash
# Run all benchmarks with verbose output
pytest tests/ml_benchmarks/ -v --tb=short

# Run specific test file
pytest tests/ml_benchmarks/test_classification_metrics.py -v

# Run specific test
pytest tests/ml_benchmarks/test_classification_metrics.py::TestClassificationMetrics::test_overall_accuracy -v

# Run with detailed output (see print statements)
pytest tests/ml_benchmarks/ -v -s
```

### Creating Test Datasets

Test datasets are stored as JSON files in `tests/ml_benchmarks/datasets/`. Each dataset includes metadata for reproducibility.

#### Dataset Structure

```json
{
  "metadata": {
    "dataset_name": "classification_benchmark_v1",
    "created_at": "2025-11-15",
    "num_samples": 200,
    "description": "Balanced test set for taxonomy classification"
  },
  "samples": [
    {
      "text": "Sample text content...",
      "true_labels": ["label1", "label2"],
      "taxonomy_node_ids": ["node-id-1", "node-id-2"],
      "difficulty": "medium"
    }
  ],
  "class_distribution": {
    "label1": 25,
    "label2": 20
  }
}
```

#### Creating a New Classification Dataset

```python
import json
from datetime import datetime

# Prepare samples
samples = []
for resource in selected_resources:
    samples.append({
        "text": resource.content,
        "true_labels": [node.name for node in resource.taxonomy_nodes],
        "taxonomy_node_ids": [str(node.id) for node in resource.taxonomy_nodes],
        "difficulty": "medium"  # or "easy", "hard"
    })

# Compute class distribution
class_distribution = {}
for sample in samples:
    for label in sample["true_labels"]:
        class_distribution[label] = class_distribution.get(label, 0) + 1

# Create dataset
dataset = {
    "metadata": {
        "dataset_name": "classification_benchmark_v2",
        "created_at": datetime.now().isoformat(),
        "num_samples": len(samples),
        "num_classes": len(class_distribution),
        "description": "Updated classification test set with new taxonomy"
    },
    "samples": samples,
    "class_distribution": class_distribution
}

# Save to file
with open("tests/ml_benchmarks/datasets/classification_test.json", "w") as f:
    json.dump(dataset, f, indent=2)
```

#### Creating a New Recommendation Dataset

```python
import json
from datetime import datetime

# Prepare interactions
interactions = []
for interaction in user_interactions:
    interactions.append({
        "user_id": str(interaction.user_id),
        "resource_id": str(interaction.resource_id),
        "interaction_type": interaction.type,  # "view", "annotation", "collection_add"
        "strength": interaction.strength,  # 0.0-1.0
        "timestamp": interaction.created_at.isoformat()
    })

# Split into train/test (80/20)
from sklearn.model_selection import train_test_split
train_interactions, test_interactions = train_test_split(
    interactions, test_size=0.2, random_state=42
)

# Create held-out test set
held_out_test = []
for interaction in test_interactions:
    held_out_test.append({
        "user_id": interaction["user_id"],
        "resource_id": interaction["resource_id"],
        "is_relevant": True  # All test interactions are relevant
    })

# Create dataset
dataset = {
    "metadata": {
        "dataset_name": "recommendation_benchmark_v2",
        "created_at": datetime.now().isoformat(),
        "num_users": len(set(i["user_id"] for i in interactions)),
        "num_items": len(set(i["resource_id"] for i in interactions)),
        "num_interactions": len(interactions)
    },
    "interactions": train_interactions,
    "held_out_test": held_out_test
}

# Save to file
with open("tests/ml_benchmarks/datasets/recommendation_test.json", "w") as f:
    json.dump(dataset, f, indent=2)
```

### Adding New Benchmarks

#### Step 1: Create Test File

Create a new test file in `tests/ml_benchmarks/`:

```python
# tests/ml_benchmarks/test_new_algorithm_metrics.py
import pytest
import json
from pathlib import Path

class TestNewAlgorithmMetrics:
    """Benchmark tests for new algorithm."""
    
    @pytest.fixture
    def test_data(self):
        """Load test dataset."""
        dataset_path = Path(__file__).parent / "datasets" / "new_algorithm_test.json"
        with open(dataset_path) as f:
            return json.load(f)
    
    @pytest.fixture
    def trained_model(self, db_session):
        """Load pre-trained model."""
        from app.services.new_algorithm_service import NewAlgorithmService
        
        service = NewAlgorithmService(db_session)
        model_path = Path("models/new_algorithm/benchmark_v1")
        
        if not model_path.exists():
            pytest.skip("Benchmark model not available")
        
        service.load_model(model_path)
        return service
    
    def test_primary_metric(self, trained_model, test_data):
        """Test primary evaluation metric."""
        # Run predictions
        predictions = []
        ground_truth = []
        
        for sample in test_data["samples"]:
            pred = trained_model.predict(sample["input"])
            predictions.append(pred)
            ground_truth.append(sample["expected_output"])
        
        # Compute metric
        from sklearn.metrics import accuracy_score
        score = accuracy_score(ground_truth, predictions)
        
        # Assert baseline threshold
        baseline = 0.70
        assert score > baseline, f"Score {score:.3f} below baseline {baseline}"
        
        # Log result
        print(f"Primary Metric: {score:.3f} (baseline: {baseline})")
```

#### Step 2: Add to Benchmark Runner

Update `tests/ml_benchmarks/benchmark_runner.py`:

```python
def run_all_benchmarks(self) -> Dict:
    """Run all benchmark suites."""
    self.results = {
        "classification": self._run_classification(),
        "collaborative_filtering": self._run_cf(),
        "search": self._run_search(),
        "summarization": self._run_summarization(),
        "performance": self._run_performance(),
        "new_algorithm": self._run_new_algorithm()  # Add new suite
    }
    
    self._generate_report()
    return self.results

def _run_new_algorithm(self) -> Dict:
    """Run new algorithm benchmarks."""
    result = pytest.main([
        "tests/ml_benchmarks/test_new_algorithm_metrics.py",
        "-v", "--tb=short", "--json-report",
        "--json-report-file=new_algorithm_results.json"
    ])
    return self._parse_pytest_results("new_algorithm_results.json")
```

#### Step 3: Update Report Generator

Update `tests/ml_benchmarks/report_generator.py`:

```python
def generate(self) -> str:
    """Generate complete benchmark report."""
    sections = [
        self._generate_header(),
        self._generate_executive_summary(),
        self._generate_methodology(),
        self._generate_classification_section(),
        self._generate_cf_section(),
        self._generate_search_section(),
        self._generate_summarization_section(),
        self._generate_performance_section(),
        self._generate_new_algorithm_section(),  # Add new section
        self._generate_regressions(),
        self._generate_recommendations(),
        self._generate_reproduction_steps()
    ]
    
    return "\n\n".join(sections)

def _generate_new_algorithm_section(self) -> str:
    """Generate new algorithm section."""
    if "new_algorithm" not in self.results:
        return ""
    
    results = self.results["new_algorithm"]
    
    section = "### New Algorithm\n\n"
    section += f"**Status**: {'✅ PASS' if results['passed'] else '❌ FAIL'}\n"
    section += f"**Tests**: {results['passed_tests']}/{results['total_tests']} passed\n"
    section += f"**Execution Time**: {results['execution_time']:.2f}s\n\n"
    
    # Add metrics table
    section += "#### Metrics\n\n"
    section += "| Metric | Score | Baseline | Target | Status |\n"
    section += "|--------|-------|----------|--------|--------|\n"
    
    for metric in results["metrics"]:
        status = "✅" if metric["score"] > metric["target"] else "⚠️" if metric["score"] > metric["baseline"] else "❌"
        section += f"| {metric['name']} | {metric['score']:.3f} | {metric['baseline']} | {metric['target']} | {status} |\n"
    
    return section
```

### Interpreting Results

#### Executive Summary

The executive summary provides a high-level overview of all algorithms:

```markdown
| Algorithm | Key Metric | Score | Baseline | Target | Status |
|-----------|------------|-------|----------|--------|--------|
| Classification | F1 Score | 0.87 | 0.70 | 0.85 | ✅ |
| NCF | NDCG@10 | 0.52 | 0.30 | 0.50 | ✅ |
```

**Status Indicators:**
- ✅ **Above target**: Excellent performance, exceeds aspirational goal
- ⚠️ **Between baseline and target**: Acceptable but room for improvement
- ❌ **Below baseline**: Unacceptable, requires immediate attention

#### Per-Algorithm Sections

Each algorithm has a detailed section with:
- Overall metrics and status
- Per-class/per-query breakdowns
- Latency percentiles (p50, p95, p99)
- Specific recommendations

**Example:**
```markdown
### Classification (Phase 8.5)

**Status**: ✅ PASS
**Tests**: 5/5 passed
**Execution Time**: 45.2s

#### Metrics
- **Accuracy**: 0.87 (✅ Above target 0.85)
- **F1 Score**: 0.86 (✅ Above target 0.85)
- **Inference Time**: 82ms p95 (✅ Below target 100ms)

#### Per-Class Performance
| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|-----|---------|
| machine-learning | 0.92 | 0.88 | 0.90 | 25 |
| quantum-computing | 0.65 | 0.58 | 0.61 | 18 |

#### Recommendations
1. ⚠️ Weak performance on "Quantum Computing" class (F1=0.61)
   - **Action**: Add 50 more training examples
   - **Priority**: Medium
```

#### Performance Regressions

The report compares current results to previous runs:

```markdown
## Performance Regressions

### Classification
- **F1 Score**: 0.87 → 0.85 (-2.3%) ⚠️
- **Inference Latency**: 82ms → 95ms (+15.9%) ⚠️

### Recommendations
1. Investigate F1 score decrease
2. Profile inference pipeline for latency increase
```

**Regression Thresholds:**
- Metric decrease >5%: Flagged as regression
- Latency increase >20%: Flagged as regression

### Troubleshooting Common Issues

#### Issue: Model Not Found

**Symptom:**
```
pytest.skip: Benchmark model not available. Run training first.
```

**Solutions:**
1. Download pre-trained checkpoints:
   ```bash
   python scripts/download_benchmark_models.py
   ```

2. Train models locally:
   ```bash
   python scripts/train_classification_model.py --data data/taxonomy_training.json
   python scripts/train_ncf_model.py --data data/interactions_training.json
   ```

3. Verify model paths:
   ```bash
   ls -lh models/classification/benchmark_v1/
   ls -lh models/ncf_benchmark_v1.pt
   ```

#### Issue: Out of Memory (OOM)

**Symptom:**
```
RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB
```

**Solutions:**
1. Reduce batch size in `tests/ml_benchmarks/config.py`:
   ```python
   BATCH_SIZE = 8  # Reduce from 32
   ```

2. Run suites individually:
   ```bash
   python tests/ml_benchmarks/benchmark_runner.py --suite classification
   ```

3. Use CPU instead of GPU:
   ```bash
   export CUDA_VISIBLE_DEVICES=""
   python tests/ml_benchmarks/benchmark_runner.py
   ```

4. Close other applications to free RAM

#### Issue: Tests Timeout

**Symptom:**
```
tests/ml_benchmarks/test_search_quality_metrics.py::test_hybrid_search_ndcg FAILED
Reason: Test exceeded 300 second timeout
```

**Solutions:**
1. Increase timeout in `pytest.ini`:
   ```ini
   [pytest]
   timeout = 3600  # 60 minutes
   ```

2. Run on faster hardware (GPU recommended)

3. Reduce test dataset size (not recommended for reproducibility)

#### Issue: Inconsistent Results

**Symptom:**
Benchmark scores vary significantly between runs

**Solutions:**
1. Verify random seeds are set in `tests/ml_benchmarks/conftest.py`:
   ```python
   import random
   import numpy as np
   import torch
   
   random.seed(42)
   np.random.seed(42)
   torch.manual_seed(42)
   ```

2. Use CPU for deterministic results:
   ```bash
   export CUDA_VISIBLE_DEVICES=""
   ```

3. Run multiple times and average results

#### Issue: Import Errors

**Symptom:**
```
ModuleNotFoundError: No module named 'transformers'
```

**Solutions:**
1. Verify virtual environment is activated:
   ```bash
   which python  # Should show .venv/bin/python
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Check Python version:
   ```bash
   python --version  # Must be 3.11+
   ```

### Best Practices

#### When to Run Benchmarks

1. **Before Merging PRs**: Ensure no regressions introduced
2. **After Model Updates**: Verify improvements or detect degradation
3. **Weekly Automated Runs**: Track performance over time
4. **Before Releases**: Comprehensive validation

#### Maintaining Test Datasets

1. **Version Control**: Commit datasets to Git for reproducibility
2. **Regular Updates**: Refresh datasets quarterly with new examples
3. **Balance Classes**: Ensure balanced distribution for classification
4. **Document Changes**: Update metadata when modifying datasets
5. **Validate Quality**: Review samples for accuracy and relevance

#### Interpreting Trends

1. **Track Over Time**: Monitor metrics across multiple runs
2. **Identify Patterns**: Look for gradual degradation or improvement
3. **Correlate Changes**: Link performance changes to code/data updates
4. **Set Alerts**: Configure CI to fail on significant regressions
5. **Document Findings**: Record insights in benchmark reports

#### Optimizing Benchmark Runtime

1. **Use GPU**: Reduces runtime by 50%
2. **Run Suites in Parallel**: Use `pytest-xdist` for parallel execution
3. **Cache Models**: Load models once per session
4. **Reduce Test Runs**: Lower `PERFORMANCE_TEST_RUNS` for faster feedback
5. **Profile Bottlenecks**: Identify slow tests and optimize

### CI/CD Integration

Benchmarks are integrated into the CI/CD pipeline for automated validation.

#### GitHub Actions Workflow

```yaml
# .github/workflows/ml_benchmarks.yml
name: ML Benchmarks

on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM UTC
  workflow_dispatch:  # Manual trigger
  pull_request:
    branches: [main]

jobs:
  benchmarks:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Download model checkpoints
        run: |
          python backend/scripts/download_benchmark_models.py
      
      - name: Run benchmarks
        run: |
          cd backend
          python tests/ml_benchmarks/benchmark_runner.py
      
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-report
          path: backend/docs/ML_BENCHMARKS.md
      
      - name: Commit report
        if: github.event_name == 'schedule'
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add backend/docs/ML_BENCHMARKS.md
          git commit -m "Update ML benchmark results [skip ci]"
          git push
      
      - name: Check for regressions
        if: github.event_name == 'pull_request'
        run: |
          cd backend
          python tests/ml_benchmarks/check_regressions.py --fail-on-regression
```

#### Pre-commit Hook

Add a pre-commit hook to run benchmarks locally:

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Running ML benchmarks..."
cd backend
python tests/ml_benchmarks/benchmark_runner.py --suite classification

if [ $? -ne 0 ]; then
    echo "Benchmarks failed. Commit aborted."
    exit 1
fi

echo "Benchmarks passed."
```

### Additional Resources

- **Full Benchmark Report**: `docs/ML_BENCHMARKS.md`
- **Benchmark History**: `docs/ML_BENCHMARKS_HISTORY.json`
- **Test Datasets**: `tests/ml_benchmarks/datasets/`
- **Benchmark Runner**: `tests/ml_benchmarks/benchmark_runner.py`
- **Report Generator**: `tests/ml_benchmarks/report_generator.py`

## ML Model Training

### Overview

Neo Alexandria uses two primary machine learning models that require training before they can be used in production or for benchmark testing:

1. **Classification Model** - Multi-label text classification for taxonomy assignment
2. **NCF Model** - Neural Collaborative Filtering for personalized recommendations

Both models can be trained using provided scripts with test datasets or custom data. Training is required before running ML benchmarks.

### Model Checkpoints

Trained models are saved to the following locations:

```
backend/models/
├── classification/
│   └── benchmark_v1/           # Classification model checkpoint
│       ├── pytorch_model.bin   # Model weights
│       ├── config.json         # Model configuration
│       ├── tokenizer_config.json
│       ├── vocab.txt
│       └── label_map.json      # Taxonomy ID mappings
└── ncf_benchmark_v1.pt         # NCF model checkpoint
```

**Checkpoint Contents:**

- **Classification**: Full Hugging Face model directory with tokenizer and label mappings
- **NCF**: PyTorch checkpoint with model state, user/item ID mappings, and hyperparameters

### Training the Classification Model

The classification model uses a fine-tuned DistilBERT for multi-label taxonomy classification.

#### Quick Start

```bash
# Navigate to backend directory
cd backend

# Train with test dataset (default)
python scripts/train_classification.py

# Train with custom dataset
python scripts/train_classification.py --data-path path/to/data.json --epochs 5
```

#### Command-Line Options

```bash
python scripts/train_classification.py \
  --data-path tests/ml_benchmarks/datasets/classification_test.json \
  --epochs 3 \
  --batch-size 16 \
  --learning-rate 2e-5 \
  --output-dir models/classification/benchmark_v1
```

**Parameters:**
- `--data-path`: Path to training data JSON file (default: test dataset)
- `--epochs`: Number of training epochs (default: 3)
- `--batch-size`: Training batch size (default: 16)
- `--learning-rate`: Learning rate for optimizer (default: 2e-5)
- `--output-dir`: Directory to save model checkpoint (default: models/classification/benchmark_v1)

#### Training Data Format

```json
{
  "metadata": {
    "num_samples": 200,
    "num_classes": 10,
    "class_distribution": {
      "000": 20,
      "100": 20
    }
  },
  "samples": [
    {
      "text": "Machine learning is a subset of artificial intelligence...",
      "taxonomy_codes": ["000", "004"],
      "confidence": 1.0
    }
  ]
}
```

#### Expected Training Time

- **CPU**: 15-30 minutes for 200 samples
- **GPU**: 5-10 minutes for 200 samples
- **Memory**: 4-8GB RAM

#### Training Output

```
Loading classification data from tests/ml_benchmarks/datasets/classification_test.json
Loaded 200 samples with 10 unique taxonomy codes
Training classification model...
Epoch 1/3: 100%|████████| 10/10 [02:15<00:00, 13.5s/it]
Validation F1: 0.85
Epoch 2/3: 100%|████████| 10/10 [02:12<00:00, 13.2s/it]
Validation F1: 0.88
Epoch 3/3: 100%|████████| 10/10 [02:10<00:00, 13.0s/it]
Validation F1: 0.90
Training complete!
Model saved to: models/classification/benchmark_v1
```

### Training the NCF Model

The NCF (Neural Collaborative Filtering) model learns user-item interaction patterns for recommendations.

#### Quick Start

```bash
# Navigate to backend directory
cd backend

# Train with test dataset (default)
python scripts/train_ncf.py

# Train with custom dataset
python scripts/train_ncf.py --data-path path/to/interactions.json --epochs 10
```

#### Command-Line Options

```bash
python scripts/train_ncf.py \
  --data-path tests/ml_benchmarks/datasets/recommendation_test.json \
  --epochs 10 \
  --batch-size 256 \
  --learning-rate 0.001 \
  --embedding-dim 64 \
  --output-path models/ncf_benchmark_v1.pt
```

**Parameters:**
- `--data-path`: Path to interaction data JSON file (default: test dataset)
- `--epochs`: Number of training epochs (default: 10)
- `--batch-size`: Training batch size (default: 256)
- `--learning-rate`: Learning rate for Adam optimizer (default: 0.001)
- `--embedding-dim`: Embedding dimension for users/items (default: 64)
- `--hidden-layers`: MLP hidden layer sizes (default: [128, 64, 32])
- `--output-path`: Path to save model checkpoint (default: models/ncf_benchmark_v1.pt)

#### Training Data Format

```json
{
  "metadata": {
    "num_users": 50,
    "num_items": 200,
    "num_interactions": 1000,
    "density": 0.1
  },
  "interactions": [
    {
      "user_id": "user_1",
      "item_id": "item_42",
      "timestamp": "2024-01-15T10:30:00",
      "interaction_type": "view",
      "implicit_rating": 1.0
    }
  ]
}
```

#### Expected Training Time

- **CPU**: 10-20 minutes for 1000 interactions
- **GPU**: 2-5 minutes for 1000 interactions
- **Memory**: 2-4GB RAM

#### Training Output

```
Loading interaction data from tests/ml_benchmarks/datasets/recommendation_test.json
Loaded 1000 interactions for 50 users and 200 items
Dataset density: 10.0%
Creating negative samples (ratio 4:1)...
Generated 4000 negative samples
Splitting data: 80% train, 20% validation
Training NCF model...
Epoch 1/10: Loss=0.6234, Val NDCG@10=0.42, Hit Rate@10=0.58
Epoch 2/10: Loss=0.5123, Val NDCG@10=0.48, Hit Rate@10=0.64
...
Epoch 10/10: Loss=0.3456, Val NDCG@10=0.55, Hit Rate@10=0.72
Training complete!
Model saved to: models/ncf_benchmark_v1.pt
```

### Using Trained Models

#### NCF Service API

The NCF service provides collaborative filtering recommendations using the trained model.

**Initialize Service:**

```python
from backend.app.services.ncf_service import NCFService
from backend.app.database.base import SessionLocal

db = SessionLocal()
ncf_service = NCFService(db, model_path="models/ncf_benchmark_v1.pt")
```

**Get Recommendations:**

```python
# Get top-10 recommendations for a user
recommendations = ncf_service.recommend(
    user_id="user_123",
    top_k=10,
    exclude_seen=True
)

# Returns: [(item_id, score), ...]
# Example: [("item_42", 0.89), ("item_17", 0.85), ...]
```

**Predict Scores:**

```python
# Predict score for specific user-item pairs
scores = ncf_service.predict(
    user_id="user_123",
    item_ids=["item_1", "item_2", "item_3"]
)

# Returns: {"item_1": 0.75, "item_2": 0.82, "item_3": 0.68}
```

**Batch Prediction:**

```python
# Efficient batch prediction
scores = ncf_service.predict_batch(
    user_id="user_123",
    item_ids=list_of_100_items
)
```

**Cold Start Handling:**

The NCF service automatically handles cold start scenarios:

```python
# For new users with no interaction history
recommendations = ncf_service.recommend(user_id="new_user_999", top_k=10)
# Returns popular items as fallback
```

#### Classification Service API

The classification service is already integrated into the resource ingestion pipeline. To use it directly:

```python
from backend.app.services.ml_classification_service import MLClassificationService
from backend.app.database.base import SessionLocal

db = SessionLocal()
classifier = MLClassificationService(
    db=db,
    model_name="distilbert-base-uncased",
    model_version="benchmark_v1"
)

# Classify text
predictions = classifier.predict(
    text="Machine learning is transforming artificial intelligence...",
    top_k=5
)

# Returns: {"000": 0.92, "004": 0.87, "100": 0.75, ...}
```

### Model Performance Expectations

#### Classification Model

- **F1 Score**: 0.85-0.90 (on test dataset)
- **Precision**: 0.83-0.88
- **Recall**: 0.87-0.92
- **Inference Latency**: <100ms (p95)

#### NCF Model

- **NDCG@10**: 0.50-0.60 (on test dataset)
- **Hit Rate@10**: 0.65-0.75
- **Inference Latency**: <50ms (p95)
- **Cold Start Latency**: <100ms (p95)

### Troubleshooting Training Issues

#### Issue: Out of Memory

**Symptoms:**
```
RuntimeError: CUDA out of memory
```

**Solutions:**
1. Reduce batch size:
   ```bash
   python scripts/train_classification.py --batch-size 8
   python scripts/train_ncf.py --batch-size 128
   ```

2. Use CPU instead of GPU:
   ```bash
   export CUDA_VISIBLE_DEVICES=""
   python scripts/train_classification.py
   ```

3. Reduce model size (NCF only):
   ```bash
   python scripts/train_ncf.py --embedding-dim 32 --hidden-layers 64 32
   ```

#### Issue: Poor Model Performance

**Symptoms:**
- Classification F1 < 0.70
- NCF NDCG@10 < 0.40

**Solutions:**

1. **Increase training data**:
   - Classification: Aim for 500+ samples
   - NCF: Aim for 2000+ interactions

2. **Adjust hyperparameters**:
   ```bash
   # Classification: Lower learning rate, more epochs
   python scripts/train_classification.py --learning-rate 1e-5 --epochs 5
   
   # NCF: Larger embeddings, more epochs
   python scripts/train_ncf.py --embedding-dim 128 --epochs 20
   ```

3. **Check data quality**:
   - Ensure balanced class distribution
   - Verify interaction data has sufficient user/item coverage
   - Remove noisy or duplicate samples

#### Issue: Training Takes Too Long

**Symptoms:**
- Classification: >1 hour on CPU
- NCF: >30 minutes on CPU

**Solutions:**

1. **Use GPU acceleration**:
   ```bash
   # Verify GPU is available
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. **Reduce dataset size** (for testing):
   ```bash
   # Use smaller subset for quick validation
   python scripts/train_classification.py --epochs 1
   ```

3. **Increase batch size** (if memory allows):
   ```bash
   python scripts/train_classification.py --batch-size 32
   python scripts/train_ncf.py --batch-size 512
   ```

#### Issue: Model Not Found in Benchmarks

**Symptoms:**
```
pytest.skip: Benchmark model not available. Train model first.
```

**Solutions:**

1. Train the required model:
   ```bash
   python scripts/train_classification.py
   python scripts/train_ncf.py
   ```

2. Verify checkpoint exists:
   ```bash
   ls -lh models/classification/benchmark_v1/
   ls -lh models/ncf_benchmark_v1.pt
   ```

3. Check model path in test fixtures:
   ```python
   # In tests/ml_benchmarks/conftest.py
   @pytest.fixture
   def trained_ncf_model(db):
       model_path = "models/ncf_benchmark_v1.pt"
       if not os.path.exists(model_path):
           pytest.skip("NCF model not found. Run: python scripts/train_ncf.py")
   ```

### Advanced Training Topics

#### Custom Training Data

To train models with your own data:

1. **Prepare data in the required JSON format** (see format examples above)

2. **Validate data format**:
   ```python
   from backend.scripts.prepare_training_data import validate_data_format
   
   with open("my_data.json") as f:
       data = json.load(f)
   
   is_valid = validate_data_format(data, "classification")
   ```

3. **Train with custom data**:
   ```bash
   python scripts/train_classification.py --data-path my_classification_data.json
   python scripts/train_ncf.py --data-path my_interaction_data.json
   ```

#### Hyperparameter Tuning

For production models, consider tuning hyperparameters:

**Classification:**
- Learning rate: Try [1e-5, 2e-5, 5e-5]
- Epochs: Try [3, 5, 10]
- Batch size: Try [8, 16, 32]

**NCF:**
- Embedding dimension: Try [32, 64, 128]
- Hidden layers: Try [[64, 32], [128, 64, 32], [256, 128, 64]]
- Learning rate: Try [0.0001, 0.001, 0.01]
- Negative sampling ratio: Try [2, 4, 8]

#### Model Versioning

To train multiple model versions:

```bash
# Train different versions
python scripts/train_classification.py --output-dir models/classification/v1
python scripts/train_classification.py --output-dir models/classification/v2

# Use specific version in service
classifier = MLClassificationService(
    db=db,
    model_version="v2"
)
```

#### Continuous Training

For production systems, implement continuous training:

1. **Collect new training data** from user interactions
2. **Retrain periodically** (weekly/monthly)
3. **Evaluate on held-out test set**
4. **Deploy if performance improves**
5. **Monitor for performance degradation**

## Deployment Guide

### Development Deployment

**Local Development:**
```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Docker Development:**
```bash
cd docker
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

###
 Phase 11: Hybrid Recommendation Engine Architecture

The Phase 11 Hybrid Recommendation Engine combines Neural Collaborative Filtering (NCF), content-based similarity, and graph-based discovery to provide personalized, intelligent recommendations. The system learns from user interactions, optimizes for diversity and novelty, and adapts to individual preferences.

#### System Overview

**Key Components:**
1. **User Profile Service** - Manages user preferences and interaction tracking
2. **Collaborative Filtering Service** - Neural Collaborative Filtering with PyTorch
3. **Hybrid Recommendation Service** - Multi-strategy recommendation generation
4. **Performance Monitoring** - Caching and latency tracking

**Data Flow:**
```
User Interaction → Track in UserInteraction → Update UserProfile
                                            ↓
                                    Trigger Preference Learning
                                            ↓
Recommendation Request → Generate Candidates (3 strategies)
                                            ↓
                            Rank with Hybrid Scoring
                                            ↓
                            Apply MMR Diversity
                                            ↓
                            Apply Novelty Boost
                                            ↓
                            Return Recommendations
```

#### Database Models

**UserProfile Model:**
```python
class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Research context
    research_domains = Column(Text, nullable=True)  # JSON array
    active_domain = Column(String(255), nullable=True)
    
    # Learned preferences
    preferred_taxonomy_ids = Column(Text, nullable=True)  # JSON array
    preferred_authors = Column(Text, nullable=True)  # JSON array
    preferred_sources = Column(Text, nullable=True)  # JSON array
    excluded_sources = Column(Text, nullable=True)  # JSON array
    
    # User settings
    diversity_preference = Column(Float, nullable=False, default=0.5)
    novelty_preference = Column(Float, nullable=False, default=0.3)
    recency_bias = Column(Float, nullable=False, default=0.5)
    
    # Metrics
    total_interactions = Column(Integer, nullable=False, default=0)
    avg_session_duration = Column(Integer, nullable=True)
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), onupdate=func.current_timestamp())


**UserInteraction Model:**
```python
class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    resource_id = Column(UUID, ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Interaction details
    interaction_type = Column(String(50), nullable=False)
    interaction_strength = Column(Float, nullable=False)
    is_positive = Column(Boolean, nullable=False, default=False)
    confidence = Column(Float, nullable=False, default=0.0)
    
    # Implicit signals
    dwell_time = Column(Integer, nullable=True)
    scroll_depth = Column(Float, nullable=True)
    annotation_count = Column(Integer, nullable=True, default=0)
    return_visits = Column(Integer, nullable=False, default=1)
    
    # Explicit feedback
    rating = Column(Integer, nullable=True)
    
    # Context
    session_id = Column(String(255), nullable=True)
    interaction_timestamp = Column(DateTime(timezone=True), server_default=func.current_timestamp(), index=True)
    
    # Relationships
    resource = relationship("Resource", back_populates="interactions")


**RecommendationFeedback Model:**
```python
class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    resource_id = Column(UUID, ForeignKey("resources.id", ondelete="CASCADE"), nullable=False)
    
    # Recommendation context
    recommendation_strategy = Column(String(50), nullable=False)
    recommendation_score = Column(Float, nullable=False)
    rank_position = Column(Integer, nullable=False)
    
    # Feedback
    was_clicked = Column(Boolean, nullable=False, default=False)
    was_useful = Column(Boolean, nullable=True)
    feedback_notes = Column(Text, nullable=True)
    
    # Timestamps
    recommended_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    feedback_at = Column(DateTime(timezone=True), nullable=True)


#### User Profile Service

The UserProfileService manages user preferences, tracks interactions, and generates user embeddings.

**Core Methods:**

```python
class UserProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def get_or_create_profile(self, user_id: str) -> UserProfile:
        """
        Get existing profile or create with defaults.
        
        Default preferences:
        - diversity_preference: 0.5 (balanced)
        - novelty_preference: 0.3 (some novelty)
        - recency_bias: 0.5 (balanced)
        
        Performance: <10ms
        """
        profile = self.db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
        
        if not profile:
            profile = UserProfile(
                id=uuid.uuid4(),
                user_id=user_id,
                diversity_preference=0.5,
                novelty_preference=0.3,
                recency_bias=0.5
            )
            self.db.add(profile)
            self.db.commit()
            self.logger.info(f"Created profile for user {user_id}")
        
        return profile


    def track_interaction(
        self,
        user_id: str,
        resource_id: str,
        interaction_type: str,
        dwell_time: Optional[int] = None,
        scroll_depth: Optional[float] = None,
        session_id: Optional[str] = None
    ) -> UserInteraction:
        """
        Track user-resource interaction with automatic strength computation.
        
        Interaction strength formula:
        - view: 0.1 + min(0.3, dwell_time/1000) + 0.1*scroll_depth
        - annotation: 0.7
        - collection_add: 0.8
        - export: 0.9
        
        Positive threshold: strength > 0.4
        
        Performance: <50ms
        """
        # Compute interaction strength
        strength = self._compute_interaction_strength(
            interaction_type, dwell_time, scroll_depth
        )
        
        # Check for existing interaction
        existing = self.db.query(UserInteraction).filter(
            UserInteraction.user_id == user_id,
            UserInteraction.resource_id == resource_id
        ).first()
        
        if existing:
            # Update existing
            existing.return_visits += 1
            existing.interaction_strength = max(existing.interaction_strength, strength)
            existing.interaction_timestamp = datetime.utcnow()
            interaction = existing
        else:
            # Create new
            interaction = UserInteraction(
                id=uuid.uuid4(),
                user_id=user_id,
                resource_id=resource_id,
                interaction_type=interaction_type,
                interaction_strength=strength,
                is_positive=strength > 0.4,
                confidence=min(1.0, strength + 0.2),
                dwell_time=dwell_time,
                scroll_depth=scroll_depth,
                session_id=session_id
            )
            self.db.add(interaction)
        
        # Update profile
        profile = self.get_or_create_profile(user_id)
        profile.total_interactions += 1
        profile.last_active_at = datetime.utcnow()
        
        # Trigger preference learning every 10 interactions
        if profile.total_interactions % 10 == 0:
            self._update_learned_preferences(user_id)
        
        self.db.commit()
        return interaction


    def get_user_embedding(self, user_id: str) -> np.ndarray:
        """
        Generate user embedding from interaction history.
        
        Algorithm:
        1. Query positive interactions (is_positive=True)
        2. Limit to 100 most recent
        3. Compute weighted average of resource embeddings
        4. Weights = interaction_strength values
        5. Return zero vector for cold start
        
        Performance: <10ms (with caching)
        """
        # Check cache
        cache_key = f"user_embedding:{user_id}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        # Query positive interactions
        interactions = (
            self.db.query(UserInteraction)
            .filter(
                UserInteraction.user_id == user_id,
                UserInteraction.is_positive == True
            )
            .order_by(UserInteraction.interaction_timestamp.desc())
            .limit(100)
            .all()
        )
        
        if not interactions:
            # Cold start: return zero vector
            return np.zeros(768)
        
        # Get resource embeddings
        embeddings = []
        weights = []
        
        for interaction in interactions:
            if interaction.resource.embedding:
                try:
                    embedding = json.loads(interaction.resource.embedding)
                    embeddings.append(embedding)
                    weights.append(interaction.interaction_strength)
                except json.JSONDecodeError:
                    continue
        
        if not embeddings:
            return np.zeros(768)
        
        # Compute weighted average
        embeddings_array = np.array(embeddings)
        weights_array = np.array(weights).reshape(-1, 1)
        
        weighted_sum = np.sum(embeddings_array * weights_array, axis=0)
        weight_sum = np.sum(weights_array)
        
        user_embedding = weighted_sum / weight_sum if weight_sum > 0 else np.zeros(768)
        
        # Cache for 5 minutes
        self._set_in_cache(cache_key, user_embedding, ttl=300)
        
        return user_embedding


#### Neural Collaborative Filtering Service

The CollaborativeFilteringService implements NCF using PyTorch for learning user-item interactions.

**NCF Model Architecture:**

```python
class NCFModel(nn.Module):
    def __init__(self, num_users: int, num_items: int, embedding_dim: int = 64):
        """
        Neural Collaborative Filtering model.
        
        Architecture:
        - User embedding: num_users × embedding_dim
        - Item embedding: num_items × embedding_dim
        - MLP layers: [128, 64, 32, 1]
        - Activation: ReLU
        - Output: Sigmoid (0-1 score)
        """
        super().__init__()
        
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.item_embedding = nn.Embedding(num_items, embedding_dim)
        
        self.mlp = nn.Sequential(
            nn.Linear(embedding_dim * 2, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, user_ids, item_ids):
        user_emb = self.user_embedding(user_ids)
        item_emb = self.item_embedding(item_ids)
        
        # Concatenate embeddings
        x = torch.cat([user_emb, item_emb], dim=1)
        
        # Pass through MLP
        score = self.mlp(x)
        
        return score.squeeze()
```


**Training Process:**

```python
class CollaborativeFilteringService:
    def train_model(self, epochs: int = 10, batch_size: int = 256):
        """
        Train NCF model on interaction history.
        
        Training data:
        - Positive samples: is_positive=True interactions
        - Negative samples: Random non-interacted items
        - Label: interaction_strength (continuous feedback)
        
        Hyperparameters:
        - Optimizer: Adam (lr=0.001)
        - Loss: BCELoss (Binary Cross-Entropy)
        - Batch size: 256
        - Epochs: 10
        
        Performance: ~10 minutes for 10K interactions (GPU)
        """
        # Query positive interactions
        interactions = (
            self.db.query(UserInteraction)
            .filter(UserInteraction.is_positive == True)
            .all()
        )
        
        # Build user/item mappings
        user_ids = list(set(i.user_id for i in interactions))
        item_ids = list(set(i.resource_id for i in interactions))
        
        user_to_idx = {uid: idx for idx, uid in enumerate(user_ids)}
        item_to_idx = {iid: idx for idx, iid in enumerate(item_ids)}
        
        # Initialize model
        model = NCFModel(len(user_ids), len(item_ids))
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
        
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = nn.BCELoss()
        
        # Training loop
        for epoch in range(epochs):
            model.train()
            total_loss = 0
            
            for batch in self._get_batches(interactions, batch_size):
                # Prepare batch
                user_indices = torch.tensor([user_to_idx[i.user_id] for i in batch])
                item_indices = torch.tensor([item_to_idx[i.resource_id] for i in batch])
                labels = torch.tensor([i.interaction_strength for i in batch])
                
                user_indices = user_indices.to(device)
                item_indices = item_indices.to(device)
                labels = labels.to(device)
                
                # Forward pass
                predictions = model(user_indices, item_indices)
                loss = criterion(predictions, labels)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(interactions)
            self.logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
        
        # Save model
        self._save_model(model, user_to_idx, item_to_idx)
```


#### Hybrid Recommendation Service

The HybridRecommendationService combines multiple strategies with sophisticated ranking and diversification.

**Two-Stage Pipeline:**

```python
class HybridRecommendationService:
    def generate_recommendations(
        self,
        user_id: str,
        limit: int = 20,
        strategy: str = "hybrid",
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Generate personalized recommendations using two-stage pipeline.
        
        Stage 1: Candidate Generation
        - Collaborative: NCF predictions (top 100)
        - Content: User embedding similarity (top 100)
        - Graph: Multi-hop neighbors (top 100)
        
        Stage 2: Ranking & Reranking
        - Hybrid scoring with weighted combination
        - MMR diversity optimization
        - Novelty boosting
        - Quality filtering
        
        Performance: <200ms for 20 recommendations
        """
        # Get user profile
        profile = self.user_profile_service.get_or_create_profile(user_id)
        
        # Check cold start
        is_cold_start = profile.total_interactions < 5
        
        # Stage 1: Generate candidates
        candidates = self._generate_candidates(user_id, strategy, is_cold_start)
        
        # Stage 2: Rank candidates
        ranked = self._rank_candidates(user_id, candidates, profile)
        
        # Apply MMR diversity
        diverse = self._apply_mmr(ranked, profile, limit * 2)
        
        # Apply novelty boost
        boosted = self._apply_novelty_boost(diverse, profile)
        
        # Apply quality filtering
        if filters and filters.get("min_quality"):
            boosted = [c for c in boosted if c["quality_score"] >= filters["min_quality"]]
        
        # Return top N
        return boosted[:limit]
```


**Hybrid Scoring Formula:**

```python
def _rank_candidates(self, user_id: str, candidates: List[Dict], profile: UserProfile) -> List[Dict]:
    """
    Rank candidates using hybrid scoring.
    
    Formula:
    hybrid_score = 
        w_collab * collaborative_score +
        w_content * content_score +
        w_graph * graph_score +
        w_quality * quality_score +
        w_recency * recency_score
    
    Default weights:
    - collaborative: 0.35
    - content: 0.30
    - graph: 0.20
    - quality: 0.10
    - recency: 0.05
    
    User can override weights via profile settings.
    """
    # Get weights (user-specific or defaults)
    weights = {
        "collaborative": 0.35,
        "content": 0.30,
        "graph": 0.20,
        "quality": 0.10,
        "recency": 0.05
    }
    
    # Compute hybrid scores
    for candidate in candidates:
        hybrid_score = (
            weights["collaborative"] * candidate.get("collaborative_score", 0.0) +
            weights["content"] * candidate.get("content_score", 0.0) +
            weights["graph"] * candidate.get("graph_score", 0.0) +
            weights["quality"] * candidate.get("quality_score", 0.0) +
            weights["recency"] * candidate.get("recency_score", 0.0)
        )
        candidate["hybrid_score"] = hybrid_score
    
    # Sort by hybrid score
    candidates.sort(key=lambda x: x["hybrid_score"], reverse=True)
    
    return candidates
```


**MMR Diversity Optimization:**

```python
def _apply_mmr(self, candidates: List[Dict], profile: UserProfile, limit: int) -> List[Dict]:
    """
    Apply Maximal Marginal Relevance for diversity.
    
    Algorithm:
    1. Start with empty result set
    2. Select highest-scoring candidate
    3. For remaining, compute MMR = λ*relevance - (1-λ)*max_similarity
    4. Select candidate with highest MMR
    5. Repeat until limit reached
    
    Parameters:
    - λ = profile.diversity_preference (0.0-1.0)
    - relevance = hybrid_score
    - max_similarity = max cosine similarity to selected items
    
    Target: Gini coefficient < 0.3
    """
    if not candidates:
        return []
    
    lambda_param = profile.diversity_preference
    selected = []
    remaining = candidates.copy()
    
    # Select first (highest score)
    selected.append(remaining.pop(0))
    
    # Iteratively select diverse items
    while remaining and len(selected) < limit:
        best_mmr = -float('inf')
        best_idx = 0
        
        for idx, candidate in enumerate(remaining):
            # Compute max similarity to selected
            max_sim = 0.0
            for selected_item in selected:
                sim = self._cosine_similarity(
                    candidate["embedding"],
                    selected_item["embedding"]
                )
                max_sim = max(max_sim, sim)
            
            # Compute MMR score
            mmr = lambda_param * candidate["hybrid_score"] - (1 - lambda_param) * max_sim
            
            if mmr > best_mmr:
                best_mmr = mmr
                best_idx = idx
        
        # Add best MMR candidate
        selected.append(remaining.pop(best_idx))
    
    return selected
```


#### Performance Optimizations

**Caching Strategy:**

```python
class RecommendationCache:
    """
    In-memory cache for user embeddings and NCF predictions.
    
    Cache entries:
    - user_embedding:{user_id} → numpy array (TTL: 5 minutes)
    - ncf_prediction:{user_id}:{resource_id} → float (TTL: 10 minutes)
    
    Invalidation:
    - On new user interaction
    - On profile update
    - On TTL expiration
    """
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        
        # Check TTL
        if time.time() - self.timestamps[key] > 300:  # 5 minutes
            del self.cache[key]
            del self.timestamps[key]
            return None
        
        return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: int = 300):
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def invalidate_user(self, user_id: str):
        """Invalidate all cache entries for a user."""
        keys_to_delete = [k for k in self.cache.keys() if user_id in k]
        for key in keys_to_delete:
            del self.cache[key]
            del self.timestamps[key]
```

**Database Query Optimization:**

```python
# Use .limit() to prevent memory issues
interactions = (
    db.query(UserInteraction)
    .filter(UserInteraction.user_id == user_id)
    .order_by(UserInteraction.interaction_timestamp.desc())
    .limit(100)  # Always limit queries
    .all()
)

# Use .in_() for batch lookups
resource_ids = [c["resource_id"] for c in candidates]
resources = (
    db.query(Resource)
    .filter(Resource.id.in_(resource_ids))
    .all()
)

# Use query.count() instead of len(query.all())
total_interactions = (
    db.query(UserInteraction)
    .filter(UserInteraction.user_id == user_id)
    .count()
)
```


#### NCF Model Training and Deployment

**Training Workflow:**

```bash
# 1. Ensure sufficient training data (>100 interactions)
curl "http://127.0.0.1:8000/admin/recommendations/stats"

# 2. Train initial model
curl -X POST http://127.0.0.1:8000/admin/ncf/train \
  -H "Content-Type: application/json" \
  -d '{
    "epochs": 10,
    "batch_size": 256,
    "learning_rate": 0.001
  }'

# 3. Validate model performance
curl "http://127.0.0.1:8000/admin/ncf/validate"

# 4. Deploy model (automatic on training completion)
# Model saved to: models/ncf/model_v{version}.pt

# 5. Monitor model health
curl "http://127.0.0.1:8000/admin/ncf/health"
```

**Retraining Schedule:**

```python
# Automatic retraining triggers:
# - Every 100 new interactions
# - Weekly scheduled task
# - Manual trigger via API

def should_retrain(db: Session) -> bool:
    """
    Check if model should be retrained.
    
    Criteria:
    - 100+ new interactions since last training
    - 7+ days since last training
    - Model performance degradation detected
    """
    last_training = get_last_training_timestamp(db)
    new_interactions = count_interactions_since(db, last_training)
    
    if new_interactions >= 100:
        return True
    
    if (datetime.utcnow() - last_training).days >= 7:
        return True
    
    return False
```

**Model Versioning:**

```python
# Model files structure:
models/
  ncf/
    model_v1.0.pt          # Model weights
    user_mapping_v1.0.json # User ID to index mapping
    item_mapping_v1.0.json # Item ID to index mapping
    metadata_v1.0.json     # Training metadata
    
# Metadata includes:
{
  "version": "1.0",
  "trained_at": "2024-01-15T10:00:00Z",
  "num_users": 150,
  "num_items": 5000,
  "num_interactions": 10000,
  "epochs": 10,
  "batch_size": 256,
  "final_loss": 0.234,
  "validation_metrics": {
    "ndcg@20": 0.67,
    "recall@20": 0.82
  }
}
```


---

## Production Deployment Guide

### Performance Optimizations Implemented

#### 1. Async SQLAlchemy Migration
- **Before**: Synchronous SQLAlchemy blocking the event loop
- **After**: Async SQLAlchemy with `AsyncSession` for true concurrency
- **Impact**: 3-5x improvement in concurrent request handling

#### 2. Dependency Caching
- **Before**: Expensive service initialization on every request
- **After**: `@lru_cache()` for AI models, classifiers, and analyzers
- **Impact**: 50-80% reduction in request latency

#### 3. Performance Monitoring
- **Before**: No visibility into performance bottlenecks
- **After**: Prometheus metrics with Grafana dashboards
- **Impact**: Proactive issue detection and performance optimization

#### 4. Production Gunicorn Configuration
- **Before**: Development-only Uvicorn setup
- **After**: Optimized Gunicorn with proper worker counts
- **Impact**: Production-ready scalability and reliability

### Quick Start

#### Option 1: Docker Compose (Recommended)

```bash
# Clone and navigate to the project
git clone <repository-url>
cd backend

# Navigate to docker directory
cd docker

# Start all services
docker-compose up -d

# Check health
curl http://localhost:8000/metrics
```

**Services Available:**
- Neo Alexandria API: http://localhost:8000
- Prometheus Metrics: http://localhost:9090
- Grafana Dashboards: http://localhost:3000 (admin/admin)

#### Option 2: Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/neo_alexandria"
export ENV=prod
export ENABLE_METRICS=true

# Run database migrations
alembic upgrade head

# Start with Gunicorn
gunicorn backend.app.main:app -c gunicorn.conf.py
```

### Configuration

#### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:pass@host:port/dbname
ENV=prod

# Optional
ENABLE_METRICS=true
MIN_QUALITY_THRESHOLD=0.7
BACKUP_FREQUENCY=weekly
TIMEZONE=UTC
```

#### Gunicorn Configuration

The `gunicorn.conf.py` file includes optimized settings:

- **Workers**: `(2 × CPU cores) + 1` for optimal concurrency
- **Worker Class**: `uvicorn.workers.UvicornWorker` for async support
- **Memory Management**: Request recycling and preloading
- **Timeouts**: Optimized for async operations
- **Logging**: Structured logging with request timing

#### Database Configuration

**PostgreSQL (Production):**
```bash
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
```

**SQLite (Development):**
```bash
DATABASE_URL=sqlite+aiosqlite:///./backend.db
```

### Monitoring

#### Metrics Endpoints

- **Prometheus Metrics**: `/metrics`
- **Health Check**: `/metrics` (returns 200 if healthy)

#### Key Metrics Tracked

1. **Request Performance**
   - `neo_alexandria_request_duration_seconds`
   - `neo_alexandria_requests_total`

2. **Business Logic**
   - `neo_alexandria_ingestion_success_total`
   - `neo_alexandria_ingestion_failure_total`
   - `neo_alexandria_active_ingestions`

3. **AI Processing**
   - `neo_alexandria_ai_processing_seconds`

4. **Database Performance**
   - `neo_alexandria_database_query_seconds`

5. **Caching**
   - `neo_alexandria_cache_hits_total`
   - `neo_alexandria_cache_misses_total`

#### Grafana Dashboards

Access Grafana at http://localhost:3000 with:
- Username: `admin`
- Password: `admin`

Pre-configured dashboards show:
- Request rates and latencies
- Error rates and types
- AI processing performance
- Database query performance
- Active ingestion processes

### Performance Benchmarks

#### Before Optimizations
- **Concurrent Requests**: ~50 req/s
- **Average Latency**: 200-500ms
- **Memory Usage**: High due to repeated service initialization
- **Error Visibility**: Limited

#### After Optimizations
- **Concurrent Requests**: 200-500 req/s (4-10x improvement)
- **Average Latency**: 50-150ms (3-4x improvement)
- **Memory Usage**: 40-60% reduction
- **Error Visibility**: Full observability with metrics

### Scaling Considerations

#### Horizontal Scaling
- Use load balancer (nginx/HAProxy) in front of multiple Gunicorn instances
- Each instance should run on different ports
- Database connection pooling handles concurrent connections

#### Vertical Scaling
- Increase `workers` in `gunicorn.conf.py` for more CPU cores
- Monitor memory usage and adjust `max_requests` accordingly
- Consider Redis for session storage and caching

#### Database Scaling
- Use connection pooling for high concurrency
- Consider read replicas for read-heavy workloads
- Monitor query performance with provided metrics

### Troubleshooting

#### Common Issues

1. **High Memory Usage**
   - Check for memory leaks in AI model loading
   - Adjust `max_requests` in Gunicorn config
   - Monitor with `neo_alexandria_active_ingestions` metric

2. **Slow Database Queries**
   - Check `neo_alexandria_database_query_seconds` metrics
   - Optimize slow queries identified in logs
   - Consider database indexing

3. **AI Processing Bottlenecks**
   - Monitor `neo_alexandria_ai_processing_seconds`
   - Consider model caching or lighter models
   - Scale AI processing horizontally

#### Health Checks

```bash
# Check API health
curl -f http://localhost:8000/metrics

# Check Prometheus
curl -f http://localhost:9090/-/healthy

# Check Grafana
curl -f http://localhost:3000/api/health
```

### Security Considerations

1. **Environment Variables**: Never commit sensitive data
2. **Database**: Use strong passwords and SSL connections
3. **Network**: Use reverse proxy (nginx) for SSL termination
4. **Monitoring**: Secure Prometheus and Grafana endpoints
5. **Updates**: Keep dependencies updated for security patches

### Backup and Recovery

#### Database Backups
```bash
# PostgreSQL
pg_dump backend > backup_$(date +%Y%m%d).sql

# Restore
psql backend < backup_20240101.sql
```

#### Application Data
- Archive storage in `./storage/archive/`
- Regular backups of uploaded content
- Configuration file backups

---

## Testing Strategy

### Overview

Neo Alexandria uses a hybrid testing approach that balances speed, reliability, and comprehensive coverage:

1. **Unit Tests** - Fast, isolated tests with mocked dependencies
2. **Integration Tests** - Test component interactions
3. **AI Tests** - Test real AI functionality (requires AI dependencies)

### Test Categories

#### Unit Tests (Fast)
- Test individual functions and classes
- Use mocks for external dependencies (AI, network, etc.)
- Should run in < 1 second per test
- Run with: `python run_tests.py unit`

#### Integration Tests
- Test multiple components working together
- May use real services but mock external APIs
- Run with: `python run_tests.py integration`

#### AI Tests (Slow)
- Test real AI functionality
- Require AI dependencies (transformers, models)
- Can be slow and may fail due to model loading issues
- Run with: `python run_tests.py ai`

### Running Tests

#### Quick Commands

```bash
# Fast tests (unit tests with mocked AI)
python run_tests.py fast

# All tests except AI
python run_tests.py unit

# Integration tests
python run_tests.py integration

# AI tests (real AI functionality)
python run_tests.py ai

# All tests
python run_tests.py all
```

#### Manual pytest Commands

```bash
# Unit tests only
pytest -m "not (ai or integration or slow)"

# AI tests only
pytest -m "ai"

# Integration tests only
pytest -m "integration"

# Fast tests (no AI dependencies)
pytest -m "not (slow or requires_ai_deps)"

# With coverage
pytest --cov=backend --cov-report=html
```

### Why Mock AI in Unit Tests?

#### Problems with Real AI in Tests:
1. **Speed**: AI models are slow to load and process
2. **Dependencies**: Requires heavy ML libraries (transformers, torch, etc.)
3. **Reliability**: Models may fail to load, network issues, etc.
4. **Determinism**: AI outputs can vary, making tests flaky
5. **CI/CD**: CI environments may not have GPU or sufficient memory

#### Benefits of Mocking:
1. **Fast**: Tests run in milliseconds instead of seconds
2. **Reliable**: No external dependencies or network calls
3. **Deterministic**: Predictable outputs for assertions
4. **Isolated**: Tests focus on business logic, not AI implementation

### How to Test AI Functionality

#### 1. Dedicated AI Tests
Use `test_ai_integration.py` to test real AI functionality:

```python
@pytest.mark.ai
@pytest.mark.requires_ai_deps
def test_ai_summary_generation():
    ai = AICore()
    summary = ai.generate_summary("Test text about machine learning")
    assert "machine learning" in summary.lower()
```

#### 2. End-to-End Tests
Test complete ingestion with real AI:

```python
@pytest.mark.ai
@pytest.mark.integration
def test_end_to_end_ai_processing():
    # Don't mock AI - use real AI service
    response = client.post("/resources", json={"url": "..."})
    # Verify AI-generated content
```

#### 3. AI Fallback Testing
Test AI service behavior when models aren't available:

```python
@pytest.mark.ai
def test_ai_fallback_behavior():
    ai = AICore()
    # Test fallback logic
```

### Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests  
- `@pytest.mark.ai` - AI-related tests
- `@pytest.mark.slow` - Slow tests
- `@pytest.mark.requires_ai_deps` - Requires AI dependencies

### CI/CD Strategy

#### Fast CI Pipeline
```bash
# Run fast tests on every commit
python run_tests.py fast
```

#### Full CI Pipeline (nightly)
```bash
# Run all tests including AI
python run_tests.py all
```

#### AI-Specific Pipeline
```bash
# Run only AI tests when AI code changes
python run_tests.py ai
```

### Best Practices

#### 1. Mock External Dependencies
```python
# Good: Mock AI service
with patch('backend.app.services.resource_service.AICore') as mock_ai:
    mock_ai.return_value.generate_summary.return_value = "Mock summary"
    # Test business logic
```

#### 2. Test AI Separately
```python
# Good: Dedicated AI test
@pytest.mark.ai
def test_ai_functionality():
    ai = AICore()
    result = ai.generate_summary("test")
    assert result
```

#### 3. Use Appropriate Test Types
- **Unit tests**: Test individual functions
- **Integration tests**: Test component interactions
- **AI tests**: Test AI functionality specifically

#### 4. Mark Tests Appropriately
```python
@pytest.mark.ai
@pytest.mark.requires_ai_deps
def test_real_ai():
    # This test requires AI dependencies
    pass

@pytest.mark.unit
def test_business_logic():
    # This test mocks AI
    pass
```

### Troubleshooting

#### AI Tests Failing
1. Check if AI dependencies are installed: `pip install transformers torch`
2. Check if models can be downloaded (network access)
3. Check available memory (AI models are large)

#### Slow Tests
1. Use `pytest -m "not slow"` to skip slow tests
2. Use `pytest -x` to stop on first failure
3. Use `pytest --tb=short` for shorter tracebacks

#### Flaky Tests
1. Check if tests are using real AI (should use mocks for unit tests)
2. Check for race conditions in async tests
3. Add appropriate timeouts and retries

---

## Scheduled Tasks

### Overview

Phase 9 introduces automated quality monitoring through two scheduled tasks:

1. **Outlier Detection** - Identifies resources with anomalous quality scores (recommended: daily)
2. **Quality Degradation Monitoring** - Detects resources whose quality has degraded over time (recommended: weekly)

### Task Descriptions

#### Outlier Detection

**Purpose**: Automatically identify resources with unusual quality patterns that may indicate data quality issues.

**Algorithm**: Uses Isolation Forest machine learning algorithm to detect anomalies across quality dimensions.

**Configuration**:
- Default batch size: 1000 resources
- Recommended schedule: Daily
- Contamination rate: 10% (expects ~10% outliers)

**Outputs**:
- Flags outliers with `is_quality_outlier = True`
- Sets `needs_quality_review = True` for human review
- Stores anomaly score and specific reasons

#### Quality Degradation Monitoring

**Purpose**: Detect resources whose quality has significantly decreased over time, indicating potential issues like broken links or outdated content.

**Algorithm**: Recomputes quality for resources older than the time window and compares to historical scores.

**Configuration**:
- Default time window: 30 days
- Recommended schedule: Weekly
- Degradation threshold: 20% drop in quality score

**Outputs**:
- Identifies degraded resources
- Sets `needs_quality_review = True`
- Returns degradation report with old/new quality scores

### Running Scheduled Tasks

#### Manual Execution

Run all tasks:
```bash
cd backend
python scripts/run_scheduled_tasks.py all
```

Run specific task:
```bash
python scripts/run_scheduled_tasks.py outlier-detection
python scripts/run_scheduled_tasks.py degradation-monitoring
```

With custom parameters:
```bash
python scripts/run_scheduled_tasks.py outlier-detection --batch-size 500
python scripts/run_scheduled_tasks.py degradation-monitoring --time-window 60
```

Get JSON output:
```bash
python scripts/run_scheduled_tasks.py all --json
```

#### Cron Configuration

Add to crontab (`crontab -e`):

```cron
# Daily outlier detection at 2 AM
0 2 * * * cd /path/to/neo-alexandria/backend && /path/to/python scripts/run_scheduled_tasks.py outlier-detection >> /var/log/neo-alexandria/outlier-detection.log 2>&1

# Weekly degradation monitoring on Sundays at 3 AM
0 3 * * 0 cd /path/to/neo-alexandria/backend && /path/to/python scripts/run_scheduled_tasks.py degradation-monitoring >> /var/log/neo-alexandria/degradation-monitoring.log 2>&1
```

#### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily/weekly)
4. Action: Start a program
   - Program: `python.exe`
   - Arguments: `scripts/run_scheduled_tasks.py outlier-detection`
   - Start in: `C:\path\to\neo-alexandria\backend`

#### Docker/Kubernetes

Add to docker/docker-compose.yml:
```yaml
services:
  scheduled-tasks:
    build: ./backend
    command: python scripts/run_scheduled_tasks.py all
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - db
    restart: "no"
```

### Configuration

Edit `backend/app/services/scheduled_tasks.py` to customize:

```python
class ScheduledTaskConfig:
    # Outlier detection configuration
    OUTLIER_DETECTION_ENABLED = True
    OUTLIER_DETECTION_BATCH_SIZE = 1000
    OUTLIER_DETECTION_SCHEDULE = "daily"
    
    # Quality degradation monitoring configuration
    DEGRADATION_MONITORING_ENABLED = True
    DEGRADATION_MONITORING_TIME_WINDOW_DAYS = 30
    DEGRADATION_MONITORING_SCHEDULE = "weekly"
```

### Monitoring and Alerts

#### Logs

Tasks log to standard output and Python logging system:
- INFO: Normal execution progress
- WARNING: Degraded resources detected
- ERROR: Task failures

Configure logging in your application:
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/neo-alexandria/scheduled-tasks.log'),
        logging.StreamHandler()
    ]
)
```

#### Metrics

Task execution returns metrics:
```json
{
  "success": true,
  "outlier_count": 42,
  "batch_size": 1000,
  "duration_seconds": 12.34,
  "timestamp": "2025-11-11T02:00:00Z"
}
```

#### Alerting

Set up alerts based on:
- High outlier count (>20% of batch)
- Degradation spike (>50 resources)
- Task failures
- Long execution times

Example with monitoring tools:
```bash
# Check exit code
python scripts/run_scheduled_tasks.py outlier-detection
if [ $? -ne 0 ]; then
    # Send alert (email, Slack, PagerDuty, etc.)
    echo "Outlier detection failed" | mail -s "Alert" admin@example.com
fi
```

### Review Queue

Resources flagged by scheduled tasks appear in the review queue:

```bash
# API endpoint
GET /quality/review-queue?sort_by=outlier_score&limit=50
```

Review queue includes:
- Resources with `needs_quality_review = True`
- Outlier score and reasons
- Quality dimension breakdown
- Last computation timestamp

### Performance Considerations

#### Outlier Detection
- Processes 1000 resources in ~30 seconds
- Memory usage: ~500MB for feature matrix
- CPU intensive during Isolation Forest training
- Consider running during low-traffic periods

#### Degradation Monitoring
- Recomputes quality for resources older than time window
- Duration depends on number of stale resources
- I/O intensive (database queries)
- Consider batching for large datasets

#### Optimization Tips
1. Run during off-peak hours (2-4 AM)
2. Adjust batch sizes based on system resources
3. Monitor execution times and adjust schedules
4. Use database indexes on quality fields
5. Consider parallel processing for large datasets

### Troubleshooting

#### Task Fails with "Insufficient Data"
- Outlier detection requires minimum 10 resources with quality scores
- Run quality computation on existing resources first

#### High Memory Usage
- Reduce batch size for outlier detection
- Process in smaller chunks

#### Long Execution Times
- Check database indexes on quality fields
- Optimize quality computation queries
- Consider caching frequently accessed data

#### No Outliers Detected
- Verify quality scores are computed for resources
- Check contamination parameter (may need adjustment)
- Review quality score distribution

---

**Last Updated**: November 15, 2025  
**Documentation Version**: 2.0.0  
**API Version**: 1.5.0 (Phase 11)


---

## Phase 12.5: Event-Driven Architecture

### Overview

Phase 12.5 transforms Neo Alexandria into a production-grade event-driven system with distributed task processing, automatic data consistency, and horizontal scalability.

### Event System

#### Event Emitter

The EventEmitter provides a centralized pub-sub system for decoupled component communication:

```python
from app.events.event_system import event_emitter, EventPriority
from app.events.event_types import SystemEvent

# Emit an event
event_emitter.emit(
    SystemEvent.RESOURCE_UPDATED,
    data={"resource_id": resource_id, "changes": ["content"]},
    priority=EventPriority.HIGH
)

# Register a handler
@event_emitter.on(SystemEvent.RESOURCE_UPDATED)
async def handle_resource_update(event):
    print(f"Resource {event.data['resource_id']} was updated")

# Synchronous handler
@event_emitter.on(SystemEvent.CACHE_INVALIDATED)
def handle_cache_invalidation(event):
    print(f"Cache invalidated: {event.data['keys']}")
```

#### Event Types

All system events follow the `{entity}.{action}` naming convention:

**Resource Events:**
- `resource.created` - New resource added
- `resource.updated` - Resource modified
- `resource.deleted` - Resource removed
- `resource.content_changed` - Content field updated
- `resource.metadata_changed` - Metadata fields updated

**Processing Events:**
- `ingestion.started` - Ingestion pipeline started
- `ingestion.completed` - Ingestion successful
- `ingestion.failed` - Ingestion error
- `embedding.generated` - Embedding created
- `quality.computed` - Quality score calculated
- `classification.completed` - ML classification done

**User Events:**
- `user.interaction_tracked` - User viewed/downloaded resource
- `user.profile_updated` - User preferences changed

**System Events:**
- `cache.invalidated` - Cache entries removed
- `search.index_updated` - FTS5 index refreshed
- `graph.edges_updated` - Citation graph modified

### Celery Task Queue

#### Task Configuration

Celery provides reliable, distributed background processing:

```python
# app/tasks/celery_app.py
from celery import Celery

celery_app = Celery(
    "neo_alexandria",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

# Task routing
celery_app.conf.task_routes = {
    "app.tasks.celery_tasks.update_search_index_task": {"queue": "urgent"},
    "app.tasks.celery_tasks.regenerate_embedding_task": {"queue": "high_priority"},
    "app.tasks.celery_tasks.classify_resource_task": {"queue": "ml_tasks"},
}

# Priority levels (0-10, higher = more urgent)
celery_app.conf.task_default_priority = 5
```

#### Core Tasks

**Embedding Regeneration:**
```python
from app.tasks.celery_tasks import regenerate_embedding_task

# Queue task
task = regenerate_embedding_task.apply_async(
    args=[resource_id],
    priority=7,
    countdown=5  # 5 second delay
)

# Check status
result = task.get(timeout=30)
```

**Quality Recomputation:**
```python
from app.tasks.celery_tasks import recompute_quality_task

task = recompute_quality_task.apply_async(
    args=[resource_id],
    priority=5,
    countdown=10
)
```

**Search Index Update:**
```python
from app.tasks.celery_tasks import update_search_index_task

# Urgent priority for immediate searchability
task = update_search_index_task.apply_async(
    args=[resource_id],
    priority=9,
    countdown=1
)
```

**Batch Processing:**
```python
from app.tasks.celery_tasks import batch_process_resources_task

# Process multiple resources with progress tracking
task = batch_process_resources_task.apply_async(
    args=[resource_ids, "regenerate_embeddings"],
    priority=5
)

# Monitor progress
while not task.ready():
    state = task.state
    if state == 'PROGRESS':
        info = task.info
        print(f"Progress: {info['current']}/{info['total']}")
    time.sleep(1)
```

#### Scheduled Tasks

Celery Beat handles periodic maintenance:

```python
# app/tasks/celery_app.py
celery_app.conf.beat_schedule = {
    "quality-degradation-monitoring": {
        "task": "app.tasks.celery_tasks.monitor_quality_degradation_task",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    "quality-outlier-detection": {
        "task": "app.tasks.celery_tasks.detect_quality_outliers_task",
        "schedule": crontab(day_of_week=0, hour=3, minute=0),  # Weekly Sunday 3 AM
    },
    "classification-model-retraining": {
        "task": "app.tasks.celery_tasks.retrain_classification_model_task",
        "schedule": crontab(day_of_month=1, hour=0, minute=0),  # Monthly 1st at midnight
    },
    "cache-cleanup": {
        "task": "app.tasks.celery_tasks.cleanup_cache_task",
        "schedule": crontab(hour=4, minute=0),  # Daily at 4 AM
    },
}
```

### Automatic Data Consistency Hooks

Event hooks ensure derived data stays synchronized automatically:

```python
# app/events/hooks.py
from app.events.event_system import event_emitter
from app.events.event_types import SystemEvent
from app.tasks.celery_tasks import regenerate_embedding_task

@event_emitter.on(SystemEvent.RESOURCE_CONTENT_CHANGED)
async def on_content_changed_regenerate_embedding(event):
    """
    When content changes, automatically queue embedding regeneration.
    Priority: HIGH (7), Delay: 5 seconds (debounce)
    """
    resource_id = event.data.get("resource_id")
    regenerate_embedding_task.apply_async(
        args=[resource_id],
        priority=7,
        countdown=5
    )

@event_emitter.on(SystemEvent.RESOURCE_METADATA_CHANGED)
async def on_metadata_changed_recompute_quality(event):
    """
    When metadata changes, automatically recompute quality score.
    Priority: MEDIUM (5), Delay: 10 seconds (debounce)
    """
    resource_id = event.data.get("resource_id")
    recompute_quality_task.apply_async(
        args=[resource_id],
        priority=5,
        countdown=10
    )

@event_emitter.on(SystemEvent.RESOURCE_UPDATED)
async def on_resource_updated_sync_search_index(event):
    """
    When resource updates, immediately sync search index.
    Priority: URGENT (9), Delay: 1 second
    """
    resource_id = event.data.get("resource_id")
    update_search_index_task.apply_async(
        args=[resource_id],
        priority=9,
        countdown=1
    )
```

### Redis Caching

#### Cache Configuration

Multi-layer caching with intelligent TTL strategy:

```python
# app/cache/redis_cache.py
from redis import Redis

class RedisCache:
    def __init__(self):
        self.redis = Redis(
            host="localhost",
            port=6379,
            db=2,
            decode_responses=True
        )
        self.stats = CacheStats()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with hit/miss tracking."""
        value = self.redis.get(key)
        if value:
            self.stats.record_hit()
            return json.loads(value)
        self.stats.record_miss()
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with TTL."""
        if ttl is None:
            ttl = self.get_default_ttl(key)
        self.redis.setex(key, ttl, json.dumps(value))
    
    def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern."""
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
            self.stats.record_invalidation(len(keys))
    
    def get_default_ttl(self, key: str) -> int:
        """Get TTL based on key type."""
        if "embedding:" in key:
            return 3600  # 1 hour
        elif "quality:" in key:
            return 1800  # 30 minutes
        elif "search_query:" in key:
            return 300   # 5 minutes
        elif "resource:" in key:
            return 600   # 10 minutes
        return 300  # Default 5 minutes
```

#### Cache Integration

```python
# app/services/embedding_service.py
class EmbeddingService:
    def __init__(self, cache: RedisCache):
        self.cache = cache
    
    def get_embedding(self, resource_id: str) -> Optional[np.ndarray]:
        """Get embedding with caching."""
        cache_key = f"embedding:{resource_id}"
        
        # Try cache first
        cached = self.cache.get(cache_key)
        if cached:
            return np.array(cached)
        
        # Generate if not cached
        embedding = self._generate_embedding(resource_id)
        
        # Store in cache
        self.cache.set(cache_key, embedding.tolist())
        
        return embedding
```

### Docker Compose Deployment

#### Service Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru --appendonly yes
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  celery_worker:
    build: .
    command: celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4
    environment:
      - DATABASE_URL=sqlite:///./backend.db
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
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
    command: celery -A app.tasks.celery_app beat --loglevel=info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis

  flower:
    build: .
    command: celery -A app.tasks.celery_app flower --port=5555
    ports:
      - "5555:5555"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - redis

volumes:
  redis_data:
```

#### Starting Services

```bash
# Navigate to docker directory
cd backend/docker

# Start all services
docker-compose up -d

# Scale workers
docker-compose up -d --scale worker=8

# View logs
docker-compose logs -f worker

# Stop services
docker-compose down
```

### Monitoring and Observability

#### Flower Dashboard

Access Celery task monitoring at `http://localhost:5555`:
- Active tasks and workers
- Task success/failure rates
- Task execution times
- Queue depths
- Worker resource usage

#### API Monitoring Endpoints

**Event History:**
```bash
curl http://localhost:8000/events/history?limit=100
```

**Cache Statistics:**
```bash
curl http://localhost:8000/cache/stats
# Response:
# {
#   "hit_rate": 0.67,
#   "hits": 1340,
#   "misses": 660,
#   "invalidations": 45,
#   "total_operations": 2000
# }
```

**Database Pool Status:**
```bash
curl http://localhost:8000/db/pool
# Response:
# {
#   "pool_size": 20,
#   "checked_in": 15,
#   "checked_out": 5,
#   "overflow": 2,
#   "total_connections": 22
# }
```

### Performance Characteristics

**Scalability:**
- Supports 100+ concurrent ingestions without degradation
- Linear throughput scaling with worker count
- Horizontal scaling across multiple machines

**Cache Performance:**
- 60-70% cache hit rate for repeated operations
- 50-70% computation reduction through caching
- Sub-millisecond cache lookups

**Task Reliability:**
- <1% task failure rate with automatic retries
- Exponential backoff for transient errors
- Dead letter queue for permanent failures

**Search Index Updates:**
- Complete within 5 seconds of resource updates
- URGENT priority ensures immediate searchability
- Automatic retry on failure

### Best Practices

**Event Emission:**
```python
# DO: Emit events after successful operations
resource = resource_service.update(resource_id, data)
event_emitter.emit(
    SystemEvent.RESOURCE_UPDATED,
    data={"resource_id": resource_id, "changes": list(data.keys())}
)

# DON'T: Emit events before operation completes
event_emitter.emit(SystemEvent.RESOURCE_UPDATED, ...)  # Too early!
resource = resource_service.update(resource_id, data)
```

**Task Queuing:**
```python
# DO: Use appropriate priority and countdown
task.apply_async(
    args=[resource_id],
    priority=7,  # HIGH priority
    countdown=5  # 5 second debounce
)

# DON'T: Queue tasks synchronously
task.delay(resource_id)  # Blocks until queued
```

**Cache Invalidation:**
```python
# DO: Use pattern-based invalidation
cache.delete_pattern(f"resource:{resource_id}:*")

# DON'T: Invalidate individual keys
cache.delete(f"resource:{resource_id}:embedding")
cache.delete(f"resource:{resource_id}:quality")
# ... many more deletes
```

**Error Handling:**
```python
# DO: Let Celery handle retries
@celery_app.task(bind=True, max_retries=3)
def my_task(self, resource_id):
    try:
        # Task logic
        pass
    except TransientError as e:
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

# DON'T: Catch all exceptions
@celery_app.task
def my_task(resource_id):
    try:
        # Task logic
        pass
    except Exception:
        pass  # Silently fails, no retry
```

---

## Phase 12: Domain-Driven Design

### Overview

Phase 12 introduces domain objects to replace primitive obsession and improve code maintainability.

### Domain Objects Foundation

#### Base Classes

**ValueObject:**
```python
from dataclasses import dataclass
from app.domain.base import ValueObject, validate_range

@dataclass
class Confidence(ValueObject):
    """Confidence score value object."""
    score: float
    
    def validate(self) -> None:
        validate_range(self.score, 0.0, 1.0, "score")
    
    def is_high(self) -> bool:
        return self.score >= 0.8
    
    def is_low(self) -> bool:
        return self.score < 0.5

# Usage
confidence = Confidence(score=0.95)
print(confidence.is_high())  # True
print(confidence.to_dict())  # {"score": 0.95}
```

**DomainEntity:**
```python
from app.domain.base import DomainEntity

class Resource(DomainEntity):
    """Resource entity with identity."""
    
    def __init__(self, resource_id: str, title: str, url: str):
        super().__init__(resource_id)
        self.title = title
        self.url = url
        self.validate()
    
    def validate(self) -> None:
        validate_non_empty(self.title, "title")
        validate_non_empty(self.url, "url")

# Usage
resource = Resource("123", "Paper Title", "https://example.com")
print(resource.entity_id)  # "123"
```

### Classification Domain Objects

```python
from app.domain.classification import ClassificationPrediction, ClassificationResult

# Create predictions
predictions = [
    ClassificationPrediction(
        category="Computer Science",
        confidence=0.95,
        source="ml_model"
    ),
    ClassificationPrediction(
        category="Artificial Intelligence",
        confidence=0.87,
        source="ml_model"
    )
]

# Create result
result = ClassificationResult(
    resource_id="123",
    predictions=predictions,
    model_version="v1.0",
    timestamp=datetime.now()
)

# Use rich behavior
top_3 = result.get_top_predictions(k=3)
high_conf = result.filter_by_confidence(min_confidence=0.8)
has_high = result.has_high_confidence(threshold=0.9)
```

### Quality Domain Objects

```python
from app.domain.quality import QualityScore

# Create quality score
quality = QualityScore(
    completeness=0.95,
    accuracy=0.88,
    consistency=0.92,
    timeliness=0.75,
    relevance=0.90
)

# Use rich behavior
overall = quality.overall_score()  # Weighted average
level = quality.quality_level()    # "excellent", "good", "fair", "poor"
is_excellent = quality.is_excellent()  # overall >= 0.9
```

### Refactoring Framework

The refactoring framework helps identify and fix code quality issues:

```bash
# Analyze codebase
python -m app.refactoring.cli analyze app/services/

# Detect primitive obsession
python -m app.refactoring.cli detect app/services/classification_service.py

# Validate code quality
python -m app.refactoring.cli validate app/services/
```

