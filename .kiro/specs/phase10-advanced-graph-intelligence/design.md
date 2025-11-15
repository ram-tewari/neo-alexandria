# Design Document - Phase 10: Advanced Graph Intelligence & Literature-Based Discovery

## Overview

Phase 10 transforms Neo Alexandria's knowledge graph from a basic similarity-based system into an advanced graph intelligence platform. This design implements five major capabilities:

1. **Multi-Layer Graph Model**: Supports multiple edge types (citation, co-authorship, subject similarity, temporal, content similarity) with weighted relationships
2. **Graph2Vec Structural Embeddings**: Learns topological patterns using Weisfeiler-Lehman graph labeling and Doc2Vec
3. **Fusion Embeddings**: Combines content-based and structure-based representations for holistic similarity
4. **HNSW Indexing**: Enables sub-100ms k-NN queries on large graphs using hierarchical navigable small world graphs
5. **Literature-Based Discovery (LBD)**: Implements ABC paradigm for hypothesis generation in both open and closed discovery modes

The system builds upon existing Phase 5 graph service, Phase 6 citation network, Phase 4 content embeddings, Phase 8.5 taxonomy, and Phase 9 quality assessment.

### Success Metrics

- 15-50% improvement in neighbor relevance with 2-hop discovery vs 1-hop
- LBD hypothesis generation with 80%+ plausibility (human-evaluated)
- Graph query latency <500ms for 2-hop neighbors on 5,000 node graphs
- HNSW index enables <100ms k-NN queries for 10,000+ node graphs
- Multi-layer graph supports 5 edge types with weighted fusion

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Discovery    │  │ Graph        │  │ Recommendation│         │
│  │ Router       │  │ Router       │  │ Router        │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     Service Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ LBD Service  │  │ Graph        │  │ Graph        │         │
│  │              │  │ Embeddings   │  │ Service      │         │
│  │              │  │ Service      │  │ (Enhanced)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                 │                  │                  │
│         └─────────────────┴──────────────────┘                  │
│                           │                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              HNSW Index (hnswlib)                        │  │
│  │         Fast k-NN on Fusion Embeddings                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     Data Layer (SQLAlchemy)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ GraphEdge    │  │ Graph        │  │ Discovery    │         │
│  │              │  │ Embedding    │  │ Hypothesis   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Resource     │  │ Citation     │  │ Resource     │         │
│  │              │  │              │  │ Taxonomy     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Graph Construction**: Multi-layer graph built from Citations, ResourceTaxonomy, Resource metadata
2. **Embedding Generation**: Graph2Vec processes ego-graphs → structural embeddings
3. **Fusion**: Content embeddings + structural embeddings → fusion embeddings
4. **Indexing**: HNSW index built from fusion embeddings for fast retrieval
5. **Discovery**: LBD service traverses graph to find A→B→C patterns
6. **Validation**: User feedback updates edge weights and hypothesis scores

## Components and Interfaces

### 1. Database Models (app/database/models.py)

#### GraphEdge Model

Stores multi-layer graph edges with type-specific metadata.

```python
class GraphEdge(Base):
    __tablename__ = "graph_edges"
    
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("resources.id", ondelete="CASCADE"))
    target_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("resources.id", ondelete="CASCADE"))
    
    edge_type: Mapped[str] = mapped_column(String(50), nullable=False)  # citation, co_authorship, etc.
    weight: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0-1.0
    
    metadata: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON metadata
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)  # Source system
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0.0-1.0
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.current_timestamp())
    
    # Relationships
    source: Mapped["Resource"] = relationship("Resource", foreign_keys=[source_id])
    target: Mapped["Resource"] = relationship("Resource", foreign_keys=[target_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_graph_edges_source', 'source_id'),
        Index('idx_graph_edges_target', 'target_id'),
        Index('idx_graph_edges_type', 'edge_type'),
        Index('idx_graph_edges_composite', 'source_id', 'target_id', 'edge_type', unique=True),
        CheckConstraint('weight >= 0.0 AND weight <= 1.0', name='check_weight_range'),
    )
```

**Design Rationale**: 
- Unique constraint on (source_id, target_id, edge_type) prevents duplicate edges
- JSON metadata field allows type-specific data without schema changes
- created_by tracks provenance for debugging and auditing


#### GraphEmbedding Model

Stores graph-based embeddings separately from content embeddings.

