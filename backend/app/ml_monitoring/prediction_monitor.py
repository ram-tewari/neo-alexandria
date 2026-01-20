"""
Prediction monitoring module for tracking ML model predictions and performance.

This module provides the PredictionMonitor class for logging predictions and
calculating performance metrics over time windows.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PredictionMonitor:
    """
    Monitor for tracking ML model predictions and calculating metrics.

    This class logs predictions with timestamps and provides methods to
    calculate performance metrics over time windows.

    Attributes:
        predictions (List[Dict]): List of logged predictions with metadata
    """

    def __init__(self):
        """Initialize the PredictionMonitor with empty prediction list."""
        self.predictions: List[Dict[str, Any]] = []
        logger.info("PredictionMonitor initialized")

    def log_prediction(
        self,
        input_text: str,
        predictions: Dict[str, Any],
        latency_ms: float,
        error: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Log a prediction with metadata.

        Args:
            input_text: Input text that was classified
            predictions: Dictionary containing prediction results (e.g., label, confidence)
            latency_ms: Prediction latency in milliseconds
            error: Optional error message if prediction failed
            user_id: Optional user ID for tracking
        """
        prediction_log = {
            "timestamp": datetime.now(),
            "input_length": len(input_text),
            "predictions": predictions,
            "latency_ms": latency_ms,
            "error": error,
            "user_id": user_id,
        }

        self.predictions.append(prediction_log)

        # Log every 100 predictions
        if len(self.predictions) % 100 == 0:
            logger.info(f"Logged {len(self.predictions)} predictions")

    def get_metrics(self, window_minutes: int = 60) -> Dict[str, Any]:
        """
        Calculate metrics for recent predictions within a time window.

        Args:
            window_minutes: Time window in minutes for calculating metrics (default: 60)

        Returns:
            Dictionary containing:
                - total_predictions: Total number of predictions in window
                - error_rate: Percentage of predictions with errors
                - latency_p50: 50th percentile latency in ms
                - latency_p95: 95th percentile latency in ms
                - latency_p99: 99th percentile latency in ms
                - avg_confidence: Average prediction confidence
                - low_confidence_rate: Percentage of predictions with confidence < 0.5
        """
        # Calculate cutoff time
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)

        # Filter predictions within time window
        recent_predictions = [
            p for p in self.predictions if p["timestamp"] >= cutoff_time
        ]

        if not recent_predictions:
            return {
                "total_predictions": 0,
                "error_rate": 0.0,
                "latency_p50": 0.0,
                "latency_p95": 0.0,
                "latency_p99": 0.0,
                "avg_confidence": 0.0,
                "low_confidence_rate": 0.0,
                "window_minutes": window_minutes,
            }

        # Calculate total predictions
        total_predictions = len(recent_predictions)

        # Calculate error rate
        error_count = sum(1 for p in recent_predictions if p["error"] is not None)
        error_rate = error_count / total_predictions if total_predictions > 0 else 0.0

        # Calculate latency percentiles
        latencies = [p["latency_ms"] for p in recent_predictions]
        latency_p50 = float(np.percentile(latencies, 50))
        latency_p95 = float(np.percentile(latencies, 95))
        latency_p99 = float(np.percentile(latencies, 99))

        # Calculate confidence metrics
        confidences = []
        low_confidence_count = 0

        for p in recent_predictions:
            if p["error"] is None and "confidence" in p["predictions"]:
                confidence = p["predictions"]["confidence"]
                confidences.append(confidence)
                if confidence < 0.5:
                    low_confidence_count += 1

        avg_confidence = float(np.mean(confidences)) if confidences else 0.0
        low_confidence_rate = (
            low_confidence_count / total_predictions if total_predictions > 0 else 0.0
        )

        metrics = {
            "total_predictions": total_predictions,
            "error_rate": error_rate,
            "latency_p50": latency_p50,
            "latency_p95": latency_p95,
            "latency_p99": latency_p99,
            "avg_confidence": avg_confidence,
            "low_confidence_rate": low_confidence_rate,
            "window_minutes": window_minutes,
        }

        logger.debug(
            f"Calculated metrics for {total_predictions} predictions in {window_minutes}min window"
        )

        return metrics

    def clear_old_predictions(self, retention_hours: int = 24) -> int:
        """
        Clear predictions older than retention period to prevent memory growth.

        Args:
            retention_hours: Number of hours to retain predictions (default: 24)

        Returns:
            Number of predictions removed
        """
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)

        initial_count = len(self.predictions)
        self.predictions = [
            p for p in self.predictions if p["timestamp"] >= cutoff_time
        ]
        removed_count = initial_count - len(self.predictions)

        if removed_count > 0:
            logger.info(
                f"Cleared {removed_count} old predictions (retention: {retention_hours}h)"
            )

        return removed_count
