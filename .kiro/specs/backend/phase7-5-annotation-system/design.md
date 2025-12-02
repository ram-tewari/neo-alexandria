# Design Document - Phase 7.5: Annotation & Active Reading System

## Overview

Phase 7.5 introduces a comprehensive annotation system that transforms Neo Alexandria from a passive content repository into an active reading and knowledge-building platform. The system enables researchers to highlight text passages, add notes, organize annotations with tags, search semantically across their personal knowledge base, and export research notes in multiple formats.

### Core Capabilities

- **Precise Text Highlighting**: Character-offset-based text selection with context preservation
- **Note-Taking**: Rich annotation notes with automatic semantic embedding generation
- **Organization**: Tag-based categorization and color-coding for visual organization
- **Search**: Full-text and semantic search across all annotations
- **Export**: Markdown and JSON export for integration with external tools
- **Integration**: Deep integration with collections, search, and recommendation systems
- **Scalability**: Support for 10,000+ annotations per resource with sub-100ms search

### Design Principles

1. **Precision**: Use character offsets for exact text positioning, not fragile XPath or DOM selectors
2. **Performance**: Async embedding generation, indexed queries, batch operations
3. **Privacy**: Annotations are private by default with explicit sharing controls
4. **Integration**: Annotations enhance existing features (search, recommendations, collections)
5. **Extensibility**: JSON fields for tags and collection associations support future features

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                      │
│  /annotations/* endpoints - CRUD, search, export             │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│              Service Layer (Business Logic)                  │
│  AnnotationService - Core CRUD, search, export               │
│  Integration: SearchService, RecommendationService           │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                   Data Layer (SQLAlchemy)                    │
│  Annotation Model - Text offsets, notes, embeddings          │
│  Relationships: Resource (FK), User (FK), Collections (JSON) │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

**Annotation Creation Flow**:
```
User selects text → API receives offsets + text → Service validates →
Extract context → Create Annotation → Enqueue embedding generation →
Return annotation → Background: Generate embedding → Update annotation
```

**Search Flow**:
```
User enters query → API receives search request →
Full-text: LIKE query on notes/highlighted_text →
Semantic: Generate query embedding → Compute similarities →
Return ranked results
```


## Components and Interfaces

### 1. Annotation Model (Database Schema)

**Location**: `backend/app/database/models.py`

**Schema Design**:

```python
class Annotation(Base):
    __tablename__ = "annotations"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    resource_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False)
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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    resource: Mapped["Resource"] = relationship("Resource", back_populates="annotations")
```

**Indexes**:
- `idx_annotations_resource`: ON (resource_id) - Fast resource annotation retrieval
- `idx_annotations_user`: ON (user_id) - Fast user annotation retrieval
- `idx_annotations_user_resource`: ON (user_id, resource_id) - Composite for filtering
- `idx_annotations_created`: ON (created_at) - Sorting by recency

**Constraints**:
- CHECK: `start_offset < end_offset` - Logical ordering
- CHECK: `start_offset >= 0 AND end_offset >= 0` - Non-negative offsets
- FK CASCADE: Delete annotations when resource deleted

**Design Rationale**:
- **Character offsets**: More reliable than DOM-based selection, works with any text format
- **JSON for arrays**: Flexible storage for tags and collection IDs without additional tables
- **Context fields**: 50 chars before/after for preview without re-parsing full content
- **Embedding field**: Enables semantic search without external vector database (Phase 7.5 scope)


### 2. AnnotationService (Business Logic)

**Location**: `backend/app/services/annotation_service.py`

**Class Structure**:

```python
class AnnotationService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService(db)
    
    # CRUD Operations
    def create_annotation(...) -> Annotation
    def update_annotation(...) -> Annotation
    def delete_annotation(...) -> bool
    def get_annotation_by_id(...) -> Annotation | None
    
    # Retrieval and Filtering
    def get_annotations_for_resource(...) -> List[Annotation]
    def get_annotations_for_user(...) -> List[Annotation]
    
    # Search
    def search_annotations_fulltext(...) -> List[Annotation]
    def search_annotations_semantic(...) -> List[tuple[Annotation, float]]
    def search_annotations_by_tags(...) -> List[Annotation]
    
    # Export
    def export_annotations_markdown(...) -> str
    def export_annotations_json(...) -> List[Dict]
    
    # Helper Methods
    def _extract_context(...) -> str
    def _generate_annotation_embedding(...) -> None
    def _cosine_similarity(...) -> float
```

**Key Algorithms**:

**Create Annotation**:
1. Validate resource exists and user has access
2. Validate offsets: `start < end`, both non-negative
3. Extract context: 50 chars before/after from resource content
4. Create Annotation record with uuid4() ID
5. Commit to database
6. If note provided: Enqueue background embedding generation
7. Return created annotation

**Full-Text Search**:
1. Build query with LIKE pattern: `%{query}%`
2. Search both `note` and `highlighted_text` fields
3. Filter by user_id (privacy)
4. Apply limit
5. Return results (target: <100ms for 10,000 annotations)

**Semantic Search**:
1. Generate embedding for query text
2. Retrieve all user annotations with embeddings
3. Compute cosine similarity for each annotation
4. Sort by similarity descending
5. Return top N with scores (target: <500ms)

**Export Markdown**:
1. Retrieve annotations (filtered by resource if specified)
2. Group by resource_id
3. For each resource:
   - Add resource title header
   - For each annotation:
     - Format as blockquote (highlighted text)
     - Add note, tags, timestamp
     - Add separator
4. Concatenate all sections
5. Return markdown string (target: <2s for 1,000 annotations)

**Performance Optimizations**:
- Embedding generation is async (doesn't block creation)
- Use composite indexes for filtering
- Eager load relationships to prevent N+1 queries
- Batch operations for export
- In-memory similarity computation for <1,000 annotations


### 3. Annotation Router (API Endpoints)

**Location**: `backend/app/routers/annotations.py`

**Endpoint Design**:

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/resources/{resource_id}/annotations` | Create annotation | Yes |
| GET | `/resources/{resource_id}/annotations` | List resource annotations | Yes |
| GET | `/annotations` | List user annotations | Yes |
| GET | `/annotations/{annotation_id}` | Get single annotation | Yes |
| PUT | `/annotations/{annotation_id}` | Update annotation | Yes |
| DELETE | `/annotations/{annotation_id}` | Delete annotation | Yes |
| GET | `/annotations/search/fulltext` | Full-text search | Yes |
| GET | `/annotations/search/semantic` | Semantic search | Yes |
| GET | `/annotations/search/tags` | Tag-based search | Yes |
| GET | `/annotations/export/markdown` | Export to Markdown | Yes |
| GET | `/annotations/export/json` | Export to JSON | Yes |

**Request/Response Schemas**:

```python
# Pydantic schemas in app/schemas/annotation.py

class AnnotationCreate(BaseModel):
    start_offset: int = Field(..., ge=0)
    end_offset: int = Field(..., ge=0)
    highlighted_text: str
    note: Optional[str] = None
    tags: Optional[List[str]] = None
    color: Optional[str] = "#FFFF00"
    collection_ids: Optional[List[str]] = None

class AnnotationUpdate(BaseModel):
    note: Optional[str] = None
    tags: Optional[List[str]] = None
    color: Optional[str] = None
    is_shared: Optional[bool] = None

class AnnotationResponse(BaseModel):
    id: str
    resource_id: str
    user_id: str
    start_offset: int
    end_offset: int
    highlighted_text: str
    note: Optional[str]
    tags: Optional[List[str]]
    color: str
    context_before: Optional[str]
    context_after: Optional[str]
    is_shared: bool
    created_at: datetime
    updated_at: datetime
    resource_title: Optional[str] = None
    
    class Config:
        from_attributes = True
```

**Authentication & Authorization**:
- All endpoints require authentication via `get_current_user_id()` dependency
- Ownership verification: Users can only modify/delete their own annotations
- Access control: Users can view their own annotations or shared annotations
- Resource access: Verify user has access to resource before creating annotations

**Error Handling**:
- 400 Bad Request: Invalid offsets, validation errors
- 403 Forbidden: Attempting to modify another user's annotation
- 404 Not Found: Annotation or resource not found
- 500 Internal Server Error: Database errors, embedding generation failures


### 4. Integration Points

#### 4.1 Resource Service Integration

**Location**: `backend/app/services/resource_service.py`

**Hook: Resource Deletion**
```python
def delete_resource(resource_id: str, user_id: str):
    # NEW Phase 7.5: Cascade delete annotations
    db.query(Annotation).filter(Annotation.resource_id == resource_id).delete()
    db.commit()
    
    # Continue with existing resource deletion logic
    ...
```

**Rationale**: Prevent orphaned annotations when resources are deleted. Database CASCADE constraint handles this automatically, but explicit service-level deletion provides better logging and control.

#### 4.2 Search Service Integration

**Location**: `backend/app/services/search_service.py`

**New Method: Enhanced Search with Annotations**
```python
def search_with_annotations(
    self,
    query: str,
    user_id: str,
    include_annotations: bool = True
) -> Dict:
    # Standard resource search
    resources = self.search(query)
    
    if not include_annotations:
        return {"resources": resources, "annotations": []}
    
    # Search user's annotations
    annotation_service = AnnotationService(self.db)
    annotations = annotation_service.search_annotations_fulltext(user_id, query)
    
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
```

**Use Case**: When searching for "machine learning", return both resources about ML and resources where the user has annotated ML-related passages.

#### 4.3 Recommendation Service Integration

**Location**: `backend/app/services/recommendation_service.py`

**New Method: Annotation-Based Recommendations**
```python
def recommend_based_on_annotations(
    self,
    user_id: str,
    limit: int = 10
) -> List[Resource]:
    annotation_service = AnnotationService(self.db)
    
    # Get recent annotations (last 100)
    annotations = annotation_service.get_annotations_for_user(
        user_id=user_id,
        limit=100,
        sort_by="recent"
    )
    
    if not annotations:
        return []
    
    # Extract annotated resource IDs (to exclude)
    annotated_resource_ids = list(set(ann.resource_id for ann in annotations))
    
    # Aggregate annotation content
    all_notes = " ".join([ann.note for ann in annotations if ann.note])
    all_tags = []
    for ann in annotations:
        if ann.tags:
            all_tags.extend(json.loads(ann.tags))
    
    # Get tag frequencies
    tag_counts = Counter(all_tags)
    top_tags = [tag for tag, _ in tag_counts.most_common(5)]
    
    # Generate embedding from notes
    if all_notes:
        notes_embedding = self.embedding_service.generate_embedding(all_notes)
        similar_resources = self.find_similar_by_embedding(
            notes_embedding,
            exclude_ids=annotated_resource_ids,
            limit=limit * 2
        )
    else:
        similar_resources = []
    
    # Also search by top tags
    tag_resources = []
    if top_tags:
        tag_resources = self.db.query(Resource).filter(
            and_(
                Resource.id.notin_(annotated_resource_ids),
                or_(*[Resource.subject.contains(tag) for tag in top_tags])
            )
        ).limit(limit).all()
    
    # Merge and deduplicate
    combined = similar_resources + tag_resources
    seen = set()
    unique = []
    for res in combined:
        if res.id not in seen:
            seen.add(res.id)
            unique.append(res)
    
    return unique[:limit]
```

**Use Case**: Recommend papers based on what the user actively annotates, not just what they ingest. This captures genuine research interest.

#### 4.4 Collection Service Integration

**Location**: `backend/app/services/collection_service.py`

**Enhancement: Include Annotation Counts**
```python
def get_collection_with_annotations(collection_id: str, user_id: str) -> Dict:
    collection = self.get_collection_by_id(collection_id)
    
    # Count annotations associated with this collection
    annotation_count = db.query(Annotation).filter(
        and_(
            Annotation.collection_ids.contains(collection_id),
            Annotation.user_id == user_id
        )
    ).count()
    
    return {
        **collection.to_dict(),
        "annotation_count": annotation_count
    }
```

**Use Case**: Show users how actively they've engaged with resources in each collection.


## Data Models

### Annotation Entity Relationship

```
┌─────────────┐         ┌──────────────┐         ┌──────────┐
│   User      │         │  Annotation  │         │ Resource │
│             │1      N │              │N      1 │          │
│ - user_id   ├────────►│ - id         ├────────►│ - id     │
│             │         │ - user_id    │         │ - title  │
└─────────────┘         │ - resource_id│         │ - content│
                        │ - start_off  │         └──────────┘
                        │ - end_offset │
                        │ - note       │         ┌──────────────┐
                        │ - tags       │         │  Collection  │
                        │ - embedding  │         │              │
                        │ - color      │         │ - id         │
                        │ - is_shared  │         │ - name       │
                        │ - collection │         └──────────────┘
                        │   _ids (JSON)│                │
                        └──────────────┘                │
                                │                       │
                                └───────────────────────┘
                                  (JSON array reference)
```

### Annotation Lifecycle States

```
┌─────────────┐
│   Created   │ - Annotation created with offsets and text
│             │ - Context extracted
│             │ - Embedding generation enqueued (if note exists)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Active    │ - Annotation visible to user
│             │ - Can be updated, searched, exported
│             │ - Embedding may be generating in background
└──────┬──────┘
       │
       ├──────► Updated (note/tags/color changed)
       │        - Embedding regenerated if note changed
       │        - updated_at timestamp refreshed
       │
       └──────► Deleted
                - Removed from database
                - Cascade: Resource deletion triggers annotation deletion
```

### JSON Field Structures

**tags field** (stored as JSON string):
```json
["methodology", "important", "future-work"]
```

**collection_ids field** (stored as JSON string):
```json
["550e8400-e29b-41d4-a716-446655440000", "6ba7b810-9dad-11d1-80b4-00c04fd430c8"]
```

**embedding field** (stored as JSON array):
```json
[0.123, -0.456, 0.789, ..., 0.321]  // 384-dimensional vector (sentence-transformers)
```


## Error Handling

### Error Types and Responses

| Error Type | HTTP Status | Scenario | Response |
|------------|-------------|----------|----------|
| ValidationError | 400 | Invalid offsets (start >= end, negative) | `{"detail": "start_offset must be less than end_offset"}` |
| ResourceNotFoundError | 404 | Resource doesn't exist | `{"detail": "Resource {id} not found"}` |
| AnnotationNotFoundError | 404 | Annotation doesn't exist | `{"detail": "Annotation {id} not found"}` |
| PermissionError | 403 | User not owner | `{"detail": "Cannot update another user's annotation"}` |
| DatabaseError | 500 | Database connection failure | `{"detail": "Internal server error"}` |

### Validation Rules

**Offset Validation**:
```python
def validate_offsets(start_offset: int, end_offset: int, content_length: int):
    if start_offset < 0 or end_offset < 0:
        raise ValidationError("Offsets must be non-negative")
    
    if start_offset >= end_offset:
        raise ValidationError("start_offset must be less than end_offset")
    
    if end_offset > content_length:
        raise ValidationError(f"end_offset ({end_offset}) exceeds content length ({content_length})")
```

**Text Verification** (optional, for data integrity):
```python
def verify_highlighted_text(content: str, start: int, end: int, expected_text: str):
    actual_text = content[start:end]
    if actual_text != expected_text:
        # Log warning but don't fail (content may have been updated)
        logger.warning(f"Highlighted text mismatch: expected '{expected_text}', got '{actual_text}'")
```

### Edge Cases

1. **Empty Note**: Valid annotation, no embedding generated
2. **Offset at Document Boundaries**: Context extraction handles start=0 or end=len(content)
3. **Duplicate Annotations**: Allowed (user may highlight same passage multiple times with different notes)
4. **Resource Content Updated**: Offsets may become invalid; annotations remain but may not align
5. **Concurrent Updates**: Database transactions prevent race conditions
6. **Large Note Text**: Limit note to 10,000 characters to prevent abuse
7. **Zero-Length Highlight**: Reject (start == end is invalid)


## Testing Strategy

### Unit Tests

**Test Coverage Areas**:

1. **Annotation CRUD** (`test_annotation_crud.py`)
   - Create annotation with valid data
   - Create annotation with invalid offsets (negative, start >= end)
   - Update annotation (note, tags, color)
   - Update annotation ownership validation
   - Delete annotation
   - Delete annotation ownership validation

2. **Annotation Retrieval** (`test_annotation_retrieval.py`)
   - Get annotations for resource (ordered by offset)
   - Get annotations for user (paginated, sorted)
   - Filter annotations by tags
   - Include shared annotations from other users
   - Eager loading prevents N+1 queries

3. **Annotation Search** (`test_annotation_search.py`)
   - Full-text search in notes
   - Full-text search in highlighted text
   - Semantic search with embeddings
   - Tag-based search (ANY tag, ALL tags)
   - Search performance with 10,000 annotations

4. **Annotation Export** (`test_annotation_export.py`)
   - Export to Markdown (single resource)
   - Export to Markdown (all resources)
   - Export to JSON
   - Export formatting correctness
   - Export performance (1,000 annotations <2s)

5. **Integration Tests** (`test_annotation_integration.py`)
   - Resource deletion cascades to annotations
   - Embedding generation on annotation creation
   - Search includes annotation matches
   - Recommendations based on annotations
   - Collection annotation counts

### Performance Tests

**Benchmarks**:

```python
def test_annotation_creation_performance():
    # Target: <50ms per annotation (excluding embedding)
    start = time.time()
    annotation = service.create_annotation(...)
    elapsed = time.time() - start
    assert elapsed < 0.05  # 50ms

def test_fulltext_search_performance():
    # Setup: Create 10,000 annotations
    # Target: <100ms search
    start = time.time()
    results = service.search_annotations_fulltext(user_id, "query")
    elapsed = time.time() - start
    assert elapsed < 0.1  # 100ms

def test_semantic_search_performance():
    # Setup: Create 1,000 annotations with embeddings
    # Target: <500ms search
    start = time.time()
    results = service.search_annotations_semantic(user_id, "query")
    elapsed = time.time() - start
    assert elapsed < 0.5  # 500ms

def test_export_performance():
    # Setup: Create 1,000 annotations
    # Target: <2s export
    start = time.time()
    markdown = service.export_annotations_markdown(user_id)
    elapsed = time.time() - start
    assert elapsed < 2.0  # 2 seconds
```

### Integration Test Scenarios

1. **End-to-End Annotation Workflow**:
   - User ingests PDF
   - User creates annotation on page 5
   - User searches for annotation by keyword
   - User exports annotations to Markdown
   - User deletes resource (annotations cascade deleted)

2. **Multi-User Annotation Sharing**:
   - User A creates private annotation
   - User B cannot see User A's annotation
   - User A marks annotation as shared
   - User B can now see shared annotation

3. **Collection Integration**:
   - User creates collection "ML Papers"
   - User adds resources to collection
   - User annotates resources with collection_ids
   - User retrieves collection with annotation count

### Test Data Fixtures

```python
@pytest.fixture
def sample_resource(db_session):
    resource = Resource(
        id=uuid.uuid4(),
        title="Sample Paper",
        content="This is a sample paper content with enough text to test annotations. " * 100
    )
    db_session.add(resource)
    db_session.commit()
    return resource

@pytest.fixture
def sample_annotation(db_session, sample_resource):
    annotation = Annotation(
        id=uuid.uuid4(),
        resource_id=sample_resource.id,
        user_id="test-user",
        start_offset=10,
        end_offset=30,
        highlighted_text="sample paper content",
        note="This is a test note",
        tags='["test", "sample"]',
        color="#FFFF00"
    )
    db_session.add(annotation)
    db_session.commit()
    return annotation
```


## Performance Optimization

### Database Optimization

**Indexes**:
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

**Query Optimization**:
- Use `joinedload()` for eager loading relationships
- Batch operations for export (single query for all annotations)
- Limit result sets with pagination
- Use database-level JSON operations for tag filtering

### Embedding Generation Strategy

**Async Processing**:
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

**Batching** (future optimization):
- Queue multiple embedding requests
- Generate embeddings in batches of 32
- Update annotations in bulk

### Search Optimization

**Full-Text Search**:
- Current: LIKE queries (sufficient for <10,000 annotations)
- Future: FTS5 virtual table for >10,000 annotations
- Indexing: Create FTS5 index on `note` and `highlighted_text`

**Semantic Search**:
- Current: In-memory cosine similarity (sufficient for <1,000 annotations)
- Future: FAISS index for >1,000 annotations
- Caching: Cache query embeddings for repeated searches

### Export Optimization

**Markdown Export**:
```python
# Efficient string concatenation
markdown_parts = []  # List of strings
for annotation in annotations:
    markdown_parts.append(format_annotation(annotation))
return "".join(markdown_parts)  # Single concatenation at end
```

**JSON Export**:
```python
# Batch query with eager loading
annotations = db.query(Annotation)\
    .options(joinedload(Annotation.resource))\
    .filter(Annotation.user_id == user_id)\
    .all()

# Convert to dicts in memory (fast)
return [annotation_to_dict(ann) for ann in annotations]
```

### Caching Strategy (Future)

**Cache Layers**:
1. **Annotation Counts**: Cache collection annotation counts (invalidate on add/remove)
2. **Query Embeddings**: Cache embeddings for common search queries
3. **Export Results**: Cache recent exports (invalidate on annotation changes)

**Cache Invalidation**:
- Annotation created/updated/deleted → Invalidate user's annotation cache
- Resource deleted → Invalidate resource annotation cache
- Collection membership changed → Invalidate collection annotation count


## Security Considerations

### Authentication & Authorization

**Access Control Matrix**:

| Operation | Owner | Other User (Private) | Other User (Shared) | Anonymous |
|-----------|-------|---------------------|---------------------|-----------|
| Create | ✓ | ✗ | ✗ | ✗ |
| Read | ✓ | ✗ | ✓ | ✗ |
| Update | ✓ | ✗ | ✗ | ✗ |
| Delete | ✓ | ✗ | ✗ | ✗ |
| Search | ✓ (own) | ✗ | ✗ | ✗ |
| Export | ✓ (own) | ✗ | ✗ | ✗ |

**Implementation**:
```python
def verify_annotation_access(annotation: Annotation, user_id: str, operation: str):
    if operation in ["update", "delete"]:
        if annotation.user_id != user_id:
            raise PermissionError("Only annotation owner can perform this operation")
    
    elif operation == "read":
        if annotation.user_id != user_id and not annotation.is_shared:
            raise PermissionError("Cannot access private annotation")
```

### Data Privacy

**Privacy by Default**:
- All annotations are private (`is_shared=False`) by default
- Users must explicitly mark annotations as shared
- Search and export only include user's own annotations

**PII Protection**:
- Annotation notes may contain sensitive information
- Never log annotation content
- Sanitize error messages to avoid leaking annotation data

### Input Validation

**Offset Validation**:
```python
# Prevent integer overflow
MAX_OFFSET = 2**31 - 1
if start_offset > MAX_OFFSET or end_offset > MAX_OFFSET:
    raise ValidationError("Offset exceeds maximum value")

# Prevent negative offsets
if start_offset < 0 or end_offset < 0:
    raise ValidationError("Offsets must be non-negative")
```

**Note Length Limit**:
```python
MAX_NOTE_LENGTH = 10_000
if note and len(note) > MAX_NOTE_LENGTH:
    raise ValidationError(f"Note exceeds maximum length of {MAX_NOTE_LENGTH} characters")
```

**Tag Validation**:
```python
MAX_TAGS = 20
MAX_TAG_LENGTH = 50
if tags and len(tags) > MAX_TAGS:
    raise ValidationError(f"Cannot have more than {MAX_TAGS} tags")
for tag in tags:
    if len(tag) > MAX_TAG_LENGTH:
        raise ValidationError(f"Tag '{tag}' exceeds maximum length of {MAX_TAG_LENGTH}")
```

### SQL Injection Prevention

- Use SQLAlchemy ORM (parameterized queries)
- Never construct raw SQL with user input
- Validate UUIDs before querying

### Rate Limiting (Future)

**Annotation Creation**:
- Limit: 100 annotations per minute per user
- Prevents abuse and spam

**Search Operations**:
- Limit: 60 searches per minute per user
- Prevents resource exhaustion

**Export Operations**:
- Limit: 10 exports per hour per user
- Exports are resource-intensive


## Migration Strategy

### Database Migration

**Alembic Migration Script**:

```python
# alembic/versions/xxxx_add_annotation_table_phase7_5.py

def upgrade():
    # Create annotations table
    op.create_table(
        'annotations',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('resource_id', GUID(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('start_offset', sa.Integer(), nullable=False),
        sa.Column('end_offset', sa.Integer(), nullable=False),
        sa.Column('highlighted_text', sa.Text(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('color', sa.String(7), nullable=False, server_default='#FFFF00'),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.Column('context_before', sa.String(50), nullable=True),
        sa.Column('context_after', sa.String(50), nullable=True),
        sa.Column('is_shared', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('collection_ids', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['resource_id'], ['resources.id'], ondelete='CASCADE'),
        sa.CheckConstraint('start_offset < end_offset', name='check_offset_order'),
        sa.CheckConstraint('start_offset >= 0 AND end_offset >= 0', name='check_offset_nonnegative')
    )
    
    # Create indexes
    op.create_index('idx_annotations_resource', 'annotations', ['resource_id'])
    op.create_index('idx_annotations_user', 'annotations', ['user_id'])
    op.create_index('idx_annotations_user_resource', 'annotations', ['user_id', 'resource_id'])
    op.create_index('idx_annotations_created', 'annotations', ['created_at'])

def downgrade():
    op.drop_index('idx_annotations_created', table_name='annotations')
    op.drop_index('idx_annotations_user_resource', table_name='annotations')
    op.drop_index('idx_annotations_user', table_name='annotations')
    op.drop_index('idx_annotations_resource', table_name='annotations')
    op.drop_table('annotations')
```

**Migration Testing**:
```bash
# Test upgrade
alembic upgrade head
# Verify table exists
sqlite3 backend.db "SELECT * FROM annotations LIMIT 1;"

# Test downgrade
alembic downgrade -1
# Verify table removed
sqlite3 backend.db ".tables" | grep annotations

# Re-upgrade
alembic upgrade head
```

### Backward Compatibility

**API Versioning**:
- New endpoints: `/annotations/*` (no conflict with existing endpoints)
- Existing endpoints unchanged
- No breaking changes to existing functionality

**Database Schema**:
- New table: `annotations` (no changes to existing tables)
- Foreign key to `resources` table (existing table)
- No migration of existing data required

### Rollback Plan

**If Issues Arise**:
1. Disable annotation endpoints in router (comment out `include_router`)
2. Run `alembic downgrade -1` to remove annotations table
3. Remove annotation service imports from other services
4. Restart application

**Data Preservation**:
- Before downgrade, export all annotations to JSON
- Store exports in `storage/annotation_backups/`
- Can re-import after fixing issues


## Future Enhancements

### Phase 8+ Considerations

**1. Collaborative Annotations**
- Shared annotation threads (multiple users commenting on same highlight)
- Annotation replies and discussions
- Notification system for annotation mentions

**2. Advanced Search**
- FTS5 full-text search for >10,000 annotations
- FAISS vector index for >1,000 annotations
- Faceted search (filter by date range, tags, resources)
- Annotation timeline visualization

**3. Rich Text Notes**
- Markdown support in annotation notes
- LaTeX equation rendering in notes
- Image attachments to annotations
- Link annotations to other annotations

**4. Export Enhancements**
- Export to Obsidian format (with backlinks)
- Export to Roam Research format
- Export to Zotero notes
- PDF export with highlighted passages

**5. AI-Powered Features**
- Auto-tagging based on note content
- Suggested annotations based on reading patterns
- Summarization of annotation clusters
- Question answering over annotations

**6. Mobile Support**
- Touch-based text selection
- Offline annotation sync
- Voice-to-text for notes
- Annotation sharing via mobile

**7. Analytics**
- Annotation heatmaps (most annotated sections)
- Reading engagement metrics
- Tag cloud visualization
- Annotation growth over time

**8. Integration Enhancements**
- Annotation-based citation networks
- Annotation influence on quality scores
- Collection recommendations based on annotation patterns
- Cross-resource annotation linking

### Technical Debt to Address

**1. Embedding Generation**
- Move to dedicated background worker (Celery/RQ)
- Batch embedding generation for efficiency
- Retry logic for failed embeddings

**2. Search Scalability**
- Implement FTS5 for full-text search
- Implement FAISS for semantic search
- Add search result caching

**3. Export Performance**
- Stream large exports instead of loading all in memory
- Add export job queue for large datasets
- Implement incremental exports (only new annotations)

**4. Data Integrity**
- Add annotation verification (check if offsets still valid)
- Implement annotation repair tool (re-extract context)
- Add data consistency checks


## Implementation Checklist

### Step 1: Database Layer
- [ ] Add Annotation model to `backend/app/database/models.py`
- [ ] Create Alembic migration script
- [ ] Test migration upgrade/downgrade
- [ ] Verify indexes created correctly
- [ ] Verify foreign key constraints work

### Step 2: Service Layer
- [ ] Create `backend/app/services/annotation_service.py`
- [ ] Implement CRUD operations (create, update, delete, get)
- [ ] Implement retrieval methods (by resource, by user)
- [ ] Implement search methods (fulltext, semantic, tags)
- [ ] Implement export methods (markdown, json)
- [ ] Implement helper methods (context extraction, embedding generation, similarity)
- [ ] Add error handling and validation

### Step 3: API Layer
- [ ] Create `backend/app/schemas/annotation.py` with Pydantic schemas
- [ ] Create `backend/app/routers/annotations.py` with endpoints
- [ ] Implement authentication dependencies
- [ ] Implement authorization checks
- [ ] Add request/response validation
- [ ] Add error handling middleware

### Step 4: Integration
- [ ] Add resource deletion hook in `resource_service.py`
- [ ] Add search integration in `search_service.py`
- [ ] Add recommendation integration in `recommendation_service.py`
- [ ] Add collection integration in `collection_service.py`
- [ ] Register annotation router in main app

### Step 5: Testing
- [ ] Write unit tests for AnnotationService
- [ ] Write integration tests for API endpoints
- [ ] Write performance tests (10,000 annotations, search, export)
- [ ] Write edge case tests (boundary conditions, errors)
- [ ] Achieve >85% code coverage

### Step 6: Documentation
- [ ] Update `backend/README.md` with Phase 7.5 section
- [ ] Update `backend/docs/API_DOCUMENTATION.md` with annotation endpoints
- [ ] Update `backend/docs/DEVELOPER_GUIDE.md` with annotation system guide
- [ ] Update `backend/docs/CHANGELOG.md` with Phase 7.5 changes
- [ ] Create `backend/docs/EXAMPLES_PHASE7_5.md` with usage examples

### Step 7: Validation
- [ ] Verify all requirements met
- [ ] Verify performance targets achieved
- [ ] Verify security controls in place
- [ ] Verify backward compatibility maintained
- [ ] Verify documentation complete

## Success Metrics

### Functional Requirements
- ✓ Support 10,000+ annotations per resource
- ✓ Full-text annotation search <100ms
- ✓ Annotation embedding generation <500ms
- ✓ Export 1,000 annotations to Markdown in <2 seconds
- ✓ Semantic annotation search with 80%+ relevance

### Non-Functional Requirements
- ✓ All tests passing with >85% coverage
- ✓ No breaking changes to existing functionality
- ✓ API documentation complete
- ✓ Migration tested (upgrade/downgrade)
- ✓ Security controls implemented (authentication, authorization, validation)

### Integration Requirements
- ✓ Resource deletion cascades to annotations
- ✓ Search includes annotation matches
- ✓ Recommendations use annotation patterns
- ✓ Collections show annotation counts

## Conclusion

Phase 7.5 transforms Neo Alexandria into an active reading platform by enabling users to highlight, annotate, search, and export their research notes. The design prioritizes precision (character offsets), performance (indexed queries, async embeddings), privacy (private by default), and integration (search, recommendations, collections).

The implementation follows established patterns from Phase 7 (collections) and Phase 6.5 (scholarly metadata), ensuring consistency and maintainability. The system is designed to scale to thousands of annotations per resource while maintaining sub-100ms search performance.

Future enhancements will add collaborative features, advanced search, rich text notes, and AI-powered capabilities, building on the solid foundation established in Phase 7.5.
