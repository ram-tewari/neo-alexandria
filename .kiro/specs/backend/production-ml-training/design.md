# Production ML Training Design Document

## Overview

This design document outlines the architecture for production-ready ML model training pipelines using real-world academic datasets (arXiv, PubMed, Semantic Scholar). The system establishes reproducible training workflows that train models on large-scale real data (≥10,000 samples), achieve high accuracy (≥90%), and support continuous model improvement through automated retraining.

### Goals

- Train classification models on ≥10,000 real arXiv papers
- Achieve ≥90% validation accuracy
- Keep model files <500MB for deployment
- Complete training in <4 hours on single GPU
- Establish automated retraining pipeline
- Support model versioning and A/B testing

### Non-Goals

- Training models other than classification (NCF, embeddings handled separately)
- Real-time online learning
- Distributed multi-GPU training
- Custom model architectures (using DistilBERT)

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                   Production ML Training System              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Dataset    │───▶│ Preprocessing│───▶│   Training   │  │
│  │  Collection  │    │   Pipeline   │    │   Pipeline   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ data/raw/    │    │data/processed│    │   models/    │  │
│  │   arxiv/     │    │              │    │classification│  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │Hyperparameter│    │    Model     │    │  Automated   │  │
│  │    Search    │    │  Versioning  │    │  Retraining  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Collection**: arXiv API → Raw JSON files (data/raw/arxiv/)
2. **Preprocessing**: Raw JSON → Cleaned JSON (data/processed/)
3. **Splitting**: Cleaned data → Train/Val/Test splits (data/splits/)
4. **Training**: Splits → Trained model (models/classification/arxiv_vX.Y.Z/)
5. **Evaluation**: Test set → Performance metrics
6. **Deployment**: Best model → Production service


## Components and Interfaces

### 1. Dataset Collection Module

**Location**: `backend/scripts/dataset_acquisition/`

#### ArxivCollector

**Purpose**: Fetch academic papers from arXiv API with rate limiting and error handling.

**Class Interface**:
```python
class ArxivCollector:
    def __init__(self, output_dir: str = "data/raw/arxiv"):
        """Initialize collector with output directory."""
        
    def collect_papers_by_category(
        self,
        category: str,
        max_results: int = 1000,
        start_date: Optional[str] = "2020-01-01"
    ) -> List[Dict]:
        """Collect papers from specific arXiv category."""
        
    def collect_balanced_dataset(
        self,
        categories: List[str],
        papers_per_category: int = 1000
    ) -> Dict[str, List[Dict]]:
        """Collect balanced dataset across multiple categories."""
        
    def create_classification_dataset(
        self,
        num_papers: int = 10000,
        output_file: str = "data/processed/arxiv_classification.json"
    ):
        """Create complete classification dataset with 10 CS categories."""
```

**Key Features**:
- Rate limiting: 3 requests/second (arXiv API limit)
- Retry logic: 3 retries with exponential backoff
- Progress logging: Every 100 papers
- Intermediate saves: Prevent data loss on failures
- Balanced sampling: Equal papers per category

**Target Categories** (10 CS subcategories):
- cs.AI: Artificial Intelligence
- cs.CL: Computation and Language (NLP)
- cs.CV: Computer Vision
- cs.LG: Machine Learning
- cs.CR: Cryptography and Security
- cs.DB: Databases
- cs.DC: Distributed Computing
- cs.NE: Neural Computing
- cs.RO: Robotics
- cs.SE: Software Engineering

**Output Format**:
```json
{
  "metadata": {
    "num_samples": 10000,
    "num_categories": 10,
    "categories": ["cs.AI", "cs.CL", ...],
    "created_at": "2025-11-16T10:00:00",
    "source": "arXiv API"
  },
  "samples": [
    {
      "text": "Title. Abstract text...",
      "label": "cs.AI",
      "arxiv_id": "2301.12345",
      "title": "Paper Title",
      "authors": ["Author 1", "Author 2"],
      "published": "2023-01-15T00:00:00"
    }
  ]
}
```

**Dependencies**:
- `arxiv` Python library
- Rate limiting: 0.5s delay between requests
- Storage: ~500MB for 10k papers


### 2. Dataset Preprocessing Module

**Location**: `backend/scripts/dataset_acquisition/`

#### DatasetPreprocessor

**Purpose**: Clean, deduplicate, and validate raw datasets for ML training.

**Class Interface**:
```python
class DatasetPreprocessor:
    def clean_text(self, text: str) -> str:
        """Clean text (remove URLs, LaTeX, normalize whitespace)."""
        
    def compute_text_hash(self, text: str) -> str:
        """Compute MD5 hash for deduplication."""
        
    def deduplicate_samples(self, samples: List[Dict]) -> List[Dict]:
        """Remove duplicates by arXiv ID and title hash."""
        
    def filter_by_quality(
        self,
        samples: List[Dict],
        min_words: int = 50
    ) -> List[Dict]:
        """Filter samples by quality criteria."""
        
    def preprocess_dataset(
        self,
        input_file: str,
        output_file: str,
        min_words: int = 50
    ) -> Dict:
        """Complete preprocessing pipeline."""
        
    def create_train_val_test_split(
        self,
        input_file: str,
        output_dir: str,
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        random_seed: int = 42
    ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Stratified split into train/val/test sets."""
```

**Preprocessing Steps**:

1. **Text Cleaning**:
   - Remove URLs: `http\S+`
   - Remove LaTeX commands: `\\[a-zA-Z]+\{[^}]*\}`
   - Remove inline math: `\$[^$]*\$`
   - Normalize whitespace: Multiple spaces → single space
   - Remove multiple punctuation: `...` → `.`

2. **Deduplication**:
   - By arXiv ID (exact match)
   - By title hash (near-duplicates)
   - MD5 hashing for efficiency

3. **Quality Filtering**:
   - Minimum 50 words in abstract
   - English language detection (character-based)
   - Valid label present
   - No empty text fields

4. **Stratified Splitting**:
   - 80% training, 10% validation, 10% test
   - Maintain class balance across splits
   - Fixed random seed (42) for reproducibility
   - sklearn's `train_test_split` with `stratify` parameter

**Output Structure**:
```
data/splits/arxiv_classification/
├── train.json      # 8,000 samples (80%)
├── val.json        # 1,000 samples (10%)
└── test.json       # 1,000 samples (10%)
```


### 3. Classification Training Module

**Location**: `backend/scripts/training/`

#### ClassificationTrainer

**Purpose**: Train DistilBERT classification models on arXiv data with GPU optimization.

**Class Interface**:
```python
class ClassificationTrainer:
    def __init__(
        self,
        model_name: str = "distilbert-base-uncased",
        output_dir: str = "models/classification/arxiv_v1"
    ):
        """Initialize trainer with model and output directory."""
        
    def load_datasets(self, data_dir: str):
        """Load train/val/test splits and build label mapping."""
        
    def train(
        self,
        train_samples: list,
        val_samples: list,
        epochs: int = 3,
        batch_size: int = 16,
        learning_rate: float = 2e-5
    ):
        """Train classification model with Hugging Face Trainer."""
        
    def evaluate(self, test_samples: list):
        """Evaluate on test set and generate classification report."""
        
    def compute_metrics(self, eval_pred):
        """Compute accuracy for evaluation callback."""
```

**Training Configuration**:

**Model Architecture**:
- Base: DistilBERT-base-uncased (66M parameters)
- Fine-tuning: Classification head for 10 categories
- Input: 512 tokens maximum
- Output: 10-class softmax

