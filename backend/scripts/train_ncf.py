"""
NCF Model Training Script

This script trains a Neural Collaborative Filtering (NCF) model on user-item
interaction data. It supports loading data from JSON files or database,
implements negative sampling for implicit feedback, and evaluates the model
using ranking metrics.

Usage:
    python backend/scripts/train_ncf.py [options]

Examples:
    # Train with default settings
    python backend/scripts/train_ncf.py

    # Train with custom hyperparameters
    python backend/scripts/train_ncf.py --epochs 20 --batch-size 512 --lr 0.001

    # Train with custom data path
    python backend/scripts/train_ncf.py --data-path path/to/data.json

    # Train with custom output directory
    python backend/scripts/train_ncf.py --output-dir models/custom/
"""

import argparse
import json
import logging
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np

# Add parent directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import NCF model directly to avoid circular imports
import importlib.util

spec = importlib.util.spec_from_file_location(
    "ncf_model", backend_dir / "app" / "models" / "ncf_model.py"
)
ncf_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ncf_module)
NCFModel = ncf_module.NCFModel

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
        description="Train Neural Collaborative Filtering (NCF) model",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Training hyperparameters
    parser.add_argument(
        "--epochs", type=int, default=10, help="Number of training epochs"
    )

    parser.add_argument(
        "--batch-size", type=int, default=256, help="Training batch size"
    )

    parser.add_argument(
        "--lr",
        "--learning-rate",
        type=float,
        default=0.001,
        dest="learning_rate",
        help="Learning rate for Adam optimizer",
    )

    # Model architecture
    parser.add_argument(
        "--embedding-dim",
        type=int,
        default=64,
        help="Dimension of user and item embeddings",
    )

    parser.add_argument(
        "--hidden-layers",
        type=int,
        nargs="+",
        default=[128, 64, 32],
        help="Hidden layer sizes for MLP (space-separated)",
    )

    # Data parameters
    parser.add_argument(
        "--data-path",
        type=str,
        default="backend/tests/ml_benchmarks/datasets/recommendation_test.json",
        help="Path to interaction data JSON file",
    )

    parser.add_argument(
        "--negative-samples",
        type=int,
        default=4,
        help="Number of negative samples per positive interaction",
    )

    parser.add_argument(
        "--val-split",
        type=float,
        default=0.2,
        help="Validation set split ratio (0.0-1.0)",
    )

    # Output parameters
    parser.add_argument(
        "--output-dir",
        type=str,
        default="backend/models",
        help="Directory to save trained model checkpoint",
    )

    parser.add_argument(
        "--model-name",
        type=str,
        default="ncf_benchmark_v1.pt",
        help="Name of the model checkpoint file",
    )

    # Other options
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility"
    )

    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "cuda", "cpu"],
        help="Device to use for training (auto, cuda, or cpu)",
    )

    return parser.parse_args()


def load_interaction_data(
    data_path: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, int], Dict[str, int]]:
    """
    Load user-item interaction data from JSON file.

    This function loads interaction data and creates ID mappings for users
    and items. The mappings convert string IDs to integer indices for use
    in embedding layers.

    Args:
        data_path: Path to JSON file containing interaction data

    Returns:
        Tuple containing:
        - List of interaction dictionaries with keys: user_id, item_id, timestamp, etc.
        - User ID to index mapping (dict[str, int])
        - Item ID to index mapping (dict[str, int])

    Raises:
        FileNotFoundError: If data file doesn't exist
        ValueError: If data format is invalid
    """
    data_file = Path(data_path)

    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    logger.info(f"Loading interaction data from {data_path}")

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")

    # Extract interactions
    if "interactions" not in data:
        raise ValueError("Missing 'interactions' key in data file")

    interactions = data["interactions"]

    if not isinstance(interactions, list) or len(interactions) == 0:
        raise ValueError("'interactions' must be a non-empty list")

    logger.info(f"Loaded {len(interactions)} interactions")

    # Build user and item ID sets
    user_ids = set()
    item_ids = set()

    for interaction in interactions:
        user_id = interaction.get("user_id")
        item_id = interaction.get("resource_id")

        if user_id:
            user_ids.add(user_id)
        if item_id:
            item_ids.add(item_id)

    # Create ID mappings (sorted for consistency)
    user_id_map = {user_id: idx for idx, user_id in enumerate(sorted(user_ids))}
    item_id_map = {item_id: idx for idx, item_id in enumerate(sorted(item_ids))}

    logger.info(f"Found {len(user_id_map)} unique users")
    logger.info(f"Found {len(item_id_map)} unique items")

    # Calculate dataset statistics
    density = len(interactions) / (len(user_id_map) * len(item_id_map))
    logger.info(f"Dataset density: {density:.4f}")

    return interactions, user_id_map, item_id_map


