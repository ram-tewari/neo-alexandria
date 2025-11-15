"""
Performance tests for quality assessment system.
Tests latency and throughput requirements for quality operations.
"""
import pytest
import time
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.services.quality_service import QualityService
from backend.app.services.summarization_evaluator import SummarizationEvaluator
from backend.app.database.models import Resource


@pytest.fixture
def quality_service(db_session: Session):
    """Create QualityService instance."""
    return QualityService(db_session)


@pytest.fixture
def summarization_evaluator(db_session: Session):
    """Create SummarizationEvaluator instance."""
    return SummarizationEvaluator(db_session)


@pytest.fixture
def create_test_resources(db_session: Session):
    """Create multiple test resources."""
    def _create(count=100):
        resources = []
        for i in range(count):
            resource = Resource(
                title=f"Performance Test Resource {i}",
                source=f"https://example.com/perf{i}",
                description=f"Performance test content {i} " * 50,
                creator=f"Summary {i}",
                type="article",
                authors=f"Author {i}",
                publication_year=2024,
                subject=["test", "performance", str(i)]
            )
            resources.append(resource)
            db_session.add(resource)
        
        db_session.commit()
        for r in resources:
            db_session.refresh(r)
        return resources
    
    return _create


class TestQualityComputationLatency:
    """Test quality computation latency requirements."""
    
    def test_single_resource_latency(self, quality_service, db_session):
        """Test quality computation for single resource completes in < 1 second."""
        # Create resource
        resource = Resource(
            title="Latency Test",
            source="https://example.com/latency",
            description="Content for latency testing",
            type="article"
        )
        db_session.add(resource)
        db_session.commit()
        db_session.refresh(resource)
        
        # Measure computation time
        start_time = time.time()
        quality_service.compute_quality(resource.id)
        end_time = time.time()
        
        latency = end_time - start_time
        
        # Should complete in less than 1 second
        assert latency < 1.0, f"Quality computation took {latency:.2f}s, expected < 1.0s"
    
    def test_average_latency_multiple_resources(self, quality_service, create_test_resources):
        """Test average latency across multiple resources."""
        resources = create_test_resources(count=10)
        
        latencies = []
        for resource in resources:
            start_time = time.time()
            quality_service.compute_quality(resource.id)
            end_time = time.time()
            latencies.append(end_time - start_time)
        
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        # Average should be well under 1 second
        assert avg_latency < 0.5, f"Average latency {avg_latency:.2f}s, expected < 0.5s"
        # Max should still be under 1 second
        assert max_latency < 1.0, f"Max latency {max_latency:.2f}s, expected < 1.0s"


class TestBatchQualityComputationThroughput:
    """Test batch quality computation throughput requirements."""
    
    def test_batch_throughput_100_resources(self, quality_service, create_test_resources):
        """Test batch quality computation achieves 100 resources/minute."""
        resources = create_test_resources(count=100)
        
        start_time = time.time()
        
        for resource in resources:
            quality_service.compute_quality(resource.id)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Calculate throughput (resources per minute)
        throughput = (len(resources) / elapsed_time) * 60
        
        # Should achieve at least 100 resources per minute
        assert throughput >= 100, f"Throughput {throughput:.1f} resources/min, expected >= 100"
    
    def test_batch_computation_scales_linearly(self, quality_service, create_test_resources):
        """Test that batch computation scales approximately linearly."""
        # Test with different batch sizes
        batch_sizes = [10, 50, 100]
        throughputs = []
        
        for size in batch_sizes:
            resources = create_test_resources(count=size)
            
            start_time = time.time()
            for resource in resources:
                quality_service.compute_quality(resource.id)
            end_time = time.time()
            
            elapsed = end_time - start_time
            throughput = (size / elapsed) * 60
            throughputs.append(throughput)
        
        # Throughput should remain relatively consistent (within 50% variance)
        avg_throughput = sum(throughputs) / len(throughputs)
        for throughput in throughputs:
            variance = abs(throughput - avg_throughput) / avg_throughput
            assert variance < 0.5, f"Throughput variance {variance:.2%} too high"


class TestOutlierDetectionPerformance:
    """Test outlier detection performance requirements."""
    
    def test_outlier_detection_1000_resources(self, quality_service, create_test_resources):
        """Test outlier detection on 1000 resources completes in < 30 seconds."""
        resources = create_test_resources(count=1000)
        
        # Set quality scores for all resources
        for i, resource in enumerate(resources):
            resource.quality_accuracy = 0.7 + (i % 10) * 0.02
            resource.quality_completeness = 0.65 + (i % 8) * 0.03
            resource.quality_consistency = 0.72 + (i % 6) * 0.025
            resource.quality_timeliness = 0.68 + (i % 12) * 0.015
            resource.quality_relevance = 0.7 + (i % 9) * 0.02
            resource.quality_overall = 0.69 + (i % 10) * 0.02
        
        quality_service.db.commit()
        
        # Measure outlier detection time
        start_time = time.time()
        quality_service.detect_quality_outliers()
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        
        # Should complete in less than 30 seconds
        assert elapsed_time < 30.0, f"Outlier detection took {elapsed_time:.2f}s, expected < 30s"
    
    def test_outlier_detection_with_batching(self, quality_service, create_test_resources):
        """Test outlier detection with different batch sizes."""
        resources = create_test_resources(count=500)
        
        # Set quality scores
        for i, resource in enumerate(resources):
            resource.quality_overall = 0.7 + (i % 10) * 0.02
            resource.quality_accuracy = 0.7
            resource.quality_completeness = 0.7
            resource.quality_consistency = 0.7
            resource.quality_timeliness = 0.7
            resource.quality_relevance = 0.7
        
        quality_service.db.commit()
        
        # Test with different batch sizes
        batch_sizes = [100, 250, 500]
        times = []
        
        for batch_size in batch_sizes:
            start_time = time.time()
            quality_service.detect_quality_outliers(batch_size=batch_size)
            end_time = time.time()
            times.append(end_time - start_time)
        
        # All should complete reasonably fast
        for t in times:
            assert t < 20.0, f"Outlier detection took {t:.2f}s with batching"