```python
class GraphEmbedding(Base):
    __tablename__ = "graph_embeddings"
    
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    resource_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("resources.id", ondelete="CASCADE"), unique=True)
    
    structural_embedding: Mapped[List[float] | None] = mapped_column(JSON, nullable=True)  # Graph2Vec
    fusion_embedding: Mapped[List[float] | None] = mapped_column(JSON, nullable=True)  # Combined
    
    embedding_method: Mapped[str] = mapped_column(String(50), nullable=False)  # graph2vec, node2vec, fusion
    embedding_version: Mapped[str] = mapped_column(String(20), nullable=False)  # v1.0
    
    hnsw_index_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # HNSW index position
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.current_timestamp())
    
    # Relationships
    resource: Mapped["Resource"] = relationship("Resource")
    
    # Indexes
    __table_args__ = (
        Index('idx_graph_embeddings_resource', 'resource_id', unique=True),
    )
```

**Design Rationale**:
- Separate table allows independent updates from content embeddings
- hnsw_index_id enables fast lookup in HNSW index
- embedding_version supports A/B testing and gradual rollouts


#### DiscoveryHypothesis Model

Stores LBD hypotheses with supporting evidence.

```python
class DiscoveryHypothesis(Base):
    __tablename__ = "discovery_hypotheses"
    
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    
    # ABC components
    a_resource_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("resources.id", ondelete="CASCADE"))
    c_resource_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("resources.id", ondelete="CASCADE"))
    b_resource_ids: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array of UUIDs
    
    # Hypothesis metadata
    hypothesis_type: Mapped[str] = mapped_column(String(20), nullable=False)  # open, closed
    plausibility_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0-1.0
    
    # Supporting evidence
    path_strength: Mapped[float] = mapped_column(Float, nullable=False)  # Product of edge weights
    path_length: Mapped[int] = mapped_column(Integer, nullable=False)  # Number of hops
    common_neighbors: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Discovery metadata
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.current_timestamp())
    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_validated: Mapped[bool | None] = mapped_column(Integer, nullable=True)  # SQLite: 0/1
    validation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    a_resource: Mapped["Resource"] = relationship("Resource", foreign_keys=[a_resource_id])
    c_resource: Mapped["Resource"] = relationship("Resource", foreign_keys=[c_resource_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_discovery_a_c', 'a_resource_id', 'c_resource_id'),
        Index('idx_discovery_type', 'hypothesis_type'),
        Index('idx_discovery_plausibility', 'plausibility_score'),
        CheckConstraint('plausibility_score >= 0.0 AND plausibility_score <= 1.0', name='check_plausibility_range'),
    )
```

**Design Rationale**:
- Composite index on (a_resource_id, c_resource_id) enables fast duplicate detection
- b_resource_ids as JSON array supports variable-length paths
- is_validated allows filtering validated/unvalidated hypotheses


### 2. Enhanced Graph Service (app/services/graph_service.py)

Extends existing GraphService with multi-layer graph and 2-hop neighbor discovery.

#### Multi-Layer Graph Construction

```python
def build_multilayer_graph(self, refresh_cache: bool = False) -> nx.MultiDiGraph:
    """
    Build multi-layer directed multigraph from database.
    
    Algorithm:
    1. Create NetworkX MultiDiGraph (supports multiple edge types)
    2. Add all resources as nodes with metadata (title, year, quality)
    3. Layer 1: Citation edges from Citation table
    4. Layer 2: Co-authorship edges (resources sharing authors)
    5. Layer 3: Subject similarity edges (shared taxonomy nodes)
    6. Layer 4: Temporal edges (same publication year)
    7. Layer 5: Content similarity edges (high embedding similarity)
    8. Cache graph with timestamp for invalidation
    
    Returns: NetworkX MultiDiGraph with ~5,000-10,000 nodes
    """
```

**Edge Type Weights**:
- Citation: 1.0 (binary, strong signal)
- Co-authorship: 1.0 / num_shared_authors (penalize prolific authors)
- Subject similarity: 0.5 (moderate signal)
- Temporal: 0.3 (weak signal)
- Content similarity: cosine_similarity (0.0-1.0)

**Performance Optimization**:
- Limit co-authorship edges to 50 resources per author
- Limit subject similarity edges to 10 connections per resource
- Limit temporal edges to 5 connections per resource
- Cache graph in memory, invalidate on edge updates


#### Two-Hop Neighbor Discovery

```python
def get_neighbors_multihop(
    self,
    resource_id: str,
    hops: int = 2,
    edge_types: List[str] = None,
    min_weight: float = 0.0,
    limit: int = 50
) -> List[Dict]:
    """
    Discover multi-hop neighbors with intelligent filtering.
    
    Algorithm:
    1. Build/retrieve cached graph
    2. BFS traversal for specified hop count (1 or 2)
    3. For each path, compute path_strength = product of edge weights
    4. Rank neighbors by combined score:
       - path_strength (50%)
       - resource quality from Phase 9 (30%)
       - novelty = 1/(1 + log(degree)) (20%)
    5. Return top-K neighbors with path metadata
    
    Returns: List of dicts with resource, distance, path, score
    """
```

