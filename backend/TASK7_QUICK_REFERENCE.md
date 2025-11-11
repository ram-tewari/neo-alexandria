# Task 7 Quick Reference - ML Training Implementation

## What Was Implemented

### 1. fine_tune() Method
**Purpose**: Complete training pipeline for transformer models

**Key Steps**:
1. Build label mapping from taxonomy IDs
2. Convert to multi-hot encoding
3. Split train/validation (80/20)
4. Tokenize texts (max_length=512)
5. Create PyTorch datasets
6. Configure Hugging Face Trainer
7. Train model
8. Evaluate on validation set
9. Optional: Semi-supervised learning
10. Save model, tokenizer, and label map

**Usage Example**:
```python
from app.services.ml_classification_service import MLClassificationService

service = MLClassificationService(db, model_version="v1.0")

# Prepare labeled data
labeled_data = [
    ("Machine learning article about neural networks", ["ml_node_id", "ai_node_id"]),
    ("Database optimization techniques", ["db_node_id"]),
    # ... more examples
]

# Optional: unlabeled data for semi-supervised learning
unlabeled_data = [
    "Article about deep learning",
    "Tutorial on SQL queries",
    # ... more texts
]

# Fine-tune the model
metrics = service.fine_tune(
    labeled_data=labeled_data,
    unlabeled_data=unlabeled_data,  # Optional
    epochs=3,
    batch_size=16,
    learning_rate=2e-5
)

print(f"F1: {metrics['f1']:.4f}")
print(f"Precision: {metrics['precision']:.4f}")
print(f"Recall: {metrics['recall']:.4f}")
```

---

### 2. _compute_metrics() Method
**Purpose**: Evaluation callback for Hugging Face Trainer

**Computes**:
- F1 score (macro average)
- Precision (macro average)
- Recall (macro average)

**Used By**: Hugging Face Trainer during evaluation

---

### 3. _semi_supervised_iteration() Method
**Purpose**: Pseudo-labeling for semi-supervised learning

**Algorithm**:
1. Predict labels for unlabeled data
2. Filter high-confidence predictions (≥0.9)
3. Add as pseudo-labeled examples
4. Combine with original labeled data
5. Re-train for 1 epoch

**Automatically Called**: When unlabeled_data provided to fine_tune()

---

### 4. predict() Method
**Purpose**: Single text classification (needed for semi-supervised)

**Usage Example**:
```python
predictions = service.predict(
    text="Article about machine learning",
    top_k=5
)

# Returns: {"node_id_1": 0.95, "node_id_2": 0.87, ...}
```

---

## Model Checkpoints

**Location**: `models/classification/{version}/`

**Files Saved**:
- `pytorch_model.bin` - Model weights
- `config.json` - Model configuration
- `tokenizer_config.json` - Tokenizer config
- `vocab.txt` - Vocabulary
- `label_map.json` - Taxonomy ID mappings

---

## Configuration Options

### Training Parameters:
- `epochs`: Number of training epochs (default: 3)
- `batch_size`: Training batch size (default: 16)
- `learning_rate`: Learning rate (default: 2e-5)

### Model Selection:
- `model_name`: Base model (default: "distilbert-base-uncased")
- Alternative: "bert-base-uncased" for higher accuracy

### Semi-Supervised:
- `unlabeled_data`: Optional list of texts
- `confidence_threshold`: Minimum confidence for pseudo-labels (0.9)

---

## Requirements Met

✅ 2.2 - Accept labeled data as text/taxonomy pairs  
✅ 2.3 - Multi-label classification support  
✅ 2.6 - F1, precision, recall metrics  
✅ 2.7 - Tokenize with max_length=512  
✅ 5.1 - Configurable training parameters  
✅ 5.2 - 80/20 train/validation split  
✅ 5.3 - Default learning_rate=2e-5  
✅ 5.4 - Default 3 epochs  
✅ 5.5 - Checkpoint after each epoch  
✅ 5.6 - Validation metrics  
✅ 5.7 - Save model, tokenizer, label map  
✅ 14.2 - Save to models/classification/{version}  
✅ 14.3 - Save label mappings as JSON  

---

## Verification

Run verification script:
```bash
python backend/verify_ml_training_implementation.py
```

Expected output: ✅ ALL CHECKS PASSED

---

## Next Steps

1. **Task 8**: Semi-supervised learning (already integrated)
2. **Task 9**: Batch inference (predict_batch)
3. **Task 10**: Active learning workflows
4. **Task 14**: API endpoints for training

---

## Performance Notes

- **Training Time**: 2-30 minutes depending on dataset size
- **GPU Acceleration**: 5-10x faster than CPU
- **Memory**: ~2-4GB GPU memory (batch_size=16)
- **Model Size**: ~250MB (DistilBERT) or ~440MB (BERT)

---

## Common Issues

### ImportError: transformers not installed
```bash
pip install transformers torch scikit-learn
```

### CUDA out of memory
- Reduce batch_size (try 8 or 4)
- Use CPU instead (slower but works)

### Low F1 score
- Need more labeled data (aim for 500+ examples)
- Try semi-supervised learning with unlabeled data
- Increase epochs (try 5-10)

---

## Documentation

- Full Summary: `backend/PHASE8_5_TASK7_SUMMARY.md`
- Design Doc: `.kiro/specs/phase8-5-ml-classification/design.md`
- Requirements: `.kiro/specs/phase8-5-ml-classification/requirements.md`
- Code: `backend/app/services/ml_classification_service.py`
