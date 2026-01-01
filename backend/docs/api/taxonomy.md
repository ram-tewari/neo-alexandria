# Taxonomy API

ML-based classification and taxonomy management endpoints.

## Overview

The Taxonomy API provides functionality for:
- Hierarchical taxonomy tree management
- ML-based resource classification using Random Forest and Logistic Regression
- Rule-based classification fallback
- Active learning for uncertain predictions
- Model training and retraining
- Classification confidence scoring

## Endpoints

### POST /taxonomy/categories

Create a new taxonomy category.

**Request Body:**
```json
{
  "name": "Machine Learning",
  "description": "Resources about machine learning and AI",
  "parent_id": null,
  "allow_resources": true
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Machine Learning",
  "slug": "machine-learning",
  "parent_id": null,
  "level": 0,
  "path": "/machine-learning",
  "description": "Resources about machine learning and AI",
  "allow_resources": true
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/taxonomy/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Machine Learning",
    "description": "ML and AI resources",
    "allow_resources": true
  }'
```

---

### POST /taxonomy/classify/{resource_id}

Classify a resource using ML and/or rule-based classification.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `use_ml` | boolean | Use ML-based classification | true |
| `use_rules` | boolean | Use rule-based classification | true |

**Response:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "primary_prediction": {
    "node_id": "660e8400-e29b-41d4-a716-446655440001",
    "node_name": "Machine Learning",
    "confidence": 0.87,
    "method": "ml"
  },
  "alternative_predictions": [
    {
      "node_id": "770e8400-e29b-41d4-a716-446655440002",
      "node_name": "Deep Learning",
      "confidence": 0.65,
      "method": "ml"
    }
  ],
  "applied_to_resource": true
}
```

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/taxonomy/classify/550e8400-e29b-41d4-a716-446655440000?use_ml=true&use_rules=true"
```

---

### GET /taxonomy/predictions/{resource_id}

Get classification predictions for a resource.

**Response:**
```json
{
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "primary_prediction": {
    "node_id": "660e8400-e29b-41d4-a716-446655440001",
    "node_name": "Machine Learning",
    "confidence": 0.87,
    "method": "ml"
  },
  "alternative_predictions": [
    {
      "node_id": "770e8400-e29b-41d4-a716-446655440002",
      "node_name": "Deep Learning",
      "confidence": 0.65,
      "method": "ml"
    }
  ]
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/taxonomy/predictions/550e8400-e29b-41d4-a716-446655440000"
```

---

### POST /taxonomy/retrain

Retrain the ML classification model with new labeled data.

**Request Body:**
```json
{
  "samples": [
    {
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "node_id": "660e8400-e29b-41d4-a716-446655440001"
    },
    {
      "resource_id": "770e8400-e29b-41d4-a716-446655440002",
      "node_id": "660e8400-e29b-41d4-a716-446655440001"
    }
  ],
  "validation_split": 0.2,
  "model_type": "random_forest"
}
```

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `validation_split` | float | Fraction for validation (0.0-1.0) | 0.2 |
| `model_type` | string | Model type: random_forest or logistic | random_forest |

**Response:**
```json
{
  "accuracy": 0.89,
  "f1_score": 0.87,
  "precision": 0.88,
  "recall": 0.86,
  "training_samples": 800,
  "validation_samples": 200,
  "model_type": "random_forest",
  "training_time_seconds": 45.3
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/taxonomy/retrain \
  -H "Content-Type: application/json" \
  -d '{
    "samples": [...],
    "validation_split": 0.2,
    "model_type": "random_forest"
  }'
```

---

### GET /taxonomy/uncertain

Get resources with uncertain classifications for active learning.

Returns resources where the classification confidence is below the threshold, indicating they would benefit from manual review.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `threshold` | float | Confidence threshold (0.0-1.0) | 0.5 |
| `limit` | integer | Maximum resources to return | 100 |

**Response:**
```json
{
  "threshold": 0.5,
  "count": 15,
  "resource_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001"
  ]
}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/taxonomy/uncertain?threshold=0.5&limit=100"
```

## Data Models

### Category Model

```json
{
  "id": "uuid",
  "name": "string (required)",
  "slug": "string (auto-generated)",
  "description": "string (optional)",
  "parent_id": "uuid (optional)",
  "level": "integer",
  "path": "string",
  "allow_resources": "boolean (default: true)"
}
```

### Classification Result Model

```json
{
  "resource_id": "uuid",
  "primary_prediction": {
    "node_id": "uuid",
    "node_name": "string",
    "confidence": "float (0.0-1.0)",
    "method": "ml|rules"
  },
  "alternative_predictions": [
    {
      "node_id": "uuid",
      "node_name": "string",
      "confidence": "float (0.0-1.0)",
      "method": "ml|rules"
    }
  ],
  "applied_to_resource": "boolean"
}
```

### Training Metrics Model

```json
{
  "accuracy": "float (0.0-1.0)",
  "f1_score": "float (0.0-1.0)",
  "precision": "float (0.0-1.0)",
  "recall": "float (0.0-1.0)",
  "training_samples": "integer",
  "validation_samples": "integer",
  "model_type": "random_forest|logistic",
  "training_time_seconds": "float"
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
    ClassificationService,
    MLClassificationService
)
```

### Events

**Emitted Events:**
- `resource.classified` - When a resource is classified
- `taxonomy.model_trained` - When ML model is trained/retrained

**Subscribed Events:**
- `resource.created` - Triggers automatic classification

## Related Documentation

- [Resources API](resources.md) - Resource management
- [Quality API](quality.md) - Quality assessment
- [Architecture: Modules](../architecture/modules.md) - Module architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [API Overview](overview.md) - Authentication, errors, pagination
