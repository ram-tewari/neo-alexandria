# Design Document

## Overview

This design document outlines the implementation of the Neural Collaborative Filtering (NCF) service and training infrastructure for Neo Alexandria's ML models. The system will enable personalized recommendations through deep learning-based collaborative filtering and provide training scripts to prepare models for benchmark testing.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Training Infrastructure                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  Classification  │         │   NCF Training   │          │
│  │ Training Script  │         │      Script      │          │
│  └────────┬─────────┘         └────────┬─────────┘          │
│           │                            │                     │
│           ▼                            ▼                     │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │ Classification   │         │   NCF Model      │          │
│  │    Dataset       │         │    Dataset       │          │
│  └────────┬─────────┘         └────────┬─────────┘          │
│           │                            │                     │
│           ▼                            ▼                     │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │ MLClassification │         │   NCF Service    │          │
│  │     Service      │         │                  │          │
│  └────────┬─────────┘         └────────┬─────────┘          │
│           │                            │                     │
└───────────┼────────────────────────────┼─────────────────────┘
            │                            │
            ▼                            ▼
   ┌────────────────┐          ┌────────────────┐
   │ Classification │          │   NCF Model    │
   │    Checkpoint  │          │   Checkpoint   │
   └────────────────┘          └────────────────┘
            │                            │
            ▼                            ▼
   ┌────────────────────────────────────────────┐
   │         Benchmark Test Suite               │
   └────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **Training Phase:**
   - Training scripts load datasets
   - Models are trained using PyTorch
   - Checkpoints are saved to disk
   - Metrics are logged

2. **Inference Phase:**
   - Services load checkpoints lazily
   - Predictions are made on-demand
   - Results are cached when appropriate

3. **Testing Phase:**
   - Fixtures load trained models
   - Benchmarks evaluate performance
   - Reports are generated

## Components and Interfaces

### 1. NCF Service (`backend/app/services/ncf_service.py`)

**Purpose:** Provides collaborative filtering recommendations using neural networks.

**Class Structure:**

```python
class NCFService:
    """Neural Collaborative Filtering service for recommendations."""
    
    def __init__(self, db: Session, model_path: Optional[str] = None):
        """Initialize NCF service with database and optional model path."""
        
    def _load_model(self) -> None:
        """Lazy load the NCF model from checkpoint."""
        
    def predict(self, user_id: str, item_ids: List[str]) -> Dict[str, float]:
        """Predict scores for user-item pairs."""
        
    def predict_batch(self, user_id: str, item_ids: List[str]) -> Dict[str, float]:
        """Batch prediction for efficiency."""
        
    def recommend(self, user_id: str, top_k: int = 10, 
                  exclude_seen: bool = True) -> List[Tuple[str, float]]:
        """Get top-K recommendations for a user."""
        
    def _handle_cold_start(self, user_id: str, top_k: int) -> List[Tuple[str, float]]:
        """Handle cold start by returning popular items."""
```

**Key Methods:**

- `predict()`: Single user-item prediction
- `predict_batch()`: Efficient batch prediction
- `recommend()`: Top-K recommendation generation
- `_handle_cold_start()`: Fallback for new users

**Dependencies:**
- PyTorch for model inference
- SQLAlchemy for database access
- NumPy for numerical operations

### 2. NCF Model (`backend/app/models/ncf_model.py`)

**Purpose:** Implements the neural network architecture for collaborative filtering.

**Architecture:**

```python
class NCFModel(nn.Module):
    """Neural Collaborative Filtering model."""
    
    def __init__(self, num_users: int, num_items: int, 
                 embedding_dim: int = 64, 
                 hidden_layers: List[int] = [128, 64, 32]):
        """
        Initialize NCF model.
        
        Architecture:
        - User embedding layer (num_users x embedding_dim)
        - Item embedding layer (num_items x embedding_dim)
        - MLP layers with ReLU activation
        - Output layer with sigmoid activation
        """
        
    def forward(self, user_ids: torch.Tensor, item_ids: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network."""
```

**Architecture Details:**

```
Input: (user_id, item_id)
    ↓
┌─────────────────┐     ┌─────────────────┐
│ User Embedding  │     │ Item Embedding  │
│   (64 dims)     │     │   (64 dims)     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ↓
              ┌─────────────┐
              │ Concatenate │
              │  (128 dims) │
              └──────┬──────┘
                     ↓
              ┌─────────────┐
              │   MLP 128   │
              │    ReLU     │
              └──────┬──────┘
                     ↓
              ┌─────────────┐
              │   MLP 64    │
              │    ReLU     │
              └──────┬──────┘
                     ↓
              ┌─────────────┐
              │   MLP 32    │
              │    ReLU     │
              └──────┬──────┘
                     ↓
              ┌─────────────┐
              │  Output 1   │
              │   Sigmoid   │
              └──────┬──────┘
                     ↓
            Prediction Score (0-1)
```

