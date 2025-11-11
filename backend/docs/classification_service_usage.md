# Classification Service Usage Guide

## Overview

The `ClassificationService` provides a unified interface for resource classification, supporting both ML-based classification (using transformer models) and rule-based classification (using keyword matching).

## Quick Start

### Basic Usage

```python
from app.services.classification_service import ClassificationService
from app.database.base import get_db

# Get database session
db = next(get_db())

# Initialize service with ML classification
service = ClassificationService(
    db=db,
    use_ml=True,
    confidence_threshold=0.3
)

# Classify a resource
result = service.classify_resource(resource_id=resource.id)

print(f"Method: {result['method']}")
print(f"Classifications: {result['classifications']}")
print(f"Filtered: {result['filtered_count']}")
```

## Configuration Options

### Initialization Parameters

```python
ClassificationService(
    db: Session,              # SQLAlchemy database session (required)
    use_ml: bool = True,      # Use ML classifier (True) or rule-based (False)
    confidence_threshold: float = 0.3  # Minimum confidence for predictions
)
```

### use_ml Flag

Controls which classification method to use:

- **`True`**: Use ML-based classification with transformer models
  - Higher accuracy
  - Confidence scores
  - Requires trained model
  - Falls back to rule-based if model unavailable

- **`False`**: Use rule-based classification with keyword matching
  - Fast and deterministic
  - No model required
  - Uses UDC-inspired codes (000-900)

### confidence_threshold

Filters ML predictions below this threshold:

- **Default**: 0.3 (30% confidence)
- **Range**: 0.0 to 1.0
- **Recommendation**: 
  - 0.3 for broad coverage
  - 0.5 for balanced precision/recall
  - 0.7 for high precision

## Classification Methods

### classify_resource()

Classifies a single resource using ML or rule-based approach.

```python
result = service.classify_resource(
    resource_id=uuid.UUID("..."),  # Resource UUID (required)
    use_ml=None                     # Override instance use_ml (optional)
)
```

**Parameters:**
- `resource_id`: UUID of resource to classify
- `use_ml`: Override instance `use_ml` setting (optional)

**Returns:**
```python
{
    "resource_id": "uuid-string",
    "method": "ml" or "rule_based",
    "classifications": [
        {
            "taxonomy_node_id": "uuid-string",  # For ML
            "confidence": 0.85,
            "needs_review": False
        }
    ],
    "filtered_count": 2  # Number of predictions below threshold
}
```

## Usage Examples

### Example 1: ML Classification

```python
# Initialize with ML classification
service = ClassificationService(db=db, use_ml=True)

# Classify resource
result = service.classify_resource(resource_id=resource.id)

# Process results
for classification in result['classifications']:
    node_id = classification['taxonomy_node_id']
    confidence = classification['confidence']
    needs_review = classification['needs_review']
    
    print(f"Node: {node_id}, Confidence: {confidence:.2f}")
    if needs_review:
        print("  ⚠️  Flagged for review (confidence < 0.7)")
```

### Example 2: Rule-Based Classification

```python
# Initialize with rule-based classification
service = ClassificationService(db=db, use_ml=False)

# Classify resource
result = service.classify_resource(resource_id=resource.id)

# Get classification code
code = result['classifications'][0]['classification_code']
print(f"Classification Code: {code}")
```

### Example 3: Custom Confidence Threshold

```python
# High precision mode (only confident predictions)
service = ClassificationService(
    db=db,
    use_ml=True,
    confidence_threshold=0.7
)

result = service.classify_resource(resource_id=resource.id)
print(f"Filtered {result['filtered_count']} low-confidence predictions")
```

### Example 4: Per-Call Override

```python
# Initialize with ML
service = ClassificationService(db=db, use_ml=True)

# Use ML for this resource
ml_result = service.classify_resource(resource_id=resource1.id, use_ml=True)

# Use rule-based for this resource
rule_result = service.classify_resource(resource_id=resource2.id, use_ml=False)
```

### Example 5: Batch Classification

