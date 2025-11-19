# ML Model Training Scripts

This directory contains scripts for training machine learning models used in Neo Alexandria.

## Available Scripts

### 1. train_classification.py

Trains the multi-label text classification model for taxonomy assignment.

**Usage:**
```bash
python scripts/train_classification.py [OPTIONS]
```

**Options:**
- `--data-path PATH` - Path to training data JSON file (default: `tests/ml_benchmarks/datasets/classification_test.json`)
- `--epochs INT` - Number of training epochs (default: 3)
- `--batch-size INT` - Training batch size (default: 16)
- `--learning-rate FLOAT` - Learning rate for optimizer (default: 2e-5)
- `--output-dir PATH` - Directory to save model checkpoint (default: `models/classification/benchmark_v1`)

**Example:**
```bash
# Train with default settings
python scripts/train_classification.py

# Train with custom hyperparameters
python scripts/train_classification.py \
  --epochs 5 \
  --batch-size 32 \
  --learning-rate 1e-5

# Train with custom dataset
python scripts/train_classification.py \
  --data-path data/my_classification_data.json \
  --output-dir models/classification/production_v1
```

**Expected Output:**
```
Loading classification data from tests/ml_benchmarks/datasets/classification_test.json
Loaded 200 samples with 10 unique taxonomy codes
Training classification model...
Epoch 1/3: 100%|████████| 10/10 [02:15<00:00, 13.5s/it]
Validation F1: 0.85
...
Training complete!
Model saved to: models/classification/benchmark_v1
```

**Training Time:**
- CPU: 15-30 minutes for 200 samples
- GPU: 5-10 minutes for 200 samples

**Memory Requirements:**
- 4-8GB RAM

### 2. train_ncf.py

Trains the Neural Collaborative Filtering (NCF) model for personalized recommendations.

**Usage:**
```bash
python scripts/train_ncf.py [OPTIONS]
```

**Options:**
- `--data-path PATH` - Path to interaction data JSON file (default: `tests/ml_benchmarks/datasets/recommendation_test.json`)
- `--epochs INT` - Number of training epochs (default: 10)
- `--batch-size INT` - Training batch size (default: 256)
- `--learning-rate FLOAT` - Learning rate for Adam optimizer (default: 0.001)
- `--embedding-dim INT` - Embedding dimension for users/items (default: 64)
- `--hidden-layers LIST` - MLP hidden layer sizes (default: [128, 64, 32])
- `--output-path PATH` - Path to save model checkpoint (default: `models/ncf_benchmark_v1.pt`)

**Example:**
```bash
# Train with default settings
python scripts/train_ncf.py

# Train with custom hyperparameters
python scripts/train_ncf.py \
  --epochs 20 \
  --batch-size 512 \
  --embedding-dim 128 \
  --learning-rate 0.0001

# Train with custom dataset
python scripts/train_ncf.py \
  --data-path data/my_interactions.json \
  --output-path models/ncf_production_v1.pt
```

**Expected Output:**
```
Loading interaction data from tests/ml_benchmarks/datasets/recommendation_test.json
Loaded 1000 interactions for 50 users and 200 items
Dataset density: 10.0%
Creating negative samples (ratio 4:1)...
Generated 4000 negative samples
Training NCF model...
Epoch 1/10: Loss=0.6234, Val NDCG@10=0.42, Hit Rate@10=0.58
...
Training complete!
Model saved to: models/ncf_benchmark_v1.pt
```

**Training Time:**
- CPU: 10-20 minutes for 1000 interactions
- GPU: 2-5 minutes for 1000 interactions

**Memory Requirements:**
- 2-4GB RAM

### 3. prepare_training_data.py

Utility functions for loading and preparing training data.

**Functions:**
- `load_classification_test_data()` - Load classification test dataset
- `load_recommendation_test_data()` - Load recommendation test dataset
- `augment_classification_data()` - Create text variations for small datasets
- `create_synthetic_interactions()` - Generate synthetic user-item interactions
- `validate_data_format()` - Validate data format and completeness

**Usage:**
```python
from scripts.prepare_training_data import load_classification_test_data

# Load test data
data = load_classification_test_data()
print(f"Loaded {len(data)} samples")
```

## Data Formats

### Classification Training Data

```json
{
  "metadata": {
    "num_samples": 200,
    "num_classes": 10,
    "class_distribution": {
      "000": 20,
      "100": 20
    }
  },
  "samples": [
    {
      "text": "Machine learning is a subset of artificial intelligence...",
      "taxonomy_codes": ["000", "004"],
      "confidence": 1.0
    }
  ]
}
```

**Fields:**
- `text` (string, required) - Text content to classify
- `taxonomy_codes` (array, required) - List of taxonomy IDs
- `confidence` (float, optional) - Label confidence (0.0-1.0)

### NCF Training Data

```json
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
    }
  ]
}
```

