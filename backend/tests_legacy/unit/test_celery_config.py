"""
Unit tests for Celery configuration and DatabaseTask base class.

Tests verify:
- Celery app configuration
- Task routing rules
- Priority queuing
- DatabaseTask session management
- Scheduled task configuration
"""

import pytest
from unittest.mock import patch, MagicMock
from celery.schedules import crontab

from app.tasks.celery_app import celery_app


class TestCeleryConfiguration:
    """Test Celery application configuration."""

    def test_celery_app_exists(self):
        """Test that Celery app is properly initialized."""
        assert celery_app is not None
        assert celery_app.main == "neo_alexandria"

    def test_task_serialization_config(self):
        """Test task serialization is configured to use JSON."""
        assert celery_app.conf.task_serializer == "json"
        assert "json" in celery_app.conf.accept_content
        assert celery_app.conf.result_serializer == "json"

    def test_timezone_config(self):
        """Test timezone is configured to UTC."""
        assert celery_app.conf.timezone == "UTC"
        assert celery_app.conf.enable_utc is True

    def test_priority_queuing_config(self):
        """Test priority queuing is configured with 10 levels."""
        assert celery_app.conf.task_queue_max_priority == 10
        assert celery_app.conf.task_default_priority == 5

    def test_task_acknowledgment_config(self):
        """Test task acknowledgment configuration."""
        assert celery_app.conf.task_acks_late is True
        assert celery_app.conf.task_reject_on_worker_lost is True

    def test_worker_optimization_config(self):
        """Test worker optimization settings."""
        assert celery_app.conf.worker_prefetch_multiplier == 4
        assert celery_app.conf.worker_max_tasks_per_child == 1000

    def test_result_expiration_config(self):
        """Test result expiration is set to 3600 seconds."""
        assert celery_app.conf.result_expires == 3600

    def test_task_routing_rules(self):
        """Test task routing rules are defined."""
        routes = celery_app.conf.task_routes

        # Check critical task routes
        assert "app.tasks.celery_tasks.regenerate_embedding_task" in routes
        assert (
            routes["app.tasks.celery_tasks.regenerate_embedding_task"]["queue"]
            == "high_priority"
        )

        assert "app.tasks.celery_tasks.update_search_index_task" in routes
        assert (
            routes["app.tasks.celery_tasks.update_search_index_task"]["queue"]
            == "urgent"
        )

        assert "app.tasks.celery_tasks.classify_resource_task" in routes
        assert (
            routes["app.tasks.celery_tasks.classify_resource_task"]["queue"]
            == "ml_tasks"
        )

        assert "app.tasks.celery_tasks.batch_process_resources_task" in routes
        assert (
            routes["app.tasks.celery_tasks.batch_process_resources_task"]["queue"]
            == "batch"
        )

    def test_task_queues_defined(self):
        """Test that task queues are properly defined."""
        queues = celery_app.conf.task_queues
        queue_names = [q.name for q in queues]

        assert "urgent" in queue_names
        assert "high_priority" in queue_names
        assert "default" in queue_names
        assert "ml_tasks" in queue_names
        assert "batch" in queue_names