**Ranking Formula**:
```
score = 0.5 * path_strength + 0.3 * quality_overall + 0.2 * novelty
novelty = 1.0 / (1 + log(node_degree + 1))
```

**Design Rationale**:
- Path strength rewards strong connections
- Quality score from Phase 9 ensures high-quality recommendations
- Novelty score prevents over-recommending highly connected hubs
- Edge type filtering enables domain-specific exploration (e.g., citations only)


### 3. Graph Embeddings Service (app/services/graph_embeddings_service.py)

New service for structural embeddings and fusion.

#### Graph2Vec Implementation

```python
def compute_graph2vec_embeddings(
    self,
    dimensions: int = 128,
    wl_iterations: int = 2
):
    """
    Compute Graph2Vec structural embeddings.
    
    Algorithm (Graph2Vec):
    1. For each node, extract 2-hop ego graph
    2. Run Weisfeiler-Lehman graph labeling (2 iterations)
       - Iteration 1: Label nodes by degree
       - Iteration 2: Label nodes by neighbor labels
    3. Treat labeled subgraph as "document"
    4. Apply Doc2Vec (via karateclub library)
    5. Store 128-dimensional embeddings in graph_embeddings table
    
    Performance: ~100 nodes/minute on standard hardware
    """
```

**Weisfeiler-Lehman Intuition**:
- Captures local graph structure through iterative labeling
- Similar structural roles → similar labels → similar embeddings
- Example: Two "bridge" nodes connecting clusters get similar embeddings

**Library Choice**: karateclub
- Mature implementation of Graph2Vec
- Handles directed/undirected graphs
- Configurable dimensions and WL iterations


#### Fusion Embeddings

```python
def compute_fusion_embeddings(self, alpha: float = 0.5):
    """
    Combine content and structural embeddings.
    
    Algorithm:
    1. For each resource with both content and structural embeddings:
       - content_vec = Resource.embedding (from Phase 4)
       - graph_vec = GraphEmbedding.structural_embedding
    2. Handle dimension mismatch by truncating to min(len(content), len(graph))
    3. Compute fusion: fusion_vec = alpha * content_vec + (1-alpha) * graph_vec
    4. Normalize to unit length: fusion_vec = fusion_vec / ||fusion_vec||
    5. Store in GraphEmbedding.fusion_embedding
    
    Default alpha=0.5 gives equal weight to content and structure
    """
```

**Fusion Benefits**:
- Content embeddings: Semantic similarity (what resources say)
- Structural embeddings: Positional similarity (how resources connect)
- Fusion: Holistic similarity (both dimensions)

**Use Cases**:
- alpha=0.7: Prioritize content (semantic search)
- alpha=0.5: Balanced (general recommendations)
- alpha=0.3: Prioritize structure (find structurally similar papers)


#### HNSW Indexing

```python
def build_hnsw_index(self, ef_construction: int = 200, M: int = 16):
    """
    Build HNSW index for fast k-NN queries.
    
    Algorithm:
    1. Query all GraphEmbedding records with fusion_embedding
    2. Initialize hnswlib index:
       - space='cosine'
       - dim=embedding_dimension
       - ef_construction=200 (build quality)
       - M=16 (connections per layer)
    3. Add embeddings to index with resource_id as label
    4. Store index to disk: hnsw_index_phase10.bin
    5. Update GraphEmbedding.hnsw_index_id with position
    
    Performance: <100ms k-NN queries on 10,000+ nodes
    """
```

**HNSW Parameters**:
- ef_construction=200: Higher = better quality, slower build
- M=16: Higher = more connections, better recall, more memory
- space='cosine': Matches embedding similarity metric

**Index Persistence**:
- Save to disk for fast startup
- Rebuild on significant graph changes (>10% new nodes)
- Support incremental updates for small changes


### 4. Literature-Based Discovery Service (app/services/lbd_service.py)

New service implementing ABC paradigm for hypothesis generation.

#### Open Discovery

```python
def open_discovery(
    self,
    a_resource_id: str,
    limit: int = 20,
    min_plausibility: float = 0.5
) -> List[Dict]:
    """
    Discover related concepts from starting point A.
    
    Algorithm (ABC Paradigm):
    1. Find all B resources connected to A (1-hop neighbors)
    2. For each B, find all C resources connected to B (2-hop from A)
    3. Exclude C resources already connected to A (no direct A→C edge)
    4. For each A→B→C path:
       - path_strength = weight(A→B) * weight(B→C)
       - common_neighbors = |neighbors(A) ∩ neighbors(C)|
       - semantic_similarity = cosine(embedding_A, embedding_C)
    5. Compute plausibility:
       plausibility = 0.4 * path_strength + 0.3 * common_neighbors_norm + 0.3 * semantic_similarity
    6. Filter by min_plausibility threshold
    7. Rank by plausibility, return top-K
    8. Store hypotheses in discovery_hypotheses table
    
    Returns: List of hypothesis dicts with C resources and evidence
    """
```