**Hyperparameters**:
- Epochs: 3
- Batch size: 16 (adjustable for memory)
- Learning rate: 2e-5
- Warmup steps: 500
- Weight decay: 0.01
- Optimizer: AdamW

**Training Features**:
- Mixed precision (fp16) on GPU
- Early stopping (patience=2 epochs)
- Gradient checkpointing for memory efficiency
- Evaluation after each epoch
- Save best model by validation accuracy
- TensorBoard logging

**PyTorch Dataset**:
```python
class ArxivClassificationDataset(Dataset):
    def __init__(self, samples: list, tokenizer, label_to_id: dict):
        self.samples = samples
        self.tokenizer = tokenizer
        self.label_to_id = label_to_id
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        text = sample["text"]
        label = self.label_to_id[sample["label"]]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=512,
            return_tensors="pt"
        )
        
        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "labels": torch.tensor(label, dtype=torch.long)
        }
```

**Training Pipeline**:
1. Load datasets and build label mapping
2. Initialize tokenizer and model
3. Create PyTorch datasets
4. Configure Hugging Face Trainer
5. Train with evaluation
6. Save best model checkpoint
7. Evaluate on test set
8. Generate classification report

**Performance Targets**:
- Validation accuracy: ≥90%
- Training time: <4 hours on V100 GPU
- Model size: <500MB
- Inference latency: <100ms per sample


### 4. Hyperparameter Search Module

**Location**: `backend/scripts/training/`

#### HyperparameterSearch

**Purpose**: Automated hyperparameter tuning using Optuna for optimal model configuration.

**Class Interface**:
```python
class HyperparameterSearch:
    def __init__(
        self,
        data_dir: str,
        output_dir: str = "models/classification/hp_search"
    ):
        """Initialize HP search with data and output directories."""
        
    def objective(self, trial: optuna.Trial) -> float:
        """Objective function for Optuna optimization."""
        
    def search(
        self,
        n_trials: int = 20,
        timeout: int = 28800  # 8 hours
    ) -> Dict[str, Any]:
        """Run hyperparameter search and return best params."""
        
    def visualize_results(self, study: optuna.Study):
        """Generate visualization of HP search results."""
```

**Search Space**:
```python
{
    "learning_rate": [1e-5, 5e-5],      # Log-uniform
    "batch_size": [8, 16, 32],          # Categorical
    "warmup_steps": [100, 500, 1000],   # Categorical
    "weight_decay": [0.0, 0.1],         # Uniform
    "epochs": [3, 5]                    # Categorical
}
```

**Optimization Strategy**:
- Framework: Optuna
- Objective: Maximize validation accuracy
- Sampler: TPE (Tree-structured Parzen Estimator)
- Pruner: MedianPruner (early stopping for unpromising trials)
- Budget: 20 trials, 8 hours maximum
- Parallel: 1 trial at a time (GPU constraint)

**Search Algorithm**:
1. Sample hyperparameters from search space
2. Train model with sampled hyperparameters
3. Evaluate on validation set
4. Report validation accuracy to Optuna
5. Prune trial if performance is poor
6. Repeat until budget exhausted
7. Return best hyperparameters

**Output**:
```json
{
  "best_params": {
    "learning_rate": 2.5e-5,
    "batch_size": 16,
    "warmup_steps": 500,
    "weight_decay": 0.01,
    "epochs": 3
  },
  "best_value": 0.912,
  "n_trials": 20,
  "search_time": 25200,
  "study_name": "arxiv_classification_hp_search"
}
```

**Visualization**:
- Optimization history plot
- Parameter importance plot
- Parallel coordinate plot
- Slice plot for each parameter


### 5. Model Versioning Module

**Location**: `backend/scripts/deployment/`

#### ModelVersioning

**Purpose**: Semantic versioning system for tracking model iterations and metadata.

**Class Interface**:
```python
class ModelVersioning:
    def __init__(self, base_dir: str = "models/classification"):
        """Initialize versioning system."""
        
    def create_version(
        self,
        model_path: str,
        version: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Create new model version with metadata."""
        
    def list_versions(self) -> List[Dict[str, Any]]:
        """List all available model versions."""
        
    def load_version(self, version: str) -> Tuple[Any, Dict]:
        """Load specific model version with metadata."""
        
    def promote_to_production(self, version: str):
        """Promote model version to production."""
        
    def compare_versions(
        self,
        version1: str,
        version2: str,
        test_data: List
    ) -> Dict[str, Any]:
        """Compare two model versions on test data."""
```

**Versioning Scheme**: Semantic Versioning (vX.Y.Z)

- **Major (X)**: Architecture changes (e.g., BERT → RoBERTa)
- **Minor (Y)**: Dataset updates or retraining
- **Patch (Z)**: Hyperparameter tuning or bug fixes

**Examples**:
- v1.0.0: Initial model trained on 10k arXiv papers
- v1.1.0: Retrained with 15k papers (dataset update)
- v1.1.1: Hyperparameter tuning on same dataset
- v2.0.0: Architecture change to RoBERTa

**Directory Structure**:
```
models/classification/
├── arxiv_v1.0.0/
│   ├── pytorch_model.bin
│   ├── config.json
│   ├── tokenizer_config.json
│   ├── vocab.txt
│   ├── label_map.json
│   └── metadata.json
├── arxiv_v1.1.0/
│   └── ...
├── arxiv_v1.1.1/
│   └── ...
├── production -> arxiv_v1.1.0/  # Symlink to production model
└── version_registry.json
```

**Metadata Format**:
```json
{
  "version": "v1.0.0",
  "created_at": "2025-11-16T10:00:00",
  "model_name": "distilbert-base-uncased",
  "dataset": {
    "source": "arXiv",
    "num_samples": 10000,
    "num_categories": 10,
    "split": "80/10/10"
  },
  "hyperparameters": {
    "epochs": 3,
    "batch_size": 16,
    "learning_rate": 2e-5,
    "warmup_steps": 500
  },
  "metrics": {
    "train_accuracy": 0.95,
    "val_accuracy": 0.912,
    "test_accuracy": 0.908,
    "f1_score": 0.905,
    "training_time": 7200
  },
  "model_size_mb": 268,
  "git_commit": "abc123def456",
  "notes": "Initial production model"
}
```

**Version Registry**:
```json
{
  "versions": [
    {
      "version": "v1.0.0",
      "path": "models/classification/arxiv_v1.0.0",
      "created_at": "2025-11-16T10:00:00",
      "status": "archived"
    },
    {
      "version": "v1.1.0",
      "path": "models/classification/arxiv_v1.1.0",
      "created_at": "2025-11-20T14:30:00",
      "status": "production"
    }
  ],
  "production_version": "v1.1.0",
  "latest_version": "v1.1.0"
}
```


### 6. A/B Testing Module

**Location**: `backend/scripts/deployment/`

#### ABTestingFramework

**Purpose**: Compare multiple model versions in production to validate improvements.

**Class Interface**:
```python
class ABTestingFramework:
    def __init__(self, db: Session):
        """Initialize A/B testing framework."""
        
    def create_experiment(
        self,
        name: str,
        control_version: str,
        treatment_version: str,
        traffic_split: float = 0.1
    ) -> str:
        """Create new A/B test experiment."""
        
    def route_prediction(
        self,
        experiment_id: str,
        user_id: str
    ) -> str:
        """Route prediction request to control or treatment."""
        
    def log_prediction(
        self,
        experiment_id: str,
        version: str,
        input_text: str,
        predictions: Dict,
        latency_ms: float
    ):
        """Log prediction for analysis."""
        
    def analyze_experiment(
        self,
        experiment_id: str
    ) -> Dict[str, Any]:
        """Analyze A/B test results."""
        
    def promote_winner(self, experiment_id: str):
        """Promote winning model to production."""
```