### 3. NCF Training Script (`backend/scripts/train_ncf.py`)

**Purpose:** Train the NCF model on user-item interaction data.

**Structure:**

```python
def load_interaction_data(data_path: str) -> Tuple[List, List, Dict, Dict]:
    """Load and prepare interaction data."""
    
def create_negative_samples(interactions: List, num_items: int, 
                           ratio: int = 4) -> List:
    """Generate negative samples for implicit feedback."""
    
def train_ncf_model(train_data: Dataset, val_data: Dataset,
                   num_users: int, num_items: int,
                   epochs: int = 10, batch_size: int = 256,
                   learning_rate: float = 0.001) -> NCFModel:
    """Train NCF model with given data."""
    
def evaluate_model(model: NCFModel, test_data: Dataset) -> Dict[str, float]:
    """Evaluate model using NDCG@10 and Hit Rate@10."""
    
def main():
    """Main training pipeline."""
```

**Training Pipeline:**

1. Load interaction data from JSON or database
2. Create user/item ID mappings
3. Generate negative samples (4:1 ratio)
4. Split into train/validation (80/20)
5. Initialize NCF model
6. Train with Adam optimizer
7. Evaluate on validation set
8. Save checkpoint with mappings

### 4. Classification Training Script (`backend/scripts/train_classification.py`)

**Purpose:** Train the classification model using existing MLClassificationService.

**Structure:**

```python
def load_classification_data(data_path: str) -> List[Tuple[str, List[str]]]:
    """Load classification dataset from JSON."""
    
def augment_dataset(data: List, target_size: int = 500) -> List:
    """Augment small datasets with variations."""
    
def train_classification_model(labeled_data: List,
                               epochs: int = 3,
                               batch_size: int = 16) -> Dict[str, float]:
    """Train classification model using MLClassificationService."""
    
def main():
    """Main training pipeline."""
```

**Training Pipeline:**

1. Load classification test dataset
2. Augment if dataset is too small
3. Initialize MLClassificationService
4. Call fine_tune() method
5. Evaluate on validation set
6. Save checkpoint as "benchmark_v1"

### 5. Data Preparation Utilities (`backend/scripts/prepare_training_data.py`)

**Purpose:** Convert test datasets into training-ready formats.

**Functions:**

```python
def load_classification_test_data() -> List[Tuple[str, List[str]]]:
    """Load classification test data from JSON."""
    
def load_recommendation_test_data() -> Tuple[List, Dict, Dict]:
    """Load recommendation test data from JSON."""
    
def augment_classification_data(data: List, multiplier: int = 3) -> List:
    """Create variations of classification examples."""
    
def create_synthetic_interactions(num_users: int, num_items: int,
                                 num_interactions: int) -> List:
    """Generate synthetic user-item interactions."""
    
def validate_data_format(data: Any, data_type: str) -> bool:
    """Validate data format and completeness."""
```

## Data Models

### NCF Training Data Format

```python
{
    "metadata": {
        "num_users": 50,
        "num_items": 200,
        "num_interactions": 1000,
        "density": 0.1
    },
    "interactions": [
        {
            "user_id": "user_1",
            "item_id": "item_42",
            "timestamp": "2024-01-15T10:30:00",
            "interaction_type": "view",
            "implicit_rating": 1.0
        },
        // ... more interactions
    ],
    "held_out_test": [
        {
            "user_id": "user_1",
            "relevant_items": ["item_89", "item_123"],
            "candidate_items": ["item_89", "item_123", "item_45", ...]
        },
        // ... more test cases
    ]
}
```

### Classification Training Data Format

```python
{
    "metadata": {
        "num_samples": 200,
        "num_classes": 10,
        "class_distribution": {
            "000": 20,
            "100": 20,
            // ... more classes
        }
    },
    "samples": [
        {
            "text": "Machine learning is a subset of AI...",
            "taxonomy_codes": ["000", "004"],
            "confidence": 1.0
        },
        // ... more samples
    ]
}
```

### Model Checkpoint Format

**Classification Checkpoint:**
```
backend/models/classification/benchmark_v1/
├── pytorch_model.bin          # Model weights
├── config.json                # Model configuration
├── tokenizer_config.json      # Tokenizer configuration
├── vocab.txt                  # Vocabulary
└── label_map.json            # Label mappings
```

**NCF Checkpoint:**
```
backend/models/ncf_benchmark_v1.pt
{
    "model_state_dict": {...},
    "user_id_map": {"user_1": 0, "user_2": 1, ...},
    "item_id_map": {"item_1": 0, "item_2": 1, ...},
    "num_users": 50,
    "num_items": 200,
    "embedding_dim": 64,
    "hidden_layers": [128, 64, 32],
    "training_metrics": {
        "ndcg@10": 0.55,
        "hit_rate@10": 0.65
    }
}
```

## Error Handling

### NCF Service Error Handling

