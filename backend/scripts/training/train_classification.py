"""
Classification model training module for arXiv paper classification.

This module provides the ClassificationTrainer class for training DistilBERT-based
classification models on arXiv academic papers.
"""

import json
import logging
import math
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

import torch
import numpy as np
from torch.utils.data import Dataset
from torch.utils.tensorboard import SummaryWriter
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback,
    TrainerCallback,
)
from sklearn.metrics import accuracy_score, classification_report, f1_score


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Custom Exceptions
class TrainingDivergenceError(Exception):
    """Raised when training loss becomes NaN or infinite."""

    pass


class CheckpointValidationError(Exception):
    """Raised when checkpoint validation fails."""

    pass


class DataValidationError(Exception):
    """Raised when data validation fails."""

    pass


# Utility Functions
def check_training_health(loss: float, step: int) -> None:
    """
    Check if training is healthy by detecting NaN or Inf loss.

    Args:
        loss: Current training loss value
        step: Current training step

    Raises:
        TrainingDivergenceError: If loss is NaN or Inf
    """
    if math.isnan(loss) or math.isinf(loss):
        error_msg = (
            f"Training diverged at step {step}: loss={loss}. "
            "Suggestions:\n"
            "  1. Reduce learning rate (try 1e-5 instead of 2e-5)\n"
            "  2. Check data quality for corrupted samples\n"
            "  3. Reduce batch size to improve gradient stability\n"
            "  4. Increase warmup steps for gradual learning rate increase"
        )
        logger.error(error_msg)
        raise TrainingDivergenceError(error_msg)


def load_checkpoint_with_validation(checkpoint_path: Path) -> Dict[str, Any]:
    """
    Load checkpoint with validation and backup fallback.

    Args:
        checkpoint_path: Path to checkpoint directory

    Returns:
        Dictionary containing model state and metadata

    Raises:
        CheckpointValidationError: If checkpoint validation fails
    """
    logger.info(f"Loading checkpoint from {checkpoint_path}")

    # Check if checkpoint directory exists
    if not checkpoint_path.exists():
        raise CheckpointValidationError(
            f"Checkpoint directory not found: {checkpoint_path}"
        )

    # Required files for a valid checkpoint
    required_files = ["pytorch_model.bin", "config.json"]

    # Check if all required files exist
    missing_files = []
    for filename in required_files:
        file_path = checkpoint_path / filename
        if not file_path.exists():
            missing_files.append(filename)

    if missing_files:
        # Try loading from backup
        backup_path = checkpoint_path.parent / f"{checkpoint_path.name}.backup"
        if backup_path.exists():
            logger.warning(f"Missing files in checkpoint: {missing_files}")
            logger.info(f"Attempting to load from backup: {backup_path}")
            return load_checkpoint_with_validation(backup_path)
        else:
            raise CheckpointValidationError(
                f"Checkpoint validation failed. Missing files: {missing_files}. "
                f"No backup found at {backup_path}"
            )

    # Try to load the model to validate it's not corrupted
    try:
        model_file = checkpoint_path / "pytorch_model.bin"
        state_dict = torch.load(model_file, map_location="cpu")

        # Validate state_dict has expected structure
        if not isinstance(state_dict, dict):
            raise CheckpointValidationError(
                "Invalid checkpoint format: state_dict is not a dictionary"
            )

        if len(state_dict) == 0:
            raise CheckpointValidationError("Invalid checkpoint: state_dict is empty")

        logger.info("Checkpoint validation successful")
        return {"checkpoint_path": checkpoint_path, "state_dict": state_dict}

    except Exception as e:
        # Try loading from backup
        backup_path = checkpoint_path.parent / f"{checkpoint_path.name}.backup"
        if backup_path.exists():
            logger.error(f"Checkpoint loading failed: {e}")
            logger.info(f"Attempting to load from backup: {backup_path}")
            return load_checkpoint_with_validation(backup_path)
        else:
            raise CheckpointValidationError(
                f"Checkpoint loading failed: {e}. No backup found at {backup_path}"
            )


