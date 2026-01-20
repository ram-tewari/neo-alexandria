"""
Classification Model Training Script

This script trains the multi-label classification model for taxonomy assignment
using the MLClassificationService. It loads labeled data from the test dataset,
optionally augments it if too small, trains the model, and saves the checkpoint.

Usage:
    python backend/scripts/train_classification.py [options]

Examples:
    # Train with default settings
    python backend/scripts/train_classification.py

    # Train with custom hyperparameters
    python backend/scripts/train_classification.py --epochs 5 --batch-size 32 --learning-rate 3e-5

    # Train with custom data path
    python backend/scripts/train_classification.py --data-path path/to/data.json

    # Train with data augmentation
    python backend/scripts/train_classification.py --augment --target-size 500
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.prepare_training_data import (
    load_classification_test_data,
    augment_classification_data,
    validate_data_format,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Train classification model for taxonomy assignment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train with default settings
  python backend/scripts/train_classification.py

  # Train with custom hyperparameters
  python backend/scripts/train_classification.py --epochs 5 --batch-size 32

  # Train with data augmentation
  python backend/scripts/train_classification.py --augment --target-size 500
        """,
    )

    # Data arguments
    parser.add_argument(
        "--data-path",
        type=str,
        default=None,
        help="Path to classification test data JSON file (default: tests/ml_benchmarks/datasets/classification_test.json)",
    )

    parser.add_argument(
        "--augment",
        action="store_true",
        help="Enable data augmentation for small datasets",
    )

    parser.add_argument(
        "--target-size",
        type=int,
        default=500,
        help="Target dataset size for augmentation (default: 500)",
    )

    # Training hyperparameters
    parser.add_argument(
        "--epochs", type=int, default=3, help="Number of training epochs (default: 3)"
    )

    parser.add_argument(
        "--batch-size", type=int, default=16, help="Training batch size (default: 16)"
    )

    parser.add_argument(
        "--learning-rate",
        type=float,
        default=2e-5,
        help="Learning rate for optimizer (default: 2e-5)",
    )

    # Model arguments
    parser.add_argument(
        "--model-name",
        type=str,
        default="distilbert-base-uncased",
        help="Base model name from Hugging Face (default: distilbert-base-uncased)",
    )

    parser.add_argument(
        "--model-version",
        type=str,
        default="benchmark_v1",
        help="Model version identifier for checkpoint (default: benchmark_v1)",
    )

    parser.add_argument(
        "--pretrained-model",
        type=str,
        default=None,
        help="Path to pre-trained model checkpoint for fine-tuning (optional)",
    )

    # Output arguments
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Custom output directory for model checkpoint (default: models/classification/{model_version})",
    )

    return parser.parse_args()


def load_classification_data(data_path: str = None) -> List[Tuple[str, List[str]]]:
    """
    Load classification data from test dataset.

    This function uses the prepare_training_data utilities to load and validate
    the classification test dataset. It logs dataset statistics for monitoring.

    Args:
        data_path: Optional path to classification data JSON file

    Returns:
        List of (text, [taxonomy_node_ids]) tuples

    Raises:
        FileNotFoundError: If data file not found
        ValueError: If data format is invalid
    """
    try:
        # Load data using utility function
        labeled_data = load_classification_test_data(data_path)

        # Log dataset statistics
        logger.info("Dataset Statistics:")
        logger.info(f"  Total samples: {len(labeled_data)}")

        # Count unique taxonomy nodes
        all_taxonomy_ids = set()
        label_counts = {}

        for text, taxonomy_ids in labeled_data:
            all_taxonomy_ids.update(taxonomy_ids)
            for tid in taxonomy_ids:
                label_counts[tid] = label_counts.get(tid, 0) + 1

        logger.info(f"  Unique taxonomy nodes: {len(all_taxonomy_ids)}")
        logger.info(
            f"  Average labels per sample: {sum(len(t) for _, t in labeled_data) / len(labeled_data):.2f}"
        )

        # Show label distribution (top 5)
        top_labels = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        logger.info("  Top 5 most common labels:")
        for label, count in top_labels:
            logger.info(f"    {label}: {count} samples")

        # Check for data quality issues
        empty_texts = sum(1 for text, _ in labeled_data if not text.strip())
        if empty_texts > 0:
            logger.warning(f"  Warning: {empty_texts} samples have empty text")

        single_label = sum(1 for _, labels in labeled_data if len(labels) == 1)
        multi_label = len(labeled_data) - single_label
        logger.info(f"  Single-label samples: {single_label}")
        logger.info(f"  Multi-label samples: {multi_label}")

        return labeled_data

    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e}")
        logger.error("Please ensure the classification test dataset exists at:")
        logger.error("  backend/tests/ml_benchmarks/datasets/classification_test.json")
        raise

    except ValueError as e:
        logger.error(f"Invalid data format: {e}")
        raise

    except Exception as e:
        logger.error(f"Error loading classification data: {e}")
        raise


