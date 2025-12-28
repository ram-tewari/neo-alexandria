"""
Unit tests for Celery task implementations.

Tests verify:
- Task retry logic with transient errors
- Task failure with permanent errors
- Batch processing progress tracking
- DatabaseTask session management
- Task execution with mocked services
"""

import pytest
from unittest.mock import patch, MagicMock

from app.tasks.celery_tasks import (
    regenerate_embedding_task,
    recompute_quality_task,
    update_search_index_task,
    update_graph_edges_task,
    classify_resource_task,
    invalidate_cache_task,
    refresh_recommendation_profile_task,
    batch_process_resources_task,
    monitor_quality_degradation_task,
    detect_quality_outliers_task,
    retrain_classification_model_task,
    cleanup_expired_cache_task,
    DatabaseTask,
)
from app.tasks.celery_app import celery_app


class TestRegenerateEmbeddingTask:
    """Test embedding regeneration task."""
    
    def test_task_configuration(self):
        """Test task is properly configured with retry settings."""
        assert regenerate_embedding_task.max_retries == 3
        assert regenerate_embedding_task.default_retry_delay == 60
        assert regenerate_embedding_task.name == "app.tasks.celery_tasks.regenerate_embedding_task"


class TestRecomputeQualityTask:
    """Test quality recomputation task."""
    
    @patch('app.tasks.celery_tasks.SessionLocal')
    @patch('app.tasks.celery_tasks.Base')
    @patch('app.services.quality_service.QualityService')
    def test_successful_quality_recomputation(self, mock_quality_service, mock_base, mock_session_local):
        """Test successful quality score recomputation."""
        from backend.app.domain.quality import QualityScore
        
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_service_instance = MagicMock()
        mock_quality_service.return_value = mock_service_instance
        
        # Return QualityScore domain object instead of dict
        quality_score = QualityScore(
            accuracy=0.85,
            completeness=0.9,
            consistency=0.8,
            timeliness=0.85,
            relevance=0.85
        )
        mock_service_instance.compute_quality.return_value = quality_score
        
        # Execute task
        recompute_quality_task("resource-123")
        
        # Verify service was called
        mock_quality_service.assert_called_once_with(mock_db)
        mock_service_instance.compute_quality.assert_called_once_with("resource-123", weights=None)
        mock_db.close.assert_called_once()
    
    @patch('app.tasks.celery_tasks.SessionLocal')
    @patch('app.tasks.celery_tasks.Base')
    @patch('app.services.quality_service.QualityService')
    def test_quality_task_error_handling(self, mock_quality_service, mock_base, mock_session_local):
        """Test quality task handles errors properly."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_service_instance = MagicMock()
        mock_quality_service.return_value = mock_service_instance
        mock_service_instance.compute_quality.side_effect = Exception("Quality computation failed")
        
        # Execute task and expect error
        with pytest.raises(Exception, match="Quality computation failed"):
            recompute_quality_task("resource-123")
        
        mock_db.close.assert_called_once()


class TestUpdateSearchIndexTask:
    """Test search index update task."""
    
    def test_task_configuration(self):
        """Test task is properly configured with URGENT priority."""
        assert update_search_index_task.max_retries == 3
        assert update_search_index_task.default_retry_delay == 5
        assert update_search_index_task.name == "app.tasks.celery_tasks.update_search_index_task"


class TestUpdateGraphEdgesTask:
    """Test graph edge update task."""
    
    @patch('app.tasks.celery_tasks.SessionLocal')
    @patch('app.tasks.celery_tasks.Base')
    @patch('app.services.graph_service.GraphService')
    @patch('app.tasks.celery_tasks.invalidate_cache_task')
    def test_successful_graph_edge_update(
        self, mock_invalidate_cache, mock_graph_service, mock_base, mock_session_local
    ):
        """Test successful graph edge update with cache invalidation."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_service_instance = MagicMock()
        mock_graph_service.return_value = mock_service_instance
        
        citations = ["cite-1", "cite-2", "cite-3"]
        
        # Execute task
        update_graph_edges_task("resource-123", citations)
        
        # Verify service was called
        mock_graph_service.assert_called_once_with(mock_db)
        mock_service_instance.add_citation_edges.assert_called_once_with("resource-123", citations)
        
        # Verify cache invalidation was queued
        mock_invalidate_cache.apply_async.assert_called_once()
        call_args = mock_invalidate_cache.apply_async.call_args
        assert "graph:neighbors:resource-123" in call_args[1]["args"][0]
        assert "graph:*" in call_args[1]["args"][0]
        assert call_args[1]["priority"] == 9
        
        mock_db.close.assert_called_once()


