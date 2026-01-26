# Design Document: Phase 20 Frontend-Backend Infrastructure Support

## Overview

Phase 20 delivers focused backend infrastructure to support frontend roadmap phases 2-8. This design focuses exclusively on genuinely missing features and necessary extensions to existing systems, avoiding all duplication with existing implementations.

### Design Principles

1. **Leverage Existing Infrastructure**: Use existing services (embeddings, static analysis, chunking, event bus) rather than rebuilding
2. **Minimal Extensions**: Extend existing services only where necessary (PDF extractor, graph service, repo parser)
3. **New Capabilities Only**: Build only genuinely missing features (hover API, auto-linking, community detection, visualization, MCP agent, architecture parsing, MCP server)
4. **Performance First**: All APIs must meet strict performance requirements (<100ms for hover, <5s for auto-linking, <10s for community detection)
5. **Event-Driven Integration**: Use existing event bus for cross-module communication

### Scope Boundaries

**In Scope**:
- 7 new capabilities across 4 domains
- 3 extensions to existing services
- Performance optimization for frontend needs

**Out of Scope** (Already Complete):
- Code embeddings (use `shared.embeddings`)
- Node2Vec graph embeddings (use `graph.embeddings`)
- Static analysis (use `graph.logic.static_analysis`)
- Document chunking (use `DocumentChunk` model)
- Dependency analysis (use `repo_parser.DependencyGraph`)
- Event bus, caching, monitoring, logging (all complete)

## Architecture

### System Context

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Applications                     │
│  (Phase 2: Editor, Phase 3: Library, Phase 4: Cortex,      │
│   Phase 5: Planner, Phase 8: MCP Client)                   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  Phase 20 Backend APIs                       │
├─────────────────────────────────────────────────────────────┤
│  Hover Info │ Auto-Link │ Graph Viz │ MCP Agent │ MCP Server│
└─────────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              Existing Backend Infrastructure                 │
├─────────────────────────────────────────────────────────────┤
│ Embeddings │ Static Analysis │ Chunking │ Graph │ Events   │
└─────────────────────────────────────────────────────────────┘
```

### Module Organization

Phase 20 adds capabilities to existing modules rather than creating new modules:

1. **Code Intelligence** (extend `graph` module)
   - New: Hover information API
   - Uses: Existing `StaticAnalyzer` from Phase 18

2. **Document Intelligence** (extend `resources` module)
   - Extend: PDF extractor for metadata
   - New: Auto-linking service

3. **Graph Intelligence** (extend `graph` module)
   - Extend: Graph service for centrality metrics
   - New: Community detection service
   - New: Visualization service

4. **AI Planning** (new `planning` module)
   - New: Multi-hop agent
   - New: Architecture parser
   - Extend: Repository parser for best practices

5. **MCP Infrastructure** (new `mcp` module)
   - New: MCP server implementation
   - New: Tool registry and invocation


## Components and Interfaces

### 1. Hover Information API

**Location**: `backend/app/modules/graph/router.py` (extend existing)

**New Endpoint**:
```python
@router.get("/code/hover")
async def get_hover_information(
    file_path: str,
    line: int,
    column: int,
    resource_id: int,
    db: Session = Depends(get_db)
) -> HoverInformationResponse
```

**Response Schema**:
```python
class HoverInformationResponse(BaseModel):
    symbol_name: Optional[str]
    symbol_type: Optional[str]  # "function", "class", "variable", etc.
    definition_location: Optional[LocationInfo]
    documentation: Optional[str]
    related_chunks: List[ChunkReference]
    context_lines: List[str]  # Surrounding code lines