**Plausibility Scoring**:
- Path strength (40%): Strong A→B→C connections
- Common neighbors (30%): Shared context between A and C
- Semantic similarity (30%): Content-based relevance

**Example**:
- A = "Machine Learning" paper
- B = "Neural Networks" paper (cites A)
- C = "Deep Learning" paper (cited by B, not directly connected to A)
- Hypothesis: A and C are related through neural networks


#### Closed Discovery

```python
def closed_discovery(
    self,
    a_resource_id: str,
    c_resource_id: str,
    max_hops: int = 3
) -> List[Dict]:
    """
    Find connecting paths between two known concepts A and C.
    
    Algorithm:
    1. Check if direct A→C edge exists (return immediately if so)
    2. Find all 2-hop paths A→B→C:
       - For each neighbor B of A
       - Check if B connects to C
       - Compute path_strength = weight(A→B) * weight(B→C)
    3. If no 2-hop paths, try 3-hop paths A→B1→B2→C (with penalty)
    4. For each path:
       - common_neighbors = |neighbors(A) ∩ neighbors(C)|
       - semantic_similarity = cosine(embedding_A, embedding_C)
    5. Compute plausibility with hop penalty:
       base_plausibility = 0.4 * path_strength + 0.3 * common_neighbors_norm + 0.3 * semantic_similarity
       plausibility = base_plausibility * (0.5 ^ (hops - 2))
    6. Rank by plausibility, return all paths
    7. Store best hypothesis in discovery_hypotheses table
    
    Returns: List of path dicts with intermediate B resources and evidence
    """
```

**Hop Penalty**:
- 2-hop: No penalty (plausibility * 1.0)
- 3-hop: 50% penalty (plausibility * 0.5)
- 4-hop: 25% penalty (plausibility * 0.25)

**Example**:
- A = "Quantum Computing" paper
- C = "Cryptography" paper
- B = "Shor's Algorithm" paper (connects both)
- Hypothesis: Quantum computing relates to cryptography through Shor's algorithm


### 5. Discovery API Router (app/routers/discovery.py)

New FastAPI router for discovery endpoints.

```python
@router.get("/discovery/open")
async def open_discovery_endpoint(
    resource_id: str,
    limit: int = 20,
    min_plausibility: float = 0.5,
    db: Session = Depends(get_db)
):
    """
    Open discovery from starting resource.
    
    Query Parameters:
    - resource_id: UUID of starting resource A
    - limit: Max hypotheses to return (default 20)
    - min_plausibility: Minimum plausibility threshold (default 0.5)
    
    Returns: {
        "hypotheses": [
            {
                "c_resource": {...},
                "b_resources": [{...}],
                "plausibility_score": 0.75,
                "path_strength": 0.8,
                "common_neighbors": 5,
                "semantic_similarity": 0.7
            }
        ]
    }
    """

@router.post("/discovery/closed")
async def closed_discovery_endpoint(
    request: ClosedDiscoveryRequest,
    db: Session = Depends(get_db)
):
    """
    Closed discovery connecting two resources.
    
    Request Body: {
        "a_resource_id": "uuid",
        "c_resource_id": "uuid",
        "max_hops": 3
    }
    
    Returns: {
        "paths": [
            {
                "b_resources": [{...}],
                "path_length": 2,
                "plausibility_score": 0.82,
                "path_strength": 0.9
            }
        ]
    }
    """
```


