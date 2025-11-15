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

### Phase 9: Multi-Dimensional Quality Assessment Architecture

Phase 9 introduces a sophisticated quality assessment framework that evaluates resources across multiple dimensions, detects quality outliers, monitors quality degradation, and evaluates summary quality using state-of-the-art metrics.

#### Quality Service Architecture

The `QualityService` class implements multi-dimensional quality assessment with five independent quality dimensions:

```python
class QualityService:
    """
    Multi-dimensional quality assessment service.
    
    Computes quality scores across five dimensions:
    - Accuracy: Citation validity, source credibility, scholarly metadata
    - Completeness: Metadata coverage, content depth, multi-modal content
    - Consistency: Title-content alignment, internal coherence
    - Timeliness: Publication recency, content freshness
    - Relevance: Classification confidence, citation count
    """
    
    def __init__(self, db: Session, quality_version: str = "v2.0"):
        self.db = db
        self.quality_version = quality_version
        self.default_weights = {
            "accuracy": 0.30,
            "completeness": 0.25,
            "consistency": 0.20,
            "timeliness": 0.15,
            "relevance": 0.10
        }
```

**Key Methods:**

##### compute_quality()

Computes multi-dimensional quality scores for a resource:

```python
def compute_quality(
    self,
    resource_id: str,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, float]:
    """
    Compute quality scores for a resource.
    
    Algorithm:
    1. Fetch resource from database
    2. Validate custom weights (if provided)
    3. Compute each dimension score:
       - _compute_accuracy()
       - _compute_completeness()
       - _compute_consistency()
       - _compute_timeliness()
       - _compute_relevance()
    4. Compute weighted overall score
    5. Update resource with all scores
    6. Return dimension scores
    
    Performance: <1 second per resource
    """
    resource = self.db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise ValueError("Resource not found")
    
    # Use custom or default weights
    weights = weights or self.default_weights
    self._validate_weights(weights)
    
    # Compute dimension scores
    accuracy = self._compute_accuracy(resource)
    completeness = self._compute_completeness(resource)
    consistency = self._compute_consistency(resource)
    timeliness = self._compute_timeliness(resource)
    relevance = self._compute_relevance(resource)
    
    # Compute weighted overall score
    overall = (
        weights["accuracy"] * accuracy +
        weights["completeness"] * completeness +
        weights["consistency"] * consistency +
        weights["timeliness"] * timeliness +
        weights["relevance"] * relevance
    )
    
    # Update resource
    resource.quality_accuracy = accuracy
    resource.quality_completeness = completeness
    resource.quality_consistency = consistency
    resource.quality_timeliness = timeliness
    resource.quality_relevance = relevance
    resource.quality_overall = overall
    resource.quality_weights = json.dumps(weights)
    resource.quality_last_computed = datetime.utcnow()
    resource.quality_computation_version = self.quality_version
    resource.quality_score = overall  # Backward compatibility
    
    self.db.commit()
    
    return {
        "accuracy": accuracy,
        "completeness": completeness,
        "consistency": consistency,
        "timeliness": timeliness,
        "relevance": relevance,
        "overall": overall
    }
```

##### Quality Dimension Computation Methods

**Accuracy Dimension:**
```python
def _compute_accuracy(self, resource: Resource) -> float:
    """
    Compute accuracy dimension score.
    
    Factors:
    - Citation validity (20%): Ratio of valid citations
    - Source credibility (15%): Domain reputation
    - Scholarly metadata (15%): DOI, PMID, arXiv presence
    - Author metadata (10%): Author information presence
    
    Baseline: 0.5 (neutral for resources without citations)
    """
    score = 0.5  # Neutral baseline
    
    # Citation validity (Phase 6 integration)
    citations = resource.citations_outbound
    if citations:
        valid_count = sum(1 for c in citations if c.target_resource_id is not None)
        score += 0.2 * (valid_count / len(citations))
    
    # Source credibility
    if resource.source:
        credible_domains = ['.edu', '.gov', '.org', 'arxiv.org', 'doi.org']
        if any(domain in resource.source for domain in credible_domains):
            score += 0.15
    
    # Scholarly metadata (Phase 6.5 integration)
    if resource.doi or resource.pmid or resource.arxiv_id:
        score += 0.15
    
    # Author metadata
    if resource.creator or resource.authors:
        score += 0.10
    
    return min(score, 1.0)
```