def augment_dataset(
    data: List[Tuple[str, List[str]]], target_size: int = 500
) -> List[Tuple[str, List[str]]]:
    """
    Augment dataset if it's too small.

    This function uses text variation techniques to create additional training
    examples while maintaining label consistency. It only augments if the
    dataset is smaller than the target size.

    Args:
        data: Original labeled data
        target_size: Minimum desired dataset size (default: 500)

    Returns:
        Augmented dataset (original + synthetic examples)
    """
    original_size = len(data)

    if original_size >= target_size:
        logger.info(
            f"Dataset size ({original_size}) already meets target ({target_size})"
        )
        logger.info("Skipping augmentation")
        return data

    logger.info(f"Dataset size ({original_size}) is below target ({target_size})")
    logger.info("Applying data augmentation...")

    try:
        # Use utility function for augmentation
        augmented_data = augment_classification_data(
            data=data,
            target_size=target_size,
            multiplier=3,  # Create up to 3 variations per sample
        )

        synthetic_count = len(augmented_data) - original_size
        logger.info(f"Created {synthetic_count} synthetic examples")
        logger.info(f"Final dataset size: {len(augmented_data)}")

        # Verify label consistency
        original_labels = set()
        for _, labels in data:
            original_labels.update(labels)

        augmented_labels = set()
        for _, labels in augmented_data:
            augmented_labels.update(labels)

        if original_labels == augmented_labels:
            logger.info("✓ Label consistency verified")
        else:
            logger.warning("⚠ Label set changed during augmentation")
            logger.warning(f"  Original labels: {len(original_labels)}")
            logger.warning(f"  Augmented labels: {len(augmented_labels)}")

        return augmented_data

    except Exception as e:
        logger.error(f"Error during data augmentation: {e}")
        logger.warning("Continuing with original dataset")
        return data


def train_classification_model(
    service,
    labeled_data: List[Tuple[str, List[str]]],
    epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 2e-5,
) -> Dict[str, float]:
    """
    Train classification model using MLClassificationService.

    This function initializes the MLClassificationService and calls its
    fine_tune() method with the provided hyperparameters. The service
    handles all training logic including:
    - Building label mappings
    - Tokenization
    - Model initialization
    - Training loop
    - Evaluation
    - Checkpoint saving

    Args:
        service: MLClassificationService instance
        labeled_data: List of (text, [taxonomy_node_ids]) tuples
        epochs: Number of training epochs (default: 3)
        batch_size: Training batch size (default: 16)
        learning_rate: Learning rate for optimizer (default: 2e-5)

    Returns:
        Dictionary with evaluation metrics (f1, precision, recall, loss)

    Raises:
        Exception: If training fails
    """
    logger.info("Starting model training...")
    logger.info("Training configuration:")
    logger.info(f"  Samples: {len(labeled_data)}")
    logger.info(f"  Epochs: {epochs}")
    logger.info(f"  Batch size: {batch_size}")
    logger.info(f"  Learning rate: {learning_rate}")
    logger.info("")

    try:
        # Call fine_tune method from MLClassificationService
        # This handles all training logic internally
        metrics = service.fine_tune(
            labeled_data=labeled_data,
            unlabeled_data=None,  # No semi-supervised learning for now
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
        )

        logger.info("Training completed successfully")
        return metrics

    except ImportError:
        logger.error("Required ML libraries not installed")
        logger.error("Please install: pip install transformers torch scikit-learn")
        raise

    except RuntimeError as e:
        logger.error(f"Training failed: {e}")
        logger.info("Troubleshooting tips:")
        logger.info("  - Try reducing batch size (--batch-size 8)")
        logger.info("  - Try reducing learning rate (--learning-rate 1e-5)")
        logger.info("  - Ensure you have enough memory (8GB+ recommended)")
        logger.info("  - Check if CUDA is available for GPU acceleration")
        raise

    except Exception as e:
        logger.error(f"Unexpected error during training: {e}")
        raise


