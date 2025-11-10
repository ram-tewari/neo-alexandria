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