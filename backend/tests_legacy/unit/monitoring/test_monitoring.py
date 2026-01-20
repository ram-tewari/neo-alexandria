"""
Unit tests for monitoring components.

Tests for:
- PredictionMonitor
- AlertManager
- Health checks
- JSON logging
"""

import pytest
import json
import logging
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from backend.app.ml_monitoring.prediction_monitor import PredictionMonitor
from backend.app.ml_monitoring.alert_manager import AlertManager
from backend.app.ml_monitoring.health_check import check_model_health
from backend.app.ml_monitoring.json_logging import (
    JSONFormatter,
    configure_json_logging,
    log_with_context,
)


class TestPredictionMonitor:
    """Tests for PredictionMonitor class."""

    def test_initialization(self):
        """Test PredictionMonitor initializes correctly."""
        monitor = PredictionMonitor()
        assert monitor.predictions == []

    def test_log_prediction(self):
        """Test logging a prediction."""
        monitor = PredictionMonitor()

        monitor.log_prediction(
            input_text="Test paper about machine learning",
            predictions={"label": "cs.LG", "confidence": 0.95},
            latency_ms=50.0,
            user_id="user123",
        )

        assert len(monitor.predictions) == 1
        assert monitor.predictions[0]["input_length"] == len(
            "Test paper about machine learning"
        )
        assert monitor.predictions[0]["predictions"]["label"] == "cs.LG"
        assert monitor.predictions[0]["latency_ms"] == 50.0
        assert monitor.predictions[0]["user_id"] == "user123"
        assert monitor.predictions[0]["error"] is None

    def test_log_prediction_with_error(self):
        """Test logging a prediction with error."""
        monitor = PredictionMonitor()

        monitor.log_prediction(
            input_text="Test input",
            predictions={},
            latency_ms=0.0,
            error="Model not loaded",
        )

        assert len(monitor.predictions) == 1
        assert monitor.predictions[0]["error"] == "Model not loaded"

    def test_get_metrics_empty(self):
        """Test getting metrics with no predictions."""
        monitor = PredictionMonitor()
        metrics = monitor.get_metrics(window_minutes=60)

        assert metrics["total_predictions"] == 0
        assert metrics["error_rate"] == 0.0
        assert metrics["latency_p50"] == 0.0

    def test_get_metrics_with_predictions(self):
        """Test calculating metrics from predictions."""
        monitor = PredictionMonitor()

        # Add some predictions
        for i in range(10):
            monitor.log_prediction(
                input_text=f"Test input {i}",
                predictions={"label": "cs.AI", "confidence": 0.8 + i * 0.01},
                latency_ms=50.0 + i * 5.0,
            )

        # Add one error
        monitor.log_prediction(
            input_text="Error input", predictions={}, latency_ms=0.0, error="Test error"
        )

        metrics = monitor.get_metrics(window_minutes=60)

        assert metrics["total_predictions"] == 11
        assert metrics["error_rate"] == pytest.approx(1 / 11, rel=0.01)
        assert metrics["latency_p50"] > 0
        assert metrics["latency_p95"] > metrics["latency_p50"]
        assert metrics["avg_confidence"] > 0

    def test_get_metrics_time_window(self):
        """Test metrics respect time window."""
        monitor = PredictionMonitor()

        # Add old prediction (manually set timestamp)
        old_prediction = {
            "timestamp": datetime.now() - timedelta(hours=2),
            "input_length": 10,
            "predictions": {"label": "cs.AI", "confidence": 0.9},
            "latency_ms": 50.0,
            "error": None,
            "user_id": None,
        }
        monitor.predictions.append(old_prediction)

        # Add recent prediction
        monitor.log_prediction(
            input_text="Recent input",
            predictions={"label": "cs.LG", "confidence": 0.85},
            latency_ms=60.0,
        )

        # Get metrics for last 60 minutes
        metrics = monitor.get_metrics(window_minutes=60)

        # Should only include recent prediction
        assert metrics["total_predictions"] == 1

    def test_clear_old_predictions(self):
        """Test clearing old predictions."""
        monitor = PredictionMonitor()

        # Add old predictions
        for i in range(5):
            old_prediction = {
                "timestamp": datetime.now() - timedelta(hours=25),
                "input_length": 10,
                "predictions": {"label": "cs.AI", "confidence": 0.9},
                "latency_ms": 50.0,
                "error": None,
                "user_id": None,
            }
            monitor.predictions.append(old_prediction)

        # Add recent predictions
        for i in range(3):
            monitor.log_prediction(
                input_text=f"Recent {i}",
                predictions={"label": "cs.LG", "confidence": 0.85},
                latency_ms=60.0,
            )

        # Clear old predictions (24 hour retention)
        removed = monitor.clear_old_predictions(retention_hours=24)

        assert removed == 5
        assert len(monitor.predictions) == 3


