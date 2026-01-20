# Design Document: Phase 17.5 - Advanced RAG Architecture Upgrade

## Overview

This design document specifies the technical architecture for upgrading Neo Alexandria 2.0 from Naive RAG to advanced RAG patterns. The upgrade introduces four key capabilities:

1. **Parent-Child Chunking**: Decouple retrieval units (small chunks) from generation units (full resources)
2. **GraphRAG**: Semantic triple storage for graph-enhanced retrieval
3. **HyDE/Reverse HyDE**: Synthetic question generation for improved query matching
4. **RAG Evaluation**: Metrics storage and measurement framework

The design maintains backward compatibility, follows the vertical slice architecture, and integrates with the existing event-driven system.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Query                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Search Module (Enhanced)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Keyword    │  │   Semantic   │  │   GraphRAG   │     │
│  │   Search     │  │   Search     │  │   Search     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Retrieval Layer                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Parent-Child Retrieval                              │  │
│  │  1. Retrieve top-k chunks by similarity              │  │
│  │  2. Expand to parent resources                       │  │
│  │  3. Include surrounding chunks for context           │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Layer                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ DocumentChunk│  │ GraphEntity  │  │  Synthetic   │     │
│  │   (Chunks)   │  │ GraphRelation│  │  Questions   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Module Responsibilities

**Resources Module**:
- DocumentChunk model and schema
- ChunkingService for document splitting
- Chunk CRUD operations
- Event emission: `resource.chunked`

**Graph Module**:
- GraphEntity and GraphRelationship models
- GraphExtractionService for entity/relationship extraction
- Graph traversal and query operations
- Event emission: `graph.entity_extracted`, `graph.relationship_extracted`

**Search Module**:
- SyntheticQuestion model
- Enhanced search strategies (parent-child, GraphRAG)
- Query expansion and reranking
- Integration with existing hybrid search

**Quality Module**:
- RAGEvaluation model
- Evaluation metrics computation (RAGAS)
- Evaluation API endpoints
- Performance tracking and reporting

## Components and Interfaces

### 1. DocumentChunk Model

**Location**: `app/modules/resources/model.py`

**Purpose**: Store small, searchable text chunks with embeddings

**Schema**:
```python
class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id: str = Column(String, primary_key=True)
    resource_id: str = Column(String, ForeignKey("resources.id", ondelete="CASCADE"))
    content: str = Column(Text, nullable=False)
    chunk_index: int = Column(Integer, nullable=False)
    embedding_id: str = Column(String, ForeignKey("embeddings.id"))
    page_number: Optional[int] = Column(Integer, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resource = relationship("Resource", backref="chunks")
    embedding = relationship("Embedding")
    
    # Indexes
    __table_args__ = (
        Index("idx_chunk_resource", "resource_id"),
        Index("idx_chunk_index", "resource_id", "chunk_index"),
    )
```

**Pydantic Schema**:
```python
class DocumentChunkCreate(BaseModel):
    resource_id: str
    content: str
    chunk_index: int
    page_number: Optional[int] = None

class DocumentChunkResponse(BaseModel):
    id: str
    resource_id: str
    content: str
    chunk_index: int
    page_number: Optional[int]
    embedding_id: Optional[str]
    created_at: datetime
```

### 2. GraphEntity Model

**Location**: `app/modules/graph/model.py`

**Purpose**: Store named entities extracted from text

**Schema**:
```python
class GraphEntity(Base):
    __tablename__ = "graph_entities"
    
    id: str = Column(String, primary_key=True)
    name: str = Column(String, nullable=False, index=True)
    type: str = Column(String, nullable=False)  # Concept, Person, Organization, Method
    description: Optional[str] = Column(Text)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    outgoing_relationships = relationship(
        "GraphRelationship",
        foreign_keys="GraphRelationship.source_entity_id",
        backref="source_entity"
    )
    incoming_relationships = relationship(
        "GraphRelationship",
        foreign_keys="GraphRelationship.target_entity_id",
        backref="target_entity"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_entity_name_type", "name", "type"),
    )
```