**Completeness Dimension:**
```python
def _compute_completeness(self, resource: Resource) -> float:
    """
    Compute completeness dimension score.
    
    Factors:
    - Required fields (30%): title, content, url
    - Important fields (30%): summary, tags, authors, publication_year
    - Scholarly fields (20%): doi, journal, affiliations, funding
    - Multi-modal content (20%): equations, tables, figures
    """
    score = 0.0
    
    # Required fields
    required = [resource.title, resource.content, resource.source]
    filled_required = sum(1 for field in required if field)
    score += 0.3 * (filled_required / 3)
    
    # Important fields
    important = [resource.summary, resource.subject, resource.creator, resource.publication_year]
    filled_important = sum(1 for field in important if field)
    score += 0.3 * (filled_important / 4)
    
    # Scholarly fields
    scholarly = [resource.doi, resource.journal, resource.affiliations, resource.funding_sources]
    filled_scholarly = sum(1 for field in scholarly if field)
    score += 0.2 * (filled_scholarly / 4)
    
    # Multi-modal content
    multimodal_score = (
        (1 if resource.has_equations else 0) +
        (1 if resource.has_tables else 0) +
        (1 if resource.has_figures else 0)
    ) / 3
    score += 0.2 * multimodal_score
    
    return score
```

**Consistency Dimension:**
```python
def _compute_consistency(self, resource: Resource) -> float:
    """
    Compute consistency dimension score.
    
    Factors:
    - Title-content alignment (15%): Keyword overlap
    - Summary-content alignment (15%): Compression ratio
    
    Baseline: 0.7 (optimistic - assume consistent unless proven otherwise)
    """
    score = 0.7  # Optimistic baseline
    
    # Title-content alignment
    if resource.title and resource.content:
        title_words = set(resource.title.lower().split())
        content_words = set(resource.content.lower().split()[:500])
        overlap = len(title_words & content_words) / len(title_words) if title_words else 0
        score += 0.15 * overlap
    
    # Summary-content alignment
    if resource.summary and resource.content:
        compression_ratio = len(resource.summary.split()) / len(resource.content.split())
        if 0.05 <= compression_ratio <= 0.15:  # Good summary length
            score += 0.15
    
    return min(score, 1.0)
```

**Timeliness Dimension:**
```python
def _compute_timeliness(self, resource: Resource) -> float:
    """
    Compute timeliness dimension score.
    
    Factors:
    - Publication recency: Decay function (20 year half-life)
    - Ingestion recency (10%): Bonus for recently ingested
    
    Baseline: 0.5 (neutral for undated content)
    """
    score = 0.5  # Neutral for undated content
    
    if resource.publication_year:
        current_year = datetime.now().year
        age_years = current_year - resource.publication_year
        
        if age_years <= 0:
            recency_score = 1.0
        else:
            # Decay function: 20 year half-life
            recency_score = max(0.0, 1.0 - (age_years / 20))
        
        score = recency_score
    
    # Ingestion recency bonus
    if resource.created_at:
        days_since_ingestion = (datetime.utcnow() - resource.created_at).days
        if days_since_ingestion <= 30:
            score += 0.1
    
    return min(score, 1.0)
```

**Relevance Dimension:**
```python
def _compute_relevance(self, resource: Resource) -> float:
    """
    Compute relevance dimension score.
    
    Factors:
    - Classification confidence (20%): Phase 8.5 ML classification
    - Citation count (30%): Logarithmic scaling
    
    Baseline: 0.5 (neutral)
    """
    score = 0.5  # Neutral baseline
    
    # Classification confidence (Phase 8.5 integration)
    if resource.taxonomy_classifications:
        avg_confidence = sum(tc.confidence for tc in resource.taxonomy_classifications) / len(resource.taxonomy_classifications)
        score += 0.2 * avg_confidence
    
    # Citation count (Phase 6 integration)
    if resource.citations_inbound:
        citation_count = len(resource.citations_inbound)
        citation_score = min(0.3, math.log10(citation_count + 1) / 10)
        score += citation_score
    
    return min(score, 1.0)
```

#### Outlier Detection with Isolation Forest

The quality service uses Isolation Forest for anomaly detection:

```python
def detect_quality_outliers(self, batch_size: int = 1000) -> int:
    """
    Detect quality outliers using Isolation Forest.
    
    Algorithm:
    1. Query resources with quality scores (batch)
    2. Require minimum 10 resources for statistical validity
    3. Build feature matrix from quality dimensions
    4. Train Isolation Forest (contamination=0.1, n_estimators=100)
    5. Predict anomaly scores
    6. Identify outliers (prediction == -1)
    7. Update resources with outlier flags
    
    Performance: <30 seconds for 1000 resources
    """
    from sklearn.ensemble import IsolationForest
    import numpy as np
    
    # Query resources with quality scores
    resources = (
        self.db.query(Resource)
        .filter(Resource.quality_overall.isnot(None))
        .limit(batch_size)
        .all()
    )
    
    if len(resources) < 10:
        raise ValueError("Insufficient resources for outlier detection (minimum 10)")
    
    # Build feature matrix
    features = []
    for resource in resources:
        feature_vector = [
            resource.quality_accuracy or 0.5,
            resource.quality_completeness or 0.5,
            resource.quality_consistency or 0.5,
            resource.quality_timeliness or 0.5,
            resource.quality_relevance or 0.5
        ]
        
        # Add summary quality dimensions if available
        if resource.summary_coherence:
            feature_vector.extend([
                resource.summary_coherence,
                resource.summary_consistency,
                resource.summary_fluency,
                resource.summary_relevance
            ])
        
        features.append(feature_vector)
    
    X = np.array(features)
    
    # Train Isolation Forest
    iso_forest = IsolationForest(
        contamination=0.1,  # Expect 10% outliers
        n_estimators=100,
        random_state=42
    )
    predictions = iso_forest.fit_predict(X)
    anomaly_scores = iso_forest.score_samples(X)
    
    # Update resources
    outlier_count = 0
    for i, resource in enumerate(resources):
        if predictions[i] == -1:  # Outlier detected
            resource.is_quality_outlier = True
            resource.outlier_score = float(anomaly_scores[i])
            resource.outlier_reasons = json.dumps(self._identify_outlier_reasons(resource))
            resource.needs_quality_review = True
            outlier_count += 1
    
    self.db.commit()
    return outlier_count
```

**Outlier Reason Identification:**
```python
def _identify_outlier_reasons(self, resource: Resource) -> List[str]:
    """
    Identify which dimensions are causing outlier status.
    
    Heuristic: Dimensions with scores <0.3 are unusual
    """
    reasons = []
    
    if resource.quality_accuracy and resource.quality_accuracy < 0.3:
        reasons.append("low_accuracy")
    if resource.quality_completeness and resource.quality_completeness < 0.3:
        reasons.append("low_completeness")
    if resource.quality_consistency and resource.quality_consistency < 0.3:
        reasons.append("low_consistency")
    if resource.quality_timeliness and resource.quality_timeliness < 0.3:
        reasons.append("low_timeliness")
    if resource.quality_relevance and resource.quality_relevance < 0.3:
        reasons.append("low_relevance")
    
    # Check summary quality dimensions
    if resource.summary_coherence and resource.summary_coherence < 0.3:
        reasons.append("low_summary_coherence")
    if resource.summary_consistency and resource.summary_consistency < 0.3:
        reasons.append("low_summary_consistency")
    if resource.summary_fluency and resource.summary_fluency < 0.3:
        reasons.append("low_summary_fluency")
    if resource.summary_relevance and resource.summary_relevance < 0.3:
        reasons.append("low_summary_relevance")
    
    return reasons
```

#### Quality Degradation Monitoring

Monitor quality changes over time to detect content issues:

```python
def monitor_quality_degradation(self, time_window_days: int = 30) -> List[Dict]:
    """
    Detect quality degradation by comparing historical scores.
    
    Algorithm:
    1. Compute cutoff date (now - time_window_days)
    2. Query resources with old quality scores
    3. Recompute quality for each resource
    4. Compare old vs new scores
    5. Flag resources with >20% degradation
    
    Use Cases:
    - Broken links (accuracy drops)
    - Outdated content (timeliness drops)
    - Metadata corruption (completeness drops)
    """
    from datetime import timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
    
    # Query resources with old quality scores
    resources = (
        self.db.query(Resource)
        .filter(Resource.quality_last_computed < cutoff_date)
        .filter(Resource.quality_overall.isnot(None))
        .all()
    )
    
    degraded_resources = []
    
    for resource in resources:
        old_quality = resource.quality_overall
        
        # Recompute quality
        new_scores = self.compute_quality(resource.id)
        new_quality = new_scores["overall"]
        
        # Check for degradation (>20% drop)
        if old_quality - new_quality > 0.2:
            degradation_pct = ((old_quality - new_quality) / old_quality) * 100
            
            degraded_resources.append({
                "resource_id": str(resource.id),
                "title": resource.title,
                "old_quality": old_quality,
                "new_quality": new_quality,
                "degradation_pct": degradation_pct
            })
            
            # Flag for review
            resource.needs_quality_review = True
    
    self.db.commit()
    return degraded_resources
```