**A/B Testing Workflow**:

1. **Setup**:
   - Define control (current production) and treatment (candidate)
   - Set traffic split (e.g., 90% control, 10% treatment)
   - Define success metrics (accuracy, latency, user satisfaction)

2. **Routing**:
   - Hash user ID to determine assignment
   - Consistent routing (same user always gets same version)
   - Log all predictions with version tag

3. **Monitoring**:
   - Track accuracy on labeled data
   - Track inference latency (p50, p95, p99)
   - Track prediction differences between versions
   - Monitor error rates

4. **Analysis**:
   - Statistical significance testing (t-test, chi-square)
   - Confidence intervals for metrics
   - Sample size calculation
   - Minimum detectable effect

5. **Decision**:
   - Promote treatment if significantly better (p < 0.05)
   - Require minimum improvement threshold (e.g., +2% accuracy)
   - Consider latency and resource usage
   - Rollback if treatment performs worse

**Experiment Configuration**:
```json
{
  "experiment_id": "exp_001",
  "name": "arxiv_v1.1.0_vs_v1.0.0",
  "control_version": "v1.0.0",
  "treatment_version": "v1.1.0",
  "traffic_split": 0.1,
  "start_date": "2025-11-16",
  "end_date": "2025-11-23",
  "status": "running",
  "metrics": {
    "primary": "accuracy",
    "secondary": ["latency_p95", "f1_score"]
  }
}
```

**Results Report**:
```json
{
  "experiment_id": "exp_001",
  "duration_days": 7,
  "control": {
    "version": "v1.0.0",
    "predictions": 45000,
    "accuracy": 0.908,
    "latency_p95": 95,
    "f1_score": 0.905
  },
  "treatment": {
    "version": "v1.1.0",
    "predictions": 5000,
    "accuracy": 0.925,
    "latency_p95": 92,
    "f1_score": 0.922
  },
  "statistical_significance": {
    "accuracy_p_value": 0.003,
    "improvement": 0.017,
    "confidence_interval": [0.012, 0.022]
  },
  "recommendation": "PROMOTE",
  "reason": "Treatment significantly better (p=0.003, +1.7% accuracy)"
}
```


### 7. Automated Retraining Pipeline

**Location**: `backend/scripts/training/`

#### RetrainingPipeline

**Purpose**: Automated pipeline that checks for new data and retrains models when beneficial.

**Class Interface**:
```python
class RetrainingPipeline:
    def __init__(
        self,
        config_path: str = "config/retraining_config.json"
    ):
        """Initialize retraining pipeline with configuration."""
        
    def check_for_new_data(self) -> Dict[str, Any]:
        """Check arXiv API for new papers since last training."""
        
    def should_retrain(
        self,
        new_data_count: int,
        current_dataset_size: int
    ) -> bool:
        """Determine if retraining is needed."""
        
    def augment_dataset(
        self,
        existing_data: List,
        new_data: List
    ) -> List:
        """Combine existing and new data."""
        
    def train_new_version(
        self,
        dataset: List,
        current_version: str
    ) -> Tuple[str, Dict]:
        """Train new model version."""
        
    def evaluate_improvement(
        self,
        new_version: str,
        production_version: str,
        test_data: List
    ) -> Dict[str, Any]:
        """Compare new model vs production."""
        
    def promote_if_better(
        self,
        new_version: str,
        comparison: Dict
    ) -> bool:
        """Promote new model if significantly better."""
        
    def run_pipeline(self):
        """Execute complete retraining pipeline."""
```

**Retraining Schedule**: Weekly (every Sunday at 2 AM)

**Retraining Triggers**:
1. **Data Growth**: Dataset grows by >10%
2. **Performance Degradation**: Production accuracy drops >5%
3. **Manual Trigger**: Admin initiates retraining
4. **Scheduled**: Weekly check regardless

**Pipeline Steps**:

1. **Check for New Data**:
   ```python
   # Query arXiv API for papers published since last training
   last_training_date = get_last_training_date()
   new_papers = arxiv_collector.collect_papers_by_category(
       category="cs.*",
       start_date=last_training_date
   )
   ```

2. **Evaluate Retraining Need**:
   ```python
   current_size = len(existing_dataset)
   new_size = len(new_papers)
   growth_rate = new_size / current_size
   
   should_retrain = growth_rate > 0.10  # 10% threshold
   ```

3. **Augment Dataset**:
   ```python
   # Combine existing and new data
   augmented_dataset = existing_dataset + new_papers
   
   # Preprocess new data
   augmented_dataset = preprocessor.preprocess_dataset(augmented_dataset)
   
   # Create new splits
   train, val, test = preprocessor.create_train_val_test_split(
       augmented_dataset
   )
   ```

4. **Train New Version**:
   ```python
   # Increment minor version
   new_version = increment_version(current_version, level="minor")
   
   # Train model
   trainer = ClassificationTrainer(output_dir=f"models/classification/arxiv_{new_version}")
   metrics = trainer.train(train, val)
   ```

5. **Evaluate on Test Set**:
   ```python
   # Load production model
   prod_model = load_model(production_version)
   
   # Load new model
   new_model = load_model(new_version)
   
   # Compare on held-out test set
   prod_accuracy = evaluate(prod_model, test_data)
   new_accuracy = evaluate(new_model, test_data)
   
   improvement = new_accuracy - prod_accuracy
   ```

6. **Promotion Decision**:
   ```python
   PROMOTION_THRESHOLD = 0.02  # 2% improvement required
   
   if improvement > PROMOTION_THRESHOLD:
       promote_to_production(new_version)
       send_notification(f"New model {new_version} promoted (+{improvement:.1%})")
   else:
       archive_model(new_version)
       send_notification(f"New model {new_version} not promoted (+{improvement:.1%})")
   ```

**Configuration**:
```json
{
  "schedule": "0 2 * * 0",
  "data_growth_threshold": 0.10,
  "promotion_threshold": 0.02,
  "max_training_time": 14400,
  "notification_email": "ml-team@example.com",
  "slack_webhook": "https://hooks.slack.com/...",
  "enable_auto_promotion": true,
  "enable_ab_testing": true,
  "ab_test_duration_days": 7
}
```

**Notification Example**:
```
Subject: Model Retraining Complete - arxiv_v1.2.0

New model version trained: arxiv_v1.2.0

Dataset:
- Previous: 10,000 samples
- New: 11,500 samples (+15%)
- Growth: 1,500 new papers

Performance:
- Production (v1.1.0): 91.2% accuracy
- New (v1.2.0): 93.5% accuracy (+2.3%)

Decision: PROMOTED to production
Reason: Exceeds 2% improvement threshold

Training time: 3.2 hours
Model size: 268 MB
```


## Data Models

### Dataset Schema

**Raw arXiv Paper**:
```python
{
    "arxiv_id": str,           # "2301.12345"
    "title": str,              # Paper title
    "abstract": str,           # Paper abstract
    "authors": List[str],      # ["Author 1", "Author 2"]
    "categories": List[str],   # ["cs.AI", "cs.LG"]
    "primary_category": str,   # "cs.AI"
    "published": str,          # ISO 8601 timestamp
    "updated": Optional[str],  # ISO 8601 timestamp
    "pdf_url": str,           # URL to PDF
    "comment": Optional[str], # Author comments
    "journal_ref": Optional[str]  # Journal reference
}
```

