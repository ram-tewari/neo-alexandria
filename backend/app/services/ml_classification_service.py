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
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

from sqlalchemy.orm import Session

# ML imports will be lazy-loaded
# import torch
# from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
# from sklearn.metrics import f1_score, precision_score, recall_score

logger = logging.getLogger(__name__)


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
        model_name: str = "distilbert-base-uncased",
        model_version: str = "v1.0"
    ):
        """
        Initialize the ML classification service.
        
        Args:
            db: SQLAlchemy database session
            model_name: Base model name from Hugging Face (default: distilbert-base-uncased)
            model_version: Model version identifier for checkpoints (default: v1.0)
        """
        self.db = db
        self.model_name = model_name
        self.model_version = model_version
        
        # Lazy loading: Initialize as None, load on first use
        self.model = None
        self.tokenizer = None
        
        # Label mappings: taxonomy_node_id <-> model label index
        self.id_to_label: Dict[int, str] = {}  # {0: "node_id_1", 1: "node_id_2", ...}
        self.label_to_id: Dict[str, int] = {}  # {"node_id_1": 0, "node_id_2": 1, ...}
        
        # Model checkpoint directory
        self.checkpoint_dir = Path("models") / "classification" / model_version
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            f"MLClassificationService initialized with model={model_name}, "
            f"version={model_version}, checkpoint_dir={self.checkpoint_dir}"
        )

    def _load_model(self) -> None:
        """
        Load model and tokenizer with lazy loading.
        
        Algorithm:
        1. Check if model already loaded (skip if yes)
        2. Import torch and transformers (lazy import)
        3. Load tokenizer from Hugging Face
        4. Try to load model from checkpoint directory
        5. If checkpoint not found, load base pre-trained model
        6. Load label mapping from JSON if exists
        7. Move model to GPU if CUDA available
        8. Set model to eval mode
        
        This method is called automatically on first prediction/training request.
        Lazy loading improves startup time and memory efficiency.
        
        Raises:
            ImportError: If required ML libraries not installed
            Exception: If model loading fails
        """
        # Skip if already loaded
        if self.model is not None and self.tokenizer is not None:
            logger.debug("Model already loaded, skipping")
            return
        
        logger.info("Loading model and tokenizer...")
        
        try:
            # Lazy import of ML libraries
            import torch
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            
            # Load tokenizer
            logger.info(f"Loading tokenizer: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Try to load from checkpoint first
            checkpoint_path = self.checkpoint_dir / "pytorch_model.bin"
            label_map_path = self.checkpoint_dir / "label_map.json"
            
            if checkpoint_path.exists():
                logger.info(f"Loading fine-tuned model from checkpoint: {self.checkpoint_dir}")
                try:
                    # Load label mapping
                    if label_map_path.exists():
                        with open(label_map_path, 'r') as f:
                            label_data = json.load(f)
                            self.id_to_label = {int(k): v for k, v in label_data['id_to_label'].items()}
                            self.label_to_id = label_data['label_to_id']
                        logger.info(f"Loaded label mapping with {len(self.id_to_label)} labels")
                    
                    # Load model from checkpoint
                    num_labels = len(self.id_to_label) if self.id_to_label else 2
                    self.model = AutoModelForSequenceClassification.from_pretrained(
                        str(self.checkpoint_dir),
                        num_labels=num_labels,
                        problem_type="multi_label_classification"
                    )
                    logger.info("Successfully loaded fine-tuned model from checkpoint")
                    
                except Exception as e:
                    logger.warning(f"Failed to load checkpoint: {e}. Falling back to base model.")
                    self.model = None
            
            # Fall back to base model if checkpoint loading failed or doesn't exist
            if self.model is None:
                logger.info(f"Loading base pre-trained model: {self.model_name}")
                # Start with 2 labels as default, will be updated during fine-tuning
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name,
                    num_labels=2,
                    problem_type="multi_label_classification"
                )
                logger.info("Successfully loaded base model")
            
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
            
        except ImportError as e:
            logger.error(f"Failed to import ML libraries: {e}")
            raise ImportError(
                "Required ML libraries not installed. "
                "Please install: pip install transformers torch scikit-learn"
            ) from e
        
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise Exception(f"Model loading failed: {e}") from e

    def _compute_metrics(self, eval_pred) -> Dict[str, float]:
        """
        Compute evaluation metrics for multi-label classification.
        
        This callback is used by Hugging Face Trainer during evaluation.
        It computes F1 score (macro average), precision, and recall.
        
        Args:
            eval_pred: EvalPrediction object with predictions and labels
                - predictions: Model logits (before sigmoid)
                - label_ids: Ground truth multi-hot encoded labels
        
        Returns:
            Dictionary with metrics:
                - f1: Macro-averaged F1 score
                - precision: Macro-averaged precision
                - recall: Macro-averaged recall
        
        Algorithm:
        1. Apply sigmoid to logits to get probabilities
        2. Threshold at 0.5 to get binary predictions
        3. Compute F1, precision, recall with macro averaging
        4. Handle multi-label classification metrics properly
        """
        from sklearn.metrics import f1_score, precision_score, recall_score
        import numpy as np
        
        logits, labels = eval_pred
        
        # Apply sigmoid to get probabilities
        predictions = 1 / (1 + np.exp(-logits))  # sigmoid
        
        # Threshold at 0.5 for binary predictions
        predictions = (predictions > 0.5).astype(int)
        
        # Compute metrics with macro averaging (treats all labels equally)
        f1 = f1_score(labels, predictions, average='macro', zero_division=0)
        precision = precision_score(labels, predictions, average='macro', zero_division=0)
        recall = recall_score(labels, predictions, average='macro', zero_division=0)
        
        logger.info(f"Evaluation metrics - F1: {f1:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}")
        
        return {
            'f1': f1,
            'precision': precision,
            'recall': recall
        }

    def fine_tune(
        self,
        labeled_data: List[Tuple[str, List[str]]],
        unlabeled_data: Optional[List[str]] = None,
        epochs: int = 3,
        batch_size: int = 16,
        learning_rate: float = 2e-5
    ) -> Dict[str, float]:
        """
        Fine-tune BERT model on labeled data with optional semi-supervised learning.
        
        This method implements the complete training pipeline:
        1. Build label mapping from unique taxonomy IDs
        2. Convert multi-label to multi-hot encoding
        3. Split train/validation (80/20)
        4. Tokenize texts with max_length=512
        5. Create PyTorch datasets
        6. Configure Hugging Face Trainer
        7. Train model with evaluation
        8. If unlabeled data provided, perform semi-supervised iteration
        9. Save model, tokenizer, and label map
        
        Args:
            labeled_data: List of (text, [taxonomy_node_ids]) tuples
                Example: [("Machine learning article", ["node_id_1", "node_id_2"]), ...]
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
        
        # Lazy import of ML libraries
        import torch
        from torch.utils.data import Dataset
        from transformers import (
            AutoTokenizer,
            AutoModelForSequenceClassification,
            Trainer,
            TrainingArguments
        )
        from sklearn.model_selection import train_test_split
        import numpy as np
        
        # Step 1: Build label mapping from unique taxonomy IDs
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
        
        # Step 2: Convert multi-label to multi-hot encoding
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
        
        # Step 3: Split train/validation (80/20)
        logger.info("Splitting train/validation (80/20)...")
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )
        logger.info(f"Train: {len(train_texts)} examples, Validation: {len(val_texts)} examples")
        
        # Step 4: Tokenize texts with max_length=512
        logger.info("Tokenizing texts...")
        if self.tokenizer is None:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        train_encodings = self.tokenizer(
            train_texts,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors='pt'
        )
        
        val_encodings = self.tokenizer(
            val_texts,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors='pt'
        )
        logger.info("Tokenization complete")
        
        # Step 5: Create PyTorch datasets
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
        
        # Initialize model with correct number of labels
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
        
        # Step 6: Configure Hugging Face Trainer
        logger.info("Configuring Trainer...")
        
        training_args = TrainingArguments(
            output_dir=str(self.checkpoint_dir),
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            weight_decay=0.01,
            eval_strategy="epoch",  # Evaluate after each epoch
            save_strategy="epoch",  # Save checkpoint after each epoch
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            logging_dir=str(self.checkpoint_dir / "logs"),
            logging_steps=10,
            save_total_limit=2,  # Keep only 2 most recent checkpoints
            report_to="none",  # Disable wandb/tensorboard
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=self._compute_metrics
        )
        
        logger.info(f"Trainer configured with epochs={epochs}, batch_size={batch_size}, lr={learning_rate}")
        
        # Step 7: Train model with Trainer API
        logger.info("Starting training...")
        train_result = trainer.train()
        logger.info(f"Training complete. Loss: {train_result.training_loss:.4f}")
        
        # Evaluate on validation set
        logger.info("Evaluating on validation set...")
        eval_metrics = trainer.evaluate()
        logger.info(f"Validation metrics: {eval_metrics}")
        
        # Step 8: Semi-supervised learning if unlabeled data provided
        if unlabeled_data and len(unlabeled_data) > 0:
            logger.info(f"Performing semi-supervised learning with {len(unlabeled_data)} unlabeled examples...")
            eval_metrics = self._semi_supervised_iteration(
                labeled_data=labeled_data,
                unlabeled_data=unlabeled_data,
                confidence_threshold=0.9
            )
            logger.info(f"Semi-supervised learning complete. Updated metrics: {eval_metrics}")
        
        # Step 9: Save model, tokenizer, and label map
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
        
        # Return evaluation metrics
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
        confidence_threshold: float = 0.9
    ) -> Dict[str, float]:
        """
        Perform one iteration of semi-supervised learning using pseudo-labeling.
        
        This method implements the pseudo-labeling algorithm:
        1. Predict labels for unlabeled data
        2. Filter predictions with confidence >= threshold
        3. Add high-confidence predictions as pseudo-labeled examples
        4. Combine with original labeled data
        5. Re-train model for 1 epoch
        
        Args:
            labeled_data: Original labeled examples
            unlabeled_data: Unlabeled texts to generate pseudo-labels for
            confidence_threshold: Minimum confidence for pseudo-labels (default: 0.9)
        
        Returns:
            Updated evaluation metrics after retraining
        
        Algorithm:
        - Uses high confidence threshold (0.9) to avoid confirmation bias
        - Only adds pseudo-labels that model is very confident about
        - Re-trains for 1 epoch to incorporate pseudo-labeled data
        
        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
        """
        logger.info(f"Starting semi-supervised iteration with {len(unlabeled_data)} unlabeled examples")
        logger.info(f"Confidence threshold: {confidence_threshold}")
        
        # Predict labels for unlabeled data
        logger.info("Generating predictions for unlabeled data...")
        pseudo_labeled_data = []
        
        for text in unlabeled_data:
            predictions = self.predict(text, top_k=10)  # Get more predictions for multi-label
            
            # Filter high-confidence predictions
            high_conf_labels = [
                taxonomy_id for taxonomy_id, conf in predictions.items()
                if conf >= confidence_threshold
            ]
            
            # Only add if we have at least one high-confidence prediction
            if high_conf_labels:
                pseudo_labeled_data.append((text, high_conf_labels))
        
        logger.info(f"Generated {len(pseudo_labeled_data)} pseudo-labeled examples")
        
        if not pseudo_labeled_data:
            logger.warning("No high-confidence pseudo-labels generated, skipping semi-supervised iteration")
            return {}
        
        # Combine with original labeled data
        combined_data = labeled_data + pseudo_labeled_data
        logger.info(f"Combined dataset size: {len(combined_data)} examples")
        
        # Re-train for 1 epoch
        logger.info("Re-training model with pseudo-labeled data...")
        eval_metrics = self.fine_tune(
            labeled_data=combined_data,
            unlabeled_data=None,  # Don't recurse
            epochs=1,  # Single epoch for semi-supervised iteration
            batch_size=16,
            learning_rate=1e-5  # Lower learning rate for fine-tuning
        )
        
        logger.info("Semi-supervised iteration complete")
        return eval_metrics

    def predict(
        self,
        text: str,
        top_k: int = 5
    ) -> Dict[str, float]:
        """
        Predict taxonomy categories for a single text.
        
        This method performs inference on a single text input and returns
        the top-K predicted taxonomy node IDs with confidence scores.
        
        Args:
            text: Input text to classify
            top_k: Number of top predictions to return (default: 5)
        
        Returns:
            Dictionary mapping taxonomy_node_id to confidence score
            Example: {"node_id_1": 0.95, "node_id_2": 0.87, ...}
        
        Algorithm:
        1. Load model if not already loaded (lazy loading)
        2. Tokenize input text
        3. Forward pass through model
        4. Apply sigmoid activation to get probabilities
        5. Get top-K predictions
        6. Convert label indices to taxonomy node IDs
        
        Performance: <100ms per prediction
        
        Requirements: 2.4, 2.5, 2.8
        """
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
            max_length=512,
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
        
        # Convert to taxonomy node IDs with confidence scores
        predictions = {}
        for idx in top_indices:
            if idx < len(self.id_to_label):
                taxonomy_id = self.id_to_label[idx]
                confidence = float(probs[idx])
                predictions[taxonomy_id] = confidence
        
        return predictions

    def predict_batch(
        self,
        texts: List[str],
        top_k: int = 5
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
        batch_size = 32 if torch.cuda.is_available() else 8
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
                max_length=512,
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
        limit: int = 100
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
        from backend.app.database.models import Resource, ResourceTaxonomy
        
        # Step 1: Query resources (prioritize predicted classifications)
        query = self.db.query(Resource)
        
        # Filter by resource_ids if provided
        if resource_ids:
            query = query.filter(Resource.id.in_(resource_ids))
        
        # Prioritize resources with predicted classifications
        # Join with ResourceTaxonomy to find resources that have been classified
        query = query.outerjoin(ResourceTaxonomy).filter(
            (ResourceTaxonomy.is_predicted == True) | (ResourceTaxonomy.id == None)
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
                predictions = self.predict(text, top_k=10)  # Get more predictions for better uncertainty estimation
                
                if not predictions:
                    logger.debug(f"No predictions for resource {resource.id}")
                    continue
                
                # Get probability array
                probs = np.array(list(predictions.values()))
                
                # Step 4: Compute entropy uncertainty metric
                # Entropy: -Σ(p * log(p))
                # Higher entropy = more uncertain
                epsilon = 1e-10  # Avoid log(0)
                entropy = -np.sum(probs * np.log(probs + epsilon))
                
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
        
        from backend.app.database.models import Resource, ResourceTaxonomy, TaxonomyNode
        
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
                ResourceTaxonomy.is_predicted == True
            ).delete()
            
            logger.info(f"Removed {deleted_count} predicted classifications")
            
            # Step 3: Add human-labeled classifications
            for taxonomy_id in correct_taxonomy_ids:
                # Check if manual classification already exists
                existing = self.db.query(ResourceTaxonomy).filter(
                    ResourceTaxonomy.resource_id == resource_id,
                    ResourceTaxonomy.taxonomy_node_id == taxonomy_id,
                    ResourceTaxonomy.is_predicted == False
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
                ResourceTaxonomy.is_predicted == False,
                ResourceTaxonomy.predicted_by == "manual"
            ).count()
            
            logger.info(f"Total manual classifications: {manual_count}")
            
            # Step 5: Trigger retraining notification if threshold met
            RETRAINING_THRESHOLD = 100
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
