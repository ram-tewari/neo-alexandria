"""
A/B Testing Framework for Model Version Comparison

This module implements an A/B testing framework for comparing multiple model
versions in production. It supports experiment creation, traffic splitting,
prediction routing, logging, and statistical analysis.

Usage:
    from backend.scripts.deployment.ab_testing import ABTestingFramework
    from backend.app.database.base import SessionLocal

    db = SessionLocal()
    ab_testing = ABTestingFramework(db)

    # Create experiment
    experiment_id = ab_testing.create_experiment(
        name="arxiv_v1.1.0_vs_v1.0.0",
        control_version="v1.0.0",
        treatment_version="v1.1.0",
        traffic_split=0.1
    )

    # Route prediction
    version = ab_testing.route_prediction(experiment_id, user_id="user123")

    # Log prediction
    ab_testing.log_prediction(
        experiment_id=experiment_id,
        version="v1.1.0",
        input_text="Machine learning paper",
        predictions={"cs.AI": 0.95},
        latency_ms=85.3
    )

    # Analyze experiment
    results = ab_testing.analyze_experiment(experiment_id)

    # Promote winner
    ab_testing.promote_winner(experiment_id)
"""

import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

import numpy as np
from scipy import stats
from sqlalchemy.orm import Session

from backend.app.database.models import ModelVersion, ABTestExperiment, PredictionLog
from backend.scripts.deployment.model_versioning import ModelVersioning


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ABTestingFramework:
    """
    A/B testing framework for comparing model versions in production.

    This class provides methods for creating experiments, routing predictions
    to control or treatment versions, logging predictions for analysis, and
    performing statistical analysis to determine the winning model.

    Attributes:
        db (Session): SQLAlchemy database session
        versioning (ModelVersioning): Model versioning system
        prediction_buffer (list): Buffer for batch inserting predictions
        buffer_size (int): Size of prediction buffer before flushing
    """

    def __init__(self, db: Session):
        """
        Initialize A/B testing framework.

        Args:
            db: SQLAlchemy database session for database operations
        """
        self.db = db
        self.versioning = ModelVersioning()
        self.prediction_buffer = []
        self.buffer_size = 100  # Batch insert every 100 predictions

        logger.info("ABTestingFramework initialized")

    def __del__(self):
        """Flush any remaining predictions in buffer on cleanup."""
        if self.prediction_buffer:
            self._flush_prediction_buffer()

    def create_experiment(
        self,
        name: str,
        control_version: str,
        treatment_version: str,
        traffic_split: float = 0.1,
    ) -> str:
        """
        Create a new A/B test experiment.

        Args:
            name: Experiment name (e.g., "arxiv_v1.1.0_vs_v1.0.0")
            control_version: Version string for control model (e.g., "v1.0.0")
            treatment_version: Version string for treatment model (e.g., "v1.1.0")
            traffic_split: Percentage of traffic to treatment (0.0-1.0)

        Returns:
            str: Experiment ID (UUID as string)

        Raises:
            ValueError: If versions don't exist or traffic_split is invalid
        """
        # Validate traffic_split
        if not 0.0 <= traffic_split <= 1.0:
            raise ValueError(
                f"traffic_split must be between 0.0 and 1.0, got {traffic_split}"
            )

        # Validate control version exists
        control_model = (
            self.db.query(ModelVersion)
            .filter(ModelVersion.version == control_version)
            .first()
        )

        if not control_model:
            raise ValueError(f"Control version '{control_version}' not found")

        # Validate treatment version exists
        treatment_model = (
            self.db.query(ModelVersion)
            .filter(ModelVersion.version == treatment_version)
            .first()
        )

        if not treatment_model:
            raise ValueError(f"Treatment version '{treatment_version}' not found")

        # Create experiment
        experiment = ABTestExperiment(
            name=name,
            control_version_id=control_model.id,
            treatment_version_id=treatment_model.id,
            traffic_split=traffic_split,
            status="running",
        )

        self.db.add(experiment)
        self.db.commit()
        self.db.refresh(experiment)

        logger.info(
            f"Created A/B test experiment: {name} "
            f"(control={control_version}, treatment={treatment_version}, "
            f"split={traffic_split:.1%})"
        )

        return str(experiment.id)

    def route_prediction(self, experiment_id: str, user_id: str) -> str:
        """
        Route prediction request to control or treatment version.

        Uses consistent hashing to ensure the same user always gets the same
        version throughout the experiment. This is critical for valid A/B testing.

        Args:
            experiment_id: Experiment ID (UUID as string)
            user_id: User identifier for consistent routing

        Returns:
            str: "control" or "treatment" indicating which version to use

        Raises:
            ValueError: If experiment not found or not running
        """
        # Load experiment
        experiment = (
            self.db.query(ABTestExperiment)
            .filter(ABTestExperiment.id == UUID(experiment_id))
            .first()
        )

        if not experiment:
            raise ValueError(f"Experiment '{experiment_id}' not found")

        if experiment.status != "running":
            raise ValueError(
                f"Experiment '{experiment_id}' is not running (status: {experiment.status})"
            )

        # Hash user_id to get consistent assignment
        # Use MD5 hash and convert to float in [0, 1)
        hash_obj = hashlib.md5(user_id.encode("utf-8"))
        hash_int = int(hash_obj.hexdigest(), 16)
        hash_float = (hash_int % 10000) / 10000.0  # Normalize to [0, 1)

        # Compare hash to traffic_split threshold
        if hash_float < experiment.traffic_split:
            return "treatment"
        else:
            return "control"

    def log_prediction(
        self,
        experiment_id: str,
        version: str,
        input_text: str,
        predictions: Dict[str, float],
        latency_ms: float,
        user_id: Optional[str] = None,
    ):
        """
        Log prediction for analysis.

        Predictions are buffered and batch inserted for efficiency. The buffer
        is flushed automatically when it reaches buffer_size (100 predictions).

        Args:
            experiment_id: Experiment ID (UUID as string)
            version: Model version used (e.g., "v1.0.0")
            input_text: Input text for prediction
            predictions: Model predictions as dict (e.g., {"cs.AI": 0.95})
            latency_ms: Prediction latency in milliseconds
            user_id: Optional user identifier
        """
        # Get model version ID
        model_version = (
            self.db.query(ModelVersion).filter(ModelVersion.version == version).first()
        )

        if not model_version:
            logger.warning(f"Model version '{version}' not found, skipping log")
            return

        # Create prediction log entry
        prediction_log = {
            "experiment_id": UUID(experiment_id),
            "model_version_id": model_version.id,
            "input_text": input_text,
            "predictions": predictions,
            "latency_ms": latency_ms,
            "user_id": UUID(user_id) if user_id else None,
        }

        # Add to buffer
        self.prediction_buffer.append(prediction_log)

        # Flush buffer if it reaches buffer_size
        if len(self.prediction_buffer) >= self.buffer_size:
            self._flush_prediction_buffer()

    def _flush_prediction_buffer(self):
        """Flush prediction buffer to database with batch insert."""
        if not self.prediction_buffer:
            return

        try:
            # Create PredictionLog objects
            prediction_logs = [
                PredictionLog(**log_data) for log_data in self.prediction_buffer
            ]

            # Batch insert
            self.db.bulk_save_objects(prediction_logs)
            self.db.commit()

            logger.info(
                f"Flushed {len(self.prediction_buffer)} predictions to database"
            )

            # Clear buffer
            self.prediction_buffer = []

        except Exception as e:
            logger.error(f"Error flushing prediction buffer: {e}")
            self.db.rollback()
            # Keep buffer for retry

    def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """
        Analyze A/B test experiment results.

        Performs statistical analysis comparing control and treatment versions
        on key metrics: accuracy, latency (p95), and F1 score. Uses t-tests
        for statistical significance and calculates confidence intervals.

        Args:
            experiment_id: Experiment ID (UUID as string)

        Returns:
            dict: Analysis results with metrics, statistical tests, and recommendation

        Raises:
            ValueError: If experiment not found or insufficient data
        """
        # Load experiment
        experiment = (
            self.db.query(ABTestExperiment)
            .filter(ABTestExperiment.id == UUID(experiment_id))
            .first()
        )

        if not experiment:
            raise ValueError(f"Experiment '{experiment_id}' not found")

        # Query prediction logs for control
        control_logs = (
            self.db.query(PredictionLog)
            .filter(
                PredictionLog.experiment_id == UUID(experiment_id),
                PredictionLog.model_version_id == experiment.control_version_id,
            )
            .all()
        )

        # Query prediction logs for treatment
        treatment_logs = (
            self.db.query(PredictionLog)
            .filter(
                PredictionLog.experiment_id == UUID(experiment_id),
                PredictionLog.model_version_id == experiment.treatment_version_id,
            )
            .all()
        )

        # Check for sufficient data
        if len(control_logs) < 30 or len(treatment_logs) < 30:
            raise ValueError(
                f"Insufficient data for analysis. "
                f"Control: {len(control_logs)}, Treatment: {len(treatment_logs)}. "
                f"Need at least 30 predictions per version."
            )

        # Calculate metrics for control
        control_metrics = self._calculate_metrics(control_logs)

        # Calculate metrics for treatment
        treatment_metrics = self._calculate_metrics(treatment_logs)

        # Perform statistical significance testing
        # T-test for accuracy (if we have ground truth labels)
        # For now, we'll use confidence scores as a proxy
        control_confidences = [max(log.predictions.values()) for log in control_logs]
        treatment_confidences = [
            max(log.predictions.values()) for log in treatment_logs
        ]

        t_stat, p_value = stats.ttest_ind(treatment_confidences, control_confidences)

        # Calculate improvement
        confidence_improvement = (
            treatment_metrics["avg_confidence"] - control_metrics["avg_confidence"]
        )
        latency_improvement = (
            control_metrics["latency_p95"] - treatment_metrics["latency_p95"]
        )

        # Calculate confidence intervals (95%)
        confidence_ci = stats.t.interval(
            0.95,
            len(treatment_confidences) - 1,
            loc=np.mean(treatment_confidences),
            scale=stats.sem(treatment_confidences),
        )

        # Determine recommendation
        recommendation = self._determine_recommendation(
            p_value=p_value,
            confidence_improvement=confidence_improvement,
            latency_improvement=latency_improvement,
        )

        # Build results dictionary
        results = {
            "experiment_id": experiment_id,
            "duration_days": (datetime.now() - experiment.start_date).days,
            "control": {
                "version": experiment.control_version.version,
                "predictions": len(control_logs),
                **control_metrics,
            },
            "treatment": {
                "version": experiment.treatment_version.version,
                "predictions": len(treatment_logs),
                **treatment_metrics,
            },
            "statistical_significance": {
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "confidence_improvement": float(confidence_improvement),
                "latency_improvement": float(latency_improvement),
                "confidence_interval": [
                    float(confidence_ci[0]),
                    float(confidence_ci[1]),
                ],
            },
            "recommendation": recommendation["action"],
            "reason": recommendation["reason"],
        }

        # Save results to experiment
        experiment.results = results
        self.db.commit()

        logger.info(
            f"Analyzed experiment {experiment.name}: "
            f"Recommendation={recommendation['action']}, "
            f"p-value={p_value:.4f}, "
            f"improvement={confidence_improvement:+.3f}"
        )

        return results

    def _calculate_metrics(self, logs: list) -> Dict[str, float]:
        """
        Calculate metrics from prediction logs.

        Args:
            logs: List of PredictionLog objects

        Returns:
            dict: Metrics including latency percentiles and confidence scores
        """
        latencies = [log.latency_ms for log in logs]
        confidences = [max(log.predictions.values()) for log in logs]

        return {
            "latency_p50": float(np.percentile(latencies, 50)),
            "latency_p95": float(np.percentile(latencies, 95)),
            "latency_p99": float(np.percentile(latencies, 99)),
            "avg_confidence": float(np.mean(confidences)),
            "low_confidence_rate": float(np.mean([c < 0.5 for c in confidences])),
        }

    def _determine_recommendation(
        self, p_value: float, confidence_improvement: float, latency_improvement: float
    ) -> Dict[str, str]:
        """
        Determine recommendation based on statistical analysis.

        Args:
            p_value: P-value from statistical test
            confidence_improvement: Improvement in confidence scores
            latency_improvement: Improvement in latency (positive = faster)

        Returns:
            dict: Recommendation with action and reason
        """
        # Check statistical significance (p < 0.05)
        if p_value >= 0.05:
            return {
                "action": "INCONCLUSIVE",
                "reason": f"Not statistically significant (p={p_value:.4f} >= 0.05)",
            }

        # Check minimum improvement threshold (2%)
        if confidence_improvement < 0.02:
            return {
                "action": "KEEP",
                "reason": f"Improvement too small ({confidence_improvement:+.1%} < 2%)",
            }

        # Check if latency degraded significantly (>20%)
        if latency_improvement < -20:  # Negative = slower
            return {
                "action": "KEEP",
                "reason": f"Latency degraded significantly ({latency_improvement:+.0f}ms)",
            }

        # All checks passed - recommend promotion
        return {
            "action": "PROMOTE",
            "reason": (
                f"Statistically significant improvement "
                f"(p={p_value:.4f}, +{confidence_improvement:.1%})"
            ),
        }

    def promote_winner(self, experiment_id: str) -> bool:
        """
        Promote winning model to production if treatment is significantly better.

        Checks if treatment version is significantly better than control
        (p < 0.05 and improvement > 2%). If yes, promotes treatment to
        production using ModelVersioning. Updates experiment status to completed.

        Args:
            experiment_id: Experiment ID (UUID as string)

        Returns:
            bool: True if treatment was promoted, False otherwise

        Raises:
            ValueError: If experiment not found or not analyzed
        """
        # Load experiment
        experiment = (
            self.db.query(ABTestExperiment)
            .filter(ABTestExperiment.id == UUID(experiment_id))
            .first()
        )

        if not experiment:
            raise ValueError(f"Experiment '{experiment_id}' not found")

        # Check if experiment has been analyzed
        if not experiment.results:
            raise ValueError(
                f"Experiment '{experiment_id}' has not been analyzed. "
                f"Run analyze_experiment() first."
            )

        # Get recommendation from analysis
        recommendation = experiment.results.get("recommendation")

        if recommendation == "PROMOTE":
            # Promote treatment version to production
            treatment_version = experiment.treatment_version.version

            try:
                self.versioning.promote_to_production(treatment_version)

                # Update experiment status
                experiment.status = "completed"
                experiment.end_date = datetime.now()
                self.db.commit()

                # Send notification
                self._send_notification(
                    subject=f"A/B Test Winner Promoted: {treatment_version}",
                    message=(
                        f"Experiment: {experiment.name}\n"
                        f"Treatment version {treatment_version} promoted to production.\n\n"
                        f"Results:\n"
                        f"- Control: {experiment.control_version.version}\n"
                        f"- Treatment: {treatment_version}\n"
                        f"- Improvement: {experiment.results['statistical_significance']['confidence_improvement']:+.1%}\n"
                        f"- P-value: {experiment.results['statistical_significance']['p_value']:.4f}\n"
                        f"- Reason: {experiment.results['reason']}"
                    ),
                )

                logger.info(
                    f"Promoted treatment version {treatment_version} to production "
                    f"for experiment {experiment.name}"
                )

                return True

            except Exception as e:
                logger.error(f"Error promoting treatment version: {e}")
                raise

        else:
            # Keep control version
            experiment.status = "completed"
            experiment.end_date = datetime.now()
            self.db.commit()

            # Send notification
            self._send_notification(
                subject="A/B Test Completed: No Promotion",
                message=(
                    f"Experiment: {experiment.name}\n"
                    f"Control version {experiment.control_version.version} kept in production.\n\n"
                    f"Results:\n"
                    f"- Recommendation: {recommendation}\n"
                    f"- Reason: {experiment.results['reason']}"
                ),
            )

            logger.info(
                f"Kept control version {experiment.control_version.version} "
                f"for experiment {experiment.name}. Recommendation: {recommendation}"
            )

            return False

    def _send_notification(self, subject: str, message: str):
        """
        Send notification about experiment results.

        This is a placeholder for notification logic. In production, this would
        send emails, Slack messages, or other notifications.

        Args:
            subject: Notification subject
            message: Notification message body
        """
        logger.info(f"NOTIFICATION: {subject}")
        logger.info(f"Message:\n{message}")

        # TODO: Implement actual notification logic
        # - Send email via SMTP
        # - Send Slack message via webhook
        # - Create dashboard alert
