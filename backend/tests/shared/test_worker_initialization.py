"""
Unit tests for Celery worker initialization and optimization.

Tests verify:
- Worker process initialization signal handler
- Embedding service pre-loading
- Model reuse across multiple tasks
- Error handling for model loading failures
- Memory usage logging

Requirements: 7.1, 7.2, 7.3, 7.4, 7.6
"""

import pytest
from unittest.mock import patch, MagicMock

from app.tasks.celery_app import init_worker_process, get_embedding_service


# Note: Tests use explicit cleanup instead of autouse fixture to avoid
# test isolation issues with the global _embedding_service variable


class TestWorkerProcessInit:
    """Test worker process initialization signal handler."""

    def setup_method(self):
        """Reset global state before each test."""
        import app.tasks.celery_app as celery_module

        celery_module._embedding_service = None

    def teardown_method(self):
        """Clean up global state after each test."""
        import app.tasks.celery_app as celery_module

        celery_module._embedding_service = None

    @patch("app.shared.embeddings.EmbeddingService")
    @patch("app.tasks.celery_app.time.time")
    def test_init_worker_process_success(self, mock_time, mock_embedding_service_class):
        """Test successful worker process initialization.

        Validates: Requirements 7.1, 7.2, 7.3
        """
        # Setup mocks
        mock_time.side_effect = [0.0, 2.5]  # Start and end times
        mock_embedding_service = MagicMock()
        mock_embedding_service.generate_embedding.return_value = [0.1] * 768
        mock_embedding_service_class.return_value = mock_embedding_service

        # Call initialization
        init_worker_process()

        # Verify embedding service was created
        mock_embedding_service_class.assert_called_once()

        # Verify test embedding was generated
        mock_embedding_service.generate_embedding.assert_called_once_with(
            "Initialization test for worker process"
        )

        # Verify global service was set
        service = get_embedding_service()
        assert service is not None
        assert service == mock_embedding_service

    @patch("app.shared.embeddings.EmbeddingService")
    @patch("app.tasks.celery_app.time.time")
    @patch("app.tasks.celery_app.time.sleep")
    def test_init_worker_process_retry_on_failure(
        self, mock_sleep, mock_time, mock_embedding_service_class
    ):
        """Test worker initialization retries on failure.

        Validates: Requirements 7.6
        """
        # Setup mocks - fail twice, then succeed
        mock_time.side_effect = [0.0, 1.0, 2.0, 3.0, 4.0]

        mock_embedding_service = MagicMock()
        mock_embedding_service.generate_embedding.return_value = [0.1] * 768

        # First two calls fail, third succeeds
        mock_embedding_service_class.side_effect = [
            Exception("Model loading failed"),
            Exception("Model loading failed again"),
            mock_embedding_service,
        ]

        # Call initialization
        init_worker_process()

        # Verify retries occurred
        assert mock_embedding_service_class.call_count == 3
        assert mock_sleep.call_count == 2

        # Verify exponential backoff delays
        mock_sleep.assert_any_call(1)  # 2^0 = 1
        mock_sleep.assert_any_call(2)  # 2^1 = 2

        # Verify service was eventually set
        service = get_embedding_service()
        assert service == mock_embedding_service

    @patch("app.shared.embeddings.EmbeddingService")
    @patch("app.tasks.celery_app.time.time")
    @patch("app.tasks.celery_app.time.sleep")
    def test_init_worker_process_all_retries_fail(
        self, mock_sleep, mock_time, mock_embedding_service_class
    ):
        """Test worker initialization handles all retries failing.

        Validates: Requirements 7.6
        """
        # Setup mocks - all attempts fail
        mock_time.side_effect = [0.0] + [1.0] * 10
        mock_embedding_service_class.side_effect = Exception("Persistent failure")

        # Call initialization - should not raise exception
        init_worker_process()

        # Verify all retries were attempted (initial + 3 retries = 4 total)
        assert mock_embedding_service_class.call_count == 4

        # Verify service is None after all failures
        import app.tasks.celery_app as celery_module

        assert celery_module._embedding_service is None

    @patch("app.shared.embeddings.EmbeddingService")
    @patch("psutil.Process")
    def test_init_worker_process_logs_memory_usage(
        self, mock_psutil_process, mock_embedding_service_class
    ):
        """Test worker initialization logs memory usage.

        Validates: Requirements 7.5
        """
        # Setup mocks
        mock_embedding_service = MagicMock()
        mock_embedding_service.generate_embedding.return_value = [0.1] * 768
        mock_embedding_service_class.return_value = mock_embedding_service

        mock_process = MagicMock()
        mock_process.memory_info.return_value.rss = 512 * 1024 * 1024  # 512 MB
        mock_psutil_process.return_value = mock_process

        # Call initialization
        init_worker_process()

        # Verify memory info was retrieved
        mock_psutil_process.assert_called_once()
        mock_process.memory_info.assert_called_once()

    @patch("app.shared.embeddings.EmbeddingService")
    def test_init_worker_process_handles_missing_psutil(
        self, mock_embedding_service_class
    ):
        """Test worker initialization handles missing psutil gracefully.

        Validates: Requirements 7.5
        """
        # Setup mocks
        mock_embedding_service = MagicMock()
        mock_embedding_service.generate_embedding.return_value = [0.1] * 768
        mock_embedding_service_class.return_value = mock_embedding_service

        # Call initialization - should not raise exception even if psutil fails
        init_worker_process()

        # Verify service was still initialized
        service = get_embedding_service()
        assert service is not None


