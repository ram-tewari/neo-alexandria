"""
Canary deployment strategy for gradual model rollouts.

This module provides the CanaryDeployment class for gradually rolling out new
model versions with automatic rollback on metric degradation. It implements
a staged rollout approach with monitoring at each stage.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .model_versioning import ModelVersioning


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CanaryDeployment:
    """
    Canary deployment strategy for gradual model rollouts.

    This class implements canary deployment where a new model version is
    gradually rolled out to increasing percentages of traffic:
    - Stage 1: 5% canary traffic
    - Stage 2: 10% canary traffic
    - Stage 3: 25% canary traffic
    - Stage 4: 50% canary traffic
    - Stage 5: 100% canary traffic (full rollout)

    At each stage, metrics are monitored for a specified duration (default 1 hour).
    If metrics degrade beyond acceptable thresholds, the deployment is rolled back.

    Attributes:
        versioning (ModelVersioning): Model versioning system
        production_version (str): Current production version
        canary_version (str): New version being deployed
        canary_percentage (int): Current canary traffic percentage
        production_model (Any): Loaded production model
        canary_model (Any): Loaded canary model
        deployment_log (List): Log of deployment events
        rollout_stages (List[int]): Traffic percentage stages
        stage_duration_seconds (int): Duration to monitor each stage
    """

    def __init__(
        self,
        production_version: Optional[str] = None,
        canary_version: Optional[str] = None,
        base_dir: str = "models/classification",
        stage_duration_seconds: int = 3600,  # 1 hour default
    ):
        """
        Initialize Canary deployment.

        Args:
            production_version: Current production version (if None, loads from registry)
            canary_version: New version to deploy (required for deployment)
            base_dir: Base directory for model versions
            stage_duration_seconds: Duration to monitor each stage (default: 3600 = 1 hour)
        """
        self.versioning = ModelVersioning(base_dir=base_dir)

        # Load production version
        if production_version is None:
            production_version = self.versioning.registry.get("production_version")
            if production_version is None:
                logger.warning("No production version found in registry")

        self.production_version = production_version
        self.canary_version = canary_version
        self.canary_percentage = 0

        self.production_model = None
        self.canary_model = None

        # Deployment configuration
        self.rollout_stages = [5, 10, 25, 50, 100]
        self.stage_duration_seconds = stage_duration_seconds

        # Deployment log for tracking events
        self.deployment_log = []

        logger.info("Canary deployment initialized")
        logger.info(f"  Production: {self.production_version}")
        logger.info(f"  Canary: {self.canary_version}")
        logger.info(f"  Rollout stages: {self.rollout_stages}")
        logger.info(f"  Stage duration: {self.stage_duration_seconds}s")

        self._log_event(
            "initialized",
            {
                "production_version": self.production_version,
                "canary_version": self.canary_version,
                "rollout_stages": self.rollout_stages,
            },
        )

    def _log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log a deployment event.

        Args:
            event_type: Type of event (e.g., "stage_started", "rolled_back")
            details: Event details dictionary
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
        }
        self.deployment_log.append(event)
        logger.debug(f"Event logged: {event_type}")

    def gradual_rollout(self) -> bool:
        """
        Gradually increase canary traffic through stages.

        This method implements the staged rollout:
        1. Load production and canary models
        2. For each stage (5%, 10%, 25%, 50%, 100%):
            a. Update traffic split
            b. Monitor metrics for stage duration
            c. Check if metrics are acceptable
            d. Rollback if metrics degrade
        3. Complete rollout if all stages pass

        Returns:
            True if rollout completed successfully, False if rolled back

        Raises:
            ValueError: If canary_version is not set
        """
        if self.canary_version is None:
            raise ValueError("canary_version must be set before rollout")

        logger.info(f"Starting gradual rollout of {self.canary_version}")
        self._log_event("rollout_started", {"version": self.canary_version})

        try:
            # Load production model
            if self.production_version:
                logger.info(f"Loading production model {self.production_version}...")
                self.production_model, _ = self.versioning.load_version(
                    self.production_version
                )
                logger.info("Production model loaded")
            else:
                logger.warning("No production version to load")

            # Load canary model
            logger.info(f"Loading canary model {self.canary_version}...")
            self.canary_model, canary_metadata = self.versioning.load_version(
                self.canary_version
            )
            logger.info("Canary model loaded")
            logger.info(f"  Model: {canary_metadata.get('model_name', 'unknown')}")
            logger.info(f"  Size: {canary_metadata.get('model_size_mb', 0):.2f} MB")

            # Iterate through rollout stages
            for stage_percentage in self.rollout_stages:
                logger.info(f"\n{'=' * 60}")
                logger.info(f"Stage: {stage_percentage}% canary traffic")
                logger.info(f"{'=' * 60}")

                # Update traffic split
                self.canary_percentage = stage_percentage
                self._update_traffic_split(stage_percentage)

                self._log_event(
                    "stage_started",
                    {
                        "percentage": stage_percentage,
                        "duration_seconds": self.stage_duration_seconds,
                    },
                )

                # Monitor for stage duration
                logger.info(f"Monitoring for {self.stage_duration_seconds}s...")

                # For testing, we can use a shorter duration
                # In production, this would be the full stage_duration_seconds
                monitor_interval = min(
                    60, self.stage_duration_seconds
                )  # Check every minute
                elapsed = 0

                while elapsed < self.stage_duration_seconds:
                    time.sleep(monitor_interval)
                    elapsed += monitor_interval

                    # Check metrics periodically
                    if not self.metrics_acceptable():
                        logger.error(f"Metrics degraded at {stage_percentage}% stage")
                        logger.error("Rolling back deployment...")

                        self._log_event(
                            "metrics_degraded",
                            {
                                "percentage": stage_percentage,
                                "elapsed_seconds": elapsed,
                            },
                        )

                        self.rollback()
                        return False

                    logger.info(
                        f"  Elapsed: {elapsed}s / {self.stage_duration_seconds}s - Metrics OK"
                    )

                logger.info(f"Stage {stage_percentage}% completed successfully")

                self._log_event("stage_completed", {"percentage": stage_percentage})

            # All stages completed successfully
            logger.info(f"\n{'=' * 60}")
            logger.info("Canary rollout complete!")
            logger.info(f"{'=' * 60}")
            logger.info(f"Version {self.canary_version} is now serving 100% of traffic")

            # Promote canary to production
            try:
                self.versioning.promote_to_production(self.canary_version)
                logger.info(
                    f"Version {self.canary_version} promoted to production in registry"
                )
            except Exception as e:
                logger.warning(f"Failed to update production registry: {e}")

            self._log_event("rollout_completed", {"version": self.canary_version})

            return True

        except Exception as e:
            logger.error(f"Rollout failed with exception: {e}")
            self._log_event(
                "rollout_failed", {"version": self.canary_version, "error": str(e)}
            )
            self.rollback()
            return False

    def _update_traffic_split(self, canary_percentage: int) -> None:
        """
        Update traffic split between production and canary.

        In a real deployment, this would update a load balancer or routing
        configuration. For this implementation, we just log the change.

        Args:
            canary_percentage: Percentage of traffic to route to canary (0-100)
        """
        production_percentage = 100 - canary_percentage

        logger.info("Traffic split updated:")
        logger.info(
            f"  Production ({self.production_version}): {production_percentage}%"
        )
        logger.info(f"  Canary ({self.canary_version}): {canary_percentage}%")

        # In production, this would call:
        # - Load balancer API to update routing rules
        # - Service mesh configuration
        # - Feature flag system
        # - etc.

    def metrics_acceptable(self) -> bool:
        """
        Check if canary metrics are acceptable compared to production.

        This method compares key metrics between canary and production:
        - Error rate: canary < production * 1.5 (50% tolerance)
        - Latency (p95): canary < production * 1.2 (20% tolerance)

        Returns:
            True if metrics are acceptable, False if degraded
        """
        logger.debug("Checking if canary metrics are acceptable...")

        try:
            # Get metrics for both versions
            canary_metrics = self._get_metrics("canary")
            production_metrics = self._get_metrics("production")

            # Compare error rates
            canary_error_rate = canary_metrics.get("error_rate", 0.0)
            production_error_rate = production_metrics.get("error_rate", 0.0)

            error_rate_threshold = production_error_rate * 1.5

            if canary_error_rate > error_rate_threshold:
                logger.warning("Canary error rate too high:")
                logger.warning(f"  Canary: {canary_error_rate:.4f}")
                logger.warning(f"  Production: {production_error_rate:.4f}")
                logger.warning(f"  Threshold: {error_rate_threshold:.4f}")
                return False

            # Compare latencies
            canary_latency = canary_metrics.get("latency_p95", 0.0)
            production_latency = production_metrics.get("latency_p95", 0.0)

            latency_threshold = production_latency * 1.2

            if canary_latency > latency_threshold:
                logger.warning("Canary latency too high:")
                logger.warning(f"  Canary: {canary_latency:.2f}ms")
                logger.warning(f"  Production: {production_latency:.2f}ms")
                logger.warning(f"  Threshold: {latency_threshold:.2f}ms")
                return False

            # Metrics are acceptable
            logger.debug("Canary metrics are acceptable")
            logger.debug(
                f"  Error rate: {canary_error_rate:.4f} vs {production_error_rate:.4f}"
            )
            logger.debug(
                f"  Latency p95: {canary_latency:.2f}ms vs {production_latency:.2f}ms"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to check metrics: {e}")
            # On error, assume metrics are not acceptable (fail-safe)
            return False

    def _get_metrics(self, version_type: str) -> Dict[str, float]:
        """
        Get metrics for a version (production or canary).

        In a real deployment, this would query a monitoring system like:
        - Prometheus
        - CloudWatch
        - Datadog
        - Custom metrics API

        For this implementation, we simulate metrics by running test predictions.

        Args:
            version_type: "production" or "canary"

        Returns:
            Dictionary with metrics:
                - error_rate: Fraction of failed predictions (0.0-1.0)
                - latency_p95: 95th percentile latency in milliseconds
                - accuracy: Prediction accuracy (if ground truth available)
        """
        logger.debug(f"Getting metrics for {version_type}...")

        # Get model for version type
        if version_type == "production":
            model_data = self.production_model
        elif version_type == "canary":
            model_data = self.canary_model
        else:
            logger.error(f"Invalid version type: {version_type}")
            return {}

        if model_data is None:
            logger.warning(f"{version_type.capitalize()} model not loaded")
            # Return safe default metrics
            return {"error_rate": 0.0, "latency_p95": 100.0, "accuracy": 0.9}

        try:
            import torch
            import numpy as np

            model = model_data["model"]
            tokenizer = model_data["tokenizer"]

            device = "cuda" if torch.cuda.is_available() else "cpu"
            model.to(device)
            model.eval()

            # Test samples for metrics
            test_samples = [
                "Machine learning enables computers to learn from data.",
                "Deep learning uses neural networks with multiple layers.",
                "Natural language processing analyzes and understands text.",
                "Computer vision allows machines to interpret visual information.",
                "Reinforcement learning trains agents through rewards.",
                "Transfer learning leverages pre-trained model knowledge.",
                "Supervised learning uses labeled training data.",
                "Unsupervised learning finds patterns in unlabeled data.",
                "Neural networks are inspired by biological neurons.",
                "Gradient descent optimizes model parameters.",
            ]

            latencies = []
            errors = 0

            with torch.no_grad():
                for text in test_samples:
                    try:
                        # Tokenize
                        inputs = tokenizer(
                            text,
                            truncation=True,
                            padding="max_length",
                            max_length=512,
                            return_tensors="pt",
                        )
                        inputs = {k: v.to(device) for k, v in inputs.items()}

                        # Measure latency
                        start_time = time.time()
                        model(**inputs)
                        latency_ms = (time.time() - start_time) * 1000

                        latencies.append(latency_ms)

                    except Exception as e:
                        logger.debug(f"Prediction error: {e}")
                        errors += 1

            # Calculate metrics
            error_rate = errors / len(test_samples) if test_samples else 0.0
            latency_p95 = np.percentile(latencies, 95) if latencies else 0.0

            metrics = {
                "error_rate": error_rate,
                "latency_p95": latency_p95,
                "num_samples": len(test_samples),
                "num_errors": errors,
            }

            logger.debug(f"{version_type.capitalize()} metrics: {metrics}")

            return metrics

        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            # Return safe default metrics
            return {"error_rate": 0.0, "latency_p95": 100.0}

    def rollback(self) -> bool:
        """
        Rollback canary deployment to production.

        This method:
        1. Sets canary percentage to 0%
        2. Routes all traffic back to production
        3. Logs rollback event

        Returns:
            True if rollback successful, False otherwise
        """
        logger.warning("Rolling back canary deployment...")

        # Set canary percentage to 0
        self.canary_percentage = 0
        self._update_traffic_split(0)

        logger.warning(
            f"All traffic routed back to production: {self.production_version}"
        )

        self._log_event(
            "rolled_back",
            {
                "from_version": self.canary_version,
                "to_version": self.production_version,
            },
        )

        logger.info("Rollback successful")
        return True

    def get_deployment_log(self) -> List[Dict[str, Any]]:
        """
        Get deployment event log.

        Returns:
            List of deployment events with timestamps and details
        """
        return self.deployment_log

    def save_deployment_log(self, output_file: str) -> None:
        """
        Save deployment log to file.

        Args:
            output_file: Path to output JSON file
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.deployment_log, f, indent=2)

        logger.info(f"Deployment log saved to {output_file}")


