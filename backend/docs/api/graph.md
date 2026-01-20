# Graph API

Knowledge graph, citation extraction, and literature-based discovery endpoints.

## Overview

The Graph API provides functionality for:
- Citation extraction and graph construction
- Hybrid neighbor exploration for mind-map visualization
- Global overview of strongest connections
- Graph embeddings (Node2Vec, DeepWalk)
- Literature-Based Discovery (LBD) using ABC pattern
- Hypothesis generation and validation

## Endpoints

### POST /api/graph/resources/{resource_id}/extract-citations

Extract citations from a resource and create citation edges in the graph.

**Response:**
```json
{
  "status": "success",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "citations": [
    {
      "marker": "[1]",
      "position": 1250,
      "context": "...as shown in previous work [1]...",
      "text": "[1]"
    }
  ],
  "count": 1
}
```

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/graph/resources/550e8400-e29b-41d4-a716-446655440000/extract-citations"
```

---

### GET /api/graph/resource/{resource_id}/neighbors

Get hybrid neighbors for mind-map view.

Returns a knowledge graph showing the most relevant neighbors for a given resource, ranked by hybrid scoring that combines vector similarity, shared subjects, and classification code matches.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Maximum neighbors to return (1-20) | 10 |

**Response:**
```json
{
  "nodes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Machine Learning Fundamentals",
      "type": "article",
      "quality_score": 0.85
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Neural Network Architectures",
      "type": "paper",
      "quality_score": 0.90
    }
  ],
  "edges": [
    {
      "source": "550e8400-e29b-41d4-a716-446655440000",
      "target": "660e8400-e29b-41d4-a716-446655440001",
      "weight": 0.87,
      "relationship_type": "semantic_similarity",
      "metadata": {
        "vector_similarity": 0.85,
        "shared_subjects": 3,
        "classification_match": true
      }
    }
  ]
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/api/graph/resource/550e8400-e29b-41d4-a716-446655440000/neighbors?limit=10"
```

---

### GET /api/graph/overview

Get global overview of strongest connections across the library.

Returns a knowledge graph showing the strongest relationships across the entire collection, combining high vector similarity pairs and significant tag overlap pairs.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Maximum edges to return (1-100) | 50 |
| `vector_threshold` | float | Minimum vector similarity (0.0-1.0) | 0.7 |

**Response:**
```json
{
  "nodes": [...],
  "edges": [...]
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/api/graph/overview?limit=50&vector_threshold=0.7"
```

---

### POST /api/graph/embeddings/generate

Generate graph embeddings using Node2Vec or DeepWalk algorithm.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `algorithm` | string | Algorithm: "node2vec" or "deepwalk" | node2vec |
| `dimensions` | integer | Embedding dimensionality (32-512) | 128 |
| `walk_length` | integer | Length of random walks (10-200) | 80 |
| `num_walks` | integer | Number of walks per node (1-100) | 10 |
| `p` | float | Return parameter for Node2Vec (0.1-10.0) | 1.0 |
| `q` | float | In-out parameter for Node2Vec (0.1-10.0) | 1.0 |

**Response:**
```json
{
  "status": "success",
  "embeddings_computed": 1250,
  "dimensions": 128,
  "execution_time": 45.3
}
```

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/graph/embeddings/generate?algorithm=node2vec&dimensions=128&walk_length=80&num_walks=10"
```

---

### GET /api/graph/embeddings/{node_id}

Get the graph embedding for a specific node (resource).

**Response:**
```json
{
  "node_id": "550e8400-e29b-41d4-a716-446655440000",
  "embedding": [0.123, -0.456, 0.789, ...],
  "dimensions": 128
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/api/graph/embeddings/550e8400-e29b-41d4-a716-446655440000"
```

---

### GET /api/graph/embeddings/{node_id}/similar

Find similar nodes using graph embeddings.

Uses cosine similarity to rank nodes by their structural similarity in the citation graph.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Maximum similar nodes (1-100) | 10 |
| `min_similarity` | float | Minimum similarity threshold (0.0-1.0) | 0.0 |

**Response:**
```json
{
  "node_id": "550e8400-e29b-41d4-a716-446655440000",
  "similar_nodes": [
    {
      "node_id": "660e8400-e29b-41d4-a716-446655440001",
      "similarity": 0.87,
      "title": "Neural Network Architectures",
      "type": "paper"
    }
  ],
  "count": 1
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/api/graph/embeddings/550e8400-e29b-41d4-a716-446655440000/similar?limit=10&min_similarity=0.7"
```

---

### POST /api/graph/discover

Discover hypotheses using ABC pattern (Literature-Based Discovery).

Finds bridging concepts B that connect concept A to concept C through the literature. Returns hypotheses ranked by support strength and novelty.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `concept_a` | string | Starting concept (required) | - |
| `concept_c` | string | Target concept (required) | - |
| `limit` | integer | Maximum hypotheses (1-100) | 50 |
| `start_date` | string | Start date for time-slicing (ISO format) | - |
| `end_date` | string | End date for time-slicing (ISO format) | - |

**Response:**
```json
{
  "concept_a": "machine learning",
  "concept_c": "drug discovery",
  "hypotheses": [
    {
      "bridging_concept": "molecular modeling",
      "support_strength": 0.85,
      "novelty_score": 0.72,
      "evidence_count": 15,
      "a_to_b_resources": ["resource_id_1", "resource_id_2"],
      "b_to_c_resources": ["resource_id_3", "resource_id_4"]
    }
  ],
  "count": 1,
  "execution_time": 3.5,
  "time_slice": {
    "start_date": "2020-01-01",
    "end_date": "2024-12-31"
  }
}
```

**Target Response Time:** < 5 seconds for typical queries

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/graph/discover?concept_a=machine+learning&concept_c=drug+discovery&limit=50"
```

---

### POST /api/graph/extract/{chunk_id}

**Phase 17.5** - Extract entities and relationships from a document chunk.

**Response:**
```json
{
  "status": "success",
  "chunk_id": "chunk-uuid-1",
  "extraction_method": "hybrid",
  "entities": [
    {
      "id": "entity-uuid-1",
      "name": "Gradient Descent",
      "type": "Concept"
    }
  ],
  "relationships": [
    {
      "id": "rel-uuid-1",
      "source_entity": "Stochastic Gradient Descent",
      "target_entity": "Gradient Descent",
      "relation_type": "EXTENDS",
      "weight": 0.9
    }
  ],
  "counts": {
    "entities": 1,
    "relationships": 1
  }
}
```

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/graph/extract/chunk-uuid-1"
```

---

### GET /api/graph/entities

**Phase 17.5** - List all entities in the knowledge graph.

**Query Parameters:**
- `entity_type` (optional): Filter by entity type (Concept, Person, Organization, Method)
- `name_contains` (optional): Filter by entity name (partial match)
- `limit` (optional): Number of results (default: 50)
- `skip` (optional): Number of results to skip (default: 0)

**Response:**
```json
{
  "entities": [
    {
      "id": "entity-uuid-1",
      "name": "Gradient Descent",
      "type": "Concept",
      "description": "An optimization algorithm",
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total_count": 150,
  "skip": 0,
  "limit": 50
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/api/graph/entities?entity_type=Concept&limit=10"
```

---

### GET /api/graph/entities/{entity_id}/relationships

**Phase 17.5** - Get all relationships for an entity.

**Query Parameters:**
- `relation_type` (optional): Filter by relation type (CONTRADICTS, SUPPORTS, EXTENDS, CITES, CALLS, IMPORTS, DEFINES)
- `direction` (optional): Filter by direction (outgoing, incoming, both) (default: both)

**Response:**
```json
{
  "entity": {
    "id": "entity-uuid-1",
    "name": "Gradient Descent",
    "type": "Concept"
  },
  "outgoing_relationships": [
    {
      "id": "rel-uuid-1",
      "target_entity": {
        "id": "entity-uuid-2",
        "name": "Optimization",
        "type": "Concept"
      },
      "relation_type": "EXTENDS",
      "weight": 0.9,
      "provenance_chunk_id": "chunk-uuid-1",
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "incoming_relationships": [],
  "counts": {
    "outgoing": 1,
    "incoming": 0,
    "total": 1
  }
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/api/graph/entities/entity-uuid-1/relationships?relation_type=EXTENDS"
```

---

### GET /api/graph/traverse

**Phase 17.5** - Traverse the knowledge graph from a starting entity.

**Query Parameters:**
- `start_entity_id` (required): Starting entity ID
- `relation_types` (optional): Comma-separated relation types to follow
- `max_hops` (optional): Maximum traversal depth (default: 2)

**Response:**
```json
{
  "start_entity": {
    "id": "entity-uuid-1",
    "name": "Gradient Descent",
    "type": "Concept"
  },
  "entities": [
    {
      "id": "entity-uuid-2",
      "name": "Stochastic Gradient Descent",
      "type": "Method",
      "description": "A variant of gradient descent"
    }
  ],
  "relationships": [
    {
      "id": "rel-uuid-1",
      "source_entity_id": "entity-uuid-2",
      "target_entity_id": "entity-uuid-1",
      "relation_type": "EXTENDS",
      "weight": 0.9
    }
  ],
  "traversal_info": {
    "max_hops": 2,
    "entities_by_hop": {
      "0": ["entity-uuid-1"],
      "1": ["entity-uuid-2"]
    },
    "total_entities": 2,
    "total_relationships": 1
  }
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/api/graph/traverse?start_entity_id=entity-uuid-1&max_hops=2&relation_types=EXTENDS,SUPPORTS"
```

---

### GET /api/graph/hypotheses/{hypothesis_id}

Get details for a specific hypothesis.

**Response:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440005",
  "hypothesis_type": "abc_pattern",
  "a_resource": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Machine Learning Methods",
    "type": "paper"
  },
  "c_resource": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Drug Discovery Techniques",
    "type": "paper"
  },
  "b_resources": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440002",
      "title": "Molecular Modeling",
      "type": "article",
      "publication_year": 2023
    }
  ],
  "plausibility_score": 0.85,
  "path_strength": 0.78,
  "path_length": 2,
  "common_neighbors": 5,
  "discovered_at": "2024-01-01T10:00:00Z",
  "is_validated": null,
  "validation_notes": null
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/api/graph/hypotheses/770e8400-e29b-41d4-a716-446655440005"
```

## Data Models

### Knowledge Graph Model

```json
{
  "nodes": [
    {
      "id": "uuid",
      "title": "string",
      "type": "string",
      "quality_score": "float (0.0-1.0)"
    }
  ],
  "edges": [
    {
      "source": "uuid",
      "target": "uuid",
      "weight": "float (0.0-1.0)",
      "relationship_type": "string",
      "metadata": "object"
    }
  ]
}
```

### Graph Embedding Model

```json
{
  "node_id": "uuid",
  "embedding": ["float"],
  "dimensions": "integer"
}
```

### Hypothesis Model

```json
{
  "id": "uuid",
  "hypothesis_type": "abc_pattern",
  "a_resource_id": "uuid",
  "c_resource_id": "uuid",
  "b_resource_ids": ["uuid"],
  "plausibility_score": "float (0.0-1.0)",
  "path_strength": "float (0.0-1.0)",
  "path_length": "integer",
  "common_neighbors": "integer",
  "discovered_at": "datetime (ISO 8601)",
  "is_validated": "boolean (optional)",
  "validation_notes": "string (optional)"
}
```

## Module Structure

The Graph module is implemented as a self-contained vertical slice:

**Module**: `app.modules.graph`  
**Router Prefix**: `/api/graph`  
**Version**: 1.0.0

```python
from app.modules.graph import (
    router,
    GraphService,
    GraphEmbeddingsService,
    LBDService,
    KnowledgeGraph
)
```

### Events

**Emitted Events:**
- `citation.extracted` - When citations are extracted from a resource
- `graph.updated` - When the knowledge graph is updated
- `hypothesis.discovered` - When a new hypothesis is discovered
- `graph.entity_extracted` - When an entity is extracted from content
- `graph.relationship_extracted` - When a relationship is extracted

**Subscribed Events:**
- `resource.created` - Triggers citation extraction
- `resource.deleted` - Removes nodes and edges from graph
- `resource.chunked` - Triggers entity and relationship extraction (Phase 17.5)

## Code Graph Features (Phase 18)

The Graph module supports code repository analysis with specialized relationship types:

**Code Relationship Types:**
- `IMPORTS` - Module/file imports another module/file
  - Example: `main.py IMPORTS utils.py`
  - Metadata: source_file, target_module, line_number
- `DEFINES` - File defines a function, class, or variable
  - Example: `utils.py DEFINES calculate_score`
  - Metadata: source_file, symbol_name, symbol_type, line_number
- `CALLS` - Function calls another function
  - Example: `main() CALLS calculate_score()`
  - Metadata: source_function, target_function, line_number, confidence

**Static Analysis:**
- AST-based relationship extraction using Tree-Sitter
- No code execution (static analysis only)
- Confidence scoring for ambiguous relationships
- Provenance tracking to source code chunks

**Code Graph Queries:**
- Find all imports for a module
- Find all definitions in a file
- Find all call sites for a function
- Traverse dependency graph
- Detect circular dependencies
- Find unused imports/definitions

**Example Queries:**

**Find all imports in a file:**
```bash
curl "http://127.0.0.1:8000/api/graph/entities/file-entity-id/relationships?relation_type=IMPORTS&direction=outgoing"
```

**Find all functions defined in a file:**
```bash
curl "http://127.0.0.1:8000/api/graph/entities/file-entity-id/relationships?relation_type=DEFINES&direction=outgoing"
```

**Find all callers of a function:**
```bash
curl "http://127.0.0.1:8000/api/graph/entities/function-entity-id/relationships?relation_type=CALLS&direction=incoming"
```

**Traverse dependency graph:**
```bash
curl "http://127.0.0.1:8000/api/graph/traverse?start_entity_id=file-entity-id&relation_types=IMPORTS&max_hops=3"
```

**Performance:**
- Static analysis: <1s per file (P95)
- Relationship extraction: <500ms per file (P95)
- Graph traversal: <200ms for 3 hops (P95)

**Supported Languages:**
- Python (.py)
- JavaScript (.js)
- TypeScript (.ts)
- Rust (.rs)
- Go (.go)
- Java (.java)

## Related Documentation

- [Resources API](resources.md) - Resource management
- [Search API](search.md) - Search functionality
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors, pagination