**Training Sample**:
```python
{
    "text": str,              # "Title. Abstract text..."
    "label": str,             # "cs.AI"
    "arxiv_id": str,          # "2301.12345"
    "title": str,             # Paper title
    "authors": List[str],     # ["Author 1", "Author 2"]
    "published": str          # ISO 8601 timestamp
}
```

**Model Checkpoint**:
```python
{
    "model_state_dict": OrderedDict,  # PyTorch model weights
    "tokenizer_config": Dict,         # Tokenizer configuration
    "label_mapping": {
        "id_to_label": Dict[int, str],  # {0: "cs.AI", 1: "cs.CL", ...}
        "label_to_id": Dict[str, int]   # {"cs.AI": 0, "cs.CL": 1, ...}
    },
    "metadata": {
        "version": str,
        "created_at": str,
        "model_name": str,
        "num_labels": int,
        "dataset_size": int,
        "hyperparameters": Dict,
        "metrics": Dict
    }
}
```

### Database Schema Extensions

**ModelVersion Table** (new):
```sql
CREATE TABLE model_versions (
    id UUID PRIMARY KEY,
    version VARCHAR(20) NOT NULL UNIQUE,  -- "v1.0.0"
    model_type VARCHAR(50) NOT NULL,      -- "classification"
    model_path TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,          -- "training", "testing", "production", "archived"
    created_at TIMESTAMP NOT NULL,
    promoted_at TIMESTAMP,
    metadata JSONB,
    metrics JSONB,
    INDEX idx_version (version),
    INDEX idx_status (status)
);
```

**ABTestExperiment Table** (new):
```sql
CREATE TABLE ab_test_experiments (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    control_version_id UUID REFERENCES model_versions(id),
    treatment_version_id UUID REFERENCES model_versions(id),
    traffic_split FLOAT NOT NULL,         -- 0.0 to 1.0
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    status VARCHAR(20) NOT NULL,          -- "running", "completed", "cancelled"
    results JSONB,
    INDEX idx_status (status),
    INDEX idx_dates (start_date, end_date)
);
```

**PredictionLog Table** (new):
```sql
CREATE TABLE prediction_logs (
    id UUID PRIMARY KEY,
    experiment_id UUID REFERENCES ab_test_experiments(id),
    model_version_id UUID REFERENCES model_versions(id),
    input_text TEXT NOT NULL,
    predictions JSONB NOT NULL,
    latency_ms FLOAT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    user_id UUID,
    INDEX idx_experiment (experiment_id),
    INDEX idx_version (model_version_id),
    INDEX idx_created_at (created_at)
);
```

**RetrainingRun Table** (new):
```sql
CREATE TABLE retraining_runs (
    id UUID PRIMARY KEY,
    trigger_type VARCHAR(50) NOT NULL,    -- "scheduled", "manual", "data_growth"
    dataset_size INT NOT NULL,
    new_data_count INT NOT NULL,
    model_version_id UUID REFERENCES model_versions(id),
    status VARCHAR(20) NOT NULL,          -- "running", "completed", "failed"
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    training_time_seconds INT,
    metrics JSONB,
    error_message TEXT,
    INDEX idx_status (status),
    INDEX idx_started_at (started_at)
);
```


## Error Handling

### Collection Errors

**API Rate Limiting**:
```python
class RateLimitError(Exception):
    """Raised when API rate limit exceeded."""
    pass

def collect_with_retry(category: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return collect_papers_by_category(category)
        except RateLimitError:
            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(f"Rate limit hit, waiting {wait_time}s...")
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

**Network Errors**:
```python
def collect_with_network_retry(category: str):
    try:
        return collect_papers_by_category(category)
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Network error: {e}")
        # Save partial results
        save_intermediate_results()
        raise
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout error: {e}")
        # Retry with longer timeout
        return collect_papers_by_category(category, timeout=60)
```

### Training Errors

**Out of Memory (OOM)**:
```python
def train_with_oom_handling(trainer, train_data):
    try:
        return trainer.train(train_data, batch_size=16)
    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            logger.warning("OOM error, reducing batch size...")
            torch.cuda.empty_cache()
            return trainer.train(train_data, batch_size=8)
        raise
```

**Training Divergence**:
```python
class TrainingDivergenceError(Exception):
    """Raised when training loss becomes NaN or infinite."""
    pass

def check_training_health(loss: float, step: int):
    if math.isnan(loss) or math.isinf(loss):
        logger.error(f"Training diverged at step {step}: loss={loss}")
        raise TrainingDivergenceError(
            f"Training diverged (loss={loss}). "
            "Try reducing learning rate or checking data quality."
        )
```

**Checkpoint Corruption**:
```python
def load_checkpoint_with_validation(checkpoint_path: str):
    try:
        checkpoint = torch.load(checkpoint_path)
        
        # Validate required keys
        required_keys = ["model_state_dict", "metadata"]
        for key in required_keys:
            if key not in checkpoint:
                raise ValueError(f"Missing key: {key}")
        
        return checkpoint
        
    except Exception as e:
        logger.error(f"Checkpoint corrupted: {e}")
        
        # Try to load from backup
        backup_path = checkpoint_path + ".backup"
        if os.path.exists(backup_path):
            logger.info("Loading from backup checkpoint...")
            return torch.load(backup_path)
        
        raise
```

### Data Quality Errors

**Invalid Data Format**:
```python
def validate_sample(sample: Dict) -> bool:
    """Validate training sample format."""
    required_fields = ["text", "label", "arxiv_id"]
    
    for field in required_fields:
        if field not in sample:
            logger.warning(f"Missing field: {field}")
            return False
    
    if not sample["text"].strip():
        logger.warning("Empty text field")
        return False
    
    if len(sample["text"].split()) < 10:
        logger.warning("Text too short (<10 words)")
        return False
    
    return True
```

**Label Inconsistency**:
```python
def validate_labels(samples: List[Dict], expected_labels: Set[str]):
    """Validate that all labels are in expected set."""
    found_labels = set()
    invalid_samples = []
    
    for i, sample in enumerate(samples):
        label = sample["label"]
        found_labels.add(label)
        
        if label not in expected_labels:
            invalid_samples.append((i, label))
    
    if invalid_samples:
        logger.error(f"Found {len(invalid_samples)} samples with invalid labels")
        for idx, label in invalid_samples[:5]:  # Show first 5
            logger.error(f"  Sample {idx}: unexpected label '{label}'")
        
        raise ValueError(
            f"Invalid labels found. Expected: {expected_labels}, "
            f"Found: {found_labels}"
        )
```

### Deployment Errors

**Model Loading Failure**:
```python
def load_model_with_fallback(version: str):
    """Load model with fallback to previous version."""
    try:
        return load_model(version)
    except Exception as e:
        logger.error(f"Failed to load model {version}: {e}")
        
        # Fall back to previous production version
        previous_version = get_previous_production_version()
        logger.warning(f"Falling back to {previous_version}")
        
        return load_model(previous_version)