def save_checkpoint_backup(checkpoint_path: Path) -> None:
    """
    Save backup of checkpoint before overwriting.

    Args:
        checkpoint_path: Path to checkpoint directory to backup
    """
    if not checkpoint_path.exists():
        return

    backup_path = checkpoint_path.parent / f"{checkpoint_path.name}.backup"

    # Remove old backup if exists
    if backup_path.exists():
        shutil.rmtree(backup_path)

    # Copy current checkpoint to backup
    shutil.copytree(checkpoint_path, backup_path)
    logger.info(f"Checkpoint backup saved to {backup_path}")


def validate_sample(sample: Dict[str, Any], index: int) -> Tuple[bool, Optional[str]]:
    """
    Validate a single training sample.

    Args:
        sample: Sample dictionary to validate
        index: Index of the sample for error reporting

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    required_fields = ["text", "label", "arxiv_id"]
    for field in required_fields:
        if field not in sample:
            return False, f"Sample {index}: Missing required field '{field}'"

    # Check text is not empty
    text = sample.get("text", "")
    if not text or not text.strip():
        return False, f"Sample {index}: Text field is empty"

    # Check text has minimum length (10 words)
    word_count = len(text.split())
    if word_count < 10:
        return False, f"Sample {index}: Text too short ({word_count} words, minimum 10)"

    # Check label is not empty
    label = sample.get("label", "")
    if not label or not label.strip():
        return False, f"Sample {index}: Label field is empty"

    return True, None


def validate_labels(
    samples: List[Dict[str, Any]], expected_labels: Optional[set] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate that all labels are in the expected set.

    Args:
        samples: List of samples to validate
        expected_labels: Optional set of expected label values

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not samples:
        return False, "Sample list is empty"

    # Extract all labels
    labels = set()
    for i, sample in enumerate(samples):
        if "label" not in sample:
            return False, f"Sample {i}: Missing 'label' field"
        labels.add(sample["label"])

    # If expected labels provided, check all labels are in the set
    if expected_labels is not None:
        unexpected_labels = labels - expected_labels
        if unexpected_labels:
            return False, f"Unexpected labels found: {unexpected_labels}"

    return True, None


def validate_dataset(
    samples: List[Dict[str, Any]], dataset_name: str = "dataset"
) -> None:
    """
    Validate entire dataset before training.

    Args:
        samples: List of samples to validate
        dataset_name: Name of the dataset for logging

    Raises:
        DataValidationError: If validation fails
    """
    logger.info(f"Validating {dataset_name} ({len(samples)} samples)...")

    if not samples:
        raise DataValidationError(f"{dataset_name} is empty")

    # Validate each sample
    invalid_samples = []
    for i, sample in enumerate(samples):
        is_valid, error_msg = validate_sample(sample, i)
        if not is_valid:
            invalid_samples.append(error_msg)
            if len(invalid_samples) >= 10:  # Limit error messages
                invalid_samples.append("... and more errors (showing first 10)")
                break

    if invalid_samples:
        error_msg = f"{dataset_name} validation failed:\n" + "\n".join(invalid_samples)
        logger.error(error_msg)
        raise DataValidationError(error_msg)

    # Validate labels
    is_valid, error_msg = validate_labels(samples)
    if not is_valid:
        logger.error(f"{dataset_name} label validation failed: {error_msg}")
        raise DataValidationError(
            f"{dataset_name} label validation failed: {error_msg}"
        )

    logger.info(f"{dataset_name} validation passed")


class TrainingHealthCallback(TrainerCallback):
    """
    Callback to monitor training health and detect divergence.
    """

    def on_log(self, args, state, control, logs=None, **kwargs):
        """Check training health on each log event."""
        if logs and "loss" in logs:
            loss = logs["loss"]
            step = state.global_step
            check_training_health(loss, step)


class TensorBoardCallback(TrainerCallback):
    """
    Callback to log training metrics to TensorBoard.
    """

    def __init__(self, writer: SummaryWriter):
        """
        Initialize TensorBoard callback.

        Args:
            writer: TensorBoard SummaryWriter instance
        """
        self.writer = writer

    def on_log(self, args, state, control, logs=None, **kwargs):
        """Log metrics to TensorBoard on each log event."""
        if logs:
            step = state.global_step

            # Log training loss
            if "loss" in logs:
                self.writer.add_scalar("Loss/train", logs["loss"], step)

            # Log learning rate
            if "learning_rate" in logs:
                self.writer.add_scalar("Learning_Rate", logs["learning_rate"], step)

            # Log validation metrics
            if "eval_loss" in logs:
                self.writer.add_scalar("Loss/validation", logs["eval_loss"], step)

            if "eval_accuracy" in logs:
                self.writer.add_scalar(
                    "Accuracy/validation", logs["eval_accuracy"], step
                )

    def on_train_end(self, args, state, control, **kwargs):
        """Close writer on training end."""
        self.writer.close()


class ClassificationTrainer:
    """
    Trainer for DistilBERT-based classification models on arXiv papers.

    This class handles the complete training pipeline including:
    - Dataset loading and label mapping
    - Model initialization and fine-tuning
    - Training with Hugging Face Trainer API
    - Evaluation with accuracy and F1 metrics
    - Model checkpoint saving

    Attributes:
        model_name (str): Name of the pre-trained model to use
        checkpoint_dir (Path): Directory for saving model checkpoints
        tokenizer: Hugging Face tokenizer (lazy loaded)
        model: Hugging Face model (lazy loaded)
        label_to_id (Dict[str, int]): Mapping from label names to IDs
        id_to_label (Dict[int, str]): Mapping from IDs to label names
        trainer: Hugging Face Trainer instance
    """

    def __init__(
        self,
        model_name: str = "distilbert-base-uncased",
        output_dir: str = "models/classification/arxiv_v1",
    ):
        """
        Initialize the ClassificationTrainer.

        Args:
            model_name: Name of the pre-trained model from Hugging Face
            output_dir: Directory path for saving model checkpoints
        """
        self.model_name = model_name
        self.checkpoint_dir = Path(output_dir)

        # Lazy loading - initialize as None
        self.tokenizer = None
        self.model = None
        self.trainer = None

        # Label mappings (will be built from training data)
        self.label_to_id: Dict[str, int] = {}
        self.id_to_label: Dict[int, str] = {}

        # Create checkpoint directory if it doesn't exist
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        logger.info("ClassificationTrainer initialized")
        logger.info(f"Model: {self.model_name}")
        logger.info(f"Checkpoint directory: {self.checkpoint_dir}")

    def load_datasets(self, data_dir: str) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Load train/val/test splits from JSON files and build label mappings.

        Args:
            data_dir: Directory containing train.json, val.json, test.json files

        Returns:
            Tuple of (train_samples, val_samples, test_samples)

        Raises:
            FileNotFoundError: If required split files are not found
            ValueError: If data format is invalid
        """
        data_path = Path(data_dir)

        # Load train, validation, and test splits
        train_file = data_path / "train.json"
        val_file = data_path / "val.json"
        test_file = data_path / "test.json"

        logger.info(f"Loading datasets from {data_dir}")

        # Check files exist
        for file_path in [train_file, val_file, test_file]:
            if not file_path.exists():
                raise FileNotFoundError(f"Required file not found: {file_path}")

        # Load JSON files
        with open(train_file, "r", encoding="utf-8") as f:
            train_data = json.load(f)
        with open(val_file, "r", encoding="utf-8") as f:
            val_data = json.load(f)
        with open(test_file, "r", encoding="utf-8") as f:
            test_data = json.load(f)

        # Extract samples (handle both direct list and dict with 'samples' key)
        train_samples = (
            train_data
            if isinstance(train_data, list)
            else train_data.get("samples", [])
        )
        val_samples = (
            val_data if isinstance(val_data, list) else val_data.get("samples", [])
        )
        test_samples = (
            test_data if isinstance(test_data, list) else test_data.get("samples", [])
        )

        # Extract unique labels from training data
        unique_labels = set()
        for sample in train_samples:
            if "label" not in sample:
                raise ValueError(f"Sample missing 'label' field: {sample}")
            unique_labels.add(sample["label"])

        # Sort labels for consistent ordering
        sorted_labels = sorted(list(unique_labels))

        # Build bidirectional label mappings
        self.label_to_id = {label: idx for idx, label in enumerate(sorted_labels)}
        self.id_to_label = {idx: label for label, idx in self.label_to_id.items()}

        # Log dataset statistics
        logger.info("Dataset statistics:")
        logger.info(f"  Train samples: {len(train_samples)}")
        logger.info(f"  Validation samples: {len(val_samples)}")
        logger.info(f"  Test samples: {len(test_samples)}")
        logger.info(f"  Number of classes: {len(self.label_to_id)}")
        logger.info(f"  Classes: {sorted_labels}")

        return train_samples, val_samples, test_samples