#### Summarization Evaluator Service

The `SummarizationEvaluator` class evaluates summary quality using state-of-the-art metrics:

```python
class SummarizationEvaluator:
    """
    Summary quality evaluation using G-Eval, FineSurE, and BERTScore.
    
    Metrics:
    - G-Eval: LLM-based evaluation (coherence, consistency, fluency, relevance)
    - FineSurE: Completeness and conciseness
    - BERTScore: Semantic similarity
    """
    
    def __init__(self, db: Session, openai_api_key: Optional[str] = None):
        self.db = db
        self.openai_api_key = openai_api_key
        if openai_api_key:
            import openai
            openai.api_key = openai_api_key
```

**G-Eval Metrics (GPT-4 based):**
```python
def g_eval_coherence(self, summary: str) -> float:
    """
    Evaluate summary coherence using GPT-4.
    
    Prompt: Rate logical flow and structure on 1-5 scale
    Normalization: (rating - 1) / 4 → 0.0-1.0 range
    Fallback: 0.7 if API unavailable
    """
    if not self.openai_api_key:
        return 0.7  # Fallback score
    
    prompt = f"""You will be given a summary. Your task is to rate the summary on coherence.

Evaluation Criteria:
Coherence (1-5) - the collective quality of all sentences. The summary should be 
well-structured and well-organized. The summary should not just be a heap of related 
information, but should build from sentence to sentence to a coherent body of 
information about a topic.

Evaluation Steps:
1. Read the summary carefully.
2. Rate the summary for coherence on a scale of 1 to 5.

Summary:
{summary}

Provide only the numeric rating (1-5):"""
    
    try:
        import openai
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        rating = float(response.choices[0].message.content.strip())
        return (rating - 1) / 4  # Normalize to 0.0-1.0
    except Exception as e:
        logger.error(f"G-Eval coherence error: {e}")
        return 0.7  # Fallback
```

**FineSurE Metrics:**
```python
def finesure_completeness(self, summary: str, reference: str) -> float:
    """
    Measure coverage of key information.
    
    Algorithm:
    1. Extract words from reference and summary
    2. Remove stopwords
    3. Compute overlap ratio
    4. Expect 15% coverage for good summaries
    """
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for'}
    
    summary_words = set(summary.lower().split()) - stopwords
    reference_words = set(reference.lower().split()) - stopwords
    
    if not reference_words:
        return 0.5
    
    overlap = len(summary_words & reference_words)
    expected_coverage = len(reference_words) * 0.15
    
    return min(1.0, overlap / expected_coverage)

def finesure_conciseness(self, summary: str, reference: str) -> float:
    """
    Measure information density.
    
    Optimal compression ratio: 5-15% of original length
    """
    compression_ratio = len(summary.split()) / len(reference.split())
    
    if 0.05 <= compression_ratio <= 0.15:
        return 1.0
    elif compression_ratio < 0.05:
        return compression_ratio / 0.05  # Too short
    else:
        return max(0.0, 1.0 - (compression_ratio - 0.15) / 0.35)  # Too long
```

**BERTScore Metric:**
```python
def bertscore_f1(self, summary: str, reference: str) -> float:
    """
    Compute BERTScore F1 for semantic similarity.
    
    Model: microsoft/deberta-xlarge-mnli
    Fallback: 0.5 on error
    """
    try:
        from bert_score import score
        
        P, R, F1 = score(
            [summary],
            [reference],
            lang="en",
            model_type="microsoft/deberta-xlarge-mnli"
        )
        
        return float(F1[0])
    except Exception as e:
        logger.error(f"BERTScore error: {e}")
        return 0.5  # Fallback
```