def verify_checkpoint(checkpoint_dir: Path) -> bool:
    """
    Verify that model checkpoint was saved correctly.

    This function checks that all required checkpoint files exist:
    - pytorch_model.bin: Model weights
    - config.json: Model configuration
    - tokenizer_config.json: Tokenizer configuration
    - vocab.txt: Vocabulary
    - label_map.json: Label mappings

    Args:
        checkpoint_dir: Path to checkpoint directory

    Returns:
        True if all required files exist, False otherwise
    """
    logger.info("Verifying checkpoint files...")

    if not checkpoint_dir.exists():
        logger.error(f"Checkpoint directory does not exist: {checkpoint_dir}")
        return False

    # Required files for the checkpoint (either pytorch_model.bin or model.safetensors)
    required_files = [
        "config.json",  # Model configuration
        "label_map.json",  # Label mappings
    ]

    # Check for model weights (either format)
    if (checkpoint_dir / "pytorch_model.bin").exists():
        size = (checkpoint_dir / "pytorch_model.bin").stat().st_size
        logger.info(f"  ✓ pytorch_model.bin ({size:,} bytes)")
    elif (checkpoint_dir / "model.safetensors").exists():
        size = (checkpoint_dir / "model.safetensors").stat().st_size
        logger.info(f"  ✓ model.safetensors ({size:,} bytes)")
    else:
        logger.error(
            "  ✗ Model weights - MISSING (neither pytorch_model.bin nor model.safetensors found)"
        )
        return False

    # Optional but expected files
    optional_files = [
        "tokenizer_config.json",  # Tokenizer configuration
        "vocab.txt",  # Vocabulary
        "special_tokens_map.json",  # Special tokens
    ]

    all_valid = True

    # Check required files
    for filename in required_files:
        filepath = checkpoint_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            logger.info(f"  ✓ {filename} ({size:,} bytes)")
        else:
            logger.error(f"  ✗ {filename} - MISSING")
            all_valid = False

    # Check optional files (warn but don't fail)
    for filename in optional_files:
        filepath = checkpoint_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            logger.info(f"  ✓ {filename} ({size:,} bytes)")
        else:
            logger.warning(f"  ⚠ {filename} - missing (optional)")

    if all_valid:
        logger.info("Checkpoint verification passed")
    else:
        logger.error("Checkpoint verification failed - missing required files")

    return all_valid


