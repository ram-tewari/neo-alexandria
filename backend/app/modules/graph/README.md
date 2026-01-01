# Graph Module

## Purpose

The Graph module provides knowledge graph, citation network, and literature-based discovery (LBD) functionality for Neo Alexandria 2.0. It enables relationship analysis, citation extraction, and hypothesis discovery across the resource collection.

## Features

### Knowledge Graph
- Build and maintain resource relationship graph
- Graph-based similarity and recommendation
- Multi-layer graph analysis
- Graph embeddings for enhanced discovery

### Graph Embeddings (Task 11 - Phase 16.7)
- **Node2Vec**: Biased random walk embeddings with configurable p and q parameters
- **DeepWalk**: Unbiased random walk embeddings (Node2Vec with p=1, q=1)
- **Configurable dimensions**: 32-512 dimensional embeddings
- **In-memory caching**: Fast retrieval with 5-minute TTL
- **Similarity search**: Cosine similarity-based node discovery
- **Performance**: <10s for 1000 nodes, <100ms for similarity search

### Citation Network
- Automatic citation extraction from resources
- Citation network analysis
- Citation-based recommendations
- Citation impact metrics

### Literature-Based Discovery (LBD) (Task 12 - Phase 16.7)
- **ABC pattern discovery**: Find bridging concepts (A→B, B→C implies A→C)
- **Hypothesis generation**: Rank hypotheses by support and novelty
- **Cross-domain connection discovery**: Identify novel relationships
- **Temporal analysis**: Time-slicing for publication date filtering
- **Evidence chains**: Build supporting evidence for hypotheses
- **Performance**: <5s for hypothesis discovery

## Public Interface

### Routers
- `graph_router`: Main graph endpoints (`/graph/*`)
- `citations_router`: Citation network endpoints (`/citations/*`)
- `discovery_router`: LBD endpoints (`/discovery/*`)

### Services
- `GraphService`: Core graph operations
- `AdvancedGraphService`: Advanced graph intelligence (Phase 10)
- `GraphEmbeddingsService`: Graph embedding generation
- `CitationService`: Citation extraction and analysis
- `LBDService`: Literature-based discovery

### Schemas
- Graph-related request/response schemas
- Citation schemas
- Discovery and hypothesis schemas

### Models
- `GraphEdge`: Graph relationship edges
- `GraphEmbedding`: Graph node embeddings
- `Citation`: Citation records
- `DiscoveryHypothesis`: LBD hypotheses

## Events

### Emitted Events
- `citation.extracted`: When citations are extracted from a resource
  - Payload: `{resource_id, citations: List[Citation]}`
- `graph.updated`: When the knowledge graph is updated
  - Payload: `{resource_id, edge_count, node_count}`
- `hypothesis.discovered`: When LBD discovers new hypotheses
  - Payload: `{hypothesis: DiscoveryHypothesis, confidence: float}`

### Subscribed Events
- `resource.created`: Extract citations and add to graph
- `resource.deleted`: Remove from graph and update relationships

## Dependencies

### Shared Kernel
- `shared.database`: Database session management
- `shared.embeddings`: Embedding generation for graph nodes
- `shared.event_bus`: Event-driven communication

### External
- NetworkX: Graph algorithms
- FAISS: Vector similarity for graph embeddings

## Usage Examples

### Graph Embeddings

```python
from app.modules.graph import GraphEmbeddingsService

# Initialize service
embeddings_service = GraphEmbeddingsService(db)

# Generate Node2Vec embeddings
result = await embeddings_service.generate_embeddings(
    algorithm="node2vec",
    dimensions=64,
    walk_length=80,
    num_walks=10,
    p=1.0,  # Return parameter
    q=1.0   # In-out parameter
)
# Returns: {"status": "success", "embeddings_computed": 100, "execution_time": 2.5}

# Generate DeepWalk embeddings (unbiased)
result = await embeddings_service.generate_embeddings(
    algorithm="deepwalk",
    dimensions=64
)

# Get embedding for a node
embedding = await embeddings_service.get_embedding(node_id="uuid-here")
# Returns: 64-dimensional numpy array

# Find similar nodes
similar = await embeddings_service.find_similar_nodes(
    node_id="uuid-here",
    limit=10,
    min_similarity=0.7
)
# Returns: List of (node_id, similarity_score) tuples
```

### Literature-Based Discovery