```

**Implementation Strategy**:
- Use existing `StaticAnalyzer` to parse AST at position
- Query `DocumentChunk` table for related chunks
- Extract context from resource content
- Cache results with 5-minute TTL

**Performance Target**: <100ms response time

---

### 2. PDF Metadata Extraction (Extension)

**Location**: `backend/app/utils/content_extractor.py` (extend existing)

**Extended Function**:
```python
def extract_content(
    file_path: str,
    content_type: str,
    extract_metadata: bool = True  # NEW parameter
) -> ContentExtractionResult
```

**New Response Fields**:
```python
class ContentExtractionResult:
    text: str  # Existing
    metadata: Dict[str, Any]  # Existing
    # NEW fields:
    page_boundaries: List[PageBoundary]  # [(start_char, end_char, page_num)]
    structured_metadata: StructuredMetadata  # Title, authors, abstract
```

**Implementation Strategy**:
- Use PyPDF2 to extract page-by-page
- Track character offsets for page boundaries
- Extract metadata from PDF info dictionary
- Use heuristics to identify abstract/summary sections

**Performance Target**: <2s for 100-page PDF

---

### 3. Auto-Linking Service

**Location**: `backend/app/modules/resources/service.py` (new service class)

**New Service Class**:
```python
class AutoLinkingService:
    def __init__(self, db: Session, embedding_generator: EmbeddingGenerator):
        self.db = db
        self.embedding_generator = embedding_generator
    
    async def link_pdf_to_code(
        self,
        pdf_resource_id: int,
        similarity_threshold: float = 0.7
    ) -> List[ChunkLink]
    
    async def link_code_to_pdfs(
        self,
        code_resource_id: int,
        similarity_threshold: float = 0.7
    ) -> List[ChunkLink]
```

**Database Schema**:
```python
class ChunkLink(Base):
    __tablename__ = "chunk_links"
    
    id: int
    source_chunk_id: int  # FK to document_chunks
    target_chunk_id: int  # FK to document_chunks
    similarity_score: float
    link_type: str  # "pdf_to_code", "code_to_pdf"
    created_at: datetime
```

**Implementation Strategy**:
1. Query all chunks for source resource
2. Generate embeddings using existing `EmbeddingGenerator`
3. Compute cosine similarity with target chunks
4. Filter by threshold (0.7)
5. Create bidirectional links
6. Emit `chunk.linked` event

**Performance Target**: <5s for 100 PDF chunks

---

### 4. Graph Centrality Metrics (Extension)

**Location**: `backend/app/modules/graph/service.py` (extend existing)

**New Methods**:
```python
class GraphService:
    # Existing methods...
    
    async def compute_degree_centrality(
        self,
        resource_ids: List[int]
    ) -> Dict[int, CentralityMetrics]
    
    async def compute_betweenness_centrality(
        self,
        resource_ids: List[int]
    ) -> Dict[int, float]
    
    async def compute_pagerank(
        self,
        resource_ids: List[int],
        damping_factor: float = 0.85
    ) -> Dict[int, float]
```

**Response Schema**:
```python
class CentralityMetrics(BaseModel):
    in_degree: int
    out_degree: int
    betweenness: float
    pagerank: float
```

**Implementation Strategy**:
- Build NetworkX graph from existing citation data
- Use NetworkX built-in algorithms
- Cache results with 10-minute TTL
- Batch compute for efficiency

**Performance Target**: <2s for 1000 nodes

---

### 5. Community Detection Service

**Location**: `backend/app/modules/graph/service.py` (new service class)

**New Service Class**:
```python
class CommunityDetectionService:
    def __init__(self, db: Session):
        self.db = db
    
    async def detect_communities(
        self,
        resource_ids: List[int],
        resolution: float = 1.0
    ) -> CommunityDetectionResult
```

**Response Schema**:
```python
class CommunityDetectionResult(BaseModel):
    communities: Dict[int, int]  # resource_id -> community_id
    modularity: float
    num_communities: int
    community_sizes: Dict[int, int]  # community_id -> size