```

**Version Conflict**:
```python
def promote_version_with_validation(new_version: str):
    """Promote model version with validation."""
    # Check if version already exists
    if version_exists(new_version):
        raise ValueError(f"Version {new_version} already exists")
    
    # Validate version format
    if not re.match(r"^v\d+\.\d+\.\d+$", new_version):
        raise ValueError(f"Invalid version format: {new_version}")
    
    # Check if new version is newer than current
    current_version = get_production_version()
    if not is_newer_version(new_version, current_version):
        raise ValueError(
            f"New version {new_version} is not newer than "
            f"current {current_version}"
        )
    
    # Promote
    promote_to_production(new_version)
```


## Testing Strategy

### Unit Tests

**Dataset Collection**:
```python
def test_arxiv_collector_rate_limiting():
    """Test that rate limiting is respected."""
    collector = ArxivCollector()
    
    start_time = time.time()
    collector.collect_papers_by_category("cs.AI", max_results=10)
    elapsed = time.time() - start_time
    
    # Should take at least 3 seconds (10 papers / 3 per second)
    assert elapsed >= 3.0

def test_arxiv_collector_retry_logic():
    """Test retry logic on API errors."""
    collector = ArxivCollector()
    
    with patch('arxiv.Client.results') as mock_results:
        mock_results.side_effect = [
            ConnectionError("Network error"),
            ConnectionError("Network error"),
            [mock_paper()]  # Success on 3rd try
        ]
        
        papers = collector.collect_papers_by_category("cs.AI", max_results=1)
        assert len(papers) == 1
        assert mock_results.call_count == 3
```

**Data Preprocessing**:
```python
def test_text_cleaning():
    """Test text cleaning removes URLs and LaTeX."""
    preprocessor = DatasetPreprocessor()
    
    text = "Check https://example.com and $\\alpha$ formula"
    cleaned = preprocessor.clean_text(text)
    
    assert "https://example.com" not in cleaned
    assert "$\\alpha$" not in cleaned

def test_deduplication():
    """Test deduplication removes duplicates."""
    preprocessor = DatasetPreprocessor()
    
    samples = [
        {"arxiv_id": "1", "title": "Paper A", "text": "Content A"},
        {"arxiv_id": "1", "title": "Paper A", "text": "Content A"},  # Duplicate
        {"arxiv_id": "2", "title": "Paper B", "text": "Content B"}
    ]
    
    unique = preprocessor.deduplicate_samples(samples)
    assert len(unique) == 2
```

**Model Training**:
```python
def test_classification_trainer_initialization():
    """Test trainer initializes correctly."""
    trainer = ClassificationTrainer(
        model_name="distilbert-base-uncased",
        output_dir="models/test"
    )
    
    assert trainer.model_name == "distilbert-base-uncased"
    assert trainer.checkpoint_dir.exists()

def test_label_mapping_creation():
    """Test label mapping is created correctly."""
    trainer = ClassificationTrainer()
    
    samples = [
        {"text": "Text 1", "label": "cs.AI"},
        {"text": "Text 2", "label": "cs.LG"},
        {"text": "Text 3", "label": "cs.AI"}
    ]
    
    trainer.load_datasets_from_samples(samples)
    
    assert len(trainer.label_to_id) == 2
    assert "cs.AI" in trainer.label_to_id
    assert "cs.LG" in trainer.label_to_id
```

### Integration Tests

**End-to-End Training Pipeline**:
```python
def test_full_training_pipeline():
    """Test complete training pipeline with small dataset."""
    # 1. Collect small dataset
    collector = ArxivCollector()
    papers = collector.collect_papers_by_category("cs.AI", max_results=100)
    
    # 2. Preprocess
    preprocessor = DatasetPreprocessor()
    cleaned = preprocessor.preprocess_dataset(papers)
    train, val, test = preprocessor.create_train_val_test_split(cleaned)
    
    # 3. Train
    trainer = ClassificationTrainer(output_dir="models/test")
    metrics = trainer.train(train, val, epochs=1, batch_size=8)
    
    # 4. Evaluate
    test_metrics = trainer.evaluate(test)
    
    # Assertions
    assert metrics["f1"] > 0.5  # Reasonable performance
    assert test_metrics["accuracy"] > 0.5
    assert (Path("models/test") / "pytorch_model.bin").exists()
```

**Model Versioning**:
```python
def test_version_creation_and_loading():
    """Test creating and loading model versions."""
    versioning = ModelVersioning()
    
    # Create version
    metadata = {
        "dataset_size": 1000,
        "accuracy": 0.90
    }
    version_path = versioning.create_version(
        model_path="models/test",
        version="v1.0.0",
        metadata=metadata
    )
    
    # Load version
    model, loaded_metadata = versioning.load_version("v1.0.0")
    
    assert loaded_metadata["dataset_size"] == 1000
    assert loaded_metadata["accuracy"] == 0.90
```

### Performance Tests

**Training Speed**:
```python
def test_training_speed():
    """Test training completes within time limit."""
    trainer = ClassificationTrainer()
    
    # Small dataset for speed test
    train_data = create_mock_dataset(size=1000)
    val_data = create_mock_dataset(size=100)
    
    start_time = time.time()
    trainer.train(train_data, val_data, epochs=1)
    elapsed = time.time() - start_time
    
    # Should complete in under 5 minutes on GPU
    assert elapsed < 300
```

**Inference Latency**:
```python
def test_inference_latency():
    """Test inference meets latency requirements."""
    trainer = ClassificationTrainer()
    trainer.load_model("models/test")
    
    text = "Machine learning paper about neural networks"
    
    latencies = []
    for _ in range(100):
        start = time.time()
        predictions = trainer.predict(text)
        latency = (time.time() - start) * 1000  # ms
        latencies.append(latency)
    
    p95_latency = np.percentile(latencies, 95)
    assert p95_latency < 100  # <100ms p95
```

### Benchmark Tests

**Model Accuracy**:
```python
def test_model_accuracy_benchmark():
    """Test model meets accuracy requirements."""
    trainer = ClassificationTrainer()
    trainer.load_model("models/production")
    
    # Load benchmark test set
    test_data = load_benchmark_dataset("arxiv_test_1000")
    
    metrics = trainer.evaluate(test_data)
    
    assert metrics["accuracy"] >= 0.90  # ≥90% accuracy
    assert metrics["f1"] >= 0.88  # ≥88% F1 score
```

**Model Size**:
```python
def test_model_size_constraint():
    """Test model size is within deployment limits."""
    model_path = Path("models/production/pytorch_model.bin")
    size_mb = model_path.stat().st_size / (1024 * 1024)
    
    assert size_mb < 500  # <500MB
```


## Performance Considerations

### Training Optimization

**GPU Utilization**:
- Mixed precision (fp16) training reduces memory by 50%
- Gradient checkpointing trades compute for memory
- Batch size tuning for optimal GPU utilization
- DataLoader with multiple workers for I/O parallelism

**Memory Management**:
```python
# Enable gradient checkpointing
model.gradient_checkpointing_enable()

# Use mixed precision
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

with autocast():
    outputs = model(**inputs)
    loss = outputs.loss

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

**Training Speed**:
- DistilBERT: 40% faster than BERT-base
- Batch size 16: ~2 hours for 10k samples on V100
- Batch size 32: ~1.5 hours (if memory allows)
- CPU training: ~20 hours (not recommended)

### Inference Optimization

**Model Quantization**:
```python
# Dynamic quantization for CPU inference
import torch.quantization

quantized_model = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear},
    dtype=torch.qint8
)

# 4x smaller model, 2-3x faster inference
```