class TestClassifyResourceTask:
    """Test classification task."""
    
    @patch('app.tasks.celery_tasks.SessionLocal')
    @patch('app.tasks.celery_tasks.Base')
    @patch('app.services.ml_classification_service.MLClassificationService')
    @patch('app.services.taxonomy_service.TaxonomyService')
    def test_successful_classification(
        self, mock_taxonomy_service, mock_ml_service, mock_base, mock_session_local
    ):
        """Test successful resource classification."""
        from backend.app.domain.classification import ClassificationResult, ClassificationPrediction
        
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_ml_instance = MagicMock()
        mock_ml_service.return_value = mock_ml_instance
        
        # Return ClassificationResult domain object instead of list of tuples
        classification_result = ClassificationResult(
            predictions=[
                ClassificationPrediction(taxonomy_id="cat-1", confidence=0.95, rank=1),
                ClassificationPrediction(taxonomy_id="cat-2", confidence=0.85, rank=2),
                ClassificationPrediction(taxonomy_id="cat-3", confidence=0.75, rank=3),
            ],
            model_version="test-model-v1",
            inference_time_ms=50.0,
            resource_id="resource-123"
        )
        mock_ml_instance.predict.return_value = classification_result
        
        mock_taxonomy_instance = MagicMock()
        mock_taxonomy_service.return_value = mock_taxonomy_instance
        
        # Execute task
        classify_resource_task("resource-123")
        
        # Verify ML service was called
        mock_ml_service.assert_called_once_with(mock_db)
        mock_ml_instance.predict.assert_called_once_with("resource-123", top_k=5)
        
        # Verify taxonomy service stored predictions
        mock_taxonomy_service.assert_called_once_with(mock_db)
        assert mock_taxonomy_instance.classify_resource.call_count == 3
        
        # Verify each prediction was stored with is_predicted=True
        calls = mock_taxonomy_instance.classify_resource.call_args_list
        assert calls[0][1]["resource_id"] == "resource-123"
        assert calls[0][1]["category_id"] == "cat-1"
        assert calls[0][1]["confidence"] == 0.95
        assert calls[0][1]["is_predicted"] is True
        
        mock_db.close.assert_called_once()


class TestInvalidateCacheTask:
    """Test cache invalidation task."""
    
    def test_task_configuration(self):
        """Test task is properly configured."""
        assert invalidate_cache_task.name == "app.tasks.celery_tasks.invalidate_cache_task"
        # Cache invalidation task doesn't use DatabaseTask base
        assert not issubclass(type(invalidate_cache_task), type(DatabaseTask))


class TestRefreshRecommendationProfileTask:
    """Test recommendation profile refresh task."""
    
    def test_task_configuration(self):
        """Test task is properly configured."""
        assert refresh_recommendation_profile_task.name == "app.tasks.celery_tasks.refresh_recommendation_profile_task"


