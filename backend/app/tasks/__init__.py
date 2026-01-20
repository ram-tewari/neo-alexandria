"""
Neo Alexandria 2.0 - Task Queue Package

This package contains Celery task queue configuration and task implementations
for distributed background processing.

Modules:
- celery_app: Celery application configuration and setup
- celery_tasks: Task implementations for background processing

Functions:
- get_embedding_service: Get pre-loaded embedding service from worker
"""

from .celery_app import celery_app, get_embedding_service

__all__ = ["celery_app", "get_embedding_service"]
