# Testing Strategy for Neo Alexandria

## Overview

Neo Alexandria uses a hybrid testing approach that balances speed, reliability, and comprehensive coverage:

1. **Unit Tests** - Fast, isolated tests with mocked dependencies
2. **Integration Tests** - Test component interactions
3. **AI Tests** - Test real AI functionality (requires AI dependencies)

## Test Categories

### Unit Tests (Fast)
- Test individual functions and classes
- Use mocks for external dependencies (AI, network, etc.)
- Should run in < 1 second per test
- Run with: `python run_tests.py unit`

### Integration Tests
- Test multiple components working together
- May use real services but mock external APIs
- Run with: `python run_tests.py integration`

### AI Tests (Slow)
- Test real AI functionality
- Require AI dependencies (transformers, models)
- Can be slow and may fail due to model loading issues
- Run with: `python run_tests.py ai`

## Running Tests

### Quick Commands

```bash
# Fast tests (unit tests with mocked AI)
python run_tests.py fast

# All tests except AI
python run_tests.py unit

# Integration tests
python run_tests.py integration

# AI tests (real AI functionality)
python run_tests.py ai

# All tests
python run_tests.py all
```

### Manual pytest Commands

```bash
# Unit tests only
pytest -m "not (ai or integration or slow)"

# AI tests only
pytest -m "ai"

# Integration tests only
pytest -m "integration"

# Fast tests (no AI dependencies)
pytest -m "not (slow or requires_ai_deps)"

# With coverage
pytest --cov=backend --cov-report=html
```

## Why Mock AI in Unit Tests?

### Problems with Real AI in Tests:
1. **Speed**: AI models are slow to load and process
2. **Dependencies**: Requires heavy ML libraries (transformers, torch, etc.)
3. **Reliability**: Models may fail to load, network issues, etc.
4. **Determinism**: AI outputs can vary, making tests flaky
5. **CI/CD**: CI environments may not have GPU or sufficient memory

### Benefits of Mocking:
1. **Fast**: Tests run in milliseconds instead of seconds
2. **Reliable**: No external dependencies or network calls
3. **Deterministic**: Predictable outputs for assertions
4. **Isolated**: Tests focus on business logic, not AI implementation

## How to Test AI Functionality

### 1. Dedicated AI Tests
Use `test_ai_integration.py` to test real AI functionality:

```python
@pytest.mark.ai
@pytest.mark.requires_ai_deps
def test_ai_summary_generation():
    ai = AICore()
    summary = ai.generate_summary("Test text about machine learning")
    assert "machine learning" in summary.lower()
```

### 2. End-to-End Tests
Test complete ingestion with real AI:

```python
@pytest.mark.ai
@pytest.mark.integration
def test_end_to_end_ai_processing():
    # Don't mock AI - use real AI service
    response = client.post("/resources", json={"url": "..."})
    # Verify AI-generated content
```

### 3. AI Fallback Testing
Test AI service behavior when models aren't available:

```python
@pytest.mark.ai
def test_ai_fallback_behavior():
    ai = AICore()
    # Test fallback logic
```

## Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests  
- `@pytest.mark.ai` - AI-related tests
- `@pytest.mark.slow` - Slow tests
- `@pytest.mark.requires_ai_deps` - Requires AI dependencies

## CI/CD Strategy

### Fast CI Pipeline
```bash
# Run fast tests on every commit
python run_tests.py fast
```

### Full CI Pipeline (nightly)
```bash
# Run all tests including AI
python run_tests.py all
```

### AI-Specific Pipeline
```bash
# Run only AI tests when AI code changes
python run_tests.py ai
```

## Best Practices

### 1. Mock External Dependencies
```python
# Good: Mock AI service
with patch('backend.app.services.resource_service.AICore') as mock_ai:
    mock_ai.return_value.generate_summary.return_value = "Mock summary"
    # Test business logic
```

### 2. Test AI Separately
```python
# Good: Dedicated AI test
@pytest.mark.ai
def test_ai_functionality():
    ai = AICore()
    result = ai.generate_summary("test")
    assert result
```

### 3. Use Appropriate Test Types
- **Unit tests**: Test individual functions
- **Integration tests**: Test component interactions
- **AI tests**: Test AI functionality specifically

### 4. Mark Tests Appropriately
```python
@pytest.mark.ai
@pytest.mark.requires_ai_deps
def test_real_ai():
    # This test requires AI dependencies
    pass

@pytest.mark.unit
def test_business_logic():
    # This test mocks AI
    pass
```

## Troubleshooting

### AI Tests Failing
1. Check if AI dependencies are installed: `pip install transformers torch`
2. Check if models can be downloaded (network access)
3. Check available memory (AI models are large)

### Slow Tests
1. Use `pytest -m "not slow"` to skip slow tests
2. Use `pytest -x` to stop on first failure
3. Use `pytest --tb=short` for shorter tracebacks

### Flaky Tests
1. Check if tests are using real AI (should use mocks for unit tests)
2. Check for race conditions in async tests
3. Add appropriate timeouts and retries