**Pydantic Schema**:
```python
class GraphEntityCreate(BaseModel):
    name: str
    type: str
    description: Optional[str] = None

class GraphEntityResponse(BaseModel):
    id: str
    name: str
    type: str
    description: Optional[str]
    created_at: datetime
```

### 3. GraphRelationship Model

**Location**: `app/modules/graph/model.py`

**Purpose**: Store semantic triples (Subject -> Predicate -> Object)

**Schema**:
```python
class GraphRelationship(Base):
    __tablename__ = "graph_relationships"
    
    id: str = Column(String, primary_key=True)
    source_entity_id: str = Column(String, ForeignKey("graph_entities.id", ondelete="CASCADE"))
    target_entity_id: str = Column(String, ForeignKey("graph_entities.id", ondelete="CASCADE"))
    relation_type: str = Column(String, nullable=False)  # CONTRADICTS, SUPPORTS, EXTENDS, CITES
    weight: float = Column(Float, default=1.0)
    provenance_chunk_id: Optional[str] = Column(String, ForeignKey("document_chunks.id"))
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    
    # Relationships defined in GraphEntity
    provenance_chunk = relationship("DocumentChunk")
    
    # Indexes
    __table_args__ = (
        Index("idx_relationship_source", "source_entity_id"),
        Index("idx_relationship_target", "target_entity_id"),
        Index("idx_relationship_type", "relation_type"),
    )
```

**Pydantic Schema**:
```python
class GraphRelationshipCreate(BaseModel):
    source_entity_id: str
    target_entity_id: str
    relation_type: str
    weight: float = 1.0
    provenance_chunk_id: Optional[str] = None

class GraphRelationshipResponse(BaseModel):
    id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: str
    weight: float
    provenance_chunk_id: Optional[str]
    created_at: datetime
```

### 4. SyntheticQuestion Model

**Location**: `app/modules/search/model.py`

**Purpose**: Store LLM-generated questions for Reverse HyDE retrieval

**Schema**:
```python
class SyntheticQuestion(Base):
    __tablename__ = "synthetic_questions"
    
    id: str = Column(String, primary_key=True)
    chunk_id: str = Column(String, ForeignKey("document_chunks.id", ondelete="CASCADE"))
    question_text: str = Column(Text, nullable=False)
    embedding_id: str = Column(String, ForeignKey("embeddings.id"))
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chunk = relationship("DocumentChunk", backref="synthetic_questions")
    embedding = relationship("Embedding")
    
    # Indexes
    __table_args__ = (
        Index("idx_synthetic_chunk", "chunk_id"),
    )
```

**Pydantic Schema**:
```python
class SyntheticQuestionCreate(BaseModel):
    chunk_id: str
    question_text: str

class SyntheticQuestionResponse(BaseModel):
    id: str
    chunk_id: str
    question_text: str
    embedding_id: Optional[str]
    created_at: datetime
```

### 5. RAGEvaluation Model

**Location**: `app/modules/quality/model.py`

**Purpose**: Store evaluation data and RAGAS metrics

**Schema**:
```python
class RAGEvaluation(Base):
    __tablename__ = "rag_evaluations"
    
    id: str = Column(String, primary_key=True)
    query: str = Column(Text, nullable=False)
    expected_answer: Optional[str] = Column(Text)
    generated_answer: Optional[str] = Column(Text)
    retrieved_chunk_ids: List[str] = Column(JSON)
    faithfulness_score: Optional[float] = Column(Float)
    answer_relevance_score: Optional[float] = Column(Float)
    context_precision_score: Optional[float] = Column(Float)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_evaluation_created", "created_at"),
    )
```

**Pydantic Schema**:
```python
class RAGEvaluationCreate(BaseModel):
    query: str
    expected_answer: Optional[str] = None
    generated_answer: Optional[str] = None
    retrieved_chunk_ids: List[str]
    faithfulness_score: Optional[float] = None
    answer_relevance_score: Optional[float] = None
    context_precision_score: Optional[float] = None

class RAGEvaluationResponse(BaseModel):
    id: str
    query: str
    expected_answer: Optional[str]
    generated_answer: Optional[str]
    retrieved_chunk_ids: List[str]
    faithfulness_score: Optional[float]
    answer_relevance_score: Optional[float]
    context_precision_score: Optional[float]
    created_at: datetime
```

