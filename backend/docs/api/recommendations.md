# Recommendations API

Personalized content recommendation endpoints using hybrid strategies.

## Overview

The Recommendations API provides:
- Multi-strategy recommendations (collaborative, content, graph)
- User profile learning from interactions
- Diversity optimization with MMR
- Novelty promotion for discovery
- Cold start handling for new users

## Endpoints

### GET /recommendations

Get personalized content recommendations based on library content.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of recommendations (1-100) | 10 |

**Response:**
```json
{
  "items": [
    {
      "url": "https://example.com/new-ml-article",
      "title": "Latest Advances in Machine Learning",
      "snippet": "Recent developments in ML algorithms",
      "relevance_score": 0.85,
      "reasoning": ["Aligned with Machine Learning, Python"]
    }
  ]
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/recommendations?limit=5"
```

---

### GET /api/recommendations

Get personalized recommendations using hybrid strategy (Phase 11).

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of recommendations (1-100) | 20 |
| `strategy` | string | Recommendation strategy | hybrid |
| `diversity` | float | Diversity preference (0.0-1.0) | user profile |
| `min_quality` | float | Minimum quality threshold (0.0-1.0) | 0.0 |

**Strategy Options:**
- `collaborative` - Neural Collaborative Filtering (requires ≥5 interactions)
- `content` - Content-based similarity only
- `graph` - Graph-based relationships only
- `hybrid` - Combines all strategies (default)

**Response:**
```json
{
  "recommendations": [
    {
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Advanced Machine Learning Techniques",
      "description": "Comprehensive guide to modern ML algorithms",
      "score": 0.87,
      "strategy": "hybrid",
      "scores": {
        "collaborative": 0.92,
        "content": 0.85,
        "graph": 0.78,
        "quality": 0.88,
        "recency": 0.65
      },
      "rank": 1,
      "novelty_score": 0.42,
      "source": "https://example.com/ml-guide",
      "classification_code": "004",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "metadata": {
    "total": 20,
    "strategy": "hybrid",
    "diversity_applied": true,
    "gini_coefficient": 0.24,
    "user_interactions": 47,
    "cold_start": false
  }
}
```

**Hybrid Scoring Formula:**
```
hybrid_score = 
  0.35 * collaborative_score +
  0.30 * content_score +
  0.20 * graph_score +
  0.10 * quality_score +
  0.05 * recency_score
```

**Performance:**
- Target latency: <200ms for 20 recommendations
- Cache hit rate: >80% for user embeddings

**Cold Start Behavior:**
- Users with <5 interactions: Uses content + graph strategies only
- Collaborative filtering enabled after 5+ interactions

---

### POST /api/interactions

Track user-resource interactions for personalized learning.

**Request Body:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "interaction_type": "view",
  "dwell_time": 45,
  "scroll_depth": 0.8,
  "session_id": "session_abc123"
}
```

**Interaction Types:**

| Type | Strength | Description |
|------|----------|-------------|
| `view` | 0.1-0.5 | Based on dwell time and scroll depth |
| `annotation` | 0.7 | User annotated the resource |
| `collection_add` | 0.8 | User added to collection |
| `export` | 0.9 | User exported the resource |
| `rating` | varies | Based on rating value |

**Response (201 Created):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "user123",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "interaction_type": "view",
  "interaction_strength": 0.42,
  "is_positive": true,
  "confidence": 0.85,
  "dwell_time": 45,
  "scroll_depth": 0.8,
  "return_visits": 1,
  "interaction_timestamp": "2024-01-15T14:30:00Z"
}
```

## Features

### Multi-Strategy Recommendations

The hybrid engine combines multiple strategies:

1. **Collaborative Filtering (NCF)**
   - Learns from user interaction patterns
   - Requires ≥5 interactions to activate
   - Uses neural network for user-item embeddings

2. **Content-Based Similarity**
   - Uses resource embeddings for semantic similarity
   - Works immediately for new users
   - Based on resource metadata and content

3. **Graph-Based Discovery**
   - Leverages knowledge graph relationships
   - Finds resources through citation networks
   - Discovers related topics through classification

### Diversity Optimization

Uses Maximal Marginal Relevance (MMR) to:
- Prevent filter bubbles
- Balance relevance with diversity
- Surface varied content types

### Novelty Promotion

Surfaces lesser-known but relevant resources:
- Tracks resource popularity
- Boosts underexposed quality content
- Balances popular vs. niche recommendations

## Data Models

### Recommendation Response Model

```json
{
  "items": [
    {
      "url": "string",
      "title": "string",
      "snippet": "string",
      "relevance_score": "float (0.0-1.0)",
      "reasoning": ["string"]
    }
  ]
}
```

### Interaction Model

```json
{
  "id": "uuid",
  "user_id": "string",
  "resource_id": "uuid",
  "interaction_type": "view|annotation|collection_add|export|rating",
  "interaction_strength": "float (0.0-1.0)",
  "is_positive": "boolean",
  "confidence": "float (0.0-1.0)",
  "dwell_time": "integer (seconds)",
  "scroll_depth": "float (0.0-1.0)",
  "return_visits": "integer",
  "interaction_timestamp": "datetime"
}
```

## Related Documentation

- [Resources API](resources.md) - Content management
- [Search API](search.md) - Discovery features
- [Graph API](graph.md) - Knowledge graph
- [Collections API](collections.md) - Collection recommendations
- [API Overview](overview.md) - Authentication, errors