```python
@router.get("/graph/resources/{resource_id}/neighbors")
async def get_multihop_neighbors(
    resource_id: str,
    hops: int = Query(2, ge=1, le=2),
    edge_types: Optional[List[str]] = Query(None),
    min_weight: float = Query(0.0, ge=0.0, le=1.0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get multi-hop neighbors with filtering.
    
    Query Parameters:
    - hops: Number of hops (1 or 2)
    - edge_types: Filter by edge types (e.g., ["citation", "co_authorship"])
    - min_weight: Minimum edge weight threshold
    - limit: Max neighbors to return
    
    Returns: {
        "neighbors": [
            {
                "resource": {...},
                "distance": 2,
                "path": ["uuid_a", "uuid_b", "uuid_c"],
                "path_strength": 0.75,
                "edge_types": ["citation", "subject_similarity"],
                "score": 0.82,
                "intermediate": "uuid_b"
            }
        ]
    }
    """

@router.get("/discovery/hypotheses")
async def list_hypotheses(
    hypothesis_type: Optional[str] = None,
    is_validated: Optional[bool] = None,
    min_plausibility: float = 0.0,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List discovery hypotheses with filtering."""

@router.post("/discovery/hypotheses/{hypothesis_id}/validate")
async def validate_hypothesis(
    hypothesis_id: str,
    validation: HypothesisValidation,
    db: Session = Depends(get_db)
):
    """
    Validate or reject a hypothesis.
    
    Request Body: {
        "is_valid": true,
        "notes": "Confirmed through manual review"
    }
    
    Side Effects:
    - Updates hypothesis.is_validated
    - If valid, increases edge weights along path by 10%
    """
```


## Data Models

### Edge Type Specifications

| Edge Type | Source | Weight Calculation | Metadata Fields |
|-----------|--------|-------------------|-----------------|
| citation | Citation table | 1.0 (binary) | citation_type, context_snippet |
| co_authorship | Resource.authors | 1.0 / num_shared_authors | shared_authors: ["name1", "name2"] |
| subject_similarity | ResourceTaxonomy | 0.5 (fixed) | shared_taxonomy_nodes: ["uuid1", "uuid2"] |
| temporal | Resource.publication_year | 0.3 (fixed) | year: 2023 |
| content_similarity | Resource.embedding | cosine_similarity | similarity_score: 0.85 |

### Embedding Dimensions

- Content embeddings (Phase 4): 768 dimensions (nomic-embed-text-v1)
- Structural embeddings (Graph2Vec): 128 dimensions (configurable)
- Fusion embeddings: min(768, 128) = 128 dimensions (truncated to match)

**Dimension Mismatch Handling**:
```python
if len(content_vec) != len(graph_vec):
    target_dim = min(len(content_vec), len(graph_vec))
    content_vec = content_vec[:target_dim]
    graph_vec = graph_vec[:target_dim]
```

### Hypothesis Plausibility Formula

```
plausibility = w1 * path_strength + w2 * common_neighbors_norm + w3 * semantic_similarity

where:
  path_strength = product of edge weights along path
  common_neighbors_norm = common_neighbors / max(degree(A), degree(C))
  semantic_similarity = cosine(embedding_A, embedding_C)
  w1 = 0.4, w2 = 0.3, w3 = 0.3 (default weights)
  
For 3+ hop paths:
  plausibility = plausibility * (0.5 ^ (hops - 2))
```


## Error Handling

### Graph Construction Errors

**Scenario**: Resource missing required metadata (authors, taxonomy, etc.)
- **Handling**: Skip edge creation for that resource, log warning
- **Recovery**: Edges auto-created when metadata added

**Scenario**: Circular dependencies in graph construction
- **Handling**: NetworkX handles cycles naturally in directed graphs
- **Prevention**: No special handling needed

### Embedding Computation Errors

**Scenario**: Graph2Vec fails on disconnected components
- **Handling**: Process each connected component separately
- **Fallback**: Use content embeddings only for isolated nodes

**Scenario**: Out of memory during embedding computation
- **Handling**: Process in batches of 100 nodes
- **Recovery**: Resume from last successful batch

### Discovery Errors

**Scenario**: No paths found between A and C
- **Response**: Return empty paths list with explanation
- **HTTP Status**: 200 OK (not an error, just no results)

**Scenario**: Resource not found
- **Response**: {"error": "Resource not found"}
- **HTTP Status**: 404 Not Found

**Scenario**: Invalid hypothesis_type parameter
- **Response**: {"error": "hypothesis_type must be 'open' or 'closed'"}
- **HTTP Status**: 400 Bad Request


## Testing Strategy

### Unit Tests

**Multi-Layer Graph Construction** (test_graph_service.py)
- Test citation edge creation from Citation records
- Test co-authorship edge creation with shared authors
- Test subject similarity edge creation from taxonomy
- Test temporal edge creation for same-year resources
- Test graph caching and invalidation
- Test edge weight calculations for each type

**2-Hop Neighbor Discovery** (test_graph_service.py)
- Test 1-hop neighbor retrieval
- Test 2-hop neighbor retrieval with path tracking
- Test edge type filtering (citations only, etc.)
- Test min_weight threshold filtering
- Test ranking by combined score (path_strength + quality + novelty)
- Test limit parameter enforcement

**Graph2Vec Embeddings** (test_graph_embeddings_service.py)
- Test ego graph extraction (2-hop radius)
- Test embedding generation for small graph (10 nodes)
- Test embedding storage in graph_embeddings table
- Test embedding dimension consistency (128)
- Test handling of disconnected components