**Batch Inference**:
```python
# Process multiple texts in batches
def predict_batch(texts: List[str], batch_size: int = 32):
    predictions = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_preds = model.predict(batch)
        predictions.extend(batch_preds)
    
    return predictions
```

**Caching**:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def predict_with_cache(text: str):
    """Cache predictions for frequently seen texts."""
    return model.predict(text)
```

### Storage Optimization

**Dataset Compression**:
```python
import gzip
import json

# Compress large datasets
with gzip.open("data/arxiv_10k.json.gz", "wt") as f:
    json.dump(dataset, f)

# 70-80% size reduction
```

**Model Checkpointing**:
```python
# Save only best model, not all epochs
training_args = TrainingArguments(
    save_strategy="epoch",
    save_total_limit=2,  # Keep only 2 most recent
    load_best_model_at_end=True
)
```

### Scalability

**Horizontal Scaling**:
- Multiple training jobs in parallel (different hyperparameters)
- Distributed data collection (multiple API keys)
- Load balancing for inference (multiple model replicas)

**Vertical Scaling**:
- Larger GPU for faster training (V100 → A100)
- More CPU cores for data preprocessing
- More RAM for larger datasets

**Cost Optimization**:
- Use spot instances for training (50-70% cheaper)
- Schedule training during off-peak hours
- Archive old model versions to cold storage
- Use CPU inference for non-critical paths


## Security and Privacy

### Data Security

**API Key Management**:
```python
# Never hardcode API keys
import os

ARXIV_API_KEY = os.getenv("ARXIV_API_KEY")
if not ARXIV_API_KEY:
    raise ValueError("ARXIV_API_KEY environment variable not set")
```

**Data Sanitization**:
```python
def sanitize_text(text: str) -> str:
    """Remove PII and sensitive information."""
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Remove phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    
    # Remove URLs with query parameters (may contain tokens)
    text = re.sub(r'https?://[^\s]+\?[^\s]+', '[URL]', text)
    
    return text
```

### Model Security

**Checkpoint Integrity**:
```python
import hashlib