## Data Models

### Entity Relationship Diagram

```
┌─────────────┐
│  Resource   │
│  (Parent)   │
└──────┬──────┘
       │ 1:N
       │
       ▼
┌─────────────────┐
│ DocumentChunk   │◄──────┐
│ (Retrieval Unit)│       │
└────────┬────────┘       │
         │ 1:1            │ N:1
         │                │
         ▼                │
┌─────────────┐           │
│  Embedding  │           │
└─────────────┘           │
                          │
┌─────────────────┐       │
│SyntheticQuestion│───────┘
│  (HyDE)         │
└─────────────────┘

┌──────────────┐
│ GraphEntity  │
└──────┬───────┘
       │ N:M
       │
       ▼
┌──────────────────┐
│GraphRelationship │
│  (Semantic       │
│   Triple)        │
└────────┬─────────┘
         │ N:1
         │
         ▼
┌─────────────────┐
│ DocumentChunk   │
│ (Provenance)    │
└─────────────────┘

┌──────────────┐
│RAGEvaluation │
│ (Metrics)    │
└──────────────┘
```

### Chunking Strategy

**Semantic Chunking** (Recommended):
- Split on sentence boundaries using spaCy or NLTK
- Target chunk size: 200-500 tokens
- Overlap: 50-100 tokens between chunks
- Preserve paragraph structure when possible

**Fixed-Size Chunking** (Fallback):
- Split at fixed character or token count
- Target chunk size: 1000 characters
- Overlap: 200 characters
- Split on whitespace to avoid mid-word breaks

**Page-Based Chunking** (PDF):
- Extract page numbers from PDF metadata
- Store page_number for citation purposes
- Combine with semantic chunking within pages

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Chunk Index Uniqueness

*For any* resource, all associated chunks must have unique chunk_index values within that resource, and chunk_index values must be sequential starting from 0.

**Validates: Requirements 1.10**

### Property 2: Foreign Key Integrity

*For any* DocumentChunk, the resource_id must reference an existing Resource, and deleting a Resource must cascade delete all associated chunks.

**Validates: Requirements 1.7**

### Property 3: Graph Triple Validity

*For any* GraphRelationship, both source_entity_id and target_entity_id must reference existing GraphEntity records.

**Validates: Requirements 2.7**

### Property 4: Provenance Linkage

*For any* GraphRelationship with a provenance_chunk_id, the chunk_id must reference an existing DocumentChunk.

**Validates: Requirements 2.6**

### Property 5: Synthetic Question Association

*For any* SyntheticQuestion, the chunk_id must reference an existing DocumentChunk, and deleting a chunk must cascade delete all associated synthetic questions.

**Validates: Requirements 3.8**

### Property 6: Evaluation Chunk References

*For any* RAGEvaluation, all chunk IDs in retrieved_chunk_ids must reference existing DocumentChunk records at the time of evaluation creation.

**Validates: Requirements 4.5**

### Property 7: Parent-Child Retrieval Consistency

*For any* search query, if a chunk is retrieved, expanding to the parent resource must return the resource that contains that chunk.

**Validates: Requirements 8.3**

### Property 8: Graph Traversal Completeness

*For any* entity in the graph, traversing relationships must return all directly connected entities without duplicates.

**Validates: Requirements 9.5**

### Property 9: Chunk Content Preservation

*For any* resource, concatenating all chunks in chunk_index order must reconstruct the original resource content (allowing for overlap).

**Validates: Requirements 6.4**

### Property 10: Embedding Generation Completeness

*For any* DocumentChunk or SyntheticQuestion, if an embedding_id is set, it must reference an existing Embedding record.

**Validates: Requirements 6.7**

## Error Handling

### Chunking Errors