class TestBatchProcessResourcesTask:
    """Test batch processing task."""
    
    @patch('app.tasks.celery_tasks.SessionLocal')
    @patch('app.tasks.celery_tasks.Base')
    @patch('app.tasks.celery_tasks.regenerate_embedding_task')
    def test_batch_regenerate_embeddings(
        self, mock_regen_task, mock_base, mock_session_local
    ):
        """Test batch embedding regeneration."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        resource_ids = ["res-1", "res-2", "res-3"]
        
        # Mock the task to avoid update_state issues
        with patch.object(batch_process_resources_task, 'update_state'):
            # Execute task
            result = batch_process_resources_task(resource_ids, "regenerate_embeddings")
        
        # Verify individual tasks were queued
        assert mock_regen_task.apply_async.call_count == 3
        
        # Verify result
        assert result["status"] == "completed"
        assert result["processed"] == 3
        assert result["operation"] == "regenerate_embeddings"
        
        mock_db.close.assert_called_once()
    
    @patch('app.tasks.celery_tasks.SessionLocal')
    @patch('app.tasks.celery_tasks.Base')
    @patch('app.tasks.celery_tasks.recompute_quality_task')
    def test_batch_recompute_quality(
        self, mock_quality_task, mock_base, mock_session_local
    ):
        """Test batch quality recomputation."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        resource_ids = ["res-1", "res-2"]
        
        # Mock the task to avoid update_state issues
        with patch.object(batch_process_resources_task, 'update_state'):
            # Execute task
            result = batch_process_resources_task(resource_ids, "recompute_quality")
        
        # Verify individual tasks were queued
        assert mock_quality_task.apply_async.call_count == 2
        
        # Verify result
        assert result["status"] == "completed"
        assert result["processed"] == 2
        
        mock_db.close.assert_called_once()
    
    @patch('app.tasks.celery_tasks.SessionLocal')
    @patch('app.tasks.celery_tasks.Base')
    def test_batch_unknown_operation(self, mock_base, mock_session_local):
        """Test batch processing with unknown operation."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        resource_ids = ["res-1"]
        
        # Mock the task to avoid update_state issues
        with patch.object(batch_process_resources_task, 'update_state'):
            # Execute task with unknown operation
            result = batch_process_resources_task(resource_ids, "unknown_operation")
        
        # Should complete but log warning
        assert result["status"] == "completed"
        assert result["processed"] == 1
        
        mock_db.close.assert_called_once()


class TestScheduledMaintenanceTasks:
    """Test scheduled maintenance tasks."""
    
    @patch('app.tasks.celery_tasks.SessionLocal')
    @patch('app.tasks.celery_tasks.Base')
    def test_monitor_quality_degradation(self, mock_base, mock_session_local):
        """Test quality degradation monitoring task."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Execute task (currently a stub)
        monitor_quality_degradation_task()
        
        # Verify session was managed
        mock_session_local.assert_called_once()
        mock_db.close.assert_called_once()
    
    @patch('app.tasks.celery_tasks.SessionLocal')
    @patch('app.tasks.celery_tasks.Base')
    def test_detect_quality_outliers(self, mock_base, mock_session_local):
        """Test quality outlier detection task."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Execute task (currently a stub)
        detect_quality_outliers_task()
        
        # Verify session was managed
        mock_session_local.assert_called_once()
        mock_db.close.assert_called_once()
    
    @patch('app.tasks.celery_tasks.SessionLocal')
    @patch('app.tasks.celery_tasks.Base')
    def test_retrain_classification_model(self, mock_base, mock_session_local):
        """Test classification model retraining task."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Execute task (currently a stub)
        retrain_classification_model_task()
        
        # Verify session was managed
        mock_session_local.assert_called_once()
        mock_db.close.assert_called_once()
    
    def test_cleanup_expired_cache_configuration(self):
        """Test cache cleanup task configuration."""
        assert cleanup_expired_cache_task.name == "app.tasks.celery_tasks.cleanup_expired_cache_task"


class TestDatabaseTaskSessionManagement:
    """Test DatabaseTask session management in various scenarios."""
    
    @patch('app.tasks.celery_tasks.SessionLocal')
    @patch('app.tasks.celery_tasks.Base')
    def test_session_closed_on_success(self, mock_base, mock_session_local):
        """Test database session is closed after successful task execution."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Execute any DatabaseTask-based task
        from app.tasks.celery_tasks import DatabaseTask
        
        @celery_app.task(bind=True, base=DatabaseTask, name='test_session_success')
        def test_task(self, db=None):
            assert db is not None
            return "success"
        
        result = test_task()
        
        assert result == "success"
        mock_db.close.assert_called_once()
    
    @patch('app.tasks.celery_tasks.SessionLocal')
    @patch('app.tasks.celery_tasks.Base')
    def test_session_closed_on_exception(self, mock_base, mock_session_local):
        """Test database session is closed even when task raises exception."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        from app.tasks.celery_tasks import DatabaseTask
        
        @celery_app.task(bind=True, base=DatabaseTask, name='test_session_error')
        def failing_task(self, db=None):
            raise RuntimeError("Task failed")
        
        with pytest.raises(RuntimeError, match="Task failed"):
            failing_task()
        
        # Session should still be closed
        mock_db.close.assert_called_once()
    
    @patch('app.tasks.celery_tasks.SessionLocal')
    @patch('app.tasks.celery_tasks.Base')
    def test_multiple_tasks_get_separate_sessions(self, mock_base, mock_session_local):
        """Test each task execution gets its own database session."""
        mock_db1 = MagicMock()
        mock_db2 = MagicMock()
        mock_session_local.side_effect = [mock_db1, mock_db2]
        
        from app.tasks.celery_tasks import DatabaseTask
        
        @celery_app.task(bind=True, base=DatabaseTask, name='test_multiple_sessions')
        def test_task(self, db=None):
            return "success"
        
        # Execute task twice
        test_task()
        test_task()
        
        # Verify both sessions were created and closed
        assert mock_session_local.call_count == 2
        mock_db1.close.assert_called_once()
        mock_db2.close.assert_called_once()