**Fusion Embeddings** (test_graph_embeddings_service.py)
- Test fusion computation with equal weights (alpha=0.5)
- Test dimension mismatch handling (truncation)
- Test normalization to unit length
- Test fusion with missing content embeddings
- Test fusion with missing structural embeddings

**HNSW Indexing** (test_graph_embeddings_service.py)
- Test index building from fusion embeddings
- Test k-NN query performance (<100ms for 1000 nodes)
- Test index persistence to disk
- Test incremental index updates
- Test query accuracy (recall@10 > 0.9)


**LBD Open Discovery** (test_lbd_service.py)
- Test A→B→C path discovery
- Test exclusion of direct A→C connections
- Test plausibility scoring formula
- Test min_plausibility filtering
- Test hypothesis storage in database
- Test ranking by plausibility

**LBD Closed Discovery** (test_lbd_service.py)
- Test 2-hop path finding between A and C
- Test 3-hop path finding with penalty
- Test path strength calculation
- Test common neighbor counting
- Test hypothesis storage with path metadata
- Test handling of no paths found

### Integration Tests

**End-to-End Discovery Workflow** (test_discovery_integration.py)
1. Create test resources with metadata
2. Build multi-layer graph
3. Compute Graph2Vec embeddings
4. Compute fusion embeddings
5. Build HNSW index
6. Perform open discovery
7. Validate hypothesis
8. Verify edge weight updates

**Recommendation Integration** (test_recommendation_integration.py)
- Test 2-hop neighbors included in recommendations
- Test fusion embeddings used for similarity
- Test graph-based vs content-based weighting (30/70)
- Test hypothesis-based recommendations

### Performance Tests

**Graph Query Latency** (test_graph_performance.py)
- 2-hop neighbor query on 5,000 node graph: <500ms
- HNSW k-NN query on 10,000 node graph: <100ms
- Multi-layer graph construction for 10,000 resources: <30s
- Graph2Vec embedding computation: >100 nodes/minute

**Memory Usage** (test_graph_performance.py)
- Multi-layer graph cache: <500MB for 10,000 nodes
- HNSW index: <200MB for 10,000 nodes with 128-dim embeddings
- Graph2Vec computation: <2GB peak memory


### API Endpoint Tests

**Discovery Endpoints** (test_discovery_api.py)
- GET /discovery/open: Success with valid resource_id
- GET /discovery/open: 404 for non-existent resource
- GET /discovery/open: Empty results for isolated resource
- POST /discovery/closed: Success with valid A and C
- POST /discovery/closed: Multiple paths returned
- GET /graph/resources/{id}/neighbors: 1-hop and 2-hop queries
- GET /graph/resources/{id}/neighbors: Edge type filtering
- GET /discovery/hypotheses: Pagination and filtering
- POST /discovery/hypotheses/{id}/validate: Success and edge weight update

## Dependencies

### Python Packages

```
# Graph algorithms and embeddings
networkx>=3.0
karateclub>=1.3.0  # Graph2Vec implementation
hnswlib>=0.7.0     # HNSW indexing

# Existing dependencies
numpy>=1.24.0
sqlalchemy>=2.0.0
fastapi>=0.100.0
pydantic>=2.0.0
```

### Installation

```bash
pip install networkx karateclub hnswlib
```

### Library Justifications

**networkx**: Industry-standard graph library, excellent MultiDiGraph support
**karateclub**: Mature graph embedding library with Graph2Vec, Node2Vec, etc.
**hnswlib**: Fast HNSW implementation, 10-100x faster than brute-force k-NN


## Integration Points

### Phase 5 Integration (Knowledge Graph)

- **Extends**: GraphService with multi-layer graph construction
- **Preserves**: Existing hybrid scoring for 1-hop neighbors
- **Adds**: 2-hop neighbor discovery, edge type filtering

### Phase 6 Integration (Citation Network)

- **Uses**: Citation table for citation edges
- **Extends**: Citation importance scores inform edge weights
- **Adds**: Citation-based path discovery in LBD

### Phase 4 Integration (Content Embeddings)

- **Uses**: Resource.embedding for content similarity edges
- **Combines**: Content embeddings with structural embeddings in fusion
- **Preserves**: Existing embedding generation pipeline

### Phase 8.5 Integration (Taxonomy)

- **Uses**: ResourceTaxonomy for subject similarity edges
- **Leverages**: Taxonomy hierarchy for weighted connections
- **Adds**: Taxonomy-based path discovery

### Phase 9 Integration (Quality Assessment)