```python
service = ClassificationService(db=db, use_ml=True)

resources = db.query(Resource).filter(Resource.classification_id.is_(None)).all()

for resource in resources:
    try:
        result = service.classify_resource(resource_id=resource.id)
        print(f"✓ Classified {resource.title}: {result['method']}")
    except Exception as e:
        print(f"✗ Failed to classify {resource.title}: {e}")
```

## Integration with Resource Ingestion

```python
from app.services.classification_service import ClassificationService
from app.services.resource_service import ResourceService

def ingest_resource(url: str, db: Session):
    # Create resource
    resource_service = ResourceService(db)
    resource = resource_service.create_resource(url=url)
    
    # Extract content
    resource_service.extract_content(resource.id)
    
    # Generate embeddings
    resource_service.generate_embeddings(resource.id)
    
    # Classify resource (NEW)
    classification_service = ClassificationService(db=db, use_ml=True)
    result = classification_service.classify_resource(resource_id=resource.id)
    
    print(f"Classified with {result['method']}: {len(result['classifications'])} categories")
    
    # Continue with quality scoring, etc.
    return resource
```

## Error Handling

### Resource Not Found

```python
try:
    result = service.classify_resource(resource_id=invalid_id)
except ValueError as e:
    print(f"Error: {e}")  # "Resource with id ... not found"
```

### ML Classifier Unavailable

```python
# Service automatically falls back to rule-based
service = ClassificationService(db=db, use_ml=True)

# If ML model not available, falls back automatically
result = service.classify_resource(resource_id=resource.id)

# Check which method was used
if result['method'] == 'rule_based':
    print("Fell back to rule-based classification")
```

### Graceful Degradation

```python
# Service handles failures gracefully
service = ClassificationService(db=db, use_ml=True)

try:
    result = service.classify_resource(resource_id=resource.id)
    # Will use rule-based if ML fails
except Exception as e:
    print(f"Classification failed: {e}")
```

## Performance Considerations

### ML Classification
- **Inference Time**: <100ms per resource
- **Batch Processing**: Use MLClassificationService.predict_batch() for efficiency
- **GPU Acceleration**: Automatically uses CUDA if available

### Rule-Based Classification
- **Inference Time**: <10ms per resource
- **No Model Loading**: Instant startup
- **Deterministic**: Same input always produces same output

## Best Practices

1. **Use ML for Production**: Higher accuracy and confidence scores
2. **Set Appropriate Threshold**: Balance precision and recall
3. **Monitor Filtered Count**: Track how many predictions are filtered
4. **Review Low Confidence**: Use `needs_review` flag for human review
5. **Batch Processing**: For large datasets, use batch methods
6. **Error Handling**: Always wrap in try-except for robustness

## Troubleshooting

### ML Classifier Not Loading

**Symptom**: Service falls back to rule-based even with `use_ml=True`

**Solutions**:
1. Check if model is trained and saved
2. Verify model path: `models/classification/v1.0/`
3. Check dependencies: `transformers`, `torch`
4. Review logs for error messages

### Low Classification Accuracy

**Symptom**: Many low-confidence predictions

**Solutions**:
1. Retrain model with more labeled data
2. Use semi-supervised learning
3. Adjust confidence threshold
4. Review and correct flagged predictions

### High Filtered Count

**Symptom**: Many predictions filtered by threshold

**Solutions**:
1. Lower confidence threshold (e.g., 0.3 → 0.2)
2. Retrain model for better confidence calibration
3. Use active learning to improve model

## Related Documentation

- [ML Classification Service](./ml_classification_service_usage.md)
- [Taxonomy Service](./taxonomy_service_usage.md)
- [Active Learning Workflow](./active_learning_workflow.md)
- [API Documentation](./API_DOCUMENTATION.md)

## Requirements Satisfied

- **Requirement 6.5**: Filter predictions by confidence threshold (>=0.3)
- **Requirement 12.4**: Use ML classifier when use_ml flag is true
- **Requirement 12.5**: Fall back to rule-based when use_ml flag is false
