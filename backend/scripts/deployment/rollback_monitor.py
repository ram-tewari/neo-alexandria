"""
Automatic rollback monitoring for production deployments.

This module provides functions for continuously monitoring production metrics
and automatically triggering rollbacks when metrics degrade beyond acceptable
thresholds.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .model_versioning import ModelVersioning


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Rollback thresholds
ERROR_RATE_THRESHOLD = 0.10  # 10%
LATENCY_P95_THRESHOLD_MS = 500  # 500ms


def monitor_and_rollback(
    check_interval_seconds: int = 60,
    max_duration_seconds: Optional[int] = None,
    base_dir: str = "models/classification",
) -> None:
    """
    Continuously monitor production metrics and rollback if issues detected.

    This function runs in a loop, periodically checking production metrics:
    - Error rate: Triggers rollback if >10%
    - Latency (p95): Triggers rollback if >500ms

    When issues are detected, it automatically rolls back to the previous
    production version and sends alert notifications.

    Args:
        check_interval_seconds: Interval between metric checks (default: 60)
        max_duration_seconds: Maximum duration to monitor (None = infinite)
        base_dir: Base directory for model versions

    Example:
        # Monitor indefinitely
        monitor_and_rollback()

        # Monitor for 1 hour
        monitor_and_rollback(max_duration_seconds=3600)
    """
    logger.info("Starting automatic rollback monitoring...")
    logger.info(f"  Check interval: {check_interval_seconds}s")
    logger.info(f"  Error rate threshold: {ERROR_RATE_THRESHOLD:.1%}")
    logger.info(f"  Latency p95 threshold: {LATENCY_P95_THRESHOLD_MS}ms")

    versioning = ModelVersioning(base_dir=base_dir)

    start_time = time.time()
    check_count = 0

    try:
        while True:
            check_count += 1
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Metric check #{check_count}")
            logger.info(f"{'=' * 60}")

            # Get production metrics
            metrics = get_production_metrics(versioning)

            if not metrics:
                logger.warning("Failed to get production metrics, skipping check")
                time.sleep(check_interval_seconds)
                continue

            # Log current metrics
            logger.info("Current metrics:")
            logger.info(f"  Error rate: {metrics.get('error_rate', 0):.4f}")
            logger.info(f"  Latency p95: {metrics.get('latency_p95', 0):.2f}ms")
            logger.info(f"  Total predictions: {metrics.get('total_predictions', 0)}")

            # Check error rate
            error_rate = metrics.get("error_rate", 0.0)
            if error_rate > ERROR_RATE_THRESHOLD:
                logger.error(
                    f"High error rate detected: {error_rate:.4f} > {ERROR_RATE_THRESHOLD:.4f}"
                )
                logger.error("Triggering automatic rollback...")

                rollback_success = rollback_to_previous_version(
                    versioning, reason=f"High error rate: {error_rate:.4f}"
                )

                if rollback_success:
                    send_alert_notification(
                        "Automatic rollback triggered: high error rate",
                        {
                            "error_rate": error_rate,
                            "threshold": ERROR_RATE_THRESHOLD,
                            "rollback_successful": True,
                        },
                    )
                    logger.info("Rollback completed, exiting monitor")
                    break
                else:
                    send_alert_notification(
                        "Automatic rollback FAILED: high error rate",
                        {
                            "error_rate": error_rate,
                            "threshold": ERROR_RATE_THRESHOLD,
                            "rollback_successful": False,
                        },
                    )
                    logger.error("Rollback failed, continuing to monitor")

            # Check latency
            latency_p95 = metrics.get("latency_p95", 0.0)
            if latency_p95 > LATENCY_P95_THRESHOLD_MS:
                logger.error(
                    f"High latency detected: {latency_p95:.2f}ms > {LATENCY_P95_THRESHOLD_MS}ms"
                )
                logger.error("Triggering automatic rollback...")

                rollback_success = rollback_to_previous_version(
                    versioning, reason=f"High latency: {latency_p95:.2f}ms"
                )

                if rollback_success:
                    send_alert_notification(
                        "Automatic rollback triggered: high latency",
                        {
                            "latency_p95": latency_p95,
                            "threshold": LATENCY_P95_THRESHOLD_MS,
                            "rollback_successful": True,
                        },
                    )
                    logger.info("Rollback completed, exiting monitor")
                    break
                else:
                    send_alert_notification(
                        "Automatic rollback FAILED: high latency",
                        {
                            "latency_p95": latency_p95,
                            "threshold": LATENCY_P95_THRESHOLD_MS,
                            "rollback_successful": False,
                        },
                    )
                    logger.error("Rollback failed, continuing to monitor")

            # Metrics are acceptable
            logger.info("✓ Metrics are within acceptable thresholds")

            # Check if max duration reached
            if max_duration_seconds is not None:
                elapsed = time.time() - start_time
                if elapsed >= max_duration_seconds:
                    logger.info(
                        f"Max duration reached ({max_duration_seconds}s), exiting monitor"
                    )
                    break

            # Wait before next check
            logger.info(f"Next check in {check_interval_seconds}s...")
            time.sleep(check_interval_seconds)

    except KeyboardInterrupt:
        logger.info("\nMonitoring stopped by user")
    except Exception as e:
        logger.error(f"Monitoring failed with exception: {e}")
        send_alert_notification("Rollback monitoring failed", {"error": str(e)})


def get_production_metrics(versioning: ModelVersioning) -> Dict[str, Any]:
    """
    Get current production metrics.

    In a real deployment, this would query a monitoring system like:
    - Prometheus
    - CloudWatch
    - Datadog
    - Custom metrics API

    For this implementation, we simulate metrics by running test predictions
    on the production model.

    Args:
        versioning: ModelVersioning instance

    Returns:
        Dictionary with metrics:
            - error_rate: Fraction of failed predictions (0.0-1.0)
            - latency_p95: 95th percentile latency in milliseconds
            - total_predictions: Number of predictions evaluated
    """
    logger.debug("Getting production metrics...")

    try:
        # Get production version
        production_version = versioning.registry.get("production_version")
        if not production_version:
            logger.warning("No production version found")
            return {}

        logger.debug(f"Production version: {production_version}")

        # Load production model
        model_data, _ = versioning.load_version(production_version)

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
            "Convolutional networks excel at image recognition.",
            "Recurrent networks process sequential data.",
            "Attention mechanisms focus on relevant information.",
            "Transformers revolutionized natural language processing.",
            "Generative models create new data samples.",
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
            "total_predictions": len(test_samples),
            "num_errors": errors,
            "production_version": production_version,
        }

        logger.debug(f"Production metrics: {metrics}")

        return metrics

    except Exception as e:
        logger.error(f"Failed to get production metrics: {e}")
        return {}


def rollback_to_previous_version(
    versioning: ModelVersioning, reason: str = "Metrics degraded"
) -> bool:
    """
    Rollback to previous production version.

    This function:
    1. Identifies the previous production version from version registry
    2. Promotes the previous version back to production
    3. Logs the rollback event

    Args:
        versioning: ModelVersioning instance
        reason: Reason for rollback

    Returns:
        True if rollback successful, False otherwise
    """
    logger.warning(f"Rolling back to previous version: {reason}")

    try:
        # Get current production version
        current_version = versioning.registry.get("production_version")
        if not current_version:
            logger.error("No current production version found")
            return False

        logger.info(f"Current production version: {current_version}")

        # Find previous production version
        # Look for the most recent version that is not the current one
        versions = versioning.registry.get("versions", [])

        # Sort by created_at timestamp (most recent first)
        sorted_versions = sorted(
            versions, key=lambda v: v.get("created_at", ""), reverse=True
        )

        previous_version = None
        for v in sorted_versions:
            if v["version"] != current_version and v.get("status") != "failed":
                previous_version = v["version"]
                break

        if not previous_version:
            logger.error("No previous version found for rollback")
            return False

        logger.info(f"Previous version identified: {previous_version}")

        # Promote previous version to production
        logger.info(f"Promoting {previous_version} to production...")
        versioning.promote_to_production(previous_version)

        logger.info(f"Rollback successful: {current_version} → {previous_version}")

        # Log rollback event
        rollback_log = {
            "timestamp": datetime.now().isoformat(),
            "from_version": current_version,
            "to_version": previous_version,
            "reason": reason,
            "success": True,
        }

        _save_rollback_log(rollback_log)

        return True

    except Exception as e:
        logger.error(f"Rollback failed: {e}")

        # Log failed rollback
        rollback_log = {
            "timestamp": datetime.now().isoformat(),
            "from_version": current_version if "current_version" in locals() else None,
            "to_version": previous_version if "previous_version" in locals() else None,
            "reason": reason,
            "success": False,
            "error": str(e),
        }

        _save_rollback_log(rollback_log)

        return False


def _save_rollback_log(rollback_log: Dict[str, Any]) -> None:
    """
    Save rollback event to log file.

    Args:
        rollback_log: Rollback event dictionary
    """
    log_file = Path("rollback_log.json")

    # Load existing log
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []

    # Append new log
    logs.append(rollback_log)

    # Save updated log
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)

    logger.info(f"Rollback event logged to {log_file}")


def send_alert_notification(message: str, details: Dict[str, Any]) -> None:
    """
    Send alert notification about rollback event.

    In a real deployment, this would send notifications via:
    - Slack webhook
    - Email (SMTP)
    - PagerDuty
    - SMS
    - Custom alerting system

    For this implementation, we log the alert and save to a file.

    Args:
        message: Alert message
        details: Alert details dictionary
    """
    logger.warning(f"ALERT: {message}")
    logger.warning(f"Details: {json.dumps(details, indent=2)}")

    # Create alert object
    alert = {
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "details": details,
        "severity": "critical",
    }

    # Save alert to file
    alert_file = Path("alerts.json")

    if alert_file.exists():
        with open(alert_file, "r", encoding="utf-8") as f:
            alerts = json.load(f)
    else:
        alerts = []

    alerts.append(alert)

    with open(alert_file, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)

    logger.info(f"Alert saved to {alert_file}")

    # In production, send to Slack:
    # import requests
    # slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
    # if slack_webhook:
    #     requests.post(slack_webhook, json={
    #         "text": f"🚨 {message}",
    #         "attachments": [{
    #             "color": "danger",
    #             "fields": [
    #                 {"title": k, "value": str(v), "short": True}
    #                 for k, v in details.items()
    #             ]
    #         }]
    #     })


def main():
    """
    Main function for command-line usage.

    Example usage:
        # Monitor indefinitely with 60s check interval
        python rollback_monitor.py monitor

        # Monitor for 1 hour with 30s check interval
        python rollback_monitor.py monitor --duration 3600 --interval 30

        # Manually trigger rollback
        python rollback_monitor.py rollback --reason "Manual rollback for testing"
    """
    import argparse

    parser = argparse.ArgumentParser(description="Automatic rollback monitoring")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Start monitoring")
    monitor_parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in seconds (default: 60)",
    )
    monitor_parser.add_argument(
        "--duration",
        type=int,
        default=None,
        help="Max duration in seconds (default: infinite)",
    )
    monitor_parser.add_argument(
        "--base-dir", default="models/classification", help="Base directory for models"
    )

    # Rollback command
    rollback_parser = subparsers.add_parser(
        "rollback", help="Manually trigger rollback"
    )
    rollback_parser.add_argument(
        "--reason", default="Manual rollback", help="Reason for rollback"
    )
    rollback_parser.add_argument(
        "--base-dir", default="models/classification", help="Base directory for models"
    )

    # Check metrics command
    metrics_parser = subparsers.add_parser("metrics", help="Check current metrics")
    metrics_parser.add_argument(
        "--base-dir", default="models/classification", help="Base directory for models"
    )

    args = parser.parse_args()

    if args.command == "monitor":
        # Start monitoring
        print("Starting automatic rollback monitoring...")
        print(f"  Check interval: {args.interval}s")
        if args.duration:
            print(f"  Max duration: {args.duration}s")
        else:
            print("  Max duration: infinite (press Ctrl+C to stop)")
        print()

        monitor_and_rollback(
            check_interval_seconds=args.interval,
            max_duration_seconds=args.duration,
            base_dir=args.base_dir,
        )

    elif args.command == "rollback":
        # Manual rollback
        versioning = ModelVersioning(base_dir=args.base_dir)

        print("Triggering manual rollback...")
        print(f"  Reason: {args.reason}")
        print()

        success = rollback_to_previous_version(versioning, reason=args.reason)

        if success:
            print("✓ Rollback successful")
            send_alert_notification(
                "Manual rollback triggered", {"reason": args.reason}
            )
        else:
            print("✗ Rollback failed")

    elif args.command == "metrics":
        # Check current metrics
        versioning = ModelVersioning(base_dir=args.base_dir)

        print("Checking current production metrics...")
        print()

        metrics = get_production_metrics(versioning)

        if metrics:
            print(f"Production version: {metrics.get('production_version', 'unknown')}")
            print(f"Error rate: {metrics.get('error_rate', 0):.4f}")
            print(f"Latency p95: {metrics.get('latency_p95', 0):.2f}ms")
            print(f"Total predictions: {metrics.get('total_predictions', 0)}")
            print()

            # Check thresholds
            error_rate = metrics.get("error_rate", 0)
            latency_p95 = metrics.get("latency_p95", 0)

            if error_rate > ERROR_RATE_THRESHOLD:
                print(f"⚠ Error rate exceeds threshold ({ERROR_RATE_THRESHOLD:.1%})")
            else:
                print(f"✓ Error rate within threshold ({ERROR_RATE_THRESHOLD:.1%})")

            if latency_p95 > LATENCY_P95_THRESHOLD_MS:
                print(f"⚠ Latency exceeds threshold ({LATENCY_P95_THRESHOLD_MS}ms)")
            else:
                print(f"✓ Latency within threshold ({LATENCY_P95_THRESHOLD_MS}ms)")
        else:
            print("✗ Failed to get metrics")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