- **Uses**: Resource.quality_overall in neighbor ranking
- **Ensures**: High-quality resources prioritized in discovery
- **Adds**: Quality-weighted plausibility scoring

### Recommendation Service Integration

```python
# In app/services/recommendation_service.py

def get_recommendations(self, resource_id: str, limit: int = 10):
    # Existing content-based recommendations (70% weight)
    content_recs = self._get_content_based_recommendations(resource_id, limit * 2)
    
    # NEW: Graph-based recommendations (30% weight)
    graph_recs = self._get_graph_based_recommendations(resource_id, limit * 2)
    
    # Combine and re-rank
    combined = self._combine_recommendations(content_recs, graph_recs, weights=[0.7, 0.3])
    
    return combined[:limit]

def _get_graph_based_recommendations(self, resource_id: str, limit: int):
    # Use 2-hop neighbors from graph service
    neighbors = graph_service.get_neighbors_multihop(resource_id, hops=2, limit=limit)
    
    # Include LBD hypotheses
    hypotheses = lbd_service.open_discovery(resource_id, limit=10)
    
    # Combine and rank by score
    return self._rank_graph_candidates(neighbors, hypotheses)
```


## Performance Considerations

### Graph Caching Strategy

**Cache Key**: Graph structure hash (based on edge count and last update timestamp)
**Cache Invalidation**: 
- Automatic: When new edges added (>10% change)
- Manual: Admin endpoint to force rebuild
- TTL: 24 hours for safety

**Memory Management**:
- Limit cached graph to 10,000 nodes
- For larger graphs, use database queries instead of in-memory graph
- Implement LRU cache for frequently accessed subgraphs

### Batch Processing

**Graph2Vec Computation**:
- Process 100 nodes per batch
- Commit embeddings every 100 nodes
- Progress logging every 100 nodes
- Estimated time: 10 minutes for 1,000 nodes

**HNSW Index Building**:
- Add embeddings in batches of 1,000
- Save index to disk every 5,000 additions
- Estimated time: 2 minutes for 10,000 nodes

### Query Optimization

**2-Hop Neighbor Discovery**:
- Use NetworkX BFS (optimized C implementation)
- Limit intermediate nodes to top 50 by edge weight
- Early termination when limit reached

**LBD Path Finding**:
- Use bidirectional search for closed discovery
- Prune paths with path_strength < 0.1
- Limit to 100 candidate paths before ranking


## Security Considerations

### Access Control

- Discovery endpoints require authentication (existing auth middleware)
- Hypothesis validation requires user_id tracking
- Private resources excluded from graph construction (respect visibility)

### Input Validation

- resource_id: Validate UUID format
- hops: Limit to 1-2 (prevent expensive queries)
- limit: Cap at 100 (prevent DoS)
- edge_types: Validate against allowed types
- min_weight: Validate range [0.0, 1.0]

### Rate Limiting

- Discovery endpoints: 10 requests/minute per user
- Graph neighbor queries: 30 requests/minute per user
- Hypothesis validation: 5 requests/minute per user

## Monitoring and Observability

### Metrics to Track

- Graph construction time (target: <30s for 10,000 resources)
- 2-hop query latency (target: <500ms)
- HNSW query latency (target: <100ms)
- Graph2Vec computation rate (target: >100 nodes/minute)
- Hypothesis plausibility distribution (monitor quality)
- Validation rate (% of hypotheses validated by users)

### Logging

- Graph cache hits/misses
- Discovery query parameters and result counts
- Hypothesis generation events
- Validation events with user feedback
- Performance warnings (slow queries >1s)

### Alerts

- Graph construction failures
- HNSW index corruption
- Discovery queries timing out (>5s)
- Memory usage >80% during embedding computation


## Migration Strategy

### Database Migration

