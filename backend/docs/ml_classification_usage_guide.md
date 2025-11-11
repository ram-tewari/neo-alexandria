# ML Classification Usage Guide

## Overview

This guide provides comprehensive instructions for using the ML-powered classification system in Neo Alexandria 2.0. The system uses fine-tuned transformer models (BERT/DistilBERT) to automatically categorize resources into a hierarchical taxonomy with confidence scores, semi-supervised learning capabilities, and active learning workflows for continuous improvement.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Taxonomy Management](#taxonomy-management)
3. [Model Training Workflow](#model-training-workflow)
4. [Semi-Supervised Learning](#semi-supervised-learning)
5. [Active Learning Workflow](#active-learning-workflow)
6. [Resource Classification](#resource-classification)
7. [Model Versioning](#model-versioning)
8. [Performance Optimization](#performance-optimization)
9. [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

1. Install ML dependencies:
```bash
pip install transformers torch scikit-learn
```

2. Verify CUDA availability (optional, for GPU acceleration):
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
```

3. Run database migrations:
```bash
cd backend
alembic upgrade head
```

### Basic Workflow

1. **Create taxonomy structure**
2. **Prepare training data** (labeled examples)
3. **Train the model** (with optional semi-supervised learning)
4. **Classify resources** automatically
5. **Review uncertain predictions** (active learning)
6. **Provide feedback** to improve the model
7. **Retrain periodically** with accumulated feedback

## Taxonomy Management

### Creating a Taxonomy Tree

Build a hierarchical category structure for your knowledge base:

```bash
# Create root node
curl -X POST http://127.0.0.1:8000/taxonomy/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Computer Science",
    "description": "Computing and software topics",
    "keywords": ["programming", "algorithms", "software"]
  }'
# Response: {"id": "cs-node-id", ...}

# Create child node
curl -X POST http://127.0.0.1:8000/taxonomy/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Machine Learning",
    "parent_id": "cs-node-id",
    "description": "ML and AI topics",
    "keywords": ["neural networks", "deep learning", "AI"]
  }'
# Response: {"id": "ml-node-id", ...}

# Create grandchild node
curl -X POST http://127.0.0.1:8000/taxonomy/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Deep Learning",
    "parent_id": "ml-node-id",
    "description": "Neural networks with multiple layers",
    "keywords": ["CNN", "RNN", "transformers"]
  }'
# Response: {"id": "dl-node-id", ...}
```

### Retrieving the Taxonomy Tree

```bash
# Get full tree
curl "http://127.0.0.1:8000/taxonomy/tree"

# Get subtree from specific node
curl "http://127.0.0.1:8000/taxonomy/tree?root_id=ml-node-id&max_depth=2"
```

### Managing Taxonomy Nodes

```bash
# Update node metadata
curl -X PUT http://127.0.0.1:8000/taxonomy/nodes/ml-node-id \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description",
    "keywords": ["AI", "neural networks", "supervised learning"]
  }'

# Move node to different parent
curl -X POST http://127.0.0.1:8000/taxonomy/nodes/ml-node-id/move \
  -H "Content-Type: application/json" \
  -d '{"new_parent_id": "new-parent-id"}'

# Delete node (reparent children)
curl -X DELETE "http://127.0.0.1:8000/taxonomy/nodes/ml-node-id"

# Delete node and all descendants
curl -X DELETE "http://127.0.0.1:8000/taxonomy/nodes/ml-node-id?cascade=true"
```

## Model Training Workflow

### Step 1: Prepare Training Data

Collect labeled examples where each example has:
- **Text**: Resource content (title + description + full text)
- **Taxonomy IDs**: One or more category IDs the resource belongs to

```python
labeled_data = [
    {
        "text": "Introduction to neural networks and backpropagation algorithms for deep learning",
        "taxonomy_ids": ["ml-node-id", "dl-node-id"]
    },
    {
        "text": "Database normalization techniques and SQL query optimization strategies",
        "taxonomy_ids": ["database-node-id"]
    },
    {
        "text": "Convolutional neural networks for image classification and object detection",
        "taxonomy_ids": ["dl-node-id", "computer-vision-node-id"]
    }
    # ... more examples (minimum 100, recommended 500+)
]
```

### Step 2: Train the Model

```bash
curl -X POST http://127.0.0.1:8000/taxonomy/train \
  -H "Content-Type: application/json" \
  -d '{
    "labeled_data": [
      {
        "text": "Introduction to neural networks and backpropagation",
        "taxonomy_ids": ["ml-node-id", "dl-node-id"]
      },
      {
        "text": "Database normalization and SQL optimization",
        "taxonomy_ids": ["database-node-id"]
      }
    ],
    "epochs": 3,
    "batch_size": 16,
    "learning_rate": 2e-5
  }'
```

**Response:**
```json
{
  "status": "accepted",
  "message": "Training task enqueued",
  "training_id": "training-uuid",
  "labeled_examples": 150,
  "estimated_duration_minutes": 10
}
```

### Step 3: Monitor Training

Training runs as a background task. The model will be saved to:
```
models/classification/v1.0/
├── pytorch_model.bin
├── config.json
├── tokenizer_config.json
├── vocab.txt
└── label_map.json
```

### Training Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `epochs` | 3 | Number of training epochs |
| `batch_size` | 16 | Batch size (increase for GPU) |
| `learning_rate` | 2e-5 | Learning rate for optimizer |

**Recommendations:**
- **Small dataset (<500 examples)**: 3-5 epochs
- **Medium dataset (500-2000 examples)**: 3 epochs
- **Large dataset (>2000 examples)**: 2-3 epochs
- **GPU available**: batch_size=32
- **CPU only**: batch_size=8

## Semi-Supervised Learning

Semi-supervised learning leverages unlabeled data to improve model performance with minimal labeled examples.

### When to Use

- You have <500 labeled examples
- You have a large corpus of unlabeled content (1000+ documents)
- You want to reduce manual labeling effort

### How It Works

1. Train initial model on labeled data
2. Predict categories for unlabeled data
3. Select high-confidence predictions (>= 0.9)
4. Add pseudo-labeled examples to training set
5. Re-train model for 1 epoch
6. Repeat if needed

### Usage Example

```bash
curl -X POST http://127.0.0.1:8000/taxonomy/train \
  -H "Content-Type: application/json" \
  -d '{
    "labeled_data": [
      {
        "text": "Neural network tutorial with code examples",
        "taxonomy_ids": ["ml-node-id", "dl-node-id"]
      }
      # ... 200 labeled examples
    ],
    "unlabeled_texts": [
      "Article about convolutional neural networks",
      "Tutorial on recurrent neural networks",
      "Guide to transformer architectures"
      # ... 5000 unlabeled texts
    ],
    "epochs": 3,
    "batch_size": 16
  }'
```

### Expected Results

- **Accuracy improvement**: 5-15% over supervised-only
- **Labeling reduction**: Train with 200 labeled + 5000 unlabeled vs 1000 labeled
- **Training time**: +20-30% due to pseudo-labeling iteration

### Best Practices

1. **Quality unlabeled data**: Use content similar to your target domain
2. **High confidence threshold**: Keep at 0.9 to avoid noise
3. **Balanced dataset**: Ensure unlabeled data covers all categories
4. **Iterative approach**: Start with labeled-only, then add unlabeled data

## Active Learning Workflow

Active learning identifies uncertain predictions for human review, focusing labeling effort on the most valuable examples.

### Step 1: Identify Uncertain Predictions

```bash
curl "http://127.0.0.1:8000/taxonomy/active-learning/uncertain?limit=50"
```

**Response:**
```json
[
  {
    "resource_id": "resource-uuid-1",
    "title": "Introduction to Neural Networks",
    "uncertainty_score": 0.87,
    "predicted_categories": [
      {
        "taxonomy_node_id": "ml-node-id",
        "name": "Machine Learning",
        "confidence": 0.65
      },
      {
        "taxonomy_node_id": "dl-node-id",
        "name": "Deep Learning",
        "confidence": 0.62
      }
    ]
  }
]
```

### Step 2: Review and Label

Present uncertain resources to human reviewers:

1. Show resource content
2. Display predicted categories with confidence scores
3. Ask reviewer to select correct categories
4. Submit feedback

### Step 3: Submit Feedback

```bash
curl -X POST http://127.0.0.1:8000/taxonomy/active-learning/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "resource_id": "resource-uuid-1",
    "correct_taxonomy_ids": ["ml-node-id", "dl-node-id"]
  }'
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

### Step 4: Retrain When Threshold Reached

When `manual_labels_count >= 100`, retrain the model:

```bash
# Fetch all manual labels from database
# Prepare training data
# Call /taxonomy/train endpoint
```

### Uncertainty Metrics

The system computes uncertainty using three metrics:

1. **Entropy**: Measures prediction uncertainty across all classes
   ```
   entropy = -Σ(p * log(p))
   ```

2. **Margin**: Difference between top-2 predictions
   ```
   margin = confidence_1st - confidence_2nd
   ```
   Small margin = uncertain

3. **Max Confidence**: Highest probability
   ```
   max_confidence = max(all_confidences)
   ```
   Low confidence = uncertain

**Combined Score:**
```
uncertainty = entropy * (1 - margin) * (1 - max_confidence)
```

### Active Learning Benefits

- **60%+ reduction** in labeling effort
- **Focus on difficult cases** where model is uncertain
- **Continuous improvement** through feedback loops
- **Efficient use** of human expertise

## Resource Classification

### Automatic Classification During Ingestion

Resources are automatically classified when ingested:

```bash
# Ingest resource (classification happens automatically)
curl -X POST http://127.0.0.1:8000/resources \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/ml-article"}'
```

**Background Process:**
1. Content extraction
2. Embedding generation
3. **ML classification** ← Automatic
4. Quality scoring
5. Storage

### Manual Classification

Classify an existing resource:

```bash
curl -X POST "http://127.0.0.1:8000/taxonomy/classify/resource-uuid"
```

### Classification Results

Classifications are stored with metadata:

```python
{
    "resource_id": "resource-uuid",
    "taxonomy_node_id": "ml-node-id",
    "confidence": 0.92,
    "is_predicted": True,
    "predicted_by": "v1.0",
    "needs_review": False,  # True if confidence < 0.7
    "review_priority": None  # Set if needs_review=True
}
```

### Confidence Thresholds

| Confidence | Behavior | Action |
|------------|----------|--------|
| >= 0.7 | High confidence | Auto-accept |
| 0.3 - 0.7 | Medium confidence | Flag for review |
| < 0.3 | Low confidence | Filtered out |

### Multi-Label Classification

Resources can belong to multiple categories:

```json
{
  "resource_id": "resource-uuid",
  "classifications": [
    {
      "taxonomy_node_id": "ml-node-id",
      "name": "Machine Learning",
      "confidence": 0.95
    },
    {
      "taxonomy_node_id": "dl-node-id",
      "name": "Deep Learning",
      "confidence": 0.88
    },
    {
      "taxonomy_node_id": "nlp-node-id",
      "name": "Natural Language Processing",
      "confidence": 0.42
    }
  ]
}
```

## Model Versioning

### Version Format

Models use semantic versioning: `v{major}.{minor}`

- **Major**: Breaking changes (label mapping changes, architecture changes)
- **Minor**: Improvements (retraining on same labels)

### Storage Structure

```
models/classification/
├── v1.0/
│   ├── pytorch_model.bin
│   ├── config.json
│   ├── tokenizer_config.json
│   ├── vocab.txt
│   └── label_map.json
├── v1.1/
│   └── ...
└── v2.0/
    └── ...
```

### Tracking Classifications

Each classification stores the model version:

```python
{
    "predicted_by": "v1.0",  # Model version
    "confidence": 0.92,
    "created_at": "2024-01-01T10:00:00Z"
}
```

### Rollback

To rollback to a previous model version:

1. Update `MLClassificationService` initialization:
```python
ml_service = MLClassificationService(
    db=db,
    model_version="v1.0"  # Specify version
)
```

2. Re-classify resources if needed

### A/B Testing

Compare model versions:

1. Classify resources with version A
2. Classify same resources with version B
3. Compare confidence scores and accuracy
4. Select best-performing version

## Performance Optimization

### GPU Acceleration

**Enable GPU:**
```python
import torch
if torch.cuda.is_available():
    print("GPU available - will be used automatically")
else:
    print("GPU not available - using CPU")
```

**Performance Comparison:**

| Operation | CPU | GPU | Speedup |
|-----------|-----|-----|---------|
| Single prediction | 80ms | 15ms | 5.3x |
| Batch (32) | 2.5s | 400ms | 6.3x |
| Training (500 examples) | 45min | 8min | 5.6x |

### Batch Processing

Process multiple resources efficiently:

```python
# Instead of:
for resource in resources:
    classify_resource(resource.id)  # Slow

# Use batch classification:
texts = [r.content for r in resources]
predictions = ml_service.predict_batch(texts, top_k=5)
```

### Model Caching

Models are lazy-loaded and cached:

- **First prediction**: ~2s (model loading)
- **Subsequent predictions**: <100ms (cached model)

### Inference Optimization

**Tips:**
1. Use batch processing for multiple resources
2. Enable GPU if available
3. Use DistilBERT instead of BERT (60% faster, 97% accuracy)
4. Adjust `top_k` parameter (fewer predictions = faster)

## Troubleshooting

### Model Not Found

**Error:** `No fine-tuned model found, using base model`

**Solution:**
1. Train a model first using `/taxonomy/train`
2. Verify model saved to `models/classification/{version}/`
3. Check model version in `MLClassificationService` initialization

### Low Classification Accuracy

**Symptoms:**
- Many low-confidence predictions
- Incorrect categories assigned
- High uncertainty scores

**Solutions:**
1. **Increase training data**: Aim for 500+ labeled examples
2. **Balance dataset**: Ensure all categories have examples
3. **Use semi-supervised learning**: Leverage unlabeled data
4. **Collect feedback**: Use active learning to improve
5. **Refine taxonomy**: Ensure categories are distinct and well-defined

### CUDA Out of Memory

**Error:** `RuntimeError: CUDA out of memory`

**Solutions:**
1. Reduce batch size: `batch_size=8` or `batch_size=4`
2. Use DistilBERT instead of BERT (smaller model)
3. Clear GPU cache: `torch.cuda.empty_cache()`
4. Use CPU instead: Disable CUDA

### Slow Training

**Symptoms:**
- Training takes >1 hour for 500 examples
- High CPU usage

**Solutions:**
1. **Enable GPU**: Install CUDA and PyTorch with GPU support
2. **Increase batch size**: Use `batch_size=32` on GPU
3. **Reduce epochs**: Use 2-3 epochs instead of 5
4. **Use DistilBERT**: 60% faster than BERT

### Classification Not Triggered

**Symptoms:**
- Resources ingested but not classified
- No classifications in database

**Solutions:**
1. Check `use_ml` flag in `ClassificationService`
2. Verify model exists and is loaded
3. Check background task logs for errors
4. Manually trigger: `POST /taxonomy/classify/{resource_id}`

### Circular Reference Error

**Error:** `Cannot move node to its own descendant`

**Solution:**
- Verify new parent is not a descendant of the node being moved
- Check taxonomy tree structure before moving

### Resources Prevent Deletion

**Error:** `Cannot delete taxonomy node with 15 assigned resources`

**Solution:**
1. Remove resource classifications first
2. Or move resources to different category
3. Then delete the node

## Code Examples

### Python Client Example

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# Create taxonomy
def create_taxonomy():
    # Root node
    response = requests.post(
        f"{BASE_URL}/taxonomy/nodes",
        json={
            "name": "Computer Science",
            "description": "Computing topics"
        }
    )
    cs_id = response.json()["id"]
    
    # Child node
    response = requests.post(
        f"{BASE_URL}/taxonomy/nodes",
        json={
            "name": "Machine Learning",
            "parent_id": cs_id,
            "description": "ML topics"
        }
    )
    ml_id = response.json()["id"]
    
    return cs_id, ml_id

# Train model
def train_model(labeled_data):
    response = requests.post(
        f"{BASE_URL}/taxonomy/train",
        json={
            "labeled_data": labeled_data,
            "epochs": 3,
            "batch_size": 16
        }
    )
    return response.json()

# Classify resource
def classify_resource(resource_id):
    response = requests.post(
        f"{BASE_URL}/taxonomy/classify/{resource_id}"
    )
    return response.json()

# Active learning workflow
def active_learning_loop():
    # Get uncertain predictions
    response = requests.get(
        f"{BASE_URL}/taxonomy/active-learning/uncertain",
        params={"limit": 50}
    )
    uncertain = response.json()
    
    # Review and submit feedback
    for item in uncertain:
        # Present to human reviewer
        correct_ids = get_human_feedback(item)
        
        # Submit feedback
        requests.post(
            f"{BASE_URL}/taxonomy/active-learning/feedback",
            json={
                "resource_id": item["resource_id"],
                "correct_taxonomy_ids": correct_ids
            }
        )

# Usage
cs_id, ml_id = create_taxonomy()
labeled_data = [
    {
        "text": "Neural networks tutorial",
        "taxonomy_ids": [ml_id]
    }
]
train_model(labeled_data)
classify_resource("resource-uuid")
active_learning_loop()
```

## Best Practices

### Taxonomy Design

1. **Keep it simple**: Start with 10-20 categories, expand as needed
2. **Clear boundaries**: Ensure categories are distinct and non-overlapping
3. **Balanced depth**: Aim for 3-5 levels maximum
4. **Descriptive names**: Use clear, unambiguous category names
5. **Add keywords**: Help the model learn category semantics

### Training Data

1. **Quality over quantity**: 500 good examples > 2000 poor examples
2. **Balanced distribution**: Each category should have 20+ examples
3. **Representative samples**: Include diverse content for each category
4. **Multi-label examples**: Include resources that span multiple categories
5. **Regular updates**: Retrain with new feedback every 100-200 labels

### Active Learning

1. **Review regularly**: Check uncertain predictions weekly
2. **Prioritize high-uncertainty**: Focus on uncertainty_score > 0.8
3. **Batch reviews**: Review 50-100 items at a time
4. **Track metrics**: Monitor accuracy improvement over time
5. **Retrain periodically**: Retrain when threshold reached (100 labels)

### Performance

1. **Use GPU**: 5-6x faster training and inference
2. **Batch processing**: Process multiple resources together
3. **Cache models**: Models are cached after first load
4. **Monitor resources**: Track GPU memory and CPU usage
5. **Optimize taxonomy**: Fewer categories = faster inference

## Additional Resources

- **API Documentation**: See `API_DOCUMENTATION.md` for complete endpoint reference
- **Developer Guide**: See `DEVELOPER_GUIDE.md` for architecture details
- **Examples**: See `EXAMPLES.md` for more code examples
- **Changelog**: See `CHANGELOG.md` for version history

## Support

For issues, questions, or feature requests:
- GitHub Issues: Report bugs and request features
- Documentation: Check API docs and developer guide
- Community: Join discussions and share feedback