def split_train_val(
    interactions: List[Dict[str, Any]], val_split: float = 0.2, seed: int = 42
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Split interactions into training and validation sets.

    Args:
        interactions: List of interaction dictionaries
        val_split: Fraction of data to use for validation (0.0-1.0)
        seed: Random seed for reproducibility

    Returns:
        Tuple of (train_interactions, val_interactions)
    """
    # Shuffle interactions
    random.seed(seed)
    shuffled = interactions.copy()
    random.shuffle(shuffled)

    # Split
    val_size = int(len(shuffled) * val_split)
    train_size = len(shuffled) - val_size

    train_interactions = shuffled[:train_size]
    val_interactions = shuffled[train_size:]

    logger.info(f"Split data: {train_size} train, {val_size} validation")

    return train_interactions, val_interactions


def create_negative_samples(
    interactions: List[Dict[str, Any]],
    user_id_map: Dict[str, int],
    item_id_map: Dict[str, int],
    num_negatives: int = 4,
    seed: int = 42,
) -> List[Tuple[int, int, int]]:
    """
    Create negative samples for implicit feedback training.

    For each positive interaction, generates N negative samples by randomly
    selecting items the user has not interacted with. This creates a balanced
    dataset for binary classification.

    Args:
        interactions: List of positive interaction dictionaries
        user_id_map: Mapping from user ID strings to indices
        item_id_map: Mapping from item ID strings to indices
        num_negatives: Number of negative samples per positive interaction
        seed: Random seed for reproducibility

    Returns:
        List of (user_idx, item_idx, label) tuples where label is 1 for
        positive and 0 for negative interactions
    """
    random.seed(seed)

    logger.info(f"Creating negative samples (ratio 1:{num_negatives})")

    # Build set of positive user-item pairs for fast lookup
    positive_pairs = set()
    for interaction in interactions:
        user_id = interaction.get("user_id")
        item_id = interaction.get("resource_id")

        if user_id in user_id_map and item_id in item_id_map:
            user_idx = user_id_map[user_id]
            item_idx = item_id_map[item_id]
            positive_pairs.add((user_idx, item_idx))

    logger.info(f"Found {len(positive_pairs)} positive interactions")

    # Create training samples
    samples = []
    all_item_indices = list(range(len(item_id_map)))

    # Add positive samples
    for user_idx, item_idx in positive_pairs:
        samples.append((user_idx, item_idx, 1))

    # Add negative samples
    negative_count = 0
    max_attempts = len(positive_pairs) * num_negatives * 10  # Safety limit
    attempts = 0

    for user_idx, item_idx in positive_pairs:
        # Generate num_negatives negative samples for this user
        user_negatives = 0

        while user_negatives < num_negatives and attempts < max_attempts:
            attempts += 1

            # Randomly select an item
            neg_item_idx = random.choice(all_item_indices)

            # Check if this is a negative sample (not in positive set)
            if (user_idx, neg_item_idx) not in positive_pairs:
                samples.append((user_idx, neg_item_idx, 0))
                user_negatives += 1
                negative_count += 1

    logger.info(f"Created {negative_count} negative samples")
    logger.info(
        f"Total samples: {len(samples)} (positive: {len(positive_pairs)}, negative: {negative_count})"
    )
    logger.info(
        f"Positive:Negative ratio: 1:{negative_count / len(positive_pairs):.2f}"
    )

    # Shuffle samples
    random.shuffle(samples)

    return samples


class NCFDataset(Dataset):
    """
    PyTorch Dataset for NCF training.

    Wraps the list of (user_idx, item_idx, label) tuples for use with
    PyTorch DataLoader.
    """

    def __init__(self, samples: List[Tuple[int, int, int]]):
        """
        Initialize dataset.

        Args:
            samples: List of (user_idx, item_idx, label) tuples
        """
        self.samples = samples

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        user_idx, item_idx, label = self.samples[idx]
        return (
            torch.tensor(user_idx, dtype=torch.long),
            torch.tensor(item_idx, dtype=torch.long),
            torch.tensor(label, dtype=torch.float32),
        )


def train_ncf_model(
    train_samples: List[Tuple[int, int, int]],
    val_samples: List[Tuple[int, int, int]],
    num_users: int,
    num_items: int,
    embedding_dim: int = 64,
    hidden_layers: List[int] = None,
    epochs: int = 10,
    batch_size: int = 256,
    learning_rate: float = 0.001,
    device: str = "auto",
    seed: int = 42,
) -> Tuple[NCFModel, Dict[str, List[float]]]:
    """
    Train NCF model with given data.

    Args:
        train_samples: Training samples as (user_idx, item_idx, label) tuples
        val_samples: Validation samples as (user_idx, item_idx, label) tuples
        num_users: Number of unique users
        num_items: Number of unique items
        embedding_dim: Dimension of embeddings
        hidden_layers: List of hidden layer sizes
        epochs: Number of training epochs
        batch_size: Training batch size
        learning_rate: Learning rate for optimizer
        device: Device to use ('auto', 'cuda', or 'cpu')
        seed: Random seed

    Returns:
        Tuple of (trained_model, training_history)
        training_history contains lists of train_loss and val_loss per epoch
    """
    if hidden_layers is None:
        hidden_layers = [128, 64, 32]

    # Set random seeds
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)

    # Determine device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"

    device = torch.device(device)
    logger.info(f"Using device: {device}")

    # Create datasets and dataloaders
    train_dataset = NCFDataset(train_samples)
    val_dataset = NCFDataset(val_samples)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,  # Use 0 for Windows compatibility
    )

    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False, num_workers=0
    )

    logger.info(
        f"Created dataloaders: {len(train_loader)} train batches, {len(val_loader)} val batches"
    )

    # Initialize model
    model = NCFModel(
        num_users=num_users,
        num_items=num_items,
        embedding_dim=embedding_dim,
        hidden_layers=hidden_layers,
    )
    model = model.to(device)

    logger.info("Initialized NCF model:")
    logger.info(f"  Users: {num_users}, Items: {num_items}")
    logger.info(f"  Embedding dim: {embedding_dim}")
    logger.info(f"  Hidden layers: {hidden_layers}")

    # Initialize optimizer and loss function
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.BCELoss()  # Binary cross-entropy for implicit feedback

    logger.info(f"Optimizer: Adam (lr={learning_rate})")
    logger.info("Loss function: Binary Cross-Entropy")

    # Training history
    history = {"train_loss": [], "val_loss": []}

    # Training loop
    logger.info("\n" + "=" * 70)
    logger.info("Training")
    logger.info("=" * 70)

    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        batch_count = 0

        for batch_idx, (user_ids, item_ids, labels) in enumerate(train_loader):
            # Move to device
            user_ids = user_ids.to(device)
            item_ids = item_ids.to(device)
            labels = labels.to(device).unsqueeze(1)  # Shape: (batch_size, 1)

            # Forward pass
            optimizer.zero_grad()
            predictions = model(user_ids, item_ids)
            loss = criterion(predictions, labels)

            # Backward pass
            loss.backward()
            optimizer.step()

            # Track loss
            train_loss += loss.item()
            batch_count += 1

            # Log every 10 batches
            if (batch_idx + 1) % 10 == 0:
                avg_loss = train_loss / batch_count
                logger.info(
                    f"Epoch [{epoch + 1}/{epochs}] "
                    f"Batch [{batch_idx + 1}/{len(train_loader)}] "
                    f"Loss: {avg_loss:.4f}"
                )

        # Calculate average training loss
        avg_train_loss = train_loss / len(train_loader)
        history["train_loss"].append(avg_train_loss)

        # Validation phase
        model.eval()
        val_loss = 0.0

        with torch.no_grad():
            for user_ids, item_ids, labels in val_loader:
                user_ids = user_ids.to(device)
                item_ids = item_ids.to(device)
                labels = labels.to(device).unsqueeze(1)

                predictions = model(user_ids, item_ids)
                loss = criterion(predictions, labels)
                val_loss += loss.item()

        avg_val_loss = val_loss / len(val_loader)
        history["val_loss"].append(avg_val_loss)

        # Log epoch summary
        logger.info(
            f"\nEpoch [{epoch + 1}/{epochs}] Summary: "
            f"Train Loss: {avg_train_loss:.4f}, "
            f"Val Loss: {avg_val_loss:.4f}\n"
        )

    logger.info("Training completed!")

    return model, history


def evaluate_model(
    model: NCFModel,
    val_interactions: List[Dict[str, Any]],
    user_id_map: Dict[str, int],
    item_id_map: Dict[str, int],
    k: int = 10,
    device: str = "cpu",
) -> Dict[str, float]:
    """
    Evaluate model using ranking metrics.

    Computes NDCG@K and Hit Rate@K on validation set. For each user,
    ranks all items and checks if relevant items appear in top-K.

    Args:
        model: Trained NCF model
        val_interactions: Validation interactions
        user_id_map: User ID to index mapping
        item_id_map: Item ID to index mapping
        k: Number of top items to consider
        device: Device to use for inference

    Returns:
        Dictionary with 'ndcg@k' and 'hit_rate@k' metrics
    """
    logger.info(f"Evaluating model with NDCG@{k} and Hit Rate@{k}")

    model.eval()
    device = torch.device(device)

    # Group interactions by user
    user_items = {}
    for interaction in val_interactions:
        user_id = interaction.get("user_id")
        item_id = interaction.get("resource_id")

        if user_id in user_id_map and item_id in item_id_map:
            if user_id not in user_items:
                user_items[user_id] = []
            user_items[user_id].append(item_id)

    logger.info(f"Evaluating {len(user_items)} users")

    ndcg_scores = []
    hit_scores = []

    all_item_ids = list(item_id_map.keys())
    all_item_indices = list(item_id_map.values())

    with torch.no_grad():
        for user_id, relevant_items in user_items.items():
            user_idx = user_id_map[user_id]

            # Get predictions for all items
            user_tensor = torch.tensor(
                [user_idx] * len(all_item_indices), dtype=torch.long
            ).to(device)
            item_tensor = torch.tensor(all_item_indices, dtype=torch.long).to(device)

            predictions = (
                model.predict(user_tensor, item_tensor).cpu().numpy().flatten()
            )

            # Create item-score pairs and sort by score
            item_scores = list(zip(all_item_ids, predictions))
            item_scores.sort(key=lambda x: x[1], reverse=True)

            # Get top-K items
            top_k_items = [item_id for item_id, _ in item_scores[:k]]

            # Calculate Hit Rate (did we hit any relevant item in top-K?)
            hit = any(item_id in relevant_items for item_id in top_k_items)
            hit_scores.append(1.0 if hit else 0.0)

            # Calculate NDCG
            # DCG = sum of (relevance / log2(rank + 1)) for items in top-K
            dcg = 0.0
            for rank, item_id in enumerate(top_k_items, start=1):
                if item_id in relevant_items:
                    dcg += 1.0 / np.log2(rank + 1)

            # IDCG = ideal DCG (all relevant items at top)
            idcg = 0.0
            for rank in range(1, min(len(relevant_items), k) + 1):
                idcg += 1.0 / np.log2(rank + 1)

            # NDCG = DCG / IDCG (or 0 if IDCG is 0)
            ndcg = dcg / idcg if idcg > 0 else 0.0
            ndcg_scores.append(ndcg)

    # Calculate average metrics
    avg_ndcg = np.mean(ndcg_scores)
    avg_hit_rate = np.mean(hit_scores)

    metrics = {f"ndcg@{k}": avg_ndcg, f"hit_rate@{k}": avg_hit_rate}

    logger.info("Evaluation results:")
    logger.info(f"  NDCG@{k}: {avg_ndcg:.4f}")
    logger.info(f"  Hit Rate@{k}: {avg_hit_rate:.4f}")

    return metrics


def save_checkpoint(
    model: NCFModel,
    user_id_map: Dict[str, int],
    item_id_map: Dict[str, int],
    metrics: Dict[str, float],
    history: Dict[str, List[float]],
    output_path: str,
    hyperparameters: Dict[str, Any],
) -> None:
    """
    Save model checkpoint with mappings and metadata.

    Args:
        model: Trained NCF model
        user_id_map: User ID to index mapping
        item_id_map: Item ID to index mapping
        metrics: Evaluation metrics
        history: Training history
        output_path: Path to save checkpoint
        hyperparameters: Model hyperparameters
    """
    output_file = Path(output_path)

    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Saving checkpoint to {output_path}")

    # Convert numpy types to Python types for serialization
    def convert_to_python_types(obj):
        """Recursively convert numpy types to Python types."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, dict):
            return {key: convert_to_python_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_python_types(item) for item in obj]
        else:
            return obj

    # Create checkpoint dictionary
    checkpoint = {
        "model_state_dict": model.state_dict(),
        "user_id_map": user_id_map,
        "item_id_map": item_id_map,
        "num_users": len(user_id_map),
        "num_items": len(item_id_map),
        "embedding_dim": hyperparameters["embedding_dim"],
        "hidden_layers": hyperparameters["hidden_layers"],
        "training_metrics": convert_to_python_types(metrics),
        "training_history": convert_to_python_types(history),
        "hyperparameters": hyperparameters,
        "timestamp": datetime.now().isoformat(),
    }

    # Save checkpoint
    torch.save(checkpoint, output_file)

    logger.info("Checkpoint saved successfully!")
    logger.info(f"  Location: {output_file.absolute()}")
    logger.info(f"  Size: {output_file.stat().st_size / 1024:.2f} KB")
    logger.info(f"  Users: {len(user_id_map)}, Items: {len(item_id_map)}")
    logger.info(f"  Metrics: {convert_to_python_types(metrics)}")


def main():
    """
    Main training pipeline.

    Pipeline:
    1. Parse command-line arguments
    2. Set random seeds for reproducibility
    3. Load and prepare interaction data
    4. Create negative samples
    5. Split into train/validation sets
    6. Initialize NCF model
    7. Train model with evaluation
    8. Save checkpoint with mappings and metrics
    """
    # Parse arguments
    args = parse_arguments()

    logger.info("=" * 70)
    logger.info("NCF Model Training")
    logger.info("=" * 70)
    logger.info("Configuration:")
    logger.info(f"  Epochs: {args.epochs}")
    logger.info(f"  Batch size: {args.batch_size}")
    logger.info(f"  Learning rate: {args.learning_rate}")
    logger.info(f"  Embedding dim: {args.embedding_dim}")
    logger.info(f"  Hidden layers: {args.hidden_layers}")
    logger.info(f"  Data path: {args.data_path}")
    logger.info(f"  Negative samples: {args.negative_samples}")
    logger.info(f"  Validation split: {args.val_split}")
    logger.info(f"  Output dir: {args.output_dir}")
    logger.info(f"  Model name: {args.model_name}")
    logger.info(f"  Random seed: {args.seed}")
    logger.info(f"  Device: {args.device}")
    logger.info("=" * 70)

    # Set random seeds
    random.seed(args.seed)

    try:
        # Load interaction data
        logger.info("\n" + "=" * 70)
        logger.info("Step 1: Loading Data")
        logger.info("=" * 70)

        interactions, user_id_map, item_id_map = load_interaction_data(args.data_path)

        # Split into train/validation
        train_interactions, val_interactions = split_train_val(
            interactions, val_split=args.val_split, seed=args.seed
        )

        # Create negative samples
        logger.info("\n" + "=" * 70)
        logger.info("Step 2: Creating Negative Samples")
        logger.info("=" * 70)

        train_samples = create_negative_samples(
            train_interactions,
            user_id_map,
            item_id_map,
            num_negatives=args.negative_samples,
            seed=args.seed,
        )

        val_samples = create_negative_samples(
            val_interactions,
            user_id_map,
            item_id_map,
            num_negatives=args.negative_samples,
            seed=args.seed + 1,  # Different seed for validation
        )

        # Train model
        logger.info("\n" + "=" * 70)
        logger.info("Step 3: Training Model")
        logger.info("=" * 70)

        model, history = train_ncf_model(
            train_samples=train_samples,
            val_samples=val_samples,
            num_users=len(user_id_map),
            num_items=len(item_id_map),
            embedding_dim=args.embedding_dim,
            hidden_layers=args.hidden_layers,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            device=args.device,
            seed=args.seed,
        )

        # Evaluate model
        logger.info("\n" + "=" * 70)
        logger.info("Step 4: Evaluating Model")
        logger.info("=" * 70)

        metrics = evaluate_model(
            model=model,
            val_interactions=val_interactions,
            user_id_map=user_id_map,
            item_id_map=item_id_map,
            k=10,
            device=args.device
            if args.device != "auto"
            else ("cuda" if torch.cuda.is_available() else "cpu"),
        )

        # Save checkpoint
        logger.info("\n" + "=" * 70)
        logger.info("Step 5: Saving Checkpoint")
        logger.info("=" * 70)

        output_path = Path(args.output_dir) / args.model_name

        hyperparameters = {
            "embedding_dim": args.embedding_dim,
            "hidden_layers": args.hidden_layers,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "negative_samples": args.negative_samples,
            "val_split": args.val_split,
            "seed": args.seed,
        }

        save_checkpoint(
            model=model,
            user_id_map=user_id_map,
            item_id_map=item_id_map,
            metrics=metrics,
            history=history,
            output_path=str(output_path),
            hyperparameters=hyperparameters,
        )

        # Training complete
        logger.info("\n" + "=" * 70)
        logger.info("Training Complete!")
        logger.info("=" * 70)
        logger.info(f"Model saved to: {output_path.absolute()}")
        logger.info("Final metrics:")
        for metric_name, metric_value in metrics.items():
            logger.info(f"  {metric_name}: {metric_value:.4f}")
        logger.info("=" * 70)

        return 0

    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