```python
# alembic/versions/xxx_add_multilayer_graph_and_lbd_phase10.py

def upgrade():
    # Create graph_edges table
    op.create_table(
        'graph_edges',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('source_id', GUID(), nullable=False),
        sa.Column('target_id', GUID(), nullable=False),
        sa.Column('edge_type', sa.String(50), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(100), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['source_id'], ['resources.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_id'], ['resources.id'], ondelete='CASCADE'),
        sa.CheckConstraint('weight >= 0.0 AND weight <= 1.0', name='check_weight_range')
    )
    
    # Create indexes
    op.create_index('idx_graph_edges_source', 'graph_edges', ['source_id'])
    op.create_index('idx_graph_edges_target', 'graph_edges', ['target_id'])
    op.create_index('idx_graph_edges_type', 'graph_edges', ['edge_type'])
    op.create_index('idx_graph_edges_composite', 'graph_edges', ['source_id', 'target_id', 'edge_type'], unique=True)
    
    # Create graph_embeddings table
    op.create_table(
        'graph_embeddings',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('resource_id', GUID(), nullable=False),
        sa.Column('structural_embedding', sa.JSON(), nullable=True),
        sa.Column('fusion_embedding', sa.JSON(), nullable=True),
        sa.Column('embedding_method', sa.String(50), nullable=False),
        sa.Column('embedding_version', sa.String(20), nullable=False),
        sa.Column('hnsw_index_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['resource_id'], ['resources.id'], ondelete='CASCADE')
    )
    
    op.create_index('idx_graph_embeddings_resource', 'graph_embeddings', ['resource_id'], unique=True)
```

    
    # Create discovery_hypotheses table
    op.create_table(
        'discovery_hypotheses',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('a_resource_id', GUID(), nullable=False),
        sa.Column('c_resource_id', GUID(), nullable=False),
        sa.Column('b_resource_ids', sa.Text(), nullable=False),
        sa.Column('hypothesis_type', sa.String(20), nullable=False),
        sa.Column('plausibility_score', sa.Float(), nullable=False),
        sa.Column('path_strength', sa.Float(), nullable=False),
        sa.Column('path_length', sa.Integer(), nullable=False),
        sa.Column('common_neighbors', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('discovered_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp()),
        sa.Column('user_id', sa.String(255), nullable=True),
        sa.Column('is_validated', sa.Integer(), nullable=True),
        sa.Column('validation_notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['a_resource_id'], ['resources.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['c_resource_id'], ['resources.id'], ondelete='CASCADE'),
        sa.CheckConstraint('plausibility_score >= 0.0 AND plausibility_score <= 1.0', name='check_plausibility_range')
    )
    
    op.create_index('idx_discovery_a_c', 'discovery_hypotheses', ['a_resource_id', 'c_resource_id'])
    op.create_index('idx_discovery_type', 'discovery_hypotheses', ['hypothesis_type'])
    op.create_index('idx_discovery_plausibility', 'discovery_hypotheses', ['plausibility_score'])

def downgrade():
    op.drop_table('discovery_hypotheses')
    op.drop_table('graph_embeddings')
    op.drop_table('graph_edges')
```

### Data Population

**Initial Graph Construction**:
1. Run migration to create tables
2. Execute graph construction script:
   ```bash
   python scripts/build_initial_graph.py
   ```
3. Compute Graph2Vec embeddings (background task):
   ```bash
   python scripts/compute_graph_embeddings.py
   ```
4. Build HNSW index:
   ```bash
   python scripts/build_hnsw_index.py
   ```

**Estimated Time**: 30-60 minutes for 5,000 resources


## Future Enhancements

### Phase 10.5 Potential Features

1. **Temporal Graph Analysis**
   - Track graph evolution over time
   - Identify emerging research trends
   - Predict future connections

2. **Advanced Embedding Methods**
   - Node2Vec for random walk-based embeddings
   - GraphSAGE for inductive learning
   - Attention-based graph embeddings

3. **Interactive Discovery**
   - User-guided exploration (expand specific B nodes)
   - Hypothesis refinement based on feedback
   - Collaborative filtering for discovery

4. **Graph Visualization**
   - Interactive D3.js visualization
   - Multi-layer graph rendering
   - Path highlighting for hypotheses

5. **Automated Hypothesis Testing**
   - Semantic similarity validation
   - Citation pattern analysis
   - Co-occurrence statistics

## Design Decisions and Rationale

### Why MultiDiGraph?

- Supports multiple edge types between same nodes
- Directed edges capture asymmetric relationships (citations)
- NetworkX provides efficient algorithms

### Why Graph2Vec over Node2Vec?

- Graph2Vec captures subgraph patterns (better for structural similarity)
- Node2Vec focuses on node neighborhoods (better for node classification)
- For LBD, we need structural patterns → Graph2Vec

### Why HNSW over FAISS?

- HNSW: Simpler, no GPU required, excellent for <100k nodes
- FAISS: Better for >1M nodes, requires GPU for best performance
- Neo Alexandria: <10k nodes expected → HNSW sufficient

### Why 2-Hop Limit?

- 1-hop: Too restrictive, misses serendipitous connections
- 2-hop: Sweet spot for discovery (A→B→C paradigm)
- 3-hop: Exponential explosion, low signal-to-noise ratio
- Compromise: Allow 3-hop in closed discovery with penalty

### Why Separate Structural and Fusion Embeddings?

- Flexibility: Can use structural-only or content-only
- Debugging: Can compare structural vs content similarity
- Experimentation: Can adjust fusion weights (alpha parameter)
- Storage: Minimal overhead (~256 floats per resource)