class TestAlertManager:
    """Tests for AlertManager class."""

    def test_initialization(self):
        """Test AlertManager initializes with thresholds."""
        manager = AlertManager(
            slack_webhook="https://hooks.slack.com/test",
            error_rate_threshold=0.05,
            latency_p95_threshold=200.0,
            low_confidence_threshold=0.30,
        )

        assert manager.slack_webhook == "https://hooks.slack.com/test"
        assert manager.error_rate_threshold == 0.05
        assert manager.latency_p95_threshold == 200.0
        assert manager.low_confidence_threshold == 0.30

    def test_check_and_alert_no_violations(self):
        """Test no alerts when metrics are within thresholds."""
        manager = AlertManager(error_rate_threshold=0.05)

        metrics = {
            "error_rate": 0.02,
            "latency_p95": 150.0,
            "low_confidence_rate": 0.20,
        }

        alerts = manager.check_and_alert(metrics)
        assert len(alerts) == 0

    def test_check_and_alert_high_error_rate(self):
        """Test alert triggered for high error rate."""
        manager = AlertManager(error_rate_threshold=0.05)

        metrics = {
            "error_rate": 0.10,
            "latency_p95": 150.0,
            "low_confidence_rate": 0.20,
        }

        alerts = manager.check_and_alert(metrics)
        assert len(alerts) == 1
        assert "HIGH ERROR RATE" in alerts[0]

    def test_check_and_alert_high_latency(self):
        """Test alert triggered for high latency."""
        manager = AlertManager(latency_p95_threshold=200.0)

        metrics = {
            "error_rate": 0.02,
            "latency_p95": 250.0,
            "low_confidence_rate": 0.20,
        }

        alerts = manager.check_and_alert(metrics)
        assert len(alerts) == 1
        assert "HIGH LATENCY" in alerts[0]

    def test_check_and_alert_low_confidence(self):
        """Test alert triggered for high low-confidence rate."""
        manager = AlertManager(low_confidence_threshold=0.30)

        metrics = {
            "error_rate": 0.02,
            "latency_p95": 150.0,
            "low_confidence_rate": 0.40,
        }

        alerts = manager.check_and_alert(metrics)
        assert len(alerts) == 1
        assert "LOW-CONFIDENCE" in alerts[0]

    def test_check_and_alert_multiple_violations(self):
        """Test multiple alerts for multiple violations."""
        manager = AlertManager(
            error_rate_threshold=0.05,
            latency_p95_threshold=200.0,
            low_confidence_threshold=0.30,
        )

        metrics = {
            "error_rate": 0.10,
            "latency_p95": 250.0,
            "low_confidence_rate": 0.40,
        }

        alerts = manager.check_and_alert(metrics)
        assert len(alerts) == 3

    @patch("requests.post")
    def test_send_slack_alert_success(self, mock_post):
        """Test sending Slack alert successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        manager = AlertManager(slack_webhook="https://hooks.slack.com/test")

        alerts = ["Test alert"]
        metrics = {"total_predictions": 100, "error_rate": 0.10}

        result = manager.send_slack_alert(alerts, metrics)

        assert result is True
        assert mock_post.called

    @patch("requests.post")
    def test_send_slack_alert_failure(self, mock_post):
        """Test handling Slack alert failure."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        manager = AlertManager(slack_webhook="https://hooks.slack.com/test")

        alerts = ["Test alert"]
        metrics = {"total_predictions": 100}

        result = manager.send_slack_alert(alerts, metrics)

        assert result is False

    def test_send_slack_alert_no_webhook(self):
        """Test sending alert without webhook configured."""
        manager = AlertManager(slack_webhook=None)

        alerts = ["Test alert"]
        metrics = {"total_predictions": 100}

        result = manager.send_slack_alert(alerts, metrics)

        assert result is False