def main():
    """
    Main training pipeline.

    Steps:
    1. Parse command-line arguments
    2. Load classification data from test dataset
    3. Optionally augment data if dataset is too small
    4. Validate data format
    5. Initialize MLClassificationService
    6. Train model using fine_tune() method
    7. Evaluate and report metrics
    8. Verify checkpoint saved successfully
    """
    logger.info("=" * 70)
    logger.info("Classification Model Training")
    logger.info("=" * 70)

    # Step 1: Parse arguments
    args = parse_arguments()

    logger.info("Configuration:")
    logger.info(f"  Data path: {args.data_path or 'default'}")
    logger.info(f"  Augmentation: {args.augment}")
    if args.augment:
        logger.info(f"  Target size: {args.target_size}")
    logger.info(f"  Epochs: {args.epochs}")
    logger.info(f"  Batch size: {args.batch_size}")
    logger.info(f"  Learning rate: {args.learning_rate}")
    logger.info(f"  Model: {args.model_name}")
    logger.info(f"  Version: {args.model_version}")
    logger.info("")

    try:
        # Step 2: Load classification data
        logger.info("Step 1/5: Loading classification data...")
        labeled_data = load_classification_data(args.data_path)
        logger.info(f"Loaded {len(labeled_data)} labeled examples")
        logger.info("")

        # Step 3: Optionally augment data
        if args.augment:
            logger.info("Step 2/5: Augmenting dataset...")
            labeled_data = augment_dataset(labeled_data, args.target_size)
            logger.info(f"Dataset size after augmentation: {len(labeled_data)}")
            logger.info("")
        else:
            logger.info("Step 2/5: Skipping data augmentation")
            logger.info("")

        # Step 4: Validate data format
        logger.info("Step 3/5: Validating data format...")
        if not validate_data_format(labeled_data, "classification"):
            logger.error("Data validation failed!")
            sys.exit(1)
        logger.info("Data validation passed")
        logger.info("")

        # Step 5: Initialize MLClassificationService
        logger.info("Step 4/5: Initializing MLClassificationService...")

        # Import directly to avoid circular imports
        import importlib.util

        # Load MLClassificationService directly
        service_path = (
            Path(__file__).parent.parent
            / "app"
            / "services"
            / "ml_classification_service.py"
        )
        spec = importlib.util.spec_from_file_location(
            "ml_classification_service", service_path
        )
        ml_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ml_module)
        MLClassificationService = ml_module.MLClassificationService

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # Create database session (using SQLite for training)
        db_path = Path("backend.db")
        if not db_path.exists():
            logger.warning(f"Database not found at {db_path}, using in-memory database")
            engine = create_engine("sqlite:///:memory:")
        else:
            engine = create_engine(f"sqlite:///{db_path}")

        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()

        # Initialize service
        if args.pretrained_model:
            logger.info(f"Using pre-trained model from: {args.pretrained_model}")
            # For fine-tuning, we'll load the pre-trained model in the service
            service = MLClassificationService(
                db=db,
                model_name=args.pretrained_model,  # Use pre-trained model path
                model_version=args.model_version,
            )
        else:
            service = MLClassificationService(
                db=db, model_name=args.model_name, model_version=args.model_version
            )
        logger.info("Service initialized successfully")
        logger.info("")

        # Step 6: Train model
        logger.info("Step 5/5: Training model...")
        logger.info("This may take several minutes...")
        logger.info("")

        metrics = train_classification_model(
            service=service,
            labeled_data=labeled_data,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
        )

        logger.info("")
        logger.info("=" * 70)
        logger.info("Training Complete!")
        logger.info("=" * 70)

        # Step 7: Report metrics
        logger.info("Final Evaluation Metrics:")
        logger.info(f"  F1 Score:  {metrics['f1']:.4f}")
        logger.info(f"  Precision: {metrics['precision']:.4f}")
        logger.info(f"  Recall:    {metrics['recall']:.4f}")
        logger.info(f"  Loss:      {metrics.get('loss', 0.0):.4f}")
        logger.info("")

        # Step 8: Verify checkpoint
        checkpoint_dir = Path("models") / "classification" / args.model_version
        if verify_checkpoint(checkpoint_dir):
            logger.info(f"✓ Model checkpoint saved successfully to: {checkpoint_dir}")
            logger.info("")
            logger.info("You can now run the benchmark tests:")
            logger.info(
                "  pytest backend/tests/ml_benchmarks/test_classification_metrics.py"
            )
        else:
            logger.error(f"✗ Model checkpoint verification failed at: {checkpoint_dir}")
            sys.exit(1)

        logger.info("")
        logger.info("=" * 70)

    except KeyboardInterrupt:
        logger.warning("\nTraining interrupted by user")
        sys.exit(1)

    except Exception as e:
        logger.error(f"\nTraining failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