```python
class NCFModelNotFoundError(Exception):
    """Raised when NCF model checkpoint is not found."""
    pass

class ColdStartError(Exception):
    """Raised when user/item is not in training data."""
    pass

# Error handling in service
try:
    model = load_checkpoint(model_path)
except FileNotFoundError:
    raise NCFModelNotFoundError(
        f"NCF model not found at {model_path}. "
        "Please train the model first using: "
        "python backend/scripts/train_ncf.py"
    )
```

### Training Script Error Handling

```python
# Data validation
if not validate_data_format(data, "classification"):
    logger.error("Invalid data format")
    sys.exit(1)

# Training errors
try:
    metrics = train_model(data)
except RuntimeError as e:
    logger.error(f"Training failed: {e}")
    logger.info("Try reducing batch size or learning rate")
    sys.exit(1)
```

## Testing Strategy

### Unit Tests

1. **NCF Model Tests:**
   - Test forward pass with sample data
   - Test embedding dimensions
   - Test output range (0-1)

2. **NCF Service Tests:**
   - Test prediction with mock model
   - Test batch prediction
   - Test cold start handling

3. **Data Preparation Tests:**
   - Test data loading
   - Test data augmentation
   - Test format validation

### Integration Tests

1. **End-to-End Training:**
   - Train classification model on test data
   - Train NCF model on test data
   - Verify checkpoints are created
   - Verify models can be loaded

2. **Benchmark Integration:**
   - Run all benchmark tests with trained models
   - Verify all tests pass
   - Verify performance meets thresholds

### Performance Tests

1. **Inference Latency:**
   - Classification: <100ms p95
   - NCF prediction: <50ms p95
   - Batch prediction efficiency

2. **Training Time:**
   - Classification: <30 minutes on CPU
   - NCF: <20 minutes on CPU

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading:**
   - Load models only when needed
   - Cache loaded models in memory

2. **Batch Processing:**
   - Process multiple predictions together
   - Use GPU when available

3. **Negative Sampling:**
   - Use efficient sampling for training
   - Cache negative samples

4. **Model Size:**
   - Use DistilBERT for classification (smaller)
   - Use moderate embedding dimensions (64)

### Resource Requirements

**Training:**
- RAM: 8GB minimum, 16GB recommended
- GPU: Optional but recommended (10x speedup)
- Disk: 2GB for models and data

**Inference:**
- RAM: 4GB minimum
- GPU: Optional
- Disk: 1GB for model checkpoints

## Security Considerations

1. **Model Checkpoints:**
   - Store in version-controlled directory
   - Validate checksums before loading
   - Use read-only permissions in production

2. **Training Data:**
   - Sanitize user-generated content
   - Remove PII from training data
   - Validate data sources

3. **API Security:**
   - Rate limit prediction endpoints
   - Validate input parameters
   - Log prediction requests

## Deployment Strategy

### Development Environment

1. Train models locally using scripts
2. Save checkpoints to `backend/models/`
3. Run benchmark tests to verify
4. Commit checkpoints to git (if <100MB)

### Production Environment

1. Train models on dedicated training server
2. Upload checkpoints to cloud storage
3. Download checkpoints during deployment
4. Load models lazily on first request

### Model Versioning

```
backend/models/
├── classification/
│   ├── benchmark_v1/      # For testing
│   ├── production_v1/     # For production
│   └── production_v2/     # New version
└── ncf_benchmark_v1.pt
└── ncf_production_v1.pt
```

## Monitoring and Logging

### Training Metrics

```python
logger.info(f"Epoch {epoch}/{epochs}")
logger.info(f"Train Loss: {train_loss:.4f}")
logger.info(f"Val Loss: {val_loss:.4f}")
logger.info(f"NDCG@10: {ndcg:.4f}")
logger.info(f"Hit Rate@10: {hit_rate:.4f}")
```

### Inference Metrics

```python
logger.info(f"Prediction latency: {latency_ms:.2f}ms")
logger.info(f"Cold start: {is_cold_start}")
logger.info(f"Batch size: {batch_size}")
```

### Error Logging

```python
logger.error(f"Model loading failed: {error}")
logger.warning(f"Cold start for user: {user_id}")
logger.debug(f"Prediction scores: {scores}")
```

## Future Enhancements

1. **Advanced NCF Architectures:**
   - Neural Matrix Factorization (NMF)
   - Generalized Matrix Factorization (GMF)
   - Attention mechanisms

2. **Hyperparameter Tuning:**
   - Automated hyperparameter search
   - Cross-validation
   - Early stopping

3. **Online Learning:**
   - Incremental model updates
   - A/B testing framework
   - Real-time feedback incorporation

4. **Model Compression:**
   - Quantization for faster inference
   - Knowledge distillation
   - Pruning for smaller models

5. **Multi-Modal Recommendations:**
   - Combine collaborative and content-based
   - Use resource metadata
   - Incorporate user profiles