**Scenario**: Resource content is too short to chunk
**Handling**: Create a single chunk with chunk_index=0 containing full content

**Scenario**: Chunking service fails mid-process
**Handling**: Rollback transaction, log error, emit `resource.chunking_failed` event

**Scenario**: Embedding generation fails for a chunk
**Handling**: Store chunk without embedding_id, retry asynchronously

### Graph Extraction Errors

**Scenario**: No entities found in chunk
**Handling**: Skip graph extraction, log warning, continue processing

**Scenario**: Entity extraction returns invalid data
**Handling**: Validate entity names and types, skip invalid entities, log errors

**Scenario**: Relationship extraction fails
**Handling**: Store entities without relationships, log error, continue

### Retrieval Errors

**Scenario**: Chunk references deleted resource
**Handling**: Filter out orphaned chunks, log data integrity issue

**Scenario**: Graph traversal encounters cycle
**Handling**: Implement cycle detection, limit traversal depth to 3 hops

**Scenario**: Parent-child expansion fails
**Handling**: Return chunk-only results, log error, degrade gracefully

### Evaluation Errors

**Scenario**: Invalid chunk IDs in evaluation data
**Handling**: Validate chunk IDs before storage, reject invalid evaluations with 400 error

**Scenario**: Metric computation fails
**Handling**: Store evaluation with null metric scores, log error

## Testing Strategy

### Unit Tests

**DocumentChunk Model**:
- Test chunk creation with valid data
- Test foreign key constraints (resource_id, embedding_id)
- Test cascade delete when resource is deleted
- Test chunk_index uniqueness per resource
- Test page_number optional field

**GraphEntity Model**:
- Test entity creation with all entity types
- Test name and type indexing
- Test relationship queries (outgoing, incoming)

**GraphRelationship Model**:
- Test relationship creation with all relation types
- Test weight validation (0.0 to 1.0)
- Test provenance linkage to chunks
- Test cascade delete when entities are deleted

**SyntheticQuestion Model**:
- Test question creation linked to chunks
- Test cascade delete when chunk is deleted
- Test multiple questions per chunk

**RAGEvaluation Model**:
- Test evaluation creation with all metrics
- Test JSON storage of chunk IDs
- Test querying by date range and score thresholds

### Integration Tests

**ChunkingService**:
- Test semantic chunking with sample documents
- Test fixed-size chunking with various sizes
- Test chunk_index assignment
- Test embedding generation for chunks
- Test event emission after chunking

**GraphExtractionService**:
- Test entity extraction from sample text
- Test relationship extraction
- Test entity deduplication
- Test provenance linkage
- Test event emission after extraction

**Parent-Child Retrieval**:
- Test chunk retrieval by similarity
- Test parent resource expansion
- Test surrounding chunk inclusion
- Test deduplication of results

**GraphRAG Retrieval**:
- Test entity extraction from query
- Test graph traversal
- Test result ranking with graph weights
- Test contradiction discovery mode

### Property-Based Tests

**Property Test 1: Chunk Index Uniqueness**
- Generate random resources with random number of chunks
- Verify all chunk_index values are unique and sequential
- **Feature: phase17-5-advanced-rag-architecture, Property 1: Chunk Index Uniqueness**

**Property Test 2: Foreign Key Integrity**
- Generate random resources and chunks
- Delete random resources
- Verify all associated chunks are deleted
- **Feature: phase17-5-advanced-rag-architecture, Property 2: Foreign Key Integrity**

**Property Test 3: Graph Triple Validity**
- Generate random entities and relationships
- Verify all relationships reference existing entities
- **Feature: phase17-5-advanced-rag-architecture, Property 3: Graph Triple Validity**

**Property Test 4: Parent-Child Retrieval Consistency**
- Generate random chunks and retrieve them
- Expand to parent resources
- Verify parent contains the retrieved chunk
- **Feature: phase17-5-advanced-rag-architecture, Property 7: Parent-Child Retrieval Consistency**

