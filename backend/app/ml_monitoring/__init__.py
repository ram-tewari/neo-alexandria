"""
Monitoring package for ML model health checks and observability.

This package provides:
- PredictionMonitor: Track predictions and calculate metrics
- AlertManager: Check metrics and send alerts
- Health checks: Verify model health and readiness
- JSON logging: Structured logging for better observability
"""

from .prediction_monitor import PredictionMonitor
from .alert_manager import AlertManager
from .health_check import check_model_health, check_classification_model_health
from .json_logging import JSONFormatter, configure_json_logging, log_with_context

__all__ = [
    "PredictionMonitor",
    "AlertManager",
    "check_model_health",
    "check_classification_model_health",
    "JSONFormatter",
    "configure_json_logging",
    "log_with_context",
]
