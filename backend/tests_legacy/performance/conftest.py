"""
Performance test fixtures.

This module imports fixtures from ml_benchmarks for use in performance tests.
"""

import sys
from pathlib import Path

# Add parent directory to path to enable imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import fixtures from ml_benchmarks conftest
from ml_benchmarks.conftest import (
    classification_test_data,
    recommendation_test_data,
    search_relevance_data,
    summarization_test_data,
    trained_classifier,
    trained_ncf_model,
    mock_openai_api,
    mock_all_external_apis,
    isolated_test_db,
    benchmark_session_db,
    benchmark_output_dir,
    set_random_seeds,
    benchmark_timeout,
    memory_monitor,
    gpu_memory_monitor,
)

__all__ = [
    "classification_test_data",
    "recommendation_test_data",
    "search_relevance_data",
    "summarization_test_data",
    "trained_classifier",
    "trained_ncf_model",
    "mock_openai_api",
    "mock_all_external_apis",
    "isolated_test_db",
    "benchmark_session_db",
    "benchmark_output_dir",
    "set_random_seeds",
    "benchmark_timeout",
    "memory_monitor",
    "gpu_memory_monitor",
]
