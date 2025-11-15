"""
Performance monitoring utilities for Phase 11 Hybrid Recommendation Engine.

Provides decorators and utilities for:
- Timing method execution
- Logging slow queries and operations
- Tracking cache hit rates
- Monitoring recommendation generation metrics
"""

import functools
import logging
import time
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """
    Singleton class to track performance metrics across the application.
    
    Tracks:
    - Method execution times
    - Cache hit/miss rates
    - Slow query counts
    - Recommendation generation metrics
    """
    
    _instance: Optional['PerformanceMetrics'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize metrics storage."""
        self.method_timings: Dict[str, list] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.slow_query_count = 0
        self.recommendation_metrics: Dict[str, Any] = {
            'total_requests': 0,
            'total_candidates': [],
            'scoring_times': [],
            'mmr_times': [],
            'novelty_times': []
        }
    
    def record_timing(self, method_name: str, duration: float):
        """
        Record method execution time.
        
        Args:
            method_name: Name of the method
            duration: Execution time in seconds
        """
        if method_name not in self.method_timings:
            self.method_timings[method_name] = []
        self.method_timings[method_name].append(duration)
    
    def record_cache_hit(self):
        """Record a cache hit."""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record a cache miss."""
        self.cache_misses += 1
    
    def record_slow_query(self):
        """Record a slow query (>100ms)."""
        self.slow_query_count += 1
    
    def record_recommendation_request(
        self,
        candidate_count: int,
        scoring_time: float,
        mmr_time: float,
        novelty_time: float
    ):
        """
        Record recommendation generation metrics.
        
        Args:
            candidate_count: Number of candidates generated
            scoring_time: Time spent scoring candidates (seconds)
            mmr_time: Time spent on MMR diversity optimization (seconds)
            novelty_time: Time spent on novelty boosting (seconds)
        """
        self.recommendation_metrics['total_requests'] += 1
        self.recommendation_metrics['total_candidates'].append(candidate_count)
        self.recommendation_metrics['scoring_times'].append(scoring_time)
        self.recommendation_metrics['mmr_times'].append(mmr_time)
        self.recommendation_metrics['novelty_times'].append(novelty_time)
    
    def get_cache_hit_rate(self) -> float:
        """
        Calculate cache hit rate.
        
        Returns:
            Cache hit rate (0.0-1.0)
        """
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return self.cache_hits / total
    
    def get_average_timing(self, method_name: str) -> Optional[float]:
        """
        Get average execution time for a method.
        
        Args:
            method_name: Name of the method
            
        Returns:
            Average execution time in seconds, or None if no data
        """
        if method_name not in self.method_timings or not self.method_timings[method_name]:
            return None
        return sum(self.method_timings[method_name]) / len(self.method_timings[method_name])
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all performance metrics.
        
        Returns:
            Dictionary with performance metrics summary
        """
        summary = {
            'cache_hit_rate': self.get_cache_hit_rate(),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'slow_query_count': self.slow_query_count,
            'method_timings': {}
        }
        
        # Add average timings for each method
        for method_name in self.method_timings:
            avg_time = self.get_average_timing(method_name)
            if avg_time is not None:
                summary['method_timings'][method_name] = {
                    'average_ms': avg_time * 1000,
                    'count': len(self.method_timings[method_name])
                }
        
        # Add recommendation metrics
        if self.recommendation_metrics['total_requests'] > 0:
            summary['recommendation_metrics'] = {
                'total_requests': self.recommendation_metrics['total_requests'],
                'avg_candidates': sum(self.recommendation_metrics['total_candidates']) / len(self.recommendation_metrics['total_candidates']),
                'avg_scoring_time_ms': sum(self.recommendation_metrics['scoring_times']) / len(self.recommendation_metrics['scoring_times']) * 1000,
                'avg_mmr_time_ms': sum(self.recommendation_metrics['mmr_times']) / len(self.recommendation_metrics['mmr_times']) * 1000,
                'avg_novelty_time_ms': sum(self.recommendation_metrics['novelty_times']) / len(self.recommendation_metrics['novelty_times']) * 1000
            }
        
        return summary
    
    def reset(self):
        """Reset all metrics."""
        self._initialize()


# Global metrics instance
metrics = PerformanceMetrics()


def timing_decorator(target_ms: float = 200.0):
    """
    Decorator to measure and log method execution time.
    
    Logs warning if execution time exceeds target.
    Records timing in global metrics.
    
    Args:
        target_ms: Target execution time in milliseconds (default: 200ms)
        
    Returns:
        Decorator function
    
    Example:
        @timing_decorator(target_ms=100.0)
        def my_method(self):
            # method implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                duration = end_time - start_time
                duration_ms = duration * 1000
                
                # Record timing
                method_name = f"{func.__module__}.{func.__qualname__}"
                metrics.record_timing(method_name, duration)
                
                # Log if exceeds target
                if duration_ms > target_ms:
                    logger.warning(
                        f"Slow operation: {method_name} took {duration_ms:.2f}ms (target: {target_ms}ms)"
                    )
                else:
                    logger.debug(f"{method_name} completed in {duration_ms:.2f}ms")
        
        return wrapper
    return decorator


def slow_query_logger(threshold_ms: float = 100.0):
    """
    Decorator to log slow database queries.
    
    Args:
        threshold_ms: Threshold in milliseconds to consider a query slow (default: 100ms)
        
    Returns:
        Decorator function
    
    Example:
        @slow_query_logger(threshold_ms=50.0)
        def query_method(self):
            # database query implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                duration = end_time - start_time
                duration_ms = duration * 1000
                
                # Log slow queries
                if duration_ms > threshold_ms:
                    method_name = f"{func.__module__}.{func.__qualname__}"
                    logger.warning(
                        f"Slow query: {method_name} took {duration_ms:.2f}ms (threshold: {threshold_ms}ms)"
                    )
                    metrics.record_slow_query()
        
        return wrapper
    return decorator
