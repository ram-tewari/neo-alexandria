"""
Neural Collaborative Filtering (NCF) Service

This module provides collaborative filtering recommendations using neural networks.
It implements the NCF model for personalized resource recommendations based on
user-item interaction patterns.

Related files:
- app/models/ncf_model.py: NCF model architecture
- app/database/models.py: UserInteraction and Resource models
- app/services/recommendation_service.py: High-level recommendation API

Features:
- Neural collaborative filtering predictions
- Batch prediction for efficiency
- Top-K recommendation generation
- Cold start handling with popular items
- Lazy model loading for efficiency
- GPU acceleration support
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class NCFModelNotFoundError(Exception):
    """Raised when NCF model checkpoint is not found."""

    pass


class NCFService:
    """
    Neural Collaborative Filtering service for recommendations.

    This service provides methods for loading trained NCF models and generating
    personalized recommendations using deep learning-based collaborative filtering.

    The service uses lazy loading for models to avoid loading them until needed,
    which improves startup time and memory efficiency.
    """

    def __init__(self, db: Session, model_path: Optional[str] = None):
        """
        Initialize the NCF service.

        Args:
            db: SQLAlchemy database session
            model_path: Path to model checkpoint (default: models/ncf_benchmark_v1.pt)
        """
        self.db = db

        # Set default model path if not provided
        if model_path is None:
            model_path = "backend/models/ncf_benchmark_v1.pt"

        self.model_path = Path(model_path)

        # Lazy loading: Initialize as None, load on first use
        self.model = None
        self.device = None

        # ID mappings: string user/item IDs <-> integer indices
        self.user_id_map: Dict[str, int] = {}  # {"user_uuid": 0, ...}
        self.item_id_map: Dict[str, int] = {}  # {"resource_uuid": 0, ...}

        # Reverse mappings for converting back
        self.user_idx_to_id: Dict[int, str] = {}
        self.item_idx_to_id: Dict[int, str] = {}

        logger.info(f"NCFService initialized with model_path={self.model_path}")

    def _load_model(self) -> None:
        """
        Load NCF model and mappings with lazy loading.

        Algorithm:
        1. Check if model already loaded (skip if yes)
        2. Import torch and NCF model (lazy import)
        3. Check if checkpoint file exists
        4. Load checkpoint from disk
        5. Extract model state dict, user/item mappings, and hyperparameters
        6. Initialize NCF model with saved hyperparameters
        7. Load model weights from state dict
        8. Move model to GPU if CUDA available, otherwise CPU
        9. Set model to evaluation mode

        This method is called automatically on first prediction request.
        Lazy loading improves startup time and memory efficiency.

        Raises:
            NCFModelNotFoundError: If checkpoint file not found
            Exception: If model loading fails
        """
        # Skip if already loaded
        if self.model is not None:
            logger.debug("Model already loaded, skipping")
            return

        logger.info("Loading NCF model and mappings...")

        try:
            # Lazy import of ML libraries
            import torch
            from app.models.ncf_model import NCFModel

            # Check if checkpoint exists
            if not self.model_path.exists():
                raise NCFModelNotFoundError(
                    f"NCF model checkpoint not found at {self.model_path}. "
                    "Please train the model first using: "
                    "python backend/scripts/train_ncf.py"
                )

            # Load checkpoint
            logger.info(f"Loading checkpoint from {self.model_path}")
            checkpoint = torch.load(self.model_path, map_location="cpu")

            # Extract mappings
            self.user_id_map = checkpoint.get("user_id_map", {})
            self.item_id_map = checkpoint.get("item_id_map", {})

            # Create reverse mappings
            self.user_idx_to_id = {
                idx: user_id for user_id, idx in self.user_id_map.items()
            }
            self.item_idx_to_id = {
                idx: item_id for item_id, idx in self.item_id_map.items()
            }

            logger.info(
                f"Loaded mappings: {len(self.user_id_map)} users, "
                f"{len(self.item_id_map)} items"
            )

            # Extract hyperparameters
            num_users = checkpoint.get("num_users", len(self.user_id_map))
            num_items = checkpoint.get("num_items", len(self.item_id_map))
            embedding_dim = checkpoint.get("embedding_dim", 64)
            hidden_layers = checkpoint.get("hidden_layers", [128, 64, 32])

            logger.info(
                f"Model hyperparameters: num_users={num_users}, num_items={num_items}, "
                f"embedding_dim={embedding_dim}, hidden_layers={hidden_layers}"
            )

            # Initialize model
            self.model = NCFModel(
                num_users=num_users,
                num_items=num_items,
                embedding_dim=embedding_dim,
                hidden_layers=hidden_layers,
            )

            # Load model weights
            self.model.load_state_dict(checkpoint["model_state_dict"])
            logger.info("Model weights loaded successfully")

            # Move to GPU if available
            if torch.cuda.is_available():
                logger.info("CUDA available, moving model to GPU")
                self.model = self.model.cuda()
                self.device = torch.device("cuda")
            else:
                logger.info("CUDA not available, using CPU")
                self.device = torch.device("cpu")

            # Set model to evaluation mode
            self.model.eval()
            logger.info("Model set to evaluation mode")

            # Log training metrics if available
            if "training_metrics" in checkpoint:
                metrics = checkpoint["training_metrics"]
                logger.info(f"Training metrics: {metrics}")

        except NCFModelNotFoundError:
            raise

        except Exception as e:
            logger.error(f"Failed to load NCF model: {e}")
            raise Exception(f"NCF model loading failed: {e}") from e

    def predict(self, user_id: str, item_ids: List[str]) -> Dict[str, float]:
        """
        Predict scores for user-item pairs.

        This method predicts interaction scores between a user and multiple items.
        Scores are between 0 and 1, where higher scores indicate stronger predicted
        interaction likelihood.

        Args:
            user_id: User identifier (UUID string)
            item_ids: List of item identifiers (resource UUID strings)

        Returns:
            Dictionary mapping item_id to prediction score
            Example: {"resource_uuid_1": 0.85, "resource_uuid_2": 0.72, ...}

            For unknown users or items, returns empty dict or skips those items.

        Algorithm:
        1. Load model if not already loaded (lazy loading)
        2. Convert user_id to index using mapping
        3. Convert item_ids to indices using mapping
        4. Create tensors for user and item indices
        5. Forward pass through model
        6. Extract scores and map back to item IDs

        Performance: <50ms for typical batch sizes
        """
        # Ensure model is loaded
        if self.model is None:
            self._load_model()

        import torch

        # Check if user is in mapping
        if user_id not in self.user_id_map:
            logger.warning(f"User {user_id} not in training data (cold start)")
            return {}

        user_idx = self.user_id_map[user_id]

        # Convert item IDs to indices, skip unknown items
        valid_items = []
        valid_indices = []

        for item_id in item_ids:
            if item_id in self.item_id_map:
                valid_items.append(item_id)
                valid_indices.append(self.item_id_map[item_id])
            else:
                logger.debug(f"Item {item_id} not in training data, skipping")

        if not valid_items:
            logger.warning("No valid items found in training data")
            return {}

        # Create tensors
        user_tensor = torch.tensor([user_idx] * len(valid_indices), dtype=torch.long)
        item_tensor = torch.tensor(valid_indices, dtype=torch.long)

        # Move to device
        user_tensor = user_tensor.to(self.device)
        item_tensor = item_tensor.to(self.device)

        # Forward pass
        self.model.eval()
        with torch.no_grad():
            scores = self.model.predict(user_tensor, item_tensor)

        # Convert to dictionary
        scores = scores.cpu().numpy().flatten()
        predictions = {
            item_id: float(score) for item_id, score in zip(valid_items, scores)
        }

        return predictions

    def predict_batch(self, user_id: str, item_ids: List[str]) -> Dict[str, float]:
        """
        Predict scores for user-item pairs with batch processing.

        This method is an alias for predict() since the predict method already
        handles batching efficiently. It's provided for API consistency.

        Args:
            user_id: User identifier (UUID string)
            item_ids: List of item identifiers (resource UUID strings)

        Returns:
            Dictionary mapping item_id to prediction score
            Example: {"resource_uuid_1": 0.85, "resource_uuid_2": 0.72, ...}

        Performance: Processes all items in a single forward pass for efficiency
        """
        return self.predict(user_id, item_ids)

    def recommend(
        self, user_id: str, top_k: int = 10, exclude_seen: bool = True
    ) -> List[Tuple[str, float]]:
        """
        Generate top-K recommendations for a user.

        This method generates personalized recommendations by:
        1. Querying candidate items from database
        2. Optionally filtering out items the user has already interacted with
        3. Predicting scores for all candidate items
        4. Sorting by score and returning top-K items

        Args:
            user_id: User identifier (UUID string)
            top_k: Number of recommendations to return (default: 10)
            exclude_seen: Whether to filter out items user has interacted with (default: True)

        Returns:
            List of (item_id, score) tuples sorted by score descending
            Example: [("resource_uuid_1", 0.95), ("resource_uuid_2", 0.87), ...]

        Algorithm:
        1. Check if user is in training data
        2. If not, use cold start handling
        3. Query all resources from database
        4. If exclude_seen, filter out items user has interacted with
        5. Use batch prediction for efficiency
        6. Sort by score descending
        7. Return top-K items

        Performance: <50ms for typical catalog sizes
        """
        # Ensure model is loaded
        if self.model is None:
            self._load_model()

        # Check if user is in training data
        if user_id not in self.user_id_map:
            logger.info(f"User {user_id} not in training data, using cold start")
            return self._handle_cold_start(user_id, top_k)

        from app.database.models import Resource, UserInteraction

        # Query all resources
        resources = self.db.query(Resource).all()
        candidate_item_ids = [str(resource.id) for resource in resources]

        logger.debug(f"Found {len(candidate_item_ids)} candidate items")

        # Filter out seen items if requested
        if exclude_seen:
            seen_items = (
                self.db.query(UserInteraction.resource_id)
                .filter(UserInteraction.user_id == user_id)
                .all()
            )
            seen_item_ids = {str(item[0]) for item in seen_items}

            candidate_item_ids = [
                item_id
                for item_id in candidate_item_ids
                if item_id not in seen_item_ids
            ]

            logger.debug(
                f"Filtered to {len(candidate_item_ids)} unseen items "
                f"(excluded {len(seen_item_ids)} seen items)"
            )

        # Predict scores for all candidates
        predictions = self.predict_batch(user_id, candidate_item_ids)

        # Sort by score descending
        sorted_items = sorted(predictions.items(), key=lambda x: x[1], reverse=True)

        # Return top-K
        top_recommendations = sorted_items[:top_k]

        logger.info(
            f"Generated {len(top_recommendations)} recommendations for user {user_id}"
        )

        return top_recommendations

    def _handle_cold_start(self, user_id: str, top_k: int) -> List[Tuple[str, float]]:
        """
        Handle cold start scenario by returning popular items.

        This method provides fallback recommendations for new users or users
        not in the training data. It returns the most popular items based on
        interaction count.

        Args:
            user_id: User identifier (UUID string)
            top_k: Number of recommendations to return

        Returns:
            List of (item_id, confidence_score) tuples
            Confidence scores are set to 0.5 to indicate cold start status
            Example: [("resource_uuid_1", 0.5), ("resource_uuid_2", 0.5), ...]

        Algorithm:
        1. Query user interactions grouped by resource
        2. Count interactions per resource
        3. Sort by interaction count descending
        4. Return top-K most popular items
        5. Set confidence score to 0.5 to indicate cold start
        6. Log cold start event for monitoring

        Fallback Strategy:
        - Uses popularity-based recommendations
        - Confidence score of 0.5 indicates cold start (vs 0.0-1.0 for model predictions)
        - Allows system to provide recommendations even for new users
        """
        from app.database.models import Resource, UserInteraction
        from sqlalchemy import func

        logger.info(f"Handling cold start for user {user_id}")

        # Query popular items (most interactions)
        popular_items = (
            self.db.query(
                UserInteraction.resource_id,
                func.count(UserInteraction.id).label("interaction_count"),
            )
            .group_by(UserInteraction.resource_id)
            .order_by(func.count(UserInteraction.id).desc())
            .limit(top_k)
            .all()
        )

        # Convert to list of tuples with confidence score
        # Use 0.5 as confidence to indicate cold start (distinguishable from model scores)
        recommendations = [(str(item.resource_id), 0.5) for item in popular_items]

        logger.info(
            f"Cold start: returning {len(recommendations)} popular items "
            f"for user {user_id}"
        )

        # If no interactions exist, return random items
        if not recommendations:
            logger.warning("No interactions found, returning random items")
            random_resources = self.db.query(Resource.id).limit(top_k).all()
            recommendations = [(str(resource.id), 0.5) for resource in random_resources]

        return recommendations