class TestCeleryBeatSchedule:
    """Test Celery Beat scheduled tasks configuration."""

    def test_beat_schedule_exists(self):
        """Test that beat schedule is configured."""
        assert celery_app.conf.beat_schedule is not None
        assert len(celery_app.conf.beat_schedule) > 0

    def test_quality_degradation_monitoring_schedule(self):
        """Test quality degradation monitoring is scheduled daily at 2 AM."""
        schedule = celery_app.conf.beat_schedule.get("monitor-quality-degradation")
        assert schedule is not None
        assert (
            schedule["task"]
            == "app.tasks.celery_tasks.monitor_quality_degradation_task"
        )

        # Check crontab schedule
        cron = schedule["schedule"]
        assert isinstance(cron, crontab)
        assert cron.hour == {2}
        assert cron.minute == {0}

    def test_quality_outlier_detection_schedule(self):
        """Test quality outlier detection is scheduled weekly on Sunday at 3 AM."""
        schedule = celery_app.conf.beat_schedule.get("detect-quality-outliers")
        assert schedule is not None
        assert schedule["task"] == "app.tasks.celery_tasks.detect_quality_outliers_task"

        # Check crontab schedule
        cron = schedule["schedule"]
        assert isinstance(cron, crontab)
        assert cron.day_of_week == {0}  # Sunday
        assert cron.hour == {3}
        assert cron.minute == {0}

    def test_classification_retraining_schedule(self):
        """Test classification model retraining is scheduled monthly on 1st at midnight."""
        schedule = celery_app.conf.beat_schedule.get("retrain-classification-model")
        assert schedule is not None
        assert (
            schedule["task"]
            == "app.tasks.celery_tasks.retrain_classification_model_task"
        )

        # Check crontab schedule
        cron = schedule["schedule"]
        assert isinstance(cron, crontab)
        assert cron.day_of_month == {1}
        assert cron.hour == {0}
        assert cron.minute == {0}

    def test_cache_cleanup_schedule(self):
        """Test cache cleanup is scheduled daily at 4 AM."""
        schedule = celery_app.conf.beat_schedule.get("cleanup-expired-cache")
        assert schedule is not None
        assert schedule["task"] == "app.tasks.celery_tasks.cleanup_expired_cache_task"

        # Check crontab schedule
        cron = schedule["schedule"]
        assert isinstance(cron, crontab)
        assert cron.hour == {4}
        assert cron.minute == {0}


class TestDatabaseTask:
    """Test DatabaseTask base class."""

    @patch("app.tasks.celery_tasks.SessionLocal")
    @patch("app.tasks.celery_tasks.Base")
    def test_database_task_provides_session(self, mock_base, mock_session_local):
        """Test that DatabaseTask provides a database session to tasks."""
        from app.tasks.celery_tasks import DatabaseTask

        # Create mock session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Create a test task
        @celery_app.task(bind=True, base=DatabaseTask)
        def test_task(self, test_arg, db=None):
            assert db is not None
            return f"processed {test_arg}"

        # Execute task
        result = test_task("test_value")

        # Verify session was created and closed
        mock_session_local.assert_called_once()
        mock_db.close.assert_called_once()
        assert result == "processed test_value"

    @patch("app.tasks.celery_tasks.SessionLocal")
    @patch("app.tasks.celery_tasks.Base")
    def test_database_task_closes_session_on_error(self, mock_base, mock_session_local):
        """Test that DatabaseTask closes session even when task raises exception."""
        from app.tasks.celery_tasks import DatabaseTask

        # Create mock session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Create a test task that raises an exception
        @celery_app.task(bind=True, base=DatabaseTask)
        def failing_task(self, db=None):
            raise ValueError("Test error")

        # Execute task and expect exception
        with pytest.raises(ValueError, match="Test error"):
            failing_task()

        # Verify session was still closed
        mock_session_local.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("app.tasks.celery_tasks.SessionLocal")
    @patch("app.tasks.celery_tasks.Base")
    def test_database_task_creates_tables(self, mock_base, mock_session_local):
        """Test that DatabaseTask ensures tables exist."""
        from app.tasks.celery_tasks import DatabaseTask

        # Create mock session
        mock_db = MagicMock()
        mock_bind = MagicMock()
        mock_db.get_bind.return_value = mock_bind
        mock_session_local.return_value = mock_db

        # Create a test task with unique name
        @celery_app.task(bind=True, base=DatabaseTask, name="test_task_creates_tables")
        def test_task_creates_tables(self, db=None):
            return "success"

        # Execute task
        result = test_task_creates_tables()

        # Verify table creation was attempted
        mock_db.get_bind.assert_called()
        assert result == "success"
