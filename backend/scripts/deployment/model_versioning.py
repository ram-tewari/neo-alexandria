"""
Model versioning system for managing trained model versions.

This module provides the ModelVersioning class for semantic versioning of trained
models, including version creation, metadata storage, version listing/loading,
production promotion, and version comparison.
"""

import json
import logging
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModelVersioning:
    """
    Semantic versioning system for trained models.

    This class manages model versions using semantic versioning (vX.Y.Z) and provides
    functionality for:
    - Creating new model versions with metadata
    - Listing and loading specific versions
    - Promoting versions to production
    - Comparing versions on test data
    - Maintaining a version registry

    Versioning Scheme:
        - Major (X): Architecture changes (e.g., BERT → RoBERTa)
        - Minor (Y): Dataset updates or retraining
        - Patch (Z): Hyperparameter tuning or bug fixes

    Attributes:
        base_dir (Path): Base directory for storing model versions
        registry_file (Path): Path to version registry JSON file
        registry (Dict): Version registry data
    """

    def __init__(self, base_dir: str = "models/classification"):
        """
        Initialize the ModelVersioning system.

        Args:
            base_dir: Base directory for storing model versions
                     (default: "models/classification")
        """
        self.base_dir = Path(base_dir)
        self.registry_file = self.base_dir / "version_registry.json"

        # Create base directory if it doesn't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            f"Model versioning initialized with base directory: {self.base_dir}"
        )

        # Load existing version registry or create new one
        self.registry = self._load_or_create_registry()

        logger.info(
            f"Version registry loaded: {len(self.registry.get('versions', []))} versions"
        )

    def _load_or_create_registry(self) -> Dict[str, Any]:
        """
        Load existing version registry or create a new one.

        Returns:
            Dictionary containing version registry data
        """
        if self.registry_file.exists():
            logger.info(f"Loading existing registry from {self.registry_file}")
            with open(self.registry_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            logger.info("Creating new version registry")
            registry = {
                "versions": [],
                "production_version": None,
                "latest_version": None,
            }
            self._save_registry(registry)
            return registry

    def _save_registry(self, registry: Optional[Dict[str, Any]] = None) -> None:
        """
        Save version registry to file.

        Args:
            registry: Registry data to save (uses self.registry if None)
        """
        if registry is None:
            registry = self.registry

        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)

        logger.debug(f"Registry saved to {self.registry_file}")

    def create_version(
        self, model_path: str, version: str, metadata: Dict[str, Any]
    ) -> str:
        """
        Create a new model version with metadata.

        This method:
        1. Validates version format (vX.Y.Z)
        2. Checks if version already exists
        3. Creates version directory
        4. Copies model files to version directory
        5. Saves metadata to metadata.json
        6. Updates version registry

        Args:
            model_path: Path to the trained model directory
            version: Version string in format vX.Y.Z (e.g., "v1.0.0")
            metadata: Dictionary containing version metadata:
                - model_name: Name of the model architecture
                - dataset: Dataset information (source, size, etc.)
                - hyperparameters: Training hyperparameters
                - metrics: Performance metrics (accuracy, F1, etc.)
                - model_size_mb: Model size in megabytes
                - notes: Optional notes about this version

        Returns:
            Path to the created version directory

        Raises:
            ValueError: If version format is invalid or version already exists
            FileNotFoundError: If model_path doesn't exist
        """
        # Validate version format (vX.Y.Z)
        if not re.match(r"^v\d+\.\d+\.\d+$", version):
            raise ValueError(
                f"Invalid version format: '{version}'. "
                "Expected format: vX.Y.Z (e.g., v1.0.0)"
            )

        logger.info(f"Creating model version: {version}")

        # Check if version already exists
        for existing_version in self.registry.get("versions", []):
            if existing_version["version"] == version:
                raise ValueError(f"Version {version} already exists")

        # Validate model_path exists
        source_path = Path(model_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Model path not found: {model_path}")

        # Create version directory (e.g., models/classification/arxiv_v1.0.0/)
        version_dir = self.base_dir / f"arxiv_{version}"
        if version_dir.exists():
            logger.warning(f"Version directory already exists: {version_dir}")
            shutil.rmtree(version_dir)

        version_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created version directory: {version_dir}")

        # Copy model files to version directory
        logger.info(f"Copying model files from {source_path} to {version_dir}")
        for item in source_path.iterdir():
            if item.is_file():
                shutil.copy2(item, version_dir / item.name)
            elif item.is_dir() and item.name not in ["logs", "__pycache__"]:
                shutil.copytree(item, version_dir / item.name, dirs_exist_ok=True)

        logger.info("Model files copied successfully")

        # Add version and timestamp to metadata
        full_metadata = {
            "version": version,
            "created_at": datetime.now().isoformat(),
            **metadata,
        }

        # Calculate model size if not provided
        if "model_size_mb" not in full_metadata:
            total_size = sum(
                f.stat().st_size for f in version_dir.rglob("*") if f.is_file()
            )
            full_metadata["model_size_mb"] = round(total_size / (1024 * 1024), 2)

        # Save metadata to metadata.json
        metadata_file = version_dir / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(full_metadata, f, indent=2)

        logger.info(f"Metadata saved to {metadata_file}")

        # Update version registry with new version
        version_entry = {
            "version": version,
            "path": str(version_dir),
            "created_at": full_metadata["created_at"],
            "status": "available",
        }

        self.registry["versions"].append(version_entry)
        self.registry["latest_version"] = version
        self._save_registry()

        logger.info(f"Version {version} created successfully")
        logger.info(f"Model size: {full_metadata['model_size_mb']:.2f} MB")
        logger.info(f"Version directory: {version_dir}")

        return str(version_dir)

    def list_versions(self) -> List[Dict[str, Any]]:
        """
        List all available model versions from the registry.

        Returns:
            List of dictionaries containing version information:
                - version: Version string (e.g., "v1.0.0")
                - path: Path to version directory
                - created_at: ISO timestamp of creation
                - status: Version status (available, production, archived)
        """
        versions = self.registry.get("versions", [])
        logger.info(f"Found {len(versions)} versions in registry")
        return versions

    def load_version(self, version: str) -> Tuple[Any, Dict[str, Any]]:
        """
        Load a specific model version with its metadata.

        This method loads the model from the version directory and returns
        both the model and its associated metadata.

        Args:
            version: Version string (e.g., "v1.0.0")

        Returns:
            Tuple of (model, metadata):
                - model: Loaded model object (transformers model)
                - metadata: Dictionary containing version metadata

        Raises:
            ValueError: If version doesn't exist
            FileNotFoundError: If version directory or files are missing
        """
        logger.info(f"Loading model version: {version}")

        # Find version in registry
        version_entry = None
        for v in self.registry.get("versions", []):
            if v["version"] == version:
                version_entry = v
                break

        if version_entry is None:
            available_versions = [
                v["version"] for v in self.registry.get("versions", [])
            ]
            raise ValueError(
                f"Version {version} not found. Available versions: {available_versions}"
            )

        # Get version directory path
        version_dir = Path(version_entry["path"])
        if not version_dir.exists():
            raise FileNotFoundError(f"Version directory not found: {version_dir}")

        # Load metadata from metadata.json
        metadata_file = version_dir / "metadata.json"
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        logger.info(f"Metadata loaded for version {version}")

        # Load model using transformers
        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            logger.info(f"Loading model from {version_dir}")
            model = AutoModelForSequenceClassification.from_pretrained(version_dir)
            tokenizer = AutoTokenizer.from_pretrained(version_dir)

            # Load label mapping if available
            label_map_file = version_dir / "label_map.json"
            if label_map_file.exists():
                with open(label_map_file, "r", encoding="utf-8") as f:
                    label_map = json.load(f)
                logger.info(
                    f"Label mapping loaded: {len(label_map.get('label_to_id', {}))} classes"
                )

            logger.info(f"Model version {version} loaded successfully")

            # Return model with tokenizer and metadata
            model_data = {
                "model": model,
                "tokenizer": tokenizer,
                "label_map": label_map if label_map_file.exists() else None,
            }

            return model_data, metadata

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def promote_to_production(self, version: str) -> None:
        """
        Promote a model version to production.

        This method:
        1. Validates that the version exists
        2. Updates the version registry to mark version as "production"
        3. Creates or updates "production" symlink to version directory
        4. Updates production_version in registry

        Args:
            version: Version string to promote (e.g., "v1.0.0")

        Raises:
            ValueError: If version doesn't exist
        """
        logger.info(f"Promoting version {version} to production")

        # Find version in registry
        version_entry = None
        version_index = None
        for i, v in enumerate(self.registry.get("versions", [])):
            if v["version"] == version:
                version_entry = v
                version_index = i
                break

        if version_entry is None:
            available_versions = [
                v["version"] for v in self.registry.get("versions", [])
            ]
            raise ValueError(
                f"Version {version} not found. Available versions: {available_versions}"
            )

        # Get version directory path
        version_dir = Path(version_entry["path"])
        if not version_dir.exists():
            raise FileNotFoundError(f"Version directory not found: {version_dir}")

        # Update previous production version status to "archived"
        previous_production = self.registry.get("production_version")
        if previous_production:
            for v in self.registry["versions"]:
                if v["version"] == previous_production:
                    v["status"] = "archived"
                    logger.info(
                        f"Previous production version {previous_production} archived"
                    )
                    break

        # Update version status to "production"
        self.registry["versions"][version_index]["status"] = "production"

        # Update production_version in registry
        self.registry["production_version"] = version

        # Save updated registry
        self._save_registry()

        # Create or update "production" symlink
        production_link = self.base_dir / "production"

        # Remove existing symlink or directory
        if production_link.exists() or production_link.is_symlink():
            if production_link.is_symlink():
                production_link.unlink()
                logger.info("Removed existing production symlink")
            else:
                logger.warning(
                    f"Production path exists as directory: {production_link}"
                )

        # Create symlink (Windows requires admin privileges or developer mode)
        try:
            # Use relative path for symlink
            relative_path = os.path.relpath(version_dir, self.base_dir)
            production_link.symlink_to(relative_path, target_is_directory=True)
            logger.info(
                f"Created production symlink: {production_link} -> {version_dir}"
            )
        except OSError as e:
            # If symlink creation fails (Windows permissions), copy directory instead
            logger.warning(f"Failed to create symlink: {e}")
            logger.info("Copying directory instead of creating symlink")
            if production_link.exists():
                shutil.rmtree(production_link)
            shutil.copytree(version_dir, production_link)
            logger.info(f"Copied production version to {production_link}")

        logger.info(f"Version {version} promoted to production successfully")

    def compare_versions(
        self, version1: str, version2: str, test_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare two model versions on test data.

        This method loads both model versions, evaluates them on the provided
        test data, and computes metrics for comparison including accuracy, F1,
        and inference latency.

        Args:
            version1: First version to compare (e.g., "v1.0.0")
            version2: Second version to compare (e.g., "v1.1.0")
            test_data: List of test samples with 'text' and 'label' fields

        Returns:
            Dictionary containing comparison results:
                - version1_metrics: Metrics for version1 (accuracy, f1, latency)
                - version2_metrics: Metrics for version2 (accuracy, f1, latency)
                - improvement: Difference in metrics (version2 - version1)
                - recommendation: Which version is better

        Raises:
            ValueError: If versions don't exist
        """
        import time
        import numpy as np
        from sklearn.metrics import accuracy_score, f1_score

        logger.info(f"Comparing versions: {version1} vs {version2}")
        logger.info(f"Test data size: {len(test_data)} samples")

        # Load both model versions
        logger.info(f"Loading version {version1}...")
        model1_data, metadata1 = self.load_version(version1)

        logger.info(f"Loading version {version2}...")
        model2_data, metadata2 = self.load_version(version2)

        # Extract models and tokenizers
        model1 = model1_data["model"]
        tokenizer1 = model1_data["tokenizer"]
        label_map1 = model1_data["label_map"]

        model2 = model2_data["model"]
        tokenizer2 = model2_data["tokenizer"]
        label_map2 = model2_data["label_map"]

        # Prepare for evaluation
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model1.to(device)
        model2.to(device)
        model1.eval()
        model2.eval()

        logger.info(f"Using device: {device}")

        def evaluate_model(model, tokenizer, label_map):
            """Evaluate a single model on test data."""
            predictions = []
            true_labels = []
            latencies = []

            label_to_id = label_map["label_to_id"] if label_map else {}

            with torch.no_grad():
                for sample in test_data:
                    text = sample["text"]
                    true_label = sample["label"]

                    # Skip if label not in mapping
                    if label_to_id and true_label not in label_to_id:
                        continue

                    # Tokenize input
                    inputs = tokenizer(
                        text,
                        truncation=True,
                        padding="max_length",
                        max_length=512,
                        return_tensors="pt",
                    )
                    inputs = {k: v.to(device) for k, v in inputs.items()}

                    # Measure inference time
                    start_time = time.time()
                    outputs = model(**inputs)
                    latency_ms = (time.time() - start_time) * 1000

                    # Get prediction
                    logits = outputs.logits
                    pred_id = torch.argmax(logits, dim=-1).item()

                    predictions.append(pred_id)
                    true_labels.append(label_to_id.get(true_label, 0))
                    latencies.append(latency_ms)

            # Compute metrics
            accuracy = accuracy_score(true_labels, predictions)
            f1 = f1_score(true_labels, predictions, average="macro")
            latency_p50 = np.percentile(latencies, 50)
            latency_p95 = np.percentile(latencies, 95)

            return {
                "accuracy": accuracy,
                "f1_score": f1,
                "latency_p50_ms": latency_p50,
                "latency_p95_ms": latency_p95,
                "num_samples": len(predictions),
            }

        # Evaluate both models
        logger.info(f"Evaluating {version1}...")
        metrics1 = evaluate_model(model1, tokenizer1, label_map1)

        logger.info(f"Evaluating {version2}...")
        metrics2 = evaluate_model(model2, tokenizer2, label_map2)

        # Calculate improvements
        improvement = {
            "accuracy": metrics2["accuracy"] - metrics1["accuracy"],
            "f1_score": metrics2["f1_score"] - metrics1["f1_score"],
            "latency_p95_ms": metrics2["latency_p95_ms"] - metrics1["latency_p95_ms"],
        }

        # Determine recommendation
        if improvement["accuracy"] > 0.02:  # >2% improvement
            recommendation = f"{version2} is significantly better"
        elif improvement["accuracy"] < -0.02:  # >2% degradation
            recommendation = f"{version1} is significantly better"
        else:
            recommendation = "No significant difference"

        # Prepare comparison results
        comparison = {
            "version1": version1,
            "version2": version2,
            "version1_metrics": metrics1,
            "version2_metrics": metrics2,
            "improvement": improvement,
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat(),
        }

        # Log results
        logger.info("\n" + "=" * 60)
        logger.info("Version Comparison Results")
        logger.info("=" * 60)
        logger.info(f"{version1}:")
        logger.info(f"  Accuracy: {metrics1['accuracy']:.4f}")
        logger.info(f"  F1 Score: {metrics1['f1_score']:.4f}")
        logger.info(f"  Latency (p95): {metrics1['latency_p95_ms']:.2f}ms")
        logger.info(f"\n{version2}:")
        logger.info(f"  Accuracy: {metrics2['accuracy']:.4f}")
        logger.info(f"  F1 Score: {metrics2['f1_score']:.4f}")
        logger.info(f"  Latency (p95): {metrics2['latency_p95_ms']:.2f}ms")
        logger.info("\nImprovement:")
        logger.info(f"  Accuracy: {improvement['accuracy']:+.4f}")
        logger.info(f"  F1 Score: {improvement['f1_score']:+.4f}")
        logger.info(f"  Latency (p95): {improvement['latency_p95_ms']:+.2f}ms")
        logger.info(f"\nRecommendation: {recommendation}")
        logger.info("=" * 60)

        return comparison


def main():
    """
    Main function for command-line usage.

    Example usage:
        # Create a new version
        python model_versioning.py create --model-path models/temp --version v1.0.0

        # List all versions
        python model_versioning.py list

        # Promote to production
        python model_versioning.py promote --version v1.0.0
    """
    import argparse

    parser = argparse.ArgumentParser(description="Model versioning system")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create version command
    create_parser = subparsers.add_parser("create", help="Create a new model version")
    create_parser.add_argument(
        "--model-path", required=True, help="Path to trained model"
    )
    create_parser.add_argument(
        "--version", required=True, help="Version string (e.g., v1.0.0)"
    )
    create_parser.add_argument(
        "--notes", default="", help="Optional notes about this version"
    )

    # List versions command
    subparsers.add_parser("list", help="List all model versions")

    # Promote command
    promote_parser = subparsers.add_parser(
        "promote", help="Promote version to production"
    )
    promote_parser.add_argument("--version", required=True, help="Version to promote")

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare two versions")
    compare_parser.add_argument("--version1", required=True, help="First version")
    compare_parser.add_argument("--version2", required=True, help="Second version")
    compare_parser.add_argument(
        "--test-data", required=True, help="Path to test data JSON"
    )

    args = parser.parse_args()

    # Initialize versioning system
    versioning = ModelVersioning()

    if args.command == "create":
        # Create new version
        metadata = {"model_name": "distilbert-base-uncased", "notes": args.notes}
        version_path = versioning.create_version(
            model_path=args.model_path, version=args.version, metadata=metadata
        )
        print(f"Version created: {version_path}")

    elif args.command == "list":
        # List all versions
        versions = versioning.list_versions()
        print(f"\nFound {len(versions)} versions:")
        print("-" * 80)
        for v in versions:
            print(f"Version: {v['version']}")
            print(f"  Status: {v['status']}")
            print(f"  Created: {v['created_at']}")
            print(f"  Path: {v['path']}")
            print()

    elif args.command == "promote":
        # Promote to production
        versioning.promote_to_production(args.version)
        print(f"Version {args.version} promoted to production")

    elif args.command == "compare":
        # Compare versions
        with open(args.test_data, "r", encoding="utf-8") as f:
            test_data = json.load(f)

        if isinstance(test_data, dict) and "samples" in test_data:
            test_data = test_data["samples"]

        comparison = versioning.compare_versions(
            version1=args.version1,
            version2=args.version2,
            test_data=test_data[:100],  # Use first 100 samples for quick comparison
        )

        print(f"\nComparison complete. Recommendation: {comparison['recommendation']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
