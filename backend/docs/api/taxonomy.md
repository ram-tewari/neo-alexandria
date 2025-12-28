# Taxonomy API

Hierarchical taxonomy management and ML-powered classification endpoints.

## Overview

The Taxonomy API provides:
- CRUD operations for hierarchical taxonomy trees
- Materialized paths for efficient queries
- ML-powered resource classification
- Active learning for continuous model improvement
- Authority control for subjects and classification

## Taxonomy Management Endpoints

### POST /taxonomy/nodes

Create a new taxonomy node in the hierarchical tree.

**Request Body:**
```json
{
  "name": "Machine Learning",
  "parent_id": "550e8400-e29b-41d4-a716-446655440000",
  "description": "ML and deep learning topics",
  "keywords": ["neural networks", "deep learning"],
  "allow_resources": true
}
```

**Response (200 OK):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "Machine Learning",
  "slug": "machine-learning",
  "parent_id": "550e8400-e29b-41d4-a716-446655440000",
  "level": 1,
  "path": "/computer-science/machine-learning",
  "description": "ML and deep learning topics",
  "keywords": ["neural networks", "deep learning"],
  "resource_count": 0,
  "descendant_resource_count": 0,
  "is_leaf": true,
  "allow_resources": true,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

---

### PUT /taxonomy/nodes/{node_id}

Update taxonomy node metadata.

**Request Body:**
```json
{
  "name": "Deep Learning",
  "description": "Neural networks with multiple layers",
  "keywords": ["CNN", "RNN", "transformers"],
  "allow_resources": true
}
```

**Note:** To change parent, use the move endpoint instead.

---

### DELETE /taxonomy/nodes/{node_id}

Delete a taxonomy node.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `cascade` | boolean | Delete descendants vs reparent children | false |

**Behavior:**
- `cascade=false`: Child nodes reparented to deleted node's parent
- `cascade=true`: All descendant nodes deleted recursively
- Fails if node has assigned resources

---

### POST /taxonomy/nodes/{node_id}/move

Move a taxonomy node to a different parent.

**Request Body:**
```json
{
  "new_parent_id": "770e8400-e29b-41d4-a716-446655440002"
}
```

**Validation:**
- Prevents circular references
- Prevents self-parenting
- Updates level and path for node and all descendants

---

### GET /taxonomy/tree

Retrieve the hierarchical taxonomy tree as nested JSON.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `root_id` | string | Starting node UUID | null (all roots) |
| `max_depth` | integer | Maximum tree depth | null (unlimited) |

**Response:** Nested tree structure with `children` arrays.

---

### GET /taxonomy/nodes/{node_id}/ancestors

Get all ancestor nodes for breadcrumb navigation.

**Performance:** O(depth) using materialized path, typically <10ms

---

### GET /taxonomy/nodes/{node_id}/descendants

Get all descendant nodes at any depth.

**Performance:** O(1) query using path pattern matching, typically <10ms

---

## Authority Control Endpoints

### GET /authority/subjects/suggest

Get subject suggestions for autocomplete.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query (required) |

**Response:**
```json
["Machine Learning", "Artificial Intelligence", "Data Science"]
```

---

### GET /authority/classification/tree

Retrieve the hierarchical classification tree (Dewey-style).

**Response:**
```json
{
  "tree": [
    {
      "code": "000",
      "name": "General",
      "description": "General knowledge and reference",
      "children": [
        {
          "code": "004",
          "name": "Computer Science",
          "description": "Computer science and programming",
          "children": []
        }
      ]
    }
  ]
}
```

---

### GET /classification/tree

Alternative endpoint for classification tree (same response).

---

## ML Classification Endpoints

### POST /taxonomy/classify/{resource_id}

Classify a resource using the fine-tuned ML model.

**Response (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Classification task enqueued",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Background Processing:**
1. Load ML model (lazy loading)
2. Extract resource content
3. Predict taxonomy categories with confidence scores
4. Filter predictions (confidence >= 0.3)
5. Store classifications
6. Flag low-confidence predictions (< 0.7) for review

---

### GET /taxonomy/active-learning/uncertain

Get resources with uncertain classifications for human review.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of samples (1-1000) | 100 |

**Response:**
```json
[
  {
    "resource_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Introduction to Neural Networks",
    "uncertainty_score": 0.87,
    "predicted_categories": [
      {
        "taxonomy_node_id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "Machine Learning",
        "confidence": 0.65
      }
    ]
  }
]
```

**Uncertainty Metrics:**
- **Entropy**: Prediction uncertainty across all classes
- **Margin**: Difference between top-2 predictions
- **Confidence**: Maximum probability

---

### POST /taxonomy/active-learning/feedback

Submit human classification feedback.

**Request Body:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "correct_taxonomy_ids": ["node_id_1", "node_id_2"]
}
```

**Response:**
```json
{
  "updated": true,
  "message": "Feedback recorded successfully",
  "manual_labels_count": 87,
  "retraining_threshold": 100,
  "retraining_recommended": false
}
```

---

### POST /taxonomy/train

Initiate ML model fine-tuning.

**Request Body:**
```json
{
  "labeled_data": [
    {
      "text": "Introduction to neural networks",
      "taxonomy_ids": ["node_id_1", "node_id_2"]
    }
  ],
  "unlabeled_texts": ["Article about CNNs..."],
  "epochs": 3,
  "batch_size": 16,
  "learning_rate": 2e-5
}
```

**Response (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Training task enqueued",
  "training_id": "990e8400-e29b-41d4-a716-446655440004",
  "labeled_examples": 150,
  "unlabeled_examples": 5000,
  "estimated_duration_minutes": 15
}
```

**Semi-Supervised Learning:**
- High-confidence predictions (>= 0.9) become pseudo-labels
- Enables effective training with <500 labeled examples

## Data Models

### Taxonomy Node Model

```json
{
  "id": "uuid",
  "name": "string",
  "slug": "string",
  "parent_id": "uuid or null",
  "level": "integer",
  "path": "string (materialized path)",
  "description": "string or null",
  "keywords": ["string"],
  "resource_count": "integer",
  "descendant_resource_count": "integer",
  "is_leaf": "boolean",
  "allow_resources": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Module Structure

The Taxonomy module is implemented as a self-contained vertical slice:

**Module**: `app.modules.taxonomy`  
**Router Prefix**: `/taxonomy`  
**Version**: 1.0.0

```python
from app.modules.taxonomy import (
    taxonomy_router,
    TaxonomyService,
    MLClassificationService,
    ClassificationService,
    TaxonomyNode,
    ClassificationResult
)
```

### Events

**Emitted Events:**
- `resource.classified` - When a resource is classified
- `taxonomy.node_created` - When a taxonomy node is added
- `taxonomy.model_trained` - When the ML model is retrained

**Subscribed Events:**
- `resource.created` - Triggers automatic classification

## Related Documentation

- [Resources API](resources.md) - Content management
- [Quality API](quality.md) - Quality assessment
- [Authority API](authority.md) - Subject authority
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors
