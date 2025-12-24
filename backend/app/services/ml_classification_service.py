"""
Neo Alexandria 2.0 - ML Classification Service (Phase 8.5)

This module implements transformer-based classification using fine-tuned BERT/DistilBERT models.
It provides methods for model training, inference, semi-supervised learning, and active learning.

Related files:
- app/services/taxonomy_service.py: Taxonomy management and resource classification
- app/database/models.py: TaxonomyNode and ResourceTaxonomy models
- app/routers/taxonomy.py: API endpoints for classification operations
- app/schemas/taxonomy.py: Pydantic schemas for API validation

Features:
- Transformer-based multi-label classification
- Fine-tuning with Hugging Face Trainer API
- Semi-supervised learning with pseudo-labeling
- Active learning with uncertainty sampling
- Lazy model loading for efficiency
- GPU acceleration support
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

from sqlalchemy.orm import Session
from ..domain.classification import (
    ClassificationResult, 
    ClassificationPrediction,
    TrainingExample,
    TrainingResult
)

# ML imports will be lazy-loaded
# import torch
# from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
# from sklearn.metrics import f1_score, precision_score, recall_score

logger = logging.getLogger(__name__)

# Model Configuration Constants
DEFAULT_MODEL_NAME: str = "distilbert-base-uncased"
DEFAULT_MODEL_VERSION: str = "v1.0"
MAX_TOKEN_LENGTH: int = 512
DEFAULT_NUM_LABELS: int = 2

# Training Hyperparameters
DEFAULT_EPOCHS: int = 3
DEFAULT_BATCH_SIZE: int = 16
GPU_BATCH_SIZE: int = 32
CPU_BATCH_SIZE: int = 8
DEFAULT_LEARNING_RATE: float = 2e-5
SEMI_SUPERVISED_LEARNING_RATE: float = 1e-5
SEMI_SUPERVISED_EPOCHS: int = 1
WEIGHT_DECAY: float = 0.01
VALIDATION_SPLIT_RATIO: float = 0.2
RANDOM_SEED: int = 42

# Prediction Thresholds
BINARY_PREDICTION_THRESHOLD: float = 0.5
HIGH_CONFIDENCE_THRESHOLD: float = 0.8
SEMI_SUPERVISED_CONFIDENCE_THRESHOLD: float = 0.9
DEFAULT_TOP_K: int = 5
UNCERTAINTY_TOP_K: int = 10

# Active Learning Constants
DEFAULT_UNCERTAINTY_LIMIT: int = 100
UNCERTAINTY_EPSILON: float = 1e-10
RETRAINING_THRESHOLD: int = 100

# Trainer Configuration
LOGGING_STEPS: int = 10
SAVE_TOTAL_LIMIT: int = 2

# Monitoring Constants
DEFAULT_METRICS_WINDOW_MINUTES: int = 60


class MLClassificationService:
    """
    Handles ML-based classification using transformer models.
    
    This service provides methods for fine-tuning BERT/DistilBERT models on taxonomy data,
    predicting classifications with confidence scores, semi-supervised learning with
    pseudo-labeling, and active learning workflows for continuous improvement.
    
    The service uses lazy loading for models to avoid loading them until needed,
    which improves startup time and memory efficiency.
    """
    
    def __init__(
        self,
        db: Session,
        model_name: str = DEFAULT_MODEL_NAME,
        model_version: Optional[str] = None,
        version: Optional[str] = None
    ) -> None:
        """
        Initialize the ML classification service.
        
        Args:
            db: SQLAlchemy database session
            model_name: Base model name from Hugging Face (default: distilbert-base-uncased)
            model_version: Model version identifier for checkpoints (default: v1.0) - DEPRECATED, use 'version'
            version: Optional specific version to load (e.g., "v1.0.0"). If not specified, loads production version.
        
        Requirements: 15.1
        """
        self.db = db
        self.model_name = model_name
        
        # Handle version parameter (new) vs model_version (legacy)
        # If version is specified, use it; otherwise fall back to model_version or default
        if version is not None:
            self.model_version = version
        elif model_version is not None:
            self.model_version = model_version
        else:
            self.model_version = None  # Will load production version
        
        # Lazy loading: Initialize as None, load on first use
        self.model = None
        self.tokenizer = None
        
        # Label mappings: taxonomy_node_id <-> model label index
        self.id_to_label: Dict[int, str] = {}  # {0: "node_id_1", 1: "node_id_2", ...}
        self.label_to_id: Dict[str, int] = {}  # {"node_id_1": 0, "node_id_2": 1, ...}
        
        # Initialize prediction monitor for tracking predictions
        from ..ml_monitoring.prediction_monitor import PredictionMonitor
        self.monitor = PredictionMonitor()
        logger.info("PredictionMonitor initialized")
        
        # Model checkpoint directory
        # If version specified, use version path; otherwise use default
        if self.model_version:
            # Try multiple possible locations for the versioned checkpoint
            possible_paths = [
                Path("models") / "classification" / f"arxiv_{self.model_version}",  # Run from project root
                Path("backend") / "models" / "classification" / f"arxiv_{self.model_version}",  # Run from project root
                Path(__file__).parent.parent.parent / "models" / "classification" / f"arxiv_{self.model_version}",  # Relative to this file
            ]
        else:
            # No version specified - will try production symlink in _load_model
            possible_paths = [
                Path("models") / "classification",  # Run from project root
                Path("backend") / "models" / "classification",  # Run from project root
                Path(__file__).parent.parent.parent / "models" / "classification",  # Relative to this file
            ]
        
        # Find the first path with actual model files (check for config.json)
        self.checkpoint_dir = None
        for path in possible_paths:
            if path.exists() and (path / "config.json").exists():
                self.checkpoint_dir = path
                logger.info(f"Found checkpoint directory with model files at: {path}")
                break
        
        # If no existing checkpoint found, use the first path as default
        if self.checkpoint_dir is None:
            self.checkpoint_dir = possible_paths[0]
            logger.info(f"No existing checkpoint found, will use: {self.checkpoint_dir}")
        
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            f"MLClassificationService initialized with model={model_name}, "
            f"version={self.model_version or 'production'}, checkpoint_dir={self.checkpoint_dir}"
        )

    def _load_model(self) -> None:
        """
        Load model and tokenizer with lazy loading.
        
        This method is called automatically on first prediction/training request.
        Lazy loading improves startup time and memory efficiency.
        
        Raises:
            ImportError: If required ML libraries not installed
            Exception: If model loading fails
        
        Requirements: 15.1, 15.2
        """
        # Skip if already loaded
        if self.model is not None and self.tokenizer is not None:
            logger.debug("Model already loaded, skipping")
            return
        
        logger.info("Loading model and tokenizer...")
        
        try:
            self._import_ml_libraries()
            self._load_tokenizer()
            checkpoint_to_load, loaded_version = self._determine_checkpoint_path()
            self._load_model_from_checkpoint(checkpoint_to_load, loaded_version)
            self._move_model_to_device()
            self.model.eval()
            logger.info(f"Model set to evaluation mode. Loaded version: {loaded_version}")
            
        except ImportError as e:
            logger.error(f"Failed to import ML libraries: {e}")
            raise ImportError(
                "Required ML libraries not installed. "
                "Please install: pip install transformers torch scikit-learn"
            ) from e
        
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise Exception(f"Model loading failed: {e}") from e
    
    def _import_ml_libraries(self) -> None:
        """
        Import required ML libraries (lazy import).
        
        This method imports PyTorch and Transformers libraries only when needed,
        improving startup time and allowing the service to run without ML dependencies
        for non-ML operations.
        
        Raises:
            ImportError: If required ML libraries are not installed
        
        Requirements: 15.1, 15.2
        """
    
    def _load_tokenizer(self) -> None:
        """
        Load tokenizer from Hugging Face.
        
        Loads the tokenizer corresponding to the base model name. The tokenizer
        is used to convert text into token IDs that the model can process.
        
        Side Effects:
            - Sets self.tokenizer to the loaded tokenizer instance
            - Downloads tokenizer files if not cached locally
        
        Requirements: 15.1, 15.2
        """
        from transformers import AutoTokenizer
        logger.info(f"Loading tokenizer: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
    
    def _determine_checkpoint_path(self) -> Tuple[Optional[Path], Optional[str]]:
        """
        Determine which checkpoint directory to use.
        
        This method implements the checkpoint loading priority:
        1. Production symlink (models/classification/production)
        2. Specified version directory (models/classification/arxiv_v1.0.0)
        3. None (will load base model from Hugging Face)
        
        Returns:
            Tuple of (checkpoint_path, version_name) where:
                - checkpoint_path: Path to checkpoint directory or None
                - version_name: Version identifier string or None
        
        Requirements: 15.1, 15.2
        """
        # Try production symlink first
        production_path = self.checkpoint_dir.parent / "production"
        if production_path.exists() and (production_path / "config.json").exists():
            logger.info(f"Found production model at: {production_path}")
            return production_path, "production"
        
        # Fall back to specified version directory
        if self.checkpoint_dir.exists() and (self.checkpoint_dir / "config.json").exists():
            logger.info(f"Using specified version directory: {self.checkpoint_dir}")
            return self.checkpoint_dir, self.model_version
        
        return None, None
    
    def _load_model_from_checkpoint(
        self, 
        checkpoint_to_load: Optional[Path], 
        loaded_version: Optional[str]
    ) -> None:
        """
        Load model from checkpoint or base model.
        
        This method attempts to load a fine-tuned model from a checkpoint directory.
        If the checkpoint doesn't exist or loading fails, it falls back to loading
        the base pre-trained model from Hugging Face.
        
        Args:
            checkpoint_to_load: Path to checkpoint directory or None for base model
            loaded_version: Version name for logging purposes
        
        Side Effects:
            - Sets self.model to the loaded model instance
            - May set self.id_to_label and self.label_to_id if checkpoint has label mapping
        
        Requirements: 15.1, 15.2
        """
        
        if checkpoint_to_load:
            self._try_load_checkpoint(checkpoint_to_load, loaded_version)
        
        # Fall back to base model if checkpoint loading failed or doesn't exist
        if self.model is None:
            self._load_base_model()
    
    def _try_load_checkpoint(self, checkpoint_path: Path, version: str) -> None:
        """
        Attempt to load model from checkpoint directory.
        
        This method tries to load a fine-tuned model from a checkpoint directory.
        It supports both PyTorch (.bin) and SafeTensors formats. If loading fails,
        it sets self.model to None to trigger fallback to base model.
        
        Args:
            checkpoint_path: Path to checkpoint directory containing model files
            version: Version name for logging purposes
        
        Side Effects:
            - Sets self.model to loaded model or None if loading fails
            - Sets self.id_to_label and self.label_to_id from label_map.json
        
        Requirements: 15.1, 15.2
        """
        from transformers import AutoModelForSequenceClassification
        
        checkpoint_path_bin = checkpoint_path / "pytorch_model.bin"
        checkpoint_path_safetensors = checkpoint_path / "model.safetensors"
        label_map_path = checkpoint_path / "label_map.json"
        config_path = checkpoint_path / "config.json"
        
        # Check if checkpoint exists (either format)
        checkpoint_exists = checkpoint_path_bin.exists() or checkpoint_path_safetensors.exists()
        
        if checkpoint_exists and config_path.exists():
            logger.info(f"Loading fine-tuned model from checkpoint: {checkpoint_path}")
            try:
                self._load_label_mapping(label_map_path)
                
                # Load model from checkpoint directory
                num_labels = len(self.id_to_label) if self.id_to_label else DEFAULT_NUM_LABELS
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    str(checkpoint_path),
                    num_labels=num_labels,
                    problem_type="multi_label_classification",
                    local_files_only=True
                )
                logger.info(f"Successfully loaded model version: {version}")
                
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}. Falling back to base model.")
                self.model = None
                self.id_to_label = {}
                self.label_to_id = {}
    
    def _load_label_mapping(self, label_map_path: Path) -> None:
        """
        Load label mapping from JSON file.
        
        The label mapping file contains bidirectional mappings between model
        label indices (0, 1, 2, ...) and taxonomy node IDs (strings).
        
        Args:
            label_map_path: Path to label_map.json file
        
        Side Effects:
            - Sets self.id_to_label: Dict[int, str] mapping indices to taxonomy IDs
            - Sets self.label_to_id: Dict[str, int] mapping taxonomy IDs to indices
        
        Requirements: 15.1, 15.2
        """
        if label_map_path.exists():
            with open(label_map_path, 'r') as f:
                label_data = json.load(f)
                self.id_to_label = {int(k): v for k, v in label_data['id_to_label'].items()}
                self.label_to_id = label_data['label_to_id']
            logger.info(f"Loaded label mapping with {len(self.id_to_label)} labels")
        else:
            logger.warning(f"Label map not found at {label_map_path}")
    
    def _load_base_model(self) -> None:
        """
        Load base pre-trained model from Hugging Face.
        
        This method loads the base pre-trained model (e.g., DistilBERT) without
        any fine-tuning. This is used when no checkpoint is available or when
        checkpoint loading fails.
        
        Side Effects:
            - Sets self.model to the base pre-trained model
            - Downloads model files if not cached locally
        
        Requirements: 15.1, 15.2
        """
        from transformers import AutoModelForSequenceClassification
        
        logger.info(f"Loading base pre-trained model: {self.model_name}")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=DEFAULT_NUM_LABELS,
            problem_type="multi_label_classification"
        )
        logger.info("Successfully loaded base model")
    
    def _move_model_to_device(self) -> None:
        """
        Move model to GPU if available, otherwise use CPU.
        
        This method checks for CUDA availability and moves the model to the
        appropriate device. GPU acceleration significantly improves inference
        and training speed.
        
        Side Effects:
            - Moves self.model to GPU or CPU
            - Sets self.device to torch.device("cuda") or torch.device("cpu")
        
        Requirements: 15.1, 15.2
        """
        import torch
        
        if torch.cuda.is_available():
            logger.info("CUDA available, moving model to GPU")
            self.model = self.model.cuda()
            self.device = torch.device("cuda")
        else:
            logger.info("CUDA not available, using CPU")
            self.device = torch.device("cpu")

    def _compute_metrics(self, eval_pred: Any) -> Dict[str, float]:
        """
        Compute evaluation metrics for multi-label classification.
        
        This callback is used by Hugging Face Trainer during evaluation.
        It computes F1 score (macro average), precision, and recall.
        
        Args:
            eval_pred: EvalPrediction object with predictions and labels
        
        Returns:
            Dictionary with metrics (f1, precision, recall)
        
        Requirements: 2.2, 2.3, 8.4, 10.1
        """
        
        logits, labels = eval_pred
        predictions = self._convert_logits_to_predictions(logits)
        metrics = self._calculate_classification_metrics(labels, predictions)
        
        logger.info(
            f"Evaluation metrics - F1: {metrics['f1']:.4f}, "
            f"Precision: {metrics['precision']:.4f}, Recall: {metrics['recall']:.4f}"
        )
        
        return metrics
    
    def _convert_logits_to_predictions(self, logits: Any) -> Any:
        """
        Convert model logits to binary predictions.
        
        Applies sigmoid activation to convert logits to probabilities, then
        thresholds at BINARY_PREDICTION_THRESHOLD (0.5) to get binary predictions.
        
        Args:
            logits: Model output logits (before sigmoid), shape (batch_size, num_labels)
        
        Returns:
            Binary predictions (0 or 1) after sigmoid and thresholding,
            shape (batch_size, num_labels)
        
        Requirements: 2.2, 2.3, 10.2
        """
        import numpy as np
        
        # Apply sigmoid to get probabilities
        predictions = 1 / (1 + np.exp(-logits))
        
        # Threshold at BINARY_PREDICTION_THRESHOLD for binary predictions
        return (predictions > BINARY_PREDICTION_THRESHOLD).astype(int)
    
    def _calculate_classification_metrics(self, labels: Any, predictions: Any) -> Dict[str, float]:
        """
        Calculate F1, precision, and recall metrics.
        
        Uses macro averaging which treats all labels equally, regardless of
        their frequency in the dataset. This is appropriate for multi-label
        classification where we care about performance across all classes.
        
        Args:
            labels: Ground truth multi-hot encoded labels, shape (batch_size, num_labels)
            predictions: Binary predictions, shape (batch_size, num_labels)
        
        Returns:
            Dictionary with f1, precision, and recall scores (all floats 0.0-1.0)
        
        Requirements: 2.2, 2.3, 8.4, 10.1
        """
        from sklearn.metrics import f1_score, precision_score, recall_score
        
        # Compute metrics with macro averaging (treats all labels equally)
        f1 = f1_score(labels, predictions, average='macro', zero_division=0)
        precision = precision_score(labels, predictions, average='macro', zero_division=0)
        recall = recall_score(labels, predictions, average='macro', zero_division=0)
        
        return {
            'f1': f1,
            'precision': precision,
            'recall': recall
        }

    def fine_tune(
        self,
        labeled_data: List[Tuple[str, List[str]]],
        unlabeled_data: Optional[List[str]] = None,
        epochs: int = DEFAULT_EPOCHS,
        batch_size: int = DEFAULT_BATCH_SIZE,
        learning_rate: float = DEFAULT_LEARNING_RATE
    ) -> Dict[str, float]:
        """
        Fine-tune BERT model on labeled data with optional semi-supervised learning.
        
        Args:
            labeled_data: List of (text, [taxonomy_node_ids]) tuples
            unlabeled_data: Optional list of unlabeled texts for semi-supervised learning
            epochs: Number of training epochs (default: 3)
            batch_size: Training batch size (default: 16)
            learning_rate: Learning rate for optimizer (default: 2e-5)
        
        Returns:
            Dictionary with evaluation metrics (F1, precision, recall)
        
        Raises:
            ValueError: If labeled_data is empty or invalid
            ImportError: If required ML libraries not installed
        
        Requirements: 2.2, 2.3, 2.7, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 14.2, 14.3
        """
        logger.info(f"Starting fine-tuning with {len(labeled_data)} labeled examples")
        
        if not labeled_data:
            raise ValueError("labeled_data cannot be empty")
        
        # Build label mapping and prepare data
        num_labels = self._build_label_mapping(labeled_data)
        texts, labels = self._convert_to_multihot_encoding(labeled_data, num_labels)
        
        # Split and tokenize data
        train_texts, val_texts, train_labels, val_labels = self._split_train_validation(texts, labels)
        train_encodings, val_encodings = self._tokenize_texts(train_texts, val_texts)
        
        # Create datasets and initialize model
        train_dataset, val_dataset = self._create_datasets(train_encodings, val_encodings, train_labels, val_labels)
        self._initialize_model_for_training(num_labels)
        
        # Train model
        trainer = self._configure_trainer(train_dataset, val_dataset, epochs, batch_size, learning_rate)
        eval_metrics = self._train_model(trainer)
        
        # Semi-supervised learning if unlabeled data provided
        if unlabeled_data and len(unlabeled_data) > 0:
            eval_metrics = self._perform_semi_supervised_learning(labeled_data, unlabeled_data, eval_metrics)
        
        # Save model and return metrics
        self._save_model_and_artifacts()
        return self._extract_metrics(eval_metrics)
    
    def _build_label_mapping(self, labeled_data: List[Tuple[str, List[str]]]) -> int:
        """
        Build label mapping from unique taxonomy IDs.
        
        Creates bidirectional mappings between model label indices (0, 1, 2, ...)
        and taxonomy node IDs (strings). The mapping is sorted alphabetically
        for consistency across training runs.
        
        Args:
            labeled_data: List of (text, [taxonomy_node_ids]) tuples
        
        Returns:
            Number of unique labels found in the dataset
        
        Side Effects:
            - Sets self.id_to_label: Dict[int, str]
            - Sets self.label_to_id: Dict[str, int]
        
        Requirements: 2.2, 2.3, 8.4, 10.1
        """
        logger.info("Building label mapping from taxonomy IDs...")
        all_taxonomy_ids = set()
        for text, taxonomy_ids in labeled_data:
            all_taxonomy_ids.update(taxonomy_ids)
        
        # Sort for consistent ordering
        sorted_taxonomy_ids = sorted(all_taxonomy_ids)
        
        # Create bidirectional mappings
        self.id_to_label = {i: taxonomy_id for i, taxonomy_id in enumerate(sorted_taxonomy_ids)}
        self.label_to_id = {taxonomy_id: i for i, taxonomy_id in enumerate(sorted_taxonomy_ids)}
        
        num_labels = len(self.id_to_label)
        logger.info(f"Built label mapping with {num_labels} unique taxonomy nodes")
        return num_labels
    
    def _convert_to_multihot_encoding(
        self, 
        labeled_data: List[Tuple[str, List[str]]], 
        num_labels: int
    ) -> Tuple[List[str], Any]:
        """
        Convert multi-label data to multi-hot encoding.
        
        Multi-hot encoding represents multiple labels as a binary vector where
        1 indicates the label is present and 0 indicates it's absent.
        Example: [0, 1, 0, 1, 0] means labels at indices 1 and 3 are present.
        
        Args:
            labeled_data: List of (text, [taxonomy_node_ids]) tuples
            num_labels: Number of unique labels in the label mapping
        
        Returns:
            Tuple of (texts, multi-hot encoded labels) where:
                - texts: List of text strings
                - labels: numpy array of shape (num_examples, num_labels)
        
        Requirements: 2.2, 2.3, 8.4, 10.1
        """
        import numpy as np
        
        logger.info("Converting to multi-hot encoding...")
        texts = []
        labels = []
        
        for text, taxonomy_ids in labeled_data:
            texts.append(text)
            
            # Create multi-hot vector
            multi_hot = np.zeros(num_labels, dtype=np.float32)
            for taxonomy_id in taxonomy_ids:
                if taxonomy_id in self.label_to_id:
                    multi_hot[self.label_to_id[taxonomy_id]] = 1.0
            
            labels.append(multi_hot)
        
        labels = np.array(labels)
        logger.info(f"Converted {len(texts)} examples to multi-hot encoding")
        return texts, labels
    
    def _split_train_validation(self, texts: List[str], labels: Any) -> Tuple[List[str], List[str], Any, Any]:
        """
        Split data into train and validation sets.
        
        Uses VALIDATION_SPLIT_RATIO (0.2) for 80/20 train/validation split.
        Random seed (RANDOM_SEED) ensures reproducibility across runs.
        
        Args:
            texts: List of text strings
            labels: Multi-hot encoded labels
        
        Returns:
            Tuple of (train_texts, val_texts, train_labels, val_labels)
        
        Requirements: 2.2, 2.3, 10.2
        """
        from sklearn.model_selection import train_test_split
        
        logger.info(f"Splitting train/validation ({int((1-VALIDATION_SPLIT_RATIO)*100)}/{int(VALIDATION_SPLIT_RATIO*100)})...")
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=VALIDATION_SPLIT_RATIO, random_state=RANDOM_SEED
        )
        logger.info(f"Train: {len(train_texts)} examples, Validation: {len(val_texts)} examples")
        return train_texts, val_texts, train_labels, val_labels
    
    def _tokenize_texts(self, train_texts: List[str], val_texts: List[str]) -> Tuple[Any, Any]:
        """
        Tokenize texts with maximum token length.
        
        Uses MAX_TOKEN_LENGTH (512) which is the maximum sequence length for
        most transformer models. Longer texts are truncated, shorter texts
        are padded to create uniform batch sizes.
        
        Args:
            train_texts: Training texts
            val_texts: Validation texts
        
        Returns:
            Tuple of (train_encodings, val_encodings) containing tokenized inputs
        
        Requirements: 2.2, 2.3, 10.2
        """
        from transformers import AutoTokenizer
        
        logger.info("Tokenizing texts...")
        if self.tokenizer is None:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        train_encodings = self.tokenizer(
            train_texts,
            truncation=True,
            padding=True,
            max_length=MAX_TOKEN_LENGTH,
            return_tensors='pt'
        )
        
        val_encodings = self.tokenizer(
            val_texts,
            truncation=True,
            padding=True,
            max_length=MAX_TOKEN_LENGTH,
            return_tensors='pt'
        )
        logger.info("Tokenization complete")
        return train_encodings, val_encodings
    
    def _create_datasets(self, train_encodings: Any, val_encodings: Any, train_labels: Any, val_labels: Any) -> Tuple[Any, Any]:
        """
        Create PyTorch datasets for training.
        
        Creates custom Dataset objects that combine tokenized inputs with labels
        in the format expected by Hugging Face Trainer.
        
        Args:
            train_encodings: Tokenized training texts
            val_encodings: Tokenized validation texts
            train_labels: Training labels (multi-hot encoded)
            val_labels: Validation labels (multi-hot encoded)
        
        Returns:
            Tuple of (train_dataset, val_dataset) as PyTorch Dataset objects
        
        Requirements: 2.2, 2.3, 8.4, 10.1
        """
        import torch
        from torch.utils.data import Dataset
        
        logger.info("Creating PyTorch datasets...")
        
        class MultiLabelDataset(Dataset):
            """Custom dataset for multi-label classification."""
            
            def __init__(self, encodings, labels):
                self.encodings = encodings
                self.labels = labels
            
            def __getitem__(self, idx):
                item = {key: val[idx] for key, val in self.encodings.items()}
                item['labels'] = torch.tensor(self.labels[idx], dtype=torch.float32)
                return item
            
            def __len__(self):
                return len(self.labels)
        
        train_dataset = MultiLabelDataset(train_encodings, train_labels)
        val_dataset = MultiLabelDataset(val_encodings, val_labels)
        logger.info("Datasets created")
        return train_dataset, val_dataset
    
    def _initialize_model_for_training(self, num_labels: int) -> None:
        """
        Initialize model with correct number of labels and move to device.
        
        Loads a fresh model from Hugging Face with the correct number of output
        labels for the current training task. Moves model to GPU if available.
        
        Args:
            num_labels: Number of classification labels (taxonomy nodes)
        
        Side Effects:
            - Sets self.model to a new model instance
            - Sets self.device to the appropriate device (GPU or CPU)
        
        Requirements: 2.2, 2.3, 8.4, 10.1
        """
        import torch
        from transformers import AutoModelForSequenceClassification
        
        logger.info(f"Initializing model with {num_labels} labels...")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=num_labels,
            problem_type="multi_label_classification"
        )
        
        # Move to GPU if available
        if torch.cuda.is_available():
            logger.info("Moving model to GPU")
            self.model = self.model.cuda()
            self.device = torch.device("cuda")
        else:
            logger.info("Using CPU")
            self.device = torch.device("cpu")
    
    def _configure_trainer(
        self, 
        train_dataset: Any, 
        val_dataset: Any, 
        epochs: int, 
        batch_size: int, 
        learning_rate: float
    ) -> Any:
        """
        Configure Hugging Face Trainer.
        
        Sets up the Trainer with appropriate hyperparameters and callbacks.
        Uses F1 score as the metric for selecting the best model checkpoint.
        
        Args:
            train_dataset: Training dataset
            val_dataset: Validation dataset
            epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate for optimizer
        
        Returns:
            Configured Trainer instance ready for training
        
        Requirements: 2.2, 2.3, 10.2
        """
        from transformers import Trainer, TrainingArguments
        
        logger.info("Configuring Trainer...")
        
        training_args = TrainingArguments(
            output_dir=str(self.checkpoint_dir),
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            weight_decay=WEIGHT_DECAY,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            logging_dir=str(self.checkpoint_dir / "logs"),
            logging_steps=LOGGING_STEPS,
            save_total_limit=SAVE_TOTAL_LIMIT,
            report_to="none",
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=self._compute_metrics
        )
        
        logger.info(f"Trainer configured with epochs={epochs}, batch_size={batch_size}, lr={learning_rate}")
        return trainer
    
    def _train_model(self, trainer: Any) -> Dict[str, Any]:
        """
        Train model and evaluate on validation set.
        
        Executes the training loop using Hugging Face Trainer, then evaluates
        the trained model on the validation set to get final metrics.
        
        Args:
            trainer: Configured Trainer instance
        
        Returns:
            Evaluation metrics dictionary containing f1, precision, recall, loss
        
        Requirements: 2.2, 2.3, 8.4, 10.1
        """
        logger.info("Starting training...")
        train_result = trainer.train()
        logger.info(f"Training complete. Loss: {train_result.training_loss:.4f}")
        
        logger.info("Evaluating on validation set...")
        eval_metrics = trainer.evaluate()
        logger.info(f"Validation metrics: {eval_metrics}")
        return eval_metrics
    
    def _perform_semi_supervised_learning(
        self, 
        labeled_data: List[Tuple[str, List[str]]], 
        unlabeled_data: List[str],
        eval_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform semi-supervised learning iteration.
        
        Uses pseudo-labeling to leverage unlabeled data. High-confidence
        predictions on unlabeled data are treated as pseudo-labels and
        added to the training set for an additional training iteration.
        
        Args:
            labeled_data: Original labeled data
            unlabeled_data: Unlabeled texts for pseudo-labeling
            eval_metrics: Current evaluation metrics
        
        Returns:
            Updated evaluation metrics after semi-supervised iteration
        
        Requirements: 3.1, 3.2, 3.3, 10.2
        """
        logger.info(f"Performing semi-supervised learning with {len(unlabeled_data)} unlabeled examples...")
        eval_metrics = self._semi_supervised_iteration(
            labeled_data=labeled_data,
            unlabeled_data=unlabeled_data,
            confidence_threshold=SEMI_SUPERVISED_CONFIDENCE_THRESHOLD
        )
        logger.info(f"Semi-supervised learning complete. Updated metrics: {eval_metrics}")
        return eval_metrics
    
    def _save_model_and_artifacts(self) -> None:
        """
        Save model, tokenizer, and label mapping to checkpoint directory.
        
        Saves all artifacts needed to reload the model later:
        - Model weights (pytorch_model.bin or model.safetensors)
        - Model configuration (config.json)
        - Tokenizer files
        - Label mapping (label_map.json)
        
        Side Effects:
            - Writes files to self.checkpoint_dir
        
        Requirements: 2.2, 2.3, 8.4, 10.1
        """
        logger.info("Saving model, tokenizer, and label mapping...")
        
        # Save model and tokenizer
        self.model.save_pretrained(str(self.checkpoint_dir))
        self.tokenizer.save_pretrained(str(self.checkpoint_dir))
        
        # Save label mapping
        label_map_path = self.checkpoint_dir / "label_map.json"
        with open(label_map_path, 'w') as f:
            json.dump({
                'id_to_label': self.id_to_label,
                'label_to_id': self.label_to_id
            }, f, indent=2)
        
        logger.info(f"Model saved to {self.checkpoint_dir}")
    
    def _extract_metrics(self, eval_metrics: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract and format evaluation metrics.
        
        Extracts the key metrics from Trainer's evaluation output and formats
        them into a clean dictionary for return to the caller.
        
        Args:
            eval_metrics: Raw evaluation metrics from trainer (includes eval_ prefix)
        
        Returns:
            Formatted metrics dictionary with f1, precision, recall, loss
        
        Requirements: 2.2, 2.3, 8.4, 10.1
        """
        return {
            'f1': eval_metrics.get('eval_f1', 0.0),
            'precision': eval_metrics.get('eval_precision', 0.0),
            'recall': eval_metrics.get('eval_recall', 0.0),
            'loss': eval_metrics.get('eval_loss', 0.0)
        }

    def _semi_supervised_iteration(
        self,
        labeled_data: List[Tuple[str, List[str]]],
        unlabeled_data: List[str],
        confidence_threshold: float = SEMI_SUPERVISED_CONFIDENCE_THRESHOLD
    ) -> Dict[str, float]:
        """
        Perform one iteration of semi-supervised learning using pseudo-labeling.
        
        Args:
            labeled_data: Original labeled examples
            unlabeled_data: Unlabeled texts to generate pseudo-labels for
            confidence_threshold: Minimum confidence for pseudo-labels (default: 0.9)
        
        Returns:
            Updated evaluation metrics after retraining
        
        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
        """
        logger.info(f"Starting semi-supervised iteration with {len(unlabeled_data)} unlabeled examples")
        logger.info(f"Confidence threshold: {confidence_threshold}")
        
        # Generate pseudo-labels
        pseudo_labeled_data = self._generate_pseudo_labels(unlabeled_data, confidence_threshold)
        
        if not pseudo_labeled_data:
            logger.warning("No high-confidence pseudo-labels generated, skipping semi-supervised iteration")
            return {}
        
        # Combine and retrain
        combined_data = labeled_data + pseudo_labeled_data
        logger.info(f"Combined dataset size: {len(combined_data)} examples")
        
        eval_metrics = self._retrain_with_pseudo_labels(combined_data)
        logger.info("Semi-supervised iteration complete")
        return eval_metrics
    
    def _generate_pseudo_labels(
        self, 
        unlabeled_data: List[str], 
        confidence_threshold: float
    ) -> List[Tuple[str, List[str]]]:
        """
        Generate pseudo-labels for unlabeled data.
        
        Predicts labels for unlabeled data and filters for high-confidence
        predictions. Only predictions above the confidence threshold are
        used as pseudo-labels for semi-supervised learning.
        
        Args:
            unlabeled_data: List of unlabeled texts
            confidence_threshold: Minimum confidence for pseudo-labels (0.0-1.0)
        
        Returns:
            List of (text, [taxonomy_ids]) tuples with high-confidence predictions
        
        Requirements: 3.1, 3.2, 3.3, 10.2
        """
        logger.info("Generating predictions for unlabeled data...")
        pseudo_labeled_data = []
        
        for text in unlabeled_data:
            result = self.predict(text, top_k=UNCERTAINTY_TOP_K)
            
            # Filter high-confidence predictions using domain object methods
            high_conf_predictions = result.get_high_confidence(threshold=confidence_threshold)
            
            # Extract taxonomy IDs
            high_conf_labels = [pred.taxonomy_id for pred in high_conf_predictions]
            
            # Only add if we have at least one high-confidence prediction
            if high_conf_labels:
                pseudo_labeled_data.append((text, high_conf_labels))
        
        logger.info(f"Generated {len(pseudo_labeled_data)} pseudo-labeled examples")
        return pseudo_labeled_data
    
    def _retrain_with_pseudo_labels(self, combined_data: List[Tuple[str, List[str]]]) -> Dict[str, float]:
        """
        Re-train model with combined labeled and pseudo-labeled data.
        
        Performs a single epoch of training on the combined dataset with a
        lower learning rate to avoid catastrophic forgetting of the original
        labeled data.
        
        Args:
            combined_data: Combined labeled and pseudo-labeled examples
        
        Returns:
            Evaluation metrics after retraining
        
        Requirements: 3.1, 3.2, 3.3, 10.2
        """
        logger.info("Re-training model with pseudo-labeled data...")
        eval_metrics = self.fine_tune(
            labeled_data=combined_data,
            unlabeled_data=None,  # Don't recurse
            epochs=SEMI_SUPERVISED_EPOCHS,
            batch_size=DEFAULT_BATCH_SIZE,
            learning_rate=SEMI_SUPERVISED_LEARNING_RATE
        )
        return eval_metrics

    def predict(
        self,
        text: str,
        top_k: int = DEFAULT_TOP_K,
        user_id: Optional[str] = None,
        experiment_id: Optional[str] = None
    ) -> ClassificationResult:
        """
        Predict taxonomy categories for a single text.
        
        This method performs inference on a single text input and returns
        the top-K predicted taxonomy node IDs with confidence scores as a
        ClassificationResult domain object.
        
        This is a QUERY method following Command-Query Separation principle:
        - Returns a value (ClassificationResult)
        - Has no side effects except logging (which is acceptable for monitoring)
        - Does not modify system state
        
        Supports A/B testing: if experiment_id is provided, routes prediction
        to control or treatment version based on user_id hashing.
        
        Args:
            text: Input text to classify
            top_k: Number of top predictions to return (default: 5)
            user_id: Optional user ID for A/B testing routing
            experiment_id: Optional experiment ID for A/B testing
        
        Returns:
            ClassificationResult containing:
                - predictions: List of ClassificationPrediction objects
                - model_version: Model version used
                - inference_time_ms: Time taken for inference
            
            Use .to_dict() for backward compatibility with dict-based APIs.
        
        Algorithm:
        1. Check if A/B testing is active (experiment_id provided)
        2. If yes, route to control or treatment version
        3. Load model if not already loaded (lazy loading)
        4. Tokenize input text
        5. Forward pass through model
        6. Apply sigmoid activation to get probabilities
        7. Get top-K predictions
        8. Convert label indices to taxonomy node IDs
        9. Create ClassificationResult domain object
        10. Log prediction (side effect for monitoring)
        11. Return ClassificationResult
        
        Performance: <100ms per prediction
        
        Requirements: 2.4, 2.5, 2.8, 15.8, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 8.2
        """
        import time
        start_time = time.time()
        
        # Determine A/B testing version (query operation)
        ab_version = self._determine_ab_version(experiment_id, user_id)
        
        # Ensure model is loaded
        if self.model is None or self.tokenizer is None:
            self._load_model()
        
        import torch
        import numpy as np
        
        # Tokenize input
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=MAX_TOKEN_LENGTH,
            return_tensors='pt'
        )
        
        # Move to device
        inputs = {key: val.to(self.device) for key, val in inputs.items()}
        
        # Forward pass
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
        
        # Apply sigmoid to get probabilities
        probs = torch.sigmoid(logits).cpu().numpy()[0]
        
        # Get top-K predictions
        top_indices = np.argsort(probs)[-top_k:][::-1]
        
        # Convert to ClassificationPrediction objects
        prediction_objects = []
        for rank, idx in enumerate(top_indices, start=1):
            if idx < len(self.id_to_label):
                taxonomy_id = self.id_to_label[idx]
                confidence = float(probs[idx])
                prediction_objects.append(
                    ClassificationPrediction(
                        taxonomy_id=taxonomy_id,
                        confidence=confidence,
                        rank=rank
                    )
                )
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Create ClassificationResult domain object
        result = ClassificationResult(
            predictions=prediction_objects,
            model_version=self.model_version or "production",
            inference_time_ms=latency_ms
        )
        
        # Log prediction (modifier operation - acceptable side effect for monitoring)
        self._log_prediction(
            text=text,
            result=result,
            user_id=user_id,
            experiment_id=experiment_id,
            ab_version=ab_version
        )
        
        return result
    
    def _determine_ab_version(
        self, 
        experiment_id: Optional[str], 
        user_id: Optional[str]
    ) -> Optional[str]:
        """
        Determine A/B testing version for prediction routing.
        
        This is a QUERY method: returns a value without side effects.
        
        Args:
            experiment_id: Optional experiment ID for A/B testing
            user_id: Optional user ID for A/B testing routing
        
        Returns:
            A/B version string ("control" or "treatment") or None if not applicable
        
        Requirements: 4.1, 4.2
        """
        if not experiment_id or not user_id:
            return None
        
        try:
            from backend.scripts.deployment.ab_testing import ABTestingFramework
            
            # Route prediction to control or treatment
            ab_testing = ABTestingFramework(self.db)
            ab_version = ab_testing.route_prediction(experiment_id, user_id)
            
            logger.info(f"A/B testing active: routing to {ab_version} version")
            
            # TODO: Load the appropriate model version based on routing
            # For now, we'll use the current model and log the routing decision
            
            return ab_version
            
        except Exception as e:
            logger.warning(f"A/B testing routing failed: {e}. Using default model.")
            return None
    
    def _log_prediction(
        self,
        text: str,
        result: ClassificationResult,
        user_id: Optional[str] = None,
        experiment_id: Optional[str] = None,
        ab_version: Optional[str] = None
    ) -> None:
        """
        Log prediction to monitoring and A/B testing systems.
        
        This is a MODIFIER method following Command-Query Separation principle:
        - Returns None (no return value)
        - Has side effects (logs to monitoring systems)
        - Modifies external state (monitoring databases/logs)
        
        This method is separated from predict() to maintain clean separation
        between query (prediction) and modifier (logging) operations.
        
        Args:
            text: Input text that was classified
            result: ClassificationResult from prediction
            user_id: Optional user ID for tracking
            experiment_id: Optional experiment ID for A/B testing
            ab_version: Optional A/B version ("control" or "treatment")
        
        Returns:
            None
        
        Side Effects:
            - Logs prediction to PredictionMonitor
            - Logs prediction to A/B testing framework if applicable
        
        Requirements: 4.3, 4.4, 4.5, 8.2
        """
        # Log to prediction monitor
        self._log_to_monitor(text, result, user_id)
        
        # Log to A/B testing framework if applicable
        if experiment_id and ab_version:
            self._log_to_ab_testing(text, result, experiment_id, ab_version, user_id)
    
    def _log_to_monitor(
        self,
        text: str,
        result: ClassificationResult,
        user_id: Optional[str] = None
    ) -> None:
        """
        Log prediction to PredictionMonitor.
        
        This is a MODIFIER method: returns None and has side effects.
        
        Args:
            text: Input text that was classified
            result: ClassificationResult from prediction
            user_id: Optional user ID for tracking
        
        Returns:
            None
        
        Side Effects:
            - Logs prediction to PredictionMonitor
        
        Requirements: 4.3, 4.4
        """
        try:
            # Get max confidence for monitoring
            max_confidence = max(
                p.confidence for p in result.predictions
            ) if result.predictions else 0.0
            
            # Convert to dict format for legacy monitor
            predictions_dict = {
                p.taxonomy_id: p.confidence 
                for p in result.predictions
            }
            
            self.monitor.log_prediction(
                input_text=text,
                predictions={
                    "predictions": predictions_dict, 
                    "confidence": max_confidence
                },
                latency_ms=result.inference_time_ms,
                error=None,
                user_id=user_id
            )
        except Exception as e:
            logger.warning(f"Failed to log prediction to monitor: {e}")
    
    def _log_to_ab_testing(
        self,
        text: str,
        result: ClassificationResult,
        experiment_id: str,
        ab_version: str,
        user_id: Optional[str] = None
    ) -> None:
        """
        Log prediction to A/B testing framework.
        
        This is a MODIFIER method: returns None and has side effects.
        
        Args:
            text: Input text that was classified
            result: ClassificationResult from prediction
            experiment_id: Experiment ID for A/B testing
            ab_version: A/B version ("control" or "treatment")
            user_id: Optional user ID for tracking
        
        Returns:
            None
        
        Side Effects:
            - Logs prediction to A/B testing framework
        
        Requirements: 4.3, 4.5
        """
        try:
            from backend.scripts.deployment.ab_testing import ABTestingFramework
            
            ab_testing = ABTestingFramework(self.db)
            
            # Convert to dict format for legacy A/B testing
            predictions_dict = {
                p.taxonomy_id: p.confidence 
                for p in result.predictions
            }
            
            ab_testing.log_prediction(
                experiment_id=experiment_id,
                version=self.model_version or "production",
                input_text=text,
                predictions=predictions_dict,
                latency_ms=result.inference_time_ms,
                user_id=user_id
            )
            
        except Exception as e:
            logger.warning(f"Failed to log A/B testing prediction: {e}")

    def predict_batch(
        self,
        texts: List[str],
        top_k: int = DEFAULT_TOP_K
    ) -> List[Dict[str, float]]:
        """
        Predict taxonomy categories for multiple texts efficiently using batch processing.
        
        This method processes multiple texts in batches for improved efficiency.
        Batch size is automatically adjusted based on GPU availability:
        - 32 for GPU (CUDA available)
        - 8 for CPU
        
        Args:
            texts: List of input texts to classify
            top_k: Number of top predictions to return per text (default: 5)
        
        Returns:
            List of dictionaries, one per input text, mapping taxonomy_node_id to confidence
            Example: [
                {"node_id_1": 0.95, "node_id_2": 0.87},
                {"node_id_3": 0.92, "node_id_1": 0.78},
                ...
            ]
        
        Algorithm:
        1. Load model if not already loaded (lazy loading)
        2. Determine batch size based on device (32 for GPU, 8 for CPU)
        3. Process texts in batches:
           a. Tokenize batch
           b. Forward pass through model
           c. Apply sigmoid activation
           d. Get top-K predictions for each text
           e. Convert indices to taxonomy node IDs
        4. Combine results from all batches
        
        Performance: Significantly faster than calling predict() in a loop
        
        Requirements: 2.5, 13.1, 13.2, 13.3
        """
        # Ensure model is loaded
        if self.model is None or self.tokenizer is None:
            self._load_model()
        
        import torch
        import numpy as np
        
        # Determine batch size based on device
        batch_size = GPU_BATCH_SIZE if torch.cuda.is_available() else CPU_BATCH_SIZE
        logger.info(f"Processing {len(texts)} texts with batch_size={batch_size}")
        
        all_predictions = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            logger.debug(f"Processing batch {i // batch_size + 1}/{(len(texts) + batch_size - 1) // batch_size}")
            
            # Tokenize batch
            inputs = self.tokenizer(
                batch_texts,
                truncation=True,
                padding=True,
                max_length=MAX_TOKEN_LENGTH,
                return_tensors='pt'
            )
            
            # Move to device
            inputs = {key: val.to(self.device) for key, val in inputs.items()}
            
            # Forward pass
            self.model.eval()
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
            
            # Apply sigmoid to get probabilities
            probs = torch.sigmoid(logits).cpu().numpy()
            
            # Get top-K predictions for each text in batch
            for text_probs in probs:
                # Get top-K indices
                top_indices = np.argsort(text_probs)[-top_k:][::-1]
                
                # Convert to taxonomy node IDs with confidence scores
                predictions = {}
                for idx in top_indices:
                    if idx < len(self.id_to_label):
                        taxonomy_id = self.id_to_label[idx]
                        confidence = float(text_probs[idx])
                        predictions[taxonomy_id] = confidence
                
                all_predictions.append(predictions)
        
        logger.info(f"Batch prediction complete: processed {len(all_predictions)} texts")
        return all_predictions

    def identify_uncertain_samples(
        self,
        resource_ids: Optional[List[str]] = None,
        limit: int = DEFAULT_UNCERTAINTY_LIMIT
    ) -> List[Tuple[str, float]]:
        """
        Identify resources with uncertain classifications for active learning.
        
        This method implements uncertainty sampling using multiple uncertainty metrics:
        - Entropy: Measures prediction uncertainty across all classes
        - Margin: Difference between top-2 predictions (small = uncertain)
        - Confidence: Maximum probability (low = uncertain)
        
        The combined uncertainty score prioritizes resources where the model is most
        uncertain, making them ideal candidates for human review and labeling.
        
        Args:
            resource_ids: Optional list of resource IDs to filter (default: all resources)
            limit: Number of most uncertain samples to return (default: 100)
        
        Returns:
            List of (resource_id, uncertainty_score) tuples sorted by uncertainty descending
            Example: [("resource_uuid_1", 0.85), ("resource_uuid_2", 0.78), ...]
        
        Algorithm:
        1. Query resources (prioritize predicted classifications)
        2. Get resource content (title + description)
        3. Predict classifications for resources
        4. Compute entropy uncertainty metric: -Σ(p * log(p))
        5. Compute margin uncertainty metric: difference between top-2 predictions
        6. Compute confidence uncertainty metric: 1 - max(probabilities)
        7. Combine uncertainty scores: entropy * (1 - margin) * (1 - max_conf)
        8. Sort by uncertainty descending
        9. Return top-N most uncertain
        
        Requirements: 4.1, 4.2, 4.3, 4.7
        """
        logger.info(f"Identifying uncertain samples (limit={limit})")
        
        # Import required libraries
        import numpy as np
        from ..database.models import Resource, ResourceTaxonomy
        
        # Step 1: Query resources (prioritize predicted classifications)
        query = self.db.query(Resource)
        
        # Filter by resource_ids if provided
        if resource_ids:
            query = query.filter(Resource.id.in_(resource_ids))
        
        # Prioritize resources with predicted classifications
        # Join with ResourceTaxonomy to find resources that have been classified
        query = query.outerjoin(ResourceTaxonomy).filter(
            (ResourceTaxonomy.is_predicted) | (ResourceTaxonomy.id is None)
        )
        
        # Get distinct resources
        resources = query.distinct().limit(limit * 2).all()  # Get more than needed for filtering
        
        logger.info(f"Found {len(resources)} resources to evaluate")
        
        if not resources:
            logger.warning("No resources found for uncertainty sampling")
            return []
        
        # Step 2-3: Get resource content and predict classifications
        uncertainty_scores = []
        
        for resource in resources:
            # Get resource content (title + description)
            text = resource.title or ""
            if resource.description:
                text += " " + resource.description
            
            if not text.strip():
                logger.debug(f"Skipping resource {resource.id} - no text content")
                continue
            
            try:
                # Predict classifications
                result = self.predict(text, top_k=UNCERTAINTY_TOP_K)  # Get more predictions for better uncertainty estimation
                
                if not result.predictions:
                    logger.debug(f"No predictions for resource {resource.id}")
                    continue
                
                # Get probability array from domain object
                probs = np.array([pred.confidence for pred in result.predictions])
                
                # Step 4: Compute entropy uncertainty metric
                # Entropy: -Σ(p * log(p))
                # Higher entropy = more uncertain
                entropy = -np.sum(probs * np.log(probs + UNCERTAINTY_EPSILON))
                
                # Normalize entropy by max possible entropy (log of number of classes)
                max_entropy = np.log(len(probs))
                normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
                
                # Step 5: Compute margin uncertainty metric
                # Margin: difference between top-2 predictions
                # Smaller margin = more uncertain
                sorted_probs = np.sort(probs)[::-1]  # Sort descending
                if len(sorted_probs) >= 2:
                    margin = sorted_probs[0] - sorted_probs[1]
                else:
                    margin = sorted_probs[0] if len(sorted_probs) > 0 else 0
                
                # Convert to uncertainty (1 - margin)
                margin_uncertainty = 1 - margin
                
                # Step 6: Compute confidence uncertainty metric
                # Confidence: maximum probability
                # Lower confidence = more uncertain
                max_confidence = np.max(probs)
                confidence_uncertainty = 1 - max_confidence
                
                # Step 7: Combine uncertainty scores
                # Combined score: entropy * (1 - margin) * (1 - max_conf)
                # This gives high scores to samples with:
                # - High entropy (uncertain across many classes)
                # - Low margin (top predictions are close)
                # - Low confidence (not confident in any prediction)
                combined_uncertainty = normalized_entropy * margin_uncertainty * confidence_uncertainty
                
                uncertainty_scores.append((str(resource.id), combined_uncertainty))
                
                logger.debug(
                    f"Resource {resource.id}: entropy={normalized_entropy:.3f}, "
                    f"margin_unc={margin_uncertainty:.3f}, conf_unc={confidence_uncertainty:.3f}, "
                    f"combined={combined_uncertainty:.3f}"
                )
                
            except Exception as e:
                logger.warning(f"Error processing resource {resource.id}: {e}")
                continue
        
        # Step 8: Sort by uncertainty descending
        uncertainty_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Step 9: Return top-N most uncertain
        top_uncertain = uncertainty_scores[:limit]
        
        top_score = top_uncertain[0][1] if top_uncertain else 0.0
        logger.info(
            f"Identified {len(top_uncertain)} uncertain samples. "
            f"Top uncertainty score: {top_score:.3f}"
        )
        
        return top_uncertain

    def get_metrics(self, window_minutes: int = DEFAULT_METRICS_WINDOW_MINUTES) -> Dict[str, Any]:
        """
        Get prediction metrics from the monitor.
        
        This method exposes the PredictionMonitor's metrics for monitoring
        and alerting purposes.
        
        Args:
            window_minutes: Time window in minutes for calculating metrics (default: 60)
        
        Returns:
            Dictionary containing metrics:
                - total_predictions: Total number of predictions in window
                - error_rate: Percentage of predictions with errors
                - latency_p50: 50th percentile latency in ms
                - latency_p95: 95th percentile latency in ms
                - latency_p99: 99th percentile latency in ms
                - avg_confidence: Average prediction confidence
                - low_confidence_rate: Percentage of predictions with confidence < 0.5
        
        Requirements: 15.8
        """
        return self.monitor.get_metrics(window_minutes=window_minutes)

    def update_from_human_feedback(
        self,
        resource_id: str,
        correct_taxonomy_ids: List[str]
    ) -> bool:
        """
        Update classification based on human feedback.
        
        This method handles human corrections to ML predictions, which are used
        to improve the model through active learning. It removes predicted
        classifications and adds manual labels with confidence 1.0.
        
        Args:
            resource_id: Resource to update
            correct_taxonomy_ids: Correct taxonomy node IDs provided by human
        
        Returns:
            True if update successful, False otherwise
        
        Algorithm:
        1. Validate resource exists
        2. Remove existing predicted classifications
        3. Add human-labeled classifications (confidence=1.0, is_predicted=False)
        4. Check if retraining threshold reached (100 new labels)
        5. Trigger retraining notification if threshold met
        
        Side Effects:
        - Updates database (removes predicted, adds manual classifications)
        - May trigger retraining notification
        - Logs feedback for model improvement tracking
        
        Requirements: 4.4, 4.5, 4.6
        """
        logger.info(f"Updating resource {resource_id} with human feedback")
        logger.info(f"Correct taxonomy IDs: {correct_taxonomy_ids}")
        
        from ..database.models import Resource, ResourceTaxonomy, TaxonomyNode
        
        try:
            # Step 1: Validate resource exists
            resource = self.db.query(Resource).filter(Resource.id == resource_id).first()
            if not resource:
                logger.error(f"Resource {resource_id} not found")
                return False
            
            # Validate taxonomy nodes exist
            for taxonomy_id in correct_taxonomy_ids:
                node = self.db.query(TaxonomyNode).filter(TaxonomyNode.id == taxonomy_id).first()
                if not node:
                    logger.error(f"Taxonomy node {taxonomy_id} not found")
                    return False
            
            # Step 2: Remove existing predicted classifications
            deleted_count = self.db.query(ResourceTaxonomy).filter(
                ResourceTaxonomy.resource_id == resource_id,
                ResourceTaxonomy.is_predicted
            ).delete()
            
            logger.info(f"Removed {deleted_count} predicted classifications")
            
            # Step 3: Add human-labeled classifications
            for taxonomy_id in correct_taxonomy_ids:
                # Check if manual classification already exists
                existing = self.db.query(ResourceTaxonomy).filter(
                    ResourceTaxonomy.resource_id == resource_id,
                    ResourceTaxonomy.taxonomy_node_id == taxonomy_id,
                    not ResourceTaxonomy.is_predicted
                ).first()
                
                if existing:
                    logger.debug(f"Manual classification already exists for {taxonomy_id}")
                    continue
                
                # Create new manual classification
                manual_classification = ResourceTaxonomy(
                    resource_id=resource_id,
                    taxonomy_node_id=taxonomy_id,
                    confidence=1.0,  # Human labels have confidence 1.0
                    is_predicted=False,  # Manual classification
                    predicted_by="manual",
                    needs_review=False,  # No review needed for manual labels
                    review_priority=None
                )
                
                self.db.add(manual_classification)
                logger.info(f"Added manual classification for taxonomy node {taxonomy_id}")
            
            # Commit changes
            self.db.commit()
            logger.info("Human feedback successfully applied")
            
            # Step 4: Check if retraining threshold reached
            # Count total manual classifications (across all resources)
            manual_count = self.db.query(ResourceTaxonomy).filter(
                not ResourceTaxonomy.is_predicted,
                ResourceTaxonomy.predicted_by == "manual"
            ).count()
            
            logger.info(f"Total manual classifications: {manual_count}")
            
            # Step 5: Trigger retraining notification if threshold met
            if manual_count >= RETRAINING_THRESHOLD:
                # Check if we just crossed the threshold
                # (to avoid repeated notifications)
                if manual_count % RETRAINING_THRESHOLD < len(correct_taxonomy_ids):
                    logger.warning(
                        f"RETRAINING RECOMMENDED: {manual_count} manual labels accumulated. "
                        f"Consider retraining the model to incorporate human feedback."
                    )
                    # In a production system, this would trigger a background task
                    # or send a notification to administrators
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating human feedback: {e}")
            self.db.rollback()
            return False



class ClassificationTrainer:
    """
    Handles training of classification models.
    
    This class provides methods for training transformer-based classification models,
    including standard supervised training, semi-supervised learning with pseudo-labeling,
    and checkpoint management.
    
    The trainer is designed to work with the MLClassificationService and provides
    a clean separation between training operations and inference operations.
    """
    
    def __init__(self, model_dir: str = "models/classification"):
        """
        Initialize the classification trainer.
        
        Args:
            model_dir: Directory for saving model checkpoints (default: "models/classification")
        
        Requirements: 8.1
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ClassificationTrainer initialized with model_dir={self.model_dir}")
    
    def train(
        self,
        training_data: List['TrainingExample'],
        model_name: str = "default",
        epochs: int = DEFAULT_EPOCHS,
        batch_size: int = DEFAULT_BATCH_SIZE,
        learning_rate: float = DEFAULT_LEARNING_RATE,
        validation_split: float = VALIDATION_SPLIT_RATIO
    ) -> 'TrainingResult':
        """
        Train classification model on labeled data.
        
        This method performs supervised training on labeled examples, saves the
        trained model checkpoint, and returns training metrics.
        
        Args:
            training_data: List of TrainingExample objects with text and labels
            model_name: Name for the trained model (default: "default")
            epochs: Number of training epochs (default: 3)
            batch_size: Training batch size (default: 16)
            learning_rate: Learning rate for optimizer (default: 2e-5)
            validation_split: Fraction of data to use for validation (default: 0.2)
        
        Returns:
            TrainingResult containing metrics and checkpoint path
        
        Raises:
            ValueError: If training_data is empty or invalid
            ImportError: If required ML libraries not installed
        
        Algorithm:
        1. Validate training data
        2. Convert TrainingExample objects to (text, labels) format
        3. Initialize MLClassificationService
        4. Call fine_tune() method
        5. Package results into TrainingResult domain object
        6. Return TrainingResult
        
        Requirements: 8.1, 8.4
        """
        import time
        from ..domain.classification import TrainingResult
        
        logger.info(f"Starting training with {len(training_data)} examples")
        logger.info(f"Model: {model_name}, Epochs: {epochs}, Batch size: {batch_size}")
        
        # Validate training data
        if not training_data:
            raise ValueError("training_data cannot be empty")
        
        # Validate all training examples
        for example in training_data:
            example.validate()
        
        # Convert TrainingExample objects to (text, [labels]) format
        # Expected by MLClassificationService.fine_tune()
        labeled_data = []
        for example in training_data:
            # Handle both single label and comma-separated labels
            if ',' in example.label:
                labels = [label.strip() for label in example.label.split(',')]
            else:
                labels = [example.label]
            
            labeled_data.append((example.text, labels))
        
        logger.info(f"Converted {len(labeled_data)} training examples")
        
        # Initialize service (we need a db session, but for training we can use None)
        # The service will handle model initialization
        from sqlalchemy.orm import Session
        db = Session()  # Create a temporary session
        
        try:
            # Create service instance
            service = MLClassificationService(
                db=db,
                model_name=DEFAULT_MODEL_NAME,
                model_version=model_name
            )
            
            # Track training time
            start_time = time.time()
            
            # Perform training
            metrics = service.fine_tune(
                labeled_data=labeled_data,
                unlabeled_data=None,
                epochs=epochs,
                batch_size=batch_size,
                learning_rate=learning_rate
            )
            
            training_time = time.time() - start_time
            
            # Get checkpoint path
            checkpoint_path = str(service.checkpoint_dir)
            
            # Create TrainingResult domain object
            result = TrainingResult(
                model_name=model_name,
                final_loss=metrics.get('loss', 0.0),
                checkpoint_path=checkpoint_path,
                metrics=metrics,
                num_epochs=epochs,
                training_time_seconds=training_time
            )
            
            logger.info(f"Training complete in {training_time:.2f}s")
            logger.info(f"Final metrics: {metrics}")
            logger.info(f"Checkpoint saved to: {checkpoint_path}")
            
            return result
            
        finally:
            db.close()
    
    def train_semi_supervised(
        self,
        labeled_data: List['TrainingExample'],
        unlabeled_data: List[str],
        confidence_threshold: float = SEMI_SUPERVISED_CONFIDENCE_THRESHOLD,
        model_name: str = "semi_supervised",
        epochs: int = DEFAULT_EPOCHS,
        batch_size: int = DEFAULT_BATCH_SIZE
    ) -> 'TrainingResult':
        """
        Train using semi-supervised learning with pseudo-labeling.
        
        This method first trains on labeled data, then generates pseudo-labels
        for unlabeled data using high-confidence predictions, and finally
        retrains on the combined dataset.
        
        Args:
            labeled_data: List of TrainingExample objects with labels
            unlabeled_data: List of unlabeled text strings
            confidence_threshold: Minimum confidence for pseudo-labels (default: 0.9)
            model_name: Name for the trained model (default: "semi_supervised")
            epochs: Number of training epochs (default: 3)
            batch_size: Training batch size (default: 16)
        
        Returns:
            TrainingResult containing metrics and checkpoint path
        
        Raises:
            ValueError: If labeled_data is empty or invalid
        
        Algorithm:
        1. Validate labeled data
        2. Convert TrainingExample objects to (text, labels) format
        3. Initialize MLClassificationService
        4. Call fine_tune() with both labeled and unlabeled data
        5. Service will handle pseudo-labeling internally
        6. Package results into TrainingResult domain object
        7. Return TrainingResult
        
        Requirements: 8.2, 8.4
        """
        import time
        from ..domain.classification import TrainingResult
        
        logger.info(f"Starting semi-supervised training")
        logger.info(f"Labeled: {len(labeled_data)}, Unlabeled: {len(unlabeled_data)}")
        logger.info(f"Confidence threshold: {confidence_threshold}")
        
        # Validate labeled data
        if not labeled_data:
            raise ValueError("labeled_data cannot be empty")
        
        # Validate all training examples
        for example in labeled_data:
            example.validate()
        
        # Convert TrainingExample objects to (text, [labels]) format
        labeled_tuples = []
        for example in labeled_data:
            # Handle both single label and comma-separated labels
            if ',' in example.label:
                labels = [label.strip() for label in example.label.split(',')]
            else:
                labels = [example.label]
            
            labeled_tuples.append((example.text, labels))
        
        logger.info(f"Converted {len(labeled_tuples)} labeled examples")
        
        # Initialize service
        from sqlalchemy.orm import Session
        db = Session()
        
        try:
            # Create service instance
            service = MLClassificationService(
                db=db,
                model_name=DEFAULT_MODEL_NAME,
                model_version=model_name
            )
            
            # Track training time
            start_time = time.time()
            
            # Perform semi-supervised training
            # The service will handle pseudo-labeling internally
            metrics = service.fine_tune(
                labeled_data=labeled_tuples,
                unlabeled_data=unlabeled_data,
                epochs=epochs,
                batch_size=batch_size,
                learning_rate=DEFAULT_LEARNING_RATE
            )
            
            training_time = time.time() - start_time
            
            # Get checkpoint path
            checkpoint_path = str(service.checkpoint_dir)
            
            # Create TrainingResult domain object
            result = TrainingResult(
                model_name=model_name,
                final_loss=metrics.get('loss', 0.0),
                checkpoint_path=checkpoint_path,
                metrics=metrics,
                num_epochs=epochs,
                training_time_seconds=training_time
            )
            
            logger.info(f"Semi-supervised training complete in {training_time:.2f}s")
            logger.info(f"Final metrics: {metrics}")
            logger.info(f"Checkpoint saved to: {checkpoint_path}")
            
            return result
            
        finally:
            db.close()
    
    def load_checkpoint(self, checkpoint_path: str) -> 'MLClassificationService':
        """
        Load model from checkpoint.
        
        This method loads a previously trained model from a checkpoint directory.
        It handles both absolute and relative paths, and searches in multiple
        possible locations.
        
        Args:
            checkpoint_path: Path to checkpoint directory (absolute or relative)
        
        Returns:
            MLClassificationService instance with loaded model
        
        Raises:
            FileNotFoundError: If checkpoint not found
            Exception: If model loading fails
        
        Algorithm:
        1. Convert checkpoint_path to Path object
        2. Check if path exists as absolute path
        3. If not, try relative to model_dir
        4. If not, try relative to project root
        5. If found, create MLClassificationService with that checkpoint
        6. Return service instance
        
        Requirements: 8.3, 8.4
        """
        logger.info(f"Loading checkpoint from: {checkpoint_path}")
        
        # Convert to Path object
        path = Path(checkpoint_path)
        
        # Try multiple possible locations
        possible_paths = [
            path,  # Absolute path or relative to current directory
            self.model_dir / checkpoint_path,  # Relative to model_dir
            Path("models") / "classification" / checkpoint_path,  # Relative to project root
            Path("backend") / "models" / "classification" / checkpoint_path,  # Relative to backend
        ]
        
        # Find the first existing path with model files
        checkpoint_dir = None
        for possible_path in possible_paths:
            if possible_path.exists() and (possible_path / "config.json").exists():
                checkpoint_dir = possible_path
                logger.info(f"Found checkpoint at: {checkpoint_dir}")
                break
        
        if checkpoint_dir is None:
            error_msg = f"Checkpoint not found: {checkpoint_path}. Tried locations: {possible_paths}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # Extract model version from checkpoint path
        # Assume format: models/classification/arxiv_v1.0.0
        model_version = checkpoint_dir.name
        if model_version.startswith("arxiv_"):
            model_version = model_version[6:]  # Remove "arxiv_" prefix
        
        # Create service instance with loaded model
        from sqlalchemy.orm import Session
        db = Session()
        
        try:
            service = MLClassificationService(
                db=db,
                model_name=DEFAULT_MODEL_NAME,
                version=model_version
            )
            
            # Force model loading
            service._load_model()
            
            logger.info(f"Successfully loaded model from checkpoint: {checkpoint_dir}")
            return service
            
        except Exception as e:
            db.close()
            logger.error(f"Failed to load checkpoint: {e}")
            raise Exception(f"Model loading failed: {e}") from e
