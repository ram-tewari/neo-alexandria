"""
Neo Alexandria 2.0 - Celery Application Configuration

This module configures the Celery distributed task queue for Neo Alexandria.
It provides reliable, prioritized background processing with automatic retries,
task routing, and scheduled task execution.

Related files:
- app/tasks/celery_tasks.py: Task implementations
- app/events/hooks.py: Event hooks that queue tasks
- app/config/settings.py: Configuration settings
- docker-compose.yml: Redis and worker deployment

Features:
- Redis-based message broker and result backend
- Priority queuing with 10 levels (0-9, higher = more urgent)
- Task routing to specialized queues (urgent, high_priority, ml_tasks, batch)
- Automatic task acknowledgment and requeuing on worker failure
- Worker optimization with prefetching and recycling
- Scheduled tasks via Celery Beat
- Result expiration after 1 hour

Architecture:
    API/Service → Event → Hook → Queue Task → Redis → Worker → Execute
"""

from celery import Celery
from celery.schedules import crontab
from kombu import Queue

from ..config.settings import get_settings

settings = get_settings()

# Initialize Celery application
celery_app = Celery(
    "neo_alexandria",
    broker=f"redis://{getattr(settings, 'REDIS_HOST', 'localhost')}:{getattr(settings, 'REDIS_PORT', 6379)}/0",
    backend=f"redis://{getattr(settings, 'REDIS_HOST', 'localhost')}:{getattr(settings, 'REDIS_PORT', 6379)}/1",
)

# Celery Configuration
celery_app.conf.update(
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing - assign tasks to appropriate queues
    task_routes={
        "app.tasks.celery_tasks.regenerate_embedding_task": {"queue": "high_priority"},
        "app.tasks.celery_tasks.recompute_quality_task": {"queue": "default"},
        "app.tasks.celery_tasks.update_search_index_task": {"queue": "urgent"},
        "app.tasks.celery_tasks.update_graph_edges_task": {"queue": "default"},
        "app.tasks.celery_tasks.classify_resource_task": {"queue": "ml_tasks"},
        "app.tasks.celery_tasks.invalidate_cache_task": {"queue": "urgent"},
        "app.tasks.celery_tasks.refresh_recommendation_profile_task": {"queue": "default"},
        "app.tasks.celery_tasks.batch_process_resources_task": {"queue": "batch"},
        "app.tasks.celery_tasks.normalize_author_names_task": {"queue": "default"},
    },
    
    # Define task queues with priority support
    task_queues=(
        Queue("urgent", routing_key="urgent", priority=9),
        Queue("high_priority", routing_key="high_priority", priority=7),
        Queue("default", routing_key="default", priority=5),
        Queue("ml_tasks", routing_key="ml_tasks", priority=5),
        Queue("batch", routing_key="batch", priority=3),
    ),
    
    # Priority queuing configuration
    task_queue_max_priority=10,  # 0-9 priority levels
    task_default_priority=5,      # Medium priority by default
    
    # Task acknowledgment configuration
    task_acks_late=True,                    # Acknowledge after task completion
    task_reject_on_worker_lost=True,        # Requeue tasks if worker crashes
    
    # Worker optimization
    worker_prefetch_multiplier=4,           # Prefetch 4 tasks per worker
    worker_max_tasks_per_child=1000,        # Restart worker after 1000 tasks (prevent memory leaks)
    
    # Result backend configuration
    result_expires=3600,                    # Results expire after 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
    },
    
    # Task execution configuration
    task_track_started=True,                # Track when tasks start
    task_time_limit=3600,                   # Hard time limit: 1 hour
    task_soft_time_limit=3300,              # Soft time limit: 55 minutes
    
    # Event monitoring
    worker_send_task_events=True,           # Send task events for monitoring
    task_send_sent_event=True,              # Send event when task is sent
)

# Celery Beat Schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Quality degradation monitoring - daily at 2 AM
    "monitor-quality-degradation": {
        "task": "app.tasks.celery_tasks.monitor_quality_degradation_task",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "default", "priority": 5},
    },
    
    # Quality outlier detection - weekly on Sunday at 3 AM
    "detect-quality-outliers": {
        "task": "app.tasks.celery_tasks.detect_quality_outliers_task",
        "schedule": crontab(day_of_week=0, hour=3, minute=0),
        "options": {"queue": "default", "priority": 5},
    },
    
    # Classification model retraining - monthly on 1st at midnight
    "retrain-classification-model": {
        "task": "app.tasks.celery_tasks.retrain_classification_model_task",
        "schedule": crontab(day_of_month=1, hour=0, minute=0),
        "options": {"queue": "ml_tasks", "priority": 5},
    },
    
    # Cache cleanup - daily at 4 AM
    "cleanup-expired-cache": {
        "task": "app.tasks.celery_tasks.cleanup_expired_cache_task",
        "schedule": crontab(hour=4, minute=0),
        "options": {"queue": "default", "priority": 3},
    },
}

# Import tasks to register them with Celery
# This must be done after celery_app is configured
try:
    from . import celery_tasks  # noqa: F401
except ImportError:
    # Tasks module not yet created
    pass
