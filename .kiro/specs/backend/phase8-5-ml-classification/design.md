# Phase 8.5 Design Document: Transformer-Based Classification & Hierarchical Taxonomy

## Overview

Phase 8.5 replaces the rule-based classification system with a state-of-the-art machine learning approach using fine-tuned transformer models (BERT/DistilBERT). The system implements a hierarchical taxonomy tree that users can manage, semi-supervised learning to leverage unlabeled data, and active learning workflows to continuously improve classification accuracy with minimal human effort.

### Key Objectives

- Achieve 40%+ improvement in classification accuracy over rule-based baseline
- Support hierarchical taxonomy with 5+ levels of depth
- Enable semi-supervised learning with <500 labeled examples
- Reduce labeling effort by 60%+ through active learning
- Maintain inference performance <100ms per resource
- Achieve F1 score >0.85 for multi-class classification

### Technology Stack

- **ML Framework**: PyTorch with Hugging Face Transformers
- **Base Models**: DistilBERT (primary), BERT-base (alternative)
- **Training**: Hugging Face Trainer API
- **Database**: SQLAlchemy with PostgreSQL/SQLite
- **API**: FastAPI with background tasks
- **Evaluation**: scikit-learn metrics

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                      │
│  /taxonomy/*  |  /classify/*  |  /active-learning/*         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Taxonomy    │  │     ML       │  │Classification│     │
│  │  Service     │  │ Classifier   │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Taxonomy    │  │  Resource    │  │   Resource   │     │
│  │   Nodes      │  │  Taxonomy    │  │   (existing) │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 ML Model Storage                             │
│  models/classification/{version}/                            │
│    - pytorch_model.bin                                       │
│    - config.json                                             │
│    - tokenizer files                                         │
│    - label_map.json                                          │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

#### Classification Flow
```
Resource Ingestion → Content Extraction → Embedding Generation
                                                ↓
                                         ML Classification
                                                ↓
                                    Store with Confidence Scores
                                                ↓
                                    Flag Low Confidence for Review
```

#### Active Learning Flow
```
Identify Uncertain → Present to Human → Collect Feedback
                                                ↓
                                         Store Manual Labels
                                                ↓
                                    Accumulate Training Data
                                                ↓
                                         Retrain Model
```


## Components and Interfaces

### 1. Database Models

#### TaxonomyNode Model

Represents a node in the hierarchical taxonomy tree with support for nested categories.

**Fields:**
- `id` (str): UUID primary key
- `name` (str): Human-readable category name
- `slug` (str): URL-friendly identifier (unique)
- `parent_id` (str, nullable): Foreign key to parent TaxonomyNode
- `level` (int): Tree depth (0 for root nodes)
- `path` (str): Materialized path for efficient queries (e.g., "/computer-science/machine-learning")
- `description` (str, nullable): Category description
- `keywords` (str, nullable): JSON array of related keywords
- `resource_count` (int): Direct resource count (cached)
- `descendant_resource_count` (int): Total including subcategories (cached)
- `is_leaf` (bool): Whether node has children
- `allow_resources` (bool): Whether resources can be directly assigned
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last modification timestamp

**Relationships:**
- `parent`: Self-referential relationship to parent node
- `children`: Self-referential relationship to child nodes

**Indexes:**
- `idx_taxonomy_parent_id`: ON (parent_id) - for parent-child queries
- `idx_taxonomy_path`: ON (path) - for hierarchical queries
- `idx_taxonomy_slug`: UNIQUE ON (slug) - for slug lookups

**Constraints:**
- `level >= 0`
- `slug` must be unique

#### ResourceTaxonomy Model

Association table for many-to-many Resource-Taxonomy relationship with classification metadata.

**Fields:**
- `id` (str): UUID primary key
- `resource_id` (str): Foreign key to Resource
- `taxonomy_node_id` (str): Foreign key to TaxonomyNode
- `confidence` (float): Model confidence score (0.0-1.0)
- `is_predicted` (bool): True if ML-classified, False if manual
- `predicted_by` (str, nullable): Model version or "manual"
- `needs_review` (bool): Flagged for human review
- `review_priority` (float, nullable): Active learning priority score
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last modification timestamp

**Relationships:**
- `resource`: Many-to-one to Resource
- `taxonomy_node`: Many-to-one to TaxonomyNode

**Indexes:**
- `idx_resource_taxonomy_resource`: ON (resource_id)
- `idx_resource_taxonomy_taxonomy`: ON (taxonomy_node_id)
- `idx_resource_taxonomy_needs_review`: ON (needs_review) - for active learning queries

**Constraints:**
- `confidence BETWEEN 0.0 AND 1.0`

### 2. ML Classification Service

#### MLClassificationService Class

Core service for transformer-based classification with semi-supervised and active learning.

**Initialization:**
```python
def __init__(
    self,
    db: Session,
    model_name: str = "distilbert-base-uncased",
    model_version: str = "v1.0"
)
```

**Key Methods:**

##### fine_tune()
Fine-tunes BERT model on labeled data with optional semi-supervised learning.

**Parameters:**
- `labeled_data`: List[(text, [taxonomy_node_ids])]
- `unlabeled_data`: Optional list of unlabeled texts
- `epochs`: Training epochs (default: 3)
- `batch_size`: Batch size (default: 16)
- `learning_rate`: Learning rate (default: 2e-5)

**Algorithm:**
1. Build label mapping from unique taxonomy IDs
2. Convert multi-label to multi-hot encoding
3. Split train/validation (80/20)
4. Tokenize texts (max_length=512)
5. Create PyTorch datasets
6. Configure Hugging Face Trainer
7. Train model with evaluation
8. If unlabeled data provided, perform semi-supervised iteration
9. Save model, tokenizer, and label map

**Returns:** Evaluation metrics (F1, precision, recall)

##### predict()
Predicts taxonomy categories for a single text.

**Parameters:**
- `text`: Input text to classify
- `top_k`: Number of predictions to return (default: 5)

**Algorithm:**
1. Tokenize text
2. Forward pass through model
3. Apply sigmoid activation
4. Get top-K predictions
5. Convert indices to taxonomy node IDs

**Returns:** Dict[taxonomy_node_id → confidence_score]

**Performance:** <100ms per prediction

##### predict_batch()
Batch prediction for efficiency.

**Parameters:**
- `texts`: List of texts to classify
- `top_k`: Number of predictions per text (default: 5)

**Algorithm:**
1. Process in batches (32 for GPU, 8 for CPU)
2. Tokenize batch
3. Forward pass
4. Apply sigmoid
5. Get top-K for each text

**Returns:** List[Dict[taxonomy_node_id → confidence_score]]

##### identify_uncertain_samples()
Identifies resources with uncertain classifications for active learning.

**Parameters:**
- `resource_ids`: Optional filter to specific resources
- `limit`: Number of samples to return (default: 100)

**Algorithm:**
1. Query resources (prioritize predicted classifications)
2. Predict classifications
3. Compute uncertainty metrics:
   - Entropy: -Σ(p * log(p))
   - Margin: difference between top-2 predictions
   - Max confidence: highest probability
4. Combined uncertainty: entropy * (1 - margin) * (1 - max_conf)
5. Sort by uncertainty descending

**Returns:** List[(resource_id, uncertainty_score)]

##### update_from_human_feedback()
Updates classification based on human feedback.

**Parameters:**
- `resource_id`: Resource to update
- `correct_taxonomy_ids`: Correct taxonomy node IDs

**Algorithm:**
1. Remove existing predicted classifications
2. Add human-labeled classifications (confidence=1.0, is_predicted=False)
3. Check if retraining threshold reached (100 new labels)
4. Trigger retraining notification if threshold met

**Side Effects:** Updates database, may trigger background retraining

##### _semi_supervised_iteration()
Performs one iteration of semi-supervised learning using pseudo-labeling.

**Parameters:**
- `labeled_data`: Original labeled examples
- `unlabeled_data`: Unlabeled texts
- `confidence_threshold`: Minimum confidence for pseudo-labels (default: 0.9)

**Algorithm:**
1. Predict labels for unlabeled data
2. Filter predictions with confidence >= threshold
3. Add high-confidence predictions as pseudo-labeled examples
4. Combine with original labeled data
5. Re-train model for 1 epoch

**Rationale:** Leverages large unlabeled corpus to improve model with minimal labeled data


### 3. Taxonomy Service

#### TaxonomyService Class

Manages hierarchical taxonomy tree with CRUD operations and resource classification.

**Initialization:**
```python
def __init__(self, db: Session)
```

**Key Methods:**

##### create_node()
Creates a new taxonomy node.

**Parameters:**
- `name`: Category name
- `parent_id`: Optional parent node ID
- `description`: Optional description
- `keywords`: Optional list of keywords
- `allow_resources`: Whether resources can be assigned (default: True)

**Algorithm:**
1. Validate parent exists (if specified)
2. Compute level = parent.level + 1 (or 0 for root)
3. Compute path = parent.path + "/" + slug
4. Create node with UUID
5. Update parent.is_leaf = False

**Returns:** Created TaxonomyNode

##### update_node()
Updates taxonomy node metadata (name, description, keywords, allow_resources).

**Note:** Cannot change parent - use move_node() for reparenting

##### delete_node()
Deletes taxonomy node with cascade or reparenting option.

**Parameters:**
- `node_id`: Node to delete
- `cascade`: If True, delete descendants; if False, reparent children

**Validation:** Raises error if node has assigned resources

##### move_node()
Moves node to different parent (reparenting).

**Parameters:**
- `node_id`: Node to move
- `new_parent_id`: New parent (None for root)

**Algorithm:**
1. Validate node exists
2. Prevent circular references (check if new_parent is descendant)
3. Update parent_id
4. Recalculate level
5. Recalculate path
6. Update all descendants' levels and paths

**Validation:** Prevents circular references and self-parenting

##### get_tree()
Retrieves taxonomy tree as nested dictionary.

**Parameters:**
- `root_id`: Optional starting node (default: all roots)
- `max_depth`: Optional depth limit

**Algorithm:**
1. Query root nodes
2. Recursively build tree structure
3. Include node metadata and children arrays

**Returns:** Nested dict structure suitable for JSON serialization

##### get_ancestors()
Gets all ancestors of a node (breadcrumb trail).

**Algorithm:**
1. Parse materialized path
2. Query nodes by slug for each path segment
3. Return in hierarchical order

**Performance:** O(depth) using materialized path

##### get_descendants()
Gets all descendants of a node.

**Algorithm:**
1. Query nodes with path LIKE 'node.path/%'
2. Return all matching nodes

**Performance:** O(1) query using path index

##### classify_resource()
Assigns taxonomy classifications to a resource.

**Parameters:**
- `resource_id`: Resource to classify
- `taxonomy_node_ids`: List of taxonomy node IDs
- `confidence_scores`: Dict of node_id → confidence
- `is_predicted`: Whether ML-predicted or manual
- `predicted_by`: Model version or "manual"

**Algorithm:**
1. Remove existing predicted classifications
2. Add new classifications with metadata
3. Flag low confidence (<0.7) for review
4. Compute review priority for flagged items
5. Update resource counts for affected nodes

**Side Effects:** Updates resource_taxonomy and taxonomy_nodes tables

##### _update_resource_counts()
Updates cached resource counts for taxonomy nodes.

**Algorithm:**
1. For each affected node:
   - Count direct resources
   - Get all descendants
   - Count resources in node + descendants
2. Update node.resource_count and node.descendant_resource_count

**Performance:** Called after classification changes

### 4. Classification Service (Enhanced)

#### ClassificationService Class

Unified classification service integrating ML and rule-based approaches.

**Initialization:**
```python
def __init__(self, db: Session, use_ml: bool = True)
```

**Key Methods:**

##### classify_resource()
Classifies a resource using ML or rule-based approach.

**Algorithm:**
1. Get resource content
2. If use_ml:
   - Use ML classifier
   - Filter predictions (confidence >= 0.3)
   - Store with confidence scores
3. Else:
   - Use legacy rule-based classifier
4. Flag low-confidence for review

**Integration Point:** Called from resource ingestion pipeline


### 5. API Endpoints

#### Taxonomy Management Endpoints

##### POST /taxonomy/nodes
Creates a new taxonomy node.

**Request Body:**
```json
{
  "name": "Machine Learning",
  "parent_id": "parent-uuid",
  "description": "ML and deep learning topics",
  "keywords": ["neural networks", "deep learning"],
  "allow_resources": true
}
```

**Response:** Created TaxonomyNode object

##### PUT /taxonomy/nodes/{node_id}
Updates taxonomy node metadata.

**Request Body:** Partial TaxonomyNodeUpdate

**Response:** Updated TaxonomyNode object

##### DELETE /taxonomy/nodes/{node_id}
Deletes taxonomy node.

**Query Parameters:**
- `cascade` (bool): Delete descendants vs reparent

**Response:** {"deleted": true/false}

**Error:** 400 if node has resources

##### POST /taxonomy/nodes/{node_id}/move
Moves node to different parent.

**Request Body:**
```json
{
  "new_parent_id": "uuid-or-null"
}
```

**Response:** {"moved": true}

##### GET /taxonomy/tree
Retrieves taxonomy tree structure.

**Query Parameters:**
- `root_id` (str, optional): Starting node
- `max_depth` (int, optional): Depth limit

**Response:** Nested tree structure

##### GET /taxonomy/nodes/{node_id}/ancestors
Gets ancestor nodes (breadcrumb trail).

**Response:** List of TaxonomyNode objects

##### GET /taxonomy/nodes/{node_id}/descendants
Gets descendant nodes.

**Response:** List of TaxonomyNode objects

#### Classification Endpoints

##### POST /taxonomy/classify/{resource_id}
Classifies a resource using ML classifier.

**Response:** 202 Accepted (background task)

**Background Task:** Runs ML classification and stores results

##### GET /taxonomy/active-learning/uncertain
Gets resources with uncertain classifications for review.

**Query Parameters:**
- `limit` (int): Number of samples (default: 100)

**Response:**
```json
[
  {"resource_id": "uuid", "uncertainty_score": 0.85},
  ...
]
```

##### POST /taxonomy/active-learning/feedback
Submits human classification feedback.

**Request Body:**
```json
{
  "resource_id": "uuid",
  "correct_taxonomy_ids": ["node-id-1", "node-id-2"]
}
```

**Response:** {"updated": true}

**Side Effects:** Removes predicted classifications, adds manual labels, may trigger retraining

##### POST /taxonomy/train
Initiates model fine-tuning.

**Request Body:**
```json
{
  "labeled_data": [
    {"text": "...", "taxonomy_ids": ["id1", "id2"]},
    ...
  ],
  "unlabeled_texts": ["...", "..."],
  "epochs": 3,
  "batch_size": 16
}
```

**Response:** 202 Accepted (background task)

**Background Task:** Runs fine-tuning and saves model

### 6. Pydantic Schemas

#### TaxonomyNodeCreate
```python
class TaxonomyNodeCreate(BaseModel):
    name: str
    parent_id: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    allow_resources: bool = True
```

#### TaxonomyNodeUpdate
```python
class TaxonomyNodeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    allow_resources: Optional[bool] = None
```

#### ClassificationFeedback
```python
class ClassificationFeedback(BaseModel):
    resource_id: str
    correct_taxonomy_ids: List[str]
```

#### ClassifierTrainingRequest
```python
class ClassifierTrainingRequest(BaseModel):
    labeled_data: List[Dict]  # [{"text": "...", "taxonomy_ids": [...]}]
    unlabeled_texts: Optional[List[str]] = None
    epochs: int = 3
    batch_size: int = 16
```


## Data Models

### Taxonomy Tree Structure

The taxonomy uses a **materialized path** pattern for efficient hierarchical queries:

```
Root Nodes (level=0, parent_id=NULL)
├── Computer Science (path="/computer-science")
│   ├── Machine Learning (path="/computer-science/machine-learning")
│   │   ├── Deep Learning (path="/computer-science/machine-learning/deep-learning")
│   │   └── NLP (path="/computer-science/machine-learning/nlp")
│   └── Databases (path="/computer-science/databases")
└── Medicine (path="/medicine")
    └── Cardiology (path="/medicine/cardiology")
```

**Advantages of Materialized Path:**
- O(1) ancestor queries (parse path string)
- O(1) descendant queries (path LIKE 'parent/%')
- No recursive CTEs needed
- Efficient with proper indexing

**Trade-offs:**
- Path updates on reparenting (acceptable for infrequent operations)
- Path length limits (mitigated by slug length limits)

### Multi-Label Classification

Resources can belong to multiple taxonomy categories:

```
Resource: "Introduction to Neural Networks"
Classifications:
  - Computer Science/Machine Learning (confidence: 0.95)
  - Computer Science/Machine Learning/Deep Learning (confidence: 0.88)
  - Computer Science/Machine Learning/NLP (confidence: 0.42)
```

**Model Output:** Multi-hot encoding with sigmoid activation
- Each taxonomy node is an independent binary classification
- Allows multiple categories per resource
- Confidence scores are independent probabilities

### Classification Metadata

Each resource-taxonomy association includes:
- **confidence**: Model certainty (0.0-1.0)
- **is_predicted**: ML vs manual classification
- **predicted_by**: Model version tracking
- **needs_review**: Active learning flag
- **review_priority**: Uncertainty score for prioritization

## Error Handling

### Validation Errors

**Circular Reference Prevention:**
```python
if self._is_descendant(new_parent_id, node_id):
    raise ValueError("Cannot move node to its own descendant")
```

**Resource Assignment Validation:**
```python
if resource_count > 0:
    raise ValueError(f"Cannot delete taxonomy node with {resource_count} resources")
```

**Parent Existence Validation:**
```python
if parent_id and not parent_exists:
    raise ValueError(f"Parent taxonomy node {parent_id} not found")
```

### Model Loading Errors

**Checkpoint Not Found:**
```python
try:
    model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path)
except:
    print("Warning: No fine-tuned model found, using base model")
    model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
```

**GPU Availability:**
```python
if torch.cuda.is_available():
    model = model.cuda()
else:
    print("Warning: CUDA not available, using CPU")
```

### Classification Errors

**Empty Predictions:**
```python
if not predictions:
    # Log warning and skip classification
    logger.warning(f"No predictions for resource {resource_id}")
    return
```

**Low Confidence Handling:**
```python
# Filter predictions below threshold
filtered_predictions = {
    node_id: conf for node_id, conf in predictions.items()
    if conf >= 0.3
}
```

## Testing Strategy

### Unit Tests

**Taxonomy Service Tests:**
- `test_create_node()`: Node creation with parent
- `test_create_root_node()`: Root node creation
- `test_update_node()`: Metadata updates
- `test_delete_node_cascade()`: Cascade deletion
- `test_delete_node_reparent()`: Reparenting on delete
- `test_move_node()`: Reparenting validation
- `test_prevent_circular_reference()`: Circular reference prevention
- `test_get_tree()`: Tree structure retrieval
- `test_get_ancestors()`: Ancestor queries
- `test_get_descendants()`: Descendant queries
- `test_classify_resource()`: Resource classification
- `test_update_resource_counts()`: Count caching

**ML Classification Service Tests:**
- `test_fine_tune()`: Model training
- `test_predict()`: Single prediction
- `test_predict_batch()`: Batch prediction
- `test_semi_supervised_learning()`: Pseudo-labeling
- `test_identify_uncertain_samples()`: Active learning
- `test_update_from_human_feedback()`: Feedback integration
- `test_model_loading()`: Lazy loading
- `test_label_mapping()`: Label conversion

**Classification Service Tests:**
- `test_classify_with_ml()`: ML classification integration
- `test_classify_with_rules()`: Rule-based fallback
- `test_confidence_filtering()`: Threshold application

### Integration Tests

**End-to-End Classification:**
1. Create taxonomy tree
2. Ingest resource
3. Verify classification triggered
4. Check confidence scores stored
5. Verify low-confidence flagged for review

**Active Learning Workflow:**
1. Classify resources with ML
2. Identify uncertain samples
3. Submit human feedback
4. Verify manual labels stored
5. Check retraining trigger

**Semi-Supervised Learning:**
1. Prepare small labeled dataset
2. Prepare large unlabeled dataset
3. Fine-tune with semi-supervised
4. Verify pseudo-labels generated
5. Check model improvement

### Performance Tests

**Inference Speed:**
- Single prediction: <100ms
- Batch prediction (32): <500ms
- GPU vs CPU comparison

**Query Performance:**
- Ancestor query: <10ms
- Descendant query: <10ms
- Tree retrieval (depth 5): <50ms

**Training Performance:**
- Fine-tuning (500 examples, 3 epochs): <10 minutes on GPU
- Semi-supervised iteration: <15 minutes


## Implementation Considerations

### Model Selection: DistilBERT vs BERT

**DistilBERT (Recommended):**
- 60% smaller than BERT
- 60% faster inference
- 97% of BERT's performance
- Better for production deployment
- Lower memory requirements

**BERT-base:**
- Higher accuracy potential
- Slower inference
- Larger model size
- Use if accuracy is critical and resources available

**Decision:** Start with DistilBERT, upgrade to BERT if accuracy requirements not met

### Semi-Supervised Learning Strategy

**Pseudo-Labeling Algorithm:**
1. Train initial model on small labeled set (100-500 examples)
2. Predict on large unlabeled corpus (10,000+ documents)
3. Select high-confidence predictions (>0.9)
4. Add pseudo-labeled examples to training set
5. Re-train model
6. Repeat if needed

**Benefits:**
- Leverages existing unlabeled content
- Reduces manual labeling effort
- Improves model generalization

**Risks:**
- Confirmation bias (model reinforces own mistakes)
- Mitigation: High confidence threshold (0.9)
- Mitigation: Active learning to correct errors

### Active Learning Strategy

**Uncertainty Sampling:**
- **Entropy**: Measures prediction uncertainty across all classes
- **Margin**: Difference between top-2 predictions (small = uncertain)
- **Confidence**: Maximum probability (low = uncertain)

**Combined Score:**
```python
uncertainty = entropy * (1 - margin) * (1 - max_confidence)
```

**Workflow:**
1. Identify top-N most uncertain predictions
2. Present to human reviewers
3. Collect correct labels
4. Store as training data
5. Retrain when threshold reached (100 new labels)

**Expected Impact:**
- 60%+ reduction in labeling effort
- Continuous model improvement
- Focus human effort on difficult cases

### Hierarchical Classification Considerations

**Parent-Child Relationships:**
- Child categories imply parent categories
- Example: "Deep Learning" → implies "Machine Learning" → implies "Computer Science"

**Implementation Options:**

**Option 1: Independent Classification (Chosen)**
- Treat each node as independent binary classification
- Model learns hierarchical patterns from training data
- Simpler implementation
- More flexible

**Option 2: Hierarchical Constraints**
- Enforce parent prediction when child predicted
- Requires custom loss function
- More complex implementation
- Guarantees consistency

**Decision:** Use Option 1 for simplicity, rely on training data to learn hierarchy

### Resource Count Caching

**Problem:** Counting resources for each node on every request is expensive

**Solution:** Cache counts in taxonomy_nodes table
- `resource_count`: Direct resources in this node
- `descendant_resource_count`: Resources in node + all descendants

**Update Strategy:**
- Update counts when classifications change
- Batch updates for efficiency
- Acceptable eventual consistency (counts updated within seconds)

**Query Pattern:**
```sql
-- Direct count
SELECT COUNT(*) FROM resource_taxonomy WHERE taxonomy_node_id = ?

-- Descendant count
SELECT COUNT(*) FROM resource_taxonomy 
WHERE taxonomy_node_id IN (
  SELECT id FROM taxonomy_nodes WHERE path LIKE '/parent/path/%'
)
```

### Model Versioning

**Version Format:** `v{major}.{minor}`
- Major: Breaking changes (label mapping changes)
- Minor: Improvements (retraining on same labels)

**Storage Structure:**
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

**Tracking:**
- Store version in `predicted_by` field
- Enables A/B testing
- Supports rollback
- Facilitates model comparison

### GPU Acceleration

**CUDA Detection:**
```python
if torch.cuda.is_available():
    model = model.cuda()
    batch_size = 32
else:
    batch_size = 8
```

**Memory Management:**
- Use gradient checkpointing for large models
- Clear cache between batches
- Monitor GPU memory usage

**Fallback:**
- Gracefully degrade to CPU if GPU unavailable
- Adjust batch size for CPU performance

### Integration with Existing Pipeline

**Resource Ingestion Flow:**
```
1. Content Extraction
2. Embedding Generation (existing)
3. → ML Classification (new)
4. Quality Scoring (existing)
5. Storage
```

**Trigger Point:**
- After content extraction completes
- Before quality scoring (classification may inform quality)
- Background task (non-blocking)

**Error Handling:**
- Classification failures don't block ingestion
- Log errors for monitoring
- Retry mechanism for transient failures

### Migration Strategy

**Phase 1: Schema Migration**
- Create taxonomy_nodes table
- Create resource_taxonomy table
- Add indexes
- Seed default taxonomy (optional)

**Phase 2: Service Implementation**
- Implement TaxonomyService
- Implement MLClassificationService
- Implement API endpoints

**Phase 3: Model Training**
- Collect initial labeled dataset
- Fine-tune first model version
- Validate performance

**Phase 4: Integration**
- Add classification to ingestion pipeline
- Enable ML classification flag
- Monitor performance

**Phase 5: Active Learning**
- Identify uncertain samples
- Collect human feedback
- Retrain model

**Rollback Plan:**
- Keep rule-based classification as fallback
- `use_ml` flag for easy toggle
- No breaking changes to existing APIs

