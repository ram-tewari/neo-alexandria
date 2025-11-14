# Phase 10: Advanced Graph Intelligence & Literature-Based Discovery - User Guide

## Overview

Phase 10 transforms Neo Alexandria's knowledge graph into an advanced graph intelligence system that enables researchers to discover implicit connections, identify research gaps, and find serendipitous insights through graph-guided exploration. This guide covers all Phase 10 features with practical examples and best practices.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Multi-Layer Graph](#multi-layer-graph)
- [Two-Hop Neighbor Discovery](#two-hop-neighbor-discovery)
- [Graph Embeddings](#graph-embeddings)
- [Literature-Based Discovery](#literature-based-discovery)
- [Hypothesis Validation](#hypothesis-validation)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Core Concepts

### What is Graph Intelligence?

Graph intelligence combines multiple relationship types, structural embeddings, and discovery algorithms to help you:

1. **Find Hidden Connections**: Discover resources connected through intermediate nodes
2. **Generate Hypotheses**: Identify potential relationships between concepts
3. **Explore Structure**: Navigate the knowledge graph using multiple relationship types
4. **Validate Insights**: Provide feedback to improve future recommendations

### The ABC Paradigm

Literature-Based Discovery (LBD) uses the ABC paradigm:

- **A**: Starting concept (what you know)
- **B**: Intermediate concept (the bridge)
- **C**: Target concept (what you discover)

**Example**: 
- A = "Machine Learning" paper
- B = "Neural Networks" paper (cites A)
- C = "Deep Learning" paper (cited by B, not directly connected to A)
- **Hypothesis**: A and C are related through neural networks

## Multi-Layer Graph

### Edge Types

Phase 10 supports five types of relationships:

| Edge Type | Description | Weight Calculation | Use Case |
|-----------|-------------|-------------------|----------|
| **citation** | One resource cites another | 1.0 (binary) | Academic lineage, influence tracking |
| **co_authorship** | Resources share authors | 1.0 / num_shared_authors | Collaboration networks |
| **subject_similarity** | Resources share taxonomy nodes | 0.5 (fixed) | Topic clustering |
| **temporal** | Resources published same year | 0.3 (fixed) | Historical context |
| **content_similarity** | High semantic similarity | cosine_similarity | Conceptual relationships |

### Graph Construction

The multi-layer graph is automatically constructed from your existing data:

```bash
# Graph is built automatically during resource ingestion
# No manual action required

# To rebuild the graph manually (if needed):
curl -X POST http://127.0.0.1:8000/graph/rebuild
```

**Performance**: Graph construction takes <30 seconds for 10,000 resources.

### Graph Caching

The graph is cached in memory for fast queries:

- **Cache Duration**: Until graph structure changes
- **Invalidation**: Automatic when new resources added or edges modified
- **Memory Usage**: ~500MB for 10,000 nodes

## Two-Hop Neighbor Discovery

### What are Two-Hop Neighbors?

Two-hop neighbors are resources connected through one intermediate node:

```
You → [1-hop] → Intermediate → [2-hop] → Discovery
```

### Basic Neighbor Query

```bash
# Get 2-hop neighbors for a resource
curl "http://127.0.0.1:8000/graph/resources/{resource_id}/neighbors?hops=2&limit=50"
```

**Response**:
```json
{
  "neighbors": [
    {
      "resource": {
        "id": "uuid",
        "title": "Deep Learning Fundamentals",
        "quality_score": 0.85
      },
      "distance": 2,
      "path": ["source_uuid", "intermediate_uuid", "target_uuid"],
      "path_strength": 0.75,
      "edge_types": ["citation", "co_authorship"],
      "score": 0.82,
      "intermediate": "intermediate_uuid"
    }
  ]
}
```

### Filtering by Edge Type

Focus on specific relationship types:

```bash
# Only citation relationships
curl "http://127.0.0.1:8000/graph/resources/{resource_id}/neighbors?hops=2&edge_types=citation"

# Citation and co-authorship
curl "http://127.0.0.1:8000/graph/resources/{resource_id}/neighbors?hops=2&edge_types=citation&edge_types=co_authorship"

# Subject similarity only
curl "http://127.0.0.1:8000/graph/resources/{resource_id}/neighbors?hops=2&edge_types=subject_similarity"
```

### Filtering by Weight

Exclude weak connections:

```bash
# Only strong connections (weight >= 0.5)
curl "http://127.0.0.1:8000/graph/resources/{resource_id}/neighbors?hops=2&min_weight=0.5"

# Very strong connections only (weight >= 0.8)
curl "http://127.0.0.1:8000/graph/resources/{resource_id}/neighbors?hops=2&min_weight=0.8"
```

### Ranking Algorithm

Neighbors are ranked by a combined score:

```
score = 0.5 * path_strength + 0.3 * quality_overall + 0.2 * novelty

where:
  path_strength = product of edge weights along path
  quality_overall = Phase 9 quality score
  novelty = 1.0 / (1 + log(degree + 1))
```

**Interpretation**:
- **High path_strength**: Strong connections through intermediate
- **High quality**: Well-curated, high-quality resources
- **High novelty**: Less-connected resources (avoid hubs)

## Graph Embeddings

### Structural Embeddings (Graph2Vec)

Graph2Vec learns structural patterns in the graph:

```bash
# Compute Graph2Vec embeddings for resources
curl -X POST http://127.0.0.1:8000/graph/embeddings/compute \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": ["{resource_id_1}", "{resource_id_2}"],
    "dimensions": 128,
    "wl_iterations": 2
  }'
```

**Parameters**:
- `dimensions`: Embedding size (default: 128)
- `wl_iterations`: Weisfeiler-Lehman iterations (default: 2)

**Use Cases**:
- Find resources with similar graph positions
- Identify structural roles (hubs, bridges, periphery)
- Cluster resources by topology

### Fusion Embeddings

Fusion embeddings combine content and structure:

```bash
# Compute fusion embeddings
curl -X POST http://127.0.0.1:8000/graph/embeddings/compute \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": ["{resource_id_1}", "{resource_id_2}"],
    "alpha": 0.5
  }'
```

**Alpha Parameter**:
- `alpha = 0.0`: Pure structural similarity
- `alpha = 0.5`: Balanced (default)
- `alpha = 1.0`: Pure content similarity

**Formula**:
```
fusion = alpha * content_embedding + (1-alpha) * structural_embedding
fusion = fusion / ||fusion||  # L2 normalization
```

### HNSW Index

Build a fast similarity index:

```bash
# Build HNSW index
curl -X POST http://127.0.0.1:8000/graph/hnsw/build \
  -H "Content-Type: application/json" \
  -d '{
    "ef_construction": 200,
    "M": 16
  }'
```

**Parameters**:
- `ef_construction`: Build quality (higher = better, slower)
- `M`: Connections per layer (higher = better recall, more memory)

**Query the index**:
```bash
# Find k-nearest neighbors
curl "http://127.0.0.1:8000/graph/hnsw/query?resource_id={resource_id}&k=10"
```

**Performance**: <100ms for 10,000+ nodes

## Literature-Based Discovery

### Open Discovery

**Goal**: Start from a known concept and discover related concepts you haven't considered.

**Use Case**: "I'm researching machine learning. What related topics should I explore?"

```bash
curl "http://127.0.0.1:8000/discovery/open?resource_id={resource_id}&limit=20&min_plausibility=0.5"
```

**Response**:
```json
{
  "hypotheses": [
    {
      "c_resource": {
        "id": "uuid",
        "title": "Quantum Machine Learning",
        "description": "Applying quantum computing to ML"
      },
      "b_resources": [
        {
          "id": "uuid",
          "title": "Quantum Algorithms",
          "role": "bridge"
        }
      ],
      "plausibility_score": 0.78,
      "path_strength": 0.85,
      "common_neighbors": 5,
      "semantic_similarity": 0.72,
      "evidence": {
        "path": ["A", "B", "C"],
        "edge_types": ["citation", "subject_similarity"]
      }
    }
  ]
}
```

**Plausibility Score**:
```
plausibility = 0.4 * path_strength + 0.3 * common_neighbors_norm + 0.3 * semantic_similarity
```

**Interpretation**:
- **0.8-1.0**: Very plausible, strong evidence
- **0.6-0.8**: Plausible, worth investigating
- **0.4-0.6**: Possible, weak evidence
- **<0.4**: Unlikely, filtered by default

### Closed Discovery

**Goal**: Connect two known concepts by finding intermediate literature.

**Use Case**: "How does quantum computing relate to cryptography?"

```bash
curl -X POST http://127.0.0.1:8000/discovery/closed \
  -H "Content-Type: application/json" \
  -d '{
    "a_resource_id": "{quantum_computing_id}",
    "c_resource_id": "{cryptography_id}",
    "max_hops": 3
  }'
```

**Response**:
```json
{
  "paths": [
    {
      "b_resources": [
        {
          "id": "uuid",
          "title": "Shor's Algorithm",
          "description": "Quantum algorithm for integer factorization"
        }
      ],
      "path_length": 2,
      "plausibility_score": 0.85,
      "path_strength": 0.90,
      "common_neighbors": 8,
      "semantic_similarity": 0.78,
      "evidence": {
        "path": ["Quantum Computing", "Shor's Algorithm", "Cryptography"],
        "edge_types": ["citation", "citation"]
      }
    }
  ]
}
```

**Hop Penalty**:
- **2-hop**: No penalty (plausibility * 1.0)
- **3-hop**: 50% penalty (plausibility * 0.5)
- **4-hop**: 25% penalty (plausibility * 0.25)

### Filtering Hypotheses

List and filter discovered hypotheses:

```bash
# All open discovery hypotheses
curl "http://127.0.0.1:8000/discovery/hypotheses?hypothesis_type=open"

# Unvalidated hypotheses with high plausibility
curl "http://127.0.0.1:8000/discovery/hypotheses?is_validated=false&min_plausibility=0.7"

# Validated hypotheses only
curl "http://127.0.0.1:8000/discovery/hypotheses?is_validated=true"

# Paginated results
curl "http://127.0.0.1:8000/discovery/hypotheses?skip=0&limit=50"
```

## Hypothesis Validation

### Why Validate?

Validation helps the system learn:

1. **Improve Recommendations**: Validated hypotheses boost edge weights
2. **Filter Noise**: Rejected hypotheses reduce future suggestions
3. **Track Progress**: Monitor which discoveries you've reviewed

### Validating a Hypothesis

```bash
curl -X POST http://127.0.0.1:8000/discovery/hypotheses/{hypothesis_id}/validate \
  -H "Content-Type: application/json" \
  -d '{
    "is_valid": true,
    "notes": "Confirmed through manual review - strong connection between quantum computing and cryptography via Shor'\''s algorithm"
  }'
```

**Effects of Validation**:

**If `is_valid = true`**:
- Edge weights along path increased by 10%
- Future hypotheses using these edges ranked higher
- Hypothesis marked as validated

**If `is_valid = false`**:
- Edge weights along path decreased by 5%
- Future hypotheses using these edges ranked lower
- Hypothesis marked as rejected

### Validation Workflow

1. **Review Hypothesis**: Read the suggested connection
2. **Check Evidence**: Examine path strength, common neighbors, semantic similarity
3. **Verify Manually**: Read the intermediate resources (B)
4. **Validate**: Mark as valid or invalid with notes
5. **Iterate**: System learns from your feedback

## API Reference

### Discovery Endpoints

#### GET /discovery/open

Open discovery from starting resource.

**Parameters**:
- `resource_id` (required): Starting resource UUID
- `limit` (optional): Max hypotheses (default: 20)
- `min_plausibility` (optional): Minimum score (default: 0.5)

**Response**: List of hypotheses with C resources and evidence

---

#### POST /discovery/closed

Closed discovery connecting two resources.

**Body**:
```json
{
  "a_resource_id": "uuid",
  "c_resource_id": "uuid",
  "max_hops": 3
}
```

**Response**: List of paths with B resources and plausibility

---

#### GET /graph/resources/{id}/neighbors

Multi-hop neighbor discovery.

**Parameters**:
- `hops` (optional): 1 or 2 (default: 2)
- `edge_types` (optional): Filter by edge types
- `min_weight` (optional): Minimum edge weight (default: 0.0)
- `limit` (optional): Max neighbors (default: 50)

**Response**: List of neighbors with path metadata

---

#### GET /discovery/hypotheses

List discovery hypotheses.

**Parameters**:
- `hypothesis_type` (optional): "open" or "closed"
- `is_validated` (optional): true/false/null
- `min_plausibility` (optional): Minimum score
- `skip` (optional): Pagination offset
- `limit` (optional): Results per page (default: 50)

**Response**: Paginated list of hypotheses

---

#### POST /discovery/hypotheses/{id}/validate

Validate or reject hypothesis.

**Body**:
```json
{
  "is_valid": true,
  "notes": "Optional validation notes"
}
```

**Response**: Updated hypothesis with validation status

## Best Practices

### Discovery Workflow

1. **Start Broad**: Use open discovery with `min_plausibility=0.5`
2. **Filter Gradually**: Increase threshold to 0.7 for high-confidence results
3. **Validate Regularly**: Provide feedback to improve recommendations
4. **Explore Paths**: Use closed discovery to understand connections
5. **Iterate**: Repeat discovery from newly found resources

### Edge Type Selection

**For Academic Research**:
- Use `citation` for literature lineage
- Use `co_authorship` for collaboration networks
- Use `subject_similarity` for topic exploration

**For Topic Clustering**:
- Use `subject_similarity` primarily
- Add `content_similarity` for semantic grouping
- Exclude `temporal` unless studying historical trends

**For Influence Analysis**:
- Use `citation` exclusively
- Set `min_weight=0.8` for strong citations only
- Use 2-hop queries to find indirect influence

### Performance Optimization

**For Large Graphs (>5,000 nodes)**:
- Use `limit=20` for faster queries
- Set `min_weight=0.3` to filter weak edges
- Use specific `edge_types` to reduce search space
- Enable graph caching (automatic)

**For Real-Time Discovery**:
- Pre-compute Graph2Vec embeddings
- Build HNSW index in advance
- Use `min_plausibility=0.6` to reduce candidates
- Limit `max_hops=2` for closed discovery

### Hypothesis Quality

**High-Quality Hypotheses Have**:
- Plausibility score > 0.7
- Path strength > 0.6
- Common neighbors > 3
- Semantic similarity > 0.5

**Red Flags**:
- Very long paths (>3 hops)
- Low path strength (<0.3)
- No common neighbors
- Low semantic similarity (<0.3)

## Troubleshooting

### No Hypotheses Found

**Possible Causes**:
1. Resource is isolated (no connections)
2. `min_plausibility` threshold too high
3. Graph not built yet

**Solutions**:
```bash
# Check resource connections
curl "http://127.0.0.1:8000/graph/resources/{resource_id}/neighbors?hops=1"

# Lower plausibility threshold
curl "http://127.0.0.1:8000/discovery/open?resource_id={id}&min_plausibility=0.3"

# Rebuild graph
curl -X POST http://127.0.0.1:8000/graph/rebuild
```

### Slow Queries

**Possible Causes**:
1. Large graph (>10,000 nodes)
2. No graph caching
3. Too many edge types

**Solutions**:
```bash
# Enable graph caching (automatic)
# Reduce edge types
curl "http://127.0.0.1:8000/graph/resources/{id}/neighbors?edge_types=citation"

# Reduce limit
curl "http://127.0.0.1:8000/discovery/open?resource_id={id}&limit=10"

# Use HNSW index for similarity queries
curl "http://127.0.0.1:8000/graph/hnsw/query?resource_id={id}&k=10"
```

### Low-Quality Hypotheses

**Possible Causes**:
1. Sparse graph (few connections)
2. No validation feedback
3. Low-quality resources

**Solutions**:
```bash
# Increase plausibility threshold
curl "http://127.0.0.1:8000/discovery/open?resource_id={id}&min_plausibility=0.7"

# Validate hypotheses regularly
curl -X POST http://127.0.0.1:8000/discovery/hypotheses/{id}/validate \
  -d '{"is_valid": true}'

# Filter by quality
curl "http://127.0.0.1:8000/graph/resources/{id}/neighbors?min_weight=0.5"
```

### Missing Embeddings

**Possible Causes**:
1. Graph2Vec not computed
2. Fusion embeddings not generated
3. HNSW index not built

**Solutions**:
```bash
# Compute Graph2Vec embeddings
curl -X POST http://127.0.0.1:8000/graph/embeddings/compute

# Build HNSW index
curl -X POST http://127.0.0.1:8000/graph/hnsw/build

# Check embedding status
curl "http://127.0.0.1:8000/graph/embeddings/status"
```

## Examples

### Example 1: Exploring Machine Learning Research

```bash
# 1. Start with a machine learning paper
RESOURCE_ID="550e8400-e29b-41d4-a716-446655440000"

# 2. Find 2-hop neighbors via citations
curl "http://127.0.0.1:8000/graph/resources/${RESOURCE_ID}/neighbors?hops=2&edge_types=citation&limit=20"

# 3. Discover related concepts
curl "http://127.0.0.1:8000/discovery/open?resource_id=${RESOURCE_ID}&min_plausibility=0.6"

# 4. Validate interesting hypotheses
HYPOTHESIS_ID="660e8400-e29b-41d4-a716-446655440001"
curl -X POST http://127.0.0.1:8000/discovery/hypotheses/${HYPOTHESIS_ID}/validate \
  -H "Content-Type: application/json" \
  -d '{"is_valid": true, "notes": "Strong connection confirmed"}'
```

### Example 2: Connecting Two Research Areas

```bash
# Connect quantum computing and cryptography
QUANTUM_ID="770e8400-e29b-41d4-a716-446655440002"
CRYPTO_ID="880e8400-e29b-41d4-a716-446655440003"

curl -X POST http://127.0.0.1:8000/discovery/closed \
  -H "Content-Type: application/json" \
  -d '{
    "a_resource_id": "'${QUANTUM_ID}'",
    "c_resource_id": "'${CRYPTO_ID}'",
    "max_hops": 3
  }'
```

### Example 3: Building a Research Map

```bash
# 1. Get starting resource
RESOURCE_ID="990e8400-e29b-41d4-a716-446655440004"

# 2. Get 1-hop neighbors (direct connections)
curl "http://127.0.0.1:8000/graph/resources/${RESOURCE_ID}/neighbors?hops=1&limit=10" > direct.json

# 3. Get 2-hop neighbors (extended network)
curl "http://127.0.0.1:8000/graph/resources/${RESOURCE_ID}/neighbors?hops=2&limit=30" > extended.json

# 4. Discover new concepts
curl "http://127.0.0.1:8000/discovery/open?resource_id=${RESOURCE_ID}&limit=20" > discoveries.json

# 5. Visualize in frontend (Phase 10 visualization)
```

## Conclusion

Phase 10's graph intelligence features enable powerful discovery workflows:

1. **Multi-Layer Graph**: Explore multiple relationship types
2. **Two-Hop Discovery**: Find non-obvious connections
3. **Graph Embeddings**: Leverage structural patterns
4. **LBD**: Generate and validate hypotheses
5. **Feedback Loop**: Improve recommendations over time

For more information, see:
- [API Documentation](API_DOCUMENTATION.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [Phase 10 Design Document](../.kiro/specs/phase10-advanced-graph-intelligence/design.md)
