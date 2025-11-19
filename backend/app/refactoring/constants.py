"""
Constants for refactoring validation framework.

Defines thresholds, weights, and configuration values used
throughout the refactoring process.
"""

# Code quality thresholds
MAX_FUNCTION_LINES = 30
MAX_CLASS_LINES = 300
MAX_PUBLIC_METHODS = 10
MAX_PARAMETERS = 5

# Code smell detection thresholds
DUPLICATION_SIMILARITY_THRESHOLD = 0.80  # 80% similarity = duplicate
LONG_FUNCTION_THRESHOLD = MAX_FUNCTION_LINES
LARGE_CLASS_THRESHOLD = MAX_CLASS_LINES
FEATURE_ENVY_RATIO = 0.6  # 60% external calls = feature envy

# Test coverage thresholds
MIN_TEST_COVERAGE = 0.85  # 85% minimum coverage
TARGET_TEST_COVERAGE = 0.90  # 90% target coverage

# Type hint coverage
MIN_TYPE_HINT_COVERAGE = 1.0  # 100% on public methods

# Complexity thresholds
MAX_CYCLOMATIC_COMPLEXITY = 10
MAX_COGNITIVE_COMPLEXITY = 15

# Validation settings
RUN_TESTS_AFTER_REFACTORING = True
AUTO_ROLLBACK_ON_FAILURE = True
ENABLE_TYPE_CHECKING = True

# File patterns
PYTHON_FILE_PATTERN = "*.py"
TEST_FILE_PATTERN = "test_*.py"
SERVICE_DIR = "backend/app/services"

# Reporting
REPORT_OUTPUT_DIR = "backend/refactoring_reports"
METRICS_OUTPUT_FILE = "refactoring_metrics.json"
