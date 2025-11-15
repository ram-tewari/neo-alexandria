# Design Document: Phase 7 Collection Management

## Overview

Phase 7 introduces a comprehensive collection management system that enables users to organize resources into curated groups with hierarchical structure, collaborative sharing, and intelligent recommendations. The design follows Neo Alexandria's established patterns for database models, service layers, and API endpoints while introducing new capabilities for aggregate embeddings and collection-based discovery.

### Key Design Principles

1. **Consistency with Existing Patterns**: Follow the Resource/Citation model patterns for ownership, relationships, and service architecture
2. **Performance First**: Support 1000+ resources per collection with sub-second operations through indexing and batch processing
3. **Semantic Intelligence**: Leverage aggregate embeddings for collection-level recommendations and similarity search
4. **Hierarchical Flexibility**: Enable nested collections without circular dependencies or orphaned data
5. **Access Control**: Implement granular visibility controls (private/shared/public) with owner-based permissions

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                      │
│  /collections/* endpoints - CRUD, membership, recommendations │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Service Layer                              │
│  CollectionService: Business logic, validation, orchestration│
│  EmbeddingService: Aggregate embedding computation           │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  Database Layer (SQLAlchemy)                 │
│  Collection, CollectionResource (association table)          │
│  Relationships: User→Collection, Collection→Resource         │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow

**Collection Creation Flow**:
1. User submits POST /collections with name, description, visibility
2. CollectionService validates input and checks authorization
3. Create Collection record with owner_id, default visibility=private
4. Return collection metadata to client

**Resource Membership Flow**:
1. User submits POST /collections/{id}/resources with resource_ids[]
2. CollectionService validates ownership and resource existence
3. Batch insert CollectionResource associations
4. Trigger aggregate embedding recomputation
5. Return updated collection with resource count

**Recommendation Flow**:
1. User requests GET /collections/{id}/recommendations
2. CollectionService retrieves collection aggregate embedding
3. Query resources/collections by cosine similarity (exclude self/members)
4. Return top N results with similarity scores

## Components and Interfaces

### Database Models

#### Collection Model

```python
class Collection(Base):
    """User-curated collection of resources with hierarchical support."""
    
    __tablename__ = "collections"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Core metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Ownership and access control
    owner_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    visibility: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="private",
        index=True
    )  # 'private' | 'shared' | 'public'
    
    # Hierarchical structure
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Semantic representation
    embedding: Mapped[List[float] | None] = mapped_column(
        JSON,
        nullable=True,
        default=None
    )
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    # Relationships
    parent: Mapped["Collection"] = relationship(
        "Collection",
        remote_side=[id],
        back_populates="subcollections"
    )
    subcollections: Mapped[List["Collection"]] = relationship(
        "Collection",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    resources: Mapped[List["Resource"]] = relationship(
        "Resource",
        secondary="collection_resources",
        back_populates="collections"
    )
```

#### CollectionResource Association Table

```python
class CollectionResource(Base):
    """Many-to-many association between collections and resources."""
    
    __tablename__ = "collection_resources"
    
    collection_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("collections.id", ondelete="CASCADE"),
        primary_key=True
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("resources.id", ondelete="CASCADE"),
        primary_key=True
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )
    
    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_collection_resources_collection', 'collection_id'),
        Index('idx_collection_resources_resource', 'resource_id'),
    )
```

### Service Layer

#### CollectionService

**Responsibilities**:
- CRUD operations with authorization checks
- Resource membership management (batch operations)
- Aggregate embedding computation and caching
- Hierarchical validation (prevent cycles)
- Recommendation generation via embedding similarity

**Key Methods**:

```python
class CollectionService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService(db)
    
    def create_collection(
        self,
        owner_id: str,
        name: str,
        description: str | None = None,
        visibility: str = "private",
        parent_id: str | None = None
    ) -> Collection:
        """
        Create new collection with validation.
        
        Validates:
        - Name length (1-255 chars)
        - Visibility value (private/shared/public)
        - Parent exists and owner matches
        - No circular reference in hierarchy
        """
    
    def update_collection(
        self,
        collection_id: str,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Collection:
        """
        Update collection metadata.
        
        Authorization: Only owner can update
        Validates: Same as create_collection
        Triggers: Embedding recompute if parent changes
        """
    
    def delete_collection(
        self,
        collection_id: str,
        user_id: str
    ) -> None:
        """
        Delete collection and cascade to subcollections.
        
        Authorization: Only owner can delete
        Cascade: Deletes all subcollections recursively
        Cleanup: Removes all CollectionResource associations
        """
    
    def add_resources(
        self,
        collection_id: str,
        user_id: str,
        resource_ids: List[str]
    ) -> Collection:
        """
        Add resources to collection (batch operation).
        
        Authorization: Only owner can modify
        Validation: All resource_ids must exist
        Batch: Insert up to 100 associations per transaction
        Trigger: Recompute aggregate embedding
        """
    
    def remove_resources(
        self,
        collection_id: str,
        user_id: str,
        resource_ids: List[str]
    ) -> Collection:
        """
        Remove resources from collection (batch operation).
        
        Authorization: Only owner can modify
        Batch: Delete up to 100 associations per transaction
        Trigger: Recompute aggregate embedding
        """
    
    def get_collection(
        self,
        collection_id: str,
        user_id: str | None = None
    ) -> Collection:
        """
        Retrieve collection with access control.
        
        Access Rules:
        - Private: Only owner
        - Shared: Owner + explicit permissions (future)
        - Public: All authenticated users
        """
    
    def list_collections(
        self,
        user_id: str | None = None,
        owner_filter: str | None = None,
        visibility_filter: str | None = None,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Collection], int]:
        """
        List collections with filtering and pagination.
        
        Filters:
        - Owner: Collections owned by specific user
        - Visibility: Filter by private/shared/public
        - Access: Only return collections user can access
        """
    
    def recompute_embedding(
        self,
        collection_id: str
    ) -> List[float] | None:
        """
        Compute aggregate embedding from member resources.
        
        Algorithm:
        1. Query all member resources with embeddings
        2. If no embeddings, return None
        3. Compute mean vector across all dimensions
        4. Normalize to unit length
        5. Store in collection.embedding
        
        Performance: O(n*d) where n=resources, d=embedding_dim
        Target: <1s for 1000 resources
        """
    
    def get_recommendations(
        self,
        collection_id: str,
        user_id: str,
        limit: int = 10,
        include_resources: bool = True,
        include_collections: bool = True
    ) -> Dict[str, List[Dict]]:
        """
        Get similar resources and collections.
        
        Returns:
        {
            "resources": [{"id": ..., "title": ..., "similarity": 0.95}],
            "collections": [{"id": ..., "name": ..., "similarity": 0.87}]
        }
        
        Algorithm:
        1. Retrieve collection aggregate embedding
        2. If include_resources: Query resources by cosine similarity
           - Exclude resources already in collection
           - Order by similarity DESC
           - Limit to N results
        3. If include_collections: Query collections by cosine similarity
           - Exclude source collection
           - Filter by visibility (user access)
           - Order by similarity DESC
           - Limit to N results
        """
    
    def validate_hierarchy(
        self,
        collection_id: str,
        new_parent_id: str
    ) -> bool:
        """
        Prevent circular references in hierarchy.
        
        Algorithm:
        1. Start at new_parent_id
        2. Traverse up parent chain
        3. If collection_id encountered → cycle detected
        4. If None reached → valid hierarchy
        """
```

#### EmbeddingService Integration

**Aggregate Embedding Computation**:

```python
def compute_aggregate_embedding(
    resource_embeddings: List[List[float]]
) -> List[float]:
    """
    Compute mean embedding from resource embeddings.
    
    Args:
        resource_embeddings: List of embedding vectors
    
    Returns:
        Mean vector normalized to unit length
    
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
    
    # Normalize
    norm = np.linalg.norm(mean_vector)
    if norm > 0:
        mean_vector = mean_vector / norm
    
    return mean_vector.tolist()
```

**Cosine Similarity Search**:

```python
def find_similar_by_embedding(
    db: Session,
    target_embedding: List[float],
    model_class: Type[Base],
    exclude_ids: List[str] = None,
    limit: int = 10
) -> List[Tuple[Base, float]]:
    """
    Find similar entities by embedding cosine similarity.
    
    Args:
        db: Database session
        target_embedding: Query embedding vector
        model_class: Resource or Collection model
        exclude_ids: IDs to exclude from results
        limit: Maximum results
    
    Returns:
        List of (entity, similarity_score) tuples
    
    Algorithm:
    1. Query all entities with non-null embeddings
    2. Compute cosine similarity for each
    3. Sort by similarity DESC
    4. Return top N
    
    Note: For production, use vector database (pgvector, Pinecone)
    """
```

### API Endpoints

#### Collection CRUD

**POST /collections**
- Request: `{"name": str, "description": str?, "visibility": str?, "parent_id": str?}`
- Response: `Collection` schema
- Auth: Required (owner_id from token)
- Status: 201 Created, 400 Bad Request, 401 Unauthorized

**GET /collections/{id}**
- Response: `Collection` schema with resource summaries
- Auth: Required (visibility check)
- Status: 200 OK, 403 Forbidden, 404 Not Found

**PUT /collections/{id}**
- Request: `{"name": str?, "description": str?, "visibility": str?, "parent_id": str?}`
- Response: `Collection` schema
- Auth: Required (owner only)
- Status: 200 OK, 400 Bad Request, 403 Forbidden, 404 Not Found

**DELETE /collections/{id}**
- Response: `{"message": "Collection deleted"}`
- Auth: Required (owner only)
- Status: 204 No Content, 403 Forbidden, 404 Not Found

**GET /collections**
- Query Params: `owner_id`, `visibility`, `page`, `limit`
- Response: `{"items": [Collection], "total": int, "page": int, "limit": int}`
- Auth: Required (filtered by access)
- Status: 200 OK

#### Resource Membership

**POST /collections/{id}/resources**
- Request: `{"resource_ids": [str]}`
- Response: `Collection` schema with updated resource count
- Auth: Required (owner only)
- Status: 200 OK, 400 Bad Request, 403 Forbidden, 404 Not Found

**DELETE /collections/{id}/resources**
- Request: `{"resource_ids": [str]}`
- Response: `Collection` schema with updated resource count
- Auth: Required (owner only)
- Status: 200 OK, 403 Forbidden, 404 Not Found

#### Recommendations

**GET /collections/{id}/recommendations**
- Query Params: `limit`, `include_resources`, `include_collections`
- Response: `{"resources": [ResourceSummary], "collections": [CollectionSummary]}`
- Auth: Required (visibility check)
- Status: 200 OK, 403 Forbidden, 404 Not Found

**GET /collections/{id}/embedding**
- Response: `{"embedding": [float], "dimension": int}`
- Auth: Required (visibility check)
- Status: 200 OK, 403 Forbidden, 404 Not Found

## Data Models

### Pydantic Schemas

```python
# Request schemas
class CollectionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    visibility: Literal["private", "shared", "public"] = "private"
    parent_id: str | None = None

class CollectionUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    visibility: Literal["private", "shared", "public"] | None = None
    parent_id: str | None = None

class ResourceMembershipUpdate(BaseModel):
    resource_ids: List[str] = Field(..., min_items=1, max_items=100)

# Response schemas
class ResourceSummary(BaseModel):
    id: str
    title: str
    creator: str | None
    quality_score: float

class CollectionResponse(BaseModel):
    id: str
    name: str
    description: str | None
    owner_id: str
    visibility: str
    parent_id: str | None
    resource_count: int
    created_at: datetime
    updated_at: datetime
    resources: List[ResourceSummary] = []

class CollectionListResponse(BaseModel):
    items: List[CollectionResponse]
    total: int
    page: int
    limit: int

class RecommendationResponse(BaseModel):
    resources: List[Dict[str, Any]]  # {id, title, similarity}
    collections: List[Dict[str, Any]]  # {id, name, similarity}
```

## Error Handling

### Authorization Errors

- **403 Forbidden**: User attempts to access/modify collection without permission
- **401 Unauthorized**: No authentication token provided

### Validation Errors

- **400 Bad Request**: Invalid input (name too long, invalid visibility, circular hierarchy)
- **404 Not Found**: Collection or resource not found

### Business Logic Errors

- **409 Conflict**: Circular reference detected in hierarchy
- **422 Unprocessable Entity**: Resource already in collection (idempotent, return success)

### Error Response Format

```json
{
    "detail": "Human-readable error message",
    "error_code": "COLLECTION_NOT_FOUND",
    "field": "parent_id"  // Optional, for validation errors
}
```

## Testing Strategy

### Unit Tests

**Model Tests** (`test_collection_model.py`):
- Collection creation with all field combinations
- Relationship integrity (parent/subcollections, resources)
- Cascade deletion behavior
- UUID generation and uniqueness

**Service Tests** (`test_collection_service.py`):
- CRUD operations with authorization
- Resource membership batch operations
- Embedding computation accuracy
- Hierarchy validation (cycle detection)
- Recommendation algorithm correctness

**Embedding Tests** (`test_collection_embeddings.py`):
- Aggregate embedding computation
- Cosine similarity calculations
- Null embedding handling
- Performance with 1000 resources

### Integration Tests

**API Tests** (`test_phase7_collections.py`):
- Full CRUD workflow via API endpoints
- Access control enforcement (private/shared/public)
- Resource membership operations
- Recommendation endpoint responses
- Pagination and filtering
- Error responses for invalid inputs

**Performance Tests** (`test_collection_performance.py`):
- Collection with 1000 resources: retrieval <500ms
- Embedding computation: <1s for 1000 resources
- Batch resource add: <2s for 100 resources
- Recommendation query: <1s

### Test Data Fixtures

```python
@pytest.fixture
def sample_collection(db_session):
    """Create collection with 10 resources."""
    collection = Collection(
        name="Test Collection",
        owner_id="user123",
        visibility="private"
    )
    db_session.add(collection)
    
    resources = [create_resource(f"Resource {i}") for i in range(10)]
    collection.resources.extend(resources)
    
    db_session.commit()
    return collection

@pytest.fixture
def nested_collections(db_session):
    """Create 3-level hierarchy."""
    parent = Collection(name="Parent", owner_id="user123")
    child = Collection(name="Child", owner_id="user123", parent=parent)
    grandchild = Collection(name="Grandchild", owner_id="user123", parent=child)
    
    db_session.add_all([parent, child, grandchild])
    db_session.commit()
    
    return parent, child, grandchild
```

## Performance Optimizations

### Database Indexing

```sql
-- Owner and visibility for access control queries
CREATE INDEX idx_collections_owner ON collections(owner_id);
CREATE INDEX idx_collections_visibility ON collections(visibility);

-- Parent for hierarchical queries
CREATE INDEX idx_collections_parent ON collections(parent_id);

-- Composite index for membership queries
CREATE INDEX idx_collection_resources_lookup 
ON collection_resources(collection_id, resource_id);
```

### Query Optimization

1. **Eager Loading**: Use `joinedload` for resources when retrieving collections
2. **Batch Operations**: Insert/delete up to 100 associations per transaction
3. **Pagination**: Always limit query results (default 50, max 100)
4. **Embedding Cache**: Store computed embeddings, invalidate on membership change

### Scalability Considerations

**Current Design (Phase 7)**:
- In-memory cosine similarity (acceptable for <10k collections)
- JSON embedding storage (portable, sufficient for MVP)

**Future Enhancements (Phase 8+)**:
- PostgreSQL pgvector extension for native vector operations
- Approximate nearest neighbor (ANN) indexes (HNSW, IVFFlat)
- Embedding dimension reduction (PCA, UMAP) for faster search
- Distributed vector database (Pinecone, Weaviate) for >100k collections

## Integration Points

### Resource Service Integration

**Hook: Resource Deletion**
```python
# In resource_service.delete_resource()
def delete_resource(db: Session, resource_id: str) -> None:
    # ... existing deletion logic ...
    
    # Remove from all collections
    db.execute(
        delete(CollectionResource)
        .where(CollectionResource.resource_id == resource_id)
    )
    
    # Trigger embedding recompute for affected collections
    affected_collections = db.execute(
        select(Collection.id)
        .join(CollectionResource)
        .where(CollectionResource.resource_id == resource_id)
    ).scalars().all()
    
    for collection_id in affected_collections:
        collection_service.recompute_embedding(collection_id)
```

### Search Service Integration

**Filter by Collection**:
```python
# Add to search endpoint
@router.get("/search")
def search_resources(
    q: str,
    collection_id: str | None = None,
    ...
):
    query = build_search_query(q)
    
    if collection_id:
        query = query.join(CollectionResource).filter(
            CollectionResource.collection_id == collection_id
        )
    
    return execute_search(query)
```

### Recommendation Service Integration

**Collection-Based Recommendations**:
```python
# Enhance existing recommendation endpoint
@router.get("/resources/{id}/recommendations")
def get_resource_recommendations(
    resource_id: str,
    include_collection_context: bool = False
):
    recommendations = recommendation_service.get_similar_resources(resource_id)
    
    if include_collection_context:
        # Find collections containing this resource
        collections = collection_service.get_collections_for_resource(resource_id)
        
        # Add collection-based recommendations
        for collection in collections:
            collection_recs = collection_service.get_recommendations(collection.id)
            recommendations.extend(collection_recs["resources"])
    
    return deduplicate_and_rank(recommendations)
```

## Migration Strategy

### Database Migration

**Alembic Migration Script**:
```python
def upgrade():
    # Create collections table
    op.create_table(
        'collections',
        sa.Column('id', GUID(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.String(255), nullable=False),
        sa.Column('visibility', sa.String(20), nullable=False, server_default='private'),
        sa.Column('parent_id', GUID(), nullable=True),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.current_timestamp()),
        sa.ForeignKeyConstraint(['parent_id'], ['collections.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('idx_collections_owner', 'collections', ['owner_id'])
    op.create_index('idx_collections_visibility', 'collections', ['visibility'])
    op.create_index('idx_collections_parent', 'collections', ['parent_id'])
    
    # Create association table
    op.create_table(
        'collection_resources',
        sa.Column('collection_id', GUID(), primary_key=True),
        sa.Column('resource_id', GUID(), primary_key=True),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=func.current_timestamp()),
        sa.ForeignKeyConstraint(['collection_id'], ['collections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resource_id'], ['resources.id'], ondelete='CASCADE')
    )
    
    # Create composite index
    op.create_index('idx_collection_resources_lookup', 'collection_resources', 
                    ['collection_id', 'resource_id'])

def downgrade():
    op.drop_table('collection_resources')
    op.drop_table('collections')
```

### Backward Compatibility

- No breaking changes to existing APIs
- New endpoints under `/collections` namespace
- Optional collection filtering in existing search/recommendation endpoints

## Security Considerations

### Access Control

1. **Owner Verification**: All mutations require owner_id match
2. **Visibility Enforcement**: Read operations respect private/shared/public rules
3. **Input Validation**: Sanitize all user inputs (name, description)
4. **Rate Limiting**: Limit collection creation (10/hour per user)

### Data Privacy

1. **Private Collections**: Never expose in public listings or recommendations
2. **Shared Collections**: Implement explicit permission model (future)
3. **Audit Logging**: Track collection access and modifications

### SQL Injection Prevention

- Use parameterized queries (SQLAlchemy ORM)
- Validate UUIDs before database operations
- Escape user input in search queries

## Monitoring and Observability

### Metrics

- Collection creation rate (per user, per day)
- Average resources per collection
- Embedding computation time (p50, p95, p99)
- Recommendation query latency
- Collection deletion rate

### Logging

```python
logger.info(
    "Collection created",
    extra={
        "collection_id": collection.id,
        "owner_id": collection.owner_id,
        "resource_count": len(collection.resources),
        "visibility": collection.visibility
    }
)
```

### Alerts

- Embedding computation >2s (performance degradation)
- High collection deletion rate (potential data loss)
- Authorization failures >10/min (potential attack)

## Future Enhancements

### Phase 8+ Considerations

1. **Collaborative Editing**: Multi-user permissions for shared collections
2. **Collection Templates**: Pre-defined structures for common use cases
3. **Smart Collections**: Auto-populate based on rules (tags, quality, date)
4. **Collection Analytics**: View counts, popular resources, engagement metrics
5. **Export/Import**: Share collections across Neo Alexandria instances
6. **Collection Versioning**: Track changes over time, restore previous states
7. **Advanced Recommendations**: Incorporate user behavior, temporal patterns
8. **Vector Database**: Migrate to pgvector or dedicated vector DB for scale