class TestHealthCheck:
    """Tests for health check functions."""

    def test_check_model_health_no_model(self):
        """Test health check with no model loaded."""
        results = check_model_health(model=None)

        assert results["model_loaded"] is False
        assert results["overall_healthy"] is False

    def test_check_model_health_with_model(self):
        """Test health check with model loaded."""
        mock_model = Mock()
        mock_model.predict = Mock(return_value={"label": "cs.AI"})

        results = check_model_health(model=mock_model, test_input="Test input")

        assert results["model_loaded"] is True
        assert results["inference_working"] is True
        assert results["latency_ms"] is not None

    def test_check_model_health_inference_failure(self):
        """Test health check when inference fails."""
        mock_model = Mock()
        mock_model.predict = Mock(side_effect=Exception("Inference error"))

        results = check_model_health(model=mock_model, test_input="Test input")

        assert results["model_loaded"] is True
        assert results["inference_working"] is False
        assert "Inference failed" in results["details"]["inference_working"]

    def test_check_model_health_high_latency(self):
        """Test health check detects high latency."""
        mock_model = Mock()

        # Simulate slow inference
        def slow_predict(text):
            import time

            time.sleep(0.3)  # 300ms
            return {"label": "cs.AI"}

        mock_model.predict = slow_predict

        results = check_model_health(
            model=mock_model, test_input="Test input", latency_threshold_ms=200.0
        )

        assert results["inference_working"] is True
        assert results["latency_acceptable"] is False
        assert results["latency_ms"] > 200.0


class TestJSONLogging:
    """Tests for JSON logging formatter."""

    def test_json_formatter_basic(self):
        """Test JSONFormatter formats basic log record."""
        formatter = JSONFormatter()

        # Create a log record
        logger = logging.getLogger("test")
        record = logger.makeRecord(
            name="test",
            level=logging.INFO,
            fn="test.py",
            lno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Format the record
        formatted = formatter.format(record)

        # Parse JSON
        log_entry = json.loads(formatted)

        assert log_entry["level"] == "INFO"
        assert log_entry["logger"] == "test"
        assert log_entry["message"] == "Test message"
        assert log_entry["line"] == 10
        assert "timestamp" in log_entry

    def test_json_formatter_with_exception(self):
        """Test JSONFormatter includes exception information."""
        formatter = JSONFormatter()

        logger = logging.getLogger("test")

        try:
            raise ValueError("Test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

            record = logger.makeRecord(
                name="test",
                level=logging.ERROR,
                fn="test.py",
                lno=20,
                msg="Error occurred",
                args=(),
                exc_info=exc_info,
            )

            formatted = formatter.format(record)
            log_entry = json.loads(formatted)

            assert "exception" in log_entry
            assert log_entry["exception"]["type"] == "ValueError"
            assert "Test error" in log_entry["exception"]["message"]
            assert "traceback" in log_entry["exception"]

    def test_json_formatter_with_extra_fields(self):
        """Test JSONFormatter includes extra fields."""
        formatter = JSONFormatter(include_extra=True)

        logger = logging.getLogger("test")
        record = logger.makeRecord(
            name="test",
            level=logging.INFO,
            fn="test.py",
            lno=30,
            msg="Training completed",
            args=(),
            exc_info=None,
        )

        # Add extra fields
        record.model_version = "v1.0.0"
        record.accuracy = 0.95

        formatted = formatter.format(record)
        log_entry = json.loads(formatted)

        assert "extra" in log_entry
        assert log_entry["extra"]["model_version"] == "v1.0.0"
        assert log_entry["extra"]["accuracy"] == 0.95

    def test_configure_json_logging(self):
        """Test configuring logger with JSON formatter."""
        logger = configure_json_logging("test_json_logger", level=logging.DEBUG)

        assert logger.level == logging.DEBUG
        assert len(logger.handlers) > 0
        assert isinstance(logger.handlers[0].formatter, JSONFormatter)

    def test_log_with_context(self):
        """Test logging with context fields."""
        logger = configure_json_logging("test_context_logger")

        # Capture log output
        import io

        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(JSONFormatter())
        logger.handlers = [handler]

        log_with_context(
            logger, logging.INFO, "Model trained", model_version="v1.0.0", accuracy=0.95
        )

        # Parse logged JSON
        log_output = log_stream.getvalue()
        log_entry = json.loads(log_output)

        assert log_entry["message"] == "Model trained"
        assert "extra" in log_entry
        assert log_entry["extra"]["model_version"] == "v1.0.0"
        assert log_entry["extra"]["accuracy"] == 0.95


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
