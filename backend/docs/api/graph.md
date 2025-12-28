# Graph API

Knowledge graph and citation network endpoints for relationship exploration.

## Overview

The Graph API provides:
- Knowledge graph for resource relationships
- Citation network analysis
- Mind-map visualization data
- PageRank importance scoring

## Knowledge Graph Endpoints

### GET /graph/resource/{resource_id}/neighbors

Find related resources for mind-map visualization.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of neighbors (1-50) | 7 |

**Response:**
```json
{
  "nodes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Machine Learning Fundamentals",
      "type": "article",
      "classification_code": "004"
    }
  ],
  "edges": [
    {
      "source": "550e8400-e29b-41d4-a716-446655440000",
      "target": "550e8400-e29b-41d4-a716-446655440001",
      "weight": 0.76,
      "details": {
        "connection_type": "classification",
        "vector_similarity": 0.8,
        "shared_subjects": ["python", "programming"]
      }
    }
  ]
}
```

---

### GET /graph/overview

Get global relationship overview of strongest connections across the library.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of edges (1-200) | 50 |
| `vector_threshold` | float | Minimum vector similarity | 0.85 |

**Response:** Same structure as neighbors endpoint with `connection_type: "hybrid"`.

---

## Citation Network Endpoints

### GET /citations/resources/{resource_id}/citations

Retrieve all citations for a specific resource.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `direction` | string | `outbound`, `inbound`, or `both` | both |

**Response:**
```json
{
  "resource_id": "uuid",
  "outbound": [
    {
      "id": "uuid",
      "source_resource_id": "uuid",
      "target_url": "string",
      "target_resource_id": "uuid or null",
      "citation_type": "reference|dataset|code|general",
      "context_snippet": "string or null",
      "position": "integer or null",
      "importance_score": "float or null",
      "created_at": "datetime",
      "target_resource": {
        "id": "uuid",
        "title": "string",
        "source": "string"
      }
    }
  ],
  "inbound": [...],
  "counts": {
    "outbound": 5,
    "inbound": 3,
    "total": 8
  }
}
```

**Example:**
```bash
# Get all citations
curl "http://127.0.0.1:8000/citations/resources/{resource_id}/citations"

# Get only outbound citations
curl "http://127.0.0.1:8000/citations/resources/{resource_id}/citations?direction=outbound"
```

---

### GET /citations/graph/citations

Get citation network for visualization.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `resource_ids` | string[] | Filter to specific resources | - |
| `min_importance` | float | Minimum importance score (0.0-1.0) | 0.0 |
| `depth` | integer | Graph traversal depth (1-2) | 1 |

**Response:**
```json
{
  "nodes": [
    {
      "id": "uuid",
      "title": "string",
      "type": "source|cited|citing"
    }
  ],
  "edges": [
    {
      "source": "uuid",
      "target": "uuid",
      "type": "reference|dataset|code|general"
    }
  ]
}
```

**Performance Notes:**
- Results limited to 100 nodes maximum
- Depth capped at 2 to prevent exponential explosion

---

### POST /citations/resources/{resource_id}/citations/extract

Manually trigger citation extraction for a resource.

**Response (202 Accepted):**
```json
{
  "status": "queued",
  "resource_id": "uuid",
  "message": "Citation extraction queued for processing"
}
```

**Background Processing:**
1. Retrieve resource content from archive
2. Determine content type (HTML, PDF, Markdown)
3. Extract citations using appropriate parser
4. Classify citation types
5. Extract context snippets
6. Store citations and trigger resolution

---

### POST /citations/resolve

Trigger internal citation resolution to match URLs to existing resources.

**Response (202 Accepted):**
```json
{
  "status": "queued"
}
```

**Processing:**
- Queries citations with `target_resource_id = NULL`
- Normalizes URLs and matches to existing resources
- Processes in batches of 100

---

### POST /citations/importance/compute

Recompute PageRank importance scores for all citations.

**Response (202 Accepted):**
```json
{
  "status": "queued"
}
```

**Algorithm:**
- Damping factor: 0.85
- Max iterations: 100
- Convergence threshold: 1e-6
- Normalizes scores to [0, 1] range

**Performance:**
- Small graphs (<100 nodes): <1s
- Medium graphs (100-1000 nodes): <5s
- Large graphs (1000+ nodes): <30s

---

## Citation Type Classification

The system automatically classifies citations:

| Type | Indicators |
|------|------------|
| `dataset` | File extensions: `.csv`, `.json`, `.xml`, `.xlsx` |
| `code` | Domains: `github.com`, `gitlab.com`, `bitbucket.org` |
| `reference` | Domains: `doi.org`, `arxiv.org`, `scholar.google` |
| `general` | All other URLs |

## Data Models

### Graph Response Model

```json
{
  "nodes": [
    {
      "id": "uuid",
      "title": "string",
      "type": "string",
      "classification_code": "string"
    }
  ],
  "edges": [
    {
      "source": "uuid",
      "target": "uuid",
      "weight": "float (0.0-1.0)",
      "details": {
        "connection_type": "vector|subject|classification|hybrid",
        "vector_similarity": "float",
        "shared_subjects": ["string"],
        "classification_match": "boolean"
      }
    }
  ]
}
```

### Citation Model

```json
{
  "id": "uuid",
  "source_resource_id": "uuid",
  "target_resource_id": "uuid or null",
  "target_url": "string",
  "citation_type": "reference|dataset|code|general",
  "context_snippet": "string or null",
  "position": "integer or null",
  "importance_score": "float or null (0.0-1.0)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Integration Examples

### Periodic Citation Resolution

```bash
# Cron job (daily at 2 AM)
0 2 * * * curl -X POST http://127.0.0.1:8000/citations/resolve
```

### Periodic Importance Updates

```bash
# Cron job (weekly on Sunday at 3 AM)
0 3 * * 0 curl -X POST http://127.0.0.1:8000/citations/importance/compute
```

### Citation Network Visualization

```javascript
const response = await fetch(
  `/citations/graph/citations?resource_ids=${resourceId}&depth=2`
);
const graph = await response.json();
renderGraph(graph.nodes, graph.edges);
```

## Module Structure

The Graph module is implemented as a self-contained vertical slice:

**Module**: `app.modules.graph`  
**Router Prefix**: `/graph`, `/citations`, `/discovery`  
**Version**: 1.0.0

```python
from app.modules.graph import (
    graph_router,
    citations_router,
    discovery_router,
    GraphService,
    CitationService,
    LBDService,
    GraphEdge,
    Citation,
    DiscoveryHypothesis
)
```

### Events

**Emitted Events:**
- `citation.extracted` - When citations are extracted from a resource
- `graph.updated` - When the knowledge graph is updated
- `hypothesis.discovered` - When a new discovery hypothesis is generated

**Subscribed Events:**
- `resource.created` - Extracts citations and updates graph
- `resource.deleted` - Removes resource from graph

## Related Documentation

- [Resources API](resources.md) - Content management
- [Search API](search.md) - Discovery features
- [Recommendations API](recommendations.md) - Related content
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors
