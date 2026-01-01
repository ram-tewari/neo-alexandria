# Recommendations API

Hybrid recommendation engine endpoints for personalized content discovery.

## Overview

The Recommendations API provides a sophisticated hybrid recommendation system combining:
- **Collaborative filtering**: Neural Collaborative Filtering (NCF) for user-item interactions
- **Content-based**: Semantic similarity using embeddings
- **Graph-based**: Citation network and knowledge graph relationships
- **Quality filtering**: Exclude low-quality or outlier resources
- **Diversity and novelty**: Configurable preferences for exploration vs exploitation

## Endpoints

### GET /recommendations

Get personalized recommendations for the authenticated user (hybrid approach).

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of recommendations (1-100) | 20 |
| `strategy` | string | Strategy: collaborative/content/graph/hybrid | hybrid |
| `diversity` | float | Override diversity preference (0.0-1.0) | - |
| `min_quality` | float | Minimum quality threshold (0.0-1.0) | - |

**Response:**
```json
{
  "recommendations": [
    {
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Machine Learning Fundamentals",
      "score": 0.87,
      "strategy": "hybrid",
      "scores": {
        "collaborative": 0.85,
        "content": 0.90,
        "graph": 0.82,
        "quality": 0.88,
        "recency": 0.75
      },
      "rank": 1,
      "novelty_score": 0.65,
      "view_count": 42
    }
  ],
  "metadata": {
    "total": 20,
    "strategy": "hybrid",
    "is_cold_start": false,
    "interaction_count": 150,
    "diversity_applied": true,
    "novelty_applied": true,
    "gini_coefficient": 0.35,
    "diversity_preference": 0.3,
    "novelty_preference": 0.2
  }
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/recommendations?limit=20&strategy=hybrid&min_quality=0.7"
```

---

### GET /recommendations/simple

Get simple recommendations (basic endpoint for compatibility).

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of recommendations (1-100) | 10 |

**Response:**
```json
{
  "items": [
    {
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Machine Learning Fundamentals",
      "score": 0.87,
      "reason": "Based on your interests"
    }
  ]
}
```

---

### POST /recommendations/interactions

Track a user-resource interaction.

**Request Body:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "interaction_type": "view",
  "dwell_time": 120,
  "scroll_depth": 0.85,
  "session_id": "session-123",
  "rating": 5
}
```

**Interaction Types:**
- `view` - User viewed the resource
- `annotation` - User created an annotation
- `collection_add` - User added to collection
- `export` - User exported the resource
- `rating` - User rated the resource (1-5 stars)

**Response (201 Created):**
```json
{
  "interaction_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "test-user",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "interaction_type": "view",
  "interaction_strength": 0.75,
  "is_positive": true,
  "created_at": "2024-01-01T10:00:00Z"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/recommendations/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "resource_id": "550e8400-e29b-41d4-a716-446655440000",
    "interaction_type": "view",
    "dwell_time": 120
  }'
```

---

### GET /recommendations/profile

Get user profile settings.

**Response:**
```json
{
  "user_id": "test-user",
  "diversity_preference": 0.3,
  "novelty_preference": 0.2,
  "recency_bias": 0.5,
  "research_domains": ["machine-learning", "nlp"],
  "active_domain": "machine-learning",
  "excluded_sources": ["example.com"],
  "total_interactions": 150,
  "last_active_at": "2024-01-01T10:00:00Z"
}
```

---

### PUT /recommendations/profile

Update user profile settings.

**Request Body:**
```json
{
  "diversity_preference": 0.4,
  "novelty_preference": 0.3,
  "recency_bias": 0.6,
  "excluded_sources": ["example.com", "spam.com"],
  "research_domains": ["machine-learning", "nlp", "computer-vision"],
  "active_domain": "computer-vision"
}
```

**Response:**
```json
{
  "user_id": "test-user",
  "diversity_preference": 0.4,
  "novelty_preference": 0.3,
  "recency_bias": 0.6,
  "research_domains": ["machine-learning", "nlp", "computer-vision"],
  "active_domain": "computer-vision",
  "excluded_sources": ["example.com", "spam.com"],
  "total_interactions": 150,
  "last_active_at": "2024-01-01T10:00:00Z"
}
```

---

### GET /recommendations/interactions

Get user interaction history.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of interactions (1-1000) | 100 |
| `offset` | integer | Pagination offset | 0 |
| `interaction_type` | string | Filter by type | - |

**Response:**
```json
[
  {
    "interaction_id": "660e8400-e29b-41d4-a716-446655440001",
    "user_id": "test-user",
    "resource_id": "550e8400-e29b-41d4-a716-446655440000",
    "interaction_type": "view",
    "interaction_strength": 0.75,
    "is_positive": true,
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

---

### POST /recommendations/feedback

Submit feedback for a recommendation.

**Request Body:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "was_clicked": true,
  "was_useful": true,
  "feedback_notes": "Very relevant to my research"
}
```

**Response (201 Created):**
```json
{
  "feedback_id": "770e8400-e29b-41d4-a716-446655440002",
  "user_id": "test-user",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "was_clicked": true,
  "was_useful": true,
  "created_at": "2024-01-01T10:00:00Z"
}
```

---

### GET /recommendations/metrics

Get performance metrics for the recommendation system.

**Response:**
```json
{
  "status": "success",
  "metrics": {
    "cache_hit_rate": 0.85,
    "avg_response_time_ms": 125.5,
    "slow_query_count": 3,
    "recommendation_generation": {
      "total_requests": 1250,
      "avg_latency_ms": 145.2,
      "p95_latency_ms": 280.5
    }
  }
}
```

---

### POST /recommendations/refresh

Trigger a refresh of recommendations for the current user.

**Response (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Recommendation refresh queued",
  "user_id": "test-user"
}
```

---

### GET /recommendations/health

Health check endpoint for Recommendations module.

**Response:**
```json
{
  "status": "healthy",
  "module": {
    "name": "recommendations",
    "version": "1.0.0",
    "domain": "recommendations"
  },
  "database": {
    "healthy": true,
    "message": "Database connection healthy"
  },
  "services": {
    "recommendation_service": {
      "available": true,
      "message": "Recommendation service available"
    },
    "user_profile_service": {
      "available": true,
      "message": "User profile service available"
    }
  },
  "event_handlers": {
    "registered": false,
    "count": 0,
    "events": []
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## Data Models

### Recommendation Item Model

```json
{
  "resource_id": "uuid",
  "title": "string",
  "score": "float (0.0-1.0)",
  "strategy": "string",
  "scores": {
    "collaborative": "float",
    "content": "float",
    "graph": "float",
    "quality": "float",
    "recency": "float"
  },
  "rank": "integer",
  "novelty_score": "float (0.0-1.0)",
  "view_count": "integer"
}
```

### User Profile Model

```json
{
  "user_id": "string",
  "diversity_preference": "float (0.0-1.0, default: 0.3)",
  "novelty_preference": "float (0.0-1.0, default: 0.2)",
  "recency_bias": "float (0.0-1.0, default: 0.5)",
  "research_domains": ["string"],
  "active_domain": "string",
  "excluded_sources": ["string"],
  "total_interactions": "integer",
  "last_active_at": "datetime (ISO 8601)"
}
```

### Interaction Model

```json
{
  "interaction_id": "uuid",
  "user_id": "string",
  "resource_id": "uuid",
  "interaction_type": "view|annotation|collection_add|export|rating",
  "interaction_strength": "float (0.0-1.0)",
  "is_positive": "boolean",
  "dwell_time": "integer (seconds, optional)",
  "scroll_depth": "float (0.0-1.0, optional)",
  "session_id": "string (optional)",
  "rating": "integer (1-5, optional)",
  "created_at": "datetime (ISO 8601)"
}
```

## Module Structure

The Recommendations module is implemented as a self-contained vertical slice:

**Module**: `app.modules.recommendations`  
**Router Prefix**: `/recommendations`  
**Version**: 1.0.0

```python
from app.modules.recommendations import (
    recommendations_router,
    HybridRecommendationService,
    UserProfileService,
    RecommendationResponse
)
```

### Events

**Emitted Events:**
- `recommendation.generated` - When recommendations are generated
- `user.profile_updated` - When user profile is updated

**Subscribed Events:**
- `resource.created` - Updates recommendation models
- `annotation.created` - Tracks user interactions
- `collection.resource_added` - Tracks user interactions

## Related Documentation

- [Resources API](resources.md) - Resource management
- [Collections API](collections.md) - Collection management
- [Graph API](graph.md) - Knowledge graph
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors, pagination