```

**Implementation Strategy**:
- Build NetworkX graph from citations
- Apply Louvain algorithm (python-louvain library)
- Compute modularity score
- Cache results with 15-minute TTL

**Performance Target**: <10s for 1000 nodes

---

### 6. Graph Visualization Service

**Location**: `backend/app/modules/graph/service.py` (new service class)

**New Service Class**:
```python
class GraphVisualizationService:
    def __init__(self, db: Session):
        self.db = db
    
    async def compute_layout(
        self,
        resource_ids: List[int],
        layout_type: str,  # "force", "hierarchical", "circular"
        **layout_params
    ) -> GraphLayoutResult
```

**Response Schema**:
```python
class GraphLayoutResult(BaseModel):
    nodes: Dict[int, NodePosition]  # resource_id -> (x, y)
    edges: List[EdgeRouting]
    bounds: BoundingBox  # min/max x/y
```

**Implementation Strategy**:
- Force-directed: NetworkX spring_layout (Fruchterman-Reingold)
- Hierarchical: NetworkX kamada_kawai_layout
- Circular: NetworkX circular_layout
- Normalize coordinates to [0, 1000] range
- Cache layouts with 10-minute TTL

**Performance Target**: <2s for 500 nodes


---

### 7. Multi-Hop Planning Agent

**Location**: `backend/app/modules/planning/` (new module)

**New Service Class**:
```python
class MultiHopAgent:
    def __init__(self, db: Session, llm_client: Any):
        self.db = db
        self.llm_client = llm_client
        self.context_history = []
    
    async def generate_plan(
        self,
        task_description: str,
        context: Dict[str, Any]
    ) -> PlanningResult
    
    async def refine_plan(
        self,
        plan_id: str,
        feedback: str
    ) -> PlanningResult
```

**Response Schema**:
```python
class PlanningResult(BaseModel):
    plan_id: str
    steps: List[PlanningStep]
    dependencies: List[Tuple[int, int]]  # (step_id, depends_on_step_id)
    estimated_duration: str
    context_preserved: Dict[str, Any]

class PlanningStep(BaseModel):
    step_id: int
    description: str
    action_type: str  # "code", "test", "document", "review"
    required_context: List[str]
    success_criteria: str
```

**Implementation Strategy**:
1. Use LLM to break down task into steps
2. Maintain conversation history for context
3. Extract dependencies from step descriptions
4. Store plans in database for refinement
5. Support iterative feedback loop

**Performance Target**: <30s per planning step

---

### 8. Architecture Document Parser

**Location**: `backend/app/modules/planning/` (new module)

**New Service Class**:
```python
class ArchitectureParser:
    def __init__(self, db: Session, llm_client: Any):
        self.db = db
        self.llm_client = llm_client
    
    async def parse_architecture_doc(
        self,
        resource_id: int
    ) -> ArchitectureParseResult
```

**Response Schema**:
```python
class ArchitectureParseResult(BaseModel):
    components: List[Component]
    relationships: List[Relationship]
    patterns: List[DesignPattern]
    gaps: List[ArchitectureGap]

class Component(BaseModel):
    name: str
    description: str
    responsibilities: List[str]
    interfaces: List[str]

class Relationship(BaseModel):
    source: str
    target: str
    relationship_type: str  # "depends_on", "implements", "extends"
    description: str

class DesignPattern(BaseModel):
    pattern_name: str
    pattern_type: str  # "creational", "structural", "behavioral"
    components_involved: List[str]
    confidence: float

class ArchitectureGap(BaseModel):
    gap_type: str  # "missing_component", "undocumented_relationship"
    description: str
    severity: str  # "low", "medium", "high"
```

**Implementation Strategy**:
1. Extract text from architecture document
2. Use LLM to identify components and relationships
3. Pattern matching for common design patterns
4. Compare with actual codebase structure (via `repo_parser`)
5. Identify gaps between documented and implemented

**Performance Target**: <10s for typical architecture doc

---

### 9. Repository Best Practices Detection (Extension)

**Location**: `backend/app/utils/repo_parser.py` (extend existing)

**New Methods**:
```python
class RepositoryParser:
    # Existing methods...
    
    def detect_best_practices(
        self,
        repo_path: str
    ) -> BestPracticesResult
    
    def extract_reusable_components(
        self,
        repo_path: str
    ) -> List[ReusableComponent]
