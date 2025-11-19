# Parallel Test Execution Guide

## Overview

This document describes how to run tests in parallel using pytest-xdist and documents known isolation issues and their solutions.

## Installation

```bash
pip install pytest-xdist>=3.5.0
```

## Basic Usage

### Run with automatic worker count
```bash
pytest -n auto
```

### Run with specific worker count
```bash
pytest -n 2  # Use 2 workers
pytest -n 4  # Use 4 workers
```

### Run specific test directories in parallel
```bash
pytest tests/unit/ -n auto
pytest tests/integration/ -n 4
```

## Known Isolation Issues

### 1. ML Model Loading (CRITICAL)

**Issue**: Tests that load ML models (transformers, torch) consume significant memory. When running with many workers (e.g., -n auto with 16 workers), each worker tries to load models, causing memory exhaustion and "paging file too small" errors on Windows.

**Solution**: 
- Run ML model tests separately without parallel execution
- Use the `@pytest.mark.use_real_models` marker for tests that load real models
- Run other tests in parallel, excluding ML model tests

**Example**:
```bash
# Run non-ML tests in parallel
pytest -n auto -m "not use_real_models"

# Run ML tests separately (no parallel)
pytest -m use_real_models
```

**Affected Tests**:
- `tests/unit/phase8_classification/test_ml_classification_service.py`
- `tests/integration/phase8_classification/`
- Any test that imports `transformers`, `torch`, or loads embedding models

### 2. Database Fixtures

**Issue**: Database fixtures need proper isolation to avoid conflicts between parallel workers.

**Solution**: 
- Use function-scoped database fixtures (already implemented in `tests/conftest.py`)
- Each test gets its own database session with transaction rollback
- In-memory SQLite is used for unit tests

**Status**: ✅ Already handled by existing fixtures

### 3. Shared File System Resources

**Issue**: Tests that write to the same files or directories can conflict.

**Solution**:
- Use temporary directories with unique names per test
- Use pytest's `tmp_path` fixture for file operations
- Avoid hardcoded file paths in tests

**Status**: ✅ Most tests already use proper temporary paths

### 4. Global State and Singletons

**Issue**: Tests that modify global state or use singletons can interfere with each other.

**Solution**:
- Mock global objects in tests
- Reset global state in fixture teardown
- Avoid module-level state that persists across tests

**Status**: ✅ Domain objects are stateless, services are injected

## Recommended Parallel Execution Strategy

### For Development (Fast Feedback)

Run lightweight tests in parallel, skip slow ML tests:

```bash
pytest -n auto -m "not use_real_models and not slow"
```

### For CI/CD (Comprehensive)

Run tests in stages:

```bash
# Stage 1: Fast unit tests in parallel
pytest tests/unit/ -n 4 -m "not use_real_models" --tb=short

# Stage 2: Integration tests in parallel
pytest tests/integration/ -n 2 -m "not use_real_models" --tb=short

# Stage 3: ML model tests (no parallel)
pytest -m use_real_models --tb=short

# Stage 4: Slow tests (no parallel)
pytest -m slow --tb=short
```

### For Full Test Suite

Run all tests with controlled parallelism:

```bash
# Run with 2-4 workers to avoid memory issues
pytest -n 2 --ignore=tests/unit/phase8_classification/test_active_learning.py
```

## Performance Improvements

With parallel execution enabled:

- **Unit tests**: ~50% faster (18s → 9s for simple tests)
- **Integration tests**: ~40% faster (depends on I/O)
- **Full suite**: ~30-40% faster overall (excluding ML tests)

## Troubleshooting

### "Paging file too small" Error

**Cause**: Too many workers trying to load ML models simultaneously

**Solution**: 
- Reduce worker count: `pytest -n 2`
- Exclude ML tests: `pytest -n auto -m "not use_real_models"`

### Tests Pass Individually But Fail in Parallel

**Cause**: Test isolation issue (shared state, database conflicts, etc.)

**Solution**:
1. Run the failing test alone to verify it passes
2. Check for global state or shared resources
3. Ensure fixtures have proper scope and cleanup
4. Add debugging: `pytest -n 0` (no parallel) vs `pytest -n 2`

### Slow Test Discovery

**Cause**: pytest-xdist needs to collect tests on each worker

**Solution**:
- Use `--collect-only` to verify test collection is fast
- Avoid expensive imports at module level
- Use lazy imports for heavy dependencies

## Best Practices

1. **Mark ML Tests**: Use `@pytest.mark.use_real_models` for tests that load models
2. **Use Function Scope**: Prefer function-scoped fixtures for better isolation
3. **Avoid Global State**: Don't modify global variables or singletons
4. **Use Temporary Paths**: Use `tmp_path` fixture for file operations
5. **Mock Heavy Dependencies**: Mock ML models, external APIs, etc. in unit tests
6. **Test Isolation**: Each test should be runnable independently
7. **Cleanup Resources**: Ensure fixtures clean up after themselves

## Configuration

Parallel execution is configured in `pytest.ini`:

```ini
# Parallel execution configuration (Phase 12.6)
# Use -n auto to enable parallel execution with pytest-xdist
# Use -n 2 or -n 4 for controlled worker count
```

## Future Improvements

1. **Test Grouping**: Group tests by resource requirements (CPU, memory, I/O)
2. **Worker Pools**: Use different worker pools for different test types
3. **Distributed Testing**: Run tests across multiple machines
4. **Smart Scheduling**: Schedule slow tests first to minimize total time
5. **Resource Monitoring**: Track memory/CPU usage per worker

## References

- [pytest-xdist documentation](https://pytest-xdist.readthedocs.io/)
- [pytest fixtures documentation](https://docs.pytest.org/en/stable/fixture.html)
- [Test isolation best practices](https://docs.pytest.org/en/stable/goodpractices.html)