def compute_checkpoint_hash(checkpoint_path: str) -> str:
    """Compute SHA256 hash of checkpoint file."""
    sha256 = hashlib.sha256()
    
    with open(checkpoint_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    
    return sha256.hexdigest()

def verify_checkpoint(checkpoint_path: str, expected_hash: str):
    """Verify checkpoint hasn't been tampered with."""
    actual_hash = compute_checkpoint_hash(checkpoint_path)
    
    if actual_hash != expected_hash:
        raise ValueError(
            f"Checkpoint integrity check failed. "
            f"Expected: {expected_hash}, Got: {actual_hash}"
        )
```

**Access Control**:
```python
# Restrict model directory permissions
import os
import stat

model_dir = Path("models/classification")
os.chmod(model_dir, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)  # 700
```

### Privacy Considerations

**Data Retention**:
- Raw data: Keep for 90 days, then archive
- Training data: Keep for 1 year
- Model checkpoints: Keep production + 2 previous versions
- Prediction logs: Aggregate and anonymize after 30 days

**Anonymization**:
```python
def anonymize_prediction_log(log: Dict) -> Dict:
    """Anonymize prediction log for analysis."""
    return {
        "model_version": log["model_version"],
        "predictions": log["predictions"],
        "latency_ms": log["latency_ms"],
        "timestamp": log["timestamp"],
        # Remove: user_id, input_text, IP address
    }
```

### Compliance

**GDPR Compliance**:
- Right to erasure: Delete user data on request
- Data minimization: Only collect necessary data
- Purpose limitation: Use data only for training
- Transparency: Document data usage in privacy policy

**Model Cards**:
```markdown
# Model Card: arXiv Classification v1.0.0

## Model Details
- Developed by: Neo Alexandria ML Team
- Model date: November 2025
- Model type: Text classification
- Model version: v1.0.0

## Intended Use
- Primary use: Classify academic papers into CS categories
- Primary users: Researchers, librarians
- Out-of-scope: Medical diagnosis, legal advice

## Training Data
- Dataset: arXiv CS papers (2020-2025)
- Size: 10,000 papers
- Categories: 10 CS subcategories
- Language: English

## Evaluation Data
- Test set: 1,000 papers (held-out)
- Metrics: Accuracy 91.2%, F1 90.8%

## Ethical Considerations
- Bias: May favor certain research areas
- Limitations: English-only, CS domain only
- Recommendations: Human review for critical decisions

## Caveats and Recommendations
- Not suitable for non-CS papers
- May misclassify interdisciplinary work
- Confidence scores should be considered
```


## Monitoring and Observability

### Training Metrics

**TensorBoard Integration**:
```python
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter(log_dir="models/classification/logs")

# Log training metrics
writer.add_scalar("Loss/train", train_loss, epoch)
writer.add_scalar("Accuracy/val", val_accuracy, epoch)
writer.add_scalar("F1/val", val_f1, epoch)

# Log learning rate
writer.add_scalar("LearningRate", optimizer.param_groups[0]['lr'], step)

# Log model graph
writer.add_graph(model, sample_input)
```

**Progress Tracking**:
```python
from tqdm import tqdm

for epoch in range(epochs):
    progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")
    
    for batch in progress_bar:
        loss = train_step(batch)
        progress_bar.set_postfix({"loss": f"{loss:.4f}"})
```

### Production Monitoring

**Prediction Metrics**:
```python
class PredictionMonitor:
    def __init__(self):
        self.predictions = []
        self.latencies = []
        self.errors = []
    
    def log_prediction(
        self,
        input_text: str,
        predictions: Dict,
        latency_ms: float,
        error: Optional[str] = None
    ):
        """Log prediction for monitoring."""
        self.predictions.append({
            "timestamp": datetime.now(),
            "input_length": len(input_text),
            "num_predictions": len(predictions),
            "top_confidence": max(predictions.values()),
            "latency_ms": latency_ms,
            "error": error
        })
    
    def get_metrics(self, window_minutes: int = 60):
        """Get metrics for last N minutes."""
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        recent = [p for p in self.predictions if p["timestamp"] > cutoff]
        
        if not recent:
            return {}
        
        latencies = [p["latency_ms"] for p in recent]
        confidences = [p["top_confidence"] for p in recent]
        
        return {
            "total_predictions": len(recent),
            "error_rate": len([p for p in recent if p["error"]]) / len(recent),
            "latency_p50": np.percentile(latencies, 50),
            "latency_p95": np.percentile(latencies, 95),
            "latency_p99": np.percentile(latencies, 99),
            "avg_confidence": np.mean(confidences),
            "low_confidence_rate": len([c for c in confidences if c < 0.5]) / len(confidences)
        }
```

**Alerting**:
```python
class AlertManager:
    def __init__(self, slack_webhook: str):
        self.slack_webhook = slack_webhook
    
    def check_and_alert(self, metrics: Dict):
        """Check metrics and send alerts if thresholds exceeded."""
        alerts = []
        
        # High error rate
        if metrics["error_rate"] > 0.05:  # >5%
            alerts.append(f"⚠️ High error rate: {metrics['error_rate']:.1%}")
        
        # High latency
        if metrics["latency_p95"] > 200:  # >200ms
            alerts.append(f"⚠️ High latency: {metrics['latency_p95']:.0f}ms (p95)")
        
        # Low confidence
        if metrics["low_confidence_rate"] > 0.30:  # >30%
            alerts.append(f"⚠️ High low-confidence rate: {metrics['low_confidence_rate']:.1%}")
        
        # Send alerts
        if alerts:
            self.send_slack_alert("\n".join(alerts))
    
    def send_slack_alert(self, message: str):
        """Send alert to Slack."""
        import requests
        
        requests.post(self.slack_webhook, json={
            "text": f"🚨 ML Model Alert\n{message}"
        })
```

### Health Checks

**Model Health**:
```python
def check_model_health():
    """Perform health check on production model."""
    checks = {
        "model_loaded": False,
        "checkpoint_valid": False,
        "inference_working": False,
        "latency_acceptable": False
    }
    
    try:
        # Check model loaded
        if model is not None:
            checks["model_loaded"] = True
        
        # Check checkpoint valid
        checkpoint_path = get_production_checkpoint_path()
        if checkpoint_path.exists():
            checks["checkpoint_valid"] = True
        
        # Check inference working
        test_text = "Machine learning test"
        start = time.time()
        predictions = model.predict(test_text)
        latency = (time.time() - start) * 1000
        
        if predictions:
            checks["inference_working"] = True
        
        if latency < 200:
            checks["latency_acceptable"] = True
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
    
    return checks

# Expose health check endpoint
@app.get("/health/ml")
def ml_health_check():
    checks = check_model_health()
    
    if all(checks.values()):
        return {"status": "healthy", "checks": checks}
    else:
        return {"status": "unhealthy", "checks": checks}, 503
```

### Logging

**Structured Logging**:
```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Configure logger
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

**Log Aggregation**:
```python
# Example: Send logs to centralized logging service
import logging.handlers

syslog_handler = logging.handlers.SysLogHandler(
    address=("logs.example.com", 514)
)
logger.addHandler(syslog_handler)
```


## Deployment Strategy

### Deployment Pipeline

```
┌─────────────┐
│   Training  │
│  Complete   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Evaluate   │
│  on Test    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Create    │
│   Version   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Staging   │
│   Deploy    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  A/B Test   │
│  (7 days)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Promote to │
│ Production  │
└─────────────┘
```

### Staging Environment

**Purpose**: Test new models before production deployment

**Configuration**:
```yaml
staging:
  model_version: "v1.2.0-rc1"
  traffic: "internal_only"
  monitoring: "verbose"
  rollback_enabled: true
  test_suite: "full"
```

**Validation Steps**:
1. Load model in staging environment
2. Run full test suite
3. Perform manual testing
4. Check performance metrics
5. Verify backward compatibility
6. Test rollback procedure

### Production Deployment

**Blue-Green Deployment**:
```python
class BlueGreenDeployment:
    def __init__(self):
        self.blue_version = "v1.1.0"  # Current production
        self.green_version = "v1.2.0"  # New version
        self.active = "blue"
    
    def deploy_green(self):
        """Deploy new version to green environment."""
        logger.info(f"Deploying {self.green_version} to green...")
        load_model(self.green_version, environment="green")
        
        # Warm up model
        self.warmup_model("green")
        
        # Health check
        if not self.health_check("green"):
            raise Exception("Green environment health check failed")
    
    def switch_to_green(self):
        """Switch traffic to green environment."""
        logger.info("Switching traffic to green...")
        self.active = "green"
        
        # Update load balancer
        update_load_balancer(target="green")
        
        # Monitor for issues
        time.sleep(60)
        
        if self.detect_issues():
            logger.error("Issues detected, rolling back...")
            self.rollback()
    
    def rollback(self):
        """Rollback to blue environment."""
        logger.warning("Rolling back to blue...")
        self.active = "blue"
        update_load_balancer(target="blue")
```

**Canary Deployment**:
```python
class CanaryDeployment:
    def __init__(self):
        self.production_version = "v1.1.0"
        self.canary_version = "v1.2.0"
        self.canary_percentage = 0
    
    def gradual_rollout(self):
        """Gradually increase canary traffic."""
        stages = [5, 10, 25, 50, 100]
        
        for percentage in stages:
            logger.info(f"Increasing canary to {percentage}%...")
            self.canary_percentage = percentage
            update_traffic_split(canary=percentage)
            
            # Monitor for 1 hour
            time.sleep(3600)
            
            # Check metrics
            if not self.metrics_acceptable():
                logger.error("Metrics degraded, rolling back...")
                self.rollback()
                return False
        
        logger.info("Canary rollout complete!")
        return True
    
    def metrics_acceptable(self) -> bool:
        """Check if canary metrics are acceptable."""
        canary_metrics = get_metrics(version=self.canary_version)
        prod_metrics = get_metrics(version=self.production_version)
        
        # Compare error rates
        if canary_metrics["error_rate"] > prod_metrics["error_rate"] * 1.5:
            return False
        
        # Compare latencies
        if canary_metrics["latency_p95"] > prod_metrics["latency_p95"] * 1.2:
            return False
        
        return True
```

### Rollback Procedure

**Automatic Rollback**:
```python
def monitor_and_rollback():
    """Monitor production and rollback if issues detected."""
    while True:
        metrics = get_production_metrics()
        
        # Check error rate
        if metrics["error_rate"] > 0.10:  # >10%
            logger.error("High error rate detected, rolling back...")
            rollback_to_previous_version()
            send_alert("Automatic rollback triggered: high error rate")
            break
        
        # Check latency
        if metrics["latency_p95"] > 500:  # >500ms
            logger.error("High latency detected, rolling back...")
            rollback_to_previous_version()
            send_alert("Automatic rollback triggered: high latency")
            break
        
        time.sleep(60)  # Check every minute
```

**Manual Rollback**:
```bash
# Rollback to previous version
python scripts/deployment/rollback.py --version v1.1.0

# Rollback to specific version
python scripts/deployment/rollback.py --version v1.0.0 --reason "Critical bug"
```

### Deployment Checklist

**Pre-Deployment**:
- [ ] Model trained and evaluated
- [ ] Test accuracy ≥90%
- [ ] Model size <500MB
- [ ] All tests passing
- [ ] Staging deployment successful
- [ ] Documentation updated
- [ ] Rollback plan prepared

**Deployment**:
- [ ] Create model version
- [ ] Deploy to staging
- [ ] Run smoke tests
- [ ] Deploy to production (canary)
- [ ] Monitor metrics
- [ ] Gradually increase traffic
- [ ] Update production symlink

**Post-Deployment**:
- [ ] Verify production metrics
- [ ] Check error logs
- [ ] Monitor for 24 hours
- [ ] Update version registry
- [ ] Archive old versions
- [ ] Send deployment notification


## Documentation and Training

### Developer Documentation

**Training Guide** (`docs/MODEL_TRAINING.md`):
```markdown
# Model Training Guide

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Collect dataset:
   ```bash
   python backend/scripts/dataset_acquisition/arxiv_collector.py
   ```

3. Preprocess data:
   ```bash
   python backend/scripts/dataset_acquisition/dataset_preprocessor.py
   ```

4. Train model:
   ```bash
   python backend/scripts/training/train_classification.py
   ```

## Detailed Steps

### 1. Dataset Collection

Collect 10,000 arXiv papers from 10 CS categories:

```bash
python backend/scripts/dataset_acquisition/arxiv_collector.py \
  --num-papers 10000 \
  --output data/processed/arxiv_classification.json
```

**Time**: ~1 hour (rate limited)
**Output**: `data/processed/arxiv_classification.json` (~500MB)

### 2. Data Preprocessing

Clean and split dataset:

```bash
python backend/scripts/dataset_acquisition/dataset_preprocessor.py \
  --input data/processed/arxiv_classification.json \
  --output data/processed/arxiv_classification_clean.json \
  --min-words 50
```

**Time**: ~5 minutes
**Output**: 
- `data/processed/arxiv_classification_clean.json`
- `data/splits/arxiv_classification/train.json`
- `data/splits/arxiv_classification/val.json`
- `data/splits/arxiv_classification/test.json`

### 3. Model Training

Train DistilBERT classifier:

```bash
python backend/scripts/training/train_classification.py \
  --data-dir data/splits/arxiv_classification \
  --output-dir models/classification/arxiv_v1.0.0 \
  --epochs 3 \
  --batch-size 16 \
  --learning-rate 2e-5
```

**Time**: ~2 hours on V100 GPU
**Output**: `models/classification/arxiv_v1.0.0/` (268MB)

### 4. Evaluation

Evaluate on test set:

```bash
python backend/scripts/evaluation/evaluate_models.py \
  --model-dir models/classification/arxiv_v1.0.0 \
  --test-data data/splits/arxiv_classification/test.json
```

**Output**: `models/classification/arxiv_v1.0.0/test_results.json`

## Hyperparameter Tuning

Run automated hyperparameter search:

```bash
python backend/scripts/training/hyperparameter_search.py \
  --data-dir data/splits/arxiv_classification \
  --n-trials 20 \
  --timeout 28800
```

**Time**: ~8 hours
**Output**: `models/classification/hp_search/best_params.json`

## Troubleshooting

### Out of Memory

Reduce batch size:
```bash
python backend/scripts/training/train_classification.py --batch-size 8
```

### Slow Training

Use GPU:
```bash
# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"

# Enable mixed precision
python backend/scripts/training/train_classification.py --fp16
```

### Low Accuracy

- Increase training epochs: `--epochs 5`
- Increase dataset size: `--num-papers 20000`
- Try different learning rate: `--learning-rate 3e-5`
```

### API Documentation

**ArxivCollector API**:
```python
"""
ArxivCollector - Fetch papers from arXiv API

Example:
    >>> collector = ArxivCollector(output_dir="data/raw/arxiv")
    >>> papers = collector.collect_papers_by_category("cs.AI", max_results=1000)
    >>> print(f"Collected {len(papers)} papers")

Args:
    output_dir (str): Directory to save collected papers
    
Methods:
    collect_papers_by_category(category, max_results, start_date):
        Collect papers from specific arXiv category
        
    collect_balanced_dataset(categories, papers_per_category):
        Collect balanced dataset across multiple categories
        
    create_classification_dataset(num_papers, output_file):
        Create complete classification dataset
"""
```

### Runbook

**Production Incident Response**:

**High Error Rate**:
1. Check model health: `curl http://api/health/ml`
2. Check recent deployments: `git log --oneline -10`
3. Check error logs: `tail -f logs/ml_service.log`
4. Rollback if needed: `python scripts/deployment/rollback.py`

**High Latency**:
1. Check GPU utilization: `nvidia-smi`
2. Check batch size: Review recent config changes
3. Check model size: `ls -lh models/production/`
4. Scale horizontally: Add more replicas

**Low Confidence Predictions**:
1. Check data drift: Compare recent inputs to training data
2. Check model version: Verify correct model loaded
3. Consider retraining: Check last training date


## Future Enhancements

### Phase 2: Additional Data Sources

**PubMed Integration**:
- Collect biomedical papers from PubMed
- Expand to 20+ categories (CS + Bio)
- Cross-domain classification

**Semantic Scholar Integration**:
- Collect citation data
- Use citation networks for classification
- Incorporate paper influence metrics

### Phase 3: Advanced Training Techniques

**Curriculum Learning**:
- Start with easy examples (high confidence)
- Gradually introduce harder examples
- Improve convergence speed

**Multi-Task Learning**:
- Joint training for classification + summarization
- Shared representations across tasks
- Better generalization

**Few-Shot Learning**:
- Adapt to new categories with few examples
- Meta-learning approaches
- Faster deployment of new categories

### Phase 4: Model Improvements

**Larger Models**:
- BERT-base (110M parameters)
- RoBERTa-base (125M parameters)
- DeBERTa-base (140M parameters)

**Ensemble Methods**:
- Combine multiple models
- Voting or stacking
- Improved accuracy (+2-3%)

**Domain Adaptation**:
- Pre-train on scientific text
- SciBERT, BioBERT
- Better performance on academic papers

### Phase 5: Infrastructure Improvements

**Distributed Training**:
- Multi-GPU training (PyTorch DDP)
- Faster training (4x speedup with 4 GPUs)
- Larger batch sizes

**Model Serving**:
- TorchServe or TensorFlow Serving
- Optimized inference
- Auto-scaling

**MLOps Platform**:
- MLflow for experiment tracking
- Kubeflow for pipeline orchestration
- Automated CI/CD for models

### Phase 6: Advanced Features

**Explainability**:
- LIME or SHAP for predictions
- Attention visualization
- Feature importance

**Active Learning at Scale**:
- Automated uncertainty sampling
- Human-in-the-loop labeling
- Continuous improvement

**Federated Learning**:
- Train on distributed data
- Privacy-preserving
- Collaborative learning

## Success Metrics

### Training Metrics

**Dataset Quality**:
- ✅ ≥10,000 samples collected
- ✅ <5% duplicates after deduplication
- ✅ ≥50 words per abstract
- ✅ Balanced classes (±10%)

**Model Performance**:
- ✅ ≥90% validation accuracy
- ✅ ≥88% test accuracy
- ✅ ≥0.85 F1 score (macro)
- ✅ <500MB model size

**Training Efficiency**:
- ✅ <4 hours training time (GPU)
- ✅ <10% memory overhead
- ✅ Successful checkpoint saving
- ✅ Reproducible results (fixed seed)

### Production Metrics

**Inference Performance**:
- ✅ <100ms latency (p95)
- ✅ <5% error rate
- ✅ >95% uptime
- ✅ <1GB memory per replica

**Model Quality**:
- ✅ >85% user satisfaction
- ✅ <10% low-confidence predictions
- ✅ Consistent with human labels (>90% agreement)

**Operational Metrics**:
- ✅ Automated retraining working
- ✅ <1 hour deployment time
- ✅ Zero-downtime deployments
- ✅ Successful rollbacks (if needed)

## Conclusion

This design document outlines a comprehensive production ML training system for Neo Alexandria. The system provides:

1. **Automated Data Collection**: Fetch real-world papers from arXiv with rate limiting and error handling
2. **Robust Preprocessing**: Clean, deduplicate, and validate data for high-quality training
3. **Efficient Training**: GPU-optimized training with DistilBERT achieving ≥90% accuracy
4. **Hyperparameter Tuning**: Automated search for optimal configurations
5. **Model Versioning**: Semantic versioning with metadata tracking
6. **A/B Testing**: Compare model versions before production deployment
7. **Automated Retraining**: Weekly checks for new data and automatic retraining
8. **Production Deployment**: Blue-green and canary deployments with automatic rollback

The system is designed to be:
- **Reproducible**: Fixed random seeds, version control, documented procedures
- **Scalable**: Horizontal and vertical scaling options
- **Maintainable**: Clear code structure, comprehensive documentation
- **Reliable**: Error handling, monitoring, alerting, rollback procedures
- **Secure**: API key management, data sanitization, access control

Next steps: Proceed to implementation tasks in `tasks.md`.