```

**Response Schema**:
```python
class BestPracticesResult(BaseModel):
    patterns: List[CodePattern]
    quality_indicators: Dict[str, float]
    recommendations: List[str]

class CodePattern(BaseModel):
    pattern_type: str  # "error_handling", "testing", "documentation"
    pattern_name: str
    examples: List[CodeExample]
    confidence: float

class ReusableComponent(BaseModel):
    component_name: str
    file_path: str
    interface: str
    usage_examples: List[str]
    dependencies: List[str]
```

**Implementation Strategy**:
1. Use existing AST parsing from `StaticAnalyzer`
2. Pattern matching for common best practices
3. Analyze test coverage and documentation
4. Extract interface definitions
5. Identify reusable utility functions/classes

**Performance Target**: <5s for typical repository

---

### 10. MCP Server Infrastructure

**Location**: `backend/app/modules/mcp/` (new module)

**New Service Class**:
```python
class MCPServer:
    def __init__(self, db: Session):
        self.db = db
        self.tool_registry = ToolRegistry()
        self.session_manager = SessionManager()
    
    async def register_tool(
        self,
        tool_name: str,
        tool_schema: Dict[str, Any],
        handler: Callable
    ) -> None
    
    async def invoke_tool(
        self,
        session_id: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> ToolInvocationResult
    
    async def list_tools(self) -> List[ToolDefinition]
```

**Response Schema**:
```python
class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    requires_auth: bool
    rate_limit: Optional[int]

class ToolInvocationResult(BaseModel):
    success: bool
    result: Any
    error: Optional[str]
    execution_time_ms: int
```

**Tool Registry**:
```python
# Register existing backend capabilities as MCP tools
REGISTERED_TOOLS = [
    "search_resources",
    "get_hover_info",
    "compute_graph_metrics",
    "detect_communities",
    "generate_plan",
    "parse_architecture",
    "link_pdf_to_code",
]
```

**Implementation Strategy**:
1. Define MCP protocol message format
2. Create tool registry with schema validation
3. Implement session management for multi-turn
4. Integrate with existing auth/rate limiting
5. Wrap existing services as MCP tools
6. Add comprehensive logging

**Performance Target**: <50ms overhead per tool invocation


## Data Models

### New Database Tables

#### 1. chunk_links

```python
class ChunkLink(Base):
    __tablename__ = "chunk_links"
    
    id = Column(Integer, primary_key=True, index=True)
    source_chunk_id = Column(Integer, ForeignKey("document_chunks.id"), nullable=False)
    target_chunk_id = Column(Integer, ForeignKey("document_chunks.id"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    link_type = Column(String, nullable=False)  # "pdf_to_code", "code_to_pdf"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    source_chunk = relationship("DocumentChunk", foreign_keys=[source_chunk_id])
    target_chunk = relationship("DocumentChunk", foreign_keys=[target_chunk_id])
    
    # Indexes
    __table_args__ = (
        Index("idx_chunk_links_source", "source_chunk_id"),
        Index("idx_chunk_links_target", "target_chunk_id"),
        Index("idx_chunk_links_similarity", "similarity_score"),
    )
```

**Purpose**: Store bidirectional links between PDF and code chunks based on semantic similarity.

---

#### 2. graph_centrality_cache

```python
class GraphCentralityCache(Base):
    __tablename__ = "graph_centrality_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    in_degree = Column(Integer, nullable=False)
    out_degree = Column(Integer, nullable=False)
    betweenness = Column(Float, nullable=False)
    pagerank = Column(Float, nullable=False)
    computed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resource = relationship("Resource")
    
    # Indexes
    __table_args__ = (
        Index("idx_centrality_resource", "resource_id"),
        Index("idx_centrality_computed", "computed_at"),
    )
```

**Purpose**: Cache centrality metrics to avoid recomputation (10-minute TTL).

---

#### 3. community_assignments

```python
class CommunityAssignment(Base):
    __tablename__ = "community_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    community_id = Column(Integer, nullable=False)
    modularity = Column(Float, nullable=False)
    resolution = Column(Float, nullable=False)
    computed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resource = relationship("Resource")
    
    # Indexes
    __table_args__ = (
        Index("idx_community_resource", "resource_id"),
        Index("idx_community_id", "community_id"),
        Index("idx_community_computed", "computed_at"),
    )
```

**Purpose**: Store community detection results (15-minute TTL).

---

#### 4. planning_sessions

```python
class PlanningSession(Base):
    __tablename__ = "planning_sessions"
    
    id = Column(String, primary_key=True)  # UUID
    task_description = Column(Text, nullable=False)
    context = Column(JSON, nullable=False)
    steps = Column(JSON, nullable=False)  # List of PlanningStep
    dependencies = Column(JSON, nullable=False)  # List of tuples
    status = Column(String, nullable=False)  # "active", "completed", "failed"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_planning_status", "status"),
        Index("idx_planning_created", "created_at"),
    )
```

**Purpose**: Store multi-hop planning sessions for iterative refinement.

---

#### 5. mcp_sessions

```python
class MCPSession(Base):
    __tablename__ = "mcp_sessions"
    
    id = Column(String, primary_key=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    context = Column(JSON, nullable=False)
    tool_invocations = Column(JSON, nullable=False)  # List of invocation records
    status = Column(String, nullable=False)  # "active", "closed"
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index("idx_mcp_user", "user_id"),
        Index("idx_mcp_status", "status"),
        Index("idx_mcp_activity", "last_activity"),
    )
```

**Purpose**: Manage MCP sessions for multi-turn interactions.

---

### Extended Database Tables

#### 1. resources (extend metadata)

**New Metadata Fields**:
```python
# Add to existing metadata JSON field:
{
    "pdf_metadata": {
        "page_boundaries": [(start, end, page_num), ...],
        "title": str,
        "authors": [str, ...],
        "abstract": str,
        "num_pages": int
    }
}
```

**Purpose**: Store structured PDF metadata without schema changes.

---

#### 2. document_chunks (no changes needed)

**Existing Schema** (Phase 17.5):
```python
class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey("resources.id"))
    parent_chunk_id = Column(Integer, ForeignKey("document_chunks.id"), nullable=True)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    metadata = Column(JSON, nullable=False)  # Flexible for PDF pages or code lines
    embedding = Column(Vector(768), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Usage**: Already supports both PDF chunks (with page metadata) and code chunks (with line metadata).


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Hover Information API Properties

**Property 1: Hover response time**
*For any* valid code position (file path, line, column), requesting hover information should return a response within 100ms
**Validates: Requirements 1.1**

**Property 2: Hover response structure**
*For any* code position where a symbol exists, the hover response should include symbol name, type information, and definition location
**Validates: Requirements 1.2**

**Property 3: Related chunks inclusion**
*For any* symbol with related code chunks, the hover response should include references to those Document_Chunk records
**Validates: Requirements 1.3**

**Property 4: Multi-language support**
*For any* code file in Python, JavaScript, TypeScript, Java, C++, Go, or Rust, hover information should be successfully extracted
**Validates: Requirements 1.5**

### PDF Metadata Extraction Properties

**Property 5: Page boundary preservation**
*For any* PDF file, after extraction the page boundary information should accurately map character offsets to page numbers
**Validates: Requirements 2.1**

**Property 6: Metadata extraction completeness**
*For any* PDF with title and author metadata, the extracted metadata should include both title and authors
**Validates: Requirements 2.2, 2.3**

**Property 7: Chunk-to-page mapping**
*For any* PDF resource with chunks, requesting page-level navigation should return accurate chunk-to-page mappings for all chunks
**Validates: Requirements 2.5**

### Auto-Linking Properties

**Property 8: Similarity computation**
*For any* PDF resource ingestion, vector similarity should be computed between all PDF chunks and existing code chunks
**Validates: Requirements 3.1, 3.3**

**Property 9: Threshold-based linking**
*For any* pair of chunks with similarity score above 0.7, a bidirectional link should be created between them
**Validates: Requirements 3.2**

**Property 10: Link metadata storage**
*For any* created link, the database record should include similarity score and link type
**Validates: Requirements 3.4**

**Property 11: Auto-linking performance**
*For any* batch of 100 PDF chunks, auto-linking should complete within 5 seconds
**Validates: Requirements 3.5**

### Graph Centrality Properties

**Property 12: Centrality metrics completeness**
*For any* graph, computing centrality should return in-degree, out-degree, betweenness, and PageRank for all nodes
**Validates: Requirements 4.1, 4.2, 4.3**

**Property 13: Centrality performance**
*For any* graph with 1000 nodes, centrality computation should complete within 2 seconds
**Validates: Requirements 4.4**

**Property 14: Centrality caching**
*For any* graph, computing centrality twice within 10 minutes should use cached results on the second computation
**Validates: Requirements 4.5**

### Community Detection Properties

**Property 15: Community assignment completeness**
*For any* graph, community detection should assign every node to exactly one community
**Validates: Requirements 5.2**

**Property 16: Modularity computation**
*For any* detected community partition, the modularity score should be in the valid range [-1, 1]
**Validates: Requirements 5.3**

**Property 17: Community detection performance**
*For any* graph with 1000 nodes, community detection should complete within 10 seconds
**Validates: Requirements 5.4**

**Property 18: Resolution parameter effect**
*For any* graph, increasing the resolution parameter should result in more communities being detected
**Validates: Requirements 5.5**

### Graph Visualization Properties

**Property 19: Layout coordinate generation**
*For any* graph and layout type (force, hierarchical, circular), all nodes should receive valid x/y coordinates
**Validates: Requirements 6.1, 6.2, 6.3, 6.5**

**Property 20: Visualization performance**
*For any* graph with 500 nodes, layout computation should complete within 2 seconds
**Validates: Requirements 6.4**

### Multi-Hop Agent Properties

**Property 21: Dependency DAG validity**
*For any* generated plan, the task dependencies should form a valid directed acyclic graph (no cycles)
**Validates: Requirements 7.3**

**Property 22: Planning step performance**
*For any* planning step, generation should complete within 30 seconds
**Validates: Requirements 7.4**

### Architecture Parser Properties

**Property 23: Format support**
*For any* architecture document in Markdown, reStructuredText, or plain text format, parsing should successfully extract components
**Validates: Requirements 8.5**

### Repository Parser Properties

**Property 24: Confidence score validity**
*For any* identified best practice, the confidence score should be in the valid range [0, 1]
**Validates: Requirements 9.4**

**Property 25: Language support**
*For any* repository in Python, JavaScript, TypeScript, Java, or Go, pattern detection should successfully identify design patterns
**Validates: Requirements 9.5**

### MCP Server Properties

**Property 26: Schema validation**
*For any* tool invocation request, invalid requests (not matching tool schema) should be rejected with validation error
**Validates: Requirements 10.2**

**Property 27: Tool execution**
*For any* valid tool invocation, the tool should execute and return results within the configured timeout
**Validates: Requirements 10.3**

**Property 28: Authentication enforcement**
*For any* tool requiring authentication, requests without valid JWT tokens should be rejected with 401 status
**Validates: Requirements 10.4**

**Property 29: Rate limiting**
*For any* user exceeding rate limits, subsequent requests should return 429 status with retry-after header
**Validates: Requirements 10.5**

**Property 30: Session context preservation**
*For any* multi-turn MCP session, context from previous tool invocations should be available in subsequent invocations
**Validates: Requirements 10.6**

**Property 31: Invocation logging**
*For any* tool invocation, a log entry should be created with tool name, arguments, result, and execution time
**Validates: Requirements 10.7**


## Error Handling

### API Error Responses

All Phase 20 APIs follow the standard error response format:

```python
class ErrorResponse(BaseModel):
    detail: str
    error_code: str
    timestamp: str
    request_id: str
```

### Error Categories

#### 1. Validation Errors (400)

**Hover Information API**:
- Invalid file path format
- Line/column out of bounds
- Unsupported file type

**Auto-Linking Service**:
- Invalid resource ID
- Invalid similarity threshold (not in [0, 1])

**Graph Services**:
- Invalid resource IDs
- Empty graph (no nodes)
- Invalid layout type

**MCP Server**:
- Invalid tool name
- Schema validation failure
- Invalid session ID

#### 2. Not Found Errors (404)

- Resource not found
- Chunk not found
- Session not found
- Tool not found

#### 3. Authentication Errors (401)

- Missing JWT token
- Invalid JWT token
- Expired JWT token

#### 4. Rate Limiting Errors (429)

- Rate limit exceeded
- Include `Retry-After` header with seconds to wait

#### 5. Timeout Errors (504)

**Hover Information API**: >100ms
**Auto-Linking Service**: >5s for 100 chunks
**Community Detection**: >10s for 1000 nodes
**Graph Visualization**: >2s for 500 nodes
**Planning Agent**: >30s per step

#### 6. Internal Errors (500)

- Database connection failure
- LLM service unavailable
- Unexpected exceptions

### Error Recovery Strategies

#### Retry Logic

- **Transient failures**: Retry with exponential backoff (max 3 attempts)
- **Rate limiting**: Wait for `Retry-After` duration
- **Timeouts**: Increase timeout for next attempt (up to 2x)

#### Graceful Degradation

- **Hover info unavailable**: Return empty context (don't fail)
- **Auto-linking timeout**: Process partial results
- **Community detection failure**: Fall back to simple clustering
- **LLM unavailable**: Return cached results or simplified analysis

#### Circuit Breaker

Use existing `CircuitBreaker` from Phase 19:
- Open circuit after 5 consecutive failures
- Half-open after 30 seconds
- Close after 2 successful requests

### Logging

All errors should be logged with:
- Error type and message
- Request context (user, resource, parameters)
- Stack trace (for 500 errors)
- Performance metrics (execution time)


## Testing Strategy

### Dual Testing Approach

Phase 20 uses both unit tests and property-based tests for comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs
- Together: Unit tests catch concrete bugs, property tests verify general correctness

### Property-Based Testing Configuration

**Library**: `hypothesis` (Python)

**Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with feature name and property number
- Tag format: `# Feature: phase20-frontend-backend-infrastructure, Property N: [property text]`

**Example**:
```python
from hypothesis import given, strategies as st

@given(
    file_path=st.text(min_size=1),
    line=st.integers(min_value=1, max_value=10000),
    column=st.integers(min_value=0, max_value=200)
)
@settings(max_examples=100)
def test_hover_response_time():
    """
    Feature: phase20-frontend-backend-infrastructure
    Property 1: Hover response time
    
    For any valid code position, requesting hover information
    should return a response within 100ms
    """
    start = time.time()
    response = hover_api.get_hover_info(file_path, line, column)
    elapsed = time.time() - start
    
    assert elapsed < 0.1  # 100ms
    assert response.status_code == 200
```

### Test Organization

```
backend/tests/
├── unit/
│   ├── test_hover_api.py
│   ├── test_auto_linking.py
│   ├── test_graph_centrality.py
│   ├── test_community_detection.py
│   ├── test_graph_visualization.py
│   ├── test_planning_agent.py
│   ├── test_architecture_parser.py
│   └── test_mcp_server.py
├── properties/
│   ├── test_hover_properties.py
│   ├── test_auto_linking_properties.py
│   ├── test_graph_properties.py
│   ├── test_planning_properties.py
│   └── test_mcp_properties.py
└── integration/
    ├── test_phase20_e2e.py
    └── test_phase20_performance.py
```

### Unit Test Coverage

**Hover Information API**:
- Valid positions with symbols
- Invalid positions (out of bounds)
- Unsupported file types
- Edge case: Empty files
- Edge case: Very large files (>10K lines)

**PDF Metadata Extraction**:
- PDFs with complete metadata
- PDFs with missing metadata
- Multi-page PDFs
- Edge case: Single-page PDFs
- Edge case: PDFs with no text

**Auto-Linking Service**:
- High similarity (>0.9)
- Threshold boundary (exactly 0.7)
- Low similarity (<0.5)
- Edge case: No existing chunks
- Edge case: Identical content

**Graph Services**:
- Small graphs (10 nodes)
- Medium graphs (100 nodes)
- Large graphs (1000 nodes)
- Edge case: Single node
- Edge case: Disconnected components

**Planning Agent**:
- Simple tasks (1-3 steps)
- Complex tasks (10+ steps)
- Tasks with dependencies
- Edge case: Circular dependencies (should fail)
- Iterative refinement

**MCP Server**:
- Valid tool invocations
- Invalid tool names
- Schema validation failures
- Authentication success/failure
- Rate limiting enforcement
- Session management

### Property Test Coverage

Each correctness property (1-31) should have a corresponding property-based test:

**Performance Properties** (1, 11, 13, 17, 20, 22):
- Generate random valid inputs
- Measure execution time
- Assert time < threshold

**Completeness Properties** (2, 3, 6, 7, 12, 15, 19):
- Generate random valid inputs
- Verify all expected fields are present
- Verify all items are processed

**Correctness Properties** (8, 9, 10, 14, 16, 18, 21, 24, 26-31):
- Generate random valid inputs
- Verify behavior matches specification
- Check invariants hold

**Multi-language Properties** (4, 23, 25):
- Generate code samples in each language
- Verify functionality works for all languages

### Integration Tests

**End-to-End Workflows**:

1. **Code Intelligence Workflow**:
   - Ingest code repository
   - Request hover information
   - Verify chunks are linked
   - Verify performance

2. **Document Intelligence Workflow**:
   - Ingest PDF document
   - Verify metadata extraction
   - Auto-link to existing code
   - Verify links are bidirectional

3. **Graph Intelligence Workflow**:
   - Build citation graph
   - Compute centrality metrics
   - Detect communities
   - Generate visualization layout
   - Verify all metrics are consistent

4. **AI Planning Workflow**:
   - Submit planning request
   - Generate multi-step plan
   - Refine plan with feedback
   - Verify dependencies are valid

5. **MCP Workflow**:
   - Start MCP session
   - Invoke multiple tools
   - Verify context preservation
   - Close session

### Performance Tests

**Benchmarks**:
- Hover API: 1000 requests, measure p50/p95/p99
- Auto-linking: 100 chunks, measure total time
- Centrality: 1000 nodes, measure computation time
- Community detection: 1000 nodes, measure detection time
- Visualization: 500 nodes, measure layout time
- Planning: 10 tasks, measure per-step time

**Load Tests**:
- Concurrent hover requests (100 simultaneous)
- Batch auto-linking (1000 chunks)
- Large graph operations (10K nodes)
- MCP server throughput (100 req/s)

### Test Data

**Golden Data Pattern**:
- Store expected outputs in JSON files
- Never modify tests to match implementation
- Fix implementation to match expectations

**Test Fixtures**:
- Sample code files (Python, JS, TS, Java, Go, Rust)
- Sample PDF documents (with/without metadata)
- Sample graphs (small, medium, large)
- Sample architecture documents
- Sample repositories

### Continuous Integration

**Pre-commit Checks**:
- Run unit tests
- Run property tests (reduced iterations: 20)
- Check code coverage (>80%)

**CI Pipeline**:
- Run full unit test suite
- Run full property test suite (100 iterations)
- Run integration tests
- Run performance benchmarks
- Generate coverage report

**Performance Regression Detection**:
- Compare benchmark results with baseline
- Fail if performance degrades >20%
- Update baseline on intentional changes