class TestGetEmbeddingService:
    """Test get_embedding_service helper function."""

    def setup_method(self):
        """Reset global state before each test."""
        import app.tasks.celery_app as celery_module

        celery_module._embedding_service = None

    def teardown_method(self):
        """Clean up global state after each test."""
        import app.tasks.celery_app as celery_module

        celery_module._embedding_service = None

    @patch("app.shared.embeddings.EmbeddingService")
    def test_get_embedding_service_success(self, mock_embedding_service_class):
        """Test getting pre-loaded embedding service.

        Validates: Requirements 7.4
        """
        # Setup - initialize worker first
        mock_embedding_service = MagicMock()
        mock_embedding_service.generate_embedding.return_value = [0.1] * 768
        mock_embedding_service_class.return_value = mock_embedding_service

        # Initialize worker
        init_worker_process()

        # Get service
        service = get_embedding_service()

        # Verify service was returned
        assert service is not None
        assert service == mock_embedding_service

    def test_get_embedding_service_not_initialized(self):
        """Test get_embedding_service raises error when not initialized.

        Validates: Requirements 7.4
        """
        # Explicitly ensure service is None
        import app.tasks.celery_app as celery_module

        celery_module._embedding_service = None

        # Verify it's actually None by checking directly
        assert celery_module._embedding_service is None, (
            "Service should be None before test"
        )

        # Attempt to get service - should raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            get_embedding_service()

        # Verify error message
        assert "Embedding service not initialized" in str(exc_info.value)
        assert "worker process" in str(exc_info.value)


class TestModelReuse:
    """Test model reuse across multiple tasks."""

    def setup_method(self):
        """Reset global state before each test."""
        import app.tasks.celery_app as celery_module

        celery_module._embedding_service = None

    def teardown_method(self):
        """Clean up global state after each test."""
        import app.tasks.celery_app as celery_module

        celery_module._embedding_service = None

    @patch("app.shared.embeddings.EmbeddingService")
    def test_model_reuse_across_tasks(self, mock_embedding_service_class):
        """Test that models are reused across multiple task executions.

        Validates: Requirements 7.2, 7.3
        """
        # Setup - initialize worker
        mock_embedding_service = MagicMock()
        mock_embedding_service.generate_embedding.return_value = [0.1] * 768
        mock_embedding_service_class.return_value = mock_embedding_service

        # Initialize worker
        init_worker_process()

        # Verify service was created once
        assert mock_embedding_service_class.call_count == 1

        # Simulate multiple task executions
        service1 = get_embedding_service()
        service2 = get_embedding_service()
        service3 = get_embedding_service()

        # Verify same service instance is returned
        assert service1 is service2
        assert service2 is service3

        # Verify no additional service instances were created
        assert mock_embedding_service_class.call_count == 1

    @patch("app.shared.embeddings.EmbeddingService")
    def test_embedding_generation_uses_preloaded_service(
        self, mock_embedding_service_class
    ):
        """Test that embedding generation uses pre-loaded service.

        Validates: Requirements 7.2, 7.4
        """
        # Setup - initialize worker
        mock_embedding_service = MagicMock()
        mock_embedding_service.generate_embedding.return_value = [0.1] * 768
        mock_embedding_service_class.return_value = mock_embedding_service

        # Initialize worker
        init_worker_process()

        # Get service and generate embeddings
        service = get_embedding_service()

        # Generate multiple embeddings
        embedding1 = service.generate_embedding("Test text 1")
        embedding2 = service.generate_embedding("Test text 2")
        embedding3 = service.generate_embedding("Test text 3")

        # Verify embeddings were generated
        assert len(embedding1) == 768
        assert len(embedding2) == 768
        assert len(embedding3) == 768

        # Verify generate_embedding was called (including init call)
        assert mock_embedding_service.generate_embedding.call_count == 4


class TestWorkerInitializationPerformance:
    """Test worker initialization performance characteristics."""

    def setup_method(self):
        """Reset global state before each test."""
        import app.tasks.celery_app as celery_module

        celery_module._embedding_service = None

    def teardown_method(self):
        """Clean up global state after each test."""
        import app.tasks.celery_app as celery_module

        celery_module._embedding_service = None

    @patch("app.shared.embeddings.EmbeddingService")
    @patch("app.tasks.celery_app.time.time")
    def test_initialization_time_logged(self, mock_time, mock_embedding_service_class):
        """Test that initialization time is logged.

        Validates: Requirements 7.5
        """
        # Setup mocks - simulate 2.5 second initialization
        mock_time.side_effect = [0.0, 2.5]

        mock_embedding_service = MagicMock()
        mock_embedding_service.generate_embedding.return_value = [0.1] * 768
        mock_embedding_service_class.return_value = mock_embedding_service

        # Call initialization with logging capture
        with patch("app.tasks.celery_app.logger") as mock_logger:
            init_worker_process()

            # Verify timing was logged
            log_calls = [str(call) for call in mock_logger.info.call_args_list]
            timing_logged = any("2.50 seconds" in call for call in log_calls)
            assert timing_logged, "Initialization time should be logged"

    @patch("app.shared.embeddings.EmbeddingService")
    def test_test_embedding_dimensions_logged(self, mock_embedding_service_class):
        """Test that test embedding dimensions are logged.

        Validates: Requirements 7.5
        """
        # Setup mocks
        mock_embedding_service = MagicMock()
        mock_embedding_service.generate_embedding.return_value = [0.1] * 768
        mock_embedding_service_class.return_value = mock_embedding_service

        # Call initialization with logging capture
        with patch("app.tasks.celery_app.logger") as mock_logger:
            init_worker_process()

            # Verify dimensions were logged
            log_calls = [str(call) for call in mock_logger.info.call_args_list]
            dimensions_logged = any("768 dimensions" in call for call in log_calls)
            assert dimensions_logged, "Embedding dimensions should be logged"