class TestSummarizationEvaluationLatency:
    """Test summarization evaluation latency requirements."""
    
    def test_evaluation_without_g_eval_latency(self, summarization_evaluator, db_session):
        """Test summary evaluation without G-Eval completes quickly."""
        resource = Resource(
            title="Summary Eval Test",
            source="https://example.com/summary-eval",
            description="Content for summary evaluation testing " * 50,
            creator="Brief summary for evaluation",
            type="article"
        )
        db_session.add(resource)
        db_session.commit()
        db_session.refresh(resource)
        
        # Measure evaluation time without G-Eval
        start_time = time.time()
        summarization_evaluator.evaluate_summary(resource.id, use_g_eval=False)
        end_time = time.time()
        
        latency = end_time - start_time
        
        # Without G-Eval should be very fast (< 2 seconds)
        assert latency < 2.0, f"Summary evaluation took {latency:.2f}s, expected < 2s"
    
    @pytest.mark.skip(reason="Requires OpenAI API key and may be slow")
    def test_evaluation_with_g_eval_latency(self, summarization_evaluator, db_session):
        """Test summary evaluation with G-Eval (requires API key)."""
        resource = Resource(
            title="G-Eval Test",
            source="https://example.com/g-eval",
            description="Content for G-Eval testing",
            creator="Summary for G-Eval",
            type="article"
        )
        db_session.add(resource)
        db_session.commit()
        
        # This test is skipped by default as it requires API key
        # and may take longer due to API calls
        start_time = time.time()
        summarization_evaluator.evaluate_summary(resource.id, use_g_eval=True)
        end_time = time.time()
        
        latency = end_time - start_time
        
        # With G-Eval may take longer but should still be reasonable
        assert latency < 10.0, f"G-Eval evaluation took {latency:.2f}s"


class TestDegradationMonitoringPerformance:
    """Test quality degradation monitoring performance."""
    
    def test_degradation_monitoring_performance(self, quality_service, create_test_resources):
        """Test degradation monitoring completes in reasonable time."""
        from datetime import timedelta
        
        resources = create_test_resources(count=200)
        
        # Set old quality scores
        for resource in resources:
            resource.quality_overall = 0.8
            resource.quality_accuracy = 0.8
            resource.quality_completeness = 0.8
            resource.quality_consistency = 0.8
            resource.quality_timeliness = 0.8
            resource.quality_relevance = 0.8
            resource.quality_last_computed = datetime.now() - timedelta(days=35)
        
        quality_service.db.commit()
        
        # Measure monitoring time
        start_time = time.time()
        quality_service.monitor_quality_degradation(time_window_days=30)
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        
        # Should complete in reasonable time (< 60 seconds for 200 resources)
        assert elapsed_time < 60.0, f"Degradation monitoring took {elapsed_time:.2f}s"


class TestMemoryUsage:
    """Test memory efficiency of quality operations."""
    
    def test_batch_processing_memory_efficiency(self, quality_service, create_test_resources):
        """Test that batch processing doesn't cause memory issues."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process large batch
        resources = create_test_resources(count=500)
        
        for resource in resources:
            quality_service.compute_quality(resource.id)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 500 MB for 500 resources)
        assert memory_increase < 500, f"Memory increased by {memory_increase:.1f}MB"
    
    def test_outlier_detection_memory_efficiency(self, quality_service, create_test_resources):
        """Test outlier detection memory usage."""
        import psutil
        import os
        
        resources = create_test_resources(count=1000)
        
        # Set quality scores
        for i, resource in enumerate(resources):
            resource.quality_overall = 0.7
            resource.quality_accuracy = 0.7
            resource.quality_completeness = 0.7
            resource.quality_consistency = 0.7
            resource.quality_timeliness = 0.7
            resource.quality_relevance = 0.7
        
        quality_service.db.commit()
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        quality_service.detect_quality_outliers()
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        # Outlier detection should be memory-efficient (< 200 MB for 1000 resources)
        assert memory_increase < 200, f"Memory increased by {memory_increase:.1f}MB"


class TestConcurrentOperations:
    """Test performance under concurrent operations."""
    
    def test_concurrent_quality_computations(self, quality_service, create_test_resources):
        """Test multiple concurrent quality computations."""
        import concurrent.futures
        
        resources = create_test_resources(count=50)
        
        def compute_quality(resource_id):
            return quality_service.compute_quality(resource_id)
        
        start_time = time.time()
        
        # Use thread pool for concurrent computations
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(compute_quality, r.id) for r in resources]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Concurrent execution should be faster than sequential
        # (though not necessarily 5x due to database locks)
        assert len(results) == 50
        assert elapsed_time < 30.0, f"Concurrent computation took {elapsed_time:.2f}s"