```python
from app.modules.graph import LBDService

# Initialize service
lbd_service = LBDService(db)

# Discover hypotheses using ABC pattern
hypotheses = await lbd_service.discover_hypotheses(
    concept_a="machine learning",
    concept_c="drug discovery",
    limit=10,
    start_date="2020-01-01",
    end_date="2024-12-31"
)
# Returns: List of hypotheses with bridging concepts, support, and evidence

# Each hypothesis includes:
# - bridging_concept: The B in A→B→C
# - confidence: support × novelty score
# - support: Number of A→B and B→C connections
# - novelty: 1 / (1 + known_ac_connections)
# - evidence_chain: Example resources showing A→B and B→C
```

### Graph Operations

```python
from app.modules.graph import GraphService, CitationService

# Get graph service
graph_service = GraphService(db)

# Find related resources
related = await graph_service.find_related_resources(
    resource_id=123,
    max_depth=2,
    min_similarity=0.7
)

# Get citation service
citation_service = CitationService(db)

# Extract citations
citations = await citation_service.extract_citations(resource_id=123)

# Get citation network
network = await citation_service.get_citation_network(
    resource_id=123,
    depth=2
)
```

## API Endpoints

### Graph Endpoints (`/graph`)
- `GET /graph/related/{resource_id}`: Find related resources
- `GET /graph/neighbors/{resource_id}`: Get graph neighbors
- `POST /graph/similarity`: Compute graph-based similarity
- `GET /graph/embeddings/{resource_id}`: Get graph embeddings

### Citation Endpoints (`/citations`)
- `GET /citations/{resource_id}`: Get resource citations
- `GET /citations/network/{resource_id}`: Get citation network
- `POST /citations/extract`: Extract citations from text
- `GET /citations/impact/{resource_id}`: Get citation impact metrics

### Discovery Endpoints (`/discovery`)
- `POST /discovery/hypotheses`: Generate LBD hypotheses
- `GET /discovery/abc-patterns`: Find ABC patterns
- `GET /discovery/cross-domain`: Find cross-domain connections
- `POST /discovery/validate`: Validate hypothesis

## Architecture

### Module Structure
```
graph/
├── __init__.py              # Public interface
├── router.py                # Main graph endpoints
├── citations_router.py      # Citation endpoints
├── discovery_router.py      # LBD endpoints
├── service.py               # Core graph service
├── advanced_service.py      # Advanced graph intelligence
├── embeddings.py            # Graph embeddings
├── citations.py             # Citation service
├── discovery.py             # LBD service
├── schema.py                # Pydantic schemas
├── model.py                 # Database models
├── handlers.py              # Event handlers
└── README.md                # This file
```

### Event Flow
```
resource.created
    ↓
handle_resource_created()
    ↓
extract_citations()
    ↓
add_to_graph()
    ↓
emit(citation.extracted)
emit(graph.updated)
```

## Testing

### Unit Tests
- Test graph algorithms
- Test citation extraction
- Test LBD hypothesis generation
- Test event handlers

### Integration Tests
- Test graph API endpoints
- Test citation network building
- Test cross-module event communication
- Test graph-based recommendations

## Performance Considerations

- **Graph embeddings**: In-memory caching with 5-minute TTL
- **Node2Vec generation**: <10s for 1000 nodes (target met)
- **Similarity search**: <100ms for 100 nodes (target met)
- **LBD discovery**: <5s for hypothesis generation (target met)
- **Cosine similarity**: 1000 computations in <1s
- Graph operations cached for frequently accessed nodes
- Batch citation extraction for multiple resources
- Lazy loading of graph neighborhoods
- Embedding generation parallelized with gensim 4.4.0
- Graph pruning for large networks

## Migration Notes

This module consolidates functionality from:
- `app/routers/graph.py` → `router.py`
- `app/routers/citations.py` → `citations_router.py`
- `app/routers/discovery.py` → `discovery_router.py`
- `app/services/graph_service.py` → `service.py`
- `app/services/graph_service_phase10.py` → `advanced_service.py`
- `app/services/graph_embeddings_service.py` → `embeddings.py`
- `app/services/citation_service.py` → `citations.py`
- `app/services/lbd_service.py` → `discovery.py`
- `app/schemas/graph.py` → `schema.py`
- `app/schemas/discovery.py` → `schema.py`

## Version History

- 1.0.0: Initial extraction from layered architecture (Phase 14)
