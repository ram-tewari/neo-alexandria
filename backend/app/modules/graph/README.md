# Graph Module

## Purpose

The Graph module provides knowledge graph, citation network, and literature-based discovery (LBD) functionality for Neo Alexandria 2.0. It enables relationship analysis, citation extraction, and hypothesis discovery across the resource collection.

## Features

### Knowledge Graph
- Build and maintain resource relationship graph
- Graph-based similarity and recommendation
- Multi-layer graph analysis
- Graph embeddings for enhanced discovery

### Citation Network
- Automatic citation extraction from resources
- Citation network analysis
- Citation-based recommendations
- Citation impact metrics

### Literature-Based Discovery (LBD)
- ABC pattern discovery (A→B, B→C implies A→C)
- Hypothesis generation
- Cross-domain connection discovery
- Novel relationship identification

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

## Usage Example

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

- Graph operations cached for frequently accessed nodes
- Batch citation extraction for multiple resources
- Lazy loading of graph neighborhoods
- Embedding generation parallelized
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