**Composite Evaluation:**
```python
def evaluate_summary(
    self,
    resource_id: str,
    use_g_eval: bool = False
) -> Dict[str, float]:
    """
    Comprehensive summary evaluation.
    
    Metrics:
    - G-Eval (optional): coherence, consistency, fluency, relevance
    - FineSurE: completeness, conciseness
    - BERTScore: F1 score
    
    Composite score weights:
    - coherence: 20%
    - consistency: 20%
    - fluency: 15%
    - relevance: 15%
    - completeness: 15%
    - conciseness: 5%
    - bertscore: 10%
    
    Performance:
    - Without G-Eval: <2 seconds
    - With G-Eval: <10 seconds (OpenAI API latency)
    """
    resource = self.db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource or not resource.summary:
        raise ValueError("Resource has no summary to evaluate")
    
    summary = resource.summary
    reference = resource.content or resource.title
    
    # G-Eval metrics (optional)
    if use_g_eval and self.openai_api_key:
        coherence = self.g_eval_coherence(summary)
        consistency = self.g_eval_consistency(summary, reference)
        fluency = self.g_eval_fluency(summary)
        relevance = self.g_eval_relevance(summary, reference)
    else:
        # Fallback scores
        coherence = consistency = fluency = relevance = 0.7
    
    # FineSurE metrics
    completeness = self.finesure_completeness(summary, reference)
    conciseness = self.finesure_conciseness(summary, reference)
    
    # BERTScore
    bertscore = self.bertscore_f1(summary, reference)
    
    # Composite score
    overall = (
        0.20 * coherence +
        0.20 * consistency +
        0.15 * fluency +
        0.15 * relevance +
        0.15 * completeness +
        0.05 * conciseness +
        0.10 * bertscore
    )
    
    # Update resource
    resource.summary_coherence = coherence
    resource.summary_consistency = consistency
    resource.summary_fluency = fluency
    resource.summary_relevance = relevance
    resource.summary_completeness = completeness
    resource.summary_conciseness = conciseness
    resource.summary_bertscore = bertscore
    resource.summary_quality_overall = overall
    
    self.db.commit()
    
    return {
        "coherence": coherence,
        "consistency": consistency,
        "fluency": fluency,
        "relevance": relevance,
        "completeness": completeness,
        "conciseness": conciseness,
        "bertscore": bertscore,
        "overall": overall
    }
```

#### Integration with Existing Services

**Resource Ingestion Integration:**
```python
# In resource_service.py
async def process_ingestion(resource_id: str, background_tasks: BackgroundTasks):
    """Process resource ingestion with quality assessment."""
    # ... existing ingestion steps ...
    
    # Compute quality after content extraction
    background_tasks.add_task(
        quality_service.compute_quality,
        resource_id
    )
```

**Recommendation Service Integration:**
```python
# In recommendation_service.py
def generate_recommendations(
    self,
    user_id: str,
    min_quality: float = 0.5,
    exclude_outliers: bool = True
) -> List[Resource]:
    """Generate recommendations with quality filtering."""
    # Build user profile
    profile_vector = self._generate_user_profile_vector(
        user_id,
        min_quality=min_quality,
        exclude_outliers=exclude_outliers
    )
    
    # Score candidates with quality boost
    candidates = self._score_candidates(
        profile_vector,
        quality_boost=1.2  # 20% boost for high-quality resources
    )
    
    return candidates
```

#### Extension Points for Custom Quality Dimensions

The quality service is designed for extensibility:

**Adding New Quality Dimensions:**
```python
# 1. Add database column
# In migration file:
op.add_column('resources', sa.Column('quality_custom_dimension', sa.Float(), nullable=True))

# 2. Add computation method
def _compute_custom_dimension(self, resource: Resource) -> float:
    """Compute custom quality dimension."""
    # Your custom logic here
    return score

# 3. Update compute_quality method
def compute_quality(self, resource_id: str, weights: Optional[Dict] = None):
    # ... existing code ...
    custom_score = self._compute_custom_dimension(resource)
    resource.quality_custom_dimension = custom_score
    
    # Update overall score calculation
    overall = (
        weights["accuracy"] * accuracy +
        weights["completeness"] * completeness +
        # ... other dimensions ...
        weights["custom_dimension"] * custom_score
    )
```

**Custom Outlier Detection Algorithms:**
```python
# Alternative to Isolation Forest
def detect_outliers_zscore(self, threshold: float = 3.0) -> int:
    """Detect outliers using Z-score method."""
    import numpy as np
    from scipy import stats
    
    resources = self.db.query(Resource).filter(Resource.quality_overall.isnot(None)).all()
    scores = [r.quality_overall for r in resources]
    
    z_scores = np.abs(stats.zscore(scores))
    outliers = np.where(z_scores > threshold)[0]
    
    for idx in outliers:
        resources[idx].is_quality_outlier = True
        resources[idx].needs_quality_review = True
    
    self.db.commit()
    return len(outliers)
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