class ArxivClassificationDataset(Dataset):
    """
    PyTorch Dataset for arXiv paper classification.

    This dataset tokenizes text samples and returns input tensors suitable
    for training with Hugging Face Transformers.

    Attributes:
        samples (List[Dict]): List of samples with 'text' and 'label' fields
        tokenizer: Hugging Face tokenizer for text encoding
        label_to_id (Dict[str, int]): Mapping from label names to IDs
        max_length (int): Maximum sequence length for tokenization
    """

    def __init__(
        self,
        samples: List[Dict],
        tokenizer,
        label_to_id: Dict[str, int],
        max_length: int = 512,
    ):
        """
        Initialize the ArxivClassificationDataset.

        Args:
            samples: List of dictionaries with 'text' and 'label' keys
            tokenizer: Hugging Face tokenizer instance
            label_to_id: Dictionary mapping label names to integer IDs
            max_length: Maximum sequence length (default: 512 for DistilBERT)
        """
        self.samples = samples
        self.tokenizer = tokenizer
        self.label_to_id = label_to_id
        self.max_length = max_length

    def __len__(self) -> int:
        """Return the number of samples in the dataset."""
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get a single tokenized sample.

        Args:
            idx: Index of the sample to retrieve

        Returns:
            Dictionary containing:
                - input_ids: Token IDs for the text
                - attention_mask: Attention mask for the text
                - labels: Label ID for classification
        """
        sample = self.samples[idx]
        text = sample["text"]
        label = sample["label"]

        # Convert label to ID
        label_id = self.label_to_id[label]

        # Tokenize text with truncation and padding
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(label_id, dtype=torch.long),
        }

    def compute_metrics(self, eval_pred) -> Dict[str, float]:
        """
        Compute evaluation metrics for the Trainer.

        This callback is used by Hugging Face Trainer during evaluation.
        For multi-class classification, we use argmax instead of sigmoid.

        Args:
            eval_pred: EvalPrediction object containing predictions and labels

        Returns:
            Dictionary with accuracy metric
        """
        logits, labels = eval_pred

        # For multi-class classification, use argmax to get predictions
        predictions = np.argmax(logits, axis=-1)

        # Compute accuracy
        accuracy = accuracy_score(labels, predictions)

        return {"accuracy": accuracy}

    def train(
        self,
        train_samples: List[Dict],
        val_samples: List[Dict],
        epochs: int = 3,
        batch_size: int = 16,
        learning_rate: float = 2e-5,
        warmup_steps: int = 500,
        weight_decay: float = 0.01,
    ) -> Dict[str, Any]:
        """
        Train the classification model using Hugging Face Trainer with OOM handling.

        Args:
            train_samples: List of training samples
            val_samples: List of validation samples
            epochs: Number of training epochs (default: 3)
            batch_size: Training batch size (default: 16)
            learning_rate: Learning rate (default: 2e-5)
            warmup_steps: Number of warmup steps (default: 500)
            weight_decay: Weight decay for regularization (default: 0.01)

        Returns:
            Dictionary containing training metrics

        Raises:
            DataValidationError: If data validation fails
            TrainingDivergenceError: If training diverges (NaN/Inf loss)
        """
        logger.info("Starting model training...")
        logger.info(f"Training samples: {len(train_samples)}")
        logger.info(f"Validation samples: {len(val_samples)}")
        logger.info(f"Epochs: {epochs}, Batch size: {batch_size}, LR: {learning_rate}")

        # Validate datasets before training
        validate_dataset(train_samples, "Training dataset")
        validate_dataset(val_samples, "Validation dataset")

        # Detect GPU availability
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")

        # Log GPU information if available
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / (
                1024**3
            )
            gpu_memory_allocated = torch.cuda.memory_allocated(0) / (1024**3)
            gpu_memory_reserved = torch.cuda.memory_reserved(0) / (1024**3)
            logger.info(f"GPU detected: {gpu_name}")
            logger.info(f"GPU memory total: {gpu_memory_total:.2f} GB")
            logger.info(f"GPU memory allocated: {gpu_memory_allocated:.2f} GB")
            logger.info(f"GPU memory reserved: {gpu_memory_reserved:.2f} GB")
            logger.info("Mixed precision (fp16) training: ENABLED")
        else:
            logger.info("No GPU detected, using CPU")
            logger.info("Mixed precision (fp16) training: DISABLED")

        # Try training with OOM handling
        try:
            return self._train_with_batch_size(
                train_samples,
                val_samples,
                epochs,
                batch_size,
                learning_rate,
                warmup_steps,
                weight_decay,
            )
        except RuntimeError as e:
            error_msg = str(e).lower()
            if "out of memory" in error_msg or "oom" in error_msg:
                logger.warning(f"Out of memory error occurred: {e}")
                logger.warning(
                    "Clearing GPU cache and retrying with reduced batch size..."
                )

                # Clear GPU cache
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    logger.info("GPU cache cleared")

                # Retry with half batch size
                reduced_batch_size = max(1, batch_size // 2)
                logger.info(f"Retrying training with batch size: {reduced_batch_size}")

                try:
                    return self._train_with_batch_size(
                        train_samples,
                        val_samples,
                        epochs,
                        reduced_batch_size,
                        learning_rate,
                        warmup_steps,
                        weight_decay,
                    )
                except RuntimeError as e2:
                    error_msg2 = str(e2).lower()
                    if "out of memory" in error_msg2 or "oom" in error_msg2:
                        logger.error(
                            "Out of memory error persists even with reduced batch size"
                        )
                        logger.error("Suggestions:")
                        logger.error(
                            f"  1. Further reduce batch size (try {reduced_batch_size // 2})"
                        )
                        logger.error(
                            "  2. Use a smaller model (e.g., distilbert-base-uncased)"
                        )
                        logger.error(
                            "  3. Reduce max sequence length (try 256 instead of 512)"
                        )
                        logger.error(
                            "  4. Use gradient accumulation to simulate larger batches"
                        )
                        raise
                    else:
                        raise
            else:
                raise

    def _train_with_batch_size(
        self,
        train_samples: List[Dict],
        val_samples: List[Dict],
        epochs: int,
        batch_size: int,
        learning_rate: float,
        warmup_steps: int,
        weight_decay: float,
    ) -> Dict[str, Any]:
        """
        Internal method to train with specific batch size.

        This method is separated to allow retry with different batch sizes.
        """
        # Load tokenizer from Hugging Face
        if self.tokenizer is None:
            logger.info(f"Loading tokenizer: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        # Initialize model with number of labels
        if self.model is None:
            num_labels = len(self.label_to_id)
            logger.info(f"Initializing model with {num_labels} labels")
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=num_labels,
                id2label=self.id_to_label,
                label2id=self.label_to_id,
            )

            # Enable gradient checkpointing for memory efficiency
            if hasattr(self.model, "gradient_checkpointing_enable"):
                self.model.gradient_checkpointing_enable()
                logger.info("Gradient checkpointing: ENABLED")
            else:
                logger.info("Gradient checkpointing: NOT SUPPORTED by model")

        # Create PyTorch datasets
        logger.info("Creating PyTorch datasets...")
        train_dataset = ArxivClassificationDataset(
            train_samples, self.tokenizer, self.label_to_id
        )
        val_dataset = ArxivClassificationDataset(
            val_samples, self.tokenizer, self.label_to_id
        )

        # Determine optimal number of workers for DataLoader
        # Use 2 workers on Linux/Mac, 0 on Windows for compatibility
        import platform

        num_workers = 2 if platform.system() != "Windows" else 0
        logger.info(f"DataLoader num_workers: {num_workers}")

        # Create TensorBoard writer
        tensorboard_log_dir = self.checkpoint_dir / "logs"
        tensorboard_log_dir.mkdir(parents=True, exist_ok=True)
        writer = SummaryWriter(log_dir=str(tensorboard_log_dir))
        logger.info(f"TensorBoard logging to: {tensorboard_log_dir}")

        # Configure training arguments
        training_args = TrainingArguments(
            output_dir=str(self.checkpoint_dir),
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            warmup_steps=warmup_steps,
            weight_decay=weight_decay,
            # Evaluation and saving strategy
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="accuracy",
            # Mixed precision training (fp16) if GPU available
            fp16=torch.cuda.is_available(),
            # DataLoader settings
            dataloader_num_workers=num_workers,
            # Logging
            logging_dir=str(self.checkpoint_dir / "logs"),
            logging_steps=100,
            logging_first_step=True,
            # Disable tqdm for cleaner logs
            disable_tqdm=False,
        )

        # Initialize Trainer with callbacks
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=self.compute_metrics,
            callbacks=[
                EarlyStoppingCallback(early_stopping_patience=2),
                TrainingHealthCallback(),  # Monitor for training divergence
                TensorBoardCallback(writer),  # TensorBoard logging
            ],
        )

        # Log model graph to TensorBoard
        try:
            # Create a sample input for the model graph
            sample_input = train_dataset[0]
            sample_batch = {
                "input_ids": sample_input["input_ids"].unsqueeze(0),
                "attention_mask": sample_input["attention_mask"].unsqueeze(0),
            }
            # Move to same device as model
            device = next(self.model.parameters()).device
            sample_batch = {k: v.to(device) for k, v in sample_batch.items()}

            writer.add_graph(
                self.model, (sample_batch["input_ids"], sample_batch["attention_mask"])
            )
            logger.info("Model graph logged to TensorBoard")
        except Exception as e:
            logger.warning(f"Could not log model graph to TensorBoard: {e}")

        # Log GPU memory before training
        if torch.cuda.is_available():
            gpu_memory_allocated = torch.cuda.memory_allocated(0) / (1024**3)
            gpu_memory_reserved = torch.cuda.memory_reserved(0) / (1024**3)
            logger.info(
                f"GPU memory before training - Allocated: {gpu_memory_allocated:.2f} GB, Reserved: {gpu_memory_reserved:.2f} GB"
            )

        # Train the model
        logger.info("Starting training...")
        train_result = self.trainer.train()

        # Log GPU memory after training
        if torch.cuda.is_available():
            gpu_memory_allocated = torch.cuda.memory_allocated(0) / (1024**3)
            gpu_memory_reserved = torch.cuda.memory_reserved(0) / (1024**3)
            gpu_memory_peak = torch.cuda.max_memory_allocated(0) / (1024**3)
            logger.info(
                f"GPU memory after training - Allocated: {gpu_memory_allocated:.2f} GB, Reserved: {gpu_memory_reserved:.2f} GB"
            )
            logger.info(f"GPU memory peak usage: {gpu_memory_peak:.2f} GB")

        # Log training results
        logger.info("Training completed!")
        logger.info(f"Training loss: {train_result.training_loss:.4f}")
        logger.info(f"Training time: {train_result.metrics['train_runtime']:.2f}s")
        logger.info(
            f"Samples per second: {train_result.metrics['train_samples_per_second']:.2f}"
        )

        # Evaluate on validation set
        logger.info("Evaluating on validation set...")
        eval_result = self.trainer.evaluate()
        logger.info(f"Validation accuracy: {eval_result['eval_accuracy']:.4f}")

        return {
            "train_loss": train_result.training_loss,
            "train_runtime": train_result.metrics["train_runtime"],
            "train_samples_per_second": train_result.metrics[
                "train_samples_per_second"
            ],
            "eval_accuracy": eval_result["eval_accuracy"],
            "eval_loss": eval_result["eval_loss"],
            "batch_size_used": batch_size,
        }

    def evaluate(self, test_samples: List[Dict]) -> Dict[str, Any]:
        """
        Evaluate the trained model on the test set.

        Args:
            test_samples: List of test samples

        Returns:
            Dictionary containing evaluation metrics

        Raises:
            ValueError: If model or tokenizer not initialized
        """
        if self.model is None or self.tokenizer is None:
            raise ValueError(
                "Model and tokenizer must be initialized before evaluation"
            )

        logger.info(f"Evaluating on test set ({len(test_samples)} samples)...")

        # Create PyTorch dataset for test data
        test_dataset = ArxivClassificationDataset(
            test_samples, self.tokenizer, self.label_to_id
        )

        # Use Trainer.predict() for inference
        predictions_output = self.trainer.predict(test_dataset)

        # Extract predictions and labels
        logits = predictions_output.predictions
        labels = predictions_output.label_ids

        # Get predicted classes
        predictions = np.argmax(logits, axis=-1)

        # Compute overall accuracy
        accuracy = accuracy_score(labels, predictions)

        # Compute macro F1 score
        macro_f1 = f1_score(labels, predictions, average="macro")

        # Generate classification report
        target_names = [self.id_to_label[i] for i in range(len(self.id_to_label))]
        report = classification_report(
            labels, predictions, target_names=target_names, output_dict=True
        )

        # Log test metrics
        logger.info(f"Test accuracy: {accuracy:.4f}")
        logger.info(f"Test macro F1: {macro_f1:.4f}")

        # Log per-class metrics
        logger.info("\nPer-class metrics:")
        for label_name in target_names:
            metrics = report[label_name]
            logger.info(
                f"  {label_name}: "
                f"precision={metrics['precision']:.3f}, "
                f"recall={metrics['recall']:.3f}, "
                f"f1={metrics['f1-score']:.3f}"
            )

        # Prepare evaluation results
        eval_results = {
            "test_accuracy": accuracy,
            "test_macro_f1": macro_f1,
            "test_samples": len(test_samples),
            "classification_report": report,
            "timestamp": datetime.now().isoformat(),
        }

        # Save evaluation results to JSON file
        results_file = self.checkpoint_dir / "test_results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(eval_results, f, indent=2)

        logger.info(f"Evaluation results saved to {results_file}")

        return eval_results

    def save_checkpoint(self) -> None:
        """
        Save model checkpoint with all required files and backup.

        This method saves:
        - Model weights (pytorch_model.bin)
        - Model configuration (config.json)
        - Tokenizer files
        - Label mapping (label_map.json)
        - Backup of previous checkpoint (if exists)

        Raises:
            ValueError: If model or tokenizer not initialized
        """
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model and tokenizer must be initialized before saving")

        logger.info(f"Saving checkpoint to {self.checkpoint_dir}")

        # Save backup of existing checkpoint before overwriting
        if self.checkpoint_dir.exists():
            save_checkpoint_backup(self.checkpoint_dir)

        # Save model with save_pretrained()
        self.model.save_pretrained(self.checkpoint_dir)
        logger.info("Model saved")

        # Save tokenizer with save_pretrained()
        self.tokenizer.save_pretrained(self.checkpoint_dir)
        logger.info("Tokenizer saved")

        # Save label mapping to label_map.json
        label_map = {"id_to_label": self.id_to_label, "label_to_id": self.label_to_id}
        label_map_file = self.checkpoint_dir / "label_map.json"
        with open(label_map_file, "w", encoding="utf-8") as f:
            json.dump(label_map, f, indent=2)
        logger.info(f"Label mapping saved to {label_map_file}")

        # Verify all required files exist
        required_files = ["pytorch_model.bin", "config.json", "label_map.json"]

        missing_files = []
        for filename in required_files:
            file_path = self.checkpoint_dir / filename
            if not file_path.exists():
                missing_files.append(filename)

        if missing_files:
            logger.warning(f"Missing files after save: {missing_files}")
        else:
            logger.info("All required files verified")

        # Log checkpoint size
        total_size = sum(
            f.stat().st_size for f in self.checkpoint_dir.rglob("*") if f.is_file()
        )
        size_mb = total_size / (1024 * 1024)
        logger.info(f"Checkpoint size: {size_mb:.2f} MB")
        logger.info(f"Checkpoint location: {self.checkpoint_dir.absolute()}")

    def load_checkpoint(self, checkpoint_path: Optional[str] = None) -> None:
        """
        Load model checkpoint with validation.

        Args:
            checkpoint_path: Path to checkpoint directory (default: self.checkpoint_dir)

        Raises:
            CheckpointValidationError: If checkpoint validation fails
        """
        if checkpoint_path is None:
            checkpoint_path = self.checkpoint_dir
        else:
            checkpoint_path = Path(checkpoint_path)

        # Validate and load checkpoint
        load_checkpoint_with_validation(checkpoint_path)

        # Load tokenizer
        logger.info("Loading tokenizer from checkpoint...")
        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)

        # Load model
        logger.info("Loading model from checkpoint...")
        self.model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path)

        # Load label mapping
        label_map_file = checkpoint_path / "label_map.json"
        if label_map_file.exists():
            with open(label_map_file, "r", encoding="utf-8") as f:
                label_map = json.load(f)
                # Convert string keys back to integers for id_to_label
                self.id_to_label = {
                    int(k): v for k, v in label_map["id_to_label"].items()
                }
                self.label_to_id = label_map["label_to_id"]
            logger.info("Label mapping loaded")
        else:
            logger.warning("Label mapping file not found, using model's label mapping")
            self.id_to_label = self.model.config.id2label
            self.label_to_id = self.model.config.label2id

        logger.info(f"Checkpoint loaded successfully from {checkpoint_path}")


def main():
    """
    Main function for command-line usage.

    Example usage:
        python train_classification.py
    """
    import argparse

    parser = argparse.ArgumentParser(description="Train arXiv classification model")
    parser.add_argument(
        "--data-dir",
        type=str,
        default="backend/data/splits/arxiv_classification",
        help="Directory containing train/val/test splits",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="backend/models/classification/arxiv_v1.0.0",
        help="Output directory for model checkpoint",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="distilbert-base-uncased",
        help="Pre-trained model name from Hugging Face",
    )
    parser.add_argument(
        "--epochs", type=int, default=3, help="Number of training epochs"
    )
    parser.add_argument(
        "--batch-size", type=int, default=16, help="Training batch size"
    )
    parser.add_argument(
        "--learning-rate", type=float, default=2e-5, help="Learning rate"
    )

    args = parser.parse_args()

    # Initialize trainer
    trainer = ClassificationTrainer(
        model_name=args.model_name, output_dir=args.output_dir
    )

    # Load datasets
    train_samples, val_samples, test_samples = trainer.load_datasets(args.data_dir)

    # Train model
    train_metrics = trainer.train(
        train_samples,
        val_samples,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
    )

    # Save checkpoint
    trainer.save_checkpoint()

    # Evaluate on test set
    test_metrics = trainer.evaluate(test_samples)

    logger.info("\n" + "=" * 50)
    logger.info("Training Complete!")
    logger.info("=" * 50)
    logger.info(f"Final validation accuracy: {train_metrics['eval_accuracy']:.4f}")
    logger.info(f"Final test accuracy: {test_metrics['test_accuracy']:.4f}")
    logger.info(f"Final test F1 (macro): {test_metrics['test_macro_f1']:.4f}")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
