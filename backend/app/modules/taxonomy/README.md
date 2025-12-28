# Taxonomy Module

## Purpose

The Taxonomy module provides ML-based classification and taxonomy management for Neo Alexandria 2.0. It enables automatic resource classification, hierarchical taxonomy tree management, and active learning capabilities to improve classification accuracy over time.

## Features

- **Taxonomy Tree Management**: Create, update, and organize hierarchical taxonomy nodes
- **ML Classification**: Automatic resource classification using trained ML models
- **Active Learning**: Identify uncertain classifications for human feedback
- **Model Training**: Train and retrain classification models with new data
- **Multi-label Classification**: Assign resources to multiple taxonomy categories

## Public Interface

### Router
- `taxonomy_router`: FastAPI router with all taxonomy endpoints

### Services
- `TaxonomyService`: Core taxonomy tree management
- `MLClassificationService`: ML-based classification
- `ClassificationService`: Classification coordination

### Schemas
- `TaxonomyNodeCreate`: Create taxonomy node request
- `TaxonomyNodeUpdate`: Update taxonomy node request
- `TaxonomyNodeResponse`: Taxonomy node response
- `TaxonomyTreeResponse`: Full taxonomy tree response
- `ClassificationRequest`: Classification request
- `ClassificationResponse`: Classification result
- `TrainingRequest`: Model training request
- `TrainingResponse`: Training result
- `ActiveLearningRequest`: Active learning request
- `ActiveLearningResponse`: Uncertain samples response

## Events

### Emitted Events

#### `resource.classified`
Emitted when a resource is classified.

**Payload:**
```python
{
    "resource_id": int,
    "classifications": List[Dict],
    "confidence_scores": Dict[str, float],
    "timestamp": datetime
}
```

#### `taxonomy.node_created`
Emitted when a new taxonomy node is created.

**Payload:**
```python
{
    "node_id": int,
    "name": str,
    "parent_id": Optional[int],
    "timestamp": datetime
}
```

#### `taxonomy.model_trained`
Emitted when an ML model is trained or retrained.

**Payload:**
```python
{
    "model_version": str,
    "accuracy": float,
    "training_samples": int,
    "timestamp": datetime
}
```

### Subscribed Events

#### `resource.created`
Triggers auto-classification of newly created resources.

**Handler:** `handle_resource_created()`

## API Endpoints

### Taxonomy Management (8 endpoints)

1. **POST /taxonomy/nodes** - Create taxonomy node
2. **PUT /taxonomy/nodes/{node_id}** - Update node
3. **DELETE /taxonomy/nodes/{node_id}** - Delete node
4. **POST /taxonomy/nodes/{node_id}/move** - Move node in tree
5. **GET /taxonomy/tree** - Get full taxonomy tree
6. **GET /taxonomy/nodes/{node_id}/ancestors** - Get node ancestors
7. **GET /taxonomy/nodes/{node_id}/descendants** - Get node descendants
8. **POST /taxonomy/classify/{resource_id}** - Classify resource

### Active Learning (2 endpoints)

9. **GET /taxonomy/active-learning/uncertain** - Get uncertain samples
10. **POST /taxonomy/active-learning/feedback** - Submit feedback

### Model Training (1 endpoint)

11. **POST /taxonomy/train** - Train ML model

## Dependencies

### Shared Kernel
- `shared.database`: Database session management
- `shared.event_bus`: Event-driven communication
- `shared.base_model`: Base SQLAlchemy model
- `shared.embeddings`: Text embeddings for classification
- `shared.ai_core`: AI operations

### External Libraries
- `transformers`: Hugging Face models for classification
- `torch`: PyTorch for ML operations
- `scikit-learn`: ML utilities and metrics

## Usage Examples

### Create Taxonomy Node

```python
from app.modules.taxonomy import TaxonomyService, TaxonomyNodeCreate

service = TaxonomyService(db)
node = await service.create_node(
    TaxonomyNodeCreate(
        name="Machine Learning",
        parent_id=1,  # Computer Science node
        description="ML and AI topics"
    )
)
```

### Classify Resource

```python
from app.modules.taxonomy import MLClassificationService

ml_service = MLClassificationService(db)
result = await ml_service.classify_resource(resource_id=123)
# Returns: ClassificationResponse with predicted categories and confidence scores
```

### Active Learning Workflow

```python
from app.modules.taxonomy import MLClassificationService

# Get uncertain samples
uncertain = await ml_service.get_uncertain_samples(limit=10)

# Submit human feedback
await ml_service.submit_feedback(
    resource_id=123,
    correct_category="Machine Learning",
    confidence=0.95
)

# Retrain model with new feedback
await ml_service.train_model()
```

## Architecture

### Module Structure

```
taxonomy/
├── __init__.py              # Public interface
├── router.py                # FastAPI endpoints
├── service.py               # Taxonomy tree management
├── ml_service.py            # ML classification
├── classification_service.py # Classification coordination
├── schema.py                # Pydantic schemas
├── model.py                 # SQLAlchemy models
├── handlers.py              # Event handlers
├── README.md                # This file
└── tests/
    ├── test_service.py
    ├── test_ml_service.py
    ├── test_router.py
    └── test_handlers.py
```

### Event Flow

```
resource.created
    ↓
handle_resource_created()
    ↓
MLClassificationService.classify()
    ↓
resource.classified event
    ↓
[Other modules can react]
```

## Testing

### Unit Tests
- `test_service.py`: Taxonomy tree operations
- `test_ml_service.py`: ML classification logic
- `test_router.py`: API endpoint behavior

### Integration Tests
- `test_handlers.py`: Event-driven classification workflow
- End-to-end classification pipeline

## Performance Considerations

- **Classification Caching**: Cache classification results to avoid recomputation
- **Batch Classification**: Support batch operations for multiple resources
- **Model Loading**: Lazy load ML models to reduce startup time
- **Active Learning**: Prioritize uncertain samples for efficient labeling

## Future Enhancements

- Multi-model ensemble classification
- Hierarchical classification (predict at multiple levels)
- Transfer learning from pre-trained models
- Automated taxonomy expansion based on content
- Classification confidence calibration

## Version History

- **1.0.0** (Phase 14): Initial extraction from layered architecture
  - Moved from `routers/taxonomy.py` and `routers/classification.py`
  - Moved from `services/taxonomy_service.py`, `services/ml_classification_service.py`, `services/classification_service.py`
  - Implemented event-driven auto-classification
  - Added active learning support
