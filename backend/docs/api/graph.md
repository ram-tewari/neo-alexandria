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

**Subscribed Events:**
- `resource.created` - Triggers citation extraction
- `resource.deleted` - Removes nodes and edges from graph

## Related Documentation

- [Resources API](resources.md) - Resource management
- [Search API](search.md) - Search functionality
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors, pagination
