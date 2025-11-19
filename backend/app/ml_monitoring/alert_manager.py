"""
Alert management module for monitoring ML model performance and sending notifications.

This module provides the AlertManager class for checking metrics against thresholds
and sending alerts via Slack when issues are detected.
"""

import logging
from typing import Dict, List, Optional, Any
import requests


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlertManager:
    """
    Manager for checking metrics and sending alerts.
    
    This class monitors ML model performance metrics and sends alerts
    to Slack when thresholds are exceeded.
    
    Attributes:
        slack_webhook (Optional[str]): Slack webhook URL for sending alerts
        error_rate_threshold (float): Maximum acceptable error rate (default: 0.05 = 5%)
        latency_p95_threshold (float): Maximum acceptable p95 latency in ms (default: 200)
        low_confidence_threshold (float): Maximum acceptable low confidence rate (default: 0.30 = 30%)
    """
    
    def __init__(
        self,
        slack_webhook: Optional[str] = None,
        error_rate_threshold: float = 0.05,
        latency_p95_threshold: float = 200.0,
        low_confidence_threshold: float = 0.30
    ):
        """
        Initialize the AlertManager.
        
        Args:
            slack_webhook: Slack webhook URL for sending alerts
            error_rate_threshold: Maximum acceptable error rate (default: 0.05 = 5%)
            latency_p95_threshold: Maximum acceptable p95 latency in ms (default: 200)
            low_confidence_threshold: Maximum acceptable low confidence rate (default: 0.30 = 30%)
        """
        self.slack_webhook = slack_webhook
        self.error_rate_threshold = error_rate_threshold
        self.latency_p95_threshold = latency_p95_threshold
        self.low_confidence_threshold = low_confidence_threshold
        
        logger.info("AlertManager initialized")
        logger.info(f"Thresholds - Error rate: {error_rate_threshold*100}%, "
                   f"Latency p95: {latency_p95_threshold}ms, "
                   f"Low confidence: {low_confidence_threshold*100}%")
    
    def check_and_alert(self, metrics: Dict[str, Any]) -> List[str]:
        """
        Check metrics against thresholds and send alerts if violations detected.
        
        Args:
            metrics: Dictionary containing performance metrics from PredictionMonitor
        
        Returns:
            List of alert messages that were triggered
        """
        alerts = []
        
        # Check error rate
        if "error_rate" in metrics:
            error_rate = metrics["error_rate"]
            if error_rate > self.error_rate_threshold:
                alert_msg = (
                    f"⚠️ HIGH ERROR RATE: {error_rate*100:.2f}% "
                    f"(threshold: {self.error_rate_threshold*100:.2f}%)"
                )
                alerts.append(alert_msg)
                logger.warning(alert_msg)
        
        # Check latency p95
        if "latency_p95" in metrics:
            latency_p95 = metrics["latency_p95"]
            if latency_p95 > self.latency_p95_threshold:
                alert_msg = (
                    f"⚠️ HIGH LATENCY (p95): {latency_p95:.2f}ms "
                    f"(threshold: {self.latency_p95_threshold:.2f}ms)"
                )
                alerts.append(alert_msg)
                logger.warning(alert_msg)
        
        # Check low confidence rate
        if "low_confidence_rate" in metrics:
            low_confidence_rate = metrics["low_confidence_rate"]
            if low_confidence_rate > self.low_confidence_threshold:
                alert_msg = (
                    f"⚠️ HIGH LOW-CONFIDENCE RATE: {low_confidence_rate*100:.2f}% "
                    f"(threshold: {self.low_confidence_threshold*100:.2f}%)"
                )
                alerts.append(alert_msg)
                logger.warning(alert_msg)
        
        # Send alerts if any were triggered
        if alerts:
            self.send_slack_alert(alerts, metrics)
        
        return alerts
    
    def send_slack_alert(self, alerts: List[str], metrics: Dict[str, Any]) -> bool:
        """
        Send alert notification to Slack.
        
        Args:
            alerts: List of alert messages to send
            metrics: Full metrics dictionary for context
        
        Returns:
            True if alert was sent successfully, False otherwise
        """
        if not self.slack_webhook:
            logger.warning("Slack webhook not configured, skipping alert notification")
            return False
        
        # Build Slack message
        alert_text = "\n".join(alerts)
        
        # Add metrics summary
        metrics_summary = (
            f"\n\n📊 *Metrics Summary:*\n"
            f"• Total predictions: {metrics.get('total_predictions', 0)}\n"
            f"• Error rate: {metrics.get('error_rate', 0)*100:.2f}%\n"
            f"• Latency p50: {metrics.get('latency_p50', 0):.2f}ms\n"
            f"• Latency p95: {metrics.get('latency_p95', 0):.2f}ms\n"
            f"• Latency p99: {metrics.get('latency_p99', 0):.2f}ms\n"
            f"• Avg confidence: {metrics.get('avg_confidence', 0):.3f}\n"
            f"• Low confidence rate: {metrics.get('low_confidence_rate', 0)*100:.2f}%\n"
            f"• Window: {metrics.get('window_minutes', 0)} minutes"
        )
        
        message = {
            "text": "🚨 *ML Model Alert*",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 ML Model Alert"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": alert_text + metrics_summary
                    }
                }
            ]
        }
        
        try:
            response = requests.post(
                self.slack_webhook,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Alert sent to Slack successfully")
                return True
            else:
                logger.error(f"Failed to send Slack alert: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending Slack alert: {e}")
            return False
    
    def send_custom_alert(self, title: str, message: str, severity: str = "warning") -> bool:
        """
        Send a custom alert to Slack.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity ("info", "warning", "error")
        
        Returns:
            True if alert was sent successfully, False otherwise
        """
        if not self.slack_webhook:
            logger.warning("Slack webhook not configured, skipping alert notification")
            return False
        
        # Choose emoji based on severity
        emoji_map = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "🚨"
        }
        emoji = emoji_map.get(severity, "ℹ️")
        
        slack_message = {
            "text": f"{emoji} *{title}*",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{emoji} {title}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                }
            ]
        }
        
        try:
            response = requests.post(
                self.slack_webhook,
                json=slack_message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Custom alert sent to Slack: {title}")
                return True
            else:
                logger.error(f"Failed to send custom alert: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending custom alert: {e}")
            return False
