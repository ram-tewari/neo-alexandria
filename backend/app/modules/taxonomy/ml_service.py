"""
ML Classification Service

Machine learning-based classification service for taxonomy prediction.
Implements active learning, model training, and prediction with confidence scores.

**Validates: Requirements 9.1-9.7**
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session

from app.database.models import Resource, TaxonomyNode

logger = logging.getLogger(__name__)


class MLClassificationService:
    """Service for ML-based resource classification."""

    def __init__(self, db: Session):
        """
        Initialize ML classification service.

        Args:
            db: Database session
        """
        self.db = db
        self.model = None
        self.model_metadata = {}
        self.model_path = None

    def load_model(self, model_path: str) -> None:
        """
        Load pre-trained classification model from disk.

        Args:
            model_path: Path to the model file (.pkl)

        Raises:
            FileNotFoundError: If model file doesn't exist
            Exception: If model loading fails

        **Validates: Requirement 9.1**
        """
        import joblib

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        try:
            self.model = joblib.load(model_path)
            self.model_path = model_path

            # Load metadata
            metadata_path = model_path.replace(".pkl", "_metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    self.model_metadata = json.load(f)

            logger.info(f"Loaded model from {model_path}")
            logger.info(f"Model metadata: {self.model_metadata}")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def predict(self, resource_id: str, top_k: int = 5) -> List[Dict]:
        """
        Predict top-K taxonomy nodes for a resource.

        Args:
            resource_id: ID of the resource to classify
            top_k: Number of top predictions to return (default: 5)

        Returns:
            List of predictions with node_id, node_name, confidence, is_uncertain

        Raises:
            ValueError: If model not loaded or resource not found

        **Validates: Requirements 9.2, 9.3, 9.4**
        """
        if not self.model:
            raise ValueError("Model not loaded. Call load_model() first.")

        # Fetch resource
        resource = self.db.query(Resource).filter_by(id=resource_id).first()
        if not resource:
            raise ValueError(f"Resource {resource_id} not found")

        # Extract features
        features = self._extract_features(resource)

        # Get predictions with probabilities
        try:
            probabilities = self.model.predict_proba([features])[0]
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise ValueError(f"Prediction failed: {e}")

        # Get top K predictions
        import numpy as np

        probabilities_array = np.array(probabilities)
        top_indices = probabilities_array.argsort()[-top_k:][::-1]

        predictions = []
        for idx in top_indices:
            node_id = self.model.classes_[idx]
            confidence = float(probabilities[idx])

            # Fetch node details
            node = self.db.query(TaxonomyNode).filter_by(id=node_id).first()

            # Identify uncertain predictions (confidence < 0.5)
            is_uncertain = confidence < 0.5

            predictions.append(
                {
                    "node_id": str(node_id),
                    "node_name": node.name if node else "Unknown",
                    "confidence": round(confidence, 4),
                    "is_uncertain": is_uncertain,
                }
            )

        return predictions

    def identify_uncertain_predictions(
        self, threshold: float = 0.5, limit: int = 100
    ) -> List[str]:
        """
        Identify resources with uncertain classifications for active learning.

        Returns resources where the highest prediction confidence is below
        the threshold, indicating the model is uncertain and would benefit
        from manual labeling.

        Args:
            threshold: Confidence threshold below which predictions are uncertain
            limit: Maximum number of uncertain resources to return

        Returns:
            List of resource IDs with uncertain classifications

        **Validates: Requirement 9.4**
        """
        # Query resources with low-confidence predictions
        # These are candidates for manual review and active learning

        uncertain_resources = []

        # Query resources that have been classified but with low confidence
        # Note: classification_confidence field may not exist yet in Resource model
        # Using a try-except to handle this gracefully
        try:
            resources = (
                self.db.query(Resource)
                .filter(Resource.classification_confidence < threshold)
                .limit(limit)
                .all()
            )
            uncertain_resources = [str(r.id) for r in resources]
        except AttributeError:
            # Field doesn't exist yet - return empty list
            logger.warning(
                "classification_confidence field not found in Resource model"
            )
            uncertain_resources = []

        logger.info(f"Found {len(uncertain_resources)} uncertain predictions")

        return uncertain_resources

    def retrain_model(
        self,
        training_data: List[Tuple[str, str]],
        validation_split: float = 0.2,
        model_type: str = "random_forest",
    ) -> Dict:
        """
        Retrain classification model with new labeled data.

        Args:
            training_data: List of (resource_id, node_id) tuples
            validation_split: Fraction of data to use for validation
            model_type: Type of model to train ("random_forest", "logistic")

        Returns:
            Dictionary with training metrics (accuracy, f1_score, etc.)

        Raises:
            ValueError: If insufficient training data

        **Validates: Requirements 9.5, 9.6, 9.7**
        """
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, f1_score, classification_report
        import joblib

        if len(training_data) < 10:
            raise ValueError("Insufficient training data. Need at least 10 samples.")

        # Prepare training data
        X = []
        y = []

        for resource_id, node_id in training_data:
            resource = self.db.query(Resource).filter_by(id=resource_id).first()
            if resource:
                features = self._extract_features(resource)
                X.append(features)
                y.append(node_id)

        if len(X) == 0:
            raise ValueError("No valid training samples found")

        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X,
            y,
            test_size=validation_split,
            random_state=42,
            stratify=y if len(set(y)) > 1 else None,
        )

        # Train model
        if model_type == "random_forest":
            model = RandomForestClassifier(
                n_estimators=100, max_depth=20, random_state=42, n_jobs=-1
            )
        elif model_type == "logistic":
            model = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        logger.info(f"Training {model_type} model with {len(X_train)} samples...")
        model.fit(X_train, y_train)

        # Evaluate on validation set
        y_pred = model.predict(X_val)
        accuracy = accuracy_score(y_val, y_pred)
        f1 = f1_score(y_val, y_pred, average="weighted")

        # Generate classification report
        report = classification_report(y_val, y_pred, output_dict=True)

        # Save model
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        model_dir = "models"
        os.makedirs(model_dir, exist_ok=True)

        model_path = os.path.join(
            model_dir, f"taxonomy_classifier_{model_type}_{timestamp}.pkl"
        )
        joblib.dump(model, model_path)

        # Save metadata
        metadata = {
            "version": timestamp,
            "model_type": model_type,
            "accuracy": float(accuracy),
            "f1_score": float(f1),
            "training_samples": len(X_train),
            "validation_samples": len(X_val),
            "classes": [str(c) for c in model.classes_],
            "classification_report": report,
            "created_at": datetime.utcnow().isoformat(),
        }

        metadata_path = model_path.replace(".pkl", "_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        # Update current model
        self.model = model
        self.model_metadata = metadata
        self.model_path = model_path

        logger.info(
            f"Model trained successfully. Accuracy: {accuracy:.4f}, F1: {f1:.4f}"
        )
        logger.info(f"Model saved to {model_path}")

        return metadata

    def _extract_features(self, resource: Resource) -> List[float]:
        """
        Extract features for classification from a resource.

        Uses the resource embedding as primary features. If no embedding
        exists, returns a zero vector.

        Args:
            resource: Resource object

        Returns:
            Feature vector as list of floats
        """
        features = []

        # Use embedding as primary features
        if resource.embedding:
            try:
                embedding = json.loads(resource.embedding)
                features.extend(embedding)
            except (json.JSONDecodeError, TypeError):
                # Fallback to zero vector
                features.extend([0.0] * 768)
        else:
            # No embedding available - use zero vector
            features.extend([0.0] * 768)

        # Could add additional features here:
        # - Text length
        # - Keyword presence
        # - Citation count
        # - Quality score
        # For now, just use embeddings

        return features

    def get_model_info(self) -> Dict:
        """
        Get information about the currently loaded model.

        Returns:
            Dictionary with model metadata
        """
        if not self.model:
            return {"error": "No model loaded"}

        return {
            "model_path": self.model_path,
            "metadata": self.model_metadata,
            "classes": [str(c) for c in self.model.classes_]
            if hasattr(self.model, "classes_")
            else [],
        }