def main():
    """
    Main function for command-line usage.

    Example usage:
        # Start canary rollout
        python canary.py rollout --canary-version v1.2.0

        # Start canary rollout with custom stage duration (5 minutes for testing)
        python canary.py rollout --canary-version v1.2.0 --stage-duration 300

        # Rollback canary deployment
        python canary.py rollback
    """
    import argparse

    parser = argparse.ArgumentParser(description="Canary deployment")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Rollout command
    rollout_parser = subparsers.add_parser("rollout", help="Start canary rollout")
    rollout_parser.add_argument(
        "--canary-version", required=True, help="Version to deploy"
    )
    rollout_parser.add_argument(
        "--production-version", help="Current production version (optional)"
    )
    rollout_parser.add_argument(
        "--stage-duration",
        type=int,
        default=3600,
        help="Stage duration in seconds (default: 3600 = 1 hour)",
    )

    # Rollback command
    rollback_parser = subparsers.add_parser(
        "rollback", help="Rollback canary deployment"
    )
    rollback_parser.add_argument(
        "--production-version", help="Version to rollback to (optional)"
    )

    # Check metrics command
    metrics_parser = subparsers.add_parser("metrics", help="Check current metrics")
    metrics_parser.add_argument(
        "--canary-version", required=True, help="Canary version"
    )
    metrics_parser.add_argument(
        "--production-version", help="Production version (optional)"
    )

    args = parser.parse_args()

    if args.command == "rollout":
        # Start canary rollout
        deployment = CanaryDeployment(
            production_version=args.production_version,
            canary_version=args.canary_version,
            stage_duration_seconds=args.stage_duration,
        )

        print(f"Starting canary rollout: {args.canary_version}")
        print(f"Stages: {deployment.rollout_stages}")
        print(f"Stage duration: {args.stage_duration}s")
        print()

        success = deployment.gradual_rollout()

        if success:
            print("\n✓ Canary rollout completed successfully")
            print(f"  Version {args.canary_version} is now in production")
        else:
            print("\n✗ Canary rollout failed and was rolled back")

        # Save deployment log
        deployment.save_deployment_log("canary_deployment_log.json")

    elif args.command == "rollback":
        # Rollback canary
        deployment = CanaryDeployment(production_version=args.production_version)

        success = deployment.rollback()

        if success:
            print(f"✓ Rolled back to production: {deployment.production_version}")
        else:
            print("✗ Rollback failed")

    elif args.command == "metrics":
        # Check metrics
        deployment = CanaryDeployment(
            production_version=args.production_version,
            canary_version=args.canary_version,
        )

        # Load models
        if deployment.production_version:
            deployment.production_model, _ = deployment.versioning.load_version(
                deployment.production_version
            )
        deployment.canary_model, _ = deployment.versioning.load_version(
            deployment.canary_version
        )

        # Check if metrics are acceptable
        acceptable = deployment.metrics_acceptable()

        # Get detailed metrics
        canary_metrics = deployment._get_metrics("canary")
        production_metrics = deployment._get_metrics("production")

        print("\nProduction Metrics:")
        print(f"  Error rate: {production_metrics.get('error_rate', 0):.4f}")
        print(f"  Latency p95: {production_metrics.get('latency_p95', 0):.2f}ms")

        print("\nCanary Metrics:")
        print(f"  Error rate: {canary_metrics.get('error_rate', 0):.4f}")
        print(f"  Latency p95: {canary_metrics.get('latency_p95', 0):.2f}ms")

        print(f"\nMetrics acceptable: {'✓ Yes' if acceptable else '✗ No'}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
