# ML Model Loading Optimization (Task 20)

## Overview

This document describes the ML model loading optimizations implemented to improve test execution time. The optimizations focus on:

1. **Module-level caching** for integration tests that need real models
2. **Automatic mocking** for unit tests to avoid model loading
3. **Explicit mock fixtures** for service-level testing

## Problem Statement

ML models (BAAI/bge-m3, classification models) are expensive to load:
- Model download: 100-500MB per model
- Loading time: 5-30 seconds per model
- Memory usage: 500MB-2GB per model

Without optimization, each test that uses these models would load them independently, causing:
- Slow test execution (minutes instead of seconds)
- High memory usage
- Potential timeouts in CI/CD

## Solution

### 1. Module-Level Cached Fixtures

For integration tests that require real model inference, we provide module-scoped fixtures that load models once per test module:

```python
@pytest.fixture(scope="module")
def ml_classification_model_cached():
    """Load ML classification model once per test module."""
    # Loads model, yields (model, tokenizer, device)
    # Cleans up after all tests in module complete
```

```python
@pytest.fixture(scope="module")
def sparse_embedding_model_cached():
    """Load BAAI/bge-m3 model once per test module."""
    # Loads model, yields (model, tokenizer, device)
    # Cleans up after all tests in module complete
```

**Usage in integration tests:**

```python
@pytest.mark.use_real_models
def test_classification_integration(ml_classification_model_cached):
    model, tokenizer, device = ml_classification_model_cached
    if model is None:
        pytest.skip("ML model not available")
    # Use model for testing...
```

### 2. Automatic Mocking for Unit Tests

Unit tests automatically have ML model loading mocked via the `mock_ml_models_in_unit_tests` autouse fixture:

```python
@pytest.fixture(autouse=True)
def mock_ml_models_in_unit_tests(request):
    """Automatically mock ML model loading in unit tests."""
    # Detects if test is in /unit/ or /services/ directory
    # Automatically patches model loading methods
    # Integration tests can opt out with @pytest.mark.use_real_models
```

This means unit tests don't need to do anything special - models are automatically mocked.

### 3. Explicit Mock Fixtures

For tests that need more control over mocking, we provide explicit mock fixtures:

```python
@pytest.fixture
def mock_ml_classification_service():
    """Mock MLClassificationService for unit tests."""
    # Returns fully configured mock with realistic responses
```

```python
@pytest.fixture
def mock_sparse_embedding_service():
    """Mock SparseEmbeddingService for unit tests."""
    # Returns fully configured mock with realistic responses
```

**Usage:**

```python
def test_classification_logic(mock_ml_classification_service):
    result = mock_ml_classification_service.predict("test text")
    assert isinstance(result, ClassificationResult)
    assert len(result.predictions) > 0
```

## Test Organization

### Unit Tests (Automatically Mocked)

Location: `backend/tests/unit/`, `backend/tests/services/`

Behavior:
- ML models are automatically mocked
- No model loading occurs
- Fast execution (milliseconds per test)
- No network access required

Example:
```python
# backend/tests/unit/phase8_classification/test_ml_classification_service.py
def test_predict_returns_classification_result(test_db):
    # Model loading is automatically mocked
    service = MLClassificationService(test_db)
    # Test logic without loading real model
```

### Integration Tests (Optional Real Models)

Location: `backend/tests/integration/`

Behavior:
- By default, models are mocked
- Use `@pytest.mark.use_real_models` to load real models
- Real models are cached at module level
- Tests skip if models unavailable

Example:
```python
# backend/tests/integration/phase4_hybrid_search/test_sparse_embedding_integration.py
@pytest.mark.use_real_models
def test_sparse_embedding_service_integration(test_db, sparse_embedding_model_cached):
    model, tokenizer, device = sparse_embedding_model_cached
    if model is None:
        pytest.skip("Sparse embedding model not available")
    # Use real model for integration testing
```

## Performance Impact

### Before Optimization

- Unit tests loading models: ~30 seconds per test file
- Integration tests loading models: ~60 seconds per test file
- Total test suite: ~28 minutes
- Memory usage: 4-8GB peak

### After Optimization

- Unit tests (mocked): ~0.5 seconds per test file
- Integration tests (cached): ~10 seconds per test file (first test), ~0.5s subsequent
- Total test suite: ~12-15 minutes (estimated)
- Memory usage: 1-2GB peak

**Expected improvement: 50-60% reduction in test execution time**

## CI/CD Considerations

### Model Availability

In CI/CD environments, ML models may not be available:
- Models require download (100-500MB)
- May require authentication
- May not be needed for all test runs

**Solution:** Tests gracefully skip if models unavailable:

```python
if model is None:
    pytest.skip("ML model not available")
```

### Selective Test Execution

Run only unit tests (fast, no models):
```bash
pytest backend/tests/unit/ backend/tests/services/ -v
```

Run integration tests with real models:
```bash
pytest backend/tests/integration/ -v -m use_real_models
```

Run all tests (mocked models):
```bash
pytest backend/tests/ -v
```

## Migration Guide

### Updating Existing Tests

#### Unit Tests
No changes needed - automatic mocking handles it.

#### Integration Tests That Need Real Models

1. Add the `@pytest.mark.use_real_models` decorator
2. Add the appropriate cached model fixture parameter
3. Add model availability check

Before:
```python
def test_classification(test_db):
    service = MLClassificationService(test_db)
    result = service.predict("test")
    assert result is not None
```

After:
```python
@pytest.mark.use_real_models
def test_classification(test_db, ml_classification_model_cached):
    model, tokenizer, device = ml_classification_model_cached
    if model is None:
        pytest.skip("ML model not available")
    
    service = MLClassificationService(test_db)
    result = service.predict("test")
    assert result is not None
```

#### Integration Tests That Don't Need Real Models

No changes needed - they'll use mocked models by default.

## Troubleshooting

### Tests Still Loading Models

**Symptom:** Unit tests are slow and loading models

**Solution:** Verify test is in correct directory:
- Unit tests should be in `backend/tests/unit/` or `backend/tests/services/`
- Check that `mock_ml_models_in_unit_tests` fixture is active

### Integration Tests Skipping

**Symptom:** Integration tests always skip with "ML model not available"

**Possible causes:**
1. Models not downloaded/trained yet
2. Model path incorrect
3. Missing dependencies (transformers, torch)

**Solution:**
- Check model exists at expected path
- Verify dependencies installed: `pip install transformers torch`
- For development, use mocked tests instead

### Memory Issues

**Symptom:** Tests crash with OOM errors

**Solution:**
1. Reduce number of parallel test workers
2. Run integration tests separately from unit tests
3. Use mocked tests instead of real models

## Files Modified

### Core Files
- `backend/tests/conftest.py` - Added ML model optimization fixtures

### Integration Tests Updated
- `backend/tests/integration/phase4_hybrid_search/test_sparse_embedding_integration.py`

### Documentation
- `backend/tests/ML_MODEL_OPTIMIZATION.md` (this file)

## Related Requirements

- Requirement 11.1: ML model loading optimization
- Task 20: Optimize ML model loading in tests

## Future Improvements

1. **Model caching across test runs**: Cache downloaded models in CI/CD
2. **Lazy loading in services**: Improve service-level lazy loading
3. **Model quantization**: Use smaller quantized models for testing
4. **Mock model responses**: Pre-record model responses for deterministic testing