**Property Test 5: Chunk Content Preservation**
- Generate random resource content
- Chunk the content
- Concatenate chunks in order
- Verify reconstructed content matches original (allowing overlap)
- **Feature: phase17-5-advanced-rag-architecture, Property 9: Chunk Content Preservation**

### Performance Tests

- Chunking: Process 10,000 words in < 5 seconds
- Graph extraction: Process 100 chunks in < 5 minutes
- Parent-child retrieval: Retrieve top-10 results in < 200ms
- GraphRAG retrieval: Retrieve top-10 results in < 500ms
- Database queries: All indexed queries < 50ms

## Implementation Notes

### Database Migration

**Migration File**: `alembic/versions/YYYYMMDD_add_advanced_rag_tables.py`

**Upgrade Steps**:
1. Create document_chunks table with indexes
2. Create graph_entities table with indexes
3. Create graph_relationships table with indexes
4. Create synthetic_questions table with indexes
5. Create rag_evaluations table with indexes
6. Add foreign key constraints with CASCADE

**Downgrade Steps**:
1. Drop rag_evaluations table
2. Drop synthetic_questions table
3. Drop graph_relationships table
4. Drop graph_entities table
5. Drop document_chunks table

### Backward Compatibility

- Resources without chunks remain valid
- Existing search continues to work (searches resources directly)
- New search strategies are opt-in via API parameters
- Chunking is triggered explicitly or via event handlers

### Event Integration

**Events Emitted**:
- `resource.chunked` - After successful chunking
- `resource.chunking_failed` - After chunking failure
- `graph.entity_extracted` - After entity extraction
- `graph.relationship_extracted` - After relationship extraction
- `search.synthetic_questions_generated` - After question generation

**Events Subscribed**:
- `resource.created` - Trigger chunking (optional)
- `resource.chunked` - Trigger graph extraction (optional)
- `resource.chunked` - Trigger synthetic question generation (optional)

### Configuration Options

```python
# Chunking Configuration
CHUNKING_ENABLED: bool = True
CHUNKING_STRATEGY: str = "semantic"  # semantic, fixed, page
CHUNK_SIZE: int = 500  # tokens for semantic, characters for fixed
CHUNK_OVERLAP: int = 100  # tokens or characters
CHUNK_ON_RESOURCE_CREATE: bool = False  # Auto-chunk new resources

# Graph Extraction Configuration
GRAPH_EXTRACTION_ENABLED: bool = True
GRAPH_EXTRACTION_METHOD: str = "llm"  # llm, spacy, hybrid
GRAPH_EXTRACT_ON_CHUNK: bool = False  # Auto-extract from chunks

# Synthetic Questions Configuration
SYNTHETIC_QUESTIONS_ENABLED: bool = False  # Expensive, opt-in
QUESTIONS_PER_CHUNK: int = 2
QUESTION_GENERATION_MODEL: str = "gpt-3.5-turbo"

# Retrieval Configuration
DEFAULT_RETRIEVAL_STRATEGY: str = "parent-child"  # parent-child, graphrag, hybrid
PARENT_CHILD_CONTEXT_WINDOW: int = 2  # Surrounding chunks to include
GRAPHRAG_MAX_HOPS: int = 2  # Graph traversal depth
```

### Performance Optimization

**Indexing Strategy**:
- Index on (resource_id, chunk_index) for fast chunk retrieval
- Index on entity name for fast entity lookup
- Index on relation_type for filtered graph queries
- Index on created_at for time-based queries

**Batch Processing**:
- Chunk resources in batches of 10
- Generate embeddings in batches of 50
- Extract entities in batches of 20

**Caching**:
- Cache entity lookups in Redis (TTL: 1 hour)
- Cache graph traversal results (TTL: 30 minutes)
- Cache synthetic questions (TTL: 24 hours)

**Async Processing**:
- Chunking runs asynchronously via Celery
- Graph extraction runs asynchronously
- Synthetic question generation runs asynchronously
- Evaluation metric computation runs asynchronously

## API Endpoints

### Chunking Endpoints

