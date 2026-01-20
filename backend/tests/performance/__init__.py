"""
Performance testing utilities for Neo Alexandria.

Provides decorators and utilities for measuring and enforcing performance requirements.
"""

import time
import functools
from typing import Callable, Any


class PerformanceRegressionError(AssertionError):
    """Raised when a performance test exceeds its time limit."""

    pass


def performance_limit(max_ms: int) -> Callable:
    """
    Decorator to enforce performance limits on test functions.

    Args:
        max_ms: Maximum allowed execution time in milliseconds

    Raises:
        PerformanceRegressionError: If execution exceeds max_ms

    Example:
        @performance_limit(max_ms=200)
        def test_fast_operation():
            # Test code that should complete in < 200ms
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                elapsed_ms = (end_time - start_time) * 1000

                if elapsed_ms > max_ms:
                    raise PerformanceRegressionError(
                        f"{func.__name__} took {elapsed_ms:.2f}ms, limit is {max_ms}ms"
                    )

                print(
                    f"✓ {func.__name__} completed in {elapsed_ms:.2f}ms "
                    f"(limit: {max_ms}ms)"
                )

        return wrapper

    return decorator


__all__ = ["performance_limit", "PerformanceRegressionError"]
