"""
Structured JSON logging module for ML training and monitoring.

This module provides a JSONFormatter class for logging events in JSON format,
making logs easier to parse and analyze with log aggregation tools.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional


class JSONFormatter(logging.Formatter):
    """
    Custom logging formatter that outputs logs in JSON format.

    This formatter creates structured JSON log entries with consistent fields
    including timestamp, level, logger name, message, and optional exception info.

    Attributes:
        include_extra (bool): Whether to include extra fields from LogRecord
    """

    def __init__(self, include_extra: bool = True):
        """
        Initialize the JSONFormatter.

        Args:
            include_extra: Whether to include extra fields from LogRecord (default: True)
        """
        super().__init__()
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as a JSON string.

        Args:
            record: LogRecord instance to format

        Returns:
            JSON string representation of the log record
        """
        # Build base log entry
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add process and thread info
        log_entry["process"] = {"id": record.process, "name": record.processName}
        log_entry["thread"] = {"id": record.thread, "name": record.threadName}

        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        # Add stack trace if present
        if record.stack_info:
            log_entry["stack_trace"] = record.stack_info

        # Add extra fields if enabled
        if self.include_extra:
            # Get all extra fields (fields not in standard LogRecord)
            standard_fields = {
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
                "getMessage",
                "taskName",
            }

            extra_fields = {}
            for key, value in record.__dict__.items():
                if key not in standard_fields and not key.startswith("_"):
                    # Try to serialize the value
                    try:
                        json.dumps(value)  # Test if serializable
                        extra_fields[key] = value
                    except (TypeError, ValueError):
                        extra_fields[key] = str(value)

            if extra_fields:
                log_entry["extra"] = extra_fields

        # Convert to JSON string
        try:
            return json.dumps(log_entry, default=str)
        except Exception as e:
            # Fallback to simple format if JSON serialization fails
            return json.dumps(
                {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "level": "ERROR",
                    "logger": "JSONFormatter",
                    "message": f"Failed to format log entry: {str(e)}",
                    "original_message": str(record.getMessage()),
                }
            )


def configure_json_logging(
    logger_name: Optional[str] = None,
    level: int = logging.INFO,
    include_extra: bool = True,
) -> logging.Logger:
    """
    Configure a logger to use JSON formatting.

    Args:
        logger_name: Name of the logger to configure (None for root logger)
        level: Logging level (default: INFO)
        include_extra: Whether to include extra fields in JSON output

    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(JSONFormatter(include_extra=include_extra))

    logger.addHandler(console_handler)

    return logger


def configure_file_json_logging(
    logger_name: Optional[str] = None,
    log_file: str = "logs/application.json",
    level: int = logging.INFO,
    include_extra: bool = True,
) -> logging.Logger:
    """
    Configure a logger to write JSON logs to a file.

    Args:
        logger_name: Name of the logger to configure (None for root logger)
        log_file: Path to log file
        level: Logging level (default: INFO)
        include_extra: Whether to include extra fields in JSON output

    Returns:
        Configured logger instance
    """
    import os

    # Get or create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create file handler with JSON formatter
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(JSONFormatter(include_extra=include_extra))

    logger.addHandler(file_handler)

    return logger


def log_with_context(
    logger: logging.Logger, level: int, message: str, **context
) -> None:
    """
    Log a message with additional context fields.

    This function adds context fields to the log record that will be
    included in the JSON output under the "extra" field.

    Args:
        logger: Logger instance to use
        level: Logging level (e.g., logging.INFO)
        message: Log message
        **context: Additional context fields to include

    Example:
        log_with_context(
            logger,
            logging.INFO,
            "Model training completed",
            model_version="v1.0.0",
            accuracy=0.95,
            training_time=3600
        )
    """
    logger.log(level, message, extra=context)


# Example usage and testing
if __name__ == "__main__":
    # Configure JSON logging
    logger = configure_json_logging("test_logger", level=logging.DEBUG)

    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    # Test with extra context
    log_with_context(
        logger,
        logging.INFO,
        "Training completed",
        model_version="v1.0.0",
        accuracy=0.95,
        epochs=3,
    )

    # Test with exception
    try:
        raise ValueError("Test exception")
    except ValueError:
        logger.exception("An error occurred during processing")

    print("\nJSON logging configured and tested successfully!")