```
POST /api/resources/{resource_id}/chunks
- Trigger chunking for a resource
- Body: { "strategy": "semantic", "chunk_size": 500, "overlap": 100 }
- Response: { "task_id": "...", "status": "processing" }

GET /api/resources/{resource_id}/chunks
- List all chunks for a resource
- Query params: page, per_page
- Response: { "chunks": [...], "total": 42 }

GET /api/chunks/{chunk_id}
- Get a specific chunk
- Response: DocumentChunkResponse
```

### Graph Endpoints

```
POST /api/graph/extract/{chunk_id}
- Trigger graph extraction for a chunk
- Response: { "task_id": "...", "status": "processing" }

GET /api/graph/entities
- List all entities
- Query params: type, name_contains, page, per_page
- Response: { "entities": [...], "total": 1000 }

GET /api/graph/entities/{entity_id}/relationships
- Get relationships for an entity
- Query params: relation_type, direction (outgoing/incoming/both)
- Response: { "relationships": [...] }

GET /api/graph/traverse
- Traverse graph from entity
- Query params: entity_id, max_hops, relation_types
- Response: { "entities": [...], "paths": [...] }
```

### Search Endpoints (Enhanced)

```
POST /api/search/advanced
- Advanced search with strategy selection
- Body: {
    "query": "...",
    "strategy": "parent-child",  # parent-child, graphrag, hybrid
    "top_k": 10,
    "context_window": 2,
    "relation_types": ["SUPPORTS", "CONTRADICTS"]
  }
- Response: {
    "results": [
      {
        "chunk": DocumentChunkResponse,
        "parent_resource": ResourceResponse,
        "surrounding_chunks": [DocumentChunkResponse],
        "graph_path": [GraphEntityResponse],
        "score": 0.95
      }
    ]
  }
```

### Evaluation Endpoints

```
POST /api/evaluation/submit
- Submit evaluation data
- Body: RAGEvaluationCreate
- Response: RAGEvaluationResponse

GET /api/evaluation/metrics
- Get aggregated metrics
- Query params: start_date, end_date
- Response: {
    "avg_faithfulness": 0.85,
    "avg_answer_relevance": 0.90,
    "avg_context_precision": 0.80,
    "total_evaluations": 500
  }

GET /api/evaluation/history
- Get evaluation history
- Query params: page, per_page, min_score
- Response: { "evaluations": [...], "total": 500 }
```

## Documentation Requirements

### Database Architecture Update

Add section to `backend/docs/architecture/database.md`:

**Advanced RAG Tables**:
- document_chunks: Retrieval units with embeddings
- graph_entities: Named entities from text
- graph_relationships: Semantic triples
- synthetic_questions: HyDE questions
- rag_evaluations: Evaluation metrics

### Graph Module Update

Update `backend/docs/architecture/modules.md`:

**Graph Module**:
- Citation extraction (existing)
- Knowledge graph (existing)
- **Semantic triple storage (NEW)**
- **Entity and relationship extraction (NEW)**
- **GraphRAG retrieval (NEW)**

### New Documentation Files

1. **Advanced RAG Architecture Guide** (`backend/docs/guides/advanced-rag.md`)
   - Parent-child chunking explanation
   - GraphRAG concepts
   - HyDE and Reverse HyDE
   - When to use each strategy

2. **RAG Evaluation Guide** (`backend/docs/guides/rag-evaluation.md`)
   - RAGAS metrics explanation
   - How to submit evaluation data
   - Interpreting metrics
   - Improving RAG quality

3. **Migration Guide** (`backend/docs/guides/naive-to-advanced-rag.md`)
   - Running the migration
   - Chunking existing resources
   - Performance considerations
   - Rollback procedures

## Success Criteria

- All 5 new tables created successfully
- Zero foreign key constraint violations
- All existing resource tests pass
- Parent-child retrieval functional
- GraphRAG retrieval functional
- Chunking processes 10,000 words in < 5 seconds
- Graph extraction processes 100 chunks in < 5 minutes
- All property tests pass with 100 iterations
- Documentation complete and reviewed
- Migration tested on both SQLite and PostgreSQL