**Fields:**
- `user_id` (string, required) - Unique user identifier
- `item_id` (string, required) - Unique item identifier
- `timestamp` (string, optional) - ISO 8601 timestamp
- `interaction_type` (string, optional) - Type of interaction (view, bookmark, etc.)
- `implicit_rating` (float, required) - Implicit feedback signal (typically 1.0)

## Model Checkpoints

Trained models are saved to:

```
backend/models/
├── classification/
│   └── benchmark_v1/           # Classification model
│       ├── pytorch_model.bin
│       ├── config.json
│       ├── tokenizer_config.json
│       ├── vocab.txt
│       └── label_map.json
└── ncf_benchmark_v1.pt         # NCF model
```

## Hyperparameter Tuning

### Classification Model

**Learning Rate:**
- Default: 2e-5
- Range: [1e-5, 5e-5]
- Higher values train faster but may be unstable

**Epochs:**
- Default: 3
- Range: [3, 10]
- More epochs improve accuracy but risk overfitting

**Batch Size:**
- Default: 16
- Range: [8, 32]
- Larger batches are faster but require more memory

### NCF Model

**Embedding Dimension:**
- Default: 64
- Range: [32, 128]
- Larger embeddings capture more patterns but train slower

**Hidden Layers:**
- Default: [128, 64, 32]
- Options: [[64, 32], [256, 128, 64]]
- Deeper networks learn complex patterns but may overfit

**Learning Rate:**
- Default: 0.001
- Range: [0.0001, 0.01]
- Lower values are more stable but train slower

**Negative Sampling Ratio:**
- Default: 4 (4 negative samples per positive)
- Range: [2, 8]
- Higher ratios improve discrimination but increase training time

## Troubleshooting

### Out of Memory Errors

**Symptoms:**
```
RuntimeError: CUDA out of memory
```

**Solutions:**
1. Reduce batch size:
   ```bash
   python scripts/train_classification.py --batch-size 8
   python scripts/train_ncf.py --batch-size 128
   ```

2. Use CPU instead of GPU:
   ```bash
   export CUDA_VISIBLE_DEVICES=""
   python scripts/train_classification.py
   ```

3. Reduce model size (NCF):
   ```bash
   python scripts/train_ncf.py --embedding-dim 32 --hidden-layers 64 32
   ```

### Poor Model Performance

**Classification F1 < 0.70:**
- Increase training data (aim for 500+ samples)
- Balance class distribution
- Increase epochs or lower learning rate
- Check for label noise

**NCF NDCG@10 < 0.40:**
- Increase interaction data (aim for 2000+ interactions)
- Ensure sufficient user/item coverage
- Increase embedding dimension
- Increase negative sampling ratio

### Slow Training

**Solutions:**
1. Use GPU acceleration (10x speedup)
2. Increase batch size (if memory allows)
3. Reduce dataset size for testing
4. Use fewer epochs for quick validation

### Model Not Found in Tests

**Symptoms:**
```
pytest.skip: Benchmark model not available
```

**Solutions:**
1. Train the required models:
   ```bash
   python scripts/train_classification.py
   python scripts/train_ncf.py
   ```

2. Verify checkpoints exist:
   ```bash
   ls -lh models/classification/benchmark_v1/
   ls -lh models/ncf_benchmark_v1.pt
   ```

## Best Practices

### Before Training

1. **Validate data format:**
   ```python
   from scripts.prepare_training_data import validate_data_format
   is_valid = validate_data_format(data, "classification")
   ```

2. **Check data statistics:**
   - Classification: Balanced class distribution
   - NCF: Sufficient user/item coverage (>10 interactions per user)

3. **Set random seed for reproducibility:**
   ```python
   import random
   import numpy as np
   import torch
   
   random.seed(42)
   np.random.seed(42)
   torch.manual_seed(42)
   ```

### During Training

1. **Monitor metrics:**
   - Classification: F1 score, precision, recall
   - NCF: NDCG@10, Hit Rate@10, training loss

2. **Watch for overfitting:**
   - Validation metrics plateau or decrease
   - Large gap between train and validation loss

3. **Save checkpoints:**
   - Models are automatically saved after training
   - Keep multiple versions for comparison

### After Training

1. **Evaluate on test set:**
   ```bash
   pytest tests/ml_benchmarks/test_classification_metrics.py
   pytest tests/ml_benchmarks/test_collaborative_filtering_metrics.py
   ```

2. **Check inference latency:**
   ```bash
   pytest tests/performance/test_ml_latency.py
   ```

3. **Compare with baseline:**
   - Classification F1 should be >0.85
   - NCF NDCG@10 should be >0.50

## Additional Resources

- **Developer Guide**: `docs/DEVELOPER_GUIDE.md` - Complete ML training documentation
- **Benchmark Report**: `docs/ML_BENCHMARKS.md` - Current model performance
- **Test Datasets**: `tests/ml_benchmarks/datasets/` - Sample training data
- **Model Architecture**: `.kiro/specs/ml-model-training/design.md` - Technical design

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the Developer Guide
3. Check existing GitHub issues
4. Open a new issue with training logs and configuration
