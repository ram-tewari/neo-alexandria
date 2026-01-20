"""
Automated Retraining Pipeline

This module implements the automated retraining pipeline that checks for new data,
determines if retraining is needed, trains new model versions, evaluates improvements,
and promotes models to production if they exceed performance thresholds.

Usage:
    python backend/scripts/training/retrain_pipeline.py --config config/retraining_config.json
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.dataset_acquisition.arxiv_collector import ArxivCollector
from scripts.dataset_acquisition.dataset_preprocessor import DatasetPreprocessor
from scripts.training.train_classification import ClassificationTrainer
from scripts.deployment.model_versioning import ModelVersioning

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RetrainingPipeline:
    """
    Automated retraining pipeline for ML models.

    Checks for new data from arXiv API, determines if retraining is needed based on
    data growth thresholds, trains new model versions, evaluates improvements against
    production models, and promotes new versions if they exceed improvement thresholds.
    """

    def __init__(self, config_path: str = "backend/config/retraining_config.json"):
        """
        Initialize retraining pipeline with configuration.

        Args:
            config_path: Path to retraining configuration JSON file
        """
        logger.info(f"Initializing RetrainingPipeline with config: {config_path}")

        # Load configuration
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Initialize components
        self.arxiv_collector = ArxivCollector(
            output_dir=self.config.get("data_dir", "backend/data/raw/arxiv")
        )
        self.preprocessor = DatasetPreprocessor()
        self.versioning = ModelVersioning(
            base_dir=self.config.get("model_base_dir", "backend/models/classification")
        )

        # Set up paths
        self.data_dir = Path(self.config.get("data_dir", "backend/data"))
        self.raw_data_dir = self.data_dir / "raw" / "arxiv"
        self.processed_data_dir = self.data_dir / "processed"
        self.splits_dir = self.data_dir / "splits" / "arxiv_classification"

        # Create directories if they don't exist
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        self.splits_dir.mkdir(parents=True, exist_ok=True)

        logger.info("RetrainingPipeline initialized successfully")
        logger.info(f"Data directory: {self.data_dir}")
        logger.info(f"Model base directory: {self.versioning.base_dir}")

    def _load_config(self) -> Dict:
        """
        Load configuration from JSON file.

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            config = json.load(f)

        logger.info(f"Loaded configuration from {self.config_path}")
        logger.info(f"Schedule: {config.get('schedule', 'not set')}")
        logger.info(
            f"Data growth threshold: {config.get('data_growth_threshold', 0.10)}"
        )
        logger.info(f"Promotion threshold: {config.get('promotion_threshold', 0.02)}")

        return config

    def check_for_new_data(self) -> Dict:
        """
        Check arXiv API for new papers published since last training.

        Queries the version registry to get the last training date, then checks
        arXiv for papers published after that date across all CS categories.

        Returns:
            Dictionary with:
                - new_data_count: Total number of new papers found
                - new_papers: List of new paper metadata
                - last_training_date: Date of last training run
                - categories: Dictionary of paper counts by category
        """
        logger.info("Checking for new data from arXiv API...")

        # Get last training date from version registry
        last_training_date = self._get_last_training_date()
        logger.info(f"Last training date: {last_training_date}")

        # Define CS categories to check
        categories = [
            "cs.AI",
            "cs.CL",
            "cs.CV",
            "cs.LG",
            "cs.CR",
            "cs.DB",
            "cs.DC",
            "cs.NE",
            "cs.RO",
            "cs.SE",
        ]

        # Collect new papers from each category
        new_papers = []
        category_counts = {}

        for category in categories:
            logger.info(f"Checking category: {category}")
            try:
                papers = self.arxiv_collector.collect_papers_by_category(
                    category=category,
                    max_results=1000,  # Limit per category
                    start_date=last_training_date,
                )
                category_counts[category] = len(papers)
                new_papers.extend(papers)
                logger.info(f"Found {len(papers)} new papers in {category}")
            except Exception as e:
                logger.error(f"Error collecting papers from {category}: {e}")
                category_counts[category] = 0

        new_data_count = len(new_papers)
        logger.info(f"Total new papers found: {new_data_count}")

        # Log statistics by category
        for category, count in category_counts.items():
            logger.info(f"  {category}: {count} papers")

        return {
            "new_data_count": new_data_count,
            "new_papers": new_papers,
            "last_training_date": last_training_date,
            "categories": category_counts,
        }

    def _get_last_training_date(self) -> str:
        """
        Get the date of the last training run from version registry.

        Returns:
            ISO 8601 date string (YYYY-MM-DD) of last training, or default date
        """
        try:
            # Load version registry
            registry_path = self.versioning.base_dir / "version_registry.json"

            if not registry_path.exists():
                # No previous training, use default start date
                default_date = self.config.get("default_start_date", "2020-01-01")
                logger.warning(
                    f"No version registry found, using default date: {default_date}"
                )
                return default_date

            with open(registry_path, "r") as f:
                registry = json.load(f)

            # Get the most recent version
            versions = registry.get("versions", [])
            if not versions:
                default_date = self.config.get("default_start_date", "2020-01-01")
                logger.warning(
                    f"No versions in registry, using default date: {default_date}"
                )
                return default_date

            # Sort by created_at and get the most recent
            versions_sorted = sorted(
                versions, key=lambda v: v.get("created_at", ""), reverse=True
            )
            latest_version = versions_sorted[0]

            # Extract date from created_at timestamp
            created_at = latest_version.get("created_at", "")
            if created_at:
                # Parse ISO 8601 timestamp and extract date
                date_str = created_at.split("T")[0]
                logger.info(
                    f"Last training date from version {latest_version.get('version')}: {date_str}"
                )
                return date_str
            else:
                default_date = self.config.get("default_start_date", "2020-01-01")
                logger.warning(
                    f"No created_at in latest version, using default date: {default_date}"
                )
                return default_date

        except Exception as e:
            logger.error(f"Error getting last training date: {e}")
            default_date = self.config.get("default_start_date", "2020-01-01")
            logger.warning(f"Using default date: {default_date}")
            return default_date

    def should_retrain(self, new_data_count: int, current_dataset_size: int) -> bool:
        """
        Determine if retraining is needed based on data growth.

        Calculates the growth rate and compares it to the configured threshold.

        Args:
            new_data_count: Number of new papers available
            current_dataset_size: Size of current training dataset

        Returns:
            True if retraining should be triggered, False otherwise
        """
        logger.info("Evaluating retraining trigger logic...")
        logger.info(f"Current dataset size: {current_dataset_size}")
        logger.info(f"New data count: {new_data_count}")

        # Avoid division by zero
        if current_dataset_size == 0:
            logger.warning("Current dataset size is 0, triggering retraining")
            return True

        # Calculate growth rate
        growth_rate = new_data_count / current_dataset_size
        logger.info(f"Growth rate: {growth_rate:.2%}")

        # Get threshold from config
        threshold = self.config.get("data_growth_threshold", 0.10)
        logger.info(f"Configured threshold: {threshold:.2%}")

        # Determine if retraining is needed
        should_retrain = growth_rate > threshold

        if should_retrain:
            logger.info(
                f"✓ Retraining triggered: growth rate {growth_rate:.2%} exceeds "
                f"threshold {threshold:.2%}"
            )
        else:
            logger.info(
                f"✗ Retraining not needed: growth rate {growth_rate:.2%} below "
                f"threshold {threshold:.2%}"
            )

        return should_retrain

    def augment_dataset(
        self, existing_data: List[Dict], new_data: List[Dict]
    ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Augment existing dataset with new data and create new splits.

        Combines existing and new data, preprocesses the new data, and creates
        new stratified train/val/test splits.

        Args:
            existing_data: List of existing training samples
            new_data: List of new paper metadata from arXiv

        Returns:
            Tuple of (train_samples, val_samples, test_samples)
        """
        logger.info("Augmenting dataset with new data...")
        logger.info(f"Existing data size: {len(existing_data)}")
        logger.info(f"New data size: {len(new_data)}")

        # Convert new papers to training samples format
        new_samples = []
        for paper in new_data:
            # Combine title and abstract as text
            text = f"{paper.get('title', '')}. {paper.get('abstract', '')}"

            # Use primary category as label
            label = paper.get("primary_category", paper.get("categories", [""])[0])

            sample = {
                "text": text,
                "label": label,
                "arxiv_id": paper.get("arxiv_id", ""),
                "title": paper.get("title", ""),
                "authors": paper.get("authors", []),
                "published": paper.get("published", ""),
            }
            new_samples.append(sample)

        logger.info(f"Converted {len(new_samples)} new papers to training samples")

        # Preprocess new samples
        logger.info("Preprocessing new samples...")
        preprocessed_new = []
        for sample in new_samples:
            # Clean text
            cleaned_text = self.preprocessor.clean_text(sample["text"])

            # Validate quality
            if len(cleaned_text.split()) >= 50:  # Minimum word count
                sample["text"] = cleaned_text
                preprocessed_new.append(sample)

        logger.info(f"After preprocessing: {len(preprocessed_new)} samples")

        # Combine with existing data
        augmented_data = existing_data + preprocessed_new
        logger.info(f"Augmented dataset size: {len(augmented_data)}")

        # Deduplicate by arXiv ID
        seen_ids = set()
        deduplicated_data = []
        for sample in augmented_data:
            arxiv_id = sample.get("arxiv_id", "")
            if arxiv_id and arxiv_id not in seen_ids:
                seen_ids.add(arxiv_id)
                deduplicated_data.append(sample)
            elif not arxiv_id:
                # Keep samples without arXiv ID
                deduplicated_data.append(sample)

        logger.info(f"After deduplication: {len(deduplicated_data)} samples")

        # Save augmented dataset to temporary file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        augmented_dir = (
            self.splits_dir.parent / f"arxiv_classification_augmented_{timestamp}"
        )
        augmented_dir.mkdir(parents=True, exist_ok=True)

        # Save augmented dataset with metadata
        augmented_dataset = {
            "metadata": {
                "num_samples": len(deduplicated_data),
                "created_at": datetime.now().isoformat(),
                "source": "augmented",
            },
            "samples": deduplicated_data,
        }

        augmented_file = augmented_dir / "augmented_dataset.json"
        with open(augmented_file, "w") as f:
            json.dump(augmented_dataset, f, indent=2)

        logger.info(f"Saved augmented dataset to {augmented_file}")

        # Create new train/val/test splits
        logger.info("Creating new stratified splits...")
        train_samples, val_samples, test_samples = (
            self.preprocessor.create_train_val_test_split(
                input_file=str(augmented_file),
                output_dir=str(augmented_dir),
                train_ratio=0.8,
                val_ratio=0.1,
                test_ratio=0.1,
                random_seed=42,
            )
        )

        logger.info(
            f"Train: {len(train_samples)}, Val: {len(val_samples)}, Test: {len(test_samples)}"
        )
        logger.info(f"Saved splits to {augmented_dir}")

        return train_samples, val_samples, test_samples

    def train_new_version(
        self, train_samples: List[Dict], val_samples: List[Dict], current_version: str
    ) -> Tuple[str, Dict]:
        """
        Train a new model version with augmented dataset.

        Increments the minor version number, trains the model, evaluates on
        validation set, and saves the checkpoint.

        Args:
            train_samples: Training data samples
            val_samples: Validation data samples
            current_version: Current production version (e.g., "v1.1.0")

        Returns:
            Tuple of (new_version, metrics)
        """
        logger.info("Training new model version...")
        logger.info(f"Current version: {current_version}")

        # Increment minor version
        new_version = self._increment_version(current_version, level="minor")
        logger.info(f"New version: {new_version}")

        # Set up output directory
        output_dir = self.versioning.base_dir / f"arxiv_{new_version}"
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")

        # Initialize trainer
        trainer = ClassificationTrainer(
            model_name=self.config.get("model_name", "distilbert-base-uncased"),
            output_dir=str(output_dir),
        )

        # Get training hyperparameters from config
        epochs = self.config.get("epochs", 3)
        batch_size = self.config.get("batch_size", 16)
        learning_rate = self.config.get("learning_rate", 2e-5)

        logger.info("Training hyperparameters:")
        logger.info(f"  Epochs: {epochs}")
        logger.info(f"  Batch size: {batch_size}")
        logger.info(f"  Learning rate: {learning_rate}")

        # Train model
        start_time = datetime.now()
        logger.info("Starting training...")

        try:
            metrics = trainer.train(
                train_samples=train_samples,
                val_samples=val_samples,
                epochs=epochs,
                batch_size=batch_size,
                learning_rate=learning_rate,
            )

            end_time = datetime.now()
            training_time = (end_time - start_time).total_seconds()

            logger.info(f"Training completed in {training_time:.0f} seconds")
            logger.info(f"Validation accuracy: {metrics.get('accuracy', 0):.4f}")
            logger.info(f"Validation F1: {metrics.get('f1', 0):.4f}")

            # Add training time to metrics
            metrics["training_time_seconds"] = int(training_time)
            metrics["dataset_size"] = len(train_samples)

            # Create version metadata
            metadata = {
                "version": new_version,
                "created_at": datetime.now().isoformat(),
                "model_name": self.config.get("model_name", "distilbert-base-uncased"),
                "dataset": {
                    "source": "arXiv",
                    "num_samples": len(train_samples),
                    "num_val_samples": len(val_samples),
                },
                "hyperparameters": {
                    "epochs": epochs,
                    "batch_size": batch_size,
                    "learning_rate": learning_rate,
                },
                "metrics": metrics,
            }

            # Save metadata
            with open(output_dir / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Saved model version {new_version}")

            return new_version, metrics

        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise

    def _increment_version(self, version: str, level: str = "minor") -> str:
        """
        Increment semantic version number.

        Args:
            version: Current version string (e.g., "v1.1.0")
            level: Version level to increment ("major", "minor", or "patch")

        Returns:
            New version string
        """
        # Remove 'v' prefix if present
        version_str = version.lstrip("v")

        # Split into major.minor.patch
        parts = version_str.split(".")
        if len(parts) != 3:
            logger.warning(f"Invalid version format: {version}, using v1.0.0")
            return "v1.0.0"

        major, minor, patch = map(int, parts)

        # Increment based on level
        if level == "major":
            major += 1
            minor = 0
            patch = 0
        elif level == "minor":
            minor += 1
            patch = 0
        elif level == "patch":
            patch += 1
        else:
            logger.warning(f"Unknown version level: {level}, incrementing minor")
            minor += 1
            patch = 0

        new_version = f"v{major}.{minor}.{patch}"
        logger.info(f"Incremented version from {version} to {new_version}")

        return new_version

    def evaluate_improvement(
        self, new_version: str, production_version: str, test_samples: List[Dict]
    ) -> Dict:
        """
        Evaluate improvement of new model vs production model.

        Loads both models, evaluates them on the held-out test set, and
        calculates the improvement in accuracy.

        Args:
            new_version: New model version to evaluate
            production_version: Current production model version
            test_samples: Test data samples

        Returns:
            Dictionary with comparison metrics and improvement
        """
        logger.info("Evaluating model improvement...")
        logger.info(f"Production version: {production_version}")
        logger.info(f"New version: {new_version}")
        logger.info(f"Test set size: {len(test_samples)}")

        # Load production model
        logger.info("Loading production model...")
        prod_model_dir = self.versioning.base_dir / f"arxiv_{production_version}"
        prod_trainer = ClassificationTrainer(
            model_name=self.config.get("model_name", "distilbert-base-uncased"),
            output_dir=str(prod_model_dir),
        )

        try:
            prod_trainer.load_model()
            logger.info("Production model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load production model: {e}")
            raise

        # Load new model
        logger.info("Loading new model...")
        new_model_dir = self.versioning.base_dir / f"arxiv_{new_version}"
        new_trainer = ClassificationTrainer(
            model_name=self.config.get("model_name", "distilbert-base-uncased"),
            output_dir=str(new_model_dir),
        )

        try:
            new_trainer.load_model()
            logger.info("New model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load new model: {e}")
            raise

        # Evaluate production model
        logger.info("Evaluating production model on test set...")
        prod_metrics = prod_trainer.evaluate(test_samples)
        logger.info(f"Production accuracy: {prod_metrics.get('accuracy', 0):.4f}")
        logger.info(f"Production F1: {prod_metrics.get('f1', 0):.4f}")

        # Evaluate new model
        logger.info("Evaluating new model on test set...")
        new_metrics = new_trainer.evaluate(test_samples)
        logger.info(f"New accuracy: {new_metrics.get('accuracy', 0):.4f}")
        logger.info(f"New F1: {new_metrics.get('f1', 0):.4f}")

        # Calculate improvement
        accuracy_improvement = new_metrics.get("accuracy", 0) - prod_metrics.get(
            "accuracy", 0
        )
        f1_improvement = new_metrics.get("f1", 0) - prod_metrics.get("f1", 0)

        logger.info(
            f"Accuracy improvement: {accuracy_improvement:+.4f} ({accuracy_improvement * 100:+.2f}%)"
        )
        logger.info(
            f"F1 improvement: {f1_improvement:+.4f} ({f1_improvement * 100:+.2f}%)"
        )

        # Create comparison dictionary
        comparison = {
            "production_version": production_version,
            "new_version": new_version,
            "test_set_size": len(test_samples),
            "production_metrics": {
                "accuracy": prod_metrics.get("accuracy", 0),
                "f1": prod_metrics.get("f1", 0),
            },
            "new_metrics": {
                "accuracy": new_metrics.get("accuracy", 0),
                "f1": new_metrics.get("f1", 0),
            },
            "improvement": {
                "accuracy": accuracy_improvement,
                "accuracy_percent": accuracy_improvement * 100,
                "f1": f1_improvement,
                "f1_percent": f1_improvement * 100,
            },
            "evaluated_at": datetime.now().isoformat(),
        }

        # Save comparison results
        new_model_dir.mkdir(parents=True, exist_ok=True)
        comparison_file = new_model_dir / "comparison_results.json"
        with open(comparison_file, "w") as f:
            json.dump(comparison, f, indent=2)

        logger.info(f"Saved comparison results to {comparison_file}")

        return comparison

    def promote_if_better(self, new_version: str, comparison: Dict) -> bool:
        """
        Promote new model to production if improvement exceeds threshold.

        Checks if the accuracy improvement exceeds the configured promotion
        threshold. If yes, promotes the new version to production. If no,
        archives the new version.

        Args:
            new_version: New model version
            comparison: Comparison dictionary from evaluate_improvement

        Returns:
            True if promoted, False otherwise
        """
        logger.info("Evaluating promotion decision...")

        # Get improvement and threshold
        accuracy_improvement = comparison["improvement"]["accuracy"]
        promotion_threshold = self.config.get("promotion_threshold", 0.02)

        logger.info(
            f"Accuracy improvement: {accuracy_improvement:+.4f} ({accuracy_improvement * 100:+.2f}%)"
        )
        logger.info(
            f"Promotion threshold: {promotion_threshold:.4f} ({promotion_threshold * 100:.2f}%)"
        )

        # Check if improvement exceeds threshold
        if accuracy_improvement > promotion_threshold:
            logger.info(
                f"✓ Improvement {accuracy_improvement * 100:+.2f}% exceeds threshold "
                f"{promotion_threshold * 100:.2f}%, promoting to production"
            )

            # Promote to production
            try:
                self.versioning.promote_to_production(new_version)
                logger.info(f"Successfully promoted {new_version} to production")

                # Update version metadata
                new_model_dir = self.versioning.base_dir / f"arxiv_{new_version}"
                metadata_file = new_model_dir / "metadata.json"

                if metadata_file.exists():
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)

                    metadata["promoted_at"] = datetime.now().isoformat()
                    metadata["promotion_reason"] = (
                        f"Accuracy improvement {accuracy_improvement * 100:+.2f}% "
                        f"exceeds threshold {promotion_threshold * 100:.2f}%"
                    )

                    with open(metadata_file, "w") as f:
                        json.dump(metadata, f, indent=2)

                return True

            except Exception as e:
                logger.error(f"Failed to promote model: {e}")
                return False
        else:
            logger.info(
                f"✗ Improvement {accuracy_improvement * 100:+.2f}% below threshold "
                f"{promotion_threshold * 100:.2f}%, not promoting"
            )

            # Archive the new version
            try:
                new_model_dir = self.versioning.base_dir / f"arxiv_{new_version}"
                metadata_file = new_model_dir / "metadata.json"

                if metadata_file.exists():
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)

                    metadata["status"] = "archived"
                    metadata["archive_reason"] = (
                        f"Accuracy improvement {accuracy_improvement * 100:+.2f}% "
                        f"below threshold {promotion_threshold * 100:.2f}%"
                    )

                    with open(metadata_file, "w") as f:
                        json.dump(metadata, f, indent=2)

                logger.info(f"Archived {new_version}")

            except Exception as e:
                logger.error(f"Failed to archive model: {e}")

            return False

    def send_notification(
        self, subject: str, message: str, results: Optional[Dict] = None
    ):
        """
        Send notification about retraining results.

        Sends notifications via email and Slack with retraining results including
        dataset size, metrics, and promotion decision.

        Args:
            subject: Notification subject line
            message: Notification message body
            results: Optional dictionary with retraining results
        """
        logger.info(f"Sending notification: {subject}")

        # Build notification message
        notification_text = f"{subject}\n\n{message}"

        if results:
            notification_text += "\n\n=== Retraining Results ===\n"

            # Dataset information
            if "dataset_size" in results:
                notification_text += "\nDataset:\n"
                notification_text += f"  Previous: {results.get('previous_dataset_size', 'N/A')} samples\n"
                notification_text += f"  New: {results['dataset_size']} samples\n"
                notification_text += (
                    f"  Growth: {results.get('new_data_count', 0)} new papers\n"
                )

            # Model versions
            if "new_version" in results:
                notification_text += "\nModel Versions:\n"
                notification_text += (
                    f"  Production: {results.get('production_version', 'N/A')}\n"
                )
                notification_text += f"  New: {results['new_version']}\n"

            # Performance metrics
            if "comparison" in results:
                comp = results["comparison"]
                notification_text += "\nPerformance:\n"

                prod_acc = comp.get("production_metrics", {}).get("accuracy", 0)
                new_acc = comp.get("new_metrics", {}).get("accuracy", 0)
                improvement = comp.get("improvement", {}).get("accuracy_percent", 0)

                notification_text += f"  Production: {prod_acc:.2%} accuracy\n"
                notification_text += f"  New: {new_acc:.2%} accuracy\n"
                notification_text += f"  Improvement: {improvement:+.2f}%\n"

            # Decision
            if "promoted" in results:
                if results["promoted"]:
                    notification_text += "\n✓ Decision: PROMOTED to production\n"
                    notification_text += f"  Reason: Exceeds {self.config.get('promotion_threshold', 0.02) * 100:.0f}% improvement threshold\n"
                else:
                    notification_text += "\n✗ Decision: NOT PROMOTED\n"
                    notification_text += f"  Reason: Below {self.config.get('promotion_threshold', 0.02) * 100:.0f}% improvement threshold\n"

            # Training time
            if "training_time_seconds" in results:
                hours = results["training_time_seconds"] / 3600
                notification_text += f"\nTraining time: {hours:.1f} hours\n"

        logger.info(f"Notification message:\n{notification_text}")

        # Send email notification
        if self.config.get("notification_email"):
            try:
                self._send_email(
                    to=self.config["notification_email"],
                    subject=subject,
                    body=notification_text,
                )
                logger.info(f"Email sent to {self.config['notification_email']}")
            except Exception as e:
                logger.error(f"Failed to send email: {e}")

        # Send Slack notification
        if self.config.get("slack_webhook"):
            try:
                self._send_slack(
                    webhook_url=self.config["slack_webhook"], message=notification_text
                )
                logger.info("Slack notification sent")
            except Exception as e:
                logger.error(f"Failed to send Slack notification: {e}")

    def _send_email(self, to: str, subject: str, body: str):
        """
        Send email notification.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # Get SMTP configuration from config
        smtp_host = self.config.get("smtp_host", "localhost")
        smtp_port = self.config.get("smtp_port", 587)
        smtp_user = self.config.get("smtp_user")
        smtp_password = self.config.get("smtp_password")
        from_email = self.config.get("from_email", "noreply@neoalexandria.ai")

        # Create message
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if smtp_user and smtp_password:
                server.starttls()
                server.login(smtp_user, smtp_password)
            server.send_message(msg)

    def _send_slack(self, webhook_url: str, message: str):
        """
        Send Slack notification.

        Args:
            webhook_url: Slack webhook URL
            message: Message to send
        """
        import requests

        # Format message for Slack
        payload = {"text": f"🤖 ML Model Retraining\n```\n{message}\n```"}

        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()

    def run_pipeline(self, trigger_type: str = "scheduled") -> Dict:
        """
        Execute complete retraining pipeline.

        Orchestrates the full retraining workflow:
        1. Check for new data
        2. Determine if retraining is needed
        3. If yes: augment dataset, train new version, evaluate improvement, promote if better
        4. Send notification with results
        5. Handle errors gracefully with retry logic

        Args:
            trigger_type: Type of trigger ("scheduled", "manual", "data_growth")

        Returns:
            Dictionary with pipeline results
        """
        logger.info("=" * 80)
        logger.info("Starting Automated Retraining Pipeline")
        logger.info(f"Trigger type: {trigger_type}")
        logger.info(f"Started at: {datetime.now().isoformat()}")
        logger.info("=" * 80)

        pipeline_start = datetime.now()
        results = {
            "trigger_type": trigger_type,
            "started_at": pipeline_start.isoformat(),
            "status": "running",
        }

        try:
            # Step 1: Check for new data
            logger.info("\n[Step 1/6] Checking for new data...")
            new_data_info = self.check_for_new_data()

            new_data_count = new_data_info["new_data_count"]
            new_papers = new_data_info["new_papers"]

            results["new_data_count"] = new_data_count
            results["last_training_date"] = new_data_info["last_training_date"]

            if new_data_count == 0:
                logger.info("No new data found, skipping retraining")
                results["status"] = "skipped"
                results["reason"] = "No new data available"

                self.send_notification(
                    subject="Retraining Pipeline - No New Data",
                    message="No new papers found since last training. Retraining skipped.",
                    results=results,
                )

                return results

            # Step 2: Load existing dataset
            logger.info("\n[Step 2/6] Loading existing dataset...")
            existing_train_file = self.splits_dir / "train.json"

            if not existing_train_file.exists():
                logger.error(f"Existing training data not found: {existing_train_file}")
                raise FileNotFoundError(
                    f"Training data not found: {existing_train_file}"
                )

            with open(existing_train_file, "r") as f:
                existing_data = json.load(f)

            current_dataset_size = len(existing_data)
            results["previous_dataset_size"] = current_dataset_size

            logger.info(f"Loaded {current_dataset_size} existing samples")

            # Step 3: Determine if retraining is needed
            logger.info("\n[Step 3/6] Evaluating retraining trigger...")
            should_retrain = self.should_retrain(new_data_count, current_dataset_size)

            if not should_retrain:
                logger.info("Retraining not needed based on growth threshold")
                results["status"] = "skipped"
                results["reason"] = "Data growth below threshold"

                self.send_notification(
                    subject="Retraining Pipeline - Threshold Not Met",
                    message=f"New data count ({new_data_count}) below threshold. Retraining skipped.",
                    results=results,
                )

                return results

            # Step 4: Augment dataset
            logger.info("\n[Step 4/6] Augmenting dataset with new data...")
            train_samples, val_samples, test_samples = self.augment_dataset(
                existing_data=existing_data, new_data=new_papers
            )

            results["dataset_size"] = len(train_samples)

            # Step 5: Get current production version
            logger.info("\n[Step 5/6] Getting current production version...")
            production_version = self._get_production_version()
            results["production_version"] = production_version

            # Step 6: Train new version
            logger.info("\n[Step 6/6] Training new model version...")
            new_version, training_metrics = self.train_new_version(
                train_samples=train_samples,
                val_samples=val_samples,
                current_version=production_version,
            )

            results["new_version"] = new_version
            results["training_metrics"] = training_metrics
            results["training_time_seconds"] = training_metrics.get(
                "training_time_seconds", 0
            )

            # Step 7: Evaluate improvement
            logger.info("\n[Step 7/7] Evaluating improvement vs production...")
            comparison = self.evaluate_improvement(
                new_version=new_version,
                production_version=production_version,
                test_samples=test_samples,
            )

            results["comparison"] = comparison

            # Step 8: Promote if better
            logger.info("\n[Step 8/8] Evaluating promotion decision...")
            promoted = self.promote_if_better(
                new_version=new_version, comparison=comparison
            )

            results["promoted"] = promoted
            results["status"] = "completed"

            # Calculate total time
            pipeline_end = datetime.now()
            total_time = (pipeline_end - pipeline_start).total_seconds()
            results["completed_at"] = pipeline_end.isoformat()
            results["total_time_seconds"] = int(total_time)

            logger.info("=" * 80)
            logger.info("Retraining Pipeline Completed Successfully")
            logger.info(f"Total time: {total_time / 3600:.1f} hours")
            logger.info("=" * 80)

            # Send success notification
            if promoted:
                subject = f"Retraining Pipeline - Model Promoted: {new_version}"
                message = f"New model {new_version} has been promoted to production!"
            else:
                subject = f"Retraining Pipeline - Model Not Promoted: {new_version}"
                message = f"New model {new_version} trained but not promoted (below threshold)."

            self.send_notification(subject=subject, message=message, results=results)

            return results

        except Exception as e:
            logger.error(f"Pipeline failed with error: {e}", exc_info=True)

            pipeline_end = datetime.now()
            total_time = (pipeline_end - pipeline_start).total_seconds()

            results["status"] = "failed"
            results["error_message"] = str(e)
            results["completed_at"] = pipeline_end.isoformat()
            results["total_time_seconds"] = int(total_time)

            # Send failure notification
            self.send_notification(
                subject="Retraining Pipeline - Failed",
                message=f"Pipeline failed with error: {e}",
                results=results,
            )

            raise

    def _get_production_version(self) -> str:
        """
        Get current production version from version registry.

        Returns:
            Production version string (e.g., "v1.1.0")
        """
        try:
            registry_path = self.versioning.base_dir / "version_registry.json"

            if not registry_path.exists():
                logger.warning("No version registry found, using default v1.0.0")
                return "v1.0.0"

            with open(registry_path, "r") as f:
                registry = json.load(f)

            production_version = registry.get("production_version", "v1.0.0")
            logger.info(f"Current production version: {production_version}")

            return production_version

        except Exception as e:
            logger.error(f"Error getting production version: {e}")
            return "v1.0.0"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run automated retraining pipeline")
    parser.add_argument(
        "--config",
        type=str,
        default="backend/config/retraining_config.json",
        help="Path to retraining configuration file",
    )
    parser.add_argument(
        "--trigger",
        type=str,
        default="manual",
        choices=["scheduled", "manual", "data_growth", "performance_degradation"],
        help="Trigger type for retraining",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Check for new data without training"
    )

    args = parser.parse_args()

    # Initialize pipeline
    pipeline = RetrainingPipeline(config_path=args.config)

    if args.dry_run:
        logger.info("Running in dry-run mode (check only, no training)")
        new_data_info = pipeline.check_for_new_data()
        logger.info(f"Found {new_data_info['new_data_count']} new papers")

        # Load existing dataset size
        existing_train_file = pipeline.splits_dir / "train.json"
        if existing_train_file.exists():
            with open(existing_train_file, "r") as f:
                existing_data = json.load(f)
            current_size = len(existing_data)

            should_retrain = pipeline.should_retrain(
                new_data_info["new_data_count"], current_size
            )

            if should_retrain:
                logger.info("✓ Retraining would be triggered")
            else:
                logger.info("✗ Retraining would not be triggered")
    else:
        # Run full pipeline
        results = pipeline.run_pipeline(trigger_type=args.trigger)

        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Status: {results['status']}")
        logger.info(f"Trigger: {results['trigger_type']}")
        logger.info(f"New data: {results.get('new_data_count', 0)} papers")

        if results["status"] == "completed":
            logger.info(f"New version: {results.get('new_version', 'N/A')}")
            logger.info(f"Promoted: {results.get('promoted', False)}")

            if "comparison" in results:
                improvement = results["comparison"]["improvement"]["accuracy_percent"]
                logger.info(f"Improvement: {improvement:+.2f}%")

        logger.info("=" * 80)
